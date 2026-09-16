"""Buat entri master + SKU untuk Wuling Darion (permintaan mendesak user 2026-07-30).

Model baru yang listing-nya sudah tayang di Undercover Autocare (Reguler, Premium,
Exclusive) tapi belum ada di master, jadi SKU-nya kosong. Generasi diambil dari
teks varian listing: **Gen 1 (2025-2026)**.

Cara: MENYALIN POLA MODEL WULING YANG SUDAH ADA (`Wuling Alvez`, 66 baris) lalu
mengganti nama model, kode model, dan rentang tahun. Menyalin pola jauh lebih aman
daripada menyusun ulang daftar warna dari nol — struktur Wuling BEDA dari template
umum: Premium & Exclusive cuma ada di UA/OT, sedangkan SP/OP punya Reguler 6 warna
(termasuk Orange) + Transparan.

Sengaja dibuat LENGKAP 66 baris, bukan cuma 3 kategori yang diminta. Alasannya baru
terbukti hari ini: entri master yang dibuat sebagian (BYD Denza D9 cuma Premium)
menimbulkan masalah belakangan dan harus dibereskan manual.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

APPLY = "--apply" in sys.argv
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]
SHEET = "Wuling"
CONTOH = "Wuling Alvez"          # pola yang disalin
KODE_CONTOH = "ALV"
BARU_NAMA = "Wuling Darion"
BARU_KODE = "DRN"
BARU_THN = "2025-2026"
BARU_GEN = "Gen 1"


def main():
    print("MODE:", "APPLY (master DITULIS)" if APPLY else "DRY-RUN")
    hasil = []
    for mf in MASTERS:
        wb = load_workbook(mf)
        ws = wb[SHEET]

        # pastikan belum ada, supaya aman dijalankan ulang
        sudah = [r for r in range(3, ws.max_row + 1)
                 if ws.cell(row=r, column=2).value
                 and BARU_NAMA.lower() in str(ws.cell(row=r, column=2).value).lower()]
        if sudah:
            print(f"   {mf[:14]}: '{BARU_NAMA}' sudah ada ({len(sudah)} baris) — dilewati")
            continue

        pola = [r for r in range(3, ws.max_row + 1)
                if str(ws.cell(row=r, column=2).value or "").strip() == CONTOH]
        if not pola:
            print(f"   {mf[:14]}: pola '{CONTOH}' tidak ketemu — DIBATALKAN")
            continue

        nomor = max((ws.cell(row=r, column=1).value or 0)
                    for r in range(3, ws.max_row + 1)
                    if isinstance(ws.cell(row=r, column=1).value, int)) + 1
        tulis = ws.max_row + 1
        for i, r in enumerate(pola):
            toko = ws.cell(row=r, column=3).value
            kat = ws.cell(row=r, column=4).value
            warna = ws.cell(row=r, column=5).value
            sku_lama = str(ws.cell(row=r, column=9).value or "")
            sku = sku_lama.replace(f"-{KODE_CONTOH}-", f"-{BARU_KODE}-", 1)
            baris = [nomor, BARU_NAMA, toko, kat, warna, BARU_GEN, BARU_THN,
                     f"{BARU_NAMA}-{toko}-{kat}-{warna}-{BARU_GEN}", sku]
            if APPLY:
                for c, v in enumerate(baris, start=1):
                    ws.cell(row=tulis + i, column=c, value=v)
            hasil.append((str(toko), str(kat), str(warna), sku))
        if APPLY:
            wb.save(mf)
        print(f"   {mf[:14]}: {len(pola)} baris '{BARU_NAMA}' ditulis mulai baris {tulis}")

    if hasil:
        n = len(hasil) // len(MASTERS) if len(MASTERS) > 1 else len(hasil)
        satu = hasil[:n] if n else hasil
        print(f"\n=== DAFTAR SKU {BARU_NAMA} ({BARU_GEN}, {BARU_THN}) ===")
        for kat in ("Exclusive", "Premium", "Reguler", "Strip", "Transparan"):
            baris = [h for h in satu if h[1] == kat]
            if not baris:
                continue
            print(f"\n  --- {kat} ---")
            seen = set()
            for toko, k, warna, sku in baris:
                if sku in seen:
                    continue
                seen.add(sku)
                print(f"     {warna:16} {sku}")


if __name__ == "__main__":
    main()
