#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi atribut wajib TikTok "Tahun" (product_property/100530, kolom 34 di
sheet Template) yang kosong, 2026-09-14.

Konteks: user upload TIKTOK_SMARTPROTECTION.xlsx (642 baris Transparan),
gagal 218/222 produk (632 baris) dengan error "atribut produk is
missing... ID:100530, nama: Tahun" + 3 baris "sku not allow add"
terpisah (Toyota 86 Transparan - bukan soal data, kemungkinan status
listing/SKU ID sudah tidak aktif di TikTok, perlu dicek manual di
Seller Center bukan dari file).

Ini BUG YANG SAMA yang sudah ditemukan & diperbaiki sesi lain utk
Otoprotection (`project-undercover-otoprotection-status.md`,
`perbaikan_otoprotection_final.py`): kolom atribut wajib TikTok kosong
di MAYORITAS baris SEJAK AWAL (bawaan file sumber, bukan disebabkan
perubahan harga sesi ini - dicek: 7020/7466 baris kosong di file sumber
asli `tiktok_src.xlsx`) - TikTok tolak SELURUH produk kalau ADA SATU
baris saja yang atributnya kosong, bukan cuma baris yang benar2 diedit.
Keputusan user (dari sesi lain, 2026-09-xx): isi blank dengan **"2026"**.

Pemakaian: python3 fix_atribut_tahun_tiktok_sp.py
"""
import openpyxl

TAHUN_COL = 34  # product_property/100530


def main():
    wb = openpyxl.load_workbook('TIKTOK_SMARTPROTECTION.xlsx', data_only=False)
    ws = wb['Template']
    n = 0
    for r in range(6, ws.max_row + 1):
        v = ws.cell(r, TAHUN_COL).value
        if v is None or (isinstance(v, str) and not v.strip()):
            ws.cell(r, TAHUN_COL).value = '2026'
            n += 1
    wb.save('TIKTOK_SMARTPROTECTION.xlsx')
    print(f"Atribut Tahun diisi '2026' di {n} baris")


if __name__ == '__main__':
    main()
