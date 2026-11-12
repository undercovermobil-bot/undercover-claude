---
name: undercover-ecommerce-ops
description: Alur kerja dan aturan untuk SELURUH project e-commerce Undercover Autocare Group (toko UA/OT/OP/SP; Shopee, TikTok, Lazada; BigSeller) - SKU sync dan Total Formula, isi/cek SKU, archive ke 100 SKU terlaris, file mass-upload Shopee/TikTok, SKU gudang, stok, harga/HPP, margin, dashboard penjualan dan iklan. Pakai untuk tugas apa pun tentang katalog, listing, SKU, stok, harga, ranking, BigSeller, atau file export marketplace, dan saat user meminta file siap upload.
---

# Undercover e-commerce ops

Skill ini berlaku untuk **semua sub-project e-commerce** (peta di `references/project-map.md`) dan menyimpan **alur kerja**
yang sudah terbukti. Aturan bisnis resmi dan status proyek ada di vault Obsidian
(`C:\Users\OWNER\Documents\Undercover Claude`, mulai dari `00 Home.md`); kalau skill dan vault berbeda, **vault menang**,
lalu perbarui skill ini. Balas dalam Bahasa Indonesia.

## Konteks singkat
- 4 toko: Undercover Autocare (UA), Otonation (OT), Otoprotection (OP), Smartprotection (SP). Kode SKU: OT=UA, OP=SP.
- Lokasi: vault (catatan/memory), `Documents\Undercover-Repo` (skrip, git), `G:\My Drive\E-commerce` (master, ranking, data),
  `Documents\Undercover` (folder kerja data/skrip analisa), `Downloads` (export marketplace dan file hasil).
- Export marketplace datang dari user (biasanya di `Downloads`): **cari sendiri** file yang dimaksud (Glob, cek timestamp).

## Prinsip lintas-project (tidak boleh dilanggar)
1. **Jangan timpa file asli.** Hasil ke folder baru `Downloads\<Toko> <Tugas> <YYYY-MM-DD>\` (atau `out\` di folder kerja).
2. **File mass-upload hanya berisi baris yang berubah**, dan hanya kolom yang dimaksud (buktikan dengan perbandingan sel per sel). Nomor baris data harus **berurutan** dari baris data pertama (baris bolong = 0 diproses; `scripts/compact_rows.py`).
3. Template membawa kolom **harga** (TikTok, Shopee) dan **stok** (Shopee Info Penjualan): upload di hari export, atau pastikan tidak ada perubahan.
4. **BigSeller read-only**: hanya membaca; tidak menulis, mengekspor, mengunduh, atau mengubah pengaturan. Satu-satunya angka omzet = Pendapatan Kotor sisi penjual.
5. **Verifikasi sebelum menyerahkan** dan laporkan apa adanya, termasuk yang belum dicek. Jangan menyimpulkan "SKU salah" sebelum membuka file Total Formula dan master; kalau keliru, cabut terang-terangan.
6. Jangan mengubah SKU listing yang SKU gudang BigSeller-nya belum ada (pemetaan stok putus).
7. Pertanyaan spot-check user sering membuka masalah sistemik: jawab satu per satu, periksa datanya, jangan menebak.
8. Simpan hasil dan keputusan ke vault (ingest: catatan project, `log.md`, tautan di `00 Home`); catat pelajaran di skill ini.
9. Hemat token: batasi daftar yang dicetak, baca catatan besar sebagian (cari kata kunci dulu), satu sesi per pekerjaan.

## Pilih alur
| Permintaan | Baca |
|---|---|
| Peta semua sub-project, aturan khas tiap sub-project, di mana kodenya | `references/project-map.md` |
| Archive produk toko ke 100 SKU terlaris, cek daftar archive | `references/workflow-archive-top100.md` |
| Isi SKU kosong / buat SKU, siapkan file SKU siap upload | `references/workflow-fill-blank-sku.md` |
| Ganti foto produk lewat mass update (hosting, batch, verifikasi) | `references/workflow-foto-marketplace.md` |
| Aturan SKU, warna, tier, Total Formula, kode format lama, acuan top-100 | `references/sku-rules.md` |
| Tata letak file Shopee/TikTok, kolom, jebakan membaca/menulis xlsx, urutan upload | `references/marketplace-files.md` |
| Pelajaran dan keputusan user yang sudah pernah terjadi | `references/lessons-learned.md` |

## Daftar verifikasi file hasil (wajib)
- Jumlah baris/produk cocok dengan ringkasan yang akan dilaporkan.
- Sel yang berbeda dari file asli = hanya kolom yang dimaksud (nama atau SKU); id produk/variasi/sku_id utuh; header identik
  (baris 1-5 TikTok, 1-6 Shopee).
- Hanya sel yang awalnya kosong yang diisi (pengisian SKU); SKU baru unik kecuali memang satu formula.
- Cocokkan dengan sumber lain: toko saudara (OP=SP), channel lain (Shopee vs TikTok), master, export live toko lain.
- Buka ulang file hasil dengan `scripts/xlsx_zip.py` untuk memastikan terbaca.

## Skrip
- `scripts/xlsx_zip.py`: pembaca xlsx berbasis zip+XML (openpyxl gagal pada export Shopee). Hanya baca.
- `scripts/verify_archive_top100.py`: integritas file archive + cek terhadap ranking top-100 + produk dengan SKU kosong.
- `scripts/compact_rows.py`: rapatkan nomor baris data (wajib untuk file yang hanya berisi sebagian produk).
- `scripts/shopee_retry_failed.py`: file ulang untuk produk yang gagal pada mass update basic info Shopee (membuang karakter yang ditolak).
- Di repo `C:\Users\OWNER\Documents\Undercover-Repo\scripts\`: `isi_sku_kosong_tiktok_sp.py` (TikTok) dan
  `isi_sku_kosong_shopee_op.py` (Shopee Info Penjualan); edit tabel `TARGET` untuk produk lain. Skrip sub-project lain dicatat di
  `references/project-map.md`.
- Jalankan Python dengan `py -3 -I` (tanpa pandas; tidak ada LibreOffice).

## Bagaimana skill ini berkembang
Setelah setiap pekerjaan e-commerce:
1. Tambahkan entri bertanggal di `references/lessons-learned.md` (yang dipelajari, jebakan, koreksi, keputusan user).
2. Kalau aturan/format/sub-project berubah, perbarui referensi yang relevan (`project-map.md` untuk sub-project baru) dan catat di Changelog.
3. Skrip baru yang bisa dipakai ulang disimpan di `scripts/` (atau repo) dan didaftarkan di bagian Skrip.
4. Aturan bisnis yang berubah dicatat juga di vault (`10 Projects/Undercover/...`) dan `log.md` vault.
5. Jaga SKILL.md singkat; rincian masuk ke `references/`.

**Sinkron ke GitHub (repo e-commerce):** salinan skill ada di `Undercover-Repo\.claude\skills\undercover-ecommerce-ops\`
(terbaca otomatis oleh sesi cloud yang meng-clone repo). `scripts\sync-skill.ps1` menyinkronkan dua arah: dipanggil auto-commit
15:45 dan saat sesi vault dimulai. Edit di mana pun boleh; bila dua sisi berubah, versi lokal dipertahankan dan versi repo ditaruh di
`_conflicts\` untuk digabung manual. Skill ini hanya untuk repo e-commerce (bukan repo Digital Marketing).

## Changelog
- 2026-11-12: dibuat dari pekerjaan archive Otoprotection (Shopee + TikTok), pengisian SKU MG S5 EV / Santa Fe / Smartpro, dan verifikasi terhadap ranking top-100; diperluas ke seluruh project e-commerce (peta sub-project); alur foto marketplace ditambahkan dari catatan sesi lain.
