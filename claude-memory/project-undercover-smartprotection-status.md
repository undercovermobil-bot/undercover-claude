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

## 2026-09-09 — Beda katalog Undercover vs Smartprotection

Dibandingkan dari ekspor live: UA (Shopee 5 file 3 Sep + TikTok + Lazada) vs
SP (4 file 8 Sep). Identitas model dipakai **kode SKU MEREK-MODEL**, bukan nama
listing — nama listing terlalu berisik (typo "Undervover", "Mobil BMW X5",
"Cover Honda BRV", 448 varian nama untuk ~340 model).

| | UA | SP |
|---|---|---|
| model berkode | 335 | 204 |
| model belum berkode | 82 | 14 |

**Hanya di Undercover: 196 model** (126 sudah berkode + 70 belum).
Terkonsentrasi di segmen premium/eksotik/EV yang SP memang tidak jual:
BMW 19 model, Volvo 9, Mazda 7, Lexus 6, Toyota 6, Chery 5, MG 5 — ditambah
Aston Martin, Bentley, Ferrari, Rolls-Royce, McLaren, Porsche, Audi (semuanya
belum berkode).

**Hanya di Smartprotection: 7 model** — Peugeot 306, Peugeot 406, Kia Sedona
Carnival, Holden (berkode) + Mitsubishi Lantis, Volswagen Polo, Honda Civic
Hatcback (belum berkode; dua terakhir kemungkinan typo).

### Jebakan yang ditemukan saat membandingkan

1. **Jangan bandingkan lewat nama listing.** Perbandingan berbasis nama
   menghasilkan 214 "hanya di UA" — inflated oleh typo & variasi penulisan.
   Berbasis kode: 126. Selisihnya murni noise penamaan.
2. **Kode kembar belum seragam antar toko.** SP masih memakai `MZD-MZ2`,
   `WLG-DAR`, `JEP-WR` untuk model yang di UA sudah jadi `MZD-2H`, `WLG-DRN`,
   `JEP-WRA`. Tanpa peta padanan ini, ketiganya salah dihitung sebagai
   "hanya ada di satu toko".
3. **Model tanpa SKU tidak kelihatan di perbandingan kode.** 9 model yang
   awalnya terlihat UA-only (BYD Seal, Chery Omoda 5, Ford Ranger, Hyundai
   Getz, Suzuki APV Luxury, dst) ternyata ADA di SP tapi listing-nya belum
   ber-SKU. Perbandingan kode saja akan melaporkan gap palsu — wajib
   cross-check ke nama listing yang SKU-nya kosong.
4. Listing non-mobil ikut terjaring (Glass Polish, Bahan Kain, Tas Portable,
   Logo Custom, iCar V23) — aturan #6 tetap harus dipasang.

File: `BEDA_KATALOG_UA_vs_SP.xlsx` (4 sheet: Hanya di Undercover, Hanya di
Smartprotection, Perlu dicek, Dikecualikan).

## 2026-09-09 — Penyesuaian kode SKU SP ke konvensi Undercover (856 baris)

Script baru `scripts/samakan_sku_smartprotection.py`. Dua jenis pekerjaan:

**A. Ganti prefix** (SKU sudah ada, kodenya beda dari UA) — 263 baris:
`MZD-MZ2`→`MZD-2H`, `WLG-DAR`→`WLG-DRN`, `JEP-WR`→`JEP-WRA`.

**B. Isi SKU** (listing ada di SP tapi SKU kosong; di Lazada terlihat "terisi"
karena auto-ID `8890956509-1788758253245-10`) — 593 baris untuk 7 model:
BYD Seal, Chery Omoda 5, Feroza Long, Ford Ranger, Hyundai Getz, Mazda CX-7,
Suzuki APV Luxury. Semua ber-TF=1 (diverifikasi di file formula) → satu kode
generasi `G1` untuk semua generasi.

Total: Shopee 289 · TikTok 274 · Lazada 293.

### Kosakata SKU SP BEDA dari UA — jangan disalin

| | UA/OT | SP/OP |
|---|---|---|
| Strip 1 (Epic) | PAB/PBR/PMR | **S1A/S1B/S1M** |
| Strip 2 (Elite) | EAB/EBR/EMR | **S2A/S2B/S2M** |
| Strip 3 (Warrior) | WAB/WBR/WMR | **S3A/S3B/S3M** |
| Warna dasar | ABU HTM BRU MRH GRN | sama + **ORG (Orange)** |
| Tier | R S P E T | **hanya R S T** (tidak ada Premium/Exclusive) |

### Ejaan varian di SP tidak konsisten — wajib ditoleransi

Dipindai dari data: **"Warior" (satu R) dipakai 1.367 baris**, ditambah
"Elita Merah", "Elite  Merah" (spasi ganda), "Elite BIru". Percobaan pertama
melewatkan 13 baris sebagai "warna tak terbaca" karena cuma mengenali
"Warrior". Pola ini kemungkinan ada juga di toko lain — selalu pindai dulu
seluruh penulisan varian sebelum menetapkan daftar kata kunci.

### Hyundai Avega: satu kode dipakai dua bodi

SP memakai `HYN-AVG` untuk **Avega Hatchback DAN Avega Sedan** sekaligus.
Diperbaiki mengikuti UA: Hatchback → `HYN-AVH` (33 baris), Sedan tetap
`HYN-AVG`. Ini bukan sekadar penyeragaman lintas toko — di dalam SP sendiri
dua produk berbeda memang tidak boleh berbagi satu kode.

Diverifikasi: 0 duplikat SKU per listing di Lazada, 0 sisa kode lama, TikTok
20/20 produk lengkap variannya, 0 perbedaan nyata di luar kolom SKU.

### Koreksi laporan beda katalog: "belum ada SKU" itu status SNAPSHOT

Laporan pertama menandai 70 model UA sebagai "belum punya kode SKU" — user
spot-check Chery Tiggo 9 dan menemukan SKU-nya SUDAH ada di Shopee
(`CHR-TI9-UA-R-G1-ABU`). Sebabnya: ekspor UA yang dipakai tertanggal
**3 September**, sebelum file `SIAP_UPLOAD_SKU_UA_*` diupload. Setelah dicek
silang ke file yang sudah dikirim: **64 dari 70 sudah punya SKU di situ**,
cuma **6 yang benar-benar belum** (Hyundai Verna, Kia Cerato, Proton Suprima S
— ketiganya menunggu opsi generasi di listing — plus Neta V, Daewoo Ssangyong
Musso, Mitsubishi Colt T120SS Pick Up).

**How to apply**: kalau melaporkan "belum ada SKU/harga", sebutkan TANGGAL
ekspor yang dipakai, dan cross-check dulu ke file yang sudah dikirim tapi
mungkin sudah diupload — status listing bisa berubah di antara ekspor dan
laporan.

## 2026-09-10 — Audit harga SP: mana yang belum berubah

User melihat "beberapa yang belum berubah". Dicek per baris (bukan per model)
ke ekspor 8 Sep. Ada TIGA kelompok berbeda, dan cuma kelompok A yang selama ini
dilaporkan:

### A. 11 model seluruhnya masih harga lama — 729 baris

Ford Fusion 261rb · Hyundai Matrix 298rb · Mercedes Benz GLB 309rb ·
Mitsubishi Eclipse 248rb · Nissan Cedric 271rb · Nissan Latio 291rb ·
Peugeot 3008 267rb · Peugeot 306 258rb · VW Fox 271rb · VW Passat 256rb ·
Wuling Darion 319rb. Semuanya **tidak ada di file HPP** (dicek ke keempat
sheet), jadi harga barunya memang belum bisa dihitung.

### B. Satu kode SKU, dua harga berbeda — 690 baris, 4 kode

| Kode | Listing A | Listing B | Selisih |
|---|---|---|---|
| DHT-FRZ | Feroza 370rb | **Daihatsu Rocky 324rb** | 46rb |
| DHT-GMX | Luxio 371rb | **Gran Max Minibus 443rb** | 72rb |
| HYN-AVG | Avega Sedan 370rb | **Avega Hatchback 325rb** | 45rb |
| TYT-AVZ | Avanza & Xenia 370rb | **Veloz 374rb** | 4rb |

Satu SKU = satu barang = wajib satu harga (preseden Calya/Sigra di UA).
HYN-AVG selesai sendiri begitu file pemisahan `HYN-AVH` diupload — Hatchback
memang produk lain. Tiga sisanya butuh keputusan angka mana yang dipakai.

### C. 18 baris nyangkut karena TYPO teks varian — semuanya TikTok

`Biru Benhru` (Panther 2, Outlander 4, Starlet 2, Voxy 2) · `Eltie Biru/Merah`
(Camry 6, Ciaz 1) · `Wrior Merah` (Datsun Go Plus 1). Baris lain di model yang
sama sudah harga baru; hanya baris bertypo yang tertinggal di harga lama
(mis. Voxy Rp297rb sedangkan standar modelnya Rp445rb).

**Kenapa typo bisa bikin terlewat**: update harga SP dijalankan lewat
pencocokan TEKS VARIAN (warna + generasi), bukan lewat prefix SKU seperti di
UA. Begitu warnanya salah tulis, barisnya tidak ketemu dan diam-diam dilewati.
Ini pola yang sama dengan "Warior" (1.367 baris) yang ditemukan saat mengisi
SKU SP — **kosakata varian SP memang penuh salah ketik**, dan setiap proses
yang bergantung pada teks varian harus memindai ejaan yang benar-benar ada di
data dulu, bukan memakai daftar kata baku.

File: `SP_HARGA_BELUM_BERUBAH.xlsx` (3 sheet A/B/C, lengkap per baris).

## 2026-09-10 — Semua perbaikan SP digabung jadi SATU file per channel

Script `scripts/gabung_perbaikan_sp.py`. Menggantikan
`SAMAKAN_SKU_SMARTPROTECTION_*` dan `PERBAIKI_HARGA_SP_TIKTOK` yang dikirim
sebelumnya (dua-duanya belum sempat diupload).

**Kenapa wajib digabung**: file update marketplace menimpa SEMUA kolom yang ada
di dalamnya. File SKU membawa harga LAMA, file harga membawa SKU LAMA — upload
yang belakangan akan mengembalikan kolom yang baru saja dibetulkan (pelajaran
2026-08-15, sudah pernah kejadian di Undercover).

| File | Baris | SKU berubah | Harga berubah |
|---|---|---|---|
| PERBAIKAN_SP_SHOPEE | 334 | 289 | 45 |
| PERBAIKAN_SP_LAZADA | 338 | 293 | 45 |
| PERBAIKAN_SP_TIKTOK | 588 | 274 | 63 |

TikTok 588 = 337 baris berubah + 251 pelengkap (template all_information wajib
memuat seluruh varian tiap produk yang disentuh).

### Keputusan harga user 2026-09-10

- **DHT-GMX** (Luxio + Gran Max Minibus) → **R 371.000 / S 414.000**.
  Gran Max Minibus turun dari 443/486. Alasan user: SP memang sedikit lebih
  murah dari UA, dan angka 443rb itu yang menyimpang, bukan 371rb.
- **TYT-AVZ** (Avanza + Xenia + Veloz) → **R 370.000 / S 413.000**.
  Veloz turun dari 374/417.
- **DHT-FRZ** (Feroza 370rb vs Daihatsu Rocky 324rb) **BELUM diputuskan** —
  sengaja tidak disentuh, masih menunggu user.
- Usulan Pcs/Roll untuk 11 model harga-lama **ditunda** atas permintaan user.

**HYN-AVG selesai sendiri**: begitu Avega Hatchback dipisah ke `HYN-AVH`,
harga 325rb-nya sah karena produknya memang beda dari Avega Sedan (370rb).

Diverifikasi ketiga file: 0 perbedaan nyata di luar kolom SKU & harga,
0 duplikat SKU per listing di Lazada, TikTok 29/29 produk lengkap variannya,
harga akhir DHT-GMX 371/414 (36+54 baris) dan TYT-AVZ 370/413 (126+189 baris)
seragam di semua listing & channel.

## 2026-09-11 — TikTok SP tuntas, plus 2 baris salah kategori yang ketahuan

Ekspor TikTok SP 11 Sep memastikan semua perubahan sudah masuk:
Gran Max Minibus R 371.000 / S 414.000 · Veloz R 370.000 / S 413.000 ·
18 baris typo varian sudah di harga standar · atribut `2026` + `16:9`
terpasang di 9 produk.

### Cacat yang saya buat sendiri: ejaan strip "Eltie" tidak dikenali

Pemindaian penuh teks varian SP menemukan **2 baris** yang kategori SKU-nya
tidak cocok dengan teks variannya — dua-duanya di TikTok:

| Produk | Varian | SKU salah | SKU benar | Harga |
|---|---|---|---|---|
| BYD Seal | `Eltie Biru` | `BYD-SEA-SP-R-G1-BRU` | `BYD-SEA-SP-S-G1-S2B` | 416.000 (sudah benar) |
| Suzuki Ciaz | `Eltie Merah` | `SZK-CIA-SP-R-G1-MRH` | `SZK-CIA-SP-S-G1-S2M` | 371.000 → **414.000** |

BYD Seal itu **kesalahan pengisian SKU saya**: `Eltie` tidak masuk daftar kata
kunci strip, jadi jatuh ke pencocokan warna dasar ("biru" → BRU) dan dapat
kategori R. Suzuki Ciaz SKU-nya memang sudah salah dari dulu, tapi **saya
memperburuknya**: karena SKU-nya berkategori R, perbaikan harga kelompok C
menariknya ke harga Reguler 371.000, padahal itu varian Strip yang seharusnya
414.000.

**Bug-nya diam-diam**: ejaan tak dikenal tidak memicu error, cuma jatuh ke
cabang warna dasar. Ketahuan hanya karena memverifikasi silang kategori SKU
vs teks varian, bukan dari proses pengisian itu sendiri.

Daftar ejaan strip SP yang sekarang ditangani: epic/epik, elite/elita/elit/
**eltie**/**eite**, warrior/warior/**wrior**, strip 1/2/3.

**How to apply**: setelah mengisi SKU massal, WAJIB cek silang — kategori di
SKU (R/S/T) harus cocok dengan yang tersirat dari teks varian. Jangan hanya
menghitung "berapa baris terisi".

### Sisa masalah harga SP (belum ditindaklanjuti)

- **DHT-FRZ**: Feroza 370rb vs Daihatsu Rocky 324rb — belum ada keputusan user.
- **HYN-GET** (Hyundai Getz): TikTok R 365rb **S juga 365rb** (selisih 0,
  seharusnya 43rb); Shopee malah 322rb. Tiga angka berbeda untuk satu model.
- **CHR-O5** (Chery Omoda 5): R 370rb S 415rb (selisih 45rb, bukan 43rb).
- 11 model masih skema harga lama (menunggu Pcs/Roll).
- 30 listing TikTok SP masih tanpa SKU format baru (395 baris) — BMW Seri 7,
  Toyota Corolla, Hyundai Kona, dst.
- Listing **Transparan** atribut TikTok-nya masih kosong semua → kalau nanti
  diedit, akan kena error atribut wajib yang sama.
