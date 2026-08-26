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
