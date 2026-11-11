---
name: project-undercover-archive-op-2026-11
description: "Archive produk Otoprotection (Shopee + TikTok) 11 Nov 2026 ke 100 SKU terlaris: hasil verifikasi vs ranking, Smartpro dan Undercover; SKU MG S5 EV dibuat; kasus SKU kosong"
type: project
tags: [archive, otoprotection, top-100, sku-sync, mg-s5-ev]
updated: 2026-11-11
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
- **SP TikTok** (SKU kosong, **sudah dibuatkan file 11 Nov**): MG S5 EV (16 varian), Corolla Gen 1–4 (60), Mini Cooper Transparan (10), Taft GT (16) = **102 baris**. Tiap kelompok dicocokkan dengan SKU OP yang sudah ada: identik. Skrip: `Undercover-Repo\scripts\isi_sku_kosong_tiktok_sp.py` (jalankan ulang pada export baru). File: `C:\Users\OWNER\Downloads\SP SKU kosong 2026-11-11\...SP-SKU.xlsx` — dibuat dari export 10 Nov dan **membawa kolom harga**, jadi sebaiknya dibuat ulang dari export TikTok SP terbaru sebelum diupload.
- **SKU salah (bukan kosong): Toyota Land Cruiser** — OP TikTok `1729910227107415374` (75 varian) dan transparan `1736328456451622222` (5), serta produk SP yang sama: **semua generasi (J60, J80, J100, J200, J300) memakai `TYT-LCR-SP-R-J60-<warna>`** (hanya 15 SKU unik dari 75 varian; transparan 1 dari 5). Master punya kode benar `TYT-LCR-SP-{R|S|T}-G1…G5` (J60=G1, J80=G2, J100=G3, J200=G4, J300=G5). Akibatnya stok kelima generasi tercampur. Belum diperbaiki.
- Pola "beberapa label generasi memakai satu kode" muncul di ±130 produk OP (mayoritas `G1`), tetapi di sebagian besar master memang hanya satu generasi — belum dicek satu per satu; hanya Land Cruiser yang terbukti berbeda dari master.

## Langkah berikutnya
- [ ] Upload file `_ARCHIVE` (Shopee & TikTok), lalu hapus produk "(Archive)" lewat UI.
- [ ] Upload file SKU MG S5 EV ke TikTok OP.
- [ ] **Pengingat:** user mengunduh export "Info Penjualan" Shopee OP (variasi produk `49467882039` dan `56417848002`) → isi SKU varian MG S5 EV Shopee. Ingatkan user.
- [ ] Unduh ulang export TikTok SP terbaru → jalankan skrip SKU SP → upload.
- [ ] Perbaiki SKU Land Cruiser (OP dan SP) memakai kode master G1–G5.
- [ ] Tambahkan MG S5 EV ke master SKU (sheet MG masih kosong).

Terkait: [[project-undercover-otoprotection-status]], [[project-undercover-sku-sync-rules]], [[daftar-sumber]].
