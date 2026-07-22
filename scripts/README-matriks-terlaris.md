# Matriks Mobil Terlaris (Top 300) — sampai Gen & Warna

Script: [`buat_matriks_terlaris.py`](buat_matriks_terlaris.py)

Membangun laporan **mobil terlaris** (Top 300 model) dari data order mentah
**Shopee / TikTok / Lazada** untuk **semua toko** (Undercover, Otonation,
Otopro, Smartpro), tapi lebih detail dari file `MOBIL TERLARIS` lama:
ada rincian sampai **generasi (gen)** dan **warna**.

## Kenapa script, bukan file jadi?

Data mentahnya puluhan file @1–2 MB. Sesuai `CLAUDE.md`, file besar tidak bisa
ditarik lewat tool/MCP (mentok batas ukuran konten). Jadi pemrosesan dilakukan
lokal di komputer yang folder Drive-nya tersinkron. Untungnya jadi **bisa
dipakai ulang tiap bulan** — cukup taruh file order baru, jalankan lagi.

## Cara pakai

```bash
# 1. Sekali saja: pasang library
pip install openpyxl

# 2. Jalankan, arahkan ke folder data
python buat_matriks_terlaris.py "C:\path\ke\Data Sales Jan - Jun 2026"
```

Atau taruh script ini di dalam folder `Data Sales Jan - Jun 2026` lalu:

```bash
python buat_matriks_terlaris.py
```

Output default: **`MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx`** (buka di Excel / Google Sheets).
Ganti nama output: `python buat_matriks_terlaris.py "<folder>" "<output.xlsx>"`.

Struktur folder yang dipindai (otomatis, rekursif — nama subfolder bebas):

```
Data Sales Jan - Jun 2026/
  Undercover/  Shopee|TikTok|Lazada/  *.xlsx (atau *.zip)
  Otonation/   Shopee/ ...
  Otopro/      Shopee|TikTok/ ...
  Smartpro/    Shopee|TikTok|Lazada/ ...
```

## Isi output (4 sheet)

| Sheet | Isi |
|---|---|
| **Top 300 Mobil** | Ranking per model (gaya file lama): No, Nama Mobil, Total Kuantitas, %, Total Penjualan, %, Jenis Cover Digabung, Jumlah Varian/SKU |
| **Detail Gen & Warna** | Tiap baris = Model + Jenis Cover + Gen + Warna, dengan Kuantitas, % dari model, Total Penjualan, Jumlah SKU |
| **Matriks Warna** | Crosstab: baris = Model + Gen, kolom = Warna, isi = kuantitas terjual (+ total baris/kolom) |
| **Metodologi** | Definisi, filter, dan **diagnostik** (jumlah baris terbaca per marketplace, yang dilewati, dll) — **cek sheet ini dulu** untuk memastikan angka wajar |

## Definisi & asumsi (bisa diubah di bagian `KONFIGURASI` dalam script)

- Cakupan: semua toko × Shopee/TikTok/Lazada, periode sesuai file di folder.
- Hanya **mobil** (Cover Mobil); motor tidak masuk ranking.
- Status **batal / belum bayar / refund / retur** dikeluarkan (bukan penjualan).
- **Kuantitas** = qty terjual − qty diretur.
- **Total Penjualan** = nilai net setelah diskon
  (Shopee `Subtotal Pesanan`, TikTok `SKU Subtotal After Discount`, Lazada `paidPrice`).
- Model digabung lintas toko/marketplace berdasarkan nama model pada listing.
- **Tipe cover** ditentukan dari penanda warna (Elite/Warrior → Strip, Silver → Premium,
  Transparan → Transparan), lalu tier di nama produk (Reguler/Premium/Exclusive).

Parsing sudah menangani 3 format berbeda (Shopee/TikTok/Lazada), format angka
Indonesia vs internasional (`307.490` vs `287000.00`), variasi berlabel
(`Warna:...,Model:...`) maupun polos (`Abu-abu,Gen 1-3 (2002-2022)` /
`Gen 1F (2016-2018),Silver`), serta file `.zip`.

> Kalau ada baris yang nama modelnya tidak terbaca, jumlah & contohnya muncul di
> sheet **Metodologi** supaya gampang ditelusuri.
