# Lanjutan SKU Sync — UA TikTok (status per 2026-07-15 sore)

Catatan handoff supaya bisa dilanjut di device lain (rumah). Baca juga
`claude-memory/project-undercover-sku-sync-status.md` bagian paling bawah
(tanggal 2026-07-15) untuk konteks penuh.

## Di mana kita sekarang

Tugas: isi SKU baris kosong di **UA TikTok** (`Tiktok Semua Informasi
Undercover 1.xlsx`), scope **331 terlaris**, patokan varian dari file
e-commerce Undercover (kalau master tidak match → master ikut e-commerce).

Keputusan user 2026-07-15: **perbaiki master DULU**, baru isi TikTok.

## Yang sudah selesai hari ini

- Master `SKU, Price, Tracking Cover Mobil.xlsx` (di `Update via Claude/`)
  sudah: restorasi 98 baris (Mercedes EQE/G-Class-Strip + Suzuki Carry-Strip)
  + merge 26 baris Lexus Orange. Size 3.464.735 byte. Ada di lokal + Drive.
- 15 file operasional "SYNCED" dari sesi cloud sudah ditaruh di
  `Update via Claude/List Produk {Brand}/` + Drive.
- Cross-check restorasi selesai (lihat memory).

## Temuan penting (kenapa "perbaiki master dulu")

Master & listing toko TIDAK selalu match. Contoh:
- **Daihatsu Terios**: master cuma py Gen 1 (1997-2006); listing jual
  "Gen 2-3 (2006-2026)" → SKU `DHT-TRS-UA-R-G2-ABU` yg TIDAK ada di master.
- **Toyota Hardtop**: master pakai kode `J40`, listing pakai `G4`.

Jadi banyak baris TikTok blank tidak bisa diisi karena master-nya belum
lengkap/beda. Perlu lengkapi master (ikut listing e-commerce) dulu.

## Rencana lanjutan (langkah konkret)

1. **Gap analysis**: dari SEMUA baris UA yg SUDAH terisi (TikTok+Shopee+Lazada),
   ekstrak kombinasi `(model, kategori, generasi, warna) -> SKU + tahun` yang
   BELUM ada di master. Itu daftar yg perlu ditambahkan ke master.
   (Belum dijalankan — script gap-analysis belum dibuat.)
2. **Review daftar gap** bareng user (ada risiko listing lama stale — cek
   silang ke master aktual, spt kasus Terios/Hardtop).
3. **Tambahkan ke master** yg sudah disetujui.
4. **Baru isi UA TikTok blank** pakai `engine.py` (master-based match).

## engine.py — mesin pencocokan (sudah jalan, validasi 78%)

- Parse nama listing → model + tier; parse variation_value → kategori+warna+gen.
- Match ke master UA lookup `(model, kat, warna) -> [gen candidates]`.
- **PENTING sebelum dipakai untuk WRITE:**
  - Ganti path `UPD`/`BASE` di atas file sesuai device ini (sekarang
    hardcoded ke `C:\Users\OWNER\...`).
  - **EXCLUDE varian catch-all** "Model/Tahun Lain" & "Tahun Lain" — HARUS
    tetap kosong (jangan diisi). Versi sekarang masih keliru mengisinya via
    fallback "single" — perbaiki dulu.
  - Sadar sebagian "mismatch" di validasi = data listing lama yg stale
    (bukan bug engine) — cek ke master aktual dulu.
- Belum ada penulisan apa pun ke file (masih validasi/dry-run).

## Cadangan / rollback

Semua file master di `Update via Claude/` punya backup `.bak_TIMESTAMP`
(restorasi, lexus merge, dll). File operasional juga di-backup sebelum ditimpa.
