#!/usr/bin/env python3
"""Daftar perubahan SKU yang harus dilakukan di LISTING Shopee (toko Undercover
Autocare) supaya sinkron dengan master hasil samakan_sku_kembar.py.

Peta di bawah diturunkan dari peta master, plus pembacaan kode generasi yang
DIPAKAI listing (listing memakai lebih banyak kode generasi daripada master,
mis. Xenia G2, Alphard G4, Rocky F7 - semuanya melebur mengikuti Total Formula).
"""
import pickle
from collections import Counter

import openpyxl
from openpyxl.styles import Alignment, Font

OUT = "PERUBAHAN SKU KEMBAR - listing Shopee UA.xlsx"
ARIAL = Font(name="Arial", size=10)
TEBAL = Font(name="Arial", size=10, bold=True)

# (prefix lama, kode generasi di listing) -> (prefix baru, kode generasi baru, alasan)
PETA = {}


def isi(pre, gens, pre_baru, gen_baru, alasan):
    for g in gens:
        PETA[(pre, g)] = (pre_baru, gen_baru, alasan)


isi("TYT-AVZ", ["G1"], "TYT-AVZ", "G1", "tetap - formula Avanza/Xenia Gen 1-2")
isi("TYT-AVZ", ["G3"], "TYT-AVZ", "G3", "tetap - formula Avanza Gen 3/Veloz")
isi("DHT-XNA", ["G1", "G2"], "TYT-AVZ", "G1", "Xenia Gen 1-2 = Avanza Gen 1-2")
isi("DHT-XNA", ["G3"], "TYT-AVZ", "G3", "Xenia Gen 3 = Avanza Gen 3")
isi("TYT-VLZ", ["G1", "G2"], "TYT-AVZ", "G3", "Sheet2: Veloz Gen 1,2,3 = Avanza Gen 3")
# 2026-08-20: arah Agya/Ayla & Rocky-lawas dikoreksi setelah branch
# claude/repo-memory-access-4hthja digabung - lihat catatan di samakan_sku_kembar.py.
isi("TYT-AGY", ["G1", "G2"], "DHT-AYL", "G1", "Agya = Ayla (DHT-AYL menang, dikonfirmasi user 08-11)")
isi("DHT-AYL", ["G1", "G2"], "DHT-AYL", "G1", "tetap")
isi("TYT-CLY", ["G1"], "TYT-CLY", "G1", "tetap")
isi("DHT-SGR", ["G1"], "TYT-CLY", "G1", "Sigra = Calya")
isi("TYT-RSH", ["G1", "G2"], "TYT-RSH", "G1", "TF=1, semua generasi 1 kode")
isi("DHT-TRS", ["G1", "G2"], "TYT-RSH", "G1", "Terios = Rush")
isi("TYT-RZE", ["G1"], "TYT-RZE", "G1", "tetap")
isi("DHT-RCK", ["G2"], "TYT-RZE", "G1", "Rocky BARU (A200) = Raize")
isi("DHT-RCK", ["F7"], "DHT-FRZ", "G1", "Rocky LAWAS (F70/F300) = Feroza (dikonfirmasi user 08-11)")
isi("TYT-ALP", ["G1", "G4"], "TYT-ALP", "G1", "TF=1, semua generasi 1 kode")
isi("TYT-VLF", ["G1"], "TYT-ALP", "G1", "Vellfire = Alphard")
isi("DHT-FRZ", ["G1", "G3"], "DHT-FRZ", "G1", "tetap - Rocky lawas & Taft GT ikut kode ini")
isi("DHT-TG", ["G1", "Hijau"], "DHT-FRZ", "G1", "Taft GT = Feroza = Rocky lawas")

PREFIX = "Undercover Autocare - Cover Mobil "


def main():
    rows = pickle.load(open("rows.pkl", "rb"))
    hasil, tak_terpeta = [], Counter()
    for pid, nama, var, sku, harga in rows:
        if not sku or sku.count("-") < 4:
            continue
        p = sku.split("-")
        pre, gen = "-".join(p[:-4]), p[-2]
        if pre not in {k[0] for k in PETA}:
            continue
        if (pre, gen) not in PETA:
            tak_terpeta[(pre, gen)] += 1
            continue
        pre_b, gen_b, alasan = PETA[(pre, gen)]
        baru = f"{pre_b}-{p[-4]}-{p[-3]}-{gen_b}-{p[-1]}"
        if baru == sku:
            continue
        hasil.append((nama.replace(PREFIX, ""), str(var), sku, baru, alasan))

    hasil = sorted(set(hasil))
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Perubahan SKU Listing"
    judul = ["Listing (Undercover Autocare)", "Varian", "SKU Lama", "SKU Baru", "Alasan"]
    for c, t in enumerate(judul, 1):
        sel = ws.cell(1, c, t)
        sel.font = TEBAL
    for r, baris in enumerate(hasil, 2):
        for c, v in enumerate(baris, 1):
            sel = ws.cell(r, c, v)
            sel.font = ARIAL
            sel.alignment = Alignment(vertical="top")
    for kol, lebar in zip("ABCDE", (38, 34, 24, 24, 46)):
        ws.column_dimensions[kol].width = lebar
    ws.freeze_panes = "A2"

    ringkas = Counter((a[2].rsplit("-", 4)[0], a[3].rsplit("-", 4)[0]) for a in hasil)
    ws2 = wb.create_sheet("Ringkasan")
    for c, t in enumerate(["Prefix Lama", "Prefix Baru", "Jumlah Varian"], 1):
        ws2.cell(1, c, t).font = TEBAL
    for r, ((lama, baru), n) in enumerate(sorted(ringkas.items(), key=lambda x: -x[1]), 2):
        for c, v in enumerate((lama, baru, n), 1):
            ws2.cell(r, c, v).font = ARIAL
    for kol, lebar in zip("ABC", (18, 18, 16)):
        ws2.column_dimensions[kol].width = lebar

    wb.save(OUT)
    print("tersimpan:", OUT)
    print("varian listing yang perlu diubah:", len(hasil))
    for (lama, baru), n in sorted(ringkas.items(), key=lambda x: -x[1]):
        print(f"  {lama:8} -> {baru:8}  {n:3} varian")
    if tak_terpeta:
        print("BELUM terpeta:", dict(tak_terpeta))


if __name__ == "__main__":
    main()
