# -*- coding: utf-8 -*-
"""
Buat SATU file SIAP UPLOAD ke Shopee yang HANYA berisi baris yang SKU-nya berubah
(Xenia/Veloz/Sigra/Terios/Rocky/Vellfire/Agya), digabung dari semua file sumber,
tapi struktur kolom & header Shopee (baris 1-6 boilerplate, Kode Produk/Kode Variasi
utk pencocokan) TETAP UTUH -- supaya file ini bisa langsung diupload, bukan cuma
laporan review.

Metadata baris 2 (search_condition dkk) sama di semua file sumber (boilerplate
export Shopee, bukan spesifik per-file) -- aman digabung jadi 1 sheet, header
diambil dari file pertama yg punya baris berubah.

Alur: repair_xlsx.py -> terapkan_listing_final.py (transform SKU) -> script ini
(saring baris yg berubah saja dari tiap file, gabung jadi 1 output).
"""
import sys, os, glob, copy
import openpyxl

FIX_DIR = sys.argv[1] if len(sys.argv) > 1 else 'ua_shopee_final/fix'
HASIL_DIR = sys.argv[2] if len(sys.argv) > 2 else 'ua_shopee_final/hasil'
OUT_PATH = sys.argv[3] if len(sys.argv) > 3 else 'ua_shopee_final/siap_upload/SIAP_UPLOAD_GABUNGAN.xlsx'

os.makedirs(os.path.dirname(OUT_PATH) or '.', exist_ok=True)

# peta nama file "fix" (sebelum transform) -> nama file "hasil" (sesudah transform)
pasangan = {}
for p in sorted(glob.glob(os.path.join(HASIL_DIR, '*.xlsx'))):
    nm = os.path.basename(p)
    cocok = None
    for pf in glob.glob(os.path.join(FIX_DIR, '*.xlsx')):
        pnm = os.path.basename(pf)
        digit_hasil = ''.join(c for c in nm if c.isdigit())
        digit_fix = ''.join(c for c in pnm if c.isdigit())
        if digit_hasil and digit_hasil == digit_fix:
            cocok = pf
            break
    if cocok:
        pasangan[cocok] = p


def salin_baris(ws_src, r_src, ws_dst, r_dst):
    for c in range(1, ws_src.max_column + 1):
        sel = ws_src.cell(row=r_src, column=c)
        dsel = ws_dst.cell(row=r_dst, column=c, value=sel.value)
        dsel.fill = copy.copy(sel.fill)
        dsel.number_format = sel.number_format


wb_out = None
ws_out = None
r_out = 7
total = 0
per_file = []

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

    if wb_out is None:
        # file pertama yg punya baris berubah -> jadi dasar output (header 1-6 dibawa apa adanya)
        wb_out = wb_baru
        ws_out = ws_baru
        semua_baris = set(range(7, ws_out.max_row + 1))
        dihapus = sorted(semua_baris - set(baris_berubah), reverse=True)
        for r in dihapus:
            ws_out.delete_rows(r, 1)
        r_out = 7 + len(baris_berubah)
    else:
        for r in baris_berubah:
            salin_baris(ws_baru, r, ws_out, r_out)
            r_out += 1

    total += len(baris_berubah)
    per_file.append((os.path.basename(f_baru), len(baris_berubah)))

if wb_out is None:
    print('Tidak ada baris berubah di file manapun.')
    sys.exit(0)

wb_out.save(OUT_PATH)

for nama, n in per_file:
    print(f'  {nama:20s} -> {n} baris')
print(f'\nTotal baris siap-upload (digabung 1 file): {total}')
print(f'Output: {OUT_PATH}')
