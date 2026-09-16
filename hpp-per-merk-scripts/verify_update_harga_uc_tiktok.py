#!/usr/bin/env python3
"""Verifikasi 'UPDATE_HARGA_UA_TIKTOK.xlsx' (batch 1-40) - baca ulang dari disk.
Sama seperti verify_update_harga_uc.py, disesuaikan utk channel TikTok."""
import glob
import re
import sys
import zipfile

import openpyxl

from update_harga_per_sku import (ALIAS, KAT_KE_JENIS, KECUALI, STARTROW,
                                   baca_harga, cari_sheet, deteksi_channel,
                                   is_outdoor_polos, resolve_cols, urai_sku)

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
SRC_FOLDER = "tiktok_uc"
OUT_FILE = "UPDATE_HARGA_UC_TIKTOK_1-40/UPDATE_HARGA_UA_TIKTOK.xlsx"
NO_AWAL, NO_AKHIR = 1, 40

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def kumpulkan_seharusnya(target):
    seharusnya = {}
    for path in sorted(glob.glob(f"{SRC_FOLDER}/*.xlsx")):
        wb = openpyxl.load_workbook(path, data_only=True)
        ch = deteksi_channel(wb)
        if ch is None:
            continue
        ws = cari_sheet(wb, ch)
        col = resolve_cols(ws, ch)
        start = STARTROW[ch]
        for r in range(start, ws.max_row + 1):
            sku = ws.cell(r, col["sku"]).value
            pfx, kat = urai_sku(sku)
            pfx = ALIAS.get(pfx, pfx)
            if pfx not in target:
                continue
            nm = str(ws.cell(r, col["nama"]).value or "")
            if any(k in nm.lower() for k in KECUALI):
                continue
            if is_outdoor_polos(nm):
                continue
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue
            baru = target[pfx][jenis]
            lama = ws.cell(r, col["harga"]).value
            try:
                if lama is not None and int(float(lama)) == baru:
                    continue
            except (TypeError, ValueError):
                pass
            seharusnya[(path, sku, r)] = baru
    return seharusnya


def main():
    target = baca_harga(HARGA_FILE, NO_AWAL, NO_AKHIR)
    seharusnya = kumpulkan_seharusnya(target)
    # kumpulkan per-sku (union lintas file, boleh duplikat SKU antar file)
    seharusnya_sku = {}
    for (path, sku, r), baru in seharusnya.items():
        seharusnya_sku[sku] = baru

    wb = openpyxl.load_workbook(OUT_FILE, data_only=True)
    ch = deteksi_channel(wb)
    cek("0. channel output terdeteksi tiktok", ch == "tiktok", f"terdeteksi {ch}")
    ws = cari_sheet(wb, ch)
    col = resolve_cols(ws, ch)
    start = STARTROW[ch]

    output = {}
    for r in range(start, ws.max_row + 1):
        sku = ws.cell(r, col["sku"]).value
        if not sku:
            continue
        output[sku] = ws.cell(r, col["harga"]).value

    cek("1. jumlah SKU unik output = seharusnya", len(output) == len(seharusnya_sku),
        f"{len(output)} vs {len(seharusnya_sku)}")
    hilang = set(seharusnya_sku) - set(output)
    cek("2. tidak ada SKU seharusnya yang hilang dari output", not hilang, str(list(hilang)[:5]))
    salah_harga = [(sku, output[sku], seharusnya_sku[sku]) for sku in output
                   if sku in seharusnya_sku and int(float(output[sku])) != seharusnya_sku[sku]]
    cek("3. harga di output = target persis", not salah_harga, str(salah_harga[:5]))
    ekstra = set(output) - set(seharusnya_sku)
    cek("4. tidak ada SKU EKSTRA di luar yang seharusnya berubah", not ekstra,
        str(list(ekstra)[:5]))

    salah_kat = []
    for sku in output:
        pfx, kat = urai_sku(sku)
        if kat not in ("R", "S"):
            salah_kat.append(sku)
    cek("5. semua baris output kategori R/S saja", not salah_kat, str(salah_kat[:5]))

    with zipfile.ZipFile(OUT_FILE) as z:
        f_aneh = sum(len(re.findall(rb"<f[ />]", z.read(n)))
                     for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    cek("6. tidak ada elemen formula di output", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print(f"\ntotal baris fisik di output: {ws.max_row - start + 1}")
    print(f"total SKU unik output: {len(output)}")
    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
