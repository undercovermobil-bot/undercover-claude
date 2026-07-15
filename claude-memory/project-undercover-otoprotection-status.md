---
name: project-undercover-otoprotection-status
description: Status kerja SKU Sync untuk toko Otoprotection (OP), dimulai 2026-07-10, di-scope ke 331 produk terlaris — struktur listingnya beda total dari UA/OT/SP
metadata:
  node_type: memory
  type: project
  originSessionId: 6eb3e44c-d7d4-4c74-9baa-9ddd25e762ff
---

Mulai 2026-07-10, setelah user instruksikan: **prioritaskan kerjaan SKU sync ke 331 produk di "MOBIL TERLARIS.xlsx" (sheet "COVER MOBIL") dulu, untuk SEMUA toko**, baru sisanya belakangan. Referensi rank tersimpan di scratchpad `terlaris_ref.csv` (tidak persisten, generate ulang dari file itu kalau perlu).

Ikuti [[feedback-undercover-update-folder-workflow]] — kerja tulis ke `Update via Claude\List Produk Otoprotection\`, file asli tidak disentuh. OP cuma punya file Shopee (`Informasi Penjualan 1 Shopee Otoprotection.xlsx` — file 2 kosong) + 2 file TikTok (belum disentuh sesi ini, TikTok-nya sangat besar ~4-7MB tiap file, belum dibuka).

**Progres tervalidasi (scope terlaris saja): 32 baris listing diperbaiki**, 0 mismatch/duplikat.

**STRUKTUR OP BEDA TOTAL dari UA/OT — penting utk sesi lanjutan:**
1. **1 listing per mobil berisi SEMUA kategori+generasi+warna sekaligus** (bukan listing terpisah per Reguler/Premium/dst seperti UA/OT). Konfirmasi: 0 nama produk yang punya >1 product_id — beda dari OT yang listing "Outdoor" polos bisa dipakai 2 pid berbeda.
2. **OP TIDAK PUNYA tier Premium/Exclusive sama sekali** — cuma Reguler+Strip (gabung 1 listing bernama "Body Cover Mobil / Selimut Mobil X") dan Transparan (listing terpisah bernama "Cover Mobil Transparan X"). Dikonfirmasi dari scan penuh 5.343 baris ber-SKU: cuma kode kategori R/S/T yang muncul, 0 kode P/E.
3. **Warna tier-Strip di listing SUDAH langsung pakai "Strip 1/2/3 + warna"** — SAMA PERSIS dengan master (beda dari OT yang perlu remap ke Elite/Epic/Warrior). Master OP juga punya warna "Strip 1 Abu".."Strip 3 Merah" sbg vocabulary asli, bukan alias.
4. **Semua nama produk TIDAK punya akhiran kategori apa pun** (0 dari 395 nama pakai suffix Reguler/Premium/dst) — kategori 100% ditentukan dari isi baris variant itu sendiri (prefix "Strip N" = Strip, warna polos = Reguler, listing "Transparan..." = Transparan).
5. **Ada sisa SKU format legacy pakai kode toko "OTP"** (bukan "SP") mis. `CVR0089-OTP-RSWB` — beda dari master yg pakai prefix "SP" utk Otoprotection. Belum diaudit skalanya.
6. **Submodel-as-generasi pattern SAMA seperti OT** (matching by name langsung ke kolom Generasi master, bukan by tahun): Suzuki Jimny (3 Pintu/5 Pintu), Toyota Starlet (Kotak/Kapsul), Mini Cooper (Clubman/Countryman/Hatch/Paceman/Roadster, DITAMBAH varian lebih spesifik "Hatch 3 Pintu"/"Hatch 5 Pintu" yg overlap dgn "Hatch" polos).
7. **Pola "Gen N : NamaPasar"** (mis. "Gen 2 : Reborn", "Gen 3 : Zenix" utk Toyota Innova; "Gen 3 : Neo Baleno" utk Suzuki Baleno) — nama pasar setelah titik-dua HARUS dibuang, cocokkan cuma bagian "Gen N"-nya ke master.
8. **Pola generasi gabungan pakai macam-macam separator**: master ada yg "Gen 1 & 2", ada yg "Gen 4&5" (tanpa spasi) — listing kadang tulis "Gen 1-2"/"Gen 4-5". Solusi yg dipakai: cocokkan lewat SET ANGKA yang diekstrak dari teks (bukan string exact match), supaya "1-2"≈"1 & 2"≈"1&2" semua ketemu.

**Hasil scan terlaris (setelah semua perbaikan classifier di atas):**
- CLEAN (sudah diperbaiki): 32 baris, 0 produk tersisa yg CLEAN murni (semua yg bisa diperbaiki otomatis sudah dieksekusi)
- ALREADY_OK: 66 produk (termasuk **Toyota Avanza #1** dan **Honda Brio #2**, top-2 terlaris — sudah benar dari awal)
- NEEDS_DECISION: 123 produk — dominan sub-pola yang sama seperti OT (submodel tidak ada di master: Toyota Hilux "Hilux Rangga", Toyota HiAce "Premio", Suzuki SX4 "S-Cross"/"X-Over" — TIGA-TIGANYA persis sama gap-nya dgn yg ditemukan di OT, kemungkinan besar produk² ini genuinely belum pernah diriset generasinya di master manapun)
- NO_MASTER: 2 — **Suzuki Carry Pickup** (rank #69, master OP cuma ada "Suzuki Carry Futura"/"Suzuki New Carry Pick-Up" versi lama, sama seperti kasus UA sebelum diunifikasi) dan **Mercedes Benz G Class** (rank #167, genuinely tidak ada entri G Class di master OP sama sekali, padahal A/B/C/CLA/CLS/E/GLA/GLB/GLC/GLE/GLS/S/SLK Class semua ada — cuma G Class yg hilang)
- Dilewati krn bukan produk terlaris: 9 produk

**(2026-07-11) Update status NEEDS_DECISION setelah verifikasi langsung ke listing live:**
- **Suzuki SX4 (submodel S-Cross/X-Over) dan Toyota Hilux/Hilux Rangga — TERNYATA SUDAH BENAR, tidak perlu perbaikan.** Sama seperti temuan di OT: SKU-nya sudah terisi format master yang tepat (`SZK-SX4-SP-...`, `TYT-HLX-SP-...`/`TYT-HLR-SP-...`), scanner cuma tidak bisa VERIFIKASI otomatis krn tidak tahu mapping submodelnya. Mapping terkonfirmasi: X-Over=Gen1, S-Cross=Gen2; Hilux Rangga=produk master terpisah (`TYT-HLR-*`, bukan bagian dari Hilux Gen manapun). Lihat detail penuh di [[project-undercover-otonation-status]] (temuan sama persis, dicek bareng).
- **Suzuki Carry Pickup + Mercedes Benz G Class + Suzuki Carry (polos, produk ke-3 yang ikut ketemu saat audit) — dikonfirmasi genuinely butuh varian generasi manual.** Ketiganya 1-dimensi (warna doang, TANPA pilihan generasi) di Shopee — SKU sebelumnya masih format legacy toko "OTP" (`CVR0067-OTP-*` utk Carry polos, `CVR0155-OTP-*` utk Carry Pickup, `CVR0117-OTP-*` utk G Class), BUKAN kosong. **Keputusan user 2026-07-11: kosongkan SKU-nya dulu (jangan tebak generasi mana), catat sebagai "perlu ditambah varian generasi manual di Shopee sebelum SKU bisa diisi".** ~43 baris total (14+14+15). Item Transparan-tier untuk Carry/G Class juga masih ada gap kecil (2 baris, format beda-beda) — belum disentuh, ikut kategori sama.

**BELUM DIKERJAKAN**: TikTok OP (2 file besar, belum dibuka sama sekali). Bagian non-terlaris dari Shopee OP (395 - 331-9 = sisanya). Mini Cooper submodel & sisa NEEDS_DECISION lain belum di-verifikasi satu-satu seperti SX4/Hilux di atas.

Why: instruksi user eksplisit soal prioritas terlaris berlaku lintas toko — dicatat di sini krn tiap toko punya struktur listing yg beda dan butuh scanner terpisah (tidak bisa reuse scan_ot2.py mentah2, walau logic intinya — submodel matching, genname numeric-set fallback — bisa di-port).

How to apply: sebelum lanjut OP, baca file ini dulu supaya tidak perlu re-discover struktur dari nol. Script kunci ada di scratchpad (`scan_op_terlaris.py`, `apply_op_fix.py`/`verify_op_fix.py`) — tidak persisten antar sesi.

**(2026-07-15) SCOPE DIPERLUAS dari 331-terlaris ke SELURUH katalog Shopee+TikTok, pakai lookup master penuh (69 sheet, filter Toko=Smartprotection karena OP berbagi prefix SP).** Hasil: Shopee1 51 baris update + 3.553 sudah benar (dari ~3.660 baris berisi); TikTok1 66 update + 3.535 benar; TikTok2 kosong (cuma placeholder).

**Prefix nama produk OP (lebih bervariasi dari perkiraan awal)**: kombinasi Reguler+Strip pakai salah satu dari `"Body Cover Mobil / Selimut Mobil "`, `"Cover Mobil / Selimut Mobil "` (typo, harusnya "Body Cover..."), `"Body Cover Mobil/ Selimut Mobil "` (spasi hilang sblm garis miring), `"Cover Mobil/ Selimut Mobil "`, `"Body Cover Mobil/ Selimut "` (Nissan Latio, hilang juga kata "Mobil" kedua). Transparan pakai `"Cover Mobil Transparan "` — konsisten, cuma 1 pola.

**Kategori ditentukan per-baris varian (bukan per-listing)**: kalau warna diawali "Strip N " → kategori Strip, kalau plain warna → Reguler — dikonfirmasi ulang, sesuai catatan lama.

**Alias/typo baru yang ditemukan & ditambahkan ke classifier** (banyak overlap dgn alias OT, lihat [[project-undercover-otonation-status]] — daftar sudah dipakai/diverifikasi ulang di OP): Honda CRV/HRV/WRV/BRV, Mazda CX-5/CX9/CX3, Mitsubishi Outlander (Sport & polos) → "Mitsubishi Mitsubishi Outlander", Mitsubishi Destinator/Kuda/Xpander Cross (semua ganda "Mitsubishi Mitsubishi..."), Mini Cooper→MINI Cooper, Hyundai Santa FE (case)→Santa Fe, **Suzuki Carry Pickup → "Suzuki Carry" (BUKAN "Suzuki New Carry Pick-Up"** — terverifikasi: master "Suzuki Carry" bare punya Gen6-11 yg cocok dgn listing, "New Carry Pick-Up" cuma py 1 gen "Baru"), Nissan XTrail/Xtrail (2 varian typo)→X-Trail, Toyota Altis→Corolla Altis, Etios Valco→Toyota Etios Valco, Hilux/Kijang bare→Toyota+nama.

**Bug klasifier penting yg diperbaiki (bukan cuma alias)**:
1. Generasi berformat "Gen N : NamaPasar" (mis. "Gen 2 : Reborn"/"Gen 3 : Zenix" utk Toyota Innova) atau "Gen N : tahun-tahun" atau "Gen N tahun-tahun" (TikTok, tanpa titik-dua) — semua ditangani dgn 1 fungsi `clean_gen_part()`: kalau ada titik-dua, buang semua setelah titik-dua (apapun isinya); kalau tidak ada titik-dua, strip trailing tahun via regex (support juga "Sekarang"/"Now" dan dash ganda "1996--2002").
2. Warna "Strip N Abu-abu"/"Strip N Biru Benhur" (listing tulis warna lengkap) vs master yg cuma simpan bentuk pendek "Strip N Abu"/"Strip N Biru" — perlu `clean_strip_color()` mapping.
3. Submodel-sebagai-generasi yg namanya TIDAK mengandung angka sama sekali (mis. Suzuki SX4 "X-Over"/"S-Cross") butuh `SUBMODEL_GEN_MAP` eksplisit (X-Over=Gen1, S-Cross=Gen2, sesuai presenden lama) krn tidak bisa dicocokkan via collapse-text biasa.
4. Generasi gabungan-rentang listing (mis. "Gen 1-3") vs master yg py label gabungan beda notasi (mis. "Gen 1, 2, 3") — numeric fallback lama (`digit-prefix slice match`) gagal utk kasus ini, ditambah fallback KEDUA: cocokkan cuma digit PERTAMA & TERAKHIR (bukan seluruh slice).

**Ditemukan (2026-07-15): 109 model OP TERNYATA sama sekali tidak punya varian generasi di listing (Shopee+TikTok), cuma warna — jauh lebih luas dari 3 produk yg sudah dikonfirmasi user 07-11 (Suzuki Carry Pickup/Mercedes G Class/Suzuki Carry polos).** Daftar lengkap 109 model ada di `Produk_Perlu_Keputusan_Manual.xlsx` (dikirim ke user). SKU dikosongkan (tidak ditebak), konsisten dgn keputusan user 07-11.

**Model genuinely tidak ada di master (bukan alias, gap asli)**: Nissan Latio, Chevrolet Estate Magnum (beda dari "Chevrolet Optra Magnum" yg ada), Toyota FJ Cruiser, Hummer H3 (beda dari "Hummer H1" yg ada) — dicatat di tracker manual.

**Belum dikerjakan**: TikTok OP file 2 (kosong, tidak perlu), Lazada OP (belum disentuh sama sekali sesi ini).

How to apply (update): scan_op_full.py di scratchpad (tidak persisten) adalah versi terbaru — arsitekturnya: alias substring-replace dgn guard anti-dobel (skip replace kalau target ekspansi sudah ada di teks), `collapse_gen()` (buang tahun/parentheses, lowercase, buang non-alfanumerik, "facelift"→"f") sbg pencocokan generasi utama, baru fallback ke deteksi "^Gen\s*\d" mentah + numeric-fallback (slice & first-last-digit) kalau collapse gagal.
