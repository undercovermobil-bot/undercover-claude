"""Audit read-only: listing Reguler UA (Shopee/TikTok/Lazada di KERJA_DIR/gdrive_fix) vs target harga formulasi
(HARGA_BARU_TOP100_v6.xlsx + override Brio/Jazz/Ignis/Agya-Ayla). Status per listing top-100 SKU:
SUDAH (semua baris R & S = target), BELUM, SEBAGIAN, TANPA TARGET (SKU belum pernah diformulasikan)."""
import sys, os, re, pickle
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
S = os.environ.get("KERJA_DIR", ".")

import warnings; warnings.filterwarnings('ignore')
import openpyxl
from update_harga_per_sku import (PREFIX, ALIAS, KECUALI, is_outdoor_polos, urai_sku,
    resolve_cols, cari_sheet, deteksi_channel, STARTROW, baca_harga)
from klasifikasi_listing_top100 import klasifikasi

target = baca_harga(f"{S}/HARGA_BARU_TOP100_v6.xlsx", 1, 100)
for pfx, reg in {'HND-BRI': 332000, 'HND-JAZ': 332000, 'SZK-IGN': 333000, 'DHT-AYL': 334000}.items():
    target[pfx]['reguler'] = reg; target[pfx]['strip'] = reg + 43000
AL = dict(ALIAS); AL.update({'DHT-GMX': 'DHT-LXO', 'TYT-HAL': 'TYT-HAC', 'MZD-2H': 'MZD-MZ2'})
old_rank = {}
for i, (nm, pfx) in enumerate(PREFIX.items()):
    old_rank.setdefault(pfx, i + 1)

out = pickle.load(open(f"{S}/ranking_per_sku.pkl", "rb"))['out']
new_rank = {g['key']: g['rank'] for g in out}
top100 = [g for g in out if g['rank'] <= 100]

FILES = ['Shopee 1.xlsx', 'Shopee 2.xlsx', 'TikTok 1.xlsx', 'Lazada.xlsx']
hasil = {}   # (channel, title) -> info
for f in FILES:
    wb = openpyxl.load_workbook(f"{S}/gdrive_fix/{f}", data_only=True)
    ch = deteksi_channel(wb); ws = cari_sheet(wb, ch); col = resolve_cols(ws, ch)
    for r in range(STARTROW[ch], ws.max_row + 1):
        nm = str(ws.cell(r, col['nama']).value or '').strip()
        if not nm: continue
        k = klasifikasi(nm)
        if k['tier'] != 'Reguler': continue
        rec = hasil.setdefault((ch, nm), {'k': k, 'rows': [], 'file': f})
        sku = ws.cell(r, col['sku']).value
        pfx, kat = urai_sku(sku)
        h = ws.cell(r, col['harga']).value
        try: h = int(float(h))
        except (TypeError, ValueError): h = None
        rec['rows'].append((AL.get(pfx, pfx) if pfx else None, kat, h, str(ws.cell(r, col['var']).value or ''), sku))
pickle.dump({'hasil': hasil, 'target': target, 'old_rank': old_rank}, open(f"{S}/audit_harga_reguler_drive.pkl", "wb"))

def status_produk(rec):
    nm = list(rec['rows'])
    pf = Counter(p for p, kat, h, v, s in rec['rows'] if p and kat in ('R', 'S'))
    if not pf: return 'SKU kosong/tak terurai', None, [], []
    pfx = pf.most_common(1)[0][0]
    if pfx not in target: return 'TANPA TARGET', pfx, [], []
    ok, salah = [], []
    for p, kat, h, v, s in rec['rows']:
        if kat not in ('R', 'S') or p != pfx: continue
        tgt = target[pfx]['reguler' if kat == 'R' else 'strip']
        (ok if h == tgt else salah).append((kat, h, tgt, v))
    if not salah: st = 'SUDAH'
    elif not ok: st = 'BELUM'
    else: st = 'SEBAGIAN'
    return st, pfx, ok, salah

for ch in ['shopee', 'tiktok', 'lazada']:
    print(f"\n===================== {ch.upper()} =====================")
    cnt = Counter(); detail = defaultdict(list)
    for (c, nm), rec in hasil.items():
        if c != ch: continue
        k = rec['k']
        arch = bool(re.search(r'\[?archived?\]?\s*$', nm, re.I))
        grp = k['status'] + (' [Archived]' if arch else '')
        st, pfx, ok, salah = status_produk(rec)
        cnt[(grp, st)] += 1
        detail[(grp, st)].append((k['rank'] or 999, nm, pfx, sorted({x[1] for x in salah}), sorted({(x[0], x[2]) for x in salah}), len(ok), len(salah)))
    for key in sorted(cnt): print(f"  {key[0]:32} {key[1]:22} {cnt[key]:4}")
    for key in sorted(detail):
        if key[0] != 'Masuk top-100' or key[1] == 'SUDAH': continue
        print(f"  --- {key} ---")
        for x in sorted(detail[key]):
            print(f"    #{x[0]:>3} {x[1][:75]:75} {x[2]} live={x[3]} target={x[4]} ok={x[5]} salah={x[6]}")
