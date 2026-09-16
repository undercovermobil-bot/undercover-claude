#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tambah kolom atribut & data paket wajib TikTok yang HILANG SAMA SEKALI
di template Otoprotection, 2026-09-14 (REVISI KE-2).

**KOREKSI PENTING dari versi pertama**: versi pertama menaruh kolom
atribut (Garansi/Model/Tahun/Bile) mulai kolom 12, TAPI TERNYATA
TikTok mencocokkan kolom BERDASARKAN POSISI, BUKAN teks header -
dibuktikan dari laporan gagal upload berikutnya (`..._result_5.xlsx`):
nilai "2026" yg ditaruh di kolom 14 (dimaksudkan utk Tahun) malah
mendarat di slot semantik `parcel_length`, sehingga (a) atribut Tahun
TETAP dilaporkan hilang (392 baris, TIDAK berkurang sama sekali dari
sebelumnya) DAN (b) muncul error BARU "Berat produk tidak boleh nol"
(60 baris) krn kolom `parcel_weight` asli (posisi 13) malah ketiban
nilai "Model" dari fix pertama, bukan angka.

Laporan gagal itu (yg py 47 kolom asli + 1 err_info) dipakai sbg
RUJUKAN POSISI PERSIS (bukan cuma teks header) kali ini:
```
1 product_id        7  product_description  13 parcel_weight   32 Garansi (100107)
2 category          8  brand                 14 parcel_length   33 Model
3 product_name       9 price                 15 parcel_width    35 Tahun
4 product_status    10 pre_order_time        16 parcel_height   45 Bile
5 sku_id            11 seller_sku            17 cod
6 variation_value   12 minimum_order_qty     18 main_image
```
(nomor di atas SUDAH dikurangi 1 dari laporan gagal krn file kerja
kita TIDAK py kolom err_info di depan).

Kolom yg TIDAK kita isi (minimum_order_quantity, cod, main_image,
image_2-9, size_chart, tts_product_url, toko_product_url,
special_product_listing_type, auction_starting_price, serta atribut
selain Garansi/Model/Tahun/Bile) DIBIARKAN KOSONG - sesuai konvensi
TikTok mass-edit "kosong = tidak ada perubahan" (row4 kolom
product_status di template resmi eksplisit bilang ini), TIDAK ditulis
sama sekali drpd berisiko menghapus data live (foto produk, dst).

Nilai yg diisi (semua row Transparan yg tersentuh):
- parcel_weight (posisi 13) = **1800** (gram - nilai yg SUDAH TERBUKTI
  benar, dipakai seragam di SEMUA 642 baris Transparan Smartprotection
  yg live & tidak pernah kena error berat)
- parcel_length/width/height (posisi 14/15/16) = **10/15/30** (cm -
  satu2nya contoh row TERISI di data SP, dipakai sbg default aman)
- Garansi (100107, posisi 31) = "Tanpa Garansi"
- Model (100177, posisi 32) = ambil teks setelah "Mercedes Benz " dari
  nama produk, KHUSUS brand Mercedes-Benz
- Tahun (100530, posisi 34) = "2026"
- Bile (102755, posisi 44) = "16:9"

Pemakaian: python3 tambah_atribut_tiktok_op.py
(WAJIB dijalankan ke file HASIL `update_harga_transparan_op.py` +
`trim_ke_transparan_saja.py` yg masih 11 kolom asli - bukan ke file
yg sudah SEMPAT dipatch versi pertama, supaya kolom 12-15 versi salah
tidak ikut kebawa/tertimpa parsial.)
"""
import re

import openpyxl

RE_MERCEDES_MODEL = re.compile(r'mercedes\s*benz\s+(.+)$', re.IGNORECASE)

# (posisi_kolom, header_key, label_tampilan, nilai_default_atau_None)
KOLOM_BARU = [
    (13, 'parcel_weight', 'Berat paket(g)', '1800'),
    (14, 'parcel_length', 'Panjang paket(cm)', '10'),
    (15, 'parcel_width', 'Lebar paket(cm)', '15'),
    (16, 'parcel_height', 'Tinggi paket(cm)', '30'),
    (32, 'product_property/100107', 'Jenis Garansi', 'Tanpa Garansi'),
    (33, 'product_property/100177', 'Model', None),  # diisi per-baris (Mercedes only)
    (35, 'product_property/100530', 'Tahun', '2026'),
    (45, 'product_property/102755', 'Bile', '16:9'),
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
        print(f"{fname}: kolom paket & atribut ditambahkan di posisi yg benar, "
              f"Model terisi di {n_model} baris")


if __name__ == '__main__':
    main()
