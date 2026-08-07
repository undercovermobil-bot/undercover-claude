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
4. **Varian generik** ("Tahun Lain"/"Model Lain"/"Custom") — **DIREVISI user 2026-08-07**: kalau model itu **Total Formula = 1**, varian generik **TETAP DIISI** kode SKU-nya (tidak ambigu, cuma ada satu kemungkinan). Kalau **Total Formula > 1**, baru **dikosongkan** — jangan ditebak generasi mana yang dimaksud. ~~(versi lama: selalu dikosongkan walau single-generasi)~~
5. **Stok warna Abu-abu pada Reguler & tier-1 (Strip1/Elite/S1A/EAB) = 0** — aturan gudang, berlaku ke SELURUH katalog. Filter berbasis kode SKU gampang jebol karena 2 skema tier pakai kode beda (S1A/S2A/S3A di SP/OP vs EAB/PAB/WAB di UA/OT) — selalu cross-check ke teks varian asli, jangan cuma pola kode.
6. **Produk luar-scope** (Karpet Mobil, Cover Motor CM####, Travel Pouch TikTok3-Undercover) HARUS dikecualikan dari pencocokan model, atau judul yang kebetulan menyebut nama mobil ikut ke-match salah.
7. **Master TIDAK dedupe baris Toko** — tetap 4 baris terpisah per model meski kode SKU sama antar pasangan (poin 1); kolom teks "Toko" tidak dihapus.

Why: aturan-aturan ini masing-masing hasil dari koreksi eksplisit user, bukan desain awal — sudah beberapa kali dibolak-balik sebelum ketemu bentuk final ini (terutama aturan #2). Mengubahnya lagi tanpa instruksi baru berisiko mengulang siklus revisi yang sama.

How to apply: kalau butuh evidence "SKU ini beneran real/terpakai" (bukan cuma valid-secara-teori di master), selalu cross-check ke data operasional riil (file `Hasil Sinkronisasi SKU/`, export BigSeller), jangan asumsikan "valid di master" = "aman dipakai tim ops" — lihat [[project-undercover-sku-sync-status]] untuk contoh (deliverable 100 Mobil Terlaris).

## Revisi aturan tambahan (2026-08-05 & 2026-08-07)

- **Hyundai Santa Fe → 2 formula** (user 2026-08-05): `G1` = Gen 1/2/3, `G2` = Gen 4/4F/5. Listing UA sudah diupdate & diupload; **MASTER masih 1 formula (semua G1) — user konfirmasi 08-07 master perlu diupdate.** Jangan "perbaiki" listing ke master untuk model ini.
- **Mazda 3 → kode model per bodystyle** (user 2026-08-05): `-3S-` sedan, `-3H-` hatchback. Berlaku SEMUA toko. Master sudah punya entri `Mazda 3 Sedan`(MZD-3S) & `Mazda 3 Hatchback`(MZD-3H), plus legacy `Mazda 3`(MZD-M3) yang harus ditinggalkan.
- **Hyundai Stargazer → 2 formula** (user 2026-08-07): Gen 1 (2022-2024) dan Gen 2 (2025-2026) dipisah. Gen 1 sudah pakai `HYN-SGZ-UA-R-G1-*`; **Gen 2 belum punya SKU baru di SEMUA toko** (148 baris: UA Shopee masih `CVR0033-UC-RPA`/kosong, UA TikTok kosong, UA Lazada format lama, OT/SP/OP kosong atau format lama). Master juga belum punya Gen 2.

**Catatan penting soal segmen generasi**: nomor `G#` **mengikuti nomor generasi asli mobil, bukan indeks grup** — grup berbagi kode dari generasi terendah di grup itu. Contoh tervalidasi Toyota Corolla (TF=9, listing UA sudah 100% benar): Gen 1&2→`G1`, Gen 3→`G3`, Gen 4→`G4`, Gen 5→`G5`, Gen 6→`G6`, Gen 7→`G7`, Gen 8→`G8`, Gen 9&10&12→`G9`, Gen 11→`G11`. Santa Fe (G1/G2) adalah **pengecualian eksplisit dari user**, bukan pola umum — jangan digeneralisasi.
