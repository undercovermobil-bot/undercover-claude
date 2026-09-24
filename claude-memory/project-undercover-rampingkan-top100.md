# Rampingkan katalog UA jadi 100 produk terlaris (mulai 2026-09-24)

## Rencana user

Katalog Undercover (UA) mau dipangkas jadi **100 produk terlaris saja**,
dievaluasi **tiap kuartal** (mobil keluar-masuk di ambang 100). Langkah
pertama: cek dulu mobil kembar (1 SKU untuk >1 mobil) yang posisinya di
luar top-100, sebelum menentukan daftar final.

## Sumber data

`MOBIL_TERLARIS_BIGSELLER.xlsx` (dibuat 2026-09-17) — periode **1 Apr - 16
Sep 2026 (169 hari)**, 30.550 unit, 369 model. Sumber: ekspor BigSeller
"Laporan Penjualan > Berdasarkan SKU Toko". Beda dari laporan lama
(`MOBIL_TERLARIS_GABUNGAN.xlsx`, Jan-Jun):
- **Gabungan 4 toko** (UA/OT/SP/OP), tidak ada kolom per-toko.
- **Lazada TIDAK termasuk** (tidak terhubung ke akun BigSeller).
- Model dikelompokkan berdasar **NAMA listing, bukan SKU** — jadi mobil
  kembar (Avanza/Xenia/Veloz dst) muncul sbg baris terpisah, dan varian
  nama/typo/penamaan OT ("... Semi Outdoor") juga jadi baris sendiri.
- Tidak ada blok Detail Premium/Exclusive per-warna (disederhanakan).

## Metode cek kembar (skrip scratchpad `twin_check.py`)

Nama mobil di data penjualan dipetakan ke **prefix SKU yang benar-benar
dipakai di listing UA** (Shopee 5 file + TikTok + Lazada, snapshot 18
Sept), lalu dicari prefix yang dipakai >1 nama. Prefix dihitung hanya
kalau mencakup >=20% baris listing nama itu (buang noise salah-tag).
Lebih andal daripada mengandalkan daftar kembar dari ingatan.

## Hasil (2026-09-24)

**Kembar yang SEMUA anggotanya di dalam top-100** (aman): Avanza #1 /
Xenia #9 / Veloz #41 (TYT-AVZ), Agya #7 / Ayla #8 (DHT-AYL), Rush #10 /
Terios #22 (TYT-RSH), Calya #15 / Sigra #26 (TYT-CLY), Alphard #28 /
Vellfire #88 (TYT-ALP), Luxio #47 / Gran Max Minibus #84 (DHT-GMX),
Raize #19 / Rocky #67 (TYT-RZE).

**Kembar yang ada anggota DI LUAR top-100**:
- **Daihatsu Taft GT #184 (8 unit)** — SKU `DHT-FRZ`, partner Feroza #37
  (230) + Rocky lama F70/F300. Total grup ~243 unit.
- **Daihatsu Gran Max #133 (18 unit)** — listing gabungan Minibus+Pick Up
  dalam 1 produk, SKU terbagi `DHT-GMX` & `DHT-GMXP`; kedua partner di
  dalam top-100.
- **Toyota Raize Semi Outdoor #215 (6)** — listing OT untuk Raize, SKU sama.

**Rocky terbelah 2 SKU**: dari 90 unit "Daihatsu Rocky", ~77 generasi
baru 2019+ (-> `TYT-RZE`, ikut Raize), ~5 F70 lama (-> `DHT-FRZ`, ikut
Feroza), ~8 tanpa info gen. Jadi "Feroza = Taft = Rocky" hanya berlaku
utk Rocky LAMA. **Feroza Long (#191) BUKAN kembar** — SKU sendiri `DHT-FRL`.

**Duplikat nama (mobil sama, beda penulisan) di luar top-100**: Carry PU
#115 (= Carry Pickup #86, `SZK-CRP`), Gran Max Pick Up Semi Outdoor #140,
Fortuner "Exxclusive" #283 (typo), + varian "Semi Outdoor" (OT) utk
Picanto/Sienta/City Hatchback/APV Luxury/Evalia/Datsun Go Plus/BYD Atto
3/Ford Escape/Delica. **Grand Livina Custom Roofbox #319 BUKAN duplikat**
— prefix sama `NSN-LVN` tapi produk & harga beda (sudah dikecualikan di
proyek harga, `KECUALI`).

**Slot top-100 yang terpakai duplikat**: ~11 slot terkonfirmasi via SKU
(Xenia, Veloz, Ayla, Terios, Sigra, Calya-typo #65, Rocky, Vellfire,
Gran Max Minibus + Gran Max MB, Gran Max PU/Pick Up) + ~3 kemungkinan
duplikat nama yg tidak bisa diverifikasi via listing UA (Strada Triton
#83 = Triton #31, Suzuki APV #76 = APV Arena #21, Honda City #72 = City
Sedan #60 — nama-nama ini dari toko lain, tidak ada di listing UA). Jadi
top-100 "per nama" sebenarnya hanya ~86-89 produk fisik berbeda.

**Perlu dicek terpisah (bukan kembar yang pernah diputuskan)**: Range
Rover / Velar / Sport berbagi `LDR-RR`, Jeep Wrangler / Rubicon berbagi
`JEP-WRA` — kemungkinan salah-tag SKU, semua di luar top-100.

## Belum dikerjakan

Ranking ulang top-100 berbasis grup SKU (gabung kembar + duplikat nama)
— ditawarkan ke user sbg langkah berikutnya, belum ada instruksi.
