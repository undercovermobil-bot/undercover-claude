# -*- coding: utf-8 -*-
"""
Peta 100 SKU top-100 -> daftar produk (nama mobil) yang memakai tiap SKU, untuk tim desain.
Dibuat 2026-10-12. Sumber: RANKING_TOP_100_PER_SKU.xlsx (sheet 'Top 100 per SKU' dan
'Daftar Mobil Listing UA'). Aturan label sama dgn build_docx_top100_produksi.js:
Rocky dipisah (2019+ vs F70 lama), baris 'Daihatsu Gran Max (listing gabungan)' dibuang
(SP/UA punya listing Minibus & Pick Up sendiri), Datsun Go / Avega (Sedan) dirapikan.

Pemakaian: python3 build_pemetaan_sku_produk.py <RANKING_TOP_100_PER_SKU.xlsx> <keluaran.xlsx>
"""
import sys, warnings
from collections import OrderedDict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
warnings.filterwarnings('ignore')

src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src, data_only=True)

top = {}
ws = wb['Top 100 per SKU']
for r in range(5, ws.max_row + 1):
    v = ws.cell(r, 1).value
    if str(v or '').strip().isdigit() and int(v) <= 100:
        top[int(v)] = dict(rank=int(v), nama=ws.cell(r, 2).value, sku=ws.cell(r, 3).value,
                           unit=ws.cell(r, 4).value)
assert sorted(top) == list(range(1, 101)), 'harus tepat 100 SKU'

RENAME = {'Datsun GO': 'Datsun Go', 'Hyundai Avega': 'Hyundai Avega (Sedan)'}
NOTE_NAMA = {
    ('Daihatsu Rocky', 'DHT-FRZ / TYT-RZE'): None,   # dipecah di bawah
}
produk = OrderedDict((k, []) for k in top)           # rank -> [(nama, catatan)]
wd = wb['Daftar Mobil Listing UA']
for r in range(5, wd.max_row + 1):
    if wd.cell(r, 5).value != 'Dipertahankan':
        continue
    nm, kode, rank = wd.cell(r, 2).value, wd.cell(r, 3).value, int(wd.cell(r, 4).value)
    if nm == 'Daihatsu Gran Max':                    # listing gabungan -> tidak didesain
        continue
    if nm == 'Daihatsu Rocky':                       # satu nama, dua cover berbeda
        produk[15].append(('Daihatsu Rocky (2019 ke atas)', 'Memakai cover Toyota Raize'))
        produk[33].append(('Daihatsu Rocky (lama, F70/F300)', 'Rocky lama memakai cover Feroza, BUKAN cover Raize'))
        continue
    produk[rank].append((RENAME.get(nm, nm), ''))

CATATAN_SKU = {
    35: 'Listing "Toyota Hilux" berisi 2 tipe bodi: Hilux (TYT-HLX) dan Hilux Rangga (TYT-HLR).',
    50: 'Listing "Toyota HiAce" berisi 2 tipe bodi: Commuter (TYT-HAC) dan Premio/Long (TYT-HAL).',
    95: 'Hyundai Avega Sedan. Avega Hatchback produk lain dan tidak masuk 100 SKU.',
    98: 'Listing "Suzuki Vitara" berisi 3 kode: Grand Vitara (SZK-GVT), Vitara generasi 4 (SZK-GVH), e Vitara (SZK-EVT).',
    26: 'Luxio dan Gran Max Minibus memakai cover yang sama. Gran Max Pick Up beda cover (No. 28).',
    28: 'Gran Max Pick Up beda cover dari Gran Max Minibus (No. 26).',
}
kode_tampil = {r: t['sku'] for r, t in top.items()}
for r in (35, 50):
    for k, v in ((r, None),):
        pass
# kode ganda dari Daftar Mobil
for rr in range(5, wd.max_row + 1):
    if wd.cell(rr, 5).value == 'Dipertahankan':
        rk, kd = int(wd.cell(rr, 4).value), wd.cell(rr, 3).value
        if rk in (35, 50) and ' / ' in str(kd):
            kode_tampil[rk] = kd
kode_tampil[98] = 'SZK-GVT / SZK-GVH / SZK-EVT'

# ---------- tulis workbook ----------
HDR = PatternFill('solid', fgColor='FFC000'); HIJAU = PatternFill('solid', fgColor='E2F0D9')
tebal = Font(name='Arial', size=10, bold=True); biasa = Font(name='Arial', size=10)
tipis = Side(style='thin', color='BFBFBF'); kotak = Border(left=tipis, right=tipis, top=tipis, bottom=tipis)
wrap = Alignment(wrap_text=True, vertical='top')

def kepala(ws, kolom, lebar):
    for i, (h, w) in enumerate(zip(kolom, lebar), 1):
        c = ws.cell(1, i, h); c.font = tebal; c.fill = HDR; c.border = kotak
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'; ws.row_dimensions[1].height = 32

wo = openpyxl.Workbook()
w1 = wo.active; w1.title = 'Per SKU'
kepala(w1, ['No (Peringkat SKU)', 'Kode SKU', 'Jumlah Produk', 'Daftar Produk yang Memakai Cover Ini', 'Catatan'],
       [11, 28, 9, 58, 62])
for i, rk in enumerate(sorted(produk), 2):
    L = produk[rk]
    isi = [rk, kode_tampil[rk], len(L), '\n'.join(n for n, _ in L), CATATAN_SKU.get(rk, '')]
    for c, v in enumerate(isi, 1):
        cell = w1.cell(i, c, v); cell.font = biasa; cell.border = kotak; cell.alignment = wrap
    if len(L) > 1:
        for c in range(1, 6):
            w1.cell(i, c).fill = HIJAU
    w1.row_dimensions[i].height = max(18, 14 * max(len(L), 1 + len(CATATAN_SKU.get(rk, '')) // 70))
w1.auto_filter.ref = f'A1:E{w1.max_row}'

w2 = wo.create_sheet('Per Produk')
kepala(w2, ['No', 'Peringkat SKU', 'Kode SKU', 'Nama Produk (Cover Mobil ...)', 'Satu Cover Dengan', 'Catatan', 'Status Desain'],
       [6, 11, 28, 36, 46, 52, 16])
n = 0
for rk in sorted(produk):
    L = produk[rk]
    for nm, cat in L:
        n += 1
        kembar = ', '.join(x for x, _ in L if x != nm)
        gabung = [CATATAN_SKU.get(rk, ''), cat]
        isi = [n, rk, kode_tampil[rk], nm, kembar, ' '.join(g for g in gabung if g), '']
        for c, v in enumerate(isi, 1):
            cell = w2.cell(n + 1, c, v); cell.font = biasa; cell.border = kotak; cell.alignment = wrap
        if kembar:
            w2.cell(n + 1, 5).fill = HIJAU
w2.auto_filter.ref = f'A1:G{w2.max_row}'
N_PRODUK = n

w3 = wo.create_sheet('Keterangan')
baris = [
    'Peta 100 SKU terlaris -> produk (nama mobil) yang harus didesain',
    '',
    f'Sumber: RANKING_TOP_100_PER_SKU.xlsx (penjualan 1 Apr - 16 Sep 2026, 4 toko gabungan).',
    f'Jumlah SKU (cover fisik): 100. Jumlah produk (nama mobil) yang didesain: {N_PRODUK}.',
    'Satu SKU = satu cover fisik. Mobil kembar (mis. Avanza/Xenia/Veloz) memakai cover yang sama, tapi tiap nama mobil tetap produk sendiri di marketplace.',
    'Baris hijau = SKU yang dipakai lebih dari satu nama mobil.',
    'Daihatsu Rocky ada dua cover: Rocky 2019+ (cover Raize, No. 15) dan Rocky lama F70/F300 (cover Feroza, No. 33).',
    'Listing gabungan "Daihatsu Gran Max" tidak dihitung: yang didesain adalah Gran Max Minibus dan Gran Max Pick Up.',
    'Kolom "Status Desain" sengaja dikosongkan supaya tim bisa mengisinya.',
]
for i, t in enumerate(baris, 1):
    c = w3.cell(i, 1, t); c.font = tebal if i == 1 else biasa; c.alignment = Alignment(wrap_text=True, vertical='top')
w3.column_dimensions['A'].width = 120

wo.save(out)
print('SKU:', len(produk), '| produk:', N_PRODUK, '| SKU multi-produk:', sum(1 for v in produk.values() if len(v) > 1))
print('SKU tanpa produk:', [r for r, v in produk.items() if not v])
