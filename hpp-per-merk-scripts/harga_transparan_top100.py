#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harga baru Transparan utk 100 model di "DATA UC HPP Top 100 Terlaris.xlsx",
2026-09-11.

Dasar dari user: sheet 'Transparan' kolom 'Harga Jual Terbaru', 2 baris
relevan (City Car/SUV = 195716.1981, MPV = 430175.4386), dibulatkan
ribuan ke atas -> 196.000 (tingkat "3 pcs/roll", mobil ukuran DI BAWAH
Fortuner/Pajero) dan 431.000 (tingkat "1 pcs/roll", mobil ukuran SE-
FORTUNER/PAJERO KE ATAS). Tiap tingkat punya rentang toleransi +Rp3.000
("tergantung ukurannya") - kecil: 196rb-199rb, besar: 431rb-434rb.

**PAKAI DATA PANJANG_MM/KATEGORI YANG SUDAH ADA** (dari
`harga_baru_sp_op_matriks_v2.py`, dipakai jg utk harga Reguler/Strip SP-OP
"Harga Baru SP-OP (matriks) FINAL.xlsx") - BUKAN nebak manual dari nol.
Semua 100 nama produk di file HPP Top 100 Terlaris COCOK PERSIS dgn key
PANJANG_MM (dicek: 100/100 ketemu) - dataset panjang bodi (mm) per model
ini sudah divalidasi & dipakai across proyek, jauh lebih presisi drpd
klasifikasi segmen/tipe-bodi manual dari nol.

Metode (adaptasi `kalibrasi_grup()`/`posisi()` dari
harga_baru_sp_op_matriks_v2/v3.py, MAX_SPREAD diperkecil dari Rp5.000 ke
Rp3.000 sesuai batas yg diminta user utk Transparan):
1. Ambang batas tingkat: PANJANG_MM Toyota Fortuner (4795mm, LEBIH KECIL
   dari Pajero Sport 4825mm) - "se-Fortuner/Pajero ke atas" = >= 4795mm.
   >=4795mm -> tingkat Besar (lantai 431rb). <4795mm -> tingkat Kecil
   (lantai 196rb).
2. Di dalam tiap tingkat, kalibrasi (lo, rentang, n_langkah) dari SEMUA
   anggota tingkat itu (bukan per Pcs/Roll x Kategori spt v2/v3, krn
   sheet Transparan cuma py 2 tingkat kasar bukan Pcs/Roll per-model
   lengkap) - MAX_SPREAD=3000, MM_PER_STEP=100 (~100mm selisih panjang =
   +Rp1.000, dibatasi +Rp3.000).
3. Posisi tiap mobil dlm rentang tingkatnya PROPORSIONAL thd panjang
   bodinya - mobil terpendek dapat harga lantai (196rb/431rb), makin
   panjang makin naik sampai +3rb.

Pemakaian: python3 harga_transparan_top100.py
"""
import math
import sys

import openpyxl

sys.path.insert(0, '.')
from harga_baru_sp_op_matriks_v2 import KATEGORI, PANJANG_MM

SRC = "Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx"
OUT = "Referensi_Harga_Baru_Transparan_Top100.xlsx"

LANTAI_KECIL = 196000
LANTAI_BESAR = 431000
AMBANG_MM = PANJANG_MM['Toyota Fortuner']  # 4795, lebih kecil dari Pajero Sport (4825)
MAX_SPREAD = 3000
STEP = 1000
MM_PER_STEP = 100


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
    src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = src['Top 100 Terlaris']
    names = []
    for r in range(2, ws_src.max_row + 1):
        nm = ws_src.cell(r, 1).value
        if nm:
            names.append(nm)
    assert len(names) == 100, f"harus 100 model, ada {len(names)}"

    missing = [n for n in names if n not in PANJANG_MM]
    if missing:
        raise SystemExit(f"Model tanpa data PANJANG_MM: {missing}")

    kecil = [n for n in names if PANJANG_MM[n] < AMBANG_MM]
    besar = [n for n in names if PANJANG_MM[n] >= AMBANG_MM]
    kalib_kecil = kalibrasi_grup([PANJANG_MM[n] for n in kecil])
    kalib_besar = kalibrasi_grup([PANJANG_MM[n] for n in besar])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Harga Transparan"
    ws.append(["No", "Nama Produk", "Kategori Bodi", "Panjang (mm)", "Tingkat",
               "Harga Baru Transparan"])

    hasil = []
    for i, nm in enumerate(names, start=1):
        panjang = PANJANG_MM[nm]
        if panjang >= AMBANG_MM:
            harga = LANTAI_BESAR + posisi(panjang, kalib_besar)
            tingkat = "Besar (se-Fortuner/Pajero ke atas, basis 1 pcs/roll)"
        else:
            harga = LANTAI_KECIL + posisi(panjang, kalib_kecil)
            tingkat = "Kecil (di bawah Fortuner/Pajero, basis 3 pcs/roll)"
        hasil.append((i, nm, KATEGORI.get(nm, ''), panjang, tingkat, harga))
        ws.append([i, nm, KATEGORI.get(nm, ''), panjang, tingkat, harga])

    for col, width in zip('ABCDEF', [4, 32, 16, 14, 50, 20]):
        ws.column_dimensions[col].width = width

    wb.save(OUT)
    print(f"Tersimpan: {OUT} ({len(names)} model)")
    print(f"Ambang batas: {AMBANG_MM}mm (panjang Toyota Fortuner)")
    print(f"Tingkat Kecil: {len(kecil)} model, rentang panjang "
          f"{min(PANJANG_MM[n] for n in kecil)}-{max(PANJANG_MM[n] for n in kecil)}mm, "
          f"kalibrasi spread={kalib_kecil[2]*STEP}")
    print(f"Tingkat Besar: {len(besar)} model, rentang panjang "
          f"{min(PANJANG_MM[n] for n in besar)}-{max(PANJANG_MM[n] for n in besar)}mm, "
          f"kalibrasi spread={kalib_besar[2]*STEP}")

    print("\nContoh Fortuner/Pajero Sport (harus di lantai 431rb):")
    for i, nm, kat, panjang, tingkat, harga in hasil:
        if nm in ('Toyota Fortuner', 'Mitsubishi Pajero Sport'):
            print(f"  {nm}: {panjang}mm -> Rp{harga:,}".replace(',', '.'))


if __name__ == '__main__':
    main()
