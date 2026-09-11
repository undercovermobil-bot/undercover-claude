#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harga baru Transparan utk 100 model di "DATA UC HPP Top 100 Terlaris.xlsx",
2026-09-11.

Dasar dari user: sheet 'Transparan' kolom 'Harga Jual Terbaru', 2 baris
relevan (City Car/SUV = 195716.1981, MPV = 430175.4386), dibulatkan
ribuan ke atas -> 196.000 (tingkat "3 pcs/roll", mobil ukuran DI BAWAH
Fortuner/Pajero) dan 431.000 (tingkat "1 pcs/roll", mobil ukuran SE-
FORTUNER/PAJERO KE ATAS). Tiap tingkat punya rentang toleransi +Rp3.000
("tergantung ukurannya") - kecil: 196rb-199rb, besar: 431rb-434rb.

User pilih: klasifikasi tiap model & posisi dlm rentang ditentukan
sendiri (pakai pengetahuan segmen/tipe bodi mobil), bukan dari sumber
data lain - TIDAK ADA daftar ukuran per-model di file yg diupload,
cuma 4 baris kategori generik (City Car/SUV/MPV/Hiace-tak lengkap).

Cakupan: 100 model di "Top 100 Terlaris" (sheet sumbernya) - LOGIKA
SAMA bisa dipakai lagi utk model di luar top-100 begitu ketemu di
listing SP/OP asli (blm ada di file ini).

Pemakaian: python3 harga_transparan_top100.py
"""
import openpyxl

SRC = "Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx"
OUT = "Referensi_Harga_Baru_Transparan_Top100.xlsx"

HARGA = {'A': [196000, 197000, 198000, 199000],
         'B': [431000, 432000, 433000, 434000]}

# (nama persis dari kolom A sheet 'Top 100 Terlaris', tingkat, index 0-3
# dlm rentang, segmen/tipe bodi utk transparansi alasan klasifikasi)
KLASIFIKASI = [
    ("Toyota Avanza", 'A', 2, "MPV kompak"),
    ("Honda Brio Satya / RS", 'A', 1, "Hatchback"),
    ("Toyota Innova", 'B', 1, "MPV menengah (Zenix/Reborn, sekelas Fortuner)"),
    ("Honda Jazz", 'A', 1, "Hatchback"),
    ("Suzuki Ertiga", 'A', 2, "MPV kompak"),
    ("Honda HR-V / e:N1", 'A', 2, "SUV kompak"),
    ("Toyota Agya", 'A', 0, "City car"),
    ("Daihatsu Ayla", 'A', 0, "City car"),
    ("Daihatsu Xenia", 'A', 2, "MPV kompak"),
    ("Nissan Livina / Grand Livina", 'A', 2, "MPV kompak"),
    ("Toyota Vios", 'A', 1, "Sedan kompak"),
    ("Toyota Fortuner", 'B', 0, "SUV menengah (acuan batas bawah)"),
    ("Honda BR-V", 'A', 2, "SUV/MPV kompak"),
    ("Toyota Calya", 'A', 0, "MPV kompak (LCGC)"),
    ("Toyota Rush", 'A', 2, "SUV kompak"),
    ("Toyota Yaris", 'A', 1, "Hatchback"),
    ("Toyota Kijang", 'A', 2, "MPV klasik (generasi lama, sekelas Avanza)"),
    ("Honda CR-V", 'A', 3, "SUV kompak-menengah (crossover, bukan body-on-frame)"),
    ("Honda Mobilio", 'A', 2, "MPV kompak"),
    ("Honda Civic", 'A', 1, "Sedan kompak-menengah"),
    ("Daihatsu Terios", 'A', 2, "SUV kompak"),
    ("Mitsubishi Xpander", 'A', 2, "MPV kompak"),
    ("Toyota Camry", 'A', 3, "Sedan menengah-besar"),
    ("Honda Accord", 'A', 3, "Sedan menengah-besar"),
    ("Toyota Corolla", 'A', 1, "Sedan kompak"),
    ("Suzuki APV Arena / Blind Van", 'A', 2, "Van/MPV ringan"),
    ("Toyota Raize", 'A', 2, "SUV kompak"),
    ("Isuzu Panther", 'A', 2, "MPV klasik (sekelas Kijang lama)"),
    ("Mitsubishi Pajero Sport", 'B', 0, "SUV menengah (acuan batas bawah)"),
    ("Daihatsu Sigra", 'A', 0, "MPV kompak (LCGC)"),
    ("Suzuki Baleno", 'A', 1, "Hatchback"),
    ("Suzuki Fronx", 'A', 2, "SUV/crossover kompak"),
    ("Honda Freed", 'A', 2, "MPV kompak"),
    ("Toyota Hilux", 'B', 2, "Pickup double cabin (sekelas Fortuner+)"),
    ("Suzuki Swift", 'A', 1, "Hatchback"),
    ("Suzuki Karimun", 'A', 0, "City car"),
    ("Mitsubishi Triton", 'B', 2, "Pickup double cabin (sekelas Pajero Sport+)"),
    ("Honda City Sedan", 'A', 1, "Sedan kompak"),
    ("Suzuki XL7", 'A', 2, "MPV/crossover kompak"),
    ("Nissan March", 'A', 0, "City car/hatchback"),
    ("Toyota HiAce", 'B', 3, "Van (commuter, tinggi & besar)"),
    ("Mazda 2 Sedan", 'A', 1, "Sedan kompak"),
    ("Toyota Hardtop", 'B', 3, "SUV 4x4 besar (Land Cruiser Hardtop/FJ40)"),
    ("Suzuki Jimny", 'A', 2, "SUV mini/off-roader"),
    ("Suzuki Ignis", 'A', 1, "Hatchback/crossover kompak"),
    ("BMW Seri 3", 'A', 2, "Sedan kompak-menengah (premium)"),
    ("Kia Picanto", 'A', 0, "City car"),
    ("Daihatsu Sirion", 'A', 1, "Hatchback"),
    ("Daihatsu Feroza", 'A', 2, "SUV kompak (klasik)"),
    ("Toyota Veloz", 'A', 2, "MPV kompak (basis Avanza)"),
    ("Toyota Alphard", 'B', 2, "MPV besar mewah"),
    ("Toyota Starlet", 'A', 1, "Hatchback"),
    ("Daihatsu Luxio", 'A', 2, "MPV/van kompak"),
    ("Toyota Etios Valco", 'A', 1, "Hatchback"),
    ("Honda WR-V", 'A', 2, "SUV kompak"),
    ("Suzuki Splash", 'A', 0, "Hatchback kecil"),
    ("Daihatsu Gran Max Pick Up", 'A', 2, "Pickup/van ringan (sekelas Avanza)"),
    ("Daihatsu Rocky", 'A', 2, "SUV kompak"),
    ("Nissan Juke", 'A', 2, "SUV/crossover kompak"),
    ("Toyota Vellfire", 'B', 2, "MPV besar mewah"),
    ("Ford Fiesta", 'A', 1, "Hatchback"),
    ("MINI Cooper", 'A', 1, "Hatchback premium"),
    ("Toyota Land Cruiser", 'B', 3, "SUV besar body-on-frame"),
    ("Honda Odyssey", 'B', 1, "MPV besar (minivan)"),
    ("Toyota Voxy", 'B', 1, "MPV/van menengah (tinggi, sekelas Alphard-lite)"),
    ("Mercedes Benz E Class", 'A', 3, "Sedan menengah-besar (premium)"),
    ("Suzuki Carry", 'A', 2, "Van/pickup ringan"),
    ("Nissan Evalia", 'A', 2, "MPV/van kompak"),
    ("Mitsubishi Mitsubishi Kuda", 'A', 2, "MPV kompak (klasik)"),
    ("Nissan X-Trail", 'A', 3, "SUV/crossover kompak-menengah"),
    ("Suzuki SX4", 'A', 1, "Crossover/hatchback kompak"),
    ("Daihatsu Taruna", 'A', 2, "SUV kompak (klasik)"),
    ("Mitsubishi Mitsubishi Xpander Cross", 'A', 2, "SUV/crossover MPV kompak"),
    ("Toyota Sienta", 'A', 2, "MPV kompak"),
    ("Mitsubishi Mitsubishi Destinator", 'A', 3, "SUV/crossover kompak-menengah"),
    ("Honda City Hatchback RS", 'A', 1, "Hatchback"),
    ("Datsun Go Plus", 'A', 0, "MPV/hatchback kompak"),
    ("BYD Atto 1", 'A', 0, "City car (EV)"),
    ("Nissan Terrano", 'A', 2, "SUV kompak"),
    ("Hyundai Creta", 'A', 2, "SUV kompak"),
    ("Mitsubishi Mirage", 'A', 0, "City car/hatchback"),
    ("Mercedes Benz S Class", 'A', 3, "Sedan besar (premium)"),
    ("Hyundai Stargazer", 'A', 2, "Crossover MPV kompak"),
    ("Chevrolet Spin", 'A', 2, "MPV kompak"),
    ("Mazda CX5", 'A', 3, "SUV/crossover kompak-menengah"),
    ("Wuling Air EV", 'A', 0, "City car (EV)"),
    ("BMW Seri 5", 'A', 3, "Sedan menengah-besar (premium)"),
    ("Toyota Harrier", 'A', 3, "SUV/crossover kompak-menengah"),
    ("Wuling Almaz", 'A', 2, "SUV/crossover kompak-menengah"),
    ("Mercedes Benz C Class", 'A', 2, "Sedan kompak-menengah (premium)"),
    ("Kia Rio Sedan", 'A', 1, "Sedan kompak"),
    ("Suzuki S-Presso", 'A', 0, "City car"),
    ("Datsun Go", 'A', 0, "City car/hatchback"),
    ("Toyota Soluna", 'A', 1, "Sedan kompak (klasik)"),
    ("Mitsubishi Mitsubishi Outlander", 'A', 3, "SUV menengah (crossover)"),
    ("Suzuki Aerio Hatchback", 'A', 1, "Hatchback"),
    ("Hyundai Palisade", 'B', 1, "SUV besar 3-baris (crossover, sekelas Fortuner+)"),
    ("Timor", 'A', 1, "Sedan kompak (klasik)"),
    ("Mazda 2 Hatchback", 'A', 1, "Hatchback"),
    ("Wuling Confero", 'A', 2, "MPV kompak"),
]


def main():
    src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = src['Top 100 Terlaris']
    rank_of = {}
    for r in range(2, ws_src.max_row + 1):
        nm = ws_src.cell(r, 1).value
        if nm:
            rank_of[nm] = r - 1

    assert len(KLASIFIKASI) == 100, f"harus 100 baris, ada {len(KLASIFIKASI)}"
    names_in = {k[0] for k in KLASIFIKASI}
    names_src = set(rank_of.keys())
    missing = names_src - names_in
    extra = names_in - names_src
    if missing or extra:
        print("PERINGATAN - nama tidak cocok persis dgn sheet sumber:")
        print(" hilang dari klasifikasi:", missing)
        print(" tidak ada di sumber:", extra)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Harga Transparan"
    ws.append(["No", "Nama Produk", "Segmen/Tipe Bodi", "Tingkat",
               "Rentang Tingkat", "Harga Baru Transparan"])
    for nm, tingkat, idx, segmen in KLASIFIKASI:
        harga = HARGA[tingkat][idx]
        label_tingkat = ("Kecil (di bawah Fortuner/Pajero, basis 3 pcs/roll)"
                          if tingkat == 'A' else
                          "Besar (se-Fortuner/Pajero ke atas, basis 1 pcs/roll)")
        rentang = "196.000 - 199.000" if tingkat == 'A' else "431.000 - 434.000"
        ws.append([rank_of.get(nm, ''), nm, segmen, label_tingkat, rentang, harga])

    for col, width in zip('ABCDEF', [4, 32, 45, 50, 20, 20]):
        ws.column_dimensions[col].width = width

    wb.save(OUT)
    print(f"Tersimpan: {OUT} ({len(KLASIFIKASI)} model)")
    tier_a = sum(1 for k in KLASIFIKASI if k[1] == 'A')
    tier_b = sum(1 for k in KLASIFIKASI if k[1] == 'B')
    print(f"Tingkat Kecil (196-199rb): {tier_a} model")
    print(f"Tingkat Besar (431-434rb): {tier_b} model")


if __name__ == '__main__':
    main()
