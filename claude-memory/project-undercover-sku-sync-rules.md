---
name: project-undercover-sku-sync-rules
description: "Format SKU, kosakata tier/toko, dan 7 aturan bisnis final untuk SKU Sync — jangan didesain ulang tanpa instruksi eksplisit"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

**Format & kosakata dasar**: sumber kebenaran = master `SKU, Price, Tracking Cover Mobil.xlsx` (1 sheet per merek mobil, 64 sheet). Format SKU: `MEREK-MODEL-TOKO-KAT-GEN-WARNA`. Kategori: Reguler/Premium/Exclusive. Tier warna Strip1/2/3 (kode SP/OP) = Elite/Epic/Warrior (istilah UA/OT) — 2 skema penamaan, tier konsep sama, jangan tertukar. Warna sel status di semua file hasil: hijau=benar, biru=diisi dari kosong, oranye=migrasi/auto-koreksi/konsolidasi, merah=perlu cek manual.

**7 aturan bisnis final** (sudah divalidasi berkali-kali dengan user, jangan didesain ulang tanpa instruksi eksplisit baru):

1. **Konsolidasi toko**: stok fisik OT=UA, OP=SP. `TARGET_STORE = {UA:UA, OT:UA, OP:SP, SP:SP}`. Sejak 2026-07-08 di-bake langsung ke MASTER (bukan cuma saat build listing) — akibatnya persentase "SKU duplikat" di master melonjak ke ~98,5% baris by design; exclude pasangan UA↔OT dan SP↔OP dari hitungan "duplikat genuine".
2. **Judul BigSeller/SKU Gudang**: prioritas dari Nama Produk listing ASLI toko (Undercover→fallback Otonation untuk kode UA; Smartprotection→fallback Otoprotection untuk kode SP), fallback terakhir "Nama Produk Bigseller" master. Final setelah 3x dibolak-balik user.
3. **SKU Gudang baru** hanya kode UA & SP (skip OT/OP) — konsisten kebijakan konsolidasi.
4. **Varian generik** ("Tahun Lain"/"Model Lain"/"Custom") → SKU dikosongkan, jangan ditebak, walau model single-generasi.
5. **Stok warna Abu-abu pada Reguler & tier-1 (Strip1/Elite/S1A/EAB) = 0** — aturan gudang, berlaku ke SELURUH katalog. Filter berbasis kode SKU gampang jebol karena 2 skema tier pakai kode beda (S1A/S2A/S3A di SP/OP vs EAB/PAB/WAB di UA/OT) — selalu cross-check ke teks varian asli, jangan cuma pola kode.
6. **Produk luar-scope** (Karpet Mobil, Cover Motor CM####, Travel Pouch TikTok3-Undercover) HARUS dikecualikan dari pencocokan model, atau judul yang kebetulan menyebut nama mobil ikut ke-match salah.
7. **Master TIDAK dedupe baris Toko** — tetap 4 baris terpisah per model meski kode SKU sama antar pasangan (poin 1); kolom teks "Toko" tidak dihapus.

Why: aturan-aturan ini masing-masing hasil dari koreksi eksplisit user, bukan desain awal — sudah beberapa kali dibolak-balik sebelum ketemu bentuk final ini (terutama aturan #2). Mengubahnya lagi tanpa instruksi baru berisiko mengulang siklus revisi yang sama.

**(2026-08-09) ⚠️ ATURAN #4 SUDAH DIREVISI — temuan dari scan Drive, bukan instruksi langsung di sesi ini.** File `CATATAN UA - perlu keputusan (2026-08-07) rev2.xlsx` menunjukkan varian catch-all ("Model/Tahun Lain"/"Model Lain/Custom") pada model BERGENERASI TUNGGAL sekarang **DIISI** SKU-nya lewat "formula tunggal" — bukan dikosongkan lagi. Sudah dieksekusi untuk banyak baris Undercover Autocare (contoh: BMW M2/M3 Lazada). Detail & yang belum diverifikasi (scope revisi: cuma model 1-generasi atau lebih luas; sudah berlaku di toko lain atau baru UA) ada di [[project-undercover-sku-sync-status]] entri 2026-08-09. **Jangan asumsikan aturan #4 versi lama di atas masih berlaku** — cross-check ke listing terbaru sebelum pakai aturan lama sbg acuan.

How to apply: kalau butuh evidence "SKU ini beneran real/terpakai" (bukan cuma valid-secara-teori di master), selalu cross-check ke data operasional riil (file `Hasil Sinkronisasi SKU/`, export BigSeller), jangan asumsikan "valid di master" = "aman dipakai tim ops" — lihat [[project-undercover-sku-sync-status]] untuk contoh (deliverable 100 Mobil Terlaris).
