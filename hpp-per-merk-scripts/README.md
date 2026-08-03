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

Sebagian besar model namanya identik dengan listing Shopee. Sisanya beda penulisan.
Sesuai keputusan user: **cocokkan yang jelas saja**, yang meragukan dikosongkan.

- Dicocokkan (lihat `ALIAS` di script): `Honda BR-V` → `Honda BRV`,
  `Mitsubishi Mitsubishi Kuda` → `Mitsubishi Kuda`,
  `Mazda CX5` → `Mazda CX-5`, `Nissan Kicks e-POWER` → `Nissan Kicks`,
  `Toyota Kijang Buaya/Doyok/Super/Kapsul` → `Toyota Kijang`,
  `Isuzu Mux` ↔ `Isuzu MU-X`, `Nissan Livina X-Gear` ↔ `Nissan Livina XGear`, dll.
- Sengaja **tidak** dicocokkan (lihat `MERAGUKAN`): `Toyota Corolla Altis`,
  `Suzuki Grand Vitara` (+ Hybrid, e VITARA — beda dari `Suzuki Vitara`, lihat di bawah),
  `Suzuki Carry Futura`, `Kia Sedona`, `Nissan Livina (All New)`.

Daftar lengkap model tanpa harga ada di sheet `CATATAN` dalam workbook.

## Model tambahan dari Shopee (tidak ada di file master SKU tracker)

User bertanya "yang dari list produk ecommerce sudah ada semua disitu?" — audit balik
2026-08-03 menjawab: **belum**. Dari 414 model Reguler unik di listing Shopee toko
Undercover Autocare, 63 di antaranya tidak ketemu padanan apapun di file master SKU
tracker (bukan salah cocok nama — modelnya memang tidak ada baris sama sekali).

- **2 ternyata cuma beda penulisan** → dicocokkan lewat `ALIAS` ke baris yang sudah ada
  (`Isuzu Mux`/`MU-X`, `Nissan Livina X-Gear`/`XGear`), bukan baris baru.
- **61 genuinely belum tercatat di master** → atas persetujuan user, ditambahkan sebagai
  baris baru lewat `MODEL_TAMBAHAN_DARI_SHOPEE`. Nama & harga baris ini **sepenuhnya dari
  Shopee**, bukan dari SKU tracker (mis. Audi cuma tercatat A4/A8 di master, padahal
  Shopee sudah jual A3/A5/A6/A7/Q3/Q5/Q7/Q8/R8/RS4 Avant/RS5/TT Coupe juga; pola sama di
  Mercedes-Benz varian EQA/EQB/EQE/EQS/AMG GT, Porsche Macan/718 Cayman, Jeep
  Gladiator/Renegade, Kia Cerato/EV6/Sorento, dll — daftar lengkap 24 brand di
  `MODEL_TAMBAHAN_DARI_SHOPEE`).
- Ditandai visual di tiap sheet: **kolom A miring + fill kuning**, supaya kelihatan
  langsung baris mana yang provenance-nya beda dari baris master lain. Daftar lengkap +
  harga juga ada di section "MODEL TAMBAHAN DARI SHOPEE" di sheet `CATATAN`.

Perhatikan `Volkswagen Beetle` vs `Volkswagen New Beetle` — kelihatannya mirip pola
Daihatsu (nama beda per era), tapi **sengaja TIDAK digabung**: keduanya mobil beda bentuk
bodi (New Beetle = desain retro 1997+, beda total dari Beetle klasik), dan Shopee sendiri
menjualnya sebagai 2 listing terpisah dengan harga beda (290rb vs 292rb — bukan identik
seperti kasus Daihatsu yang harganya sama persis di kedua nama).

Total baris naik dari 449 → **510** (61 baris baru). Yang dapat harga naik dari 365 → 426.

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

1. Tidak boleh ada 2 nama produk di sheet yang sama yang keliatan model yang sama
   (`cek_tidak_ada_duplikat_generasi` — lihat kasus Daihatsu di bawah; ada allowlist
   eksplisit utk pasangan yang mirip pola tapi terbukti beda produk, mis. VW Beetle/New Beetle).
2. `CATATAN` sheet tidak boleh punya elemen `<f>` (formula) sama sekali — lihat bug di bawah.
3. Skenario C kosong → memastikan tidak ada `#DIV/0!` dan D/G/Y/Z/AC benar-benar kosong.
4. Cek silang tiap baris berharga: `W` harus 33,45% dari J, `X = J-W`, `AB = J*1,1`.
5. Uji silang ke angka yang sudah diketahui: baris `Toyota Avanza` diisi C=5 & J=295.000
   harus menghasilkan angka identik dengan baris `Avanza Reguler` Sheet3
   (HPP 179.500, Cair MP 196.322,5, Margin Bersih 28.322,5).

Status terakhir: 510 baris, 426 berharga, semua lolos.

Karena openpyxl menulis formula tanpa cached value, angka baru muncul saat file dibuka di
Excel/Google Sheets (langsung dihitung ulang otomatis).

## Bug yang pernah bikin Excel minta "repair" (sudah diperbaiki)

Dua versi awal file ini memicu dialog Excel "We found a problem with some content... do you
want us to recover". Log perbaikan Excel (`Removed Records: Formula from
/xl/worksheets/sheet1.xml part` — sheet1 = `CATATAN`) memastikan penyebab sebenarnya:

Di sheet `CATATAN`, teks dokumentasi seperti `=IFERROR(B/C,"")` dan `=IF(D="","",SUM(D:F))`
ditulis apa adanya sebagai penjelasan formula. Tapi openpyxl **otomatis** menganggap string
manapun yang diawali `=` sebagai formula sungguhan (`Cell._bind_value`,
`value.startswith("=")` → `data_type='f'`), lalu menulisnya sebagai elemen `<f>` di XML.
Karena "B/C" dan "D:F" di situ bukan referensi sel yang valid (tanpa nomor baris — itu cuma
teks penjelasan generik, bukan formula per-baris), Excel mendeteksinya sebagai formula cacat
dan membuangnya saat "repair".

Fix (di `tulis_catatan()`):
1. Teks dokumentasi diganti jadi `"Formula: IFERROR(...)"` dst — tidak lagi diawali `=`.
2. Sebagai jaring pengaman, `tulis()` sekarang mengecek: kalau suatu value string diawali
   `=`, paksa `sel.data_type = "s"` setelah assignment supaya openpyxl tidak pernah
   menganggapnya formula, apapun isinya.
3. `verify.py` menambahkan `cek_catatan_tanpa_formula()` yang membongkar XML mentah
   `CATATAN` dan gagal kalau ada elemen `<f>` di situ — supaya regresi serupa ketahuan
   otomatis, bukan nunggu laporan "file rusak" dari user lagi.

(Ada juga satu bug lebih kecil di iterasi pertama: sel kosong di `CATATAN` sempat ditulis
dengan `value=""`, yang oleh openpyxl diserialisasi sebagai `<c t="inlineStr" />` tanpa child
`<is>` — melanggar skema OOXML. Sudah ikut diperbaiki di `tulis()`: sel yang isinya kosong
sekarang dilewati total, tidak disentuh sama sekali.)
