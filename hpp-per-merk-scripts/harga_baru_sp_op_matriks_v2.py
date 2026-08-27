#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUPERSEDED 2026-08-27 oleh `harga_baru_sp_op_matriks_v3.py` -- generate file
ini (v2) MEMBUKTIKAN bug drift (200 harga lama, 33 di antaranya ikut
geser +-Rp1.000-3.000 gara-gara 92 model baru masuk grup yang sama, lihat
verifikasi di project-undercover-harga-referensi.md). v3 mengunci
kalibrasi dari 200 model lama supaya tidak drift lagi + tambahan aturan
top-10 pakai harga terendah. Dict KATEGORI_TAMBAHAN2/PANJANG_TAMBAHAN2 di
file ini MASIH dipakai (di-import oleh v3), JANGAN diubah.

Versi 2 dari `harga_baru_sp_op_matriks.py` -- user upload ulang
`HPP_STP_OTP_.xlsx` (2026-08-27) dgn 292 model di sheet 'HPP 12%' (200 lama
+ 92 model BARU ditambahkan, 0 model dihapus). Diverifikasi eksplisit:
200 model lama PERSIS SAMA (nama, Pcs/Roll, harga mentah, urutan baris
2-201) di file baru ini -- jadi KATEGORI/PANJANG_MM (100 pertama) dan
KATEGORI_TAMBAHAN/PANJANG_TAMBAHAN (100 kedua, dari v1) dipertahankan APA
ADANYA, TIDAK diubah. Cuma 92 model baru (KATEGORI_TAMBAHAN2/
PANJANG_TAMBAHAN2 di bawah) yang diklasifikasi baru di sini.

**PENGECUALIAN - Ferrari F8 Tributo (baris 263 sumber) TIDAK DIHITUNG.**
Sumber datanya sendiri kosong (Pcs/Roll, Biaya Per PCS, HPP semua blank di
file HPP_STP_OTP_.xlsx), beda dari 3 Ferrari lain di baris sekitarnya
(812 Superfast/GTC4Lusso/SF90 Stradale, yg semua Pcs/Roll=5 & harga mentah
sama persis 369.955) yg datanya lengkap. Kemungkinan besar barisnya cuma
belum diisi Pcs/Roll saat copy-template, TAPI tidak diasumsikan sepihak --
minta user isi dulu Pcs/Roll-nya di sumber, baru dihitung menyusul.

Klasifikasi 92 model baru pakai pengetahuan otomotif umum (bukan data
eksplisit di file, sama seperti round 1) -- **1 nama ambigu: "Holden" tanpa
nama model spesifik** (mis. Commodore/Kingswood/dll beda ukuran jauh).
Dipakai asumsi mobil sedan besar ala Commodore (~4900mm) sbg placeholder,
TAPI ini PALING PERLU dikoreksi user drpd yg lain di daftar ini.

Pemakaian: python3 harga_baru_sp_op_matriks_v2.py
"""
import math
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

from harga_baru_sp_op_matriks import KATEGORI, PANJANG_MM

SRC = "HPP_STP_OTP_v2_292model.xlsx"
SHEET_SRC = "HPP 12%"
OUT = "Harga Baru SP-OP (matriks) v2.xlsx"

STEP = 1000
MAX_SPREAD = 5000
MM_PER_STEP = 100

DIKECUALIKAN = {"Ferrari F8 Tributo"}  # sumber data kosong, lihat docstring

# ---- 92 model BARU (ronde 2, 2026-08-27) ----
KATEGORI_TAMBAHAN2 = {
    'Volkswagen Beetle': 'Hatchback', 'BMW iX': 'SUV besar',
    'Chery Tiggo Cross': 'SUV compact', 'Chevrolet Trooper': 'SUV besar',
    'DFSK Glory 580': 'SUV besar', 'DFSK Seres E1': 'City Car',
    'Daihatsu Ceria': 'City Car', 'Geely EX2': 'Hatchback',
    'Hyundai Excel': 'Sedan', 'Kia Seltos': 'SUV compact',
    'MG HS': 'SUV besar', 'MG ZS Crossover': 'SUV compact',
    'MINI Clubman': 'Hatchback', 'Mazda 6': 'Sedan',
    'Mazda CX-60': 'SUV besar', 'Mercedes Benz GLA Class': 'SUV compact',
    'Mercedes Benz GLS Class': 'SUV besar', 'Mercedes Benz SLK Class': 'Sport/Supercar',
    'Nissan Kicks e-POWER': 'SUV compact', 'Porsche Panamera': 'Sedan',
    'Suzuki Ciaz': 'Sedan', 'Toyota Yaris Cross': 'SUV compact',
    'Wuling BinguoEV': 'Hatchback',
    'Audi A4': 'Sedan', 'BMW i4': 'Sedan', 'Chery Tiggo 8': 'SUV besar',
    'Citroen C3': 'Hatchback', 'DFSK Glory 560': 'SUV compact',
    'Ford Laser': 'Sedan', 'GAC Aion Hyptec HT': 'SUV besar',
    'Hummer H1': 'SUV besar', 'Hyundai Sonata': 'Sedan',
    'Jeep Cherokee': 'SUV besar', 'Jeep Compass': 'SUV compact',
    'Kia Sedona': 'MPV besar', 'Lexus GS': 'Sedan', 'Lexus LS': 'Sedan',
    'Mazda CX-30': 'SUV compact', 'Mercedes Benz CLA Class': 'Sedan',
    'Mitsubishi Delica': 'MPV besar', 'Peugeot 405': 'Sedan',
    'Peugeot 5008': 'SUV besar', 'Porsche 718 Cayman': 'Sport/Supercar',
    'Renault Koleos': 'SUV besar', 'Subaru Forester': 'SUV besar',
    'Volvo 850 Sedan': 'Sedan', 'Volvo 960': 'Sedan',
    'Audi A3': 'Sedan', 'Audi A6': 'Sedan', 'Audi A8': 'Sedan',
    'Audi Q3': 'SUV compact', 'Audi Q8': 'SUV besar',
    'BMW Seri 8': 'Sport/Supercar', 'BMW X3': 'SUV besar', 'BMW i8': 'Sport/Supercar',
    'Chery Tiggo 7 Pro': 'SUV besar', 'Chevrolet Cruze': 'Sedan',
    'Chevrolet Optra Magnum': 'Hatchback', 'Chevrolet Trailblazer': 'SUV besar',
    'Daihatsu Hi Max': 'Pickup', 'Ferrari 812 Superfast': 'Sport/Supercar',
    'Ferrari GTC4Lusso': 'Sport/Supercar', 'Ferrari SF90 Stradale': 'Sport/Supercar',
    'Fiat 500': 'City Car', 'Holden': 'Sedan',  # <- PALING PERLU dikoreksi, lihat docstring
    'Hyundai Elantra': 'Sedan', 'Isuzu D-MAX': 'Pickup',
    'Lamborghini Huracan': 'Sport/Supercar', 'Lexus ES': 'Sedan',
    'Lexus LX': 'SUV besar', 'Lexus NX': 'SUV besar',
    'MG ZS': 'SUV compact', 'MG ZS EV': 'SUV compact',
    'MINI Convertible': 'Hatchback', 'Maserati Quattroporte': 'Sedan',
    'Mazda BT-50': 'Pickup', 'Mazda CX-8': 'SUV besar',
    'McLaren 570S': 'Sport/Supercar', 'Mercedes Benz B Class': 'MPV keluarga',
    'Nissan Magnite': 'SUV compact', 'Nissan Note': 'Hatchback',
    'Peugeot 406': 'Sedan', 'Porsche 911': 'Sport/Supercar',
    'Porsche Cayenne': 'SUV besar', 'Porsche Taycan': 'Sedan',
    'Rolls-Royce Ghost': 'Sedan', 'Subaru WRX': 'Sedan',
    'Toyota GR Corolla': 'Hatchback', 'Toyota Previa': 'MPV besar',
    'Volvo XC40': 'SUV compact', 'Wuling Mini EV': 'City Car',
}
PANJANG_TAMBAHAN2 = {
    'Volkswagen Beetle': 4129, 'BMW iX': 4953, 'Chery Tiggo Cross': 4330,
    'Chevrolet Trooper': 4720, 'DFSK Glory 580': 4519, 'DFSK Seres E1': 2990,
    'Daihatsu Ceria': 3295, 'Geely EX2': 4080, 'Hyundai Excel': 4285,
    'Kia Seltos': 4370, 'MG HS': 4574, 'MG ZS Crossover': 4323,
    'MINI Clubman': 4253, 'Mazda 6': 4870, 'Mazda CX-60': 4740,
    'Mercedes Benz GLA Class': 4410, 'Mercedes Benz GLS Class': 5207,
    'Mercedes Benz SLK Class': 4134, 'Nissan Kicks e-POWER': 4295,
    'Porsche Panamera': 5049, 'Suzuki Ciaz': 4490, 'Toyota Yaris Cross': 4200,
    'Wuling BinguoEV': 4008,
    'Audi A4': 4762, 'BMW i4': 4783, 'Chery Tiggo 8': 4722, 'Citroen C3': 4008,
    'DFSK Glory 560': 4295, 'Ford Laser': 4330, 'GAC Aion Hyptec HT': 4750,
    'Hummer H1': 4686, 'Hyundai Sonata': 4900, 'Jeep Cherokee': 4624,
    'Jeep Compass': 4405, 'Kia Sedona': 5115, 'Lexus GS': 4915, 'Lexus LS': 5235,
    'Mazda CX-30': 4395, 'Mercedes Benz CLA Class': 4688, 'Mitsubishi Delica': 4740,
    'Peugeot 405': 4399, 'Peugeot 5008': 4641, 'Porsche 718 Cayman': 4379,
    'Renault Koleos': 4673, 'Subaru Forester': 4640, 'Volvo 850 Sedan': 4696,
    'Volvo 960': 4867,
    'Audi A3': 4506, 'Audi A6': 4939, 'Audi A8': 5172, 'Audi Q3': 4484,
    'Audi Q8': 4986, 'BMW Seri 8': 4843, 'BMW X3': 4708, 'BMW i8': 4689,
    'Chery Tiggo 7 Pro': 4700, 'Chevrolet Cruze': 4597,
    'Chevrolet Optra Magnum': 4515, 'Chevrolet Trailblazer': 4886,
    'Daihatsu Hi Max': 4180, 'Ferrari 812 Superfast': 4657,
    'Ferrari GTC4Lusso': 4922, 'Ferrari SF90 Stradale': 4710, 'Fiat 500': 3546,
    'Holden': 4900, 'Hyundai Elantra': 4650, 'Isuzu D-MAX': 5265,
    'Lamborghini Huracan': 4520, 'Lexus ES': 4975, 'Lexus LX': 5065,
    'Lexus NX': 4660, 'MG ZS': 4323, 'MG ZS EV': 4323, 'MINI Convertible': 3821,
    'Maserati Quattroporte': 5262, 'Mazda BT-50': 5280, 'Mazda CX-8': 4900,
    'McLaren 570S': 4530, 'Mercedes Benz B Class': 4419, 'Nissan Magnite': 3994,
    'Nissan Note': 4245, 'Peugeot 406': 4670, 'Porsche 911': 4519,
    'Porsche Cayenne': 4931, 'Porsche Taycan': 4963, 'Rolls-Royce Ghost': 5546,
    'Subaru WRX': 4670, 'Toyota GR Corolla': 4410, 'Toyota Previa': 4800,
    'Volvo XC40': 4425, 'Wuling Mini EV': 2917,
}
KATEGORI.update(KATEGORI_TAMBAHAN2)
PANJANG_MM.update(PANJANG_TAMBAHAN2)

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)
ARIAL_MIRING = Font(name="Arial", size=10, italic=True)
HDR = PatternFill('solid', fgColor='FFC000')
HIJAU = PatternFill('solid', fgColor='C6EFCE')
RP = '_-[$Rp-421]* #,##0_-;-[$Rp-421]* #,##0_-;_-[$Rp-421]* "-"??_-;_-@_-'


def ceil1000(x):
    return int(math.ceil(x / 1000.0) * 1000)


def hitung_langkah(panjang_sorted):
    unik = sorted(set(panjang_sorted))
    lo, hi = unik[0], unik[-1]
    rentang = hi - lo
    if rentang == 0:
        return {lo: 0}
    spread = min(int(math.floor(rentang / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
    if spread == 0:
        return {p: 0 for p in unik}
    n_langkah = spread // STEP
    return {p: int(math.floor((p - lo) / rentang * n_langkah + 0.5)) * STEP for p in unik}


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb[SHEET_SRC]

    produk = []
    dilewati = []
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=1).value
        if not nm:
            continue
        nm = str(nm).strip()
        if nm in DIKECUALIKAN:
            dilewati.append(nm)
            continue
        pr = ws.cell(row=r, column=3).value
        hjt = ws.cell(row=r, column=29).value
        if nm not in KATEGORI:
            raise SystemExit(f"BELUM ada kategori utk: {nm}")
        if nm not in PANJANG_MM:
            raise SystemExit(f"BELUM ada data panjang utk: {nm}")
        if pr is None or hjt is None:
            raise SystemExit(f"Data Pcs/Roll atau harga kosong utk: {nm} (baris {r})")
        pr = int(round(float(pr)))
        produk.append({"nama": nm, "pcsroll": pr, "hjt": hjt,
                        "kat": KATEGORI[nm], "panjang": PANJANG_MM[nm],
                        "baru_di_sp_op": nm in KATEGORI_TAMBAHAN2})

    lantai = {}
    for p in produk:
        lantai.setdefault(p["pcsroll"], ceil1000(p["hjt"]))

    grup = defaultdict(list)
    for p in produk:
        grup[(p["pcsroll"], p["kat"])].append(p)

    for (pr, kat), anggota in grup.items():
        peta = hitung_langkah(sorted(a["panjang"] for a in anggota))
        for a in anggota:
            a["harga_baru"] = lantai[pr] + peta[a["panjang"]]

    wb2 = openpyxl.Workbook()
    ws1 = wb2.active
    ws1.title = "Harga Baru SP-OP"
    kolom = ["No", "Nama Produk", "Pcs/Roll", "Tipe Mobil", "Panjang (mm)",
             "Harga Jual Terbaru (mentah)", "Harga Baru (Reguler)", "Klasifikasi Baru?"]
    for i, h in enumerate(kolom, 1):
        c = ws1.cell(1, i, h)
        c.fill = HDR
        c.font = ARIAL_TEBAL
        c.alignment = Alignment(wrap_text=True, vertical="center")

    for i, p in enumerate(produk, 1):
        r = i + 1
        ws1.cell(r, 1, i)
        ws1.cell(r, 2, p["nama"])
        ws1.cell(r, 3, p["pcsroll"])
        ws1.cell(r, 4, p["kat"])
        ws1.cell(r, 5, p["panjang"])
        c6 = ws1.cell(r, 6, round(p["hjt"]))
        c6.number_format = RP
        c7 = ws1.cell(r, 7, p["harga_baru"])
        c7.number_format = RP
        c7.fill = HIJAU
        ws1.cell(r, 8, "Ya - RONDE 2 (2026-08-27)" if p["baru_di_sp_op"] else "")
        for c in range(1, 9):
            ws1.cell(r, c).font = ARIAL

    for col, w in zip("ABCDEFGH", [5, 40, 9, 15, 12, 20, 16, 20]):
        ws1.column_dimensions[col].width = w
    ws1.freeze_panes = "A2"
    ws1.auto_filter.ref = f"A1:H{len(produk)+1}"

    ws2 = wb2.create_sheet("Matriks")
    for i, h in enumerate(["Pcs/Roll", "Tipe Mobil", "Nama Produk", "Panjang (mm)",
                            "Harga Baru (Reguler)"], 1):
        c = ws2.cell(1, i, h)
        c.fill = HDR
        c.font = ARIAL_TEBAL
    r = 2
    for pr in sorted({p["pcsroll"] for p in produk}, reverse=True):
        for kat in sorted({p["kat"] for p in produk if p["pcsroll"] == pr}):
            anggota = sorted([p for p in produk if p["pcsroll"] == pr and p["kat"] == kat],
                              key=lambda x: (x["panjang"], x["nama"]))
            for p in anggota:
                ws2.cell(r, 1, pr).font = ARIAL
                ws2.cell(r, 2, kat).font = ARIAL
                ws2.cell(r, 3, p["nama"]).font = ARIAL
                ws2.cell(r, 4, p["panjang"]).font = ARIAL
                c5 = ws2.cell(r, 5, p["harga_baru"])
                c5.number_format = RP
                c5.fill = HIJAU
                c5.font = ARIAL
                r += 1
            r += 1
    for col, w in zip("ABCDE", [10, 15, 40, 12, 16]):
        ws2.column_dimensions[col].width = w
    ws2.freeze_panes = "A2"

    ws3 = wb2.create_sheet("CATATAN")
    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 70
    baris = [1]

    def tulis(a, b="", tebal=False, miring=False):
        r_ = baris[0]
        for kol, val in (("A", a), ("B", b)):
            if val in ("", None):
                continue
            sel = ws3[f"{kol}{r_}"]
            sel.value = val
            sel.font = ARIAL_TEBAL if tebal else (ARIAL_MIRING if miring else ARIAL)
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris[0] += 1

    tulis("CATATAN v2 (2026-08-27)", "", tebal=True)
    tulis("Perubahan dari v1", f"User upload ulang '{SRC}' dgn {len(produk)+len(dilewati)} "
          "model di sheet HPP 12% (200 lama + 92 baru). 200 model lama diverifikasi PERSIS "
          "SAMA (nama, Pcs/Roll, harga mentah, urutan) - kategori/panjangnya TIDAK diubah.")
    tulis("92 model baru", "Diklasifikasi baru pakai pengetahuan otomotif umum, konvensi "
          "kategori sama persis dgn round 1 (lihat kolom 'Klasifikasi Baru?' = "
          "'Ya - RONDE 2' di sheet 'Harga Baru SP-OP').")
    if dilewati:
        tulis("DIKECUALIKAN dari perhitungan ini", ", ".join(dilewati) +
              " - data Pcs/Roll & HPP kosong di sumber (beda dari Ferrari lain di "
              "baris sekitarnya yg datanya lengkap, Pcs/Roll=5). Minta user lengkapi "
              "dulu di sheet HPP 12%, baru dihitung menyusul.")
    tulis("PALING PERLU DIKOREKSI", "'Holden' - nama generik tanpa model spesifik "
          "(Commodore/Kingswood/dll beda ukuran jauh). Dipakai asumsi sedan besar "
          "ala Commodore (~4900mm) sbg placeholder - tolong konfirmasi/koreksi model "
          "persisnya.")
    tulis("")
    tulis("92 MODEL RONDE 2 (perlu direview)", "", tebal=True)
    tulis("Nama Produk", "Kategori (baru)", tebal=True)
    for nm in sorted(KATEGORI_TAMBAHAN2):
        tulis(nm, f"{KATEGORI_TAMBAHAN2[nm]}, {PANJANG_TAMBAHAN2[nm]}mm")

    wb2.save(OUT)

    print(f"tersimpan: {OUT}")
    print(f"total model dihitung: {len(produk)} (dilewati: {dilewati})")
    for pr in sorted({p["pcsroll"] for p in produk}, reverse=True):
        print(f"\n===== {pr} pcs/roll -> lantai Rp{lantai[pr]:,} =====".replace(",", "."))
        for kat in sorted({p["kat"] for p in produk if p["pcsroll"] == pr}):
            anggota = sorted([p for p in produk if p["pcsroll"] == pr and p["kat"] == kat],
                              key=lambda x: x["panjang"])
            hs = [a["harga_baru"] for a in anggota]
            print(f"  [{kat}] Rp{min(hs):,} - Rp{max(hs):,}  ({len(anggota)} model)".replace(",", "."))


if __name__ == "__main__":
    main()
