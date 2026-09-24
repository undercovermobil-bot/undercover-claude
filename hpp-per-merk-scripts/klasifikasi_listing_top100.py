"""Tandai tiap produk di listing (Shopee mass_update_basic_info) masuk top-100 SKU atau tidak.
Pakai peta nama->SKU (sku_map.pkl) & hasil ranking_per_sku.py. Folder data dari env KERJA_DIR."""
import os, re, sys, pickle
from collections import Counter
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sku_map_lib import base_name, norm
S = os.environ.get("KERJA_DIR", ".")

d = pickle.load(open(f"{S}/sku_map.pkl", "rb"))
ua, spop = d['ua'], d['spop']
out = pickle.load(open(f"{S}/ranking_per_sku.pkl", "rb"))['out']
rank_of = {g['key']: g['rank'] for g in out}
qty_of = {g['key']: g['qty'] for g in out}
VIT = {'SZK-GVT', 'SZK-GVH', 'SZK-EVT'}
# nama lama / penamaan lain -> SKU, diambil dari MANUAL di ranking_per_sku.py (satu sumber kebenaran)
import ast
_src = open(os.path.join(HERE, 'ranking_per_sku.py')).read()
_m = re.search(r'^MANUAL = (\{.*?^\})', _src, re.S | re.M)
NAMA_LAMA = {norm(k): v[0] for k, v in ast.literal_eval(_m.group(1)).items()}
QTY_AMBANG = out[99]['qty']
SALES_BY_NAME = {}
_wb = openpyxl.load_workbook(f"{S}/MOBIL_TERLARIS_BIGSELLER.xlsx", data_only=True)['Top Model Mobil']
for _r in range(6, _wb.max_row):
    if _wb.cell(_r, 1).value is None: continue
    _k = norm(re.sub(r'(?i)\s*(semi outdoor|reguler.*|exxclusive)$', '', str(_wb.cell(_r, 2).value)))
    SALES_BY_NAME[_k] = SALES_BY_NAME.get(_k, 0) + (_wb.cell(_r, 3).value or 0)
# judul yg SKU-nya sama dgn produk top-100 tapi produknya beda (lihat ranking_per_sku.TERPISAH)
PRODUK_TERPISAH = {'nissangrandlivinacustomroofbox': 'Grand Livina Custom Roofbox = produk terpisah (bukan Grand Livina biasa)'}
NON_MOBIL = ('cover motor', 'selimut motor', 'sarung motor', 'karpet', 'pouch')
TIER_RE = re.compile(r'\b(reguler|premium|exclusive|transparan|semi outdoor|extreme outdoor|outdoor)\b', re.I)

def nama_bersih(title):
    n = base_name(title)
    while True:
        n2 = re.sub(r'^(cover|mobil|body)\s+', '', n, flags=re.I)
        n2 = re.sub(r'^(\w+)\s+\1\b', r'\1', n2, flags=re.I)
        n2 = re.sub(r'^Mercedes\s+(?!Benz\b)', 'Mercedes Benz ', n2, flags=re.I)
        if n2 == n: return n
        n = n2

def klasifikasi(title):
    t = str(title or '')
    tier_m = TIER_RE.search(t)
    tier = tier_m.group(1).title() if tier_m else '-'
    archive = bool(re.search(r'\barchive\s*$', t, re.I))
    tl = t.lower()
    if any(k in tl for k in NON_MOBIL) or not re.search(r'(cover|selimut|sarung)\s+mobil', tl) or 'logo custom' in tl:
        return {'status': 'Bukan cover mobil', 'tier': tier, 'archive': archive, 'nama': '', 'keys': [], 'rank': None, 'dasar': ''}
    nm = nama_bersih(t)
    b = norm(nm)
    if b in PRODUK_TERPISAH:
        return {'status': 'Di luar top-100', 'tier': tier, 'archive': archive, 'nama': nm, 'keys': [], 'rank': None, 'dasar': PRODUK_TERPISAH[b]}
    b_raw = norm(base_name(t))
    src = ua.get(b) or ua.get(b_raw) or spop.get(b) or spop.get(b_raw)
    if not src and (b in NAMA_LAMA or b_raw in NAMA_LAMA):
        k = NAMA_LAMA.get(b) or NAMA_LAMA.get(b_raw)
        rank = rank_of.get(k)
        return {'status': 'Masuk top-100' if rank and rank <= 100 else 'Di luar top-100', 'tier': tier, 'archive': archive,
                'nama': nm, 'keys': [k], 'rank': rank, 'dasar': f'SKU {k} (nama lama/penamaan lain, lihat MANUAL di ranking_per_sku.py)'}
    if not src:
        # tidak ada di peta SKU: cek penjualan per NAMA di laporan; semua kasus yg ketemu jauh di bawah ambang
        q = SALES_BY_NAME.get(b, 0)
        status = 'Masuk top-100' if q >= QTY_AMBANG else 'Di luar top-100'
        return {'status': status, 'tier': tier, 'archive': archive, 'nama': nm, 'keys': [], 'rank': None,
                'dasar': f'nama tidak ada di peta SKU listing; penjualan per nama Apr-Sep = {q} unit (ambang top-100 = {QTY_AMBANG} unit)'}
    tot = sum(src.values())
    keys = sorted({('SZK-VITARA' if p in VIT else p) for p, n in src.items() if n / tot >= 0.2})
    ranks = [rank_of[k] for k in keys if k in rank_of]
    rank = min(ranks) if ranks else None
    status = 'Masuk top-100' if rank and rank <= 100 else 'Di luar top-100'
    dasar = 'SKU ' + ' / '.join(keys) + ('' if ranks else ' — tidak ada penjualan tercatat Apr-Sep 2026')
    return {'status': status, 'tier': tier, 'archive': archive, 'nama': nm, 'keys': keys, 'rank': rank, 'dasar': dasar}

def baca_listing(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = []
    for r in range(7, ws.max_row + 1):
        pid = ws.cell(r, 1).value
        if not pid: continue
        rows.append({'row': r, 'pid': str(pid), 'psku': ws.cell(r, 2).value, 'title': ws.cell(r, 3).value})
    return rows

if __name__ == '__main__':
    rows = baca_listing(sys.argv[1])
    for x in rows: x.update(klasifikasi(x['title']))
    print(Counter(x['status'] for x in rows))
    print(Counter((x['status'], x['tier']) for x in rows if x['status'] != 'Bukan cover mobil').most_common())
    print('Archive:', Counter(x['status'] for x in rows if x['archive']))
    for x in rows:
        if x['status'] == 'Perlu dicek': print('CEK:', x['pid'], x['title'])
    pickle.dump(rows, open(f"{S}/klasifikasi_listing.pkl", "wb"))
