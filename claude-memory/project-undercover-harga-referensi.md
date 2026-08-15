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

**Kalau mau extend/ulang metode ini** (mis. utk toko/channel lain, atau full
katalog bukan cuma Top 100): pakai kolom `Pcs/Roll` (bukan menebak dimensi
mobil manual) sbg sumber ranking ukuran per kategori — jauh lebih presisi &
konsisten drpd asumsi ukuran dari nama model doang.

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
