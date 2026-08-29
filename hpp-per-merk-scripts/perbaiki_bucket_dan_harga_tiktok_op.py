#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanjutan setelah audit OP+harga SP/OP (2026-08-29): 2 pekerjaan tambahan
dari pertanyaan user ("kenapa TikTok OP ngga sekalian harganya?" + "TikTok
OP yg masih belum ada SKUnya ini produk apa aja?") YANG MEMBONGKAR BUG
SISTEMIK BARU saat menjawabnya:

**Bug ditemukan**: pola bucket-code yang SAMA PERSIS dengan bug Hyundai
Elantra yang sudah diperbaiki minggu lalu (kode kayak "GB20152020" dipakai
utk >1 generasi asli berbeda) TERNYATA masih ada di **8 produk lain**
tier Strip SP (Chevrolet Trooper, Hyundai Sonata, Jeep Cherokee, Kia
Sedona/Carnival, Lexus RX, Mercedes Benz CLS Class, Mercedes Benz GLA
Class, Peugeot 3008) - dikonfirmasi TIDAK ADA satu pun di file Total
Formula, jadi source of truth SATU-SATUNYA adalah tier Reguler produk itu
SENDIRI (yg sudah terbukti bersih/konsisten, tidak py kode bucket).
**8 dari 9 aman diperbaiki otomatis** (kode Strip yg beda dari peta
gen->kode yg SUDAH dibuktikan Reguler tinggal disamakan) - **1 (Lexus LX)
DIFLAG bukan diperbaiki** krn tier Reguler-nya SENDIRI py kode bucket
(tidak ada sumber bersih dalam produk itu utk jadi rujukan).

Elantra sendiri ternyata py salinan TERPISAH & TIDAK SINKRON di listing
OP (beda dari SP yg sudah dibenerin 439-row dulu) - 42 baris OP masih
pakai kode lama/bucket yang sama persis dgn yang sudah diperbaiki di SP.

Pemakaian: python3 perbaiki_bucket_dan_harga_tiktok_op.py
    (baca bucket_fixes_final.pkl, elantra_op_fix.pkl - hasil investigasi
    ad-hoc sebelumnya, timpa ke file UPDATE_* yg SUDAH dikirim ke user)
"""
import pickle

import openpyxl
from openpyxl.styles import PatternFill

import audit_dan_isi_sku_otoprotection as op_audit
import propagasi_sku_tiktok_otoprotection as prop
import update_sku_harga_sp_op as harga_sp_op

KUNING = PatternFill('solid', fgColor='FFFF00')

SRC_TO_OUT_SP = {"sp_sku_fixed/1.xlsx": "UPDATE_SKU_HARGA_SMARTPROTECTION_1.xlsx",
                  "sp_sku_fixed/2.xlsx": "UPDATE_SKU_HARGA_SMARTPROTECTION_2.xlsx"}
SRC_TO_OUT_OP = {"op_src/fixed/1.xlsx": "UPDATE_SKU_HARGA_OTOPROTECTION_1.xlsx",
                  "op_src/fixed/2.xlsx": "UPDATE_SKU_HARGA_OTOPROTECTION_2.xlsx"}


def apply_fixes_to_output(fixes, src_to_out):
    """fixes: list of (src_path, row, nm, variant, old_sku, new_sku)."""
    by_out = {}
    for src_path, r, nm, variant, old_sku, new_sku in fixes:
        out_path = src_to_out[src_path]
        by_out.setdefault(out_path, []).append((r, new_sku))

    for out_path, rows in by_out.items():
        wb = openpyxl.load_workbook(out_path, data_only=False)
        ws = wb['Sheet1']
        for r, new_sku in rows:
            cell = ws.cell(r, 6)
            cell.value = new_sku
            cell.fill = KUNING
        wb.save(out_path)
        print(f"  {out_path}: {len(rows)} SKU diperbaiki (bug bucket-code)")


def main():
    d = pickle.load(open('bucket_fixes_final.pkl', 'rb'))
    sp_fixes, op_fixes = d['sp_fixes'], d['op_fixes']
    elantra_op_fix = pickle.load(open('elantra_op_fix.pkl', 'rb'))

    print("=== Perbaiki bug bucket-code (8 produk baru) + Elantra OP tidak sinkron ===")
    apply_fixes_to_output(sp_fixes, SRC_TO_OUT_SP)
    apply_fixes_to_output(op_fixes, SRC_TO_OUT_OP)
    apply_fixes_to_output(elantra_op_fix, SRC_TO_OUT_OP)

    print("\n=== Rebuild kandidat OP (skrg sudah termasuk semua koreksi) utk TikTok ===")
    candidates, base_display = prop.build_op_candidates()
    literal_bases = op_audit.build_literal_bases(candidates)
    uniform_bases = op_audit.build_uniform_bases(candidates)
    earliest_bases = op_audit.build_earliest_bases(candidates)
    print(f"Grup kandidat OP: {len(candidates)}")

    targets, price_by_target = harga_sp_op.load_price_targets()
    key_to_target = harga_sp_op.sp_audit.build_alias_map(targets)
    keys_sorted = sorted(key_to_target.keys(), key=len, reverse=True)

    for (path, startrow), out_path in zip(prop.TIKTOK_FILES, prop.OUT_FILES):
        wb = openpyxl.load_workbook(path, data_only=False)
        ws = wb['Template']
        matched, unmatched = prop.match_rows(ws, startrow, candidates, literal_bases, uniform_bases, earliest_bases)
        for r, nm, variant, sku, reason in matched:
            ws.cell(r, 11).value = sku

        harga_stats = {'reguler': 0, 'strip': 0, 'tier_gagal': 0}
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, 3).value
            if not nm or op_audit.is_transparan_product(nm):
                continue
            variant = ws.cell(r, 6).value
            if not variant:
                continue
            base = op_audit.clean_base(nm)
            bn = harga_sp_op.sp_audit.normalize(base)
            t = harga_sp_op.sp_audit.match_target(bn, key_to_target, keys_sorted)
            if t is None:
                fz = harga_sp_op.sp_audit.match_fuzzy(bn, key_to_target, keys_sorted)
                if fz:
                    t = fz[1]
            if t is None:
                continue
            tier, color = harga_sp_op.tier_warna_toleran(prop.tier_warna_tiktok_op, variant)
            if tier is None:
                harga_stats['tier_gagal'] += 1
                continue
            new_price = price_by_target[t] + (harga_sp_op.STRIP_MARKUP if tier == 'S' else 0)
            ws.cell(r, 9).value = new_price
            harga_stats['strip' if tier == 'S' else 'reguler'] += 1

        wb.save(out_path)
        print(f"\n{out_path}: {len(matched)} SKU cocok, harga: {harga_stats}")
        print(f"  tersimpan: {out_path}")


if __name__ == '__main__':
    main()
