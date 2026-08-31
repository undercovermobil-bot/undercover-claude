#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit & isi SKU kosong/legacy utk listing Otoprotection (OP), 2026-08-29.

Beda mendasar dari audit Smartprotection (SP): token TOKO di SKU utk OP
BUKAN "OP" tapi "SP" (rule #1 sku-sync-rules.md: konsolidasi stok fisik
OP=SP, `TARGET_STORE = {..., OP:SP, SP:SP}`, dibake ke master sejak
2026-07-08). Jadi SKU yang benar utk OP itu SAMA PERSIS dgn SKU SP utk
kombinasi produk+tier+warna+generasi yg sama - bukan ditebak/diturunkan
terpisah. Prioritas isi SKU kosong/legacy OP:
1. Cocokkan ke data SP yang SUDAH terbukti benar (sp_sku_fixed/1-2.xlsx,
   digabung dengan hasil audit 439-row final_sku_fill7.pkl).
2. Kalau produk itu 0 di SP juga, pakai data OP sendiri (baris lain
   produk yg sama yg sudah py SKU modern valid).
3. Beberapa fallback umum (bukan tebakan generik, semua berbasis preseden
   yg SUDAH dikonfirmasi user di proyek ini):
   - `ambiguous_pick_earliest_gen`/`earliest_base_new_combo`: listing OP
     sering TIDAK memecah varian per generasi (user: "otoprotection ini
     varian produknya lebih sedikit") - preseden Nissan X-Trail yg sudah
     dikonfirmasi user: label gabungan/tanpa info generasi pakai kode
     generasi PALING AWAL/TERENDAH.
   - `uniform_base_new_combo`: produk TF=1 (semua kode SKU-nya sama
     lintas tier/warna) - kombinasi tier+warna yg belum pernah tercatat
     di manapun aman diisi kode yg sama.
4. Kasus KHUSUS (SPECIAL_CASES, hasil tanya-jawab eksplisit dgn user
   2026-08-29 - JANGAN diubah tanpa instruksi baru):
   - "Toyota Altis" (OP, 15 baris, semua kosong, TANPA info generasi sama
     sekali) = Toyota Corolla Altis, dikonfirmasi user SAMA DENGAN Toyota
     Corolla generasi ke-9 (bukan "generasi paling awal Corolla" G7 -
     Altis sbg nama trim baru dipakai mulai Gen 9). Prefix pinjam dari
     Corolla (TYT-CRL), kode generasi G9 SERAGAM (user konfirmasi listing
     OP cuma py 1 generasi varian).
   - "Nissan Latio", "Wuling Alvez", "Wuling Darion": 0 data SAMA SEKALI
     di SP maupun OP (prefix belum pernah ada) - user eksplisit minta
     dibuatkan prefix baru (2026-08-29), dipakai jg utk isi baris SP yg
     SAMA (Latio & Darion TERNYATA juga ada listingnya blank total di SP,
     ditemukan user: "wuling darion aku lihat ada produknya juga di toko
     smartprotection" - Latio juga ketemu blank total di SP saat verifikasi).
     Prefix ikuti konvensi 3-huruf brand+3-huruf model yg sudah dipakai
     puluhan model lain (dicek 0 tabrakan ke SEMUA prefix SP eksisting):
       - Nissan Latio -> NSN-LAT (2 generasi asli TANPA teks "Gen N",
         cuma rentang tahun bare: "2004-2012"->G1, "2014-2016"->G2,
         urutan kronologis paling awal=G1 preseden X-Trail; baris "Tahun
         Lain" TETAP dilewati sesuai aturan #4 sku-sync-rules.md)
       - Wuling Alvez -> WLG-ALV (TF=1, dikonfirmasi via
         Data_Mobil_Lebih_dari_1_Formula_3.xlsx Sheet2: "Wuling Alvez"
         Total Formula=1 - G1 seragam)
       - Wuling Darion -> WLG-DAR (TF=1 by inspection: SEMUA baris listing
         cuma py 1 label "Gen 1", tidak ada di file formula tapi tidak
         ada generasi lain yg terlihat di listing manapun - G1 seragam)

Pemakaian: python3 audit_dan_isi_sku_otoprotection.py
    (path OP/SP source di-hardcode di bawah - sesuaikan kalau dipakai
    ulang; baca final_sku_fill7.pkl dari audit SP sebelumnya)
"""
import re
import pickle
from collections import defaultdict

import openpyxl

SP_FILES = ["sp_sku_fixed/1.xlsx", "sp_sku_fixed/2.xlsx"]
OP_FILES = ["op_src/fixed/1.xlsx", "op_src/fixed/2.xlsx"]
FINAL_SKU_FILL_PKL = "final_sku_fill7.pkl"

PREFIX_RE = re.compile(
    r'^(Body\s+)?(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut(\s+Mobil)?)'
    r'(\s*/\s*(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut(\s+Mobil)?))*\s+', re.IGNORECASE)
SUFFIX_TRANSPARAN_RE = re.compile(r'\s+Transparan$', re.IGNORECASE)
PREFIX_TRANSPARAN_RE = re.compile(r'^Transparan\s+', re.IGNORECASE)
TYPO_FIX = [(re.compile(r'\bMitshubishi\b', re.IGNORECASE), 'Mitsubishi'),
            (re.compile(r'\bMistubishi\b', re.IGNORECASE), 'Mitsubishi'),
            (re.compile(r'\bVolkkswagen\b', re.IGNORECASE), 'Volkswagen')]


def is_transparan_product(nm):
    """OP py 2 pola: suffix '...X Transparan' (spt SP) DAN prefix
    '(Cover Mobil) Transparan X' (produk cover transparan tersendiri -
    warna/tier tidak berlaku, selalu di luar scope skema SKU warna/tier)."""
    if SUFFIX_TRANSPARAN_RE.search(nm):
        return True
    return bool(PREFIX_TRANSPARAN_RE.match(PREFIX_RE.sub('', nm)))


def clean_base(nm):
    nm = SUFFIX_TRANSPARAN_RE.sub('', PREFIX_RE.sub('', nm)).strip()
    for pat, rep in TYPO_FIX:
        nm = pat.sub(rep, nm)
    return nm


def clean_base_transparan(nm):
    """clean_base() cuma strip pola SUFFIX '...X Transparan' (gaya SP) -
    utk produk Transparan sendiri, base name jg perlu strip pola PREFIX
    'Transparan X' (gaya OP) supaya KEDUA gaya penamaan normalize ke nama
    mobil yg SAMA (mis. 'Cover Mobil Transparan Mercedes Benz G Class'
    dan 'Mercedes Benz G Class Transparan' harus jadi bn yg sama)."""
    nm = PREFIX_RE.sub('', nm)
    nm = SUFFIX_TRANSPARAN_RE.sub('', nm)
    nm = PREFIX_TRANSPARAN_RE.sub('', nm)
    nm = nm.strip()
    for pat, rep in TYPO_FIX:
        nm = pat.sub(rep, nm)
    return nm


def gen_and_leftover_transparan(variant):
    """Beda dari gen_and_leftover() biasa: produk Transparan TIDAK py
    axis warna/tier sama sekali (selalu 1 warna: transparan) jadi teks
    varian TIDAK diawali 'warna,' spt Reguler/Strip - kadang cuma
    'Gen 1 : 2015-2022', kadang cuma trim/sub-model tanpa gen sama
    sekali (mis. 'Navara PRO-4X'), kadang cuma 'Default'. Proses SELURUH
    teks varian langsung (bukan potong stlh koma dulu)."""
    rest = variant.strip()
    m = GEN_RE.search(rest)
    gen = m.group(1) if m else None
    if gen is not None:
        leftover = YEAR_RE.sub('', GEN_RE.sub('', rest))
    else:
        leftover = rest
    return gen, re.sub(r'[^a-z0-9]', '', leftover.lower())


TRANSPARAN_SOURCES = [
    ("sp_sku_fixed/1.xlsx", "Sheet1", 2, 4, 6, 7),
    ("sp_sku_fixed/2.xlsx", "Sheet1", 2, 4, 6, 7),
    ("op_src/fixed/1.xlsx", "Sheet1", 2, 4, 6, 7),
    ("op_src/fixed/2.xlsx", "Sheet1", 2, 4, 6, 7),
    ("sp_lazada_tiktok_src/lazada.xlsx", "template", 3, 14, 13, 5),
    ("sp_lazada_tiktok_src/tiktok.xlsx", "Template", 3, 6, 11, 6),
    ("op_src/tiktok1.xlsx", "Template", 3, 6, 11, 6),
    ("op_src/tiktok2.xlsx", "Template", 3, 6, 11, 6),
]


def build_transparan_master():
    """Referensi SKU Transparan (kategori tetap 'T', 'warna' tetap 'TRP'
    krn tidak py axis warna) - digabung dari SEMUA sumber SEKALIGUS
    (Shopee SP+OP, Lazada SP, TikTok SP+OP), BEDA dari build_sp_master()
    yg cuma scan Shopee SP - krn coverage Transparan per-platform jauh
    lebih jarang/timpang drpd Reguler/Strip (banyak produk cuma py
    Transparan valid di 1 platform doang, lihat investigasi 2026-08-31)."""
    master = defaultdict(set)
    base_display = {}
    for path, sheet, namecol, varcol, skucol, startrow in TRANSPARAN_SOURCES:
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
        except FileNotFoundError:
            continue
        ws = wb[sheet]
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm or not is_transparan_product(nm):
                continue
            variant = ws.cell(r, varcol).value
            if not variant:
                continue
            sku = ws.cell(r, skucol).value
            if not sku or not str(sku).strip():
                continue
            segs = str(sku).split('-')
            if len(segs) != 6 or segs[2] != 'SP' or segs[3] != 'T':
                continue
            base = clean_base_transparan(nm)
            bn = norm(base)
            base_display[bn] = base
            gen, leftover = gen_and_leftover_transparan(variant)
            master[(bn, 'T', 'TRP')].add((gen, leftover, sku))
    return master, base_display


REGULAR_STRIP_SOURCES = [
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 4, 6, 7),
    ("UPDATE_SKU_HARGA_OTOPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx", "template", 3, 14, 13, 5),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_TIKTOK.xlsx", "Template", 3, 6, 11, 6),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_1.xlsx", "Template", 3, 6, 11, 6),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx", "Template", 3, 6, 11, 6),
]


def build_model_gen_map():
    """Peta (bn -> {nomor_gen_asli: kode_gen}), diturunkan dari baris
    Reguler/Strip yg SUDAH FINAL (pasca SEMUA koreksi sesi ini: bucket-fix,
    Elantra sync, Lexus LX, Total Formula Corolla/Civic Type R/Mazda 2
    Sedan, dst) - dipakai utk isi kode generasi Transparan produk yg 0
    referensi Transparan-nya SENDIRI di semua platform (investigasi user
    2026-08-31: 'apa tidak bisa disesuaikan dari format Reguler/Strip yg
    baru?'). Prinsipnya: kode generasi itu properti FISIK MOBIL, bukan
    milik tier - Corolla Gen 3 kodenya G3 baik itu Reguler, Strip, ATAU
    Transparan, jadi aman diturunkan lintas tier utk model yg SAMA."""
    m = defaultdict(lambda: defaultdict(set))
    prefix_by_bn = {}
    for fname, sheet, namecol, varcol, skucol, startrow in REGULAR_STRIP_SOURCES:
        try:
            wb = openpyxl.load_workbook(fname, data_only=False)
        except FileNotFoundError:
            continue
        ws = wb[sheet]
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm or is_transparan_product(nm):
                continue
            variant = ws.cell(r, varcol).value
            if not variant:
                continue
            sku = ws.cell(r, skucol).value
            if not sku:
                continue
            segs = str(sku).split('-')
            if len(segs) != 6 or segs[2] != 'SP':
                continue
            gm = GEN_RE.search(variant)
            if not gm:
                continue
            real_gen = gm.group(1)
            base = clean_base(nm)
            bn = norm(base)
            m[bn][real_gen].add(segs[4])
            prefix_by_bn[bn] = ('-'.join(segs[:2]), segs[2])
    gen_map = {}
    for bn, gens in m.items():
        clean = {g: next(iter(codes)) for g, codes in gens.items() if len(codes) == 1}
        if clean:
            gen_map[bn] = clean
    return gen_map, prefix_by_bn


def norm(s):
    s = s.lower().replace('-', '').replace('/', ' ').replace(':', ' ')
    return re.sub(r'\s+', ' ', s).strip()


GEN_RE = re.compile(r'Gen\s*(\d+)', re.IGNORECASE)
YEAR_RE = re.compile(r'\b\d{4}(\s*-\s*\d{4})?\b')


def gen_and_leftover(variant):
    """gen = angka literal "Gen N" kalau ada; leftover = teks sisa setelah
    warna - kalau ADA "Gen N", tahun boleh dibuang (cross-platform lesson
    2026-08-29: tahun bisa beda 1 tahun antar sumber utk generasi yg sama);
    kalau TIDAK ADA "Gen N", tahun WAJIB dipertahankan sbg leftover krn itu
    satu-satunya pembeda generasi (mis. Hyundai Santa Fe "2012-2018"/
    "2018-2022" tanpa kata Gen)."""
    rest = variant.split(',', 1)[1].strip() if ',' in variant else ''
    m = GEN_RE.search(rest)
    gen = m.group(1) if m else None
    if gen is not None:
        leftover = YEAR_RE.sub('', GEN_RE.sub('', rest))
    else:
        leftover = rest
    return gen, re.sub(r'[^a-z0-9]', '', leftover.lower())


WARNA_REGULER = {'abu-abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
                  'merah': 'MRH', 'hijau army': 'GRN', 'orange': 'ORG'}
TIER_STRIP = {'epic': 'S1', 'elite': 'S2', 'warior': 'S3', 'warrior': 'S3'}
WARNA_STRIP = {'abu': 'A', 'biru': 'B', 'merah': 'M'}


def tier_warna_sp(variant):
    """Format Smartprotection: kata tier ('Epic'/'Elite'/'Warior')."""
    color_part = variant.split(',')[0].strip().lower()
    if color_part in WARNA_REGULER:
        return 'R', WARNA_REGULER[color_part]
    words = color_part.split()
    if len(words) == 2 and words[0] in TIER_STRIP and words[1] in WARNA_STRIP:
        return 'S', f"{TIER_STRIP[words[0]]}{WARNA_STRIP[words[1]]}"
    return None, None


def tier_warna_op(variant):
    """Format Otoprotection: literal 'Strip N Warna' (N sudah = nomor
    kode S<N>) - beda dari SP yg pakai nama tier (Epic/Elite/Warior)."""
    color_part = variant.split(',')[0].strip().lower()
    if color_part in WARNA_REGULER:
        return 'R', WARNA_REGULER[color_part]
    m = re.match(r'^strip\s*([123])\s+(abu-abu|abu|biru|merah)$', color_part)
    if m:
        warna_key = 'abu' if m.group(2) == 'abu-abu' else m.group(2)
        return 'S', f"S{m.group(1)}{WARNA_STRIP[warna_key]}"
    return None, None


def expand_slash_aliases(table, base_display):
    """Nama master 'X / Y' (mis. 'Kia Sedona / Carnival') - listing lain
    kadang cuma pakai salah satu bagian. Daftarkan tiap bagian sbg key
    tambahan yg menunjuk ke grup yg SAMA."""
    table = dict(table)
    for bn, disp in list(base_display.items()):
        if ' / ' not in disp:
            continue
        for part in disp.split(' / '):
            part_bn = norm(part.strip())
            if not part_bn or part_bn == bn:
                continue
            for (b2, tier, color), vals in list(table.items()):
                if b2 == bn:
                    key = (part_bn, tier, color)
                    table[key] = table.get(key, set()) | vals
            base_display.setdefault(part_bn, part.strip())
    return table


def build_literal_bases(table):
    """Produk yg SEMUA kode generasinya literal G<n> (1 kode per generasi,
    bukan formula TF>1/grouped) - dideteksi OTOMATIS, bukan hardcode per
    nameplate, supaya generalis & tidak keliru diterapkan ke model yg py
    formula grouped."""
    base_entries = defaultdict(list)
    for (bn, tier, color), vals in table.items():
        for gen, leftover, sku in vals:
            base_entries[bn].append((tier, color, gen, sku))
    literal_bases = {}
    for bn, entries in base_entries.items():
        with_gen = [e for e in entries if e[2] is not None]
        if not with_gen:
            continue
        ok_literal = True
        prefix2_toko = set()
        for tier, color, gen, sku in with_gen:
            segs = sku.split('-')
            if len(segs) != 6 or segs[4] != f"G{gen}":
                ok_literal = False
                break
            prefix2_toko.add(('-'.join(segs[:2]), segs[2]))
        if ok_literal and len(prefix2_toko) == 1:
            literal_bases[bn] = next(iter(prefix2_toko))
    return literal_bases


def build_uniform_bases(table):
    """Produk TF=1 (semua kode SKU lintas tier/warna SAMA PERSIS) - dipakai
    utk isi kombinasi tier+warna yg BELUM PERNAH tercatat di manapun."""
    base_entries = defaultdict(list)
    for (bn, tier, color), vals in table.items():
        for gen, leftover, sku in vals:
            base_entries[bn].append(sku)
    uniform_bases = {}
    for bn, skus in base_entries.items():
        segs_list = [s.split('-') for s in skus]
        if any(len(s) != 6 for s in segs_list):
            continue
        gencodes = set(s[4] for s in segs_list)
        prefix2_toko = set(('-'.join(s[:2]), s[2]) for s in segs_list)
        if len(gencodes) == 1 and len(prefix2_toko) == 1:
            prefix2, toko = next(iter(prefix2_toko))
            uniform_bases[bn] = (prefix2, toko, next(iter(gencodes)))
    return uniform_bases


def build_earliest_bases(table):
    """Perluasan ambiguous_pick_earliest_gen: produk multi-generasi TANPA
    info generasi di teks varian (mis. Toyota 86 warna Orange, Lexus NX
    warna Orange - 0 data sama sekali utk warna itu) - kalau SEMUA grup
    tier+warna produk itu yg py >1 kode sepakat pada 1 kode "paling awal"
    yg sama, jadikan default utk kombinasi yg belum tercatat sama sekali.
    Cocok utk 2 bentuk data sumber: nomor generasi eksplisit ("Gen 1"/
    "Gen 2", urut dari angka) ATAU rentang tahun bare tanpa kata "Gen"
    (urut dari tahun mulai) - grup mana pun boleh pakai salah satu,
    asal konsisten per grup."""
    per_base = defaultdict(set)
    for (bn, tier, color), vals in table.items():
        with_gen = [v for v in vals if v[0] is not None]
        with_year = [v for v in vals if v[0] is None and re.match(r'^\d{4}', v[1])]
        if len(with_gen) >= 2:
            earliest = min(with_gen, key=lambda v: int(v[0]))
        elif len(with_year) >= 2:
            earliest = min(with_year, key=lambda v: int(re.match(r'^(\d{4})', v[1]).group(1)))
        else:
            continue
        segs = earliest[2].split('-')
        if len(segs) == 6:
            per_base[bn].add(('-'.join(segs[:2]), segs[2], segs[4]))
    return {bn: next(iter(c)) for bn, c in per_base.items() if len(c) == 1}


def resolve(table, literal_bases, bn, tier, color, gen, leftover, uniform_bases=None, earliest_bases=None):
    vals = table.get((bn, tier, color))
    if vals:
        if gen is not None:
            matches = [v for v in vals if v[0] == gen]
            if len(matches) == 1:
                return matches[0][2], 'gen_match'
            if len(matches) > 1:
                lm = [v for v in matches if v[1] == leftover]
                if len(lm) == 1:
                    return lm[0][2], 'gen+leftover'
                return None, 'gen_ambiguous'
        else:
            lm = [v for v in vals if v[1] == leftover]
            if len(lm) == 1:
                return lm[0][2], 'leftover_match'
            skus = set(v[2] for v in vals)
            if len(skus) == 1:
                return next(iter(skus)), 'unique_sku'
            # Platform lain (Lazada/TikTok) kadang py TAHUN AKHIR beda tipis
            # utk generasi yg SAMA (mis. Shopee "2008-2022" vs Lazada
            # "2008-2024") - preseden Civic Hatchback Gen10 (lesson
            # 2026-08-29). Cocokkan dari TAHUN AWAL SAJA (4 digit pertama)
            # SEBELUM jatuh ke fallback "pilih paling awal" - jauh lebih
            # presisi drpd asumsi selalu generasi tertua.
            leftover_start = re.match(r'^(\d{4})', leftover)
            if leftover_start:
                ym = [v for v in vals if re.match(r'^(\d{4})', v[1]) and v[1][:4] == leftover_start.group(1)]
                if len(ym) == 1:
                    return ym[0][2], 'leftover_start_year_match'
            others = set(s.rsplit('-', 2)[0] + '-' + s.rsplit('-', 1)[1] for s in skus)
            if len(others) == 1 and len(vals) > 1:
                def start_year(v):
                    m = re.match(r'^(\d{4})', v[1])
                    return int(m.group(1)) if m else 99999999
                best = min(vals, key=start_year)
                if start_year(best) != 99999999:
                    return best[2], 'ambiguous_pick_earliest_gen'
            return None, 'ambiguous_no_gen'
    if gen is not None and bn in literal_bases:
        prefix2, toko = literal_bases[bn]
        return f"{prefix2}-{toko}-{tier}-G{gen}-{color}", 'literal_extrapolated'
    if vals:
        skus = set(v[2] for v in vals)
        if len(skus) == 1:
            return next(iter(skus)), 'gen_not_found_fallback_unique'
        return None, 'gen_not_found_no_fallback'
    if uniform_bases and bn in uniform_bases:
        prefix2, toko, gencode = uniform_bases[bn]
        return f"{prefix2}-{toko}-{tier}-{gencode}-{color}", 'uniform_base_new_combo'
    if gen is None and earliest_bases and bn in earliest_bases:
        prefix2, toko, gencode = earliest_bases[bn]
        return f"{prefix2}-{toko}-{tier}-{gencode}-{color}", 'earliest_base_new_combo'
    return None, 'no_candidate_group'


# Kasus khusus hasil konfirmasi eksplisit user 2026-08-29 (lihat docstring
# modul) - dicek SEBELUM fallback umum, krn 0 data di manapun.
SPECIAL_CASES_UNIFORM = {
    # bn: (prefix2, toko, gencode)
    'toyota altis': ('TYT-CRL', 'SP', 'G9'),
    'wuling alvez': ('WLG-ALV', 'SP', 'G1'),
    'wuling darion': ('WLG-DAR', 'SP', 'G1'),
}
SPECIAL_CASES_CHRONO = {
    # bn: (prefix2, toko, {leftover: gencode})
    'nissan latio': ('NSN-LAT', 'SP', {'20042012': 'G1', '20142016': 'G2'}),
}


def resolve_with_special_cases(table, literal_bases, bn, tier, color, gen, leftover,
                                uniform_bases=None, earliest_bases=None):
    if bn in SPECIAL_CASES_UNIFORM:
        prefix2, toko, gencode = SPECIAL_CASES_UNIFORM[bn]
        return f"{prefix2}-{toko}-{tier}-{gencode}-{color}", 'special_case_uniform'
    if bn in SPECIAL_CASES_CHRONO:
        prefix2, toko, ymap = SPECIAL_CASES_CHRONO[bn]
        # Sebagian platform (mis. TikTok) label Latio pakai "Gen 1"/"Gen 2"
        # eksplisit alih-alih tahun bare - kebetulan URUTANNYA sama dgn
        # kode kronologis yg sudah ditentukan (Gen 1=G1=2004-2012,
        # Gen 2=G2=2014-2016), jadi nomor generasi literal juga valid.
        if gen is not None and f"G{gen}" in ymap.values():
            return f"{prefix2}-{toko}-{tier}-G{gen}-{color}", 'special_case_chrono_gen_literal'
        if leftover in ymap:
            return f"{prefix2}-{toko}-{tier}-{ymap[leftover]}-{color}", 'special_case_chrono'
        return None, 'special_case_chrono_leftover_not_mapped'
    return resolve(table, literal_bases, bn, tier, color, gen, leftover, uniform_bases, earliest_bases)


# Semua pickle override TAMBAHAN (di luar final_sku_fill7/op_audit_final)
# yg pernah ditemukan sesudahnya - key 'sp_fixes'/'op_fixes' isinya list
# (path, r, nm, variant, old_sku, new_sku). WAJIB didaftarkan di SINI SAJA
# (satu tempat) lalu dipakai oleh SEMUA fungsi builder override (sp_master,
# op_candidates, sp_sku_overrides, op_sku_overrides) - lesson 2026-08-29:
# pernah kelewat nambahin ke sebagian fungsi doang, hasilnya file yg sudah
# dikirim ke user masih py nilai lama krn functionnya baca sumber beda2.
EXTRA_OVERRIDE_PICKLES = ['bucket_fixes_final.pkl', 'elantra_op_fix.pkl', 'round3_corrections.pkl']


def load_extra_overrides(key):
    """key: 'sp_fixes' atau 'op_fixes'. Baca semua pickle di
    EXTRA_OVERRIDE_PICKLES yg py key itu, gabung jadi 1 dict override."""
    overrides = {}
    for fname in EXTRA_OVERRIDE_PICKLES:
        try:
            d = pickle.load(open(fname, 'rb'))
        except FileNotFoundError:
            continue
        for path, r, nm, variant, old_sku, new_sku in d.get(key, []):
            overrides[(path, r)] = new_sku
    return overrides


def build_sp_master():
    """Gabungkan SEMUA SKU SP yang sudah valid (modern, toko=SP) dari
    sp_sku_fixed/1-2.xlsx, ditimpa oleh hasil audit 439-row (final_sku_fill7)
    DAN semua EXTRA_OVERRIDE_PICKLES (bug bucket-code, Elantra OP tidak
    sinkron, koreksi formula/Lexus LX 2026-08-29 round 3) - ini
    SATU-SATUNYA sumber kebenaran utk isi SKU OP (toko OP == SP). WAJIB
    include semua koreksi, kalau tidak baris yg "kelihatan py SKU valid"
    (padahal salah) akan dianggap benar."""
    d = pickle.load(open(FINAL_SKU_FILL_PKL, "rb"))
    overrides = {(path, r): sku for target, path, r, pid, varid, variant, sku, metode in d['ok']}
    overrides.update(load_extra_overrides('sp_fixes'))

    master = defaultdict(set)
    base_display = {}
    for path in SP_FILES:
        ws = openpyxl.load_workbook(path, data_only=True)['Sheet1']
        for r in range(7, ws.max_row + 1):
            nm = ws.cell(r, 2).value
            if not nm or is_transparan_product(nm):
                continue
            variant = ws.cell(r, 4).value
            if not variant:
                continue
            sku = overrides.get((path, r), ws.cell(r, 6).value)
            if not sku or not str(sku).strip():
                continue
            segs = str(sku).split('-')
            if len(segs) != 6 or segs[2] != 'SP':
                continue
            base = clean_base(nm)
            bn = norm(base)
            base_display[bn] = base
            tier, color = tier_warna_sp(variant)
            if tier is None:
                continue
            gen, leftover = gen_and_leftover(variant)
            master[(bn, tier, color)].add((gen, leftover, sku))
    return master, base_display


def scan_rows_needing_fix(files, tier_warna_fn):
    """Baca semua baris file2 (format Shopee sales_info), kembalikan
    (1) list semua baris dgn metadata, (2) tabel 'good rows' (SKU modern
    valid toko=SP) utk dipakai sbg referensi internal fallback."""
    table = defaultdict(set)
    base_display = {}
    rows_all = []
    for path in files:
        ws = openpyxl.load_workbook(path, data_only=True)['Sheet1']
        for r in range(7, ws.max_row + 1):
            nm = ws.cell(r, 2).value
            if not nm:
                continue
            variant = ws.cell(r, 4).value
            sku = ws.cell(r, 6).value
            is_transparan = is_transparan_product(nm)
            base = clean_base(nm)
            bn = norm(base)
            base_display[bn] = base
            is_blank = not sku or not str(sku).strip()
            is_legacy = False
            if not is_blank:
                segs = str(sku).split('-')
                is_legacy = not (len(segs) == 6 and segs[2] == 'SP')
            rows_all.append((path, r, nm, base, bn, variant, sku, is_blank, is_legacy, is_transparan))
            if not is_transparan and not is_blank and not is_legacy and variant:
                tier, color = tier_warna_fn(variant)
                if tier:
                    gen, leftover = gen_and_leftover(variant)
                    table[(bn, tier, color)].add((gen, leftover, sku))
    return rows_all, table, base_display


def audit_otoprotection():
    sp_master_raw, sp_base_display = build_sp_master()
    sp_master = expand_slash_aliases(sp_master_raw, sp_base_display)
    sp_literal_bases = build_literal_bases(sp_master)
    sp_uniform_bases = build_uniform_bases(sp_master)
    sp_earliest_bases = build_earliest_bases(sp_master)

    op_rows_all, op_table_raw, op_base_display = scan_rows_needing_fix(OP_FILES, tier_warna_op)
    op_table = expand_slash_aliases(op_table_raw, op_base_display)
    op_literal_bases = build_literal_bases(op_table)
    op_uniform_bases = build_uniform_bases(op_table)
    op_earliest_bases = build_earliest_bases(op_table)

    ok, gagal, skip = [], [], []
    for path, r, nm, base, bn, variant, sku, is_blank, is_legacy, is_transparan in op_rows_all:
        if is_transparan or not (is_blank or is_legacy):
            continue
        if not variant or nm.strip().lower().startswith('custom'):
            continue  # baris non-produk (mis. jasa custom tambahan) - di luar scope
        if 'tahun lain' in variant.lower() or 'model lain' in variant.lower():
            skip.append((path, r, nm, variant))
            continue
        tier, color = tier_warna_op(variant)
        if tier is None:
            gagal.append((path, r, nm, variant, sku, 'tier_parse_fail'))
            continue
        gen, leftover = gen_and_leftover(variant)
        new_sku, reason = resolve_with_special_cases(
            sp_master, sp_literal_bases, bn, tier, color, gen, leftover, sp_uniform_bases, sp_earliest_bases)
        source = 'SP_MASTER'
        if not new_sku:
            new_sku2, reason2 = resolve_with_special_cases(
                op_table, op_literal_bases, bn, tier, color, gen, leftover, op_uniform_bases, op_earliest_bases)
            if new_sku2:
                new_sku, source, reason = new_sku2, 'OP_INTERNAL', reason2
            else:
                gagal.append((path, r, nm, variant, sku, f"SP:{reason}|OP:{reason2}"))
                continue
        ok.append((nm, path, r, new_sku, f"{source}:{reason}"))
    return ok, gagal, skip, sp_master, sp_literal_bases, sp_uniform_bases, sp_earliest_bases


if __name__ == '__main__':
    ok, gagal, skip, *_ = audit_otoprotection()
    print(f"OP: {len(ok)} baris siap diisi, {len(gagal)} gagal/butuh keputusan, "
          f"{len(skip)} dilewati (Tahun Lain/Model Lain)")
    pickle.dump({'ok': ok, 'gagal': gagal, 'skip': skip},
                open('op_audit_final.pkl', 'wb'))
