# -*- coding: utf-8 -*-
"""
Pemetaan SKU Xenia & Veloz -> Avanza, di level MASTER.
- Xenia Gen 1 (2003-2011) & Gen 2 (2011-2021) -> pakai kode SKU Avanza "Gen 1 & 2" (G1)
- Veloz Gen 1 (2011-2021) & Gen 2 (2021-2026) -> pakai kode SKU Avanza "Gen 3" (G3)
Dicocokkan lewat (Toko, Kategori Produk, Warna) -> ambil SKU Avanza asli persis,
BUKAN direkonstruksi manual, supaya tidak ada resiko salah format.
"""
import openpyxl, collections
from openpyxl.styles import PatternFill

SRC = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/6d869641-SKU_Price_Tracking_Cover_Mobil.xlsx'
OUT = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/MASTER_preview_Xenia_Veloz_ke_Avanza.xlsx'

wb = openpyxl.load_workbook(SRC, data_only=False)
wst = wb['Toyota']
wsd = wb['Daihatsu']

C_NAMA, C_TOKO, C_KAT, C_WARNA, C_GEN, C_THN, C_BS, C_SKU = 2, 3, 4, 5, 6, 7, 8, 9

# ---------- 1. bangun lookup SKU Avanza ----------
avz_g1 = {}   # (toko, kat, warna) -> sku   (Gen "1 & 2")
avz_g3 = {}   # (toko, kat, warna) -> sku   (Gen "3")
for r in range(3, wst.max_row + 1):
    nm = wst.cell(row=r, column=C_NAMA).value
    if nm != 'Toyota Avanza':
        continue
    gen = str(wst.cell(row=r, column=C_GEN).value or '').strip()
    key = (wst.cell(row=r, column=C_TOKO).value, wst.cell(row=r, column=C_KAT).value,
           wst.cell(row=r, column=C_WARNA).value)
    sku = wst.cell(row=r, column=C_SKU).value
    if gen == 'Gen 1 & 2':
        avz_g1[key] = sku
    elif gen == 'Gen 3':
        avz_g3[key] = sku

print(f'lookup Avanza G1 (Gen 1&2): {len(avz_g1)} kombinasi')
print(f'lookup Avanza G3 (Gen 3)  : {len(avz_g3)} kombinasi')

# ---------- 2. terapkan ke Xenia (Daihatsu sheet) ----------
xenia_rows = []
xenia_gagal = []
for r in range(3, wsd.max_row + 1):
    nm = wsd.cell(row=r, column=C_NAMA).value
    if nm != 'Daihatsu Xenia':
        continue
    key = (wsd.cell(row=r, column=C_TOKO).value, wsd.cell(row=r, column=C_KAT).value,
           wsd.cell(row=r, column=C_WARNA).value)
    sku_lama = wsd.cell(row=r, column=C_SKU).value
    sku_baru = avz_g1.get(key)
    if sku_baru is None:
        xenia_gagal.append((r, key, sku_lama))
    else:
        xenia_rows.append((r, key, sku_lama, sku_baru))

# ---------- 3. terapkan ke Veloz (Toyota sheet) ----------
veloz_rows = []
veloz_gagal = []
for r in range(3, wst.max_row + 1):
    nm = wst.cell(row=r, column=C_NAMA).value
    if nm != 'Toyota Veloz':
        continue
    key = (wst.cell(row=r, column=C_TOKO).value, wst.cell(row=r, column=C_KAT).value,
           wst.cell(row=r, column=C_WARNA).value)
    sku_lama = wst.cell(row=r, column=C_SKU).value
    sku_baru = avz_g3.get(key)
    if sku_baru is None:
        veloz_gagal.append((r, key, sku_lama))
    else:
        veloz_rows.append((r, key, sku_lama, sku_baru))

print(f'\nXenia: {len(xenia_rows)} baris cocok, {len(xenia_gagal)} GAGAL cocok')
print(f'Veloz: {len(veloz_rows)} baris cocok, {len(veloz_gagal)} GAGAL cocok')
for r, k, s in xenia_gagal[:10]:
    print('  XENIA GAGAL r', r, k, s)
for r, k, s in veloz_gagal[:10]:
    print('  VELOZ GAGAL r', r, k, s)

# ---------- 4. cek berapa yg BENAR2 beda dr sebelumnya (bukan kebetulan sama) ----------
xenia_beda = [x for x in xenia_rows if x[2] != x[3]]
veloz_beda = [x for x in veloz_rows if x[2] != x[3]]
print(f'\nXenia SKU benar2 berubah: {len(xenia_beda)} / {len(xenia_rows)}')
print(f'Veloz SKU benar2 berubah: {len(veloz_beda)} / {len(veloz_rows)}')

print('\ncontoh Xenia (5 baris pertama):')
for r, k, lama, baru in xenia_rows[:5]:
    print(f'   {k} : {lama}  ->  {baru}')
print('\ncontoh Veloz (5 baris pertama):')
for r, k, lama, baru in veloz_rows[:5]:
    print(f'   {k} : {lama}  ->  {baru}')

import json
json.dump({
    'xenia_rows': xenia_rows, 'veloz_rows': veloz_rows,
    'xenia_gagal': xenia_gagal, 'veloz_gagal': veloz_gagal,
}, open('/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/mapping_xenia_veloz.json', 'w'), ensure_ascii=False)
print('\n-> mapping disimpan ke mapping_xenia_veloz.json')
