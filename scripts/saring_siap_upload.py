# -*- coding: utf-8 -*-
"""
Buat file SIAP UPLOAD ke Shopee yang HANYA berisi baris yang SKU-nya berubah
(Xenia/Veloz/Sigra/Terios/Rocky/Vellfire/Agya), tapi struktur kolom & header
Shopee (baris 1-6 boilerplate, Kode Produk/Kode Variasi utk pencocokan) TETAP UTUH
-- supaya file ini bisa langsung diupload, bukan cuma laporan review.

Alur: repair_xlsx.py -> terapkan_listing_final.py (transform SKU) -> script ini
(saring baris yg berubah saja, simpan header asli).
"""
import sys, os, glob
import openpyxl

FIX_DIR = sys.argv[1] if len(sys.argv) > 1 else 'ua_shopee_final/fix'
HASIL_DIR = sys.argv[2] if len(sys.argv) > 2 else 'ua_shopee_final/hasil'
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else 'ua_shopee_final/siap_upload'

os.makedirs(OUT_DIR, exist_ok=True)

# peta nama file "fix" (sebelum transform) -> nama file "hasil" (sesudah transform)
pasangan = {}
for p in glob.glob(os.path.join(HASIL_DIR, '*.xlsx')):
    nm = os.path.basename(p)
    cocok = None
    for pf in glob.glob(os.path.join(FIX_DIR, '*.xlsx')):
        pnm = os.path.basename(pf)
        # cocokkan lewat angka di nama file (1/2/3/4/5)
        digit_hasil = ''.join(c for c in nm if c.isdigit())
        digit_fix = ''.join(c for c in pnm if c.isdigit())
        if digit_hasil and digit_hasil == digit_fix:
            cocok = pf
            break
    if cocok:
        pasangan[cocok] = p

total = 0
for f_lama, f_baru in pasangan.items():
    wb_lama = openpyxl.load_workbook(f_lama, data_only=True)
    ws_lama = wb_lama[wb_lama.sheetnames[0]]
    wb_baru = openpyxl.load_workbook(f_baru, data_only=False)
    ws_baru = wb_baru[wb_baru.sheetnames[0]]

    baris_berubah = []
    for r in range(7, ws_baru.max_row + 1):
        sku_lama = ws_lama.cell(row=r, column=6).value
        sku_baru = ws_baru.cell(row=r, column=6).value
        if sku_baru and sku_baru != sku_lama:
            baris_berubah.append(r)

    if not baris_berubah:
        continue

    # hapus baris yg TIDAK berubah (dari bawah ke atas supaya index tidak geser)
    semua_baris = set(range(7, ws_baru.max_row + 1))
    dihapus = sorted(semua_baris - set(baris_berubah), reverse=True)
    for r in dihapus:
        ws_baru.delete_rows(r, 1)

    nama_out = 'SIAP_UPLOAD_' + os.path.basename(f_baru)
    out_path = os.path.join(OUT_DIR, nama_out)
    wb_baru.save(out_path)
    total += len(baris_berubah)
    print(f'  {os.path.basename(f_baru):20s} -> {nama_out:35s} ({len(baris_berubah)} baris, header Shopee utuh)')

print(f'\nTotal baris siap-upload: {total}')
