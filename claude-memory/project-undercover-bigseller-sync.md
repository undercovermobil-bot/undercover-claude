---
name: project-undercover-bigseller-sync
description: "Sub-proyek sync SKU listing (skema formula baru) ke SKU Gudang Big Seller — mulai 2026-07-28, keputusan user + jebakan teknis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9235e50b-3311-43ed-a15e-4665c26b7c5e
  modified: 2026-08-06T01:55:20.193Z
---

Sub-proyek **Sync SKU Gudang Big Seller**, mulai 2026-07-28. Beda dari [[project-undercover-sku-sync-status]] (yang menyamakan SKU antar listing) dan [[project-undercover-stock-sync-status]] (yang sync kuantitas): ini menyamakan **daftar SKU listing → SKU Gudang di Big Seller**.

## Lokasi & jenis file (verifikasi ulang tiap sesi, bisa pindah)

Input ada di `C:\Users\OWNER\Documents\Undercover\SKU Gudang Big Seller\` — **di luar repo git**, satu level di atasnya. Tiga jenis:
- **18 file listing** (`UA_Shopee_1.xlsx` dst) — sudah berisi SKU skema formula baru, hasil sesi cloud 07-27/28.
- **`SKU_Gudang…(1..7).xlsx`** = daftar SKU yang ADA di Big Seller (33.295 SKU). Menjawab "sudah ada / belum".
- **`SKU_Match…(28)(1..29).xlsx`** = **pemetaan** listing↔SKU gudang (86.915 baris; kolom `Nomor SKU Gudang`, `Marketplace`, `Nama Produk`, `ID Produk`, `SKU Toko`, `Variasi ID`). Menjawab "listing mana tertaut ke SKU gudang mana" + mendeteksi pemetaan yang akan putus.

## Jebakan teknis (jangan buang waktu mengulang)

- **`SKU_Gudang`/`SKU_Match` menyimpan dimension palsu `A1:A1`.** `load_workbook(read_only=True)` berhenti di baris 1 dan mengembalikan **0 baris tanpa error** — gejalanya diam, bukan exception. Baca file itu dengan `read_only=False`. File listing tidak kena.
- Bug `activePane="bottom_left"` pada export Shopee tetap berlaku — lihat [[project-undercover-sku-sync-status]].
- **Format SKU motor = `MEREK-MODEL-UA-KAT-MTR-WARNA`** — `MTR` ada di segmen **generasi** (ke-5), bukan segmen toko. Regex yang menganggap `MTR` di segmen ke-3 akan menghasilkan 0 motor secara diam-diam.
- Konvensi judul di Big Seller **tidak seragam**: 25.316 SKU `Model-Toko-Kategori-Warna-Gen`, 4.448 `Cover Mobil <model> <kat> <warna>`, 3.403 lain, 128 `Cover Motor …`.

## Keputusan user 2026-07-28 (jangan didesain ulang)

1. **Varian `_` Lazada** (9.322 SKU, mis. `…-ABU_G3`) → dipetakan ke **SKU gudang base**, tidak dibuatkan SKU gudang sendiri. Barangnya fisik sama; akhiran `_` cuma syarat keunikan Lazada. **User sudah membuat rules pemetaannya sendiri di Big Seller**, jadi tidak perlu impor pemetaan manual.
2. **Segmen OT/OP dikoreksi ke UA/SP** sebelum dibuat (aturan konsolidasi #1 & #3). Ternyata menurunkan "belum ada" dari 4.389 → 3.614: 775 SKU sebenarnya sudah ada begitu segmennya dikonsolidasi.
3. **SKU listing bermasalah dilewati**, tidak dibuatkan SKU gudang — hanya dilaporkan.
4. **SKU gudang yatim dibiarkan** di Big Seller (histori pesanan lama utuh), hanya didaftar.
5. **Judul mobil**: `Model-Toko-Kategori-Warna-Gen`. **Judul motor**: `Model-Toko-Kategori-Warna-Motor` — penanda `Motor` mengisi segmen generasi yang kosong supaya motor tetap terbedakan di inventory.

## Konteks penting dari user

**128 SKU motor `CM####` yang dibuat 2026-07-28 adalah tambalan dadakan**, bukan pilihan skema — dibuat karena sistem Big Seller mewajibkan ada SKU gudang supaya barang bisa keluar dari inventory. Skema yang benar tetap `MTR`. Jadi ke-128 itu masuk daftar yatim.

## Hasil batch pertama

Dari 16.303 SKU listing layak-gudang: **12.689 sudah ada (77,8%), 3.614 belum ada (22,2%)** — 1.829 mobil + 1.785 motor (seluruh SKU motor skema baru memang belum ada). Yatim 20.606. Output di `…\SKU Gudang Big Seller\Hasil Sync 2026-07-28\`: `Impor SKU Gudang Baru.xlsx` (template 40 kolom, hanya kolom Nomor SKU + Judul diisi) dan `Laporan Sinkronisasi SKU Gudang 2026-07-28.xlsx` (7 sheet).

**Urutan eksekusi yang disarankan ke user: impor SKU gudang dulu, baru upload listing ke marketplace.** 9.490 SKU Toko lama akan hilang saat listing di-upload → 33.332 baris pemetaan putus; kalau urutannya terbalik ada jendela waktu di mana pesanan masuk tanpa SKU gudang dan stok tidak terpotong.

## Audit aturan formula (2026-07-28, dipicu spot-check user soal Brio)

**File formula yang benar = `C:\Users\OWNER\Downloads\Data Mobil Lebih dari 1 Formula.xlsx` → SHEET2** (207 model, kolom `Nama Mobil` / `Generasi` / `Total Formula`). Sheet1 hanya memuat 13 model dan **bukan** acuan lengkap — sempat kupakai dan menghasilkan 85 "pelanggaran" palsu. Sebaran Total Formula: 195 model TF=1, 9 model TF=2, Baleno 3, Corolla 9, Civic 11.

Aturan: **Total Formula = N berarti model itu hanya boleh memakai N kode generasi di SKU**, berapa pun jumlah generasi aslinya. Contoh user: Brio punya Gen 1 & Gen 2 tapi TF=1 → SKU-nya hanya `G1`, tidak ada `G2`. (Terverifikasi: `HND-BRI` memang hanya `G1`.)

Hasil audit seluruh listing: **209 model sesuai, 5 melanggar, 135 model belum ada di file formula.**

**5 model melanggar** (TF=1 tapi memakai 2 kode generasi) — kode yang benar `G1`, sisanya berlebih:
`VLK-TIG` (+G2, 24 SKU gudang terlanjur dibuat), `HND-CRV` (+G4, 66), `HND-WRV` (+G2, 66), `TYT-FTN` (+G2, 66), `TYT-AGY` (+G2, 66). Total **288 SKU gudang terlanjur ada di Big Seller** untuk kode berlebih; hanya 20 baris listing yang masih memakainya. Perbaikan listing belum dilakukan.

**Jebakan yang harus diingat:** 79 model di luar file formula masih multi-generasi. Membuat SKU gudang untuk model-model itu sekarang berisiko — kalau file formula nanti diperluas, SKU-nya berubah lagi dan SKU gudang yang baru dibuat langsung jadi yatim. Karena itu file impor **dipecah dua**: `SIAP IMPOR` (2.620) dan `TUNDA (model belum berformula)` (994).

## Update listing 2026-07-29 (19 file diganti user)

Jumlah baris identik (113.932), **1.371 sel SKU berubah**, 0 nama produk & 0 varian berubah. Isi perubahannya: 1.310 = koreksi segmen toko OT→UA / OP→SP (saran 07-28 dijalankan user di sumber), 34 = Nissan Livina X-Gear `G1`/`G2` → `5S`/`7S` (Total Formula-nya akhirnya ditentukan: 5-seater vs 7-seater), 18 = tukar tier Elite↔Epic di Hyundai Matrix & Chevrolet Trooper, 4 = placeholder angka Lazada Gran Max jadi `DHT-GMX`/`DHT-GMXP`, sisanya perbaikan warna tertukar (Navara, Hilux Rangga). Muncul juga `UA_TikTok_2.xlsx` (isinya kosong, 0 baris).

**Dampak ke Big Seller: NOL.** Semua SKU yang berubah ternyata sudah ada di Big Seller, jadi daftar 3.614 yang perlu dibuat **identik** — file impor 07-28 masih valid (diverifikasi: 0 SKU beda, 0 judul beda). Yang bergeser hanya laporan: yatim 20.606→20.640 (+34 NSN-LXG `G1`/`G2` jadi yatim), sudah-ada 12.689→12.655, perlu-dibenahi 9.616→9.612, koreksi OT/OP 1.311→0.

**5 pelanggaran formula BELUM dibetulkan** di update ini (Tiguan/CRV/WRV/Fortuner/Agya masih 2 kode generasi).

**Pelajaran:** kalau user mengganti file listing, diff posisional per file (jumlah baris sama → bandingkan indeks) jauh lebih murah daripada memproses ulang dari nol, dan langsung menunjukkan apakah Big Seller benar-benar terpengaruh.

## RISIKO STOK akibat peleburan generasi (ditemukan 2026-07-29)

Spot-check user ("kalau banyak generasi ditarik ke G1, apakah aman?") membongkar konsekuensi yang sebelumnya terlewat. Peleburan generasi memang aman dari sisi *kelengkapan SKU* — diuji 4 cara, 0 celah:
1. Seluruh 113.932 baris listing jatuh ke tepat satu keranjang (76.794 sudah ada di BS / 13.117 masuk file impor / 9.609 perlu dibenahi / 14.412 tanpa SKU) — **0 baris lolos**.
2. Ke-1.371 SKU yang berubah 29 Jul: 1.031 sudah ada di BS, 340 masuk file impor, 0 tak tercakup.
3. Dari 8.387 SKU berkode `G1`: 7.513 sudah ada, **874 belum ada dan semuanya sudah masuk file impor**, 0 tak tercakup.
4. 256 kombinasi model/toko/kategori non-motor punya kode generasi tanpa SKU gudang; semua SKU-nya sudah masuk file impor.

**TAPI stoknya TIDAK ikut pindah.** Big Seller tidak memindahkan stok otomatis saat SKU listing berganti kode generasi. Kondisi per ekspor 28 Juli: dari 20.640 SKU gudang yatim, **16.315 masih ber-stok > 0 (81.927 unit)**; **9.728 di antaranya punya SKU pengganti aktif di listing, menahan 48.781 unit**. Arah terbesar: `G2→G1` 2.647, `G3→G1` 1.800, `G4→G1` 1.238. Contoh: `HND-BRI-UA-R-G2-HTM` menahan 28 unit padahal listing sekarang memakai `HND-BRI-UA-R-G1-HTM`. Dari 9.728 SKU tujuan itu, **1.599 belum ada di Big Seller** — jadi urutannya wajib: impor SKU baru dulu, baru pindahkan stok.

Daftar lengkapnya ada di sheet **"Stok Perlu Dipindahkan"** pada laporan 29 Juli.

## Ekspor Big Seller baru 2026-07-29 (04:34) — file impor BELUM dijalankan

User mengganti ekspor `SKU_Gudang`/`SKU_Match` ke tanggal 29 (file lama dihapus, tidak ada duplikat glob). Perubahan: **33.295 → 33.348 SKU (+53)**, 0 SKU hilang, pemetaan 86.915 → 86.989 (+74), stok turun di 220 SKU (−304 unit, penjualan normal), 0 stok naik.

**Ke-53 SKU baru itu semuanya `CM####`** — tambalan motor dadakan lagi, bukan hasil impor. Jadi **file `SIAP IMPOR` (2.620 SKU) belum dijalankan**; angka "belum ada" tetap **3.614**. Yatim naik 20.640 → 20.693.

**Masalah baru yang terungkap:** total `CM####` di Big Seller sekarang **181** (128 lama + 53 baru), dan **176 di antaranya produk yang sama persis dengan SKU MTR di file impor** — menahan **820 unit stok**. Kalau file impor dijalankan apa adanya, 176 SKU gudang jadi kembar untuk barang fisik yang sama. Hanya 5 yang tak punya padanan MTR (KTM Duke 390). Daftar lengkap di sheet **"Motor CM Tambalan vs MTR"**.

**Jebakan parsing yang sempat menipu:** judul berformat `Model-Toko-Kategori-Warna-Gen` **tidak boleh dipecah dengan `split('-')`** — nama model bisa memuat tanda hubung (`Yamaha MT-25`, `Kawasaki Ninja ZX-6R`, `Nissan X-Trail`). Pakai `-<Nama Toko>-` sebagai pemisah tegas. Kesalahan ini sempat membuat pencocokan CM→MTR terbaca 102/181 padahal sebenarnya 176/181. Kosakata warna juga beda antara CM (`Hijau`, `Biru`) dan MTR (`Hijau Army`, `Biru Benhur`) — perlu kanonikalisasi.

## Keputusan user 2026-07-29 (lanjutan)

6. **SKU motor `CM####` TIDAK di-rename.** User memilih membuat SKU `MTR` baru di Big Seller, lalu **membuat pemetaan sendiri setelah SKU di e-commerce diubah**. Jadi 181 CM#### dibiarkan; jangan buatkan file rename/edit SKU gudang.
7. **File impor mengisi `Gudang` = `Default Warehouse`**, mengikuti pola impor user sendiri yang terbukti jalan (`impor_untuk_membuat_sku_gudang_in (2).xlsx`, 29 Jul, dipakai membuat 53 SKU CM).
8. **Stok TIDAK diisi 5 rata** (user mengoreksi ini) — diisi sesuai kondisi SKU pendahulunya: **nilai TERTINGGI dari SKU lama, bukan jumlah**; kalau tak ada pendahulu → 5.

**TEMUAN KUNCI soal stok Big Seller: 80,5% SKU gudang berstok TEPAT 5 — itu nilai default, bukan stok fisik.** (0 → 15,9%; selain 0/5 cuma 1.214 SKU / 3,6%.) Akibatnya **menjumlahkan stok pendahulu itu keliru**: Kia Sportage G1 akan jadi 35 karena 7 generasi lama masing-masing berstok default 5, padahal generasi-generasi itu barang fisik yang SAMA (itu justru alasan formulanya dilebur). Aturan MAX menghasilkan 3.773 unit (rata-rata 5,0), aturan JUMLAH menghasilkan 8.978 unit — menggelembung 2,4×.

Hasil akhir: dari 3.614 SKU impor, **750 mewarisi stok** (741 di SIAP IMPOR + 9 di TUNDA), 2.864 produk baru dapat 5. Yang berstok selain 5 cuma **74 SKU**. Jejaknya ada di sheet **"Asal Stok SKU Baru"**.

**Template impor Big Seller: kolom yang benar-benar dipakai user cuma 4** — `*Nomor SKU` (1), `*Judul` (2), `Gudang` (5), `Stok` (6). Sisa 36 kolom dikosongkan. Baris contoh bawaan template (Masa Berlaku `Aktifkan`/90/10, Satuan Tambahan `Bungkus`/12, `Kotak`/6) itu **ilustrasi, bukan default** — jangan ikut disalin.

## Upload Shopee UA 2026-07-29: 529 baris gagal — error transien, bukan data

User mengunggah perubahan SKU ke Shopee UA. File hasil `Result_shopee_mass_update_sales_info_361186752_*.xlsx` memuat **529 baris gagal di 14 listing**, semuanya dengan **satu alasan sama**: *"Item masih dalam proses pembuatan. Tunggu 5 detik sebelum membuat variasi."*

**Hipotesis yang diuji dan GUGUR: bukan karena SKU berulang dalam satu listing.** Peleburan generasi memang membuat satu SKU dipakai beberapa varian (mis. `MBZ-CC-UA-E-G1-ABU` di Gen 1–5). Tapi **541 dari 1.660 listing Shopee UA (32,6%) punya SKU berulang dan berhasil**; yang gagal cuma 14 (0,8%). Jumlah varian juga bukan sebabnya — dari 16 listing ber-98-varian, cuma 2 yang gagal. Jadi ini murni rate-limit/race condition di sisi Shopee.

**Penanganan:** cukup unggah ulang baris yang gagal. File hasil Shopee **strukturnya identik dengan template unggah** (15 kolom, blok header baris 1–6), jadi tinggal disalin dengan kolom `Alasan Gagal` (kolom 15) dikosongkan — tidak perlu membangun ulang dari file listing. Sudah dibuatkan `Retry Upload Shopee UA - semua.xlsx` (529 baris) + versi dipecah 7 batch @≤2 listing supaya tidak memicu error yang sama.

Catatan: 46 dari 529 baris memang ber-SKU kosong — itu varian generik ("Model Lain/Custom") sesuai aturan #4, bukan kesalahan.

## Upload TikTok UA 2026-07-29: 19 produk gagal `sku not allow add` — SAMA modelnya dgn Shopee

UA_TikTok_3 (23.445 baris) dipecah 3 untuk batas 10rb baris TikTok. Hasil: Bagian 1 = 392 sukses / 13 gagal, Bagian 3 = 457 sukses / 6 gagal, Bagian 2 (736 produk) tidak jalan sama sekali.

**PELAJARAN PEMECAHAN FILE: TikTok memproses per PRODUK, bukan per baris.** Aku memecah berdasarkan jumlah baris (7.814/7.813/7.818 — nyaris identik), tapi jumlah produknya jadi timpang: **405 / 736 / 463**. Bagian 2 memuat 1,82× produk Bagian 1 (banyak produk kecil: 214 produk hanya 1 varian) sehingga jauh lebih lambat. **Lain kali seimbangkan berdasarkan jumlah product_id, bukan jumlah baris.**

**Kegagalan bersifat PER MODEL, bukan per listing:** 8 model — Hyundai Atoz, Hyundai Santa Fe, Kia Sonet, Toyota Corona, Toyota Harrier, Mitsubishi Galant, Timor, Mercedes Benz C Class — dan untuk tiap model **SELURUH listingnya gagal** (Reguler + Premium + Exclusive), 0 yang lolos. **Model yang sama ini juga gagal di Shopee**, jadi diagnosis Shopee sebelumnya ("transien, cukup unggah ulang") kemungkinan besar KELIRU — penyebabnya spesifik ke listing itu, bukan antrean.

**Tiga hipotesis diuji dan GUGUR** (jangan diulang):
1. *SKU kembar di dalam satu produk* — 343 dari 361 produk ber-SKU kembar justru SUKSES.
2. *Ukuran/jumlah varian* — dari 16 listing ber-98-varian, hanya 2 gagal.
3. *SKU dipakai lintas produk* — cuma 1/19 gagal memakai SKU lintas-produk, sementara 57/849 sukses memakainya.
Tidak ada satu pun fitur data di file kami yang memisahkan 19 produk itu dari 849 lainnya.

**Dugaan tersisa (belum terbukti): sku_id/variation_id di file ekspor sudah basi** untuk listing-listing itu — kalau produknya diedit di platform setelah ekspor diambil, `sku_id` lama tak lagi cocok sehingga TikTok menganggapnya penambahan SKU baru (`sku not allow add`) dan Shopee menganggap item masih dalam proses. **Cara mengujinya: ekspor ulang 8 model itu langsung dari Seller Center, lalu terapkan ulang perubahan SKU di atas ekspor segar.**

**Catatan teknis:** file "Unduh Entri yang Gagal" TikTok **tidak bisa langsung diunggah ulang** — formatnya 42 kolom dengan `err_info` di kolom 1, sedangkan template unggah 45 kolom tanpa kolom itu. Bangun file retry dengan memfilter file sumber asli berdasarkan `product_id` yang gagal.

## Atribut Model (100177) TikTok — kegagalan 29 Juli setelah Bagian 2A/2B

Unggahan 2A/2B menyisakan **317 produk gagal** dengan *"atribut produk is missing, ID:100177, nama: Model"* (1.475 baris), plus 6 produk `sku not allow add` dan 3 produk error rasio gambar.

**Aturan atribut per kategori (dari sheet `HiddenStyle`):** Model **Mandatory** untuk `Kursi & Sarung Kursi (815120)` dan `Radiator… (813968)`, tapi **Optional** untuk `Cover & Shelter Mobil (931592)`. Mayoritas cover MOTOR ternyata berkategori "Kursi & Sarung Kursi" — itu sebabnya cuma produk motor yang kena.

**KUNCI: Model boleh nilai kustom.** Instruksi resmi di baris 5 template: *"Pilih nilai dari menu menurun atau masukkan nilai kustom."* Daftar dropdown-nya (sheet `HiddenAttr`, pasangan kolom 3-4) berisi 1.851 nilai **tanpa nama merek** (`KLX 140`, bukan `Kawasaki KLX 140`) dan **tidak lengkap** — Vario, Scoopy, Soul GT, ZH2 tidak ada. Kalau dipaksa memakai daftar itu, cuma 92 dari 317 produk yang bisa dicocokkan. Karena nilai kustom diizinkan, dipakai instruksi user: **Model = `<Merek> <Tipe>` dari nama produk**.

**`brand` (kolom 7) ditandai "Tidak dapat diedit" dan Opsional** — jadi pengisiannya kemungkinan diabaikan TikTok. Tetap diisi `Undercover Autocare (7398062051938748165)` (format harus menyertakan ID) pada 235 baris yang kosong, sesuai permintaan user; tidak berbahaya kalau diabaikan.

**Jebakan indeks kolom:** file hasil TikTok punya `err_info` di kolom 1 sehingga seluruh kolom bergeser 1 dibanding template unggah (brand kol 8 vs 7, Model kol 34 vs 33). **Jangan hardcode indeks — ambil dari header** (`h1.index('brand')`).

**Jebakan parsing nama produk:** nama seperti `Body Cover Motor / Sarung / Selimut Motor Vario` perlu pembuangan token pembuka berantai; token `/` menyusut jadi string kosong setelah `strip('/-')` sehingga loop berhenti terlalu dini kalau string kosong tidak ikut dibuang. 11 listing generik memang tidak memuat merek di namanya (Vario, Beat, NMAX, PCX, Scoopy, Aerox, Supra X, Vega, Maxi, CRF1100L Africa Twin) — Model-nya terisi tanpa merek, wajar.

Hasil: `Retry TikTok UA - Model & brand diisi.xlsx` — 1.475 baris, 317 produk, 219 nilai Model unik, Model & brand terisi 100%.

## Status Shopee UA per ekspor segar 2026-07-31 — tinggal 11 listing / 182 baris

Ekspor live Shopee UA 31 Jul (`Documents\Undercover\Cek gagal upload\1..5.xlsx`, 23.268 baris / 1.663 listing) dibandingkan ke file target `SKU Gudang Big Seller\UA_Shopee_1..5.xlsx`: **hanya 182 baris di 11 listing yang SKU-nya masih beda**. Retry 30–31 Juli sudah menuntaskan 18 dari 29 listing yang gagal.

**Keempat file `Result_*` 29 Juli ternyata SALING LEPAS**, bukan retry beruntun: 529/93/61/19 baris di 14/8/5/2 listing, irisan NOL — totalnya **702 baris di 29 listing**, bukan 529 di 14 listing seperti tercatat di bagian atas. Digabung jadi `Error Upload\UC\Retry Upload Shopee UA - Gabungan.xlsx`.

Sisa 11 listing itu **seluruhnya subset dari 29 yang gagal** (0 listing bermasalah di luar daftar itu) dan **semuanya produk terlaris** — 5 model saja: Toyota Corona (111 baris), Toyota Harrier (34), Hyundai Atoz (17), Mitsubishi L300 Pickup (14), Hyundai Santa Fe (6). Karena ranking model-model ini 96–166, hasilnya sama saja mau pakai batas top-215, top-217, atau top-331.

**10 dari 11 beralasan transien** ("Item masih dalam proses pembuatan") → cukup unggah ulang. **1 listing tidak akan pernah lolos lewat unggah ulang**: pid `27755059717` Mitsubishi L300 Pickup Reguler — *"Jumlah gambar produk harus antara 3 dan 9"*, harus dibetulkan dulu di Seller Center.

**Pola membangun file unggah yang benar (dipakai 31 Jul):** ambil baris dari **ekspor LIVE**, lalu timpa **hanya kolom SKU** dengan nilai dari file target. Jangan pakai baris file target apa adanya — `sales_info` juga menulis Harga & Stok (dua-duanya "Wajib"), dan file target 29 Jul sudah basi (terbukti 3 baris stoknya beda dari live). Salin pula `_style` per sel dari baris sumber supaya format Shopee ikut terbawa (header r3 fill `FFED7D31` teks putih tebal, r4–r6 `FFD9D9D9`, font teal `FF00BFA5` di kolom SKU Induk/SKU, `freeze_panes=A5`, lebar kolom 20, number_format `@` untuk kolom teks dan `0` untuk Kode Produk). Hasil: `Cek gagal upload\Upload Shopee UA - SKU Terlaris Belum Terupdate.xlsx`.

**KOREKSI catatan 28 Juli — 5 model pelanggar formula sudah beres.** `VLK-TIG`, `HND-CRV`, `HND-WRV`, `TYT-FTN`, `TYT-AGY` di ekspor live 31 Juli **semuanya tinggal kode `G1`** (32–34 baris per model, 0 kode berlebih). Catatan "5 pelanggaran formula BELUM dibetulkan" di bagian atas file ini sudah tidak berlaku.

**Ekspor Shopee kena DUA bug baca sekaligus** — `activePane="bottom_left"` (invalid, bikin `load_workbook` melempar `ValueError`) DAN dimension palsu. Obatnya: rewrite atribut `activePane` di `xl/worksheets/*.xml` jadi `topLeft`, lalu muat dengan `read_only=False`. Ekspor `Result_*` tidak kena bug ini, ekspor listing biasa kena.

**Terbuka, belum ditelusuri:** 239 varian ada di file target tapi **tidak ada di ekspor live**, tersebar di 42 listing (paling banyak 14 varian/listing — Corona, Atoz, Avega Hatchback, Harrier, Range Rover, Timor, Grandis, Kia Sonet). Perlu dipastikan apakah varian itu memang dihapus dari Shopee atau `variation_id`-nya berubah.

## Status Shopee UA per ekspor segar 2026-08-03 — cek scope 215 terlaris, tinggal 1 listing / 14 baris

User pindahkan lokasi ekspor ke subfolder baru `Cek gagal upload\Shopee\` (sebelumnya langsung di `Cek gagal upload\`) — sejalan dengan munculnya subfolder `TikTok\` juga. Ekspor live 5 file (23.164 baris cover-mobil berhasil dicocokkan via `Kode Variasi`, 0 duplikat/tabrakan) dibandingkan ke target `SKU Gudang Big Seller\UA_Shopee_1..5.xlsx` (masih snapshot 07-29, belum ada yang lebih baru) DAN difilter ke ranking **top-215** dari `C:\Users\OWNER\Documents\Undercover\MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx` (di luar repo, sheet "Top 300 Mobil", kolom `No`=rank, data row 6-222, dibuat 07-29, rank tertinggi 217) — file inilah sumber definisi "top-215/217" yang disebut di catatan 31 Juli di atas.

**Hasil: dari 9.789 baris varian / 584 listing / 201 model yang cocok ke top-215, cuma 14 baris di 1 listing yang masih SKU lama** — Mitsubishi L300 Pickup Reguler (pid `27755059717`, rank #166), semua 14 varian masih literal `"SKU"` (placeholder, tak pernah diisi). **Listing ini SAMA PERSIS dengan yang diflag 31 Juli tak akan lolos re-upload biasa** ("Jumlah gambar produk harus antara 3 dan 9") — terkonfirmasi 3 hari kemudian masih persis sama, artinya foto produknya memang belum dibetulkan di Seller Center. SKU target sudah dihitung (`MTB-LP-UA-{R/S}-G1-{warna}`) & disiapkan di `Cek gagal upload\Retry Upload Shopee UA - Mitsubishi L300 Pickup (2026-08-03).xlsx`, TAPI upload-nya akan gagal lagi dengan alasan sama sampai jumlah foto produk dibetulkan dulu di Seller Center (bukan sesuatu yang bisa diperbaiki lewat file SKU).

**Di luar top-215 (FYI, bukan fokus permintaan user kali ini)**: Ferrari 488 Spider & Wuling Darion juga masih ada baris SKU lama/kosong, tapi keduanya tidak masuk 300 model terlaris sama sekali. Vinfast VF3 (produk baru) 0 SKU di semua 17 varian (Reguler/Premium/Exclusive) — juga belum masuk ranking (kemungkinan terlalu baru, penjualannya belum sempat ke-capture saat ranking dibuat 07-29). 2 baris Timor Premium (Silver/Abu-abu) tidak ada pembanding di file target (variasi ditambahkan setelah snapshot 07-29) tapi SKU-nya sudah berformat benar `TIM-TIM-UA-P-G1-*` — bukan masalah, cuma gap referensi.

**Jebakan baru untuk sesi depan**: ranking "Top 300 Mobil" nyelip 4 baris produk BUKAN model mobil (Headlamp Restorer #65, Glass Polish Magic #69, Black Trim Reborn #82, Snow Wash Active Foam #114) — skip kalau memfilter "N model mobil terlaris". Nama model plain di ranking kadang tak match 1:1 ke nama produk Shopee karena Shopee split per bodystyle yang tak dipisah di ranking (Suzuki APV→Arena/Luxury, Honda City→Hatchback/Sedan, Mazda 2→Hatchback/Sedan, Kia Rio→Hatchback/Sedan, Suzuki Aerio→Hatchback/Sedan, Daihatsu Gran Max→Minibus/Pick Up, ranking "Toyota Hardtop / Land Cruiser" gabungan→2 listing terpisah di Shopee) — semua sudah dicek manual sesi ini, 0 gap tersembunyi, tapi kalau nama tak ketemu match langsung, jangan simpulkan "belum dicek" sebelum cek submodel/bodystyle-nya. Peugeot 206 (#169) genuinely tidak ada listingnya sama sekali di UA Shopee (yang ada cuma 2008/3008/5008) — bukan alias miss.

## Cek formula TikTok UA 2026-08-03 (fresh export `Cek gagal upload\TikTok\...template_1/2/3.xlsx`)

User upload ulang ekspor TikTok UA. **Nomor file BEDA urutan dari target** — fresh `_1`=Travel Pouch (20 baris), `_2`=Cover Mobil (23.001 baris, kategori "Cover & Shelter Mobil (931592)" dominan), `_3`=Cover Motor; sedangkan target `SKU Gudang Big Seller\UA_TikTok_1/2/3.xlsx` urutannya `_1`=Motor, `_2`=Pouch, `_3`=Cover Mobil. **Jangan asumsikan file-index sama antara ekspor & target — selalu match by `sku_id` (kolom D/4, ID variasi TikTok), bukan posisi file/baris.** Sheet `Template`, data mulai row 6, `seller_sku` kolom K(11) — konsisten dgn catatan lama.

Baris Cover Mobil dibandingkan ke gabungan target UA_TikTok_1..3 (23.462 entri) by sku_id: 22.977 cocok, awalnya kelihatan **432 baris di 20 listing masih SKU lama** — **DIKOREKSI jadi 423 baris / 19 listing** setelah user konfirmasi 1 dari 20 pid itu adalah listing BYD Atto 3 arsip (lihat di bawah).

**19 listing itu pecah 2 pola:**
1. **6 model "belum dilebur ke formula G1"** (409 baris) — SKU masih pakai kode generasi lama per-tahun (G2..G10, G1F) padahal targetnya sudah collapse ke `G1` semua: Mitsubishi Galant (108: 84 Reguler+16 Premium+8 Exclusive), Hyundai Santa Fe (85), Toyota Corona (97), Mercedes Benz C Class (68 — tier Premium-nya pakai nama alternatif "Body Cover Mobil Mercedes Benz C Class Premium", tanpa suffix "- Undercover Autocare"), Toyota Harrier (34), Hyundai Atoz (17). **INI 6 DARI 8 MODEL YANG SAMA PERSIS gagal upload TikTok 29 Juli** dgn error `sku not allow add` (lihat catatan di atas) — Kia Sonet & Timor dari 8 model itu TIDAK muncul lagi di daftar sekarang (kemungkinan sudah beres di listing, belum diverifikasi eksplisit). Dugaan lama "sku_id sudah basi" di catatan 29 Juli sekarang bisa diuji ulang: **ekspor 08-03 ini PERSIS "re-ekspor segar dari Seller Center" yang disarankan saat itu** — retry upload di atas data ini (bukan di atas ekspor lama) punya peluang lebih besar berhasil.
2. **1 listing kosong total** (14 baris) — Peugeot 405 Reguler, placeholder `"SKu"`/`"SKU"`, belum pernah diisi SKU sama sekali.

**Bukan masalah nyata, cuma informasional**: Wuling Darion (3 tier, 17 baris) — SKU live sudah correctly-formatted (`WLG-DRN-UA-*-G1-*`) tapi target/master belum punya entri model ini sama sekali (kosong) — pola SAMA PERSIS dgn temuan di Shopee hari ini (lihat di atas). Vinfast VF3 (17 baris, semua kosong total) & 2 baris Timor Premium (SKU-nya sudah benar) — `sku_id`-nya tidak ada di file target sama sekali (0 match), konsisten dgn temuan Shopee: model terlalu baru / target belum di-generate ulang sejak snapshot 07-29, bukan bug.

**(Koreksi) BYD Atto 3 Reguler pid `1731375819348411418` (9 baris awalnya masuk hitungan) BUKAN listing aktif — user konfirmasi via screenshot Seller Center: listing ini sudah DIARSIPKAN, dibuat 14/05/2025, 14 SKU warna polos tanpa info generasi.** Listing AKTIF-nya adalah pid `1735577758939972634` (dibuat 29/07/2026, 28 SKU, varian sudah punya info Gen 1 + "Model/Tahun Lain" terpisah per warna) — **sudah 100% benar (28/28 OK)**, tidak perlu perbaikan. Konfirmasi tambahan: 2 listing BYD Atto 3 lain (Exclusive pid `1735577676937528346` 2 baris, Premium pid `1735577677161268250` 4 baris) juga sudah 100% OK. **Pelajaran: data ekspor SKU tidak punya kolom status arsip** — tidak ada cara mendeteksi ini dari file listing sendiri, harus screenshot/konfirmasi user via Seller Center. Kalau nemu listing lama duplikat (nama sama, pid beda, salah satunya SKU-nya jelek/tak pernah dibenahi) dari model lain di masa depan, curigai pola yang sama sebelum dimasukkan ke file retry — tanyakan dulu ke user mana yang aktif.

File koreksi sudah disiapkan: `Cek gagal upload\Retry Upload TikTok UA - 19 produk formula belum diterapkan (2026-08-03).xlsx` (480 baris = full product block dari 19 listing itu, termasuk baris yang sudah benar supaya tiap listing lengkap saat diupload — TikTok proses per-produk; 423 SKU diganti ke target, sisanya dibiarkan). **Belum diupload, nunggu keputusan user.**

**Dua jebakan teknis ditemukan & diperbaiki saat membangun file retry ini (proses 3 iterasi, dicatat sbg pola reusable utk file retry TikTok/Big-Seller berikutnya):**
1. **Harus pertahankan SELURUH struktur workbook asli, bukan cuma sheet `Template`.** Percobaan pertama bikin file retry dgn `openpyxl.Workbook()` baru (cuma 1 sheet) — user tegur "samakan format dgn yang siap upload". File TikTok asli py 8 sheet (`Template, Instruction, HiddenStyle, HiddenAttr, SpecialProductListingType, TemplateConfig, Brand, SalePlatform`), `Template` sendiri 45 kolom termasuk kolom atribut kategori (`Model` di kolom 33, dst).
2. **`ws.delete_rows()` TIDAK ikut membersihkan `data_validations`.** Setelah struktur 8-sheet dipertahankan, Excel masih menampilkan "we found a problem with some content... do you want us to try to recover" saat file dibuka. Root cause: template asli py **183.989 entri `<dataValidation>`** — bukan 1 per kolom, tapi 1 PER BARIS untuk ~8 kolom atribut kategori-dependent (spt `Model`, krn pilihan dropdown beda per kategori produk; 22.996 baris × 8 kolom ≈ jumlah itu). Setelah baris dipangkas dari 23.001 ke ratusan, puluhan ribu `dataValidation` itu masih menunjuk baris yang sudah tidak ada → Excel curiga & minta "repair". **Fix: `ws.data_validations.dataValidation = []`** (hapus semua validasi) sebelum save — aman krn validasi TikTok yang sesungguhnya terjadi di server saat upload, bukan bergantung pada metadata Excel ini.

**Pola pembuatan file retry yang benar (hasil akhir)**: `load_workbook(path)` PENUH (bukan bikin baru) → snapshot baris yang mau disimpan (value+style per sel) → `ws.delete_rows(6, max_row-5)` SEKALI (hapus semua baris data dalam 1 panggilan, jauh lebih cepat dari hapus satu-satu) → tulis ulang baris yang disimpan mulai row 6 dgn SKU di-override sesuai target → **`ws.data_validations.dataValidation = []`** → save. Efek samping bagus: ukuran file turun dari ~50MB ke ~300KB (sheet1.xml openpyxl nulis SEMUA string sbg `inlineStr` bukan shared-string table by default — perilaku openpyxl yg konsisten, bukan bug, tapi bikin file besar kalau tidak dipangkas). **How to apply**: kapan pun bikin file retry TikTok/Big-Seller dgn cara "load full workbook asli lalu pangkas baris", WAJIB (1) pertahankan semua sheet asli DAN (2) strip data validations sebelum save.

Ke-5 baris BYD Atto 3 warna-polos (Abu-abu/Hitam/Biru/Merah/Hijau) yang sempat kelihatan sbg "residual bug 07-17 tak terselesaikan" TERNYATA seluruhnya ada di pid arsip di atas — sudah ikut ter-exclude begitu pid itu dibuang dari file, bukan perlu ditangani terpisah.

## Cek formula TikTok UA 2026-08-05 — SEMUA fix 08-03 sudah live, top-215 100% bersih

User upload ekspor TikTok baru lagi (`Cek gagal upload\TikTok\...20260805_..._1/2/3.xlsx` — nomor file GESER LAGI, kali ini `_1`=Cover Mobil 22.915 baris, `_2`=Cover Motor, `_3`=Travel Pouch; pola pergeseran nomor file ini konsisten tiap ekspor, jangan pernah asumsikan berdasar nomor, selalu cek isi/kategori dulu).

**Jebakan kolom baru**: header `quantity` HILANG dari ekspor kali ini (dibanding 08-03) — `seller_sku` geser dari kolom **11 ke kolom 10**. File target `UA_TikTok_1/2/3.xlsx` tetap kolom 11 (tidak berubah, snapshot lama). **WAJIB selalu ambil index kolom dari header row 1 (`header.index('seller_sku')`), jangan hardcode 11** — ini persis pola yang sudah diperingatkan di catatan lama (kolom TikTok suka geser), sekarang kejadian beneran.

**Hasil scan penuh + filter top-215** (pakai ranking file yang sama, `MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx`): dari 9.669 baris / 563 listing / 189 model yang termasuk top-215, **100% OK, 0 NEEDS_UPDATE.** Semua 19 listing yang diperbaiki 08-03 (Mitsubishi Galant, Hyundai Santa Fe, Toyota Corona, Mercedes Benz C Class, Toyota Harrier, Hyundai Atoz, Peugeot 405) sudah live dgn benar — retry file yang dibuat 08-03 berhasil diupload.

Sisa gap (17 baris) SAMA PERSIS dgn temuan 08-03: cuma Wuling Darion (3 tier), target masih kosong krn model belum ada di master — bukan bug, tinggal tunggu master dilengkapi. Vinfast VF3 (17 baris kosong total) & 2 baris Timor juga konsisten (sku_id tidak ada di target).

**Konfirmasi tambahan berguna**: listing **"Mitsubishi L300" di TikTok** (beda nama dari Shopee yg "Mitsubishi L300 Pickup") **sudah 100% OK/benar** — independen dari listing Shopee-nya yang masih terblokir validasi jumlah foto. Jadi blocker L300 itu spesifik ke Shopee, tidak mempengaruhi TikTok.

**27 nama ranking top-215 gagal exact-match ke nama produk TikTok, sudah dicek satu-satu**: mayoritas pola sama seperti Shopee (Shopee split bodystyle: APV Arena/Luxury, Honda City Hatchback/Sedan, Mazda 2/3 Hatchback/Sedan, Kia Rio Hatchback/Sedan, Suzuki Aerio Hatchback/Sedan, Gran Max Minibus/Pick Up, Pajero→Pajero Sport, Hardtop/Land Cruiser terpisah, Wrangler tanpa "Rubicon", Tiggo 8 dgn suffix "Pro") — semua confirmed OK, 0 gap tersembunyi. **8 nama genuinely TIDAK ADA listing Cover Mobil-nya sama sekali di TikTok** (beda dari "ada tapi salah nama"): Mitsubishi Strada Triton (cuma ada "Mitsubishi Triton" biasa), Daihatsu Taft GT, Hyundai Getz, BYD Seal, Geely EX2, Mercedes Benz SLK Class, Daihatsu Ceria, Volvo 850 Sedan — belum pernah dibuatkan listing TikTok utk model2 ini (bukan soal SKU, soal listing belum ada).

## Cek formula Lazada UA 2026-08-05 — 566 baris/21 listing/8 model belum dilebur, SEMUA masuk top-215

User upload ekspor Lazada baru: `Cek gagal upload\Lazada\pricestock403342000257export1785895181356_0805-09-59-41.xlsx`. Struktur: sheet `template` (+ `template_hide`, `Hasil  Proses`, `global_hide`), kolom by-header (bukan hardcode) — `sku.skuId` (5) = ID variasi stabil utk matching, `Seller SKU` (13) = SKU kita, `status` (6) = active/inactive, data mulai row 5. Sama seperti Shopee/TikTok, `UA_Lazada.xlsx` (21.869 baris) dipakai sbg target, di-match by `sku.skuId` (bukan posisi baris).

**Hasil: 21.441 baris cocok, 566 masih SKU lama (97,4% sudah benar). SEMUA 566 baris itu ada di dalam top-215** (rank 96–125, 0 baris di luar) — 8 model: Toyota Corona (168: 138 R+20 P+10 E), Mitsubishi Galant (151: 126+16+9), Mercedes Benz C Class (77: 64+8+5), Hyundai Santa Fe (100: 83+11+6), Toyota Harrier (34: 28+4+2), Hyundai Atoz (19: 15+2+2), Mitsubishi Grandis (11, cuma Reguler), Kia Sonet (6: 4+2).

**Pola sama persis dgn yang sudah difix di Shopee (31 Jul) & TikTok (03 Agu): SKU masih pakai kode generasi lama per-tahun (G2..G10) padahal harusnya `G1` semua** (mis. `TYT-COR-UA-S-G4-EBR` → seharusnya `TYT-COR-UA-S-G1-EBR`; Lazada py suffix disambiguasi `_G6`/`_G9` dst utk generasi yg secara fisik sama tapi perlu SKU unik per listing Lazada — target file SUDAH benar termasuk suffix ini, jadi perbandingan langsung tetap akurat). **6 dari 8 model ini (Corona/Galant/C Class/Santa Fe/Harrier/Atoz) SAMA PERSIS dengan yang gagal TikTok 29 Juli & sudah dibetulkan di TikTok+Shopee** — artinya **fix formula-G1 itu TIDAK PERNAH dipropagasi ke Lazada sama sekali**, channel ini kelewat dari semua retry sebelumnya. **Kia Sonet** juga bagian dari 8-model gagal TikTok 29 Juli asli, tapi entah kenapa tidak muncul lagi di scan TikTok 08-03/08-05 (kemungkinan sudah kebetulan benar di TikTok, TIDAK diverifikasi eksplisit) — di Lazada masih rusak. **Mitsubishi Grandis BARU, belum pernah muncul di temuan Shopee/TikTok sebelumnya** — kemungkinan Grandis di channel lain sudah benar (scan-scan sebelumnya full-catalog, harusnya kena kalau rusak di sana), tapi belum di-cross-check eksplisit.

Semua 566 baris di listing berstatus `active` (0 di listing `inactive`) — beda dari kasus BYD Atto 3 TikTok, di sini tidak ada isu duplikat-arsip.

**Bukan masalah, cuma informasional**: Vinfast VF3 (17 baris) — `sku.skuId`-nya tidak ada di target sama sekali, SKU-nya masih ID auto-generate Lazada (pola `{pid}-{skuid}-{n}`, bukan SKU kita) — konsisten dgn temuan 2 channel lain: model terlalu baru, master belum py entri.

File koreksi disiapkan: `Cek gagal upload\Retry Upload Lazada UA - 21 listing formula belum diterapkan (2026-08-05).xlsx` (608 baris = full block 21 listing, 566 SKU diganti, sisanya dibiarkan). Dibangun pakai pola yang sama & sudah terbukti aman dari kasus TikTok 08-03: load workbook PENUH (4 sheet dipertahankan), snapshot+delete_rows sekali+tulis ulang, **strip data validations sebelum save** (Lazada cuma py 6 dataValidation, jauh di bawah kasus TikTok yg 183rb, tapi tetap distrip demi konsisten & aman) — 0 masalah XML terverifikasi. **Belum diupload, nunggu keputusan user.**

## Root cause upload Lazada 29 Juli gagal sebagian (10.587/21.865) — dianalisis dari laporan "Failed Product" asli

User kasih 2 file dari Seller Center: (1) `Unduh berkas Excel` ternyata cuma file yang diupload lagi (21.865 baris, bukan laporan gagal — jangan salah pakai file ini lain kali), (2) `Download Failed Product` (`pricestock..._0729-17-23-17.xlsx`, sheet `Hasil  Proses` + `template`) — INI yang py detail sebenarnya. Dipecah jadi 2 penyebab, dihitung persis dari isi log:

1. **10.534 dari ~11.278 baris "tidak sukses" BUKAN kegagalan — pesan `Hasil Proses`-nya literal "Data no change in file,not update."** Lazada bandingkan baris upload ke data live-nya; kalau menurut Lazada tidak ada yg berubah (kemungkinan besar krn cuma bandingkan Harga/Stok — endpoint-nya sendiri namanya "pricestock" — bukan SKU), baris itu DILEWATI SELURUHNYA, termasuk kolom SKU yg sebenarnya beda. **Ini persis pola yang sudah diketahui dari Shopee 31 Juli** ("file target 29 Jul sudah basi, 3 baris stoknya beda dari live") — tapi utk Lazada dampaknya lebih parah: bukan cuma stok yg salah ke-skip, SKU-nya pun ikut tidak ter-apply kalau harga/stok kebetulan sama persis dgn yg sudah live. **How to apply: SELALU generate file upload Lazada dari ekspor LIVE PALING BARU (bukan target/master lama) supaya harga/stok pasti beda dikit dari yg live dan Lazada beneran memproses barisnya** — sama seperti pola "ambil baris dari ekspor LIVE" yg sudah dipakai utk Shopee.

2. **744 baris / 22 listing — error genuinely: `F_IC_SCENE_EDIT_092: Duplicate input sku ID`.** 22 listing ini PERSIS SAMA dgn 8 model yg ditemukan masih rusak di Lazada 05 Agustus (Toyota Corona, Mitsubishi Galant, Hyundai Santa Fe, Mercedes Benz C Class, Toyota Harrier, Hyundai Atoz, Mitsubishi Grandis, Kia Sonet — pecah per tier R/P/E). **Ditelusuri sampai baris spesifik**: skuId yg disebut "conflict" di pesan error SEMUANYA adalah varian **"Model/Tahun Lain" (catch-all)** — varian yg per aturan #4 memang sengaja TIDAK diberi SKU asli (Seller SKU-nya tetap placeholder auto-generate Lazada `{pid}-{timestamp}-{n}`, bukan salah kita). Dugaan kuat (belum 100% confirmed cara kerja internal Lazada): saat SEMUA ~14 baris catch-all 1 produk (5 warna Reguler + 9 tier Strip) diupload BERSAMAAN dalam 1 request sbg bagian dari batch raksasa 21.865 baris, sistem Lazada gagal generate/validasi SKU auto-placeholder-nya scr bersamaan dan menganggapnya "duplicate", **menjatuhkan SELURUH PRODUK (semua variannya, bukan cuma yg catch-all) — itulah kenapa polanya selalu "SELURUH listing gagal", bukan cuma baris tertentu.**

**Kenapa retry 608-baris tadi (05 Agustus) sukses 100% padahal produk yg sama**: (a) dibangun dari ekspor LIVE paling baru (bukan target basi) → harga/stok kemungkinan sudah beda dari 07-29 shg Lazada beneran memproses, bukan skip; (b) batch JAUH lebih kecil (608 vs 21.865 baris sekaligus) → kemungkinan mengurangi/menghindari kondisi race/collision yg memicu "duplicate input sku ID" pada baris catch-all. **How to apply ke depan: kalau mau upload ULANG SELURUH katalog Lazada (bukan cuma listing yg kepetakan bermasalah), JANGAN kirim >20rb baris sekaligus — pecah per batch lebih kecil (ratusan-ribuan baris), dan selalu dari ekspor live terbaru.**

## Revisi aturan 2026-08-05: Hyundai Santa Fe pecah 2 formula, Mazda 3 dapat kode bodystyle

**Keputusan user (revisi dari status sebelumnya, JANGAN didesain ulang tanpa instruksi baru):**
1. **Hyundai Santa Fe**: sebelumnya Total Formula=1 (semua generasi → `G1`). SEKARANG **Total Formula=2**: **Gen 1, 2, 3 (2001-2018) → `G1`**, **Gen 4, 4 Facelift, 5 (2019-2024) → `G2`**. Sudah ditambahkan ke `C:\Users\OWNER\Downloads\Data Mobil Lebih dari 1 Formula.xlsx` Sheet2 sbg entri No. 214 (row 532-533), backup file lama disimpan `.bak_20260805` di folder sama.
2. **Mazda 3**: bukan soal Total Formula (bukan peleburan generasi), tapi **kode model di segmen SKU ke-2 dibedakan per bodystyle**: **`3S` untuk Sedan**, **`3H` untuk Hatchback**. Dicek dari listing Shopee: Sedan sudah kebetulan pakai `MZD-3S-...` (tidak perlu diubah), Hatchback masih pakai `MZD-M3-...` (perlu diganti ke `MZD-3H-...`) — TAPI harus diverifikasi ulang di semua channel/kombinasi, jangan asumsikan cuma Hatchback yg salah.

**Konteks untuk sesi depan**: pengecekan "produk mana yang belum sesuai 215 terlaris" yang sedang dikerjakan di UA (Undercover Autocare) ini **akan diperluas ke toko Smartprotection, Otoprotection, dan Otonation juga** — bukan permintaan sekarang, tapi rencana lanjutan yang sudah dikonfirmasi user, catat supaya sesi depan tidak kaget/tidak perlu tanya ulang scope-nya.

## Eksekusi revisi Santa Fe & Mazda 3 di UA — 2026-08-05

Revisi dari section di atas SUDAH DIEKSEKUSI penuh: target file diupdate + file upload dibuat, utk Undercover (UA) di 3 channel. **Belum diupload user, cuma disiapkan.**

**Struktur listing yang ditemukan (penting utk sesi depan):**
- **Mazda 3 punya 2 grup listing per channel** (Sedan & Hatchback), tapi **penamaannya TIDAK seragam antar channel**: TikTok & Lazada sudah eksplisit "Mazda 3 Sedan .../Mazda 3 Hatchback ..." di nama produk. **Shopee TIDAK** — grup Hatchback di Shopee namanya cuma "Mazda 3 {Reguler/Premium/Exclusive}" polos (tanpa kata "Hatchback" sama sekali), harus dibedakan dari Sedan lewat SKU prefix yg sudah ada (`3S` vs `M3`) atau pid, BUKAN dari nama produk. Jangan tertukar dgn "Mazda Mazda 323 Interplay" (produk beda total, kode `M3I`).
- Pid per channel (dicatat supaya sesi depan tak perlu re-derive): **Shopee** Sedan={8715979977 R, 20969563464 P, 20844907627 E}, Hatchback={28513184519 R, 40054813684 P, 29913185141 E}. **TikTok** Sedan={1729570012014151706 R, 1729599009893615642 P, 1729576405019035674 E}, Hatchback={1730234696329036826 R, 1730234729038578714 P, 1730234737554261018 E}. **Lazada** Sedan={8674018839 R, 8674022602 P, 8674030182 E}, Hatchback={8674024581 R, 8674024578 P, 8674018854 E}.

**Temuan bonus (bug lama, di luar scope revisi tapi langsung ketemu & sekalian dibetulkan krn di listing yg sama):**
1. **TikTok Mazda 3 Sedan Reguler**: 5 baris (warna "Warrior Biru", semua 5 generasi) masih salah pakai kode Hatchback `MZD-M3-...` — seharusnya `MZD-3S-...` dari dulu, independen dari revisi baru ini.
2. **Shopee Mazda 3 Hatchback Exclusive**: 5 baris (Gen1/2/3/3F/4) SKU-nya kosong total (belum pernah diisi) — bukan catch-all "Model Lain", genuinely gap generasi asli.
3. **Lazada Mazda 3 Hatchback**: 20 baris (2 Exclusive + 18 Reguler-tier-Strip, semua Gen3/3F) masih placeholder auto-generate Lazada, sama sekali belum py SKU asli.
Ketiganya sudah dihitung SKU yang benar (color-code parser: Abu-abu→ABU, Hitam→HTM, Biru Benhur→BRU, Merah→MRH, Hijau Army→GRN, Silver→SLV; Strip {Elite/Epic/Warrior}+{Abu/Biru/Merah}→{E/P/W}+{AB/BR/MR}; kategori dari kata di nama produk, TAPI baris Reguler dgn warna Strip-tier pakai kode kategori `S` bukan `R`) & masuk file upload.

**Hasil akhir per channel** (baris berubah dari total baris full-block yg disiapkan, biar listing lengkap saat diupload):
| Channel | Baris berubah | Total baris disiapkan | Listing tersentuh |
|---|---|---|---|
| Shopee | 136 | 204 | 6 (Santa Fe R/P/E + Mazda3 Hatchback R/P/E) |
| TikTok | 141 | 257 | 7 (+ Mazda3 Sedan Reguler utk fix bug lama #1) |
| Lazada | 170 | 187 | 6 |

**File target reference SUDAH diupdate** (backup `.bak_20260805` dibuat dulu utk semua): `UA_Shopee_1.xlsx` (+45), `UA_Shopee_2.xlsx` (+86), `UA_Shopee_4.xlsx` (+5), `UA_TikTok_3.xlsx` (+141), `UA_Lazada.xlsx` (+170) — semua 447 baris (136+141+170) berhasil di-match & diupdate (0 gagal match), termasuk baris-baris gapfill di atas krn ternyata entri targetnya sudah ada, cuma nilainya salah/kosong.

**File upload siap disiapkan di `Cek gagal upload\`**:
- `Retry Upload Shopee UA - Santa Fe & Mazda 3 revisi (2026-08-05).xlsx` (204 baris, format `sales_info` biasa)
- `Retry Upload TikTok UA - Santa Fe & Mazda 3 revisi (2026-08-05).xlsx` (257 baris, 8-sheet dipertahankan + dataValidations di-strip, sama pola yg terbukti aman)
- `Retry Upload Lazada UA - Santa Fe & Mazda 3 revisi (2026-08-05).xlsx` (187 baris, 4-sheet dipertahankan + dataValidations di-strip)

**Juga diupdate**: `Data Mobil Lebih dari 1 Formula.xlsx` Sheet2 — entri baru No.214 Hyundai Santa Fe (Gen1-3=G1, Gen4-5=G2), backup `.bak_20260805` di folder Downloads yang sama. Mazda 3 SENGAJA TIDAK ditambahkan ke file ini krn bukan kasus Total Formula (bukan peleburan generasi), tapi keputusan kode-model per-bodystyle.

**Belum dikerjakan**: OT/OP/SP belum disentuh sama sekali utk revisi ini (scope eksplisit user cuma UA "sekarang" — perluasan ke 3 toko lain itu rencana terpisah, lihat catatan revisi di atas).

## KOREKSI KRITIS 2026-08-05: fix Lazada di atas awalnya CACAT — lupa keunikan SKU per listing

User upload retry Lazada pertama, hasilnya **181 dari 187 baris gagal** dgn error `BIZ_CHECK_SELLER_SKU_DUPLICATE: SKU Penjual yang Anda masukkan sama`. Root cause: **Lazada mewajibkan `Seller SKU` unik per baris DALAM SATU listing** (beda dari Shopee/TikTok yg justru sengaja membolehkan >1 varian berbagi 1 SKU — itu esensi "formula" konsolidasi). Fix pertama cuma nge-swap kode generasi (G1→G2 dst) tanpa cek apakah hasilnya bentrok dgn baris lain di listing yg sama — jadi banyak baris jatuh ke SKU identik.

**Temuan lebih dalam saat investigasi**: **Hyundai Santa Fe di LAZADA ternyata TIDAK PERNAH benar² dikonsolidasi ke formula sejak awal** — beda dari Shopee/TikTok. Data live sebelum disentuh sesi ini masih pakai kode PER-GENERASI ASLI yg genuinely unik (`G1,G2,G3,G4,G4F,G5` masing2 beda), BUKAN skema "semua→G1 + suffix `_Gn`" yg dipakai listing lain (mis. Toyota Corona, Honda Jazz) atau yg tersimpan di file target lama. File target `UA_Lazada.xlsx` (snapshot lama) MEMANG sudah py rencana skema konsolidasi+suffix utk Santa Fe, tapi listing live-nya sendiri tidak pernah disinkronkan ke situ. **Mazda 3 Hatchback SEBALIKNYA sudah lama pakai skema konsolidasi+suffix yg benar** (`MZD-M3-UA-S-G1-EAB_G1`, dst) — cuma 2 baris gap (Gen3/Gen3F) yg perlu suffix baru, bukan re-derive total.

**Fix final (verified 0 duplikat di 187/187 baris, semua 6 listing)**:
- **Santa Fe**: DIHITUNG ULANG TOTAL dari live data asli (bukan dari json hasil fix pertama yg sudah kadung salah) — dikelompokkan per (pid, kategori, warna), dipecah ke grup G1 (Gen1/2/3) & G2 (Gen4/4F/5), dalam tiap grup **anggota gen TERENDAH jadi kode polos (bare), sisanya disuffix `_G{nomor gen asli}`** (mis. `_G2`, `_G3`, `_G4F`, `_G5`). 85 baris berubah (naik dari klaim awal yg jg 85 tapi nilainya salah).
- **Mazda 3 gapfill (Lazada)**: 2 baris gap (Gen3/Gen3F) per warna di-suffix `_G32`/`_G3` (ikut pola literal yg sudah ada di listing yg sama utk warna lain, spt "Merah" yg py `_G32`=Gen3 & `_G3`=Gen3F — bukan pola yg saya karang sendiri).
- File target `UA_Lazada.xlsx` & file retry `Retry Upload Lazada UA - Santa Fe & Mazda 3 revisi (2026-08-05).xlsx` SUDAH ditimpa ulang dgn nilai yg benar. **Shopee & TikTok TIDAK terpengaruh bug ini** (platform itu boleh SKU kembar, tidak butuh suffix).

**How to apply ke depan — WAJIB dicek setiap kali bikin/ubah SKU utk Lazada**: (1) SKU Lazada harus unik PER LISTING, tidak cukup benar secara formula/master; (2) kalau >1 baris dalam 1 listing bakal punya SKU dasar yg sama (peleburan generasi), WAJIB kasih suffix `_G{nomor generasi asli baris itu}` ke semua kecuali satu (biasanya generasi terendah); (3) SEBELUM membangun file upload, jalankan self-check: group baris per (Product ID, Seller SKU final), pastikan tidak ada grup >1 baris; (4) **jangan asumsikan status konsolidasi listing dari file target/master** — selalu verifikasi ke ekspor LIVE listing itu sendiri, karena bisa saja (spt Santa Fe ini) listing live belum pernah benar² disinkronkan walau targetnya sudah lama dihitung.

**(2026-08-05 lanjutan) Upload Shopee UA Santa Fe & Mazda 3: 102 baris gagal transien, semuanya Mazda 3 Hatchback.** `Result_shopee_mass_update_sales_info_361186752_20260805115939.xlsx` — semua 102 baris (Reguler 84, Premium 12, Exclusive 6) satu alasan sama: *"Item masih dalam proses pembuatan. Tunggu 5 detik sebelum membuat variasi."* — pola transien yg sudah dikenal sejak 29 Juli, SKU-nya sendiri sudah benar (`MZD-3H-UA-...`), Santa Fe di file yg sama SEMUA sukses. Retry dibuat langsung dari file `Result_*` (salin 15 kolom + blok header 1-6, kosongkan kolom `Alasan Gagal`) → `Cek gagal upload\Retry Upload Shopee UA - Mazda 3 Hatchback (2026-08-05).xlsx`, 102 baris. Belum diupload ulang.

## Cek formula Otonation (OT) 2026-08-05 — perluasan pertama ke toko non-UA, 118 baris/8 listing belum sesuai

Sesuai rencana perluasan (lihat catatan revisi di atas), sesi ini mulai cek OT (toko pertama dari 3 yg direncanakan: SP/OP/OT). User taruh ekspor baru di `Cek gagal upload\OT\1.xlsx` & `2.xlsx` (Shopee sales_info, shop id 407202910, folder direorganisasi — UA sekarang di `Cek gagal upload\UA\{Shopee,TikTok,Lazada}\`, bukan langsung di `Cek gagal upload\` lagi). Target reference: `SKU Gudang Big Seller\OT_Shopee_1.xlsx` & `_2.xlsx` (sudah ada dari sesi lama, format identik UA_Shopee) — **konsisten dgn aturan konsolidasi #1: OT pakai prefix `UA` di SKU-nya sendiri** (fisik gudang sama dgn UA), match by `Kode Variasi` sama seperti UA.

**Struktur nama produk OT beda dari UA**: `Cover Mobil / Sarung Mobil {Model}` (polos) atau `Cover Mobil / Sarung Mobil {Model} {Semi Outdoor|Extreme Outdoor|Outdoor}` — bukan Reguler/Premium/Exclusive spt UA. "Outdoor" bertingkat 3 (polos/Semi/Extreme) kemungkinan analog Reguler/Premium/Exclusive tapi belum dikonfirmasi user. Tier warna Strip pakai teks **"Strip 1/2/3"** (bukan "Elite/Epic/Warrior" spt UA) — tapi ini cuma soal teks nama varian, SKU target sudah benar duluan (Strip1→P/Epic, dst — sudah ter-encode di target file, tidak perlu diterjemahkan ulang).

**Hasil: 9.251 baris cocok, 118 baris/8 listing belum sesuai** — pecah 2 penyebab:
1. **84 baris — Toyota Corona (3 listing) & Mitsubishi Galant (2 listing)**: bug formula-G1 LAMA yg sama persis dgn yg sudah dibetulkan di UA (kode generasi lama G2..G11 blm dilebur ke G1). Target file OT sudah benar dari dulu, tinggal apply.
2. **34 baris — Hyundai Santa Fe (2 listing) & Mazda 3 Hatchback (1 listing)**: kena revisi BARU hari ini (G1/G2 split utk Santa Fe, `3H` utk Mazda3 Hatchback) — **target file OT_Shopee LAMA masih py rule lama (G1 semua utk Santa Fe, `M3` utk Mazda3)**, jadi dihitung ulang pakai rule baru (bukan dipercaya dari target lama) & target file-nya SUDAH diupdate juga (34 baris, backup `.bak_20260805` dibuat dulu).

File retry: `Cek gagal upload\Retry Upload Otonation - SKU belum sesuai (2026-08-05).xlsx` (123 baris = full block 8 listing, 118 SKU diganti). **Belum diupload.**

**Catatan metodologi utk sesi SP/OP berikutnya**: SELALU cek dulu apakah model yg kena revisi terbaru (Santa Fe/Mazda3) ada di toko itu — kalau ada, jangan percaya target file store tsb scr mentah (bisa jadi masih versi rule lama krn belum ikut ter-update sesi ini), hitung ulang pakai fungsi `santafe_new_sku`/`mazda3_new_sku` dari live data langsung.

## Cek formula Smartprotection (SP) 2026-08-05 — toko ke-2 dari perluasan, 82 baris/8 listing

User taruh ekspor baru di `Cek gagal upload\SP\Shopee\1.xlsx` & `2.xlsx` (shop id 473932094). Target: `SKU Gudang Big Seller\SP_Shopee_1.xlsx` & `_2.xlsx` — **SP pakai prefix SKU sendiri `SP`** (beda dari OT yg pakai `UA` — sesuai aturan konsolidasi: OP=SP secara fisik, bukan UA). Tier warna Strip pakai kode singkat `S1A/S2A/S3A` dst (S1=Epic,S2=Elite,S3=Warrior + A/B/M=Abu/Biru/Merah) — beda dari UA/OT yg pakai `EAB/PAB/WAB`-style, tapi ini otomatis aman krn cuma nyalin dari SKU yg sudah ada, tidak perlu diterjemahkan ulang.

**Jebakan baru ditemukan sesi ini**: **teks varian SP untuk Santa Fe SAMA SEKALI TIDAK py kata "Gen"** — cuma rentang tahun polos (`"Warior Abu,2012-2018"`, `"2005-2012"`). Fungsi `santafe_new_sku()` yg parse `vname` cari pola "Gen N" GAGAL TOTAL di sini (regex tidak ketemu, fallback ke "tidak berubah" — nyaris ke-skip diam-diam tanpa terdeteksi kalau tidak dicek ulang manual). **Fix: baca nomor generasi dari SEGMEN KE-5 SKU SAAT INI sendiri** (`G1/G2/G3/G4/G4F/G5` — sudah pasti ada krn listing lama SP genuinely pakai kode per-generasi asli spt OT/Lazada UA, bukan dari teks varian) — jauh lebih robust, tidak bergantung pola teks yg beda2 per toko. **How to apply: mulai sesi depan (OP dst), JANGAN pakai `santafe_new_sku(current_sku, vname)` — pakai versi yg baca generasi dari `current_sku` sendiri, karena vname formatnya sudah terbukti beda2 tiap toko** (UA="Gen N (tahun)", OT="Gen N (tahun)", SP="tahun polos tanpa kata Gen").

**Hasil: 7.782 baris cocok, 82 baris/8 listing belum sesuai** — 2 penyebab:
1. **51 baris — bug formula lama** (Mitsubishi Galant 14 + Galant Transparan 5 legacy CVR-code, Mercedes Benz C Class 28 pakai kode aneh `GB19821993`-style + C Class Transparan 1, Toyota Corona Transparan 2, Mitsubishi Grandis Transparan 1) — target SP sudah benar dari dulu, tinggal apply.
2. **31 baris — Hyundai Santa Fe** (28 non-Transparan + 3 Transparan) kena revisi baru — dihitung ulang & target `SP_Shopee_1.xlsx` diupdate (backup `.bak_20260805` dibuat), Mazda 3 di SP TIDAK bermasalah (tidak ada di daftar NEEDS_UPDATE — kemungkinan sudah OK atau belum ada listingnya, ada 2 baris "no_target" utk Mazda 3 Sedan/Hatchback masing2, kemungkinan varian baru/belum di-generate targetnya, bukan salah).

File retry: `Cek gagal upload\Retry Upload Smartprotection - SKU belum sesuai (2026-08-05).xlsx` (118 baris = full block 8 listing, 82 SKU diganti). **Belum diupload.**

**FYI belum ditindak**: 71 baris "no_target" (varid tidak ada di target sama sekali) — mayoritas (30) Hyundai Atoz, SKU-nya blank total di listing DAN tidak ada entri target-nya (genuinely belum pernah di-assign SKU, beda kasus dari revisi Santa Fe/Mazda3, butuh kerja terpisah kalau mau diisi).

## KOREKSI PENTING 2026-08-05: cek SP Shopee kelewat Mazda 3 sama sekali — pola ini WAJIB dicek eksplisit di toko manapun

User tegur via screenshot: Mazda 3 Sedan & Hatchback di SP Shopee SAMA-SAMA masih pakai `MZD-M3-SP-...` (belum kena revisi 3S/3H). **Root cause: target file `SP_Shopee_1/2.xlsx` JUGA masih py `MZD-M3` utk kedua listing itu** (belum pernah direvisi krn target dibuat sebelum revisi hari ini) — jadi diff current-vs-target NGGAK KELUAR sbg mismatch (current==target, sama2 salah). **Pola bug ini SAMA PERSIS dgn yg sudah ditemukan utk Santa Fe di semua toko** (OT, SP Shopee) — tapi kemarin cuma diterapkan eksplisit ke Santa Fe, LUPA diterapkan ke Mazda 3 juga. **How to apply ke depan (WAJIB, bukan opsional): setiap cek toko baru (OP dst), SELALU cek Mazda 3 Sedan/Hatchback DAN Santa Fe secara eksplisit dgn cari pid-nya langsung, JANGAN cuma andalkan diff-vs-target — target bisa saja "salah dgn konsisten" sehingga diff tidak mendeteksi apa-apa.**

**Fix SP Shopee (patch retroactive)**: 61 baris tambahan ditemukan (4 listing: Mazda 3 Sedan/Sedan Transparan/Hatchback/Hatchback Transparan) — digabung ke retry sebelumnya, total sekarang **143 baris / 12 listing** (naik dari 82/8). Target `SP_Shopee_1.xlsx` diupdate lagi (+61). File retry ditimpa ulang.

**Struktur file direorganisasi user**: folder sekarang `Cek gagal upload\{UA,SP,OT,OP}\{Shopee,TikTok,Lazada}\`, output-nya JUGA ditaruh per-toko di folder yg sama (bukan `Cek gagal upload\` root lagi).

## Cek TikTok & Lazada Smartprotection (SP) 2026-08-05

**TikTok SP** (`Cek gagal upload\SP\TikTok\...xlsx`, target `SP_TikTok.xlsx`): diff standar 0 mismatch (SEMUA sama krn target ikut basi juga) — dicek eksplisit Mazda3+SantaFe spt pelajaran di atas, ketemu **38 baris**: 24 Mazda3 (5 Hatchback legacy CVR + 3 Hatchback Transparan + 2 Sedan Transparan legacy + 14 Sedan Reguler yg TOTAL KOSONG dari awal) + 14 Santa Fe (listing utama masih 100% kode legacy `CVR0089-STP-...`, TANPA split generasi sama sekali di listing ini — beda dari "Santa Fe Transparan" yg sudah py kode modern `HYN-SFE-SP-T-G1-TRP` seragam tapi TIDAK dipecah G1/G2 krn cuma 1 kode utk semua rentang tahun, sengaja dibiarkan krn bukan bug baru). Target `SP_TikTok.xlsx` diupdate (24/38 — 14 baris Santa Fe tak py entri target sama sekali, wajar krn baru migrasi dari legacy). File: `Cek gagal upload\SP\Retry Upload Smartprotection TikTok - SKU belum sesuai (2026-08-05).xlsx` (52 baris, 38 diganti).

**Lazada SP** (`Cek gagal upload\SP\Lazada\...xlsx`, target `SP_Lazada.xlsx`): diff standar dapat 167 baris (7 model bug formula lama: Toyota Harrier, BMW Seri 5, Mitsubishi Galant, Mercedes Benz C Class, Timor, Kia Sonet, Suzuki Agya Transparan — target-nya SUDAH py suffix disambiguasi Lazada yg benar, verified 0 duplikat, langsung pakai apa adanya + 28 baris Santa Fe). **Santa Fe di toko ini TERNYATA STRUKTURNYA SIMPEL — cuma 2 baris per warna (satu G3/masuk grup baru G1, satu G4F/masuk grup baru G2), TIDAK ADA tabrakan sama sekali** krn tiap grup cuma py 1 anggota (beda dari kasus UA Lazada yg 6 generasi jadi 1 SKU dgn potensi tabrakan besar) — reklasifikasi G3→G1/G4F→G2 langsung dari segmen SKU aman tanpa suffix tambahan. **Santa Fe Transparan (4 baris terpisah, placeholder Lazada murni)** perlu disambiguasi baru krn 3 dari 4 tahun jatuh ke grup G1 yg sama (dibikin `_G2`/`_G3` ordinal).

**Mazda 3 di Lazada JUGA kena pola sama seperti Shopee/TikTok (target basi + banyak baris placeholder murni)**: 43 baris fill (Hatchback 20 + Sedan 20 + Hatchback Transparan 3 + Sedan Transparan... — lihat detail di script). **Ditemukan pola suffix historis SP Lazada utk Mazda3 SANGAT tidak konsisten**: sebagian pakai suffix nama-warna spt `_MERA`(Merah)/`_BIRU`(Biru Benhur)/`_HITA`(Hitam)/`_HIJA`(Hijau Army), dan slot mana yg "bare" vs "suffixed" antar-warna TIDAK KONSISTEN (kadang tahun lama bare, kadang tahun baru bare) — **jangan coba tebak/samakan pola lama ini, cukup pastikan fill baru UNIK thd yg sudah ada** (dipakai skema ordinal `_G2`/`_G3` sendiri utk baris yg genuinely kosong, tidak menyentuh yg sudah ada). **Verifikasi akhir: 0 duplikat di 253/253 baris final file, semua 13 listing** (dicek ulang penuh dari file output, bukan cuma dari rencana perubahan).

File: `Cek gagal upload\SP\Retry Upload Smartprotection Lazada - SKU belum sesuai (2026-08-05).xlsx` (253 baris, 214 diganti). Target `SP_Lazada.xlsx` diupdate (203/214 — 11 baris genuinely tak py entri target).

**Ringkasan SP semua channel**: Shopee 143 baris/12 listing, TikTok 38/5, Lazada 214/13. **Belum ada yang diupload user.**

## Cek formula Otoprotection (OP) 2026-08-06 — toko ke-4/terakhir dari perluasan awal, 107 baris/2 channel

`Cek gagal upload\OP\{Shopee,TikTok}\` (shop id Shopee 476733837). Target: `OP_Shopee_1/2.xlsx`, `OP_TikTok_1/2.xlsx` — **OP pakai prefix SKU `SP`** (konsisten dgn aturan konsolidasi OP=SP). Metodologi penuh dari pelajaran sebelumnya diterapkan sejak awal: diff standar + cek eksplisit Santa Fe/Mazda3 + verifikasi model formula-lama lain (Corona/Galant/Harrier/dst) via cek langsung segmen generasi (bukan cuma percaya diff).

**OP Shopee: 65 baris/9 listing.** Diff standar cuma nangkep Santa Fe 14 baris (krn target OP jg masih formula lama utk Santa Fe — pola sama spt toko lain). Setelah investigasi manual: **Santa Fe 30 baris** (listing ini cuma py 2 rentang tahun "2018-2023"/"2023-sekarang", KEDUANYA masuk grup G2 baru — G1 TIDAK ADA anggota di listing ini sama sekali, jadi seluruh listing jadi G2 semua, aman krn Shopee ga perlu unique), **Mazda 3: 13 baris** (Hatchback 6 legacy + Sedan 6 legacy + Hatchback Transparan 1 blank total), **3 model formula-lama lain ditemukan via cek manual** (Toyota Harrier 6 baris, Timor 1 baris, **BMW Seri 5 SEMUA 15 baris masih legacy CVR0087-OTP total** — tidak pernah dimigrasi sama sekali).

**OP TikTok: 42 baris/9 listing** (relatif jauh lebih bersih dari channel lain sesi ini — diff standar cuma 4 baris Mercedes Transparan legacy). Setelah cek eksplisit: **Santa Fe 15 baris** (listing ini TIDAK PUNYA info generasi SAMA SEKALI di teks varian — cuma warna polos, beda dari versi Shopee-nya yg py rentang tahun — di-default ke G1 krn tak ada info utk nentuin grup mana, konsisten dgn cara OT TikTok ditangani sebelumnya), **Mazda3 23 baris** (Hatchback: 13 baris SEMUA masih `MZD-M3` blm pernah di-3H-kan + 2 legacy; Sedan: 6 legacy; Transparan Hatchback: 1 masih `MZD-M3`).

**Jebakan teknis baru ditemukan & diperbaiki sesi ini**:
1. **Regex tier-warna sempat salah arah**: nulis `stir?p` (maksudnya toleransi typo "Stirp") tapi pola itu JUSTRU gagal cocok dgn ejaan BENAR "Strip" (krn "st"+opsional-r+"p" tidak match "st"+"r"+"i"+"p") — 12 dari 14 baris Strip-tier OP Shopee Santa Fe nyaris ke-skip diam2 sebelum ketahuan dari angka hasil yg janggal (14 bukan 30). **Fix: pakai `(?:strip|stirp)` eksplisit, bukan optional-letter trick.** How to apply: kalau bikin regex toleransi typo, TES dulu against ejaan BENAR juga, jangan asumsikan optional-char otomatis mencakup kedua kasus.
2. Typo warna baru ditemukan: "Biru Binhur" (bukan cuma "Biru Benhur") di listing Mazda3 Sedan OP TikTok — ditambahkan ke color-map.
3. **Verifikasi model formula-lama TIDAK CUKUP cuma cari kata kunci `-G(\d+)-` via regex bebas** — sempat false-positive nangkep "GAL"(dari kode brand MTB-GAL) sbg "generasi AL". **Fix: split SKU by `-` dan ambil index [4] scr eksplisit** (posisi segmen generasi yg pasti), baru simpulkan bug/tidak.

File retry: `Cek gagal upload\OP\Retry Upload Otoprotection Shopee - SKU belum sesuai (2026-08-06).xlsx` (106 baris, 65 diganti), `Cek gagal upload\OP\Retry Upload Otoprotection TikTok - SKU belum sesuai (2026-08-06).xlsx` (52 baris, 42 diganti). Target `OP_Shopee_1/2.xlsx` & `OP_TikTok_1/2.xlsx` diupdate (backup `.bak_20260806`). **Belum diupload.**

**Perluasan cek 215-terlaris ke 4 toko (UA/OT/SP/OP) kini SELESAI first-pass.** Ringkasan lengkap semua toko (baris blm sesuai / channel dicek): UA (semua channel sudah diupload user & terverifikasi 08-05), OT Shopee 118, SP Shopee 143 + TikTok 81(msh proses cek no_target lanjutan) + Lazada 214, OP Shopee 65 + TikTok 42. **Belum dicek**: Lazada utk OT & OP (perlu tanya user apakah toko ini py channel Lazada).

**Utang dari sesi ini (belum selesai)**: janji ke user utk lanjutkan investigasi mendalam no_target bucket SP Shopee & SP Lazada (nyari pola Corona/Grandis-style spt yg ketemu di SP TikTok) — sempat mulai (breakdown no_target sudah ditarik) tapi terpotong pindah ke OP. Lanjutkan sesi depan kalau user tanya lagi/minta lanjut.

## KOREKSI BESAR 2026-08-06: full-sweep cek 215-terlaris ke SEMUA 4 toko — klaim "SELESAI first-pass" kemarin TERNYATA jauh dari lengkap

User tanya ulang (2x, dgn kata2 beda): "Sudah itu aja yg belum sesuai? SKU nya sudah sesuai dengan list produk 215 produk terlaris?" lalu "Ke empat toko sudah terupdate semua ya sku produk di 215 terlarisnya?" — trigger utk verifikasi menyeluruh, bukan percaya hasil kemarin.

**Metodologi baru (jauh lebih ketat dari sebelumnya)**: bukan lagi diff current-vs-target-file, dan bukan lagi cuma cek model2 tertentu yg "kelihatannya" bermasalah (Santa Fe/Mazda3/segelintir legacy model). Sebagai gantinya: **full positional-format sweep** ke SEMUA baris di SEMUA file sumber (live export toko, bukan file target) — tiap SKU displit by `-`, diklasifikasi BLANK (kosong total) / NOT6PART (belum py format 6-segmen, msh `CVR####` dll) / BADGEN (sudah 6 segmen tapi segmen ke-5/generasi bukan pola `G\d+`, msh kode custom lama spt `5S`,`J40`,`XOV`,`COM`,`3P`,`KTK`,`YJ`) / OK. Lalu tiap baris non-OK di-crossref ke 2 sumber: (a) ranking `MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx` utk filter cuma yg No<=215, (b) `Data Mobil Lebih dari 1 Formula.xlsx` Sheet2 utk pastikan modelnya memang SUDAH py formula resmi (bukan model long-tail yg emang belum pernah masuk proyek).

**Root cause kenapa hasil kemarin jauh meleset**: metode diff-vs-target KEBOBOLAN sistemik kalau target file (`SKU Gudang Big Seller/*.xlsx`) itu SENDIRI juga belum pernah diupdate ke formula baru — current==target (sama2 salah/kosong) jadi diff bilang "OK" padahal keduanya salah. Pola ini sudah ketemu berkali-kali di level PER-MODEL sepanjang sesi (Mazda3 SP Shopee, Corona/Grandis SP TikTok, dll — lihat entry2 di atas) tapi baru sekarang ketahuan ini bukan beberapa kasus terisolasi, melainkan **pola sistemik yg mempengaruhi ribuan baris di SEMUA toko**.

**Angka final per toko** (baris SKU belum sesuai format formula baru, TERBATAS ke 215 model terlaris + model yg sudah py formula resmi — bukan seluruh katalog):

| Toko | Baris blm sesuai | Listing/produk terdampak |
|---|---|---|
| UA | 2.588 | 213 |
| OT | 863 | 120 |
| SP | 2.602 | 112 |
| OP | 1.576 | 128 |
| **TOTAL** | **7.629** | — |

**Jawaban jujur ke pertanyaan user: BELUM, keempat toko BELUM terupdate semua utk 215 produk terlaris.** Yang sudah difix & (sebagian) diupload sepanjang sesi 08-03 s/d 08-06 (UA semua channel, OT Shopee 118, SP Shopee 143+TikTok 81+Lazada 214, OP Shopee 65+TikTok 42) cuma **sebagian kecil** dari total riil 7.629 — karena yg kemarin ditemukan lewat diff-vs-target atau cek manual per-model, sementara mayoritas gap yg baru ketemu ini justru row yg target-nya SENDIRI belum pernah disentuh (banyak yg BLANK total atau msh kode `CVR####` legacy, bukan "kelupaan apply revisi" spt Santa Fe/Mazda3 kemarin).

**Contoh model besar yg baru ketahuan dari full-sweep ini** (blm pernah masuk radar sesi2 sebelumnya krn target filenya jg blank/legacy sejak awal): Toyota Land Cruiser (BADGEN besar2an di 4 toko), Jeep Wrangler Rubicon (BADGEN, ratusan baris terutama OT/OP), Toyota HiAce/Hardtop/Starlet/Suzuki SX4/Jimny/Nissan Livina X-Gear (semua msh py kode custom lama spt `5S`/`J40`/`COM`/`XOV`/`3P` di posisi segmen generasi — bukan `CVR` legacy, tapi format LAMA formula yg belum dikonversi ke `G1/G2`), Hyundai Atoz/Avega/Stargazer/Kia Carens/Rio (banyak BLANK total, kemungkinan variant yg baru dibuatkan listing tapi SKU-nya belum pernah diisi sejak awal).

**Belum dikerjakan (next step)**: baris2 ini baru DIKLASIFIKASI status & di-crossref ke ranking+formula — **SKU tujuan yg benar utk masing2 baris BELUM dihitung**, target file belum diupdate, retry file belum dibuat. Mengingat skalanya (7.629 baris, 573 listing produk, 4 toko × sampai 3 channel), user perlu kasih arahan prioritas dulu sebelum eksekusi masal (per toko? per channel? by rank tertinggi dulu?) — jangan main comot semua sekaligus tanpa checkpoint spt sesi2 sebelumnya (resiko kesalahan besar tanpa terkontrol, apalagi ada kasus BLANK yg mungkin sengaja/variant nonaktif, perlu diverifikasi bukan asumsi semua harus diisi).

**Script/file kunci utk lanjutan** (di scratchpad, path session-specific tapi pola bisa dipakai ulang):
- `formula_ref.py` — loader `Data Mobil Lebih dari 1 Formula.xlsx` Sheet2 jadi dict `norm(nama)->{no,name,tf}`, dipakai sbg filter "model ini sudah resmi py formula belum".
- `full_audit.py` — sweep SEMUA baris SEMUA toko/channel (111.934 baris total) dari file SUMBER LANGSUNG (bukan target), classify format, crossref ranking+formula, simpan `full_audit_all_rows.json`.
- `full_audit_summary.py` — filter `full_audit_all_rows.json` ke status!=OK + rank<=215 + formula_no ada, hasil di `full_audit_violations.json` (7.629 baris) — ini sumber angka tabel di atas.
- Fungsi `extract_model()` di `full_audit.py` — strip prefix ("Undercover Autocare -", "(Body )?Cover Mobil( / Selimut( Mobil)?)?", "Cover Mobil Transparan") + strip trailing kata tier/kategori (Reguler/Premium/Exclusive/Outdoor variants/Sedan/Hatchback/dst) scr iteratif sampai stabil, baru dicocokkan ke ranking/formula by normalized-name. Tervalidasi: bucket "tidak match" isinya cuma non-model (Cover Motor, Travel Pouch, dll) — bukan model asli yg kelewat.

**Catatan penting**: baris "Sisa pekerjaan" versi lama di bawah (9.616 + 14.412 baris) adalah angka SELURUH katalog dari checkpoint lama (sebelum perluasan 215-terlaris) — BEDA scope dari 7.629 di atas (yg khusus 215 terlaris + model berformula resmi). Jangan digabung/dibandingkan langsung, keduanya legitimate tapi berbeda ruang lingkup dan sumber hitung.

## Sisa pekerjaan (angka lama, seluruh katalog — checkpoint sebelum perluasan 215-terlaris)

- 9.616 baris SKU listing perlu dibenahi (7.007 placeholder angka Lazada, sisanya skema lama `CVR####` + 239 baris ber-SKU literal `"SKU"`).
- 14.412 baris listing masih tanpa SKU sama sekali.
- Typo `Warior` (seharusnya `Warrior`) di teks varian listing SP/OP — dinormalkan di judul, tapi **sumbernya di listing belum diperbaiki**.

## 2026-08-07: audit ulang 4 toko — angka 08-06 KURANG HITUNG, ini yang final

User spot-check 2 produk (Vellfire di OP TikTok SKU kosong; Harrier di SP TikTok masih `CVR0083-STP-RPA`), lalu tanya "Ke empat toko sudah terupdate semua ya sku produk di 215 terlarisnya?". Keduanya terkonfirmasi persis seperti dilaporkan user — sekali lagi membuktikan pola di [[user-undercover-profile]]: spot-check user hampir selalu menunjuk bug sistemik.

**Angka FINAL (ganti tabel 08-06 yang 7.629):**

| Toko | Baris blm sesuai | (08-06 lama) |
|---|---|---|
| UA | 3.757 | 2.588 |
| OT | 872 | 863 |
| SP | 2.602 | 2.602 ✔ |
| OP | 1.546 | 1.576 |
| **TOTAL** | **8.777** | 7.629 |

Dari 63.364 baris top-215 di 9 kombinasi toko×channel: **86,1% sudah sesuai, 8.777 belum**. Terdampak 741 listing, 113 model dari 215. Kepatuhan per channel rata: 83–88% (terendah SP/Lazada 83,4%, tertinggi UA/TikTok 88,3%) — jadi **tidak ada satu channel pun yang selesai**.

**Kenapa 08-06 kurang hitung — bug extractor nama produk.** UA punya 2 pola penamaan: `Undercover Autocare - Cover Mobil X Reguler` DAN pola terbalik `Cover Mobil X Reguler - Undercover Autocare`. `extract_model()` versi 08-06 cuma strip prefix, tidak strip sufiks `- Undercover Autocare`, jadi **1.149 baris UA TikTok + 6 UA Shopee gagal dicocokkan ke ranking dan hilang diam-diam** dari hitungan. Bukan false positive baru — ini baris asli yang kelewat. SP cocok persis (2.602) karena penamaannya seragam.

**Pelajaran metodologi pencocokan nama model → ranking (jangan diulang salahnya):**
- **Substring matching SALAH** (dicoba dulu, ditolak): "Range Rover Sport/Velar/Evoque" ikut terhitung sbg "Range Rover" #132, "Ford Ranger T6" ikut "Ford Ranger" — menggelembungkan UA jadi 4.051 palsu. Sub-model beda itu model beda.
- **Exact matching juga SALAH** (terlalu ketat): "Kia Rio Sedan" & "Mazda 3 Sedan" terbuang padahal induknya (#100, #152) top-215.
- **Yang BENAR = dua tahap**: cocokkan nama utuh dulu ke ranking; hanya kalau gagal, lepas sufiks bodystyle (`Sedan/Hatchback/Pickup/Car/Kapsul`) lalu cocokkan lagi. Ini menjaga "Hyundai Avega Sedan" (#135) dan "Hyundai Avega Hatchback" (#140) tetap terpisah — keduanya entri ranking sendiri — sekaligus menangkap "Kia Rio Sedan"→"Kia Rio".
- **Wajib sanity-check**: setelah matching, pastikan bucket "tidak match" tidak mengandung nama yang sebenarnya ADA di top-215 (di run final: 0, bersih). Tanpa cek ini bug 08-06 tidak akan ketahuan.

**Deliverable**: `Cek gagal upload/REKAP SKU 215 Terlaris - 4 Toko (2026-08-07).xlsx` — sheet RINGKASAN (tabel per toko×channel), sheet per toko (UA/OT/SP/OP, tiap baris: rank, model, channel, nama produk, varian, SKU sekarang, jenis masalah, nomor baris, file sumber), sheet PER MODEL (113 model × sebaran 4 toko).

**Script final** (scratchpad): `all_stores_sweep.py` (sweep 111.935 baris semua toko/channel dari file sumber live → `all_stores_sweep.json`), `all_stores_top215_v3.py` (matching 2-tahap + crossref ranking & formula → `top215_bad_v3.json`), `build_report_v3.py` (bangun xlsx rekap). Versi v1/v2 sengaja ditinggal sbg bukti kedua metode matching yang salah.

**Status: masih tahap DIAGNOSIS.** SKU tujuan per baris belum dihitung, target file belum diupdate, retry file belum dibuat. Skala 8.777 baris/741 listing terlalu besar untuk dikerjakan sekaligus tanpa checkpoint — perlu arahan prioritas user dulu (per toko? per channel? rank tertinggi dulu?). Khusus baris **SKU kosong** (2.782 baris) jangan diasumsikan semua harus diisi — perlu dipastikan dulu bukan varian nonaktif/sengaja.

## KOREKSI METODOLOGI 2026-08-07 (kedua kali dalam sehari): cek format regex SALAH, harus lawan MASTER

Angka 8.777 di atas **terlalu tinggi** — klasifikasi `BADGEN` (segmen ke-5 bukan pola `G\d+`) ternyata **false positive besar-besaran**. Master `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` memang **sengaja** memakai kode generasi non-`G#` untuk mobil yang generasinya tidak bernomor: `COM` (HiAce Commuter), `J40`/`J60`/`J100` (Hardtop, Land Cruiser), `3P`/`5P` (Jimny), `5S`/`7S` (Livina X-Gear), `KPS`/`KTK` (Starlet Kapsul/Kotak), `XOV` (SX4 X-Over), `YJ`/`TJ`/`JK`/`JL` (Wrangler). Dari 18.997 baris master UA, **2.077 memang non-`G#` by design**. Jadi ~3.343 baris "BADGEN" lintas 4 toko itu sebagian besar SUDAH BENAR.

**Aturan baru: jangan pernah menilai kepatuhan SKU dari pola regex.** Uji yang benar = **SKU baris ini harus salah satu SKU sah model tsb di master** (`sku_by_model[norm(model)]`). Master = sumber kebenaran, punya kolom Nama Produk/Toko/Kategori/Warna/Generasi/SKU, 69.480 baris, 76 sheet merek, 4 toko (UA 18.997 / OT 18.385 / SP 16.049 / OP 16.049).

**Hasil UA dengan metode master** (file listing terbaru user 2026-08-07, 67.300 baris, 29.591 masuk top-215):

| Status | Baris | Arti |
|---|---|---|
| OK | 25.234 | cocok master |
| NO_MASTER | 1.505 | model belum ada di master sama sekali |
| SENGAJA_KOSONG | 1.023 | varian generik, aturan #4 — benar kosong |
| PLACEHOLDER_ANGKA | 846 | SKU angka auto-Lazada |
| TIDAK_ADA_DI_MASTER | 636 | |
| GENERIK_BER_SKU | 233 | varian generik tapi ada SKU — harusnya kosong |
| KOSONG | 114 | kosong padahal bukan generik |

→ **1.829 baris perlu perhatian** (bukan 3.757). Dari situ **1.099 bisa diperbaiki otomatis** (252 isi-dari-master + 847 dikosongkan sesuai aturan #4), **730 perlu keputusan user**.

**Dua jebakan matching yang ketemu & wajib diingat:**
1. **Sufiks keunikan Lazada** (`_G3`, `_MERA`) harus di-strip sebelum dibandingkan ke master — kalau tidak, 5.183 baris Lazada salah divonis "tidak ada di master".
2. **Urutan lookup master harus dari yang PALING SPESIFIK**: teks model utuh dari judul (`"Mazda 3 Sedan"`) DULU, baru nama ranking (`"Mazda 3"`). Master punya entri terpisah `Mazda 3 Sedan`(MZD-3S), `Mazda 3 Hatchback`(MZD-3H), DAN legacy `Mazda 3`(MZD-M3). Pakai nama ranking duluan → 430 baris Mazda 3 salah divonis.

**JEBAKAN PALING BERBAHAYA — resolver hampir membatalkan revisi user.** Saat generasi baris tidak ada di master, pool kandidat menyusut jadi 1 SKU lalu **diterima diam-diam**. Efeknya hampir: Santa Fe `G2`→`G1` (membatalkan revisi user 05-08!), Xenia `G3`→`G1`, HiAce Premio→Commuter, Hilux Rangga→Hilux biasa, Navara PRO-4X→Navara biasa, dan **4 generasi Jeep Wrangler (JK/JL/TJ/YJ) diruntuhkan jadi YJ semua**. Perbaikan: **generasi WAJIB cocok persis; kalau master tidak punya, JANGAN tebak — masukkan ke daftar keputusan.** Plus daftar `MASTER_TERTINGGAL` (sekarang berisi Hyundai Santa Fe) untuk model yang listing-nya lebih baru dari master.

**Master ternyata juga punya lubang** (bukan cuma listing yang salah): Santa Fe belum dipecah G1/G2; Corolla master mulai dari Gen 6 padahal listing punya Gen 1-5 (185 baris); Mini Cooper **tidak ada sama sekali** di master (88 baris); Xenia Gen 3/Veloz belum jadi formula terpisah; Stargazer Gen 2 (2025-2026) belum ada; HiAce "Premio", Hilux "Rangga", Navara "PRO-4X" belum ada. **Arah perbaikannya ke master, bukan ke listing.**

**Deliverable UA 2026-08-07** (di `Cek gagal upload/UA/`, semua BELUM diupload):
- `Retry Upload Shopee UA - SKU belum sesuai master (2026-08-07).xlsx` — 1.080 baris, 334 SKU diubah
- `Retry Upload TikTok UA - SKU belum sesuai master (2026-08-07).xlsx` — 45 baris, 40 diubah (8 sheet asli utuh)
- `Retry Upload Lazada UA - SKU belum sesuai master (2026-08-07).xlsx` — 2.869 baris, 725 diubah, **0 duplikat Seller SKU terverifikasi**
- `CATATAN UA - perlu keputusan (2026-08-07).xlsx` — 3 sheet: PERLU KEPUTUSAN (ringkas per kelompok + usulan), DETAIL (730 baris), SUDAH DIPERBAIKI (1.099 baris, lama→baru)

**Catatan risiko belum terjawab**: 614 baris Lazada dikosongkan SKU-nya sesuai aturan #4 — belum pernah diuji apakah Lazada menerima Seller SKU kosong. Kalau upload menolak, kembalikan nilai lama untuk baris tsb.

**Script** (scratchpad): `master_index.py` (loader+index master), `ua_check_vs_master.py` (klasifikasi 7 status), `ua_resolve.py` (penyelesai SKU + guard), `ua_build_uploads.py` (3 file upload + cek duplikat Lazada), `ua_build_decisions.py`. Urutan toko berikutnya per instruksi user: UA dulu (ini), lalu user kirim listing OT/SP/OP satu per satu.

### Update 2026-08-07 sore: jawaban user + file final UA (hanya baris berubah)

User menjawab 6 pertanyaan; hasilnya sebagian besar "listing sudah benar, master yang tertinggal":
- **Corolla SUDAH BENAR 100%** — tervalidasi lawan screenshot user: Gen 1&2→G1, 3→G3, 4→G4, 5→G5, 6→G6, 7→G7, 8→G8, Gen 9&10&12→G9, Gen 11→G11 = tepat 9 tipe SKU sesuai TF=9. Master cuma punya 5 dari 9 (kurang G1/G3/G4/G5).
- **Veloz 51 = Xenia Gen 3 (2021-2026)**; semua 148 baris di 4 toko sudah konsisten `G3`. Master Xenia baru punya G1.
- **Stargazer → 2 formula** (keputusan baru user). Gen 2 (2025-2026) belum berkode di SEMUA toko (148 baris). UA-nya sudah difix jadi `HYN-SGZ-UA-{R|S|P|E}-G2-{warna}`.
- **HiAce Premio**: listing sebenarnya SUDAH membedakan lewat kode model — Commuter=`TYT-HAC`, Premio=`TYT-HAL` — tapi keduanya pakai segmen generasi `COM`. 148 baris konsisten di 4 toko. Master cuma punya TYT-HAC. **Menunggu keputusan user**: Premio tetap `COM` atau dapat kode generasi sendiri.
- **Mini Cooper**: 368 baris di 4 toko; `3P`/`5P` sudah dipakai di UA Shopee/OT/SP/OP, yang kosong cuma UA TikTok & UA Lazada. Master belum punya Mini Cooper sama sekali.

**Jebakan baru: Mini Cooper TIDAK boleh di-auto-fix.** Teks variannya punya DUA token (sub-model Clubman/Roadster/Paceman + jumlah pintu), dan parser varian menukarnya — hasil deriviasi ngawur ("Roadster,5 Pintu"→`3P`, "Clubman,3 Pintu"→`5P`). Sudah dikecualikan eksplisit di `ua_resolve2.py`.

**Jebakan peta "sibling"**: sumbernya harus SEMUA baris ber-SKU well-formed (6 segmen, bukan placeholder/CVR), **bukan** cuma yang cocok master — kalau difilter ke status OK saja, model yang listing-nya benar tapi belum masuk master (Corolla Gen 1-5) tidak ikut jadi rujukan dan 72 baris gagal diperbaiki.

**File final UA** (`Cek gagal upload/UA/`, isi HANYA baris yang berubah sesuai permintaan user; versi "Retry Upload …" yang memuat listing utuh sudah dihapus):
- `Upload Shopee UA - hanya baris berubah (2026-08-07).xlsx` — 350 baris
- `Upload TikTok UA - hanya baris berubah (2026-08-07).xlsx` — 65 baris (8 sheet asli utuh)
- `Upload Lazada UA - hanya baris berubah (2026-08-07).xlsx` — 805 baris, 0 duplikat Seller SKU, 614 di antaranya **dikosongkan** (aturan #4)
- `CATATAN UA - perlu keputusan (2026-08-07).xlsx` — 2 sheet: SUDAH DIPERBAIKI (1.220) & PERLU KEPUTUSAN (609)

Total 1.220 baris diperbaiki, 609 menunggu keputusan (mayoritas: Santa Fe 153 & Corolla 113 & Xenia 51 = master yang perlu ditambah, bukan listing salah).

### REVISI ATURAN #4 (user 2026-08-07, sore) — varian generik formula-tunggal DIISI

Instruksi user: *"Yang varian seperti tahun lainnya kalau di formulanya cuma ada 1 tetap di isi kode skunya aja, kalau formulanya lebih dari 1 baru di kosongkan saja."* Aturan #4 di [[project-undercover-sku-sync-rules]] sudah diperbarui.

Logikanya: kalau model cuma punya 1 formula, varian "Model/Tahun Lain" tidak ambigu — pasti SKU itu. Baru kalau >1 formula, tidak boleh ditebak generasinya.

**Cara hitung jumlah formula** (dipakai di `ua_generic_rule.py`): `max(` jumlah kode generasi berbeda di MASTER utk model+toko, jumlah kode generasi berbeda di LISTING pada SKU well-formed `)`. Pakai max karena master & listing sama-sama bisa tertinggal — Corolla contohnya: master 5 kode, listing 9 kode, yang benar 9.

**Dampak ke UA**: dari 2.495 baris varian generik → **1.810 DIISI** (formula tunggal), **17 dikosongkan** (formula >1, semuanya Honda Civic Hatchback yang punya 6 formula), 608 sudah benar, 26 gagal dipastikan. Ini membalik pekerjaan sebelumnya: versi sebelum revisi mengosongkan 847 baris, sekarang justru mayoritas diisi.

**Total perbaikan UA jadi 2.200 baris** (dari 1.220): Shopee 751, TikTok 645, Lazada 804. Rincian sumber: 1.810 aturan #4 revisi, 252 dari master, 73 dari baris sejenis, 48 aturan Stargazer, 17 dikosongkan.

**Catatan Lazada**: 684 baris generik dapat sufiks keunikan `_G2` otomatis karena SKU-nya bentrok dengan baris "Gen 1" di listing yang sama (mis. `HND-CTR-UA-S-G1-EAB` → `HND-CTR-UA-S-G1-EAB_G2`). Sesuai konvensi historis Lazada. Terverifikasi 0 duplikat. Baris dikosongkan turun drastis dari 614 → 17, jadi risiko "Lazada tolak SKU kosong" yang dicatat sebelumnya hampir hilang.

**File final** (`Cek gagal upload/UA/`): `Upload {Shopee|TikTok|Lazada} UA - hanya baris berubah (2026-08-07).xlsx` + `CATATAN UA - perlu keputusan (2026-08-07) rev2.xlsx` (nama "rev2" karena file versi pertama sedang dibuka user di Excel → PermissionError saat ditimpa; kalau ketemu 2 file catatan, **yang rev2 yang benar**). Sisa 635 baris perlu keputusan.

## 2026-08-08: file impor SKU Gudang Big Seller — SKU yang ada di listing tapi belum di gudang

User instruksi: cek folder `SKU Gudang Big Seller/` (file baru dimasukkan), bandingkan SKU listing e-commerce vs SKU yang sudah ada di Big Seller, buatkan file impor untuk yang belum ada. Dua contoh diberikan sebagai petunjuk: Mazda 2 Hatchback (`-2H-`) dan varian warna Orange di SP/OP — **keduanya terkonfirmasi masuk hasil**.

**Sumber data**: 8 file `SKU_Gudang20260808012521258(1-8).xlsx` sheet `SKU` (35.158 SKU gudang sudah ada, kolom `Nomor SKU`/`Judul`) + `impor_untuk_membuat_sku_gudang_in.xlsx` sheet `SKU` (template impor, 40 kolom, kolom 1-2 = `*Nomor SKU (Wajib Diisi)` / `*Judul (Wajib)`, baris 2 di file asli cuma contoh isian bukan data).

**Metodologi diff**: kumpulkan SKU well-formed (6 segmen) dari SEMUA listing e-commerce yang sudah disweep sesi ini (`all_stores_sweep.json` utk OT/SP/OP + `ua_0807_all.json` dioverride dgn `ua_fix_v3.json` utk UA — pakai kondisi SETELAH perbaikan yg blm diupload, bukan kondisi lama), konsolidasi segmen toko (OT→UA, OP→SP sesuai aturan #1), lalu selisihkan terhadap set SKU gudang yang sudah ada.

**Hasil**: 1.043 SKU baru perlu dibuat (UA 708, SP 335), tersebar di 39 kode model. Semua tervalidasi ADA landasannya (848 langsung cocok SKU di master, 195 kombinasi gen/warna baru tapi modelnya dikenal master — termasuk 17 `MZD-2H` yang diduga user, dan varian Orange yang juga diduga user). **0 SKU yang benar-benar tanpa dasar** — sempat dicurigai ada yg mencurigakan (kode gen `GB19912002`, `F2`, `B5` dst) tapi setelah dicek ke master ternyata memang format sah yg sudah dipakai (`GB` = "Gen Baru" utk mobil yg rentang tahunnya digabung tanpa nomor gen; `F`/`B` = kode facelift/body BMW-Volkswagen).

**Cara menyusun Judul** (kolom 2, wajib), prioritas 3 tingkat:
1. **Saudara** — cari SKU lain di gudang dgn prefix sama (model-toko-kategori-generasi) beda cuma di kode warna, salin judulnya & ganti nama warnanya. Paling akurat karena otomatis ikut gaya judul yg sudah dipakai utk SKU tetangga (gudang TERNYATA punya >1 gaya judul campur aduk utk model yg sama, mis. Lancer ada yg `Abu-abu,2007-2022` ada yg `Reguler-Abu-abu-Gen 10` — bukan galat, memang historisnya begitu).
2. **Master** — `Model-Toko-Kategori-Warna-Gen` (aturan #5), pilih baris master yg segmen generasinya paling cocok dgn SKU (exact match dulu, fallback ke generasi terendah kalau tak ketemu).
3. **Susun manual** dari segmen SKU + nama produk listing (dipakai kalau 1&2 gagal, mis. model sama sekali baru di gudang spt `MZD-2H`).

**Jebakan yg sempat kejadian**: percobaan pertama pilih baris master SEMBARANG tanpa cocokkan generasi ke segmen SKU — `MTB-LAN-SP-R-G1-ORG` (segmen gen = G1) sempat dapat judul "...Gen 10" karena kebetulan baris master pertama yg ke-scan adalah Gen 10 bukan Gen 1 (di master, banyak baris SKU sama tapi field Generasi beda krn representasi longgar). Baru ketahuan pas eyeball manual. Diperbaiki dgn cocokkan `re.sub(non-alnum)` pada representasi generasi vs segmen SKU sebelum pilih baris master.

**Validasi otomatis sebelum simpan**: semua judul terisi (tidak kosong), tidak ada SKU duplikat dalam file baru, tidak ada SKU yang sudah ada di gudang. Ketiganya lolos di run final.

**Deliverable**: `SKU Gudang Big Seller/impor_sku_gudang_BARU (2026-08-08).xlsx` — sheet `SKU`, 40 kolom (format identik template asli, cuma kolom 1&2 terisi, sisanya kosong spt template — user yg isi Stok/Modal/dll manual sesuai kebutuhan). **Belum diimpor ke Big Seller.**

**Script kunci** (scratchpad): `gudang_diff.py` (kumpulkan SKU listing terkonsolidasi vs gudang → `gudang_missing.json`), `build_gudang_import_v2.py` (3-tingkat penyusun Judul + validasi → file final). v1 (`build_gudang_import.py`) ditinggal sbg bukti prioritas judul yg lebih kasar (cuma master+susun, tanpa saudara — 100% kasusnya kebetulan cocok tapi kurang tahan utk kasus generasi-ganda spt Lancer).

**Catatan utk sesi depan**: 1.043 ini HANYA yg ketahuan dari listing yg sudah disweep sesi ini (UA + hasil sweep OT/SP/OP tgl 08-05/06 — bisa jadi sudah agak basi kalau ada perubahan listing baru). Kalau user kasih listing terbaru toko lain, ulangi diff ini dgn data segar.

## 2026-08-08 (lanjutan): 2 temuan user membongkar masalah lebih dalam dari sekadar file impor

User tanya 2 hal spesifik dari file impor v2: (1) kenapa Hyundai Elantra SKU-nya aneh, (2) Santa Fe kok ada G3/G4, harusnya cuma sampai G2. Investigasi lanjutan:

**Temuan A — Santa Fe Orange TERBUKTI kelewat di revisi 08-05 (bug ke-3 dgn pola sama).** Cross-check ke `sp_final.json`/`sp_tiktok_final.json`/`sp_lazada_final.json` (fix Santa Fe yg sudah dihitung 08-05): **tidak ada satupun baris Orange di dalamnya** — 31, 14, 32 baris masing2 file, semua warna KECUALI Orange. Sama persis pola bug Corona/Grandis SP TikTok yg ditemukan sebelumnya (warna/varian tertentu lolos dari cakupan fix). Bahkan retry file yg SUDAH DIKIRIM ke user (`Retry Upload Smartprotection - SKU belum sesuai (2026-08-05).xlsx`) terbukti masih membawa Orange dgn SKU lama G3/G4 — **fix yg sudah didelivery pun cacat**.

**Root cause lebih dalam**: dicek ke gudang Big Seller, ternyata **SELURUH sisi G2 (skema baru) utk SP Santa Fe belum pernah dibuat SKU gudangnya** — bukan cuma Orange. G1 lengkap 16/16 kombinasi kategori+warna (sesuai master), tapi G2 cuma 1/16 (kebetulan T-G2-TRP). Artinya baru Transparan yg sempat masuk gudang; Reguler+Strip G2 (15 SKU) belum pernah dibuat sama sekali. UA sebaliknya SUDAH lengkap G1 maupun G2 (17/17 masing2) — konsisten dgn UA yg sudah lebih dulu selesai disinkron penuh sesi ini.

**Perbaikan**: (a) file impor gudang — buang 2 SKU lama HYN-SFE-SP-R-G3/G4-ORG (salah, jangan dibuat), tambah 15 SKU G2 yg benar (Reguler×6 + Strip×9, judul diturunkan dari sibling G1 dgn ganti teks "Gen 1"->"Gen 2"); (b) file retry-upload BARU utk listing SP (bukan cuma gudang) — `Cek gagal upload/SP/Upload {Shopee|Lazada|TikTok} SP - Santa Fe Orange belum sesuai (2026-08-08).xlsx`: Shopee 2 baris (G3→G1, G4→G2), Lazada 2 baris (G3→G1, G4F→G2), TikTok 19 baris/2 toko produk lengkap (Orange kosong→G1, DAN temuan tambahan: varian Transparan "2018-2023" masih pakai T-G1-TRP padahal harusnya T-G2-TRP — kedua T-G1-TRP dan T-G2-TRP SUDAH ada di gudang jadi ini murni bug listing, bukan gap gudang).

**Pelajaran baru**: kalau fix sebuah model "sudah selesai" tercatat di memory, JANGAN percaya penuh — cross-check ke gudang Big Seller utk verifikasi SEMUA kombinasi kategori+warna+generasi resmi (dari master) benar2 lengkap ada, bukan cuma percaya file retry yg pernah dibuat. Cara verifikasi: generate SEMUA kombinasi valid dari master (bukan cuma yg kebetulan muncul di data listing/diff), lalu cek satu-satu ke gudang.

**Temuan B — 12 model punya 2 skema generasi tumpang tindih di master, TIDAK diketahui mana yg berlaku.** Model² spt Hyundai Elantra, Hyundai Sonata, Kia Sedona, Jeep Cherokee, Lexus LX/NX/RX, Mercedes CLS/GLA, Mitsubishi Delica, Chevrolet Trooper, Peugeot 3008 — master-nya punya G1,G2,G3...Gn (skema lama, 1 kode per generasi) **BERBARENGAN** dgn GB{tahunmulai}{tahunselesai} (skema baru gaya konsolidasi, mirip revisi Santa Fe G1/G2 tp pakai label rentang-tahun bukan nomor-grup).

**Elantra dicek paling detail (live listing SP, 321 baris)**: hasilnya kacau — rentang tahun yg SAMA di teks varian memetakan ke kode generasi yg BEDA-BEDA antar baris (mis. teks "1995-2000" muncul dgn kode G1, G5F, G7, GB20152020, DAN GB20202024 di baris² berbeda). Ini bukan 2 skema yg konsisten & bisa dipilih salah satu — datanya sendiri sudah tercampur-aduk, tidak bisa dipercaya sbg sumber utk menentukan SKU gudang yg benar.

**Keputusan**: 115 baris (12 model ini) DIKELUARKAN dari file impor gudang, didaftar terpisah di `SKU Gudang Big Seller/CATATAN - 12 model perlu keputusan skema generasi (2026-08-08).xlsx` (kolom: kode model, jumlah baris, daftar gen skema lama, daftar gen skema baru). **Belum ada keputusan user** — jangan dibuatkan SKU gudang utk 12 model ini sampai jelas skema mana yg berlaku (atau perlu investigasi/pembersihan data terpisah spt Elantra).

**File final gudang** (v3, replace v2): `SKU Gudang Big Seller/impor_sku_gudang_BARU (2026-08-08).xlsx` — 941 baris (dari 1.043: -115 model bermasalah, -2 Santa Fe salah, +15 Santa Fe G2 benar).

**Script tambahan** (scratchpad): `build_gudang_import_v3.py` (koreksi final: exclude 12 model + fix Santa Fe lengkap), `sp_shopee_santafe_fix2.py` (retry Shopee dibangun dari file asli, versi pertama sempat salah pakai `openpyxl.Workbook()` kosong lagi — kesalahan yg SAMA persis dgn insiden UA 08-07, harus selalu diingat: bangun dari file asli, JANGAN workbook baru).

## 2026-08-10: Hyundai Atoz SP & OP — SKU sama sekali belum pernah dibuat

User kirim screenshot listing Atoz SP dgn semua "Kode Variasi: -" (kosong total), minta dibuatkan SKU utk SP+OP sekaligus impor gudangnya. Ini model yg dari awal sesi memang sudah tercatat sbg "no_target bucket, semua blank, gap belum terselesaikan" (lihat entri²  lama) — sekarang baru benar² dikerjakan.

**Master**: `HYN-ATZ`, TF=1 (Gen1=Gen1F, satu formula), SP/OP kategori Reguler(6 warna)+Strip(9: S1/S2/S3×Abu/Biru/Merah)+Transparan(1) = 16 kombinasi.

**Jebakan warna Strip yg ketemu lagi**: listing OP Shopee menulis varian Strip LANGSUNG sbg teks "Strip 1 Abu"/"Strip 2 Biru"/"Strip 3 Merah" (bukan "Elite/Epic/Warrior" spt kebanyakan listing lain). Parser awal cuma kenal pola Elite/Epic/Warrior → 18 dari 32 baris OP Shopee gagal ke-parse di percobaan pertama. **Kedua gaya penulisan itu valid dan setara** — "Elite Abu"=S2A, "Strip 2 Abu"=S2A, sama² merujuk kode S2A; regex tambahan `strip\s*(\d)\s+(warna)` menangkap gaya kedua. Setelah fix: 32/32 lengkap di semua 5 kombinasi toko×channel.

**Hasil**: 160 baris diperbaiki (SP Shopee 32, SP TikTok 32, SP Lazada 32, OP Shopee 32, OP TikTok 32 — genap semua krn produk ini memang cuma 32 varian per toko, semuanya kosong dari awal). 16 SKU unik dihasilkan, **semua 16 belum ada di gudang Big Seller** (wajar, produk ini belum pernah disentuh) → file impor terpisah `impor_sku_gudang_Hyundai_Atoz (2026-08-10).xlsx`.

**File**: `Cek gagal upload/{SP,OP}/Upload {Shopee|TikTok|Lazada} {SP|OP} - Hyundai Atoz (2026-08-10).xlsx` (5 file, semua dibangun dari file sumber asli — verifikasi sheet/header/kolom identik ke file asli, 0 xml rusak) + `SKU Gudang Big Seller/impor_sku_gudang_Hyundai_Atoz (2026-08-10).xlsx` (16 baris, format 40 kolom sama persis template).

**Script**: `atoz_sp_op.py` di scratchpad — pola reusable utk model lain yg blank total (TF=1, tinggal pasang REGULER dict + toko + source paths, otomatis handle Shopee/TikTok(produk-lengkap)/Lazada(dedup-suffix) sekaligus multi-toko dgn kode SKU dikonsolidasi terpisah dari nama folder).

## 2026-08-13: Mitsubishi Lancer Reguler (OT/SP/OP) + rescan pola serupa

User temukan Lancer Reguler (Abu/Hitam/Biru/Merah/Hijau/Orange) di Otoprotection masih CVR-lama, sedangkan Strip sudah `MTB-LAN-SP-S-G1-...`. Terkonfirmasi persis, dan ternyata di SEMUA toko (OT/SP/OP) -- Lancer memang belum pernah difix sesi manapun sebelumnya (cuma tercatat di audit, tak pernah dieksekusi). UA sendiri sudah 100% OK (204/204).

**Hasil per toko/channel** (60 baris fix, master bersih TF=1 semua G1):
OT Shopee 18, SP Shopee 3 + TikTok 9 + Lazada 16, OP Shopee 7 + TikTok 7. File: `Cek gagal upload/{OT|SP|OP}/Upload {Shopee|TikTok|Lazada} {toko} - Mitsubishi Lancer (2026-08-13).xlsx`.

**Bug script sempat kejadian lagi**: OP Shopee py 2 file sumber (1.xlsx+2.xlsx), loop awal simpan tiap file ke NAMA OUTPUT SAMA -> file kedua timpa file pertama, 6 baris dari file1 hilang. Fix: gabung semua source jadi 1 output (basis file pertama, ambil baris dr file manapun yg berubah) -- pola yg SAMA persis dgn yg sudah dicatat utk Shopee multi-file sebelumnya, jangan lupa lagi.

**Rescan menyeluruh** (data source 08-05/06, msh valid krn OT/SP/OP tak ada upload baru sejak itu): pola PERSIS Lancer -- model top-215 dgn sebagian kategori/warna sudah G1-formula, sebagian msh CVR-lama/blank/placeholder -- ternyata **BUKAN kasus terisolasi, melainkan 58 model, 2.553 baris** (di luar Lancer/Santa Fe/Atoz yg sudah ditangani). Terbesar: Toyota Corolla(214), Suzuki Carry(84), Mini Cooper(106), BMW Seri5(63), BMW X1(57), Mitsubishi Galant(57), Chevrolet Orlando(94), BMW X5(99), Isuzu Mux(96), Mazda 3(115, msh py Mazda3-Hatchback-code lama jg meski sdh direvisi UA -- brarti OT/SP/OP blm ikut revisi -3S-/-3H- baik). Rincian lengkap per model di file REKAP.

**Deliverable**: `Cek gagal upload/REKAP SKU OT-SP-OP - lanjutan Lancer (2026-08-13).xlsx` -- sheet RINGKASAN (58 model x breakdown BLANK/CVR-lama/placeholder x toko-channel terdampak), sheet DETAIL (2.553 baris lengkap varian+SKU+masalah).

**Status: BARU DIAGNOSIS, belum dieksekusi** (skala terlalu besar utk sekali jalan tanpa arahan prioritas user, sama spt keputusan di audit 08-07 sebelumnya). Lancer sendiri (bagian dr temuan user kali ini) SUDAH selesai dieksekusi+file siap upload.

**Script kunci**: `master_index.py` (rebuild ringan, versi lama kehapus dari scratchpad), `lancer_fix.py` (pola reusable per-model spesifik, cocok dipakai ulang model lain), `ot_sp_op_rescan.py` (rescan comprehensive pola-Lancer, filter exclude yg sudah ditangani sesi ini via set HANDLED).

**Catatan teknis**: file besar (`all_stores_sweep.json` 111.935 baris, `top215_bad_v3.json` dll) di scratchpad OS-managed, bisa kehapus antar sesi/waktu (terjadi kali ini) -- kalau perlu data itu lagi, cek dulu ada/tidak sebelum asumsikan, siap rebuild dari file sumber Cek gagal upload/ kalau hilang (masih valid selama tanggal source belum berubah).

## 2026-08-13 lanjutan: eksekusi massal SP+OP, 49 model rescan

User pilih prioritas: SP+OP dulu (dari REKAP 58-model tadi, subset SP+OP = 49 model, 2.023 baris).

**Resolver generic** (bukan hardcode per-model spt Lancer): parse warna dari vname (plain / Elite-Epic-Warrior 2-kata / "Strip N Warna") -> (tier,huruf) atau kode plain, kategori dari pname, validasi ke pool master Smartprotection per model. Kunci lookup model DUA tahap: nama spesifik dari pname dulu (mis. "Mazda 3 Sedan"), baru fallback ke nama generic ranking ("Mazda 3") -- URUTAN INI WAJIB.

**Bug nyaris kejadian (ke-4 kalinya pola serupa)**: percobaan pertama pakai nama generic ranking langsung sbg kunci lookup -> Mazda 3 Sedan DAN Hatchback (100 baris) ke-resolve ke kode LEGACY `MZD-M3` krn master py entri bare "Mazda 3" (legacy) YG MASIH ADA berdampingan dgn "Mazda 3 Sedan"/"Mazda 3 Hatchback" (benar) -- generic-name match ketemu yg legacy duluan. Ini KELAS BUG SAMA dgn Santa Fe 08-08 (pool salah pilih krn tak spesifik). Fix: coba nama spesifik dari pname dulu (`specific_model_text()`, strip prefix/kategori-suffix), baru fallback. Setelah fix: Mazda3 turun dari 100 resolved (SALAH) jadi 53 resolved (BENAR, kode 3S/3H) + 50 unresolved (jujur, drpd salah diam2).

**Hasil**: 1.523 dari 2.023 baris terselesaikan otomatis (SP 1001, OP 522). Sisa 500 baris didominasi kasus keras yg butuh gen-matching manual (Toyota Corolla 200 -- multi-formula persis kaya kasus UA, Mini Cooper 92, Suzuki Carry 67, Hyundai Avega Hatchback 54 -- model blm ada di master SP sama sekali).

**File**: `Cek gagal upload/{SP|OP}/Upload {Shopee|TikTok|Lazada} {toko} - Rescan 49 Model (2026-08-13).xlsx` (5 file, OP tak py Lazada). `CATATAN SP-OP - 500 baris belum terselesaikan (2026-08-13).xlsx`.

**Belum**: OT (530 baris dari REKAP awal, toko ke-3 blm digarap -- user prioritas SP+OP dulu), rescan 500 sisa butuh kerja manual per-model spt Lancer.

**Script**: `sp_op_mass_fix.py` (resolver generic reusable), `sp_op_build_uploads.py` (builder pakai src+vid matching persis, bukan pname+vname yg rawan tabrakan).

## 2026-08-14: Evalia/Audi Q5/Mazda CX9 (dr order Big Seller gagal link SKU gudang), UA+SP

User temukan 3 produk dr layar order Big Seller ("Kesalahan: Pesanan blm dihubungkan dgn SKU Gudang"): Nissan Evalia, Audi Q5, Mazda CX9. Evalia+CX9 sudah py master (TF=1 efektif keduanya, walau CX9 py 2 baris "Gen" beda tp collapse ke SKU G1 sama). **Audi Q5 sama sekali tak ada di master** -- brand baru, cuma py preseden Audi A4/A8 (kode AUD-A4/AUD-A8) sbg acuan pola. Konstruksi manual: G1(2009-2012)/G1F(2012-2017)/G2(2018-2024) dibedakan (ikut pola A4 yg jg pisah G5/G5F), UA-only (Q5 blm ada listing di SP).

**Hasil**: 239 baris fix (UA Shopee 48+TikTok 65+Lazada 99, SP Shopee 13+Lazada 14; SP TikTok 0 -- ternyata sudah 100% benar duluan). 15 baris residual tak terselesaikan: 9 baris Q5 "Gen X" tanpa warna sama sekali (data yatim), 6 baris CX9 SP (2 "3 kandidat" msh misteri kecil + 4 Transparan krn master SP CX9 memang tak py kategori Transparan).

**2 bug ditemukan+diperbaiki saat resolver dibangun** (kelas sama dgn bug2 sebelumnya, dicatat biar next time langsung kena):
1. Perbandingan `tuple_slice == list_literal` SELALU False (`('ABU',) != ['ABU']`) -- semua kombinasi plain-color gagal match walau datanya identik. Fix: jangan slice-compare, cek elemen langsung (`pc[1]==code`).
2. Filter kandidat lupa exclude kategori lain (Reguler-lookup ikut kebawa Premium+Exclusive krn sama2 py warna Abu-abu) -- "3 kandidat" padahal 1 SKU x 3 kategori. Fix: filter eksplisit `r['kategori']==cat_target` sebelum cek warna.

**Format gudang import DIREVISI** (user kirim contoh `impor_untuk_membuat_sku_gudang_in (2).xlsx`, instruksi "buat model seperti ini"): kolom Gudang="Default Warehouse" dan Stok=5 (bukan dikosongkan spt sebelumnya), Judul pakai gaya **"{Toko} - Cover Mobil {Model} {Kategori} {Warna}"** (bukan gaya hyphen "Model-Toko-Kategori-Warna-Gen" yg dipakai sblmnya) -- setidaknya utk UA. **Ini kemungkinan preferensi BARU/default kedepan utk toko UA, catat & pakai lagi kalau ada gudang-import UA berikutnya**, tp verifikasi ulang ke user kalau ragu krn cuma 1 contoh.

**File**: `Cek gagal upload/{UA|SP}/Upload {Shopee|TikTok|Lazada} {toko} - Evalia-AudiQ5-MazdaCX9 (2026-08-14).xlsx` (5 file byk 0-row diskip otomatis), `SKU Gudang Big Seller/impor_sku_gudang_Audi_Q5 (2026-08-14).xlsx` (48 baris, cuma Q5 yg genuinely baru; Evalia+CX9 SKU-nya semua udah ada di gudang).

**Script**: `three_models_sweep.py`+`three_models_fix.py`+`three_models_build.py` (scratchpad) -- pola generic serupa `sp_op_mass_fix.py` tp ditambah cabang "konstruksi baru tanpa master" utk model yg belum exist sama sekali (Q5).

## 2026-08-20: CX9 Lazada gagal (34/34 duplicate) — akar masalah churn suffix, bukan _G salah

08-14 CX9 Lazada upload GAGAL 100% (34/34 baris) error "Duplicate input sku ID". Evalia+Q5 di file sama SUKSES (65/65) walau sama2 pakai suffix `_G2` — jadi bukan suffix-nya yg salah.

**Akar masalah**: source-nya SUDAH py suffix historis (`MZD-CX9-UA-R-G1-MRH_G1` utk baris Gen1, bare utk Gen2 -- master collapse Gen1&Gen2 jadi 1 SKU sama). Resolver lama SELALU hitung ulang suffix dari nol (bare dulu, baru _G2,_G3...) tanpa peduli baris itu SUDAH py suffix valid yg beda -- akibatnya baris yg `_G1`(sudah unik, gak perlu diapa2in) ikut di-**rename** jadi `_G2`. Rename yg gak perlu ini yg kena tolak Lazada (bukan soal isi akhirnya duplikat, tp soal RENAME PAKSA ke slot yg sblmnya py histori beda).

**Aturan baru, WAJIB dipakai tiap Lazada dedup-suffix ke depan**: sebelum assign suffix, cek dulu `base_of(current_sku)` (strip trailing `_G\d+`) — kalau SUDAH SAMA dgn base target, **JANGAN SENTUH baris itu sama sekali**, walau nomor suffix-nya "gak sesuai urutan logis". Suffix baru cuma utk baris yg basis SEKARANG genuinely beda dr target (CVR-lama/placeholder/blank), dan nomor suffix-nya dihitung dari SEMUA sibling (yg disentuh maupun yg dibiarkan), bukan direset ulang dr `_G2`.

Hasil setelah fix: dari 34 baris "berubah" versi lama, cuma **17 yg genuinely perlu diubah** (17 sisanya dibiarkan apa adanya). File baru: `Cek gagal upload/UA/Upload Lazada UA - Mazda CX9 perbaikan (2026-08-20).xlsx`. **Belum diverifikasi berhasil** (baru dibangun, blm ada laporan upload).

**Script**: `cx9_lazada_refix.py` (scratchpad) -- pola `base_of()` + "jangan sentuh yg udah cocok basis" ini generalizable, pakai lagi kalau nemu kasus serupa (produk formula-collapse yg py histori suffix campur aduk).

## 2026-08-20: Wuling Darion gudang import, SP

User laporan dr Otoprotection TikTok: Wuling Darion blm py SKU Gudang. Master ADA (TF=1, 16 kombinasi: Reguler 6 warna + Strip 9 + Transparan 1, kode `WLG-DRN`), semua 16 **belum ada di gudang** (produk baru). File: `SKU Gudang Big Seller/impor_sku_gudang_Wuling_Darion (2026-08-20).xlsx`, format terbaru (Gudang="Default Warehouse", Stok=5, Judul gaya "Smartprotection - Cover Mobil Wuling Darion {Kategori} {Warna}").

Catatan: cuma gudang import yg diminta, blm dicek/dibenerin SKU listingnya sendiri (beda dr kasus Evalia/Q5/CX9 yg sekalian fix listing) -- kalau listing OP/SP Darion ternyata jg blm pakai kode ini, itu tugas terpisah blm dikerjakan.

## 2026-08-21: Mitsubishi Colt T120SS Pick Up gudang import, UA

User laporan dr screenshot order gagal ("Undercover Autocare - Cover Mobil Mitsubishi Colt T120SS Pick Up Reguler"). Model sama sekali tak ada di master (dicek scan prefix SKU semua sheet Mitsubishi -- "Colt" absen total) -- brand baru murni, tak py listing existing utk direferensi. Konstruksi manual ikut template Mitsubishi L300 Pickup (pickup klasik sejenis, TF=1, cuma Reguler 5 warna + Strip 9, tanpa Premium/Exclusive/Transparan). Kode `MTB-CT1` (bukan singkatan literal T120SS, ikut pola L300->`LP` yg jg singkat bukan literal).

**Bug kecil ditemukan+fix**: draft awal judul baris Strip salah tulis "...Pick Up Reguler {tier}" (harusnya "Strip {tier}") -- kebawa copy-paste dr baris Reguler, ketahuan dr review manual sebelum save final.

File: `SKU Gudang Big Seller/impor_sku_gudang_Colt_T120SS (2026-08-21).xlsx`, 14 baris (Reguler 5 + Strip 9), format terbaru (Gudang="Default Warehouse", Stok=5, Judul "Undercover Autocare - Cover Mobil Mitsubishi Colt T120SS Pick Up {Kategori} {Warna}").

Catatan: cuma gudang import yg dibangun (sesuai permintaan) -- kode SKU listing (Shopee/TikTok/Lazada UA) blm dibuatkan krn produk ini kemungkinan baru mau di-listing, blm ada baris existing utk diperbaiki.

## 2026-08-22: Suzuki Carry vs Carry Pickup dipisah, kode baru SZK-CRP, SEMUA toko+channel

User laporan screenshot: listing "Suzuki Carry Pick Up" dan "Suzuki Carry Reguler" share SKU sama persis (`SZK-CAR-UA-R-G1-ABU`) padahal ukuran fisik beda -- minta kode dibedakan + upload file semua toko/channel + gudang import.

Sweep "carry" (exclude "futura") semua toko/channel: 776 baris total. Master cuma py `Suzuki Carry`(SZK-CAR, UA-only, 102 baris, Gen6-Gen11 semua collapse->segmen G1, kategori Exclusive 1 warna/Premium 2/Reguler 5/Strip 9, tanpa Transparan walau listing live py Transparan) dan `Suzuki New Carry Pick-Up`(SZK-NCR, ada di 4 toko tp cuma 1 generasi "Baru") -- **SZK-NCR dicek BUKAN produk yg sama** dgn listing "Carry Pick Up" (yg rentang Gen6-11 spt Carry sendiri, bukan model modern 1-gen), jadi diputuskan kode BARU `SZK-CRP` (bukan reuse SZK-NCR). Struktur kategori/warna ikut sama persis pola SZK-CAR, gen tetap G1 semua toko.

Deteksi pickup vs reguler dari substring "pick up"/"pickup"/"pick-up" pd nama produk.

**2 bug ditemukan+diperbaiki saat resolver dibangun**:
1. Kategori "outdoor" OT (Extreme Outdoor=Exclusive/Outdoor bare=Premium/Semi Outdoor=Reguler) -- substring-match urutan salah, bare 'outdoor' ke-match duluan sblm sempat cek 'semi outdoor'/'extreme outdoor'. Fix: taruh pola lebih spesifik duluan di list pencocokan.
2. **Kode tier Strip UA/OT ketuker pakai dict warna 1-huruf milik SP/OP** (harusnya UA/OT py dict 2-huruf sendiri: EAB/PAB/WAB, bukan EA/PA/WA) -- akibatnya semua baris Strip UA/OT keluar kode rusak/kependekan. Ketahuan dr spot-check hasil terlihat kode kayak "...-S-G1-PA" bukan "...-S-G1-PAB". **Pola resiko berulang, cek [[project-undercover-sku-sync-rules]] section Carry** tiap bikin resolver baru yg nyentuh Strip UA/OT.

Hasil: 592 resolved, 6 unresolved (OT "Carry/Carry Pickup Outdoor" Gen7/8/10 tanpa label warna eksplisit di teks varian -- Premium py 2 pilihan warna [Abu/Silver] jadi genuinely ambigu, **belum dilaporkan ke user, perlu konfirmasi manual**). Per kode: SZK-CRP 461 baris, SZK-CAR 131 baris.

File: 9 file upload -- `Cek gagal upload/{toko}/Upload {channel} {toko} - Suzuki Carry Split (2026-08-22).xlsx` (UA Shopee/TikTok/Lazada, OT Shopee, SP Shopee/TikTok/Lazada, OP Shopee/TikTok -- OT tak py TikTok/Lazada, OP Lazada tak diminta/tak ada source). Gudang: `SKU Gudang Big Seller/impor_sku_gudang_Suzuki_Carry_Split (2026-08-22).xlsx`, 35 kode baru yg blm ada di gudang (2x SZK-CAR-SP [Reguler-Orange + Transparan] + 16x SZK-CRP-SP + 17x SZK-CRP-UA -- SZK-CRP-OT/OP tak dibuatkan, ikut aturan#3 konsolidasi gudang UA+SP saja). Semua 10 file terverifikasi format (struktur sheet cocok source asli) sebelum dikirim.

**Script**: `carry_split_sweep.py`+`carry_split_fix.py`+`carry_build.py` (scratchpad) -- pola sama dgn `three_models_*.py`.

## 2026-08-22: Hyundai Verna gudang import, UA -- model baru, kode HYN-VRN, template dari Accent

User laporan screenshot order gagal ("Cover Mobil Hyundai Verna Reguler - Undercover Autocare", TikTok, SKU gudang blank). Verna **tak ada sama sekali** di master (dicek: 0 baris), juga tak ketemu di listing UA Shopee/TikTok manapun yg py di lokal (kemungkinan listing baru, dibuat setelah export 08-05/06/07 yg jadi acuan sesi ini). Tak py preseden twin-model eksplisit dr user (beda dr kasus Xenia=Avanza dkk yg dikonfirmasi tertulis) -- **jangan asumsikan Verna=Accent sbg identitas SKU yg sama**, cuma dipakai STRUKTURnya (Reguler 5 warna+Strip 9+Premium 2+Exclusive 1, semua G1) sbg template krn sedan Hyundai paling sebanding, sama pola dgn Colt T120SS pakai L300 sbg template tanpa klaim itu sbg produk sama.

Kode baru `HYN-VRN` (cek 0 collision di master & gudang existing). Scope UA doang (order asalnya dr situ, blm ada bukti Verna dijual toko lain). 17 baris dibangun preemptif full 4 kategori (bukan cuma Reguler yg gagal) - ikuti pola Colt T120SS (build kategori penuh sesuai template, bukan cuma yg lagi bermasalah), tp **BELUM dikonfirmasi user apakah scope kategori/generasi ini akurat** (ketidakpastian lebih besar dr Colt/Darion krn di sana msh ada minimal 1 bukti data riil [gambar produk/listing existing], di sini betul2 nol data selain 1 screenshot).

File: `SKU Gudang Big Seller/impor_sku_gudang_Hyundai_Verna (2026-08-22).xlsx`, 17 baris. Kalau user lapor kategori/warna lain yg dibutuhkan, atau ternyata scope generasi harus beda, sesuaikan tanpa perlu bangun ulang dari nol -- tinggal tambah baris yg kurang.

## 2026-09-01: pola baru ditemukan -- model LENGKAP di master tp NOL persen ada di gudang (Toyota GR86, Honda Civic Hatchback)

User laporan 2 screenshot terpisah (order gagal krn "belum dihubungkan SKU Gudang"): Toyota GR 86 (`TYT-G86-SP-T-G1-TRP`) dan Honda Civic Hatchback (`HND-CVH-SP-T-G10-TRP`). **Beda dgn Verna/Colt/Darion** (model gak ada di master sama sekali) -- 2 model ini **SUDAH lengkap terdefinisi penuh di master** (G86: 66 kode unik, Gen1-2, UA+SP; Civic Hatchback: 198 kode unik, Gen6-11, UA+SP), SKU yg dikirim user di order PERSIS cocok pola master, tp pas dicek ke SEMUA 8 file `SKU_Gudang20260808012521258(*).xlsx`, **0% dari kode2 itu pernah ada di gudang** (bukan cuma yg 1 baris di order, TAPI SELURUH keluarga kode model itu). Kesimpulan: model2 ini pernah di-setup SKU listing-nya (makanya sudah py kode rapi sesuai master) tp gudang Big Seller-nya emang belum PERNAH diimpor sama sekali -- gap total, bukan gap sebagian.

**Pelajaran utk kasus serupa ke depan**: kalau user laporan order gagal dgn SKU yg KELIHATAN sudah rapi/sesuai pola (bukan kode CVR-lama/kosong), JANGAN asumsikan cuma 1 baris itu yg bolong -- selalu cek dulu ke master utk dapetin SELURUH keluarga kode model itu (`load_master` + filter model), baru cross-check SEMUA-nya ke gudang existing. Kemungkinan besar SELURUH model itu emang belum pernah diimpor, bukan cuma varian yg ketauan dr order ini. File dibangun full sesuai temuan: `impor_sku_gudang_Toyota_GR86 (2026-09-01).xlsx` (66 baris) + `impor_sku_gudang_Honda_Civic_Hatchback (2026-09-01).xlsx` (198 baris).

## 2026-09-01: Peugeot 306 -- master HANYA py baris UA, tak py SP/Transparan/Orange sama sekali (gap struktural, beda dr gap gudang biasa)

Order gagal ke-3 di screenshot yg sama: Peugeot 306, 2 order (Otonation "Semi Outdoor, Orange, Fase 2" & Smartprotection "Transparan, Fase 2"), SKU masih kode CVR lama (`CVR0181-OTP-RPO` / `CVR0181-STP-RTP`), blm dimigrasi ke skema baru sama sekali. Master dicek: Peugeot 306 CUMA py 51 baris, **SEMUA toko='Undercover Autocare' doang** -- gak spt 100% model lain di master yg selalu py baris Otonation/Smartprotection/Otoprotection paralel (rule konsolidasi #1). Juga **gak py kategori Transparan** dan **gak py warna Orange** di Reguler-nya sama sekali (cuma 5 warna standar), padahal order nyata SP eksplisit minta Transparan dan order OT eksplisit minta Orange.

**Keputusan**: TIDAK proaktif bangun struktur SP penuh (Transparan+Reguler 6 warna+Strip 9 × 3 Fase = 48 baris spekulatif ngikut pola model lain) krn ini perubahan struktural ke model yg SUDAH ada di master (beda dr Colt/Darion/Verna yg 100% kosong, jadi bebas pakai template). Cuma dibangun **2 kode yg persis dibutuhkan 2 order nyata ini**: `PEU-M306-UA-R-F2-ORG` (catatan: pakai segmen generasi `F2` bukan `G2` -- model ini pakai istilah "Fase" bukan "Gen" di SKU-nya sendiri, ikuti persis) dan `PEU-M306-SP-T-F2-TRP`. User sudah diberitahu 2 hal: (1) master py gap struktural (mungkin perlu di-lengkapi manual oleh user/tim, bukan cuma soal gudang), (2) **warna "Orange" pada order Otonation itu ANOMALI** -- di SEMUA model lain sepanjang sesi ini, Orange SELALU eksklusif sisi Smartprotection/Otoprotection, sisi Undercover/Otonation gak pernah py pilihan Orange. Belum dikonfirmasi apakah ini pola baru yg disengaja utk Peugeot 306 atau salah pilih warna waktu order -- **jangan generalisasi "Orange kadang muncul di UA/OT" ke model lain** sebelum ada konfirmasi eksplisit, ini masih dicatat sbg anomali 1 kasus.

File: `SKU Gudang Big Seller/impor_sku_gudang_Peugeot_306 (2026-09-01).xlsx`, 2 baris. **Belum dikerjakan**: fix SKU listing Peugeot 306 sendiri (masih CVR-lama) -- baru gudang doang yg diminta/dikerjakan.

## 2026-09-01: Jaecoo J5 gudang import, UA+SP -- pola "0% gudang" ke-3 kalinya (sama spt GR86/Civic Hatchback)

2 order gagal (Reguler Hitam Gen1 + "Elite Merah" Gen1 -- warna tier walau judul produk bilang "Reguler", tetap diarahkan ke kategori Strip krn ngikut warna bukan judul, konsisten dgn logika `parse_color` yg dipakai sepanjang sesi). Master py Jaecoo J5 lengkap 34 kode unik (UA 17 + SP 17, TF=1) -- **cek pola SP J5 SEDIKIT beda dr kebanyakan model lain**: Reguler SP cuma 5 warna standar (TANPA Orange) dan TANPA kategori Transparan -- rupanya bukan semua model py Orange/Transparan di sisi SP, jangan asumsikan otomatis ada. Dicek ke gudang: 34/34 (100%) belum pernah diimpor -- pola sama persis dgn GR86 & Civic Hatchback (lihat catatan 2026-09-01 sebelumnya), makin menguatkan: kalau order gagal py SKU RAPI (bukan CVR-lama), cek dulu SELURUH keluarga kode model itu ke gudang sblm asumsi cuma 1 baris yg bolong.

File: `SKU Gudang Big Seller/impor_sku_gudang_Jaecoo_J5 (2026-09-01).xlsx`, 34 baris (bukan cuma 2 yg gagal).
