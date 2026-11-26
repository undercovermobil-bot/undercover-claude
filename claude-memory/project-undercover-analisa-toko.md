---
name: project-undercover-analisa-toko
description: Dashboard analisa per toko (9 toko, halaman per toko) - penjualan, iklan, organik, funnel, diagnosa, lantai diskon, aksi; data 26 Nov 2026
type: project
tags: [undercover, dashboard, analisa, shopee, tiktok, lazada, iklan, campaign]
updated: 2026-11-26
---

# Analisa Toko Undercover Group (dashboard per toko)

Artifact (tipe Data, privat): https://claude.ai/artifact/QvRZmXC6QxPAtEmtn3YVbg — 9 tab toko (UC/SP Shopee-TikTok-Lazada, OP Shopee-TikTok, OT Shopee). Contoh format: dashboard OP dari akun Claude lain https://claude.ai/artifact/KZyHWR1GXhPP553i45KxH3 (25 Nov, hanya bisa dibaca lewat Chrome Browser 4).

## Cara membangun ulang
- Data mentah (read-only, 26 Nov): `Documents\Undercover\data\toko_2026-11-26\` — `uc_dash_bigseller.json` (BigSeller: penjualan harian 1 Okt-25 Nov + bulanan Jun-Nov 9 toko, iklan Shopee Jun-Nov, iklan TikTok per hari), `uc_dash_shopee_<toko>.json` (Seller Center: traffic harian, iklan produk/toko per hari, iklan per produk 30 hari vs sebelumnya), `uc_oplog_<toko>.json` (riwayat pengaturan iklan 30 hari).
- Skrip: `Documents\Undercover\tools\analisa_toko.py` (+ teks temuan/aksi `catatan_toko.py`) → `out\dash_toko\*.json` (kpi, bulanan, harian, funnel, produk, diskon, catatan, aksi). Diunggah sebagai file dataset, halaman di `files/index.html` store artifact.
- Profil Chrome: Browser 1 = Otonation, 2 = Otoprotection, 3 = Undercover (+ BigSeller), 5 = Smartprotection, 4 = akun Claude lain (tidak login Shopee). Nama tampilan bisa berubah; cek `shop_info`.
- Endpoint Shopee (read-only): traffic `/api/mydata/traffic/dashboard/trend/?period=past30days|month&dt=YYYYMMDD`; iklan harian `/api/pas/v1/report/get_time_graph/` (agg_interval 1 = 15 menit); per iklan `/api/pas/v1/homepage/query/`; riwayat `/api/pas/v1/operation_log/query/` (maks 32 hari terakhir, end_time ≤ sekarang).
- Unduhan Blob dari profil Undercover di seller.shopee.co.id diblokir Chrome; jalan keluar: tulis JSON ke `<pre>` lalu `get_page_text`.

## Temuan utama 26 Nov 2026
- **Smartprotection Shopee**: 3 poin penalti (keterlambatan kirim 11,11%), tidak bisa daftar promosi 26 hari (±22 Des); Ingatkan 12 Des 3.877 variasi, 0 disetujui. Iklan 18% omzet, konversi iklan turun 5,7%→2,1%. Iklan Toko Otomatis ROAS 1,6.
- **Otonation Shopee**: 3 poin penalti (pesanan tidak terselesaikan 15,38%), larangan promosi 26 hari. Iklan Toko Otomatis ROAS 1,6. Omzet Nov naik 18%.
- **Otoprotection Shopee**: sehat (1 poin) tapi 12.12 & VIP belum dinominasikan. Iklan Toko+ ROAS 0,43. 23-25 Nov perubahan massal iklan tercatat "sistem" (bukan akun seller) — perlu dikonfirmasi.
- **Undercover Shopee**: sehat; laju Nov Rp989 jt (−5,6% vs Okt). Pengunjung/hari turun 3 minggu beruntun 1.425→1.329→1.184 (−17%; Okt rata 1.248), tayangan iklan minggu terakhir −19%, dan konversi toko turun (±7,7%→6,5-6,9%); CTR naik → bukan foto utama. (Koreksi 26 Nov: klaim awal "trafik +25%" salah karena membandingkan 30 hari dengan periode 26 hari; per hari produk dilihat hanya +8%.) Brio 10 perubahan pengaturan/30 hari; Innova & Ayla diubah 26 Nov.
- **TikTok** (Seller Center dicek 26 Nov, URL `seller-id.tokopedia.com/health-center` dan `/promotion/campaign-tools/management`): ketiga toko kinerja "Baik" (UC skor 248, SP & OP 200) tetapi respons chat 12 jam di bawah 85% (UC 75,5%, SP 66,7%, OP 76,7%) dan banyak pelanggaran pemenuhan pesanan (31/21/17). UC 22 campaign, SP 13, OP 11; belum ada yang ikut Co-Funded Voucher Gajian Sale & 12.12 (penjual tanggung 60%: voucher 25% untuk pesanan ≥Rp300 rb = beban ±15% harga; daftar s/d 13 Des 07.00). Saran: OP ikut (batas diskon ±24%), UC hanya produk terlaris tanpa potongan tambahan (batas ±16%), SP lewati (batas ±12%). Iklan: SP Produk_Pilihan ROAS 3,5 ≈ impas; OP target 16 terlalu tinggi; UC ROAS 13.
- Atribusi iklan Shopee/TikTok (broad/GMV Max) > omzet toko → organik diukur dari porsi kunjungan produk dari klik iklan (UC 47%, SP 64%, OP 60%, OT 61%), bukan selisih omzet.
- Foto kompetitor: lihat [[feedback-undercover-iklan-shopee-stabil]].

Terkait: [[project-undercover-margin]], [[2026-11-18 Audit Shopee Smartprotection iklan campaign affiliate]], [[feedback-undercover-hpp-strip-premium]].
