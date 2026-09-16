#!/usr/bin/env python3
"""Verifikasi 'UPDATE_HARGA_UA_SHOPEE.xlsx' (batch 1-40) - baca ulang dari disk.
Cek kelengkapan (semua baris stale dalam scope ikut) & ketepatan (harga = target),
tanpa mempercayai laporan konsol script itu sendiri."""
import sys
import zipfile
import re
from collections import defaultdict

import openpyxl

from update_harga_per_sku import (ALIAS, KAT_KE_JENIS, KECUALI, baca_harga,
                                   is_outdoor_polos, resolve_cols, urai_sku)

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
SRC_FOLDER = "uc_fixed"
OUT_FILE = "UPDATE_HARGA_UC_1-40/UPDATE_HARGA_UA_SHOPEE.xlsx"
NO_AWAL, NO_AKHIR = 1, 40

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def kumpulkan_seharusnya(target):
    """scan ulang SEMUA 5 file sumber, tentukan baris mana yang SEHARUSNYA berubah."""
    import glob
    seharusnya = {}  # sku -> (harga_baru, nama, var)
    for path in sorted(glob.glob(f"{SRC_FOLDER}/*.xlsx")):
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb["Sheet1"]
        col = resolve_cols(ws, "shopee")
        for r in range(7, ws.max_row + 1):
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
            seharusnya[sku] = (baru, nm, ws.cell(r, col["var"]).value)
    return seharusnya


def main():
    target = baca_harga(HARGA_FILE, NO_AWAL, NO_AKHIR)
    seharusnya = kumpulkan_seharusnya(target)

    wb = openpyxl.load_workbook(OUT_FILE, data_only=True)
    ws = wb["Sheet1"]
    col = resolve_cols(ws, "shopee")

    output = {}
    for r in range(7, ws.max_row + 1):
        sku = ws.cell(r, col["sku"]).value
        if not sku:
            continue
        output[sku] = ws.cell(r, col["harga"]).value

    cek("1. jumlah baris output = jumlah baris seharusnya", len(output) == len(seharusnya),
        f"{len(output)} vs {len(seharusnya)}")

    hilang = set(seharusnya) - set(output)
    cek("2. tidak ada baris seharusnya yang hilang dari output", not hilang,
        str(list(hilang)[:5]))

    salah_harga = [(sku, output[sku], seharusnya[sku][0]) for sku in output
                   if sku in seharusnya and int(float(output[sku])) != seharusnya[sku][0]]
    cek("3. harga di output = target persis", not salah_harga, str(salah_harga[:5]))

    ekstra = set(output) - set(seharusnya)
    cek("4. tidak ada baris EKSTRA (di luar yang seharusnya berubah)", not ekstra,
        str(list(ekstra)[:5]))

    # 5. semua baris output kat R/S saja, tidak ada P/E/T yang kebawa
    salah_kat = []
    for sku in output:
        pfx, kat = urai_sku(sku)
        if kat not in ("R", "S"):
            salah_kat.append(sku)
    cek("5. semua baris output kategori R/S saja", not salah_kat, str(salah_kat[:5]))

    # 6. XML sehat
    with zipfile.ZipFile(OUT_FILE) as z:
        f_aneh = sum(len(re.findall(rb"<f[ />]", z.read(n)))
                     for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    cek("6. tidak ada elemen formula di output", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print(f"\ntotal target prefix: {len(target)}")
    print(f"total baris seharusnya berubah: {len(seharusnya)}")
    print(f"total baris di output: {len(output)}")

    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
