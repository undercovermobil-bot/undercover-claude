"""Pecah baris master MINI Cooper berlabel generasi "Hatch" polos jadi 3P + 5P.

Dasar: user konfirmasi 2026-07-28 — "Minicooper hatch sama ada varian 3 pintu dan
5 pintu". Sebelumnya 16 baris ini sengaja dibiarkan karena tidak bisa ditebak.

Kondisi awal (dicek di master 2026-07-28): label "Hatch" polos HANYA ada di kategori
Premium (8), Exclusive (4), Transparan (4) = 16 baris, tersebar rata di 4 toko.
Kategori Reguler & Strip sudah punya "Hatch 3 Pintu"/"Hatch 5 Pintu" tersendiri,
jadi pemecahan ini TIDAK menimbulkan baris kembar.

Cara: baris asli diubah jadi varian 3 pintu, lalu ditambahkan baris kembarannya
untuk 5 pintu di akhir sheet (urutan baris tidak memengaruhi lookup). Semua kolom
lain disalin apa adanya dari baris sumber.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter

APPLY = "--apply" in sys.argv
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]
SHEET = "MINI"
NAMA, TOKO, KAT, WARNA, GEN, TAHUN, BIGS, SKU = 2, 3, 4, 5, 6, 7, 8, 9
NCOL = 9


def seg(sku, kode):
    p = str(sku).split("-")
    return "-".join(p[:4] + [kode] + p[5:]) if len(p) == 6 else sku


def run(apply):
    stat = Counter()
    contoh = []
    for mf in MASTERS:
        try:
            wb = load_workbook(mf, data_only=False)
        except FileNotFoundError:
            stat["file_hilang"] += 1
            continue
        ws = wb[SHEET]
        sasaran = []
        for r in range(2, ws.max_row + 1):
            if str(ws.cell(row=r, column=NAMA).value or "").strip() != "MINI Cooper":
                continue
            if str(ws.cell(row=r, column=GEN).value or "").strip() != "Hatch":
                continue
            sasaran.append(r)

        # kembaran 5 pintu ditulis di bawah baris terakhir yg terpakai
        tulis = ws.max_row + 1
        for r in sasaran:
            asli = [ws.cell(row=r, column=c).value for c in range(1, NCOL + 1)]
            if apply:
                ws.cell(row=r, column=GEN, value="Hatch 3 Pintu")
                ws.cell(row=r, column=SKU, value=seg(asli[SKU - 1], "3P"))
                for c in range(1, NCOL + 1):
                    ws.cell(row=tulis, column=c, value=asli[c - 1])
                ws.cell(row=tulis, column=GEN, value="Hatch 5 Pintu")
                ws.cell(row=tulis, column=SKU, value=seg(asli[SKU - 1], "5P"))
            if len(contoh) < 8:
                contoh.append((mf[:14], asli[TOKO - 1], asli[KAT - 1], asli[WARNA - 1],
                               asli[SKU - 1], seg(asli[SKU - 1], "3P"), seg(asli[SKU - 1], "5P")))
            tulis += 1
            stat[f"dipecah[{mf[:14]}]"] += 1
        if apply and sasaran:
            wb.save(mf)
    return stat, contoh


if __name__ == "__main__":
    print("MODE:", "APPLY (master DITULIS)" if APPLY else "DRY-RUN")
    stat, contoh = run(APPLY)
    for k, v in stat.most_common():
        print(f"   {v:5}  {k}")
    if not stat:
        print("   (tidak ada baris 'Hatch' polos tersisa — sudah dipecah sebelumnya)")
    print("\ncontoh (toko, kategori, warna, SKU lama -> 3P, 5P):")
    for c in contoh:
        print("   ", c)
