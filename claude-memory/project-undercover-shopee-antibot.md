---
name: project-undercover-shopee-antibot
description: Shopee Price Monitor mandek karena Shopee mendeteksi Chromium yang dikontrol Playwright; sudah pivot ke Apify actor
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

Aplikasi Python modular (config/utils/database/discovery/monitor/compare/dashboard + main.py CLI, SQLite, dashboard Streamlit) untuk memantau harga kompetitor di Shopee.

**Status: mentok pada scraping langsung, sudah dipivot.** Shopee (per 2026) mendeteksi Chromium yang dikontrol Playwright itu sendiri, bukan soal login/headless — diuji 5 kombinasi headless/headed × dengan/tanpa login, semua kena block (`90309999` atau halaman error). Login manual berhasil (`storage_state.json`) tapi tetap diblok begitu dipakai automation. `curl` polos ke API → 403.

Why: dicatat supaya sesi berikutnya tidak mengulang 5 percobaan yang sudah terbukti gagal. Kesimpulan tervalidasi: vanilla Playwright + stealth ringan TIDAK cukup untuk Shopee 2026. Dua opsi kalau mau jalan beneran: (a) API scraping berbayar — ScraperAPI/Apify, atau (b) browser anti-deteksi + proxy residensial.

**Sudah berhasil dipivot**: pakai Apify actor `4nhvc7lTKzkDrk7bD` (Shopee Search & Category Scraper) — tes 3 keyword → 97 produk asli masuk DB, dashboard jalan di localhost:8501.

How to apply: backend scraping terisolasi di class `ShopeeScraper` (discovery.py) — kalau ganti backend lagi, cukup swap di situ tanpa sentuh DB/dashboard/compare. Backend siap pakai: `apify_backend.py` dan `scraperapi_backend.py` (keduanya terverifikasi ada di folder export per 2026-07-08). Belum dikerjakan: jadwal cron harian, perluasan keyword per tipe mobil spesifik.
