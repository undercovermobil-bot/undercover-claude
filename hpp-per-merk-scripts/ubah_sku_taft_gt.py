#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ubah kode SKU Daihatsu Taft GT dari prefix lama `DHT-TG` jadi `DHT-FRZ`
(kode Feroza), SEKALIGUS harganya (382rb Reguler/425rb Strip) - digabung
1 file supaya tidak ada kolom yang "ketinggalan lama" saat diupload
(lihat pelajaran "file update marketplace menimpa SEMUA kolom" di
feedback-undercover-sku-sync-lessons.md).

Instruksi eksplisit user 2026-08-26: "sekalian yg taft gt bantu ubah kode
SKU nya biar pakai kode SKU nya feroza juga" - menyusul keputusan 2026-08-20
bahwa Taft GT satu SKU dengan Feroza & Rocky lawas (DHT-FRZ).

Cuma toko Shopee (14 baris) - Taft GT tidak dijual di TikTok (sudah dicek,
0 baris ketemu).
"""
import copy
import glob
import sys

import openpyxl
from openpyxl.styles import PatternFill

from update_harga_per_sku import baca_harga, resolve_cols, salin, urai_sku

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
PREFIX_LAMA = "DHT-TG"
PREFIX_BARU = "DHT-FRZ"
SRC_FOLDER = "uc_fixed"
OUT = "UPDATE_SKU_HARGA_TAFT_GT_UA_SHOPEE.xlsx"
KUNING = PatternFill("solid", fgColor="FFFF00")
ORANGE = PatternFill("solid", fgColor="FFC000")


def main():
    target = baca_harga(HARGA_FILE, 49, 49)
    info = target["DHT-FRZ"]
    print(f"target DHT-FRZ: reguler Rp{info['reguler']:,} strip Rp{info['strip']:,}")

    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Sheet1"
    r_out = 1
    n_kena = 0

    for path in sorted(glob.glob(f"{SRC_FOLDER}/*.xlsx")):
        ws = openpyxl.load_workbook(path, data_only=False)["Sheet1"]
        wsv = openpyxl.load_workbook(path, data_only=True)["Sheet1"]
        col = resolve_cols(wsv, "shopee")

        for r in range(7, wsv.max_row + 1):
            sku = wsv.cell(r, col["sku"]).value
            pfx, kat = urai_sku(sku)
            if pfx != PREFIX_LAMA:
                continue
            jenis = {"R": "reguler", "S": "strip"}.get(kat)
            if not jenis:
                continue

            if r_out == 1:
                # salin header (baris 1-6) apa adanya dari file pertama yg kena
                for hr in range(1, 7):
                    salin(ws, hr, ws_out, hr, ws.max_column)
                r_out = 7

            salin(ws, r, ws_out, r_out, ws.max_column)
            sku_baru = PREFIX_BARU + sku[len(PREFIX_LAMA):]
            sel_sku = ws_out.cell(r_out, col["sku"])
            sel_sku.value = sku_baru
            sel_sku.fill = KUNING
            sel_harga = ws_out.cell(r_out, col["harga"])
            sel_harga.value = info[jenis]
            sel_harga.fill = ORANGE
            r_out += 1
            n_kena += 1

    if n_kena == 0:
        print("tidak ada baris DHT-TG ketemu - tidak ada yang perlu ditulis")
        return

    wb_out.save(OUT)
    print(f"tersimpan: {OUT}")
    print(f"baris diubah: {n_kena} (kolom SKU=kuning, kolom Harga=oranye)")


if __name__ == "__main__":
    main()
