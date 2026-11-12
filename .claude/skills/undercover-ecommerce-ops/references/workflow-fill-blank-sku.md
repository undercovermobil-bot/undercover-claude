# Alur: isi SKU kosong / buat SKU, siapkan file siap upload

Dipakai untuk produk yang SKU variannya kosong (mis. MG S5 EV, Corolla Gen 1-4 Smartpro, Mini Cooper Transparan, Taft GT, Santa Fe Transparan).

## Langkah
1. **Temukan yang kosong** di export (TikTok `seller_sku` kolom K; Shopee Info Penjualan kolom F). `verify_archive_top100.py` bagian [C] mendaftarkannya untuk produk yang dipertahankan.
   Cek juga toko saudara dan channel lain: kasus yang sama sering ada di Smartpro dan di Shopee dan TikTok sekaligus.
2. **Pastikan layak diisi**: produk top-100 (ranking) dan bukan varian generik ("Tahun Lain", "Model Lain", "Custom" dibiarkan kosong).
3. **Turunkan aturan dari data yang sudah ada**, bukan dari ingatan: kumpulkan pasangan label varian -> akhiran SKU dari SKU yang sudah terisi di file yang sama
   (warna, strip), dan pastikan **bulat 100%** (satu label = satu akhiran). Lihat tabel di `sku-rules.md`.
4. **Tentukan kode generasi lewat Total Formula** (`sku-rules.md`): beberapa label generasi bisa satu kode (Corolla Gen 2 = `G1`). Untuk produk yang sama di
   channel/toko lain, tiru SKU yang sudah ada (OP = SP; Shopee = TikTok); bila berbeda dari aturan formula, tandai sebagai keputusan untuk user.
5. **Buat file** dengan skrip repo (edit tabel `TARGET`):
   - TikTok: `Undercover-Repo\scripts\isi_sku_kosong_tiktok_sp.py <export.xlsx> <keluaran.xlsx>`
   - Shopee Info Penjualan: `Undercover-Repo\scripts\isi_sku_kosong_shopee_op.py <export.xlsx> <keluaran.xlsx>` (per file export)
   Skrip hanya mengisi sel yang kosong, menulis baris yang berubah saja, dan menyimpan template apa adanya.
6. **Verifikasi** (wajib, jalankan nyata):
   - sel yang berbeda dari file asli hanya kolom SKU (TikTok indeks 10, Shopee indeks 5); id produk/variasi utuh; header identik; semua yang diubah awalnya kosong;
   - himpunan SKU per kelompok sama dengan SKU toko/channel saudara (atau selisihnya dijelaskan oleh aturan formula);
   - tidak ada SKU kosong tersisa pada produk target; file terbuka dengan `xlsx_zip.py`.
7. **Serahkan** di folder baru `Downloads\<Toko> SKU <tugas> <tanggal>\`, sebutkan: jumlah baris, kode yang dipakai, asumsi, dan yang belum
   (channel lain, SKU gudang BigSeller, master). Ingatkan urutan upload dan bahwa file membawa harga/stok.

## Setelah SKU baru terisi
- SKU gudang BigSeller untuk kode baru perlu ada agar stok tersambung (kode UA dan SP saja); cek export `SKU_Gudang...`.
- Tambahkan model baru ke master SKU bila belum ada (mis. sheet MG kosong per 2026-11-12) - di salinan "Update via Claude".
- Catat di vault (catatan project, `log.md`).

## Jebakan teknis
- Produk Shopee tanpa variasi: SKU Induk legacy (`CVR####-OTP-...`) dan kolom SKU kosong; isi kolom SKU dengan SKU channel lain toko yang sama.
- Label Strip berbeda per kanal/toko: TikTok OP "Strip 1 Abu-abu", Shopee OP "Strip 1 Abu", SP/UA "Epic Abu".
- Variasi Transparan Mini Cooper berbentuk "Hatch, 3 Pintu" (sub-model + pintu), bukan warna: kodenya `3P`/`5P`.
- Edit XML: cari baris dengan `\br="N"`; sel kosong TikTok berisi shared string kosong, bukan sel hilang (resep di `marketplace-files.md`).- **TikTok: isi atribut wajib sebelum menyerahkan file** (`scripts/tiktok_isi_atribut_wajib.py <file SKU> <keluaran>`): tanpa Imported goods file SKU ditolak seluruhnya (kasus MG S5 EV OP 12 Nov; file SP #7 punya masalah yang sama).
