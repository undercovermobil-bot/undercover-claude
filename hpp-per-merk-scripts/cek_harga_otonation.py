#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cek APAKAH file listing Otonation (OT) yang baru diupload user sudah sesuai
dengan harga baru top-100 - HANYA membaca & membandingkan, TIDAK menulis apa
pun ke listing.

Reuse helper yang sudah divalidasi dari branch claude/repo-memory-access-4hthja
(scripts/update_harga_per_sku.py): PREFIX{} (nama model -> prefix SKU,
diverifikasi langsung ke data OT), ALIAS{} (prefix belum-sinkron -> prefix
induk), is_outdoor_polos() (guard "Outdoor" polos/"Extreme Outdoor" = tier
Premium/Exclusive, BUKAN Reguler - persis instruksi user "hanya yang semi
outdoor atau yg setara"), urai_sku(), baca_harga().

Target harga: 'Harga Baru UC Top 100 (matriks).xlsx' (dibuat pakai
harga_baru_matriks.py yang identik dgn HARGA_BARU_TOP100_v4.xlsx yang dipakai
saat eksekusi asli 2026-08-18) - struktur sheet 'Harga Baru' sama persis
sehingga baca_harga() bisa dipakai apa adanya.
"""
import sys
from collections import defaultdict

import openpyxl

sys.path.insert(0, ".")
from update_harga_per_sku import (ALIAS, KECUALI, PREFIX, TAMBAHAN_STRIP,
                                   baca_harga, is_outdoor_polos, urai_sku)

TARGET_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
LISTING_FILES = ["ot_fixed/1.xlsx", "ot_fixed/2.xlsx"]

# File listing OT sumber (Shopee, sudah kena bug XML activePane - perbaiki dulu
# pakai repair_xlsx.py sebelum dipakai di sini) berubah tiap kali user upload
# baru; kalau mau jalankan ulang, ganti TARGET_FILE/LISTING_FILES di atas atau
# pass lewat argv: python3 cek_harga_otonation.py <target.xlsx> <listing1.xlsx> [listing2.xlsx ...]
if len(sys.argv) > 2:
    TARGET_FILE = sys.argv[1]
    LISTING_FILES = sys.argv[2:]


def main():
    target = baca_harga(TARGET_FILE, 1, 100)
    print(f"target: {len(target)} prefix SKU (dari {TARGET_FILE})\n")

    cocok = 0
    beda = []
    dilewati_outdoor_polos = 0
    dilewati_kecuali = 0
    dilewati_kategori_lain = defaultdict(int)
    dilewati_prefix_di_luar_scope = defaultdict(int)
    total_semi = 0

    for f in LISTING_FILES:
        wb = openpyxl.load_workbook(f, data_only=True)
        ws = wb["Sheet1"]
        for r in ws.iter_rows(min_row=7, values_only=True):
            nama, var, sku, harga = r[1], r[3], r[5], r[6]
            if not nama or not sku:
                continue
            low = nama.lower()
            if is_outdoor_polos(nama):
                dilewati_outdoor_polos += 1
                continue
            if any(k in low for k in KECUALI):
                dilewati_kecuali += 1
                continue
            prefix, kat = urai_sku(sku)
            if prefix is None:
                continue
            prefix = ALIAS.get(prefix, prefix)
            if kat not in ("R", "S"):
                dilewati_kategori_lain[kat] += 1
                continue
            if prefix not in target:
                dilewati_prefix_di_luar_scope[prefix] += 1
                continue

            total_semi += 1
            jenis = "reguler" if kat == "R" else "strip"
            expect = target[prefix][jenis]
            try:
                actual = int(float(harga))
            except (TypeError, ValueError):
                actual = None
            if actual == expect:
                cocok += 1
            else:
                beda.append((f, target[prefix]["label"], prefix, jenis, nama, var, sku,
                              actual, expect))

    print(f"baris 'Semi Outdoor'/setara (R & S) dalam scope top-100: {total_semi}")
    print(f"  cocok dgn target : {cocok}")
    print(f"  BEDA dari target : {len(beda)}")
    print(f"\ndilewati - 'Outdoor' polos/Extreme (tier Premium/Exclusive, bukan scope): {dilewati_outdoor_polos}")
    print(f"dilewati - masuk KECUALI (custom/roofbox/x-gear): {dilewati_kecuali}")
    print(f"dilewati - kategori SKU lain (P/E/T): {dict(dilewati_kategori_lain)}")
    print(f"dilewati - prefix di luar 100 top-seller (produk lain, wajar): {sum(dilewati_prefix_di_luar_scope.values())} baris, {len(dilewati_prefix_di_luar_scope)} prefix unik")

    if beda:
        print(f"\n=== {len(beda)} BARIS BEDA DARI TARGET ===")
        by_label = defaultdict(list)
        for row in beda:
            by_label[row[1]].append(row)
        for label, rows in sorted(by_label.items(), key=lambda x: int(x[0].split()[0])):
            print(f"\n  {label}  ({len(rows)} baris beda)")
            for f, _, prefix, jenis, nama, var, sku, actual, expect in rows[:6]:
                a = f"Rp{actual:,}" if actual is not None else repr(actual)
                print(f"    [{f}] {jenis:8s} SKU={sku:24s} aktual={a:>12} target=Rp{expect:,}  ({nama[:50]})".replace(",", "."))
            if len(rows) > 6:
                print(f"    ... +{len(rows)-6} baris lagi")


if __name__ == "__main__":
    main()
