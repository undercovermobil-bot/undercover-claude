#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gabungan FINAL utk 1x upload ke Shopee: harga batch 1-40 + Feroza (#49) +
SKU Taft GT diubah ke DHT-FRZ, SEMUA dalam 1 file (bukan file terpisah).

User (2026-08-26): "Aku belum upload file ecommercenya, tambahkan
perubahannya di file ini supaya bisa langsung" - jadi file harga
UPDATE_HARGA_UA_SHOPEE.xlsx yang sebelumnya dikirim (882 baris, Taft GT harga
sudah benar via ALIAS tapi SKU-nya masih DHT-TG) digabung ulang dari SUMBER
ASLI (bukan re-edit file hasil) supaya satu-satunya sumber kebenaran tetap
5 file Shopee mentah - konsisten dgn cara kerja proses() di
update_harga_per_sku.py, cuma ditambah 1 langkah: kalau prefix ASLI baris itu
`DHT-TG`, kolom SKU ikut ditulis ulang jadi `DHT-FRZ...`.

TikTok TIDAK perlu diregenerasi - Taft GT tidak dijual di sana (sudah
diverifikasi 0 baris), jadi file TikTok yang sudah dikirim sebelumnya
(UPDATE_HARGA_UC_TIKTOK_1-40_v2/UPDATE_HARGA_UA_TIKTOK.xlsx) tetap berlaku
apa adanya, tidak perlu disentuh lagi.
"""
import glob
import sys

import openpyxl
from openpyxl.styles import PatternFill

from update_harga_per_sku import (ALIAS, KAT_KE_JENIS, KECUALI, baca_harga,
                                   is_outdoor_polos, resolve_cols, salin,
                                   urai_sku)

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
SRC_FOLDER = "uc_fixed"
OUT = "UPDATE_HARGA_UA_SHOPEE.xlsx"
PREFIX_TAFTGT_LAMA = "DHT-TG"
PREFIX_TAFTGT_BARU = "DHT-FRZ"
ORANGE = PatternFill("solid", fgColor="FFC000")
KUNING = PatternFill("solid", fgColor="FFFF00")


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    target = baca_harga(HARGA_FILE, 1, 40)
    target.update(baca_harga(HARGA_FILE, 49, 49))
    print(f"target: {len(target)} prefix (1-40 + Feroza #49)")

    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Sheet1"
    r_out = 1
    n_harga, n_sku = 0, 0

    for path in sorted(glob.glob(f"{SRC_FOLDER}/*.xlsx")):
        ws = openpyxl.load_workbook(path, data_only=False)["Sheet1"]
        wsv = openpyxl.load_workbook(path, data_only=True)["Sheet1"]
        col = resolve_cols(wsv, "shopee")

        for r in range(7, wsv.max_row + 1):
            sku = wsv.cell(r, col["sku"]).value
            pfx, kat = urai_sku(sku)
            pfx_resolved = ALIAS.get(pfx, pfx)
            if pfx_resolved not in target:
                continue
            nm = str(wsv.cell(r, col["nama"]).value or "")
            if any(k in nm.lower() for k in KECUALI):
                continue
            if is_outdoor_polos(nm):
                continue
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue

            baru = target[pfx_resolved][jenis]
            lama = wsv.cell(r, col["harga"]).value
            sku_baru = sku
            ubah_sku = pfx == PREFIX_TAFTGT_LAMA
            if ubah_sku:
                sku_baru = PREFIX_TAFTGT_BARU + sku[len(PREFIX_TAFTGT_LAMA):]

            harga_sama = False
            try:
                harga_sama = lama is not None and int(float(lama)) == baru
            except (TypeError, ValueError):
                pass
            if harga_sama and not ubah_sku:
                continue  # sudah benar semua, tidak perlu ikut file update

            if r_out == 1:
                for hr in range(1, 7):
                    salin(ws, hr, ws_out, hr, ws.max_column)
                r_out = 7

            salin(ws, r, ws_out, r_out, ws.max_column)
            if not harga_sama:
                sel = ws_out.cell(r_out, col["harga"])
                sel.value = baru
                sel.fill = ORANGE
                n_harga += 1
            if ubah_sku:
                sel = ws_out.cell(r_out, col["sku"])
                sel.value = sku_baru
                sel.fill = KUNING
                n_sku += 1
            r_out += 1

    import os
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUT)
    wb_out.save(out_path)
    print(f"tersimpan: {out_path}")
    print(f"total baris: {r_out - 7}")
    print(f"  baris dgn harga berubah : {n_harga}")
    print(f"  baris dgn SKU berubah   : {n_sku} (Daihatsu Taft GT, {PREFIX_TAFTGT_LAMA}->{PREFIX_TAFTGT_BARU})")


if __name__ == "__main__":
    main()
