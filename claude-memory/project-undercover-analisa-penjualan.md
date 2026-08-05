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

### File hasil

`MOBIL_TERLARIS_v2_plus_TikTok.xlsx` — **file BARU**, file asli tidak disentuh.
3 sheet: `Top Model Gabungan` (303 model, kolom unit dipisah Shopee+Lazada vs TikTok),
`Detail TikTok` (2.562 baris), `Ringkasan & Catatan`. Sudah diverifikasi: zip utuh,
0 rumus menyimpang, autofilter dipasang setelah baris terisi.

### Proyeksi setelah TikTok masuk

Sisa lubang: TikTok Otoprotection + Smartprotection (4 file di Drive), UC Shopee Maret (.zip),
Lazada OT/OP. Estimasi TikTok OP ~1.072 + SP ~1.016 + UC Maret ~4.160
-> **~40.400 unit -> ~223 unit/hari**. Klaim 200/hari **makin terkonfirmasi masuk akal**.

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
