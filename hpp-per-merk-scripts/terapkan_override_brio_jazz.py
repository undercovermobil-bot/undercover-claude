#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Override manual: Honda Brio & Honda Jazz PENGECUALIAN dari spread per-panjang
bodi, dipatok PERSIS di lantai kelas pcs=6 (Rp332.000 Reguler / Rp375.000 Strip),
bukan lantai+3rb hasil spread normal (Rp335rb/378rb).

Instruksi eksplisit user 2026-08-26 (AskUserQuestion): "kalau tidak salah khusus
brio dan jazz saja yg pakai plafon terbawah itu, di 332rb, yg produk lainnya
tetap sesuai plan sebelumnya aja pakai harga yg di spread itu" - dikonfirmasi
setelah user menunjukkan screenshot listing Shopee live Honda Brio Reguler
Rp332.000/Strip Rp375.000, yang TIDAK cocok dgn hasil spread (Rp335rb/378rb)
yang sudah dihitung `harga_baru_matriks.py`.

SEMUA produk lain TETAP pakai hasil spread apa adanya - TIDAK ada perubahan
metode global, cuma 2 baris ini yang di-override manual.

Dijalankan SEKALI ke 'Harga Baru UC Top 100 (matriks).xlsx' supaya jadi sumber
kebenaran tunggal untuk proses selanjutnya (update_harga_per_sku.py tinggal
baca file ini apa adanya, tidak perlu logic override terpisah).
"""
import openpyxl

FILE = "Harga Baru UC Top 100 (matriks).xlsx"
OVERRIDE = {
    "Honda Brio Satya / RS": (332000, 375000),
    "Honda Jazz": (332000, 375000),
}


def main():
    wb = openpyxl.load_workbook(FILE, data_only=True)
    ws = wb["Harga Baru"]
    kena = []
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(r, 2).value
        if nm in OVERRIDE:
            reg, strip = OVERRIDE[nm]
            lama = (ws.cell(r, 7).value, ws.cell(r, 8).value)
            ws.cell(r, 7).value = reg
            ws.cell(r, 8).value = strip
            kena.append((nm, lama, (reg, strip)))
    assert len(kena) == len(OVERRIDE), f"tidak semua model ketemu: {kena}"
    wb.save(FILE)
    print("tersimpan:", FILE)
    for nm, lama, baru in kena:
        print(f"  {nm}: {lama} -> {baru}")


if __name__ == "__main__":
    main()
