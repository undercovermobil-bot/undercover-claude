# -*- coding: utf-8 -*-
"""Terapkan mapping_5pasangan.json ke MASTER (hanya kolom SKU). File BARU, master asli tidak disentuh."""
import openpyxl, json
from openpyxl.styles import PatternFill

SRC = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/6d869641-SKU_Price_Tracking_Cover_Mobil.xlsx'
OUT = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/MASTER_5pasangan.xlsx'
JSON_MAP = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/mapping_5pasangan.json'

ORANGE = PatternFill('solid', fgColor='FFC000')
C_SKU = 9

data = json.load(open(JSON_MAP))
wb = openpyxl.load_workbook(SRC, data_only=False)

n = 0
for label, rows in data.items():
    for sheet, r, key, lama, baru in rows:
        cell = wb[sheet].cell(row=r, column=C_SKU)
        assert cell.value == lama, f'{label} r{r} beda: {cell.value!r} != {lama!r}'
        cell.value = baru
        cell.fill = ORANGE
        n += 1

wb.save(OUT)
print(f'-> {OUT}')
print(f'   {n} sel SKU diubah')

# verifikasi
import zipfile
print('zip rusak?', zipfile.ZipFile(OUT).testzip())
wb2 = openpyxl.load_workbook(OUT, data_only=True)
chk = 0
for label, rows in data.items():
    for sheet, r, key, lama, baru in rows:
        if wb2[sheet].cell(row=r, column=C_SKU).value != baru:
            chk += 1
print(f'   verifikasi: {chk} baris TIDAK sesuai (harus 0)')

# pastikan Nama Produk tidak ikut berubah -- cocokkan via kata kunci di label,
# tahan terhadap perubahan teks label (mis. tambahan suffix "[FIX: ...]")
KUNCI_NAMA = [
    ('Sigra', 'Daihatsu Sigra'), ('Rocky', 'Daihatsu Rocky'), ('Vellfire', 'Toyota Vellfire'),
    ('Agya', 'Toyota Agya'), ('Terios', 'Daihatsu Terios'),
]


def nama_asli(label):
    for kunci, nama in KUNCI_NAMA:
        if kunci in label:
            return nama
    raise KeyError(f'tidak ada kunci nama utk label {label!r}')


beda_nama = 0
for label, rows in data.items():
    for sheet, r, key, lama, baru in rows:
        if wb2[sheet].cell(row=r, column=2).value != nama_asli(label):
            beda_nama += 1
print(f'   Nama Produk berubah tak sengaja: {beda_nama} (harus 0)')

print('\n=== ringkasan per pasangan ===')
for label, rows in data.items():
    print(f'  {label:26s} : {len(rows)} baris')
