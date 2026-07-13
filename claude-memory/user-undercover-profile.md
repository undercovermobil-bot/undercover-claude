---
name: user-undercover-profile
description: Pemilik/pengelola bisnis cover mobil multi-toko di Indonesia; kerja lintas beberapa akun Claude untuk proyek yang sama
metadata: 
  node_type: memory
  type: user
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

User mengelola bisnis body cover mobil ("cover mobil") yang jualan lewat 4 toko — Undercover Autocare (UA), Otonation (OT), Otoprotection (OP), Smartprotection (SP) — di marketplace Shopee, TikTok, dan Lazada. Komunikasi & dokumen bisnis dalam Bahasa Indonesia; kode/artefak teknis dalam Inggris.

**Instruksi eksplisit (2026-07-09): balas dalam Bahasa Indonesia**, bukan cuma dokumen/komunikasi bisnis — respons chat Claude sendiri harus Bahasa Indonesia mulai sesi ini. Why: user minta langsung ("setelah ini gunakan bahasa indonesia") di tengah investigasi SKU Sync. How to apply: default ke Bahasa Indonesia untuk teks respons ke user (kode, nama variabel, SKU tetap Inggris/format teknis asli); kalau pindah sesi/akun baru dan tidak ada sinyal lain, aman untuk tetap pakai Indonesia sebagai default karena ini pola komunikasi user secara umum, bukan cuma preferensi sesaat.

User menjalankan proyek ini dari beberapa akun/sesi Claude berbeda, dan memindahkan konteks antar sesi lewat dokumen "seed context" yang ditulis manual (ditempel sebagai pesan pertama atau di-upload), bukan lewat satu sesi berkelanjutan. Lihat [[project-undercover-overview]] untuk hasil transplant konteks terbaru (2026-07-08).

User teliti soal akurasi katalog — sering cek manual 1 produk spesifik sebelum menerima deliverable sebagai "selesai," dan pertanyaan spot-check semacam itu berulang kali membongkar bug sistemik yang lebih besar (lihat [[feedback-undercover-sku-sync-lessons]]). Perlakukan pertanyaan "kenapa produk X begini?" sebagai sinyal untuk investigasi menyeluruh, bukan pertanyaan sepele.
