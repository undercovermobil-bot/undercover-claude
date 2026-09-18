#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tulis harga baru Transparan ke listing Otoprotection (OP) aktual
(Shopee 1-2, TikTok 1-2 - OP TIDAK jualan di Lazada), 2026-09-14.
Lanjutan langsung dari `update_harga_transparan_sp.py` (SP) - metode,
kalibrasi, ALIAS_MANUAL, dan ESTIMASI_MM SAMA PERSIS (diimpor langsung,
bukan disalin) supaya kedua toko konsisten & 1 sumber kebenaran.

HANYA kolom harga yang disentuh - SKU sama sekali tidak diubah.

Pemakaian: python3 update_harga_transparan_op.py
"""
from collections import defaultdict

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit
from update_harga_transparan_sp import (
    AMBANG_MM, LANTAI_BESAR, LANTAI_KECIL, PAKSA_BESAR, build_index,
    kalibrasi_grup, posisi, resolve_model,
)
from estimasi_15_model_transparan import ESTIMASI_MM
import harga_baru_sp_op_matriks_v2 as m

TOP100_SRC = "Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx"

FILES = [
    ("op_src/1.xlsx", "SHOPEE_OTOPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7, 7),
    ("op_src/2.xlsx", "SHOPEE_OTOPROTECTION_2.xlsx", "Sheet1", 2, 4, 6, 7, 7),
    ("op_tiktok1_src.xlsx", "TIKTOK_OTOPROTECTION_1.xlsx", "Template", 3, 6, 11, 9, 6),
    ("op_tiktok2_src.xlsx", "TIKTOK_OTOPROTECTION_2.xlsx", "Template", 3, 6, 11, 9, 6),
]


def main():
    src = openpyxl.load_workbook(TOP100_SRC, data_only=True)
    ws_src = src['Top 100 Terlaris']
    top100 = [ws_src.cell(r, 1).value for r in range(2, ws_src.max_row + 1)
               if ws_src.cell(r, 1).value]
    kecil0 = [n for n in top100 if m.PANJANG_MM[n] < AMBANG_MM and n not in PAKSA_BESAR]
    besar0 = [n for n in top100 if m.PANJANG_MM[n] >= AMBANG_MM and n not in PAKSA_BESAR]
    kalib_kecil = kalibrasi_grup([m.PANJANG_MM[n] for n in kecil0])
    kalib_besar = kalibrasi_grup([m.PANJANG_MM[n] for n in besar0])
    print(f"Kalibrasi terkunci (SAMA dgn SP) - kecil: {kalib_kecil}, besar: {kalib_besar}")

    idx = build_index()
    estimasi_harga = {}
    for nm, (panjang, _alasan) in ESTIMASI_MM.items():
        if panjang >= AMBANG_MM or nm in PAKSA_BESAR:
            estimasi_harga[op_audit.norm(nm)] = LANTAI_BESAR + posisi(panjang, kalib_besar)
        else:
            estimasi_harga[op_audit.norm(nm)] = LANTAI_KECIL + posisi(panjang, kalib_kecil)

    def harga_untuk_key(bn_match_name):
        panjang = m.PANJANG_MM[bn_match_name]
        if panjang >= AMBANG_MM or bn_match_name in PAKSA_BESAR:
            return LANTAI_BESAR + posisi(panjang, kalib_besar)
        return LANTAI_KECIL + posisi(panjang, kalib_kecil)

    tidak_ketemu = defaultdict(int)
    resolved_cache = {}

    for src_path, out_path, sheet, namecol, varcol, skucol, pricecol, startrow in FILES:
        wb = openpyxl.load_workbook(src_path, data_only=False)
        ws = wb[sheet]
        n_updated = n_skipped = 0
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm or not op_audit.is_transparan_product(nm):
                continue
            base = op_audit.clean_base_transparan(nm)
            bn = op_audit.norm(base)
            if base not in resolved_cache:
                match = resolve_model(base, idx)
                if match:
                    resolved_cache[base] = ('dataset', harga_untuk_key(match))
                elif bn in estimasi_harga:
                    resolved_cache[base] = ('estimasi', estimasi_harga[bn])
                else:
                    resolved_cache[base] = (None, None)
            kind, harga = resolved_cache[base]
            if harga is None:
                tidak_ketemu[base] += 1
                n_skipped += 1
                continue
            ws.cell(r, pricecol).value = harga
            n_updated += 1
        wb.save(out_path)
        print(f"{out_path}: {n_updated} baris diupdate, {n_skipped} baris dilewati")

    print(f"\nModel TIDAK ketemu referensi ukuran ({len(tidak_ketemu)} model, "
          f"{sum(tidak_ketemu.values())} baris):")
    for b, c in sorted(tidak_ketemu.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {b}")


if __name__ == '__main__':
    main()
