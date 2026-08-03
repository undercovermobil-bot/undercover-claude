# HPP per Merk (varian Reguler)

Script pembuat workbook **`DATA UC HPP per Merk (Reguler).xlsx`** — 1 sheet per merk mobil,
isinya format kolom Sheet3 `DATA_UC_HPP.xlsx` (A s/d AC + formulanya), tapi barisnya diisi
model-model mobil per merk dari file SKU Price Tracking.

Dibuat 2026-08-03 atas permintaan user. File xlsx-nya sendiri **tidak masuk git** (lihat
`.gitignore`) — tinggal di Google Drive / dikirim langsung ke user. Yang disimpan di sini
cuma scriptnya, supaya bisa dibuat ulang kalau harga Shopee sudah berubah.

## Aturan yang dipakai

| Hal | Keputusan |
|---|---|
| Baris | 1 baris = 1 model (bukan per generasi). Total 453 baris di 76 sheet merk. |
| Varian | **Reguler saja.** Premium / Exclusive / Transparan / Strip tidak dimasukkan. |
| Kolom C (Pcs/Roll ACTUAL) | Dikosongkan semua — diisi manual oleh user. |
| Kolom I (Margin) | Dikosongkan (di Sheet3 aslinya juga kosong). |
| Kolom J (Harga Jual ACTUAL) | Harga listing Shopee toko Undercover Autocare, varian warna Reguler. Kalau modelnya tidak ada di Shopee → dikosongkan. |
| Konstanta B, E, F, H + semua persen | Ikut baris contoh `Avanza Reguler` di Sheet3 (Harga Kain 715.000, SDM 16.500, Tali Rit 20.000, Iklan 18.000, Adm 10,45%, GOE 5,5%, PX 4,5%, SX 2,5%, Affiliate **5%**, Event Toko 5,5%). |

Catatan soal Affiliate: di Sheet3 nilainya 5% pada baris yang harganya terisi
(Avanza Reguler & Kia Picanto) dan 8% pada baris sisanya. Karena user menunjuk
baris **Avanza Reguler** sebagai contoh, dipakai **5%**.

## Sumber data

1. **Daftar merk & model** — `SKU, Price, Tracking Cover Mobil.xlsx`
   (76 sheet merk). Diambil `Nama Produk` unik yang `Kategori Produk = "Reguler"`.
2. **Harga** — `Informasi Penjualan Shopee Undercover 1-5 (SYNCED v3).xlsx` di Google Drive
   (export Mass Update Shopee). Yang dibaca: listing berjudul
   `Undercover Autocare - Cover Mobil <model> Reguler`, lalu **hanya** varian dengan warna
   Reguler (Abu-abu / Hitam / Merah / Biru Benhur / Hijau Army).
   Varian Strip (Elite / Epic / Warrior) ada di listing yang sama tapi harganya
   ±Rp60.000 lebih mahal — sengaja tidak dipakai.
3. **Format sel & formula** — `DATA_UC_HPP.xlsx` Sheet3.

## Penyesuaian formula (dan alasannya)

Karena kolom C dikosongkan, formula asli `=B/C` akan jadi `#DIV/0!` di semua baris, dan
errornya menular ke G, Y, Z, AC. Jadi:

| Kolom | Sheet3 asli | Dipakai di sini |
|---|---|---|
| D | `=B2/C2` | `=IFERROR(B2/C2,"")` |
| G | `=SUM(D2:F2)` | `=IF(D2="","",SUM(D2:F2))` |
| Y | `=G2+H2+W2` | `=IF(G2="","",G2+H2+W2)` |
| Z | `=J2-Y2` | `=IF(Y2="","",J2-Y2)` |
| AC | `=(J2+AA2)-Y2` | `=IF(Y2="","",(J2+AA2)-Y2)` |

Kolom G ikut dijaga karena tanpa itu HPP akan menampilkan **36.500** (cuma SDM + tali rit,
karena `SUM` mengabaikan sel teks) — angka yang kelihatan wajar padahal salah.
Isi perhitungannya sendiri tidak diubah. Begitu kolom C diisi, semuanya jalan seperti Sheet3.

Kolom lain sama persis: `L=J*K`, `N=M*J`, `P=J*O`, `R=Q*J`, `T=J*S`, `V=U*J`,
`W=L+N+P+R+T+V`, `X=J-W`, `AA=J*10%`, `AB=J+AA`.

## Pencocokan nama model

334 dari 453 model namanya identik dengan listing Shopee. Sisanya beda penulisan.
Sesuai keputusan user: **cocokkan yang jelas saja**, yang meragukan dikosongkan.

- Dicocokkan (lihat `ALIAS` di script): `Honda BR-V` → `Honda BRV`,
  `Daihatsu All New Ayla` → `Daihatsu Ayla`, `Mitsubishi Mitsubishi Kuda` → `Mitsubishi Kuda`,
  `Mazda CX5` → `Mazda CX-5`, `Nissan Kicks e-POWER` → `Nissan Kicks`,
  `Toyota Kijang Buaya/Doyok/Super/Kapsul` → `Toyota Kijang`, dll.
- Sengaja **tidak** dicocokkan (lihat `MERAGUKAN`): `Toyota Corolla Altis`,
  `Suzuki Grand Vitara` (+ Hybrid, e VITARA), `Suzuki Carry Futura`, `Kia Sedona`,
  `Nissan Livina (All New)`.

Hasil akhir: **369 model dapat harga, 84 dikosongkan.** Daftar lengkap yang dikosongkan
ada di sheet `CATATAN` dalam workbook.

## Menjalankan ulang

```bash
pip install openpyxl
# taruh 5 file Informasi Penjualan Shopee di ./shopee/uc1.xlsx .. uc5.xlsx
# sesuaikan SKU_SRC di build_hpp_per_merk.py
python3 build_hpp_per_merk.py
python3 verify.py
```

## Verifikasi

`recalc.py` (LibreOffice) **tidak bisa dipakai** di container sesi ini — `soffice` gagal
memuat file xlsx apa pun, termasuk file uji 3 sel. Gantinya `verify.py` membaca formula apa
adanya dari workbook hasil lalu mengevaluasinya sendiri:

1. Skenario C kosong → memastikan tidak ada `#DIV/0!` dan D/G/Y/Z/AC benar-benar kosong.
2. Cek silang tiap baris berharga: `W` harus 33,45% dari J, `X = J-W`, `AB = J*1,1`.
3. Uji silang ke angka yang sudah diketahui: baris `Toyota Avanza` diisi C=5 & J=295.000
   harus menghasilkan angka identik dengan baris `Avanza Reguler` Sheet3
   (HPP 179.500, Cair MP 196.322,5, Margin Bersih 28.322,5).

Status terakhir: 453 baris, 369 berharga, semua lolos.

Karena openpyxl menulis formula tanpa cached value, angka baru muncul saat file dibuka di
Excel/Google Sheets (langsung dihitung ulang otomatis).
