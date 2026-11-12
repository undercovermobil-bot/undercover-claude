# Alur: archive toko ke 100 SKU terlaris

Contoh pertama: Otoprotection (OP), 11-12 Nov 2026. Smartpro dan Undercover sudah dirampingkan sebelumnya (jadi pembanding).
Catatan lengkap: vault `project-undercover-archive-op-2026-11`.

## Input yang dibutuhkan dari user
- TikTok: semua halaman `Tiktoksellercenter_batchedit_<tgl>_all_information_template[_N].xlsx` toko tersebut.
- Shopee: `mass_update_basic_info_<idToko>_*.xlsx` (nama) **dan** export "Info Penjualan" (varian + SKU; bisa dipecah `1.xlsx`, `2.xlsx`).
- Acuan: `G:\My Drive\E-commerce\RANKING TOP 100 PER SKU.xlsx` (lihat `sku-rules.md`).
- Opsional pembanding: export live Smartpro/Undercover (di Downloads) untuk melihat model apa yang tersisa setelah mereka diarchive.

## Langkah
1. **Definisikan top-100**: peringkat <= 100 di "Peringkat Lengkap" (alias `SZK-VITARA` = `SZK-GVT`). Model = 2 segmen pertama SKU.
2. **Klasifikasi per PRODUK** (archive berlaku per listing, bukan per varian): dipertahankan bila minimal satu SKU variannya model top-100;
   di-archive bila tidak. Listing campuran (mis. Hilux `HLR/HLX`, HiAce `HAC/HAL`, Grand Vitara) dipertahankan utuh karena rencana
   memang menyatukannya.
3. **Produk tanpa SKU**: putuskan lewat nama terhadap sheet "Daftar Mobil Listing UA" / "Peringkat Lengkap". Yang masuk top-100 dipertahankan dan SKU-nya diisi
   (alur `workflow-fill-blank-sku.md`); yang tidak, di-archive. Tampilkan daftarnya ke user.
4. **Model "kembar" di luar top-100** (kode terpisah, peringkat > 100: Avega Hatchback, Feroza Long, Mazda 2 Sedan, Aerio Sedan, Mazda 3, BMW M3) **ikut di-archive**
   (keputusan user; SP dan UA juga hanya menyisakan versi utamanya).
5. **Bandingkan dengan toko yang sudah dirampingkan** (export live SP/UA): jumlah produk dan set model harus sebanding (OP: 219 Shopee / 218 TikTok = SP).
   Perbedaan nama listing (SP: "Signature Waterproof", "Transparan Anti Air") dinormalkan dulu sebelum membandingkan.
6. **Buat file archive**: hanya kolom nama berubah menjadi `nama lama + " (Archive)"` (TikTok kolom C, Shopee basic info kolom C); baris lain dan sel lain identik.
   Pakai edit XML mentah (`marketplace-files.md`).
7. **Verifikasi**: `py -3 -I scripts/verify_archive_top100.py --ranking ... --tiktok ASLI ARCHIVE [--tiktok ...] --shopee ASLI ARCHIVE --sales INFO1 INFO2`.
   Harus: [A]=0, [B]=0, format nama 0 salah, sel lain berbeda 0; [C] (SKU kosong pada produk dipertahankan) ditindaklanjuti.
8. **Serahkan** dengan daftar file siap upload dan kekurangannya (toko lain, SKU gudang, master, keputusan kode yang tertunda).

## Urutan upload dan penghapusan
- TikTok: file `_ARCHIVE` dulu, baru file SKU. Shopee: basic info (rename) dan Info Penjualan (SKU) tidak saling bergantung.
- Setelah rename: hapus produk bertanda "(Archive)" lewat UI marketplace (manual oleh user).
- Cek export hari-H: nama produk harus sama dengan saat file archive dibuat dan belum ada "(Archive)".

## Jebakan yang sudah terjadi
- "100 SKU" = 100 grup kode, bukan 100 nama mobil (sekitar 110 nama di sheet UA).
- Daftar stok `daftar-urutan.js` tidak memuat Land Cruiser (peringkat 51) padahal top-100: jangan dipakai sebagai acuan archive.
- `RINGKASAN` buatan sesi lain boleh dipakai sebagai petunjuk, tetapi **verifikasi ulang** dari file asli.
- SKU Land Cruiser satu untuk semua generasi itu benar (Total Formula = 1), hanya kodenya `J60` (format lama) yang belum `G1`.

## Setelah upload Shopee: baca file Result dan ulangi yang gagal
1. File `Result_...` hanya memuat baris gagal. Hitung: gagal yang namanya berakhiran "(Archive)" = perlu diulang; sisanya (produk tidak berubah) abaikan.
2. `py -3 -I scripts/shopee_retry_failed.py --archive <file archive> --result <Result> --out <retry.xlsx>`: baris berurutan dari 7, karakter ditolak dibuang dari deskripsi.
3. Setelah semua diupload, minta export basic info terbaru dan jalankan `verify_archive_top100.py` (file asli = export sebelum archive; file archive = export terbaru)
   untuk memastikan jumlah produk "(Archive)" = jumlah yang direncanakan. Contoh OP 12 Nov: 264 direncanakan, 174 berhasil, 90 gagal karena `➤`/`✔`.
