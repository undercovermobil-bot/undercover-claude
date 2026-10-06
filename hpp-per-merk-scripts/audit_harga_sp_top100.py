# -*- coding: utf-8 -*-
"""
Audit read-only harga listing Smartprotection (SP) terhadap harga terbaru
yang pernah diformulasikan, sekaligus menandai tiap produk masuk/tidak
daftar top-100 SKU baseline Q3 2026 (project-undercover-top100-sku-2026Q3.md).
Dibuat 2026-10-06: user mau tahu berapa produk SP yang sudah harga terbaru,
sebagai bahan merampingkan katalog SP seperti Undercover.

Target harga (dihitung ULANG dari skrip asli, tidak ditebak):
- Signature Waterproof (varian warna dasar = R, Epic/Elite/Warrior = S):
  Reguler = "Harga Baru (Reguler)" dari harga_baru_sp_op_matriks_v3.py
  (HPP STP OTP, 291 model, kalibrasi dikunci, top-10 lantai);
  Strip = Reguler + Rp43.000.
- Transparan Anti Air: formula update_harga_transparan_sp.py (196rb kecil /
  431rb besar, ambang Fortuner 4795mm, Innova dipaksa besar, kalibrasi
  dikunci dari 100 model Top-Terlaris) + ESTIMASI_MM dari
  estimasi_15_model_transparan.py.

Model dikenali dari JUDUL (sama seperti skrip update aslinya), keanggotaan
top-100 dari PREFIX SKU (definisi resmi top-100 = per SKU).

Pemakaian:
  KERJA_DIR=<folder> python3 audit_harga_sp_top100.py <shopee1.xlsx> <shopee2.xlsx> <tiktok.xlsx>
  KERJA_DIR berisi 'Harga Baru SP-OP (matriks) v3.xlsx' dan
  'Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx'. Hasil: KERJA_DIR/AUDIT_HARGA_SP_TOP100.xlsx
"""
import os, re, sys, pickle, warnings
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
warnings.filterwarnings('ignore')
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
import audit_dan_isi_sku_otoprotection as op_audit
import harga_baru_sp_op_matriks_v2 as m
import update_harga_transparan_sp as tr
from estimasi_15_model_transparan import ESTIMASI_MM
from update_harga_per_sku import ALIAS as ALIAS_UA

S = os.environ.get('KERJA_DIR', '.')
STRIP = 43000
MEM_TOP100 = os.path.join(HERE, '..', 'claude-memory', 'project-undercover-top100-sku-2026Q3.md')

# prefix listing -> kunci top-100 (kembar & nama prefix lama)
ALIAS_TOP = dict(ALIAS_UA)
ALIAS_TOP.update({'DHT-LXO': 'DHT-GMX', 'TYT-HAL': 'TYT-HAC', 'MZD-MZ2': 'MZD-2H',
                  'SZK-GVT': 'SZK-VITARA', 'SZK-GVH': 'SZK-VITARA', 'SZK-EVT': 'SZK-VITARA'})

TIPE_RE = re.compile(r'\s+(signature waterproof|transparan anti air|transparan)\b.*$', re.I)


def top100():
    s = open(MEM_TOP100, encoding='utf-8').read()
    rows = re.findall(r'^\| (\d+) \| `([A-Z0-9-]+)` \| ([^|]+) \| ([\d.]+) \|', s, re.M)
    assert len(rows) == 100, len(rows)
    return {k: (int(n), nm.strip()) for n, k, nm, _ in rows}


def target_signature():
    ws = openpyxl.load_workbook(f'{S}/Harga Baru SP-OP (matriks) v3.xlsx', data_only=True)['Harga Baru SP-OP']
    return {ws.cell(r, 2).value: int(ws.cell(r, 7).value) for r in range(2, ws.max_row + 1) if ws.cell(r, 2).value}


def target_transparan():
    wsrc = openpyxl.load_workbook(f'{S}/Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx', data_only=True)['Top 100 Terlaris']
    t100 = [wsrc.cell(r, 1).value for r in range(2, wsrc.max_row + 1) if wsrc.cell(r, 1).value]
    kecil = tr.kalibrasi_grup([m.PANJANG_MM[n] for n in t100 if m.PANJANG_MM[n] < tr.AMBANG_MM and n not in tr.PAKSA_BESAR])
    besar = tr.kalibrasi_grup([m.PANJANG_MM[n] for n in t100 if m.PANJANG_MM[n] >= tr.AMBANG_MM and n not in tr.PAKSA_BESAR])
    def harga(panjang, paksa_besar=False):
        if panjang >= tr.AMBANG_MM or paksa_besar:
            return tr.LANTAI_BESAR + tr.posisi(panjang, besar)
        return tr.LANTAI_KECIL + tr.posisi(panjang, kecil)
    out = {k: harga(p, k in tr.PAKSA_BESAR) for k, p in m.PANJANG_MM.items()}
    est = {k: harga(p) for k, (p, _) in ESTIMASI_MM.items()}
    return out, est


TYPO_TIER = [(re.compile(r'^\s*(eltie|elita|elit)\b', re.I), 'Elite'), (re.compile(r'^\s*epik\b', re.I), 'Epic')]


def tier_baris(x):
    """R (warna dasar) / S (Epic/Elite/Warrior) dari teks varian, toleran typo;
    fallback segmen ke-4 SKU."""
    v = str(x['var'] or '')
    for pat, rep in TYPO_TIER:
        v = pat.sub(rep, v)
    tier, _ = op_audit.tier_warna_sp(v)
    if tier is None:
        b = str(x['sku'] or '').split('-')
        tier = b[3].upper() if len(b) >= 6 and b[3].upper() in ('R', 'S') else None
    return tier


def nama_dasar(title):
    t = re.split(r'\s+-\s+smartprotection\b', str(title), flags=re.I)[0]
    t = op_audit.PREFIX_RE.sub('', t)
    t = TIPE_RE.sub('', t)
    t = op_audit.PREFIX_TRANSPARAN_RE.sub('', t).strip()
    for pat, rep in op_audit.TYPO_FIX:
        t = pat.sub(rep, t)
    return t


def baca(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]; ws.reset_dimensions()
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(x) for x in rows[0]]
    if 'et_title_product_name' in hdr:
        ch, start = 'shopee', 6
        c = {k: hdr.index(v) for k, v in dict(pid='et_title_product_id', nm='et_title_product_name', var='et_title_variation_name',
                                                sku='et_title_variation_sku', h='et_title_variation_price').items()}
    else:
        ch, start = 'tiktok', 5
        c = {k: hdr.index(v) for k, v in dict(pid='product_id', nm='product_name', var='variation_value',
                                                sku='seller_sku', h='price').items()}
    out = []
    for r in rows[start:]:
        if not r[c['nm']]:
            continue
        out.append({k: r[i] for k, i in c.items()})
    return ch, out


def main(paths):
    T100 = top100()
    def kunci_nama(x):
        x = re.sub(r'\([^)]*\)', '', str(x))          # buang keterangan "(baru)", "(F70 lama)", dst.
        return re.sub(r'[^a-z0-9]', '', x.lower())
    nama_top = {}
    for k, (_, nm) in sorted(T100.items(), key=lambda kv: kv[1][0]):
        for x in nm.split(' / '):
            nama_top.setdefault(kunci_nama(x), k)
    sig = target_signature()
    trp, est = target_transparan()
    est_norm = {op_audit.norm(k): k for k in est}
    idx = tr.build_index()

    produk = {}   # (ch, pid) -> info
    for p in paths:
        ch, rows = baca(p)
        for x in rows:
            key = (ch, str(x['pid']))
            pr = produk.setdefault(key, {'ch': ch, 'pid': str(x['pid']), 'nm': str(x['nm']), 'rows': []})
            pr['rows'].append(x)

    # pass 1: kenali model dari judul; peta prefix SKU -> model utk judul yg tak dikenali
    for pr in produk.values():
        pr['tipe'] = 'Transparan' if re.search(r'transparan', pr['nm'], re.I) else 'Signature'
        pr['base'] = nama_dasar(pr['nm'])
        pr['model0'] = tr.resolve_model(pr['base'], idx)
        pr['pfx0'] = Counter('-'.join(str(x['sku']).strip().split('-')[:2]).upper() for x in pr['rows']
                             if x['sku'] and len(str(x['sku']).split('-')) >= 6)
    model_by_pfx = defaultdict(Counter)
    for pr in produk.values():
        if pr['model0'] and pr['pfx0']:
            model_by_pfx[pr['pfx0'].most_common(1)[0][0]][pr['model0']] += 1

    for pr in produk.values():
        t = pr['nm']
        base = pr['base']
        model = pr['model0']
        sumber = None
        lewat_sku = False
        if not model and pr['pfx0']:
            cand = model_by_pfx.get(pr['pfx0'].most_common(1)[0][0])
            if cand and len(cand) == 1:   # prefix SKU-nya cuma dipakai 1 model -> aman
                model = next(iter(cand)); lewat_sku = True
        if pr['tipe'] == 'Transparan':
            if model and model in trp:
                sumber = 'formula Transparan'
            elif op_audit.norm(base) in est_norm:
                model = est_norm[op_audit.norm(base)]; sumber = 'estimasi Transparan'
        else:
            if model and model in sig:
                sumber = 'matriks SP-OP v3'
            else:
                model = None
        if sumber and lewat_sku:
            sumber += ' (model dikenali lewat SKU)'
        pr['model'], pr['sumber'] = model, sumber
        # keanggotaan top-100 lewat prefix SKU
        pfx = Counter()
        for x in pr['rows']:
            b = str(x['sku'] or '').strip().split('-')
            if len(b) >= 6:
                k = '-'.join(b[:2]).upper()
                pfx[ALIAS_TOP.get(k, k)] += 1
        pr['prefix'] = '/'.join(k for k, _ in pfx.most_common())
        keys = [k for k in pfx if k in T100]
        dasar = 'SKU'
        if not pfx:
            calon = [base] + ([model] + model.split(' / ') if model else [])
            k = next((nama_top[kunci_nama(c)] for c in calon if kunci_nama(c) in nama_top), None)
            keys = [k] if k else []
            dasar = 'nama (tanpa SKU)'
        pr['top_keys'] = keys
        pr['rank'] = min((T100[k][0] for k in keys), default=None)
        pr['top100'] = 'Masuk top-100' if keys else 'Di luar top-100'
        pr['dasar_top'] = dasar
        # cek harga per baris
        ok = salah = tak_kenal = 0
        live = Counter(); tgt_set = set()
        for x in pr['rows']:
            try:
                h = int(float(x['h']))
            except (TypeError, ValueError):
                h = None
            live[h] += 1
            if not sumber:
                continue
            if pr['tipe'] == 'Transparan':
                tgt = trp[model] if sumber == 'formula Transparan' else est[model]
            else:
                tier = tier_baris(x)
                if tier is None:
                    tak_kenal += 1; continue
                tgt = sig[model] + (STRIP if tier == 'S' else 0)
            tgt_set.add(tgt)
            if h == tgt:
                ok += 1
            else:
                salah += 1
        pr['ok'], pr['salah'], pr['tak_kenal'] = ok, salah, tak_kenal
        pr['live'] = ', '.join(f'{k:,}' for k, _ in live.most_common() if k)
        pr['target'] = ', '.join(f'{k:,}' for k in sorted(tgt_set))
        if not sumber:
            pr['status'] = 'TANPA TARGET'
        elif salah == 0 and ok:
            pr['status'] = 'SUDAH'
        elif ok == 0:
            pr['status'] = 'BELUM'
        else:
            pr['status'] = 'SEBAGIAN'

    # pass 2: SKU kembar (1 SKU = 1 cover = 1 harga). Produk yg harganya belum
    # cocok dgn target namanya sendiri tapi SAMA PERSIS dgn kembaran yg sudah
    # benar (prefix SKU utama sama, tipe & channel sama) -> dianggap sudah.
    utama = defaultdict(list)
    for pr in produk.values():
        if pr['pfx0']:
            k = pr['pfx0'].most_common(1)[0][0]
            utama[(pr['ch'], pr['tipe'], ALIAS_TOP.get(k, k))].append(pr)
        elif pr['top_keys']:   # listing tanpa SKU: kembar dikenali dari nama di daftar top-100
            utama[(pr['ch'], pr['tipe'], pr['top_keys'][0])].append(pr)
    def harga_per_tier(pr):
        out = defaultdict(set)
        for x in pr['rows']:
            tier = tier_baris(x) if pr['tipe'] == 'Signature' else 'T'
            try:
                out[tier or '?'].add(int(float(x['h'])))
            except (TypeError, ValueError):
                pass
        return out
    for L in utama.values():
        benar = [q for q in L if q['status'] == 'SUDAH']
        for pr in L:
            if pr['status'] in ('SUDAH',) or not benar:
                continue
            hp = harga_per_tier(pr)
            for q in benar:
                hq = harga_per_tier(q)
                if all(len(v) == 1 for v in hp.values()) and all(hp[k] == hq.get(k) for k in hp):
                    pr['status'] = 'SUDAH'
                    pr['sumber'] = f"ikut kembar {q['base']} (SKU sama)"
                    pr['target'] = q['target']
                    break

    pickle.dump({'produk': produk, 'top100': T100}, open(f'{S}/audit_harga_sp_top100.pkl', 'wb'))
    tulis_xlsx(produk, T100)
    laporan(produk, T100)


def laporan(produk, T100):
    for ch in ('shopee', 'tiktok'):
        P = [p for p in produk.values() if p['ch'] == ch]
        print(f'\n========== {ch.upper()}: {len(P)} produk ==========')
        c = Counter((p['top100'], p['tipe'], p['status']) for p in P)
        for k in sorted(c):
            print(f'  {k[0]:16} {k[1]:11} {k[2]:13} {c[k]:4}')
        c2 = Counter((p['tipe'], p['status']) for p in P)
        print('  -- total per tipe/status:', dict(sorted(c2.items())))
        keys_ada = defaultdict(set)
        for p in P:
            for k in p['top_keys']:
                keys_ada[k].add(p['tipe'])
        tak_ada = [k for k in T100 if k not in keys_ada]
        print(f'  SKU top-100 yg punya listing: {len(keys_ada)}/100; tak ada listing: {tak_ada}')
        print(f'  SKU top-100 tanpa Signature: {[k for k in T100 if k in keys_ada and "Signature" not in keys_ada[k]]}')
        print(f'  SKU top-100 tanpa Transparan: {[k for k in T100 if k in keys_ada and "Transparan" not in keys_ada[k]]}')
        for st in ('BELUM', 'SEBAGIAN', 'TANPA TARGET'):
            L = sorted((p['rank'] or 999, p['tipe'], p['base'], p['live'], p['target'], p['ok'], p['salah']) for p in P
                       if p['status'] == st and p['top100'] == 'Masuk top-100')
            if L:
                print(f'  -- top-100 {st}:')
                for x in L:
                    print(f'     #{x[0]:>3} {x[1]:10} {x[2][:34]:34} live={x[3]} target={x[4]} ok={x[5]} salah={x[6]}')


def tulis_xlsx(produk, T100):
    wb = openpyxl.Workbook()
    HDR = PatternFill('solid', fgColor='FFC000'); B = Font(bold=True)
    WARNA = {'SUDAH': 'C6EFCE', 'BELUM': 'FFC7CE', 'SEBAGIAN': 'FFEB9C', 'TANPA TARGET': 'D9D9D9'}
    first = True
    for ch in ('shopee', 'tiktok'):
        ws = wb.active if first else wb.create_sheet()
        first = False
        ws.title = f'{ch.capitalize()} per Produk'
        kol = ['Kode Produk', 'Nama Produk', 'Tipe', 'Model (dikenali)', 'Prefix SKU', 'Top-100', 'Rank top-100',
               'Status Harga', 'Baris cocok', 'Baris beda', 'Harga live', 'Harga terbaru (target)', 'Sumber target']
        for i, h in enumerate(kol, 1):
            c = ws.cell(1, i, h); c.fill = HDR; c.font = B; c.alignment = Alignment(wrap_text=True)
        P = sorted((p for p in produk.values() if p['ch'] == ch), key=lambda p: (p['top100'] != 'Masuk top-100', p['rank'] or 999, p['base'], p['tipe']))
        for r, p in enumerate(P, 2):
            vals = [p['pid'], p['nm'], p['tipe'], p['model'] or p['base'], p['prefix'], p['top100'], p['rank'],
                    p['status'], p['ok'], p['salah'], p['live'], p['target'], p['sumber'] or '-']
            for i, v in enumerate(vals, 1):
                ws.cell(r, i, v)
            ws.cell(r, 8).fill = PatternFill('solid', fgColor=WARNA[p['status']])
        for col, w in zip('ABCDEFGHIJKLM', [14, 60, 11, 30, 20, 15, 8, 13, 8, 8, 22, 22, 20]):
            ws.column_dimensions[col].width = w
        ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
    # ---- Ringkasan: rumus COUNTIFS ke sheet per produk (nilai ditanam inject_cache.py) ----
    rk = wb.create_sheet('Ringkasan', 0)
    rk['A1'] = 'Status harga listing Smartprotection vs harga terbaru + daftar top-100 SKU (baseline Q3 2026)'
    rk['A1'].font = Font(bold=True, size=12)
    STATUS = ['SUDAH', 'BELUM', 'SEBAGIAN', 'TANPA TARGET']
    r = 3
    for ch in ('shopee', 'tiktok'):
        sh = f"'{ch.capitalize()} per Produk'"
        n = sum(1 for p in produk.values() if p['ch'] == ch) + 1
        rng = lambda col: f'{sh}!${col}$2:${col}${n}'
        rk.cell(r, 1, ch.capitalize()).font = Font(bold=True, size=11)
        r += 1
        for i, h in enumerate(['Kelompok', 'Tipe'] + STATUS + ['Total'], 1):
            c = rk.cell(r, i, h); c.fill = HDR; c.font = B
        r0 = r + 1
        for kel in ('Masuk top-100', 'Di luar top-100'):
            for tipe in ('Signature', 'Transparan'):
                r += 1
                rk.cell(r, 1, kel); rk.cell(r, 2, tipe)
                for j, st in enumerate(STATUS):
                    col = openpyxl.utils.get_column_letter(3 + j)
                    rk.cell(r, 3 + j, f'=COUNTIFS({rng("F")},$A{r},{rng("C")},$B{r},{rng("H")},{col}${r0 - 1})')
                rk.cell(r, 7, f'=SUM(C{r}:F{r})')
        r += 1
        rk.cell(r, 1, 'Total').font = B
        for j in range(5):
            col = openpyxl.utils.get_column_letter(3 + j)
            rk.cell(r, 3 + j, f'=SUM({col}{r0}:{col}{r - 1})').font = B
        r += 2
    catatan = [
        'Target harga: Signature = matriks SP-OP v3 (HPP STP OTP, Strip = Reguler + Rp43.000); Transparan = formula Transparan (196rb/431rb, ambang Fortuner).',
        'Mobil kembar (1 SKU = 1 harga) dihitung SUDAH bila harganya sama dengan kembaran yang sudah benar: Veloz ikut Avanza 370rb, Gran Max Minibus ikut Luxio 371rb (keputusan user 2026-09-10), Taft GT ikut Feroza 370rb.',
        'TANPA TARGET = model yang tidak ada di file HPP STP OTP (harga barunya memang belum pernah dihitung).',
        'Top-100 = daftar resmi 100 SKU Undercover (baseline Q3 2026); keanggotaan dari prefix SKU, atau nama untuk listing yang belum ber-SKU.',
    ]
    for t in catatan:
        rk.cell(r, 1, t); r += 1
    for col, w in zip('ABCDEFG', [18, 12, 10, 10, 11, 14, 9]):
        rk.column_dimensions[col].width = w
    wb.save(f'{S}/AUDIT_HARGA_SP_TOP100.xlsx')


if __name__ == '__main__':
    main(sys.argv[1:])
