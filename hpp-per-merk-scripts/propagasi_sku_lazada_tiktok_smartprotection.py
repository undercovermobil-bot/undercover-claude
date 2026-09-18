#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Propagasi 439 SKU final Smartprotection (hasil
`audit_dan_isi_sku_smartprotection.py`, dari file Shopee) ke listing Lazada
& TikTok utk toko yg sama - SKU harus identik lintas-platform krn mewakili
identitas stok gudang yang sama (2026-08-29).

BEDA dgn `buat_file_update_sku_smartprotection.py` (Shopee): di sana kita
KLON row dari 2 file sumber ke 1 template baru (perlu null-out kolom lain,
lihat bug #1/#2 di docstring situ). Di sini kita EDIT IN-PLACE 1 file
per-platform (Lazada/TikTok) - cuma isi ULANG 1 kolom (Seller SKU) di baris
yg match, kolom lain TIDAK disentuh sama sekali - jadi tidak ada risiko
"kebawa data kolom lain" krn tidak ada operasi copy-row.

Tantangan uniknya di sini bukan soal openpyxl, tapi soal MATCHING lintas
platform, krn teks varian & nama produk TIDAK seragam persis:
1. **Typo beda per-platform**: sumber Shopee (dipakai bangun kunci lookup)
   kadang typo ("Mitshubishi Xforce") padahal Lazada/TikTok EJAAN BENAR
   ("Mitsubishi Xforce") - atau sebaliknya, typo yang SAMA di semua
   platform (Grandis: "Mistubishi" di ketiganya, jadi tidak masalah krn
   konsisten). -> WAJIB normalisasi typo brand yg diketahui SEBELUM
   dipakai jadi key, supaya platform manapun ejaannya, keynya sama.
2. **Teks generasi/tahun beda platform utk generasi SAMA**: mis. Shopee &
   TikTok bilang "Gen 10 (2015-2021)"/"Gen 10 : 2015-2021", tapi Lazada
   utk SKU Honda Civic Hatchback yg SAMA malah "Gen 10 : 2016-2021" (beda
   1 tahun) - kalau key-nya include teks tahun literal, ini GAGAL match
   walau sebenarnya generasi yg dimaksud sama. -> Key dibangun dari NOMOR
   GENERASI ("Gen N") kalau ada, BUKAN teks tahun; teks tahun/sisa cuma
   dipakai sbg disambiguator tambahan ("leftover") utk produk yg TIDAK
   punya "Gen N" sama sekali (mis. Mini Cooper "3 Pintu" vs "5 Pintu").
3. **TikTok kadang collapse variasi tahun jadi 1 baris per warna** (mis.
   Holden, Mitsubishi Grandis di TikTok cuma warna, TANPA dimensi
   tahun/generasi sbg variasi terpisah - beda dari Shopee/Lazada yg pecah
   per generasi). Ini valid krn produk itu TF=1 (1 kode generasi yg sama
   utk semua generasi asli, sudah diverifikasi dari data Shopee) - jadi 1
   baris TikTok tsb boleh nampung kode yg sama dgn banyak baris
   Shopee/Lazada. Ditangani otomatis oleh fallback "unique_sku" di bawah
   (kalau tidak ada nomor generasi di teks varian, tapi grup
   produk+tier+warna itu di data sumber ternyata cuma py 1 kode SKU unik).
4. **Sebagian baris Lazada/TikTok py "Gen N" yg TIDAK ada di 439 hasil
   fix** (krn baris itu di Shopee SUDAH benar sebelumnya, jadi tidak masuk
   daftar "perlu diisi/diperbaiki") - mis. Hyundai Elantra Gen 1/4/5/6/7
   (yg masuk fix cuma Gen 2/3 Reguler & Gen 2-7 Strip). Krn Elantra
   dikonfirmasi TIDAK ada di file Total Formula (aturan fallback: literal
   Gen N -> GN, lihat project-undercover-harga-referensi.md 2026-08-29),
   & prefix+toko-nya sudah pasti dari 439 hasil fix, generasi yg "hilang"
   ini AMAN dihitung ulang scr langsung (bukan nebak formula baru, cuma
   nerapin literal rule yg SAMA ke nomor generasi yg beda) - lihat
   `literal_bases()`. Deteksi OTOMATIS (cek semua kode existing produk itu
   beneran literal G<n>, BUKAN hardcode per-nameplate) supaya generalis &
   tidak keliru diterapkan ke produk yg py formula TF>1 (grouped).

Verifikasi silang (2026-08-29): dari 157 grup (produk+tier+warna) hasil
439 fix, TikTok 100% ketemu (492 baris ditulis), Lazada 148/157 (520
baris ditulis) - 9 grup sisanya SEMUA "Holden Strip" & sudah dikonfirmasi
via full-text scan bahwa Holden memang TIDAK dijual di Lazada sama sekali
(bukan bug matching).

Pemakaian: python3 propagasi_sku_lazada_tiktok_smartprotection.py
    (baca final_sku_fill7.pkl - sesuaikan kalau dipakai ulang utk audit
    baru; path Lazada/TikTok sumber di-hardcode di bawah)
"""
import re
import pickle
from collections import defaultdict, Counter

import openpyxl

PKL_PATH = "final_sku_fill7.pkl"
SUMBER_FILES = ["sp_sku_fixed/1.xlsx", "sp_sku_fixed/2.xlsx"]
LAZADA_IN = "sp_lazada_tiktok_src/lazada.xlsx"
TIKTOK_IN = "sp_lazada_tiktok_src/tiktok.xlsx"
LAZADA_OUT = "UPDATE_SKU_SMARTPROTECTION_LAZADA.xlsx"
TIKTOK_OUT = "UPDATE_SKU_SMARTPROTECTION_TIKTOK.xlsx"

PREFIX_RE = re.compile(
    r'^(Body\s+)?(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut\s+Mobil)'
    r'(\s*/\s*(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut\s+Mobil))*\s+', re.IGNORECASE)
SUFFIX_TRANSPARAN_RE = re.compile(r'\s+Transparan$', re.IGNORECASE)

# Typo brand yg TERBUKTI beda ejaan antar-platform utk produk yg SAMA
# (dicek manual by name+kategori, 2026-08-29) - JANGAN tambah tanpa
# verifikasi bahwa ini typo, bukan brand/model yg beneran beda.
TYPO_FIX = [
    (re.compile(r'\bMitshubishi\b', re.IGNORECASE), 'Mitsubishi'),
    (re.compile(r'\bMistubishi\b', re.IGNORECASE), 'Mitsubishi'),
]

WARNA_REGULER = {'abu-abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
                  'merah': 'MRH', 'hijau army': 'GRN', 'orange': 'ORG'}
TIER_STRIP = {'epic': 'S1', 'elite': 'S2', 'warior': 'S3', 'warrior': 'S3'}
WARNA_STRIP = {'abu': 'A', 'biru': 'B', 'merah': 'M'}
GEN_RE = re.compile(r'Gen\s*(\d+)', re.IGNORECASE)
YEAR_RE = re.compile(r'\b\d{4}(\s*-\s*\d{4})?\b')


def clean_base(nm):
    nm = SUFFIX_TRANSPARAN_RE.sub('', PREFIX_RE.sub('', nm)).strip()
    for pat, rep in TYPO_FIX:
        nm = pat.sub(rep, nm)
    return nm


def norm(s):
    s = s.lower().replace('-', '').replace('/', ' ').replace(':', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def tier_warna(variant):
    color_part = variant.split(',')[0].strip().lower()
    if color_part in WARNA_REGULER:
        return 'R', WARNA_REGULER[color_part]
    words = color_part.split()
    if len(words) == 2 and words[0] in TIER_STRIP and words[1] in WARNA_STRIP:
        return 'S', f"{TIER_STRIP[words[0]]}{WARNA_STRIP[words[1]]}"
    return None, None


def gen_and_leftover(variant):
    rest = variant.split(',', 1)[1].strip() if ',' in variant else ''
    m = GEN_RE.search(rest)
    gen = m.group(1) if m else None
    leftover = GEN_RE.sub('', rest)
    leftover = YEAR_RE.sub('', leftover)
    return gen, re.sub(r'[^a-z0-9]', '', leftover.lower())


def build_candidates():
    """(base_norm, tier, warna_kode) -> {(gen, leftover, sku_baru), ...}
    dari 439 hasil fix Shopee, dibaca ULANG posisi row-nya utk ambil nama
    produk PERSIS (bukan nama target audit yg generik - penting utk kasus
    spt Mazda 3 Hatchback vs Sedan yg beda produk tapi 1 target audit)."""
    d = pickle.load(open(PKL_PATH, 'rb'))
    ok = d['ok']
    sheets = {p: openpyxl.load_workbook(p, data_only=True)['Sheet1'] for p in SUMBER_FILES}

    candidates = defaultdict(set)
    base_display = {}
    for target, path, r, pid, varid, variant, sku_baru, metode in ok:
        nm = sheets[path].cell(r, 2).value
        base = clean_base(nm)
        bn = norm(base)
        base_display[bn] = base
        tier, color = tier_warna(variant)
        if tier is None:
            continue
        gen, leftover = gen_and_leftover(variant)
        candidates[(bn, tier, color)].add((gen, leftover, sku_baru))
    return candidates, base_display


def build_literal_bases(candidates):
    """Deteksi OTOMATIS produk yg kode generasinya literal G<n> (bukan
    formula TF>1/grouped) dgn cek SEMUA entri kandidatnya sendiri - dipakai
    utk extrapolasi ke nomor generasi yg ADA di Lazada/TikTok tapi TIDAK
    ada di 439 hasil fix (krn baris itu di Shopee sudah benar duluan)."""
    base_entries = defaultdict(list)
    for (bn, tier, color), vals in candidates.items():
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


def resolve(candidates, literal_bases, bn, tier, color, gen, leftover):
    vals = candidates.get((bn, tier, color))
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
            skus = set(v[2] for v in vals)
            if len(skus) == 1:
                return next(iter(skus)), 'unique_sku'
            lm = [v for v in vals if v[1] == leftover]
            if len(lm) == 1:
                return lm[0][2], 'leftover_match'
            return None, 'ambiguous_no_gen'
    if gen is not None and bn in literal_bases:
        prefix2, toko = literal_bases[bn]
        return f"{prefix2}-{toko}-{tier}-G{gen}-{color}", 'literal_extrapolated'
    if vals:
        skus = set(v[2] for v in vals)
        if len(skus) == 1:
            return next(iter(skus)), 'gen_not_found_fallback_unique'
        return None, 'gen_not_found_no_fallback'
    return None, 'no_candidate_group'


def match_rows(ws, name_col, variant_col, startrow, candidates, literal_bases):
    matched, unmatched = [], []
    for r in range(startrow, ws.max_row + 1):
        nm = ws.cell(r, name_col).value
        if not nm or SUFFIX_TRANSPARAN_RE.search(nm):
            continue
        variant = ws.cell(r, variant_col).value
        if not variant:
            continue
        base = clean_base(nm)
        bn = norm(base)
        tier, color = tier_warna(variant)
        if tier is None:
            continue
        gen, leftover = gen_and_leftover(variant)
        sku, reason = resolve(candidates, literal_bases, bn, tier, color, gen, leftover)
        if sku:
            matched.append((r, sku, reason))
        else:
            unmatched.append((r, nm, variant, reason))
    return matched, unmatched


def tulis_dan_simpan(path_in, path_out, sheet, sku_col, matched):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    ws = wb[sheet]
    for r, sku, reason in matched:
        cell = ws.cell(r, sku_col)
        cell.value = sku
    wb.save(path_out)
    return ws.max_row


def main():
    candidates, base_display = build_candidates()
    literal_bases = build_literal_bases(candidates)
    print(f"Grup produk+tier+warna dari 439 hasil fix: {len(candidates)}  |  "
          f"produk terdeteksi berpola literal G<n>: {len(literal_bases)}")

    wb_l = openpyxl.load_workbook(LAZADA_IN, data_only=False)
    ws_l = wb_l['template']
    m_l, u_l = match_rows(ws_l, 3, 14, 5, candidates, literal_bases)
    reason_l = Counter(x[2] for x in m_l)
    print(f"\nLAZADA: {len(m_l)} baris cocok/ditulis, {len(u_l)} baris relevan gagal-cocok")
    print("  metode:", dict(reason_l))
    mr_l = tulis_dan_simpan(LAZADA_IN, LAZADA_OUT, 'template', 13, m_l)
    print(f"  tersimpan: {LAZADA_OUT} (max_row={mr_l}, unchanged from source)")

    wb_t = openpyxl.load_workbook(TIKTOK_IN, data_only=False)
    ws_t = wb_t['Template']
    m_t, u_t = match_rows(ws_t, 3, 6, 6, candidates, literal_bases)
    reason_t = Counter(x[2] for x in m_t)
    print(f"\nTIKTOK: {len(m_t)} baris cocok/ditulis, {len(u_t)} baris relevan gagal-cocok")
    print("  metode:", dict(reason_t))
    mr_t = tulis_dan_simpan(TIKTOK_IN, TIKTOK_OUT, 'Template', 11, m_t)
    print(f"  tersimpan: {TIKTOK_OUT} (max_row={mr_t}, unchanged from source)")

    # cakupan: SKU apa saja dari 439 hasil fix yg TIDAK ketemu tempatnya sama sekali
    def cakupan(matched_list, label):
        found = set(x[1] for x in matched_list)
        missing = []
        for key, vals in candidates.items():
            miss = set(v[2] for v in vals) - found
            if miss:
                missing.append((key, miss))
        print(f"\n{label}: {len(candidates) - len(missing)}/{len(candidates)} grup lengkap.")
        for key, miss in missing:
            print(f"  TIDAK ADA DI {label}: {base_display[key[0]]} {key[1]} {key[2]} -> {miss}")

    cakupan(m_l, "LAZADA")
    cakupan(m_t, "TIKTOK")

    pickle.dump({'m_l': m_l, 'u_l': u_l, 'm_t': m_t, 'u_t': u_t,
                 'candidates': dict(candidates), 'base_display': base_display},
                open('propagasi_hasil.pkl', 'wb'))


if __name__ == '__main__':
    main()
