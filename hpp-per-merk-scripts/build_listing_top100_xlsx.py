"""Laporan: produk di listing Shopee (mass_update_basic_info) yg masuk / di luar top-100 SKU.
Jalankan klasifikasi_listing_top100.py dulu. Pemakaian: python3 build_listing_top100_xlsx.py <output.xlsx>"""
import os, sys, pickle
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
S = os.environ.get("KERJA_DIR", ".")
rows = pickle.load(open(f"{S}/klasifikasi_listing.pkl", "rb"))
out = pickle.load(open(f"{S}/ranking_per_sku.pkl", "rb"))['out']
by_key = {g['key']: g for g in out}
# nama produk per SKU (semua mobil kembar) diambil dari workbook ranking yg sudah dibuat
wr = openpyxl.load_workbook(f"{S}/RANKING_TOP100_PER_SKU.xlsx", data_only=True)['Peringkat Lengkap']
nama_sku = {wr.cell(r, 3).value: wr.cell(r, 2).value for r in range(5, wr.max_row + 1) if wr.cell(r, 3).value}

F = 'Arial'
fn, fb = Font(name=F, size=10), Font(name=F, size=10, bold=True)
ft = Font(name=F, size=13, bold=True)
fh = Font(name=F, size=10, bold=True, color='FFFFFF'); hf = PatternFill('solid', fgColor='1F4E78')
fl = Font(name=F, size=10, color='008000')
fill = {'Masuk top-100': PatternFill('solid', fgColor='E2EFDA'), 'Di luar top-100': PatternFill('solid', fgColor='FCE4D6'),
        'Bukan cover mobil': PatternFill('solid', fgColor='EDEDED')}
bd = Border(bottom=Side(style='thin', color='BFBFBF'))

HDR = ['Kode Produk', 'Nama Produk (judul listing)', 'Nama Mobil', 'Tier', 'Status', 'Peringkat SKU',
       'Kode SKU', 'Produk per SKU (semua mobil kembar)', 'Unit Terjual SKU (Apr-Sep)', 'Judul Sudah "Archive"', 'Dasar']
W = [14, 62, 26, 10, 16, 10, 16, 40, 12, 11, 60]

def isi(ws, data, title, note):
    ws['A1'] = title; ws['A1'].font = ft
    ws['A2'] = note; ws['A2'].font = fn
    for i, h in enumerate(HDR, 1):
        c = ws.cell(4, i, h); c.font = fh; c.fill = hf
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    ws.row_dimensions[4].height = 32
    for i, x in enumerate(data):
        r = 5 + i
        keys = x['keys']
        vals = [x['pid'], x['title'], x['nama'], x['tier'], x['status'], x['rank'],
                ' / '.join(keys), ' | '.join(nama_sku.get(k, '') for k in keys if nama_sku.get(k)),
                sum(by_key[k]['qty'] for k in keys if k in by_key) or (0 if x['status'] != 'Bukan cover mobil' else None),
                'Ya' if x['archive'] else '', x['dasar']]
        for j, v in enumerate(vals, 1):
            c = ws.cell(r, j, v); c.font = fn; c.border = bd; c.fill = fill[x['status']]
        ws.cell(r, 1).number_format = '@'
        ws.cell(r, 9).number_format = '#,##0'
    for col, w in zip('ABCDEFGHIJK', W): ws.column_dimensions[col].width = w
    ws.freeze_panes = 'C5'
    ws.auto_filter.ref = f"A4:K{max(5, 4 + len(data))}"
    return 4 + len(data)

wb = openpyxl.Workbook()
rk = wb.active; rk.title = 'Ringkasan'

tier_order = {'Reguler': 0, 'Premium': 1, 'Exclusive': 2}
key_all = lambda x: ({'Masuk top-100': 0, 'Di luar top-100': 1, 'Bukan cover mobil': 2}[x['status']],
                     x['rank'] or 9999, x['nama'].lower(), tier_order.get(x['tier'], 9), x['title'])
semua = sorted(rows, key=key_all)
ws_all = wb.create_sheet('Semua Produk')
last_all = isi(ws_all, semua, 'Semua produk di listing Shopee Undercover + status top-100 SKU',
               'Sumber: mass_update_basic_info_361186752_20260924120444.xlsx (produk aktif). Filter kolom Status untuk memilah.')
for st, nm in [('Masuk top-100', 'Masuk Top-100'), ('Di luar top-100', 'Di Luar Top-100'), ('Bukan cover mobil', 'Bukan Cover Mobil')]:
    isi(wb.create_sheet(nm), [x for x in semua if x['status'] == st], f'Produk: {st}',
        'Salinan dari sheet "Semua Produk" yang sudah difilter.')

# ---- Ringkasan (rumus COUNTIFS ke sheet Semua Produk) ----
rk['A1'] = 'Ringkasan: listing Shopee Undercover vs Top-100 SKU'; rk['A1'].font = ft
rk['A2'] = ('Top-100 SKU dari RANKING_TOP100_PER_SKU.xlsx (penjualan Apr–Sep 2026, 4 toko, per SKU). Satu SKU bisa dipakai beberapa '
            'mobil kembar, jadi 100 SKU = 110 nama mobil. Status berlaku per MOBIL: semua tier (Reguler/Premium/Exclusive) mobil itu ikut statusnya.')
rk['A2'].font = fn; rk['A2'].alignment = Alignment(wrap_text=True, vertical='top'); rk.merge_cells('A2:F2'); rk.row_dimensions[2].height = 45
ST = "'Semua Produk'!$E$5:$E$%d" % last_all
TR = "'Semua Produk'!$D$5:$D$%d" % last_all
rk['A4'] = 'Status'; rk['B4'] = 'Jumlah Produk'; rk['C4'] = 'Reguler'; rk['D4'] = 'Premium'; rk['E4'] = 'Exclusive'
for c in 'ABCDE':
    rk[f'{c}4'].font = fh; rk[f'{c}4'].fill = hf; rk[f'{c}4'].alignment = Alignment(horizontal='center')
for i, st in enumerate(['Masuk top-100', 'Di luar top-100', 'Bukan cover mobil']):
    r = 5 + i
    rk.cell(r, 1, st).font = fb
    rk.cell(r, 1).fill = fill[st]
    rk.cell(r, 2, f'=COUNTIFS({ST},A{r})').font = fl
    for j, t in enumerate(['Reguler', 'Premium', 'Exclusive']):
        rk.cell(r, 3 + j, f'=COUNTIFS({ST},A{r},{TR},"{t}")').font = fl
rk['A8'] = 'Total'; rk['A8'].font = fb
rk['B8'] = '=SUM(B5:B7)'; rk['B8'].font = fb
n_mobil_in = len({x['nama'].lower() for x in rows if x['status'] == 'Masuk top-100'})
n_mobil_out = len({x['nama'].lower() for x in rows if x['status'] == 'Di luar top-100'})
arch = [x for x in rows if x['archive']]
catatan = [
    ('Nama mobil', f'Masuk top-100: {n_mobil_in} mobil · Di luar top-100: {n_mobil_out} mobil (dihitung dari listing ini).'),
    ('Cara mencocokkan', 'Judul listing -> nama mobil -> kode SKU (dari SKU varian di ekspor Shopee/TikTok/Lazada Undercover 18 Sep 2026) -> peringkat SKU. '
                         'Mobil yang tidak ada di peta SKU (mis. Neta V, Proton Suprima S, iCar V23, Kia Cerato, Colt T120SS) dicek per nama di laporan penjualan: semuanya 0–2 unit, jauh di bawah ambang 29 unit.'),
    ('Produk terpisah', 'Nissan Grand Livina Custom Roofbox dihitung terpisah dari Grand Livina biasa (di luar top-100). Livina X-Gear punya SKU sendiri.'),
    ('Perhatian', ('Judul berakhiran "Archive" yang masuk top-100: ' + '; '.join(x['title'] for x in arch if x['status'] == 'Masuk top-100')
                   + '. Ini sisa uji coba archive Premium 20 Sep; model Honda Civic Sedan sekarang peringkat SKU #18. '
                     'Perlu diputuskan apakah tier Premium-nya tetap diarsipkan.') if any(x['status'] == 'Masuk top-100' for x in arch) else '-'),
]
r = 10
rk.cell(r, 1, 'Catatan').font = fb
for k, v in catatan:
    r += 1
    rk.cell(r, 1, k).font = fb; rk.cell(r, 1).alignment = Alignment(vertical='top')
    c = rk.cell(r, 2, v); c.font = fn; c.alignment = Alignment(wrap_text=True, vertical='top')
    rk.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    rk.row_dimensions[r].height = 14 * max(1, -(-len(v) // 90))
for col, w in zip('ABCDEF', [20, 16, 12, 12, 12, 30]): rk.column_dimensions[col].width = w
wb.save(sys.argv[1])
print('saved', sys.argv[1])
