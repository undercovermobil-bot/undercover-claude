---
name: project-undercover-margin
description: "Analisa margin per pesanan (income Shopee/TikTok vs HPP, setelah iklan) dibangun 2-3 Nov 2026; hasil Okt, keputusan HPP per toko, skrip dan artifact"
type: project
tags: [margin, hpp, dashboard, analisa]
updated: 2026-11-04
---

# Analisa margin Undercover (mulai 2026-11-02)

Tujuan user: tahu margin riil per pesanan = income yang cair dari marketplace dikurangi HPP, lalu dikurangi iklan; dan income sebagai % dari harga jual Shopee untuk melihat biaya Shopee sebenarnya. Detail teknis lengkap (kolom file, rumus yang diverifikasi) ada di [[manual-export-to-dashboard-mapping]]; cara tarik data BigSeller di [[bigseller-dashboard-refresh]]. Induk: [[project-undercover-dashboard]].

## Hasil Oktober 2026 (laporan 2 Nov, Undercover saja)
- Margin setelah iklan: **Shopee Rp164,5 jt (15,6%)**, **TikTok Rp58,1 jt (18,8%)**.
- 6–7% penjualan bersih tanpa HPP (cover motor, Exclusive, custom), diestimasi dengan rasio sama; bisa diisi di sheet HPP.
- Pesanan belum cair memakai estimasi (TikTok Onhold; Shopee = rasio yang sudah cair) → **jalankan ulang setelah income November**.

## Keputusan user
- **HPP per toko (3 Nov):** Undercover & Otonation memakai file HPP UC (`G:\My Drive\E-commerce\DATA UC HPP Top 100 Terlaris.xlsx`, sheet `Top 100 Terlaris`); Smartpro & Otoprotection memakai Google Sheet "HPP STP OTP" (sheet "Harga jual 7%", HPP = 715000/pcs + 39500, cache `data\hpp_stp_otp.json`).
- Varian Signature Waterproof, Transparan, Semi Outdoor memakai HPP yang sama (asumsi). Exclusive/Premium/motor/custom sengaja tidak dicocokkan ke HPP Reguler.
- Agya, Ayla, Jazz, Ignis: 6 pcs/roll (Rp158.667), sesuai sheet `Top 100 Terlaris` (keputusan 2 Nov).
- "Biaya Isi Saldo Otomatis" = top-up saldo iklan, bukan biaya Shopee → dikeluarkan agar iklan tidak terhitung dua kali.

## Skrip dan keluaran (di `C:\Users\OWNER\Documents\Undercover`, bukan repo git)
- `tools\margin_report.py` → `out\Margin_Undercover_Okt2026.xlsx` (2 Nov)
- `tools\margin_all.py` → `out\margin_data.json` (semua toko); `tools\dashboard_datasets.py` → `out\ds\*.json`
- `tools\manual_to_data.py` → `out\dashboard_data.manual.json` + `out\laporan_manual.md`
- Artifact dashboard margin (private): https://claude.ai/artifact/2KpyFjMqox3MkUyXf16Mcj. Artifact penjualan & iklan 2W18… **tidak diubah** oleh pekerjaan ini.

## Belum lengkap (per 3 Nov)
- Iklan Otoprotection (Shopee CPC, Shop+, TikTok) dan Otonation Shop+ untuk 2 Okt–1 Nov.
- Undercover: Shopee CPC 6 Okt, TikTok Product data 28 Okt; order 1 Nov.
- Tidak ada file Lazada untuk iklan; dashboard tidak punya blok iklan Lazada.
- Smartpro Shopee tidak punya `Order.all` (hanya `Order.toship` kosong), kecuali yang masuk 3 Nov 13:52; TikTok Onhold hanya untuk Undercover.

## Tindak lanjut
- [ ] Jalankan ulang margin setelah income November dan iklan Otoprotection/Otonation lengkap.
- [ ] Skrip di `Documents\Undercover\tools` belum di git/Drive — pertimbangkan dipindah ke `Undercover-Repo`.
