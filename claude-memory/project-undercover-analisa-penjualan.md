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

## Skrip

`scripts/cek_penjualan.py`, `scripts/cek_penjualan2.py`, `scripts/estimasi_lubang.py`.

## Tindak lanjut yang belum dikerjakan

- Perbaiki reader TikTok (format "Semua pesanan" beda dari Shopee `Order.all.*`) lalu
  generate ulang laporan.
- Extract `Order.all.20260301_20260331.zip` (UC Shopee Maret) jadi xlsx.
- Lengkapi export Lazada + TikTok untuk Otonation, Lazada untuk Otopro.
- Kalau mau angka **produksi** (bukan penjualan): masukkan motor + produk non-cover +
  order luar marketplace.
