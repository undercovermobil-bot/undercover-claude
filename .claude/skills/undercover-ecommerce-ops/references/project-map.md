# Peta sub-project e-commerce

Detail dan status terbaru selalu di vault (`00 Home.md`). Di sini: tujuan, aturan khas, dan di mana kodenya.
Tambahkan baris di sini setiap ada sub-project baru.

| Sub-project | Intinya | Aturan khas / jebakan | Catatan vault, kode |
|---|---|---|---|
| **SKU Sync** | Samakan SKU semua listing 4 toko x channel ke 1 master | 9 aturan final (jangan didesain ulang); edit salinan di folder "Update via Claude", jangan timpa file asli; file mass-upload hanya baris yang berubah; master dibagi lintas toko/channel; filter berbasis kode SKU rapuh (2 skema tier) | `project-undercover-sku-sync-rules`, `-sku-sync-status`, status per toko (`-otonation/-otoprotection/-smartprotection-status`), `feedback-undercover-sku-sync-lessons`; skrip `Undercover-Repo\scripts\`, `sku-sync-scripts\` |
| **Sync SKU Gudang BigSeller** (mulai 28 Jul) | Sinkronkan SKU listing ke SKU Gudang BigSeller | SKU gudang dibuat dulu, baru listing diupload; berkas `SKU_Gudang...` (SKU yang ada) dan `SKU_Match...` (pemetaan); impor dipecah SIAP IMPOR / TUNDA (model belum berformula); klasifikasi baris BLANK / NOT6PART / BADGEN / OK; audit 7.629 baris belum sesuai (per 6 Agu) | `project-undercover-bigseller-sync` |
| **Stock Sync** (mulai 17 Jul) | Sinkron kuantitas stok listing dari `Stock_Opname.xlsx` | Beda dari SKU Sync; batch pertama warna Abu-abu Reguler; layout Stock Opname berubah (kolom STOK 4+3k) | `project-undercover-stock-sync-status` |
| **Sistem stok Google Sheet** (Okt) | Apps Script STOK/IN/OUT untuk "Stok Cover UC" dan "Stok Cover STP" | Trigger installable (bukan `onEdit`), sheet lama diganti nama "(lama)", Log Stok, zona waktu WIB | `project-undercover-sistem-stok-gsheet`, `sistem-stok-PANDUAN`; kode `Undercover-Repo\sistem-stok-gsheet\` |
| **Harga dan HPP** | Matriks harga per tipe bodi; harga baru per toko; HPP per model | HPP per toko: UA dan OT memakai file HPP UC, SP dan OP memakai Google Sheet "HPP STP OTP"; Exclusive/Premium/Custom tanpa HPP | `project-undercover-harga-referensi`, `hpp-per-merk-README`; skrip `Undercover-Repo\hpp-per-merk-scripts\` |
| **Analisa penjualan (Mobil Terlaris)** | Ranking produk per SKU, ±201 unit/hari | Ranking resmi: `G:\My Drive\E-commerce\RANKING TOP 100 PER SKU.xlsx`; mobil kembar berbagi satu kode | `project-undercover-analisa-penjualan` |
| **Dashboard penjualan dan iklan** | Satu file HTML untuk meeting bulanan (artifact claude.ai) | BigSeller read-only; Pendapatan Kotor satu-satunya omzet; artifact meeting v13 dikunci, arsip v3 beku; jangan menulis "ralat/revisi" di tampilan atasan; angka bulan lalu bergeser = laporkan selisih, tunggu keputusan; tiap tanggal 1 catat poin penalti | `project-undercover-dashboard`, `dashboard-README`, `bigseller-dashboard-refresh`, `manual-export-to-dashboard-mapping`; sumber `G:\My Drive\E-commerce\Undercover-Dashboard\dashboard-src\` |
| **Margin** | Income marketplace vs HPP, setelah iklan; dashboard React; kapasitas diskon | Dasar income per tanggal cair (pesanan belum cair = estimasi); biaya isi saldo otomatis bukan biaya Shopee; skrip di folder kerja | `project-undercover-margin`; skrip `Documents\Undercover\tools\` (belum di git) |
| **Archive ke 100 terlaris** (Nov) | Rampingkan listing OP ke 100 SKU terlaris seperti SP/UA | Lihat `workflow-archive-top100.md` | `project-undercover-archive-op-2026-11` |
| **Foto produk ke marketplace** (Nov, Smartprotection) | Ganti foto lewat mass update Shopee/Lazada/TikTok | Caption gambar dicek, hosting Postimg (Direct link), batch kecil, baris berurutan; lihat `workflow-foto-marketplace.md` | `project-undercover-foto-smartprotection-marketplace`, `feedback-undercover-foto-marketplace-lessons` |
| **Shopee Price Monitor** | Pantau harga kompetitor | Scraping langsung diblok; pakai Apify actor; backend terisolasi di `ShopeeScraper` | `project-undercover-shopee-antibot`; kode `Export Undercover ke Akun Claude Lain\` |
| **Audit foto produk** | Audit sampul belum branding (selesai 6 Jul) | Deteksi lewat dimensi foto tidak 100% andal | `project-undercover-photo-shopee-audit` |
| **Memory/vault** | Vault Obsidian = memory utama; sinkron memory e-commerce ke GitHub | ingest/query/lint, `log.md`, folder sumber tetap `Documents\Undercover Sumber`; hanya `project-/feedback-/user-undercover-*` ikut ke repo | `CLAUDE.md` vault; skrip `sync-vault-memory.ps1`, `lint-vault.ps1` |

## Pola lintas sub-project
- Sumber kebenaran: master SKU, file Total Formula, ranking top-100, file HPP; export marketplace hanyalah keadaan saat itu.
- Setiap pekerjaan berakhir dengan: file hasil di folder baru, verifikasi, catatan vault (+ `log.md`), pelajaran di skill ini.
- Akun/browser: GitHub dan BigSeller hanya lewat sesi login user (Claude in Chrome atau browser bawaan); tidak pernah memasukkan password.
