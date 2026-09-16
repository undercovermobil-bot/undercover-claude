#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bangun ULANG (versi final, 2026-08-31) file update Lazada & TikTok utk
Smartprotection (SP) - SKU + HARGA sekaligus, pakai `build_sp_master()`
dari `audit_dan_isi_sku_otoprotection.py` sbg sumber kandidat (BUKAN
`final_sku_fill7.pkl` mentah spt versi awal 2026-08-29) krn sp_master
sudah include SEMUA koreksi yg ditemukan belakangan: bug bucket-code (9
produk), Elantra OP tidak sinkron, koreksi formula Total Formula (Civic
Type R, Mazda 2 Sedan, Hyundai Excel, Isuzu Mux), Lexus LX. Kalau pakai
final_sku_fill7 mentah, file Lazada/TikTok yg dihasilkan bakal MEMBAWA
BALIK nilai lama yg sudah terbukti salah.

Harga: sama formula yg dipakai di seluruh proyek ini sejak dikonfirmasi
user 2026-08-29 - Reguler dari `Harga Baru SP-OP (matriks) FINAL.xlsx`,
Strip = Reguler + Rp43.000 flat.

Pemakaian: python3 update_sku_harga_lazada_tiktok_smartprotection.py
"""
import re
from collections import Counter, defaultdict

import openpyxl
from openpyxl.styles import PatternFill

import audit_dan_isi_sku_otoprotection as op_audit
import update_sku_harga_sp_op as harga_sp_op

LAZADA_IN = "sp_lazada_tiktok_src/lazada.xlsx"
TIKTOK_IN = "sp_lazada_tiktok_src/tiktok.xlsx"
LAZADA_OUT = "UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx"
TIKTOK_OUT = "UPDATE_SKU_HARGA_SMARTPROTECTION_TIKTOK.xlsx"

TYPO_FIX = [(re.compile(r'\bMitshubishi\b', re.IGNORECASE), 'Mitsubishi'),
            (re.compile(r'\bMistubishi\b', re.IGNORECASE), 'Mitsubishi')]


def clean_base_lazada_tiktok(nm):
    nm = op_audit.SUFFIX_TRANSPARAN_RE.sub('', op_audit.PREFIX_RE.sub('', nm)).strip()
    for pat, rep in TYPO_FIX:
        nm = pat.sub(rep, nm)
    return nm


def tier_warna_lazada_tiktok(variant):
    """Lazada/TikTok SP pakai vocab sama dgn Shopee SP (Epic/Elite/Warior)
    TAPI kadang warna reguler versi pendek ('Biru'/'Hijau' bukan 'Biru
    Benhur'/'Hijau Army') - lihat lesson propagasi TikTok OP 2026-08-29."""
    color_part = variant.split(',')[0].strip().lower()
    warna_short = dict(op_audit.WARNA_REGULER)
    warna_short.update({'biru': 'BRU', 'hijau': 'GRN'})
    if color_part in warna_short:
        return 'R', warna_short[color_part]
    words = color_part.split()
    tier_word = {'epic': 'S1', 'elite': 'S2', 'warior': 'S3', 'warrior': 'S3'}
    if len(words) == 2 and words[0] in tier_word and words[1] in op_audit.WARNA_STRIP:
        return 'S', f"{tier_word[words[0]]}{op_audit.WARNA_STRIP[words[1]]}"
    return None, None


def dedup_suffix(gen, leftover):
    """Token pembeda dari generasi/tahun baris ybs, dipakai saat SKU 'bersih'
    hasil resolve() bentrok dgn baris lain di produk yg sama (collapse
    TF=1 lintas beberapa baris gen berbeda) - lihat lesson 2026-08-31 soal
    duplikat SKU Lazada."""
    if gen is not None:
        return f"_G{gen}"
    if leftover:
        m = re.match(r'^(\d{4})', leftover)
        if m:
            return f"_{m.group(1)}"
        m2 = re.match(r'^([a-z]{2,4})\d', leftover)
        if m2:
            return f"_{m2.group(1).upper()}"
    return None


def match_and_write(path_in, path_out, sheet, name_col, variant_col, sku_col, price_col,
                     startrow, candidates, literal_bases, uniform_bases, earliest_bases,
                     key_to_target, keys_sorted, price_by_target, dedup_per_product=False):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    ws = wb[sheet]
    stats = Counter()
    used = defaultdict(set)
    for r in range(startrow, ws.max_row + 1):
        nm = ws.cell(r, name_col).value
        if not nm or op_audit.is_transparan_product(nm):
            continue
        variant = ws.cell(r, variant_col).value
        if not variant:
            continue
        base = clean_base_lazada_tiktok(nm)
        bn = op_audit.norm(base)
        tier, color = tier_warna_lazada_tiktok(variant)

        gen, leftover = (None, None)
        if tier is not None:
            gen, leftover = op_audit.gen_and_leftover(variant)
            sku, reason = op_audit.resolve_with_special_cases(
                candidates, literal_bases, bn, tier, color, gen, leftover, uniform_bases, earliest_bases)
            if sku:
                candidate = sku
                if dedup_per_product and candidate in used[nm]:
                    suf = dedup_suffix(gen, leftover)
                    if suf and (candidate + suf) not in used[nm]:
                        candidate = candidate + suf
                    else:
                        i = 2
                        while f"{sku}_{i}" in used[nm]:
                            i += 1
                        candidate = f"{sku}_{i}"
                    stats['sku_dedup_suffixed'] += 1
                ws.cell(r, sku_col).value = candidate
                stats['sku_' + reason] += 1

        if dedup_per_product:
            final_val = ws.cell(r, sku_col).value
            if final_val:
                used[nm].add(final_val)

        t = harga_sp_op.sp_audit.match_target(bn, key_to_target, keys_sorted)
        if t is None:
            fz = harga_sp_op.sp_audit.match_fuzzy(bn, key_to_target, keys_sorted)
            if fz:
                t = fz[1]
        if t is not None and tier is not None:
            new_price = price_by_target[t] + (harga_sp_op.STRIP_MARKUP if tier == 'S' else 0)
            ws.cell(r, price_col).value = new_price
            stats['harga_' + ('strip' if tier == 'S' else 'reguler')] += 1

    wb.save(path_out)
    return stats


def main():
    sp_master_raw, sp_base_display = op_audit.build_sp_master()
    candidates = op_audit.expand_slash_aliases(sp_master_raw, sp_base_display)
    literal_bases = op_audit.build_literal_bases(candidates)
    uniform_bases = op_audit.build_uniform_bases(candidates)
    earliest_bases = op_audit.build_earliest_bases(candidates)
    print(f"Kandidat SP (sudah termasuk semua koreksi): {len(candidates)} grup")

    targets, price_by_target = harga_sp_op.load_price_targets()
    key_to_target = harga_sp_op.sp_audit.build_alias_map(targets)
    keys_sorted = sorted(key_to_target.keys(), key=len, reverse=True)

    stats_l = match_and_write(LAZADA_IN, LAZADA_OUT, 'template', 3, 14, 13, 9, 5,
                               candidates, literal_bases, uniform_bases, earliest_bases,
                               key_to_target, keys_sorted, price_by_target, dedup_per_product=True)
    print(f"\nLAZADA -> {LAZADA_OUT}")
    print(" ", dict(stats_l))

    stats_t = match_and_write(TIKTOK_IN, TIKTOK_OUT, 'Template', 3, 6, 11, 9, 6,
                               candidates, literal_bases, uniform_bases, earliest_bases,
                               key_to_target, keys_sorted, price_by_target)
    print(f"\nTIKTOK -> {TIKTOK_OUT}")
    print(" ", dict(stats_t))


if __name__ == '__main__':
    main()
