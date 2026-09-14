#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tambah kolom atribut wajib TikTok yang HILANG SAMA SEKALI di template
Otoprotection (2026-09-14, lanjutan). Beda dari kasus SP (kolomnya ADA
tapi kosong) - template TikTok OP yang diberikan user cuma 11 kolom,
TIDAK ADA kolom product_property sama sekali. User upload, gagal 398
baris/190 produk: 392 "Tahun" (100530) + 6 "Model" (100177, khusus
brand Mercedes-Benz).

Laporan hasil gagal dari TikTok (`..._result_3.xlsx`) ternyata MEMUAT
struktur kolom LENGKAP (48 kolom, row1=header teknis
'product_property/XXXXX', row3=label tampilan, row4=Wajib/Opsional,
row5=instruksi) - dipakai sbg RUJUKAN header persis, BUKAN sbg file
dasar (laporan itu cuma berisi 398 baris yg GAGAL, bukan semua 460
baris yg sukses+gagal, jadi tidak boleh dipakai gantikan file asli).

Kolom ditambahkan mulai kolom 12 (setelah 'seller_sku'):
- 100107 Garansi = "Tanpa Garansi" (preventif, sama spt SP)
- 100177 Model = ambil teks setelah "Mercedes Benz " dari nama produk,
  KHUSUS baris brand Mercedes-Benz (kosong utk brand lain - atribut
  ini spesifik Mercedes, sudah dikonfirmasi sesi lain utk Otoprotection)
- 100530 Tahun = "2026" (sesuai error report)
- 102755 Bile = "16:9" (preventif, sama spt SP - hindari ronde gagal
  berikutnya persis pola yg sudah terjadi di SP)

Pemakaian: python3 tambah_atribut_tiktok_op.py
"""
import re

import openpyxl

RE_MERCEDES_MODEL = re.compile(r'mercedes\s*benz\s+(.+)$', re.IGNORECASE)

KOLOM_BARU = [
    (12, 'product_property/100107', 'Jenis Garansi', 'Tanpa Garansi'),
    (13, 'product_property/100177', 'Model', None),  # diisi per-baris (Mercedes only)
    (14, 'product_property/100530', 'Tahun', '2026'),
    (15, 'product_property/102755', 'Bile', '16:9'),
]

FILES = ["TIKTOK_OTOPROTECTION_1.xlsx", "TIKTOK_OTOPROTECTION_2.xlsx"]


def main():
    for fname in FILES:
        wb = openpyxl.load_workbook(fname, data_only=False)
        ws = wb['Template']

        for col, key, label, _default in KOLOM_BARU:
            ws.cell(1, col).value = key
            ws.cell(3, col).value = label
            ws.cell(4, col).value = 'Wajib Diisi Sesuai Syarat'
            # row 5 (instruksi) dilewati - ada merged cell di beberapa
            # kolom (mis. N5:P5), tidak fungsional utk upload

        n_model = 0
        for r in range(6, ws.max_row + 1):
            nm = ws.cell(r, 3).value
            if not nm:
                continue
            for col, key, label, default in KOLOM_BARU:
                if key == 'product_property/100177':
                    m = RE_MERCEDES_MODEL.search(nm)
                    if m:
                        ws.cell(r, col).value = m.group(1).strip()
                        n_model += 1
                else:
                    ws.cell(r, col).value = default

        wb.save(fname)
        print(f"{fname}: kolom atribut ditambahkan, Model terisi di {n_model} baris")


if __name__ == '__main__':
    main()
