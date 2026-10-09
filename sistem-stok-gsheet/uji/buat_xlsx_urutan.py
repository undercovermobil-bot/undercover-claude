"""Buat file xlsx untuk diimpor ke Google Sheet (sheet "Urutan UC", "Urutan STP", "Tidak masuk") dari uji/daftar-urutan.js.

Pakai (dari folder sistem-stok-gsheet):
  node -e "console.log(JSON.stringify(require('./uji/daftar-urutan')))" > /tmp/daftar.json
  python3 -I uji/buat_xlsx_urutan.py /tmp/daftar.json "Urutan Stok UC STP.xlsx"

Kolom yang dibaca script Kode.gs (lewat judul baris 1): Nama Produk, Kode SKU, Baris lama, Nama di sheet lama, Harga dari baris.
Kolom lain hanya informasi. Sheet "Tidak masuk" tidak dipakai script (daftar produk stok 0 yang dibuang) dan tidak dibuat di sini
karena datanya ada di analisis sesi; tambahkan manual kalau perlu.
"""
import json, sys
import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter as L

d = json.load(open(sys.argv[1], encoding='utf-8'))
HDR = ['No', 'Nama Produk', 'Kode SKU', 'Baris lama', 'Nama di sheet lama', 'Harga dari baris', 'Stok sekarang', 'Bagian', 'Peringkat', 'Status', 'Catatan']
LEBAR = [5, 40, 40, 10, 34, 10, 9, 8, 9, 10, 80]
WARNA = {'hijau': 'B6D7A8', 'baru': 'CFE2F3', 'cek': 'FFE599', 'sisa': 'EFEFEF'}

wb = openpyxl.Workbook()
wb.remove(wb.active)
for kode in ('UC', 'STP'):
    ws = wb.create_sheet('Urutan ' + kode)
    ws.append(HDR)
    for i, e in enumerate(d[kode], 1):
        ws.append([i, e['nama'], e['sku'] or None, ', '.join(str(r) for r in e['baris']) or None, ' | '.join(e['namaLama']) or None,
                   e['harga'] if e['harga'] != '' else None, e['stok'] if e['stok'] != '' else None, e['bagian'],
                   e['peringkat'] if e['peringkat'] != '' else None, e['status'], e['catatan'] or None])
        w = WARNA['hijau'] if e['bagian'] == '1' else WARNA['baru'] if e['status'] == 'BARU' else WARNA['cek'] if e['status'] == 'CEK' else WARNA['sisa'] if e['bagian'] == '3' else None
        if w:
            for c in range(1, len(HDR) + 1):
                ws.cell(i + 1, c).fill = PatternFill('solid', fgColor=w)
    for c, w in enumerate(LEBAR, 1):
        ws.column_dimensions[L(c)].width = w
    ws.freeze_panes = 'C2'
    for c in range(1, len(HDR) + 1):
        ws.cell(1, c).font = Font(bold=True)
wb.save(sys.argv[2])
print({k: len(d[k]) for k in ('UC', 'STP')})
