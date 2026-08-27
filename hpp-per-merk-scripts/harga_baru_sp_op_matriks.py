#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUPERSEDED 2026-08-27 oleh `harga_baru_sp_op_matriks_v3.py` -- v1 ini (200
model) py bug desain: kalau ada model baru ditambahkan ke grup (Pcs/Roll x
Kategori) yang sama, rentang panjang-bodi dihitung ULANG dari SELURUH
anggota grup saat itu, jadi harga model LAMA ikut geser tiap kali ada
tambahan (ketemu saat nambah 92 model di v2). v3 mengunci kalibrasi dari
200 model ini SEKALI, tidak dihitung ulang lagi ke depannya. Dict
KATEGORI/PANJANG_MM di file ini MASIH dipakai (di-import oleh v2/v3),
JANGAN diubah -- cuma fungsi/proses hitungnya yang sudah digantikan.

Harga jual baru untuk toko Smartprotection (SP) & Otoprotection (OP), 200 model,
Reguler -- memakai metode matriks (Pcs/Roll x kategori bodi x panjang fisik)
yang SUDAH DIVALIDASI user untuk Undercover Autocare (branch
claude/repo-memory-access-4hthja, scripts/harga_baru_matriks.py + memory
project-undercover-harga-referensi.md), BUKAN metode rank-harga-UC yang
sempat dipakai sebelumnya di harga_baru_sp_op.py (KELIRU - dibuat sebelum
menemukan riwayat kerja yang sudah ada di branch lain).

100 dari 200 model sudah py kategori & panjang bodi (mm) dari dict yang sudah
divalidasi di branch tsb (dipertahankan APA ADANYA, tidak diubah). 100 model
sisanya (KATEGORI_TAMBAHAN, PANJANG_TAMBAHAN) diklasifikasi baru mengikuti
konvensi kategori yang sama persis (City Car, Hatchback, Sedan, SUV compact,
SUV besar, MPV keluarga, MPV besar, Pickup, + Sport/Supercar utk mobil sport
yang belum py preseden di 100 pertama) - berdasar pengetahuan otomotif umum,
BUKAN dari kolom data eksplisit (file listing tidak py kolom "tipe bodi"/
"panjang"), konsisten dgn metodologi asli yang dicatat di
project-undercover-harga-referensi.md.

Aturan harga (identik versi UC):
1. Pcs/Roll -> lantai harga, MANDIRI per tier (tidak menumpuk antar tier).
2. Dalam (Pcs/Roll x kategori), mobil diurutkan dari panjang bodi terkecil.
3. Kenaikan kelipatan Rp1.000, rentang total per grup maksimal Rp5.000.
4. Lebar spread grup dari skala absolut (tiap 100mm selisih = Rp1.000, capped
   Rp5.000), posisi tiap mobil proporsional thd panjangnya di dalam spread itu.

CATATAN: user TIDAK minta kolom Strip (Elite/Epic/Warrior) kali ini - scope
cuma "Harga Jual Terbaru" (Reguler) dari sheet HPP 12%, jadi kolom Strip
TIDAK disertakan (beda dgn versi UC top100 yang py TAMBAHAN_STRIP).
"""
import math
import sys
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/21438ea2-HPP_STP_OTP_.xlsx"
SHEET_SRC = "HPP 12%"
OUT = "Harga Baru SP-OP (matriks).xlsx"

STEP = 1000
MAX_SPREAD = 5000
MM_PER_STEP = 100

# ---- 100 model pertama: dict PERSIS dari branch claude/repo-memory-access-4hthja,
# scripts/harga_baru_matriks.py (sudah divalidasi user, TIDAK diubah). ----
KATEGORI = {
    'Toyota Avanza': 'MPV keluarga', 'Honda Brio Satya / RS': 'City Car',
    'Toyota Innova': 'MPV besar', 'Honda Jazz': 'Hatchback',
    'Suzuki Ertiga': 'MPV keluarga', 'Honda HR-V / e:N1': 'SUV besar',
    'Toyota Agya': 'City Car', 'Daihatsu Ayla': 'City Car',
    'Daihatsu Xenia': 'MPV keluarga', 'Nissan Livina / Grand Livina': 'MPV keluarga',
    'Toyota Vios': 'Sedan', 'Toyota Fortuner': 'SUV besar',
    'Honda BR-V': 'SUV besar', 'Toyota Calya': 'MPV keluarga',
    'Toyota Rush': 'SUV besar', 'Toyota Yaris': 'Hatchback',
    'Toyota Kijang': 'MPV besar', 'Honda CR-V': 'SUV besar',
    'Honda Mobilio': 'MPV keluarga', 'Honda Civic': 'Sedan',
    'Daihatsu Terios': 'SUV besar', 'Mitsubishi Xpander': 'MPV keluarga',
    'Toyota Camry': 'Sedan', 'Honda Accord': 'Sedan',
    'Toyota Corolla': 'Sedan', 'Suzuki APV Arena / Blind Van': 'MPV keluarga',
    'Toyota Raize': 'SUV compact', 'Isuzu Panther': 'MPV besar',
    'Mitsubishi Pajero Sport': 'SUV besar', 'Daihatsu Sigra': 'MPV keluarga',
    'Suzuki Baleno': 'Hatchback', 'Suzuki Fronx': 'SUV compact',
    'Honda Freed': 'MPV keluarga', 'Toyota Hilux': 'Pickup',
    'Suzuki Swift': 'Hatchback', 'Suzuki Karimun': 'City Car',
    'Mitsubishi Triton': 'Pickup', 'Honda City Sedan': 'Sedan',
    'Suzuki XL7': 'MPV keluarga', 'Nissan March': 'City Car',
    'Toyota HiAce': 'MPV besar', 'Mazda 2 Sedan': 'Sedan',
    'Toyota Hardtop': 'SUV besar', 'Suzuki Jimny': 'SUV compact',
    'Suzuki Ignis': 'City Car', 'BMW Seri 3': 'Sedan',
    'Kia Picanto': 'City Car', 'Daihatsu Sirion': 'Hatchback',
    'Daihatsu Feroza': 'SUV compact', 'Toyota Veloz': 'MPV keluarga',
    'Toyota Alphard': 'MPV besar', 'Toyota Starlet': 'Hatchback',
    'Daihatsu Luxio': 'MPV keluarga', 'Toyota Etios Valco': 'Hatchback',
    'Honda WR-V': 'SUV compact', 'Suzuki Splash': 'City Car',
    'Daihatsu Gran Max Pick Up': 'Pickup', 'Daihatsu Rocky': 'SUV compact',
    'Nissan Juke': 'SUV compact', 'Toyota Vellfire': 'MPV besar',
    'Ford Fiesta': 'Hatchback', 'MINI Cooper': 'Hatchback',
    'Toyota Land Cruiser': 'SUV besar', 'Honda Odyssey': 'MPV besar',
    'Toyota Voxy': 'MPV besar', 'Mercedes Benz E Class': 'Sedan',
    'Suzuki Carry': 'Pickup', 'Nissan Evalia': 'MPV keluarga',
    'Mitsubishi Mitsubishi Kuda': 'MPV besar', 'Nissan X-Trail': 'SUV besar',
    'Suzuki SX4': 'SUV compact', 'Daihatsu Taruna': 'SUV compact',
    'Mitsubishi Mitsubishi Xpander Cross': 'MPV keluarga', 'Toyota Sienta': 'MPV keluarga',
    'Mitsubishi Mitsubishi Destinator': 'SUV compact', 'Honda City Hatchback RS': 'Hatchback',
    'Datsun Go Plus': 'MPV keluarga', 'BYD Atto 1': 'City Car',
    'Nissan Terrano': 'SUV besar', 'Hyundai Creta': 'SUV compact',
    'Mitsubishi Mirage': 'City Car', 'Mercedes Benz S Class': 'Sedan',
    'Hyundai Stargazer': 'MPV keluarga', 'Chevrolet Spin': 'MPV keluarga',
    'Mazda CX5': 'SUV besar', 'Wuling Air EV': 'City Car',
    'BMW Seri 5': 'Sedan', 'Toyota Harrier': 'SUV besar',
    'Wuling Almaz': 'SUV besar', 'Mercedes Benz C Class': 'Sedan',
    'Kia Rio Sedan': 'Sedan', 'Suzuki S-Presso': 'City Car',
    'Datsun Go': 'City Car', 'Toyota Soluna': 'Sedan',
    'Mitsubishi Mitsubishi Outlander': 'SUV besar', 'Suzuki Aerio Hatchback': 'Hatchback',
    'Hyundai Palisade': 'SUV besar', 'Timor': 'Sedan',
    'Mazda 2 Hatchback': 'Hatchback', 'Wuling Confero': 'MPV keluarga',
}
PANJANG_MM = {
    'Wuling Air EV': 2974, 'Suzuki S-Presso': 3565, 'Kia Picanto': 3595,
    'Suzuki Karimun': 3600, 'Suzuki Splash': 3715, 'BYD Atto 1': 3780,
    'Datsun Go': 3785, 'Honda Brio Satya / RS': 3815, 'Nissan March': 3825,
    'Mitsubishi Mirage': 3845, 'Suzuki Ignis': 3700, 'Toyota Agya': 3760,
    'Daihatsu Ayla': 3760,
    'Daihatsu Sirion': 3710, 'Toyota Starlet': 3730, 'Toyota Etios Valco': 3775,
    'Suzuki Swift': 3840, 'MINI Cooper': 3850, 'Toyota Yaris': 3945,
    'Ford Fiesta': 3950, 'Mazda 2 Hatchback': 4065, 'Suzuki Aerio Hatchback': 4145,
    'Honda City Hatchback RS': 4349, 'Suzuki Baleno': 3995, 'Honda Jazz': 4045,
    'Toyota Soluna': 4180, 'Timor': 4365, 'Honda City Sedan': 4553,
    'Mazda 2 Sedan': 4340, 'Kia Rio Sedan': 4370, 'Toyota Vios': 4425,
    'Toyota Corolla': 4630, 'Honda Civic': 4648, 'Mercedes Benz C Class': 4751,
    'BMW Seri 3': 4709, 'Toyota Camry': 4885, 'Honda Accord': 4901,
    'BMW Seri 5': 4963, 'Mercedes Benz E Class': 4935, 'Mercedes Benz S Class': 5179,
    'Datsun Go Plus': 3995, 'Daihatsu Sigra': 4070, 'Toyota Sienta': 4235,
    'Toyota Calya': 4070, 'Daihatsu Luxio': 4165, 'Honda Freed': 4215,
    'Suzuki APV Arena / Blind Van': 4230, 'Chevrolet Spin': 4360,
    'Honda Mobilio': 4386, 'Suzuki Ertiga': 4395, 'Daihatsu Xenia': 4395,
    'Toyota Avanza': 4395, 'Nissan Evalia': 4400,
    'Nissan Livina / Grand Livina': 4420, 'Suzuki XL7': 4450,
    'Hyundai Stargazer': 4460, 'Toyota Veloz': 4475, 'Wuling Confero': 4530,
    'Mitsubishi Xpander': 4595, 'Mitsubishi Mitsubishi Xpander Cross': 4595,
    'Toyota Kijang': 4400, 'Mitsubishi Mitsubishi Kuda': 4450,
    'Isuzu Panther': 4485, 'Toyota Innova': 4735, 'Honda Odyssey': 4840,
    'Toyota Voxy': 4695, 'Toyota Alphard': 4945, 'Toyota Vellfire': 4945,
    'Toyota HiAce': 5265,
    'Suzuki Jimny': 3645, 'Daihatsu Rocky': 3995, 'Toyota Raize': 3995,
    'Suzuki Fronx': 3995, 'Daihatsu Taruna': 4030, 'Honda WR-V': 4060,
    'Nissan Juke': 4135, 'Suzuki SX4': 4135, 'Daihatsu Feroza': 3765,
    'Hyundai Creta': 4315, 'Mitsubishi Mitsubishi Destinator': 4680,
    'Toyota Hardtop': 3840, 'Honda HR-V / e:N1': 4330, 'Nissan Terrano': 4415,
    'Daihatsu Terios': 4435, 'Toyota Rush': 4435, 'Honda BR-V': 4456,
    'Mazda CX5': 4575, 'Wuling Almaz': 4655, 'Nissan X-Trail': 4690,
    'Mitsubishi Mitsubishi Outlander': 4695, 'Honda CR-V': 4703,
    'Toyota Harrier': 4740, 'Toyota Fortuner': 4795,
    'Mitsubishi Pajero Sport': 4825, 'Toyota Land Cruiser': 4950,
    'Hyundai Palisade': 4995,
    'Suzuki Carry': 4195, 'Daihatsu Gran Max Pick Up': 4195,
    'Mitsubishi Triton': 5300, 'Toyota Hilux': 5325,
}

# ---- 100 model TAMBAHAN (baru, khusus file SP/OP 200-model) ----
# Klasifikasi manual (pengetahuan otomotif umum), konvensi kategori SAMA persis
# dgn 100 di atas. "Sport/Supercar" kategori baru (belum py preseden di 100
# pertama) utk mobil sport/coupe murni yang tidak masuk kategori manapun di atas.
KATEGORI_TAMBAHAN = {
    # City Car
    'Hyundai Atoz': 'City Car', 'Chevrolet Spark': 'City Car',
    'Hyundai Grand i10': 'City Car',
    # Hatchback
    'Chevrolet Aveo': 'Hatchback', 'Hyundai Avega Hatchback': 'Hatchback',
    'Hyundai Getz': 'Hatchback', 'Kia Rio Hatchback': 'Hatchback',
    'Volkswagen Golf': 'Hatchback', 'Volkswagen Polo': 'Hatchback',
    'Volkswagen Scirocco': 'Hatchback', 'Peugeot 206': 'Hatchback',
    'Mercedes Benz A Class': 'Hatchback', 'Honda Civic Hatchback': 'Hatchback',
    'Honda Civic Type R': 'Hatchback', 'Ford Focus': 'Hatchback',
    'MG 4 EV': 'Hatchback', 'Toyota GR Yaris': 'Hatchback',
    'Suzuki Forsa': 'Hatchback',
    # Sedan
    'BMW M3': 'Sedan', 'BMW Seri 2': 'Sedan', 'BMW Seri 4': 'Sedan',
    'BMW Seri 7': 'Sedan', 'Hyundai Accent': 'Sedan', 'Hyundai Avega': 'Sedan',
    'Mitsubishi Galant': 'Sedan', 'Mitsubishi Lancer': 'Sedan',
    'Nissan Teana': 'Sedan', 'Toyota Corolla Altis': 'Sedan',
    'Toyota Corona': 'Sedan', 'Toyota Crown': 'Sedan',
    'Mercedes Benz CLS Class': 'Sedan', 'BYD SEAL': 'Sedan', 'Mazda 3': 'Sedan',
    # SUV compact (5-seater subcompact/compact crossover)
    'Mitsubishi Xforce': 'SUV compact', 'Ford Ecosport': 'SUV compact',
    'Kia Sonet': 'SUV compact', 'MG S5 EV': 'SUV compact',
    'Chery Omoda 5': 'SUV compact', 'DFSK Glory i-Auto': 'SUV compact',
    'Daihatsu Taft GT': 'SUV compact', 'Daihatsu Feroza Long': 'SUV compact',
    'Subaru XV': 'SUV compact', 'Mazda CX-3': 'SUV compact',
    'Toyota CHR': 'SUV compact', 'Wuling Alvez': 'SUV compact',
    'Hyundai Kona': 'SUV compact', 'BYD Atto 3': 'SUV compact',
    'Chevrolet Trax': 'SUV compact', 'Datsun Cross': 'SUV compact',
    'MINI Countryman': 'SUV compact', 'BMW X1': 'SUV compact',
    # SUV besar (mid-size / 7-seater crossover & SUV)
    'BMW X5': 'SUV besar', 'Ford Escape': 'SUV besar', 'Ford Everest': 'SUV besar',
    'Hyundai Santa Fe': 'SUV besar', 'Hyundai Tucson': 'SUV besar',
    'Isuzu Mux': 'SUV besar', 'Kia Sportage': 'SUV besar',
    'Lexus RX': 'SUV besar', 'Mazda CX-7': 'SUV besar', 'Mazda CX-9': 'SUV besar',
    'Mercedes Benz GLC Class': 'SUV besar', 'Mercedes Benz GLE Class': 'SUV besar',
    'Nissan Terra': 'SUV besar', 'Volkswagen Tiguan': 'SUV besar',
    'Chevrolet Captiva': 'SUV besar', 'Opel Blazer': 'SUV besar',
    'Suzuki Grand Vitara': 'SUV besar', 'Chery Tiggo 8 Pro': 'SUV besar',
    'Hyundai Ioniq 5': 'SUV besar', 'Range Rover': 'SUV besar',
    'Jeep Wrangler': 'SUV besar', 'Jeep Wrangler Rubicon': 'SUV besar',
    'Mercedes Benz G Class': 'SUV besar',
    # MPV keluarga (compact MPV)
    'Kia Carens': 'MPV keluarga', 'Toyota Wish': 'MPV keluarga',
    'Suzuki APV Luxury': 'MPV keluarga', 'Nissan Livina X-Gear': 'MPV keluarga',
    'Honda Stream': 'MPV keluarga',
    # MPV besar (van/minivan besar)
    'Chevrolet Orlando': 'MPV besar',
    'Daihatsu Gran Max Minibus / Blind Van': 'MPV besar',
    'Hyundai Staria': 'MPV besar', 'Lexus LM': 'MPV besar',
    'Mazda Biante': 'MPV besar', 'Nissan Elgrand': 'MPV besar',
    'Nissan Serena': 'MPV besar', 'Kia Grand Carnival': 'MPV besar',
    'Dodge Journey': 'MPV besar', 'Daihatsu Espass': 'MPV besar',
    'Toyota Nav1': 'MPV besar', 'Wuling Cortez': 'MPV besar',
    'Mitsubishi Grandis': 'MPV besar',
    # Pickup
    'Ford Ranger': 'Pickup', 'Mitsubishi L300 Pickup': 'Pickup',
    'Nissan Navara': 'Pickup',
    # Sport/Supercar
    'BMW M2': 'Sport/Supercar', 'BMW Z4': 'Sport/Supercar',
    'Toyota GR 86': 'Sport/Supercar', 'Mazda MX 5 RF': 'Sport/Supercar',
    'Lamborghini Aventador': 'Sport/Supercar',
}
PANJANG_TAMBAHAN = {
    'Hyundai Atoz': 3495, 'Chevrolet Spark': 3595, 'Hyundai Grand i10': 3805,
    'Chevrolet Aveo': 4039, 'Hyundai Avega Hatchback': 4155,
    'Hyundai Getz': 3850, 'Kia Rio Hatchback': 4065,
    'Volkswagen Golf': 4284, 'Volkswagen Polo': 4053,
    'Volkswagen Scirocco': 4256, 'Peugeot 206': 3835,
    'Mercedes Benz A Class': 4419, 'Honda Civic Hatchback': 4315,
    'Honda Civic Type R': 4595, 'Ford Focus': 4360,
    'MG 4 EV': 4287, 'Toyota GR Yaris': 3995, 'Suzuki Forsa': 3835,
    'BMW M3': 4794, 'BMW Seri 2': 4526, 'BMW Seri 4': 4768,
    'BMW Seri 7': 5391, 'Hyundai Accent': 4370, 'Hyundai Avega': 4300,
    'Mitsubishi Galant': 4750, 'Mitsubishi Lancer': 4570,
    'Nissan Teana': 4880, 'Toyota Corolla Altis': 4630,
    'Toyota Corona': 4520, 'Toyota Crown': 4870,
    'Mercedes Benz CLS Class': 4988, 'BYD SEAL': 4800, 'Mazda 3': 4660,
    'Mitsubishi Xforce': 4210, 'Ford Ecosport': 4090, 'Kia Sonet': 3995,
    'MG S5 EV': 4570, 'Chery Omoda 5': 4405, 'DFSK Glory i-Auto': 4400,
    'Daihatsu Taft GT': 3860, 'Daihatsu Feroza Long': 4200,
    'Subaru XV': 4465, 'Mazda CX-3': 4275, 'Toyota CHR': 4405,
    'Wuling Alvez': 4370, 'Hyundai Kona': 4205, 'BYD Atto 3': 4455,
    'Chevrolet Trax': 4280, 'Datsun Cross': 3995, 'MINI Countryman': 4433,
    'BMW X1': 4500,
    'BMW X5': 4922, 'Ford Escape': 4524, 'Ford Everest': 4914,
    'Hyundai Santa Fe': 4830, 'Hyundai Tucson': 4630, 'Isuzu Mux': 4825,
    'Kia Sportage': 4515, 'Lexus RX': 4890, 'Mazda CX-7': 4685,
    'Mazda CX-9': 5075, 'Mercedes Benz GLC Class': 4716,
    'Mercedes Benz GLE Class': 4924, 'Nissan Terra': 4885,
    'Volkswagen Tiguan': 4486, 'Chevrolet Captiva': 4635,
    'Opel Blazer': 4720, 'Suzuki Grand Vitara': 4300,
    'Chery Tiggo 8 Pro': 4722, 'Hyundai Ioniq 5': 4635,
    'Range Rover': 5052, 'Jeep Wrangler': 4882, 'Jeep Wrangler Rubicon': 4882,
    'Mercedes Benz G Class': 4901,
    'Kia Carens': 4540, 'Toyota Wish': 4590, 'Suzuki APV Luxury': 4235,
    'Nissan Livina X-Gear': 4300, 'Honda Stream': 4560,
    'Chevrolet Orlando': 4665, 'Daihatsu Gran Max Minibus / Blind Van': 4335,
    'Hyundai Staria': 5253, 'Lexus LM': 5090, 'Mazda Biante': 4620,
    'Nissan Elgrand': 4930, 'Nissan Serena': 4770, 'Kia Grand Carnival': 5155,
    'Dodge Journey': 4894, 'Daihatsu Espass': 4185, 'Toyota Nav1': 4770,
    'Wuling Cortez': 4770, 'Mitsubishi Grandis': 4765,
    'Ford Ranger': 5359, 'Mitsubishi L300 Pickup': 4215, 'Nissan Navara': 5255,
    'BMW M2': 4475, 'BMW Z4': 4324, 'Toyota GR 86': 4265,
    'Mazda MX 5 RF': 4000, 'Lamborghini Aventador': 4797,
}
KATEGORI.update(KATEGORI_TAMBAHAN)
PANJANG_MM.update(PANJANG_TAMBAHAN)

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
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=1).value
        if not nm:
            continue
        nm = str(nm).strip()
        pr = ws.cell(row=r, column=3).value
        hjt = ws.cell(row=r, column=29).value
        if nm not in KATEGORI:
            raise SystemExit(f"BELUM ada kategori utk: {nm}")
        if nm not in PANJANG_MM:
            raise SystemExit(f"BELUM ada data panjang utk: {nm}")
        pr = int(round(float(pr)))
        produk.append({"nama": nm, "pcsroll": pr, "hjt": hjt,
                        "kat": KATEGORI[nm], "panjang": PANJANG_MM[nm],
                        "baru_di_sp_op": nm in KATEGORI_TAMBAHAN})

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
        ws1.cell(r, 8, "Ya - lihat CATATAN" if p["baru_di_sp_op"] else "")
        for c in range(1, 9):
            ws1.cell(r, c).font = ARIAL

    for col, w in zip("ABCDEFGH", [5, 40, 9, 15, 12, 20, 16, 18]):
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

    tulis("CATATAN", "", tebal=True)
    tulis("Metode", "Matriks Pcs/Roll x kategori bodi x panjang fisik mobil - metode "
          "yang SUDAH DIVALIDASI user untuk toko Undercover Autocare (ditemukan di "
          "branch claude/repo-memory-access-4hthja setelah user menunjukkannya). "
          "MENGGANTIKAN metode rank-harga-UC yang sempat dipakai di percobaan "
          "pertama file 'Harga Baru SP-OP (Reguler).xlsx' - metode itu KELIRU, "
          "dibuat sebelum riwayat kerja yang benar ditemukan.")
    tulis("Sumber", f"'{SRC.rsplit('/', 1)[-1]}', sheet '{SHEET_SRC}' - {len(produk)} model.")
    tulis("Aturan", "1) Pcs/Roll -> lantai harga per tier, mandiri (tidak menumpuk). "
          "2) Dalam grup (Pcs/Roll x kategori), mobil diurutkan dari panjang bodi "
          "terkecil -> terbesar. 3) Kenaikan kelipatan Rp1.000, rentang grup maks "
          "Rp5.000. 4) Lebar spread dari skala absolut (100mm=Rp1.000, cap Rp5.000), "
          "posisi tiap mobil proporsional thd panjangnya.")
    tulis("PENTING - 100 dari 200 model BARU diklasifikasi", "Kategori & panjang bodi "
          "utk 100 model yang SUDAH ada di top-100 UC dipertahankan APA ADANYA dari "
          "branch tsb (tidak diubah). 100 model SISANYA (kolom 'Klasifikasi Baru?' = "
          "'Ya' di sheet 'Harga Baru SP-OP') BARU diklasifikasi di file ini, memakai "
          "pengetahuan otomotif umum dgn konvensi kategori yang sama - BUKAN dari "
          "kolom data eksplisit (file tidak py kolom tipe bodi/panjang). Kalau ada "
          "yang terasa kurang tepat kategorinya, tolong dikoreksi.")
    tulis("Kategori baru", "'Sport/Supercar' ditambahkan (belum ada preseden di 100 "
          "model pertama) - dipakai utk BMW M2/Z4, Toyota GR 86, Mazda MX-5 RF, "
          "Lamborghini Aventador.")
    tulis("Scope", "Cuma harga Reguler (kolom 'Harga Jual Terbaru' di sheet HPP 12%). "
          "Kolom Strip (Elite/Epic/Warrior +Rp43.000 di versi UC) TIDAK disertakan - "
          "user tidak memintanya untuk SP/OP kali ini.")
    tulis("")
    tulis("100 MODEL YANG BARU DIKLASIFIKASI (perlu direview)", "", tebal=True)
    tulis("Nama Produk", "Kategori (baru)", tebal=True)
    for nm in sorted(KATEGORI_TAMBAHAN):
        tulis(nm, f"{KATEGORI_TAMBAHAN[nm]}, {PANJANG_TAMBAHAN[nm]}mm")

    wb2.save(OUT)

    print(f"tersimpan: {OUT}")
    print(f"total model: {len(produk)} (100 lama + {len(KATEGORI_TAMBAHAN)} baru)")
    for pr in sorted({p["pcsroll"] for p in produk}, reverse=True):
        print(f"\n===== {pr} pcs/roll -> lantai Rp{lantai[pr]:,} =====".replace(",", "."))
        for kat in sorted({p["kat"] for p in produk if p["pcsroll"] == pr}):
            anggota = sorted([p for p in produk if p["pcsroll"] == pr and p["kat"] == kat],
                              key=lambda x: x["panjang"])
            hs = [a["harga_baru"] for a in anggota]
            print(f"  [{kat}] Rp{min(hs):,} - Rp{max(hs):,}  ({len(anggota)} model)".replace(",", "."))


if __name__ == "__main__":
    main()
