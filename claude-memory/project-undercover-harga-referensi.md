# Referensi Harga per Tipe Bodi Mobil (mulai 2026-08-14)

## Konteks

User berencana update harga produk cover mobil, dan menduga ada pola: dalam
kategori bodi yang sama (city car, SUV, MPV, dll), mobil yang ukuran fisiknya
lebih kecil harganya lebih murah daripada yang lebih besar. Trigger: Honda
Brio (city car) Rp284.000 vs Daihatsu Ayla (city car) Rp287.000 — beda tipis,
tapi konsisten.

**Sumber data**: 5 file UA Shopee (`1.xlsx`-`5.xlsx`, snapshot 2026-08-12),
kolom Harga, difilter ke kategori **Reguler warna dasar** saja (bukan tier
Elite/Epic/Warrior, bukan Premium/Exclusive) — supaya perbandingan apple-to-
apple, karena tier warna & kategori produk beda-beda menaikkan harga di luar
faktor ukuran mobil. 413 model mobil unik ketemu harganya (di luar cover
motor, yang dikeluarkan dari analisis).

**Metode klasifikasi**: tipe bodi dikelompokkan manual berdasar pengetahuan
otomotif umum (bukan dari kolom data eksplisit — file listing tidak punya
kolom "tipe bodi"). 203/413 model berhasil diklasifikasi ke 9 kategori utama;
sisanya (terutama merek/model kurang umum) belum dikategorikan.

## Hasil: interval harga per kategori (Reguler warna dasar)

| Kategori | N model | Termurah | Termahal | Interval | % |
|---|---|---|---|---|---|
| City Car / LCGC | 29 | Hyundai Atoz Rp245rb | Geely EX2 Rp290rb | Rp45rb | 18,4% |
| Hatchback compact | 18 | Suzuki Swift Rp286rb | Honda Civic Hatchback Rp300rb | Rp14rb | 4,9% |
| Sedan compact/mid | 21 | Nissan Latio Rp291rb | Toyota Crown Rp309rb | Rp18rb | 6,2% |
| SUV compact/crossover 5-seater | 22 | Nissan Magnite Rp289rb | BYD Atto 3 Rp300rb | Rp11rb | 3,8% |
| SUV besar 7-seater/mid-size | 31 | Honda BRV Rp300rb | Fortuner/Pajero Sport Rp380rb | Rp80rb | 26,7% |
| MPV keluarga (5-7 seater) | 21 | Daihatsu Sigra Rp293rb | Suzuki XL7 Rp311rb | Rp18rb | 6,1% |
| MPV besar/premium van | 15 | Mitsubishi Grandis Rp307rb | Toyota HiAce Rp337rb | Rp30rb | 9,8% |
| Pickup | 11 | Suzuki Carry Pickup Rp283rb | Chevrolet Colorado Rp323rb | Rp40rb | 14,1% |
| Sport/Supercar/Ultra-luxury | 35 | Porsche 718 Cayman Rp408rb | Bentley Mulsanne Rp487rb | Rp79rb | 19,4% |

**Kesimpulan: pola user TERKONFIRMASI.** Dalam kategori yang sama, harga naik
seiring ukuran fisik mobil — konsisten di semua kategori. Interval TIPIS
(<10%) di kategori yang anggotanya seragam ukuran (Hatchback, Sedan, SUV
compact, MPV keluarga) — beda harga cuma Rp5-20rb antar model termurah &
termahal. Interval LEBAR (>15%) di kategori yang mencampur sub-segmen ukuran
beda jauh:
- **SUV besar**: BRV/Rush/RAV4/CRV (compact-crossover naik kelas, Rp300-313rb)
  vs Fortuner/Pajero Sport (body-on-frame sungguhan, jauh lebih besar,
  Rp380rb) — outlier signifikan, gap Rp67-80rb dari SUV besar lainnya.
- **Pickup**: Carry Pickup (kabin kecil komersial) vs Ranger/Triton/Colorado/
  D-MAX (double-cab besar) — beda jenis pickup, bukan cuma beda merek.
- **Sport/Supercar**: variasi bentuk & ukuran body sangat beragam (coupe 2-pintu
  vs sedan besar Bentley/Rolls Royce), bukan cuma soal ukuran tapi juga
  kerumitan bentuk body custom-cut.

## Detail sorted per kategori kunci (city car, SUV, MPV — yg user tanya eksplisit)

**City Car / LCGC** (kecil ke besar, Rp245rb-290rb):
Hyundai Atoz(245) < Wuling Air EV(262) < Daihatsu Ceria(267) < Vinfast VF3/
Wuling Mini EV/DFSK Mini EV(270) < DFSK Seres E1(272) < Chery EQ1(273) <
Kia Picanto/Fiat 500(279) < Hyundai Grand i10/Getz/Suzuki S-Presso(281) <
Suzuki Celerio/Toyota Starlet/Suzuki Ignis(282) < Chevrolet Spark/Datsun Go/
Renault Kwid(283) < Suzuki Karimun/Honda Brio(284) < BYD Atto 1(285) <
Suzuki Splash/Kia Pride/Neta V(286) < Toyota Agya/Daihatsu Ayla(287) <
Datsun GO Plus(288) < Geely EX2(290)

**SUV compact/crossover** (Rp289rb-300rb): Nissan Magnite/Renault Kiger(289)
< Suzuki Vitara Brezza(290) < Toyota Raize/Daihatsu Rocky(292) < ... <
Honda HRV/Toyota Yaris Cross/Mitsubishi Xforce/Hyundai Creta/Kia Seltos/
MG ZS(298) < BYD Atto 3(300)

**SUV besar** (Rp300rb-380rb): Honda BRV/Jeep Compass(300) < Toyota Rush/
Daihatsu Terios/Mazda CX-5/Hyundai Tucson/Kia Sportage(302) < ... < Range
Rover/Toyota Land Cruiser(315) < Isuzu Mux(328) < **Toyota Fortuner/
Mitsubishi Pajero Sport(380) — jauh di atas yang lain**

**MPV keluarga** (Rp293rb-311rb): Daihatsu Sigra/Toyota Calya(293) < Xenia/
Avanza/Veloz/Ertiga/Mobilio/Freed/Alvez(298) < Suzuki APV(299) < Xpander/
Grand Livina/Kia Carens(302) < Wuling Confero(304) < Chevrolet Spin(306) <
Wuling Cortez(308) < Suzuki XL7(311)

## Eksekusi nyata 2026-08-15: harga baru dari file HPP Top 100 Terlaris

User upload `DATA_HARGA_JUAL_UC_HPP_Top_100_Terlaris.xlsx` (100 produk terlaris,
sheet "HPP 12%"), kolom "Harga Jual Terbaru" (hasil hitungan cost+margin per
Pcs/Roll — makin banyak pcs per roll kain = mobil makin kecil = HPP makin
murah). **Temuan penting**: kolom ini murni fungsi dari `Pcs/Roll`, BUKAN dari
tipe/ukuran mobil aktual — semua produk dgn Pcs/Roll sama dapat harga IDENTIK
persis walau beda kategori bodi total (mis. Toyota Avanza, Honda Jazz, Suzuki
Ertiga, Toyota Vios semua Pcs/Roll=5 -> harga sama 381.591). Instruksi user:
pakai kategori city car/SUV/MPV/dll sbg patokan tambahan, mobil terkecil per
kategori jadi harga dasar (floor), mobil lain naik bertahap max Rp5.000/step,
kelipatan ribuan, dibulatkan ke atas.

**Metode final** (`scripts/` blm disimpan permanen — reproduksi manual dari
riwayat sesi ini kalau perlu diulang):
1. Klasifikasi tiap 100 produk ke 8 kategori bodi manual (City Car, Hatchback,
   Sedan, SUV compact, SUV besar, MPV keluarga, MPV besar, Pickup) pakai
   pengetahuan otomotif umum — 100/100 berhasil diklasifikasi.
2. Per kategori, `Pcs/Roll` (data BAWAAN file, sudah proxy ukuran fisik yg
   presisi — makin besar Pcs/Roll = mobil makin kecil) dipakai sbg dasar
   ranking ukuran, BUKAN nebak dimensi manual — supaya konsisten sama data
   biaya kain yg sudah dihitung user.
3. Tier Pcs/Roll TERBESAR dlm kategori (mobil terkecil) -> harga dasar =
   `ceil(harga_jual_terbaru_mentah / 1000) * 1000`.
4. Tier Pcs/Roll berikutnya (mobil lebih besar) -> harga dasar + Rp5.000
   (step tetap = batas maksimal yg diizinkan user, dipakai konsisten spy
   simpel & bisa direproduksi). Kelipatan bertahap tiap tier, bukan
   proporsional ke gap HPP asli (yg bisa >Rp50rb antar tier -> terlalu jauh
   dari batas 5rb yg diminta user).
5. Kolom "Harga Baru (Strip: Elite/Epic/Warrior)" = harga Reguler baru + Rp56.000
   (instruksi eksplisit user, angka tetap flat utk semua produk & kategori).

**Hasil per kategori** (harga dasar -> harga tier berikutnya, Rupiah):
- City Car: Wuling Air EV(Pcs/Roll7)=296rb -> Brio/Karimun/March/Picanto/dst(P6)=301rb -> Agya/Ayla/Ignis(P5)=306rb
- Hatchback: Yaris/Swift/Sirion/dst(P6)=332rb -> Jazz/Baleno(P5)=337rb
- Sedan: City Sedan/Soluna/Timor(P6)=332rb -> Vios/Civic/Camry/Corolla/dst(P5)=337rb
- SUV compact: Raize/Fronx/Jimny/WRV/Rocky/dst(P6)=332rb -> Feroza/Destinator/Creta(P5)=337rb
- SUV besar: HRV/BRV/Rush/CRV/Terios/Hardtop/dst(P5)=382rb -> Fortuner/Pajero Sport/Land Cruiser/Palisade(P4)=387rb
- MPV keluarga: Sigra/Sienta/Go Plus(P6)=332rb -> Avanza/Ertiga/Xenia/Calya/dst(P5)=337rb
- MPV besar: Innova/Kijang/Panther/Odyssey/Kuda(P5)=382rb -> Alphard/Vellfire/Voxy(P4)=387rb -> HiAce(P3)=392rb
- Pickup: Triton/Gran Max PU/Carry(P5)=382rb -> Hilux(P4)=387rb

File hasil (3 kolom baru: Tipe Mobil, Harga Baru Reguler, Harga Baru Strip)
dikirim ke user sbg `DATA_HARGA_JUAL_UC_HPP_Top_100_Terlaris_HASIL.xlsx`,
formula & sheet lain di file asli tidak disentuh.

### REVISI (v2, masih menunggu review user) — matriks dibalik: Pcs/Roll DULU

User menolak versi pertama & mengoreksi urutan matriksnya. **Aturan final v2**
(script: `scripts/harga_baru_matriks.py`):
1. **Pcs/Roll = penentu LANTAI harga**, dihitung sendiri per tier dan **TIDAK
   saling menumpuk**: 7→Rp296rb, 6→Rp332rb, 5→Rp382rb, 4→Rp457rb, 3→Rp583rb
   (semua = ceil-ribuan dari 'Harga Jual Terbaru' mentah tier itu). Jadi mobil
   di tier 4 pcs/roll mulai dari Rp457rb, BUKAN melanjutkan tangga tier 5.
   Contoh kanonik user: Fortuner (4 pcs/roll, terkecil di grup SUV besar-nya)
   = Rp457.000, bukan hasil +5rb dari harga BR-V yg 5 pcs/roll.
2. Di dalam tiap **(Pcs/Roll × kategori bodi)**, mobil diurut dari panjang bodi
   TERKECIL; yg terkecil dapat lantai, yg lebih besar naik bertahap.
3. Kenaikan kelipatan Rp1.000, rentang total per grup maksimal Rp5.000.
4. Kolom Strip (Elite/Epic/Warrior) = harga Reguler + Rp56.000 (flat).

**Cara menghitung lebar interval per grup — 2 tahap (penting, dua-duanya perlu):**
- LEBAR spread grup dari skala ABSOLUT: tiap ~100mm selisih panjang
  terkecil↔terbesar = Rp1.000, dibatasi Rp5.000. Tanpa ini, grup yg ukurannya
  mirip-mirip ikut dipaksa menyebar penuh Rp5.000 (mis. Ignis vs Agya/Ayla yg
  cuma beda 60mm jadi berjarak sama jauhnya dgn Mazda 2 vs S-Class yg beda
  839mm — jelas salah).
- POSISI tiap mobil di dalam spread itu PROPORSIONAL thd panjangnya. Tanpa ini,
  satu mobil yg jauh lebih kecil bikin sisanya mentok di harga sama semua (mis.
  Toyota Hardtop 3.840mm di SUV besar 5 pcs/roll bikin 11 mobil lain kena cap
  Rp387rb identik).
Hasil v2 kebetulan pas dgn dua tebakan user: Fortuner Rp457rb & BR-V Rp385rb.

**Data panjang bodi (mm) per model di-hardcode di script** (dari pengetahuan
otomotif umum, bukan dari kolom file) — kalau menambah model baru, WAJIB isi
`PANJANG_MM` & `KATEGORI`, script sengaja `SystemExit` kalau ada model tanpa
salah satunya, biar tidak diam-diam salah harga.

### JEBAKAN TEKNIS: openpyxl merusak workbook ber-formula

Versi pertama ditulis dgn cara menambah kolom ke workbook ASLI lalu
`wb.save()`. Akibatnya user lapor **"formulanya jadi banyak yg kosong"**.
Penyebab pasti (sudah diverifikasi dgn membandingkan XML dalam zip): openpyxl
menulis ulang tiap sel formula TANPA cached value — dari ~8.200 formula di 6
sheet, **0 yg menyisakan nilai** (aslinya ratusan punya). openpyxl juga
membuang `xl/calcChain.xml`, `xl/sharedStrings.xml`, dan `xl/metadata`. Excel
memang disuruh hitung ulang (`fullCalcOnLoad="1"`), tapi viewer lain (preview
HP, Google Sheets, LibreOffice, atau Excel mode manual-calc) menampilkannya
KOSONG. **How to apply: JANGAN pernah menambah kolom ke workbook ber-formula
milik user lewat openpyxl.** Tulis hasil sbg workbook BARU berisi nilai statis
saja, dan biarkan file sumber tidak tersentuh.

**Kalau mau extend/ulang metode ini** (mis. utk toko/channel lain, atau full
katalog bukan cuma Top 100): pakai kolom `Pcs/Roll` (bukan menebak dimensi
mobil manual) sbg penentu lantai harga — itu data biaya kain riil yg sudah
dihitung user, jauh lebih presisi drpd asumsi ukuran dari nama model doang.
Panjang bodi hanya dipakai utk mengurutkan DI DALAM grup, bukan utk menentukan
harga dasar.

## Cara pakai untuk update harga terbaru

1. Kalau update harga 1 model, cek dulu posisinya di tabel kategori terkait
   di atas — harga baru sebaiknya tetap konsisten urutan (jangan sampai city
   car kecil jadi lebih mahal dari city car yang lebih besar dalam kategori
   sama).
2. Interval antar-model dalam 1 kategori seragam biasanya Rp5.000-20.000 saja
   (city car, hatchback, sedan, SUV compact, MPV keluarga) — kalau mau naikkan
   harga 1 model signifikan lebih dari itu tanpa alasan ukuran/bahan beda,
   cek ulang apakah wajar.
3. Kategori campuran sub-segmen (SUV besar, pickup, supercar) WAJAR py gap
   lebih lebar (>15%) — jangan paksa rata kalau memang beda kelas ukuran
   (mis. Fortuner vs BRV).
4. Analisis ini baru dari kategori **Reguler warna dasar** UA Shopee saja.
   Tier lain (Strip/Elite/Epic/Warrior, Premium, Exclusive) & toko lain
   (OT/OP/SP) belum dicek — kemungkinan pola serupa (proporsional), tapi
   belum diverifikasi. Kalau mau extend analisis ke tier/toko lain, ulangi
   metode yang sama (extract harga per model per kategori produk, filter
   warna dasar, group by tipe bodi).
5. 210/413 model BELUM diklasifikasi ke tipe bodi (merek/model kurang umum
   atau ambigu) — daftar mentah harga per model ada di riwayat sesi
   2026-08-14, belum disimpan permanen sbg file terpisah (regenerate dari
   `scripts/` kalau perlu: extract kolom B/D/G Sheet1 UA Shopee, filter
   kategori=Reguler & warna bukan tier Elite/Epic/Warrior/Strip-N, group by
   nama model, ambil harga modus).


## Eksekusi produk 11-20 (2026-08-18) — pindah ke pencocokan berbasis SKU

Script: `scripts/update_harga_per_sku.py` (menggantikan `update_harga_listing.py`
utk batch berikutnya). Sumber harga: `HARGA_BARU_TOP100_v4.xlsx` kolom "Harga
Baru (Reguler)"; strip = reguler + Rp43.000.

**Perubahan metode paling penting: cocokkan lewat PREFIX SKU, bukan nama listing.**
Instruksi eksplisit user — kalau Rush naik, Terios (SKU sama) harus ikut naik.
Beberapa model beda nama memakai cover identik sehingga SKU-nya satu, artinya
stoknya satu barang dan harganya WAJIB satu angka. Terverifikasi di UA:

| Prefix | Model yang berbagi |
|---|---|
| TYT-RSH | Toyota Rush + Daihatsu Terios |
| TYT-CLY | Toyota Calya + Daihatsu Sigra |
| TYT-AVZ | Toyota Avanza + Daihatsu Xenia + Toyota Veloz |
| DHT-AYL | Daihatsu Ayla + Toyota Agya |

Pencocokan lewat nama (metode batch 1-10) MELEWATKAN pasangan seperti ini.
Efek samping yang menguntungkan: prefix SKU otomatis memisahkan model bernama
mirip tapi produknya beda — Yaris (TYT-YRS) tidak menyeret Yaris Cross
(TYT-YRC)/GR Yaris (TYT-GRY); Civic (HND-CVC) tidak menyeret Civic Hatchback
(HND-CVH)/Civic Type R (HND-CTR).

### Keputusan user: Calya vs Sigra

File harga memberi Calya (#14) Pcs/Roll 5 → Rp382rb tapi Sigra (#30) Pcs/Roll 6
→ Rp333rb, padahal keduanya mobil kembar, panjang sama 4070mm, SKU sama
TYT-CLY, dan harga listing-nya saat itu sama-sama Rp293rb. Karena SKU satu,
harga harus satu. **User memilih Rp382.000 (Pcs/Roll 5).** Artinya kalau nanti
memproses Sigra di batch #30, JANGAN pakai Rp333rb dari file — sudah diputuskan
ikut Calya.

### JEBAKAN: SKU kembar belum sinkron di semua channel

Konsolidasi SKU kembar baru jalan di Shopee. Kondisi 2026-08-18:

| Model | Shopee | TikTok | Lazada |
|---|---|---|---|
| Sigra | TYT-CLY | TYT-CLY | **DHT-SGR** |
| Terios | TYT-RSH | TYT-RSH | **DHT-TRS** |
| Veloz | TYT-AVZ | TYT-AVZ | **TYT-VLZ** |
| Xenia | TYT-AVZ | TYT-AVZ + **DHT-XNA** | **DHT-XNA** |
| Agya | DHT-AYL | DHT-AYL + **TYT-AGY** | **TYT-AGY** |

Akibatnya update berbasis SKU melewatkan kembaran di Lazada/TikTok. Ditambal
lewat `ALIAS{}` di script (prefix belum-sinkron → prefix induk). **Itu tambalan
harga, bukan perbaikan SKU** — konsolidasi SKU-nya sendiri masih PR di proyek
SKU Sync. Konsekuensi lain: batch 1-10 (Veloz/Xenia/Agya) kemungkinan besar
BELUM ternaikkan di Lazada & TikTok karena waktu itu masih pencocokan nama —
perlu dicek ulang.

### JEBAKAN: prefix SKU tidak boleh ditebak dari nama model

Tebakan `NSN-GLV` untuk Livina ternyata salah, yang benar `NSN-LVN`. Selalu
verifikasi prefix langsung ke data listing sebelum dipakai. Script sengaja
`SystemExit` kalau ada produk dalam rentang yang belum terdaftar di `PREFIX{}`.

### JEBAKAN: satu prefix bisa memuat produk lain yang harganya beda

"Nissan Grand Livina Custom Roofbox Reguler" memakai prefix NSN-LVN yang sama
dengan Livina biasa, tapi harganya Rp352rb vs Rp385rb. Penjaga `KECUALI`
(x-gear/custom/roofbox) tetap dipasang. Batch 11-20 sudah dicek bersih dari
kasus ini, tapi batch berikutnya belum tentu.

### Temuan sampingan: harga TikTok kependekan Rp100.000

Yaris strip di TikTok Rp252rb padahal Shopee Rp352rb; Calya strip TikTok
separuh Rp253rb separuh Rp353rb. Pola salah ketik digit ratusan-ribu (2 vs 3).
Sudah ikut terkoreksi. Kalau menemukan harga yang menyimpang ~Rp100rb dari
channel lain, curigai pola yang sama.

### Hasil batch 11-20

406 baris Shopee, 462 TikTok, 462 Lazada (hanya baris yang berubah, tier R & S).
Sumber: Shopee export 2026-08-18, TikTok snapshot 2026-08-15, Lazada 2026-08-13.

Pemakaian ulang untuk batch berikutnya (mis. 21-30):
```
python3 scripts/update_harga_per_sku.py <file_harga.xlsx> 21 30 <out_dir> <folder_listing...>
```
Lengkapi dulu `PREFIX{}` untuk produk 21-30 — script berhenti kalau ada yang belum terdaftar.


## Perbaikan script 2026-08-18: kolom dicari lewat nama header, bukan nomor tetap

User upload file TikTok terbaru (`Tiktoksellercenter_batchedit_20260818_sales_information_template.xlsx`)
dan Lazada terbaru. Ternyata TikTok Seller Center py 2 varian template export:
- **all_information** (dipakai batch 11-20 pertama): 41 kolom, sheet tambahan
  `Brand` + `HiddenAttr`. Kolom: nama=3, var=6, sku=11, harga=9.
- **sales_information** (file 18 Agustus ini): 8 kolom saja, TANPA sheet `Brand`.
  Kolom BEDA TOTAL: nama=3, var=5, sku=7, harga=6.

Kalau nomor kolom di-hardcode per channel (cara lama), ganti varian template =
harga tertulis ke kolom yang salah tanpa ketahuan (tidak error, cuma salah
sasaran diam-diam — bug paling berbahaya). **Diperbaiki**: `update_harga_per_sku.py`
sekarang cari kolom lewat NAMA header di baris 1 (`resolve_cols()`), pola field
name-nya stabil lintas varian (`product_name`, `variation_value`, `seller_sku`,
`price` utk TikTok; field serupa utk Shopee/Lazada) walau nomor kolomnya beda.
Juga `deteksi_channel()` diperbaiki: sheet `template_hide` jadi penanda unik
Lazada (dicek SEBELUM fallback generik `'template' in n`), krn TikTok varian
baru tidak lagi py sheet `Brand` sbg pembeda dan sheet-nya bernama 'Template'
yg jadi sama dgn 'template' Lazada setelah di-lowercase.

**Kalau nanti kolom template berubah lagi**: script akan `SystemExit` dgn pesan
kolom mana yg tidak ketemu, bukan diam-diam salah tulis — cek `HEADER_KEY{}`
kalau itu terjadi.

## JEBAKAN TERKONFIRMASI: batch 1-10 (Avanza/Ayla) bocor di Lazada

Cross-check file Lazada terbaru (18 Agustus) vs harga target: **Veloz di
Lazada masih Rp298.000**, padahal Avanza & Xenia (SKU sama TYT-AVZ) sudah
Rp385.000 di Lazada. TikTok sudah benar utk Agya/Veloz/Xenia bertiga (SKU-nya
match ke ALIAS). Ini mengkonfirmasi dugaan yg dicatat sblmnya: batch 1-10
dikerjakan sblm pindah ke pencocokan berbasis SKU, jadi kembaran yg beda nama
listing (Veloz utk Avanza) kemungkinan terlewat di Lazada. **Sudah dibereskan 2026-08-18**, sekaligus ketemu penyebabnya: SKU Veloz di
Lazada ternyata baru disinkronkan ke TYT-AVZ (sama dgn Avanza) di suatu waktu
ANTARA snapshot 13→18 Agustus — sebelumnya masih SKU sendiri TYT-VLZ (lihat
riwayat proyek SKU Sync utk kapan persisnya). Jadi bukan human error di
update harga kemarin; listingnya memang baru "ikut nempel" ke SKU induk
belakangan (proyek SKU Sync jalan terpisah dari update harga), dan harganya
belum sempat menyusul. 28 baris Lazada (10 R Rp298rb->385rb, 18 S
Rp358rb->428rb) sudah dikirim & diverifikasi 0 masalah.

**Pelajaran umum**: kalau nemu SKU kembar yg harganya belum sama, jangan
langsung asumsikan itu bug update harga -- cek dulu riwayat SKU-nya, bisa jadi
konsolidasi SKU-nya sendiri yg baru terjadi belakangan.


## Eksekusi Otonation (OT) 2026-08-18: full 100 produk sekaligus

Beda dari batch UA sebelumnya (bertahap 10 produk), user minta OT langsung
semua 100 produk top-terlaris dalam 1 kali jalan. Script `update_harga_per_sku.py`
diperluas: `PREFIX{}` sekarang lengkap 100 entri (sebelumnya cuma 1-20), dan
`__main__` nambah argumen `nama_toko` supaya nama file output tidak selalu
"UA" (dipakai: `python3 update_harga_per_sku.py <harga.xlsx> 1 100 <out_dir> OT <folder...>`).

**OT cuma py channel Shopee** (2 file diupload, sudah kena bug XML activePane
yg sama spt Shopee UA, diperbaiki pakai `repair_xlsx.py`). 83,8% baris OT (7.692
dari 9.180) sudah SKU format master; sisanya kode lama `CVR####-OTN-XX`
(pra-migrasi, konsisten dgn catatan lama di `project-undercover-otonation-status.md`)
— otomatis dilewati oleh `urai_sku()` (butuh 6 segmen), aman, tapi berarti
update harga TIDAK menjangkau baris2 itu sampai SKU-nya disinkronkan.

**Metode pemetaan nama->prefix untuk 80 produk baru (21-100)**: exact-match
token (bukan subset -- subset match ternyata salah tangkap Yaris Cross/GR
Yaris ke bawah "Toyota Yaris", persis jebakan yg sama kayak batch UA
sebelumnya) antara nama di file harga vs nama listing OT, dgn STOP-word yg
diperluas mencakup istilah kategori khas OT (`outdoor`,`semi`,`indoor`,`dan`,
`extreme`) supaya "Cover Mobil X - Reguler - Semi Outdoor" match ke "X" polos.
87/100 langsung ketemu tunggal, 10 butuh keyword manual (Brio/HR-V/BR-V/CR-V/
WR-V/APV/Pajero Sport/Mazda 2 Sedan/City Hatchback RS/Outlander -- semuanya
py qualifier tambahan spt "Satya/RS" yg bikin token-set beda dari listing).

**Kasus multi-prefix yg perlu keputusan (BUKAN tebakan, semua diverifikasi):**
- **Toyota Hilux** -> `TYT-HLX` saja. `TYT-HLR` (Hilux Rangga) dikecualikan --
  sudah dikonfirmasi lama sbg produk master terpisah (lihat
  project-undercover-otonation-status.md, generasi sendiri 2024-2026).
- **Daihatsu Rocky** -> `TYT-RZE` (kembar modern Toyota Raize 2019-2026).
  DIKONFIRMASI bukan tebakan: harga baris "Daihatsu Rocky" & "Toyota Raize" di
  file HARGA_BARU_TOP100_v4 SAMA PERSIS (Rp336rb/379rb) -- bukti independen yg
  cocok sama Raize. SKU F70/F300 (Rocky klasik 1984-2002, kembar Feroza) yg
  hidup di listing SAMA "Daihatsu Rocky" otomatis kebagian lewat entri
  'Daihatsu Feroza' sendiri (Rp382rb/425rb) -- tidak perlu entri terpisah,
  prefix-based filtering udah otomatis benar tanpa perlu logic khusus.
- **Toyota HiAce** -> `TYT-HAC` ("Commuter") SAJA. `TYT-HAL` ("Premio",
  kemungkinan "HiAce Long") SENGAJA TIDAK disentuh -- beda dari Rush/Terios
  dkk (itu rebadge identik, terverifikasi harganya emang sama). Commuter vs
  Premio bisa jadi beda ukuran fisik asli, file harga cuma py 1 baris "Toyota
  HiAce" tanpa keterangan generasi/submodel. **User belum memutuskan** apakah
  Premio perlu disamakan jg -- kalau iya, tambah `ALIAS['TYT-HAL']='TYT-HAC'`.

**BENTROK harga (SKU sama, harga beda di file) -- diselesaikan konsisten dgn
keputusan sebelumnya, bukan pilihan baru:**
- Calya(382rb) vs Sigra(333rb) [`TYT-CLY`] -> pakai Calya, sama kayak
  keputusan user 2026-08-18 pas UA.
- Avanza(385rb) vs Veloz(386rb) [`TYT-AVZ`] -> pakai Avanza, konsisten sama
  yg SUDAH dideploy ke UA/TikTok/Lazada (beda cuma Rp1rb, sepertinya
  pembulatan independen per baris di file harga, bukan disengaja).
Mekanisme BENTROK di `baca_harga()` otomatis pakai baris yg PERTAMA ketemu di
file (row order), yg kebetulan match keputusan yg diinginkan di kedua kasus
ini -- tapi JANGAN andalkan urutan file scr default terus, selalu cross-check
manual kalau ada BENTROK baru.

**PENTING -- dikoreksi 2026-08-19, dijelaskan user**: temuan "6 baris
anomali Rp780-810rb" di atas SALAH ARAH sebagai "harga lama placeholder".
User klarifikasi: di OT, listing **"Outdoor" POLOS setara tier PREMIUM UA**
(bukan Reguler) -- **"Semi Outdoor"** yg setara Reguler. Jadi rentang harga
jauh lebih tinggi di listing "Outdoor" polos itu MEMANG BENAR, bukan bug.

Investigasi lanjutan (scan semua 100 produk, bukan cuma yg kelihatan
anomali): ketemu **31 baris di 15 model berbeda** yg hidup di listing
"Outdoor" polos TAPI SKU-nya SALAH TAG segmen 'R'/'S' (Reguler/Strip) padahal
seharusnya 'P' (Premium) -- harganya SENDIRI SUDAH BENAR Premium (Rp700rb-
1,06jt, sesuai model), cuma kode SKU-nya yg keliru. Model yg kena: BMW Seri
5(7), Mercedes S Class(7), Toyota Harrier(3), HR-V(2), X-Trail(2), + masing2
1 baris di Rush/Terios, Avanza/Xenia, Stargazer, City Hatchback RS, Sirion,
Suzuki XL7, Camry, Corolla, Vellfire (+1 Nissan Serena, di luar top-100 jadi
tidak relevan). Kalau update harga Reguler/Strip dijalankan naif ikut segmen
SKU apa adanya (spt versi pertama script), 30 baris ini KETIMPA jadi harga
Reguler yg salah -- padahal produknya beneran Premium.

**Fix**: `scripts/update_harga_per_sku.py` sekarang py `is_outdoor_polos(nm)`
-- exclude baris apa pun yg nama listingnya mengandung "outdoor" TAPI TIDAK
mengandung "semi outdoor"/"extreme outdoor"/"indoor dan outdoor", TERLEPAS
dari kata SKU-nya. Guard ini jalan SEBELUM cek segmen R/S, jadi baris yg
salah-tag ikut kelindungi walau SKU bilang R/S. Hasil setelah fix: 3.290
baris (turun dari 3.320 di versi pertama yg salah), 0 baris outdoor-polos
bocor saat diverifikasi ulang.

**Kalau extend ke toko lain (OP/SP) atau produk >100**: WAJIB pakai
`is_outdoor_polos()` yg sudah ada di script (jangan filter manual berdasar
ambang harga spt yg pertama kali dicoba -- itu cuma nangkep kasus yg
harganya kebetulan tinggi, MELEWATKAN kasus yg harga Premium modelnya
kebetulan rendah/normal-looking, false negative). Guard ini murni berbasis
TEKS NAMA LISTING, bukan besaran harga, jadi menjangkau semua kasus terlepas
dari harga modelnya berapa. SKU yg salah tag itu SENDIRI belum diperbaiki --
di luar cakupan update harga, PR terpisah utk proyek SKU Sync.

**Hasil**: 3.320 baris Shopee OT (1.205 R + 2.115 S), 92/93 prefix terpakai
(cuma Mazda 2 Sedan #42 yg 0 baris -- genuinely tidak dijual OT, hanya Mazda 2
Hatchback yg ada). 0 masalah integritas file.

**PREFIX{} lengkap 100 produk sekarang tersimpan permanen di
`scripts/update_harga_per_sku.py`** -- toko lain (OP/SP) kemungkinan besar
bisa pakai prefix yg SAMA (desain SKU `-UA-` dipakai bersama semua toko), tapi
tetap WAJIB cross-check ke data listing masing2 toko dulu sebelum jalan (kayak
Mazda 2 Hatchback yg ternyata py prefix OT sendiri `MZD-MZ2`, beda dari
prefix asli master `MZD-2H` yg dipakai UA -- jangan asumsikan 100% seragam).

---

## Eksekusi 2026-08-20 (branch `claude/sku-price-tracking-sheets-7ogdnv`): dibawa masuk dari branch lain + dipakai untuk SP/OP

File memory ini awalnya cuma ada di branch `claude/repo-memory-access-4hthja` (sesi
lain, akun/device lain) - **tidak ikut sinkron** ke branch kerja lain. User yang
menunjukkan lokasinya ("ada di branch claude/repo-memory-access-4hthja coba cek")
setelah sempat ditanyakan soal update harga UC dan riwayatnya tidak ketemu.
**Pelajaran: kalau memory yang dicari tidak ketemu di `claude-memory/` branch
saat ini, TANYAKAN ke user apakah ada branch lain sebelum menyimpulkan "tidak ada
catatannya" — jangan cuma andalkan grep di 1 branch.**

### Kesalahan yang sempat terjadi sebelum file ini ditemukan

Dua file "harga baru" sempat dibuat pakai metode yang SALAH (rank harga UC/ACTUAL,
disebar rata ke 6 tingkat) karena metode matriks (Pcs/Roll x kategori bodi x
panjang fisik) di atas belum ditemukan:
- `harga_baru_sp_op.py` -> `Harga Baru SP-OP (Reguler).xlsx` (200 model)
- `harga_baru_uc_top100.py` -> `Harga Baru UC Top 100 (Reguler).xlsx` (100 model)

Kedua file itu **SUDAH DIGANTIKAN** oleh versi matriks yang benar (lihat di bawah).
Scriptnya dipertahankan di repo dgn catatan SUPERSEDED di docstring (bukan
dihapus, biar riwayatnya jelas), TAPI JANGAN dipakai lagi sbg acuan metode.

### UC Top 100: dihitung ulang pakai `harga_baru_matriks.py` yang sudah divalidasi

Script & dict `KATEGORI`/`PANJANG_MM` disalin APA ADANYA dari branch
`claude/repo-memory-access-4hthja` (`scripts/harga_baru_matriks.py`, versi final
setelah revisi TAMBAHAN_STRIP 56rb->43rb) - tidak diubah sama sekali. Dijalankan
ke file `DATA_UC_HPP_Top_100_Terlaris.xlsx` (sheet HPP 12%) yang sama persis
dipakai user sebelumnya. Hasil cocok dgn 2 patokan yang tercatat di memory:
**Toyota Fortuner = Rp457.000, Honda BR-V = Rp385.000.**

### SP/OP (200 model): metode sama, 100 model tambahan diklasifikasi baru

File `HPP_STP_OTP_.xlsx` (sheet HPP 12%, toko Smartprotection & Otoprotection)
punya 200 model - 100 di antaranya sudah py kategori+panjang dari dict di atas
(dipertahankan sama persis), **100 SISANYA BARU diklasifikasi** (kategori bodi +
panjang mm) khusus untuk eksekusi ini, pakai pengetahuan otomotif umum dgn
konvensi kategori yang sama (ditambah 1 kategori baru: "Sport/Supercar", belum
py preseden di 100 model pertama - dipakai utk BMW M2/Z4, Toyota GR 86, Mazda
MX-5 RF, Lamborghini Aventador).

**PENTING - 100 klasifikasi baru ini BELUM divalidasi user** (beda dgn 100
yang lama, yang sudah lolos beberapa ronde koreksi user thn 2026-08-14/15).
Lihat sheet CATATAN di file hasil (`Harga Baru SP-OP (matriks).xlsx`) utk daftar
lengkap 100 model + kategori + panjang yang dipakai - kalau user mengoreksi
salah satu, catat di sini juga.

Script: `hpp-per-merk-scripts/harga_baru_sp_op_matriks.py` ->
`verify_harga_matriks_sp_op.py` (11 cek, semua lulus).

**Beda dari versi UC**: SP/OP kali ini TIDAK menyertakan kolom Strip (Elite/
Epic/Warrior +Rp43.000) - user cuma minta harga Reguler dari sheet HPP 12%,
belum ada instruksi eksplisit soal Strip untuk SP/OP.

---

## Verifikasi 2026-08-20: cek listing Otonation vs harga baru top-100

User upload 2 file listing Shopee OT ("1.xlsx"/"2.xlsx", kena bug XML activePane
yang sama, diperbaiki `repair_xlsx.py`), minta dicek "apakah sudah sesuai" harga
baru — **scope eksplisit user: hanya produk 'Semi Outdoor' atau yang setara**.

Script: `hpp-per-merk-scripts/cek_harga_otonation.py` (read-only, tidak menulis
apa pun) — reuse `PREFIX{}`/`ALIAS{}`/`is_outdoor_polos()`/`urai_sku()`/
`baca_harga()` dari `update_harga_per_sku.py` (salinan verbatim branch lain).

**Hasil: 3.248/3.262 baris (99,6%) dalam scope sudah cocok persis dengan target.**

Temuan konkret (2 kategori beda sifat):

1. **Suzuki Carry generasi "Gen 2 F (2023)" masih harga lama flat Rp315.000**
   (target: Rp382.000 Reguler / Rp425.000 Strip) — 14 baris. SKU-nya (`SZK-CAR-
   UA-*-G1-*`) **SAMA PERSIS** dengan generasi "Gen 2 (2018-2022)" yang SUDAH
   benar (382rb/425rb) — jadi di Shopee ada 2 baris varian dengan SKU identik
   tapi harga BERBEDA pada satu listing yang sama. Genuinely belum ke-update,
   bukan false positive.

2. **3 model tidak bisa dicek via SKU sama sekali** (prefix target 0 baris
   ketemu):
   - **Daihatsu Luxio**: SKU listing OT pakai prefix `DHT-GMX-...` (bukan
     `DHT-LXO`), tapi **harganya sendiri sudah benar** (383rb/426rb = persis
     target Luxio) — murni salah tag prefix SKU, bukan masalah harga. Ini PR
     terpisah di proyek SKU Sync, bukan harga.
   - **Honda City Hatchback RS** & **Mazda 2 Sedan**: SKU listing OT **kosong
     total** (`None`), harga flat tanpa diferensiasi R/S (City Hatchback RS
     Rp307.000 vs target 337rb/380rb; Mazda 2 Sedan Rp300.000 vs target
     382rb/425rb) — kelihatan jelas BELUM diupdate, tapi tidak bisa
     diverifikasi otomatis via SKU krn kolom SKU-nya blank di listing.

**How to apply**: kalau minta cek serupa lagi (toko/channel lain, atau setelah
Suzuki Carry Gen 2 F diperbaiki), jalankan ulang `cek_harga_otonation.py` dgn
argumen `<target.xlsx> <listing1.xlsx> [listing2.xlsx ...]`. 3 model tanpa SKU
di atas tidak akan pernah ketahuan otomatis lewat cara ini — kalau mau dicek
scope lebih luas, cross-check manual by NAMA produk juga, jangan cuma via SKU.

---

## Eksekusi 2026-08-20 (lanjutan): UC top-40, otomatis sertakan kembar di luar scope

User upload 5 file Shopee UA terbaru (`1.xlsx`-`5.xlsx`, sama bug XML activePane,
diperbaiki `repair_xlsx.py`), minta lanjut ke 40 model terlaris (23 katanya sudah
selesai kemarin), **dengan syarat**: kalau ada SKU kembar, ikutkan walau modelnya
sendiri di luar 40 terlaris.

**Cara memenuhi syarat itu tanpa logic khusus**: panggil `update_harga_per_sku.py`
dengan rentang **1-40** (bukan 24-40). `baca_harga()` mengelompokkan target per
PREFIX SKU (bukan per nama model) — jadi kalau salah satu anggota grup kembar ada
di rank 1-40 (mis. Avanza #1, Raize #27), prefix targetnya (`TYT-AVZ`, `TYT-RZE`)
otomatis kepakai untuk SEMUA baris listing yang SKU-nya prefix itu, TERLEPAS dari
rank model itu sendiri — jadi Veloz (rank 52, sudah `TYT-AVZ` & sudah benar
harganya, 0 perubahan) dan Daihatsu Rocky varian A200 (rank 60, prefix `TYT-RZE`,
14 baris ikut naik) otomatis tersapu tanpa perlu whitelist manual. Reproses rank
1-23 yang "katanya sudah selesai" itu AMAN & idempoten (baris yang sudah benar
otomatis dilewati oleh `proses()` — `if lama == baru: continue`).

**Temuan sampingan**: ternyata #2 Honda Brio & #4 Honda Jazz (harusnya masuk grup
"23 sudah selesai") ikut BERUBAH (28 baris masing-masing, dari harga lama ke
harga baru) — jadi klaim "23 terlaris sudah diupdate" TIDAK 100% akurat, atau ada
listing yang balik ke harga lama sesudahnya. Dilaporkan ke user, tidak diam-diam
"dianggap benar".

**Bukti tambahan yang menguatkan koreksi arah Agya/Ayla & Rocky-lawas (lihat bagian
di atas)**: dicek langsung ke listing SHOPEE LIVE (bukan cuma riwayat memory) —
"Daihatsu Rocky" listing SUDAH memakai prefix `DHT-FRZ` utk varian F70/F300 dan
`TYT-RZE` utk varian Gen 2 (A200), PERSIS sama dengan arah yang baru dikoreksi di
`samakan_sku_kembar.py`. Listing produksi sudah lebih dulu benar sebelum master
lokal di branch ini menyusul.

**Hasil**: 364 SKU unik berubah (882 baris fisik di listing — banyak SKU muncul di
lebih dari 1 dari 5 file Shopee, halaman listing berbeda tapi produk fisik sama;
dicek eksplisit 0 SKU dengan harga TIDAK konsisten antar duplikat). Output:
`UPDATE_HARGA_UA_SHOPEE.xlsx` (siap upload Shopee Seller Center, format batch-edit
asli dipertahankan, cuma baris yang berubah yang disertakan). Verifikasi independen
(`verify_update_harga_uc.py`, baca ulang dari disk, TIDAK percaya laporan konsol
`update_harga_per_sku.py` sendiri): 6 cek, semua lulus — kelengkapan (tidak ada
baris seharusnya-berubah yang hilang), ketepatan (harga = target persis), tidak ada
baris ekstra di luar scope, cuma kategori R/S, XML bersih.

TikTok & Lazada UC belum disentuh batch ini (user cuma upload Shopee) — proses
sama persis begitu file TikTok/Lazada UC terbaru diupload (folder argumen tambahan
ke `update_harga_per_sku.py`, script sudah auto-deteksi channel per file).

## Soal "Luxio = Gran Max" (dicek 2026-08-20, TIDAK ketemu)

User bertanya apakah pernah dibahas "SKU Luxio disamakan dengan Gran Max karena
formula mirip". Dicek MENYELURUH: seluruh `claude-memory/` (semua file di branch
ini setelah digabung), `scripts/formula_config.py`, dan riwayat commit penuh
(`git log --all -S "Luxio"`) — **tidak ketemu** diskusi seperti itu. Yang ketemu
malah kebalikannya: master SENGAJA membedakan Gran Max Minibus (`DHT-GMX`) dan
Gran Max Pick Up (`DHT-GMXP`) sebagai 2 SKU terpisah (dikonfirmasi user 2026-07-27,
lihat `project-undercover-sku-sync-status.md` bagian "Bug matcher tipe-badan").
Kalau user mengingat pembahasan ini, kemungkinan ada di device/sesi lain yang belum
tersinkron ke branch manapun yang bisa diakses sesi ini — tanya user detail lebih
lanjut (tanggal kira-kira, konteks) sebelum menyimpulkan lebih jauh. Untuk sekarang,
Daihatsu Luxio memakai prefix `DHT-GMX` di listing OT (ditemukan 2026-08-20 saat
cek harga Otonation) tetap dianggap SALAH TAG SKU (bug), bukan keputusan sengaja.

---

## Eksekusi 2026-08-26: UC TikTok top-40 (menyusul batch Shopee)

User upload 3 file TikTok Seller Center ("all_information" template, sheet
`Template`+`Instruction`+`Brand`+dst) - persis pola lama yang sudah dikenal
(lihat bagian atas soal 2 varian template TikTok): **file 1 = cover motor**
(2 baris, di luar scope), **file 2 = travel pouch** (20 baris, di luar scope,
sesuai aturan bisnis #6), **file 3 = katalog cover mobil sungguhan** (22.657
baris, ini yang diproses). `update_harga_per_sku.py` auto-deteksi channel per
file (`deteksi_channel()`) jadi ke-3 file bisa langsung dilempar sekaligus ke
satu folder tanpa perlu memilah manual - file 1&2 otomatis 0 baris kena krn
prefix SKU-nya di luar scope 100 top-seller.

Metode sama persis dengan batch Shopee sebelumnya: rentang **1-40** (bukan
24-40) supaya kembar di luar 40 ikut tersapu otomatis lewat prefix SKU. Bukti
konsisten dgn batch Shopee: Daihatsu Rocky varian A200 (rank 60) ikut naik ke
Rp336rb/379rb lewat prefix `TYT-RZE` yang sama dengan Raize (#27); Honda Brio
(#2) & Honda Jazz (#4) SAMA-SAMA masih harga lama di TikTok juga (bukan cuma
Shopee) - menguatkan temuan sebelumnya bahwa klaim "23 terlaris sudah update"
tidak akurat utk kedua produk ini di SEMUA channel, bukan cuma satu.

**Bug lama yang masih ada, ikut terkoreksi sbg efek samping**: Toyota Raize
Strip di TikTok tercatat Rp252.000 (seharusnya ~Rp352rb) - pola "salah ketik
digit ratusan-ribu" yang sudah pernah dicatat (lihat bagian
"Temuan sampingan: harga TikTok kependekan Rp100.000" di atas). Overwrite ke
harga target (Rp379rb) otomatis memperbaikinya, tidak perlu penanganan khusus.

**Hasil**: 420 SKU unik / 952 baris fisik berubah. Output:
`UPDATE_HARGA_UA_TIKTOK.xlsx` (8 sheet dipertahankan utuh: Template,
Instruction, HiddenStyle, HiddenAttr, SpecialProductListingType,
TemplateConfig, Brand, SalePlatform - cuma isi baris di `Template` yang
berubah). `verify_update_harga_uc_tiktok.py`: 7 cek independen, semua lulus.

Lazada UC belum disentuh (belum diupload user) - tinggal tambahkan folder file
Lazada ke `update_harga_per_sku.py` kalau sudah ada, prosesnya identik.

---

## KOREKSI 2026-08-26: Honda Brio & Honda Jazz dipatok di lantai, BUKAN hasil spread

User tunjukkan screenshot Shopee Seller Center live: "Cover Mobil Honda Brio
Reguler" harganya **Rp332.000 (Reguler) / Rp375.000 (Strip)** — beda dari hasil
spread `harga_baru_matriks.py` yang menghitung Rp335.000/Rp378.000 (Brio bukan
mobil terpendek di grup City Car pcs=6, kalah dari S-Presso/Picanto/Karimun yang
dapat lantai persis Rp332rb).

Ditanyakan eksplisit ke user (AskUserQuestion, 2 opsi: tetap spread vs semua
flat) — **jawaban user: HANYA Brio & Jazz yang dipatok di lantai (332rb/375rb),
produk lain TETAP pakai hasil spread apa adanya.** Bukan perubahan metode
global, murni 2 pengecualian manual.

**Diterapkan** via `terapkan_override_brio_jazz.py` — override 2 baris di
`Harga Baru UC Top 100 (matriks).xlsx` (Reguler 335rb->332rb, Strip 378rb->375rb
utk Honda Brio Satya/RS & Honda Jazz), lalu `update_harga_per_sku.py` dijalankan
ulang dari file yang sudah dikoreksi itu (bukan logic override terpisah - file
target jadi satu-satunya sumber kebenaran). Hasil: Shopee 882->826 baris,
TikTok 952->896 baris (Brio/Jazz yang sudah live di 332rb/375rb otomatis
di-skip krn sudah benar, sisanya identik dgn sebelumnya). Kedua file
diverifikasi ulang (`verify_update_harga_uc.py`/`_tiktok.py`), semua lulus.

**Pelajaran**: kalau nemu 1 produk yang harga live-nya tidak cocok hasil
hitungan, JANGAN asumsikan salah satu (hitungan ATAU live) otomatis benar utk
SEMUA produk lain juga — tanya user scope-nya spesifik ke produk mana. Di sini
ternyata cuma 2 dari ~40 produk yang exception, bukan seluruh metode yang
salah.

---

## Eksekusi 2026-08-26 (lanjutan): grup Rocky lawas/Feroza/Taft GT ikut diupdate

User minta eksplisit: "Rocky gen awal" (F70/F300) diupdate juga karena "1 link
dengan Rocky gen 2" dan "SKUnya mirip dengan Taft" + "ada 1 lagi yg sama kode
SKUnya" — persis grup `DHT-FRZ` (Feroza + Rocky lawas + Taft GT) yang sudah
dikonfirmasi 2026-08-20.

Feroza sendiri rank **#49** di top-100 (bukan #51 - sempat salah tebak,
dikoreksi cepat via lookup langsung ke file). Target dibangun dari 2
pemanggilan `baca_harga()` terpisah (1-40 + 49-49 khusus Feroza) - BUKAN
rentang lebar 1-49, supaya rank 41-48/50 yang tidak diminta user (HiAce,
Mazda 2, Hardtop, Jimny, Ignis, BMW Seri 3, Picanto, Sirion) TIDAK ikut
ke-update tanpa diminta.

**Temuan penting yang butuh alias baru**: dicek langsung ke listing riil -
Rocky F70/F300 sudah pakai `DHT-FRZ` (benar), tapi **Daihatsu Taft GT masih
pakai prefix LAMA `DHT-TG`** (belum ikut migrasi SKU kembar ke listing).
Ditambahkan `ALIAS['DHT-TG'] = 'DHT-FRZ'` di `update_harga_per_sku.py` (pola
persis sama dengan alias lain yang sudah ada) supaya baris Taft GT tetap ikut
ter-update walau SKU-nya belum disinkronkan manual. Taft GT ternyata TIDAK
dijual di TikTok (0 baris ketemu di file TikTok, wajar - bukan bug).

Harga sebelum vs sesudah unifikasi (3 listing beda2, sekarang sama semua
382rb/425rb): Feroza 288rb/348rb, Rocky F70/F300 292rb/352rb (beda dari
Feroza walau SKU sama - bukti tambahan bahwa unifikasi ini memang belum
pernah diterapkan ke harga), Taft GT 288rb/348rb.

**Catatan Feroza Long (`DHT-FRL`) SENGAJA TIDAK ikut** — bukan anggota grup
ini (harga listing beda, sudah dikonfirmasi 2026-08-20), prefix-nya tidak
masuk target sama sekali jadi otomatis tidak tersentuh.

Script: `update_batch_1_40_plus_feroza.py` (reuse `baca_harga()`+`proses()`
langsung, bukan CLI). Hasil: Shopee 882 baris/364 SKU unik, TikTok 938
baris/406 SKU unik (naik dari batch sebelumnya krn tambahan Feroza+Rocky
lawas+Taft GT, Brio/Jazz tetap 0 baris sesuai override sebelumnya).
`verify_batch_1_40_plus_feroza.py`: 6 cek x 2 channel, semua lulus.

---

## Eksekusi 2026-08-26 (lanjutan): SKU Daihatsu Taft GT diubah ke DHT-FRZ

User minta eksplisit: "sekalian yg taft gt bantu ubah kode SKU nya biar pakai
kode SKU nya feroza juga" — bukan cuma harga (yang sudah dikerjakan via ALIAS
sebelumnya), tapi kode SKU di listing itu sendiri diubah permanen dari
`DHT-TG` jadi `DHT-FRZ`.

Digabung SEKALIGUS dengan harga baru (382rb Reguler/425rb Strip) dalam SATU
file (`ubah_sku_taft_gt.py` → `UPDATE_SKU_HARGA_TAFT_GT_UA_SHOPEE.xlsx`) —
BUKAN file terpisah untuk SKU vs harga, sesuai pelajaran lama "file update
marketplace menimpa SEMUA kolom, dua file dari basis beda akan saling
me-revert" (lihat `feedback-undercover-sku-sync-lessons.md` 2026-08-15).

14 baris (5 Reguler + 9 Strip), semua di Shopee UA file 1.xlsx baris
1037-1050 (Taft GT tidak dijual di TikTok). Setelah SKU diganti, nilainya
jadi PERSIS SAMA dengan SKU Feroza sendiri di baris lain (mis.
`DHT-FRZ-UA-R-G1-ABU`) — ini memang tujuannya (1 SKU fisik = 1 cover yang
sama), bukan bug/duplikat.

**PENTING - beda tingkat risiko dari update harga biasa**: ini mengubah kode
SKU (bukan cuma harga), yang mengalir ke SKU Gudang BigSeller & tracking stok
lintas channel. Setelah diupload, tidak ada jalan mudah untuk "batalkan" -
kalau salah, perlu perbaikan SKU lagi secara eksplisit. Setelah file ini
diupload, ALIAS['DHT-TG']='DHT-FRZ' di `update_harga_per_sku.py` jadi tidak
relevan lagi utk batch masa depan (SKU sumbernya sudah DHT-FRZ langsung),
tapi TIDAK PERLU dihapus - alias yang tidak pernah match itu aman, cuma
idle.

---

## Eksekusi 2026-08-26 (final): harga + SKU Taft GT digabung jadi 1 file Shopee

User belum sempat upload file harga sebelumnya - minta perubahan SKU Taft GT
(DHT-TG->DHT-FRZ) DIGABUNG ke file harga yang sama supaya cuma 1x upload.

`update_batch_1_40_plus_feroza_taftgt_sku.py` membangun ULANG dari 5 file
Shopee UA mentah (bukan edit file hasil sebelumnya) - target harga (1-40 +
Feroza #49) + langkah tambahan: kalau prefix ASLI baris = `DHT-TG`, kolom SKU
ikut ditulis `DHT-FRZ...`. Hasil: **882 baris, 1 file**
(`UPDATE_HARGA_UA_SHOPEE.xlsx`) - 868 baris cuma harga berubah, 14 baris
(Taft GT) harga+SKU berubah bareng.

TikTok TIDAK digabung ulang - dikonfirmasi ke user Taft GT memang tidak
dijual di TikTok (0 baris, sudah diverifikasi 2x independen). File TikTok
sebelumnya (`UPDATE_HARGA_UC_TIKTOK_1-40_v2/UPDATE_HARGA_UA_TIKTOK.xlsx`,
938 baris) tetap berlaku apa adanya.

`verify_batch_final.py` (independen dari script pembuat, baca ulang dari
disk): 6 cek termasuk pencocokan POSISI-DEMI-POSISI (bukan cuma set/dict)
supaya urutan baris ikut terverifikasi persis sama antara yang dihasilkan
script vs yang seharusnya menurut audit ulang dari 5 file sumber. Semua
lulus.

**File final yang berlaku untuk diupload user**:
- Shopee: `UPDATE_HARGA_UC_1-40_final/UPDATE_HARGA_UA_SHOPEE.xlsx` (882 baris,
  gabungan harga + SKU Taft GT)
- TikTok: `UPDATE_HARGA_UC_TIKTOK_1-40_v2/UPDATE_HARGA_UA_TIKTOK.xlsx` (938
  baris, harga saja, tidak ada Taft GT)

File-file versi sebelumnya (`UPDATE_HARGA_UC_1-40_v2/...`,
`UPDATE_SKU_HARGA_TAFT_GT_UA_SHOPEE.xlsx` terpisah) SUDAH TIDAK BERLAKU,
digantikan oleh file final di atas.

---

## 2026-08-26: TikTok batch-edit ERROR "sku not allow delete" - HANYA Toyota Hilux, produk lain semua sukses

User upload file hasil batch-edit TikTok Seller Center
(`Tiktoksellercenter_batchedit_20260826_all_information_result.xlsx`, sheet
Template, 56 baris gagal dari total 942 baris di
`UPDATE_HARGA_UC_TIKTOK_1-40_v2/UPDATE_HARGA_UA_TIKTOK.xlsx`). Semua 56 baris
gagal = **persis semua baris Toyota Hilux Reguler+Strip** (5 warna x 4 gen =
20 Reguler, 9 varian x 4 gen = 36 Strip), error seragam `"sku not allow
delete"`. Hilux Rangga (SKU beda, `TYT-HLR-...`) tidak kena, tidak termasuk
batch ini.

**Investigasi (bukan cuma baca error, tapi cross-check independen):**
1. Seller SKU Hilux (mis. `TYT-HLX-UA-R-G1-ABU`) memang KEMBAR di 4 baris
   variation_value berbeda (Gen 1-2/3-4/5-6/7-8) - konsekuensi normal TF=1
   (aturan #9 SKU sync). Dicek byte-per-byte: nilai seller_sku di file
   sumber listing (`tiktok_uc/3.xlsx`), file update kita, dan file error
   PERSIS SAMA - batch ini TIDAK mengubah SKU Hilux sama sekali, cuma harga
   (322rb->457rb Reguler, 382rb->500rb Strip). Jadi TikTok menolak update
   HARGA MURNI pada SKU yang sudah ada, bukan menolak perubahan SKU.
2. **Pola "SKU kembar lintas variation_value" BUKAN penyebab umum** - dicek
   distribusi cluster seller_sku kembar di seluruh 942 baris batch: Honda
   Accord (5 baris kembar/SKU), Mitsubishi Triton (6), Toyota Camry (6),
   Toyota Corolla (2-3), Mitsubishi Pajero Sport (3) - SEMUA berhasil update
   tanpa error, padahal pola strukturnya identik dengan Hilux (malah lebih
   besar clusternya). Ini menegaskan ULANG catatan lama "Shopee/TikTok boleh
   kembar" (lih. `project-undercover-sku-sync-status.md` baris 250) MASIH
   BENAR sebagai aturan umum - Hilux adalah ANOMALI produk spesifik, bukan
   bukti aturan itu salah.
3. Kesimpulan: kemungkinan besar ini lock/state di sisi platform TikTok yang
   spesifik ke product_id Hilux itu (mis. sisa promo/campaign aktif yang
   mengunci SKU, atau state SKU record yang belum sinkron sejak
   Hilux Rangga ditambahkan sbg varian) - BUKAN bug di file/script kita,
   dan tidak bisa didiagnosis lebih jauh dari data spreadsheet saja.

**Dampak & tindak lanjut**: 886/942 baris (semua produk lain + Feroza) sudah
sukses ter-update di TikTok. Harga Hilux Reguler (457rb) & Strip (500rb) di
TikTok BELUM berubah (masih 322rb/382rb) - perlu diupdate MANUAL langsung
di UI Seller Center (bukan batch-edit) untuk 2 tier itu saja. Kalau manual
juga gagal dgn pesan sama, itu tanda perlu hubungi CS TikTok Shop dgn
product_id `1729572004275521562`.

**How to apply**: kalau ada error batch-edit TikTok lagi, JANGAN langsung
simpulkan "SKU kembar = penyebabnya" - cek dulu apakah produk LAIN dengan
pola SKU-kembar yang sama di batch yang sama juga gagal (kalau tidak, bukan
soal SKU kembar secara umum, cek apa yang unik dari produk yang gagal itu
sendiri: histori edit terakhir, promo aktif, dll).

---

## 2026-08-26/27: File Hilux khusus TikTok + batch harga Lazada UA 1-40+Feroza

**File isolasi Hilux TikTok** (`update_harga_hilux_tiktok.py`) - target
`{'TYT-HLX': {'reguler':457000,'strip':500000}}`, sumber `tiktok_uc/`.
Hasil 56 baris, diverifikasi independen: `sku_id`-nya PERSIS SAMA dgn 56
`sku_id` yg gagal di file error batch besar (set diff kosong), harga semua
benar (Reguler 457rb, Strip 500rb sesuai kategori SKU). Dikirim ke user utk
dicoba upload terpisah - belum ada laporan hasil coba-upload-ulangnya.

**Batch harga Lazada UA #1-40 + Feroza #49** - user upload file export
"Harga & Stok" Lazada asli (`pricestock403342000257export...xlsx`, sheet
`template`, 21.133 baris, format INI SUDAH cocok dgn
SHEET/STARTROW/HEADER_KEY['lazada'] yg sudah ada di `update_harga_per_sku.py`
sejak awal - tidak perlu script baru, cukup panggil `proses()` langsung).
Script baru `update_batch_1_40_plus_feroza_lazada.py` cuma wrapper tipis.

Temuan sebelum proses: **Taft GT 0 baris di Lazada** (sama seperti TikTok,
dicek eksplisit nama "Taft" dan SKU "DHT-TG") - tidak perlu langkah ubah-SKU.
Rocky lawas (F70/F300) di Lazada ternyata SUDAH pakai prefix `DHT-FRZ`
tercampur dalam SATU produk "Daihatsu Rocky" bareng Rocky baru (`TYT-RZE`) -
beda dari Shopee yg masih pakai `DHT-TG` lama, jadi tidak perlu ALIAS
tambahan di Lazada.

Hasil: **1.400 baris berubah**, produk #11-40 + Feroza #49. Produk #1-10
(Avanza, Brio, Innova, Jazz, Ertiga, HR-V, Agya, Xenia/Veloz, Livina)
**0 baris** - dicek eksplisit ke source, ternyata harganya DI LAZADA SUDAH
BENAR sebelum batch ini (bukan gagal ke-match, memang sudah sinkron -
`proses()` sengaja skip baris yg sudah sama). Verifikasi independen: rekonstruksi
ulang baris-yg-harus-berubah langsung dari file sumber (bukan trust laporan
skrip) lalu dibandingkan POSISI-DEMI-POSISI ke file output - 1400/1400 cocok
persis.

Catatan format Lazada: SKU dasar yg kembar antar-generasi (TF=1, sama spt
Hilux di Shopee/TikTok) di Lazada DIBERI SUFFIX `_G1`/`_G3`/`_G5`/`_G7` dst
oleh sistem Lazada sendiri saat upload awal (utk penuhi syarat "Seller SKU
tidak boleh digandakan") - jadi Lazada TIDAK pernah benar-benar py SKU
identik di 2 baris, biarpun makna fisiknya sama. Kita cuma ubah kolom
Harga, kolom SKU tidak disentuh, jadi tidak melanggar aturan itu.

File hasil: `UPDATE_HARGA_UC_1-40_LAZADA.xlsx`.

---

## 2026-08-27: Isi template diskon Shopee OT (Otonation) top-100

User upload 3 file: `templatediscount.xlsx` (template diskon toko Shopee
kosong, kolom Kode Produk/Kode Variasi/Harga diskon dst - 9 kolom) + 2 file
export listing OT mentah (`1.xlsx`/`2.xlsx`, kena bug `activePane` yg sama,
diperbaiki `repair_xlsx.py`). User nanya sekaligus konfirmasi: "kemarin aku
di otonation cuma ubah 100 produk terlaris ya?" - dijawab lewat pencocokan
data, bukan tebakan.

Pencocokan pakai infrastruktur yg sama (`urai_sku`, `ALIAS`, `KECUALI`,
`is_outdoor_polos`, `resolve_cols`) thd `baca_harga(..., 1, 100)` dari
"Harga Baru UC Top 100 (matriks).xlsx" (target OT = target UC krn OT
konsolidasi stok ke UA - sudah established sejak `cek_harga_otonation.py`).
**Hasil: 3.262 baris, 98 produk unik** - PERSIS sama dgn angka total baris
yg ditemukan `cek_harga_otonation.py` sebelumnya (3.262), jadi terkonfirmasi
independen bahwa dugaan user benar: batch kemarin memang scope-nya top-100.

**70 baris ternyata beda antara harga LIVE di listing OT vs target resmi
matriks** - diputuskan isi kolom "Harga diskon" pakai TARGET RESMI, bukan
live, supaya tidak ikut menyebarkan masalah yg sudah diketahui ke kampanye
diskon baru:
- **Brio & Jazz, 56 baris** (28+28): live OT masih 335rb/378rb (harga
  spread lama, SEBELUM koreksi floor 332rb/375rb yg diputuskan user via
  screenshot Shopee - lihat eksekusi Brio/Jazz sebelumnya di file ini).
  OT belum ikut dikoreksi ke floor.
- **Suzuki Carry, 14 baris** (varian Gen 2F): live OT masih 315rb, vs
  target 382rb(R)/425rb(S) - ini persis temuan lama `cek_harga_otonation.py`
  ("Suzuki Carry Gen 2F stale, 14 baris") yg ternyata BELUM diperbaiki di
  listing OT sampai sekarang.

Kolom "Harga Awal" & "Batas Pembelian" sengaja dikosongkan (opsional di
template - biarkan Shopee pakai harga listing saat ini scr otomatis saat
kampanye jalan, tidak perlu kita tebak).

Script: `isi_template_diskon_ot_top100.py`. File hasil:
`TEMPLATE_DISKON_OT_TOP100_FINAL.xlsx`. Verifikasi independen dari disk:
3262 baris, 3262 kode_variasi unik (no duplikat), 0 baris dgn field wajib
kosong.

**How to apply**: kalau ada permintaan serupa lagi (isi template
diskon/promo dari data harga terpisah), field harga SEBAIKNYA diisi dari
sumber TARGET/RESMI, bukan nilai live listing saat itu - live listing bisa
saja belum sempat dikoreksi (kasus Brio/Jazz/Carry di atas), dan kampanye
diskon baru adalah kesempatan bagus utk sekalian membetulkan tanpa perlu
batch terpisah. Tapi WAJIB laporkan selisihnya ke user (jangan diam-diam),
krn user mungkin py alasan lain kenapa live-nya beda.

**Revisi 2026-08-27 (sama hari)**: user balas 2 hal soal file diskon di
atas - (1) Suzuki Carry Gen 2F sudah diperbaiki manual match ke Gen 2, (2)
kolom "Harga Awal" TERNYATA perlu diisi juga (bukan dikosongkan), dan
"Harga diskon" = **3% lebih murah dari Harga Awal**, dgn tegas: utk
Brio/Jazz basisnya 332rb (target resmi), BUKAN 335rb (harga live). Ini
justru MENGUATKAN keputusan sebelumnya pakai target resmi (bukan live) -
user sendiri yg minta demikian scr eksplisit, jadi keputusan "how to apply"
di atas terbukti benar.

Formula: `harga_diskon = harga_awal - (harga_awal*3)//100` (integer, exact -
semua target kelipatan Rp1.000, 3%-nya otomatis kelipatan Rp10, tidak ada
isu pembulatan). Diverifikasi independen: 3262 baris, kode_variasi unik
(no duplikat), rekalkulasi ulang tiap baris cocok 100%, Harga Awal Brio/Jazz
terkonfirmasi 332rb/375rb (bukan 335rb/378rb).

Script `isi_template_diskon_ot_top100.py` sudah direvisi ikut formula
final ini (Harga Awal + diskon 3%, bukan cuma Harga diskon = target polos).
File hasil final: `TEMPLATE_DISKON_OT_TOP100_3PERSEN.xlsx`.

**Revisi lanjutan (sama hari)**: user minta ganti persentase dari 3% ke
3,5%. Formula jadi `harga_diskon = harga_awal - (harga_awal*35)//1000`
(integer, tetap eksak krn semua target kelipatan Rp1.000). Diverifikasi
independen: 3262 baris, kode_variasi unik, kalkulasi 100% cocok. Script
`isi_template_diskon_ot_top100.py` diupdate ke 3,5% (fungsi `diskon35`).
File hasil final YANG BERLAKU: `TEMPLATE_DISKON_OT_TOP100_35PERSEN.xlsx`
(file `..._3PERSEN.xlsx` sebelumnya SUDAH TIDAK BERLAKU, digantikan). Kalau
user minta ganti persen lagi nanti, jangan asumsikan 3,5% ini permanen -
cek chat/memory terbaru dulu.

---

## 2026-08-27: SP/OP lanjut ke 292 model (v2) - ketemu bug drift - diperbaiki (v3)

User tanya status "update harga SP/OP terakhir sampe mana" (lihat status
sebelumnya: baru sampai file target 200 model, BELUM pernah dieksekusi ke
listing beneran). Lalu user upload `HPP_STP_OTP_.xlsx` versi baru dgn 92
model TAMBAHAN di sheet 'HPP 12%' (200 lama + 92 baru = 292, 0 dihapus).

**Verifikasi sebelum proses**: 200 model lama PERSIS SAMA di file baru
(nama, Pcs/Roll, harga mentah, URUTAN baris 2-201) - dicek eksplisit position-
by-position, 0 beda. Pcs/Roll 92 model baru semua masih di rentang lama
[3,4,5,6,7], TIDAK ada tier baru. **1 baris rusak di sumber**: "Ferrari F8
Tributo" (baris 263) - Pcs/Roll, Biaya Per PCS, HPP semua kosong (beda dari
3 Ferrari lain di sekitarnya yg datanya lengkap, Pcs/Roll=5, harga mentah
369.955 sama persis) - DIKECUALIKAN dari perhitungan, minta user lengkapi
dulu di sumber.

### v2 (`harga_baru_sp_op_matriks_v2.py`): 92 model diklasifikasi, TAPI ketemu bug drift

92 model baru diklasifikasi kategori+panjang pakai pengetahuan otomotif
umum (konvensi sama spt round 1). **1 nama ambigu: "Holden" tanpa model
spesifik** (Commodore/Kingswood/dll beda ukuran jauh) - dipakai placeholder
sedan besar ~4900mm, PALING PERLU dikoreksi user drpd yg lain di daftar.

Generate v2 lalu diverifikasi bandingkan ke v1 (200 model) → **ketemu 33
harga model LAMA ikut BERUBAH +-Rp1.000-3.000** (Brio, Jazz, Agya, Ayla,
Civic, Camry, Accord, Corolla, Hilux, dll) padahal cuma nambah model baru.
Root cause: rentang panjang-bodi min-max per grup (Pcs/Roll x Kategori)
dihitung ULANG dari SELURUH anggota grup (lama+baru) tiap generate, jadi
posisi proporsional mobil lama ikut geser kalau ada anggota baru masuk
dgn panjang lebih pendek/panjang dari rekor lama. Ditunjukkan konkret ke
user pakai contoh grup City Car Pcs/Roll=6 (Honda Brio Rp326rb->Rp327rb
gara2 DFSK Seres E1/Daihatsu Ceria/Fiat 500 masuk grup yg sama).

User: **"nanti tiap ada mobil baru yg dimasukkan bakal geser terus dong?"**
- benar, itu bug desain, bukan sekali-ini-saja. User juga nanya apa
rentang harusnya berdasar SELURUH mobil di master - dijawab: **master
TIDAK punya kolom panjang bodi (mm)**, itu klasifikasi manual dari
pengetahuan umum sejak awal, jadi cek master tidak menyelesaikan soal ini.

### v3 (`harga_baru_sp_op_matriks_v3.py`): FIX permanen + 1 aturan baru dari user

**Fix #1 - kalibrasi dikunci**: rentang (lo/hi/skala Rp-per-100mm) per
grup (Pcs/Roll x Kategori) SEKARANG DIHITUNG SEKALI dari 200 model LAMA
saja (`kalibrasi_grup()`), lalu dipakai ULANG (`posisi()`) utk memposisikan
SEMUA anggota (lama & baru). Anggota baru yg panjangnya di luar rentang
lama tetap dipetakan pakai skala yang sama, dibatasi 0..Rp5.000 (linear,
tidak pernah negatif/tidak pernah lewat cap). **Permanen ke depan** - kalau
ada tambahan model lagi nanti, kalibrasi TETAP dikunci dari 200 model ini
(bukan dari 292 atau berapa pun jumlah saat itu), supaya tidak drift lagi.
1 kombinasi grup (Pcs/Roll=6 x SUV besar) sama sekali tidak py anggota
lama (isinya cuma Chery Tiggo 8 baru) - dihitung dari anggota barunya
sendiri, jadi baseline baru ke depan utk grup itu.

**Fix #2 - 10 produk terlaris pakai harga TERENDAH**: permintaan eksplisit
user - Avanza, Brio, Innova, Jazz, Ertiga, HR-V, Agya, Ayla, Xenia, Livina
(No.1-10 di file, sama seperti urutan batch UC top-100) diisi HARGA
TERENDAH per tier Pcs/Roll-nya (lantai), BUKAN hasil spread. Contoh yg
dikonfirmasi user: Brio Rp322.000 (bukan Rp326rb), Avanza Rp370.000 (bukan
Rp373rb). Ditandai fill biru + kolom "Keterangan" di file hasil.

**Verifikasi independen (posisi per model, bukan cuma total)**: 190 model
lama (200 dikurang 10 top-floor) → 0 beda dari v1 (fix drift TERBUKTI
berhasil). 10 model top-floor → semua berubah sesuai formula lantai
(diharapkan/sengaja). 91 model baru (round 2, Ferrari F8 Tributo
dikecualikan) → semua punya harga masuk akal.

**File hasil final**: `Harga Baru SP-OP (matriks) FINAL.xlsx` (dari
`harga_baru_sp_op_matriks_v3.py`, 291 baris). v1/v2 file & script DITANDAI
SUPERSEDED di docstring (tetap disimpan, dict KATEGORI/PANJANG_MM-nya
masih dipakai/di-import oleh v3, JANGAN dihapus).

**Belum ada progres**: file ini masih tahap "harga target siap", BELUM
dieksekusi ke listing SP/OP yang sebenarnya (sama seperti status sebelum
sesi ini) - masih perlu file export listing Shopee/TikTok/Lazada SP & OP
terbaru kalau mau lanjut ke tahap update listing beneran.

**How to apply**: kalau desain "hitung ulang dari grup yang kebetulan ada
di 1 file run" ketemu lagi di skenario lain (bukan cuma SP/OP), curigai
pola yang sama - method yang recompute dari "anggota yang kebetulan hadir
saat ini" gampang drift kalau datanya bertahap nambah dari waktu ke waktu.
Solusi: kunci kalibrasi dari baseline yang sudah divalidasi, jangan
recompute from scratch tiap ada data baru.

---

## 2026-08-27: Audit + usulan SKU Smartprotection (SP) - 291 produk vs listing riil

User upload 2 file listing Shopee SP riil ("1.xlsx"/"2.xlsx", format
"sales_info" sama seperti file OT sebelumnya, kena bug `activePane` yang
sama, diperbaiki `repair_xlsx.py`). Tanya: apakah 291 produk yang ada di
"Harga Baru SP-OP (matriks) FINAL.xlsx" sudah semua terisi kode SKU.

**Iterasi pencocokan nama (PENTING - jangan ulang kesalahan ini)**: nama
produk di listing SP SERING BEDA dari nama di file harga:
- Brand didrop: listing "Feroza" (bukan "Daihatsu Feroza")
- Trim/suffix didrop: listing "Mitsubishi Pajero" utk target "Mitsubishi
  Pajero Sport"
- Kode tanpa strip: listing "Honda BRV"/"HRV"/"CRV"/"WRV" (bukan
  "BR-V"/"HR-V"/dst)
- Brand dobel di HPP_STP_OTP_.xlsx: "Mitsubishi Mitsubishi Outlander" dll
  (typo lama, tetap ada di target) vs listing "Mitsubishi Outlander" biasa
- Prefix "Body Cover Mobil / Sarung / Selimut Mobil" (bukan cuma "Cover
  Mobil / Selimut Mobil")

User SENDIRI yang nemuin 2 kasus pertama (screenshot Shopee: Pajero &
Feroza ternyata ADA + SKU-nya LENGKAP) setelah laporan audit pertama saya
salah bilang "tidak ditemukan" - HARUS diperbaiki matching-nya, bukan
percaya laporan pertama begitu saja. **How to apply ke depan**: kalau
audit lintas-nama (file harga vs listing riil) bilang "tidak ditemukan"
utk banyak produk, JANGAN langsung simpulkan produk itu belum dijual -
cek dulu apakah itu cuma soal nama beda (brand didrop, trim didrop, tanda
hubung hilang), coba alias 2-ARAH (bukan cuma "target adalah prefix
listing" tapi juga sebaliknya).

**Hasil final** (setelah matching diperbaiki): dari 291 target - **148
SKU lengkap semua, 36 sebagian kosong, 4 semua kosong, 103 tidak
ditemukan** (103 ini kemungkinan besar sebagian besar genuinely belum
dijual di SP - 66 dari 103 itu dari 91 model ronde-2 yg baru saja
ditambahkan sesi lalu, wajar; TAPI belum divalidasi 100% krn keterbatasan
matching nama, ada beberapa kandidat spesifik yg dicurigai sama tapi beda
nama: "Suzuki Vitara" (listing) vs "Suzuki Grand Vitara" (target), ada
juga TYPO brand di listing "Mitshubishi Xforce" yg bikin tidak ke-match ke
"Mitsubishi Xforce" - belum dikonfirmasi user, dicatat sbg temuan
terpisah, BUKAN diperbaiki otomatis krn XForce risiko keliru kalau
ternyata beda model).

**Total Formula (TF) - dikonfirmasi MASIH BERLAKU** (rule #9,
project-undercover-sku-sync-rules.md) - user tanya eksplisit apa masih
ada memory soal ini sebelum minta generate SKU baru, DIKONFIRMASI ada &
dipakai sbg pagar supaya tidak menebak generasi.

**Metode isi SKU kosong (urutan prioritas, semua diverifikasi dari data
riil produk itu sendiri, TIDAK ada yang ditebak dari luar)**:
1. Variant "Tahun Lain"/"Model Lain" -> SENGAJA dilewati (rule #4 lama,
   169 baris) - bukan gap, jangan diisi.
2. Sibling SAMA produk + SAMA tier (Reguler/Strip) + SAMA teks tahun yang
   SUDAH py SKU -> tinggal ganti segmen warna (31 baris, keyakinan
   TINGGI). **Bug yang sempat kejadian & diperbaiki**: percobaan pertama
   cuma cocokkan teks-tahun TANPA cek tier, jadi baris "Orange,2019-2026"
   (Reguler) sempat salah ambil kode dari sibling "Elite Merah,2019-2026"
   (Strip) - ke-detect sendiri sebelum dikirim ke user, diperbaiki dgn
   nambah syarat tier harus sama juga.
3. Fallback TF=1 seragam: kalau SEMUA baris produk itu yg sudah terisi
   cuma pakai 1 kode generasi bersih "G<n>" (bukan kode bucket "GB..."),
   generasi manapun yg kosong (walau tahun aslinya beda) ikut kode yang
   sama itu - VALID krn TF=1 sudah TERBUKTI dari data produk itu sendiri,
   bukan asumsi generik (58 baris: BMW X5, Holden, Hyundai Excel, dkk).
4. **TIDAK diisi** (249 baris): (a) 4 produk 0 SKU sama sekali - Honda
   Civic Hatchback (90), Honda Civic Type R (90), Mazda 2 Sedan (45),
   Daihatsu Espass (15). Prefix Civic Hatchback/Type R/Mazda 2 Sedan
   SUDAH diketahui dari `update_harga_per_sku.py` (HND-CVH, HND-CTR,
   MZD-2S) tapi skema generasinya belum bisa dipastikan tanpa sibling/
   master. Daihatsu Espass malah prefix-nya sendiri belum pernah ada.
   (b) **Hyundai Elantra (9 baris) - KENA bug "skema generasi ganda" yang
   SUDAH terdokumentasi 2026-07-18** (lihat project-undercover-sku-sync-
   status.md baris ~234-243, nama "Hyundai Elantra/Sonata" eksplisit
   disebut di situ) - kode campur G1/G3/G4/G5/G6/G7 DAN kode bucket-tahun
   GB20152020/GB20202024/G5F. Perbaikan yang benar WAJIB tarik dari file
   master 69-sheet asli sesuai metode yang sudah dicatat di situ, BUKAN
   ditebak dari file listing SP ini saja.

Script: `audit_dan_isi_sku_smartprotection.py` (gabungan audit + usulan,
versi final dari 4 iterasi cek_sku_smartpro*.py). File hasil:
`AUDIT_SKU_SMARTPROTECTION.xlsx` (status per produk) +
`USULAN_SKU_SMARTPROTECTION.xlsx` (89 SKU diusulkan + sheet "Tidak Diisi -
Perlu Info" utk 5 produk di atas).

**How to apply**: tabel kode warna SP (Reguler: Abu-abu=ABU/Hitam=HTM/
Biru Benhur=BRU/Merah=MRH/Hijau Army=GRN/Orange=ORG; Strip: Epic=S1/
Elite=S2/Warior=S3 + Abu=A/Biru=B/Merah=M, mis. "Epic Biru"->S1B) berlaku
umum, diverifikasi puluhan contoh lintas-brand - bisa dipakai lagi kalau
ada audit SKU serupa utk OP/OT/UA.

**Revisi sama hari - fallback typo brand ditambahkan**: user tunjukkan
LAGI 1 kasus via screenshot Shopee - "Mitsubishi Grandis" dilaporkan
"tidak ditemukan" padahal listingnya ADA (28/30 baris malah sudah py SKU,
cuma FORMAT LAMA "CVR0029-STP-RPA" dst, bukan format MEREK-MODEL-TOKO-KAT-
GEN-WARNA modern). Root cause: listing riilnya TYPO "Mistubishi Grandis"
(huruf ketuker), sama pola dgn "Mitshubishi Xforce" yg sudah ketemu
sebelumnya tapi belum di-generalisasi jadi perbaikan matching.

Ditambah fallback fuzzy (Levenshtein) KHUSUS kata pertama (brand): jarak
edit <=2, panjang kata asli >=5 huruf, DAN kata-kata lain + JUMLAH kata
WAJIB sama persis. **Sempat false-positive** sebelum syarat "jumlah kata
sama" ditambah: "Ford Fusion" (2 kata) kepancing cocok ke alias "Forsa"
(1 kata, hasil brand-didrop dari target "Suzuki Forsa") krn cuma
bandingkan kata pertama tanpa cek sisa kata ada/tidak. **How to apply**:
fuzzy-match brand HARUS disertai syarat jumlah-kata-sama, jangan cuma
"kata pertama mirip" - kalau tidak, alias pendek (hasil brand/trim-didrop)
gampang menyedot listing yang secara kebetulan py kata pertama mirip tapi
sebenarnya model yang SAMA SEKALI beda.

Hasil setelah fix: **148 lengkap, 37 sebagian kosong, 5 semua kosong** (naik
dari 4 - Mitsubishi Xforce ketemu listingnya tapi ternyata 0 SKU sama
sekali, masuk daftar "perlu prefix dari luar" bareng Civic H/TypeR/Mazda2
Sedan/Espass), **101 tidak ditemukan**. Grandis: 2 baris Orange
diusulkan pakai pola LEGACY 1-huruf yang sama persis skemanya dgn tabel
warna modern cuma disingkat 1 huruf (A/H/B/M/G utk 5 warna Reguler yang
sudah ada) -> Orange = "O", jadi "CVR0029-STP-RPO" (medium confidence,
beda dari sibling-copy yang high-confidence krn ini skema legacy yg baru
pertama kali ditemukan, bukan yang sudah divalidasi berulang spt ORG).

Total SKU final yang diusulkan: **91** (89 skema modern + 2 Grandis legacy).
File final: `AUDIT_SKU_SMARTPROTECTION.xlsx`, `USULAN_SKU_SMARTPROTECTION.xlsx`.
Script `audit_dan_isi_sku_smartprotection.py` diupdate dgn fungsi
`levenshtein()`+`match_fuzzy()`.

**Lanjutan sama hari - scan lebih luas + file upload**: user minta cek
produk LAIN dgn kasus serupa (typo/nama beda) sebelum lanjut apply SKU.
Scan whole-name Levenshtein (bukan cuma kata brand) thd 101 sisa "tidak
ditemukan" vs semua nama listing yg genuinely tidak match apapun (14 nama
unik) - hasil 9 kandidat mirip, tapi **7 dari 9 adalah FALSE ALARM**
(model REAL yang beda, cuma kebetulan mirip krn nomor/kode pendek):
Peugeot 3008 vs 5008 (beda mobil), Mercedes GLB vs SLK Class (beda segmen
total), Peugeot 306 vs 405, Hyundai Matrix vs Staria, Nissan Latio vs
Note, Volkswagen Fox vs Scirocco, Wuling Darion vs Alvez - SEMUA dicek
manual pengetahuan otomotif, BUKAN typo, jangan digabung.

**2 kandidat TERVERIFIKASI benar** (dicek prefix SKU yg sudah dipakai
listing, bukan cuma mirip nama):
- **"Suzuki Vitara"** (listing) = target **"Suzuki Grand Vitara"** -
  prefix listing `SZK-GVT`/`SZK-GVH` (Gen1-3/Gen4) + varian "e Vitara"
  (`SZK-EVT`) semua di-bundle dlm 1 produk - persis "Grand Vitara" cuma
  judul listing dipendekkan. SUDAH lengkap semua SKU-nya (tidak perlu
  usulan baru).
- **"Toyota 86"** (listing) = target **"Toyota GR 86"** - prefix listing
  `TYT-G86` utk Gen1(2012-2021)/Gen2(2021-2023). Sudah lengkap juga
  (blank yg ada semua "Tahun Lain", sengaja dikosongkan).

Ditambahkan sbg `ALIAS_MANUAL_TERVERIFIKASI` di script (terpisah dari
alias otomatis krn butuh verifikasi prefix manual per kasus, JANGAN
tambah alias baru ke situ tanpa cek prefix SKU eksisting dulu). Hasil
akhir: **149 lengkap, 38 sebagian kosong, 5 semua kosong, 99 tidak
ditemukan**. (Catatan: Toyota GR 86 kehitung "sebagian kosong" bukan
"lengkap" krn 14 baris "Tahun Lain"-nya tetap kehitung "kosong" di
status kategori audit, walau itu memang sengaja dikosongkan - bukan
gap beneran, cuma cara kategorisasi status yg belum bedakan alasan.)

**File upload dibuat**: `UPDATE_SKU_SMARTPROTECTION.xlsx` - format PERSIS
sama dgn file sumber (`sales_info` Shopee, kolom Kode Produk/Nama Produk/
Kode Variasi/Nama Variasi/SKU Induk/SKU/Harga, header baris 1-6 disalin
dari file asli), 91 baris = 91 SKU yg diusulkan di atas, Harga TIDAK
diubah (disalin apa adanya dari sumber, cuma kolom SKU yang beda).
Diverifikasi independen: 91 baris, 91 Kode Variasi unik (no duplikat),
0 baris SKU kosong, 0 baris Harga kosong. User belum konfirmasi hasil
upload-nya ke Shopee - kalau upload gagal (mis. "sku not allow delete"
spt kasus TikTok Hilux sebelumnya), catat di sini juga.

**Revisi sama hari - user minta "format sama persis kayak di Shopee"**:
versi pertama dibuat dari `openpyxl.Workbook()` KOSONG (cuma 7 kolom nilai
polos, tanpa style/lebar-kolom/sheet lain dari file asli) - beda dari pola
yang SUDAH TERBUKTI berhasil sepanjang proyek ini (`update_harga_per_sku.py`
`proses()`/`salin()`: klon UTUH file sumber via
`openpyxl.load_workbook(path, data_only=False)`, timpa baris data yg
perlu, JANGAN bikin workbook baru dari nol). Diperbaiki: klon file
`sp_sku_fixed/1.xlsx` utuh (semua style/format/lebar kolom ikut), timpa 91
baris data (91 baris ini asalnya CAMPUR dari file-1 & file-2, karena
target row-output r_out=7+i tidak selalu = row sumber r).

**Bug ditemukan & diperbaiki saat verifikasi**: kolom di luar 7 kolom yang
kita isi (GTIN, **Stok**, Min/Maks Pembelian, dst, sampai kolom O) di file
sumber TERNYATA ADA ISINYA (mis. kolom Stok = "5" di HAMPIR SEMUA baris,
bukan kosong) - kalau tidak dibersihkan, baris output yang datanya berasal
dari FILE-2 tapi menempati posisi baris FILE-1 (krn kita gabung 2 sumber
jadi 1 output berurutan) akan KEBAWA nilai kolom Stok dkk milik baris
FILE-1 yang TIDAK RELEVAN - risiko upload Shopee menimpa Stok produk
dengan angka yang salah/nyasar. **WAJIB kosongkan eksplisit kolom di luar
yang benar-benar kita isi**, jangan asumsikan kolom lain sudah kosong dari
sono cuma karena headernya tidak kita pakai.

**Bug kedua, lebih halus - openpyxl `.cell(row, col, value=None)` adalah
NO-OP, BUKAN mengosongkan sel**: percobaan pertama "kosongkan" pakai
`ws.cell(r, c, value=None)` GAGAL DIAM-DIAM (nilai lama TETAP ada, bahkan
di in-memory sebelum save) - openpyxl memperlakukan `value=None` sbg
"jangan diisi apa-apa" (parameter default sentinel), BUKAN instruksi
"set value jadi None". **Cara benar**: ambil dulu objek sel
(`cell = ws.cell(r, c)`), baru assign atribut langsung
(`cell.value = None`). **How to apply**: kapan pun perlu MENGOSONGKAN sel
lewat openpyxl (bukan cuma ganti isi), selalu pakai assignment atribut
langsung, JANGAN lewat parameter `value=` di pemanggilan `.cell()` -
sudah kejadian nyaris lolos ke user krn verifikasi awal cuma cek
"SKU kosong?"/"Harga kosong?" makanya luput, ketauan setelah user minta
cek format lebih teliti dan verifikasi diperluas ke SEMUA kolom.

File final (sudah benar): `UPDATE_SKU_SMARTPROTECTION.xlsx` - klon utuh
struktur Shopee asli, 91 baris terisi (kolom 1-7), kolom 8+ eksplisit
kosong, tidak ada baris/sel nyasar.

---

## 2026-08-27: Lanjutan - klarifikasi Vitara/Xforce "stale file", scan lebih dalam, + 3 produk 0-SKU diisi pakai skema sibling body-style

**Klarifikasi penting**: user screenshot Shopee tunjuk baris "Suzuki Grand
Vitara" & "Mitsubishi Xforce" = "Tidak Ditemukan" di file audit - itu versi
FILE LAMA (sebelum alias manual Vitara/86 ditambahkan). Versi TERBARU
sudah benar (Vitara="Lengkap", Xforce="Semua Kosong" krn listing-nya
ketemu via fuzzy typo-fix tapi SKU-nya beneran 0). **Pelajaran: kalau
kirim file dgn NAMA SAMA berkali-kali, user bisa nyasar ke versi lama yg
sempat didownload - selalu tegaskan versi/angka terbaru di pesan, jangan
asumsikan user otomatis liat versi paling akhir.**

**Scan lebih dalam** (kata kunci paling distinctive tiap target "tidak
ditemukan" dicari sbg substring di SEMUA nama listing, bukan cuma yg
belum match): 10 kandidat ketemu, **7 FALSE POSITIVE** (kata generik yg
kebetulan sama - "Cross"/"Sedan"/"Class"/"Max"/"Pickup" muncul di banyak
mobil BEDA total): Datsun Cross vs Yaris Cross/Xpander Cross, Mitsubishi
L300 Pickup vs Suzuki Carry Pickup, Mercedes SLK vs Class lain, Volvo 850
Sedan vs Sedan lain, Daihatsu Hi Max vs Gran Max. **3 perlu dicatat tapi
TIDAK digabung** (beda dari Vitara/86 krn TIDAK ada bukti prefix
konklusif): Kia Grand Carnival (listing "Kia Sedona / Carnival" SUDAH
ke-assign ke target "Kia Sedona" - kemungkinan sama/kembar, tapi jangan
paksa 1 listing ke 2 target), Jeep Wrangler vs Wrangler Rubicon (kasus
lama yg sudah didokumentasikan ambigu, lihat sku-sync-status.md), Toyota
GR Corolla vs Corolla biasa (beda tier/harga, tidak ada bukti prefix sama
spt kasus GR86).

**3 produk 0-SKU diisi** pakai metode baru: **pinjam skema generasi dari
"sibling body-style"** (model sama, badan beda, biasanya SATU nameplate
py TF yg konsisten lintas body-style) - BUKAN nebak, tapi baca dari data
riil yg SUDAH disinkron:
- **Honda Civic Hatchback** (prefix `HND-CVH`, sudah diketahui) & **Honda
  Civic Type R** (`HND-CTR`) - pinjam skema dari **Honda Civic Sedan**
  yang SUDAH lengkap: TIDAK collapse, tiap generasi asli (Gen6-11) py kode
  sendiri PERSIS sama dgn angka generasinya (Gen 8 -> G8, dst) - dicek
  variant teks Hatchback/Type R MEMANG pakai label "Gen 6-11" yang SAMA
  persis dgn Sedan (bukti kuat body-style yg sama, generasi yg sama).
- **Mazda 2 Sedan** (prefix `MZD-2S`) - pinjam skema dari **Mazda 2
  Hatchback** yang sudah lengkap: TF=1 (semua 3 generasi asli collapse ke
  G1) - beda dari Civic, jadi TIDAK bisa asumsikan 1 pola generik "semua
  ikut Sedan-nya" - tiap nameplate WAJIB dicek sibling-nya sendiri.

Total 225 baris baru (90+90+45). **Mitsubishi Xforce, Daihatsu Espass
TETAP tidak diisi** - keduanya TIDAK py sibling body-style dalam katalog
SP (nameplate berdiri sendiri), jadi tidak ada data riil utk dipinjam;
Espass bahkan prefix-nya sendiri belum pernah ada. Hyundai Elantra tetap
diblok krn bug skema-ganda yg sudah didokumentasikan (lihat entri
sebelumnya).

**Total SKU final: 316** (91 sebelumnya + 225 baru). File final (format
klon Shopee asli, sudah lulus semua verifikasi termasuk cek kolom 8+ &
duplikat): `UPDATE_SKU_SMARTPROTECTION.xlsx`, `USULAN_SKU_SMARTPROTECTION.xlsx`
(3 warna beda utk 4 metode: hijau=sibling exact, kuning=TF1 seragam,
oranye=borrow sibling body-style, kuning-tua=legacy 1-huruf).

**How to apply ke depan**: kalau ketemu produk 0-SKU lagi, SEBELUM
menyerah/minta master file, cek dulu apakah nameplate itu py "saudara
body-style" lain (Sedan/Hatchback/Coupe dari model yang sama) yang SUDAH
tersinkron di katalog yang sama - kalau ada, pinjam skema generasinya
(cocokkan dulu apakah label generasi/tahun di teks variannya identik,
baru boleh pinjam). Kalau tidak ada sibling sama sekali, itu baru
genuinely butuh master file/keputusan user, jangan ditebak.

---

## 2026-08-27: Xforce dapat prefix dari listing UA + Grandis migrasi penuh ke format modern

User screenshot listing **Undercover Autocare (UA)** utk Mitsubishi
Xforce - SUDAH py SKU modern `MTB-XFO-UA-R-G1-<warna>` (1 generasi saja,
"Gen 1 2023-2026", wajar krn model masih baru). **Sumber prefix baru: cek
listing TOKO LAIN (UA/OT/SP/OP) kalau ada yg SUDAH sinkron** - prefix SKU
sama lintas toko (cuma segmen ke-3 "TOKO" yg beda per store, sesuai format
`MEREK-MODEL-TOKO-KAT-GEN-WARNA`), jadi kalau UA sudah py, tinggal
"disesuaikan" (ganti segmen toko UA->SP, generasi Gen1 SP jg 2023-2026 -
SAMA PERSIS shg gcode G1 langsung dipakai tanpa perlu translate).
**How to apply**: utk produk 0-SKU yg BUKAN py sibling body-style, coba
minta user cek listing toko LAIN dulu sebelum simpulkan "butuh master
file" - kadang toko lain sudah lebih dulu disinkron manual.

Hasil: **15 baris Mitsubishi Xforce** terisi prefix `MTB-XFO` (toko SP).

**Mitsubishi Grandis - user pilih migrasi PENUH ke format modern** (bukan
cuma isi 2 baris kosong pakai skema legacy spt sebelumnya). Prefix modern
`MTB-GRA` sudah KETEMU dari varian Transparan-nya sendiri
(`MTB-GRA-SP-T-G1-TRP`, di luar cakupan harga tapi berguna sbg referensi
prefix) - brand ini kelihatan lagi "setengah migrasi" (Transparan sudah
pindah, Reguler/Strip belum). **30 baris (28 yg SUDAH py SKU legacy +
2 yg kosong) SEMUA ditimpa** ke `MTB-GRA-SP-<KAT>-G1-<WARNA>` (G1 seragam,
konsisten dgn kode Transparan & pola legacy lama yg jg TF=1 - 2 generasi
asli 2011-2018/2018-2022 sama2 G1).

**PENTING - ini beda jenis operasi dari batch2 sebelumnya**: 28 dari 30
baris Grandis ini MENIMPA SKU yang SUDAH ADA (bukan cuma isi kosong) -
ditandai terpisah "MIGRASI" (fill oranye di file update, beda dari kuning
utk isi-baru biasa) supaya user sadar ini perubahan SKU pada baris yg
sebelumnya sudah aktif dipakai (ada histori penjualan/stok terikat ke SKU
lama), bukan sekadar mengisi yang kosong.

**Total SKU final: 359** (314 sebelumnya - 2 Grandis-lama-legacy yg
digantikan + 15 Xforce + 30 Grandis-migrasi). **Tersisa 2 produk blocked**:
Daihatsu Espass (15, masih butuh prefix - user diminta cek listing UA/toko
lain jg spt Xforce kalau ada) & Hyundai Elantra (9, bug skema-ganda,
butuh master file). File final (sudah terverifikasi 0 sel nyasar, 0
duplikat, 0 kosong): `UPDATE_SKU_SMARTPROTECTION.xlsx`,
`USULAN_SKU_SMARTPROTECTION.xlsx`.

**Lanjutan sama hari - Espass selesai, Elantra TETAP tidak bisa walau ada
referensi UA**: user kasih screenshot UA utk Daihatsu Espass (`DHT-ESP`,
1 generasi doang - cocok persis dgn data SP yg emang cuma bare-color tanpa
info generasi) - **15 baris diisi langsung**, aman krn simpel & tidak ada
ambiguitas skema.

User JUGA kasih screenshot UA utk Hyundai Elantra (Gen1 1990-1995->G5,
Gen2 1995-2000->G5F, Gen3 2000-2006->G6), tanya "bisa ambil dari referensi
UA kan?" - **JAWABANNYA TETAP TIDAK**, beda dari Xforce/Espass. Alasan:
**referensi UA ini justru mengungkap 3 SISTEM PENOMORAN GENERASI YANG
SALING BEDA, bukan cuma 1 sistem yang tinggal disalin**:
1. SP tier Reguler: per-generasi asli (G1 utk Gen1&3, G4, G5, G6, G7)
2. SP tier Strip: CAMPUR - G1 utk Gen1&3 (sama dgn Reguler), TAPI
   GB20152020 utk Gen2&5&6 dan GB20202024 utk Gen7 (BEDA sistem dari
   Reguler, walau row Gen/tahun yg SAMA - bukti: Gen2:1995-2000 Reguler=
   `G5F` tapi Strip=`GB20152020`, DUA KODE BEDA utk SATU generasi yg sama)
3. UA: py rentang tahun SENDIRI yg beda dari SP (UA py "Gen1 1990-1995"
   yg SP TIDAK PUNYA entrinya sama sekali - SP entri paling awal adalah
   "Gen2 1995-2000")

Dengan 3 sistem yang tidak sinkron ini, assign kode ke 9 baris kosong
(Strip Gen4) beresiko GENUINELY SALAH - tidak ada cara aman menyimpulkan
apakah Strip-Gen4 harus ikut pola Reguler-nya sendiri ("G4", konsisten
dgn Gen1&3) atau ikut pola bucket Strip-nya sendiri (butuh tau rentang
bucket yg benar, yg TIDAK ketahuan dari data manapun yg ada). **How to
apply**: referensi toko lain (spt Xforce/Espass) cuma valid dipakai kalau
skema-nya SATU & KONSISTEN - begitu ketemu bukti ada >1 sistem berbeda yg
tumpang tindih (skema ganda), referensi toko lain JUSTRU menambah bukti
kompleksitas, bukan menyelesaikannya - tetap wajib master file.

**Total SKU final: 374** (359 sebelumnya + 15 Espass). Tersisa HANYA
Hyundai Elantra (9 baris) yang blocked.

---

## 2026-08-27: Elantra ternyata BISA - "skema ganda" itu bug penulisan, bukan 2 sistem valid

User tidak terima kesimpulan "butuh master file" - curiga "ada bug di
penulisan", minta diperbaiki. **User benar** - setelah re-analisis lebih
teliti (bukan cuma voting kode dari SEMUA baris campur tier, tapi voting
KHUSUS dari tier Reguler yg sudah terbukti bisa dipercaya): ternyata
kode "GB20152020"/"GB20202024" itu MUSTAHIL valid - **1 kode bucket yg
SAMA dipakai utk 3 GENERASI ASLI BERBEDA** (GB20152020 dipakai baik utk
Gen2:1995-2000, Gen5:2010-2015, MAUPUN Gen6:2016-2020 - jelas salah,
tidak mungkin 1 kode benar utk 3 rentang tahun yg beda total). Ini genuine
bug, BUKAN skema kedua yang sah.

**Metode fix**: hitung kode "benar" per generasi asli dari KONSENSUS tier
Reguler SAJA (5-6 baris per generasi, semuanya SUDAH benar & konsisten
KECUALI 2 baris "Orange" yang nyimpang sendiri - itu juga bug penulisan
terpisah, ke-expose otomatis krn kalah suara vs 5 warna lain). **JEBAKAN
yang sempat kejadian**: percobaan PERTAMA voting dari SEMUA baris (R+S
digabung) - Strip py 9 baris/generasi vs Reguler cuma 5-6, jadi kode
BUCKET YANG SALAH malah MENANG VOTING (menang jumlah baris) dan hasilnya
JUSTRU mau nimpa kode Reguler yang BENAR jadi ikut kode bucket yang SALAH
- arahnya kebalik. **Ketauan sebelum dikirim ke user** krn hasil awal
"Orange,Gen6->GB20152020" kelihatan aneh dibanding pola yg sudah
dikonfirmasi. **How to apply**: kalau voting mayoritas dipakai utk
nentuin "kode benar", PASTIKAN sumber suara itu representatif/reliable
dulu - jangan campur sumber yang levelnya beda kepercayaannya (di sini:
Reguler = SUDAH terbukti bersih dari cross-check lain, Strip = JUSTRU
yang dicurigai salah) dalam 1 kotak suara yang sama, nanti yang salah
malah menang krn jumlah baris lebih banyak.

Hasil: **47 baris Elantra diperbaiki** (2 koreksi di Reguler yg salah
"Orange", 36 koreksi kode bucket Strip yg salah jadi kode Reguler yg
benar per generasi, 9 isi baris Strip Gen4 yang kosong). **Total SKU
final: 421** (374 + 47) - **SEMUA produk yang ketemu di listing SP kini
sudah 0 gagal**, tidak ada lagi yang "blocked".

**How to apply ke depan (paling penting)**: kalau ketemu lagi kasus
"skema generasi kelihatan campur/tidak konsisten", JANGAN langsung
simpulkan "butuh master file" - cek dulu apakah itu genuinely 2 sistem
valid, atau cuma 1 sistem yang lagi RUSAK di sebagian baris (bukti: kode
yang sama dipakai utk >1 generasi asli yang beda rentang tahunnya =
mustahil valid, itu tanda bug bukan sistem paralel). Voting dari sumber
yang SUDAH terbukti bersih (baris lain di produk yang sama, tier lain,
dst) seringkali cukup - tidak selalu perlu file eksternal.

---

## 2026-08-27: KOREKSI - fix Elantra "voting dari Reguler" SALAH, harusnya literal Gen->G<n>

**Fix di atas (47 baris, voting dari tier Reguler) ITU SENDIRI SALAH.**
User mempertanyakan lagi: "kenapa Gen 3 tapi kode SKU -G1-? harusnya
sesuai nama variasinya (Gen3->G3), atau sesuaikan formulanya kalau ada."
Ini nunjukkin kekeliruan metodologi yang lebih dalam: **saya keliru
menyamakan "konsisten" dengan "benar"** - kode G1/G5F yang ada di tier
Reguler itu SENDIRI kemungkinan sudah salah dari awal (bukan cuma Strip
yang salah), cuma karena konsisten dipakai berulang saya asumsikan itu
"ground truth" tanpa verifikasi independen ke sumber otoritatif.

User upload `Data_Mobil_Lebih_dari_1_Formula_3.xlsx` (Sheet2, 1305 baris,
sama seperti versi lama yang didokumentasikan di
`project-undercover-bigseller-sync.md`/`sku-sync-status.md` - format
kolom No/Nama Mobil/Generasi/Total Formula/Notes, data mulai baris 4).
**Hyundai Elantra TIDAK ADA di file ini** (dicek eksplisit, 12 entri
Hyundai lain ada: Creta, Stargazer, Palisade, Atoz, Santa Fe, Avega,
Tucson, Avega Hatchback, Getz, Kona, Accent, Excel - Elantra tidak
termasuk). **Aturan fallback dari user**: kalau mobil TIDAK ada di file
formula, pakai **literal**: "Gen N" -> `G<N>`, "Gen N Facelift" -> `G<N>F`.

Dihitung ULANG dari nol (bukan nambal 47 sebelumnya): 65 dari 90 baris
Elantra (non-Transparan) ternyata perlu diubah ke skema literal murni -
LEBIH BANYAK dari 47 sebelumnya, krn skema literal mengoreksi JUGA baris
Reguler Gen2/Gen3 yang tadinya saya anggap "benar" (padahal salah:
Gen2 seharusnya G2 bukan G5F, Gen3 seharusnya G3 bukan G1). Gen4/5/6/7
Reguler KEBETULAN sudah benar sejak awal (angka literalnya emang sudah
cocok), makanya cuma sebagian yang perlu diubah.

**Total SKU final: 439** (374 + 65, menggantikan 47 versi sebelumnya
sepenuhnya). Semua 90 baris Elantra (non-Transparan, non-"Tahun Lain" -
tidak ada Tahun Lain di produk ini) kini konsisten literal.

**How to apply ke depan (KRITIS, revisi dari lesson sebelumnya)**:
1. **JANGAN PERNAH anggap kode yang sudah ada di listing itu "benar"
   hanya karena konsisten/berulang** - konsistensi cuma bukti "sengaja
   ditulis begitu", BUKAN bukti "sesuai aturan resmi". Source of truth
   SEBENARNYA adalah file Total Formula (`Data_Mobil_Lebih_dari_1_Formula
   _N.xlsx` Sheet2) - kalau model ADA di situ, ikuti Total Formula-nya
   (grup->kode generasi pertama di grup, TF=1->G1 semua). Kalau TIDAK ada
   di situ, defaultnya LITERAL (Gen N -> GN, Gen N Facelift -> GNF) -
   BUKAN "samakan ke tier/baris lain yang kelihatan konsisten".
2. Voting/konsensus dari data internal (tier lain, sibling, dst) HANYA
   valid dipakai kalau TIDAK ADA cara memverifikasi ke sumber otoritatif
   (file formula) - begitu file formula bisa dicek, itu SELALU menang
   dari konsensus internal, walau konsensus internal kelihatan "rapi".
3. File formula ini TIDAK cover semua model (Elantra tidak ada) - kalau
   model tidak ketemu di situ, JANGAN diam2 pakai kode yang sudah ada di
   listing (bisa jadi warisan bug lama) - tanya user aturan default
   (literal) baru dipakai, seperti kasus ini.

---

## 2026-08-29: Propagasi 439 SKU final Smartprotection ke Lazada & TikTok

Setelah 439 SKU final Shopee SP selesai (`UPDATE_SKU_SMARTPROTECTION.xlsx`),
user upload export Lazada & batch-edit TikTok baru (SP juga) dan minta
dibuatkan file update SKU utk 2 platform itu, dibundel bareng Shopee.

**Beda mendasar dari pembuatan file Shopee**: file Shopee dibangun dgn
KLON row dari 2 file sumber ke template baru (perlu null-out kolom lain,
lihat lesson 2026-08-27 di `feedback-undercover-sku-sync-lessons.md`). Di
Lazada/TikTok cukup EDIT IN-PLACE 1 file per-platform - isi ulang 1 kolom
(`Seller SKU` Lazada = kolom 13 sheet `template`; `seller_sku` TikTok =
kolom 11 sheet `Template`) di baris yg cocok, kolom lain tidak disentuh
sama sekali (tidak ada operasi copy-row, jadi tidak ada risiko "kebawa
data kolom lain").

**Tantangan sebenarnya: MATCHING lintas platform**, krn teks
varian/produk tidak seragam persis antar Shopee/Lazada/TikTok:
1. Typo brand beda PER PLATFORM utk produk yg SAMA - Shopee (sumber
   lookup) tulis "Mitshubishi Xforce" (typo), tapi Lazada/TikTok tulis
   BENAR "Mitsubishi Xforce" - kalau key lookup dibangun mentah2 dari nama
   Shopee, Xforce di Lazada/TikTok TIDAK AKAN PERNAH ketemu. Sebaliknya
   "Mistubishi Grandis" (typo beda) KONSISTEN di ketiga platform, jadi
   tidak masalah. Fix: normalisasi typo brand yg SUDAH diverifikasi
   (`TYPO_FIX` di script) diterapkan ke SEMUA platform sebelum jadi key,
   bukan cuma satu arah.
2. Teks tahun beda platform utk GENERASI YANG SAMA - Shopee/TikTok bilang
   Honda Civic Hatchback "Gen 10 (2015-2021)"/"Gen 10 : 2015-2021", tapi
   Lazada utk baris yg SAMA malah "Gen 10 : 2016-2021" (beda 1 tahun).
   Key lookup awal include teks tahun literal -> gagal cocok padahal
   generasinya sama. Fix: key dibangun dari NOMOR GENERASI ("Gen N") kalau
   ada, teks tahun/sisa cuma jadi disambiguator tambahan ("leftover")
   utk produk yg TIDAK punya "Gen N" sama sekali (mis. Mini Cooper "3
   Pintu" vs "5 Pintu").
3. TikTok collapse variasi tahun jadi 1 baris per warna utk produk TF=1
   (mis. Holden, Grandis di TikTok cuma py dimensi warna, tanpa tahun
   sbg variasi terpisah - beda dari Shopee/Lazada yg pecah per generasi/
   tahun meski kodenya toh sama semua). Valid, bukan bug - 1 baris TikTok
   itu boleh nampung kode yg sama dgn banyak baris Shopee/Lazada. Fallback
   "unique_sku": kalau grup produk+tier+warna itu di data sumber cuma py 1
   kode SKU unik (walau row lookup sumber py >1 gen/tahun berbeda), pakai
   itu tanpa perlu nomor generasi cocok persis.
4. Sebagian baris Lazada/TikTok py "Gen N" yg TIDAK ada di 439 hasil fix
   (krn baris itu di Shopee SUDAH BENAR sebelumnya, jadi tidak masuk
   daftar "perlu diisi/diperbaiki") - mis. Hyundai Elantra Gen 1/4/5/6/7
   Reguler (yg masuk 439 fix cuma Gen 2/3 Reguler & Gen 2-7 Strip). Krn
   Elantra sudah dikonfirmasi TIDAK ada di file Total Formula & pakai
   fallback literal Gen N->GN (lihat entri 2026-08-27 di atas), generasi
   yg "hilang" ini AMAN dihitung ulang langsung dgn rumus yg SAMA (bukan
   nebak formula baru) - prefix+toko-nya sudah pasti dari 439 hasil fix
   yg ada. **Deteksi bukan hardcode per-nameplate**: script cek OTOMATIS
   semua kode existing tiap produk beneran murni literal G<n> (fungsi
   `build_literal_bases()`) - kalau ada SATU SAJA kode yg menyimpang dari
   G<n> (tanda produk itu py formula TF>1/grouped), produk itu di-exclude
   dari extrapolasi, supaya tidak keliru diterapkan ke model yg py
   formula. Dari 157 grup produk+tier+warna, 5 produk terdeteksi otomatis
   murni literal (Elantra, Civic Hatchback, Civic Type R, Xforce,
   Chevrolet Optra Magnum).

**Hasil akhir**: dari 157 grup (produk+tier+warna) hasil 439 fix, TikTok
100% ketemu tempatnya (492 baris ditulis: 314 gen_match langsung, 118
unique_sku/TF=1, 40 literal_extrapolated, 18 fallback TF=1-tanpa-gen, 2
leftover Mini Cooper). Lazada 148/157 (520 baris ditulis) - 9 grup sisanya
SEMUA "Holden Strip" & sudah dikonfirmasi via full-text scan katalog bahwa
Holden memang TIDAK dijual di Lazada sama sekali (produk itu memang tidak
ada, bukan bug matching - Holden Reguler juga tidak ada karena semua
varian Holden yg masuk 439 fix kebetulan Strip semua, Reguler-nya sudah
benar dari awal di Shopee).

Verifikasi file hasil: reload & bandingkan tiap sel vs file sumber -
SEMUA perubahan cuma di kolom SKU yg dimaksud (453/520 Lazada & sisanya
TikTok beneran berubah nilainya, sisanya kebetulan nilai lama = nilai
baru shg tidak "berubah" scr diff tapi tetap benar). Ada drift kosmetik
'' (empty string) -> `None` di beberapa sel opsional (row header Lazada,
kolom opsional TikTok spt parcel dimension) - **ini murni artefak
load+save openpyxl, TERJADI JUGA di roundtrip TANPA edit sama sekali**
(dites eksplisit: load lalu save ulang tanpa ubah apa2 menghasilkan diff
yg SAMA) - bukan bug dari script propagasi ini, dan tidak berdampak krn
kolom2 itu opsional/deskriptif (TikTok sendiri bilang di instruksi
templatenya: "dikosongkan saat edit massal = dianggap tidak ada
perubahan").

Script: `hpp-per-merk-scripts/propagasi_sku_lazada_tiktok_smartprotection.py`.

---

## 2026-08-29: Audit SKU Otoprotection (OP) + update harga SP & OP sekaligus

User upload 4 file listing Otoprotection (2 Shopee `1.xlsx`/`2.xlsx`, 2
TikTok batch-edit terpecah `tiktok1.xlsx`/`tiktok2.xlsx`) minta dibuatkan
update SKU-nya, SEKALIGUS minta update harga baru utk SP (belum pernah
diupload sama sekali - SKU maupun harga) dan OP, pakai
`Harga Baru SP-OP (matriks) FINAL.xlsx` (291 model) yang sudah dibuat
sebelumnya.

**Temuan kunci**: token TOKO di SKU Otoprotection **BUKAN "OP" tapi
"SP"** - rule #1 `project-undercover-sku-sync-rules.md`: konsolidasi
stok fisik `OP=SP` (`TARGET_STORE = {..., OP:SP, SP:SP}`, dibake ke
master sejak 2026-07-08). Jadi SKU yang benar utk OP itu **identik**
dgn SKU SP utk kombinasi produk+tier+warna+generasi yg sama - bukan
skema terpisah. Ini mengubah total strategi audit: 552 baris OP
kosong/legacy berhasil diisi terutama dgn cross-reference ke data SP yg
SUDAH benar (295 `gen_match` langsung + 103 `ambiguous_pick_earliest_gen`
+ dst), BUKAN dgn menebak dari data OP sendiri yg lebih sedikit.

**2 fallback baru (generalisasi dari preseden Nissan X-Trail yg sudah
dikonfirmasi user)**, ditambahkan ke `audit_dan_isi_sku_otoprotection.py`:
- `ambiguous_pick_earliest_gen`: listing OP SERING tidak memecah varian
  per generasi (user sendiri bilang "otoprotection variannya lebih
  sedikit") - kalau semua kode SKU yg py tier+warna SAMA di SP cuma beda
  di kode generasi, pakai yg PALING AWAL (start-year terkecil) - berlaku
  jg utk kode generasi NON-G<n> (chassis code kayak F2/F3, B5/B8, G1F/G2
  - urutan diambil dari tahun, bukan asumsi format G<n>).
- `uniform_base_new_combo` / `earliest_base_new_combo`: kombinasi
  tier+warna yg SAMA SEKALI belum tercatat di manapun (mis. Ford Fusion
  warna Orange, Toyota 86 warna Orange - SP sendiri gak py entri ini) -
  aman diisi dari kode yg konsisten dipakai produk itu di kombinasi lain.

**4 kasus khusus, hasil tanya-jawab eksplisit dgn user (AskUserQuestion,
2026-08-29) - JANGAN diubah tanpa instruksi baru**, lihat
`SPECIAL_CASES_UNIFORM`/`SPECIAL_CASES_CHRONO` di
`audit_dan_isi_sku_otoprotection.py`:
1. **Formula harga Strip**: user tolak opsi "pertahankan selisih/persen
   lama" (selisih lama TIDAK seragam per model: +18rb/+20rb/+30rb/+60rb) -
   pilih formula BARU seragam: **Strip = Reguler baru + Rp43.000 flat**,
   utk SEMUA model, semua tier Strip (S1/S2/S3 sama).
2. **"Toyota Altis" (OP) = Toyota Corolla mulai Gen 9** (bukan "generasi
   paling awal Corolla" G7 - user eksplisit: nama trim Altis dipakai
   mulai gen ke-9). Pinjam prefix `TYT-CRL`, generasi **G9 SERAGAM**
   (listing OP cuma py 1 generasi varian, dikonfirmasi user).
3. **Nissan Latio, Wuling Alvez, Wuling Darion**: 0 data SAMA SEKALI di
   SP maupun OP - user eksplisit minta dibuatkan prefix baru, DAN dipakai
   jg utk isi baris SP sendiri yg SAMA (ternyata Latio & Darion ADA
   listingnya di SP juga, blank total - user yg nunjuk Darion, Latio
   ketemu saat verifikasi). Prefix baru (dicek 0 tabrakan): `NSN-LAT`
   (Latio, TF≠1 asli - 2 generasi murni dari rentang tahun bare tanpa
   kata "Gen": "2004-2012"→G1, "2014-2016"→G2, urutan kronologis; baris
   "Tahun Lain" tetap dilewati), `WLG-ALV` (Alvez, TF=1 dikonfirmasi via
   `Data_Mobil_Lebih_dari_1_Formula_3.xlsx`), `WLG-DAR` (Darion, TF=1 by
   inspection - cuma 1 label "Gen 1" di semua listing).

**Hasil SKU**: OP 552/567 baris relevan terisi (15 sisanya "Tahun Lain",
sengaja dilewati sesuai aturan #4). SP dapat TAMBAHAN 43 baris
(Latio+Darion, di luar 439 sebelumnya) - total SKU SP yg dikoreksi
sekarang 482.

**Hasil harga**: 291 target, 192/291 model ketemu match di SP maupun OP
(99 sisanya genuinely tidak dijual, dicek silang: sama persis dgn "99
Tidak Ditemukan" dari audit SKU SP sebelumnya - cross-check independen yg
konsisten). SP: 6.963 baris harga diupdate (2.742 Reguler, 4.221 Strip).
OP: 5.891 baris (2.354 Reguler, 3.537 Strip). SEMUA formula diverifikasi
ulang dari file hasil: 0 mismatch diff≠43000 dari 195 produk per toko.

**File digabung SKU+harga JADI SATU** (lihat lesson 2026-08-15) krn
SP & OP dua-duanya belum pernah diupload - `UPDATE_SKU_HARGA_
SMARTPROTECTION_{1,2}.xlsx`, `UPDATE_SKU_HARGA_OTOPROTECTION_{1,2}.xlsx`
(klon in-place dari file sumber asli, cuma kolom SKU+Harga yg berubah,
diverifikasi via `iter_rows` - 0 diff non-blank di luar 2 kolom itu).
TikTok OP (`UPDATE_SKU_OTOPROTECTION_TIKTOK_{1,2}.xlsx`) SKU-only (tidak
diminta update harga TikTok di fase ini) - dipropagasi dari 552 hasil OP
Shopee + fallback yg sama, 5.207/6.398 baris relevan cocok (858 beneran
berubah, sisanya sudah benar dari awal), 144 sisa gap dilaporkan ke user
(60 Toyota Corolla Gen1-4 - gap lama di master SP sendiri yg formula-nya
grouped TF>1 shg tidak aman ditebak; sisanya produk yg 0 data di manapun,
belum ditanyakan user).

---

## 2026-08-29 (lanjutan sama hari): User minta harga TikTok OP + daftar gap - membongkar bug bucket-code di 8 produk lain

User minta 2 hal stlh menerima 6 file di atas: (1) "kenapa TikTok OP ngga
sekalian harganya? sekalian update" (2) "TikTok OP yg masih belum ada
SKUnya ini produk mobil apa aja?". Menjawab #2 (nge-list produk gap)
JUSTRU membongkar bug baru: Hyundai Elantra & Hyundai Sonata muncul di
daftar gap TikTok PADAHAL Elantra harusnya SUDAH 100% beres (439-row fix
sebelumnya). Investigasi: **listing OP PUNYA SALINAN TERPISAH Elantra**
yang TIDAK PERNAH disentuh 439-row fix itu (fix itu cuma nyentuh
`sp_sku_fixed/*.xlsx`, bukan `op_src/fixed/*.xlsx`) - 42 baris OP masih
pakai kode bucket lama (`GB20152020`, `GB20202024`) yang identik dgn bug
Elantra yang sudah diperbaiki di SP.

**Investigasi diperluas (bukan cuma Elantra)**: scan SEMUA produk SP yg
tier Strip-nya py kode berawalan "GB" (pola bucket) - ketemu **9 produk**
(termasuk Elantra yg sudah beres): Chevrolet Trooper, Hyundai Sonata,
Jeep Cherokee, Kia Sedona/Carnival, Lexus LX, Lexus RX, Mercedes Benz CLS
Class, Mercedes Benz GLA Class, Peugeot 3008. **Dicek ke file Total
Formula - TIDAK SATU PUN dari 8 produk baru ini ada di situ**, jadi
source of truth-nya cuma tier Reguler produk itu sendiri (kalau bersih)
atau literal Gen->G<n>.

**Metode perbaikan (general, otomatis, bukan hardcode per-produk)**:
bangun peta `(gen_or_leftover_tahun) -> kode_generasi` dari tier REGULER
produk itu sendiri (paling terpercaya krn historisnya sudah bersih/live),
lalu timpa SEMUA baris tier Strip yg kode generasinya BEDA dari peta itu.
**8 dari 9 aman** (Reguler-nya sendiri konsisten, tidak py kode bucket
maupun tabrakan) - Chevrolet Trooper, Hyundai Sonata, Jeep Cherokee, Kia
Sedona/Carnival, Lexus RX, Mercedes Benz CLS Class (walau angka
generasinya kebalik dari kronologis - G2 utk yg lebih tua, G1 utk yg
lebih baru - PROPAGASI TETAP AMAN krn tujuannya nyamain Strip ke Reguler,
BUKAN membetulkan skema Reguler-nya, itu keputusan terpisah kalau memang
salah), Mercedes Benz GLA Class. **1 DIFLAG, TIDAK diperbaiki**: **Lexus
LX** - tier Reguler-nya SENDIRI py kode bucket (`GB20002007`), jadi tidak
ada sumber bersih dalam produk itu utk jadi rujukan - butuh investigasi
manual/tanya user, sama seperti Elantra dulu butuh file Total Formula.

**Hasil**: SP dapat 135 baris tambahan diperbaiki (total SKU SP
terkoreksi jadi 617), OP dapat 72 (bug sama, salinan independen) + 42
(Elantra tidak sinkron) = 114 baris tambahan (total 666). TikTok OP
sekarang 5.252/6.398 cocok (gap turun dari 144 ke 124 - Elantra & Sonata
hilang dari daftar gap). **Harga TikTok OP ditambahkan** (kolom `price`
TikTok, sama formula Reguler+Rp43rb utk Strip): 2.444 Reguler + 3.663
Strip = 6.107 baris.

**Jebakan teknis yang kejadian & harus diingat**: fungsi pembangun
kandidat/master (`build_sp_master()`, `build_op_candidates()`,
`build_sp_sku_overrides()`, `build_op_sku_overrides()` di
`update_sku_harga_sp_op.py`) SEMUANYA baca override dari pickle hasil
audit LAMA (`final_sku_fill7.pkl`/`op_audit_final.pkl`) yang HANYA
mencakup baris yg ORIGINALNYA blank/legacy - begitu ketemu bug baru
("baris yg dari awal SUDAH kelihatan py SKU valid, tapi ternyata salah"),
override BARU (`bucket_fixes_final.pkl`, `elantra_op_fix.pkl`) harus
ditambahkan ke **SEMUA SATU-SATUNYA titik pembangun override**, bukan cuma
1-2 dari 4 - pertama kali cuma nambahin ke `build_sp_master()` &
`build_op_candidates()` (utk TikTok) tapi LUPA `build_op_sku_overrides()`
(utk file Shopee OP), akibatnya file Shopee OP yang sudah dikirim ke user
MASIH py kode Elantra/Sonata lama walau TikTok & cross-reference-nya udah
benar - ketauan dari verifikasi ulang manual per-file, BUKAN otomatis
tertangkap. **How to apply**: kalau nemu bug baru yg butuh override
tambahan di alur multi-tahap (banyak fungsi baca dari sumber yg sama),
bikin CHECKLIST semua titik yg baca sumber itu SEBELUM mulai edit, jangan
nambahin satu-satu sambil jalan - gampang kelewat kalau fungsinya
strukturnya mirip tapi tersebar di file berbeda.

Sisa gap TikTok OP (124, turun dari 144): 60 Toyota Corolla Gen1-4 (gap
lama, formula grouped, tidak aman ditebak), 15 Nissan Latio "Model
Lain/Custom" (skip sengaja, versi TikTok dari "Tahun Lain"), 14 Lexus RZ,
14 Toyota FJ Cruiser, 14 Hummer H3, 5 Volkswagen Kombi, 1 Peugeot 306, 1
Nissan Cedric - SEMUA 0 data di SP maupun OP, belum ditanyakan ke user.

Script tambahan: `perbaiki_bucket_dan_harga_tiktok_op.py`.

---

## 2026-08-31: Lexus LX diperbaiki, Toyota Corolla + "kasus serupa" dari Total Formula, semua file SP/OP final dikirim ulang

User minta 3 hal: (1) perbaiki Lexus LX + kasus serupa, (2) isi Toyota Corolla Gen1-dst yg kosong sesuai formula asli (kirim screenshot formula Corolla) + kasus serupa, (3) kirim ULANG SEMUA file upload SP+OP (Shopee/TikTok/Lazada) krn belum ada satu pun yg diupload.

**Lexus LX**: dikonfirmasi TIDAK ada di file Total Formula. Data SP: 2
generasi asli ("2000-2007" jadi kode bucket `GB20002007`, "2008-2022"
jadi kode "G1" bersih tapi SALAH kalau dianggap "generasi pertama").
Diperbaiki jadi kronologis murni: 2000-2007->**G1**, 2008-2022->**G2**
(28 baris SP, tier R+S). **Scan kasus serupa** (produk lain yg tier
MANAPUN py kode bucket "GB"): Lexus LX SATU-SATUNYA, tidak ada yg lain.
OP tidak disentuh (listing OP Lexus LX itu sendiri sudah collapse jadi 1
bucket tanpa info tahun - `G1` di situ tetap benar krn convention "label
gabungan = generasi PALING AWAL").

**Toyota Corolla**: BLOCKER TEKNIS ditemukan - Gen 1-6 (yg kosong di
screenshot user) **TIDAK ADA SEBAGAI BARIS SAMA SEKALI** di file export
`sp_sku_fixed/1.xlsx` (cuma py 90 baris = Gen7-12 x 15 tier/warna,
verifikasi via hitung baris+PID). Artinya listing LIVE Shopee sudah py
lebih banyak varian (sampai Gen 1) drpd yg tertangkap di export terakhir
- kemungkinan export lama/sebelum varian baru ditambah. **Tidak bisa
diisi via edit spreadsheet krn tidak ada Kode Variasi utk ditarget** -
butuh export BARU dari Shopee, atau user isi manual di UI pakai kode yg
sudah dihitung: Gen1->G1, Gen2->G1 (1 grup sama, "Corolla Betawi"),
Gen3->G3, Gen4->G4 (Gen5 dst sudah benar/G5,G6,G7,G8,G9(x3: 9,10,12),G11
- constant dgn Total Formula: TYT-CRL-SP-{tier}-G<kode>-{warna}).

**Total Formula file DIBACA ULANG scr terprogram** (bukan cuma dicari
manual per-produk), 213 entri, 2 pola grouping: (a) TF == jumlah baris ->
tiap baris grup sendiri (kode = gen TERKECIL di baris itu) - preseden
Corolla/Avanza; (b) **TF == 1 dgn baris > 1** -> SEMUA baris gabung jadi
1 grup (kode = gen TERKECIL dari SELURUH baris, bukan per-baris) -
preseden Hyundai Excel (3 baris Gen1/2/3, TF=1 -> semua G1, CONFIRM sama
dgn keputusan lama). 187/213 entri numerik murni berhasil diparse; 3
py TF="?" (eksplisit tidak pasti di filenya sendiri: Honda Civic
Hatchback, Nissan Livina X-Gear) atau data ganjil (Hyundai Stargazer
TF=2 tapi cuma 1 baris) - DILEWATI, tidak dipaksa.

**Koreksi "kasus serupa" yg AMAN diterapkan** (blank-gap fill, tidak ada
resiko nimpa yg sudah benar krn baris asalnya kosong):
- Isuzu Mux (2 baris, TF=1 -> G1)
- Hyundai Excel (9 SP + 9 OP, TF=1 -> G1, CONFIRM keputusan lama sudah
  benar meski dari metode beda)

**Koreksi yg MENGUBAH nilai yg sebelumnya SUDAH diisi (borrow-sibling,
ternyata salah setelah dicek ke TF file asli)** - preseden Elantra lagi,
"metode sibling-borrow" TERBUKTI BUKAN pengganti sah utk file Total
Formula begitu bisa dicek langsung:
- **Honda Civic Type R**: py entri TF SENDIRI terpisah dari "Honda Civic"
  (yg TF=11, per-generasi G1-G11 - dipakai keliru sbg basis borrow
  sebelumnya). Entri asli Civic Type R: **TF=1**, Gen6-11 SEMUA jadi
  **G6** (bukan G6,G7,G8,G9,G10,G11 spt yg di-borrow dari Civic Sedan).
  90 baris SP + 90 baris OP dikoreksi.
- **Mazda 2 Sedan**: py entri TF SENDIRI (bukan perlu borrow dari Mazda 2
  Hatchback spt sebelumnya) - "Gen 2 (2007-2014)"/"Gen 3 (2014-2019)"
  TF=1 (catatan di file: "Baru Ada di Toko Undercover saja") -> SEMUA
  jadi **G2** (bukan G1 hasil borrow Hatchback). Gen 1 (2002-2007) TIDAK
  masuk entri TF ini sama sekali - tetap G1 by literal fallback (karena
  utk gen yg gak ke-cover TF, default literal tetap berlaku). 30 baris SP
  + 30 baris OP dikoreksi.
- Mitsubishi Xforce: py entri TF sendiri (TF=1, cuma "Gen 1") - dicek,
  TIDAK ADA perubahan (sudah G1 dari awal, konsisten).

**4 kandidat "mismatch" DIFLAG, SENGAJA TIDAK diubah** (ambigu/berisiko,
beda dari kasus di atas yg baris asalnya blank) - Toyota Veloz, Toyota
Voxy, Honda HRV, Honda City Hatchback. Detail knp tidak aman:
- Toyota Veloz: py entri TF SENDIRI (Gen1/2026, TF=1->G1) TAPI listing SP
  py "Toyota Veloz" pakai kode G3 - kemungkinan krn "Veloz" listing SP
  itu maksudnya "varian Veloz dari Avanza Gen3" (liat entri Avanza:
  "Gen 3 (2021-2026) VELOZ" -> G3), BUKAN mobil "Toyota Veloz" versi
  nomor generasi sendiri (nama yg sama dipakai 2 konteks beda di file
  formula). Butuh konfirmasi user, bukan tebakan.
- Toyota Voxy, Honda HRV: entri TF py DATA GANJIL (HRV: baris "Gen 2"
  ditulis 2 KALI identik - typo/duplikat data entry, bukan makna asli;
  Voxy Gen3/Gen4 TF=1 tapi listing SP py kode berbeda) - kualitas data
  filenya sendiri diragukan, jangan dipaksa jadi rujukan.
- Honda City Hatchback: TF eksplisit **"?"** di file (penulis filenya
  sendiri tidak yakin) - source resminya SENDIRI bilang tidak pasti,
  jangan dipakai override keputusan lama (G1 seragam, borrow dari Mazda
  2 Hatchback-style sibling, sudah dikonfirmasi user 2026-07-18 sbg
  benar).

**Lesson teknis baru**: fallback "cocokkan by tahun AWAL saja" (`leftover
_start_year_match`, ditambahkan ke `resolve()`) - Lazada py kasus "Lexus
LX 2008-2024" vs kanonis SP "2008-2022" (beda TAHUN AKHIR doang, platform
lain nulis rentang aktif "sampai sekarang" beda2) - sebelum ada fallback
ini, sistem jatuh ke "pilih generasi PALING AWAL" scr membabi-buta,
hasilnya SALAH nempelkan G1 (generasi 2000-an) ke baris yg jelas2 tahun
awalnya 2008 (generasi kedua). Fallback baru cocokkan 4-digit tahun AWAL
dulu SEBELUM nyerah ke "pilih paling awal" - jauh lebih presisi.

**File FINAL yg dikirim (8 file, revisi terakhir)**:
- `UPDATE_SKU_HARGA_SMARTPROTECTION_{1,2}.xlsx` (Shopee SP, SKU+harga)
- `UPDATE_SKU_HARGA_OTOPROTECTION_{1,2}.xlsx` (Shopee OP, SKU+harga)
- `UPDATE_SKU_OTOPROTECTION_TIKTOK_{1,2}.xlsx` (TikTok OP, SKU+harga)
- `UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx` (Lazada SP, SKU+harga -
  **DIBANGUN ULANG dari `build_sp_master()`** yg sudah termasuk SEMUA
  koreksi di atas, BUKAN dari `final_sku_fill7.pkl` mentah spt versi
  2026-08-29 pertama - kalau pakai yg lama, file ini bakal BAWA BALIK
  nilai yg baru saja dikoreksi)
- `UPDATE_SKU_HARGA_SMARTPROTECTION_TIKTOK.xlsx` (TikTok SP, SKU+harga,
  sama - dibangun ulang)

Semua 8 file diverifikasi ulang via `iter_rows` (0 diff non-blank di
luar kolom SKU/Harga yg dimaksud) dan cek formula harga (Strip-Reguler =
43rb utk SEMUA produk yg match target, mismatch yg tersisa SEMUA
produk non-target/harga lama).

Script: `update_sku_harga_lazada_tiktok_smartprotection.py` (versi final
Lazada/TikTok SP, superseded
`propagasi_sku_lazada_tiktok_smartprotection.py` yg cuma SKU dari
439-fix mentah). Semua override tambahan (bucket-fix, Elantra-OP-sync,
formula-correction, Lexus LX) didaftarkan terpusat di SATU list
`op_audit.EXTRA_OVERRIDE_PICKLES` + fungsi `load_extra_overrides()`,
dipakai oleh SEMUA fungsi builder (sp_master, op_candidates,
sp_sku_overrides, op_sku_overrides) - supaya tidak berulang lagi
lesson "lupa 1 dari 4 titik" dari fix sebelumnya.

Script: `audit_dan_isi_sku_otoprotection.py`, `update_sku_harga_sp_op.py`,
`propagasi_sku_tiktok_otoprotection.py`.

**(2026-08-31, lanjutan) Verifikasi pasca-kirim atas pertanyaan user soal 2 screenshot TikTok OP (Avanza & Honda City Hatchback) + scan sistemik "prefix berubah" - ketemu 1 bug isolated (Navara PRO-4X) + 1 bug SISTEMIK BARU (duplikat SKU Lazada), keduanya diperbaiki.**
- **Screenshot Avanza (G1/G3 split)**: pola yg ditunjukkan user SUDAH BENAR & jadi rujukan kerja sepanjang sesi ini - tidak ada kasus lain yg pola-nya beda dari itu.
- **Screenshot Honda City Hatchback ("kenapa pakai kode Jazz?")**: prefix `HND-JAZ` yg user lihat itu state LAMA (sebelum upload file baru) - di file yg sudah dikirim (`UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx`) sudah `HND-CHB`, konsisten dgn Shopee SP/OP. Tidak perlu aksi baru, cuma penjelasan ke user.
- **Scan sistemik "source SKU != output SKU" di SEMUA 8 file yg dikirim** (lanjutan dari pertanyaan Avanza) nemu 3 kandidat "prefix berubah": Toyota Vellfire (`TYT-VLF`->`TYT-ALP`), Mazda 3 Hatchback (`MZD-M3`->`MZD-3H`), Jeep Wrangler Rubicon (`JEP-WR`->`JEP-WRA`, 46 baris Lazada). Diverifikasi satu-satu:
  - Vellfire->`TYT-ALP`: BENAR, sesuai rule #8 established (Alphard+Vellfire kembar, `project-undercover-sku-sync-rules.md`).
  - Mazda 3 Hatchback->`MZD-3H`: BENAR - mayoritas baris DALAM listing yg sama sudah pakai `MZD-3H`, cuma sebagian baris Reguler yg nyasar sisa `MZD-M3` lama; hasil pipeline cuma menyeragamkan ke kode yg SUDAH dominan di listing itu sendiri, bukan tebakan baru.
  - Jeep Wrangler Rubicon->`JEP-WRA`: BENAR juga (bukan override yg perlu dibatalkan) - mayoritas baris listing "Jeep Wrangler Rubicon" milik SP Lazada SUDAH pakai `JEP-WRA` sblm disentuh, konsisten dgn resolusi established 2026-07-18 (listing SP/OP bernama "...Rubicon" scr definisi Bigseller mereka MEMANG map ke `JEP-WRA`, bukan `JEP-WR` yg dipakai model chassis-spesifik lain) - LIHAT PERINGATAN LAMA di `project-undercover-sku-sync-status.md` baris ~917-932 yg eksplisit bilang jangan buru2 timpa pasangan ini tanpa cek baris asli; sudah dicek, aman.
  - **Navara PRO-4X (row 725, `UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx`)**: BUG NYATA, prefix salah ketiban `NSN-NVR` (base Navara) padahal seharusnya `NSN-NVP` (Navara PRO-4X, pembeda YG DISENGAJA) - sumber: `clean_base()` tidak preserve trim "PRO-4X" (lihat lesson di `feedback-undercover-sku-sync-lessons.md`). Scan ke seluruh 8 file (kata kunci pro-4x/rubicon/commuter/facelift, source vs output) konfirmasi HANYA 1 baris ini yg kena. **Diperbaiki** via patch langsung ke sel yg sudah dikirim.
- **Bug BARU & lebih luas ditemukan saat verifikasi Jeep Wrangler Rubicon**: proses "membersihkan" SKU ke format kanonis 6-segmen (menghapus suffix lama spt `_G1`/`_ELIT`/`_MERA`) TERNYATA menghasilkan **SKU DUPLIKAT** dlm 137 dari 376 produk (5288 baris) di `UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx` - suffix "berantakan" itu ternyata sengaja jadi pembeda baris utk produk yg beberapa generasi aslinya collapse ke 1 kode kanonis yg sama (TF=1), krn Lazada wajib SKU unik per varian (beda dari Shopee/TikTok). File SUMBER (sblm disentuh) dikonfirmasi 0 duplikat. **Fix**: `update_sku_harga_lazada_tiktok_smartprotection.py` ditambah post-write dedup pass (param `dedup_per_product=True`, KHUSUS Lazada, tidak dipasang di TikTok) - baris yg SKU kanoniknya tabrakan dgn baris lain di produk yg sama otomatis dapat suffix pembeda baru dari data variannya sendiri (nomor gen, tahun awal, atau kode chassis alfabetik spt JK/TJ/YJ/JL utk kasus Jeep). 3273 baris kena suffix baru. Diverifikasi ulang: 0 grup duplikat tersisa, row count utuh (7968), 0 diff tak terduga di kolom selain SKU/Harga.

**File FINAL (sudah termasuk 2 fix di atas) yg dikirim ulang**: `UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx` (Navara PRO-4X fixed) dan `UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx` (dedup fixed, regenerated). 6 file lain (Shopee SP 1-2, Shopee OP 1-2, TikTok OP 1, TikTok SP) TIDAK berubah dari revisi sebelumnya.

**(2026-08-31, lanjutan lagi) User upload 2 laporan hasil percobaan upload (Lazada `pricestock...export.xlsx`, TikTok `Tiktoksellercenter_batchedit...result.xlsx`) - ketemu GAP BESAR yg belum pernah dilaporkan: kategori Transparan TIDAK PERNAH disentuh sama sekali sepanjang seluruh sesi SKU+harga ini.**
- **Laporan Lazada**: 172 baris "Data no change in file, not update" (BUKAN error/rejection - cuma pemberitahuan Lazada "tidak ada perubahan, jadi tidak diupdate"). 525 dari total row-index yg kena PERSIS match rentang baris Transparan (6682-7968) - konfirmasi Transparan memang tidak ditulis apa pun oleh pipeline manapun. 43 row-index sisanya (Hyundai Matrix Gen1, Mitsubishi Lantis "Tahun Lain") itu baris non-Transparan yg base-name/variant-nya tidak match ke salah satu 291 target harga - gap kecil & sudah diketahui/wajar (bukan Transparan, bukan bug baru).
- **Laporan TikTok**: cuma 7 baris gagal, SEMUANYA "Cover Mobil Transparan Mercedes Benz [X] Class" - errornya "atribut produk is missing... ID:100177, nama: Model" = TikTok minta field dropdown "Model" (atribut kategori TikTok, BUKAN kolom SKU/harga apa pun di file kita) yg belum pernah diisi utk listing2 itu. Sama sekali tidak terkait SKU/harga - ini gap SETUP KATALOG TikTok yg sudah ada dari sebelumnya, harus diisi manual di UI TikTok Seller Center, bukan lewat file spreadsheet.
- **Root cause Transparan tidak tersentuh**: `build_sp_master()` (fungsi kandidat SENTRAL yg dipakai SEMUA pipeline SKU sesi ini) punya baris eksplisit `if not nm or is_transparan_product(nm): continue` - Transparan SENGAJA dikecualikan dari situ. Utk HARGA ini memang keputusan sadar (skema harga Transparan beda, di luar 291 target Reguler/Strip - didokumentasikan di komentar `update_sku_harga_sp_op.py`), tapi utk SKU ternyata TIDAK ADA keputusan sadar - cuma warisan scope dari `build_sp_master()` yg dirancang khusus utk Reguler/Strip, lalu semua pipeline turunannya (Lazada/TikTok SP, TikTok OP) ikut skip Transparan total tanpa ada yg pernah eksplisit mempertimbangkan itu.
- **Skala gap**: scan ke SEMUA 8 file, dari total ~2551 baris Transparan, 401 (211 legacy-format + 190 blank) TIDAK PERNAH diverifikasi/diperbaiki sepanjang sesi ini.
- **User diberi 2 pilihan (AskUserQuestion) dan pilih: "SKU dulu saja, harga nanti"** + "harga Transparan belum ada daftar baru, pakai harga lama dulu".
- **Fix**: `build_transparan_master()` baru (di `audit_dan_isi_sku_otoprotection.py`) - gabungkan SEMUA SKU Transparan valid (6-segmen, toko=SP, kategori=T, warna konstan "TRP") dari SEMUA 8 sumber SEKALIGUS (bukan cuma Shopee SP spt build_sp_master(), krn coverage Transparan jauh lebih jarang/timpang per platform - butuh 2 fungsi baru pendukung: `clean_base_transparan()` yg strip PREFIX-style "Transparan X" (gaya OP) SEKALIGUS SUFFIX-style "X Transparan" (gaya SP) supaya kedua gaya penamaan ketemu di base name yg sama; `gen_and_leftover_transparan()` yg proses SELURUH teks varian langsung tanpa potong-koma dulu, krn Transparan tidak py axis warna sama sekali (beda dari Reguler/Strip yg selalu "warna,generasi")). Script baru `isi_sku_transparan.py` jalankan `resolve()` (dipakai APA ADANYA, generik thd tier/warna: di sini tier='T' warna='TRP' konstan) ke tiap baris Transparan yg blank/legacy di 8 file, + `dedup_per_product` khusus Lazada (pola duplikat yg sama ditemukan lagi: sufiks `_TRP_G2`/`_TRP_G3` di data yg sudah valid, bukti Transparan jg butuh disambiguator Lazada).
- **Hasil**: 130 baris diperbaiki otomatis. Sisa 271 baris (39 model berbeda, terkonsentrasi di ~10 model besar: Mini Cooper 50, Honda Civic Type R 30, Civic Hatchback 24, Toyota Corolla 20, Mazda 2 Sedan 15, Mitsubishi Eclipse 12, Mercedes Benz G Class 12, Hyundai Elantra 10, Peugeot 306 10, VW Passat 7, dst) - **genuinely 0 referensi SKU Transparan valid di SEMUA 8 file/platform**, TIDAK diisi (tidak ditebak). Pola menarik: mayoritas nama model ini SAMA PERSIS dgn produk yg butuh koreksi Total Formula utk tier Reguler/Strip (Mini Cooper "in-between" TF, Civic Type R TF=1->G6, Mazda 2 Sedan TF=1->G2, Corolla TF=9 grouped, Elantra bucket-code bug) - kemungkinan besar kode generasi utk Transparan-nya BISA diturunkan dari mapping TF yg SUDAH ada utk Reguler/Strip (belum dieksekusi, ditawarkan sbg langkah lanjutan opsional ke user).
- Diverifikasi: 0 duplikat SKU baru di Lazada, row count utuh di semua 8 file, 0 diff di luar kolom SKU (kolom harga BENAR-BENAR tidak tersentuh, sesuai keputusan user).

**(2026-08-31, lanjutan ketiga) User tanya: "271 baris sisa itu apa tidak bisa disesuaikan dari format Transparan yg baru?" - jawaban: BISA, sebagian besar, via prinsip "kode generasi = properti fisik mobil, bukan milik tier".** Insight kunci: Corolla Gen 3 kodenya G3 baik itu Reguler, Strip, ATAU Transparan - jadi kalau Transparan sendiri 0 referensi tapi Reguler/Strip model yg SAMA sudah py kode generasi yg benar (hasil semua koreksi sesi ini), kode itu AMAN diturunkan lintas tier.
- **`build_model_gen_map()` baru** (di `audit_dan_isi_sku_otoprotection.py`): scan baris Reguler/Strip yg SUDAH FINAL (7 sumber: Shopee SP+OP, Lazada SP, TikTok SP+OP - versi POST-FIX, bukan source mentah) -> peta `{model: {nomor_gen_asli: kode_gen}}` + prefix MEREK-MODEL per model.
- **Fallback tambahan `formula_map2.pkl`** (parse mentah file Total Formula dari sesi sebelumnya): dipakai kalau generasi yg dicari GENUINELY tidak py baris Reguler/Strip sama sekali di manapun (bukan cuma blank) - kasus Toyota Corolla Gen1-6 (export Shopee stale, barisnya sendiri tidak ada, sudah didokumentasikan sblmnya) tapi file Total Formula TETAP py datanya krn itu sumber independen dari export marketplace.
- Juga ganti pemanggilan dari `resolve()` polos ke `resolve_with_special_cases()` - sempat kelewat menangkap Wuling Alvez/Darion & Toyota Altis->Corolla-G9 (special case yg sudah established) di iterasi pertama.
- **Hasil kumulatif**: 401 -> 138 baris bermasalah (263 baris tambahan diperbaiki, TERMASUK Toyota Corolla full-resolved lewat fallback Total Formula). **Sisa 138 baris/27 model** genuinely 0 referensi SKU Transparan/Reguler/Strip di SEMUA 7-8 sumber DAN tidak ada di file Total Formula: **Mini Cooper (50 baris) sendirian hampir separuh sisa** - ini BUKAN kasus baru, sudah dari dulu didokumentasikan sbg "IN-BETWEEN" TF case yg DITUNDA user ("logic menyusul", formula=2 tp 5 grup, belum pernah diberi aturan) bahkan utk Reguler/Strip-nya sendiri; sisanya 26 model kecil (Mitsubishi Eclipse 12, Mercedes G Class 12, Peugeot 306 10, VW Passat 7, Ford Fusion 6, Civic Hatchback 6, Mazda CX9 5, Espass 5, Timor 5, VW Fox 4, + 17 model 1-baris) genuinely tidak py jejak SKU valid apa pun utk dijadikan rujukan.
- Diverifikasi ulang: 0 duplikat Lazada, 0 diff kolom lain, row count utuh di semua 8 file.

## Audit status harga UA per ekspor 3 September 2026: 41/100 produk sudah harga baru

Diukur langsung dari ekspor live (Shopee 5 file `ua_cek_0819`, TikTok & Lazada
3 Sep), bukan dari catatan pekerjaan — dicocokkan lewat prefix SKU + tier
(R = "Harga Baru (Reguler)", S = reguler + Rp43.000) ke `HARGA_BARU_TOP100_v4.xlsx`.

| Status | Jumlah produk |
|---|---|
| Sudah harga baru (3 channel konsisten) | **41** |
| Belum | **59** |

Yang sudah: **#1–#40 kecuali #2 Brio & #4 Jazz**, ditambah #49 Feroza, #50 Veloz,
#58 Rocky (dua terakhir ikut naik karena SKU kembar: Veloz→`TYT-AVZ`,
Rocky→`TYT-RZE`). #21 Terios, #30 Sigra, #8 Ayla, #9 Xenia juga ikut lewat SKU
kembar. Status Shopee/TikTok/Lazada **identik di semua 41 produk** — tidak ada
lagi channel yang tertinggal seperti kasus Veloz-Lazada Agustus.

**#49 Feroza bukan hasil update** — harga lamanya kebetulan sudah persis
Rp382.000 (selisih 0), jadi memang tidak perlu naik.

### Dua temuan yang perlu ditindaklanjuti

1. **#2 Brio & #4 Jazz kurang Rp3.000** (live Rp332rb, target Rp335rb; strip
   Rp375rb vs Rp378rb). Semua produk lain yang belum, kurangnya Rp13.000–246.000
   (rata-rata Rp73.000). Pola beda-tipis ini khas sisa versi harga sebelum v4 /
   selisih strip lama Rp40.000 — bukan produk yang belum dikerjakan.
2. **#53 Luxio & #99 Mazda 2 Hatchback tidak akan tersentuh script apa adanya.**
   `PREFIX{}` memetakan keduanya ke `DHT-LXO` / `MZD-MZ2`, padahal listing UA
   memakai kode induk `DHT-GMX` / `MZD-2H` (hasil penyeragaman SKU kembar).
   Script tidak error — hanya menemukan 0 baris, diam-diam terlewat. Perbaiki
   `PREFIX{}`/`ALIAS{}` dulu sebelum batch 41-100. Harga live keduanya masih
   lama (Luxio Rp296–300rb vs target Rp383rb; Mazda 2 HB Rp291rb vs Rp335rb).

**Catatan riwayat**: memory repo ini hanya mencatat UA batch 1-10 & 11-20.
Produk 21-40 ternyata SUDAH live juga — dikerjakan di sesi/device lain yang
snapshot memory-nya belum masuk ke sini. Kalau menghitung "sudah sampai mana",
ukur dari ekspor live seperti audit ini, jangan dari catatan batch.

## Eksekusi UA produk 1-60 (2026-09-07): 20 model, 560 baris per channel

Dijalankan sekali untuk rentang **1-60** (bukan 41-60) supaya sisa selisih
Rp3.000 di Brio & Jazz ikut terkoreksi. Script melewati baris yang harganya
sudah benar, jadi produk 1-40 yang sudah live tidak ikut masuk file.

Sumber: Shopee ekspor 3 Sep (5 file), TikTok & Lazada 3 Sep.
Hasil: **Shopee 560 baris, Lazada 560, TikTok 574** (560 + 14 baris pelengkap,
lihat di bawah). 20 listing tersentuh, semuanya listing "Reguler" — tier
Premium/Exclusive/Transparan tidak disentuh sesuai aturan.

Kenaikan terbesar: HiAce 337->583rb (+246rb), Alphard & Vellfire 317->460rb,
Ignis 282->382rb, BMW Seri 3 304->384rb.

### Perbaikan `PREFIX{}` yang mencegah dua model terlewat diam-diam

- `Daihatsu Luxio`: `DHT-LXO` -> **`DHT-GMX`**. Luxio & Gran Max Minibus kembar
  dan seluruh listing sudah memakai kode induk; `DHT-LXO` sudah tidak ada di
  channel mana pun. Efeknya Gran Max Minibus ikut naik ke harga Luxio
  (Rp383.000) — benar, karena satu SKU = satu harga.
- `Mazda 2 Hatchback`: `MZD-MZ2` -> **`MZD-2H`** (untuk batch berikutnya).

### Toyota HiAce: satu listing, DUA produk berbeda

Listing "HiAce Reguler" memuat dua tipe bodi dengan SKU berbeda:
`TYT-HAC` (Commuter) dan **`TYT-HAL` (Premio)**. Daftar harga cuma punya satu
entri "Toyota HiAce" (5265mm, Pcs/Roll 3), jadi **Premio TIDAK dinaikkan** —
14 baris dibiarkan Rp337.000 sampai user memutuskan. Ini kebalikan dari jebakan
Grand Livina Roofbox: bukan produk lain yang ikut kena, tapi produk lain yang
ikut menumpang di listing yang sama.

### TikTok: file WAJIB memuat seluruh varian tiap produk yang disentuh

Ekspor TikTok 3 Sep bertemplate `all_information` (45 kolom, ada sheet `Brand`).
Karena HiAce Premio tidak ikut berubah, produk itu jadi tidak lengkap variannya
dan berisiko dibaca sebagai permintaan hapus. Ditambal script baru
`scripts/lengkapi_varian_tiktok.py` yang menyalin balik varian yang kurang
APA ADANYA (14 baris) -> 574 baris. Diverifikasi: 20/20 produk lengkap.

### Temuan sampingan

- **Mazda 2 Sedan** punya 1 varian salah harga sejak awal: "Hitam, Gen 2"
  Rp356.000 sedangkan 14 varian Reguler lain Rp296.000. Ikut ternormalisasi.
- **Suzuki Ignis** naik paling tidak proporsional di kelasnya (Rp382.000,
  sementara city car lain Rp332-334rb) karena `Pcs/Roll`-nya 5 (bukan 6) di
  data HPP user. Bukan salah hitung — angkanya dari data produksi sendiri —
  tapi layak dicek ulang kalau terasa kemahalan.
- Verifikasi tiap file dilakukan **kolom per kolom terhadap ekspor sumber**
  (kunci: Shopee `Kode Produk`+`Kode Variasi`, TikTok `sku_id`, Lazada
  `sku.skuId`): 0 perbedaan nyata di luar kolom harga, 0 harga meleset target.

### Revisi 2026-09-07 (jawaban user) — 616 baris per channel

Tiga koreksi dari user setelah file pertama dikirim:

1. **HiAce Premio ikut naik.** Formula & Pcs/Roll-nya sama dengan Commuter, jadi
   `ALIAS['TYT-HAL'] = 'TYT-HAC'`. 14 baris/channel ikut ke Rp583rb/626rb.
   Efek sampingnya bagus: produk HiAce jadi lengkap variannya di TikTok tanpa
   perlu baris pelengkap.
2. **Mazda 2 Hatchback (#99) ikut diupdate** — Rp291rb->335rb, strip
   Rp351rb->378rb, 42 baris/channel. Karena nomornya di luar 1-60, dijalankan
   RUN TERPISAH (`99 99`) lalu digabung pakai script baru
   `scripts/gabung_file_upload.py` (cek header identik + irisan kunci = 0).
   Menaikkan rentang jadi 1-99 SALAH — ikut menyeret produk 61-98.
3. **Suzuki Ignis Pcs/Roll = 6, bukan 5.** Harga jadi **Rp333.000**
   (strip Rp376.000), turun dari Rp382.000 di v4. Angka 333rb dipilih supaya
   tangga City Car tetap urut menurut panjang: Karimun 3600mm Rp332rb ->
   **Ignis 3700mm Rp333rb** -> Splash 3715mm Rp334rb. File harga disimpan
   sebagai `HARGA_BARU_TOP100_v5.xlsx` (v4 TIDAK diubah).

**Alphard & Vellfire memang SATU SKU** (pertanyaan user): dicek di listing
Shopee, keduanya `TYT-ALP-UA-...` persis sama sampai segmen terakhir —
Alphard 28 baris (2 generasi, kode sama), Vellfire 14 baris. Jadi harganya
wajib satu angka, dan file ini sudah begitu (Rp460rb/503rb).

Hasil akhir: **616 baris per channel, 21 produk/22 model** (Shopee, TikTok,
Lazada). Diverifikasi ulang kolom-per-kolom: 0 perbedaan nyata di luar kolom
harga, 0 harga meleset, TikTok 21/21 produk lengkap variannya.

### KOREKSI 2026-09-07: override Brio & Jazz TIDAK ikut terbawa ke file HARGA_BARU_TOP100

Keputusan 2026-08-26 (Brio & Jazz dipatok di lantai **Rp332.000/375.000**, bukan
hasil spread Rp335.000/378.000) ternyata cuma diterapkan ke
`Harga Baru UC Top 100 (matriks).xlsx`. File `HARGA_BARU_TOP100_v2..v4.xlsx` —
yang justru dipakai semua eksekusi UA/OT sejak Agustus — **masih memuat angka
spread Rp335.000**. Akibatnya:

- Audit 2026-09-07 salah menyimpulkan Brio & Jazz "kurang Rp3.000". Harga live
  UA (Rp332rb/375rb) sebenarnya SUDAH BENAR. Hitungan yang benar untuk audit
  itu: **43/100 produk sudah harga baru, bukan 41**.
- File update batch 1-60 versi pertama & kedua ikut menaikkan Brio & Jazz
  56 baris/channel — salah, dan ditarik sebelum diupload.

**Diperbaiki**: `HARGA_BARU_TOP100_v5.xlsx` sekarang memuat Brio & Jazz di
Rp332.000/375.000 (sekaligus Ignis Rp333.000). Setelah itu keduanya otomatis
hilang dari file update karena harga live-nya sudah sama. Hasil akhir batch
1-60 + Mazda 2 Hatchback: **560 baris/channel, 20 model**.

**How to apply**: setiap override harga manual WAJIB ditulis balik ke file
harga yang jadi sumber eksekusi berikutnya, bukan cuma ke file yang kebetulan
sedang dipakai saat itu. Kalau ada beberapa file harga beredar
(`matriks`, `TOP100_v*`), samakan dulu atau tetapkan satu yang jadi rujukan.
Pengecualian manual seperti ini tidak akan ketahuan dari data — script cuma
melihat selisih angka dan menganggapnya "belum diupdate".

## 2026-09-10 — Perbaikan 18 baris SP yang tertinggal + usulan Pcs/Roll 11 model

**Kelompok C selesai**: 18 baris TikTok SP yang harganya tertinggal karena typo
teks varian diperbaiki ke harga modus model+tier-nya. File
`PERBAIKI_HARGA_SP_TIKTOK.xlsx` — 269 baris (18 berubah + sisanya pelengkap,
karena template all_information TikTok butuh varian lengkap per produk).
Diverifikasi: 0 perubahan di luar kolom harga, 7/7 produk lengkap variannya.

**Usulan Pcs/Roll untuk 11 model kelompok A** (BELUM dikonfirmasi user —
Pcs/Roll itu data produksi, bukan turunan dimensi):

| Model | Generasi yg dijual | Usul P/R | Pembanding di daftar HPP |
|---|---|---|---|
| Volkswagen Fox | 2003-2009 | 6 | Datsun Go, BYD Atto 1 |
| Peugeot 306 | 1997-2002 | 6 | Toyota Yaris, Suzuki Swift |
| Hyundai Matrix | 2001-2010 | 6 | Honda Jazz, Toyota Agya |
| Mitsubishi Eclipse | 1999-2011 | 5 | Toyota Vios, Honda City |
| Nissan Latio | 2004-2016 | 5 | Toyota Vios |
| Peugeot 3008 | 2007-2024 | 5 | Honda HR-V, Chery Tiggo |
| Mercedes Benz GLB | 2020-2024 | 5 | Honda CR-V |
| Wuling Darion | 2025-2026 | 5 | Wuling Almaz |
| Volkswagen Passat | 1996-2024 | 5 | Toyota Camry, Honda Accord |
| Nissan Cedric | 1965-2004 | 5 (bisa 4) | Toyota Crown |
| Ford Fusion | 2005-2024 | **perlu dipastikan** | Fusion Eropa (MPV kecil, P/R 6) vs Fusion Amerika (sedan, P/R 5) |

Dasar: pita Pcs/Roll di daftar HPP cuma 5 nilai — P/R 7 (mobil mikro, 287rb),
6 (city car/hatchback, 322rb), 5 (sedan/MPV/SUV compact, 370rb), 4 (SUV/MPV
besar, 443rb), 3 (HiAce, 565rb). Generasi yang dijual diambil dari teks varian
listing SP sendiri, jadi bukan tebakan model mana yang dimaksud.

**Harga lama TIDAK bisa dipakai sbg petunjuk ukuran**: urutan harga lama
ke-11 model itu tidak berkorelasi dengan ukuran sama sekali (Passat Rp256rb
lebih murah dari Hyundai Matrix Rp298rb). Dicek juga ke Undercover — kesebelas
model itu **harga lama juga di UA**, jadi tidak ada rujukan harga baru dari
toko lain.
