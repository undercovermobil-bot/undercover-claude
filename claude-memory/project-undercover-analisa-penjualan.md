# Analisa Data Penjualan (Mobil Terlaris) — mulai 2026-08-05

Sub-proyek analisa, beda dari SKU Sync. Sumber: file `MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx`
(dibuat 2026-07-22 16:59 oleh script user, folder sumber `C:\Users\OWNER\Downloads\Sales`).
Versi sebelumnya `Mobil_Terlaris.xlsx` (upload 07-23) — **diagnostik identik**, jadi bug di
bawah ini bukan sekali kejadian.

## Struktur file

3 sheet:
- `Top 300 Mobil` — header di **baris 5**, data mulai **baris 6**. Isinya 217 model
  (bukan 300), + **baris terakhir = baris TOTAL** ("TOTAL (semua model, termasuk di luar
  Top 300)") yang berisi 27.229. Kalau menjumlah kolom Kuantitas tanpa memfilter baris
  bernomor, hasilnya dobel (54.291 = 27.062 model + 27.229 baris TOTAL). **Jebakan.**
- `Detail Gen & Warna` — header di **baris 3**, data mulai **baris 4**. 2.242 baris,
  217 model unik (sama persis dgn Top 300, 0 selisih).
- `Metodologi` — definisi + blok DIAGNOSTIK yang isinya paling penting (lihat bawah).

Kolom `% Kuantitas` / `% Nilai` disimpan sebagai **pecahan** (0,08711) bukan angka 8,711 —
diformat persen di Excel. Hati-hati waktu hitung balik total.

## Rumus di file — SUDAH DIVERIFIKASI BENAR SEMUA (2026-08-05)

Dicek satu per satu, **bukan sampling**: 217 baris Top 300 + 2.242 baris Detail.
**0 baris menyimpang.**

| Kolom | Rumus | Hasil cek |
|---|---|---|
| Rata-rata Terjual/Hari | Kuantitas ÷ 181 | 0 salah |
| Rata-rata/Minggu | Rata-rata/Hari × 7 | 0 salah |
| Rata-rata/Bulan | Rata-rata/Hari × 30 (bulan = 30 hari, bukan 30,4) | 0 salah |
| Estimasi Stok | ceil(Rata-rata/Hari × 7) | 0 salah |

Pembagi **181 hari = 1 Jan – 30 Jun 2026** (31+28+31+30+31+30). Angka ini **hardcoded**
di script user (Metodologi r29 mengakuinya), TAPI **kebetulan benar** — nama file mentah
di Drive memang `Order.all.20260101_20260131.xlsx` s/d `Order.all.20260601_20260630.xlsx`.

Jadi: **aritmetikanya tidak ada yang salah.** Yang bermasalah adalah data yang masuk.

## BUG DATA — 3 lubang besar (temuan 2026-08-05)

Dari blok DIAGNOSTIK di sheet Metodologi:
```
Total baris order terbaca: 33.529
    Shopee: 33.369 | TikTok: 0 | Lazada: 160
```

1. **TikTok = 0 baris.** Padahal file order TikTok ADA di Drive — 7 file, ±5,8 MB, di
   folder `Data Sales Jan - Jun 2026/{Undercover,Otopro,Smartpro}/TikTok/`, nama
   `Semua pesanan-2026-07-22-*.xlsx`. Script sama sekali tidak berhasil membacanya.
   **Ini lubang terbesar.**
2. **Undercover/Shopee bulan Maret berupa `.zip`**, bukan `.xlsx`
   (`Order.all.20260301_20260331.zip`, 1,9 MB). Hampir pasti dilewati script yang
   nge-glob `*.xlsx`. UC Shopee itu toko terbesar (±1,4 MB/bulan vs toko lain 25–310 KB),
   jadi kehilangan 1 bulan penuh di toko terbesar.
3. **Lazada cuma 160 baris** dari 4 file. Selain itu **Otonation tidak punya folder
   TikTok maupun Lazada sama sekali**, dan **Otopro tidak punya folder Lazada**.

## Angka hasil (per 181 hari)

Apa adanya di file: **27.229 unit → 150,4 unit/hari**, Rp 8.022.510.728
(≈ Rp 294.631/unit, ≈ Rp 44,3 jt omzet/hari).

Estimasi kalau lubang ditutup (dasar: kepadatan Shopee 2.835 unit mobil per MB file mentah):

| Skenario | Total unit | Unit/hari |
|---|---|---|
| Apa adanya sekarang | 27.229 | 150,4 |
| + UC Shopee Maret | 31.389 | 173,4 |
| + Maret + TikTok (asumsi 40%) | 37.963 | 209,7 |
| + Maret + TikTok (asumsi 70%) | 42.893 | 237,0 |
| + Maret + TikTok (asumsi 100%) | 47.823 | 264,2 |

**Klaim "rata-rata produksi 200/hari" = 36.200 unit/181 hari → masuk akal, bahkan
kemungkinan lebih akurat daripada angka 150 di file.** Angka 150 itu **lantai**, bukan
kebenaran.

## PENJUALAN ≠ PRODUKSI (jangan disamakan)

File ini mengukur penjualan marketplace, bukan produksi. Yang tidak masuk:
- **motor** — 767 baris order sengaja dilewati ("Hanya MOBIL"), padahal tetap diproduksi
- **batal/refund** — 5.184 baris dilewati; sebagian sudah terlanjur diproduksi
- **retur penuh** — 438 baris dilewati
- **produk non-cover** (shampoo, Headlamp Restorer, dll) — tidak dihitung
- **order di luar marketplace** (offline/reseller/WA) — tidak ada di file sama sekali

Jadi produksi/hari secara struktural **selalu lebih besar** dari penjualan/hari di file ini.

## Komposisi penjualan (dari 27.062 unit yang terhitung)

| Jenis Cover | Unit | % |
|---|---|---|
| Reguler | 23.165 | 85,60% |
| Strip | 3.315 | 12,25% |
| Premium | 336 | 1,24% |
| Exclusive | 246 | 0,91% |

Top 5 model: Toyota Avanza 2.372 (13,10/hari) · Honda Brio 2.124 (11,73) ·
Toyota Innova 1.814 (10,02) · Honda Jazz 1.194 (6,60) · Suzuki Ertiga 1.038 (5,73).

446 model unik total, tapi hanya 217 yang tampil; sisa "ekor panjang" 167 unit (0,61%).

## Catatan Metodologi lain yang perlu diingat

- Blok Detail Strip di sheet Top 300 = qty per label Strip apa adanya, **DI LUAR** Warna Polos.
- Blok Detail Premium/Exclusive = **SUBSET** dari Warna Polos — **jangan dijumlah dobel**.
- Kuantitas = qty terjual − qty diretur.
- Nilai NET setelah diskon (Shopee: Subtotal Pesanan; TikTok: SKU Subtotal After Discount;
  Lazada: paidPrice).

## UPDATE 2026-08-05 — data TikTok akhirnya masuk

User upload `Semua pesanan-2026-08-05-13_44.xlsx` (TikTok Seller Center, toko **Undercover**).
Sheet `OrderSKUList`, 9.355 baris x 65 kolom. **Header di baris 1, deskripsi kolom di baris 2,
data mulai baris 3.** Dimensi tidak terbaca lewat `read_only=True` (max_row/max_col = 1) —
harus load biasa.

Kolom penting: `Order Status`, `Order Substatus`, `Seller SKU`, `Product Name`, `Variation`,
`Quantity`, `Sku Quantity of return`, `SKU Subtotal After Discount`, `Created Time`
(format **DD/MM/YYYY HH:MM:SS**), `Product Category`, `Purchase Channel`.

### Hasil (aturan disamakan dgn Metodologi v1)

| | unit | nilai | /hari |
|---|---|---|---|
| v1 (Shopee+Lazada) | 27.229 | Rp 8.022.510.728 | 150,4 |
| TikTok Undercover | **6.896** | **Rp 2.075.884.551** | 38,1 |
| **Gabungan v2** | **33.958** | **Rp 10.051.059.487** | **187,6** |

Naik +25,3% unit. Periode terkonfirmasi: Created Time 2026-01-01 s/d 2026-06-30, **nol baris
di luar periode** — jadi pembagi 181 hari benar untuk TikTok juga.

### Temuan baru yang penting

1. **TikTok Seller Center MENCAKUP TOKOPEDIA.** Dari 6.896 unit: TikTok 4.230 (61,3%),
   **Tokopedia 2.666 (38,7%)**. Tokopedia selama ini tidak pernah terhitung sama sekali,
   dan tidak pernah disebut di Metodologi v1.
2. **Kolom `Product Category` TikTok TIDAK BISA DIPERCAYA.** "Kursi & Sarung Kursi" berisi
   *Body Cover Motor NMAX*; "Radiator, Pendinginan Mesin" berisi *Cover Motor Benelli*;
   ada juga "Tinju & Seni Bela Diri" (samsak). **Pilah pakai NAMA PRODUK, jangan kategori.**
3. **Kelengkapan Seller SKU di order TikTok naik tajam** — bukti kerja SKU Sync berhasil:
   Jan 8,9% · Feb 10,3% · Mar 11,8% · Apr 13,6% · **Mei 49,7% · Jun 83,1%**.
   Order menyimpan SKU saat transaksi, jadi bulan lama tidak bisa diperbaiki surut.
4. **Typo di nama listing TikTok**: `Undervover Autocare` (Toyota Calya, 88 unit) dan
   `Fortuner Exxclusive`. Perlu diperbaiki di listing.
5. Nama produk TikTok punya beberapa pola berbeda yang bikin pencocokan gagal kalau
   parsernya naif: `Toyota Rush - Autocare Undercover` (urutan toko dibalik, 389 unit!),
   `Body Cover Mobil / Sarung / Selimut Mobil Mobilio` (model di akhir, tanpa merek),
   `Suzuki Carry PU`. Parser ada di `scripts/nama_tiktok.py` — pencocokan naik dari
   6.096 -> 6.702 unit setelah diperbaiki.
6. 86 model TikTok tidak ada di Top 300 v1 (194 unit) — memang bagian "ekor panjang"
   446 model, wajar.

### UPDATE lanjutan — TikTok Otoprotection & Smartprotection ikut masuk (2026-08-05)

User upload 2 file lagi: `...14_02_Otopro.xlsx` (1.472 baris) dan `...14_04_Smartpro.xlsx`
(1.390 baris). Struktur identik (sheet `OrderSKUList`, 65 kolom).
**Tapi pola nama produknya BEDA** — `Cover Mobil / Selimut Mobil Suzuki Jimny`,
**tanpa nama toko sama sekali**. Jadi deteksi toko harus per-file, bukan dari nama produk.
Pola prefix ini ditambahkan ke `nama_tiktok.py`.

| Toko (TikTok) | Unit | Nilai | /hari | SKU terisi |
|---|---|---|---|---|
| Undercover | 6.896 | Rp 2.075.884.551 | 38,10 | 26,7% |
| Otoprotection | 1.210 | Rp 279.972.702 | 6,69 | **96,9%** |
| Smartprotection | 1.122 | Rp 238.328.892 | 6,20 | **88,2%** |
| **TikTok total** | **9.228** | **Rp 2.594.186.145** | **50,98** | |

### ANGKA FINAL v3

| | unit | nilai | /hari |
|---|---|---|---|
| v1 (Shopee+Lazada) | 27.062 tampil / 27.229 total | Rp 8,02 M | 150,4 |
| TikTok 3 toko | 9.228 | Rp 2,59 M | 51,0 |
| **GABUNGAN v3** | **36.290** | **Rp 10.569.361.081** | **200,50** |

**200,5 unit/hari — klaim user "rata-rata produksi 200/hari" TERKONFIRMASI hampir persis.**
Padahal UC Shopee Maret (~4.160 unit) masih belum masuk, jadi angka sebenarnya masih di atas ini.

### Sinyal bisnis: penjualan OP & SP anjlok Mei–Juni

Unit per bulan (TikTok):

| Toko | Jan | Feb | Mar | Apr | Mei | Jun |
|---|---|---|---|---|---|---|
| Undercover | 1.053 | 1.056 | 1.673 | 1.168 | 1.004 | 942 |
| Otoprotection | 238 | 202 | 287 | 245 | **137** | **101** |
| Smartprotection | 220 | 189 | 323 | 247 | **107** | **36** |

Undercover stabil, tapi **SP turun 84% (220 -> 36)** dan **OP turun 58% (238 -> 101)**
dari Januari ke Juni. Perlu diselidiki: masalah listing, stok, harga, atau iklan?
(Catatan: analisis iklan = proyek Digital Marketing terpisah, jangan dicampur ke repo ini.)

Perhatikan juga SKU terisi OP 96,9% dan SP 88,2% jauh lebih baik dari UA 26,7% —
UA punya listing paling banyak & paling lama, jadi paling banyak order lama tanpa SKU.

### Penyelarasan format Gen & Warna (permintaan user 2026-08-05)

User minta nama mobil tetap seperti sheet `Top 300 Mobil` dan **generasi disesuaikan
dengan format sheet `Detail Gen & Warna`**. Kosakata Gen laporan (92 label unik):

- `Semua Gen (1 Formula)` — 1.208 baris, dipakai model yang cuma punya 1 formula
- `Model/Tahun Lain` — 162 baris, fallback
- `Gen N (YYYY-YYYY)` — mis. `Gen 1-2 (2003-2020)`, `Gen 3 (2021-2026)`
- gen bernama: `Gen 2 (Reborn)`, `Gen 3 (Zenix)`

Kosakata Warna (255 label): `Abu-abu`, `Hitam`, `Hijau Army`, `Merah`, `Biru Benhur`,
`Silver`, `Orange`, plus warna strip `Elite/Epic/Warrior + Abu/Merah/Biru` dan
`Strip 1/2/3 + warna`. Kosong ditulis literal `(tanpa warna)` / `(tanpa gen)`.

Modul `scripts/selaras_gen.py` memetakan label mentah -> label baku **per model**, urutan:
1. cocok persis
2. gen bernama (reborn/zenix/venturer/facelift)
3. **irisan tahun terbesar** — `Gen 3F (2016-2022)` -> label baku yang rentang tahunnya
   paling banyak beririsan
4. nomor gen sama
5. gagal -> `Model/Tahun Lain`

Kalau model cuma punya 1 label baku (mis. Honda BRV = `Semua Gen (1 Formula)`), **semua**
varian jatuh ke situ. Hasil: 94,9% unit dapat label baku, 5,1% jadi `Model/Tahun Lain`.

### LAPORAN v5 — struktur sama persis dgn file asli, angka gabungan (2026-08-05)

User minta: hitung langsung gabungan (tanpa kolom terpisah per marketplace), dan buatkan
sheet `Detail Gen & Warna` seperti file asli. Hasil: `MOBIL_TERLARIS_GABUNGAN_v5.xlsx`.

**Struktur sheet `Top 300 Mobil` = 66 kolom, 4 blok** (merged cell di baris 4 persis
seperti aslinya: `I4:AA4`, `AB4:BC4`, `BD4:BJ4`, `BK4:BN4`):

| Blok | Kolom | Isi |
|---|---|---|
| dasar | 1–8 | No, Nama Mobil, Total Kuantitas, % Kuantitas, Total Penjualan, % Nilai, Jenis Cover Digabung, Rata-rata Terjual/Hari |
| WARNA POLOS | 9–27 | 6 warna + Total + 6 % + 6 rata/hari (19 kolom) |
| DETAIL STRIP | 28–55 | 9 kombinasi + Total + 9 % + 9 rata/hari (28 kolom) |
| DETAIL PREMIUM | 56–62 | Abu-abu, Silver + Total + 2 % + 2 rata (7 kolom) |
| DETAIL EXCLUSIVE | 63–66 | Abu-abu + Total + % + rata (4 kolom) |

Aturan yang diverifikasi ulang dari file asli (berhasil merekonstruksi Avanza v1 persis):
- `Total Warna Polos` = jumlah **6 kolom warna yg ditampilkan saja** — Silver dll TIDAK masuk
- semua `%` dibagi **Total Kuantitas model ybs**, bukan grand total
- `Strip 1/2/3` = **Epic/Elite/Warrior** berturut-turut
- blok Premium/Exclusive adalah **subset** dari Warna Polos, blok Strip **di luar** Warna Polos

### BUG PENTING: urutan penentuan jenis cover

Metodologi v1 menulis: *"Tipe cover dari penanda WARNA (Elite/Warrior->Strip, Silver->Premium,
Transparan->Transparan) **lalu** tier di nama produk."* — **warna dulu, baru nama produk.**
Script-ku semula membaca tier dari nama produk saja, akibatnya **1.362 unit salah tier**.

Penyebabnya nyata di listing: banyak produk **dinamai "Reguler" tapi variannya warna Strip**, mis.
`Cover Mobil Suzuki Ertiga Reguler` varian `Epic Abu` (239 unit),
`Cover Mobil Honda Civic Reguler` varian `Epic Merah` (151 unit),
`Cover Mobil Toyota Calya Reguler` varian `Elite Abu` (245 unit).
Bahkan **tidak ada satu pun** produk TikTok yang namanya mengandung kata Strip/Elite/Epic/Warrior —
100% penanda tier ada di warna. Efeknya: Total Strip 3.315 -> **4.677**.

Fungsi `jenis_cover(nama, warna, tier_nama)` di `scripts/laporan_v5.py` sekarang menerapkan
urutan yang benar. Juga ada `rapikan_warna_strip()`: `Elite Abu-abu` -> `Elite Abu`,
`Strip 1 Abu-abu` -> `Strip 1 Abu` (konvensi laporan pakai nama warna pendek).

### Angka final v5

| | unit | nilai |
|---|---|---|
| model dirinci (321 model) | 36.290 | Rp 10.569.361.081 |
| ekor panjang v1 tak dirinci | 167 | Rp 47.335.792 |
| **GRAND TOTAL** | **36.457** | **Rp 10.616.696.873** |

**201,42 unit/hari** · 1.410/minggu · 6.043/bulan · harga rata-rata Rp 291.212/unit.

Komposisi: Reguler 30.345 · Strip 4.677 · Premium 520 · Exclusive 429 · Transparan 319.

### File hasil

`MOBIL_TERLARIS_GABUNGAN_v5.xlsx` — **FILE PATOKAN**, menggantikan v2/v3/v4.
3 sheet meniru file asli: `Top 300 Mobil` (321 model x 66 kolom), `Detail Gen & Warna`
(3.330 baris), `Metodologi`. Diverifikasi: zip utuh, 0 kesalahan konsistensi
(Total Warna Polos, Total Strip, %, rata-rata/hari), 0 rumus menyimpang.

`MOBIL_TERLARIS_v4_final.xlsx` (versi lama, kolom masih dipisah per marketplace) — Gen & Warna sudah selaras
dgn laporan, 561 baris berlabel `Model/Tahun Lain`, 0 warna kosong.
Struktur sheet sama dgn v3 di bawah ini.

`MOBIL_TERLARIS_v3_TikTok_3toko.xlsx` — **file BARU**, file asli tidak disentuh.
4 sheet: `Top Model Gabungan` (321 model; kolom unit dipisah Shopee+Lazada vs TikTok,
plus rincian TikTok UA/OP/SP), `Detail TikTok` (3.754 baris), `Ringkasan per Toko`,
`Ringkasan & Catatan`. Diverifikasi: zip utuh, 0 rumus menyimpang, kolom per-toko
jumlahnya konsisten dgn kolom TikTok, autofilter dipasang setelah baris terisi.
(v2 `MOBIL_TERLARIS_v2_plus_TikTok.xlsx` = versi Undercover saja, sudah digantikan v3.)

### Akurasi estimasi sebelumnya

Estimasi berbasis ukuran file ternyata cukup akurat: prediksi OP ~1.072 (aktual 1.210),
SP ~1.016 (aktual 1.122). Metode "unit per MB file mentah" layak dipakai lagi
untuk menaksir lubang data.

### KOREKSI 2026-08-05 — klaim "UC Shopee Maret belum masuk" itu KELIRU

**Ini kesalahanku, dan polanya penting untuk diingat.** Aku menyimpulkan Maret belum
terhitung karena file di **Google Drive** berekstensi `.zip`. Padahal Metodologi jelas
menyebut script jalan dari folder **LOKAL** `C:\Users\OWNER\Downloads\Sales`. Isi folder
lokal tidak bisa disimpulkan dari isi Drive — user meng-upload zip ke Drive, tapi di lokal
sudah ter-extract jadi `.xlsx`. **Ekstensi file di Drive bukan bukti tentang apa yang dibaca script.**

User mengirim file Maret aslinya (2 part, 5.881 baris, 4.479 unit mobil, Rp 1.401.748.230).
Empat uji dijalankan, semuanya menyimpulkan **Maret SUDAH termasuk di v1**:

1. **Uji (model)**: 0 dari 151 model punya kuantitas Maret melebihi total v1.
2. **Uji (model, warna)**: 0 pelanggaran nyata (2 temuan ternyata artefak parsing
   kolom `Nama Variasi` yang urutannya beda).
3. **Uji musiman** (acuan: musiman TikTok UC yang datanya lengkap 6 bulan —
   Maret = 24,3% dari 6 bulan, memang bulan puncak/Lebaran):
   porsi Maret aktual 16,4% dari v1. Prediksi hipotesis "sudah termasuk" meleset 13,7%,
   hipotesis "belum termasuk" meleset 32,5%. **"Sudah termasuk" menang telak.**
4. **Uji silang baris motor & batal**: Maret punya 140 baris motor -> ekstrapolasi 6 bulan
   = 577 vs 767 tercatat di diagnostik (konsisten). Maret 1.058 baris batal ->
   ekstrapolasi = 5.655 vs 5.184 tercatat (meleset 9%, konsisten).

**Jangan tambahkan Maret ke laporan — itu akan menghitung ganda.**
Angka final tetap **36.290 unit / 200,5 per hari**, bukan 223.

**Pelajaran umum**: uji granular (model, gen, warna) TIDAK BISA dipakai membandingkan
laporan vs data mentah, karena label Gen di laporan sudah dinormalisasi
("Gen sudah disetarakan dgn list Undercover terkini") sehingga tidak pernah cocok dengan
label mentah. Yang bisa dibandingkan: nama model dan warna.

### Lubang tersisa

- Lazada Otonation & Otoprotection: folder tidak ada di Drive
- TikTok Otonation: folder tidak ada di Drive
- Lazada umumnya cuma 160 baris — kemungkinan export belum lengkap
- (UC Shopee Maret **BUKAN** lubang — sudah termasuk)

## Skrip

`scripts/cek_penjualan.py`, `cek_penjualan2.py`, `estimasi_lubang.py`,
`baca_tiktok.py`, `tiktok_rinci.py`, `tiktok_final.py`, `nama_tiktok.py` (parser nama),
`gabung_tiktok2.py` (pembuat laporan v2).

## Tindak lanjut yang belum dikerjakan

- ~~Perbaiki reader TikTok~~ **SELESAI 2026-08-05** (`scripts/baca_tiktok.py` +
  `nama_tiktok.py`), tapi baru toko **Undercover**. Masih perlu export TikTok
  Otoprotection & Smartprotection.
- Extract `Order.all.20260301_20260331.zip` (UC Shopee Maret) jadi xlsx.
- Lengkapi export Lazada + TikTok untuk Otonation, Lazada untuk Otopro.
- Kalau mau angka **produksi** (bukan penjualan): masukkan motor + produk non-cover +
  order luar marketplace.


## BUG DITEMUKAN 2026-08-05 (sore) — "warna" berupa tahun (mis. "2023") sudah ADA DI FILE ASLI

User spot-check di sheet `Detail Gen & Warna` v5, Honda Brio: kolom Warna berisi nilai
aneh spt `2023`, `2018-2023`, `2012-2016`, `2016-2018`, `Gen 2F (2023)` — bukan nama warna.

**Dikonfirmasi dgn bukti, BUKAN dugaan**: dibuka file `Mobil_Terlaris.xlsx` versi 23 Juli
(satu-satunya salinan lama yg masih ada di disk setelah container reset) — sheet
`Detail Gen & Warna`-nya **SUDAH** berisi 327 baris dgn pola sama di SELURUH model, termasuk
PERSIS baris Honda Brio yg sama dgn screenshot user: `2023` (qty 4), `Gen 2F (2023)` (qty 5),
`2012-2016` (qty 1), `2016-2018` (qty 1), `2018-2023` (qty 1), dll.

**Kesimpulan: ini bug di PIPELINE ASLI milik user** (script yg jalan dari folder lokal
`C:\Users\OWNER\Downloads\Sales`, dibuat 2026-07-22 16:59) — **bukan sesuatu yg
diperkenalkan Claude**. Untuk sebagian order (kemungkinan varian yg cuma py1 axis: warna
ATAU tahun, tanpa "Gen" sbg prefix — sering terjadi pada Transparan yg memang tidak
punya opsi warna), kolom Warna di pipeline asli itu keisi teks tahun/generasi.

**Tapi Claude IKUT ANDIL**: `scripts/selaras_gen.py` (`Penyelaras.warna_baku`) membangun
kosakata warna "valid" dgn men-scan kolom Warna sheet Detail v1 apa adanya — termasuk
nilai buggy ini — jadi saat TikTok dimerge, nilai serupa (mis. varian TikTok yg juga cuma
berisi tahun) ikut lolos tanpa divalidasi. **Seharusnya divalidasi**: kalau isi kolom Warna
cocok pola tahun murni (`^\d{4}$`) / rentang tahun (`^\d{4}\s*-\s*\d{4}$`) / diawali
"Gen", itu BUKAN warna — harus ditandai `(tanpa warna)`.

### Perbaikan yang perlu dilakukan di `selaras_gen.py` / `laporan_v5.py`
Tambah validasi: kalau nilai Warna hasil parsing cocok pola tahun/gen, paksa jadi
`(tanpa warna)` (dan kalau itu memang info generasi yg berguna, arahkan ke kolom Gen
lewat `SEL.gen()`, bukan dibiarkan nyasar ke kolom Warna).

### Container reset lagi (2026-08-05 sore)
Local git checkout & folder upload sesi ini kereset ke state 27 Juli — file2 upload hari
ini (MOBIL_TERLARIS asli fbc7083b, 3 file TikTok, 2 file Maret) HILANG dari disk. Scripts
aman (sudah di git, dipulihkan via `git reset --hard origin/<branch>`). Perbaikan v5 di
atas BELUM dieksekusi ulang — perlu user upload ulang file2 sumber dulu.
