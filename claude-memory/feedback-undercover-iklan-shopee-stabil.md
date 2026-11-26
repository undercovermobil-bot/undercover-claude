---
name: feedback-undercover-iklan-shopee-stabil
description: Iklan GMV Max Shopee - jangan ubah target ROAS/modal terlalu sering, plus cara membaca tanggal upload foto Shopee dari ID gambar
type: feedback
tags: [undercover, shopee, iklan, gmv-max, foto, kompetitor]
updated: 2026-11-20
---

# Iklan GMV Max Shopee: stabilitas pengaturan + tanggal foto

## Aturan iklan (dari audit 20 Nov 2026, toko Undercover)
- Ubah target ROAS/modal **maksimal 1x per 7 hari per iklan**, langkah kecil (±1 poin / ±10%). Riwayat 30 hari Undercover: perubahan target ROAS massal tiap 3-6 hari (22 Okt, 27 Okt, 30 Okt, 2 Nov, 9-10 Nov, 14 Nov, 16 Nov, 20 Nov).
- Menaikkan target ROAS memangkas impresi. Contoh Brio: 14→15 pada 14 Nov, impresi harian 3,3-4,5rb → 2,1-3,0rb.
- Peringatan "Operasi Tidak Optimal - perubahan modal terlalu sering" di Brio/Avanza berasal dari **Modal Dinamis**: 11 Nov sistem menaikkan modal 3x lalu reset 12 Nov 00:00. Modal Dinamis sudah dimatikan user. Modal Brio Rp800rb jauh di atas belanja harian ±Rp350rb, jadi modal bukan pembatas.
- Masa tunggu 7 hari dihitung **per iklan dari perubahan terakhirnya**, bukan satu tanggal untuk semua iklan. Brio: data 15-18 Nov (sebelum traffic toko turun 19 Nov) sudah cukup sebagai bukti. Saran 20 Nov: kembalikan ROAS ke 14 sekali saja, lalu jangan diubah sampai lewat 25 Nov; cek 23-24 Nov apakah impresi kembali >=3,3rb/hari.
- Modal Dinamis bukan penyebab turunnya Brio: setelah reset 12 Nov, impresi 12-13 Nov masih normal (3,3-3,4rb); turun baru setelah ROAS dinaikkan 14 Nov.
- Riwayat bisa dibaca di detail iklan → "Riwayat Pengaturan Iklan" (filter 30 hari). Endpoint read-only: `/api/pas/v1/operation_log/query/`.
- Saldo iklan sempat Rp62rb dengan belanja ±Rp2,5 jt/hari. Pastikan isi saldo otomatis aktif agar iklan tidak berhenti.

## Tanggal upload foto Shopee
- ID gambar Shopee baru berbentuk `id-11134207-7rbk0-m6w67miris8se5`. Ambil 8 karakter pertama segmen terakhir (`m6w67mir`), lalu `parseInt(...,36)` = epoch milidetik saat upload (contoh: 8 Feb 2025).
- Tervalidasi: foto satu galeri produk jatuh di tanggal yang sama atau berdekatan.
- ID lama (hex 32 karakter) tidak bisa dibaca dengan cara ini.
- Thumbnail di hasil pencarian bisa berbeda dari foto utama di halaman produk.
- Dipakai untuk melihat kapan kompetitor mengganti foto utama: lihat [[2026-11-18 Audit Shopee Smartprotection iklan campaign affiliate]].

Terkait: [[project-undercover-dashboard]], [[feedback-undercover-foto-marketplace-lessons]]
