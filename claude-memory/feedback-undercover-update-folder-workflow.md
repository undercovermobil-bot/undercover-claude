---
name: feedback-undercover-update-folder-workflow
description: Mulai 2026-07-10 — semua file yang diedit lewat Claude ditulis ke folder "Update via Claude" terpisah, JANGAN overwrite file asli di lokasi asalnya
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6eb3e44c-d7d4-4c74-9baa-9ddd25e762ff
---

**Mulai 2026-07-10, JANGAN edit file listing/master di lokasi aslinya langsung.** Sebelum sesi ini, semua fix SKU Sync (Kategori A-D, GR86, dst) ditulis LANGSUNG ke file asli di `List Produk Undercover/`, `List Produk Otonation/`, dst — cuma di-backup ke scratchpad sesi (temporer, hilang antar sesi). User minta ini diubah: buat folder khusus, jangan overwrite file asli.

**Lokasi folder khusus:** `C:\Users\chand\Documents\Undercover\Export Undercover ke Akun Claude Lain\List Produk SKU\Update via Claude\`

**Struktur:** mirror persis struktur folder asli (`List Produk SKU\`), supaya gampang dibandingkan/dipetakan manual oleh user/tim produksi:
```
Update via Claude\
  SKU, Price, Tracking Cover Mobil.xlsx          <- master (isi UA saja yg sudah diupdate per 2026-07-10; SP/OP/OT belum)
  List Produk Undercover\
    Informasi Penjualan Shopee Undercover 1-5.xlsx
    Tiktok Semua Informasi Undercover 1.xlsx
    Stok & Harga Lazada Undercover.xlsx
  List Produk Otonation\      <- dibuat saat mulai kerjakan toko ini
  List Produk Otoprotection\  <- dibuat saat mulai kerjakan toko ini
  List Produk Smartprotection\ <- dibuat saat mulai kerjakan toko ini
```

**Cara kerja mulai sekarang:** sebelum edit file toko manapun (SP/OP/OT/UA), COPY dulu file yg relevan dari lokasi asli ke subfolder yg sesuai di "Update via Claude", baru edit COPY-nya di sana. File di lokasi asli TIDAK PERNAH disentuh lagi mulai titik ini. Kalau perlu baca data terkini (bukan nulis), tetap boleh baca dari lokasi asli — cuma proses TULIS yang wajib ke folder baru.

**Perubahan Undercover (UA) 2026-07-10 sudah disalin retroaktif** ke folder baru ini (atas permintaan user) — meski proses aslinya masih pakai pola lama (edit-in-place + backup scratchpad). File asli UA di lokasinya sendiri JUGA sudah ter-update (karena waktu itu masih pola lama) — jadi utk UA, file asli DAN folder baru sama-sama sudah versi terbaru. Untuk toko berikutnya (SP/OP/OT), file asli akan TETAP di versi lama, cuma copy di folder baru yang ter-update.

Why: user mau ada 1 tempat jelas berisi "apa saja yang Claude ubah" tanpa risiko file operasional asli (yang mungkin sedang dipakai tim produksi) keubah diam-diam sebelum direview.

How to apply: di awal sesi kerja SKU Sync manapun, cek dulu apakah folder ini sudah ada & apa isinya (mungkin sudah pernah dikerjakan sebagian di sesi lain) sebelum menganggap file asli itu "current state" — kalau folder "Update via Claude" untuk toko yang sedang dikerjakan sudah ada isinya, cek DI SITU dulu buat versi terbaru, bukan di lokasi file asli.

**(2026-07-11) Alur mass-upload e-commerce, penting utk cara mengemas hasil akhir:** user akan mass-upload manual ke tiap e-commerce SETELAH semua kerjaan SKU Sync clear/direview — TAPI file mass-upload itu HANYA boleh berisi baris/produk yang benar-benar BERUBAH SKU-nya, bukan seluruh katalog. Alasannya: kalau produk yang tidak berubah ikut disertakan, proses upload massal itu berisiko me-reset stok produk tersebut di e-commerce (stok akan tertimpa nilai di file, padahal stoknya di dunia nyata sudah beda). User akan kasih file stok/harga TERBARU terpisah tiap kali mau upload (jadi versi stok di "Update via Claude" tidak perlu terus disinkronkan real-time).

How to apply: kalau diminta menyiapkan file "siap upload" nanti, JANGAN kirim file lengkap semua produk — filter dulu ke baris yang SKU-nya benar-benar berubah dari versi asli (bandingkan file asli vs "Update via Claude"), dan tunggu file stok/harga terbaru dari user sebelum menggabungkan. Ini juga alasan kenapa laporan "Perlu Dicek"/"Sudah Diperbaiki" penting dijaga akurat per-baris (bukan cuma angka total) — supaya gampang di-filter jadi file mass-upload nanti.

Lihat [[project-undercover-sku-sync-status]] untuk detail teknis pekerjaan yang sudah dan belum dilakukan per toko.
