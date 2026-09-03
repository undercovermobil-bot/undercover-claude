# -*- coding: utf-8 -*-
"""
Audit dua hal sekaligus di listing e-commerce:

A. **Format SKU** -- berapa baris yang sudah pakai format master terbaru
   (MEREK-MODEL-TOKO-KAT-GEN-WARNA) vs yang masih kode lama / kosong.

B. **Kesesuaian formula** -- utk model yang terdaftar di daftar referensi
   (`Data_Mobil_Lebih_dari_1_Formula.xlsx` Sheet2, 213 model), cek apakah
   SEGMEN GENERASI di SKU sudah sesuai skema berbasis FORMULA (jumlah kode =
   jumlah formula jahitan cover, bukan jumlah generasi).

Skema formula & pencocokan nama model TIDAK ditulis ulang di sini -- dipakai
ulang dari `formula_config.py` (aturan + config per model) dan
`apply_formula_sku.py` (`match_model`, regex `MASTERFMT`), supaya audit ini
menilai pakai definisi yang SAMA dengan yang dipakai saat menerapkan
perubahan. Kalau aturannya direvisi, audit ikut berubah otomatis.

Pemakaian:
  python3 audit_sku_format_formula.py <file_formula.xlsx> <folder_listing...>
"""
import sys, os, glob, re, warnings
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import formula_config as FC

# arahkan config ke file referensi yang dipakai sesi ini SEBELUM modul lain
# memuatnya di level modul. Nilai default argumen `load(path=FORMULA_XLSX)`
# sudah terikat saat fungsi didefinisikan, jadi mengganti atribut modul saja
# tidak cukup -- default-nya ikut ditimpa.
FORMULA_PATH = sys.argv[1]
FC.FORMULA_XLSX = FORMULA_PATH
FC.load.__defaults__ = (FORMULA_PATH,)

import apply_formula_sku as AF   # noqa: E402  (harus setelah patch di atas)

CFG, BLOCKED = FC.load(FORMULA_PATH)
AF.CFG, AF.BLOCKED = CFG, BLOCKED
AF.CFG_SIG = {m: AF._sig(m) for m in CFG}
AF.CFG_TOK = {m: set(AF._toks(m)) for m in CFG}
AF.BLK_SIG = {m: AF._sig(m) for m in BLOCKED}
AF.BLK_TOK = {m: set(AF._toks(m)) for m in BLOCKED}
AF._cache = {}

MASTERFMT = AF.MASTERFMT

# kolom Shopee: nama=2, varian=4, sku=6 ; data mulai baris 7
NAMA, VAR, SKU, START = 2, 4, 6, 7

# produk di luar cakupan cover mobil -- aturan bisnis #6, kalau ikut dicocokkan
# judulnya yang kebetulan menyebut nama mobil akan salah match
LUAR_SCOPE = ('karpet', 'cover motor', 'travel pouch', 'pouch')


def baca(folders):
    rows = []
    for f in folders:
        for path in sorted(glob.glob(os.path.join(f, '*.xlsx'))):
            from openpyxl import load_workbook
            ws = load_workbook(path, data_only=True)['Sheet1']
            for r in range(START, ws.max_row + 1):
                nm = ws.cell(row=r, column=NAMA).value
                if not nm:
                    continue
                rows.append((os.path.basename(path), r, str(nm),
                             str(ws.cell(row=r, column=VAR).value or ''),
                             ws.cell(row=r, column=SKU).value))
    return rows


def audit(rows):
    fmt = Counter()
    contoh_lama = Counter()
    for _, _, nm, var, sku in rows:
        s = str(sku).strip() if sku not in (None, '') else ''
        if not s:
            fmt['kosong'] += 1
        elif MASTERFMT.match(s):
            fmt['format_master'] += 1
        else:
            fmt['format_lama'] += 1
            contoh_lama[s.split('-')[0][:12]] += 1
    return fmt, contoh_lama


def cek_formula(rows):
    """bandingkan segmen generasi aktual vs yang seharusnya menurut skema formula"""
    per_model = defaultdict(lambda: Counter())
    detail_salah = defaultdict(Counter)
    tak_kenal = Counter()

    for fn, r, nm, var, sku in rows:
        low = nm.lower()
        if any(k in low for k in LUAR_SCOPE):
            continue
        s = str(sku).strip() if sku not in (None, '') else ''
        model, tag = AF.match_model(nm)
        if model is None:
            tak_kenal[nm] += 1
            continue
        if tag == 'blocked':
            per_model[model]['ditunda'] += 1
            continue
        if not s:
            per_model[model]['sku_kosong'] += 1
            continue
        if not MASTERFMT.match(s):
            per_model[model]['format_lama'] += 1
            continue

        aktual = s.split('-')[4]
        harus = FC.seg_for_variant(CFG[model], var)
        if harus is None:
            per_model[model]['tak_tentu'] += 1
        elif aktual.upper() == harus.upper():
            per_model[model]['sesuai'] += 1
        else:
            per_model[model]['tidak_sesuai'] += 1
            detail_salah[model][f'{aktual} -> {harus}'] += 1

    return per_model, detail_salah, tak_kenal


if __name__ == '__main__':
    folders = sys.argv[2:]
    rows = baca(folders)
    print(f'Total baris varian dibaca: {len(rows):,}\n')

    fmt, contoh_lama = audit(rows)
    tot = sum(fmt.values())
    print('=== A. STATUS FORMAT SKU ===')
    for k, label in [('format_master', 'Sudah format terbaru'),
                     ('format_lama', 'Masih format lama'),
                     ('kosong', 'SKU kosong')]:
        n = fmt.get(k, 0)
        print(f'  {label:24s} {n:6,}  ({n/tot*100:5.1f}%)')
    if contoh_lama:
        print('  contoh awalan kode lama:', dict(contoh_lama.most_common(6)))

    per_model, detail_salah, tak_kenal = cek_formula(rows)
    print(f'\n=== B. KESESUAIAN FORMULA ({len(CFG)} model referensi siap dicek) ===')

    ada = {m: c for m, c in per_model.items() if m in CFG}
    bersih, bermasalah = [], []
    for m, c in ada.items():
        if c.get('tidak_sesuai', 0) == 0:
            bersih.append(m)
        else:
            bermasalah.append((c['tidak_sesuai'], m, c))

    n_cek = sum(sum(c.values()) for c in ada.values())
    agg = Counter()
    for c in ada.values():
        agg.update(c)
    print(f'  Model referensi yang ketemu di listing : {len(ada)} / {len(CFG)}')
    print(f'  Model yang SEMUA SKU-nya sudah sesuai  : {len(bersih)}')
    print(f'  Model yang masih ada yang tidak sesuai : {len(bermasalah)}')
    print(f'\n  Rincian baris ({n_cek:,} baris di model referensi):')
    for k, label in [('sesuai', 'Sudah sesuai formula'),
                     ('tidak_sesuai', 'TIDAK sesuai formula'),
                     ('tak_tentu', 'Tak bisa ditentukan (varian generik/ambigu)'),
                     ('sku_kosong', 'SKU kosong'),
                     ('format_lama', 'Format lama'),
                     ('ditunda', 'Model ditunda (aturan belum final)')]:
        n = agg.get(k, 0)
        if n:
            print(f'    {label:44s} {n:6,}  ({n/n_cek*100:5.1f}%)')

    if bermasalah:
        bermasalah.sort(reverse=True)
        print(f'\n  Model dengan SKU tidak sesuai (urut terbanyak):')
        for n, m, c in bermasalah:
            pola = ', '.join(f'{k} ({v}x)' for k, v in detail_salah[m].most_common(3))
            print(f'    {n:5,} baris  {m:32s} {pola}')

    hilang = sorted(set(CFG) - set(ada))
    if hilang:
        print(f'\n  Model referensi TIDAK ketemu di listing ini: {len(hilang)}')
        print('   ', ', '.join(hilang[:12]) + (' ...' if len(hilang) > 12 else ''))

    if BLOCKED:
        print(f'\n  Model sengaja DITUNDA (aturan belum final): {len(BLOCKED)}')
        for k, v in BLOCKED.items():
            print(f'    - {k}: {v}')
