#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Potong file hasil `update_harga_transparan_sp.py` supaya HANYA berisi
baris Transparan (yang harganya benar-benar berubah) - 2026-09-14.

User tegur: file yang dikirim sebelumnya masih bawa SELURUH katalog
(baris non-Transparan yang harganya TIDAK disentuh ikut kebawa) - salah
ingat lesson 2026-07-11: file mass-upload cuma boleh berisi baris yang
BENAR-BENAR berubah, produk yang tidak berubah TIDAK BOLEH ikut disertakan
krn upload massal bisa me-reset stok/data produk itu di e-commerce.

Metode: sama seperti `buat_file_reupload_transparan.py` - hapus baris via
delete_rows per rentang kontigu (bukan satu-satu, supaya tidak O(n^2)
utk file besar), cuma pembeda: kali ini SEMUA baris Transparan
dipertahankan (tidak ada baris "extra error" khusus krn ini bukan
konteks laporan upload gagal).

Pemakaian: python3 trim_ke_transparan_saja.py
"""
import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit

FILES = [
    ("SHOPEE_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 7),
    ("SHOPEE_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 7),
    ("LAZADA_SMARTPROTECTION.xlsx", "template", 3, 5),
    ("TIKTOK_SMARTPROTECTION.xlsx", "Template", 3, 6),
]


def to_ranges(rows):
    ranges = []
    start = prev = None
    for r in rows:
        if start is None:
            start = r
        elif r != prev + 1:
            ranges.append((start, prev - start + 1))
            start = r
        prev = r
    if start is not None:
        ranges.append((start, prev - start + 1))
    return ranges


def main():
    for fname, sheet, namecol, startrow in FILES:
        wb = openpyxl.load_workbook(fname, data_only=False)
        ws = wb[sheet]

        to_delete = []
        kept = 0
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if nm and op_audit.is_transparan_product(nm):
                kept += 1
                continue
            to_delete.append(r)

        for start, count in reversed(to_ranges(to_delete)):
            ws.delete_rows(start, count)

        wb.save(fname)
        print(f"{fname}: transparan dipertahankan={kept}  dihapus={len(to_delete)}")


if __name__ == '__main__':
    main()
