#!/usr/bin/env python3
"""
Menyamakan SKU untuk MOBIL KEMBAR (badge engineering) di file master
"SKU, Price, Tracking Cover Mobil".

Latar (instruksi user 2026-08-19/20):
  - "Twin harusnya BERBAGI 1 SKU"
  - "ya, Rush+Terios jadi TYT-RSH kode skunya"          -> prefix Toyota yang menang
  - "TYT-ALP (Alphard)"                                  -> Alphard+Vellfire
  - "opsi satu benar, tapi rocky yg generasi awal =
     feroza = taft gt"                                   -> Rocky lawas TIDAK ikut Raize,
                                                            tapi satu grup dgn Feroza+Taft GT
  - "pakai model seperti di excel ini aja yg sheet 2"     -> jumlah kode generasi mengikuti
                                                            Total Formula (TF) di Sheet2
                                                            Data_Mobil_Lebih_dari_1_Formula_2.xlsx

Bukti pendukung (harga listing Shopee toko Undercover Autocare, varian Reguler termurah):
    Avanza = Xenia = Veloz  298.000
    Agya   = Ayla           287.000
    Calya  = Sigra          293.000
    Rush   = Terios         302.000
    Raize  = Rocky (baru)   292.000
    Alphard= Vellfire       317.000
    Feroza = Taft GT        288.000   <- Feroza Long 295.000, BEDA, sengaja tidak digabung
Harga sama persis = ukuran cover sama = memang 1 SKU.

PENTING - aturan repo (CLAUDE.md): file master ASLI tidak boleh diedit langsung.
Script ini menulis ke COPY.
"""
import re
import sys
from collections import Counter, defaultdict

import openpyxl

MASTER_SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/5337f5dd-SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"
MASTER_OUT = "SKU, Price, Tracking Cover Mobil - SKU KEMBAR DISAMAKAN.xlsx"

KOL_NAMA, KOL_TOKO, KOL_KAT, KOL_WARNA, KOL_GEN, KOL_SKU = 2, 3, 4, 5, 6, 9

# Prefix kanonik grup Feroza/Taft GT/Rocky lawas.
# ASUMSI: user menjawab "opsi satu benar" untuk opsi "Rocky lawas tetap DHT-RCK",
# lalu menambahkan bahwa Feroza & Taft GT itu mobil yang sama -> DHT-RCK jadi kanonik.
# Kalau user lebih suka DHT-FRZ (nama pasar Indonesia, tidak rancu dgn Rocky 2021),
# cukup ganti 1 konstanta ini.
PREFIX_ROCKY_LAWAS = "DHT-RCK"

# (nama produk di master, generasi di master) -> (prefix SKU baru, kode generasi baru)
GRUP = {
    "Avanza + Xenia + Veloz (TF=2)": {
        ("Toyota Avanza", "Gen 1 & 2"): ("TYT-AVZ", "G1"),
        ("Daihatsu Xenia", "Gen 1"): ("TYT-AVZ", "G1"),
        ("Daihatsu Xenia", "Gen 2"): ("TYT-AVZ", "G1"),
        ("Toyota Avanza", "Gen 3"): ("TYT-AVZ", "G3"),
        ("Daihatsu All New Xenia", "Gen 3"): ("TYT-AVZ", "G3"),
        # Sheet2 catatan: "Avanza Gen 3 = Xenia Gen 3 = Veloz Gen 1,2,3"
        # -> SEMUA generasi Veloz masuk formula Gen 3, termasuk Veloz 2011-2021.
        ("Toyota Veloz", "Gen 1"): ("TYT-AVZ", "G3"),
        ("Toyota Veloz", "Gen 2"): ("TYT-AVZ", "G3"),
    },
    "Agya + Ayla (TF=1)": {
        ("Toyota Agya", "Gen 1"): ("TYT-AGY", "G1"),
        ("Toyota Agya", "Gen 2"): ("TYT-AGY", "G1"),
        ("Daihatsu Ayla", "Gen 1"): ("TYT-AGY", "G1"),
        ("Daihatsu Ayla", "Gen 1F1"): ("TYT-AGY", "G1"),
        ("Daihatsu Ayla", "Gen 1F2"): ("TYT-AGY", "G1"),
        ("Daihatsu Ayla", "Gen 2"): ("TYT-AGY", "G1"),
        ("Daihatsu All New Ayla", "Gen 2 (A350)"): ("TYT-AGY", "G1"),
    },
    "Calya + Sigra (TF=1)": {
        ("Toyota Calya", "Gen 1"): ("TYT-CLY", "G1"),
        ("Daihatsu Sigra", "Gen 1"): ("TYT-CLY", "G1"),
    },
    "Rush + Terios (TF=1)": {
        ("Toyota Rush", "Gen 1"): ("TYT-RSH", "G1"),
        ("Toyota Rush", "Gen 2"): ("TYT-RSH", "G1"),
        ("Daihatsu Terios", "Gen 1"): ("TYT-RSH", "G1"),
        ("Daihatsu Terios / New Terios", "Gen 2 & 3"): ("TYT-RSH", "G1"),
    },
    "Raize + Rocky baru (TF=1)": {
        ("Toyota Raize", "Gen 1"): ("TYT-RZE", "G1"),
        ("Daihatsu Rocky", "Gen 2 (A200)"): ("TYT-RZE", "G1"),
    },
    "Alphard + Vellfire (TF=1)": {
        ("Toyota Alphard", "Gen 1 - 3"): ("TYT-ALP", "G1"),
        ("Toyota Alphard", "Gen 4"): ("TYT-ALP", "G1"),
        ("Toyota Vellfire", "Gen 2"): ("TYT-ALP", "G1"),
        ("Toyota Vellfire", "Gen 2F"): ("TYT-ALP", "G1"),
        ("Toyota Vellfire", "Gen 3"): ("TYT-ALP", "G1"),
        ("Toyota Vellfire", "Gen 3F"): ("TYT-ALP", "G1"),
        ("Toyota Vellfire", "Gen 4"): ("TYT-ALP", "G1"),
    },
    "Rocky lawas + Feroza + Taft GT (TF=1)": {
        ("Daihatsu Rocky", "F70/F300"): (PREFIX_ROCKY_LAWAS, "G1"),
        ("Daihatsu Feroza", "Gen 1&2"): (PREFIX_ROCKY_LAWAS, "G1"),
        ("Daihatsu Feroza", "Gen 3"): (PREFIX_ROCKY_LAWAS, "G1"),
        ("Daihatsu Taft GT", "Gen 1"): (PREFIX_ROCKY_LAWAS, "G1"),
    },
}

PETA = {}
GRUP_DARI = {}
for nama_grup, isi in GRUP.items():
    for k, v in isi.items():
        assert k not in PETA, f"kunci dobel antar grup: {k}"
        PETA[k] = v
        GRUP_DARI[k] = nama_grup


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip())


def bongkar(sku):
    """Pecah SKU jadi (prefix, toko, kat, gen, warna) - dihitung dari KANAN supaya
    aman untuk prefix model yang mengandung tanda hubung."""
    p = str(sku).split("-")
    if len(p) < 5:
        return None
    return "-".join(p[:-4]), p[-4], p[-3], p[-2], p[-1]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else MASTER_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else MASTER_OUT

    wb = openpyxl.load_workbook(src)
    ubah = Counter()
    sudah_pas = Counter()
    pindah = defaultdict(Counter)      # grup -> "LAMA -> BARU" -> jumlah
    tak_ketemu = set(PETA)
    rusak = []

    for ws in wb.worksheets:
        for r in range(3, ws.max_row + 1):
            nama = norm(ws.cell(r, KOL_NAMA).value)
            if not nama:
                continue
            gen = norm(ws.cell(r, KOL_GEN).value)
            kunci = (nama, gen)
            if kunci not in PETA:
                continue
            tak_ketemu.discard(kunci)
            sel = ws.cell(r, KOL_SKU)
            b = bongkar(sel.value)
            if b is None:
                rusak.append((ws.title, r, nama, gen, sel.value))
                continue
            prefix_lama, toko, kat, gen_lama, warna = b
            prefix_baru, gen_baru = PETA[kunci]
            baru = f"{prefix_baru}-{toko}-{kat}-{gen_baru}-{warna}"
            grup = GRUP_DARI[kunci]
            if baru == str(sel.value):
                sudah_pas[grup] += 1
                continue
            pindah[grup][f"{prefix_lama}-*-{gen_lama}-*  ->  {prefix_baru}-*-{gen_baru}-*"] += 1
            sel.value = baru
            ubah[grup] += 1

    print(f"sumber : {src}")
    total_u = total_s = 0
    for nama_grup in GRUP:
        u, s = ubah[nama_grup], sudah_pas[nama_grup]
        total_u += u
        total_s += s
        print(f"\n== {nama_grup}")
        print(f"   baris diubah      : {u}")
        print(f"   baris sudah sesuai: {s}")
        for k, n in sorted(pindah[nama_grup].items(), key=lambda x: -x[1]):
            print(f"     {k}  ({n} baris)")
    print(f"\nTOTAL baris diubah      : {total_u}")
    print(f"TOTAL baris sudah sesuai: {total_s}")

    if tak_ketemu:
        print("\nPERINGATAN - kunci (nama, generasi) TIDAK ketemu di master:")
        for k in sorted(tak_ketemu):
            print("  ", k)
    if rusak:
        print("\nPERINGATAN - SKU tidak bisa dibongkar:")
        for x in rusak:
            print("  ", x)

    wb.save(out)
    print("\ntersimpan:", out)


if __name__ == "__main__":
    main()
