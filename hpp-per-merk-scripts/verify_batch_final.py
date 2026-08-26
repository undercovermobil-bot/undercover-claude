#!/usr/bin/env python3
"""Verifikasi UPDATE_HARGA_UC_1-40_final/UPDATE_HARGA_UA_SHOPEE.xlsx (harga
batch 1-40+Feroza + SKU Taft GT->DHT-FRZ, digabung 1 file) - independen dari
script pembuatnya, baca ulang dari disk."""
import glob
import sys
import zipfile
import re

import openpyxl

from update_harga_per_sku import (ALIAS, KAT_KE_JENIS, KECUALI, baca_harga,
                                   is_outdoor_polos, resolve_cols, urai_sku)

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"
SRC_FOLDER = "uc_fixed"
OUT = "UPDATE_HARGA_UC_1-40_final/UPDATE_HARGA_UA_SHOPEE.xlsx"
PREFIX_LAMA, PREFIX_BARU = "DHT-TG", "DHT-FRZ"

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def main():
    target = baca_harga(HARGA_FILE, 1, 40)
    target.update(baca_harga(HARGA_FILE, 49, 49))

    seharusnya = []  # (sku_final_diharapkan, harga_diharapkan)
    for path in sorted(glob.glob(f"{SRC_FOLDER}/*.xlsx")):
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb["Sheet1"]
        col = resolve_cols(ws, "shopee")
        for r in range(7, ws.max_row + 1):
            sku = ws.cell(r, col["sku"]).value
            pfx, kat = urai_sku(sku)
            pfx_r = ALIAS.get(pfx, pfx)
            if pfx_r not in target:
                continue
            nm = str(ws.cell(r, col["nama"]).value or "")
            if any(k in nm.lower() for k in KECUALI) or is_outdoor_polos(nm):
                continue
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue
            baru = target[pfx_r][jenis]
            lama = ws.cell(r, col["harga"]).value
            sku_final = PREFIX_BARU + sku[len(PREFIX_LAMA):] if pfx == PREFIX_LAMA else sku
            harga_sama = False
            try:
                harga_sama = lama is not None and int(float(lama)) == baru
            except (TypeError, ValueError):
                pass
            if harga_sama and pfx != PREFIX_LAMA:
                continue
            seharusnya.append((sku_final, baru))

    wb = openpyxl.load_workbook(OUT, data_only=True)
    ws = wb["Sheet1"]
    col = resolve_cols(ws, "shopee")
    output = [(ws.cell(r, col["sku"]).value, ws.cell(r, col["harga"]).value)
              for r in range(7, ws.max_row + 1)]

    cek("1. jumlah baris output = seharusnya (urutan sama)", len(output) == len(seharusnya),
        f"{len(output)} vs {len(seharusnya)}")
    mismatch = [(i, o, s) for i, (o, s) in enumerate(zip(output, seharusnya))
                if (o[0], int(float(o[1]))) != (s[0], s[1])]
    cek("2. tiap baris (posisi sama) SKU & harga cocok persis", not mismatch, str(mismatch[:5]))

    # 3. tidak ada lagi DHT-TG tersisa di output
    sisa_dht_tg = [o for o in output if o[0] and o[0].startswith(PREFIX_LAMA + "-")]
    cek("3. tidak ada SKU DHT-TG tersisa di output", not sisa_dht_tg, str(sisa_dht_tg[:5]))

    # 4. semua SKU baru DHT-FRZ yang berasal dari Taft GT match pola SKU Feroza yang sudah ada
    taft_baru = [o for o in output if o[0] and "G1-" in o[0] and o[1] in (382000, 425000)
                 and o[0].startswith(PREFIX_BARU + "-")]
    cek("4. minimal 14 baris DHT-FRZ dgn harga Feroza (Taft GT ikut)",
        len(taft_baru) >= 14, f"ketemu {len(taft_baru)}")

    # 5. brio/jazz tidak ada
    brio_jazz = [1 for r in range(7, ws.max_row + 1)
                 if ws.cell(r, col["nama"]).value and
                 ("brio" in ws.cell(r, col["nama"]).value.lower() or
                  "jazz" in ws.cell(r, col["nama"]).value.lower())]
    cek("5. 0 baris Brio/Jazz", not brio_jazz, str(len(brio_jazz)))

    with zipfile.ZipFile(OUT) as z:
        f_aneh = sum(len(re.findall(rb"<f[ />]", z.read(n)))
                     for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n))
    cek("6. tidak ada elemen formula", f_aneh == 0, f"{f_aneh} <f>")

    print(f"\ntotal baris output: {len(output)}")
    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
