# -*- coding: utf-8 -*-
"""Laporan gagal upload campaign Shopee ("Harga Diskon Sebelum Pajak <= X") ->
file upload ulang untuk varian yang gagal saja.

Harga Diskon = X - MARGIN (MARGIN=1 rupiah: margin 1 rupiah terbukti lolos
pada upload 2026-10-13, 6.718 varian; harga == X persis belum teruji).
Template dari file template campaign (preview_submit_tmp_id), isi kolom 1-15
dari baris laporan (kolom 16 'Alasan Gagal' dibuang).

Pemakaian: python3 ulang_gagal_campaign_shopee.py <template.xlsx> <out.xlsx> <laporan_gagal.xlsx...>
(file input sudah lewat repair_xlsx.py; maks 5.000 variasi per file upload)
"""
import sys, re, openpyxl
from openpyxl.styles import PatternFill

MARGIN = 1
ORANGE = PatternFill('solid', fgColor='FFC000')
template, out, *laporan = sys.argv[1:]
wb = openpyxl.load_workbook(template)
ws = wb.active
r_out, lain, sudah = 4, 0, set()
for p in laporan:
    src = openpyxl.load_workbook(p).active
    for r in range(4, src.max_row + 1):
        vid = src.cell(r, 4).value
        if not vid or str(vid) in sudah:
            continue
        m = re.search(r'<=\s*(\d+)', str(src.cell(r, 16).value))
        if not m:
            lain += 1
            continue
        sudah.add(str(vid))
        for c in range(1, 16):
            ws.cell(r_out, c).value = src.cell(r, c).value
        sel = ws.cell(r_out, 11)
        sel.value = int(m.group(1)) - MARGIN
        sel.fill = ORANGE
        r_out += 1
wb.save(out)
n = r_out - 4
print(f'{n} varian ditulis; alasan lain (dilewati): {lain}')
if n > 5000:
    print('PERINGATAN: > 5.000 variasi, pecah file sebelum upload')
