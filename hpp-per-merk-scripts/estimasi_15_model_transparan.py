#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi harga Transparan utk 15 model yang sebelumnya dilewati (0 referensi
ukuran di dataset PANJANG_MM), 2026-09-14. User pilih: estimasi sekarang
pakai pengetahuan otomotif umum, ditandai jelas sbg ESTIMASI (beda dari
213 model lain yang datanya tervalidasi/eksplisit).

Kalibrasi tingkat kecil/besar TETAP dikunci dari 100 model Top-Terlaris
(sama seperti `update_harga_transparan_sp.py`) - model estimasi ini
diposisikan pakai skala yang sama, diklem 0..3000.

Dijalankan ke 4 file yang SUDAH dipotong ke Transparan-saja
(`trim_ke_transparan_saja.py`) - HANYA isi baris yang price-nya masih
kosong/harga lama (15 model ini), baris lain (yang sudah dapat harga di
run sebelumnya) tidak disentuh.

Pemakaian: python3 estimasi_15_model_transparan.py
"""
import math

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit
import harga_baru_sp_op_matriks_v2 as m

LANTAI_KECIL = 196000
LANTAI_BESAR = 431000
AMBANG_MM = m.PANJANG_MM['Toyota Fortuner']
MAX_SPREAD = 3000
STEP = 1000
MM_PER_STEP = 100
PAKSA_BESAR = {'Toyota Innova'}

TOP100_SRC = "Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx"

# Estimasi panjang bodi (mm) - PENGETAHUAN OTOMOTIF UMUM, BUKAN dari
# dataset PANJANG_MM tervalidasi. Ditandai sbg estimasi ke user.
ESTIMASI_MM = {
    'Nissan Cedric': (4720, 'sedan JDM besar (Y31-Y33), mirip kelas Toyota Crown tapi umumnya sedikit lebih pendek'),
    'Mitsubishi Eclipse': (4460, 'sports coupe 2-pintu kompak'),
    'Peugeot 306': (4200, 'hatchback/sedan kompak 90an'),
    'Peugeot 3008': (4450, 'SUV/crossover kompak, sekelas CR-V/CX-5'),
    'Suzuki Aerio Sedan': (4300, 'varian sedan dari Aerio Hatchback (4145mm) + tambahan bagasi'),
    'Volkswagen Passat': (4780, 'sedan menengah, rata2 lintas generasi (varian lama lbh pendek, terbaru B8 ~4870mm)'),
    'Ford Fusion': (4240, 'versi Indonesia = hatchback/crossover kompak basis Fiesta, BUKAN sedan Amerika'),
    'Mazda 3 Hatchback': (4460, "~200mm lebih pendek dari 'Mazda 3' (Sedan, 4660mm) - pola umum sedan vs hatchback sechassis"),
    'Mazda Lantis': (4380, 'nama JDM utk Mazda 323/Astina/Familia, hatchback/sedan kompak'),
    'Mercedes Benz GLB Class': (4634, 'SUV compact 7-seat terkecil di lini Mercedes'),
    'Wuling Darion': (4720, '7-seat crossover MPV kelas menengah, sekelas Xpander/sedikit lebih besar'),
    'Hummer H3': (4783, 'SUV terkecil Hummer, PAS DI BAWAH ambang Fortuner (4795mm) scr spek'),
    'Hyundai Matrix': (4325, 'compact tall-hatchback/MPV mini awal 2000an'),
    'Volkswagen Fox': (3835, 'hatchback kecil/city car'),
    'Daihatsu Gran Max': (4195, "pakai panjang varian Pick Up (entri 'Daihatsu Gran Max Pick Up' yg sudah ada) - listing tak sebut Pick Up/Minibus"),
}

FILES = [
    ("SHOPEE_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 7, 7),
    ("SHOPEE_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 7, 7),
    ("LAZADA_SMARTPROTECTION.xlsx", "template", 3, 9, 5),
    ("TIKTOK_SMARTPROTECTION.xlsx", "Template", 3, 9, 6),
]


def kalibrasi_grup(panjang_list):
    unik = sorted(set(panjang_list))
    lo, hi = unik[0], unik[-1]
    rentang = hi - lo
    if rentang == 0:
        return lo, 0, 0
    spread = min(int(math.floor(rentang / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
    n_langkah = spread // STEP
    return lo, rentang, n_langkah


def posisi(panjang, kalib):
    lo, rentang, n_langkah = kalib
    if rentang == 0:
        return 0
    mentah = int(math.floor((panjang - lo) / rentang * n_langkah + 0.5)) * STEP
    return max(0, min(mentah, MAX_SPREAD))


def main():
    src = openpyxl.load_workbook(TOP100_SRC, data_only=True)
    ws_src = src['Top 100 Terlaris']
    top100 = [ws_src.cell(r, 1).value for r in range(2, ws_src.max_row + 1)
               if ws_src.cell(r, 1).value]
    kecil0 = [n for n in top100 if m.PANJANG_MM[n] < AMBANG_MM and n not in PAKSA_BESAR]
    besar0 = [n for n in top100 if m.PANJANG_MM[n] >= AMBANG_MM and n not in PAKSA_BESAR]
    kalib_kecil = kalibrasi_grup([m.PANJANG_MM[n] for n in kecil0])
    kalib_besar = kalibrasi_grup([m.PANJANG_MM[n] for n in besar0])

    harga_model = {}
    print("Estimasi 15 model:")
    for nm, (panjang, alasan) in ESTIMASI_MM.items():
        if panjang >= AMBANG_MM:
            harga = LANTAI_BESAR + posisi(panjang, kalib_besar)
            tingkat = "Besar"
        else:
            harga = LANTAI_KECIL + posisi(panjang, kalib_kecil)
            tingkat = "Kecil"
        harga_model[nm] = harga
        print(f"  {nm:28} {panjang}mm  {tingkat:6} -> Rp{harga:,}  ({alasan})".replace(',', '.'))

    idx_by_norm = {op_audit.norm(k): v for k, v in harga_model.items()}

    for fname, sheet, namecol, pricecol, startrow in FILES:
        wb = openpyxl.load_workbook(fname, data_only=False)
        ws = wb[sheet]
        n_updated = 0
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm:
                continue
            base = op_audit.clean_base_transparan(nm)
            bn = op_audit.norm(base)
            if bn in idx_by_norm:
                ws.cell(r, pricecol).value = idx_by_norm[bn]
                n_updated += 1
        wb.save(fname)
        print(f"{fname}: {n_updated} baris diisi harga estimasi")


if __name__ == '__main__':
    main()
