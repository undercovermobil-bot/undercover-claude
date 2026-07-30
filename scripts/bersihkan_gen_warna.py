"""Bersihkan baris master yang kolom GENERASI-nya berisi NAMA WARNA.

Bug data lama (tercatat sejak 2026-07-17): pada BYD Atto 3 (22 baris) dan
Daihatsu Taft GT (16 baris), nilai "Hijau" masuk ke kolom Generasi — kemungkinan
salah kolom saat input. Skema formula sudah menormalkan segmen SKU-nya jadi `G1`,
jadi baris-baris ini sekarang **kembar persis** dgn baris "Gen 1" yang sah
(toko, kategori, warna, dan SKU sama), cuma beda label generasi.

Penanganan:
  - Kalau baris warna itu punya KEMBARAN sah (Gen 1 dgn toko/kategori/warna sama)
    -> baris warna DIHAPUS, karena murni duplikat.
  - Kalau TIDAK punya kembaran -> label Generasi diperbaiki jadi "Gen 1" dan rentang
    tahunnya disalin dari saudara satu produk, supaya datanya tidak hilang.

Jalankan dry-run dulu; `--apply` untuk menulis.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict

MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]
APPLY = "--apply" in sys.argv
WARNA = {"hijau", "abu", "abu-abu", "merah", "biru", "hitam", "silver", "putih",
         "biru benhur", "hijau army", "orange"}
NAMA, TOKO, KAT, WRN, GEN, THN, BIGS, SKU = 2, 3, 4, 5, 6, 7, 8, 9


def run(apply):
    hapus_total = perbaiki_total = 0
    for mf in MASTERS:
        wb = load_workbook(mf)
        for s in wb.sheetnames:
            ws = wb[s]
            sah = {}          # (nama, toko, kategori, warna) -> tahun, utk baris ber-generasi normal
            tersangka = []
            for r in range(3, ws.max_row + 1):
                nm = ws.cell(row=r, column=NAMA).value
                g = ws.cell(row=r, column=GEN).value
                if not nm or not g:
                    continue
                key = (str(nm), str(ws.cell(row=r, column=TOKO).value),
                       str(ws.cell(row=r, column=KAT).value),
                       str(ws.cell(row=r, column=WRN).value))
                if str(g).strip().lower() in WARNA:
                    tersangka.append((r, key, str(nm)))
                else:
                    sah.setdefault(key, (str(g), ws.cell(row=r, column=THN).value))

            # tahun rujukan per produk, dipakai kalau baris harus diperbaiki bukan dihapus
            tahun_produk = {}
            for (nm, tk, kt, wr), (g, th) in sah.items():
                if th:
                    tahun_produk.setdefault(nm, (g, th))

            buang = []
            for r, key, nm in tersangka:
                if key in sah:
                    buang.append(r)
                else:
                    g, th = tahun_produk.get(nm, ("Gen 1", None))
                    if apply:
                        ws.cell(row=r, column=GEN, value=g)
                        if th:
                            ws.cell(row=r, column=THN, value=th)
                        bigs = ws.cell(row=r, column=BIGS).value
                        if bigs:
                            ws.cell(row=r, column=BIGS,
                                    value=str(bigs).rsplit("-", 1)[0] + "-" + g)
                    perbaiki_total += 1
                    print(f"   PERBAIKI {mf[:12]} {s} baris {r}: {nm} -> generasi '{g}'")

            for r in sorted(buang, reverse=True):
                if apply:
                    ws.delete_rows(r)
                hapus_total += 1
            if buang:
                print(f"   HAPUS    {mf[:12]} {s}: {len(buang)} baris duplikat "
                      f"(baris {min(buang)}-{max(buang)})")
        if apply:
            wb.save(mf)
    return hapus_total, perbaiki_total


if __name__ == "__main__":
    print("MODE:", "APPLY (master DITULIS)" if APPLY else "DRY-RUN")
    h, p = run(APPLY)
    print(f"\nbaris dihapus (duplikat) : {h}")
    print(f"baris diperbaiki labelnya: {p}")
