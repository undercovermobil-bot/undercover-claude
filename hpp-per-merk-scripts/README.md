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

Total baris naik dari 449 → **506** (57 baris baru). Yang dapat harga naik dari 365 → 423.

## Menambahkan model itu ke file master (`tambah_model_ke_master.py`)

User minta model-model itu dimasukkan sekalian ke master. Sebelum menulis apa pun,
daftar "hilang" **diaudit ulang memakai KODE SKU, bukan nama produk** — dan itu
mengubah hasilnya:

- Listing Shopee **"Suzuki Vitara" ternyata = master "Suzuki Grand Vitara"** (SKU-nya
  `SZK-GVT`, dan `GVT` memang kode master untuk Grand Vitara). Secara nama kelihatan
  seperti 2 model berbeda; tanpa cek SKU ini akan jadi entri master duplikat sekaligus
  meninggalkan Grand Vitara tanpa harga. Sekarang masuk `ALIAS`, bukan model baru.
- `Honda City Hatchback` & `Mazda 323 Interplay` sempat keflag "hilang" oleh script
  audit karena script itu tidak tahu `ALIAS` — keduanya sudah tercakup.

Hasil akhir: **57 model ditambahkan, 7.572 baris baru** (69.480 → 77.052).

### Produk "Custom" dikecualikan

Instruksi user 2026-08-03: *"semua yang custom tidak usah di include"* — berlaku untuk
workbook HPP **dan** file master. Sejalan dengan aturan bisnis #4 (varian Custom → SKU
jangan ditebak) & #6 (produk luar-scope dikecualikan).

Yang kena: `Honda Civic FD Custom`, `Nissan Grand Livina Custom Roofbox`,
`Toyota Vios Custom`. Filternya berbasis **pola nama** (`\bcustom\b`, case-insensitive),
bukan daftar manual, supaya listing Custom baru ikut tersaring otomatis.

Master aslinya sudah dicek: tidak punya model bernama "Custom" sama sekali, jadi filter
ini cuma menyaring calon baris tambahan dari Shopee — tidak ada data master yang dibuang.

Listing Shopee lain yang mengandung kata "Custom" (`Toyota Calya Reguler Custom`,
`Maserati GranTurismo Reguler CUSTOM SPOILER`, `Toyota Triton Reguler CUSTOM Bumper...`)
memang tidak pernah terbaca sebagai model sejak awal — judulnya tidak berakhir dengan
kata tier, jadi tidak lolos parser.

### Label generasi yang ditolak (data listing Shopee-nya yang perlu dibetulkan)

| Model | Label di listing | Masalah |
|---|---|---|
| Isuzu D-MAX | `Gen Gen 2F 1 (2015-2` | Teksnya rusak/kepotong |
| Mercedes Benz EQA | `Gen 1F (2017-2022)` | EQA baru rilis 2021 |
| Mercedes Benz EQB | `Gen 1F (2017-2022)` | EQB baru rilis 2021 |
| Porsche Macan | `Gen 4 (2016-2024)` | Macan tidak punya Gen 4; rentangnya sama persis dengan 718 Cayman |

Ditolak supaya data keliru tidak menular ke master. Generasi lain dari model yang sama
tetap masuk.

### Struktur baris yang dibuat

Mengikuti pola **saudara sesheet** (bukan pola global) — komposisi kategori/warna
beda-beda antar merk. Contoh Audi A3 (mengikuti Audi A4/A8), per generasi:

| Toko | Strip | Reguler | Premium | Exclusive |
|---|---|---|---|---|
| Undercover Autocare | 9 | 5 | 2 | 1 |
| Otonation | 9 | 5 | 2 | 1 |
| Smartprotection | 9 | 5 | 2 | 1 |
| Otoprotection | 9 | 5 | 2 | 1 |

Aturan bisnis #1 (konsolidasi toko) diterapkan: baris Otonation memakai kode SKU `-UA-`,
baris Otoprotection memakai `-SP-`. Aturan #7 tetap dipatuhi — 4 baris toko terpisah,
tidak di-dedupe.

### Kode SKU — perlu direview

Master sendiri **tidak konsisten** soal kode model (`MBZ-ECL` untuk E Class tapi
`MBZ-CC` untuk C Class; `PEU-M206` pakai awalan M tapi `FER-488S` tidak). Jadi kode
untuk model baru digenerate dengan aturan deterministik + tabel override `KODE_MANUAL`
yang mengikuti tetangga sesheet, misalnya:

- `HYN-I20` (Grand i20) mengikuti `HYN-I10` (Grand i10)
- `HYN-IQ6` (Ioniq 6) mengikuti `HYN-IQ5` (Ioniq 5)
- `LDR-RRS` / `LDR-RRV` (Range Rover Sport/Velar) mengikuti `LDR-RR` / `LDR-RRE`
- `MBZ-VCL` (V Class) mengikuti `MBZ-BCL` / `MBZ-ECL` / `MBZ-GCL`
- `MCL-720` (720S) mengikuti `MCL-570` (570S)
- Ferrari tanpa awalan M (`FER-488G`) mengikuti `FER-488S`

Kode ini jadi identitas operasional permanen (dipakai BigSeller & listing 4 toko),
jadi **wajib direview user sebelum dipromosikan ke master asli.**

### Verifikasi (`verify_master.py`)

Dibaca ULANG dari disk — wajib, karena openpyxl bisa `save()` sukses tanpa error tapi
diam-diam tidak menulis yang diminta (lihat pelajaran bug `ws.cell(value=None)`).

1. Semua baris lama utuh, isi & urutannya tidak berubah.
2. Baris tambahan persis milik model baru, jumlahnya cocok dengan laporan.
3. Tidak ada baris identik ganda (proses multi-pass wajib dicek duplikasi).
4. Prefix SKU baru tidak menabrak model lama mana pun.
5. Kode toko & kategori di tiap SKU sesuai aturan konsolidasi.
6. Dalam 1 model+generasi, tiap (toko, kategori, warna) hanya muncul sekali.
7. Pasangan konsolidasi UA↔OT dan SP↔OP punya SKU identik.

Status: semua lolos.

### Catatan: master yang diberikan kehilangan Mercedes Benz EQE

Memory proyek mencatat EQE sudah dibuatkan di master 2026-07-11, tapi di file master
yang dipakai sesi ini EQE **tidak ada**. Fix lain dari 07-17 (BYD Atto 3, Geely EX2)
justru ada, jadi file ini memang versi terbaru — EQE-nya yang hilang entah di
regenerasi mana. Kebetulan EQE termasuk 57 model yang ditambahkan sekarang, jadi
gap-nya ikut tertutup. Perlu dicek apakah ada hasil kerja 07-11 lain yang ikut hilang.

## Versi 100 Terlaris (`build_top100_terlaris.py`)

`DATA UC HPP Top 100 Terlaris.xlsx` — permintaan user: format sama, tapi cuma 100
model mobil terlaris, jadi 1 sheet saja (bukan 76 sheet per merk).

**Sumber ranking**: `Mobil Terlaris.xlsx` (Google Drive, diupdate 2026-08-10), sheet
"Top 300 Mobil" — ranking penjualan REAL (qty net setelah retur, 4 toko x
Shopee/TikTok/Lazada), bukan asumsi/daftar manual.

Script ini **reuse langsung** fungsi-fungsi dari `build_hpp_per_merk.py`
(`baca_harga_shopee`, `baca_model_per_merk`, `ALIAS`, `tulis_sheet`, `norm`) supaya
100% konsisten dengan workbook per-merk — bukan re-implementasi logic.

### Resolusi nama ranking → baris master

Ranking pakai judul listing (kadang beda dari nama master), jadi tiap baris dicocokkan
lewat 2 lapis: (1) index nama master + reverse-`ALIAS` (nama gaya Shopee → nama
master), (2) tabel `RESOLUSI_MANUAL` utk kasus yang perlu verifikasi tambahan:

| Ranking | → Baris master | Bukti |
|---|---|---|
| Honda City / Honda City Sedan | Honda City Sedan | Generasi ranking (2002-2004, 2011-2013, dst) match Sedan, BUKAN Hatchback RS yang cuma py 1 generasi (2021-2026) |
| Mazda 2 | Mazda 2 Sedan | Generasi ranking (split 2007-2010, cutoff 2014-2019) match persis Sedan; Hatchback master gen-nya nyambung 2007-2014 |
| Kia Rio | Kia Rio Sedan | Generasi ranking (2005-2009, 2011-2016, 2016-2020) match persis Sedan |
| Mitsubishi Pajero | Mitsubishi Pajero Sport | Rentang tahun ranking (2008-2015, 2015-2026) = generasi Pajero Sport; Pajero klasik berhenti produksi ~2003 |
| Suzuki APV Arena / Suzuki APV | Suzuki APV Arena / Blind Van | "Suzuki APV" py literal value "Arena (2007-2022)" di kolom Gen-nya sendiri di data ranking |
| Mitsubishi Strada Triton | Mitsubishi Triton | Nama resmi berbeda, mobil sama |
| Daihatsu Gran Max PU | Daihatsu Gran Max Pick Up | "PU" = singkatan Pick Up |
| Honda City Hatchback | Honda City Hatchback RS | ALIAS sudah ada |
| Suzuki Carry Pickup | Suzuki Carry | Sudah dikonfirmasi via SKU sebelumnya |

Kasus **duplikat judul** (2 baris ranking, 1 model master) otomatis di-collapse jadi 1
baris — bukan didobel. **Bukan mobil** (3 produk aksesori/perawatan yang kebetulan
ikut ke-rank, judulnya diawali "Undercover Autocare -") dikecualikan otomatis. Karena
100 slot butuh diisi PENUH oleh mobil unik, script otomatis lanjut membaca ranking di
bawah #100 (sampai #110) buat mengisi slot yang gugur dari duplikat/non-mobil.

Hasil: 100/100 model dapat harga, 0 gagal cocok.

### Format

Sama persis 76-sheet version: kolom A-AC, kolom C dikosongkan (diisi manual user),
formula D/G/Y/Z/AC dijaga IFERROR/IF. **Baris diurutkan sesuai rank penjualan**
(#1 = paling laris di baris 2), bukan alfabetis — beda dari versi 76-sheet yang
ngikut urutan file SKU tracker.

## Versi 300 Terlaris (`build_top300_terlaris.py`)

`DATA UC HPP Top 300 Terlaris.xlsx` — lanjutan dari versi 100. User kirim sumber
ranking baru & minta diperluas ke 300 model.

**Sumber ranking berganti**: `MOBIL_TERLARIS_GABUNGAN.xlsx` (dikirim user 2026-08-19)
menggantikan `Mobil Terlaris.xlsx` yang dipakai versi 100. Gabungan
Shopee+Lazada+TikTok/Tokopedia, periode 1 Jan-30 Jun 2026 (181 hari, 36.457 unit,
Rp 10,6 M), 321 model dirinci — jauh lebih lengkap dari sumber lama (217 model,
sebagian besar cuma Shopee). Struktur kolom sama (No/Peringkat di kolom 1, Nama
Mobil di kolom 2), cuma baris data mulai row 6 (bukan row 5 di sumber lama).

**Hasil akhir: 292 model, BUKAN 300.** Sheet sumbernya sendiri "cuma" 321 baris
(walau namanya "Top 300 Mobil"), dan setelah dikurangi yang genuinely bukan model
unik tersendiri, 292 adalah batas maksimal yang valid — bukan kegagalan script,
levelnya sudah maksimal dari data yang ada:

| Alasan dikeluarkan | Jumlah |
|---|---|
| Duplikat judul (model sama, 2 ejaan listing beda) | ~21 |
| Bukan produk cover mobil (aksesori/perawatan, judul diawali nama toko) | 3 |
| Genuinely tidak ada di master — **sudah divalidasi sesi audit OP/SP sebelumnya**, bukan temuan baru (Chevrolet Estate Magnum, Hyundai Verna, Hummer H3, Toyota FJ Cruiser) | 4 |
| Ambigu, data ranking tidak cukup utk pilih kandidat (Suzuki Aerio Sedan vs Hatchback, Daihatsu Gran Max Minibus vs Pick Up — rentang tahun master identik) | 2 |
| Ada di master tapi cuma kategori Strip, tidak py varian Reguler (Volkswagen Kombi) | 1 |

Semua kasus di atas ada di sheet `CATATAN` dgn rank asli + alasan spesifik.

### 12 resolusi manual baru (di luar yg sudah ada di versi 100)

Ditemukan & diverifikasi (bukan tebakan) waktu data diperluas ke 321 baris:
`Toyota 86`→`Toyota GR 86`, `Mercedes E Class`→`Mercedes Benz E Class`,
`Toyota Altis`→`Toyota Corolla Altis` (**satu-satunya yg genuinely nambah baris baru** —
11 lainnya cuma duplikat judul dari model yg sudah kepakai lewat listing lain),
`Mitsubishi L300`→`Mitsubishi L300 Pickup`, `Volkkswagen Polo`→`Volkswagen Polo`
(typo di file sumber), `Aion Hyptec HT`→`GAC Aion Hyptec HT`, `Mazda CX30`→`Mazda CX-30`,
`Daihatsu Gran Max MB`→`... Minibus / Blind Van`, `Toyota Hardtop / Land Cruiser`→
`Toyota Land Cruiser` (generasi ranking 2021-2022 cuma cocok Land Cruiser J300, Hardtop
cuma py 1 generasi J40 1960-1985), dan **`Honda Fortuner`→`Toyota Fortuner`** — bug
salah-brand yang SUDAH DIKONFIRMASI di sesi audit OP/SP sebelumnya (listing salah tag
merek, mobilnya beneran Toyota Fortuner).

### Diagnostik baru: bedakan "tidak ada di master" vs "ada tapi bukan Reguler"

`resolusi_index_semua_kategori()` — index tambahan dari SEMUA baris master tanpa
filter Kategori. Kalau sebuah nama ranking gagal cocok ke index Reguler-only tapi
ADA di index semua-kategori ini, pesannya jadi eksplisit "ada di master tapi cuma
kategori non-Reguler" (kasus Volkswagen Kombi, cuma py varian Strip) — bukan
disamaratakan dgn "genuinely tidak ada" yang bisa bikin user salah simpul.

## Versi urutan gabungan (`build_top300_urutan_gabungan.py`)

`DATA UC HPP Top 300 Terlaris (urutan gabungan).xlsx` — instruksi user 2026-08-19:

> "Sesuaikan urutan di 100 pertamanya pakai yg terlaris 100 ini, kemudian selanjutnya
> hingga 300 an pakai file yg sebelumnya aku kirim, kalau ada list produk yg
> urutannya berbeda dengan 100 terlaris, taruh di setelah urutan nomor 100"

Artinya: posisi 1-100 **dikunci** memakai urutan dari `DATA UC HPP Top 100
Terlaris.xlsx` (dikirim user balik — versi lama, sumber `Mobil Terlaris.xlsx` 217
model), posisi 101+ lanjut dari ranking GABUNGAN (321 model), model yang sudah
kepakai di 100 pertama tidak didobel.

**Verifikasi sebelum digabung**: dicek eksplisit apakah semua 100 model dari file
top-100 lama benar-benar ada di list GABUNGAN (bukan asumsi) — hasilnya **overlap
100%, 0 model hilang**, meski urutannya beda-beda (mis. `Toyota Rush` #15 di
top-100 lama tapi #8 di GABUNGAN; `Honda BR-V` #13 vs #16). Karena overlap bersih,
penggabungan tidak perlu fuzzy-match tambahan.

Data (harga kolom J, formula) diambil dari **pipeline saat ini**
(`baca_harga_shopee`/`peta_harga_untuk`), bukan nilai beku di file top-100 lama —
supaya semua baris konsisten dengan koreksi yang sudah dilakukan sepanjang sesi.

Hasil: 292 baris total (100 dikunci + 192 lanjutan GABUNGAN), 288 dapat harga.

`build_top300_terlaris.py` di-refactor supaya logika resolusi ranking-nya
(`resolusi_ranking()`) & lookup harga (`peta_harga_untuk()`) bisa dipakai ulang
oleh script ini, bukan duplikasi kode.

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

1. Nama produk tidak boleh berisiko tampil terpotong di Excel
   (`cek_nama_produk_tidak_terpotong` — lihat bug tampilan di bawah).
2. Tidak boleh ada 2 nama produk di sheet yang sama yang keliatan model yang sama
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

## Bug tampilan: nama produk kepotong jadi "RS" / "(Hybrid)" (sudah diperbaiki)

User melaporkan sheet Honda punya baris bernama `RS` dan `(Hybrid)` — kelihatan seperti
data rusak / nama merk hilang. **Datanya sebenarnya benar** (`Honda Civic Sedan / RS`,
`Honda Prelude (Hybrid)`); yang salah cara Excel menampilkannya.

Penyebabnya kombinasi 4 hal yang diwarisi dari format Sheet3:

1. Kolom A lebarnya 17.86 karakter (Sheet3 aslinya isinya nama pendek, "Avanza Reguler")
2. `wrap_text=True` → nama panjang dipecah jadi 2 baris teks
3. Tinggi baris dikunci 15.75 → cuma muat 1 baris
4. Rata vertikal `bottom` → yang tampil justru potongan **TERAKHIR**

Jadi `Honda Civic Sedan / RS` tampil sebagai `/ RS`. Kena **100 nama di 40+ merk** —
semua Mercedes tampil `Class`, `Toyota Corolla Altis` → `Altis`, `Daihatsu Gran Max
Minibus / Blind Van` → `Van`.

Fix: kolom A `wrap_text` dimatikan dan lebarnya mengikuti nama terpanjang di sheet ybs
(min 17.86). `verify.py` menambahkan `cek_nama_produk_tidak_terpotong()` yang gagal
kalau wrap aktif lagi atau ada nama lebih panjang dari lebar kolomnya.

Catatan: 4 model di sheet Land Rover memang tidak memuat kata "Land Rover"
(`Range Rover`, `Range Rover Evoque/Sport/Velar`) — itu penamaan asli di master dan
Range Rover memang sub-merk Land Rover, jadi sengaja tidak diubah (mengubahnya akan
memutus kaitan ke master).

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

---

# Penyamaan SKU Mobil Kembar (badge engineering)

Script: `samakan_sku_kembar.py` → `verify_kembar.py` → `laporan_listing_kembar.py`

## Keputusan user (2026-08-19/20)

- Mobil kembar **berbagi 1 SKU** (bukan SKU sendiri-sendiri yang "disamakan formatnya").
- Prefix **Toyota yang menang** kalau grupnya lintas merk: "Rush+Terios jadi TYT-RSH".
- Alphard+Vellfire → `TYT-ALP`.
- Rocky **generasi awal (F70/F300) ≠ Rocky baru**: "opsi satu benar, tapi rocky yg
  generasi awal = feroza = taft gt".
- Jumlah kode generasi mengikuti **Total Formula (TF)** di Sheet2
  `Data_Mobil_Lebih_dari_1_Formula_2.xlsx`.

## Bukti pendukung: harga listing Shopee (Reguler termurah)

| Grup | Harga |
|---|---|
| Avanza = Xenia = Veloz | 298.000 |
| Agya = Ayla | 287.000 |
| Calya = Sigra | 293.000 |
| Rush = Terios | 302.000 |
| Raize = Rocky baru | 292.000 |
| Alphard = Vellfire | 317.000 |
| Feroza = Taft GT | 288.000 |
| ~~Feroza Long~~ | 295.000 → **beda, sengaja TIDAK digabung** |

Harga listing sama persis = ukuran cover sama = memang 1 SKU. Ini dipakai sebagai
verifikasi independen atas pernyataan user, bukan sebagai sumber keputusan.

## Hasil di master

1.438 baris berubah, 726 baris memang sudah sesuai (total 2.164 baris grup kembar).

| Grup | Prefix kanonik | Perpindahan |
|---|---|---|
| Avanza+Xenia+Veloz (TF=2) | `TYT-AVZ` | `DHT-XNA`→G1 (132), `TYT-VLZ`→G3 (132), `DHT-XNA` G3→G3 (66) |
| Agya+Ayla (TF=1) | `TYT-AGY` | `DHT-AYL` (330) |
| Calya+Sigra (TF=1) | `TYT-CLY` | `DHT-SGR` (66) |
| Rush+Terios (TF=1) | `TYT-RSH` | `DHT-TRS` (132) |
| Raize+Rocky baru (TF=1) | `TYT-RZE` | `DHT-RCK` Gen 2 (A200) (66) |
| Alphard+Vellfire (TF=1) | `TYT-ALP` | `TYT-VLF` (330) |
| Rocky lawas+Feroza+Taft GT (TF=1) | `DHT-RCK` | `DHT-FRZ` (132), `DHT-TG` (52) |

## Tabrakan SKU yang ikut ketahuan & beres

`DHT-RCK-*-G1-*` di master dipakai **dua mobil yang sama sekali berbeda**: Rocky
F70/F300 (1984-2002, SUV kotak) dan Rocky Gen 2 A200 (2021-2026, crossover kembaran
Raize). Setelah pemisahan: F70/F300 tetap `DHT-RCK`, A200 jadi `TYT-RZE`.

Bukti tambahan bahwa keduanya memang beda: listing Shopee sudah memakai kode generasi
berbeda (`F7` vs `G2`) di dalam satu listing — jadi yang salah selama ini justru master
yang menyamakan keduanya jadi `G1`.

## Catatan penting yang perlu keputusan user

1. **Prefix kanonik grup Rocky lawas** dipakai `DHT-RCK` (dari jawaban user "opsi satu
   benar" = Rocky lawas tetap `DHT-RCK`). Kalau lebih suka `DHT-FRZ` (nama pasar
   Indonesia, tidak rancu dengan Rocky 2021), cukup ganti konstanta
   `PREFIX_ROCKY_LAWAS` di `samakan_sku_kembar.py`.
2. **Sheet2 no.60 menulis Daihatsu Rocky TF=1** dengan kedua generasi (F70/F300 dan
   Gen 2) dalam satu entri — artinya file formula menganggap keduanya 1 cover. Ini
   **bertentangan** dengan instruksi user. Yang dipakai instruksi user (didukung bukti
   kode generasi terpisah di listing). Sheet2 perlu dikoreksi jadi 2 entri.
3. **Veloz Gen 1 (2011-2021)** ikut formula Avanza **Gen 3** (`G3`), bukan G1 — mengikuti
   catatan Sheet2 "Avanza Gen 3 = Xenia Gen 3 = Veloz Gen 1,2,3". Ini counter-intuitif
   (bodi Veloz 2011-2021 basisnya Avanza Gen 2), jadi perlu konfirmasi.
4. **Harga Rocky lawas 292.000 vs Feroza/Taft GT 288.000** — kalau memang satu cover,
   salah satu listing salah harga (beda 4.000). Perlu diseragamkan.
5. **`Daihatsu Ayla` Gen 2 dan `Daihatsu All New Ayla` Gen 2 (A350)** adalah mobil yang
   sama dengan dua nama baris di master (132 baris kembar). Sengaja **tidak dihapus** —
   menghapus baris master itu keputusan user. Pola yang sama: `Daihatsu Xenia` /
   `Daihatsu All New Xenia`, `Daihatsu Sirion` / `Daihatsu New Sirion`,
   `Daihatsu Terios` / `Daihatsu Terios / New Terios`.

## KOREKSI: audit "7 pelanggaran Total Formula" itu SALAH

Laporan sebelumnya (2026-08-20) menyebut 7 model melanggar TF. Setelah diaudit ulang
lewat `audit_tf2.py`: **0 pelanggaran** dari 192 entri Sheet2 yang ketemu di master.

Penyebab false positive: audit lama mengelompokkan **per nama model di master**, padahal
satu entri formula bisa dipegang beberapa nama baris. Contoh:

- `Daihatsu Xenia` TF=2 "cuma pakai G1" → kode `G3`-nya ada di baris bernama
  **`Daihatsu All New Xenia`**. Total 2 kode = sesuai.
- `Honda Civic` TF=11 → `Honda Civic` (11 kode) + `Honda Civic Sedan` + `Honda Civic
  Sedan / RS`. Total tepat 11 kode.
- `Nissan Navara` TF=2 → `Nissan Navara` (G1) + `Nissan Navara PRO-4X` (G4) = 2 kode.
- `Toyota Corolla` TF=9 → `Corolla` + `Corolla Altis` + `Corolla Cross` = 6 kode (≤ 9).

Ini persis jebakan yang sudah dicatat di `feedback-undercover-sku-sync-lessons.md`
(pernah menghasilkan "85 pelanggaran palsu"). **Selalu kelompokkan per entri formula,
jangan per nama baris master.**

## Perubahan yang harus menyusul di listing Shopee

`laporan_listing_kembar.py` → `PERUBAHAN SKU KEMBAR - listing Shopee UA.xlsx`
(**319 varian** di toko Undercover Autocare).

Listing memakai kode generasi yang lebih banyak dari master dan harus ikut melebur:
Xenia `G2`, Veloz `G2`, Agya `G2`, Rush `G2`, Terios `G2`, Alphard `G4`, Feroza `G3`,
Rocky `F7`/`G2`.

Bug listing yang ikut ketahuan: **`DHT-TG-UA-R-Hijau-*`** — slot generasi di 4 varian
Reguler Taft GT diisi kata warna `"Hijau"`, bukan kode generasi.

## Verifikasi (`verify_kembar.py`, 12 cek, semuanya dibaca ulang dari disk)

1. daftar sheet sama · 2. jumlah baris tiap sheet sama · 3. **tidak ada kolom selain SKU
yang berubah** · 4. jumlah SKU berubah tepat 1.438 · 5. semua baris grup kembar pakai
prefix+kode generasi target · 6. semua kunci peta ketemu di master · 7. prefix lama
(`DHT-XNA` `TYT-VLZ` `DHT-AYL` `DHT-SGR` `DHT-TRS` `DHT-FRZ` `DHT-TG` `TYT-VLF`) hilang
total · 8. kembar satu grup menghasilkan SKU identik per toko/kategori/warna ·
9. jumlah kode generasi ≤ TF · 10. Rocky lawas ≠ Rocky baru · 11. kode toko di SKU hanya
`UA`/`SP` (aturan konsolidasi OT→UA, OP→SP) · 12. tidak ada elemen `<f>` di XML (anti
dialog "repair" Excel).

Semua lulus.
