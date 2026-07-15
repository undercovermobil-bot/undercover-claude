---
name: project-undercover-smartprotection-status
description: Status kerja SKU Sync untuk toko Smartprotection (SP), dimulai 2026-07-11, di-scope ke 331 produk terlaris — struktur mirip Otoprotection tapi arah mapping warna kebalikan
metadata:
  node_type: memory
  type: project
  originSessionId: 6eb3e44c-d7d4-4c74-9baa-9ddd25e762ff
---

Mulai 2026-07-11, lanjutan langsung dari kerja Otoprotection (OP) di sesi yg sama, masih dlm instruksi "prioritaskan 331 produk terlaris dulu, semua toko" (lihat [[feedback-undercover-sku-sync-lessons]]). Ikuti [[feedback-undercover-update-folder-workflow]] — kerja tulis ke `Update via Claude\List Produk Smartprotection\`, file asli tidak disentuh.

File SP: `Informasi Penjualan 1 Shope Smartpro.xlsx` + `Informasi Penjualan 2 Shopee Smartpro.xlsx` (2 file Shopee aktif, beda dari OT/OP yg salah satu filenya kosong) + `Semua informasi TikTok Smartpro.xlsx` (~3.9MB, belum disentuh) + `Stok & Harga Lazada Smartpro.xlsx` (~724KB, belum disentuh).

**Progres tervalidasi (scope terlaris, Shopee saja): 539 baris listing diperbaiki**, 0 mismatch/duplikat.

**STRUKTUR SP: gabungan pola OP + pola UA/OT, dgn 1 twist penting:**
1. Sama seperti OP: 1 listing per mobil isi semua kategori+generasi+warna sekaligus (Reguler+Strip gabung 1 nama "Body Cover Mobil / Selimut Mobil X", Transparan listing terpisah "Cover Mobil Transparan X" ATAU kadang suffix "X Transparan" di akhir nama -- dua pola beda, clean_name() perlu handle keduanya kalau mau reuse). Shopee SP juga TIDAK kelihatan py listing Premium/Exclusive terpisah (cuma R/S/T kode SKU yg ketemu di 2 file Shopee), padahal master SP py entry Premium/Exclusive -- kemungkinan besar P/E dijual di TikTok/Lazada bukan Shopee (belum diverifikasi, SP py TikTok+Lazada yg lumayan besar beda dari OP).
2. **PENTING beda dari OP**: listing SP pakai TEKS "Elite/Epic/Warrior(Warior)" persis kayak UA/OT, TAPI master SP nyimpen warna sbg kode "Strip 1/2/3" persis kayak OP. Jadi arah mapping-nya: **Epic->Strip 1, Elite->Strip 2, Warrior/Warior->Strip 3** (sama urutan dgn yg dikonfirmasi user utk OT, tinggal dibalik arah konversinya: OT butuh Strip-N->EEW, SP butuh EEW->Strip-N). Typo "Warior" (kurang 1 r) muncul lagi di sini, konsisten sama toko lain.
3. Ada juga kasus kapitalisasi liar spt "HItam" (I besar) -- ditangani via lookup case-insensitive ke `MASTER_COLOR_CANON` lalu dikembalikan ke bentuk kanonik master, BUKAN sekadar dicek keanggotaannya (kalau cuma dicek keanggotaan tapi teks aslinya dipakai, "HItam" != master "Hitam" pas exact-match final).
4. Pola "2022 - Sekarang" ("Sekarang"=skrng/present, bukan tahun akhir) -- aman krn cuma y1 yg dipakai utk matching, bukan full-text match.

**Hasil scan terlaris (Shopee, 2 file):**
- CLEAN (diperbaiki): 73 produk, 539 baris
- ALREADY_OK: 144 produk
- NEEDS_DECISION: 139 produk (belum diinvestigasi detail per-produk sesi ini -- based on precedent OT/OP kemungkinan besar pola serupa: submodel yg tidak ada di master, tahun yg gagal cocok exact, dst)
- NO_MASTER: 16, **SEMUA "Transparan"-suffixed** (mis. "Honda Brio Transparan" rank #2!) -- dikonfirmasi genuinely gap kategori Transparan (BUKAN alarm nama), sama dgn gap yg sudah diketahui dari OT (lihat [[project-undercover-otonation-status]] & task tracking "gap kategori Transparan").
- Dilewati krn bukan produk terlaris: 32

**Gap master 331-terlaris (LINTAS 4 TOKO, dikerjakan sesi yg sama sblm mulai SP)**: sudah 100% tertutup kecuali gap Transparan yg genuinely gap struktural lama. 3 gap non-Transparan yg ditemukan (Mercedes Benz EQE, Suzuki Carry/Pickup, Mercedes Benz G Class) SEMUA sudah dibuatkan entri master utk SP juga (SZK-CAR & MBZ-GCL & MBZ-EQE, pakai skema warna Strip-N krn SP py kode itu, include Premium/Exclusive krn master SP py kategori itu).

**BELUM DIKERJAKAN**: 139 NEEDS_DECISION belum diinvestigasi detail, TikTok SP (~3.9MB, belum dibuka), Lazada SP (~724KB, belum dibuka), 16 gap Transparan (deferred bareng OT).

Why: instruksi user 331-terlaris berlaku lintas toko, SP toko terakhir dari 4. Struktur listingnya unik (campuran pola OP+UA dgn arah mapping warna kebalikan OT) makanya dicatat detail di sini biar tidak perlu re-discover kalau lanjut sesi depan.

How to apply: baca file ini dulu sblm lanjut SP. Script kunci scratchpad (`scan_sp_terlaris.py` -- hasil adaptasi dari `scan_op_terlaris.py` + EEW->StripN mapping, `apply_sp_fix.py`/`verify_sp_fix.py`), tidak persisten antar sesi.

**(2026-07-15) SCOPE DIPERLUAS dari 331-terlaris ke SELURUH katalog, SEMUA 4 file sekaligus (2 Shopee + TikTok + Lazada), pakai lookup master penuh (69 sheet, filter Toko=Smartprotection).** Hasil: Shopee1 73 update+2.314 benar, Shopee2 22+1.411, TikTok 71+3.714, Lazada 78+3.689. Arah mapping Epic→Strip1/Elite→Strip2/Warrior→Strip3 terkonfirmasi ulang lewat cross-check SKU existing (bukan cuma dari dokumentasi lama).

**Prefix nama produk SP lebih bervariasi dari dugaan**: selain `"Cover Mobil / Selimut Mobil "` standar, ada juga `"Body Cover Mobil / Sarung / Selimut Mobil "` (Mitsubishi Triton), `"Cover Mobil/ Selimut Mobil "` (spasi hilang, Hyundai Avega Sedan). **Pola Transparan TERNYATA 2 jenis nyata** (bukan cuma dugaan lama): (a) prefix terpisah `"Cover Mobil Transparan X"`, DAN (b) suffix `"X Transparan"` di produk yg pakai prefix Reguler biasa (mis. "Cover Mobil / Selimut Mobil Toyota Corolla Transparan") — kalau cuma tangani salah satu, ratusan baris salah ke-tag sbg "model tidak ada di master" (nama model jadi ikut "... Transparan"). **Motor/helm juga muncul di file SP** ("Body Cover Motor / Selimut Motor X", "Sarung Helm / Cover Helm Anti Air") — di luar scope bisnis cover mobil, biarkan saja (otomatis ke-skip krn prefix tidak cocok).

**Kasus ambigu ditemukan & diselesaikan**: listing bare "Suzuki Vitara" (tanpa sub-nama) ternyata menggabungkan generasi dari 3 model master berbeda dalam SATU listing: Gen1-3 → "Suzuki Grand Vitara", Gen4 (2023-2026) → "Suzuki Grand Vitara Hybrid", token "e Vitara" → "Suzuki e VITARA" (gen master-nya "Gen 1 (Electric)", butuh SUBMODEL_GEN_MAP eksplisit krn teks "e Vitara" tidak bisa dicocokkan otomatis ke "Gen 1 (Electric)"). Disambiguasi berdasarkan isi teks varian per baris, bukan tebak.

**Alias/typo SP-spesifik yg ditambahkan** (di luar yg sudah di-share dgn OT/OP, lihat [[project-undercover-otoprotection-status]]): "Kia Sedona / Carnival"→"Kia Sedona", "Mistubishi Grandis" (typo r hilang huruf 's')→"Mitsubishi Grandis", "Feroza" bare→"Daihatsu Feroza", "isuzu Panther" (huruf kecil)→"Isuzu Panther", "Mercedes Benz Gls/Glc/Cla Class" (huruf kecil sebagian)→huruf besar semua, "Volkswagen Beatle" (typo)→"Beetle", "Volswagen Polo" (typo, beda dari "Volkkswagen Polo" versi OP)→"Volkswagen Polo".

**Kasus salah-brand di listing (BUKAN typo ejaan, tapi nama brand yg salah sama sekali) — tidak di-alias, dicatat manual**: "Honda Fortuner" (Fortuner itu Toyota), "Suzuki Agya" (Agya itu Toyota) — di Lazada. "Mitsubishi Lantis" juga dicurigai salah brand (master cuma punya "Mazda Lantis") tapi tidak dipaksa alias krn bisa saja produk beda.

**Ditemukan (2026-07-15): ~105 model SP TERNYATA sama sekali tidak punya varian generasi di listing (Shopee+TikTok+Lazada), cuma warna** — pola sama persis dengan OP (lihat [[project-undercover-otoprotection-status]]), daftar model hampir identik. Dicatat di `Produk_Perlu_Keputusan_Manual.xlsx`, SKU dikosongkan (tidak ditebak).

**Model genuinely tidak ada di master**: Nissan Latio, Chevrolet Estate Magnum, Mitsubishi Lantis (curiga salah brand), Daihatsu Gran Max bare (ambigu Pick Up vs Minibus/Blind Van, tidak dipaksa pilih).

**Kolom SKU per file (dikonfirmasi)**: Shopee1&2 = kolom F index 6, startrow 7. TikTok = sheet "Template" kolom K (seller_sku) index 11, startrow 6. Lazada = sheet "template" kolom M (Seller SKU) index 13, varian di kolom N (Variations Combo) index 14, startrow 5.

**Kuirk openpyxl (TikTok & Lazada, file besar)**: resave mengubah sel string-kosong `''` jadi `None` di ribuan sel yg tidak disentuh (kolom opsional yg memang selalu kosong) — sudah diverifikasi 100% diff di luar kolom SKU persis pola ini (0 perubahan data lain), termasuk sebagian diff DI kolom SKU sendiri utk baris yg SKU-nya memang masih kosong. Aman utk upload ulang, sudah diinfokan ke user.

**Belum dikerjakan**: tidak ada file SP yang tersisa dari 4 file utama (2 Shopee+TikTok+Lazada) — semua sudah disentuh sesi ini. Sisa PR murni di level "butuh keputusan manual" (lihat tracker), bukan file yg belum disentuh.

How to apply: script terbaru `scan_sp_full.py` di scratchpad (tidak persisten) — arsitektur identik dgn `scan_op_full.py` OP, ditambah `tier_to_strip_color()` utk konversi Epic/Elite/Warrior→Strip-N (kebalikan dari OT yg convert Strip-N→EEW), dan `resolve_ambiguous_model()` khusus utk kasus "Suzuki Vitara" gabungan 3-model.
