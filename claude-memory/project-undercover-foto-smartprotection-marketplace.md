---
type: project
tags: [undercover, smartprotection, foto, shopee, lazada, tiktok]
updated: 2026-11-05
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
- [ ] TikTok 31–60: v1 (`i.ibb.co`) dan v2 (`i.ibb.co.com`) sama-sama ditolak 30/30 (2026-11-04 dan 2026-11-05). v3 = 30 sampul HOME diunggah ke Postimages lewat Claude in Chrome (2026-11-05), file `..._v3-postimg.xlsx`, menunggu unggah. Link Postimg tidak bisa dibuka dari jaringan/Chrome di sini (halaman error), jadi isi gambarnya belum terverifikasi; kalau v3 gagal, coba Pusat Media TikTok atau URL CDN Shopee setelah Shopee selesai.
- [ ] Unggah Shopee 31–60 (batch 1–5), Lazada foto produk lalu varian; cek hasil, ulang yang gagal.
- [ ] Kalau Shopee/Lazada juga menolak `i.ibb.co`, buat versi `i.ibb.co.com`.
- [ ] Foto Transparan, ±50 Signature sisanya, Xpander Cross.

## Set 60+ (folder `Smartpro\SMARTPRO NEW 60+`, 48 model) — audit 2026-11-06
Temuan, belum diperbaiki saat dicatat: (1) HOME dua spasi `SMARTPRO SIGNATURE  XFORCE HOME.jpg` dan `...E CLASS  HOME.jpg`; (2) `ELITE FEVEREST`,`-1`,`-2` seharusnya `ELITE EVEREST`; (3) Juke dan Palisade punya 16 file salinan ganda masing-masing (Signature -6..-11, Epic/Elite/Warrior -3..-5, `HOME-1`, isi byte sama dengan aslinya); (4) HOME salah tulis: "BMW C Class" (seharusnya Mercedes-Benz C Class; katalog "Mercedes Benz C Class", file `BMW C Class*` ikut diganti nama) dan "Mercedez Benz E Class" (Mercedes); (5) `SIGNATURE CORTEZ-5.png` caption terpotong (tanpa "Biru Benhur"). Selain itu 48 model lengkap (16 file), 1083x1083, caption cocok, zip sama dengan folder.

**Perbaikan set 60+ (2026-11-06):** spasi ganda HOME (XFORCE, E CLASS) dan FEVEREST dirapikan; Cortez dipulihkan (Abu-Abu asli dari zip, Biru Benhur perbaikan user jadi `-5`); C Class jadi `MERCEDES BENZ C Class` (15 PNG + HOME baru); 32 salinan ganda Juke/Palisade dipindah ke `Smartpro\_arsip_sebelum_revisi\Salinan ganda Juke-Palisade` (isi identik, diverifikasi). Folder 60+ kini 768 gambar = 48 model x 16. Pelajaran: di PowerShell jangan menamai fungsi `H` (alias `h` = Get-History).

**Link set 60+ (2026-11-06):** rencana unggah ke Postimages lewat Claude in Chrome: 658 gambar unik (768 file, sisanya kembar) dalam 31 batch <=9 MB, disiapkan di `Undercover\up60`. Batch 1 (22 gambar) sempat terunggah (galeri `https://postimg.cc/gallery/FLZ3rcg/8d0751bb`), tetapi `postimg.cc` lalu tidak bisa dibuka di Chrome (Privacy error / halaman galeri gagal; `postimages.org` tetap bisa) sehingga Direct link tidak bisa diambil. Dihentikan menunggu jaringan/jalur lain. Jangan lewati peringatan sertifikat.
