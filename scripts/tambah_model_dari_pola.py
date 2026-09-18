"""Tambah model baru ke master dengan MENYALIN POLA model lain di sheet yang sama.

Dipakai untuk model yang listing-nya sudah tayang tapi belum ada di master, sehingga
SKU-nya kosong. Menyalin pola jauh lebih aman daripada menyusun ulang daftar
warna/kategori dari nol: struktur tiap merek BEDA (mis. Wuling tidak punya Premium
& Exclusive di SP/OP tapi punya warna Orange; Ferrari punya 4 kategori penuh di
semua toko), dan menyusun manual gampang meleset.

Selalu dibuat LENGKAP mengikuti pola sumber, bukan cuma kategori yang diminta —
entri master yang dibuat sebagian terbukti bikin masalah belakangan (kasus
BYD Denza D9 yang cuma punya Premium, 2026-07-30).

Cara pakai:
    python3 tambah_model_dari_pola.py <sheet> <model_sumber> <nama_baru> <kode_baru> <tahun> [--apply]
Contoh:
    python3 tambah_model_dari_pola.py Ferrari "Ferrari 488 Pista Spider" \
        "Ferrari 488 Spider" 488S "2015-2019" --apply
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]


def tambah(sheet, sumber, nama_baru, kode_baru, tahun, apply, gen="Gen 1"):
    hasil = []
    for mf in MASTERS:
        wb = load_workbook(mf)
        if sheet not in wb.sheetnames:
            print(f"   {mf[:14]}: sheet '{sheet}' tidak ada — DILEWATI")
            continue
        ws = wb[sheet]

        sudah = [r for r in range(3, ws.max_row + 1)
                 if str(ws.cell(row=r, column=2).value or "").strip().lower() == nama_baru.lower()]
        if sudah:
            print(f"   {mf[:14]}: '{nama_baru}' sudah ada ({len(sudah)} baris) — dilewati")
            continue

        pola = [r for r in range(3, ws.max_row + 1)
                if str(ws.cell(row=r, column=2).value or "").strip() == sumber]
        if not pola:
            print(f"   {mf[:14]}: pola '{sumber}' tidak ketemu — DIBATALKAN")
            continue

        # kode model sumber diambil dari SKU-nya, supaya penggantian tepat sasaran
        kode_sumber = str(ws.cell(row=pola[0], column=9).value or "").split("-")[1]
        nomor = max((ws.cell(row=r, column=1).value or 0)
                    for r in range(3, ws.max_row + 1)
                    if isinstance(ws.cell(row=r, column=1).value, int)) + 1
        tulis = ws.max_row + 1
        for i, r in enumerate(pola):
            toko = ws.cell(row=r, column=3).value
            kat = ws.cell(row=r, column=4).value
            warna = ws.cell(row=r, column=5).value
            sku = str(ws.cell(row=r, column=9).value or "").replace(
                f"-{kode_sumber}-", f"-{kode_baru}-", 1)
            baris = [nomor, nama_baru, toko, kat, warna, gen, tahun,
                     f"{nama_baru}-{toko}-{kat}-{warna}-{gen}", sku]
            if apply:
                for c, v in enumerate(baris, start=1):
                    ws.cell(row=tulis + i, column=c, value=v)
            if mf == MASTERS[0]:
                hasil.append((str(toko), str(kat), str(warna), sku))
        if apply:
            wb.save(mf)
        print(f"   {mf[:14]}: {len(pola)} baris '{nama_baru}' (kode {kode_baru}, "
              f"pola dari '{sumber}' kode {kode_sumber})")
    return hasil


def cetak(hasil, judul):
    print(f"\n=== SKU {judul} ===")
    for kat in ("Exclusive", "Premium", "Reguler", "Strip", "Transparan"):
        baris = [h for h in hasil if h[1] == kat]
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
    arg = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    if len(arg) < 5:
        print(__doc__)
        raise SystemExit(1)
    sheet, sumber, nama, kode, tahun = arg[:5]
    print("MODE:", "APPLY (master DITULIS)" if apply else "DRY-RUN")
    h = tambah(sheet, sumber, nama, kode, tahun, apply)
    if h:
        cetak(h, f"{nama} (Gen 1, {tahun})")
