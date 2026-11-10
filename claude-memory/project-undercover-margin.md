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

## Affiliate riil dan pelacak data (6 Nov)
- Affiliate Undercover Shopee Okt: komisi 1,63% dari seluruh harga jual cair; hanya 40,8% pesanan kena affiliate dengan tarif rata-rata 3,8% (P50 2,8%, P90 7,2%, maks 9,2%; kelompok 2,5–3% dan 5,5–7,5%). Komisi dihitung dari harga jual setelah diskon penjual. TikTok: 1,41% total, 38,3% pesanan, tarif rata-rata 3,7% (2–2,5% dan 4–5%, maks 5%). Margin setelah iklan pesanan affiliate 13,3% vs non-affiliate 15,8% (Shopee); 16,4% vs 17,9% (TikTok).
- Skenario Shopee (margin rata-rata, kasus buruk: pesanan non-affiliate pindah jadi affiliate, tanpa tambahan volume): tarif +3 poin dengan porsi affiliate 60% → ±12,3%; +5 poin dengan porsi 70% → ±10,2% (dari 14,8%). TikTok +5 poin porsi 70% → ±12,7% (dari 17,2%). Skrip ad-hoc `scratchpad\aff.py`.
- Definisi margin sheet user = uang cair − HPP (iklan sudah dihitung sebagai % dalam tumpukan biaya); sama dengan definisi dashboard (margin setelah iklan). Sheet Avanza: 23.750 / 479.094 = ±5% memang desain harga. Keterangan "asal angka 5%" di catatan sebelumnya hanyalah dugaan, bukan konfirmasi user.
- Pelacak data diperbarui (65 baris): ditambah baris "Jun-Sep (data historis)" (estimasi) dan "November (1-6 Nov)" (belum ada) per toko×marketplace; baris HPP menyebut produk tanpa HPP terbanyak. Drive berisi CSV iklan Shopee harian 1 Okt–4 Nov (satu toko, belum dipetakan) dan file `Analisis_Koreksi_Agu_Okt.xlsx` (5 Nov) yang belum diperiksa; Downloads tidak punya Order/Income baru sejak 3 Nov.

## Data Jul–Sep riil dan pesanan batal salah penjual (9 Nov)
- User mengunggah file Sales Jul–Sep (Order.all, Income Shopee, Semua pesanan + income TikTok, Lazada) untuk 4 toko di `G:\My Drive\E-commerce\E-commerce Data\Sales\<toko>\` (satu file per bulan). Loader `tools\margin_all.py` kini menggabung semua file per toko (file terbaru menang bila nomor pesanan sama; baris income TikTok/Lazada ganda dibuang). Pesanan Jul–Sep 100% sudah cair; Pendapatan Kotor cocok dengan BigSeller (selisih <0,5%).
- `tools\dashboard_export.py`: default `--start 2026-07-01`; Jul–Okt dari file marketplace, Juni tetap dari BigSeller dengan rasio Jul–Okt. Iklan Jul–Sep tetap dari BigSeller (file iklan marketplace hanya mulai 1 Okt; `--ads-from`). Tracker: baris "Jun-Sep" diganti "Iklan Jul-Sep" dan "Juni (data historis)".
- Hasil riil (semua toko, margin = uang masuk − HPP): Jul 13,4% sebelum iklan / 7,3% setelah iklan; Agu 17,3% / 10,4%; Sep 22,6% / 15,2%; Okt 22,7% / ±14,5%. Penyebab margin Jun–Agu rendah: **harga jual naik**, bukan salah HPP. Undercover Shopee harga rata-rata per unit Rp289rb (Jun) → Rp294rb (Jul) → Rp315rb (Agu) → Rp343rb (Sep–Okt); HPP per unit stabil ±Rp175rb (HPP/harga 60% → 50%). Avanza Rp296rb → Rp382rb.
- Rasio uang masuk riil lebih tinggi dari rasio Okt yang dipakai sebelumnya: Undercover Shopee 73–74% (Okt 71%), TikTok 74,5–75%.
- **Pesanan batal salah penjual** (menu Ringkasan, 6 kartu + tabel alasan): kategori Pengiriman gagal (termasuk COD ditolak; di TikTok belum dibayar tetap dihitung), Penjual terlambat/tidak atur kirim, Paket hilang/rusak, Dibatalkan penjual, Sistem (lainnya). Tidak dihitung: dibatalkan pembeli, belum dibayar. Aturan ada di `cancel_cat_shopee` dan `cancel_cat_tiktok` (`margin_all.py`); pembeli "penjual tidak responsif" dianggap batal pembeli. Nilai = harga setelah diskon penjual; laba kotor potensi = nilai × rasio uang masuk toko − HPP barang batal. Data di `margin-data.json` kunci `cancels`, `cancelCats`, `cancelFrom` (mulai 1 Jul; Juni tidak ada). Lazada tanpa alasan batal, tidak dihitung.
- Besaran: Jul 113 pesanan batal salah penjual (Rp36,6 jt), Agu 83 (Rp26,7 jt), Sep 98 (Rp36,0 jt), Okt 61 (Rp21,4 jt; laba kotor hilang Rp5,0 jt).
- Dashboard v10 dipublikasi; tampilan awal kini bulan terakhir (Okt), bukan seluruh rentang detail.

## Optimasi dashboard v11 (10 Nov)
- Iklan kini diambil per hari dari file marketplace bila ada; hari tanpa file sebelum `--ads-from` (1 Okt) memakai BigSeller. Begitu user mengunggah iklan Jul–Sep ke `Ads\<toko>\`, cukup jalankan ulang `py -3 -I tools\dashboard_export.py`, tanpa ubah kode. Cek 10 Nov: belum ada file iklan Jul–Sep (Drive hanya sampai iklan November ±8 Nov).
- Ringkasan: tabel "Per bulan" (Jun–Okt: pendapatan, uang masuk, HPP, iklan, margin sebelum/setelah iklan, pesanan batal), tidak terpengaruh filter tanggal.
- Pelacak data diringkas dari 74 ke 56 baris: baris Juni dan November dijadikan satu per "Semua toko"; baris "Iklan Jul-Sep" menghitung hari yang sudah dari file marketplace. November: file iklan sudah ada, pesanan dan income November diunduh awal Desember (jalankan ekspor dengan `--end 2026-11-30`).

## Iklan November di dashboard v12 (10 Nov)
- Keputusan user 10 Nov: iklan sebelum Oktober TIDAK diunduh dari marketplace; Jul-Sep tetap dari BigSeller. Pelacak: "Iklan Jul-Sep" = Lengkap (sumber BigSeller), "Juni (data historis)" = Lengkap (tidak ditagih lagi).
- `tools\dashboard_export.py`: `--end` = hari terakhir penjualan (31 Okt), `--ads-end auto` = hari terbaru yang punya file iklan (kini 9 Nov). Hari setelah `--end` hanya berisi iklan; kunci JSON `salesTo`. Pelacak baru: "Iklan November" per toko (hari yang kurang tercantum) dan baris global "November (bulan berjalan)".
- Dashboard: halaman Iklan menampilkan sampai 9 Nov. Halaman lain dibatasi sampai 31 Okt (ada catatan bila rentang melewati itu; rentang murni November menampilkan "Penjualan belum ada" dengan tombol ke menu Iklan). ROAS Riil dan margin tidak dihitung untuk rentang yang melewati hari penjualan terakhir. Tampilan awal tetap Oktober; preset 7/30 hari terakhir relatif ke 31 Okt.
- Data iklan November 1-9 Nov: Undercover Shopee/TikTok dan Smartpro sampai 8 Nov (Smartpro TikTok tanpa 2 Nov), Otoprotection sampai 3 Nov, Otonation sampai 9 Nov.
- Awal Desember: unduh Order dan Income November per toko, lalu `py -3 -I tools\dashboard_export.py --end 2026-11-30`.

## Ringkasan format laba rugi, dashboard v13 (10 Nov)
- Permintaan user: dashboard rapi siap untuk klien, urutan dari penjualan termasuk pembatalan penjual, istilah keuangan. Ringkasan dirombak menjadi alur laporan laba rugi:
  Penjualan bruto (pesanan dibayar setelah diskon penjual) − Pembatalan oleh penjual − Retur dan refund = **Penjualan bersih** (= Pendapatan Kotor sisi penjual) − HPP = **Laba kotor** − Biaya marketplace (penjualan bersih − dana diterima: komisi, layanan, selisih ongkir, voucher penjual) − Biaya iklan = **Laba kontribusi** (sebelum biaya operasional dan pajak). Memo: Dana diterima dari marketplace.
- Catatan istilah: "Laba kotor" di dashboard kini = penjualan bersih − HPP (standar akuntansi). Angka lama "margin sebelum iklan" (uang masuk − HPP) tidak lagi ditampilkan; "margin setelah iklan" = laba kontribusi. "Uang masuk" diganti "Dana diterima" di semua halaman.
- Laba kontribusi kini dihitung untuk semua toko walau file iklan belum lengkap (ditandai oranye "+", catatan "belum final"); sebelumnya margin setelah iklan disembunyikan bila iklan tidak lengkap.
- Susunan Ringkasan: 6 kartu (bruto, bersih, laba kotor, biaya marketplace, biaya iklan, laba kontribusi) → pita angka pendukung (pesanan, rata-rata per pesanan, dana diterima, ROAS Riil, pembatalan penjual, retur) → tabel Laporan laba rugi (nilai, % penjualan bersih, periode lalu, perubahan; potongan ditulis dalam kurung) + penjualan bersih per toko → grafik → Laba rugi per toko → Laba rugi per bulan → Pembatalan oleh penjual.
- Data: kolom harian baru `refund` (negatif) di `margin-data.json`; retur Jul–Okt ±0,8–1,1% penjualan bersih. Okt: bruto Rp1,522 M, bersih Rp1,489 M, laba kotor Rp741 jt (49,7%), biaya marketplace Rp403 jt (27,1%), iklan Rp121 jt (8,1%), laba kontribusi Rp217 jt (14,6%).

## Filter multi-pilih (v14) dan saran optimasi Undercover & Smartpro (10 Nov)
- Dashboard v14: filter Toko dan Marketplace bisa pilih beberapa sekaligus (`MultiSelectMenu` di `select-menu.tsx`; `Filter.store`/`platform` kini `string[]`, kosong = semua).
- Temuan data Jul–Okt (laba kontribusi = penjualan bersih − HPP − biaya marketplace − iklan):
  - Undercover Shopee: pesanan 4.070 → 2.974 (−27%), rata-rata per pesanan Rp302rb → Rp354rb; laba kontribusi Rp92 jt (7,5%) → Rp179 jt (Sep, 15,5%) → Rp150 jt (Okt, 14,2%). Kenaikan harga terbukti menaikkan laba. Okt turun karena biaya Layanan Promo XTRA+ naik 4,8% → 6,9% harga (±Rp22 jt/bulan; juga naik di Smartpro 4,5 → 5,9%) dan iklan naik Rp72 → Rp80 jt sementara ROAS Riil turun 17,1 → 13,1.
  - Undercover TikTok: kontribusi 6,8% → 16,4%; komisi platform & Mall 11,6% vs Smartpro 7,4% (selisih ±4 poin ≈ Rp13 jt/bulan, kemungkinan biaya layanan Mall). Pengiriman gagal (COD) 83 pesanan Jul–Okt.
  - Cover Motor Regular rugi sebelum iklan: Shopee −13% (146 unit Okt, harga Rp117rb, HPP Rp101rb), TikTok −6,4%. Titik impas ±Rp138rb; untuk 10% sebelum iklan ±Rp160rb.
  - Smartpro Shopee: iklan 15,5% penjualan (Sep 20,6%, kontribusi −1,1%); impas ROAS Riil ±4,3x, Sep 4,9x. Biaya marketplace 22,9% (lebih murah dari Undercover 28,1%). Smartpro TikTok iklan 13,4%, pesanan turun 144 → 51.
  - PPh 22 0,5% mulai Okt di semua toko: pajak dipungut di muka, bisa dikreditkan.
- Saran yang diberikan ke user: lihat percakapan 10 Nov (prioritas: harga/iklan motor, cek Promo XTRA+, batas anggaran iklan per toko, SOP kirim tepat waktu dan konfirmasi COD, isi HPP Exclusive/Premium).

## Belum lengkap (per 5 Nov)
- Logo Undercover untuk dashboard.
- Otoprotection Shopee: file iklan Shop+ 2–31 Okt (Rp50.000 di 1 Okt, jadi memang jalan).
- TikTok Onhold untuk Smartpro dan Otoprotection (estimasi memakai rasio).
- Tab Pending Shopee (opsional), file Income November untuk finalisasi, penjualan 1 Nov semua toko.
- Tidak ada file Lazada untuk iklan; dashboard tidak punya blok iklan Lazada.

## Tindak lanjut
- [ ] Jalankan ulang margin setelah income November dan iklan Shop+ Otoprotection lengkap, lalu publish ulang dashboard React.
- [ ] Skrip di `Documents\Undercover\tools` dan `dashboard-app` belum di git/Drive — pertimbangkan dipindah ke `Undercover-Repo`.

## Selisih asumsi sheet harga vs biaya riil (5 Nov, malam)
- Sheet `Detail Harga Terbaru HPP 12%` memasang tumpukan biaya ±57% dari harga (iklan 7,5, admin 10,45, GOE 5,5, promo XTRA 6,5, SPaylater 2,5, affiliate 8, event toko 5,5, **PPN 11%**) dan menyisakan margin 5% (Avanza: harga Rp479.094, cair Rp206.250, HPP Rp182.500). Riil Undercover Shopee Okt: admin 10,4, GOE 5,4, promo 6,9, pembayaran 1,8, affiliate rata-rata 1,6 (aktif di 41% pesanan), voucher/koin 0,65, PPh 22 0,5, iklan 7,9, refund 0,9 → ±37%. Selisih ±20 poin = affiliate penuh, event toko, PPN.
- Analisa diskon dihitung dari harga jual riil di e-commerce saat ini (rata-rata Okt, setelah diskon penjual ±3,7%), bukan dari harga di sheet. **User memutuskan: abaikan baris PPN 11% di sheet** (jangan dipotong; 5 Nov).
- Rekonsiliasi: tumpukan biaya sheet tanpa PPN = ±46% (termasuk iklan 7,5%), memakai affiliate 8% dan event toko 5,5% di setiap pesanan. Di harga riil margin = ±5,7% (6 dan 5 pcs) dan ±4,2% (4 pcs), ruang diskon ≈ 0–1%: asal batas "5%" user. Dengan biaya riil rata-rata (±37%) margin ±14–15%, ruang ±14%. Pesanan yang benar-benar menyentuh tumpukan sheet <1%.

## Ruang diskon khusus Reguler polos (6 Nov)
- Skrip `tools\discount_reguler.py` (loader kini membawa kolom variasi: `vars`). Reguler polos = tanpa awalan Epic/Elite/Warrior/Strip, tanpa motor/Exclusive/Premium/Custom. Undercover Okt: Shopee 1.805 pesanan, TikTok 451.
- Shopee: harga rata-rata Rp322–434rb, margin setelah iklan 14,1–15,7%; diskon maks (margin 5%) 12,1% (HPP 158.667), 13,9% (182.500), 14,1% (218.250) pada biaya riil; dengan semua potongan aktif −0,8 s/d −3,1% (harga harus naik); dengan tumpukan sheet tanpa PPN −3 s/d −5%. TikTok: 15,1 / 16,0 / 17,5% normal, 10,5 / 11,4 / 13,0% semua aktif.
- Harga list riil di data Okt: Avanza dan Innova Rp385.000, Brio Rp332.000, Fortuner Rp457.000; harga terjual rata-rata Avanza Shopee Rp371.142 (margin setelah iklan 14,6%, uang cair ±Rp263rb). User menyebut harga awal Avanza seharusnya ±Rp332rb: belum dikonfirmasi (kemungkinan harga baru atau keliru dengan Brio). Jika Avanza Rp332rb: margin setelah iklan ±7,6% Shopee, ±8,9% TikTok biaya riil; −2,4% Shopee bila potongan penuh. Lantai harga Avanza (margin 5%): Shopee Rp319rb normal / Rp375rb semua aktif; TikTok Rp313rb / Rp330rb.
- Sheet user (cair Rp206.250 untuk Avanza) adalah model kasus buruk pada harga Rp479rb, bukan angka yang terjadi di pesanan nyata.
- Dikonfirmasi user (6 Nov): harga list Avanza Reguler = Rp385.000 (Rp332rb itu Brio). Skenario Avanza Rp332rb di atas tidak berlaku; hasil Reguler polos dengan data Okt tetap dipakai.

## Varian Strip dan skenario HPP +11% (6 Nov)
- Strip (user): HPP + Rp21.000, Alphard + Rp27.000, HiAce + Rp31.000. Diterapkan lewat `line_hpp()` di `tools\margin_all.py` untuk nama variasi berawalan "Strip" (dipakai juga `dashboard_export.py`). Varian Strip hanya muncul di Otoprotection dan Otonation (Okt: ±17 + 5 pesanan); Jun–Sep (BigSeller) tidak membawa nama variasi sehingga tidak disesuaikan. Dampak margin sebelum iklan: Otoprotection Shopee −Rp147rb, Otoprotection TikTok −Rp210rb, Otonation Shopee −Rp126rb. Epic/Elite/Warrior masih tanpa HPP.
- "HPP 11%" dari user ditafsirkan dua cara dan dihitung dua-duanya (`discount_reguler.py --hpp-mult 1.11` dan `--margin 0.11`). HPP ×1,11 (Reguler polos, Okt): Avanza Shopee margin setelah iklan 9,2% (dari 14,6%), diskon maks 5,8% (HPP 6 pcs 4,0%); TikTok Avanza 12,7%, diskon maks 8,1%; semua potongan aktif Shopee −10,5% (harga harus naik), TikTok +3,2%. Target margin 11%: Shopee diskon maks 3,4–5,6%, TikTok 7,0–9,6%.
- Koreksi tafsiran (6 Nov): "HPP 11%" dari user = **user berencana membayar PPN 11%** (bukan HPP naik). Skrip `discount_reguler.py --ppn 0.11` (11% dari harga, seperti sheet) dan `--ppn 0.0991` (11/111, harga sudah termasuk PPN). Reguler polos Okt, margin setelah iklan dan PPN: Shopee Avanza 3,6% / 4,7%, Brio 2,7% / 3,8%; TikTok Avanza 7,0% / 8,1%, Brio 4,7% / 5,8%. Ruang diskon (margin 5%, termasuk refund): Shopee HPP 182.500 −3,1% / −1,1% (harga harus naik), 158.667 −5,2% / −3,2%; TikTok 182.500 0% / +1,8%, 158.667 −1,0% / +0,8%. Menghapus diskon penjual rata-rata Shopee (3,1%) ≈ mengembalikan margin ke ±5–6%. Belum dihitung: PPN masukan dari pembelian kain (bila ada faktur pajak, PPN bersih ±6% bukan ±10–11%).

## Epic/Elite/Warrior = Strip (6 Nov, malam)
- User: Epic, Elite, Warrior sama dengan Strip → HPP = Reguler polos + Rp21rb (Alphard +27rb, HiAce +31rb). `line_hpp()` di `tools\margin_all.py` kini menambah untuk variasi berawalan Strip/Epic/Elite/Warrior/Warior. Koreksi: sebelumnya varian itu (dalam produk berjudul Reguler) dihitung dengan HPP polos, bukan "tanpa HPP". Dampak margin Okt setelah iklan: Undercover Shopee 154,9 → 145,1 jt, Undercover TikTok 53,9 → 50,5 jt, Smartpro Shopee 3,98 → 3,47 jt, Smartpro TikTok 2,22 → 2,19 jt; Otoprotection TikTok 4,96 jt, Otonation 1,23 jt (varian Strip sudah dihitung sebelumnya).
- `discount_reguler.py` kini default semua varian mobil (pakai `line_hpp`), `--plain-only` untuk polos saja. Hasil semua varian ≈ polos: Shopee diskon maks 12,1–15,0%, TikTok 10,4–17,8% normal; dengan PPN 11% dari harga Shopee margin setelah iklan dan PPN Avanza 3,6%, Brio 2,9%; TikTok Avanza 6,9%, Brio 5,0%. Dashboard v8 diterbitkan dengan HPP ini (tanpa PPN).
- Dokumen yang masih kurang (per 6 Nov): Onhold TikTok Okt (Smartpro, Otoprotection), iklan Shop+ 2–31 Okt Otoprotection Shopee, tab Pending Shopee (opsional; Undercover 606 pesanan), income November, data November semua toko, data riil Jun–Sep, HPP Exclusive/Premium dan model di luar daftar, file logo.

## Saldo yang disarankan tetap di e-commerce (6 Nov)
- Data Okt per toko×marketplace (iklan/hari rata-rata, P95, maks; refund maks per minggu), skrip ad-hoc `scratchpad\cash.py`. Iklan P95/hari: UC Shopee Rp3,9 jt (maks 6,5 jt), UC TikTok 1,0 jt, Smartpro Shopee 0,40 jt, Smartpro TikTok 0,11 jt, Otopro Shopee 0,08 jt (data Shop+ kurang), Otopro TikTok 0,17 jt, Otonation Shopee 0,11 jt. Refund maks/minggu: UC Shopee 3,1 jt, UC TikTok 2,2 jt, lainnya 0.
- Rumus saran: iklan 3 hari × P95 (hemat) atau 7 hari (aman) + cadangan refund 1,5 × maks mingguan + bantalan Rp1 jt (selisih ongkir/denda). Hemat ≈ UC Shopee 17 jt, UC TikTok 6,5 jt, Smartpro Shopee 2,5 jt, Smartpro TikTok 1,5 jt, Otopro Shopee 1,5 jt, Otopro TikTok 1,5 jt, Otonation 1,5 jt (total ±32 jt); aman ±55 jt. Saat 11.11 naikkan cadangan iklan ×2. Dana belum cair besar (UC Shopee ±156 jt, UC TikTok ±58 jt) memang tidak bisa ditarik. Alasan suspend: tidak bisa dipastikan; sarankan tanya Seller Support.

## Pembaruan data 7 Nov
- Masuk sejak 5 Nov: Onhold TikTok Okt untuk Smartpro dan Otoprotection (6 Nov), Shop+ Otoprotection Shopee kini 24/31 hari Okt (kurang 5 Okt, 13–15 Okt, 23–25 Okt) dan 1–3 Nov. Dashboard v9 diterbitkan dengan data ini.
- Iklan terakhir per toko (cek 7 Nov): Undercover dan Smartpro (Shopee dan TikTok) 1 Nov; Otonation Shopee 2 Nov; Otoprotection Shopee 4 Nov (Data Keseluruhan) dan 5 Nov (Iklan Produk Otomatis), Shop+ 3 Nov; Otoprotection TikTok 3 Nov. Hanya Otoprotection yang tampak otomatis. Data sales November sengaja belum ada (ditarik tiap awal bulan).
- Masih kurang: Shop+ Otoprotection Shopee tanggal di atas (margin setelah iklan toko itu belum bisa dihitung), iklan Nov per toko, tab Pending Shopee (opsional), income November, data riil Jun–Sep, HPP Exclusive/Premium/Custom, logo.

## Cek data 9 Nov dan margin Jun–Sep
- Data baru sejak 7 Nov: iklan Undercover Shopee (Data Keseluruhan, Iklan Produk Otomatis, Shop+) dan TikTok sampai 6 Nov. Lainnya tidak berubah: Smartpro iklan 1 Nov; Otonation 2 Nov; Otoprotection Shopee 4/5 Nov (Shop+ 3 Nov), TikTok 3 Nov. Tidak ada file sales/income baru (folder Sales hanya berisi Okt).
- Jun–Sep **tidak punya data uang cair riil**: uang masuk = Pendapatan Kotor × rasio uang masuk Okt per toko (Undercover Shopee 71,6%, TikTok 74,1%, Smartpro Shopee 76,6%, dll.; total ±72,7%). Iklan Jun–Sep dari data iklan BigSeller. HPP dari nama produk BigSeller.
- Margin setelah iklan per bulan (estimasi, dashboard): Jun 89,5 jt (6,4% dari pendapatan 1.407 jt), Jul 108,9 jt (6,3%), Agu 163,1 jt (9,0%), Sep 238,5 jt (14,4%), Okt 211,6 jt (14,2%). HPP/pendapatan turun dari 61% (Jun) ke 50% (Okt): belum dijelaskan (kemungkinan bauran produk/harga/pemetaan nama); perlu diperiksa sebelum dipercaya. Untuk angka riil perlu Income Shopee/TikTok Jun–Sep.
