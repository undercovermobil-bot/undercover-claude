#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bangun file upload SKU Smartprotection dari hasil
`audit_dan_isi_sku_smartprotection.py` - format PERSIS klon file Shopee
asli (bukan workbook baru dari nol), konsisten dgn pola `salin()` di
update_harga_per_sku.py yang sudah terbukti dipakai berhasil sepanjang
proyek ini.

2 bug yang sempat kejadian & sudah diperbaiki di sini (jangan diulang):
1. Kolom di luar 7 kolom yg kita isi (GTIN/Stok/Min-Maks Pembelian dst,
   sampai kolom terakhir file asli) TERNYATA ada isinya di sumber (mis.
   Stok="5" di hampir semua baris) - kalau tidak dikosongkan eksplisit,
   baris hasil gabungan dari file lain bisa kebawa nilai kolom itu punya
   baris LAIN yang tidak relevan (risiko salah timpa Stok dkk saat upload).
2. `ws.cell(row, col, value=None)` itu NO-OP di openpyxl (diperlakukan
   sbg "parameter kosong", bukan "set ke None") - HARUS ambil objek sel
   dulu lalu assign atribut langsung: `cell = ws.cell(row, col);
   cell.value = None`.

Pemakaian: python3 buat_file_update_sku_smartprotection.py
    (baca final_sku_fill2.pkl dari audit sebelumnya - sesuaikan sumbernya
    kalau dipakai ulang utk audit baru)
"""
import copy
import pickle

import openpyxl
from openpyxl.styles import PatternFill

PKL_PATH = "final_sku_fill2.pkl"
SUMBER_TEMPLATE = "sp_sku_fixed/1.xlsx"   # dipakai sbg klon dasar struktur/style
SUMBER_FILES = ["sp_sku_fixed/1.xlsx", "sp_sku_fixed/2.xlsx"]
OUT = "UPDATE_SKU_SMARTPROTECTION.xlsx"
STARTROW = 7
N_KOL_ISI = 7  # Kode Produk, Nama Produk, Kode Variasi, Nama Variasi, SKU Induk, SKU, Harga
KUNING = PatternFill('solid', fgColor='FFFF00')


def salin_baris(ws_s, r_s, ws_d, r_d, n_kol_isi, n_kol_total):
    for c in range(1, n_kol_isi + 1):
        s = ws_s.cell(row=r_s, column=c)
        dd = ws_d.cell(row=r_d, column=c)
        dd.value = s.value
        dd.fill = copy.copy(s.fill)
        dd.font = copy.copy(s.font)
        dd.number_format = s.number_format
        dd.alignment = copy.copy(s.alignment)
        dd.border = copy.copy(s.border)
    # kolom di luar yg kita isi WAJIB dikosongkan eksplisit (lihat catatan
    # bug #1 di docstring) - assignment atribut langsung (bug #2)
    for c in range(n_kol_isi + 1, n_kol_total + 1):
        ws_d.cell(row=r_d, column=c).value = None


def main():
    d = pickle.load(open(PKL_PATH, 'rb'))
    ok = d['ok']  # (target, path, r, pid, varid, variant, sku_baru, metode)

    sheets_f = {f: openpyxl.load_workbook(f, data_only=False)['Sheet1'] for f in SUMBER_FILES}

    wb_out = openpyxl.load_workbook(SUMBER_TEMPLATE, data_only=False)
    ws_out = wb_out['Sheet1']
    n_kol_total = ws_out.max_column

    for i, (target, path, r, pid, varid, variant, sku_baru, metode) in enumerate(ok):
        r_out = STARTROW + i
        salin_baris(sheets_f[path], r, ws_out, r_out, N_KOL_ISI, n_kol_total)
        sel = ws_out.cell(r_out, 6)
        sel.value = sku_baru
        sel.fill = KUNING

    sisa_mulai = STARTROW + len(ok)
    if sisa_mulai <= ws_out.max_row:
        ws_out.delete_rows(sisa_mulai, ws_out.max_row - sisa_mulai + 1)

    wb_out.save(OUT)
    print(f"tersimpan: {OUT}, total baris: {len(ok)}")


if __name__ == '__main__':
    main()
