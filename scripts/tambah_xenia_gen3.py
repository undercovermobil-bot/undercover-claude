# -*- coding: utf-8 -*-
"""
Tambah 66 baris Xenia "Gen 3 (2021-2026)" ke master, meniru struktur Avanza Gen 3
persis (toko/kategori/warna sama), SKU-nya LANGSUNG memakai SKU Avanza Gen 3 yg sama
(konsolidasi, bukan kode baru) -- sesuai instruksi user: "xenia gen 3 ikut avanza g3".

Dijalankan SETELAH preview_xenia_veloz.py / terapkan_master_xenia_veloz.py yg menangani
Gen 1 & Gen 2 Xenia + Veloz. Baris Gen 3 ini genuinely BARU (Xenia sebelumnya cuma py
2 generasi di master), jadi ditambahkan, bukan menimpa baris yg sudah ada.
"""
import openpyxl
from openpyxl.styles import PatternFill
from copy import copy

SRC = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/MASTER_Xenia_Veloz_ke_Avanza.xlsx'
OUT = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/MASTER_Xenia_Veloz_ke_Avanza_v2.xlsx'
ORANGE = PatternFill('solid', fgColor='FFC000')

wb = openpyxl.load_workbook(SRC, data_only=False)
wst = wb['Toyota']
wsd = wb['Daihatsu']

C_NAMA, C_TOKO, C_KAT, C_WARNA, C_GEN, C_THN, C_BS, C_SKU = 2, 3, 4, 5, 6, 7, 8, 9

# ---------- ambil baris Avanza Gen 3 sbg pola (66 baris) ----------
pola = []
for r in range(3, wst.max_row + 1):
    if wst.cell(row=r, column=C_NAMA).value != 'Toyota Avanza':
        continue
    if str(wst.cell(row=r, column=C_GEN).value or '').strip() != 'Gen 3':
        continue
    pola.append({
        'toko': wst.cell(row=r, column=C_TOKO).value,
        'kat': wst.cell(row=r, column=C_KAT).value,
        'warna': wst.cell(row=r, column=C_WARNA).value,
        'gen': wst.cell(row=r, column=C_GEN).value,
        'thn': wst.cell(row=r, column=C_THN).value,
        'sku': wst.cell(row=r, column=C_SKU).value,
    })
print(f'pola Avanza Gen 3: {len(pola)} baris')
assert len(pola) == 66, f'harusnya 66, dapat {len(pola)}'

# ---------- cek Xenia belum punya baris Gen 3 (hindari duplikat kalau dijalankan 2x) ----------
sudah_ada = any(
    wsd.cell(row=r, column=C_NAMA).value == 'Daihatsu Xenia'
    and str(wsd.cell(row=r, column=C_GEN).value or '').strip() == 'Gen 3'
    for r in range(3, wsd.max_row + 1)
)
if sudah_ada:
    print('Xenia Gen 3 SUDAH ADA di master ini -- tidak ditambah lagi (hindari dobel).')
else:
    mulai = max(wsd.max_row + 1, 3)
    # style acuan: baris Xenia yg sudah ada (biar format sel konsisten)
    baris_acuan = 3
    for i, p in enumerate(pola):
        r = mulai + i
        nilai = ['', 'Daihatsu Xenia', p['toko'], p['kat'], p['warna'], p['gen'], p['thn'], '', p['sku']]
        for col, v in enumerate(nilai, 1):
            if col == 1:
                continue
            cell = wsd.cell(row=r, column=col, value=v)
            ref = wsd.cell(row=baris_acuan, column=col)
            cell.font = copy(ref.font)
            cell.border = copy(ref.border)
            cell.alignment = copy(ref.alignment)
            cell.number_format = ref.number_format
        wsd.cell(row=r, column=C_SKU).fill = ORANGE  # tandai: hasil konsolidasi
    print(f'-> {len(pola)} baris Xenia Gen 3 ditambahkan (baris {mulai}-{mulai+len(pola)-1})')

wb.save(OUT)
print(f'\nsaved -> {OUT}')

# ---------- verifikasi ----------
import zipfile
print('zip rusak?', zipfile.ZipFile(OUT).testzip())
wb2 = openpyxl.load_workbook(OUT, data_only=True)
wsd2 = wb2['Daihatsu']
xg3 = [(r, wsd2.cell(row=r, column=C_TOKO).value, wsd2.cell(row=r, column=C_KAT).value,
        wsd2.cell(row=r, column=C_WARNA).value, wsd2.cell(row=r, column=C_SKU).value)
       for r in range(3, wsd2.max_row + 1)
       if wsd2.cell(row=r, column=C_NAMA).value == 'Daihatsu Xenia'
       and str(wsd2.cell(row=r, column=C_GEN).value or '').strip() == 'Gen 3']
print(f'Xenia Gen 3 di file hasil: {len(xg3)} baris')
for x in xg3[:5]:
    print('  ', x)
# pastikan semua SKU-nya persis SKU Avanza Gen 3 (bukan dikarang)
sku_avz = {p['sku'] for p in pola}
sku_xen = {x[4] for x in xg3}
print('semua SKU Xenia Gen3 == SKU Avanza Gen3?', sku_xen == sku_avz)
