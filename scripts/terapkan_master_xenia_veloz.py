# -*- coding: utf-8 -*-
"""
Terapkan pemetaan Xenia/Veloz->Avanza ke MASTER, HANYA kolom SKU (kolom 9).
Nama Produk/Kategori/Warna/Generasi/Rentang Tahun/Nama Produk Bigseller TIDAK disentuh
(produk tetap dijual sbg Xenia/Veloz, cuma kode SKU-nya konsolidasi ke Avanza).
Output: FILE BARU, MASTER asli tidak disentuh.
"""
import openpyxl, json
from openpyxl.styles import PatternFill

SRC = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/6d869641-SKU_Price_Tracking_Cover_Mobil.xlsx'
OUT = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/MASTER_Xenia_Veloz_ke_Avanza.xlsx'
JSON_MAP = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/mapping_xenia_veloz.json'

ORANGE = PatternFill('solid', fgColor='FFC000')  # konvensi proyek: oranye = migrasi/konsolidasi

data = json.load(open(JSON_MAP))

wb = openpyxl.load_workbook(SRC, data_only=False)
wst = wb['Toyota']
wsd = wb['Daihatsu']

C_SKU = 9
n = 0
for r, key, lama, baru in data['xenia_rows']:
    cell = wsd.cell(row=r, column=C_SKU)
    assert cell.value == lama, f'r{r} beda: {cell.value!r} != {lama!r}'
    cell.value = baru
    cell.fill = ORANGE
    n += 1
for r, key, lama, baru in data['veloz_rows']:
    cell = wst.cell(row=r, column=C_SKU)
    assert cell.value == lama, f'r{r} beda: {cell.value!r} != {lama!r}'
    cell.value = baru
    cell.fill = ORANGE
    n += 1

wb.save(OUT)
print(f'-> {OUT}')
print(f'   {n} sel SKU diubah ({len(data["xenia_rows"])} Xenia + {len(data["veloz_rows"])} Veloz)')

# verifikasi
import zipfile
print('zip rusak?', zipfile.ZipFile(OUT).testzip())
wb2 = openpyxl.load_workbook(OUT, data_only=True)
wst2, wsd2 = wb2['Toyota'], wb2['Daihatsu']
chk = 0
for r, key, lama, baru in data['xenia_rows'][:3] + data['veloz_rows'][:3]:
    ws2 = wsd2 if (r, key, lama, baru) in data['xenia_rows'] else wst2
for r, key, lama, baru in data['xenia_rows']:
    if wsd2.cell(row=r, column=C_SKU).value != baru:
        chk += 1
for r, key, lama, baru in data['veloz_rows']:
    if wst2.cell(row=r, column=C_SKU).value != baru:
        chk += 1
print(f'   verifikasi pasca-save: {chk} baris TIDAK sesuai (harus 0)')

# pastikan nama produk / kategori / warna / generasi TIDAK berubah
beda_lain = 0
for r, key, lama, baru in data['xenia_rows']:
    if wsd2.cell(row=r, column=2).value != 'Daihatsu Xenia':
        beda_lain += 1
for r, key, lama, baru in data['veloz_rows']:
    if wst2.cell(row=r, column=2).value != 'Toyota Veloz':
        beda_lain += 1
print(f'   Nama Produk masih Xenia/Veloz (bukan ikut jadi Avanza): {beda_lain} yg salah (harus 0)')
