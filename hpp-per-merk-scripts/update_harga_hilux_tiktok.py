# -*- coding: utf-8 -*-
"""
File TikTok ulang KHUSUS Toyota Hilux (TYT-HLX), reguler+strip, target harga
sama seperti batch 1-40 sebelumnya (457rb/500rb) - dipisah dari batch 942
baris karena batch itu ditolak TikTok dgn "sku not allow delete" utk SEMUA
56 baris Hilux (lihat project-undercover-harga-referensi.md, 2026-08-26).
Investigasi sudah membuktikan ini BUKAN soal SKU kembar (produk lain dgn
pola sama sukses) - jadi file ini isolasi Hilux saja utk dicoba upload
ulang terpisah, tanpa mengubah SKU sama sekali (cuma harga).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from update_harga_per_sku import proses

TARGET = {
    'TYT-HLX': {'reguler': 457000, 'strip': 500000, 'label': '34 Toyota Hilux'},
}

if __name__ == '__main__':
    out_dir = sys.argv[1]
    folders = sys.argv[2:]
    hasil, laporan, kena_model = proses(TARGET, out_dir, folders, nama_toko='UA')
    print('Listing yang kena:')
    for label in kena_model:
        for nm, n in sorted(kena_model[label].items()):
            print(f'  {n:4d} baris  {nm}')
    for ch, rows in laporan.items():
        print(f'[{ch}] {len(rows)} baris -> {os.path.basename(hasil[ch])}')
