# -*- coding: utf-8 -*-
"""
Update harga Reguler (+Strip) UA untuk SISA SKU top-100 (baseline Q3 2026) yang
belum memakai harga formulasi matriks -- hasil audit 2026-10-01
(audit_harga_reguler_top100.py): 32 SKU sudah punya target tapi belum live +
15 SKU baru masuk top-100 yang belum pernah diformulasikan.

Sumber target:
1. 32 SKU lama -> sheet 'Harga Baru' hasil harga_baru_matriks.py atas
   "Copy of DATA UC HPP Top 100 Terlaris.xlsx" versi Drive 2026-09-28
   (HARGA_BARU_TOP100_v7_recompute.xlsx). Identik dgn v6+override utk semua
   SKU kecuali Brio/Jazz (override lantai 332rb, tidak disentuh di sini).
2. 15 SKU baru -> metode matriks yang SAMA, tapi kalibrasi 100 model lama
   DIKUNCI (harga_slot): model baru disisipkan ke grup (Pcs/Roll x kategori)
   yang sudah ada tanpa menggeser harga model yang sudah live. Pcs/Roll dari
   "HPP STP OTP" (Drive) -- terbukti 100/100 sama dgn Pcs/Roll UA utk model
   yang ada di kedua file. Kategori & panjang dari harga_baru_sp_op_matriks.py
   (klasifikasi yang sudah dipakai live di SP/OP).

Output (folder <KERJA_DIR>/output_harga_sisa_top100):
- UPDATE_HARGA_UA_SHOPEE.xlsx : baris variasi yang harganya berubah saja
  (Shopee 1 + Shopee 2 digabung, toko yang sama).
- UPDATE_HARGA_UA_TIKTOK.xlsx : SEMUA baris produk yang tersentuh (pelajaran
  "sku not allow delete"), atribut wajib Tahun/Bile yang kosong diisi
  "2026"/"16:9" (pelajaran SP/OP & archive v4).
- UPDATE_HARGA_UA_LAZADA.xlsx : baris yang harganya berubah saja.
- RINGKASAN_HARGA_SISA_TOP100.xlsx : daftar SKU, harga lama -> baru, dasar.

Pemakaian: KERJA_DIR=<folder> python3 update_harga_reguler_sisa_top100.py
"""
import os, sys, re, math, pickle
from collections import defaultdict, Counter
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from update_harga_per_sku import (urai_sku, resolve_cols, cari_sheet, deteksi_channel,
                                  STARTROW, salin, is_outdoor_polos, baca_harga, TAMBAHAN_STRIP)
import harga_baru_sp_op_matriks as SPM

S = os.environ.get('KERJA_DIR', '.')
HARGA_V7 = f'{S}/HARGA_BARU_TOP100_v7_recompute.xlsx'
HPP_SPOP = f'{S}/hpp_drive/HPP_STP_OTP_drive.xlsx'
SRC = {'shopee': [f'{S}/gdrive_fix/Shopee 1.xlsx', f'{S}/gdrive_fix/Shopee 2.xlsx'],
       'tiktok': [f'{S}/gdrive_fix/TikTok 1.xlsx'],
       'lazada': [f'{S}/gdrive_fix/Lazada.xlsx']}
OUT = f'{S}/output_harga_sisa_top100'
ORANGE = PatternFill('solid', fgColor='FFC000')
KUNING = PatternFill('solid', fgColor='FFF2CC')
STEP, MAX_SPREAD, MM_PER_STEP = 1000, 5000, 100

# 32 SKU yang target-nya sudah ada tapi belum live (audit 2026-10-01)
LAMA = ['NSN-XTR', 'TYT-LCR', 'BYD-AT1', 'TYT-VOX', 'MTB-DST', 'FRD-FIE', 'HYN-CRT',
        'TYT-SNT', 'HND-ODY', 'MZD-CX5', 'MNI-COO', 'SZK-CAR', 'HND-CHB', 'WLG-ALM',
        'SZK-SPR', 'MTB-XPC', 'NSN-EVA', 'SZK-SX4', 'MBZ-ECL', 'WLG-AEV', 'NSN-TER',
        'MTB-KUD', 'HYN-SGZ', 'DTN-DGO', 'TYT-HAR', 'WLG-CNF', 'CHV-SPN', 'MBZ-CC',
        'SZK-ARH', 'HYN-PLS', 'DHT-TAR', 'BMW-S5']
# 15 SKU baru: (prefix listing, label, nama di HPP STP OTP / sp_op_matriks)
BARU = [
    (('SZK-CRP',), 'Suzuki Carry Pickup', 'Suzuki Carry'),   # = entri 'Suzuki Carry' (Pickup 4195mm) di matriks UA
    (('SZK-AL',), 'Suzuki APV Luxury', 'Suzuki APV Luxury'),
    (('NSN-SRN',), 'Nissan Serena', 'Nissan Serena'),
    (('NSN-LXG',), 'Nissan Livina X-Gear', 'Nissan Livina X-Gear'),
    (('CHV-CPT',), 'Chevrolet Captiva', 'Chevrolet Captiva'),
    (('HYN-SFE',), 'Hyundai Santa Fe', 'Hyundai Santa Fe'),
    (('WLG-CRZ',), 'Wuling Cortez', 'Wuling Cortez'),
    (('HND-STR',), 'Honda Stream', 'Honda Stream'),
    (('MG-SE',), 'MG S5 EV', 'MG S5 EV'),
    (('MTB-XFO',), 'Mitsubishi Xforce', 'Mitsubishi Xforce'),
    (('HND-CVH',), 'Honda Civic Hatchback', 'Honda Civic Hatchback'),
    (('HYN-AVG',), 'Hyundai Avega', 'Hyundai Avega'),
    (('KIA-SON',), 'Kia Sonet', 'Kia Sonet'),
    (('SZK-GVT', 'SZK-GVH', 'SZK-EVT'), 'Suzuki Vitara (Grand Vitara/e Vitara)', 'Suzuki Grand Vitara'),
    (('FRD-EVE',), 'Ford Everest', 'Ford Everest'),
]
KECUALI = ('custom', 'roofbox')   # 'x-gear' sengaja TIDAK: X-Gear kini SKU top-100 sendiri (NSN-LXG)


def baca_matriks_terkunci():
    ws = openpyxl.load_workbook(HARGA_V7, data_only=True)['Harga Baru']
    prod = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value is None:
            continue
        prod.append({'nama': ws.cell(r, 2).value, 'pr': int(ws.cell(r, 3).value),
                     'kat': ws.cell(r, 4).value, 'p': ws.cell(r, 5).value, 'h': int(ws.cell(r, 7).value)})
    return prod


def harga_slot(prod, pr, kat, p):
    """Harga model baru di grup (pr, kat) yg kalibrasinya dikunci ke model lama.
    Di dalam rentang panjang grup: posisi proporsional (rumus hitung_langkah).
    Lebih pendek dari anggota terkecil: lantai. Lebih panjang dari anggota
    terbesar: lanjut Rp1.000/100mm, total rentang tetap maks Rp5.000.
    Grup belum ada: lantai tier Pcs/Roll."""
    lantai = min(x['h'] for x in prod if x['pr'] == pr)
    g = [x for x in prod if x['pr'] == pr and x['kat'] == kat]
    if not g:
        return lantai, f'grup P{pr} {kat} belum ada -> lantai'
    lo = min(x['p'] for x in g); hi = max(x['p'] for x in g)
    top = max(x['h'] for x in g) - lantai
    if p <= lo:
        off, cara = 0, f'<= terkecil grup ({lo}mm) -> lantai'
    elif p >= hi:
        off = min(top + int(math.floor((p - hi) / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
        cara = f'>= terbesar grup ({hi}mm, +{top // 1000}rb) -> +{off // 1000}rb'
    else:
        spread = min(int(math.floor((hi - lo) / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
        off = int(math.floor((p - lo) / (hi - lo) * (spread // STEP) + 0.5)) * STEP
        cara = f'di antara {lo}-{hi}mm (spread {spread // 1000}rb) -> +{off // 1000}rb'
    sekitar = sorted(g, key=lambda x: abs(x['p'] - p))[:2]
    pemb = ', '.join(f"{x['nama']} {x['p']}mm={x['h'] // 1000}rb" for x in sekitar)
    return lantai + off, f'{cara}; pembanding: {pemb}'


def bangun_target():
    v7 = baca_harga(HARGA_V7, 1, 100)
    target, info = {}, []
    for pfx in LAMA:
        t = v7[pfx]
        target[pfx] = {'reguler': t['reguler'], 'strip': t['reguler'] + TAMBAHAN_STRIP,
                       'label': t['label'].split(' ', 1)[1]}
        info.append((pfx, target[pfx]['label'], 'Target lama (rank lama 61-100)', '', '', '', target[pfx]['reguler'],
                     'HARGA_BARU_TOP100 (matriks, HPP Drive 28-09)'))
    prod = baca_matriks_terkunci()
    ua_pr = {x['nama']: x['pr'] for x in prod}
    hpp = openpyxl.load_workbook(HPP_SPOP, data_only=True)['HPP 12%']
    PR = {str(hpp.cell(r, 1).value).strip(): hpp.cell(r, 3).value for r in range(2, hpp.max_row + 1)
          if hpp.cell(r, 1).value}
    for pfxs, label, sumber in BARU:
        if sumber in ua_pr:   # Suzuki Carry: pakai data matriks UA langsung
            x = next(x for x in prod if x['nama'] == sumber)
            pr, kat, p = x['pr'], x['kat'], x['p']
        else:
            pr, kat, p = int(PR[sumber]), SPM.KATEGORI[sumber], SPM.PANJANG_MM[sumber]
        h, cara = harga_slot(prod, pr, kat, p)
        for pfx in pfxs:
            target[pfx] = {'reguler': h, 'strip': h + TAMBAHAN_STRIP, 'label': label}
        info.append(('/'.join(pfxs), label, 'SKU baru top-100 Q3', pr, kat, p, h, cara))
    return target, info


def judul_reguler(nm):
    return bool(re.search(r'\breguler\b', nm, re.I))


def proses_file(path, target, laporan, semua_varian=False):
    """Kembalikan (wb, ws, start, baris_disimpan) -- baris yg perlu ikut file upload."""
    wb = openpyxl.load_workbook(path)
    ch = deteksi_channel(wb); ws = cari_sheet(wb, ch); col = resolve_cols(ws, ch)
    start = STARTROW[ch]
    hdr = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1) if ws.cell(1, c).value}
    c_pid = 1
    ubah = {}
    for r in range(start, ws.max_row + 1):
        pfx, kat = urai_sku(ws.cell(r, col['sku']).value)
        if pfx not in target or kat not in ('R', 'S'):
            continue
        nm = str(ws.cell(r, col['nama']).value or '')
        if any(k in nm.lower() for k in KECUALI) or is_outdoor_polos(nm):
            continue
        if not judul_reguler(nm):
            laporan['anomali'].append((ch, nm, ws.cell(r, col['sku']).value, 'SKU R/S di judul non-Reguler, dilewati'))
            continue
        baru = target[pfx]['reguler' if kat == 'R' else 'strip']
        sel = ws.cell(r, col['harga'])
        lama = sel.value
        try:
            if int(float(lama)) == baru:
                continue
        except (TypeError, ValueError):
            pass
        ubah[r] = (pfx, kat, lama, baru)
    for r, (pfx, kat, lama, baru) in ubah.items():
        sel = ws.cell(r, col['harga'])
        sel.value = str(baru) if isinstance(lama, str) else baru
        sel.fill = ORANGE
        laporan['rows'].append((ch, pfx, kat, lama, baru, str(ws.cell(r, col['nama']).value)))
    if semua_varian:   # TikTok: ikutkan SEMUA varian produk yg tersentuh
        pids = {ws.cell(r, c_pid).value for r in ubah}
        simpan = [r for r in range(start, ws.max_row + 1) if ws.cell(r, c_pid).value in pids]
        for key, isi in (('product_property/100530', '2026'), ('product_property/102755', '16:9')):
            c = hdr[key]
            for r in simpan:
                if ws.cell(r, c).value in (None, ''):
                    ws.cell(r, c).value = isi
                    ws.cell(r, c).fill = KUNING
                    laporan['atribut'][key] += 1
    else:
        simpan = sorted(ubah)
    return wb, ws, start, simpan, ch


def tulis(wb, ws, start, simpan, ekstra, out):
    """Pindahkan baris `simpan` ke atas (mulai `start`), buang sisanya, lalu
    tempel baris dari file lain (ekstra = list (ws_sumber, baris))."""
    n_kol = ws.max_column
    for i, r in enumerate(simpan):
        if start + i != r:
            salin(ws, r, ws, start + i, n_kol)
    sisa = start + len(simpan)
    if sisa <= ws.max_row:
        ws.delete_rows(sisa, ws.max_row - sisa + 1)
    t = sisa
    for ws_s, r in ekstra:
        salin(ws_s, r, ws, t, n_kol); t += 1
    wb.save(out)
    return t - start


def main():
    os.makedirs(OUT, exist_ok=True)
    target, info = bangun_target()
    laporan = {'rows': [], 'anomali': [], 'atribut': Counter()}
    hasil = {}
    for ch, paths in SRC.items():
        dasar = None; ekstra = []
        for path in paths:
            wb, ws, start, simpan, ch2 = proses_file(path, target, laporan, semua_varian=(ch == 'tiktok'))
            assert ch2 == ch, (path, ch2)
            if dasar is None:
                dasar = (wb, ws, start, simpan)
            else:
                ekstra.extend((ws, r) for r in simpan)
        out = f'{OUT}/UPDATE_HARGA_UA_{ch.upper()}.xlsx'
        n = tulis(*dasar, ekstra, out)
        hasil[ch] = (out, n)

    # ringkasan
    wbo = openpyxl.Workbook(); w1 = wbo.active; w1.title = 'Harga Baru 47 SKU'
    kol = ['Prefix SKU', 'Model', 'Kelompok', 'Pcs/Roll', 'Kategori', 'Panjang (mm)', 'Harga Lama (Reguler)',
           'Harga Baru Reguler', 'Harga Baru Strip', 'Baris Shopee', 'Baris TikTok', 'Baris Lazada', 'Dasar perhitungan']
    for i, h in enumerate(kol, 1):
        c = w1.cell(1, i, h); c.font = Font(bold=True); c.fill = ORANGE; c.alignment = Alignment(wrap_text=True)
    per = defaultdict(Counter); lama_of = defaultdict(Counter)
    for ch, pfx, kat, lama, baru, nm in laporan['rows']:
        key = next((i[0] for i in info if pfx in i[0].split('/')), pfx)
        per[key][ch] += 1
        if kat == 'R':
            lama_of[key][int(float(lama))] += 1
    for r, (pfx, label, kelompok, pr, kat, p, h, dasar) in enumerate(info, 2):
        lama = ', '.join(f'{k:,}' for k, _ in lama_of[pfx].most_common())
        vals = [pfx, label, kelompok, pr, kat, p, lama, h, h + TAMBAHAN_STRIP,
                per[pfx]['shopee'], per[pfx]['tiktok'], per[pfx]['lazada'], dasar]
        for i, v in enumerate(vals, 1):
            w1.cell(r, i, v)
    for col, wd in zip('ABCDEFGHIJKLM', [20, 34, 26, 9, 13, 11, 16, 14, 14, 10, 10, 10, 90]):
        w1.column_dimensions[col].width = wd
    w1.freeze_panes = 'C2'
    wbo.save(f'{OUT}/RINGKASAN_HARGA_SISA_TOP100.xlsx')

    pickle.dump({'target': target, 'info': info, 'laporan': laporan}, open(f'{OUT}/target.pkl', 'wb'))
    print('Target:')
    for i in info:
        print(f'  {i[0]:24} {i[1]:38} {i[6]:>8,}  {i[7]}')
    for ch, (out, n) in hasil.items():
        n_ubah = sum(1 for x in laporan['rows'] if x[0] == ch)
        print(f'[{ch}] {n} baris di file ({n_ubah} harga berubah) -> {out}')
    print('Atribut TikTok diisi:', dict(laporan['atribut']))
    print('Anomali:', laporan['anomali'][:20], len(laporan['anomali']))


if __name__ == '__main__':
    main()
