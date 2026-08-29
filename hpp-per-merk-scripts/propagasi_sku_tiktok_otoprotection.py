#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Propagasi SKU Otoprotection (OP, hasil audit_dan_isi_sku_otoprotection.py,
552 baris) + baris OP yg SUDAH benar sebelumnya -> ke listing TikTok OP
(tiktok1.xlsx = 1 baris Transparan doang, tiktok2.xlsx = 6827 baris),
2026-08-29.

Sama seperti propagasi Lazada/TikTok Smartprotection sebelumnya (matching
berbasis nomor generasi bukan teks tahun, normalisasi typo), TAPI teks
varian TikTok OP py variasi vocab LEBIH BANYAK drpd Shopee OP sendiri:
- Warna reguler kadang bentuk PENDEK: "Biru" (bukan "Biru Benhur"),
  "Hijau" (bukan "Hijau Army"), plus typo "Biru Bnehur" (huruf ketuker).
- Tier Strip kadang pakai kata SP-style (Epic/Elite/Warior/Warrior),
  BUKAN cuma "Strip N" kayak listing Shopee OP - keduanya sama2 dipakai
  dlm 1 file yg sama (campuran, kemungkinan sebagian baris migrasi
  copy-paste dari data SP).
- "Strip N Abu" vs "Strip N Abu-abu" dua-duanya dipakai (beda dari
  Shopee OP yg juga py 2 bentuk ini).

Pemakaian: python3 propagasi_sku_tiktok_otoprotection.py
"""
import re
import pickle
from collections import defaultdict, Counter

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit

TIKTOK_FILES = [("op_src/tiktok1.xlsx", 6), ("op_src/tiktok2.xlsx", 6)]
OUT_FILES = ["UPDATE_SKU_OTOPROTECTION_TIKTOK_1.xlsx", "UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx"]

WARNA_REGULER_SHORT = dict(op_audit.WARNA_REGULER)
WARNA_REGULER_SHORT.update({'biru': 'BRU', 'hijau': 'GRN', 'biru bnehur': 'BRU'})
TIER_STRIP_WORD = {'epic': 'S1', 'elite': 'S2', 'warior': 'S3', 'warrior': 'S3'}


def tier_warna_tiktok_op(variant):
    color_part = variant.split(',')[0].strip().lower()
    if color_part in WARNA_REGULER_SHORT:
        return 'R', WARNA_REGULER_SHORT[color_part]
    m = re.match(r'^strip\s*([123])\s+(abu-abu|abu|biru|merah)$', color_part)
    if m:
        wk = 'abu' if m.group(2) == 'abu-abu' else m.group(2)
        return 'S', f"S{m.group(1)}{op_audit.WARNA_STRIP[wk]}"
    words = color_part.split()
    if len(words) == 2 and words[0] in TIER_STRIP_WORD and words[1] in op_audit.WARNA_STRIP:
        return 'S', f"{TIER_STRIP_WORD[words[0]]}{op_audit.WARNA_STRIP[words[1]]}"
    return None, None


def build_op_candidates():
    """(base_norm, tier, warna) -> {(gen, leftover, sku)} dari SEMUA baris
    OP yg SUDAH py SKU modern benar: baris yg sudah bagus dari awal + 552
    hasil audit_dan_isi_sku_otoprotection.py."""
    d = pickle.load(open('op_audit_final.pkl', 'rb'))
    overrides = {(path, r): sku for nm, path, r, sku, reason in d['ok']}

    candidates = defaultdict(set)
    base_display = {}
    for path in op_audit.OP_FILES:
        ws = openpyxl.load_workbook(path, data_only=True)['Sheet1']
        for r in range(7, ws.max_row + 1):
            nm = ws.cell(r, 2).value
            if not nm or op_audit.is_transparan_product(nm):
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
            base = op_audit.clean_base(nm)
            bn = op_audit.norm(base)
            base_display[bn] = base
            tier, color = op_audit.tier_warna_op(variant)
            if tier is None:
                continue
            gen, leftover = op_audit.gen_and_leftover(variant)
            candidates[(bn, tier, color)].add((gen, leftover, sku))
    return candidates, base_display


def match_rows(ws, startrow, candidates, literal_bases, uniform_bases, earliest_bases):
    matched, unmatched = [], []
    for r in range(startrow, ws.max_row + 1):
        nm = ws.cell(r, 3).value
        if not nm or op_audit.is_transparan_product(nm):
            continue
        variant = ws.cell(r, 6).value
        if not variant:
            continue
        base = op_audit.clean_base(nm)
        bn = op_audit.norm(base)
        tier, color = tier_warna_tiktok_op(variant)
        if tier is None:
            unmatched.append((r, nm, variant, 'tier_parse_fail'))
            continue
        gen, leftover = op_audit.gen_and_leftover(variant)
        sku, reason = op_audit.resolve_with_special_cases(
            candidates, literal_bases, bn, tier, color, gen, leftover, uniform_bases, earliest_bases)
        if sku:
            matched.append((r, nm, variant, sku, reason))
        else:
            unmatched.append((r, nm, variant, reason))
    return matched, unmatched


def main():
    candidates, base_display = build_op_candidates()
    literal_bases = op_audit.build_literal_bases(candidates)
    uniform_bases = op_audit.build_uniform_bases(candidates)
    earliest_bases = op_audit.build_earliest_bases(candidates)
    print(f"Grup kandidat OP: {len(candidates)}  literal: {len(literal_bases)}  "
          f"uniform: {len(uniform_bases)}  earliest: {len(earliest_bases)}")

    for (path, startrow), out_path in zip(TIKTOK_FILES, OUT_FILES):
        wb = openpyxl.load_workbook(path, data_only=False)
        ws = wb['Template']
        matched, unmatched = match_rows(ws, startrow, candidates, literal_bases, uniform_bases, earliest_bases)
        reasons = Counter(m[4] for m in matched)
        print(f"\n{path}: {len(matched)} cocok, {len(unmatched)} tidak cocok")
        print("  metode:", dict(reasons))
        for r, sku, reason in [(m[0], m[3], m[4]) for m in matched]:
            ws.cell(r, 11).value = sku
        wb.save(out_path)
        print(f"  tersimpan: {out_path}")

        if unmatched:
            c = Counter(u[1] for u in unmatched)
            print("  produk tidak cocok (top 15):")
            for k, v in c.most_common(15):
                print("   ", v, k)

    pickle.dump({'candidates': dict(candidates), 'base_display': base_display},
                open('op_tiktok_candidates.pkl', 'wb'))


if __name__ == '__main__':
    main()
