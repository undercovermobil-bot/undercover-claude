---
type: project
tags: [undercover, dashboard, bigseller]
updated: 2026-10-30
---

# Dashboard Penjualan & Iklan — Undercover Autocare Group

Dashboard 1 file HTML (Chart.js) berisi penjualan & iklan 9 toko ([[toko-dan-id-bigseller]]), sumber BigSeller sisi penjual, dipakai meeting bulanan.

**Lokasi sumber:** `G:\My Drive\E-commerce\Undercover-Dashboard\dashboard-src\` (`template.html`, `script.js`, `data/dashboard_data.json`, `build.py`). Detail teknis: [[dashboard-README]], cara tarik data: [[bigseller-pull-snippets]], desain: [[Plan - Dashboard Penjualan & Iklan (Jun-Sep 2026)]].

## Status (per 2026-10-21, terakhir tercatat)
- Data 1 Jun – 20 Okt 2026, N=142 hari. Artifact utama v4.
- Okt 1–20: Pendapatan Kotor Rp960.807.214, pesanan valid 2.676/2.871, biaya iklan Rp76.312.136, ROAS Riil 12,59x, Δ vs 1–20 Sep −16,9%.
- Bulanan: Jun 1.407.364.859 · Jul 1.715.485.260 · Agu 1.807.840.680 · Sep 1.659.040.141 (setelah revisi live 14 Okt).

## Artifact
| Link | Status |
|---|---|
| https://claude.ai/artifact/2W18PfBwBaZ56KPGc9dEm6 | **Utama**, boleh di-update (baca dulu, publish ke URL sama) |
| https://claude.ai/artifact/VLbze83JXquCSDNMgTDFQd | Arsip beku v3 (Jun–Sep) — jangan disentuh |
| https://claude.ai/artifact/PKhFeWgXqMfreXLs6e5wD8 | Meeting v13 — **dikunci** |

## Aturan keras
1. BigSeller **read-only** — jangan tulis/ekspor/unduh/ubah setting.
2. Pendapatan Kotor (sisi penjual) = satu-satunya angka omzet. Jangan pakai metrik sisi pembeli.
3. Jangan tulis "ralat"/"revisi" di tampilan untuk atasan.
4. Angka bulan lalu yang bergeser → laporkan selisih, tunggu keputusan pemilik.
5. Build: `python -X utf8 build.py --out "../Dashboard Harian - Penjualan & Iklan - Jun-Okt 2026.html"` (selalu `--out`).

## Tugas berikutnya
- [ ] **1 Nov 2026**: tarik poin penalti akhir Oktober 4 toko Shopee → isi `HEALTH_MONTHEND['2026-10-31']` di `script.js`.
- [ ] Perpanjang data ke 21–31 Okt (rekonsiliasi ulang Jun–Okt dulu), tambah preset bulan November.
