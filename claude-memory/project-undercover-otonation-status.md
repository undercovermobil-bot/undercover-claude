---
name: project-undercover-otonation-status
description: Status kerja SKU Sync untuk toko Otonation (OT), dimulai 2026-07-10 setelah Undercover selesai — jauh lebih berantakan dari UA, banyak pola baru ditemukan
metadata:
  node_type: memory
  type: project
  originSessionId: 6eb3e44c-d7d4-4c74-9baa-9ddd25e762ff
---

Mulai 2026-07-10 (sesi sama setelah UA selesai). Otonation (OT) hanya punya channel Shopee (3 file: `Informasi Penjualan Shopee Otonation 1-3.xlsx`, file 3 kosong/tidak dipakai). Ikuti [[feedback-undercover-update-folder-workflow]] — semua kerja tulis ke `Update via Claude\List Produk Otonation\`, file asli TIDAK disentuh.

**Progres tervalidasi:** 513 baris listing diperbaiki (436+12+4+57+4, lima batch bertahap seiring classifier diperbaiki) + 374 baris master baru untuk 6 produk yang hari yang sama juga baru dibuat untuk UA (Ford Fusion, Mercedes Benz G Class, Mitsubishi Eclipse, Peugeot 306, VW Fox, VW Passat) — SKU dipakai SAMA PERSIS dengan versi UA (prefix `-UA-` shared lintas toko, dikonfirmasi audit background task 2026-07-10: 100% baris Otonation pakai prefix UA by design, bukan bug). Semua terverifikasi 0 mismatch, 0 duplikat per batch.

**Kemampuan classifier ditambah (penting utk reuse sesi depan, semua di `scan_ot2.py`):**
- Deteksi submodel: kalau variant listing tidak punya info tahun sama sekali tapi 1 bagiannya cocok literal ke kolom "Generasi" master (case-insensitive) — mis. "Roadster", "Kotak", "Kapsul", "Commuter", "3 Pintu"/"5 Pintu" — dianggap submodel bukan warna. Alias "X Doors"(EN)→"X Pintu"(ID) otomatis dinormalisasi.
- **Bug penting yang ditemukan & diperbaiki**: utk variant 2-bagian TANPA tahun (mis. "Kapsul,Silver"), deteksi warna-vs-submodel awalnya salah — nge-anggap kedua bagian kandidat warna dan bagian terakhir menimpa yg pertama, hilangkan info submodel. Fix: klasifikasi tiap bagian eksplisit lewat cek keanggotaan di `MASTER_COLOR_CANON` (bukan asumsi urutan) — bagian yg BUKAN warna dikenali = submodel.
- Kalau match tahun gagal/ambigu tapi teks generasi (setelah dibuang bagian tahun-nya) cocok literal ke kolom Generasi master, dipakai sbg fallback disambiguator (kasus: beberapa submodel Mini Cooper berbagi tahun mulai yg sama).

**7 produk 1-dim yang BUKAN pola arsip "Sarung Mobil" — STATUS FINAL (2026-07-11, dicek langsung ke listing live setelah user konfirmasi beberapa mapping via screenshot):**
- **Suzuki Jimny, Toyota Starlet, Suzuki SX4, Toyota Hilux (+Hilux Rangga), Toyota Innova, Nissan Navara (+PRO-4X) — SEMUA TERNYATA SUDAH BENAR, TIDAK PERLU PERBAIKAN.** Dicek ulang baris-per-baris di listing live ("Outdoor"/"Semi Outdoor"/"Extreme Outdoor", semua file Shopee OT): SKU-nya sudah terisi dengan format master yang tepat. Kesalahan sebelumnya: scanner otomatis tidak tahu cara memetakan submodel-submodel ini (X-Over/S-Cross, Hilux Rangga, Reborn/Zenix, PRO-4X, dst) jadi baris-baris ini ke-flag NEEDS_DECISION meski sebenarnya SUDAH tersinkron dari sononya. Mapping yang sekarang terkonfirmasi (user + verifikasi langsung ke data):
  - Suzuki SX4: **X-Over = Gen 1, S-Cross = Gen 2** (dikonfirmasi user & sudah match persis di listing UA & OT & OP).
  - **Toyota Hilux Rangga = PRODUK MASTER TERPISAH** (kode `TYT-HLR-*`, generasi sendiri "Gen 1" 2024-2026), BUKAN salah satu generasi dari Toyota Hilux biasa (`TYT-HLX-*`, Gen1-2/3-4/5-6/7-8 pakai kode gen terendah). Sudah ada di master keempat toko. Dikonfirmasi user.
  - Toyota Innova: **Gen 2 (Reborn) = Gen 2, Gen 3 (Zenix) = Gen 3** — buang nama pasar dalam kurung, cocokkan nomor gen polos. Dikonfirmasi user.
  - **Nissan Navara PRO-4X = PRODUK MASTER TERPISAH** (kode `NSN-NVP-*`, Gen 4 2020-2026), BUKAN submodel dari "Nissan Navara" biasa (`NSN-NVR-*`, Gen1-3). Dikonfirmasi user.
  - Pola umum di listing "Outdoor" (2 warna: Abu-abu/Silver): Abu-abu→Reguler, Silver→Premium — TAPI untuk baris submodel (Hilux Rangga, Navara PRO-4X) di listing "Outdoor" yang sama, KEDUA warna (Abu-abu & Silver) sama-sama masuk Premium (submodel ini kelihatannya hanya dijual Premium lewat listing "Outdoor"; tier Reguler+Strip-nya ada di listing "Semi Outdoor" terpisah). Bukan bug — pola konsisten across produk.
- **Mercedes Benz CLA Class — GENUINELY BELUM BISA DIPETAKAN.** 15 baris listing "Semi Outdoor" (product_id di file `Informasi Penjualan Shopee Otonation 2.xlsx`, sekitar baris 5839-5853) SKU-nya kosong total, variannya CUMA warna (Hitam/Biru/Abu-Abu/dst + Strip 1/2/3+warna) TANPA info generasi sama sekali — padahal master CLA Class punya 2 generasi (Gen1 2013-2019, Gen2 2019-2024) dengan SKU beda per generasi. Sama persis pola "bare-variant" yang juga ditemukan di Otoprotection (Suzuki Carry/Carry Pickup/Mercedes G Class) — perlu ditambah pilihan generasi di listing Shopee dulu sebelum SKU bisa diisi. Masuk terlaris rank #229. **Keputusan user (2026-07-11): masukkan ke daftar "perlu ditambah varian manual" bareng item Otoprotection**, JANGAN coba tebak generasinya.

**Pola struktural baru yang ditemukan di OT (tidak ada di UA), penting untuk sesi lanjutan:**
1. **Skema warna tier-Strip beda total dari master**: listing OT pakai "Strip 1/Strip 2/Strip 3 + warna" (mis. "Strip 2 Abu-Abu"), BUKAN "Elite/Epic/Warrior + warna" seperti master. Mapping dikonfirmasi user: **Strip 1=Epic, Strip 2=Elite, Strip 3=Warrior**. Sub-nama warna juga perlu dipendekkan ke bentuk short-form Strip (Abu-abu→Abu, Biru Benhur→Biru, Merah tetap Merah) — bentuk panjang "Abu-abu" TIDAK match ke master yang pakai "Elite Abu" bukan "Elite Abu-abu". ~5.700 dari 11.534 baris varian kena pola ini (hampir separuh listing OT).
2. **Penamaan kategori produk sangat tidak konsisten**, banyak akhiran berbeda utk kategori master yang sama:
   - "Extreme Outdoor" → Exclusive (konsisten 100%)
   - "Semi Outdoor" / "Indoor dan Outdoor" → Reguler (konsisten 100%, keduanya campur warna Reguler+Strip dalam 1 listing)
   - "Outdoor" polos → AMBIGU, dipakai identik utk listing Reguler DAN Premium (nama produk SAMA PERSIS, cuma beda product_id) — harus dideteksi dari SET WARNA aktual di listing itu sendiri (subset {Abu-abu,Silver} → Premium, selain itu → Reguler), BUKAN dari teks nama.
   - "Cover Mobil / Sarung Mobil X" tanpa akhiran apa pun, warna-only tanpa generasi → **INI LISTING ARSIP LAMA** (dikonfirmasi user 2026-07-10) — versi aktifnya ada di listing terpisah dgn akhiran "Semi Outdoor" dst yg SUDAH punya varian warna+generasi lengkap. JANGAN coba perbaiki SKU listing arsip ini, cukup diabaikan/dilewati.
   - "X Transparan" (nama produk literal mengandung kata "Transparan") → kategori Transparan, warna JUGA selalu "Transparan" (bukan warna asli mobilnya) — kalau variant listing cuma nulis generasi tanpa warna eksplisit, default warna = "Transparan" bukan "Abu-abu".
3. **Gap kategori Transparan sangat luas** (~269+ baris teridentifikasi, kemungkinan lebih banyak lagi belum ke-scan penuh) — BUKAN bug baru, sudah lama diketahui (lihat item 1 di [[project-undercover-sku-sync-status]]). User pilih **ditunda dulu**, prioritas ke bucket lain.
4. **Nama produk master vs listing sering beda ejaan/singkatan**, butuh alias map manual (mirip kasus Livina X-Gear di UA): Honda CRV→"Honda CR-V", Honda HRV→"Honda HR-V / e:N1", Honda WRV→"Honda WR-V", Mazda CX-5→"Mazda CX5" (tanpa strip), Mazda CX9→"Mazda CX-9" (pakai strip), Mitsubishi Outlander Sport→"Mitsubishi Mitsubishi Outlander" (nama master dobel "Mitsubishi"), Mitsubishi Destinator→"Mitsubishi Mitsubishi Destinator" (sama, dobel), Mitsubishi Pajero→"Mitsubishi Pajero Sport", Nissan Grand Livina→"Nissan Livina / Grand Livina", Toyota 86→"Toyota GR 86", "Volskwagen Tiguan" (typo di nama listing sendiri)→"Volkswagen Tiguan". Alias map ini sudah ditulis di `scan_ot2.py` (scratchpad sesi, TIDAK persisten — perlu ditulis ulang sesi depan, atau simpan skripnya ke lokasi permanen kalau mau reuse).

**Kelompok masih tersisa (belum dikerjakan, per 2026-07-10 akhir sesi):**
- **Gap Transparan** (~269+ baris) — ditunda, keputusan user.
- **~338 produk NEEDS_DECISION** sisa setelah semua perbaikan classifier di atas — dominan sekarang: (a) baris "1-dim" warna-only tanpa generasi utk produk multi-generasi TAPI ini kemungkinan besar listing arsip (pola sama seperti "Sarung Mobil X" — perlu verifikasi per kasus; CLA Class dicek 2026-07-11 dan TERNYATA genuinely butuh tambahan varian manual, bukan arsip — lihat status final di atas), (b) beberapa produk dgn tahun listing tidak cocok generasi manapun di master (pola sama seperti Kategori C di UA — Chevrolet, dll), (c) produk sub-model: Mini Cooper (Roadster/Paceman/Hatch/Clubman/Countryman) masih perlu dicek — Navara PRO-4X SUDAH beres (lihat status final di atas), jangan diulang.
- **Sisa produk NO_MASTER** (~41 setelah alias fix) — kemungkinan besar genuinely belum ada di master OT (bukan cuma gagal fuzzy-match lagi, sudah dicek yang jelas), perlu audit satu-satu kalau mau lanjut Kategori D-style utk OT.

**Script kunci (scratchpad sesi, tidak persisten)**: `scan_ot2.py` (scanner utama, versi terbaru dgn semua fix di atas), `apply_ot_fix.py`/`verify_ot_fix.py` (apply+verify generik, baca `ot_fix_plan2.csv`), `fix_master_categoryD_ot.py` (nambah baris master 6 produk baru).

Why: OT ternyata jauh lebih berantakan dari UA — bukan cuma soal generasi/tahun master, tapi skema warna tier-Strip yang beda total dan penamaan produk yang campur-aduk. Metodologi UA (exact-year-match + auto-collision-check) masih valid sbg fondasi, tapi butuh banyak layer normalisasi tambahan sebelum bisa jalan bersih di OT.

How to apply: sebelum lanjut kerja OT di sesi depan, baca file ini dulu lengkap sebelum mulai scan ulang dari nol — banyak pola yang kelihatan seperti "bug baru" ternyata sudah pernah ditemukan & dipetakan di sini.

**(2026-07-15) Scope diperluas ke SEMUA brand (bukan cuma 331-terlaris), lookup master dibangun ulang penuh (69 sheet, sebelumnya sempat ke-skip sheet Suzuki 3.372 baris krn bug cek-header — sudah diperbaiki, lihat [[project-undercover-sku-sync-status]]).** Script baru `scan_ot_full.py` (scratchpad, tidak persisten) — hasil akhir setelah semua fix sesi ini: File1 (`OT_Shopee_1.xlsx`) 647 update + 2.514 sudah benar; File2 645 update + 1.859 benar (naik dari checkpoint awal sesi 477+356 update krn serangkaian fix di bawah).

**Alias/typo baru yang ditambahkan** (di luar yang sudah ada di item 4 atas): Mini Cooper→MINI Cooper, Hyundai Santa FE (case)→Santa Fe, **Suzuki Carry Pickup→"Suzuki Carry" bare (BUKAN "Suzuki New Carry Pick-Up"** — "Suzuki Carry" py Gen6-11 yg cocok, "New Carry Pick-Up" cuma py 1 gen "Baru"), Suzuki APV Arena→"Suzuki APV Arena / Blind Van", Mitsubishi Kuda→"Mitsubishi Mitsubishi Kuda" (dobel), Mercedes Benz GLS→"...GLS Class", Honda BRV→"Honda BR-V", Honda Brio→"Honda Brio Satya / RS", Mitsubishi Xpander Cross→dobel "Mitsubishi Mitsubishi...", Daihatsu Gran Max Minibus→"... / Blind Van", Nissan Livina XGear→"X-Gear" (hubung), Hyundai Avega Sedan→"Hyundai Avega" (tanpa "Sedan", master gak py entri terpisah), Nissan Kicks→"...e-POWER", Toyota Hiace (case)→"Toyota HiAce". Typo listing murni (bukan alias bisnis): "HIsuzu Mux"→"Isuzu Mux", "Toyota Toyota Hardtop" (dobel brand)→"Toyota Hardtop", "Jazz" bare (bukan substring, exact-match only)→"Honda Jazz".

**Bug penting yang diperbaiki**:
1. Guard anti-dobel-alias: alias yg MEMPERPANJANG teks (mis. "Mercedes Benz GLS"→"...GLS Class") bisa salah nempel dobel kalau teksnya udah lengkap ("GLS Class"→"GLS Class Class") — fix: skip replace kalau target alias udah ada duluan di teks DAN target lebih panjang dari key (`len(v)>len(k) and v in name: skip`). Alias yg MEMPERPENDEK (Avega Sedan→Avega, Carry Pickup→Carry) aman diproses selalu tanpa guard ini.
2. Bug default warna "Abu-abu" utk kategori Exclusive — SALAH, master Exclusive warna-nya SELALU `None`/kosong (diverifikasi: 996/996 baris Exclusive di master py warna None). Baris kode lama yg maksa warna="Abu-abu" utk Exclusive dihapus total.
3. Prefix nama produk yang typo: `"Cover Mobil / Selimut Mobil"` tanpa spasi trailing (fallback), `"Cover Mobil Honda Jazz - Semi Outdoor"` (template beda sama sekali, prefix tersendiri utk 1 listing spesifik).
4. `classify_variant()` dibuat model-aware: cek dulu apakah teks varian (setelah buang tahun) match LANGSUNG ke salah satu label generasi master model itu (case-insensitive, tahan varian "Facelift"↔"F", tahan parenthetical tahun) via `collapse_gen()` — ini nangkep sekaligus kasus submodel Mini Cooper (Roadster/Paceman/dst), Toyota Hiace (Commuter), dan skema warna Mitsubishi Kuda (generasi py tahun ketiban ke label itu sendiri).
5. Model ambigu yang butuh diintip isi variannya dulu sebelum ditentukan: "Suzuki APV" bare (Arena/Luxury/default→Arena, dikonfirmasi dari SKU existing yg sudah benar), "Toyota HiAce"+varian "Premio"→redirect ke model terpisah "Toyota HiAce Long".

**Model ambigu tanpa keputusan otomatis (perlu manual, DICATAT bukan ditebak)**: Honda City / Mazda 2 / Kia Rio bare (master py 2 sub-model Sedan/Hatchback masing-masing, listing tidak sebut yg mana), Nissan Livina XGear (skema generasi listing Gen1/Gen1F sama sekali gak nyambung ke skema submodel master "5-Seater"/"7-Seater"). Semua 4 sudah masuk `Produk_Perlu_Keputusan_Manual.xlsx`.

**Sisa ~1.000 baris NO_LOOKUP sekarang didominasi kasus GENUINE (bukan bug klasifier lagi)**: (a) gap kategori Transparan yg memang tidak ada di master utk banyak model (konsisten dgn gap lama yg sudah diketahui), (b) generasi sangat lawas yg gak pernah di-riset (mis. Toyota Corolla Gen1-5 thn 1966-1987), (c) skema generasi listing pakai kode chassis Eropa (Mercedes W-code, BMW E/F/G-code, VW B-code) yang TIDAK py pemetaan otomatis ke skema "Gen N" master — butuh riset manual per model kalau mau dikejar, TIDAK auto-fix karena resiko salah tebak tinggi.

Why: dicatat detail supaya sesi depan tidak perlu re-discover bug yang sama (terutama guard anti-dobel-alias dan bug default-warna-Exclusive yang keduanya sempat bikin regresi kalau tidak hati-hati).


## (2026-08-19) Bug SKU salah-tag di listing "Outdoor" polos -- DIPERBAIKI

Ditemukan pas kerja update harga (lihat project-undercover-harga-referensi.md
utk kronologi lengkap): 31 baris di 15 model, hidup di listing kategori
**"Outdoor" POLOS** (setara tier Premium UA, dikonfirmasi user -- BUKAN
"Semi Outdoor" yg setara Reguler), tapi SKU-nya bersegmen **'R' (Reguler)**
padahal seharusnya **'P' (Premium)**. Semua kasus: warna Abu-abu, harga
SENDIRI sudah benar Premium (Rp700rb-1,06jt) -- murni segmen SKU-nya yg keliru.

Model kena: Terios(TYT-RSH), Xenia(TYT-AVZ), Vellfire(TYT-ALP), HR-V(HND-HRV),
X-Trail(NSN-XTR), Suzuki XL7(SZK-XL7), Sirion(DHT-SRN), Camry(TYT-CMY),
Nissan Serena(NSN-SRN), Corolla(TYT-CRL), Stargazer(HYN-SGZ), City
Hatchback(HND-CHB), Mercedes S Class(MBZ-SS), BMW Seri 5(BMW-S5), Toyota
Harrier(TYT-HAR).

**Diverifikasi ketat sebelum eksekusi**: SETIAP kombinasi prefix+gen+warna
hasil ganti R->P dicocokkan ke keseluruhan SKU master UA (`ua_skus` set) --
100% match, termasuk kasus yg kelihatan janggal (Corolla Gen 5 -- OT sendiri
tidak py baris Premium G5 lain sbg pembanding, tapi ternyata memang ada di
master UA). Jadi bukan SKU baru yg diciptakan, murni koreksi segmen yg salah
ketik/salah proses ke kode yg SUDAH ADA di master.

**Fix**: `scripts/fix_sku_outdoor_polos.py` (pakai helper `is_outdoor_polos()`
dari `update_harga_per_sku.py`) -- ganti SEGMEN KE-4 SKU (R/S -> P) doang,
gen+warna+prefix tidak disentuh. Hanya kolom SKU yg berubah, harga tidak
disentuh (sudah benar dari awal). Hasil: 31 baris Shopee OT, 0 masalah.

**Kalau extend ke toko lain (OP/SP)**: pola yg sama (listing "Outdoor" polos
py SKU tersasar R/S padahal harusnya P) kemungkinan berulang -- jalankan
`fix_sku_outdoor_polos.py` yg sama, tapi WAJIB verifikasi ulang tiap hasil ke
set SKU master (jangan asumsikan otomatis benar tanpa cross-check, spt yg
dilakukan di sini).


## (2026-09-04) Pengisian SKU massal OT -- 874 baris, `scripts/isi_sku_massal.py`

Script yang sama dengan UA, diperluas supaya mengerti kosakata OT. Hasil: **874
baris** (844 isi-kosong + 30 format lama), 0 masalah. Sumber kode: 498 dari
listing OT sendiri, 491 dari master, cuma **3 kode model baru**.

### Pemetaan kategori OT -- DIBUKTIKAN dari data, bukan ditebak

Dicek ke baris OT yang SKU-nya SUDAH benar (n=7.714):

| Nama listing | Segmen SKU | Bukti |
|---|---|---|
| Extreme Outdoor | **E** | 520/520 |
| Outdoor (polos) | **P** | 718/718 |
| Semi Outdoor | R/S | 5.745 (tidak ada P/E) |
| Indoor dan Outdoor | R/S | 692 |

Kata tier eksplisit ("- Premium - Outdoor") selalu menang atas kosakata Outdoor.
Hasil akhir file konsisten 100% dengan tabel ini.

### JEBAKAN BESAR: pembersih nama model harus tahu kosakata KEDUA toko

Percobaan pertama menghasilkan **109 kode model baru yang SAMPAH** -- `BMW-X5O`
("BMW X5 Outdoor"), `CHR-OM5S` ("Chery Omoda 5 Semi Outdoor"), `AUD-A42`
("Sarung Audi A4"), `HND-CHS2`, dst. Sebabnya `TIER_RE`/`BOIL_RE` cuma
membuang kosakata UA (Reguler/Premium/Exclusive), sedangkan OT memakai
Outdoor/Semi Outdoor/Extreme Outdoor/Sarung Mobil. Akibatnya kata kategori
bocor ke nama model, sehingga (a) kode barunya salah dan (b) model yang SAMA
tidak saling ketemu antar tier maupun ke master. Setelah kosakata OT ikut
dibuang: 109 -> **3** kode baru.

**How to apply**: kalau memproses toko dengan penamaan listing berbeda, PERIKSA
dulu berapa kode model baru yang dihasilkan. Angka yang melonjak (puluhan model
umum seperti BMW X5 / Honda Civic dianggap "baru") = tanda kuat kosakata
kategorinya belum dibuang, bukan tanda katalognya memang baru.

### Hal lain yang ditemukan

- **Warna bentuk pendek**: OT menulis warna dasar "Abu"/"Biru" (bukan
  "Abu-abu"/"Biru Benhur"). Ditambahkan ke `WARNA_DASAR`; aman karena
  `WARNA_STRIP` selalu dicek lebih dulu sehingga "Elite Abu" tidak salah jatuh.
- **Listing arsip lama** ("Cover Mobil / Sarung Mobil X" tanpa akhiran
  kategori) -- 351 baris, sengaja TIDAK disentuh sesuai keputusan user
  2026-07-10. Ditangani lewat `ARSIP_RE`.
- **"Toyota Altis" vs master "Toyota Corolla Altis"** -- sempat dibuatkan kode
  duplikat TYT-ALT2. Diperbaiki lewat `ALIAS_MODEL`. Pola ini kemungkinan
  berulang di toko lain: nama listing lebih pendek dari nama master.

### Perlu keputusan user

`SZK-FE` dibuat untuk listing "Suzuki Forsa Esteem", padahal master sudah punya
"Suzuki Forsa" (`SZK-FOR`). Forsa & Esteem generasi berurutan mobil yang sama --
bisa jadi harusnya ikut SZK-FOR. TIDAK ditebak, dilaporkan ke user.
