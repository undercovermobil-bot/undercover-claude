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
