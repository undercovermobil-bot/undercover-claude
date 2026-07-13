---
name: project-undercover-overview
description: "Peta tingkat-tinggi proyek Undercover — bisnis, toko, sub-proyek, dan cara memverifikasi lokasi file di sesi baru"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

Undercover = pemeliharaan katalog produk untuk bisnis cover mobil dengan 4 toko (Undercover Autocare/UA, Otonation/OT, Otoprotection/OP, Smartprotection/SP) di Shopee/TikTok/Lazada. Tiga sub-proyek:

1. **SKU Sync** (utama, paling bernilai) — menyamakan SKU semua listing ke 1 master, hasilkan file siap-upload per toko/channel. Lihat [[project-undercover-sku-sync-rules]], [[project-undercover-sku-sync-status]].
2. **Shopee Price Monitor** — pemantau harga kompetitor, mandek karena anti-bot Shopee. Lihat [[project-undercover-shopee-antibot]].
3. **Audit Foto Produk** — audit sekali-jalan, selesai 2026-07-06. Lihat [[project-undercover-photo-shopee-audit]].

Why: dicatat karena user berpindah-pindah akun Claude untuk proyek yang sama (lihat [[user-undercover-profile]]), jadi sub-proyek & statusnya perlu index yang bisa diakses tanpa mengulang riset tiap kali pindah akun.

How to apply: sebelum asumsi file ada/tidak ada di suatu path, jalankan Glob langsung di sesi berjalan — jangan percaya path hardcoded dari memory atau dari dokumen seed lama, karena struktur folder persis bisa berubah antar export/sesi. Contoh nyata (2026-07-08): nama file master mengandung koma yang bikin exact-match Glob gagal padahal filenya ada — kalau exact match gagal, coba pola wildcard `**/*kata kunci*` sebelum menyimpulkan file hilang. Working directory primer sesi ini sendiri bisa kosong total — cek "Additional working directories" di info environment sesi; biasanya di situ file project sebenarnya berada (per 2026-07-08: folder `Undercover\Export Undercover ke Akun Claude Lain`).

**Konvensi penamaan folder "List Produk <Toko>"**: ada 2 macam — folder BERTANGGAL (mis. "List Produk Undercover 6 Juli 2026") adalah snapshot BEKU dari tanggal itu, dan folder TANPA tanggal (mis. "List Produk Undercover", "List Produk Smartprotection", "List Produk Otoprotection", "List Produk Otonation" — semua di dalam `List Produk SKU/`) adalah working folder yang isinya di-update user langsung tiap kali re-export dari BigSeller/marketplace. **Selalu pakai folder TANPA tanggal + cek timestamp file di dalamnya** — jangan asumsikan folder bertanggal itu representasi kondisi live, karena riwayatnya (2026-07-09) year-range generasi di snapshot "6 Juli" untuk Chevrolet Cruze (2001-2008/2008-2024) sudah beda dari kondisi live/export terbaru (2008-2016/2015-2024). Per 2026-07-09, keempat toko (UA, SP, OP, OT) sudah punya export segar di folder tanpa-tanggal masing-masing.
