#!/usr/bin/env python3
"""Verifikasi UPDATE_HARGA_UA_{SHOPEE,TIKTOK}.xlsx (batch 1-40 + Feroza #49) -
baca ulang dari disk, tidak percaya laporan konsol."""
import glob
import re
import sys
import zipfile

import openpyxl

from update_harga_per_sku import (ALIAS, KAT_KE_JENIS, KECUALI, STARTROW,
                                   baca_harga, cari_sheet, deteksi_channel,
                                   is_outdoor_polos, resolve_cols, urai_sku)

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"


def bangun_target():
    t = baca_harga(HARGA_FILE, 1, 40)
    t.update(baca_harga(HARGA_FILE, 49, 49))
    return t


def kumpulkan_seharusnya(target, src_folder):
    seharusnya = {}
    for path in sorted(glob.glob(f"{src_folder}/*.xlsx")):
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
            seharusnya[sku] = baru
    return seharusnya


def cek_satu(label, src_folder, out_file):
    print(f"\n===== {label} =====")
    galat = []

    def cek(nama, kondisi, pesan=""):
        print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
        if not kondisi:
            galat.append(nama)

    target = bangun_target()
    seharusnya = kumpulkan_seharusnya(target, src_folder)

    wb = openpyxl.load_workbook(out_file, data_only=True)
    ch = deteksi_channel(wb)
    ws = cari_sheet(wb, ch)
    col = resolve_cols(ws, ch)
    start = STARTROW[ch]
    output = {}
    for r in range(start, ws.max_row + 1):
        sku = ws.cell(r, col["sku"]).value
        if sku:
            output[sku] = ws.cell(r, col["harga"]).value

    cek("1. jumlah SKU unik output = seharusnya", len(output) == len(seharusnya),
        f"{len(output)} vs {len(seharusnya)}")
    cek("2. tidak ada SKU seharusnya yang hilang", not (set(seharusnya) - set(output)),
        str(list(set(seharusnya) - set(output))[:5]))
    salah = [(s, output[s], seharusnya[s]) for s in output
             if s in seharusnya and int(float(output[s])) != seharusnya[s]]
    cek("3. harga output = target persis", not salah, str(salah[:5]))
    cek("4. tidak ada SKU ekstra", not (set(output) - set(seharusnya)),
        str(list(set(output) - set(seharusnya))[:5]))
    cek("5. Daihatsu Taft GT (via alias DHT-TG->DHT-FRZ) ikut kalau ada di file sumber",
        True, "cek manual di bawah")

    with zipfile.ZipFile(out_file) as z:
        f_aneh = sum(len(re.findall(rb"<f[ />]", z.read(n)))
                     for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    cek("6. tidak ada elemen formula", f_aneh == 0, f"{f_aneh} <f>")

    print(f"total baris fisik: {ws.max_row - start + 1}, SKU unik: {len(output)}")
    return galat


def main():
    g1 = cek_satu("SHOPEE", "uc_fixed", "UPDATE_HARGA_UC_1-40_v2/UPDATE_HARGA_UA_SHOPEE.xlsx")
    g2 = cek_satu("TIKTOK", "tiktok_uc", "UPDATE_HARGA_UC_TIKTOK_1-40_v2/UPDATE_HARGA_UA_TIKTOK.xlsx")
    galat = g1 + g2
    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
