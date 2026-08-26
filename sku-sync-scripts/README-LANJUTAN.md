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

1. ✅ **Gap analysis SUDAH DIJALANKAN** (`gap_analysis.py`). Hasil: dari semua
   baris UA terisi (TikTok1+Shopee1-5+Lazada), ada **6.957 SKU dipakai listing
   tapi TIDAK ada di master**:
   - **610 top-331 (mobil)** ← ini yg relevan utk perbaiki master
   - 2.349 motor (di luar scope proyek cover mobil)
   - 3.998 non-top-331
   Daftar lengkap: **`Gap SKU Master - dari Listing UA (2026-07-15).xlsx`**
   (di folder `Update via Claude/`, sudah di lokal + Drive). Sheet 1 = 610
   top-331, sheet 2 = motor + non-top.
   - ⚠️ Nama model di file itu masih agak berantakan (parser prefix belum
     tangani format "Undercover Autocare - Cover Mobil {model}" — jadi 1 model
     bisa kepecah 2 grup). Data SKU-nya valid, tinggal rapikan grouping.
2. **Review 610 SKU top-331** bareng user SEBELUM ditambahkan ke master —
   ⚠️ SEBAGIAN kemungkinan data listing lama yg STALE/salah (spt Terios
   `DHT-TRS-UA-R-G2-*` padahal master cuma py Gen 1, Hardtop `G4` vs master
   `J40`). Jangan telan bulat-bulat; cek per model apakah generasi itu memang
   ada. User bilang "master ikut e-commerce" TAPI tetap perlu buang yg jelas
   error/typo.
3. **Tambahkan ke master** yg sudah disetujui (pakai openpyxl, append ke sheet
   brand yg sesuai, ikuti format kolom master: No/Nama Produk/Toko/Kategori/
   Warna/Generasi/Rentang Tahun/Nama Bigseller/SKU + kolom INPUT S/T/L/BS/ACC).
4. **Baru isi UA TikTok blank** pakai `engine.py` (master-based match) — setelah
   master lengkap, coverage engine akan naik dari ~46% dry-run sekarang.

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
