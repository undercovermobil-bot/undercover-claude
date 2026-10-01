# -*- coding: utf-8 -*-
"""Verifikasi INDEPENDEN file hasil update_harga_reguler_sisa_top100.py: baca ulang
sumber & output dari disk, bangun ulang ekspektasi sendiri (tidak memakai
laporan/fungsi proses pembuatnya), lalu bandingkan baris demi baris.
Pemakaian: KERJA_DIR=<folder> python3 verify_update_harga_sisa_top100.py"""
import os, sys, re, math, pickle
from collections import Counter, defaultdict
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from update_harga_per_sku import baca_harga
import harga_baru_matriks as HM

S = os.environ.get('KERJA_DIR', '.')
OUT = f'{S}/output_harga_sisa_top100'
T = pickle.load(open(f'{OUT}/target.pkl', 'rb'))
target = T['target']
gagal = []
def cek(ok, pesan):
    print(('  OK   ' if ok else '  GAGAL ') + pesan)
    if not ok: gagal.append(pesan)

def pfx_kat(sku):
    b = str(sku or '').strip().split('-')
    return ('-'.join(b[:2]).upper(), b[3].upper()) if len(b) >= 6 else (None, None)

# 1. target 32 SKU lama == HARGA_BARU_TOP100_v6 (dipakai audit 09-18 & rollout 1-60)
v6 = baca_harga(f'{S}/HARGA_BARU_TOP100_v6.xlsx', 1, 100)
lama = [p for p, *_ in T['info'] if '/' not in p and p in v6]
cek(len(lama) == 32 and all(target[p]['reguler'] == v6[p]['reguler'] for p in lama),
    f'32 target lama identik dgn HARGA_BARU_TOP100_v6 ({len(lama)} prefix)')
cek(all(t['strip'] == t['reguler'] + 43000 for t in target.values()), 'semua Strip = Reguler + Rp43.000')
cek(len({p for p, *_ in T['info']}) == 47, '47 grup SKU (32 lama + 15 baru)')

# 2. 15 SKU baru: bandingkan dgn hitung ulang grup PENUH (model baru ikut dihitung
#    pakai hitung_langkah asli) -- informatif: berapa yg sama & apakah model lama bergeser
ws = openpyxl.load_workbook(f'{S}/HARGA_BARU_TOP100_v7_recompute.xlsx', data_only=True)['Harga Baru']
prod = [dict(nama=ws.cell(r, 2).value, pr=ws.cell(r, 3).value, kat=ws.cell(r, 4).value, p=ws.cell(r, 5).value,
             h=ws.cell(r, 7).value) for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value]
sama = geser = 0
for pfx, label, kel, pr, kat, p, h, dasar in T['info']:
    if '(rank lama' in kel: continue
    g = [x for x in prod if x['pr'] == pr and x['kat'] == kat]
    lantai = min(x['h'] for x in prod if x['pr'] == pr)
    peta = HM.hitung_langkah(sorted([x['p'] for x in g] + [p]))
    h_penuh = lantai + peta[p]
    gs = sum(1 for x in g if lantai + peta[x['p']] != x['h'])
    sama += (h_penuh == h); geser += gs
    if h_penuh != h or gs:
        print(f'     info {label}: kunci={h:,} vs hitung-penuh={h_penuh:,}; model lama yg akan bergeser kalau hitung penuh: {gs}')
print(f'     info: {sama}/15 harga model baru sama dgn hitung-penuh; total {geser} harga model lama akan bergeser kalau dihitung penuh (makanya dikunci)')

# 3. baris demi baris
SPEC = {
    'shopee': dict(src=['Shopee 1.xlsx', 'Shopee 2.xlsx'], sheet='Sheet1', start=7, key=(1, 3), nama=2, sku=6, harga=7, pid=1),
    'tiktok': dict(src=['TikTok 1.xlsx'], sheet='Template', start=6, key=(5,), nama=3, sku=11, harga=9, pid=1),
    'lazada': dict(src=['Lazada.xlsx'], sheet='template', start=5, key=(5,), nama=3, sku=13, harga=9, pid=1),
}
for ch, sp in SPEC.items():
    print(f'[{ch}]')
    src_rows, harap, prod_rows = {}, {}, defaultdict(set)
    hdr_src = None
    for f in sp['src']:
        w = openpyxl.load_workbook(f'{S}/gdrive_fix/{f}')[sp['sheet']]
        if hdr_src is None:
            hdr_src = [[w.cell(r, c).value for c in range(1, w.max_column + 1)] for r in range(1, sp['start'])]
        for r in range(sp['start'], w.max_row + 1):
            vals = [w.cell(r, c).value for c in range(1, w.max_column + 1)]
            if all(v in (None, '') for v in vals): continue
            k = tuple(str(vals[i - 1]) for i in sp['key'])
            assert k not in src_rows, (ch, k)
            src_rows[k] = vals
            prod_rows[str(vals[sp['pid'] - 1])].add(k)
            pfx, kat = pfx_kat(vals[sp['sku'] - 1])
            nm = str(vals[sp['nama'] - 1] or '').lower()
            if pfx in target and kat in ('R', 'S') and 'reguler' in nm and 'custom' not in nm and 'roofbox' not in nm:
                exp = target[pfx]['reguler' if kat == 'R' else 'strip']
                if int(float(vals[sp['harga'] - 1])) != exp:
                    harap[k] = exp
    w = openpyxl.load_workbook(f'{OUT}/UPDATE_HARGA_UA_{ch.upper()}.xlsx')[sp['sheet']]
    hdr_out = [[w.cell(r, c).value for c in range(1, w.max_column + 1)] for r in range(1, sp['start'])]
    cek(hdr_out == hdr_src, 'baris header identik dgn sumber')
    out_rows = {}
    for r in range(sp['start'], w.max_row + 1):
        vals = [w.cell(r, c).value for c in range(1, w.max_column + 1)]
        if all(v in (None, '') for v in vals): continue
        k = tuple(str(vals[i - 1]) for i in sp['key'])
        cek_dup = k in out_rows
        if cek_dup: gagal.append(f'{ch} duplikat {k}')
        out_rows[k] = vals
    cek(all(k in src_rows for k in out_rows), f'semua {len(out_rows)} baris output ada di sumber')
    berubah = {k for k, v in out_rows.items() if str(v[sp['harga'] - 1]) != str(src_rows[k][sp['harga'] - 1])}
    cek(berubah == set(harap), f'baris yg harganya berubah ({len(berubah)}) == ekspektasi independen ({len(harap)})')
    cek(all(int(out_rows[k][sp['harga'] - 1]) == harap[k] for k in berubah & set(harap)), 'semua harga baru == target')
    cek(all(isinstance(out_rows[k][sp['harga'] - 1], type(src_rows[k][sp['harga'] - 1])) for k in out_rows), 'tipe sel harga sama dgn sumber (teks)')
    hdr1 = hdr_src[0]
    boleh = {sp['harga'] - 1}
    if ch == 'tiktok':
        boleh |= {hdr1.index('product_property/100530'), hdr1.index('product_property/102755')}
    beda_lain = 0; atr_salah = 0
    for k, v in out_rows.items():
        s = src_rows[k]
        for i in range(len(s)):
            if i in boleh:
                if ch == 'tiktok' and i != sp['harga'] - 1 and v[i] != s[i]:
                    exp = '2026' if i == hdr1.index('product_property/100530') else '16:9'
                    atr_salah += not (s[i] in (None, '') and v[i] == exp)
                continue
            beda_lain += (v[i] != s[i])
    cek(beda_lain == 0, f'kolom lain tidak berubah sama sekali (selisih: {beda_lain})')
    if ch == 'tiktok':
        cek(atr_salah == 0, 'atribut Tahun/Bile hanya diisi di sel kosong dgn "2026"/"16:9"')
        hdr_i = (hdr1.index('product_property/100530'), hdr1.index('product_property/102755'))
        cek(all(v[i] not in (None, '') for v in out_rows.values() for i in hdr_i), 'tidak ada Tahun/Bile kosong di output')
        pids_harap = {str(src_rows[k][sp['pid'] - 1]) for k in harap}
        pids_out = {str(v[sp['pid'] - 1]) for v in out_rows.values()}
        cek(pids_out == pids_harap, f'produk di output ({len(pids_out)}) == produk yg tersentuh ({len(pids_harap)})')
        cek(all(set(k for k, v in out_rows.items() if str(v[sp['pid'] - 1]) == p) == prod_rows[p] for p in pids_out),
            'tiap produk TikTok membawa SEMUA variannya (anti "sku not allow delete")')
    else:
        cek(set(out_rows) == set(harap), 'output hanya berisi baris yg berubah')
    grp = Counter(pfx_kat(out_rows[k][sp['sku'] - 1])[0] for k in berubah)
    grp47 = Counter()
    for pfx, *_ in T['info']:
        grp47[pfx] = sum(grp[p] for p in pfx.split('/'))
    kosong = [p for p, n in grp47.items() if n == 0]
    cek(not kosong, f'ke-47 grup SKU ada perubahan di channel ini' + (f' (kosong: {kosong})' if kosong else ''))

print('\nHASIL:', 'SEMUA LULUS' if not gagal else f'{len(gagal)} GAGAL: {gagal}')
