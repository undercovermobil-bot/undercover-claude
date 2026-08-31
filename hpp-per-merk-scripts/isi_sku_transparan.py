#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi SKU Transparan yang masih blank/legacy di SEMUA 8 file upload
SP+OP, 2026-08-31 (lanjutan).

Konteks: sepanjang sesi SKU+harga kemarin (2026-08-29 s/d 08-31),
kategori Transparan TIDAK PERNAH disentuh sama sekali - HARGA sengaja
(skema harga beda, di luar 291 target Reguler/Strip - lihat komentar di
update_sku_harga_sp_op.py), tapi SKU ternyata ikut kelewat krn
build_sp_master() secara eksplisit exclude Transparan dari scan
kandidat (baris `if not nm or is_transparan_product(nm): continue`).
User cek laporan hasil upload Lazada ("Data no change, not update" utk
525 baris - persis rentang baris Transparan) + tanya soal Transparan
lain, lalu konfirmasi: SKU Transparan diperbaiki SEKARANG, HARGA tetap
pakai harga lama (belum ada daftar harga Transparan yg baru).

Metode: build_transparan_master() (baru, di audit_dan_isi_sku_otoprotection.py)
gabungkan SEMUA SKU Transparan valid (6-segmen, toko=SP, kategori=T) dari
SEMUA 8 sumber sekaligus (Shopee SP+OP, Lazada SP, TikTok SP+OP) - beda
dari build_sp_master() yg cuma Shopee SP, krn coverage Transparan
per-platform jauh lebih jarang/timpang. resolve() dipakai APA ADANYA
(generik thd tier/warna, di sini tier='T' warna='TRP' konstan).

HANYA menulis kolom SKU. Kolom harga TIDAK disentuh sama sekali (utk
SEMUA baris, termasuk Transparan) - sesuai keputusan user.

Lazada perlu dedup_per_product SAMA seperti Reguler/Strip (lesson
2026-08-31: SKU kanonis yg collapse lintas generasi butuh suffix
pembeda krn Lazada wajib unik per varian) - dipakai jg utk Transparan
krn pola yg sama (_TRP_G2/_TRP_G3) sudah ketemu di data yg sudah valid.

Pemakaian: python3 isi_sku_transparan.py
"""
import re
from collections import Counter, defaultdict

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit

FILES = [
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7, False),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 4, 6, 7, False),
    ("UPDATE_SKU_HARGA_OTOPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7, False),
    ("UPDATE_SKU_HARGA_OTOPROTECTION_2.xlsx", "Sheet1", 2, 4, 6, 7, False),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx", "template", 3, 14, 13, 5, True),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_TIKTOK.xlsx", "Template", 3, 6, 11, 6, False),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_1.xlsx", "Template", 3, 6, 11, 6, False),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx", "Template", 3, 6, 11, 6, False),
]


def dedup_suffix(gen, leftover):
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


def is_valid_transparan_sku(sku):
    if not sku or not str(sku).strip():
        return False
    segs = str(sku).split('-')
    return len(segs) == 6 and segs[2] == 'SP' and segs[3] == 'T'


def main():
    master, base_display = op_audit.build_transparan_master()
    candidates = op_audit.expand_slash_aliases(master, base_display)
    literal_bases = op_audit.build_literal_bases(candidates)
    uniform_bases = op_audit.build_uniform_bases(candidates)
    earliest_bases = op_audit.build_earliest_bases(candidates)
    print(f"Kandidat Transparan: {len(candidates)} grup dari {len(base_display)} model")

    for fname, sheet, namecol, varcol, skucol, startrow, needs_dedup in FILES:
        wb = openpyxl.load_workbook(fname, data_only=False)
        ws = wb[sheet]
        stats = Counter()
        used = defaultdict(set)
        if needs_dedup:
            for r in range(startrow, ws.max_row + 1):
                nm = ws.cell(r, namecol).value
                sku = ws.cell(r, skucol).value
                if nm and sku:
                    used[nm].add(sku)

        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm or not op_audit.is_transparan_product(nm):
                continue
            variant = ws.cell(r, varcol).value
            if not variant:
                continue
            existing = ws.cell(r, skucol).value
            if is_valid_transparan_sku(existing):
                stats['sudah_valid'] += 1
                continue

            base = op_audit.clean_base_transparan(nm)
            bn = op_audit.norm(base)
            gen, leftover = op_audit.gen_and_leftover_transparan(variant)
            sku, reason = op_audit.resolve(
                candidates, literal_bases, bn, 'T', 'TRP', gen, leftover, uniform_bases, earliest_bases)
            if not sku:
                stats['tidak_ketemu_' + reason] += 1
                continue

            candidate = sku
            if needs_dedup and candidate in used[nm]:
                suf = dedup_suffix(gen, leftover)
                if suf and (candidate + suf) not in used[nm]:
                    candidate = candidate + suf
                else:
                    i = 2
                    while f"{sku}_{i}" in used[nm]:
                        i += 1
                    candidate = f"{sku}_{i}"
                stats['dedup_suffixed'] += 1
            ws.cell(r, skucol).value = candidate
            if needs_dedup:
                used[nm].add(candidate)
            stats['diperbaiki_' + reason] += 1

        wb.save(fname)
        print(f"\n{fname}")
        print(" ", dict(stats))


if __name__ == '__main__':
    main()
