---
name: project-undercover-bigseller-sync
description: "Sub-proyek sync SKU listing (skema formula baru) ke SKU Gudang Big Seller — mulai 2026-07-28, keputusan user + jebakan teknis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9235e50b-3311-43ed-a15e-4665c26b7c5e
  modified: 2026-07-29T09:53:04.786Z
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

## Sisa pekerjaan

- 9.616 baris SKU listing perlu dibenahi (7.007 placeholder angka Lazada, sisanya skema lama `CVR####` + 239 baris ber-SKU literal `"SKU"`).
- 14.412 baris listing masih tanpa SKU sama sekali.
- Typo `Warior` (seharusnya `Warrior`) di teks varian listing SP/OP — dinormalkan di judul, tapi **sumbernya di listing belum diperbaiki**.
