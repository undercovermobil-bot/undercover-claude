---
type: project
tags: [undercover, smartprotection, foto, shopee, lazada, tiktok]
updated: 2026-11-10
description: "Penggantian foto produk Smartprotection Signature (set 1–30 dan 31–60) di Shopee, Lazada, TikTok: lokasi file, susunan kolom per platform, pemetaan warna, status, TODO"
---

# Foto Smartprotection → Shopee, Lazada, TikTok

Mengganti foto produk **Smartprotection Signature** ke desain baru lewat file mass update tiap platform. Pelajaran teknis yang bisa dipakai ulang ada di [[feedback-undercover-foto-marketplace-lessons]]. Audit foto sampul lama (Juli–Agustus 2026): [[project-undercover-photo-shopee-audit]].

## Status (2026-11-05)
| Set | Isi | Status |
|---|---|---|
| 1–30 (`Smartpro\SMARTPRO NEW`) | 30 model: 10 awal (Agya, Ayla, Avanza, HRV, Terios, Brio, Innova, Xenia, Jazz, Veloz) + 20 (Yaris, Civic Sedan, Kijang, Vellfire, APV Arena, CRV, Vios, Alphard, Grand Livina, Ertiga, Rush, BRV, Camry, Fortuner, Calya, Sigra, Raize, Triton, XL7, Rocky) | **Selesai** di ketiga platform, diverifikasi isi gambarnya 2026-11-04 (Shopee 20/20, Lazada foto produk 20/20 setelah retry Triton/CRV/XL7, Lazada varian 840 SKU, TikTok 20/20). |
| 31–60 (`Smartpro\Smartpro 31-60`) | 30 model: Accord, Baleno, BMW Seri 3, BYD Atto 1, City Sedan, Corolla, Feroza, Freed, Fronx, Gran Max, Gran Max Pickup, Hardtop, Hilux, HiAce, Ignis, Jimny, Land Cruiser, Luxio, March, Mazda 2, Mobilio, Pajero Sport, Panther, Picanto, Sirion, Swift, Taft GT, WRV, Xpander, X-Trail | File siap 2026-11-04. **TikTok**: sampul HOME ibb `i.ibb.co` ditolak untuk 30/30 produk (2026-11-04) → file v2 pakai `i.ibb.co.com` dibuat 2026-11-05, menunggu unggah. Lazada varian (5 Nov): 25/30 produk berhasil; 5 gagal (Corolla, Swift, City Sedan, Jimny, Taft GT) karena Lazada gagal mengunduh 1–2 gambar per produk dari `i.ibb.co` (kode 530) → file ulang `..._ULANG-5produk_ibbcom.xlsx` (315 SKU, host `i.ibb.co.com`) dibuat 2026-11-05, menunggu unggah. Shopee & Lazada foto produk: belum ada laporan hasil. |

Belum ada foto: ±50 produk Signature lain, semua produk **Transparan**, dan **Xpander Cross** (katalog punya, foto belum).

## Lokasi (semua di `C:\Users\OWNER\Documents\Undercover`)
- Foto sumber 1–30: `Smartpro\SMARTPRO NEW` (480 file). Link: Google Doc "URL Foto Produk Smartpro" (Postimg).
- Foto sumber 31–60: `Smartpro\Smartpro 31-60` (480 file) + daftar link ibb `image url 31-60.txt`. Versi lama yang diganti ada di `Smartpro\_arsip_sebelum_revisi`. `SMARTPRO NEW 31-60.zip` basi (sebelum revisi nama).
- File siap unggah: `Foto Produk\{Shopee,Lazada,TikTok}\` (set 1–30) dan `...\31-60\` (set 31–60). Shopee 31–60 ada file penuh + 5 batch (6 produk). TikTok 31–60: `..._ISI_31-60.xlsx` (gagal) dan `..._v2-ibbcom.xlsx`.
- Dasar file 31–60: ekspor marketplace 2026-11-04 (Shopee `mass_update_media_info_...114105`, Lazada `basic...1104-11-43-53` dan `skuimg...1104-11-45-20`, TikTok `..._20261104_media_information_template`).

## Isi foto per model
16 file per model: 6 Signature (`SIGNATURE X`, `-1`…`-5`), 3 Epic, 3 Elite, 3 Warrior (`SERI X`, `-1`, `-2`) + `SMARTPRO SIGNATURE X HOME.jpg` (sampul). Semua 1083×1083.
- Signature: polos=Abu-abu, `-1`=Hitam, `-2`=Merah, `-3`=Hijau Army, `-4`=Orange, `-5`=Biru Benhur.
- Epic/Elite/Warrior: polos=Abu, `-1`=Biru Benhur, `-2`=Merah (nama variasi di marketplace: "Epic Abu", "Epic Biru", "Epic Merah", dst).
- Foto kembar (isi byte sama) sengaja dipakai antar model mirip (mis. Alphard=Vellfire, Rocky=BRV, Accord=Corolla untuk Epic/Elite/Warrior); hosting menggabungkannya jadi satu link.

## Susunan kolom per platform
| Platform | Sampul | Foto bersama | Foto varian |
|---|---|---|---|
| Shopee (mass update media) | kolom E = HOME | F–M = 8 foto bersama | 15 pasang nama/foto kolom Q…AT (foto = kolom nama +1) |
| Lazada foto produk (`basic`) | F = HOME | G–M = 7 foto bersama (tanpa foto tetesan air, maks 8 slot) | — |
| Lazada varian (`skuimg`) | — | — | kolom H (Gambar1) tiap SKU = foto warna; kunci = bagian pertama kolom "Variations Combo" ("Warrior Merah,Gen 1…"); sama untuk semua generasi |
| TikTok (media template) | D = HOME | E–L = 8 foto bersama (urutan sama Shopee, termasuk tetesan air) | tidak ada varian |
8 foto bersama: Varian Warna, Varian Strip, produk, tetesan air, cara pakai, mobil di jalan, Review Customer, Ketentuan Garansi. URL-nya diambil dari baris produk yang sudah selesai (Agya) di ekspor terbaru tiap platform.

## Catatan data
- Nama variasi di marketplace kadang typo: "Warior", "Elita", "Hijau" (Land Cruiser Shopee, bukan "Hijau Army"). Cocokkan dengan normalisasi, jangan ubah nama variasinya.
- SKU induk Veloz Shopee masih `CVR0163-STP=R` (perubahan lewat upload media diabaikan Shopee; perbaiki di halaman produk). SKU induk Rocky Shopee kosong sejak awal.
- Kijang: file Elite/Epic pernah tertukar nama (diperbaiki 2026-10-31); `EPIC TRITON-2` dan `ELITE GRAND LIVINA-1` di Drive set 1–30 masih cacat, sheet memakai link ibb.co.com pengganti.

## TODO
- [ ] Unggah `TikTok_60+_atribut-impor-dan-foto_48produk_allinfo.xlsx` (All Information) — atribut "Imported goods"=Tidak + foto baru dalam satu file. Catatan: asumsi "Tidak" (produksi lokal); konfirmasi ke user bila ada produk barang impor.
- [ ] Unggah Shopee 31–60 (batch 1–5), Lazada foto produk lalu varian; cek hasil, ulang yang gagal.
- [ ] Kalau Shopee/Lazada juga menolak `i.ibb.co`, buat versi `i.ibb.co.com`.
- [ ] Foto Transparan, ±50 Signature sisanya, Xpander Cross.

## Set 60+ (folder `Smartpro\SMARTPRO NEW 60+`, 48 model) — audit 2026-11-06
Temuan, belum diperbaiki saat dicatat: (1) HOME dua spasi `SMARTPRO SIGNATURE  XFORCE HOME.jpg` dan `...E CLASS  HOME.jpg`; (2) `ELITE FEVEREST`,`-1`,`-2` seharusnya `ELITE EVEREST`; (3) Juke dan Palisade punya 16 file salinan ganda masing-masing (Signature -6..-11, Epic/Elite/Warrior -3..-5, `HOME-1`, isi byte sama dengan aslinya); (4) HOME salah tulis: "BMW C Class" (seharusnya Mercedes-Benz C Class; katalog "Mercedes Benz C Class", file `BMW C Class*` ikut diganti nama) dan "Mercedez Benz E Class" (Mercedes); (5) `SIGNATURE CORTEZ-5.png` caption terpotong (tanpa "Biru Benhur"). Selain itu 48 model lengkap (16 file), 1083x1083, caption cocok, zip sama dengan folder.

**Perbaikan set 60+ (2026-11-06):** spasi ganda HOME (XFORCE, E CLASS) dan FEVEREST dirapikan; Cortez dipulihkan (Abu-Abu asli dari zip, Biru Benhur perbaikan user jadi `-5`); C Class jadi `MERCEDES BENZ C Class` (15 PNG + HOME baru); 32 salinan ganda Juke/Palisade dipindah ke `Smartpro\_arsip_sebelum_revisi\Salinan ganda Juke-Palisade` (isi identik, diverifikasi). Folder 60+ kini 768 gambar = 48 model x 16. Pelajaran: di PowerShell jangan menamai fungsi `H` (alias `h` = Get-History).

**Link set 60+ (2026-11-06):** rencana unggah ke Postimages lewat Claude in Chrome: 658 gambar unik (768 file, sisanya kembar) dalam 31 batch <=9 MB, disiapkan di `Undercover\up60`. Batch 1 (22 gambar) sempat terunggah (galeri `https://postimg.cc/gallery/FLZ3rcg/8d0751bb`), tetapi `postimg.cc` lalu tidak bisa dibuka di Chrome (Privacy error / halaman galeri gagal; `postimages.org` tetap bisa) sehingga Direct link tidak bisa diambil. Dihentikan menunggu jaringan/jalur lain. Jangan lewati peringatan sertifikat.

**Link set 60+ (2026-11-09):** 658 gambar unik (768 file) diunggah ke Postimages lewat Claude in Chrome dalam 31 batch (1 unggahan per galeri; input file diganti setelah unggah). Direct link diambil dari dropdown `embed_box`=`code_direct`; pencocokan nama dinormalisasi (hapus non-alfanumerik) karena Postimg mengubah nama (spasi jadi tanda hubung). Hasil: `Smartpro\SMARTPRO NEW 60+\image url 60+ (postimg).txt` dan `...(nama file dan link).csv`. Kegagalan sebelumnya (postimg.cc Privacy error 2026-11-06) hilang pada 2026-11-09.

**Set 60+ file marketplace (2026-11-09):** dibuat dari ekspor 9 Nov, hanya 48 produk (file ringkas, baris berurutan): Shopee 8 batch x 6, Lazada foto produk 1 file, Lazada varian 3 file (510/510/463 SKU), TikTok 1 file; di `Foto Produk\{Shopee,Lazada,TikTok}0+`. Catatan: Nissan Evalia di Shopee tanpa variasi Orange (14 variasi); TikTok E Class bertitel lama "Cover Mobil / Selimut Mobil Mercedes Benz E Class"; Kuda Shopee typo "Eite Biru". Sampul HOME memakai link Postimg (TikTok menolak ibb).

**Lazada foto produk 60+ (2026-11-10):** hasil unggah 35/48 berhasil; 13 gagal ("Fail to migrate third party CDN main images", tanpa kode): Stargazer, Air EV, Stream, Santa Fe, Serena, Vitara, Cortez, Starlet, Carry Pickup, Mercedes C Class, Everest, Aerio Hatchback, MG S5 EV. File ulang `Lazada_foto-produk_60+_ULANG-13produk.xlsx` (link Postimg yang sama) dibuat.

**Lazada foto produk 60+ ulang 13 produk (2026-11-10):** **Sukses 13/13** (ID Upload 7397410, file `Lazada_foto-produk_60+_ULANG-13produk...`). Foto produk 60+ di Lazada selesai 48/48.

**TikTok 60+ — KOREKSI (2026-11-10):** ketiga file result (9:56, 10:38, dan result ulang) ternyata masing-masing berisi **48 produk gagal, bukan 2** — pembacaan awal keliru karena mode `read_only` openpyxl memotong jumlah baris file TikTok ini (dimensi sheet salah). Jadi unggah `TikTok_60+_48produk.xlsx` gagal **48/48**, semua dengan alasan sama: **atribut wajib "Imported goods" (ID 102254) kosong** — TikTok menjadikannya wajib di kategori *Cover & Shelter Mobil*. Pelajaran: jangan percaya `max_row` openpyxl `read_only` untuk file TikTok.

**TikTok 60+ fix atribut + foto sekaligus (2026-11-10):** file `all_information` ternyata pre-filled 218 produk (4.159 baris SKU) dan punya kolom `product_property/102254` "Imported goods" (pilihan dropdown: Ya/Tidak, dari sheet HiddenAttr kolom O/P) — pembacaan awal yang bilang kolomnya tidak ada keliru karena truncation `read_only`. Dibuat `Foto Produk\TikTok\60+\TikTok_60+_atribut-impor-dan-foto_48produk_allinfo.xlsx` (0,55 MB): template pre-filled dipangkas ke 48 produk (1.391 baris SKU), semua baris diisi Imported goods = **"Tidak"** + foto baru (main Postimg + 8 CDN) di kolom main_image–image_9; deskripsi/harga/stok data asli tidak diubah. Menunggu unggah (jenis template All Information). Verifikasi: 48/48 produk, 1.391/1.391 baris atribut terisi, sampul postimg 1.391, deskripsi lengkap.

**TikTok 31–60 (2026-11-10, dari riwayat unggah):** file `..._v4-postimg-direct_30-produk.xlsx` tercatat **Selesai (30 produk)** pada 05/11 — set 31–60 di TikTok **selesai**, tidak perlu v3 lagi.

**Shopee 60+ batch 1–2 (2026-11-10):** batch1 3/6 sukses (gagal: APV Luxury, Xpander Cross, Destinator), batch2 3/6 sukses (gagal: SX4, Vitara, Captiva). Alasan semua: "Maaf, server gagal upload beberapa foto. Mohon coba lagi nanti." = error sementara sisi Shopee (link sama dipakai produk lain yang sukses) → cukup unggah ulang file batch yang sama, tidak perlu file baru.
