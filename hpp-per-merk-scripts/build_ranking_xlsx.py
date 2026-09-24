import os, sys, pickle
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
S = os.environ.get("KERJA_DIR", ".")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, "ranking_per_sku.py")).read().split("# nama grup = anggota terlaris")[0])  # reuse MANUAL/SPLIT/TERPISAH + groups
R = pickle.load(open(f"{S}/ranking_per_sku.pkl", "rb"))
out, rows = R['out'], R['rows']

ua_pfx = set()
for c in ua.values():
    ua_pfx.update(c.keys())
def ada_ua(key):
    if key.startswith('NAMA:'): return '?'
    if key == 'SZK-VITARA': return 'Ya' if {'SZK-GVT','SZK-GVH','SZK-EVT'} & ua_pfx else 'Tidak'
    return 'Ya' if key in ua_pfx else 'Tidak'

F = 'Arial'
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=13, bold=True)
f_input = Font(name=F, size=10, color='0000FF')
f_link = Font(name=F, size=10, color='008000')
hdr_fill = PatternFill('solid', fgColor='1F4E78')
f_hdr = Font(name=F, size=10, bold=True, color='FFFFFF')
new_fill = PatternFill('solid', fgColor='E2EFDA')
thin = Side(style='thin', color='BFBFBF')
border = Border(bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')

wb = openpyxl.Workbook()

# ---------------- Keterangan (input + catatan) ----------------
ket = wb.active
ket.title = 'Keterangan'
ket['A1'] = 'Ranking Produk per SKU — dasar perampingan katalog Undercover ke 100 terlaris'
ket['A1'].font = f_title
ket['A3'] = 'Input'; ket['A3'].font = f_bold
ket['A4'] = 'Total kuantitas semua model (unit)'; ket['B4'] = 30550
ket['A5'] = 'Jumlah hari periode'; ket['B5'] = 169
ket['A6'] = 'Ambang produk yang dipertahankan'; ket['B6'] = 100
for c in ('B4', 'B5', 'B6'):
    ket[c].font = f_input
ket['B4'].number_format = '#,##0'
ket['C4'] = 'Sumber: MOBIL_TERLARIS_BIGSELLER.xlsx, baris TOTAL sheet "Top Model Mobil" (data dari user)'
ket['C5'] = 'Sumber: periode laporan 1 Apr – 16 Sep 2026 (data dari user)'
ket['C6'] = 'Rencana user: katalog dirampingkan jadi 100 produk terlaris, dievaluasi tiap kuartal'
notes = [
    ('Sumber data', 'MOBIL_TERLARIS_BIGSELLER.xlsx (dibuat 2026-09-17), ekspor BigSeller "Laporan Penjualan > Berdasarkan SKU Toko", periode 1 Apr – 16 Sep 2026.'),
    ('Cakupan', 'GABUNGAN 4 toko (Undercover, Otonation, Otoprotection, Smartprotection), channel Shopee + TikTok/Tokopedia. Lazada TIDAK termasuk (tidak terhubung ke BigSeller). Angka bukan khusus toko Undercover saja.'),
    ('Masalah yang diperbaiki', 'Laporan asli mengelompokkan per NAMA listing. Mobil kembar yang berbagi 1 SKU (Avanza/Xenia/Veloz, Agya/Ayla, Feroza/Taft GT/Rocky lama, dst) dan penulisan nama berbeda untuk mobil yang sama ("Gran Max PU" vs "Gran Max Pick Up", listing Otonation "... Semi Outdoor", typo "Undervover") muncul sebagai baris terpisah, sehingga ±15 slot top-100 terpakai produk yang sama.'),
    ('Metode', 'Tiap nama di laporan dipetakan ke prefix SKU (2 segmen pertama, mis. TYT-AVZ) yang dipakai di listing Undercover (Shopee/TikTok/Lazada, snapshot 18 Sep 2026); kalau tidak ada di listing Undercover, pakai listing Smartprotection/Otoprotection; kalau tidak ada di keduanya, dipetakan manual dengan bukti rentang generasi di sheet Detail. Unit & penjualan dijumlah per prefix. Rincian per nama ada di sheet "Pemetaan Nama".'),
    ('Kolom "Ada di Listing UA"', 'Ya = prefix SKU grup ini dipakai di listing Undercover snapshot 18 Sep 2026. Tidak = hanya dijual toko lain (permintaannya tetap terhitung). ? = grup tanpa SKU pasti.'),
    ('Batas ambang', 'Peringkat #99 Ford Everest & #100 Suzuki Vitara = 30 unit; #101–#104 (Mitsubishi Outlander, Mitsubishi Mirage, BMW Seri 5, Toyota GR 86) sama-sama 29 unit. Selisih di ambang hanya 1 unit, dan Suzuki Vitara baru mencapai 30 karena digabung dengan listing Grand Vitara (6 unit) — posisi di sekitar #95–#105 sangat mudah bertukar di evaluasi kuartal berikutnya.'),
    ('Rocky dipecah', 'Daihatsu Rocky (90 unit): 77 unit generasi 2019+ dan 8 unit tanpa info generasi masuk ke Raize (TYT-RZE); 5 unit Rocky lama F70 masuk ke Feroza (DHT-FRZ).'),
    ('Gran Max dipecah', 'Listing "Daihatsu Gran Max" (18 unit) berisi Minibus dan Pick Up sekaligus tanpa info bodi di data penjualan, jadi dibagi rata 9 ke Minibus/Luxio (DHT-GMX) dan 9 ke Pick Up (DHT-GMXP).'),
    ('Sengaja TIDAK digabung', 'Grand Livina Custom Roofbox & Livina X-Gear (produk & harga beda), Toyota Vios Custom & Maserati Custom Spoiler (produk custom), Range Rover Velar/Sport (prefix LDR-RR sama dengan Range Rover tapi mobil beda — kemungkinan salah tag SKU, perlu dicek), Mazda 2 / Mazda 3 / Kia Rio / Suzuki Aerio tanpa keterangan bodi (tidak bisa dipastikan Hatchback atau Sedan). Feroza Long tetap terpisah (SKU sendiri DHT-FRL). Suzuki Carry tetap terpisah dari Carry Pickup (SKU beda sesuai keputusan 2026-08-22).'),
    ('Perlu keputusan user', 'Mazda 2 (117 unit, peringkat baru #51) tidak menyebut bodi (Hatchback MZD-2H atau Sedan MZD-2S). Kalau ternyata Hatchback, digabung ke Mazda 2 Hatchback → 219 unit dan 1 slot top-100 jadi kosong, diperebutkan 4 produk yang sama-sama 29 unit (lihat Batas ambang).'),
    ('Warna font', 'Biru = angka input (bisa diubah). Hitam = rumus. Hijau = rumus yang mengambil dari sheet lain.'),
]
ket['A8'] = 'Catatan'; ket['A8'].font = f_bold
r = 9
for k, v in notes:
    ket.cell(r, 1, k).font = f_bold
    c = ket.cell(r, 2, v); c.font = f_norm; c.alignment = wrap
    ket.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    ket.row_dimensions[r].height = max(15, 15 * (len(v) // 95 + 1))
    ket.cell(r, 1).alignment = wrap
    r += 1
for rr in range(3, 7):
    for cc in range(1, 4):
        if ket.cell(rr, cc).font != f_input:
            if rr == 3: continue
            if cc != 2: ket.cell(rr, cc).font = f_norm
ket.column_dimensions['A'].width = 34
ket.column_dimensions['B'].width = 14
for col in 'CDEF':
    ket.column_dimensions[col].width = 22

TOTAL = "Keterangan!$B$4"
HARI = "Keterangan!$B$5"
AMBANG = "Keterangan!$B$6"

# ---------------- Pemetaan Nama ----------------
pm = wb.create_sheet('Pemetaan Nama')
pm_hdr = ['Nama di Laporan', 'Peringkat Lama', 'Unit', 'Total Penjualan (Rp)', 'Kode Grup (Prefix SKU)', 'Dasar Pemetaan']
entries = []
split_names = set(SPLIT)
for rank, nm, qty, rp in rows:
    if nm in SPLIT:
        for key, q, why in SPLIT[nm]:
            entries.append((nm, rank, q, round(rp * q / qty), key, 'DIPECAH: ' + why))
        continue
    if nm in TERPISAH:
        entries.append((nm, rank, qty, rp, 'NAMA: ' + nm, 'Tidak digabung: ' + TERPISAH[nm]))
    elif nm in MANUAL:
        key, why = MANUAL[nm]
        entries.append((nm, rank, qty, rp, key, 'Manual: ' + why))
    else:
        b = norm(base_name(nm))
        if ua.get(b):
            entries.append((nm, rank, qty, rp, dominant(ua[b]), 'SKU di listing Undercover'))
        elif spop.get(b):
            entries.append((nm, rank, qty, rp, dominant(spop[b]), 'SKU di listing Smartprotection/Otoprotection'))
        else:
            entries.append((nm, rank, qty, rp, 'NAMA: ' + nm, 'Tidak ada di listing, berdiri sendiri'))
pm['A1'] = 'Pemetaan tiap nama di laporan penjualan ke grup SKU'; pm['A1'].font = f_title
pm['A2'] = 'Unit & penjualan asli dari sheet "Top Model Mobil". Baris dipecah (Rocky, Gran Max) muncul 2x dengan bagian unitnya; penjualan Rp dibagi proporsional unit.'
pm['A2'].font = f_norm
for i, h in enumerate(pm_hdr, 1):
    c = pm.cell(4, i, h); c.font = f_hdr; c.fill = hdr_fill; c.alignment = Alignment(wrap_text=True, vertical='center')
PM_FIRST = 5
for i, (nm, rank, q, rp, key, why) in enumerate(entries):
    rr = PM_FIRST + i
    vals = [nm, rank, q, rp, key, why]
    for j, v in enumerate(vals, 1):
        c = pm.cell(rr, j, v); c.font = f_norm
    pm.cell(rr, 3).number_format = '#,##0'
    pm.cell(rr, 4).number_format = '#,##0'
    if why.startswith(('DIPECAH', 'Manual', 'Tidak digabung')):
        for j in range(1, 7): pm.cell(rr, j).fill = PatternFill('solid', fgColor='FFF2CC')
PM_LAST = PM_FIRST + len(entries) - 1
tr = PM_LAST + 1
pm.cell(tr, 1, 'TOTAL').font = f_bold
pm.cell(tr, 3, f'=SUM(C{PM_FIRST}:C{PM_LAST})').font = f_bold
pm.cell(tr, 4, f'=SUM(D{PM_FIRST}:D{PM_LAST})').font = f_bold
pm.cell(tr, 3).number_format = '#,##0'; pm.cell(tr, 4).number_format = '#,##0'
pm.cell(tr + 1, 1, 'Cek: harus sama dengan total di Keterangan').font = f_norm
c = pm.cell(tr + 1, 3, f'=C{tr}-{TOTAL}'); c.font = f_link; c.number_format = '#,##0;-#,##0;"OK (0)"'
for col, w in zip('ABCDEF', [44, 10, 9, 16, 22, 80]):
    pm.column_dimensions[col].width = w
pm.freeze_panes = 'A5'
pm.auto_filter.ref = f"A4:F{PM_LAST}"

UNIT_RNG = f"'Pemetaan Nama'!$C${PM_FIRST}:$C${PM_LAST}"
RP_RNG = f"'Pemetaan Nama'!$D${PM_FIRST}:$D${PM_LAST}"
KEY_RNG = f"'Pemetaan Nama'!$E${PM_FIRST}:$E${PM_LAST}"
key_disp = lambda k: ('NAMA: ' + k[5:]) if k.startswith('NAMA:') else k

# ---------------- sheet ranking ----------------
HDR = ['Peringkat Baru', 'Nama Produk', 'Kode Grup (Prefix SKU)', 'Total Unit', '% dari Total Unit',
       'Total Penjualan (Rp)', 'Rata-rata Terjual/Hari', 'Peringkat Lama Terbaik', 'Status',
       'Jumlah Nama Digabung', 'Nama yang Digabung (peringkat lama, unit)', 'Ada di Listing UA']
def build_rank_sheet(ws, title, groups, note):
    ws['A1'] = title; ws['A1'].font = f_title
    ws['A2'] = note; ws['A2'].font = f_norm
    for i, h in enumerate(HDR, 1):
        c = ws.cell(4, i, h); c.font = f_hdr; c.fill = hdr_fill
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    ws.row_dimensions[4].height = 30
    first = 5
    for i, g in enumerate(groups):
        rr = first + i
        kd = key_disp(g['key'])
        mem = ' + '.join(f"{m[1]} (#{m[0]}, {m[2]})" for m in g['members']) if len(g['members']) > 1 else ''
        ws.cell(rr, 1, g['rank'])
        ws.cell(rr, 2, g['nama'])
        ws.cell(rr, 3, kd)
        ws.cell(rr, 4, f'=SUMIFS({UNIT_RNG},{KEY_RNG},C{rr})')
        ws.cell(rr, 5, f'=D{rr}/{TOTAL}')
        ws.cell(rr, 6, f'=SUMIFS({RP_RNG},{KEY_RNG},C{rr})')
        ws.cell(rr, 7, f'=D{rr}/{HARI}')
        ws.cell(rr, 8, g['best_old'])
        ws.cell(rr, 9, f'=IF(H{rr}<={AMBANG},"Tetap","Masuk Baru")')
        ws.cell(rr, 10, f'=COUNTIFS({KEY_RNG},C{rr})')
        ws.cell(rr, 11, mem)
        ws.cell(rr, 12, ada_ua(g['key']))
        for j in range(1, 13):
            c = ws.cell(rr, j); c.font = f_norm; c.border = border
        for j in (4, 6, 7, 9, 10):
            ws.cell(rr, j).font = f_link
        ws.cell(rr, 4).number_format = '#,##0'
        ws.cell(rr, 5).number_format = '0.00%'
        ws.cell(rr, 6).number_format = '#,##0'
        ws.cell(rr, 7).number_format = '0.00'
        ws.cell(rr, 11).alignment = Alignment(wrap_text=True, vertical='top')
        if g['best_old'] > 100:
            for j in range(1, 13): ws.cell(rr, j).fill = new_fill
    last = first + len(groups) - 1
    tr = last + 1
    ws.cell(tr, 2, 'TOTAL').font = f_bold
    ws.cell(tr, 4, f'=SUM(D{first}:D{last})').font = f_bold
    ws.cell(tr, 5, f'=SUM(E{first}:E{last})').font = f_bold
    ws.cell(tr, 6, f'=SUM(F{first}:F{last})').font = f_bold
    ws.cell(tr, 4).number_format = '#,##0'; ws.cell(tr, 5).number_format = '0.0%'; ws.cell(tr, 6).number_format = '#,##0'
    for col, w in zip('ABCDEFGHIJKL', [9, 30, 18, 9, 9, 16, 10, 10, 11, 9, 70, 9]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = 'C5'
    ws.auto_filter.ref = f"A4:L{last}"
    return first, last, tr

t = wb.create_sheet('Top 100 per SKU', 0)
f1, l1, tr1 = build_rank_sheet(t, 'Top 100 Produk per SKU (kembar & nama ganda sudah digabung)', out[:100],
    'Periode 1 Apr – 16 Sep 2026 · 4 toko gabungan · Shopee + TikTok (tanpa Lazada). Baris hijau = produk yang sebelumnya di luar top-100 (per nama) dan sekarang masuk.')
t.cell(tr1 + 2, 2, 'Tepat di bawah ambang:').font = f_bold
for k, g in enumerate(out[100:104]):
    t.cell(tr1 + 3 + k, 1, g['rank']).font = f_norm
    t.cell(tr1 + 3 + k, 2, g['nama']).font = f_norm
    t.cell(tr1 + 3 + k, 3, key_disp(g['key'])).font = f_norm
    c = t.cell(tr1 + 3 + k, 4, f'=SUMIFS({UNIT_RNG},{KEY_RNG},C{tr1 + 3 + k})'); c.font = f_link
t.cell(tr1 + 8, 2, 'Top-100 mencakup').font = f_norm
c = t.cell(tr1 + 8, 5, f'=D{tr1}/{TOTAL}'); c.font = f_bold; c.number_format = '0.0%'
t.cell(tr1 + 8, 6, 'dari seluruh unit terjual').font = f_norm

full = wb.create_sheet('Peringkat Lengkap', 1)
build_rank_sheet(full, 'Peringkat Lengkap Semua Produk per SKU', out,
    'Semua grup produk (325), urut total unit. Baris hijau = di top-100 lama tidak ada, tapi masuk berkat penggabungan (hanya relevan untuk peringkat <= 100).')

wb.move_sheet('Keterangan', offset=1)
wb.move_sheet('Pemetaan Nama', offset=1)
wb.save(f"{S}/RANKING_TOP100_PER_SKU.xlsx")
print("saved", wb.sheetnames, "pemetaan rows", len(entries))
