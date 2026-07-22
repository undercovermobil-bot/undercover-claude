# Matriks Mobil Terlaris (Top 300) — sampai Gen & Warna

Script: [`buat_matriks_terlaris.py`](buat_matriks_terlaris.py) — **tidak butuh `pip install` apa pun.**
Hanya pakai library bawaan Python (baca & tulis `.xlsx` sendiri lewat `zipfile`/`xml`).
Kalau `pip` di komputermu bermasalah/offline, script ini tetap jalan asal Python-nya ada.

Membangun laporan **mobil terlaris** (Top 300 model) dari data order mentah
**Shopee / TikTok / Lazada** untuk **semua toko** (Undercover, Otonation,
Otopro, Smartpro), tapi lebih detail dari file `MOBIL TERLARIS` lama:
ada rincian sampai **generasi (gen)** dan **warna**.

## Kenapa script, bukan file jadi?

Data mentahnya puluhan file @1–2 MB — baik yang di Google Drive maupun yang
di folder lokal seperti `Downloads\Sales`. File sebesar itu tidak bisa
diproses langsung oleh asisten cloud, jadi pemrosesan dilakukan lokal di
komputermu tempat file-nya berada. Bonus: **bisa dipakai ulang tiap bulan**
— cukup taruh file order baru, jalankan lagi.

## Cara pakai — Windows, paling gampang (dobel klik)

1. Salin 2 file ini ke folder data sales-mu (mis. `C:\Users\OWNER\Downloads\Sales`):
   - `buat_matriks_terlaris.py`
   - `jalankan_matriks.bat`
2. Dobel-klik **`jalankan_matriks.bat`**.
3. Kalau diminta path folder, Enter saja (default sudah diarahkan ke
   `Downloads\Sales`) atau ketik path foldernya.
4. Tunggu sampai muncul "Selesai" → file
   `MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx` muncul di folder yang sama.

Kalau muncul pesan Python tidak ditemukan: buka **Microsoft Store**, cari
**"Python 3"**, install (gratis, tanpa perlu jadi admin), lalu jalankan
`.bat`-nya lagi.

## Cara pakai — lewat Command Prompt / PowerShell

```bat
cd "C:\path\ke\scripts"
python buat_matriks_terlaris.py "C:\Users\OWNER\Downloads\Sales"
```

Kalau `python` tidak dikenali, coba `py` sebagai gantinya:

```bat
py buat_matriks_terlaris.py "C:\Users\OWNER\Downloads\Sales"
```

Output default: **`MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx`** (ditulis di folder
tempat kamu menjalankan perintah). Ganti nama/lokasi output:
`python buat_matriks_terlaris.py "<folder data>" "<output.xlsx>"`.

Struktur folder yang dipindai (otomatis, rekursif — nama subfolder bebas):

```
Data Sales Jan - Jun 2026/
  Undercover/  Shopee|TikTok|Lazada/  *.xlsx (atau *.zip)
  Otonation/   Shopee/ ...
  Otopro/      Shopee|TikTok/ ...
  Smartpro/    Shopee|TikTok|Lazada/ ...
```

## Isi output (3 sheet)

| Sheet | Isi |
|---|---|
| **Top 300 Mobil** | Ranking per model (No, Nama Mobil, Total Kuantitas, %, Total Penjualan, %, Jenis Cover Digabung, Jumlah Varian/SKU) **+ matriks warna polos terintegrasi**: satu kolom per warna (diurut dari terlaris) + kolom "Total Warna Polos", lalu baris **TOTAL** dan baris **% tiap warna** (dari total warna polos). Strip/Elite/Epic/Warrior **dikeluarkan** dari kolom warna; Premium/Exclusive/Transparan ikut (Silver = Premium) |
| **Detail Gen & Warna** | Tiap baris = Model + Jenis Cover + Gen + Warna, dengan Kuantitas, % dari model, Total Penjualan, Jumlah SKU |
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
