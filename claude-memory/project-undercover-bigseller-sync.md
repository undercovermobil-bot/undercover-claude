---
name: project-undercover-bigseller-sync
description: "Sub-proyek sync SKU listing (skema formula baru) ke SKU Gudang Big Seller — mulai 2026-07-28, keputusan user + jebakan teknis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9235e50b-3311-43ed-a15e-4665c26b7c5e
  modified: 2026-08-05T02:56:38.614Z
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

## Sisa pekerjaan

- 9.616 baris SKU listing perlu dibenahi (7.007 placeholder angka Lazada, sisanya skema lama `CVR####` + 239 baris ber-SKU literal `"SKU"`).
- 14.412 baris listing masih tanpa SKU sama sekali.
- Typo `Warior` (seharusnya `Warrior`) di teks varian listing SP/OP — dinormalkan di judul, tapi **sumbernya di listing belum diperbaiki**.
