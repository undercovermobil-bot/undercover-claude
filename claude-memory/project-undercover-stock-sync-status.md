---
name: project-undercover-stock-sync-status
description: "Sub-proyek BARU (mulai 2026-07-17) — sync kolom STOK (kuantitas, bukan SKU) dari file Stock_Opname.xlsx ke listing e-commerce, dimulai dari warna Abu-abu kategori Reguler"
metadata:
  node_type: memory
  type: project
---

## Apa ini

Berbeda dari sub-proyek "SKU Sync" (yang menyamakan KODE SKU) — ini soal kolom **STOK/kuantitas** (Shopee "Stok", TikTok "Kuantitas", Lazada "Jumlah Stok") yang selama ini banyak bernilai 0 atau placeholder (misal Lazada sering default ~996-1000, bukan angka real). Sumber kebenaran stok fisik: file **`Stock_Opname.xlsx`** yang diupload user (bukan di Drive/git — file operasional, tanya user lagi kalau butuh versi terbaru), berisi banyak sheet tapi user cuma mau pakai 2: **"Stok Cover UC"** (167 baris produk) dan **"Stok Cover STP"** (93 baris produk).

## (2026-07-17) Batch pertama: warna Abu-abu, kategori Reguler saja

User eksplisit scope ke 1 warna dulu ("khusus untuk warna abu abu"). Keputusan yang dikonfirmasi user via pertanyaan (jangan diasumsikan ulang, sudah final utk batch ini):
- **Rumus stok = kolom IN saja** (BUKAN IN−OUT). Kolom OUT diabaikan total.
- **"Stok Cover UC" → Undercover Autocare (UA) + Otonation (OT)** (keduanya, konsisten dgn konsolidasi SKU UA/OT sebelumnya). **"Stok Cover STP" → Smartprotection (SP) + Otoprotection (OP)**.
- **Semua channel** (Shopee + TikTok + Lazada) utk toko yg dipilih.
- **1 angka Stock Opname (per model, tidak dipecah generasi) di-mirror ke SEMUA baris generasi** utk kombinasi (model, kategori=Reguler, warna=Abu-abu) yg sama — karena stok fisiknya memang 1 pool yg sama, bukan dipisah per generasi.
- **Sheet "Stok Cover UC" py section "STOK Reseller ASTA" mulai baris ~175** (reseller terpisah, PUNYA stok sendiri di luar stok utama) — WAJIB **exclude**, cuma pakai baris 4-170 (sebelum section itu). Ada juga section "STOK Reseller ROBY (CP)" setelahnya (baris ~208+) — otomatis ikut ter-exclude krn di luar rentang 4-170.

## Metode teknis (penting utk sesi depan)

**JANGAN re-parse nama produk/varian text seperti di SKU Sync** — jauh lebih robust pakai **SKU yang SUDAH valid** (hasil kerja SKU Sync sebelumnya) sbg kunci: baca SKU tiap baris listing, reverse-lookup ke `master_lookup_full.json`/`master_lookup_sp.json` (dapat `(model,kategori,generasi,warna)`), filter `kategori=='Reguler' and warna=='Abu-abu'` (kode SKU utk kombinasi ini SELALU match pola regex `-R-[^-]+-ABU$`, diverifikasi 0 mismatch ke seluruh master). Ini otomatis toko-agnostik (jalan sama persis utk UA/OT/OP/SP) tanpa perlu tulis parser nama-produk terpisah per toko/channel.

**Kolom per channel** (referensi cepat, sama dgn SKU Sync):
- Shopee: sheet "Sheet1", header row3, data mulai row7. SKU=kolom F(6), **Stok=kolom I(9)**.
- TikTok: sheet "Template", header row3, data mulai row6. SKU=kolom K(11), **Kuantitas=kolom J(10)**.
- Lazada: sheet "template", header row1, data mulai row5. SKU=kolom M(13), **Jumlah Stok=kolom H(8)**.

**Matching nama model Stock Opname → nama model master**: nama di Stock Opname jauh lebih singkat/tanpa brand (mis. "Grand Vitara" bukan "Suzuki Grand Vitara", "Honda Brio " bukan "Honda Brio Satya / RS") — dibutuhkan normalizer khusus (strip brand prefix, squash spasi/hubung utk tangani inkonsistensi kayak "Mazda Cx8" vs master "Mazda CX-8", "Rav 4" vs "Toyota RAV4"). **Hindari substring-matching utk core name <4 karakter** — kalau tidak, "Mazda 2" bisa nyasar match ke "BMW Seri 2"/"Geely EX2"/dll krn sama-sama mengandung karakter "2", dan "Destinator" bisa nyasar ke "Lexus ES" (substring "es" muncul di "de-**s**tinator"... eh "es" di huruf 2-3 "d**es**tinator"). Skrip matcher: `match_stock_models.py` (scratchpad).

**Model kembar/badge-engineering (1 baris Stock Opname → mirror ke 2 model master berbeda)** — dikonfirmasi masuk akal krn body/cover fisiknya identik: Toyota Agya/Daihatsu Ayla, Toyota Avanza/Daihatsu Xenia, Toyota Calya/Daihatsu Sigra, Daihatsu Terios/Toyota Rush, Toyota Raize/Daihatsu Rocky (cuma ada di sheet UC), Toyota Alphard/Toyota Vellfire. Skrip: `build_stock_targets.py` py dict `TWIN_PAIRS` hardcoded per sheet.

## Hasil batch ini

**1085 baris stok diupdate** (71 model dari UC + 41 model dari STP resolved dgn confidence tinggi), 0 error, **idempoten** (re-run kedua = 0 perubahan, konvergen), row count semua 17 file tetap sama (tidak ada baris hilang/nambah). Beberapa nilai lama Lazada yg ketimpa BUKAN 0 tapi angka ~996-1000 (pola placeholder default Lazada, bukan stok asli — expected).

**15 item DI-SKIP (butuh keputusan manual user, JANGAN ditebak)**:
- **Toyota Innova/Kijang-Innova/Zenix-Reborn split** (muncul di kedua sheet UC & STP) — Stock Opname py 2 baris terpisah utk model yg SAMA-SAMA map ke master "Toyota Innova" tunggal, tapi generasi beda (Kijang-Innova = gen lama, Zenix/Reborn = gen baru) — kontras dgn asumsi "mirror ke semua generasi", di sini justru HARUS dipecah per rentang generasi. Perlu user tentukan generasi mana masuk grup mana.
- **Mazda 2** (Hatchback vs Sedan, 2 model master beda) — 1 baris Stock Opname, mana yg dimaksud atau keduanya?
- **Suzuki APV** (Arena/Blind Van vs Luxury, 2 model beda) — sama, perlu keputusan.
- **Aerio** (Sedan vs Hatchback) — sama.
- **Honda City** (Hatchback RS vs Sedan, cuma muncul di STP) — sama.
- **Land Cruiser / Hardtop** (2 model beda, bukan kembar — cuma muncul di STP) — sama.
- **Nissan Livina** (3 model beda: Livina/Grand Livina, Livina All New, Livina X-Gear) — ambigu 3 arah.
- **Mercedes Benz Boxer** — "Boxer" bukan model Mercedes asli (itu nama van Peugeot/Citroen/Fiat), kemungkinan salah brand di Stock Opname atau memang produk lain yg belum ada di master.
- **Twincam**, **Magnum Estate** — nama tidak ketemu representasi jelas di master sama sekali (mungkin nickname/typo utk model lain).
- **"Motor" + sub-item "Sentra"/"Spin"/"Forza"** (di ekor sheet UC, baris ~168-170 & STP) — ini kategori MOTOR (motorcycle cover), BUKAN mobil — di luar scope "stok produk mobilnya" sesuai instruksi eksplisit user, sengaja tidak disentuh.

**Lazada Otonation & Lazada Otoprotection TIDAK disentuh** — bukan keputusan scope, murni krn filenya memang belum pernah ada/di-sync sesi manapun (konsisten dgn catatan lama di [[project-undercover-sku-sync-status]]).

## (2026-07-17, lanjutan sesi sama) Batch kedua: warna Abu family diperluas ke tier Strip (Elite/Epic/Warrior Abu) + default-0

User spot-check lagi: Otonation Toyota Veloz "Strip 1 Abu" (=Epic Abu) SKU `TYT-VLZ-UA-S-G1-PAB` masih stok 999 (placeholder lama). Instruksi baru: (1) cek warna "Abu" di tier Strip juga (bukan cuma Reguler), (2) **kalau kombinasi model+warna itu genuinely TIDAK ADA datanya di Stock Opname (kolom kosong utk model yg SUDAH confidently resolved), tetap set ke 0** — beda dari batch pertama yg CUMA menyentuh baris dgn nilai IN eksplisit dan MEMBIARKAN sisanya (termasuk placeholder 999/1000) apa adanya.

**Kolom Stock Opname tambahan yg dipakai** (sheet UC & STP struktur sama): Elite Abu IN=kolom 13, Epic Abu IN=kolom 19, Warrior Abu IN=kolom 25 (kode SKU suffix: Elite Abu=`-EAB`, Epic Abu=`-PAB`, Warrior Abu=`-WAB` — P utk Epic sesuai konvensi tier lama, lihat [[project-undercover-sku-sync-rules]]).

**Metode**: reuse `match_results_uc.json`/`match_results_stp.json` (hasil resolusi nama model dari batch pertama, row→kandidat model, TIDAK berubah krn independen dari kolom warna) + re-baca Stock_Opname.xlsx langsung utk 4 kolom (Abu-abu, Elite Abu, Epic Abu, Warrior Abu) per row yg sama. Utk tiap kombinasi (model resolved dgn confidence, warna), value = angka IN kalau ada, **0 kalau blank**. Model kembar (TWIN_PAIRS) & model ambigu/tidak-ketemu (15 item dari batch pertama) diperlakukan SAMA di semua 4 warna (ambigu tetap di-skip total, tidak disentuh atau di-nolkan, krn beda kasus dgn "tidak ada datanya" — ambigu itu soal KETIDAKPASTIAN cocok ke model mana, bukan soal "datanya kosong").

**Bug conflict-detection ditemukan & diperbaiki**: kalau 1 model master ternyata dituju oleh >1 baris Stock Opname berbeda (mis. "Honda Civic" dituju oleh baris "Civic Vtis"/"Civic Fb"/"Civic Estilo" — kemungkinan besar itu genuinely sub-varian/generasi Civic yg BEDA tapi Stock Opname tidak menuliskannya cukup jelas utk dibedakan oleh matcher), kode awal cuma SKIP baris yg belakangan kalau nilainya beda dari yg pertama — tapi model_value dict TETAP menyimpan nilai dari baris PERTAMA yg "menang" begitu saja (bug: harusnya kalau konflik terdeteksi, model itu JANGAN diproses sama sekali, bukan pakai nilai baris pertama). **Fix**: kumpulkan semua model yg kena conflict ke dalam 1 set, lalu `.pop()` dari `model_value` dict di akhir (baca `build_stock_targets2.py`). Ditemukan 6 model kena conflict: **Honda Civic, BYD M6, Suzuki Baleno** (sheet UC), **Nissan March, Mitsubishi Pajero Sport, Honda Civic** (sheet STP) — SEMUA warna (Reguler Abu-abu maupun Strip Abu) utk model-model ini sengaja TIDAK disentuh, perlu user cek manual model mana yg dimaksud di Stock Opname.

**Hasil batch kedua**: **1430 baris tambahan** (484 Epic Abu + 486 Elite Abu + 451 Warrior Abu + 9 Reguler Abu-abu tambahan yg kelewat di batch pertama krn dulu blank di-skip bukan di-nolkan). Verifikasi: idempoten (0 sisa), row count 17 file tetap sama persis (0 baris hilang/nambah). Banyak nilai lama yg ketimpa berupa placeholder aneh: 999, 1000, 9998, 9999 — bukan stok asli.

## Kalau lanjut warna lain / batch berikutnya

Skrip (scratchpad, TIDAK persisten antar sesi, perlu ditulis ulang kalau sesi baru): `match_stock_models.py` (fuzzy-match nama model, hasil di `match_results_uc.json`/`match_results_stp.json`), `build_stock_targets2.py` (resolve ke model_value dict per (kategori,warna), default 0 kalau blank, exclude model conflict), `apply_stock_abuabu2.py` (baca SKU→filter (kategori,warna) via dict lookup ke rev master→tulis kolom stok, idempoten, general utk banyak kombinasi warna sekaligus). Warna/tier yg BELUM disentuh: Hitam, Biru Benhur, Merah, Hijau Army (Reguler), Premium, Exclusive/Transparan (kolom kombinasi, tidak per-warna di Stock Opname). Pola yg sama tinggal diperluas (`COLOR_COLS` dict di `build_stock_targets2.py`) kalau user minta warna lain.

Lihat [[feedback-undercover-sku-sync-lessons]] utk pelajaran teknis terkait (SKU sbg kunci matching yg robust, dll).

## (2026-10-08) PERINGATAN layout Stock Opname berubah
User memasang sistem stok otomatis ([[project-undercover-sistem-stok-gsheet]]). Setelah migrasi, sheet "Stok Cover UC"/"Stok Cover STP" berformat **STOK|IN|OUT** (stok warna k di kolom 4+3k), bukan IN|OUT (kolom 4+2k). Kolom "IN" sekarang input sementara (selalu kosong) — **baca kolom STOK**, cek label baris 3 dulu. STP punya warna tambahan **Orange** (Reguler, setelah Hijau Army) → posisi kolom STP ≠ UC; petakan dari nama warna baris 2. Sheet format lama tersimpan sebagai "... (lama)" dan tidak diupdate lagi.
