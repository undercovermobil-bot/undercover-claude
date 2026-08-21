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

## Mazda 2 → kode model per bodystyle (user 2026-08-07, sama pola dengan Mazda 3)

**Hatchback** → `-2H-`, **Sedan** → `-2S-`. Berlaku SEMUA toko (instruksi eksplisit user: "simpan memory ini untuk nanti di toko lain juga"). Bukan perubahan Total-Formula, cuma kode-nama model — persis pola Mazda 3 (`-3S-`/`-3H-`).

Status saat ditemukan (UA, master): Sedan **sudah benar** (`MZD-2S`), Hatchback **masih kode lama** `MZD-MZ2` — konversi cuma ganti segmen model (segmen 2), segmen lain (kategori/generasi/warna) tetap sama persis. Pola cek untuk toko lain: kalau listing masih `MZD-MZ2-...`, itu Hatchback yang belum dikonversi.

**Pola umum yang mulai terlihat**: Mazda sepertinya menomori bodystyle dengan kode `{angka}{S|H}` (3→3S/3H, 2→2S/2H). Kalau ketemu Mazda model lain dengan bodystyle ganda di toko lain, cek dulu ke user sebelum menyamaratakan pola ini — jangan diasumsikan otomatis berlaku ke semua model Mazda.

## Aturan baru 2026-08-12: model "kembar" pakai kode SKU model dasar (bukan kode sendiri)

Instruksi user (berlaku SEMUA toko, formula produk sama krn kembar/rebadge): twin (kiri) adopsi kode SKU dasar (kanan), kategori+warna tetap normal, hanya segmen model (dan kadang generasi) yg ganti.

| Twin | Dasar | Kode dasar | Catatan generasi |
|---|---|---|---|
| Daihatsu Xenia | Toyota Avanza | TYT-AVZ | **per-gen**: Xenia gen1&2->G1, Xenia gen3->G3 (ikut skema Avanza sendiri: G1=gen1&2, G3=gen3 -- Avanza TIDAK py G2, loncat G1->G3) |
| Toyota Veloz | Toyota Avanza | TYT-AVZ | SEMUA gen Veloz -> G3 (Veloz = branding gen-3 Avanza) |
| Daihatsu Sigra | Toyota Calya | TYT-CLY | TF=1, semua->G1 |
| Daihatsu Terios | Toyota Rush | TYT-RSH | TF=1, semua->G1 |
| Toyota Raize | Daihatsu Rocky | DHT-RCK | TF=1, semua->G1 |
| Toyota Alphard | Toyota Vellfire | TYT-VLF | TF=1, semua->G1 |
| Daihatsu Ayla | Toyota Agya | TYT-AGY | TF=1, semua->G1 |

**Arah pasangan dikonfirmasi dari rank top-215** (bukan cuma tebak dari urutan kalimat user): base selalu rank lebih tinggi KECUALI Raize(#27) vs Rocky(#60) dan Alphard(#53) vs Vellfire(#62) — di 2 pasang itu yg secara rank lebih populer (Raize, Alphard) malah jadi TWIN, bukan base. Jangan asumsikan "yg lebih laku = base" utk model baru yg mirip pola ini — pola user based on urutan kalimat "X = Y" (X adopsi Y), bukan rank.

**Jebakan penting**: awalnya salah paksa Xenia SEMUA gen ke G1 (termasuk baris "Xenia Gen 3 (2021-2026)" yg ada di listing nyata) — user instruksinya eksplisit "begitupun gen berikutnya" = per-generasi, BUKAN blanket. Fix: cek angka gen dari teks varian, gen>=3 -> G3, selain itu G1.

**Bug data ditemukan (bukan bug proyek, murni human error listing)**: produk TikTok "...Toyota Agya Reguler" py current SKU `DHT-AYL-...` (kode Ayla, ketuker), 30 baris. Otomatis kebenerin oleh proses konsolidasi ini juga (karena Ayla->Agya = kode sama persis), tapi dicatat sbg bukti listing memang sering keliru tempel SKU model lain.

**Status UA (source fresh 2026-08-12, hanya UA)**: Shopee 0 (sudah benar semua -- ternyata sebagian sdh dikerjakan manual/sesi lain sebelum diminta), TikTok 211 baris/17 produk, Lazada 48 baris. File: `Cek gagal upload/UA/Upload {TikTok|Lazada} UA - Twin Model (2026-08-12).xlsx`.

**BELUM dikerjakan**: OT/SP/OP (user minta "di semua toko" tapi source yg dikirim 08-12 cuma UA) -- perlu listing fresh OT/SP/OP baru sebelum bisa diterapkan ke situ.

## Mitsubishi Colt T120SS Pick Up (2026-08-21) — model baru, kode MTB-CT1

Tak ada di master sama sekali. Ikut pola Mitsubishi L300 Pickup (model pickup klasik sejenis, TF=1, cuma Reguler(5 warna)+Strip(9), tanpa Premium/Exclusive/Transparan) sbg template. Kode `CT1` (Colt T1-series), bukan singkatan literal T120SS krn sudah ada pola L300→`LP` (singkat, bukan literal).
