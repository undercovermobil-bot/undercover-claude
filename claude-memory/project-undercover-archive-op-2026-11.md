---
name: project-undercover-archive-op-2026-11
description: "Archive produk Otoprotection (Shopee + TikTok) 11 Nov 2026 ke 100 SKU terlaris: hasil verifikasi vs ranking, Smartpro dan Undercover; SKU MG S5 EV dibuat; kasus SKU kosong"
type: project
tags: [archive, otoprotection, top-100, sku-sync, mg-s5-ev]
updated: 2026-11-12
---

# Archive produk Otoprotection (11 Nov 2026)

Tujuan user: merampingkan listing Otoprotection (OP) ke **100 SKU terlaris**, seperti yang sudah dilakukan di Smartpro (SP) dan Undercover (UA). Cara: nama produk diubah jadi `"<nama lama> (Archive)"` lewat mass update, lalu produknya dihapus lewat UI marketplace.

## Definisi "100 SKU terlaris"
- **100 grup kode SKU**, bukan 100 nama mobil: satu kode bisa mewakili beberapa nama (mis. `TYT-AVZ` = Avanza/Xenia/Veloz). Sumber: `G:\My Drive\E-commerce\RANKING TOP 100 PER SKU.xlsx` (1 Apr–16 Sep 2026, 4 toko gabungan). Peringkat 1–100 dipertahankan; 101–104 (Outlander, GR 86, Mirage, X1) di luar.
- Sheet "Daftar Mobil Listing UA" di file itu memetakan nama mobil → kode → status: **110 nama mobil "Dipertahankan"** (109 tanpa Land Cruiser — inilah kemungkinan asal angka "109 model" di `RINGKASAN`; bukan salah catat).
- Turunannya: `sistem-stok-gsheet/uji/daftar-urutan.js` (daftar stok; STP = 99 kode, tidak memuat Land Cruiser). Lihat [[project-undercover-sistem-stok-gsheet]].
- Peringkat 98 di ranking bernama `SZK-VITARA`; di listing memakai `SZK-GVT/EVT/GVH` (Grand Vitara) — produk yang sama. Hilux = `TYT-HLR/HLX` dan HiAce = `TYT-HAC/HAL` memang satu listing "Dipertahankan" di rencana.

## File (di `C:\Users\OWNER\Downloads\OP Archive 2026-11-11`)
Shopee `mass_update_basic_info_476733837_ARCHIVE.xlsx`, TikTok `..._all_information_template_1_ARCHIVE.xlsx` dan `_2_ARCHIVE.xlsx`, plus `RINGKASAN Archive Otoprotection.xlsx` (dibuat sesi lain). File asli (tanpa `_ARCHIVE`) di Downloads.

## Hasil verifikasi (2026-11-11)
| Cek | Hasil |
|---|---|
| Shopee | 483 listing: **219 dipertahankan, 264 di-archive** |
| TikTok | 486 produk (8.059 varian): 218 dipertahankan, **268 di-archive** (267 + 1) |
| Produk top-100 ikut di-archive | **0** |
| Produk dipertahankan tapi bukan top-100 | **0** |
| Isi file archive | **Hanya kolom nama** yang berubah, format `nama lama + " (Archive)"`; sel lain identik; nama terpanjang 66 karakter |

## Dibandingkan dengan Smartpro dan Undercover (export live di Downloads, 10–11 Nov)
- **SP**: 219 produk Shopee dan 218 produk TikTok — sama dengan jumlah yang dipertahankan OP; set modelnya sama.
- **Land Cruiser** dan **MG S5 EV** ada di SP dan UA (dipertahankan) → OP yang mempertahankannya konsisten.
- Model "kembar" di luar top-100 **tidak ada** di SP maupun UA; hanya versi utamanya: Avega **Sedan** (bukan Hatchback), Feroza (bukan Long), Mazda 2 **Hatchback** (bukan Sedan), Aerio **Hatchback** (bukan Sedan); **Mazda 3 dan BMW M3 tidak ada**. OP meng-archive yang sama.
- Dua kekhawatiran awal ternyata tidak berlaku: Land Cruiser tidak di daftar stok STP tetapi dipertahankan SP; listing Hilux/HiAce/Grand Vitara yang bercampur kode memang bagian rencana.

## SKU MG S5 EV (peringkat 88)
- Kondisi awal: kedua produk TikTok OP (Transparan 1 varian, Reguler+Strip 15 varian) **tanpa SKU penjual**; SP TikTok sama. Shopee: 2 produk (`49467882039` Transparan, `56417848002` Reguler/Strip), parent SKU kosong. Sheet **MG di master SKU kosong** (hanya header) — SKU MG belum ada di master.
- SKU dibuat dengan kode SP (OP = SP), pola dipetik dari 236 varian yang sudah ada (cocok 100%): model `MG-SE`, generasi `G1`.
  - Reguler `MG-SE-SP-R-G1-` + ABU/HTM/BRU/MRH/GRN(Hijau)/ORG; Strip `MG-SE-SP-S-G1-` + S1A/S1B/S1M, S2A/S2B/S2M, S3A/S3B/S3M; Transparan `MG-SE-SP-T-G1-TRP`.
- **File siap upload TikTok** (hanya 16 baris berubah, kolom `seller_sku` saja): `C:\Users\OWNER\Downloads\OP MG S5 EV SKU 2026-11-11\Tiktoksellercenter_batchedit_20261111_all_information_template_1_MG-S5-EV-SKU.xlsx`.
- **Belum**: SKU varian Shopee (butuh export "mass update sales info" untuk dua ID di atas), dan baris MG S5 EV di master SKU.

## Peringkat model yang dipertanyakan (batas 100)
Dipertahankan: Corolla #30, Taft GT = kode Feroza #33, Mini Cooper #65, Land Cruiser #51, MG S5 EV #88. Tidak masuk (benar tidak ada di SP/UA/OP): Mazda 3 Hatchback #131, Mazda 3 Sedan #209, BMW M3 #121.

## Kasus serupa (produk top-100 dengan SKU kosong atau salah)
- **OP**: SKU kosong hanya MG S5 EV (SKU format lain seperti `J40`, `3P/5P`, `KTK/KPS` adalah kode sub-model yang sah).
- **SP TikTok** (SKU kosong, **sudah dibuatkan file 11 Nov**): MG S5 EV (16 varian), Corolla Gen 1–4 (60), Mini Cooper Transparan (10), Taft GT (16) = **102 baris**. MG, Mini Cooper, dan Taft GT identik dengan SKU OP yang sudah ada; Corolla mengikuti aturan formula (Gen 1–2 satu formula → Gen 2 = `G1`, sama dengan SKU Transparan SP; OP Reguler Corolla Gen 2 masih `G2`, tidak sesuai formula). Harga tidak berubah sejak 10 Nov (konfirmasi user), jadi file boleh diupload apa adanya. Skrip: `Undercover-Repo\scripts\isi_sku_kosong_tiktok_sp.py` (jalankan ulang pada export baru). File: `C:\Users\OWNER\Downloads\SP SKU kosong 2026-11-11\...SP-SKU.xlsx` — dibuat dari export 10 Nov dan **membawa kolom harga**, jadi sebaiknya dibuat ulang dari export TikTok SP terbaru sebelum diupload.
- **Toyota Land Cruiser — satu SKU untuk semua generasi itu BENAR** (koreksi 2026-11-11). Total Formula Land Cruiser = 1 (`Data Mobil Lebih dari 1 Formula.xlsx`, Sheet2), jadi J60/J80/J100/J200/J300 memang satu formula dan berbagi SKU (OP TikTok `1729910227107415374` 75 varian → 15 SKU; transparan `1736328456451622222` 5 varian → 1 SKU; SP sama). Yang belum sesuai hanya **kodenya**: listing memakai `J60` (format lama, kategori BADGEN di audit 6 Agu), aturan Total Formula = 1 memberi `G1` → `TYT-LCR-SP-{R|S|T}-G1-…`. Master SKU masih berisi G1–G5 untuk Land Cruiser (tidak selaras dengan file formula). Konversi J60→G1 belum dilakukan dan harus mengikuti urutan di [[project-undercover-bigseller-sync]]: pastikan SKU gudang `G1` sudah ada di BigSeller sebelum listing diupload.
- Pola "beberapa label generasi memakai satu kode" (±130 produk OP, mayoritas `G1`) adalah aturan Total Formula (N formula = N kode), bukan kesalahan.

## Status file upload (2026-11-12)
Export Shopee OP "Info Penjualan" (`Downloads\1.xlsx` 6.077 baris + `2.xlsx` 1.686 baris, 483 produk — identik dengan 483 produk basic-info) diterima 12 Nov 09:24. Nama produk hari ini **sama dengan kemarin dan belum ada "(Archive)"**: archive belum diupload.
- Verifikasi ulang di level SKU varian Shopee: 0 produk top-100 ikut di-archive, 0 produk dipertahankan di luar top-100.
- SKU kosong di produk yang dipertahankan: **MG S5 EV (16 varian)** dan **Hyundai Santa Fe Transparan** (produk tanpa variasi `24550732727`; SKU Induk masih legacy `CVR0089-OTP-RTP`, kolom SKU kosong). Diisi: MG `MG-SE-SP-…-G1-…` (sama dengan TikTok OP), Santa Fe `HYN-SFE-SP-T-G1-TRP` (sama dengan TikTok OP). Skrip: `Undercover-Repo\scripts\isi_sku_kosong_shopee_op.py`.
- File siap upload (hanya kolom SKU yang berubah, id variasi utuh): `Downloads\OP Shopee SKU 2026-11-12\1_SKU-MG-S5-EV.xlsx` (16 baris) dan `2_SKU-Santa-Fe-Transparan.xlsx` (1 baris). File membawa kolom harga dan stok dari export 12 Nov 09:24 — upload hari itu juga.
- Urutan upload TikTok OP: file `_ARCHIVE` dulu, baru file SKU MG S5 EV (file archive membawa SKU MG kosong).

## Belum ada / belum dicek
- Shopee Smartpro: SKU kosong (MG S5 EV, Corolla Gen 1–4, Mini Cooper Transparan, Taft GT) kemungkinan sama seperti di TikTok — butuh export "Info Penjualan" Shopee SP; Undercover belum dicek.
- SKU gudang BigSeller untuk kode baru (`MG-SE-SP-…`, Corolla `G1`–`G4`, Mini/Taft untuk SP) belum dicek — perlu export SKU Gudang.
- Baris MG S5 EV di master SKU; konversi Land Cruiser `J60`→`G1`; kode Taft GT `F70` dan Corolla OP Reguler Gen 2 `G2`.
## Hasil upload Shopee OP (2026-11-12 10:43)
Upload `..._ARCHIVE.xlsx` (483 baris): **174 dari 264 produk berhasil di-rename**; 182 baris gagal = 90 produk yang di-archive + 92 produk yang tidak berubah, semuanya "Deskripsi produk mengandung karakter yang tidak valid [➤]" (181) atau `[✔]` (1). Produk yang tidak berubah gagal tanpa dampak.
- **Perbaikan:** `Downloads\OP Shopee Archive Retry 2026-11-12\mass_update_basic_info_476733837_ARCHIVE_RETRY.xlsx` — 90 produk, baris berurutan 7–96, karakter `➤`/`✔` dibuang dari deskripsi (nama dan SKU induk identik dengan file archive; diverifikasi). Setelah diupload: minta export basic info terbaru lalu jalankan `verify_archive_top100.py`; target 264 produk "(Archive)".
- Temuan terkait: file SKU hasil buatan saya (TikTok MG/SP, Shopee MG/Santa Fe) berisi nomor baris asli (baris bolong → marketplace memproses 0 baris); semuanya sudah direnumerasi dan diverifikasi (isi tidak berubah), dan skrip pengisi SKU kini merapatkan baris otomatis.
## Status 12 Nov sore (hasil upload ulang Shopee + TikTok)
**Shopee OP: archive SELESAI.** Export basic info 12 Nov 14:33 (`mass_update_basic_info_476733837_20261112143359.xlsx`, dicocokkan per id produk dengan export 11 Nov): 483 produk, **264 "(Archive)" = 264 rencana**, 219 utuh (nama tidak berubah), 90 deskripsi berbeda hanya karena `➤`/`✔` dibuang (file ulang). Verifikasi ulang rencana vs ranking: [A]=0, [B]=0. Produk "(Archive)" Shopee OP siap dihapus user lewat UI.

**TikTok OP: semua upload gagal (3 file result).** File archive `template_1` (485 produk, 8.058 baris) gagal 8.058/8.058; `template_2` (Golf) 1/1; file SKU MG S5 EV 16/16 (result diunduh dua kali, identik). Penyebab: **atribut wajib TikTok kosong** — Imported goods (ID 102254; 3.092 baris), Tahun (100530; 4.961 baris), Model (100177; 5 baris Mercedes Transparan yang nyasar ke kategori Radiator). Kasus sama dengan foto Smartpro 10 Nov ([[project-undercover-foto-smartprotection-marketplace]]); saya tidak membaca catatan itu sebelum membuat file TikTok.
- Perbaikan: skrip `scripts/tiktok_isi_atribut_wajib.py` di skill [[skill-undercover-ecommerce-ops]] (hanya mengisi sel kosong; sel lain identik; terverifikasi). File archive TikTok kini hanya berisi produk "(Archive)" (267 produk, 3.908 baris; Golf 1 baris). File SKU MG S5 EV (16 baris) dan SKU Smartpro (102 baris) diisi Imported goods = **Tidak** (produksi lokal; **dikonfirmasi user 2026-11-12**, sama dengan keputusan 10 Nov).
- Semua file yang masih perlu diupload dikumpulkan di **`C:\Users\OWNER\Documents\Undercover Siap Upload\`** (6 file bernomor dengan nama marketplace + toko, plus `0 BACA DULU - urutan upload.txt`).
- Belum diketahui apakah file Shopee SKU (MG S5 EV, Santa Fe) sudah diupload; export Info Penjualan terbaru diperlukan untuk memastikan.

## Langkah berikutnya
- [x] Shopee OP archive: 264/264 selesai (12 Nov 14:33). [ ] Hapus produk "(Archive)" Shopee OP lewat UI (manual user).
- [ ] Upload TikTok OP: file 1 dan 2 (archive, All Information), lalu hapus produk "(Archive)" lewat UI; file 3 (SKU MG S5 EV). Kirim file Result; kemungkinan ada atribut lain yang kurang (satu pesan per baris).
- [x] Export "Info Penjualan" Shopee OP diterima 12 Nov → file SKU MG S5 EV + Santa Fe Transparan dibuat; tinggal diupload (file 4 dan 5 di folder Siap Upload; upload hari export).
- [ ] Upload file SKU Smartpro TikTok (file 6; atribut Imported goods kini terisi; harga tidak berubah sejak 10 Nov, tidak perlu unduh ulang kecuali ada perubahan lain).
- [ ] Konversi kode Land Cruiser `J60` → `G1` (OP dan SP) — hanya setelah SKU gudang G1 ada di BigSeller; bagian dari audit kode format lama (J40, F70, COM, XOV, 3P, KTK) di [[project-undercover-bigseller-sync]].
- [ ] Taft GT memakai `F70`, padahal Total Formula = 1 dan ranking menyebut satu SKU dengan Feroza (`G1`); file SKU Smartpro meniru kode OP yang sudah ada (`F70`) — putuskan bersama konversi kode lama.
- [ ] Tambahkan MG S5 EV ke master SKU (sheet MG masih kosong).

Terkait: [[project-undercover-otoprotection-status]], [[project-undercover-sku-sync-rules]], [[daftar-sumber]].
