---
name: project-undercover-margin
description: "Analisa margin per pesanan (income Shopee/TikTok vs HPP, setelah iklan) dibangun 2-3 Nov 2026; hasil Okt, keputusan HPP per toko, skrip dan artifact"
type: project
tags: [margin, hpp, dashboard, analisa]
updated: 2026-11-05
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

## Hasil Oktober 2026, semua toko (jalankan 5 Nov, setelah iklan Otoprotection/Otonation masuk)
Margin setelah iklan (pesanan dibuat 1–31 Okt, HPP per toko di atas): Undercover Shopee Rp164,8 jt (15,6%), Undercover TikTok Rp58,0 jt (18,7%), Smartpro Shopee Rp3,6 jt (7,6%), Smartpro TikTok Rp1,1 jt (7,1%), Otoprotection TikTok Rp4,3 jt (17,2%), Otonation Shopee Rp1,4 jt (10,0%). Total enam baris lengkap Rp233 jt (15,9%). Otoprotection Shopee belum bisa (iklan Shop+ belum ada; CPC sudah lengkap). Lazada tanpa data iklan.
- Dana cair di file Income disusun menurut **tanggal cair**: pesanan Oktober yang belum cair (Shopee 606 pesanan UC) baru muncul di file Income **November**; angka Oktober memakai estimasi sampai itu. Tab Pending Shopee hanya memperbaiki estimasi, tidak wajib.

## Dashboard React (5 Nov 2026)
- Permintaan user: tampilan seperti komponen shadcn `app-dashboard-shell` (Tailwind 4 + TypeScript), tanpa bagian workspace, metrik disesuaikan data, plus kalender rentang tanggal "Dari / Sampai" dan kolom **biaya iklan** per toko & marketplace.
- Proyek: `C:\Users\OWNER\Documents\Undercover\dashboard-app` (Vite + React 19 + Tailwind 4, struktur shadcn `src/components/ui`, `components.json`). Komponen: `app-dashboard-shell.tsx`, `date-range-picker.tsx`, `app-dashboard-shell-utils/{app-block-kit,views}.tsx` (kit ditulis sendiri karena file aslinya tidak ikut dikirim).
- Data: `tools\dashboard_export.py` → `dashboard-app\src\data\margin-data.json` (per pesanan, iklan harian, potongan harian; semua angka dihitung ulang di browser untuk rentang tanggal/toko/marketplace apa pun).
- Build: `npm run build` → `dist\fragment.html` (satu file) → publish ke artifact **https://claude.ai/artifact/LPAmvucR6uaSEVGvQADh66** (private, "Margin Undercover Group"). Artifact lama bertipe Dashboard (2KpyFj…) sudah tidak ditemukan per 2026-11-05 (dihapus atau tidak dibagikan).
- Refresh: `py -3 -I tools\margin_all.py; py -3 -I tools\dashboard_datasets.py; py -3 -I tools\dashboard_export.py; cd dashboard-app; npm run build`, lalu publish ulang `dist\fragment.html` ke URL yang sama.

## Dashboard React v2 (5 Nov 2026, permintaan user)
- Angka utama diganti **Pendapatan Kotor** (sisi penjual, ≈ harga setelah diskon penjual dan refund); ada **ROAS Riil** (Pendapatan Kotor ÷ biaya iklan) dan **ROAS Platform**, ACOS, CTR, CPC, CR (Shopee).
- Menu: Ringkasan, **Iklan** (matriks iklan per toko), **Biaya Marketplace** (diskon penjual, diskon marketplace, biaya per kelompok), Produk, Pesanan, **Pelacak data** (apa yang kurang per toko dan marketplace, plus apa yang harus diunduh).
- Warna utama biru (#0f62d6 terang, #3d9bff gelap, dari dashboard lama); dropdown toko/marketplace dibuat sendiri (select bawaan tidak terbaca di mode gelap). **Logo Undercover belum ada**: tidak ditemukan di Drive, Documents, Downloads; sementara monogram "UC". Perlu file logo dari user, taruh di `dashboard-app\src\assets` lalu ganti `BrandMark`.
- Data Jun–Okt 2026 (153 hari). Okt dari file ekspor marketplace. **Jun–Sep dari data BigSeller lama** (`data\dashboard_data.base_2026-11-01.json`), uang masuk, HPP, diskon dan biaya marketplace diperkirakan dengan rasio Oktober per toko dan HPP per produk. Atas permintaan user, dashboard **tidak boleh menulis keterangan estimasi** untuk bulan sebelum Oktober. Daftar pesanan per nomor hanya ada mulai 1 Okt.
- Skrip: `tools\dashboard_export.py` (data v2 + pelacak), `tools\margin_all.py` (bidang diskon ditambah). Default rentang = Oktober.

## Kapasitas diskon penjual (konsultasi 5 Nov 2026)
Skrip `tools\discount_capacity.py`. Syarat user: margin minimal 5% **setelah iklan**. Model per pesanan: p(1−v−refund) − biaya tetap − HPP − iklan per pesanan ≥ 5% p. Data Undercover Okt (pesanan cair satu unit).
- Shopee (harga rata-rata → diskon tambahan maks dari harga sekarang; normal / affiliate penuh / semua potongan aktif P95): HPP 158.667 (Rp328.794) 13,8% / 6,2% / tidak ada ruang (butuh naik ±1%); HPP 182.500 (Rp378.679) 15,7% / 8,2% / 1,1%; HPP 218.250 (Rp438.568) 15,0% / 7,5% / 0,3%.
- TikTok: HPP 158.667 (Rp335.726) 17,0% / 12,9% / 12,5%; 182.500 (Rp380.699) 17,7% / 13,7% / 13,3%; 218.250 (Rp448.594) 18,6% / 14,6% / 14,2%.
- Asumsi: iklan tetap per pesanan (Rp27 rb Shopee, Rp28 rb TikTok), volume tidak naik karena diskon, HPP sama untuk semua varian. Smartpro/Otopro/Otonation margin lebih tipis (7–17%), ruang diskon jauh lebih kecil (Smartpro Shopee ±3–4%).

## Pembaruan HPP dan dashboard v3 (5 Nov)
- Tabel HPP: `Documents\Undercover\data\hpp_models.json` (316 model → pcs/roll; HPP Reguler = 715.000/pcs + 24.500 + 15.000; motor Regular 99.083, Jumbo 118.944). Dibaca oleh `tools\margin_all.py` (`build_hpp`). Model di luar dua sheet dicari ukurannya di web dan disamakan dengan model terdekat; daftar + catatan ada di kunci `research` pada JSON.
- Belum jelas: sheet Transparan (MPV 1 pcs → Rp306.500 terlihat janggal) tidak dipakai; HPP motor masih asumsi; Exclusive/Premium/Custom tanpa HPP.
- Dashboard v3 (artifact LPAmvu…): kartu KPI menampilkan delta vs periode sebelumnya (bulan penuh vs bulan sebelumnya, ≤1 bulan vs tanggal sama bulan lalu, lebih panjang vs periode sama panjang sebelumnya); perbandingan hanya memakai toko yang ada di kedua periode. Font judul Fraunces dibuang.
- Margin Okt setelah iklan (HPP baru): UC Shopee 154,9 jt, UC TikTok 53,9 jt, Smartpro Shopee 3,26 jt, Smartpro TikTok 1,12 jt, Otopro TikTok 4,37 jt, Otonation 1,36 jt.

## Pembaruan 5 Nov (sore): HPP Transparan/motor, biaya per toko, keaktifan potongan
- HPP dihitung **per model/varian** (pcs/roll per model): mis. Avanza 5 pcs → Rp182.500, Brio 6 pcs → Rp158.667. Motor Regular dan Motor Strip Rp99.083, Motor Jumbo Rp118.944 (dikonfirmasi user dari sheet Motor, HPP atas).
- Transparan (sheet Transparan, HPP atas): setara/di atas Innova Rp306.500 (1 pcs/roll); di bawahnya (Avanza, Brio, dst.) Rp121.833 (3 pcs/roll). Diterapkan sebagai varian "Model (Transparan)" di `margin_all.py`; model dengan pcs ≤4 otomatis besar, model Midsize yang sebanding Innova didaftar di `data\hpp_models.json` kunci `transparan.big_models` (perkiraan panjang ≥ ~4,6 m, perlu dikoreksi user). Hanya 63 dari 4.266 unit Okt yang Transparan.
- Koreksi: kelompok "7 pcs/roll" di analisa diskon sebelumnya sebenarnya cover **motor** (HPP Rp99.083, harga rata-rata ±Rp117 rb), bukan mobil 7 pcs. `discount_capacity.py` kini mengelompokkan per nilai HPP persis. Cover motor rugi setelah iklan (−38% Shopee, −32% TikTok) dengan asumsi iklan rata-rata per pesanan.
- Skrip baru `tools\fee_report.py`: biaya per toko×marketplace dan keaktifan potongan opsional (Okt, pesanan cair). Biaya admin Shopee: Undercover 10,3%, Smartpro/Otopro/Otonation ±8,2%. Komisi platform TikTok: Undercover 11,6%, lainnya 7,4%.
- Keaktifan Undercover Shopee (Okt, 2.368 cair): affiliate 40,8% pesanan, voucher/koin penjual 58,4%, promo XTRA tinggi (>7,5%) 20,1%; ketiganya bersamaan 5,4%; total potongan ≥33% 5,3%, ≥35% 1,3%. TikTok: affiliate 38,3% pesanan; total potongan tidak pernah ≥30%. Data biaya nyata hanya ada untuk Oktober (Jun–Sep estimasi).

## Koreksi Transparan dan margin menurut total potongan (5 Nov, malam)
- Batas Transparan besar/kecil dipastikan dari harga listing Smartpro Shopee (`Downloads\mass_update_sales_info_473932094_20261105145144.xlsx`): ±Rp431–434rb = besar (HPP Rp306.500, 1 pcs/roll), ±Rp196–199rb = kecil (HPP Rp121.833, 3 pcs/roll). Besar = setara/di atas Innova, panjang ≥ ~4,73 m (Innova, Fortuner, Pajero Sport, Triton, Hilux, HiAce, Alphard, Vellfire, Odyssey, Everest, Santa Fe, Palisade, Land Cruiser, Camry, Accord, BMW Seri 5, E Class). Voxy, Serena, Captiva, Destinator, Harrier, Almaz, Kijang kecil. Model tanpa listing besar ditambah menurut panjang (`transparan.extra_by_length`). Aturan "pcs ≤4 otomatis besar" dicabut.
- `tools\fee_margin.py`: margin per pesanan menurut total potongan persen (Undercover Okt, 1 unit, ber-HPP). Shopee semua 14,8% setelah iklan; potongan ≥35% (1,3% pesanan) margin 7,0% setelah iklan (14,6% sebelum iklan), 33–35% 9,3%. Hampir semua pesanan punya diskon penjual (Shopee 93%, rata-rata 3,7% dari harga list; TikTok 58%, 2,1%). TikTok semua 17,2%, total potongan tidak pernah ≥30%.
- Diskon tambahan maks berlaku untuk Shopee (13,9–15,6%) dan TikTok (17,3–18,7%) pada potongan normal; Shopee turun ke ±0–1,5% bila semua potongan aktif. Cover motor tidak boleh didiskon (sudah rugi).

## Belum lengkap (per 5 Nov)
- Logo Undercover untuk dashboard.
- Otoprotection Shopee: file iklan Shop+ 2–31 Okt (Rp50.000 di 1 Okt, jadi memang jalan).
- TikTok Onhold untuk Smartpro dan Otoprotection (estimasi memakai rasio).
- Tab Pending Shopee (opsional), file Income November untuk finalisasi, penjualan 1 Nov semua toko.
- Tidak ada file Lazada untuk iklan; dashboard tidak punya blok iklan Lazada.

## Tindak lanjut
- [ ] Jalankan ulang margin setelah income November dan iklan Shop+ Otoprotection lengkap, lalu publish ulang dashboard React.
- [ ] Skrip di `Documents\Undercover\tools` dan `dashboard-app` belum di git/Drive — pertimbangkan dipindah ke `Undercover-Repo`.
