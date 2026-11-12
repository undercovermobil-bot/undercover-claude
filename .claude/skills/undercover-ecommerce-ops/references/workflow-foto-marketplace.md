# Alur: ganti foto produk lewat mass update marketplace

Ringkasan dari vault (`feedback-undercover-foto-marketplace-lessons`, `project-undercover-foto-smartprotection-marketplace`, sesi 5 Nov 2026,
Smartprotection). Baca catatan vault itu untuk detail dan angka lengkap.

## Sebelum membuat link
- Periksa **tulisan di dalam gambar**, bukan hanya nama file: caption seri + warna (Epic/Elite/Warrior) sering bergeser, nama model salah ketik,
  warna foto tidak cocok caption. Cocokkan ejaan model dengan katalog marketplace; cek nama file ganda antar folder.
- File kembar (hash sama) boleh; hosting menggabungkannya jadi satu link.

## Hosting gambar
- TikTok menolak `i.ibb.co`; Postimg diterima (cadangan `i.ibb.co.com`). Ambil **Direct link** Postimg (bukan `src` thumbnail di galeri; thumbnail ditolak TikTok: min. 300x300).
- Unggah lewat Claude in Chrome: maks 10 MB per panggilan (±15 gambar per batch).
- Shopee: unggah 20 produk sekaligus gagal; pecah 4-6 produk per batch. Lazada: gagal per produk bila satu gambar gagal diunduh; unggah ulang hanya produk itu.

## Struktur file
- Baris bolong = 0 diproses: susun baris berurutan dari baris data pertama (Shopee 7, Lazada 5, TikTok 6).
- Perubahan SKU induk lewat mass update media diabaikan Shopee. Kunci pencocokan: Product ID (atau `sku.skuId` Lazada), bukan nomor baris.
- Edit dengan tambal XML (lihat `marketplace-files.md`), jangan `openpyxl.save`.

## Verifikasi
- Setelah upload, bandingkan foto di platform dengan file sumber (server lokal + built-in browser + canvas CORS, ±1.200 gambar/menit); jangan mengandalkan screenshot.
- Hasil upload (file hasil marketplace) diperiksa per produk; ulangi hanya yang gagal.
