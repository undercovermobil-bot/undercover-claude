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

## Ranking top-100 per SKU (2026-09-24, SELESAI, dikirim ke user)

File: `RANKING_TOP100_PER_SKU.xlsx` (4 sheet: Top 100 per SKU, Peringkat
Lengkap, Keterangan, Pemetaan Nama). 369 nama di laporan -> **325 produk
(grup SKU)**. Top-100 per SKU = 29.146 unit = **95,4% seluruh unit**.

- **85 tetap + 15 masuk baru** (sebelumnya di luar top-100 per nama):
  Wuling Cortez, Honda Stream, Wuling Confero, Honda Civic Hatchback,
  Chevrolet Spin, Mitsubishi Xforce, MG S5 EV, Mercedes Benz C Class,
  Suzuki Aerio Hatchback, Hyundai Palisade, Hyundai Avega (+Avega Sedan),
  Kia Sonet, Daihatsu Taruna, Ford Everest, Suzuki Vitara (+Grand Vitara).
- **Tidak ada yang keluar** dari top-100 lama.
- **Ambang sangat tipis**: #99 Ford Everest & #100 Suzuki Vitara = 30
  unit; #101-#104 (Outlander, Mirage, BMW Seri 5, Toyota GR 86+86) = 29
  unit. Suzuki Vitara baru 30 karena digabung listing Grand Vitara (6).
- Semua produk top-100 ada di listing UA (snapshot 18 Sep), kecuali
  "Mazda 2" (tanpa SKU pasti).

**Aturan penggabungan** (detail per nama di sheet Pemetaan Nama, dasar
per baris tercatat):
1. Default: nama -> prefix SKU dominan di listing UA; kalau tidak ada,
   listing SP/OP (sp_src, op_src, op_tiktok*, lazada_src, sp_tiktok).
2. **MANUAL** (nama lama/penamaan toko lain yg tidak ada di listing, bukti
   dari rentang generasi sheet Detail): Honda Civic->HND-CVC (nama lama
   Civic Sedan, 396 unit!), Gran Max PU->DHT-GMXP, Gran Max MB->DHT-GMX,
   Honda City->HND-CTY, Suzuki APV->SZK-APV, Strada Triton->MTB-TRN,
   **Mitsubishi Pajero->MTB-PJS** (listing SP/OP bernama "Pajero" isinya
   Pajero Sport), Carry PU->SZK-CRP, Mercedes E Class->MBZ-ECL, Starlet
   Kapsul->TYT-STR, Aion Hyptec HT->GAC-HH, Hardtop/Land Cruiser->TYT-HTP,
   Suzuki Vitara + Grand Vitara -> 1 grup (listing multi-SKU GVT/GVH/EVT).
3. **DIPECAH**: Daihatsu Rocky 90 = 85 ke TYT-RZE (77 gen 2019+ & 8 tanpa
   info gen ikut mayoritas) + 5 F70 ke DHT-FRZ. Daihatsu Gran Max 18 (listing
   gabungan tanpa info bodi) = 9 DHT-GMX + 9 DHT-GMXP.
4. **SENGAJA TIDAK digabung**: Grand Livina Custom Roofbox, Livina X-Gear
   (NSN-LXG), Vios Custom, Maserati Custom Spoiler, Range Rover Velar/Sport
   (LDR-RR sama, curiga salah tag), Mazda 2 / Mazda 3 / Kia Rio / Suzuki
   Aerio tanpa bodi, Feroza Long, Suzuki Carry vs Carry Pickup.

**Perlu keputusan user (belum ditanyakan eksplisit)**: "Mazda 2" (117
unit, #51) tanpa bodi — kalau Hatchback, gabung ke MZD-2H (219 unit) ->
1 slot top-100 kosong, diperebutkan 4 produk seri 29 unit.

## Pertanyaan user 2026-09-24: "yg SKU-nya gabung ikut masuk 100?"

Jawaban: YA — 1 baris di sheet Top 100 = 1 SKU = 1 cover fisik; nama
kembar sudah terhitung di baris itu (mis. Feroza 243 = Feroza 230 + Rocky
lama 5 + Taft GT 8). Dalam bentuk NAMA MOBIL di listing UA, **100 SKU =
109 nama mobil** (99 SKU + baris "Mazda 2" tanpa SKU; 10 nama tambahan =
kembar: Xenia, Veloz, Ayla/Agya, Terios, Sigra, Rocky, Vellfire, Luxio,
Gran Max gabungan, Taft GT). Stok/produksi tetap 100 cover.

Ditambah sheet **"Daftar Mobil Listing UA"** di `RANKING_TOP100_PER_SKU.xlsx`:
**415 nama mobil** di listing UA (setelah buang cover motor/karpet/pouch &
duplikat judul spt "Mobil Timor"/"Daihatsu Daihatsu ..."/"Mercedes" vs
"Mercedes Benz") -> **109 Dipertahankan, 306 di luar top-100** (93 di
antaranya 0 terjual di periode Apr-Sep = tidak ada SKU-nya di data
penjualan). Kolom Status pakai rumus thd ambang di Keterangan!B6, jadi
ikut berubah kalau ambang diubah. Tinggi baris kolom "Nama yang
Digabung" juga dirapikan (screenshot user kelihatan terpotong).

Catatan: di luar top-100 masih ada nama berbagi prefix yang BUKAN kembar
yang diputuskan (Range Rover/Velar/Sport, Discovery/Discovery Sport,
Ferrari 488 Pista/Spider, Fiat 500/Aircross, Wrangler/Rubicon, L300/L300
Pickup) — tidak mempengaruhi daftar dipertahankan, cuma info.

## UPDATE 2026-09-24: Mazda 2 = Hatchback (keputusan user) + aturan seri

- User konfirmasi **"Mazda 2" = Mazda 2 Hatchback** -> digabung ke `MZD-2H`
  (MANUAL di `ranking_per_sku.py`): 117 + 102 = **219 unit, #37**. Grup kini
  324 (bukan 325). Nama grup dipaksa lewat `NAMA_GRUP` (MZD-2H "Mazda 2
  Hatchback", DHT-GMXP "Gran Max Pick Up", HND-CVC "Honda Civic Sedan") krn
  anggota terlarisnya pakai penamaan lama/toko lain.
- Slot yg kosong diperebutkan 4 produk sama-sama 29 unit. **Aturan seri
  (keputusan Claude, bisa diubah user): unit sama -> Total Penjualan (Rp)
  lebih besar di atas.** Hasil: **#100 BMW Seri 5 (Rp 8,50 jt)**; di luar:
  #101 Outlander (8,07 jt), #102 GR 86 (7,74 jt), #103 Mirage (6,19 jt).
  Aturan ini juga menggeser urutan seri lain (Suzuki Vitara #98, Ford
  Everest #99).
- **Angka FINAL saat ini**: top-100 = 29.175 unit (95,5%), **84 tetap + 16
  masuk baru** (15 sebelumnya + BMW Seri 5), 0 keluar; semua 100 ada di
  listing UA. Daftar Mobil Listing UA: 415 nama -> **110 dipertahankan**,
  305 di luar top-100.
- Angka di bagian atas file ini (325 grup, 85+15, 109 nama, "Mazda 2
  perlu keputusan") sudah TIDAK berlaku — pakai angka di bagian ini.

## Skrip (disimpan di repo, siap dipakai ulang kuartal berikutnya)

`hpp-per-merk-scripts/`: `sku_map_lib.py` (peta nama listing -> prefix SKU,
simpan `sku_map.pkl`), `ranking_per_sku.py` (aturan MANUAL/SPLIT/TERPISAH +
grouping), `build_ranking_xlsx.py` (tulis workbook, rumus SUMIFS ke sheet
Pemetaan Nama), `inject_cache.py` (hitung nilai rumus & tanam sbg cached
value). Semua baca folder data dari env `KERJA_DIR`. Urutan:
`repair_xlsx.py` utk listing -> `sku_map_lib.py` -> `build_ranking_xlsx.py`
-> `inject_cache.py <file>`. **Kuartal berikutnya: cek ulang SPLIT (qty
Rocky/Gran Max diambil manual dari sheet Detail, script `assert` kalau
total tidak cocok) dan MANUAL (nama baru di laporan yg tidak ketemu di
listing akan jadi grup sendiri — cek daftar "berdiri sendiri").**

## JEBAKAN TEKNIS: LibreOffice rusak di kontainer cloud (2026-09-24)

`soffice` gagal membuka file xlsx APA PUN ("source file could not be
loaded", bahkan file 1 sel; `recalc.py` skill xlsx timeout). Solusi:
`inject_cache.py` mengevaluasi rumus dari TEKS rumusnya sendiri (pola
SUMIFS/COUNTIFS/SUM/IF/bagi/kurang saja) lalu menanam `<v>` ke XML —
file tetap berisi rumus (Excel hitung ulang) sekaligus tidak tampil
kosong di preview HP/Google Sheets (keluhan lama user soal "formula
kosong", lihat project-undercover-harga-referensi.md). Hasil diverifikasi
silang ke grouping Python: 0 selisih. Butuh `pip install lxml`.
