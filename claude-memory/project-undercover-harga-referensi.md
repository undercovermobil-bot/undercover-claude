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
