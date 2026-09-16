#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versi Lazada dari batch harga 1-40 + Feroza (#49) yang sudah jalan di
Shopee (`update_batch_1_40_plus_feroza_taftgt_sku.py`) dan TikTok. User
upload file export "Harga & Stok" Lazada UA (sheet `template`, header baris
1, data mulai baris 5 - format INI SUDAH didukung `proses()` di
`update_harga_per_sku.py` lewat SHEET/STARTROW/HEADER_KEY['lazada'], jadi
tidak perlu script pemroses baru, cukup panggil proses() langsung).

Taft GT TIDAK ada sama sekali di Lazada (dicek eksplisit: 0 baris nama
"Taft" maupun SKU "DHT-TG") - sama seperti TikTok - jadi tidak perlu
langkah ubah-SKU seperti versi Shopee.

Produk #1-10 (Avanza, Brio, Innova, Jazz, Ertiga, HR-V, Agya, Xenia/Veloz,
Livina) ternyata SUDAH punya harga target yang benar di Lazada sebelum
batch ini jalan - proses() otomatis skip baris yang sudah benar, jadi
0 baris dari produk itu ikut ke file output (bukan bug/lolos).

Pemakaian:
    python3 update_batch_1_40_plus_feroza_lazada.py <harga_file.xlsx> \
        <folder_lazada_src> <out_dir>
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from update_harga_per_sku import baca_harga, proses

if __name__ == '__main__':
    harga_file = sys.argv[1]
    src_folder = sys.argv[2]
    out_dir = sys.argv[3]

    target = baca_harga(harga_file, 1, 40)
    target.update(baca_harga(harga_file, 49, 49))
    print(f'target: {len(target)} prefix (1-40 + Feroza #49)')

    hasil, laporan, kena_model = proses(target, out_dir, [src_folder], nama_toko='UA')
    for ch, rows in laporan.items():
        print(f'[{ch}] {len(rows)} baris -> {os.path.basename(hasil[ch])}')
    print('\nModel yang kena:')
    for label in sorted(kena_model, key=lambda x: int(x.split()[0])):
        for nm, n in sorted(kena_model[label].items()):
            print(f'  {label:26s} {n:4d} baris  {nm}')
