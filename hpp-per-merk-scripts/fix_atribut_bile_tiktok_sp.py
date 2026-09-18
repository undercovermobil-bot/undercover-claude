#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi atribut wajib TikTok "Bile" (product_property/102755) yang kosong,
2026-09-14 (lanjutan). Setelah "Tahun" (100530) diisi, TikTok tolak lagi
632 baris/218 produk dengan atribut BERIKUTNYA: ID:102755, nama: Bile -
pola "TikTok laporkan atribut wajib satu per satu" yang sudah
didokumentasikan sesi lain (`feedback-undercover-sku-sync-lessons.md`
baris ~350-363, `project-undercover-otoprotection-status.md`).

Nilai yang sudah dikonfirmasi user dari kasus sebelumnya: **"16:9"**
(satu2nya nilai yang muncul di baris yang sudah terisi, konsisten dgn
history Otoprotection & UA "atribut 100530=2026, 102755=16:9").

Sekalian isi `product_property/100107` (Jenis Garansi, kolom 32) dgn
**"Tanpa Garansi"** - preventif (bukan reaktif), krn dari kasus
Otoprotection/UA sebelumnya atribut ini KADANG (bukan selalu) ikut
wajib utk produk tertentu (Hyundai Kona wajib, Geely EX2 tidak) -
mengisi wajar krn "Tanpa Garansi" plausible utk semua cover mobil &
sudah ada presedennya, drpd tunggu upload gagal ronde ke-3.

Kolom lain (100335, 100556-100579, 100701) SENGAJA TIDAK diisi - 100%
kosong di SELURUH file (tidak ada 1 pun contoh nilai terisi utk
dijadikan rujukan) & temanya tidak relevan sama sekali ke cover mobil
(alat suspensi, alat ukur, perkakas tangan, dll - kemungkinan besar
kolom template kategori lain yg tidak berlaku), DAN belum pernah
dilaporkan sbg wajib di error manapun sejauh ini - isi tebakan salah
lebih berisiko drpd dibiarkan kosong.

Pemakaian: python3 fix_atribut_bile_tiktok_sp.py
"""
import openpyxl

BILE_COL = 43   # product_property/102755
GARANSI_COL = 32  # product_property/100107


def main():
    wb = openpyxl.load_workbook('TIKTOK_SMARTPROTECTION.xlsx', data_only=False)
    ws = wb['Template']
    n_bile = n_garansi = 0
    for r in range(6, ws.max_row + 1):
        v = ws.cell(r, BILE_COL).value
        if v is None or (isinstance(v, str) and not v.strip()):
            ws.cell(r, BILE_COL).value = '16:9'
            n_bile += 1
        v2 = ws.cell(r, GARANSI_COL).value
        if v2 is None or (isinstance(v2, str) and not v2.strip()):
            ws.cell(r, GARANSI_COL).value = 'Tanpa Garansi'
            n_garansi += 1
    wb.save('TIKTOK_SMARTPROTECTION.xlsx')
    print(f"Bile (102755) diisi '16:9' di {n_bile} baris")
    print(f"Garansi (100107) diisi 'Tanpa Garansi' di {n_garansi} baris")


if __name__ == '__main__':
    main()
