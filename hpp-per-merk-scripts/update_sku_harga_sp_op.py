#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gabung SKU fix + update harga baru jadi SATU file per toko/platform utk
Smartprotection (SP) dan Otoprotection (OP), 2026-08-29.

**KENAPA DIGABUNG (bukan file terpisah)**: lesson 2026-08-15 di
feedback-undercover-sku-sync-lessons.md - "file update marketplace itu
MENIMPA SEMUA KOLOM yang ada di dalamnya, dua file update yg dibuat dari
basis beda akan saling me-revert". SP & OP dua-duanya BELUM pernah
diupload sama sekali (SKU maupun harga) - jadi SATU file per toko yg
benar di kedua kolom sekaligus, bukan 2 file terpisah.

Formula harga (dikonfirmasi user 2026-08-29):
- Reguler: langsung pakai "Harga Baru (Reguler)" dari
  `Harga Baru SP-OP (matriks) FINAL.xlsx` (291 model).
- Strip (S1/S2/S3, SEMUA tier sama): Reguler baru + Rp43.000 flat, UNTUK
  SEMUA MODEL - bukan pertahankan selisih lama per-model (selisih lama
  ternyata TIDAK seragam: ada yg +18rb, +20rb, +30rb, +60rb tergantung
  model - user pilih formula baru yg seragam, bukan pertahankan pola lama).

Baris yg TIDAK disentuh harganya: (a) produk Transparan (skema harga beda,
di luar 291 target ini), (b) baris yg base product-nya tidak match ke
salah satu 291 target (dicek via alias map yg sama dgn audit SKU SP), (c)
baris yg tier/warna-nya tidak bisa di-parse (mis. typo tidak dikenal) -
supaya tidak salah taruh harga Reguler di baris Strip atau sebaliknya.

SKU yg ditulis: SP dari 439 hasil audit sebelumnya
(final_sku_fill7.pkl) + 43 tambahan (Nissan Latio & Wuling Darion, baris
blank SP sendiri yg ketemu pas audit OP - lihat
audit_dan_isi_sku_otoprotection.py); OP dari 552 hasil
audit_dan_isi_sku_otoprotection.py.

Pemakaian: python3 update_sku_harga_sp_op.py
"""
import re
import pickle
import copy

import openpyxl
from openpyxl.styles import PatternFill

import audit_dan_isi_sku_smartprotection as sp_audit
import audit_dan_isi_sku_otoprotection as op_audit

TARGET_PATH = "Harga Baru SP-OP (matriks) FINAL.xlsx"
STRIP_MARKUP = 43000

SP_FILES = ["sp_sku_fixed/1.xlsx", "sp_sku_fixed/2.xlsx"]
OP_FILES = ["op_src/fixed/1.xlsx", "op_src/fixed/2.xlsx"]

KUNING = PatternFill('solid', fgColor='FFFF00')  # SKU diisi/diperbaiki
HIJAU = PatternFill('solid', fgColor='C6EFCE')   # harga diupdate

# Typo/singkatan tier/warna yg ketemu saat cocokkan harga (2026-08-29) -
# CUMA dipakai utk keputusan Reguler-vs-Strip harga (bukan utk isi SKU,
# krn baris ini SUDAH py SKU / bukan scope audit SKU) - koreksi ejaan
# sebelum parse tier, bukan ganti aturan tier itu sendiri.
TIER_TYPO_FIX = [
    (re.compile(r'^Elita\b', re.IGNORECASE), 'Elite'),
    (re.compile(r'^Eite\b', re.IGNORECASE), 'Elite'),
    (re.compile(r'^Srtip\b', re.IGNORECASE), 'Strip'),
    (re.compile(r'^Stirp\b', re.IGNORECASE), 'Strip'),
    (re.compile(r'^Hijau$', re.IGNORECASE), 'Hijau Army'),
    (re.compile(r'^Biru$', re.IGNORECASE), 'Biru Benhur'),
]


def tier_warna_toleran(tier_warna_fn, variant):
    tier, color = tier_warna_fn(variant)
    if tier is not None:
        return tier, color
    color_part, _, rest = variant.partition(',')
    fixed = color_part.strip()
    for pat, rep in TIER_TYPO_FIX:
        fixed = pat.sub(rep, fixed)
    if fixed == color_part.strip():
        return None, None
    return tier_warna_fn(fixed + (',' + rest if rest else ''))


def load_price_targets():
    ws = openpyxl.load_workbook(TARGET_PATH, data_only=True)['Harga Baru SP-OP']
    targets, price_by_target = [], {}
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(r, 2).value
        price = ws.cell(r, 7).value
        if nm and price:
            targets.append(nm)
            price_by_target[nm] = price
    return targets, price_by_target


def build_sp_sku_overrides():
    d = pickle.load(open('final_sku_fill7.pkl', 'rb'))
    overrides = {(path, r): sku for target, path, r, pid, varid, variant, sku, metode in d['ok']}
    supplement = pickle.load(open('sp_supplement_latio_darion.pkl', 'rb'))
    for nm, path, r, sku, reason in supplement:
        overrides[(path, r)] = sku
    overrides.update(op_audit.load_extra_overrides('sp_fixes'))
    return overrides


def build_op_sku_overrides():
    d = pickle.load(open('op_audit_final.pkl', 'rb'))
    overrides = {(path, r): sku for nm, path, r, sku, reason in d['ok']}
    # Baris yg SUDAH "kelihatan py SKU valid" dari awal (bukan blank/legacy)
    # jadi TIDAK masuk cakupan audit di atas, tapi ternyata salah (bug
    # bucket-code / Elantra OP tidak sinkron / koreksi formula round 3) -
    # WAJIB ditambah manual, kalau tidak baris ini lolos tanpa dikoreksi.
    overrides.update(op_audit.load_extra_overrides('op_fixes'))
    return overrides


def apply_updates(files, out_files, prefix_re, tier_warna_fn, sku_overrides, key_to_target, keys_sorted,
                   price_by_target):
    stats = {'sku_ditulis': 0, 'harga_diupdate': 0, 'harga_reguler': 0, 'harga_strip': 0,
              'tier_gagal_parse_tapi_match_target': 0}
    tier_gagal_samples = []
    for path, out_path in zip(files, out_files):
        wb = openpyxl.load_workbook(path, data_only=False)
        ws = wb['Sheet1']
        for r in range(7, ws.max_row + 1):
            nm = ws.cell(r, 2).value
            if not nm:
                continue
            variant = ws.cell(r, 4).value

            if (path, r) in sku_overrides:
                cell = ws.cell(r, 6)
                cell.value = sku_overrides[(path, r)]
                cell.fill = KUNING
                stats['sku_ditulis'] += 1

            if op_audit.is_transparan_product(nm) or not variant:
                continue
            base = prefix_re.sub('', nm).strip()
            bn = sp_audit.normalize(base)
            t = sp_audit.match_target(bn, key_to_target, keys_sorted)
            if t is None:
                fz = sp_audit.match_fuzzy(bn, key_to_target, keys_sorted)
                if fz:
                    t = fz[1]
            if t is None:
                continue
            tier, color = tier_warna_toleran(tier_warna_fn, variant)
            if tier is None:
                stats['tier_gagal_parse_tapi_match_target'] += 1
                if len(tier_gagal_samples) < 30:
                    tier_gagal_samples.append((path, r, nm, variant))
                continue
            new_price = price_by_target[t] + (STRIP_MARKUP if tier == 'S' else 0)
            pcell = ws.cell(r, 7)
            pcell.value = new_price
            pcell.fill = HIJAU
            stats['harga_diupdate'] += 1
            stats['harga_reguler' if tier == 'R' else 'harga_strip'] += 1

        wb.save(out_path)
        print(f"  tersimpan: {out_path}")
    return stats, tier_gagal_samples


def main():
    targets, price_by_target = load_price_targets()
    key_to_target = sp_audit.build_alias_map(targets)
    keys_sorted = sorted(key_to_target.keys(), key=len, reverse=True)
    print(f"Total target harga: {len(targets)}")

    sp_overrides = build_sp_sku_overrides()
    print(f"\n=== SMARTPROTECTION (SP) === SKU overrides: {len(sp_overrides)}")
    # tier_warna_sp (bukan sp_audit.tier_dan_warna) - versi ini kenal ejaan
    # "Warrior" (huruf-r ganda) SELAIN "Warior", lihat catatan project soal
    # variasi ejaan tier Strip; sp_audit punya sumber utama utk alias
    # nama produk (build_alias_map/match_target/match_fuzzy).
    sp_out = ["UPDATE_SKU_HARGA_SMARTPROTECTION_1.xlsx", "UPDATE_SKU_HARGA_SMARTPROTECTION_2.xlsx"]
    stats_sp, gagal_sp = apply_updates(SP_FILES, sp_out, sp_audit.PREFIX_RE, op_audit.tier_warna_sp,
                                        sp_overrides, key_to_target, keys_sorted, price_by_target)
    print(stats_sp)

    op_overrides = build_op_sku_overrides()
    print(f"\n=== OTOPROTECTION (OP) === SKU overrides: {len(op_overrides)}")
    op_out = ["UPDATE_SKU_HARGA_OTOPROTECTION_1.xlsx", "UPDATE_SKU_HARGA_OTOPROTECTION_2.xlsx"]
    stats_op, gagal_op = apply_updates(OP_FILES, op_out, op_audit.PREFIX_RE, op_audit.tier_warna_op,
                                        op_overrides, key_to_target, keys_sorted, price_by_target)
    print(stats_op)

    pickle.dump({'stats_sp': stats_sp, 'gagal_sp': gagal_sp, 'stats_op': stats_op, 'gagal_op': gagal_op},
                open('update_sku_harga_report.pkl', 'wb'))


if __name__ == '__main__':
    main()
