---
name: project-undercover-sku-sync-status
description: "Checkpoint status SKU Sync per 2026-07-08 (+ 07-09: bug generasi-ketiban meluas ke 91 produk; +07-11: koreksi — 5 produk Kategori D non-terlaris ternyata baru sebagian tersinkron, sengaja ditunda) — apa yang selesai vs sengaja ditunda"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

Snapshot per 2026-07-08 — verifikasi ulang ke file aktual sebelum dipakai sebagai dasar keputusan, karena ini snapshot beku, bukan status live.

**Selesai & terverifikasi:**
- Rollout 63 merek + pilot Toyota + audit data-quality + audit kepatuhan aturan (0 pelanggaran).
- Revisi taksonomi generasi besar-besaran (master disesuaikan ke pola listing Undercover Shopee).
- Fix bug sistemik "bare-variant" (produk varian 1-dimensi diam-diam terbuang) — +3.646 baris dikembalikan lintas 9 kombinasi toko/channel.
- Fix 18 model gap generasi, konvensi "Outdoor" khusus Otonation, duplikasi SKU Lazada generasi-tunggal (44 produk Crown-family, 30 resolved).
- Fix stok Abu-abu=0 diperluas ke seluruh katalog (0 sisa di semua toko).
- Konsolidasi kode toko di-bake ke MASTER (OT→UA, OP→SP permanen) — 29.145 sel berubah di 46 sheet. **Re-verifikasi penuh 2026-07-10**: user curiga baris Toko='Otonation' dgn SKU prefix 'UA' (mis. Chevrolet Cruze baris 1073) itu bug data-entry. Full scan 69 sheet/59.188 baris (semua toko) ketemu: 100% baris Otonation pakai prefix UA (16.165/16.165), 100% baris Otoprotection pakai prefix SP (12.980/12.980), 0 baris "unexpected segment", 0 baris konsolidasi yg SKU-nya beda dari sibling UA/SP row — kesimpulan: pola itu BY DESIGN (sesuai aturan #1), bukan bug, dan konsolidasinya 100% konsisten tanpa sisa anomali di seluruh master.
- Deliverable "100 Mobil Terlaris": 18.358 baris teoretis → divalidasi ke 31.224 SKU real dari 82 file operasional → 16.672 (90,8%) terkonfirmasi real, sisanya ditandai "Belum Terkonfirmasi". File ini hidup DI LUAR folder proyek utama (per export 2026-07-08 ada di subfolder "Dari Downloads (di luar folder proyek asli)").

**Belum selesai / sengaja ditunda:**
1. Gap Transparan-Otonation (master tidak punya SKU kategori Transparan untuk Otonation/Undercover).
2. ~51 model + ribuan baris "bare-color-only" di Otoprotection/Smartprotection-TikTok (listing cuma 1 dimensi varian warna, tanpa pilihan generasi) — daftar ada di file "Model Perlu Update Manual (Otoprotection & Smartprotection-TikTok).xlsx".
3. 14 produk Crown-family-like yang generasinya genuinely butuh riset manual (Chevrolet Aveo/Cruze, Dodge Journey, Kia Sedona/Carnival, Mazda 3/3 Sedan, Nissan Teana, Toyota CHR/Corona/Nav1/Previa, VW Golf, Suzuki Forsa). **UPDATE 2026-07-09: cakupan bug ini jauh lebih besar dari 14 produk** — lihat item 8.
4. 26 produk di luar folder "166 Model Baru" dengan bug sama (generasi tunggal Lazada) tapi master sudah lengkap — tinggal eksekusi mekanis.
5. 132 SKU duplikat pre-existing (Daihatsu Ayla, Wuling BAO — sengaja 1 SKU untuk 2 generasi, butuh keputusan user) + 180 SKU invalid pre-existing di Smartprotection — belum diaudit.
6. 47 sheet merek di master masih KOSONG TOTAL (Volkswagen, Lexus, Jeep, Land Rover, Peugeot, Volvo, Porsche, Audi, Ferrari, dll) — akar penyebab utama baris yang belum bisa dapat SKU. Isi merek volume-tinggi dulu kalau mau naikkan coverage.
7. Belum cross-verify file listing e-commerce lama vs kode toko master yang baru dikonsolidasi (poin 1 di [[project-undercover-sku-sync-rules]]) — kemungkinan sudah konsisten tapi belum dicek eksplisit.
8. **(Baru 2026-07-09) Bug "SKU generasi ketiban generasi lain" jauh lebih luas dari item 3** — user spot-check 1 produk (Chevrolet Cruze SP, lihat pola: baris "Gen 2" pakai SKU baris "Gen 1"-nya persis) di file listing Smartprotection yang baru diupload (`List Produk Smartprotection/Informasi Penjualan 1&2 Shope(e) Smartpro.xlsx`, `Semua informasi TikTok Smartpro.xlsx`, `Stok & Harga Lazada Smartpro.xlsx`). Full scan (21.372 baris, 4 file) ketemu 3 sub-pola berbeda, total ~91 produk terdampak:
   - **392 baris / 28 produk** — warna reguler/strip berbagi SKU antar-generasi (Shopee+TikTok, bukan Lazada). Dari situ: 70 baris bisa diperbaiki mekanis SEKARANG (master sudah punya SKU generasi lain yg benar, termasuk Cruze warna Hijau Army/Orange kategori Reguler); 167 baris master-nya sendiri belum punya SKU generasi lain (extends item 3 — daftar produk lengkap ada di laporan HTML, bukan cuma 14); 155 baris pakai kode SKU LEGACY gaya `CVR00xx-STP-...` yang sama sekali di luar format master (mis. Peugeot 306, Toyota 86, BMW X5) — kemungkinan produk ini belum pernah dimigrasi ke sistem SKU standar sama sekali.
   - **234 baris / 61 produk** — kategori Transparan: SATU SKU dipakai untuk SEMUA generasi sekaligus (bukan cuma 2, kadang sampai 11 rentang tahun berbagi 1 SKU, mis. Toyota Corona/Mitsubishi Galant). 56/61 pakai kode legacy `CVR00xx-STP-RTP`, cuma 5 yang format standar (Honda Mobilio, Hyundai Avega Sedan, Kia Sportage, Nissan Serena, Toyota Yaris).
   - **29 baris / 2 produk** — gap murni bukan duplikat (SKU memang belum pernah diisi): Chevrolet Aveo Gen 2 (semua 14 warna) dan Toyota Corolla Gen 1-5 (1966-1987, cuma Gen 6 yang ada SKU-nya).
   - Sanity-check terpisah: 1.246 baris "Tahun Lain" + 28 baris "Model Lain" dengan SKU kosong itu BUKAN bug — sesuai aturan #4 di [[project-undercover-sku-sync-rules]], sengaja dikosongkan.
   - Temuan sampingan: kolom "Seller SKU" Lazada 27% (2.078/7.614 baris) isinya ID auto-generate Lazada sendiri (pola `{product_id}-{sku_id}-{n}`), bukan SKU kita — artinya SKU asli belum kepasang sama sekali di baris-baris itu, beda masalah dari duplikasi di Shopee/TikTok, belum diaudit detail per produk mana saja yang kena.
   - Laporan detail (91 produk, per-kategori, per-channel) ada di artifact HTML yang dibuat sesi 2026-07-09 — kalau sudah tidak ada di riwayat chat, ulangi scan-nya (skrip Python ada di scratchpad sesi itu, tidak persisten, kemungkinan perlu ditulis ulang).
   - **Bug yang sama TIDAK cuma di Smartprotection — dikonfirmasi juga di Undercover (UA).** User cek langsung tampilan Shopee seller-center (screenshot live) untuk Chevrolet Cruze Reguler-UA: Gen 1 (2008-2016)/Gen 2 (2015-2024), hampir semua warna berbagi SKU sama persis antar generasi (kode `CVR0026-UC-...`). Terverifikasi juga di file export baru (`List Produk Undercover/Informasi Penjualan Shopee Undercover 3.xlsx` baris 2072-2099, kategori Exclusive di file 4 baris 949-950). **Penting:** SKU yang benar-benar LIVE/dipakai toko untuk Cruze adalah format lama `CVR0026-UC-...`, BUKAN format master `CHV-CRU-SP-...` — jadi untuk produk-produk lama begini, master belum tentu representasi SKU yang sungguh dipakai operasional.
   - **(2026-07-09) SCAN LENGKAP 4 TOKO SELESAI** — total 503 kombinasi (toko × produk) bermasalah, 3.836 baris. Breakdown per toko (kombinasi produk bermasalah): Otonation 269, Undercover Autocare 205, Otoprotection 23, Smartprotection 6 (SP kelihatan kecil karena sebagian besar isu SP sudah masuk hitungan bug-duplikat/legacy yang lebih detail di item 8 atas, angka 6 ini spesifik hasil konsolidasi lintas-toko). Daftar prioritas lengkap (diurut ranking [[[MOBIL TERLARIS - Status Update SKU.xlsx]]] — **file ini basi, jangan percaya warnanya**, tapi rankingnya masih valid) ada di `MASTER_PRIORITY.csv` di scratchpad sesi 2026-07-09 — tidak persisten, perlu diulang dari 4 skrip scan (scan_store.py, scan_mismatch.py per toko, consolidate_all.py) kalau sesi baru.
   - **Ketemu jenis bug KEDUA yang lebih halus 2026-07-09**: bukan cuma "SKU sama persis dipakai ≥2 generasi" (bug A), tapi juga "nomor generasi di SKU geser dari label aslinya" (mis. BMW Seri 3 Undercover, warna Epic Abu: Gen 2 pakai kode G1, Gen 3 pakai G2, dst — geser -1 terus). User sempat kira ini false positive karena screenshot cek manualnya kebetulan cuma sampai warna yang benar (Abu-abu, Elite Abu). Lihat [[feedback-undercover-sku-sync-lessons]] untuk detail metodenya. Hasil per toko (baris geser, distinct produk): SP 318/11, UA 241/21, OP 211/15, OT 166/16.
   - **Insight penting: mobil TERLARIS (top ~35 ranking) ternyata isu-nya relatif KECIL & SERAGAM** — hampir semua cuma butuh 1 perbaikan kecil di kategori Transparan (1 SKU dipakai utk semua generasi, ganti jadi per-generasi). Yang isu-nya BESAR/berat (ratusan baris, format legacy) justru di ranking menengah-bawah (BMW Seri 3 #43, Mini Cooper #64, Toyota Land Cruiser #66 — SKU-nya literal teks "SKU", belum diisi sama sekali, dikonfirmasi user via screenshot). Toyota Yaris (#33) kasus istimewa — ~130 baris bermasalah gabungan 4 toko, kemungkinan karena banyak sub-model (Yaris/Yaris Cross) tercampur.
   - **MULAI EKSEKUSI PERBAIKAN 2026-07-09** (user pilih opsi: buat/pakai SKU master untuk produk terlaris SELAIN yang di-highlight hijau; skip listing arsip seperti Innova Premium pid 16991650252 yang ternyata produk diarsipkan). **SELESAI & terverifikasi (semua di Undercover Shopee, folder tanpa-tanggal `List Produk Undercover/`):**
     - BMW Seri 3 Reguler (Shopee-4, pid 11536464842): warna Epic Abu geser -1, 6 baris → G1-G7 benar.
     - Mini Cooper Reguler+Exclusive (Shopee-4, pid 8915986263 & 8319792695) + Premium (Shopee-3, pid 23013721487): 48+6 baris legacy `CVR0086-UC-*` → master `MNI-COO-UA-*`. Master pisah "MINI Cooper" (sub-model Clubman/Countryman/Hatch/Paceman/Roadster; Reguler cuma Paceman+Roadster) dari "MINI Countryman" (produk terpisah). User konfirmasi via screenshot.
     - Toyota Land Cruiser Reguler+Exclusive (Shopee-3, pid 25282411420 & 24650511699): 90 baris, SKU sebelumnya literal "SKU" (kosong) → master `TYT-LCR-UA-*`. Master pakai kode chassis J60=G1...J300=G5.
     - Toyota GR 86: (a) FIX MASTER — 66 baris label typo `Gen 2`→`Gen 1` untuk tahun 2012-2020 (kolom Generasi + Nama Bigseller; SKU sudah benar G1, TIDAK disentuh). (b) FIX LISTING Shopee-3 Reguler (pid 23556427670) + Exclusive (pid 20593673419): 45 baris legacy `CVR0169-UC-*` → `TYT-G86-UA-*`.
   - **FALSE POSITIVE dari detektor "geser generasi"** (jangan buang waktu): Ford Fiesta & Nissan March pakai kode generasi-GABUNGAN resmi (`G13`=Gen 1-3, `G45`=Gen 4-5, `G23`=Gen 2-3) — detektor salah baca "G13" sebagai generasi-13. Sudah cocok 100% dengan master, BUKAN bug. Selalu cek master dulu sebelum "perbaiki" produk dari daftar mismatch.
   - **BELUM SELESAI / butuh keputusan user:**
     - Suzuki Carry Pickup (#69): master pisah jadi 2 produk ("Suzuki Carry Futura" Lama 1991-2019 & "Suzuki New Carry Pick-Up" Baru 2019-2026), masing-masing cuma 5 warna dasar TANPA tier Strip. Listing punya 6 generasi bernomor (Gen 6-11, 1976-2024) + warna Strip. Gen 6-8 (1976-1991) & semua warna Strip TIDAK ADA di master → perlu keputusan mapping + apakah bikin SKU baru.
     - GR 86 sisa listing (BELUM diperbaiki, heterogen): Premium ada 2 listing beda (Shopee-1 pid 43954650210 SKU kosong+ada warna; Shopee-4 pid 14498231102 single-color ambigu); TikTok Reguler/Premium/Exclusive banyak SKU kosong + 1 baris Gen1 salah G2; Lazada pakai placeholder ID Lazada. Belum disentuh.
     - Belum dicek lawan master: Toyota Yaris, Hyundai Ioniq 5, Honda City Hatchback, Nissan X-Trail, Toyota Vellfire, Daihatsu Feroza, Honda CRV (semua channel Lazada/TikTok, bukan Shopee).
   - Backup tiap file disimpan di scratchpad sesi (`BACKUP*`) sebelum diedit. Skrip fix: fix_bmw_seri3.py, fix_mini_cooper.py, fix_mini_premium.py, fix_land_cruiser.py, fix_gr86_master_label.py, fix_gr86_listing.py.
   - **(2026-07-09) PIPELINE BATCH-FIX dibangun & dijalankan** (`pipeline.py` + `apply_fix_plan.py` di scratchpad) untuk 86 produk UA sisa (kategori Reguler, 5 file Shopee Undercover). Metode: cocokkan (warna, tahun-mulai-persis) listing↔master, kategori Reguler/Strip ditentukan dari nama warna. **Wajib exact-year-match, JANGAN overlap/nearest** — overlap match terbukti salah tempel di batas tahun (Mercedes B Class "Gen 3F 2023-2024" salah nempel ke master "Gen 3" yang berakhir 2023). **Wajib cek tabrakan SKU-tujuan otomatis per produk** (>=2 baris beda dituju ke SKU sama = master tidak reliable, demote ke NEEDS_DECISION, jangan auto-fix) — pengecualian: baris "Model/Tahun Lain" yang sama-sama dikosongkan (None) BUKAN tabrakan. Hasil: **62 produk / 3.612 baris berhasil di-fix & terverifikasi** (baca-ulang dari file, 0 mismatch, 0 duplikat SKU per produk). **24 produk masih NEEDS_DECISION**: 8 nama produk tidak ketemu sama sekali di master (Ford Fusion, Mercedes G Class, Mitsubishi Eclipse, Nissan Livina XGear, Peugeot 306, VW Fox, VW Passat + 1 lagi), 16 punya baris dengan tahun listing yang tidak persis cocok generasi manapun di master (termasuk **Chevrolet Cruze** — bukti lain bahwa taksonomi generasi Cruze di master memang belum genuine, konsisten dengan status di [[project-undercover-sku-sync-rules]] soal 14 produk Crown-family). Total UA yang genuinely selesai sekarang: BMW Seri 3, Mini Cooper, Land Cruiser, GR 86 (4 manual) + 62 (batch) = 66 produk. Sisa PR: Suzuki Carry Pickup (keputusan pending), Toyota Yaris/X-Trail/Vellfire/Feroza (keputusan pending), 24 produk NEEDS_DECISION dari batch, dan produk di luar kategori Reguler (Premium/Exclusive/Transparan) yang belum ikut ter-scan pipeline ini.

**(2026-07-10) SEMUA 24 PRODUK NEEDS_DECISION DARI PIPELINE + KASUS PENDING LAINNYA SELESAI DIEKSEKUSI.** User memberi keputusan per kategori (lihat rincian di sesi tsb), semua sudah diimplementasi & diverifikasi ulang dari disk (0 mismatch, 0 duplikat SKU per produk, setiap batch). Ringkasan hasil:
- **Kategori A (typo "Warior"→"Warrior")**: 322 baris, 7 produk (Dodge Journey, Hyundai Excel, Hyundai Stargazer, Isuzu Mux, Nissan Evalia, Toyota Corona, Toyota Previa). Typo yang sama juga ditemukan lagi di Jeep Wrangler saat kerjakan Kategori B.
- **Kategori B (master punya 2 skema SKU konflik utk generasi sama)**: Kia Seltos (Gen1 vs SP2), Mercedes Benz GLS Class (Gen1 vs GL), Jeep Wrangler (kode chassis asli JK/JL/TJ/YJ vs skema generik G1-G4) — semua listing ternyata konsisten pakai SATU skema (yg bukan-generik utk Jeep), jadi skema satunya diperlakukan sbg basi & diabaikan (BUKAN dihapus dari master, cuma tidak dipakai lagi). Bonus temuan: master Jeep Wrangler Premium punya tahun geser 1 tahun dari Reguler/Strip/Exclusive utk chassis sama (JK/TJ/JL) — sudah diseragamkan. Total 186 baris. Mazda 3 Hatchback DILEWATI — user konfirmasi listingnya sudah diarsipkan.
- **Kategori C (tahun master vs listing tidak cocok)**: Chevrolet Cruze (2001-2008/2008-2024 → 2008-2016/2015-2024), Timor (tahun kosong → diisi 1996-2000), Mercedes B Class (tambah "Gen 3 Facelift" 2023-2024 baru, Gen 3 lama diperbaiki jadi 2019-2023), Nissan Kicks (tambah "Gen 1 Facelift" 2021-2024 baru, Gen 1 lama jadi 2016-2021), Toyota Yaris (satu2nya entri master "Gen 1 2023-2026" total salah → diubah jadi Gen1 2006-2013 + Gen2 2014-2026 baru — listing ternyata SUDAH benar dari awal, tinggal tunggu master-nya diperbaiki). Pola "Facelift": Generasi label pakai teks penuh "Gen N Facelift" (bukan cuma kode), SKU suffix pakai kode pendek (G3F/G1F), ikuti presenden Mazda 3.
- **Kategori D (produk sama sekali tidak ada di master)**: 6 produk beneran baru dibuatkan entri (Ford Fusion FRD-FUS, Mercedes G Class MBZ-GCL, Mitsubishi Eclipse MTB-ECL, Peugeot 306 PEU-M306 pakai label "Fase N" bukan "Gen N", VW Fox VLK-FOX, VW Passat VLK-PAS pakai kode chassis asli B1/B2/B3/B5-B9 skip B4). Nissan Livina XGear TERNYATA SUDAH ADA di master dgn nama "Nissan Livina X-Gear" (pakai tanda hubung) — gagal ke-detect sebelumnya krn fuzzy-match substring tidak tahan beda ejaan hubung. **Pelajaran: selalu cek variasi ejaan/hubung sebelum simpulkan "produk tidak ada di master."**
- **Varian bodi terpisah (pola baru ditemukan sesi ini)**: 3 kasus di mana listing punya nama mirip produk master tapi skema generasi/tahun sama sekali tidak nyambung — bukan "kurang 1 generasi" tapi genuinely varian bodi berbeda yang belum pernah punya entri sendiri. User konfirmasi: buat entri master baru berdiri sendiri untuk semua.
  - Hyundai Avega Hatchback (HYN-AVH, Gen3-5, 2005-2022) — terpisah dari "Hyundai Avega" (sedan) yang sudah cocok sempurna dgn master.
  - Daihatsu Feroza Long (DHT-FRL, Gen3-4, 1985-2007) — terpisah dari "Daihatsu Feroza" (sudah cocok sempurna dgn master).
  - Suzuki Carry (SZK-CAR, Gen6-11, 1976-2024) — unifikasi 2 nama listing berbeda ("Suzuki Carry Pickup" & "Suzuki Carry" polos) ke SATU produk master baru; entri lama "Suzuki Carry Futura"/"Suzuki New Carry Pick-Up" dibiarkan ada tapi tidak dipakai lagi.
- **Nissan X-Trail**: aturan dikonfirmasi user — label gabungan ("Gen 1-2 2001-2013") pakai kode generasi TERENDAH. Ternyata 3 dari 4 listing SUDAH benar; cuma 1 listing duplikat (Shopee-4 Premium pid 19669472741) yang masih SKU legacy sama utk 5 generasi — **dikonfirmasi user diarsipkan**, tidak disentuh.
- **Toyota Yaris Shopee-3 pid 21569458396**: dikonfirmasi user diarsipkan (pola sama Innova), tidak disentuh.
- Total pekerjaan hari ini: >1.100 baris listing diperbaiki, ~560 baris master baru dibuat (9 produk/varian baru: Ford Fusion, Mercedes G Class, Mitsubishi Eclipse, Peugeot 306, VW Fox, VW Passat, Hyundai Avega Hatchback, Daihatsu Feroza Long, Suzuki Carry), 3 produk existing dapat generasi baru (Mercedes B Class, Nissan Kicks, Toyota Yaris), semua lewat script ad-hoc di scratchpad (`fix_master_*.py` per kasus + `fix_listing_cruze_timor.py`/`apply_fix_cruze_timor.py` reusable utk semua listing fix — nama file historis dari kasus pertama, isinya sudah general).
- **GR 86 SEMUA CHANNEL SELESAI (lanjutan sesi sama, setelah "oke lanjut")**: Shopee Premium (2 listing, 6 baris — Gen1 listing tertulis "2013" tapi cocok ke master G1 2012-2020 krn tak ada kandidat lain di dekatnya). TikTok (31 baris, 3 dari 4 listing bisa diperbaiki; 1 listing Reguler kedua pid 1731375811678471194 di TikTok-1 baris 13106-13119 TIDAK bisa diperbaiki krn variannya cuma warna tanpa info generasi sama sekali — dibiarkan kosong, kemungkinan listing basi/duplikat). Lazada (34 baris) — proses 2 tahap krn kesalahan awal (lihat [[feedback-undercover-sku-sync-lessons]] soal jangan skip SKU yg "kelihatan benar"): baru ketahuan setelah tahap 1 bahwa 14 baris yang SUDAH berformat `TYT-G86-UA-*` ternyata kena bug geser-generasi juga (label "Gen 2" tapi SKU G1) — baru ketahuan & terfix di tahap 2, re-run tahap 3 hasilnya 0 (konvergen). Semua source SKU Lazada GR86 sebelumnya adalah placeholder auto-generate Lazada (`{product_id}-{sku_id}-{n}`), bukan ID kosong.
- Kolom SKU per channel (penting utk sesi depan): Shopee = kolom F "SKU" (index 6). TikTok = sheet "Template", kolom K "seller_sku" (index 11) — BUKAN kolom D "sku_id" (itu ID internal TikTok). Lazada = sheet "template", kolom M "Seller SKU" (index 13) — kolom G "SKU Lazada" (index 7) itu ID internal Lazada, bukan SKU kita; kolom N "Variations Combo" (index 14) isi teks varian gabungan warna+generasi.
- Lihat [[feedback-undercover-sku-sync-lessons]] utk pola bug baru yang ditemukan sesi ini (kolom warna/tahun terbalik urutan di Premium, false-collision lintas-listing-duplikat, dll).

**(2026-07-11) KOREKSI klaim "Kategori D selesai" di atas — 5 dari 7 produk ternyata cuma sebagian tersinkron, bukan tuntas.** User tanya kenapa Volkswagen Passat Reguler (98 baris) masih kosong SKU-nya di file "Update via Claude". Audit ulang (baca langsung kolom `et_title_variation_sku` tiap listing, bukan percaya angka "154 baris" yang dilaporkan 07-10) ketemu: klaim itu overstated — kemungkinan besar kerja Kategori D terpotong di tengah jalan saat prioritas beralih ke instruksi "331 produk terlaris dulu, semua toko" (lihat [[feedback-undercover-sku-sync-lessons]]), dan 5 dari 7 produk Kategori D itu **tidak ada sama sekali** di `MOBIL TERLARIS - Status Update SKU.xlsx` (dicek eksplisit) sehingga kelewat balik dikerjakan. Status real per produk (OK / kosong / masih SKU legacy lama, dari 5 file Shopee Undercover):
- Ford Fusion: 68 OK / 17 kosong / 0 legacy — hampir tuntas.
- Peugeot 306: 31 OK / 16 kosong / 3 legacy — sebagian besar tuntas.
- Volkswagen Fox: 2 OK / 2 kosong / 30 legacy — baru mulai.
- Volkswagen Passat: 16 OK / 76 kosong / 33 legacy — baru mulai (cuma tier Premium yang beneran tersinkron; Reguler & Exclusive nyaris 0%).
- Mitsubishi Eclipse: 4 OK / 39 kosong / 42 legacy — baru mulai.

"Legacy" = kolom SKU (`et_title_variation_sku`) masih berisi kode lama gaya `CVR0112-UC-...` (bukan format master `MEREK-MODEL-UA-KAT-GEN-WARNA`), bukan kosong — jadi kelihatan "ada isinya" kalau cuma dicek `is not None`, padahal itu bukan SKU yang sudah disinkronkan. Master untuk kelima produk ini SUDAH lengkap semua tier/kombinasi (dicek ulang, tidak ada gap) — yang belum adalah tulis-ke-listing-nya.

**(2026-07-13) KOREKSI BESAR — "HAMPIR SELESAI" utk UA ternyata cuma benar utk Shopee. Lazada & TikTok TIDAK ikut ke-mirror.** User tanya "apa UA sudah selesai?" — dicek langsung, hasilnya:
- **Lazada UA** (`Stok & Harga Lazada Undercover.xlsx`, 22.444 baris total): cuma 6.237 (28%) yang formatnya sesuai master terkini. Sample produk yg sudah difix di Shopee sesi ini (Dodge Journey, Kia Seltos, Chevrolet Cruze, Ford Fusion, Mercedes B Class, Daihatsu Feroza Long — total 300+ baris) HAMPIR SEMUA masih SKU lama/legacy di Lazada — SATU PUN tidak ada yang ke-mirror, KECUALI GR86 (yang memang sengaja dikerjakan semua channel) dan Hyundai Avega Hatchback (75% OK, alasan tidak jelas kenapa ini beda, kemungkinan kebetulan sudah benar dari sebelum proyek).
- **TikTok Undercover file 1** (`Tiktok Semua Informasi Undercover 1.xlsx`, 23.943 baris): PARTIAL & TIDAK KONSISTEN — Chevrolet Cruze 100% OK (34/34), Dodge Journey & Kia Seltos 50% (17/34), GR86 52% (34/65, cocok dgn catatan lama "3 dari 4 listing"), Mercedes B Class cuma 14% (12/85), Ford Fusion 0% (0/85). Total keseluruhan file ~50% (11.914/23.943) — angka ini kemungkinan besar cuma refleksi baseline "sudah benar dari sebelum proyek" utk sebagian produk, BUKAN hasil kerja sesi ini.
- **TikTok Undercover file 2 & 3**: belum dibuka sama sekali.
- **Kesimpulan**: pipeline batch-fix Kategori A-D sesi 07-09/07-10 SECARA EKSPLISIT cuma nulis ke "5 file Shopee Undercover" (lihat catatan pipeline di atas) — TIDAK PERNAH menyentuh Lazada/TikTok. Jadi ratusan produk yang sudah "selesai" di Shopee kemungkinan besar MASIH SALAH di Lazada & sebagian TikTok. Ini scope kerja baru yang besar, belum pernah dihitung/direncanakan sebelumnya.

Why: user hampir menganggap UA "selesai" berdasar chip laporan yang cuma bicara ttg Shopee — nyaris kejadian yang sama seperti VW Passat (klaim selesai yg ternyata parsial). How to apply: JANGAN pernah bilang toko/channel "selesai" tanpa cek eksplisit SEMUA channel (Shopee+TikTok+Lazada) — kalau kerjaan sesi tertentu cuma nyentuh 1 channel (spt pipeline yg cuma Shopee), sebutkan itu eksplisit di laporan, jangan biarkan pembaca menyimpulkan channel lain ikut beres.

**(2026-07-13) Gap kategori Transparan Otonation TERNYATA MAYORITAS masuk 331 terlaris (96%).** Cross-check eksplisit: dari 185 produk berkategori Transparan tanpa SKU di listing OT (643 baris total, lebih besar dari perkiraan lama "~269+"), **178 produk (96%) ADA di 331 terlaris** — cuma 7 non-terlaris (Volkswagen Fox, Volkswagen Passat, Mitsubishi Eclipse, Peugeot 306, Ford Fusion, Ford Everest, + "Toyota 86" yg kemungkinan false-negative nama vs "Toyota GR 86" yg terlaris). Artinya gap Transparan ini SEHARUSNYA prioritas tinggi (bukan "ditunda dulu" santai) kalau konsisten dgn instruksi "terlaris dulu, semua toko" — beda dari kesan sebelumnya bahwa ini "utang lama" yang boleh nunggu lama.

**Mercedes Benz G Class (produk ke-6 dari Kategori D asli) BEDA — ternyata MASUK terlaris (rank #167 di "MOBIL TERLARIS - Status Update SKU.xlsx")**, jadi langsung diperbaiki 07-11, bukan ditunda: 30 baris Reguler+Exclusive (Premium sudah benar dari 07-10) diubah dari SKU legacy `CVR0117-UC-*` ke format master `MBZ-GCL-UA-*`. Hasil akhir produk ini: 34 baris benar, 2 blank (Premium "Model Lain/Custom", memang tidak ada target master), 15 masih legacy (SEMUA baris "Model/Tahun Lain" tanpa generasi eksplisit — sama seperti pola blank di produk lain, tidak ada target master utk kategori "any year", sengaja dibiarkan). 0 duplikat SKU. **Pelajaran: sebelum menunda suatu produk sbg "non-terlaris", cek satu-satu — jangan asumsikan semua anggota 1 batch kerja (mis. "7 produk Kategori D") berstatus sama.**

**Sengaja BELUM dikerjakan 07-11** — user eksplisit minta fokus ke produk yang ada di 331-terlaris dulu; kelima produk SISANYA ini (di luar G Class) genuinely tidak ada di ranking itu. Jadi diturunkan ke prioritas paling akhir, konsisten dengan aturan di [[feedback-undercover-sku-sync-lessons]] soal produk non-ranking. Kalau lanjut nanti: polanya seragam (5 warna Reguler + 9 warna Strip [Elite/Epic/Warrior × Abu/Biru/Merah] + 2 warna Premium + 1 warna Exclusive, per generasi/chassis/fase — sama persis strukturnya cuma label generasi beda: Ford Fusion="Gen N"/"Gen 2F N", Peugeot 306="Fase N", VW Fox="Gen 1" doang, VW Passat="B1/B2/B3/B5-B9", Mitsubishi Eclipse="Gen 1-4"), master sudah siap tinggal tulis-ulang listing pakai lookup langsung ke master per (kategori,warna,generasi) — sudah ada draft logika parsing di scratchpad sesi ini (belum sempat dieksekusi).

**(2026-07-13) Lazada UA — 11.901 baris diperbaiki (propagasi dari fix Kategori A-D di Shopee), format-OK naik dari 28% ke 65%.** Dibangun pipeline generik (`lazada_pipeline2.py`) yg reuse logic dari `pipeline.py` (exact-year-match, kategori dari suffix nama produk, fallback warna utk tier campuran Reguler/Strip) + tambahan **normalized-name alias matching** (`norm()` = buang semua non-alfanumerik lalu substring-match) utk tangani alias hubung/spasi kayak "Honda WRV" (listing) vs "Honda WR-V" (master) — pola yg sama kayak temuan lama "Nissan Livina XGear vs X-Gear", ternyata juga banyak muncul di Lazada (WR-V/BR-V/CR-V/HR-V semua kena).
- Tabrakan SKU dicek per-produk sebelum apply: 1 produk (**Wuling Baojun 310**, 51 baris) dikecualikan krn Gen1 vs Gen1F nabrak ke SKU sama dalam SATU listing (bukan pola "2 pid beda", genuinely ambigu) — didemote ke NEEDS_DECISION, tidak di-auto-fix.
- **Bug baru ditemukan & dicatat sbg pelajaran**: `ws.cell(row=r, column=c, value=None)` di openpyxl **TIDAK mengosongkan cell** — method `cell()` py signature `value=None` sbg default "tidak diisi", jadi kalau eksplisit passing `value=None` untuk mengosongkan, itu DIABAIKAN (cell tetap nilai lama). Ketahuan dari re-verifikasi (3.323 baris "Model/Tahun Lain" yg seharusnya dikosongkan ternyata masih nilai lama, padahal 8.578 baris dgn SKU asli berhasil ditulis). Fix: HARUS pakai `cell = ws.cell(row=r, column=c); cell.value = None` (attribute assignment eksplisit), bukan lewat parameter method.
- **Gap terpisah & JAUH lebih besar ditemukan**: 232 produk unik (3.952 baris) di Lazada **sama sekali tidak ada di master untuk toko manapun** — brand-brand premium/mewah (Lexus, Audi, Bentley, Maserati, Aston Martin, Lamborghini, Rolls Royce, Volvo, Tesla, dst) + beberapa mainstream (Kia Sorento, Isuzu D-MAX). Ini BUKAN gap sinkronisasi (bukan soal "listing vs master beda"), tapi produk yg dijual di Lazada TANPA PERNAH py entri master SAMA SEKALI. Scope-nya beda dari tugas "mirror fix Shopee" — didokumentasikan terpisah, TIDAK dikerjakan sesi ini (butuh keputusan user: mau dibikinkan master barunya atau tidak, mengingat sebagian brand ini kemungkinan bervolume rendah).
- **Sisa NEEDS_DECISION lain (~1.452 baris)**: variasi "tahun tidak persis cocok generasi manapun" (kemungkinan tahun listing Lazada beda dari Shopee utk produk yg sama — belum diinvestigasi kenapa) + beberapa produk dgn >1 kandidat master SKU beda utk tahun yg sama (kemungkinan sisa duplikasi taksonomi generasi lama).
- **TikTok UA** (`Tiktok Semua Informasi Undercover 1.xlsx`, belum diperbaiki, baru diaudit): coverage 50% agregat tapi SANGAT tidak konsisten per produk (0%-100%) — perlu pipeline serupa, kolom target `seller_sku` (index 11, 1-based kolom K), belum dieksekusi.

Why: dicatat granular per-item karena tiap item butuh keputusan/effort beda — sebagian nunggu keputusan user (item 5), sebagian tinggal eksekusi mekanis (item 4), sebagian butuh riset manual (item 3).

How to apply: kalau user minta "lanjutkan SKU sync," tawarkan pilihan dari list di atas alih-alih menebak prioritas. Cek dulu apakah script engine (engine.py, build_all.py, build_pilot.py, gen_word_all.py, xlsx_loader.py, split_files.py) ada di working directory sesi ini — riwayatnya, script ini TIDAK ikut ter-export/persisten antar sesi (hanya hidup di scratchpad sementara; terkonfirmasi tidak ada satupun di export 2026-07-08), jadi kemungkinan besar harus direkonstruksi ulang dari nol mengikuti [[project-undercover-sku-sync-rules]] + dokumen `CATATAN Sinkronisasi SKU - Semua Merek.docx` (bagian "Cara Kerja"/"Catatan Teknis") sebelum bisa lanjut ke item manapun di atas. Jangan asumsikan dari memory ini bahwa engine pasti tidak ada — cek langsung (Glob) karena bisa saja user sudah membuatnya lebih tahan-lama sejak catatan ini ditulis.

**(2026-07-15, sesi cloud) LOMPATAN BESAR — scope diperluas dari "331 terlaris" ke SELURUH katalog, 4 toko sekaligus, via lookup master penuh 69 sheet.** Konteks: sebelumnya kerja SKU sync di-scope ke 331 produk terlaris dulu (lihat catatan-catatan di atas). Sesi ini (setelah user upload master asli langsung & minta lanjut sync ke file operasional per toko) dibangun ulang dari nol infrastrukturnya:
- **`master_lookup_full.json`** (scratchpad, tidak persisten) — lookup `(model, kategori, generasi, warna) -> SKU` dari SEMUA 69 sheet brand, filter `Toko == "Undercover Autocare"`, dipakai untuk UA & OT (yang berbagi SKU prefix UA). 61.628 baris master total discan, 17.249 entri lookup UA. **Bug infrastruktur penting yang ditemukan & diperbaiki**: sheet "Suzuki" (3.372 baris) awalnya ke-skip total dari lookup karena cek header terlalu ketat (`hdr[0] != 'No'`, padahal kolom A sheet Suzuki kosong) — diperbaiki jadi cek `hdr[1] == 'Nama Produk'` (kolom B, universal di semua 69 sheet).
- **`master_lookup_sp.json`** (scratchpad) — sama tapi filter `Toko == "Smartprotection"`, dipakai untuk OP & SP (berbagi SKU prefix SP). 14.303 entri lookup. Nama model & daftar generasi (`master_model_names_sp.json`/`master_gens_by_model_sp.json`) IDENTIK dengan versi UA (diverifikasi eksplisit) karena kolom Nama Produk/Generasi tidak toko-spesifik — cuma ketersediaan SKU yang beda.
- **OT (Otonation) — semua-brand, bukan cuma 331-terlaris**: file `Informasi Penjualan Shopee Otonation 1 & 2.xlsx` di-scan penuh (bukan cuma terlaris). Hasil akhir: File1 647 baris update + 2.514 sudah benar (dari ~4.100), File2 445 update + 1.859 benar. Bug klasifier yang ditemukan & diperbaiki sesi ini (lihat [[project-undercover-otonation-status]] untuk daftar alias/typo lengkap): puluhan alias merek/model baru, bug default warna "Abu-abu" utk kategori Exclusive yang seharusnya kosong (master Exclusive warna-nya selalu `None`), typo listing (HIsuzu Mux, Toyota Toyota Hardtop, spasi hilang "MobilSuzuki"), salah alias "Suzuki Carry Pickup" (bukan ke "Suzuki New Carry Pick-Up" tapi ke "Suzuki Carry" polos yang py Gen6-11).
- **OP (Otoprotection) — PERTAMA KALI disentuh dengan lookup penuh** (sebelumnya cuma 331-terlaris, Shopee saja). Sesi ini: Shopee1 (51 update+3.553 benar), TikTok1 (66 update+3.535 benar), TikTok2 kosong. Struktur & mapping warna sesuai [[project-undercover-otoprotection-status]] (Strip-N native, no Premium/Exclusive). **Temuan besar**: 109 model ternyata SAMA SEKALI tidak punya varian generasi di listing (cuma warna) — pola yang sebelumnya cuma diketahui utk 3 produk (Suzuki Carry Pickup/Mercedes G Class), ternyata jauh lebih luas. Dicatat di `Produk_Perlu_Keputusan_Manual.xlsx`.
- **SP (Smartprotection) — PERTAMA KALI disentuh dengan lookup penuh** (sebelumnya cuma 331-terlaris, Shopee saja). Sesi ini: 4 file sekaligus (Shopee1: 73 update+2.314 benar; Shopee2: 22+1.411; TikTok: 71+3.714; Lazada: 78+3.689). Konfirmasi arah mapping SP: listing pakai teks Elite/Epic/Warrior (kayak UA/OT) tapi master SP simpan sbg Strip1/2/3 (kayak OP) — arahnya Epic→Strip1, Elite→Strip2, Warrior→Strip3. Temuan sama seperti OP: ~105 model tanpa varian generasi di listing.
- **File `Produk_Perlu_Keputusan_Manual.xlsx`** (dikirim ke user, scratchpad) — tracker terpusat semua kasus yang butuh keputusan manual (bukan bug klasifier): produk tanpa varian generasi (109 OP + 105 SP model), model genuinely tidak ada di master (Nissan Latio, Chevrolet Estate Magnum, Toyota FJ Cruiser, Hummer H3, dll), 2 kasus salah brand di listing SP (Honda Fortuner harusnya Toyota, Suzuki Agya harusnya Toyota), + item lama dari sesi 07-14 (Lexus NX/LX/RX skema generasi ganda, dll).
- **Kuirk teknis openpyxl ditemukan & diverifikasi aman**: resave workbook TikTok (sheet "Template", banyak kolom opsional selalu kosong) mengubah sel `''` (string kosong) jadi `None` di ribuan sel yang TIDAK disentuh — sudah diverifikasi 2x (OP & SP) bahwa 100% diff di luar kolom SKU persis pola ini (tidak ada perubahan data lain), dan bahkan di KOLOM SKU sendiri sebagian diff adalah `''→None` utk baris yg SKU-nya memang masih kosong (bukan salah-ubah). Aman untuk upload ulang ke TikTok, tapi tetap diinfokan ke user demi transparansi.
- Semua file dikirim ke user via chat dengan nama baru (`... - SYNCED.xlsx` / `- SYNCED v2.xlsx`), tidak menimpa file asli, sesuai aturan kerja.
- **BELUM DIKERJAKAN sesi ini**: TikTok UA (masih terhambat ukuran file >4MB, nunggu upload manual user), Lazada OT (belum disentuh sama sekali), Lazada OP (belum disentuh), gap Transparan struktural lama (masih dideferred), ~1.000-an baris NO_LOOKUP di tiap toko yang butuh riset chassis-code-ke-Gen-N manual (mis. Mercedes W-code, BMW E/F/G-code, VW B-code — skema chassis eropa vs skema "Gen N" master, tidak ada pemetaan otomatis yg aman ditebak).

Why: dicatat detail karena ini pertama kalinya OP & SP disentuh di luar scope 331-terlaris, dan infrastruktur lookup-nya (SP-toko-filtered) baru dibangun sesi ini — sesi depan tidak perlu bangun ulang dari nol kalau baca catatan ini dulu.

**(2026-07-15, sesi lokal PC) Sesi cloud di atas (`session_01NQ1bq2AiYDdpsH13oEgfGe`) ternyata push ke branch terpisah `claude/repo-memory-access-4hthja`, BELUM di-merge ke `main`** — user paste ringkasan sesi itu ke sesi lokal ini tanpa sadar itu sesi/device terpisah, sempat bingung file mana yg harus ditaruh dimana. File Shopee/Lazada/TikTok yg "dikirim via chat" (15 file `-SYNCED`) TIDAK bisa diambil dari sesi lokal ini (beda sesi = tidak ada akses file). User perlu ambil manual dari sesi cloud itu sendiri.

**Master file "asli" yang dipakai sesi cloud sbg input (`SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx`, ketemu di Downloads user 07-14 14:28, size 3.499.027 byte) py ANOMALI yg belum terjawab**: dibanding versi lama (`Update via Claude\SKU, Price, Tracking Cover Mobil.xlsx` 07-11), 5 sheet brand mewah bertambah net +1.836 baris (Lamborghini/Lexus/Maserati/Tesla/Volvo — cocok dgn 26 model baru di `master_baru_5brand.csv` yg juga ada di Downloads, "13 model mewah" versi user). Tapi 6 sheet lain BERKURANG:
- Ford/Mitsubishi Motors/Peugeot/Volkswagen: **aman** — SKU unik identik lama vs baru (`comm -23` dua list SKU ter-sort = 0 selisih), yg hilang murni baris duplikat (konsisten dgn kerja "Audit Duplikasi SKU" yg emang berjalan).
- **Mercedes-Benz: 44 SKU BENERAN hilang** (bukan duplikat) — seluruh "Mercedes Benz EQE" Gen 1 (4 toko x semua kategori) + "Mercedes Benz G Class" kategori Strip Gen1&2 (khusus Otoprotection+Smartprotection).
- **Suzuki: 54 SKU BENERAN hilang** — seluruh "Suzuki Carry" kategori Strip Gen6-11 (khusus Otoprotection+Smartprotection).
- **Konteks penting**: "Suzuki Carry Pickup" & "Mercedes Benz G Class" adalah 2 dari [[project-undercover-otoprotection-status]] NO_MASTER gap yg ditemukan 07-11 (waktu itu G Class BENAR² tidak py entri master sama sekali). Jadi entri Strip G-Class/Carry yg hilang di file 07-14 ini kemungkinan adalah FIX yg sempat ditambahkan ke master antara 07-11 dan 07-11 10:15 (jam save `Update via Claude` versi lama), lalu KETIMPA HILANG lagi oleh proses yang bikin file 07-14.

**KEPUTUSAN USER (2026-07-15): ke-3 item WAJIB dikembalikan** — "itu nanti untuk pondasi kerangka produk", jadi bukan discontinue yg disengaja. **Sudah dieksekusi & selesai** hari yang sama: 44 baris Mercedes-Benz (EQE Gen1 semua toko + G Class Strip Gen1&2 OP/SP) + 54 baris Suzuki (Carry Strip Gen6-11 OP/SP) — di-copy PERSIS (verbatim, cuma renumber `r=` cell reference, bukan re-generate) dari backup `.bak_20260715_114443` (versi 07-11, sebelum ke-drop), di-append ke akhir sheet Mercedes-Benz (row 2854-2897) & Suzuki (row 3373-3426) via manipulasi XML langsung (saat itu tidak ada Python/openpyxl/LibreOffice di device ini — semua 3 dicek, tidak ada satupun terinstall).

**(2026-07-15, lanjutan) Ke-15 file dari sesi cloud sudah diambil user (download manual) & ditaruh semua ke `Update via Claude\` + Drive.** File master yg didownload ulang (`SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx`, versi jam 14:50) ternyata beda dikit dari versi pagi — tambahan 26 baris di sheet Lexus (13 SKU unik x 2 toko UA+OT): varian warna **Orange** utk Lexus NX/RX/LX (ini yg dimaksud "+ Orange" di deskripsi awal user, terpisah dari lompatan 5-brand mewah yg sudah diproses duluan). Di-merge pakai openpyxl (bukan XML manual lagi) ke master yg sudah py restorasi EQE/G-Class/Carry — tidak saling menimpa krn beda sheet. Hasil akhir master: 69 sheet, Mercedes-Benz 2897 baris, Suzuki 3426 baris, Lexus 2336 baris, semua terverifikasi via openpyxl.

14 file operasional (Shopee Undercover 1-5, Lazada Undercover, Shopee Otonation 1-2, Shopee Otoprotection 1, TikTok Otoprotection 1, Shopee Smartpro 1-2, TikTok Smartpro, Lazada Smartpro) sudah ditimpa ke folder `Update via Claude\List Produk {Brand}\` masing2 (nama persis sesuai file lama, semua di-backup dgn suffix `.bak_TIMESTAMP` dulu sebelum ditimpa). Semua 15 file (master+14) sudah di-copy juga ke `G:\My Drive\...\Update via Claude\` yg sama, dikonfirmasi lewat Drive API sudah naik ke cloud (bukan cuma mount lokal).

**Belum berubah**: TikTok UA (nunggu upload manual user, file besar), Lazada Otonation, Lazada Otoprotection — 3 ini masih exactly seperti sebelumnya, sesi cloud belum menyentuhnya.

How to apply: kalau user tanya status terkini, semua 15 file dari batch "SYNCED" hari ini SUDAH ada & current di lokal+Drive per 2026-07-15 sore. Fokus berikutnya: cross-check apakah 2 SKU (G-Class-Strip/Carry-Strip) yg baru direstore sudah ke-resolve dgn benar di file2 operasional OP/SP ini (sesi cloud yg generate file2 itu build lookup-nya SEBELUM restorasi ini ada).

**(2026-07-15, update) Python 3.14.6 + openpyxl 3.1.5 sudah terinstall user di PC ini setelah sesi di atas** (`python -m pip install openpyxl` — pip bukan command terpisah di PATH, harus lewat `python -m pip`). LibreOffice/`soffice` & `pandas`/`markitdown` masih belum dicek ulang setelah ini. **Sesi depan: pakai [[skill xlsx]]/openpyxl seperti biasa untuk kerja spreadsheet di device ini, TIDAK perlu lagi manual XML surgery** (pendekatan darurat sesi ini terbukti jalan tapi rawan bug — sempat ada regex renumber yg salah rusak isi SKU, ketangkap sebelum diterapkan, lihat catatan script di atas). Live-listing Shopee toko Undercover Autocare TIDAK bisa diverifikasi langsung (domain shopee.co.id diblokir kebijakan browser tool + halaman render JS jadi WebFetch kosong) — restorasi berbasis data historis exact-match, bukan verifikasi live.

---
**(2026-07-15, CROSS-CHECK restorasi + SURVEI sync — hasil lengkap)**

**Struktur file operasional (dikonfirmasi via openpyxl):**
- Shopee (semua toko): sheet `Sheet1`, Nama Produk kolom B(2), Nama Variasi kolom D(4), SKU kolom F(6), data mulai row 7.
- TikTok (semua toko): sheet `Template`, product_name kolom C(3), variation_value kolom E(5), seller_sku kolom K(11), data mulai row 6.
- Lazada: sheet `template`, Seller SKU kolom M(13), data mulai row 5.

**Cross-check G-Class/Carry/EQE Strip di file operasional (apakah restorasi master perlu propagasi?):**
- **SP Shopee 1**: G Class & Carry SUDAH terisi (28/42), pakai SKU master scheme prefix UA (`MBZ-GCL-UA-S-G1-S1A`). Yang kosong (14) HANYA varian ",Tahun Lain" (tanpa generasi spesifik → wajar kosong). Tidak perlu aksi.
- **OP TikTok 1 & SP TikTok**: G Class/Carry/Carry-Pickup terisi PENUH (15/15, 14/14). Info generasi ADA di variation_value TikTok jadi bisa auto-map. Kosong cuma di varian "Transparan …Tahun Lain".
- **OP Shopee 1**: G Class/Carry/Carry-Pickup SEMUA kosong (15 variasi masing2). SEBABNYA: variation_value OP Shopee TIDAK punya info generasi (cuma "Strip 1 Abu", "Merah", "Orange" — tanpa tahun/gen). Ini kasus "produk tanpa varian generasi di listing" (109 model OP) yg per keputusan user 07-11 SENGAJA dikosongkan (tidak bisa ditebak generasinya). BUKAN akibat gap master, BUKAN fixable oleh restorasi. Konsisten benar.
- **Kesimpulan cross-check**: restorasi master (98 baris) penting utk KELENGKAPAN MASTER (pondasi), tapi file operasional TIDAK kehilangan SKU — sudah terisi dari sesi2 sebelumnya (sebelum drop 07-14). Drop 07-14 cuma kena file master, tidak meng-hapus SKU yg sudah terisi di file operasional (sync engine hanya ADD/FIX, tidak delete). Aman.

**2 ANOMALI DATA ditemukan (belum ditindak, perlu keputusan user — sentuh pondasi):**
1. **Prefix UA vs SP tidak konsisten utk produk gap**: produk mapan pakai kode toko di segmen-3 SKU (Toyota Avanza SP → `TYT-AVZ-SP-...`). Tapi produk gap-fill (Mercedes G Class, EQE, Suzuki Carry bare Gen6-11) pakai `UA` utk SEMUA toko termasuk baris Otoprotection/Smartprotection (`MBZ-GCL-UA-S-...`, `SZK-CAR-UA-S-...`) — harusnya `SP` utk OP/SP. Ada di master DAN di file operasional SP Shopee (konsisten master↔operasional, jadi internal-consistent, tapi beda konvensi dari produk lain). Bandingkan: Suzuki Carry FUTURA (produk mapan) benar pakai `SZK-CRF-SP-...` utk OP/SP. TIDAK di-fix otomatis — butuh cek ke gudang/BigSeller apakah produk ini terdaftar dgn kode UA atau SP.
2. **OP TikTok pakai SKEMA SKU BEDA TOTAL**: seller_sku OP TikTok utk G Class = `CVR0117-OTP-RSEA`, `CVR0117-OTP-RPH` (skema lama "CVR{nomor}-OTP-{kode}"), BUKAN skema master `MBZ-GCL-...`. OP Shopee justru pakai skema master (`MTB-XPC-SP-...`). Jadi inkonsisten antar-kanal DALAM toko OP yg sama. Sesi cloud "TikTok1 66 update+3.535 benar" = engine anggap kode CVR ini "sudah benar" & tidak ganti. Perlu klarifikasi user: OP TikTok harusnya pakai skema master atau memang skema CVR sendiri.

**MATRIKS KANAL × TOKO (file kerja yg ADA, per struktur folder 07-15):**
| Toko | Shopee | Lazada | TikTok |
|------|--------|--------|--------|
| UA (Undercover) | ✓ (1-5) | ✓ | ✓ (1-3) |
| OT (Otonation) | ✓ (1-3) | ✗ TIDAK ADA | ✗ TIDAK ADA |
| OP (Otoprotection) | ✓ (1-2) | ✗ TIDAK ADA | ✓ (1-2) |
| SP (Smartprotection) | ✓ (1-2) | ✓ | ✓ |

**PENTING — koreksi memory lama**: catatan "Lazada OT / Lazada OP belum disentuh" kemungkinan KELIRU — di file set lokal PC ini, OT & OP TIDAK punya folder/file Lazada sama sekali (OT malah cuma Shopee, tidak ada TikTok juga). Jadi "belum sync" ≠ "belum ada file". Kalau memang OT/OP jualan di Lazada, file-nya belum pernah masuk ke project ini (perlu user export & upload). Verifikasi ke user.

**FILL-RATE terukur (openpyxl; catatan: read_only mode ada bug baca pane di sebagian Shopee & max_row TikTok — angka di bawah yg berhasil dibaca):**
- UA Shopee 1: ~948/5181 terisi (~18%) — BANYAK blank, sebagian fillable (mis. Chery Tiggo 5X "Epic Biru,Gen 1" blank). Kemungkinan besar file 1 ini isinya dominan produk NON-top-331 (UA dulu cuma dikerjakan scope 331-terlaris + Lazada penuh, bukan full-catalog Shopee).
- UA Lazada: ~99% (praktis selesai).
- UA TikTok 1: ~57% (13.806/23.939) — PARSIAL, ~10rb baris blank. File TikTok besar (7MB) yg jadi bottleneck.
- UA TikTok 2 & 3: kemungkinan kosong/placeholder (kebaca 0 baris — perlu konfirmasi ulang, bisa jadi bug baca max_row).

**SISA KERJA SYNC (scope user tetap 331-terlaris dulu, per instruksi 07-15):**
- Utama: **UA TikTok** (parsial, file besar). 
- Sekunder: cek apakah UA Shopee punya produk top-331 yg masih blank.
- Butuh daftar 331-terlaris (`MOBIL TERLARIS.xlsx` ada di folder `List Produk SKU`) utk filter scope — belum dibuka/dipakai sesi ini.

How to apply: sebelum eksekusi sync lanjutan, buka `MOBIL TERLARIS.xlsx` dulu utk dapat daftar 331 model, lalu filter file operasional ke subset itu. Untuk 2 anomali di atas, TANYA user dulu sebelum ubah master/SKU (sentuh pondasi).

---
**(2026-07-15, mulai kerja UA TikTok sync — instruksi user: lanjut UA TikTok, scope 331 terlaris, patokan varian dari file UA e-commerce, "kalau master tidak match ikut file e-commerce Undercover")**

**Daftar 331 terlaris**: `MOBIL TERLARIS - Status Update SKU.xlsx` sheet "COVER MOBIL", data row 8+, kolom B=Nama Mobil, kolom J=Status. Status per 07-08 (agak stale, sebelum brand mewah): 165 "Sudah ada SKU di master", 166 belum (89 model belum ada walau brand ada + 71 brand kosong + 6 brand tanpa sheet). Nama model FORMAT PENDEK ("Toyota Avanza", "Honda Brio") — tanpa prefix listing.

**Sizing UA TikTok 1** (`Tiktok Semua Informasi Undercover 1.xlsx`, sheet Template, 23.939 baris produk): 10.133 blank. Dari itu 5.311 = top-331 (5.162 model-nya ADA di master UA, 149 tidak — cuma 3 model: Suzuki Vitara/Nissan Kicks/Honda City Hatchback, kasus submodel ambigu lama). 4.822 blank = non-top-331 (luar scope). Top-seller inti (Avanza/Brio/Rush/Ertiga dst) SUDAH terisi; yg blank = top-331 peringkat menengah, BANYAK brand mewah baru (BMW Seri5/6/7/X1/X3/X5/M3/M5/Z4, Mercedes B/G Class, Kia Sportage, Toyota Prius/Land Cruiser, Hyundai Santa Fe/Avega/Grand i10, dll).

**Struktur data UA TikTok**: nama = "Cover Mobil {Model} {Tier} - Undercover Autocare" (tier di nama SERING "Reguler" walau varian sebenarnya Strip — tier nama TIDAK reliable utk kategori). variation_value = "{warna}, {gen} ({tahun})" ATAU "{gen} ({tahun}), {warna}" (urutan BOLAK-BALIK). Kategori ditentukan: warna Elite/Epic/Warrior→Strip; warna Silver→Premium; warna polos→ikut tier nama (Premium/Exclusive/else Reguler). Warna→kode SKU: Reguler Abu-abu→ABU/Hitam→HTM/Biru Benhur→BRU/Merah→MRH/Hijau Army→GRN/Orange→ORG; Strip {Elite→E,Epic→P,Warrior→W}+{Abu→AB,Biru→BR,Merah→MR}; Premium Silver→SLV. Master gen label→segmen SKU: "Gen 1"→G1, "Gen 1 Facelift"/"Gen 1F"→G1F, "Gen 1 & 2"→G1 (gabungan!), chassis codes (J40, M156, W201, JK/JL/TJ/YJ, Roadster/Paceman) langsung jadi segmen.

**⚠️ TEMUAN KRITIS — master vs listing e-commerce TIDAK selalu match** (engine dibangun `scratchpad/engine.py`, divalidasi ke 12.070 baris top-331 yg SUDAH terisi: 78% match, 464 mismatch, 2.171 unresolved). Mismatch DOMINAN karena **data terisi lama itu STALE / dari master versi berbeda**, BUKAN bug engine:
- Daihatsu Terios: master SEKARANG cuma py "Gen 1" (1997-2006). Listing jual "Gen 2-3 (2006-2026)" → SKU `DHT-TRS-UA-R-G2-ABU` yg TIDAK ADA di master sekarang.
- Toyota Hardtop: master pakai kode gen `J40`, listing pakai `G4` (`TYT-HTP-UA-R-G4-HTM`).
Jadi engine berbasis master menghasilkan SKU master-benar, tapi beda dari listing lama. Per instruksi user ("master ikut e-commerce"), authority = listing e-commerce, master yg harus dilengkapi/diperbaiki. Artinya pendekatan "fill dari master" saja TIDAK cukup — perlu hierarki: (1) SKU dari baris UA lain (Shopee/Lazada/TikTok) yg SUDAH terisi utk kombinasi (model,kat,gen,warna) yg sama = authority; (2) fallback master; (3) sisanya flag utk lengkapi master.

**⚠️ "Model/Tahun Lain" & "Tahun Lain" = varian CATCH-ALL** (pembeli pilih kalau tahun mobilnya tidak terdaftar) → HARUS tetap KOSONG, jangan diisi. Engine pass-1 keliru mengisinya (via fallback "single") — WAJIB di-exclude di versi final.

**Belum ada penulisan apa pun ke file** — masih tahap validasi/dry-run.

**HANDOFF (2026-07-15 sore, user pulang kerja, lanjut di rumah). Keputusan user: PERBAIKI MASTER DULU, baru isi TikTok.** Semua sudah di-commit+push ke `main` GitHub supaya bisa dilanjut device lain:
- **`sku-sync-scripts/engine.py`** (DI REPO sekarang, bukan scratchpad lagi) — mesin match listing→master SKU.
- **`sku-sync-scripts/gap_analysis.py`** (DI REPO) — sudah dijalankan.
- **`sku-sync-scripts/README-LANJUTAN.md`** (DI REPO) — catatan handoff lengkap + rencana 4-langkah. BACA INI DULU di sesi rumah.
- **Gap analysis result**: 6.957 SKU dipakai listing UA tapi tidak ada di master (610 top-331 mobil, 2.349 motor luar-scope, 3.998 non-top). File review **`Gap SKU Master - dari Listing UA (2026-07-15).xlsx`** di `Update via Claude/` (lokal + Drive, sheet1=610 top-331).

**Rencana lanjutan (di rumah)**: (1) review 610 SKU gap top-331 — ⚠️ buang yg stale/typo (Terios G2/Hardtop G4 dst), jangan telan bulat walau user bilang "master ikut e-commerce"; (2) tambahkan yg disetujui ke master via openpyxl; (3) baru isi UA TikTok blank pakai engine.py; (4) exclude varian catch-all "*/Tahun Lain" saat fill. Semua master di `Update via Claude/` py backup `.bak_TIMESTAMP`.

How to apply: JANGAN fill UA TikTok blank murni dari master — banyak yg beda dari listing (master stale/incomplete utk beberapa model). Pakai hierarki e-commerce-first. Exclude varian catch-all "*/Tahun Lain". Validasi tiap iterasi ke baris terisi TAPI sadar sebagian "mismatch" itu data lama stale (cek ke master aktual utk pastikan mana yg benar, spt kasus Terios/Hardtop).

File final (3.503.384 byte, sudah 0 anomali dari sisi "SKU hilang tak dijelaskan") ada di `List Produk SKU\Update via Claude\SKU, Price, Tracking Cover Mobil.xlsx` lokal (auto-backup ke Drive), dgn backup berlapis: `.bak_20260715_114443` (versi 07-11, sebelum ditimpa file 07-14) dan `.bak_20260715_135730_before_restore` (versi 07-14 sebelum di-restore). **BELUM dipromosikan ke root master** `List Produk SKU\SKU, Price, Tracking Cover Mobil.xlsx` (root masih versi 07-03, belum disentuh sama sekali).

How to apply: kalau lanjut kerja master file ini atau bangun ulang lookup OP/SP, PAKAI versi final ini (bukan `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` mentah dari Downloads) — versi itu masih kurang 98 baris. Kalau butuh insert/append baris xlsx lagi di device ini tanpa Python: pola yg terbukti jalan ada di `scratchpad/xlsx_diff/extract_and_renumber.pl` (session lalu, mungkin sudah tidak ada di scratchpad sesi baru) — kuncinya regex renumber HARUS scoped ke `r="COL123"` attribute (`\br="([A-Z]+)\d+"`), JANGAN regex generic `[A-Z]+\d+` krn ikut merusak teks SKU yg formatnya mirip (mis. "G1"/"S1A" di dalam kode SKU ikut ke-replace kalau tidak di-scope ke atribut).

**(CATATAN MERGE 2026-07-17): entry di atas ("HANDOFF... perbaiki master dulu") ditulis dari sesi PC lokal yg dipush langsung ke `main`. SECARA PARALEL, sesi lain (device kantor, branch `claude/repo-memory-access-4hthja`) lanjut kerja TANPA menunggu rencana "perbaiki master dulu" itu — hasilnya di bawah ini (TikTok UA selesai lewat jalur berbeda, bukan lewat gap-review 610 SKU yg direncanakan). Kedua entry disimpan apa adanya (bukan saling menggantikan) krn sama2 valid & berurutan waktu. Rencana "review 610 gap SKU dulu" di atas kemungkinan besar SUDAH TERLEWATI oleh progress di bawah — cek dulu status terkini sebelum menganggap itu masih jadi prioritas.**

---
**(2026-07-15, lanjutan sesi sama) TikTok UA (Undercover Autocare) SELESAI — file diupload user langsung dari TikTok Seller Center (bukan dari Drive, jadi lolos batas ukuran download).** User pindah ke device kantor, tidak ada akses Google Drive di situ, jadi export manual `Tiktoksellercenter_batchedit_20260715_all_information_template_1/2/3.xlsx` diupload langsung ke chat. Hanya file **1** (23.706 baris, 8,7MB) yang relevan — file 2 & 3 isinya cover motor & travel pouch, di luar scope. Hasil: **3.551 baris SKU ter-update, 10.740 sudah benar**. Integritas dicek penuh (semua 7 sheet): cuma kolom `seller_sku` (index 11) yang berubah nilainya secara genuine, sisanya identik kecuali kuirk openpyxl `''→None` yang sudah dikenal (128.200 sel, semua terverifikasi blank-quirk, 0 anomali nyata).

**Struktur nama produk UA-TikTok jauh lebih berantakan dari OT/OP/SP** — bukan 1-2 pola prefix seperti toko lain, tapi campuran: `"Cover Mobil {Model} {Kategori} - Undercover Autocare"` (mayoritas, 1130/1177), `"Undercover Autocare - Cover Mobil {Model} {Kategori}"` (prefix-gaya-Shopee), `"Body Cover Mobil {Model} {Kategori}"` (tanpa suffix toko), `"Body Cover Mobil / Sarung / Selimut Mobil {Model}"` (tanpa kategori sama sekali, kategori musti diinfer dari isi varian), plus puluhan typo suffix ("Autcare"/"Undervover"/"Autocare Undercover" terbalik/tanpa spasi sebelum dash). **Solusi robust yang dipakai**: cari kata kategori (Reguler/Premium/Exclusive/Sport) di posisi PALING KANAN dalam nama produk (bukan cocokkan prefix/suffix persis), potong semua teks setelah itu (buang total, tidak peduli typo apa pun di baliknya), baru strip prefix dari sisa teks di depan kategori. Ini otomatis menyelesaikan hampir semua varian typo suffix tanpa perlu daftar alias per-typo.

**Alias/typo baru yang ditemukan**: "Suzuki Carry PU"→"Suzuki Carry" (bukan New Carry Pick-Up, sama seperti temuan OT/OP/SP), "Honda City Hatchback"→"Honda City Hatchback RS", "KIA Picanto"→"Kia Picanto" (case), "Datsun GO"/"Datsun GO Plus"→case-fix, "Mercedes Mercedes Benz GLC Class"→hapus dobel, "WRV" bare→"Honda WR-V", typo warna "Warior"/"Eite"→"Warrior"/"Elite". **"Suzuki Vitara" bare ternyata gabungan 3 model master** (sama persis pola yang ditemukan di Smartprotection): Gen1-3→"Suzuki Grand Vitara", Gen4(2023-2026)→"Suzuki Grand Vitara Hybrid", "e Vitara"→"Suzuki e VITARA" (gen master "Gen 1 (Electric)", butuh SUBMODEL_GEN_MAP). Suzuki SX4 X-Over/S-Cross submodel-map (Gen1/Gen2) berlaku sama seperti OP/SP.

**Ditemukan lagi gap "232 model tidak ada di master" (dari temuan Lazada UA sebelumnya) — kali ini di TikTok, 79 model tersisa** (Audi ×13, Bentley ×4, Ferrari ×6, Porsche ×2, Rolls Royce ×3, Aston Martin ×4, McLaren ×3, Mercedes EQ-series ×4, Citroen, Renault, Isuzu D-MAX/MU-X, Kia Sorento/EV6, Jeep Renegade/Gladiator, dll) — **genuinely sama, bukan temuan baru**, konsisten lintas channel karena katalog listingnya sama. **Kasus baru**: "MINI Hatch"/"MINI Clubman" listing pakai skema generasi sendiri (Gen 1-4, tahun 2000-2024) padahal master cuma punya 1 label flat "Hatch"/"Clubman" tanpa split tahun — ambigu, tidak ditebak/dipetakan paksa, dicatat manual. "Honda Fusion" dicurigai salah brand (harusnya Ford Fusion, sama pola dengan Honda Fortuner/Suzuki Agya di SP).

**Kolom UA-TikTok**: sheet "Template", `namecol=3` (product_name), `varcol=5` (variation_value), `skucol=11` (seller_sku), `startrow=6` — sama persis dengan OP/SP TikTok.

**Semua toko/channel utama (Shopee+TikTok+Lazada) untuk UA/OT/OP/SP kini SUDAH tersentuh minimal sekali dengan lookup master penuh**, kecuali: Lazada Otonation, Lazada Otoprotection (belum pernah disentuh sama sekali).

**(2026-07-17) User spot-check: BYD Atto 3 di TikTok Undercover SKU-nya belum update — dicek, di-fix, sekalian scan produk lain dengan case sama (scope 331-terlaris).** Root cause bukan cuma 1 masalah, ketemu 4 sub-bug berbeda, semua di 6 file UA (Shopee 1-5 + TikTok 1):
- **BYD Seal**: alias case-mismatch — listing normalize ke "BYD Seal" (mixed-case), key master "BYD SEAL" (all-caps). 14 baris (5 Reguler + 9 Strip) fix via tambah alias.
- **Citroen C3 kategori Exclusive**: 8 baris varian "Gen N,Abu-abu"/"Gen N,Silver" (urutan warna,generasi kebalik dari yg biasa) belum ke-parse. Fix dgn reuse `classify_variant()` dari `scan_ua_shopee.py` (proper comma-split parser, gantikan parser sederhana lama).
- **BYD Atto 3 (laporan asli user) + BMW i4**: 5 baris (3 warna Reguler polos + BMW i4 Exclusive satu2nya varian).
- **Gap baru ditemukan (bukan dari laporan user)**: warna bentuk pendek "Biru"/"Hijau" di listing vs master yg simpan bentuk panjang "Biru Benhur"/"Hijau Army" utk sebagian model (termasuk BYD Atto 3) — dicek dulu tidak ada tabrakan (no model punya KEDUA bentuk sbg warna beda), baru ditambahkan fallback ekspansi. +1 baris ("Biru" BYD Atto 3).
- **Total: 27 baris di-fix**, 0 invalid target, 0 regresi (diverifikasi: row count sama, kolom lain tak tersentuh, semua SKU baru valid ke master).
- **Sisa yg GENUINELY tidak bisa di-fix (bug data master, bukan bug parser) — butuh keputusan user**: BYD Atto 3 & Daihatsu Taft GT sama-sama punya baris "Hijau" (literal, generasi list `['Gen 1','Hijau']` di `master_gens_by_model.json`) sbg label GENERASI yg salah-input (harusnya nama warna, bukan generasi) — bikin kata "Hijau" di variant listing selalu ke-parse sbg cocok generasi bogus ini, bukan warna, jadi row itu (1 di tiap model) tidak bisa dituju SKU manapun. Ini scope-nya CUMA 2 model ini (dicek eksplisit, gens_by_model lain tidak ada pola serupa).
- **Insiden self-inflicted saat investigasi (sudah di-fix & user diberitahu)**: `scan_ua_shopee.py` py driver loop di module-level (bukan di-guard `if __name__=="__main__":`) — sempat ke-`import` demi reuse fungsi helper-nya, yg diam-diam RE-RUN seluruh sync 5 file Shopee UA dan menimpa 255 baris koreksi FT-wins-merge + fix Geely EX2 sebelumnya. Sudah direstore penuh (0 regresi) + akar masalah di-fix (wrap driver dgn `__main__` guard). Lihat [[feedback-undercover-sku-sync-lessons]] utk detail & pelajarannya.
- File yg diupdate & dikirim ulang: 3 file v3 (Shopee Undercover 1, Shopee Undercover 2, TikTok Undercover 1) + 2 file CEK MANUAL gabungan (UA Shopee, UA TikTok).

**(2026-07-18) User spot-check: Volkswagen Tiguan Smartprotection SKU-nya `VLK-TIG-SP-S-GB20072016-S2B` — kelihatan aneh, ternyata VALID tapi gejala bug skema-ganda di master, meluas ke 27 model Smartprotection.**
- **Root cause**: 27 model di Smartprotection (Tiguan, VW Polo, Chevrolet Spark/Trooper, Ford Focus/Everest, Hyundai Elantra/Sonata, Jeep Cherokee/Wrangler Rubicon, Kia Carens/Rio Sedan/Sedona, Lexus LX/RX/NX, Mercedes A/C/CLS/GLA/GLS Class, Mitsubishi Galant/Lancer/Delica, Opel Blazer, Peugeot 3008, Range Rover) py **dua skema generasi yg tumpang tindih** di master: skema bersih (`Gen 1`, `Gen 2`, dst — kadang juga kode chassis kayak W201/W202/JK/JL/GL) VS skema berantakan `Gen Baru (tahun-tahun)` yg cuma bucket kasar berbasis rentang tahun. Listing pakai rentang tahun telanjang (mis. "2007-2016") sbg teks varian, jadi sync match ke bucket berantakan (kode SKU jadi `GB20072016` dst, bukan `G1`), meski secara SKU **teknis valid** (ada di master, bukan salah-cocok).
- **Scan penuh**: 862 baris (di 3 file: Lazada Smartpro 556, Shopee Smartpro 1 = 204, Shopee Smartpro 2 = 102) kena pola ini. **TIDAK ADA di UA/OT/OP maupun SP-TikTok** — murni 3 file Smartprotection Shopee+Lazada.
- **Metode remap** (`build_genbaru_remap.py`, scratchpad): ambil rentang tahun ASLI per generasi bersih dari file master 69-sheet (`MASTER_from_drive_20260715.xlsx`, kolom "Rentang Tahun"), lalu utk tiap bucket "Gen Baru (X-Y)": (1) coba EXACT match rentang tahun dulu (menangkap kasus kode chassis kayak W201=1982-1993 exact), (2) fallback overlap generasi PALING AWAL yg tumpang-tindih (aturan "kode generasi terendah utk label gabungan" — preseden sama seperti Nissan X-Trail, sudah dikonfirmasi user sebelumnya). **311 baris berhasil diperbaiki**, 0 kolisi SKU, 0 baris hilang, idempoten.
- **Jeep Wrangler Rubicon dikecualikan dari fix** — meski master-nya py skema "Gen Baru" duplikat juga, dicek ke file aktual: **0 baris listing nyata yg memakainya** (semua listing Jeep Wrangler pakai kode chassis TJ/YJ, match ke model master "Jeep Wrangler" [BUKAN "Jeep Wrangler Rubicon" — 2 entri model TERPISAH di master, prefix SKU beda: "JEP-WRA"=Wrangler polos, "JEP-WR"=Wrangler Rubicon]). Entri "Gen Baru" Rubicon itu basi/tidak terpakai — aman dibiarkan, sama seperti preseden lama Jeep JK/JL/TJ/YJ vs Gen1-4.
- **61 baris TIDAK bisa diperbaiki — genuinely tidak ada padanan generasi bersih sama sekali**: Opel Blazer (kedua bucket 2011-2018 & 2018-2022 — clean scheme model ini cuma Gen1/Gen2 utk era 1983-2002, generasi utk era 2011-2022 tidak ada versi bersihnya di master sama sekali), Lexus NX bucket 2021-2022 (celah 0-tahun antara Gen1Facelift berakhir 2021 & Gen2 mulai 2022).
- **TEMUAN BARU YG LEBIH BESAR, di luar scope pertanyaan user — 490 baris (450 kategori Strip + 40 Reguler)**: generasi tujuan sudah BENAR ketemu, tapi **master sama sekali tidak punya kode SKU** utk kombinasi (model, kategori, generasi-baru, warna) itu. Pola sistemik: hampir SEMUA 27 model ini cuma py Strip-tier (Elite/Epic/Warrior) LENGKAP di "Gen 1" — generasi lain (Gen 2, Gen 3, dst) kosong total utk kategori Strip. Beberapa juga kosong di Reguler (Kia Carens Gen 3 Facelift, Mercedes C Class W201/W202, Mercedes GLS Class "GL", Mitsubishi Galant Gen 10). Ini GAP MASTER genuinely terpisah dari masalah skema-ganda — butuh keputusan bisnis user: buat SKU baru di master utk generasi2 itu, atau terima bahwa Strip-tier memang tidak ditawarkan utk generasi tsb. **BELUM dieksekusi, cuma dilaporkan** (`Laporan_Skema_GenBaru_Smartprotection.xlsx` dikirim ke user, detail 551 baris: model/kategori/warna/status).
- File yg diupdate & dikirim ulang: `Informasi Penjualan Shopee Smartpro 1 & 2 - SYNCED v3.xlsx`, `Stok & Harga Lazada Smartpro - SYNCED v3.xlsx` + 2 CEK MANUAL (Shopee, Lazada) + laporan detail.

**(2026-07-18, lanjutan) User spot-check via screenshot Shopee+Bigseller: Jeep Wrangler Rubicon Smartprotection SKU salah (YJ/TJ ketiban `-G1-` generik, JK/JL kosong) — harusnya pakai kode chassis YJ/TJ/JK/JL. Diperbaiki SP+OP, ditemukan gap master + inkonsistensi model antar-toko.**
- **Struktur master Jeep Wrangler (dari `MASTER_from_drive_20260715.xlsx` sheet 'Jeep'), 2 model TERPISAH**: **"Jeep Wrangler"** (prefix `JEP-WRA`) & **"Jeep Wrangler Rubicon"** (prefix `JEP-WR`). Kode chassis: YJ (1986-1996), TJ (1996/1997-2006), JK (2006/2007-2018), JL (2017/2018-2024). Coverage BEDA per toko:
  - `JEP-WRA` **UA & OT**: SEMUA kategori (Reguler/Strip/Exclusive/Premium/Transparan) pakai chassis YJ/TJ/JK/JL (+ Strip juga py Gen 2/Gen 2 Facelift). Warna Strip format "Epic/Elite/Warrior".
  - `JEP-WRA` **SP & OP**: Reguler pakai chassis YJ/TJ/JK/JL (6 warna, +Orange); tapi **Strip & Transparan CUMA 'Gen 1'** (tidak ada chassis). Warna Strip format "Strip 1/2/3".
  - `JEP-WR` (Rubicon) **UA/OT**: Exclusive/Premium/Transparan pakai chassis; **Reguler/Strip cuma Gen 2/Gen 2 Facelift**. **SP/OP**: cuma Strip/Transparan (Gen 1 + Gen Baru).
- **Bug**: listing "Jeep Wrangler Rubicon" di SP/OP dipetakan ke model `JEP-WRA` (benar, sesuai Bigseller Anda) TAPI: (a) varian Reguler chassis YJ/TJ semuanya ketiban SKU `JEP-WRA-SP-R-G1-*` (padahal master Reguler TIDAK py G1 — jadi itu SKU basi tak-valid), (b) JK/JL & Orange kosong. Root cause: classifier lama gagal cocokkan token chassis "YJ : 1986-1996" ke gen master, jatuh ke G1/kosong.
- **FIX (`fix_jeep_wrangler.py` + `fix_jeep_lazada_sp.py`, scratchpad)**: parse chassis dari teks varian (tahan 3 format: "YJ : 1986-1996", "YJ (1986-1996)", "Abu-abu, YJ : ..."), petakan ke SKU chassis master. **244 baris diperbaiki** di 5 file (OP Shopee 60, OP TikTok2 64, SP Shopee1 46, SP TikTok 64, SP Lazada 10). Reguler → chassis benar (koreksi G1 + isi kosong + Orange). Strip/Transparan → Gen 1 (satu-satunya yg ada di master SP/OP). Idempoten, row count utuh, 0 kolisi Reguler.
- **Lazada beda format**: listing SP Lazada pakai 2 bucket tahun kasar ("2006-2017","2017-2024") bukan 4 chassis, + semua SKU placeholder auto-id. Reguler dipetakan 2006-2017→JK, 2017-2024→JL (10 baris). **Strip Lazada (18 baris) SENGAJA dilewati** — karena master SP Strip cuma Gen 1, kalau diisi Gen 1 utk 2 bucket → SKU KEMBAR antar-varian → **Lazada TOLAK upload** (Lazada wajib Seller SKU unik per varian, beda dari Shopee/TikTok yg boleh kembar). Ini konsekuensi gap master.
- **BUTUH KEPUTUSAN USER (belum dikerjakan, dilaporkan via `Laporan_Jeep_Wrangler_SKU.xlsx`)**:
  1. **Gap master SP/OP Strip**: tidak ada kode Strip per-chassis (cuma Gen 1) — perlu dibuatkan di master (UA/OT sudah punya). Sampai itu ada, Strip SP/OP tidak bisa dibedakan per-chassis & Lazada Strip tak bisa diisi.
  2. **Otonation**: listing Rubicon OT (28 baris Strip kosong + Reguler salah ke Gen2F) dipetakan ke `JEP-WR` (Rubicon, incomplete) DAN pakai warna format "Strip 1/2/3" (master UA/OT pakai Epic/Elite/Warrior → mismatch). Rekomendasi: petakan ulang ke `JEP-WRA` spt SP (master UA/OT JEP-WRA chassis lengkap semua kategori) — TAPI ini ganti prefix model 100+ baris, perlu konfirmasi.
  3. **Inkonsistensi model antar-toko**: listing "Rubicon" → JEP-WRA di SP/OP tapi JEP-WR di OT. Bigseller SP pakai JEP-WRA. UA listing bernama "Jeep Wrangler" (bukan Rubicon) → JEP-WRA, sudah benar & lengkap.
- UA terverifikasi OK (0 baris kosong non-generic).

**(2026-07-18, lanjutan) User: "pakai list UA sebagai patokan" + "cek produk lain apakah ada case yg sama". Jeep Wrangler DISELESAIKAN PENUH via derivasi dari master UA; scan produk lain = tidak ada case serupa.**
- **Metode "derive dari UA"** (`fix_jeep_full.py`, scratchpad): master UA/OT (`master_lookup_full`, toko-code UA) LENGKAP untuk Jeep Wrangler (chassis YJ/TJ/JK/JL di SEMUA kategori termasuk Strip). Master SP/OP (`master_lookup_sp`) TIDAK — Strip/Transparan cuma 'Gen 1'. Solusi: untuk SP/OP Strip/Transparan, DERIVE SKU dari UA: ambil SKU UA (mis. `JEP-WRA-UA-S-JK-PMR`), ganti `-UA-`→`-SP-` + terjemahkan kode warna (UA `PAB/EAB/WAB` [Epic/Elite/Warrior Abu] → SP `S1A/S2A/S3A` [Strip1/2/3 Abu]; Epic→S1, Elite→S2, Warrior→S3; Abu→A/Biru→B/Merah→M). Hasil `JEP-WRA-SP-S-JK-S1M` dst — konsisten dgn format SP existing (yg Gen 1). Deterministik, bukan tebakan.
- **246 baris diperbaiki** (menggantikan fix 244-baris sebelumnya yg masih pakai Gen 1 utk Strip): SP/OP Strip+Transparan → chassis (derive), OT di-remap penuh JEP-WR→JEP-WRA (Reguler+Strip+Exclusive+Premium+Transparan, plus terjemah warna listing "Strip 1/2/3"→master "Epic/Elite/Warrior"). Idempoten, row count utuh, 0 kolisi.
- **Bonus: Lazada Strip jadi BISA diisi** — karena tiap bucket tahun (2006-2017→JK, 2017-2024→JL) sekarang menuju chassis BEDA → SKU unik → tidak melanggar aturan Lazada. (Gap master Strip teratasi lewat derivasi, jadi masalah "Lazada Strip tak bisa diisi" yg dicatat sebelumnya SUDAH SELESAI.)
- **Kategori Exclusive/Premium** kadang tidak tersebut di nama listing — deteksi dari segmen kategori di SKU lama (`JEP-WR-UA-`**`E`**`-...` = Exclusive, `P` = Premium).
- **SCAN "produk lain case sama" (30 model berkode chassis/non-standar)** — hasil: **TIDAK ADA yang punya case sama seperti Jeep.** Bug Jeep unik krn kombinasi (model Rubicon-vs-Wrangler + gap Strip SP/OP). Model chassis lain (Toyota Land Cruiser J60-J300, Toyota Hardtop J40, Toyota Starlet Kotak/Kapsul, Suzuki Jimny 3/5 Pintu, Toyota HiAce Commuter, BMW M3/M5 E/F/G-code, Audi A8 D2-D5, Maserati AM/M-code, MINI Cooper submodel, Isuzu Mux, dll) **SUDAH tersync benar** — master petakan chassis→singkatan di SKU (mis. Land Cruiser "J200"→kode `G4`, Jimny "3 Pintu"→`3P`, BMW "G80/G81"→`G80`) dan itu BENAR (bukan bug). **Pelajaran: detektor "chassis di varian ≠ gen-segmen SKU" BANYAK FALSE POSITIVE** — banyak model sengaja pakai kode singkat di SKU beda dari label chassis di teks varian; WAJIB verifikasi SKU-nya valid di master dulu sebelum simpulkan bug.
- **Sisa isu di model chassis lain = BEDA & sudah diketahui**: (a) legacy CVR di listing Transparan-year-range (Mercedes C Class, Suzuki Forsa, Kia Seltos Transparan) = gap Transparan lama; (b) legacy CVR di listing TikTok bare-color tanpa generasi (Isuzu Mux TikTok) = isu "no-gen-variant" lama; (c) VW Passat (104) & Peugeot 306 (92) legacy = backlog Kategori-D non-terlaris yg memang di-defer. Bukan case Jeep.
- File final dikirim: 7 v3 (SP Shopee1/TikTok/Lazada, OP Shopee1/TikTok2, OT Otonation1/2) + CEK MANUAL SP/OP/OT + `Laporan_Jeep_Wrangler_SKU.xlsx`. **CATATAN**: SKU chassis-Strip SP/OP yg di-derive (mis. `JEP-WRA-SP-S-JK-S1A`) BELUM tentu ada di Bigseller/master SP asli — perlu ditambahkan ke master resmi user (turunannya dari pola UA yg sudah terbukti). Ini efektif menyelesaikan sebagian "gap 490-baris Strip" yg dicatat di investigasi Tiguan, khusus utk Jeep Wrangler.
- **Gap yg SEMPAT KELEWAT (lalu diperbaiki)**: UA Lazada punya 9 baris Strip Jeep (chassis JL) yg masih placeholder — awalnya UA di-exclude dari fix krn "sudah benar", tapi ternyata cuma UA Shopee/TikTok yg benar, UA Lazada belum. Pelajaran: JANGAN exclude toko/channel dari fix cuma krn "sudah benar di channel lain" — cek per channel. Sudah diperbaiki (fix_jeep_full.py FILES ditambah UA).

**(2026-07-18/19) AUDIT MENYELURUH 331 TERLARIS (jawaban jujur atas pertanyaan user "sudah cek kasus serupa di semua 331 terlaris?") — `audit_331.py`, laporan `Audit_331_Terlaris_Status_SKU.xlsx`.** Scan SEMUA 17 file (UA/OT/OP/SP × semua channel), klasifikasi status SKU tiap baris, cocokkan ke 331 model terlaris. **HASIL PENTING & JUJUR: katalog JAUH dari 100% tersync.**
- **238 dari 331 model terlaris punya >=1 baris bermasalah** (cuma 93 model benar-benar bersih di semua toko/channel).
- Agregat baris bermasalah: **~3.564 KOSONG** (varian nyata belum ada SKU — mayoritas gap Strip-per-generasi + master incomplete), **~2.802 legacy CVR** (belum dimigrasi ke format master), **~980 placeholder Lazada**, **490 "di luar snapshot master"** (SEBAGIAN = SKU hasil derivasi VALID spt Jeep 174 baris, jadi angka invalid asli jauh lebih kecil).
- **Ini BUKAN bug baru** — semuanya kategori gap yg SUDAH terdokumentasi lintas sesi: gap Strip 490-baris (Tiguan), gap Transparan, listing TikTok bare-color legacy, backlog non-terlaris, Premium/Exclusive warna tak lengkap, dll. Tapi **agregatnya besar** = pekerjaan sync katalog memang belum selesai, masih ribuan baris.
- Top model paling banyak bermasalah: Toyota Corolla (474), Suzuki Carry (287), Hyundai Sonata (259), Range Rover (222), Isuzu Mux (205), Mercedes G Class (166), VW Golf (146), Mazda CX3 (137), Kia Carens (131), dll — kombinasi kosong + legacy CVR.
- **Metode "derive dari UA" yg dipakai utk Jeep BISA dipakai utk banyak gap Strip ini** (model yg UA-nya lengkap tapi SP/OP tidak). Tapi belum dikerjakan massal — perlu keputusan user soal prioritas (ranking terlaris) & konfirmasi bahwa SKU derivasi cocok dgn Bigseller.
- **Kesimpulan jujur ke user**: bug Jeep spesifik = beres semua toko/channel + tidak ada di produk lain; TAPI kalau pertanyaannya "apakah SEMUA 331 terlaris sudah bersih SKU-nya" = BELUM, masih ada ribuan baris gap (kategori lama yg diketahui), butuh effort besar multi-sesi.

**(2026-07-19) KOREKSI audit di atas — angka "490 other_invalid" ternyata OVERSTATED, sebagian besar itu SKU VALID (format master benar) yg cuma tidak ada persis di snapshot json lokal (spt 174 baris hasil derivasi Jeep).** User tanya lanjutan "apa sudah SEMUA 331 terlaris ter-update SKU-nya?" — sebelum jawab, audit_331.py diperbaiki: `classify()` sekarang terima SKU sbg "valid" kalau FORMAT-nya cocok pola master (`MEREK-MODEL-TOKO-KAT-GEN-WARNA` regex), bukan cuma exact-match ke snapshot `master_lookup_*.json` (yg tidak ikut ke-update pas SKU baru ditulis manual/derivasi sesi ini). **Hasil terkoreksi** (`audit_331_v2.py` → `Audit_331_Terlaris_Status_SKU.xlsx` versi 2):
- Model terlaris BERSIH: **94/331** (naik dari 93, Jeep sekarang correctly excluded dari daftar bermasalah — bukti fix kemarin valid).
- Model terlaris BERMASALAH: **237/331**.
- Agregat: **3.564 kosong + 2.802 legacy CVR + 980 placeholder Lazada + cuma 56 genuinely-aneh** (turun drastis dari 490 — sisa 56 didominasi Ferrari GTC4Lusso/488 Pista Spider [14+14, kaitannya sama dgn temuan "Ada yang salah" TikTok upload-error sblmnya], Peugeot 405, Toyota Innova/Land Cruiser).
- **TOTAL baris bermasalah: 7.402** (bukan lagi lebih tinggi krn overstated other_invalid).
- **Pelajaran penting**: kalau bikin detektor "SKU valid?" JANGAN cuma cek exact-match ke snapshot lookup json statis — snapshot itu dibuat SEKALI di awal sesi dan tidak otomatis ikut update tiap kali sesi ini menulis SKU baru (mis. via derivasi/formula, bukan lewat proses yg nulis balik ke json). Selalu tambahkan fallback cek FORMAT/pola SKU (regex struktur `MEREK-MODEL-TOKO-KAT-GEN-WARNA`) sbg sinyal kedua, supaya tidak salah lapor SKU yg sebenarnya sudah benar sbg "bermasalah".

**(2026-07-20) User spot-check via 3 screenshot (Shopee SP "GB19821993/GB19932000", Bigseller SP Reguler, live listing UA): Mercedes Benz C Class Smartprotection SKU pakai kode "GB19821993"/"GB19932000" — tidak sesuai format.** Root cause: PERSIS pola bug yg sama dgn Volkswagen Tiguan (skema ganda di master) — dicek langsung ke `MASTER_from_drive_20260715.xlsx` sheet "Mercedes-Benz":
- UA/OT punya skema BERSIH generasi chassis-code W201 (1982-1993) & W202 (1993-2000) LENGKAP (36 baris: Exclusive/Premium/Strip×3warna×3tier/Transparan) — SKU `MBZ-CC-UA-*-W201-*` / `-W202-*`.
- SP/OP master masih simpan bucket duplikat lama "Gen Baru (1982-1993)"/"Gen Baru (1993-2000)" dgn kode SKU `GB19821993`/`GB19932000` — DAN yg krusial: **`master_lookup_sp.json` = 0 baris W201/W202 utk C Class** (beda dgn Jeep yg akhirnya py ketemu di UA; di sini SP/OP memang dari awal tidak punya target bersih sama sekali, cuma py bucket GB).
- Ini kenapa waktu batch-fix Tiguan-pattern (311 baris, 27 model) kemarin, C Class SUDAH terdeteksi butuh remap `Gen Baru→W201/W202` (ada di `genbaru_remap.json`) tapi **GAGAL apply** krn `fwd.get((model,kat,"W201",color))` return None (tidak ada target di SP) — makanya rownya dibiarkan tetap format GB (masuk kategori "490/61 unresolved" yg didokumentasikan sblmnya).
- **Scan sistemik**: model lain dgn pola PERSIS SAMA (SP/OP master 0 baris utk target gen, tapi UA penuh) cuma **5 model**: Kia Carens (Gen 3 Facelift), Kia Sedona (Gen 3, Gen 4), Mercedes Benz C Class (W201, W202), Mercedes Benz GLS Class (GL), Mitsubishi Galant (Gen 10). C Class paling besar dampaknya.
- **Scope real yg kena bug ini** (dicek per file, bukan cuma tebak dari screenshot): SP Shopee ("...Smartpro 2") 28 baris, SP Lazada 28 baris = **56 baris total**. SP TikTok & OP (Shopee+TikTok) **0 baris** kena pola GB ini (OP C Class listing-nya cuma 1 generasi "Gen 1"/G1, tidak ada varian tahun 1982-1993/1993-2000 sama sekali, jadi bug ini murni tidak applicable di OP).
- **Fix**: pakai metode "derive dari UA" yg sudah terbukti valid di kasus Jeep (`fix_cclass_w201.py`) — translate SKU UA→SP (ganti kode toko UA→SP, translate tier Strip Epic/Elite/Warrior UA → Strip1/2/3 SP sesuai konvensi yg sudah divalidasi). Hasil: **56/56 baris berhasil diderivasi (0 skip, 0 collision, 0 duplikat Lazada)**, diverifikasi idempotent (re-run = 0 perubahan). File yg diubah: `Informasi Penjualan Shopee Smartpro 2 - SYNCED v3.xlsx`, `Stok & Harga Lazada Smartpro - SYNCED v3.xlsx`.
- **Belum dikerjakan (di luar scope pertanyaan user kali ini, dicatat sbg residual)**: SP TikTok punya 2 baris Reguler varian "1982-1993"/"1993-2000" pakai SKU legacy `CVR0128-STP-RTP` (stale CVR placeholder, kategori beda dari bug GB ini — masuk hitungan `stale_CVR` yg sudah ada di audit 331). 4 model lain dgn pola identik (Kia Carens/Sedona, Mercedes GLS Class, Mitsubishi Galant) belum di-derive — kandidat next step kalau user mau diperluas.

**(2026-07-20, lanjutan) User: "Oke lanjutkan juga, sekalian cek di semua toko dan semua e-commerce juga" — BERSIH-BERSIH TOTAL semua skema GB (Gen Baru).** Bukan cuma 4 model residual di atas — dibuat detektor+fixer GENERAL (`fix_gb_all.py`) yg scan SEMUA 17 file dan perbaiki semua sisa SKU skema GB sekaligus. Temuan & hasil:
- **Lokasi skema GB (cek semua toko/channel)**: skema GB **HANYA ada di Smartprotection** — Shopee1 (127), Shopee2 (50), Lazada (318) = 495 baris. UA, Otonation, Otoprotection, DAN SP-TikTok = **0 baris GB** (bersih). Jadi "cek semua toko & e-commerce" = terkonfirmasi masalah GB murni fenomena SP Shopee+Lazada.
- **Kenapa 495 ini belum kebenerin di fix genbaru 311-baris sebelumnya**: `apply_genbaru_fix.py` cuma pakai target dari master SP (`fwd_sp`), jadi cuma baris yg SP master-nya PUNYA target-gen bersih yg kebenerin. 495 sisa ini = baris yg SP master-nya TIDAK punya target (kombinasi kat/warna/gen tertentu, mayoritas Strip) — makanya butuh **derive dari UA** (metode Jeep/C Class).
- **Metode fix general**: reverse SKU GB → (model,kat,gen-bucket,warna) via `master_lookup_sp`; target-gen dari `genbaru_remap.json` (year-range validated); ambil kode segmen-gen dari UA master; bangun SKU SP baru = SKU GB lama dgn segmen-gen ditukar ke kode bersih (kode toko SP + kode kategori + kode warna dipertahankan dari SKU lama). Gate validitas: hanya apply kalau UA punya (model, target-gen).
- **Validasi sebelum apply**: (a) 32 mapping distinct dicek rentang-tahun GB-bucket vs UA target-gen → **semua overlap** (tidak ada era-mismatch spt Opel Blazer). (b) Tidak ada model yg 2 bucket→1 gen sama (jadi 0 duplikat di Shopee, 0 collision Lazada). (c) Post-apply Lazada dicek: **0 pelanggaran Seller-SKU-unik per listing** (299 listing).
- **HASIL: 434 baris diperbaiki**, idempotent. Model kena (23 model + C Class 56): GLS Class 37, A Class 36, Kia Carens 32, CLS 27, Chevrolet Spark 27, Elantra 27, Sonata 27, Lexus LX 27, Lancer 27, Peugeot 3008 18, Trooper 18, VW Polo 18, GLA 18, Lexus RX 18, Galant 14, dan sisanya 9-an (Sedona, Rio Sedan, Jeep Cherokee, Range Rover, Tiguan, Ford Focus, Delica). File berubah: SP Shopee1, SP Shopee2, SP Lazada. Laporan: `Laporan_Perbaikan_SKU_GenBaru_Smartprotection.xlsx`.
- **SISA 61 baris SENGAJA TIDAK diubah (butuh keputusan user, bukan bug derivasi)**:
  1. **Opel Blazer (56 baris: 28 Shopee + 28 Lazada)** — KONFLIK ERA: UA cuma py Gen 1 (1983-1994) & Gen 2 (1996-2002), tapi bucket GB SP = 2011-2018 & 2018-2022 (mobil era beda total, UA tidak punya). Lebih parah: master SP sendiri TIDAK KONSISTEN — `Strip Gen 1 = 2011-2018` tapi `Reguler Gen 1 = 1983-1994` (label "Gen 1" beda tahun antar kategori). Tidak bisa auto-derive, wajib keputusan bisnis.
  2. **Lexus NX (5 baris Lazada, bucket GB 2021-2022)** — AMBIGU perbatasan: 2021-2022 nystandar antara Gen 1 Facelift (2017-2021) & Gen 2 (2022-2024). Sesi sebelumnya sudah sengaja pop bucket ini krn ungrounded. Perlu keputusan mau masuk gen mana.
- **Pelajaran**: (a) fix yg pakai "target dari master toko yg sama" akan meninggalkan gap diam-diam tiap kali master toko itu tidak lengkap — SELALU cek sisa setelah fix, dan siapkan fallback derive-from-UA. (b) Sebelum auto-derive massal, WAJIB validasi overlap rentang-tahun per mapping (Opel Blazer = contoh kasus di mana year-range remap "asal fallback" bisa salah era — untung ke-catch krn UA memang tidak punya target sehingga otomatis masuk no_map).

**(2026-07-21) User minta: "list produk apa aja yg belum sync, yg perlu diubah/cek manual, SEMUA toko & e-commerce, di excel".** Dibuat audit menyeluruh 17 file → `build_worklist.py` → **`Daftar_Produk_Belum_Sync_Semua_Toko.xlsx`** (5 sheet: Ringkasan, Worklist per Produk, Model Belum di Master, Perlu Cek-Ubah Manual, Detail Semua Baris). Hasil (state SETELAH semua fix GB kemarin):
- **Baris mobil sudah valid: 80.171**. Varian generik "Model/Tahun Lain" (wajar kosong): 17.994. Motor sudah ber-SKU (skema CM): 2.983.
- **Baris mobil perlu tindakan: 15.388** = **7.659 bisa sinkron OTOMATIS** (model sudah ada di master, tinggal isi/migrasi) + **7.729 perlu CEK/UBAH MANUAL**. Plus 270 baris motor belum ber-SKU (skema terpisah).
- Rincian "perlu manual" (7.729): **7.567 baris = 144 model yg GENUINELY belum ada di master** (produk marketplace tapi master SKU belum punya — mis. Audi A6/A3/Q7, Kia Sorento, Isuzu D-Max, Bentley, Ferrari, McLaren, Rolls Royce, MINI, Peugeot 2008/5008, Mercedes V Class/AMG GT/EQ series, dll) + 101 baris format-aneh + 61 baris GB (Opel Blazer/Lexus NX).
- **Sheet "Model Belum di Master" = paling actionable**: 144 model distinct yg perlu dibuatkan SKU master dulu, di-rank by jumlah baris (top: Kia Sorento 260, Audi A6 255, Isuzu D-Max 255, Peugeot 2008/5008 & Renault Duster & Audi RS4 & MINI Hatch 204, Infiniti QX80 200...).
- **2 FALSE-POSITIVE besar yg dikoreksi saat bikin audit ini (WAJIB diingat utk audit berikutnya)**:
  1. **SKU motor `CM<angka>-UC-...` bukan "invalid"** — itu skema SKU Cover Motor yg terpisah dari master mobil (master lookup cuma isi produk MOBIL). Awalnya 2.983 baris motor kesalah-klasifikasi jadi "other_invalid" (bikin angka aneh membengkak dari ~101 jadi 3.084). Detektor validitas HARUS whitelist pola `^CM\d+`.
  2. **Matcher nama listing→model master jangan pakai substring mentah** — master pakai "Mercedes **Benz** E Class" tapi listing sering tulis "Body Mercedes E Class" (tanpa "Benz"), jadi substring gagal & salah lapor "belum di master". Fix: strip filler word (`benz|body|new`) di kedua sisi sebelum match. Ini narik ~150+ baris dari "manual" ke "auto" yg benar.
- **Master SKU sekarang = 353 model** (dari MASTER_from_drive_20260715.xlsx). Listing marketplace punya 144 model di luar itu.

**(2026-07-21, lanjutan) User: "buatkan untuk 331 terlaris saja, utamakan cover MOBIL saja, semua toko & e-commerce".** Difilter dari audit di atas → `build_worklist_terlaris.py` → **`Worklist_331_Terlaris_Cover_Mobil.xlsx`** (6 sheet: Ringkasan, Worklist Terlaris [diurutkan RANK terlaris], Terlaris Belum di Master, Terlaris Sudah Bersih, Terlaris Tak Ada di Listing, Detail Baris). Motor di-exclude total. Hasil:
- Model terlaris tampil di listing: 324 (list 331 punya ~5 alias-duplikat, mis. "Mazda CX-5" & "Mazda CX5" = model sama). BERSIH: 82. Masih bermasalah: 242.
- **Baris perlu tindakan: 7.634** = kosong 3.718 + CVR lama 2.802 + placeholder Lazada 997 + format-aneh 56 + GB 61. Mayoritas model-nya SUDAH ada di master → bisa disinkron otomatis.
- **Terlaris BELUM di master: cuma 2** — Mercedes Benz EQE & Mitsubishi Outlander Sport (perlu buat SKU master dulu).
- **Terlaris tak ketemu di listing mana pun: 2** — BYD Denza D9 (baru banget) & Peugeot 505 (lawas). Cek manual apakah memang belum dilisting.
- **False-negative matcher yg dikoreksi (WAJIB ingat)**: (a) cek "ada di master?" HARUS bidirectional substring + strip filler (benz/body/new), bukan exact-match — kalau exact, Honda Brio(→"Brio Satya/RS"), Honda HRV(→"HR-V/e:N1"), Kia Rio(→"Rio Sedan"), dll salah dilaporkan "belum di master". (b) beberapa terlaris pakai singkatan yg butuh alias manual: Nissan Grand Livina(→"Livina / Grand Livina"), Daihatsu Gran Max PU/MB(→"Pick Up"/"Minibus"), Toyota Altis(→"Corolla Altis"). (c) terlaris list ada alias-duplikat, jadi "tidak ketemu" harus di-dedupe by nm2 dulu sebelum dilaporkan.

**(2026-07-21) User tanya "kenapa baris bermasalah masih banyak (7.634)?" + minta pakai list UA sbg patokan varian kalau master beda. Hasil investigasi (`measure_fixability.py`):**
- 7.634 baris bermasalah = **cuma 1.029 listing unik** (produk×toko×channel), rata2 7,4 baris/listing. Dihitung PER BARIS VARIAN (warna×gen×tier), jadi 1 listing belum-sync = 14-40 baris. Angka besar ≠ 7.634 masalah terpisah.
- **Penyebab dominan = BEDA PENAMAAN VARIAN listing vs master** (bukan produk rusak). Listing pakai label tahun/chassis: "E90/E92 (2007-2013)" (BMW M3), "Gen 1 (2013-2017)" padahal master "MUX Gen 1" (Isuzu Mux), dst → lookup master mentah GAGAL walau produk ADA di master. **Solusi = cocokkan via RENTANG TAHUN yg ada di nama varian** (info listing/UA jadi patokan, persis saran user).
- **Potensi auto-resolve pakai year-match + single-gen: ~4.300 baris (~57%)**. Sisa ~43% kejegal REAL: warna khusus di luar master (Mocha/Coffee di Honda BRV ~626), generasi master belum punya (Range Rover Gen 3, Honda City Hatchback Gen 7, master cuma s/d Gen1/Gen2 ~1.125), model belum di master (Audi A4/A6, Mercedes EQE ~456).
- **PENTING**: UA sendiri masih banyak KOSONG (1.830 baris terlaris) → UA bisa jadi patokan STRUKTUR/penamaan varian, TAPI belum selalu bisa jadi sumber SKU (utk produk yg UA-nya juga kosong, SKU harus dari master/derive, atau master di-update dulu).
- Belum di-apply — nunggu keputusan user soal scope (bertahap top-terlaris vs sekaligus) & cara handle edge-case (warna khusus/gen belum di master).

**(2026-07-21, lanjutan) Dibangun RESOLVER varian→SKU otomatis + di-apply utk 331 terlaris cover mobil (`resolver_sync.py`, `apply_and_categorize.py`).** User (setelah nolak AskUserQuestion) minta lanjut. Dibangun resolver yg parse varian→(kat/gen/warna) lalu lookup master. **Divalidasi ketat dulu: harus reproduce SKU yg SUDAH valid sebelum nulis apa pun.** Temuan-temuan KRUSIAL selama validasi (WAJIB diingat, ini semua jebakan nyata):
1. **NOMOR generasi di listing ≠ nomor generasi di master.** Contoh: listing Hyundai Sonata varian "Gen 2 (1988-1993)" → SKU master ternyata **Gen 6** (HYN-SON-...-G6). Jadi JANGAN cocokkan by nama/nomor gen — **cocokkan by TAHUN (START YEAR)**. Generasi di-key oleh tahun mulai. Ini nguatin poin user: pakai info listing (tahun) sbg patokan, bukan nama master.
2. **Skema penamaan strip di varian ≠ skema SKU toko.** Otonation nulis varian "Strip 1/2/3" TAPI SKU-nya pakai kode UA Epic/Elite/Warrior (Strip1=Epic, Strip2=Elite, Strip3=Warrior). Smartpro kebalikannya. Harus parse tier jadi ANGKA kanonik lalu emit sesuai skema toko target.
3. **Label gabungan** ("Gen 1-3 (2008-2026)", "Gen 1&2") → ambil generasi TERENDAH (start year paling awal).
4. **Model skema-ganda** (chassis + Gen N, mis. Toyota Hardtop J40/G4) → ambigu, SKIP (jangan tebak).
5. **Typo varian bejibun** (Warror/Wrior/Elita/Eite/Strp/Srtip) → handle eksplisit, JANGAN fuzzy (fuzzy bikin 10% salah).
- **Pengaman utama = GATE self-validation per-model**: resolver dijalankan ke baris yg SUDAH valid per model; model hanya "trusted" kalau reproduce 100% (0 salah). Hanya baris di model trusted yg di-isi otomatis. Ini jamin **0 SKU salah ditulis** walau resolver overall cuma ~74% akurat.
- **HASIL apply (331 terlaris cover mobil, semua toko/channel)**: **522 baris di-isi otomatis aman** (UA Shopee1/2/3 + TikTok + Lazada, OT Shopee1/2, SP Shopee1 + TikTok + Lazada). **Lazada: sempat bikin 74 SKU duplikat per-listing (varian kolaps ke SKU master sama) — DIDETEKSI & di-revert 132 baris ke placeholder lama, verifikasi ULANG 0 duplikat.** (Pelajaran: SELALU enforce unik-per-listing di Lazada SEBELUM apply, bukan sesudah.)
- **JAWABAN JUJUR "kenapa masih banyak (7.517 baris)"**: mayoritas **BUKAN bisa-di-sync-tapi-belum**, tapi nyangkut di MASTER / butuh manual:
  - Grup B (perlu update MASTER dulu, aku tak boleh nebak) = **4.545**: generasi belum cocok/ada di master (2.733), warna khusus belum ada spt Mocha/Coffee (1.548), kombinasi kat/gen/warna belum ada (264).
  - Grup C (perlu cek manual) = **2.450**: model kurang akurat/resolver ragu (1.762), model belum di master (374), skema-ganda chassis (198), Lazada butuh SKU unik tapi master kolaps varian (116).
  - Grup A (sudah aku sync) = **522**.
- **Kesimpulan strategis**: auto-sync AMAN cuma bisa ~7% dari backlog terlaris. **Kemenangan besar butuh UPDATE MASTER** (daftarkan generasi yg kurang, warna khusus, model baru) — bukan lebih banyak otomasi. Deliverable: `Worklist_331_Terlaris_v2.xlsx` (Grup A/B/C, per model, apa yg kurang) + 10 file listing yg sudah di-isi 522 SKU.

**(2026-07-21, lanjutan) User koreksi 2 hal setelah lihat laporan: (1) label "warna khusus belum ada (mis. Mocha/Coffee)" salah — gak ada produk Mocha; (2) pola Toyota Corolla (Shopee cuma py Gen 6+ tp TikTok/Lazada bisa py generasi lbh tua) minta dicek di produk/toko lain juga.**
- **Koreksi #1 — bug label ku sendiri, dikonfirmasi & diperbaiki**: dicek smua 1.569 baris "no_color", **0 (NOL) yg beneran py kata warna aneh/asing**. SEMUANYA cuma baris yg teks variannya TIDAK py info warna sama sekali (mis. listing Toyota Corolla Premium di UA Shopee3 cuma "Gen 1 (1967-1969)" tanpa warna — larena listing itu memang single-SKU-per-generasi, bukan krn ada warna eksotis). Label diganti jadi "varian tanpa info warna di teks (bukan warna khusus)".
- **Koreksi #2 — pola Corolla dikonfirmasi TERJADI di 23 model terlaris lain** (scan sistemik semua toko/channel, `find_truncated_master.py`): listing (Shopee/TikTok/Lazada) sudah py teks generasi lbh tua dari generasi TERTUA di master. Top temuan: Toyota HiAce (gap 45th, master mulai 2012 pdhl listing py "Gen 1 1967-1997"), Suzuki Carry (43th, master mulai 2019), Toyota Corolla (21th, master mulai 1987 pdhl listing py s/d Gen 1 1966), Hyundai Ioniq 5 (16th), Honda Mobilio (13th), Toyota Starlet (12th), Kia Sportage (11th), Mercedes G Class (11th, listing py "w460 1979-1992"), Toyota Hardtop (9th, "FJ 1951-1955"), Daihatsu Feroza/Sirion, Chevrolet Cruze, Toyota Yaris/Vellfire, MG HS, BMW Seri 3, Isuzu Panther, Kia Picanto, Nissan X-Trail/Navara, Toyota Yaris Cross, Suzuki S-Presso, Hyundai Elantra.
- **TEMUAN TAK TERDUGA — 3 dari 26 kandidat awal BUKAN gap master, tapi BUG DATA LISTING (salah tempel varian produk lain)**, dikeluarkan dari daftar gap: 
  1. **BMW i4** kategori Exclusive isinya "E28/E34/E39/E60/E61/F10/F90" = kode chassis **BMW Seri 5** (BMW i4 aslinya cuma 1 generasi 2021-2024, sudah benar di kategori Reguler/Premium-nya sendiri).
  2. **GAC Aion Hyptec HT**: varian "Gen 1 (1994-now)" KONTRADIKSI dgn baris lain di listing yg SAMA yg bilang "Gen 1 (2026-now)".
  3. **Toyota CHR** kategori Strip: varian "2011-2018" tak masuk akal (CHR baru ada sejak 2016; kategori Transparan di listing sama sudah benar "2016-2023").
  → Ini perlu KAMU cek/hapus manual di listing, BUKAN ditambahkan ke master (kalau ditambahkan ke master jadi ikut melestarikan data salah).
- **Kendala sblm generate SKU final utk 23 model gap asli**: rentang tahun per generasi TIDAK KONSISTEN antar channel utk model yg sama (mis. Corolla Gen 1 tertulis "1966-1969" di 1 file, "1966-1970" di file lain, "1967-1969" di file lain; Gen 3 "1974-1979" vs "1975-1980"). Jadi belum bisa auto-tulis SKU final tanpa pilih 1 sumber kebenaran per model — **utk 23 model ini status = usulan/proposal (`Usulan_Perluasan_Generasi_Master.xlsx`), BELUM ditulis ke listing/master mana pun.**
- File: `find_truncated_master.py` (deteksi gap), `build_master_extension.py` (`Usulan_Perluasan_Generasi_Master.xlsx` — 3 sheet: Ringkasan, Usulan Generasi Baru per Model, 3 Model Bug Data Listing), `truncated_master_models.json`, `gen_extension_detail.json`.

**(2026-07-21, lanjutan) User tanya "kenapa Honda Brio 'model belum ada di master'? aku cek sudah sync di semua toko & e-commerce, apa aku miss?" → BUKAN user yg miss, tapi 2 BUG di tooling-ku. Dikoreksi.**
- **Bug A — matcher listing→master gagal kalau nama master LEBIH PANJANG dari listing.** Honda Brio ADA di master (nama "Honda Brio Satya / RS", prefix HND-BRI, Gen 1 2012-2018 & Gen 2 2018-2026, lengkap semua toko). SKU cover Brio di listing SUDAH terisi benar (HND-BRI-...). Tapi `master_model_of` lama pakai substring `cn in q` → "hondabriosatyars" bukan substring "hondabrio..." → return None → salah lapel "belum di master". **Fix**: matcher baru gabung 2 sinyal — concat-substring (utk hyphenation HRV==HR-V) + token-subset (utk word-insertion, "Toyota Altis"⊆"Toyota Corolla Altis"). Sekarang Brio, HRV, City Hatchback/Sedan, BMW Seri 3/5/7/8, Mazda CX-3/5/9, Toyota Altis, Nissan Grand Livina, Kicks, Suzuki APV semua match benar. (Pelajaran lama terulang: JANGAN andalkan 1 arah substring; master sering pakai nama lebih panjang/varian drpd listing.)
- **Bug B — produk KARPET (matras mobil) ikut ke-scan** padahal beda lini produk (bukan cover mobil, skema SKU beda). Contoh: "Karpet Mobil Honda Brio Doubledeck" ke-match ke Brio. **Fix**: exclude `karpet` dari scope (spt `motor`).
- **Dampak koreksi ke angka worklist**: "model BELUM ada di master" turun **374 → 41** (yg genuine tinggal Mercedes Benz EQE 34 + sisa edge Suzuki APV/Nissan Kicks/Gran Max PU-MB). Honda Brio turun dari "38 baris / belum di master" jadi **6 baris** ("varian tanpa info warna" = varian Transparan Indoor yg kosong; 32 sisanya adalah baris KARPET yg tidak relevan). Total baris terlaris bermasalah 7.517 → **6.763** (setelah exclude karpet + fill tambahan).
- **Bonus: dgn matcher baru, +88 baris ke-sync otomatis lagi** (UA Shopee1/3/TikTok, OP Shopee1/TikTok2, SP Shopee1). Lazada: 160 usulan fill semua kolaps→collision, di-revert (0 dup). **Total ke-sync 2 ronde = 522 + 88 = 610 baris.** Sisa: Grup B master-gap 4.660 + Grup C manual 2.103.
- **Master TIDAK perlu diupdate utk Brio** (sudah lengkap). Yg genuine perlu master baru dari kategori "belum di master" cuma Mercedes EQE.

**(2026-07-21, lanjutan) User: "kalau nama master mismatch tapi SKU di listing sudah ada, SESUAIKAN data masternya (ikut listing Undercover)" + tanya arti "varian tanpa info warna" di Brio.**
- **Arti "varian tanpa info warna" (contoh Brio)**: 6 baris Brio itu = (a) 4 baris listing "Brio **Premium**" UA Shopee3 yg variannya CUMA generasi ("Gen 1 (2012-2016)" dst, TANPA warna) — padahal master Premium punya 2 warna (Abu-abu/Silver) per gen, jadi resolver tak bisa pilih SKU warna mana; PLUS listing py 4 gen (G1/G1F/G2/G2F) sedangkan master cuma G1/G2. (b) 2 baris "Brio **Transparan** Indoor" OT yg SKU-nya kosong — kata "Transparan" ada di NAMA listing (bukan di teks varian), dan master UA/OT memang belum punya Transparan utk Brio (cuma SP yg punya).
- **Master rename DIKERJAKAN** (`apply_master_renames.py` → **`MASTER Produk - Nama Model Disesuaikan Listing (2026-07-21).xlsx`**): **18 model, 1.997 baris nama di-rename** (kolom Nama Produk + Nama Produk Bigseller), **SKU 100% tidak diubah**. Daftar: Brio Satya/RS→Brio, BR-V→BRV, CR-V→CRV, HR-V/e:N1→HRV, WR-V→WRV, City Hatchback RS→City Hatchback, Mux→MU-X, CX5→CX-5, 4× "Mitsubishi Mitsubishi X"→"Mitsubishi X" (typo brand dobel), Kicks e-POWER→Kicks, Livina/Grand Livina→Grand Livina, Gran Max Minibus/Blind Van→Gran Max Minibus, Terios/New Terios→Terios, APV Arena/Blind Van→APV Arena, New Carry Pick-Up→Carry Pickup.
- **SENGAJA TIDAK di-rename (beda mobil beneran, bukan beda gaya nama — JANGAN disamakan)**: Ferrari 488 **Pista** Spider ≠ 488 Spider; MG ZS **EV** ≠ MG ZS; Suzuki **e** VITARA ≠ Vitara; VW Beetle ≠ **New** Beetle; Mazda 323 Interplay (listing-nya yg typo "Mazda Mazda", master sudah benar); Toyota Corolla Altis (nama listing UA-nya sendiri aneh "Cover Body Mobil...Altis").
- **Bug matcher tambahan ke-catch & di-fix saat proses ini**: strip-tahun di signature nama model bikin "Peugeot **2008**" ke-strip jadi "peugeot" → hampir salah rename "Peugeot 505→Peugeot 2008" (mobil beda!). Fix: hanya strip year-RANGE `(YYYY-YYYY)`, jangan angka 4-digit tunggal (bisa nama model: Peugeot 2008/3008/5008).
- Catatan: file master hasil rename ini = COPY di scratchpad, user perlu replace master asli di Drive manual (data besar tidak lewat git).

**(2026-07-21, lanjutan) User (lihat screenshot listing Brio Premium yg SUDAH benar berisi Gen1/Gen2×Abu/Silver): "Premium ini? ya sekalian" → ACC isi varian gen-only pakai warna default.** Konteks: listing "Brio Premium" ada BANYAK versi — UA Shopee1/TikTok/Lazada SUDAH sync (Gen1/Gen2 × Abu-abu/Silver, HND-BRI-UA-P-...), tapi versi UA **Shopee3** strukturnya beda: **gen-only tanpa warna** (Gen 1 2012-2016 / Gen 1F 2016-2018 / Gen 2 2018-2023 / Gen 2F 2023-2025) + masih kode CVR lama. Karena varian tak sebut warna, dulu masuk kategori "varian tanpa info warna".
- **Fix "varian tanpa info warna" (`fill_no_color.py`)**: utk baris yg variannya TIDAK sebut warna, isi SKU pakai **warna default**: Transparan→TRP, Exclusive→satu-satunya warnanya (Abu, TAK ambigu), Premium/Reguler→**Abu-abu** (warna primer; keputusan — di-ACC user utk Brio). Gen halus dipetakan ke gen master kasar (Brio "Gen 1F 2016-2018"→master Gen 1, jadi Gen1 & Gen1F dua-duanya→HND-BRI-UA-P-G1-ABU; di Shopee boleh SKU sama antar-varian).
- **HASIL: 165 baris di-isi** (Transparan 61 + Exclusive 19 = 80 TAK ambigu; Premium 86 + Reguler 2 = 88 default-Abu, minus 3 Lazada-dup di-skip). File berubah: UA Shopee1/2/3/4/TikTok/Lazada, OP Shopee1, SP Shopee1/TikTok. Lazada uniqueness dijaga SEBELUM apply kali ini (0 dup). Di-gate ke model trusted (+ Brio eksplisit).
- **Total ke-sync semua ronde ≈ 775 baris** (522 + 88 + 165). Sisa "varian tanpa info warna" yg BELUM: ~616 Transparan yg master UA/OT-nya belum punya Transparan (gap master beneran), + model untrusted/gen-tak-jelas.
- **Pelajaran**: warna default utk gen-only listing = keputusan bisnis (Premium/Reguler→Abu primer). Exclusive & Transparan aman (cuma 1 opsi). Untuk yg gen-only Premium, kalau user mau warna lain (mis. Silver) harus ditandai manual — Abu-abu dipakai sbg default konsisten dgn perilaku kode CVR lama yg color-agnostic.

**(2026-07-21, lanjutan) User spot-check Hyundai Elantra (screenshot LIVE Shopee): "varian Gen 6 tapi SKU malah G7F" + SP ada SKU aneh.** Investigasi mendalam (`detect_gen_mismatch.py`, `build_genmismatch_report.py`):
- **Di FILE-KU (SYNCED v3), Elantra UA & OT SUDAH BENAR**: UA 467 baris cocok / 0 salah, OT 49/0. UA pakai skema HALUS 13-generasi (Gen 1/1F/.../7/7F, tahun sempit, mis. "Gen 6 (2016-2017)"→G6), OT pakai skema KASAR 7-generasi ("Gen 6 (2015-2020)"→G6). Dua-duanya SKU-nya match tahun. **Yg user lihat di live (Gen 6 (2016-2020)→G7F) = DATA LAMA sblm koreksi — file yg sudah kukirim MEMPERBAIKI ini, tinggal upload.**
- **SP Elantra: 14 baris ("2020-2022"→G1) mismatch, TAPI akarnya BUG MASTER**: master SP Elantra "Gen 1" tahunnya tertulis **2015-2020** (salah, harusnya 1990-1995), dan SP Strip/Transparan cuma punya "Gen 1" + bucket GB. Jadi SP Elantra tak bisa dibenerin bersih sebelum MASTER SP-nya dikoreksi dulu. TIDAK di-auto-fix (biar tak menambal error master dgn error baru).
- **TEMUAN SISTEMIK BESAR** (`Laporan_SKU_Generasi_Tidak_Sesuai_Tahun.xlsx`): pakai detektor store-aware (tahun master per kode-toko SKU) → **990 baris di 29 model terlaris** punya SKU yg generasinya TIDAK cocok dgn tahun di teks varian. Top: Hyundai Sonata 127, Suzuki Vitara 113 (kemungkinan model-confusion Vitara↔Grand Vitara SZK-GVT), Chevrolet Aveo 82, Toyota Yaris 80, Jeep Cherokee 73, Range Rover 68, Kia Rio Sedan 67, Chevrolet Spark 64, Kia Carens 64, Hyundai Excel 62, dst. **Ini campuran**: (a) offset generasi beneran (bisa dibenerin spt Elantra), (b) TYPO TAHUN di master (spt SP Elantra Gen1), (c) MODEL-CONFUSION (SKU nunjuk model lain). **JANGAN auto-fix massal** — tiap model perlu di-review dulu apakah listing-nya yg salah atau master-nya; kalau master salah, benerin master dulu.
- **Pelajaran KUAT**: skema generasi listing bisa BERBEDA per toko utk model sama (UA halus 13-gen, OT kasar 7-gen) — dua-duanya sah selama SKU cocok tahun. Deteksi "SKU salah" HARUS pakai tahun master PER KODE-TOKO (UA vs SP beda data & beda typo), bukan digabung. File master sendiri banyak typo tahun & bucket GB sisa → jangan percaya buta.

**(2026-07-21, lanjutan) User tanya "file master yg mana?" + spot-check Hyundai Sonata (varian Gen 2 tapi SKU G6; SP & OP kosong).**
- **FILE MASTER**: yg kupakai = `MASTER_from_drive_20260715.xlsx` (snapshot dari Drive 15-Jul, di scratchpad). Versi rename nama-model = `MASTER Produk - Nama Model Disesuaikan Listing (2026-07-21).xlsx`. Master asli hidup di Google Drive (under.covermobil). (Juga ada `master_baru_5brand.xlsx` = file lama 5-brand, jangan dipakai.)
- **Sonata: master BENAR** (Gen 2=1988-1993 dst, tahun rapi, PUNYA SKU SP/OP HYN-SON-SP-...). Masalah murni di LISTING: UA 84 baris OFFSET (Gen 2→G5/G6, harusnya G2), OT 15 kosong, OP 61 kosong+1 offset, SP 43 kosong+10 offset. Beda dari Elantra-SP (yg master-nya typo) — Sonata bisa dibenerin bersih.
- **FIX (`fix_model_offset.py sonata --apply`)**: reassign offset + isi kosong pakai `resolver_sync.resolve_sku` (year-match) → **120 baris beres** (84 offset dibetulkan jadi Gen N cocok tahun + 36 kosong diisi). Verifikasi SESUDAH: **UA offset=0, OT offset=0**, OP sisa 1, SP sisa 10 (sisa 11 ini master SP/OP Strip/Transparan-nya belum punya gen itu = gap master, bukan bisa dibenerin sekarang). Lazada 0 dup.
- **BUG PENTING di tool-ku yg ke-catch & di-fix**: set `master_skus` (utk cek "target SKU ada?") awalnya dibangun dgn MERGE dua lookup dict `{**full,**sp}` → key (model,kat,gen,warna) SAMA antara UA & SP bikin nilai UA KETIMPA SP → ratusan SKU UA hilang dari set → salah tolak (219 "target tak ada" padahal ada). Fix: union `set(full.values())|set(sp.values())`. **Pelajaran: kalau butuh himpunan SEMUA nilai dari 2 dict, JANGAN merge by key (bisa saling timpa) — union values langsung.**
- **`fix_model_offset.py` REUSABLE** utk model offset lain yg master-nya bersih (tinggal `python3 fix_model_offset.py <namamodel> --apply`). Tapi tetap cek dulu master model itu bener (bukan typo/model-confusion) sebelum jalan.

**(2026-07-23) User tanya ulang "Sonata ini udah solved belum?" → re-verifikasi live + ketemu 1 bug baru (Transparan-by-name).**
- **Re-cek live**: status 07-21 di atas MASIH BENAR. UA/OT Sonata 0 offset (beres). OP/SP sisa 11 baris offset = gap master asli (SP/OP Strip/Transparan blm punya gen itu), TIDAK bisa dibenerin tanpa update master dulu — ini BUKAN bug tooling, memang belum bisa selesai.
- **Tapi bagian "SP & OP kosong SKU-nya"**: pas dicek ulang detail per-baris, ketemu ~180 baris msh kosong via `derive-from-UA` yg hasilnya TAK ADA di master (`no_master_key`/`derived` tapi bukan di `master_skus`) = gap master genuine, sama kelasnya dgn 11 di atas (skala lbh besar krn kena semua kombinasi gen×warna×Transparan/Strip, bukan cuma yg offset).
- **BUG BARU ketemu**: listing yg NAMA-nya sendiri sebut "Transparan" (mis. "Cover Mobil Transparan Hyundai Sonata") tapi teks varian CUMA "Gen N (tahun)" — tanpa kata "Transparan" diulang di varian. `parse_color()` cuma baca teks varian, jadi return `no_color` → baris ketinggalan kosong padahal harusnya jelas Transparan (kategori itu tak ada pilihan warna lain). **Fix di `resolver_sync.py` `resolve_sku()`**: kalau `parse_color(var)` gagal DAN nama listing mengandung "transparan" → paksa kategori/warna = Transparan.
- **Verifikasi aman**: re-run validation harness sesudah patch → match naik 76%→78%, mismatch turun 4%→3% (bukan regresi). `recompute_trusted.py` ulang → 169 model trusted (konsisten).
- **Apply ke SEMUA model** (bukan cuma Sonata, krn pola bug sama berlaku ke listing manapun yg judulnya sebut Transparan) via `fix_transparan_name_gap.py --apply`: **222 baris beres** (155 ganti kode CVR-legacy + 67 isi kosong), tersebar OT 24 / OP 27 / SP 171. Semua "ganti" dicek dulu → 155/155 memang kode `CVR*` lama (bukan sesuatu yg valid ketiban). Lazada uniqueness dijaga (1 baris di-skip krn collision, 0 dup baru).
- **Temuan sampingan (BUKAN dari fix ini, pre-existing)**: file Lazada UA (`Stok & Harga Lazada Undercover`) punya 4 pasang baris "BMW X5 Premium" dgn SKU IDENTIK antar 2 listing beda (row 2416 vs 3063, dst — satu row varian lengkap "Gen X,Abu-abu", satu row cuma "Gen X" tanpa warna, sama-sama diarahkan ke SKU warna Abu-abu yg sama). Ini pelanggaran unique-SKU-per-listing Lazada yg SUDAH ADA dari sebelum sesi ini, belum diperbaiki — perlu keputusan user (kemungkinan listing "tanpa warna" itu harus dihapus/diarahkan ke SKU beda).
- **KESIMPULAN utk user**: Sonata "udah solved" = YA untuk bug listing (generasi offset & sebagian kosong krn nama-Transparan), TIDAK utk bagian yg akar masalahnya gap di master SP/OP sendiri (~190 baris gabungan, perlu tambah data master, bukan script).

**(2026-07-23, lanjutan) User upload `Mobil_Terlaris.xlsx` (Top 300 baru) + info "Transparan Otonation sudah diarsipkan" + minta perbaiki Sonata & kasus serupa.**
- **Perbandingan Top-300 baru vs 331 lama**: TIDAK identik — data sudah di-refresh (kuantitas beda, mis. Avanza 2342→2372). 208/217 model baru match persis ke 331 lama, 3 lagi cuma beda gaya nama. **~108 model di 331 lama sudah TIDAK masuk Top-300 baru** — termasuk Hyundai Sonata sendiri, Hyundai Elantra, Jeep Cherokee, Chevrolet Optra Magnum, Kia Sedona, Toyota Previa, Suzuki Grand Vitara. Daftar 331 terlaris yg dipakai sesi ini mulai usang; scope berikutnya sebaiknya di-refresh ke file baru ini kalau user minta.
- **Otonation + Transparan = ARSIP (bukan bug)** — dikonfirmasi user. **Action item ke depan**: JANGAN lagi tandai gap "Transparan tak ada di master Otonation/UA" sebagai temuan yg perlu dikejar; itu keputusan bisnis (produk dihentikan), bukan sinkronisasi yg belum selesai.
- **AKAR MASALAH Sonata SP/OP kosong, ditemukan lewat investigasi mendalam (bukan cuma gap data seperti dikira sebelumnya) — ADA 2 BUG TOOLING BARU di `resolver_sync.py`, keduanya sama-sama "generasi tidak category-aware":**
  1. `gens_ua`/`gens_sp` (set label generasi per model) dulu digabung LINTAS KATEGORI — jadi generasi "Gen 2" dari kategori Reguler ikut dianggap valid label utk kategori Transparan/Strip yg sebenarnya generasinya beda skema (lebih kasar). **Fix**: tambah `gens_ua_kat`/`gens_sp_kat` keyed `(model,kategori)`, `parse_gen()` sekarang terima parameter `kat` dan filter ke situ (fallback ke versi lama kalau kategori itu sendiri kosong).
  2. **Lebih dalam lagi**: `mgen_year` (tabel tahun per label generasi) JUGA digabung lintas kategori pakai `setdefault` — jadi label "Gen 1" kepatok ke tahun kategori Reguler (mis. 1985-1987) walau kategori Transparan py "Gen 1" SENDIRI dgn rentang tahun beda total (1983-2001, broad bucket). Ini yg bikin varian "Gen 2 (1988-1993)" Transparan gagal ketemu SKU walau harusnya cocok ke bucket "Gen 1" Transparan yg overlap penuh. **Fix**: tambah `mgen_year_kat` keyed `(model,kategori)`, dipakai duluan sebelum fallback ke tabel lama.
  - **Validasi**: harness reproduksi naik 78%→80% match, mismatch turun sedikit, 0 regresi terlihat di sample mismatch (semua contoh mismatch yg tersisa adalah kasus lama yg sudah dikenal: rentang tahun open-ended "sekarang/2026" bikin ambigu gen mana yg "current").
  - **`trusted_models.json` naik jadi 174 model** (dari 169).
- **Gap tambahan ditemukan & diperbaiki di MASTER (bukan cuma listing)**: 864 kombinasi (model,kategori,warna,generasi) yg SUDAH ADA & valid di baris Toko=Smartprotection, tapi baris Toko=Otoprotection-nya TIDAK PERNAH dibuat sama sekali di master — lintas puluhan model (Chevrolet Spark, Ford Focus, Hyundai Elantra, Hyundai Sonata, Kia Carens, Lexus LX/RX, beberapa kelas Mercedes, Mitsubishi Lancer, VW Tiguan, Opel Blazer, Ford Everest, Jeep Cherokee, Kia Rio Sedan, Range Rover, Mitsubishi Delica, dll — masing2 26-32 baris). **User approve via chat biasa ("Oke lanjutkan") setelah AskUserQuestion ditolak sistem** — tool call ditolak, saya lanjut tanya di teks biasa, itu baru di-ACC.
  - **Fix**: disalin PERSIS dari baris Smartprotection yg sudah tervalidasi (SKU sama persis, cuma kolom Toko + Nama Produk Bigseller diganti) ke KEDUA file master lokal (`MASTER_from_drive_20260715.xlsx` dan `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` — lihat catatan di bawah soal kenapa ada 2 file). 864 baris ditambahkan ke masing-masing.
  - **Catatan jujur**: setelah ditelusuri, mirror OP ini TERNYATA TIDAK mengubah perilaku resolver (`master_lookup_sp.json`/`fwd_sp` cuma dibangun dari baris Toko=Smartprotection lewat `build_lookup_sp.py` — OP listing tetap lookup ke `fwd_sp` yg sama). Jadi mirror ini murni perbaikan KELENGKAPAN DATA MASTER (konsistensi kolom Toko, berguna kalau ada proses lain yg baca kolom Toko langsung), BUKAN yg menyelesaikan bug Sonata — yg benar2 menyelesaikan adalah 2 fix tooling di atas (category-aware gen matching).
  - **TEMUAN PENTING lain**: ada 2 salinan lokal file master yg BERBEDA (`MASTER_from_drive_20260715.xlsx` vs `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx`, md5 beda, dibuat script berbeda) — utk Sonata isinya identik (dicek manual), tapi belum diverifikasi utk model lain. `master_lookup_full.json`/`master_lookup_sp.json` (yg dipakai fwd_ua/fwd_sp) dibangun dari `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` (lewat `build_lookup.py`/`build_lookup_sp.py`), sedangkan tabel tahun generasi (`mgen_year`) di `resolver_sync.py` dibangun langsung dari `MASTER_from_drive_20260715.xlsx`. Kedua file sudah disinkronkan manual (edit yg sama diterapkan ke dua-duanya) tapi INI PERLU DIRAPIKAN jadi SATU sumber saja di sesi berikutnya supaya tidak ada risiko divergensi diam-diam.
- **Rollout perbaikan ke SEMUA 331 terlaris** (`fix_all_terlaris.py`, generalisasi dari `fix_model_offset.py` tapi loop semua model sekaligus per file, bukan 1 model per run): dijalankan dry-run→sample-check→apply.
  - **Hasil: 1.455 baris diperbaiki** (822 isi-kosong + 439 ganti kode lama/stale + 194 offset generasi dibetulkan), **50 model terdampak**. Top model: Range Rover (230), Chevrolet Spark (102), Ford Focus (102), Kia Rio Sedan (90), Suzuki Carry (82), Jeep Cherokee (80), Volkswagen Golf (73), Ford Everest (63), Mazda CX-3 (59), Mercedes Benz E Class (52), Land Rover Discovery (47), Mazda 3 (40), Kia Carens (40), Hyundai Excel (40), Toyota Corolla (33), Chevrolet Cruze (31), Chevrolet Aveo (31), Mazda CX-30 (29), Chevrolet Trooper (27), Kia Sedona (18), dst.
  - **Sisa (BUKAN bug, genuine gap/kasus khusus)**: 4.933 baris tak bisa di-resolve otomatis (butuh investigasi manual per model — kombinasi nama/generasi/warna yg masih ambigu), 84 baris "target tak ada di master" (mis. Sonata Strip utk tahun 1985-1998 — SP/OP memang belum pernah py cakupan Strip utk generasi setua itu, beda dari gap Transparan yg ternyata cuma bug matching; ini genuine perlu tambah generasi baru ke master kalau mau dilengkapi), 232 baris di-skip karena akan bikin duplikat SKU di Lazada (aman, sesuai desain).
  - **Verifikasi**: 0 duplikat SKU baru di Lazada (4 duplikat di Lazada Undercover = pre-existing dari sebelum sesi ini, soal BMW X5 Premium, belum diperbaiki — perlu keputusan user terpisah). Validation harness re-run sesudah apply: 80% match, 3% mismatch, mismatch count malah turun (banyak baris offset yg tadinya "salah" sekarang jadi "benar").
- **File yg berubah hari ini (semua ada di scratchpad, sebagian sudah dikirim ke user)**: `MASTER_from_drive_20260715.xlsx`, `SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` (864 baris Otoprotection ditambahkan), + listing: UA Shopee1-4, UA TikTok, UA Lazada, OT Shopee1-2, OP Shopee1, OP TikTok2, SP Shopee1-2, SP TikTok, SP Lazada.
- **Pelajaran kuat baru**: kalau ada kategori (Strip/Transparan/Exclusive) yg generasinya LEBIH KASAR dari kategori lain (Reguler) utk model yg sama, JANGAN bangun tabel generasi (baik SET label maupun TAHUNnya) secara model-wide — harus per (model,kategori), soalnya label yg sama (mis. "Gen 1") bisa punya arti/rentang tahun BERBEDA TOTAL antar kategori. Ini kelas bug yg sama dgn "dual-scheme" yg sudah diketahui sebelumnya, tapi lebih halus (tidak kelihatan dari nama label yg konsisten "Gen N", cuma kelihatan kalau dicek rentang tahunnya).

## RENCANA BESAR BARU: SKU berbasis FORMULA (mulai 2026-07-24) — MASIH DESAIN, BELUM DIEKSEKUSI

**Instruksi eksplisit user 2026-07-24 (override aturan "7 aturan final jangan diubah"):** ubah cara tulis SKU. **Jumlah kode SKU (segmen generasi) = jumlah FORMULA (ukuran jahitan cover), BUKAN jumlah generasi.** Fokus tetap ke daftar terlaris terbaru.

**Sumber data:** file upload user `Data_Mobil_Lebih_dari_1_Formula.xlsx` **Sheet2** (versi terakhir 213 model, kolom: No, Nama Mobil, Generasi/grup, Total Formula, Notes). Ada 2 versi upload — pakai yg TERBARU (229eb2b0..., 213 model). Snapshot lokal: `_formula_config_v2.json` (config per model), `_formula_models_v2.json`.

**Logika final (dikonfirmasi lewat contoh user):**
- **Total Formula = 1** → SEMUA generasi collapse jadi SATU kode. Kode = **G1** (relabel) utk model bergenerasi-angka. Contoh user: Kijang (Gen1,2,3→semua G1), Hilux (4 grup→G1), Rocky (F70/F300+Gen2 → G1, "karena ada urutan Gen 2 nya, kalau 1 formula tulis G1, berlaku utk produk lain kasus sama").
- **Total Formula = jumlah grup** → tiap grup 1 kode = **nomor generasi PERTAMA di grup**. Contoh: Avanza (Gen1-2→G1, Gen3→G3), Corolla 9 formula (Gen1-2→G1, Gen3→G3, ... Gen9,10,12→G9, Gen11→G11), Civic 11→G1..G11.
- **IN-BETWEEN** (formula >1 tapi ≠ jumlah grup) → cuma Mini Cooper (formula 2, 5 grup). DITUNDA (user bilang "logic menyusul").
- Segmen bagian lain SKU (MEREK-MODEL-TOKO-KATEGORI-WARNA) TIDAK berubah, cuma segmen generasi.
- **Model bergenerasi-NAMA (bukan angka)** tetap pakai nama, TIDAK dipaksa G1: Hardtop→J40 (user konfirm; ada listing lama pakai G4 yg perlu direvisi ke J40), HiAce→COM, Starlet→KTK/KPS (sudah benar), Jimny→3P/5P, BMW M3→chassis E30/E36/dst, Jeep Wrangler→TJ/JK/JL. (Beda dari Rocky yg PUNYA Gen-angka.)

**MASALAH KRUSIAL yg ditemukan (belum diputuskan user):**
- **17 model collapse yg master-nya TIDAK punya G1** (Vellfire punya G2+ saja, Suzuki Carry G6+, HRV G2+, Rocky F7+G2, dst). Kalau "paksa G1" (Opsi A, rekomendasi Claude, ikut instruksi Rocky) → **MASTER harus ikut ditulis ulang** supaya punya segmen G1. Kalau "pakai terendah yg ada" (Opsi B) → master aman tapi kode tak seragam. **User BELUM jawab** (AskUserQuestion 2x tak dijawab; user prefer prosa & bilang "lempar saja pertanyaannya" tapi lalu re-send file yg sama tanpa jawab).
- **Cakupan** (listing saja vs listing+master) juga belum dijawab.

**Cross-check Gen/Tahun file-formula vs master UA (`Rancangan_SKU_Formula_DRAFT_2026-07-24.xlsx`):** 46 selisih. **User klarifikasi: FILE FORMULA yg jadi patokan** (bukan master UA), karena master UA sering KURANG lengkap. Poin penting user:
- Grup seperti "Gen 1-2" TIDAK harus ada sbg grup di listing/master — kalau ada Gen 1 saja atau Gen 2 saja itu sudah dianggap ada & sesuai. Termasuk kalau cuma ada di varian **Exclusive** (Reguler slot varian terbatas krn ada varian warna; Exclusive bisa muat lebih banyak generasi krn tanpa warna). → Jadi banyak flag "Gen belum ada di master UA" itu FALSE ALARM.
- Vellfire: listing pakai Gen 2..Gen 4 (mulai Gen 2, bukan 1), tapi formula "Gen 1-3" → collapse G1. Di listing skrg tidak konsisten (ada G1, G2, G3F). 
- Wuling Air EV: listing tahun sampai 2026 (formula 2022-2026 benar, master 2022-2024 outdated). Skrg sudah mostly G1.

**Sudah dibuat (deliverable, dikirim ke user):**
- `Rancangan_SKU_Formula_DRAFT_2026-07-24.xlsx` — 4 sheet: logika, peta kode SKU baru per model, cek Gen-Tahun vs UA, perlu-keputusan.
- `Pilot_SKU_Formula_PREVIEW_2026-07-24.xlsx` — PREVIEW before→after 8 model contoh (Kijang/Avanza/Corolla/Hilux/Vellfire/Rocky/Hardtop/Civic). Hasil: **1.592 baris akan berubah** di 8 model itu (Hilux 444, Kijang 398, Corolla 350, Rocky 296, Vellfire 87, Hardtop 17; Avanza & Civic 0 = sudah benar). **102 SKU-baru-unik belum ada di master** (butuh Opsi A master-update). **132 SKU jadi kembar di Lazada** (skema collapse bikin banyak varian 1 SKU → Lazada wajib unik → varian perlu digabung/dihapus).

**Script:** parser Sheet2 + config di inline python (belum dijadikan file .py permanen). Preview generator inline. `variant_new_seg()`: collapse→G1 (atau nama utk named-gen), per-row→match gen-number ke grup lalu ambil code grup.

**STATUS: SUDAH DIEKSEKUSI 2026-07-24** (lihat bagian "EKSEKUSI" di bawah). Keputusan user: collapse→**G1 dipaksa** (master ikut diupdate), cakupan **listing + master**.

### EKSEKUSI skema formula (2026-07-24) — SUDAH APPLY

**Keputusan final user (dijawab lewat prosa + screenshot, setelah AskUserQuestion 2x tak dijawab):**
- Collapse (TF=1) → **selalu G1**, walau master belum punya G1 → master ikut ditulis ulang. User eksplisit: Vellfire→G1 ("di listing e-commerce ada Gen 1 nya"), HRV→G1, Rocky→G1, "berlaku juga untuk produk lain kalau ada case yg sama".
- Cakupan: **listing + master**.
- **Hyundai Stargazer**: TF=2 tapi file formula cuma punya 1 grup → user kasih screenshot listing: ada Gen 1 (2022-2024) & Gen 2 (2025-2026) → jadi G1+G2. Ditangani lewat `EXTRA_GROUPS` di `formula_config.py`.
- **Daihatsu Gran Max dipisah MB (minibus) vs PU (pickup)** — di file formula namanya tercecer 4 gaya (Gran Max PU / Gran Max Pick Up / Gran Max Minibus / Gran Max MB) → digabung lewat `MERGE_NAME`.
- Generasi bernama tetap pakai nama (TIDAK dipaksa G1): Hardtop→J40 (user konfirm; listing lama ada yg pakai G4, sudah dikoreksi), HiAce→COM, Land Cruiser→J60, Starlet→KTK/KPS, Jimny→3P/5P, SX4→XOV/SCR, BMW M3 & Jeep Wrangler→chassis.

**Script permanen (REUSABLE, di scratchpad):**
- `formula_config.py` — parser Sheet2 file formula + aturan → `CFG` (205 model siap) & `BLOCKED` (6 ditunda). Fungsi kunci `seg_for_variant(cfg, var)`: prioritas (1) label bernama, (2) nomor Gen di teks varian, (3) overlap rentang tahun.
- `apply_formula_sku.py` — apply ke 17 file listing + 2 file master. Ada dry-run default, `--apply` utk eksekusi. Punya matcher nama sendiri (concat-sig + token-subset, sama pola dgn `resolver_sync.master_model_of`) yg JUGA mengenali nama model BLOCKED supaya barisnya sengaja dilewati (bukan salah-match ke model lain).

**HASIL APPLY:**
- **34.511 baris listing diubah** di **138 model**; **24.541 baris master diubah** (di KEDUA file master).
- 24.807 baris sudah benar (tak disentuh); 11.264 dilewati krn SKU-nya belum format standar (CVR legacy/kosong); 1.946 dilewati krn model ditunda; 48 varian tak terbaca.
- Top model terdampak: BMW Seri 3 (888), Mercedes E Class (779), Toyota Camry (750), Mitsubishi Triton (740), Land Cruiser (740), Range Rover (739), Nissan Serena/Honda Accord/Odyssey/Ford Fiesta (592 masing-masing).

**VERIFIKASI sebelum apply (penting, jangan skip kalau mengulang):**
1. Model collapse → 100% hasilnya seragam 1 kode, **0 penyimpangan**.
2. Model per-row → **4.587 baris dicek, 100% cocok** dgn nomor generasi di teks varian.
3. **Backup semua file asli** di `BACKUP_sebelum_formula_20260724/` (19 file, 24 MB).
- **Pelajaran**: sempat kelihatan seperti bug waktu sampel menunjukkan Corolla `G6→G5`. Setelah ditelusuri ternyata BENAR — teks variannya "Gen 5 (1983-1987)" dan SKU lama G6-nya yg salah (sisa bug offset lama). **Jangan menilai benar/salah dari pasangan SKU lama→baru saja; harus lihat teks variannya.**

**KONSEKUENSI PENTING — LAZADA: 3.696 baris jadi SKU KEMBAR dalam 1 listing.** Ini melekat pada desain (1 formula = 1 SKU, sedangkan Lazada wajib SKU unik per listing). Varian2 tsb memang produk fisik SAMA. **User harus menggabung/menghapus varian tsb di Lazada** — daftar lengkap di sheet 'Lazada Perlu Digabung' pada `Hasil_SKU_Formula_2026-07-24.xlsx`. Belum ada aksi otomatis utk ini.

**6 MODEL DITUNDA (belum diubah, nunggu jawaban user):**
1. **Mini Cooper** — TF=2 tapi 5 tipe (Hatch/Clubman/Countryman/Roadster/Paceman); user bilang "logic menyusul".
2. **Nissan Navara** — TF=2 tapi 4 grup generasi; grup mana berbagi formula belum jelas.
3. **Nissan Livina X-Gear** — kolom Total Formula masih '?' di file.
4. **Honda Civic Hatchback** — Total Formula masih '?'.
5. **Daihatsu Gran Max** (polos, tanpa PU/MB) — ambigu maksudnya yg mana.
6. **Mitsubishi Strada Triton** — duplikat Mitsubishi Triton (ditandai ungu user) → sengaja di-skip permanen, tidak perlu aksi.

**Deliverable dikirim ke user**: `Hasil_SKU_Formula_2026-07-24.xlsx` (5 sheet: Ringkasan, Ringkasan per Model, Detail Perubahan 34.511 baris, Lazada Perlu Digabung, Model Ditunda) + master baru + 17 file listing.

## PRODUK MOTOR — rancangan SKU baru (2026-07-24, user minta "sekalian update SKU produk motor")

**Struktur motor BEDA FUNDAMENTAL dari mobil — WAJIB diingat:**
- **Motor TIDAK PUNYA GENERASI sama sekali.** Varian listing HANYA warna. Jadi SKU motor tak perlu segmen generasi (mobil 6 segmen, motor 5).
- Kategori motor cuma **Reguler** (5 warna polos + 3 warna Elite) & **Premium** (1 warna, teks varian selalu literal "Default"). Tidak ada Exclusive/Transparan.
- Motor praktis **cuma dijual di Undercover Autocare** (Shopee3, Shopee4, TikTok; + 9 baris nyasar di SP Shopee1).
- Skala: **3.248 baris "Cover Motor"**, **228 model unik**, 14 merek (Yamaha 44, Honda 41, Kawasaki 39, Benelli 31, Ducati 17, Vespa 15, KTM 12, Suzuki 11, dst).

**SKU motor sekarang** = skema legacy `CM####-UC-<suffix>` (mis. `CM0185-UC-RPM`), sekeluarga dgn `CVR####` legacy mobil. Decode suffix: `RP<W>` = Reguler polos + huruf warna (A/H/M/B/G), `RSE<W>` = Elite, `PRPA` = Premium. **Nomor CM = identitas model** (227 nomor unik) — dipakai utk normalisasi nama listing yg tulisannya beda-beda (10 nomor CM punya >1 ejaan nama, mis. CM0009 = 'Aerox' & 'Yamaha Aerox'; CM0174 typo 'KKawasaki Z900').
- **Masalah padding**: nomor CM ditulis 2 gaya (`CM0183` vs `CM00183`) di 121 model — harus di-normalisasi (parse pakai `CM0*(\d+)`).

**BUG BESAR ditemukan (pre-existing, terlepas dari skema baru): 815 baris (29,3% dari baris berwarna) di 166 listing punya KODE WARNA SKU TIDAK COCOK dgn teks variannya.** Polanya deterministik & seragam (bukan typo acak) — kode warna tergeser posisi, konsisten 163 baris per warna:
`Abu-abu→RPM (harusnya RPA)`, `Hitam→RPB (RPH)`, `Biru Benhur→RPH (RPB)`, `Merah→RPG (RPM)`, `Hijau Army→RPA (RPG)`. Ini pola salah-tempel massal (urutan SKU ditempel ke urutan varian yg beda). Listing yg benar (mis. Kawasaki Ninja H2) urutannya Merah/Hijau/Abu/Hitam/Biru → RPM/RPG/RPA/RPH/RPB. **Teks varian = acuan kebenaran**, kode warna tinggal dihitung ulang dari nama warna.

**Rancangan skema baru (2 opsi, di file `Rancangan_SKU_MOTOR_2026-07-24.xlsx`, 5 sheet):**
- **Opsi A (rekomendasi Claude)**: `MEREK-MODEL-TOKO-KATEGORI-WARNA` → `HND-VAR125-UA-R-ABU`. 5 segmen; motor vs mobil otomatis kebedain dari jumlah segmen.
- **Opsi B**: `MEREK-MODEL-TOKO-KATEGORI-MTR-WARNA` → `HND-VAR125-UA-R-MTR-ABU`. 6 segmen, seragam bentuknya dgn mobil + penanda 'MTR' eksplisit (enak buat tooling yg expect 6 segmen).
- Kode merek konsisten dgn mobil di mana overlap: Honda=HND, Suzuki=SZK, BMW=BMW. Baru utk motor: Yamaha=YMH, Kawasaki=KWS, Vespa=VSP, Ducati=DCT, Benelli=BNL, KTM=KTM, Aprilia=APR, Cleveland=CLV, BF Goodrich=BFG, Alrendo=ALR, Bajaj=BJJ.
- Kategori: R/P/S (S utk Elite). Warna sama dgn mobil: ABU/HTM/MRH/BRU/GRN; Elite: EAB/EBR/EGR/EMR.
- Generator kode model: token angka dipertahankan utuh, token campur huruf-angka (CB150, KLX150SM, R15, H2) dipertahankan s/d 7 char, token huruf murni diambil 3 huruf; total ≤10 char; tabrakan diberi suffix angka. **Hati-hati bug**: versi awal `t[:3]` bikin `CB150`→`CB1` dan `KLX150SM`→`KLX` (tabrakan) — sudah difix dgn deteksi `re.search(r'\d', t)`.
- **Hasil: 1.801 baris SKU, 1.790 unik.** 11 "duplikat" semuanya JINAK (typo warna yg memang produk sama: 'Hijau'='Hijau Army', 'Eite Hijau'='Elite Hijau', 'Elite BIru'='Elite Biru').

**Pertanyaan ke user yg belum dijawab (sheet 'Perlu Keputusan'):** (1) pilih Opsi A/B; (2) konfirmasi Premium motor warnanya Abu-abu (sekarang cuma tertulis "Default"); (3) model bernama "Maxi" saja (tanpa merek) — diasumsikan Yamaha Maxi; (4) ACC fix bug 815 baris warna; (5) apakah motor mau dijual di toko lain juga; (6) apakah motor mau ada kategori Exclusive/Transparan.

**Script/artefak**: `_motor_rows.json`, `_motor_cm.json`, `_motor_norm.json`, `_motor_catalog.json`, `_motor_sku_proposal.json`, `_motor_badcolor.json` (semua di scratchpad; generator masih inline python, belum jadi .py permanen).

**Jawaban user 2026-07-27 (sebagian):**
- **Format motor = Opsi B (6 segmen, ada penanda 'MTR')** → `MEREK-MODEL-UA-KAT-MTR-WARNA`.
- **ACC betulkan bug warna tertukar** → SUDAH DIKERJAKAN (lihat di bawah).
- Sisa pertanyaan (warna Premium, 'Maxi') masih ditanyakan user ke tim produksi.

**SUDAH DIEKSEKUSI 2026-07-27 — perbaikan 815 baris warna motor tertukar** (`fix_motor_warna.py`, ada dry-run + `--apply`):
- Teks varian = acuan; kode warna dihitung ulang dari nama warnanya. Skema `CM####-UC-<suffix>` yg lama DIPERTAHANKAN (belum ganti ke skema baru — nunggu jawaban warna Premium & 'Maxi').
- Hasil: **815 baris diperbaiki di 166 listing**. File berubah: UA Shopee3 (924 baris benar), UA Shopee4 (508), UA TikTok (1.346).
- **Verifikasi sesudah: 2.778 baris cek warna → 100% benar, 0 sisa salah.**
- **Jebakan yg kena**: menjalankan `--apply` lalu verifikasi dry-run dalam SATU perintah bikin `_motor_warna_changes.json` KETIMPA jadi kosong (dry-run kedua menemukan 0 perubahan lalu menulis ulang file log). Perbaikannya sendiri tetap berhasil — dikonfirmasi dgn baca ulang isi file. **Lain kali: pisahkan run apply dan run verifikasi, atau jangan pakai nama file log yg sama.**

## Riset LAZADA + BigSeller SKU Mapping Rules (2026-07-27)

**Masalah**: skema formula bikin banyak varian 1 listing berbagi SKU, padahal Lazada wajib Seller SKU unik. User menolak solusi "gabung varian manual di Lazada" (terlalu lama).

**Riset ke dokumentasi BigSeller** (artikel yg user kirim `help.bigseller.com/in/detailPage/4/1/4142` — **403 kalau di-WebFetch langsung, perlu login**; isinya didapat lewat WebSearch):
BigSeller punya fitur **SKU Mapping Rules** yg bisa mencocokkan beberapa Store SKU ke SATU merchant/warehouse SKU dgn mengabaikan awalan/akhiran. Dua mode:
1. **Berdasarkan JUMLAH KARAKTER** — "Ignore Last N characters". Contoh resmi: `AAQ-03` + ignore last 1 → `AAQ-0`. **Butuh panjang akhiran KONSISTEN.**
2. **Berdasarkan PEMISAH (delimiter)** — isi delimiter tetap (mis. `&`) + pilih kemunculan ke-berapa dari kanan; semua setelah delimiter itu dibuang. Contoh resmi: `Red&001&xxs&Shopee` + delimiter `&` ke-1 → `Red&001&xxs`. **TIDAK butuh panjang konsisten.**

**Jawaban utk pertanyaan user "apakah perlu abaikan 3 karakter akhir? jumlah karakternya konsisten 3 ngga?":**
- Dgn akhiran yg saya rancang sebelumnya (`-G1`,`-G11`,`-EPIC`,`-KTK`), panjangnya **TIDAK konsisten**: terukur 2–6 karakter (6.710 baris 3-char, 538 4-char, 499 5-char, 159 6-char, 4 2-char). Jadi **"ignore last 3" akan MERUSAK** sebagian SKU.
- Maka ada 2 jalan benar:
  - **Opsi A — DELIMITER (rekomendasi)**: pakai pemisah yg TIDAK pernah muncul di SKU dasar, mis. `_` atau `#` → `HND-CTY-UA-P-G1-SLV_G3`. Rule BigSeller: Ignore Suffix + delimiter `_` + kemunculan ke-1. Panjang bebas, dan SKU tanpa `_` tidak terpengaruh. **Sudah dicek: karakter non-alfanumerik yg ADA di Seller SKU Lazada saat ini cuma `-` , jadi `_` dan `#` dua-duanya aman.**
  - **Opsi B — PANJANG TETAP**: semua SKU Lazada diberi akhiran 2 digit `-01`,`-02`… (selalu tepat 3 karakter termasuk tanda minus) lalu rule "ignore last 3". Konsisten TAPI harus disematkan ke **SELURUH 21.031 baris** Lazada berformat master (kalau ada baris tanpa akhiran, rule-nya akan memotong SKU itu secara salah). Maks varian berbagi 1 SKU = 10, jadi 2 digit cukup.
- Script `fix_lazada_unik.py` sudah ada (dry-run + `--apply`), tapi **masih memakai akhiran gaya lama `-G3` yg panjangnya tidak konsisten** → HARUS diubah dulu ke Opsi A atau B sebelum dipakai. Simulasi sebelumnya: 7.910 baris diberi akhiran → 0 SKU kembar tersisa di kedua file Lazada.

## Bug matcher tipe-badan + audit "kasus serupa Gran Max" (2026-07-27)

**User curiga baris "Daihatsu Gran Max" polos itu salah karena Gran Max harusnya ada tipe Minibus/Pickup — TERNYATA BENAR, dan ada BUG di matcher saya.**
- Master SUDAH benar membedakan: **Gran Max Minibus = `DHT-GMX`**, **Gran Max Pick Up = `DHT-GMXP`**.
- **BUG**: listing menulis "Minibus"/"Pick Up" sedangkan file formula menulis "MB"/"PU" → matcher tak bisa menyamakan → 295 baris jatuh ke base "Daihatsu Gran Max" yg berstatus DITUNDA → **barisnya kelewat, tidak ikut diproses** (untung tidak menulis SKU salah).
- **Fix**: tambah `ALIAS_RE` + `_prenorm()` di `apply_formula_sku.py` — rewrite nama listing sebelum matching: `Gran Max Minibus→Gran Max MB`, `Gran Max Pick Up→Gran Max PU`, `Carry Pick Up|Carry PU→Carry Pickup`. Sesudah fix, `dilewati_model_ditunda` turun 1.946→1.651 dan semua baris tsb ternyata **SKU-nya memang sudah G1** (0 perubahan data diperlukan) — jadi ini murni perbaikan akurasi matching, bukan koreksi data.

**Audit sistematis "kasus serupa"** (cari nama model yg jadi PREFIX nama model lain): **16 kasus**. Mayoritas SAH (mobil beneran beda): Pajero vs Pajero Sport, Xpander vs Xpander Cross, Yaris vs Yaris Cross, City vs City Sedan/Hatchback, Mazda 2 vs Sedan/Hatchback, Civic vs Civic Type R/Hatchback, Feroza vs Feroza Long, Datsun Go vs GO Plus, APV vs APV Arena/Luxury, Kia Rio vs Rio Hatchback, Avega vs Avega Hatchback, Tiggo 8 vs Tiggo 8 Pro, Terra vs Terrano. **Diverifikasi: matcher mengarahkan semuanya dgn BENAR** (Type R→config Type R, Hatchback→config Hatchback, dst).
- **Ejaan kembar ditemukan**: `Nissan X-Trail` vs `Nissan XTrail` (dua entri utk mobil sama; dua-duanya TF=1 jadi tak berdampak, tapi sebaiknya disatukan di file formula).
- **SISA MASALAH GRAN MAX (perlu jawaban user)**: 7 baris listing namanya TANPA tipe — "Cover Mobil Daihatsu Gran Max **Premium**" (3), "**Exclusive**" (3), "**Transparan**" (1). Ini genuinely ambigu: Minibus atau Pick Up? Sekarang di-skip.
- **Keluarga Suzuki Carry** ternyata di master ada **3 model terpisah**: `Suzuki Carry`=CAR (102 baris), `Suzuki Carry Futura`=CRF (66), `Suzuki New Carry Pick-Up`=NCR (66). Tapi file formula user cuma punya "Suzuki Carry" & "Suzuki Carry Pickup" — **Carry Futura tidak ada di file formula**. Perlu dikonfirmasi user.

**Fakta tambahan yg ditemukan saat menjawab pertanyaan user (2026-07-27):**
- **Produk MOTOR cuma ada di Undercover Autocare** — dikonfirmasi scan seluruh 17 file: UA Shopee3 (1.090 baris/232 listing), UA Shopee4 (580/124), UA TikTok (1.574/411). **Otonation, Otoprotection, Smartprotection TIDAK menjual cover motor.** Yg terdeteksi di luar itu: 9 baris di SP Shopee1 (listing "Body Cover Motor / Selimut Motor <model>" — SKU-nya KOSONG semua, cuma varian Hitam, kemungkinan listing lama/nyasar) + 2 baris di UA Shopee2 yg sebenarnya produk shampoo ("Snow Wash ... Mobil & Motor"), bukan cover motor. Jadi perbaikan 815 baris warna kemarin memang SUDAH mencakup semua toko yg relevan.
- **Warna Premium motor = ABU** (dikonfirmasi user: "sama seperti yg di premiumnya cover mobil").
- **Produk 'Maxi' diabaikan dulu** (instruksi user).

## Keputusan & temuan lanjutan (2026-07-27, sesi lanjut)

**LAZADA = OPSI A (delimiter `_`) — dipilih user.** `fix_lazada_unik.py` sudah diubah: konstanta `SEP = "_"`, akhiran jadi `HND-CTY-UA-P-G1-SLV_G3`.
- **Kekhawatiran user**: "rule ignore-suffix di BigSeller kan berlaku utk semua e-commerce, apakah Shopee/TikTok aman kalau SKU-nya tetap gabungan?" → **AMAN, dan justru ini alasan Opsi A dipilih**: mode delimiter hanya memotong kalau pemisahnya ADA. SKU Shopee/TikTok tidak mengandung `_` sama sekali (sudah dicek: karakter non-alfanumerik di SKU cuma `-`), jadi tidak tersentuh. Kalau memakai mode "potong N karakter" (Opsi B), Shopee/TikTok JUSTRU akan rusak karena rule-nya berlaku tanpa syarat. **Catatan kejujuran: perilaku BigSeller belum bisa saya uji langsung (butuh login) — sarankan user tes dulu ke 1-2 produk sebelum massal.**

**NISSAN NAVARA — aturan dari user**: formula 1 = Gen 1,2,3 ; formula 2 = PRO-4X. Diimplementasikan lewat mekanisme baru `MANUAL_GROUPS` di `formula_config.py` (pengelompokan eksplisit: daftar `(kode, [kata kunci di teks varian])`), dipakai `seg_for_variant()` sebelum logika normal.
- Master ternyata sudah memisahkan KODE MODEL: **Navara = `NSN-NVR`**, **Navara PRO-4X = `NSN-NVP`** (PRO-4X tercatat sbg "Gen 4" 2020-2026). Karena kode modelnya beda, dua-duanya boleh memakai segmen **G1** tanpa bertabrakan → hasil: `NSN-NVR-...-G1` & `NSN-NVP-...-G1`.
- Diverifikasi: **442 baris Navara berubah** (NVR 296, NVP 146), 0 tabrakan lintas-model. Navara keluar dari daftar DITUNDA.

**GRAN MAX 7 baris "tanpa tipe" — TERNYATA TIDAK AMBIGU**, tipenya ada di TEKS VARIAN (bukan di nama listing):
- **6 baris di UA Lazada** (listing "…Gran Max Premium" & "…Gran Max Exclusive"): variannya **"Blindvan (2008-2024)"**, **"Pickup (2008-2024)"**, "Model Lain/Custom". SKU-nya masih placeholder angka Lazada (`8664138934-…`), jadi memang belum pernah dapat SKU master.
- **1 baris di SP TikTok** ("…Gran Max Transparan", varian "Gen 1 : 2007-2026") SKU-nya `DHT-GMXP-SP-T-G1-TRP` — **sudah benar** (GMXP = pickup, G1).
- Artinya: Blindvan→keluarga Minibus (`DHT-GMX`), Pickup→`DHT-GMXP`. Konsisten dgn rename master 2026-07-21 yg menggabung "Minibus/Blind Van"→Minibus. **Masih perlu konfirmasi user** apakah Blindvan memang disamakan dgn Minibus.

**SUZUKI CARRY — user: "hanya carry dan carry pickup".** Dicek: **`Suzuki Carry Futura` (kode CRF, 66 baris) ADA di master tapi TIDAK ADA di listing e-commerce manapun** → kemungkinan model usang/tidak dijual. Perlu keputusan user: hapus dari master atau biarkan.

**HASIL APPLY (2026-07-27):**
- **Navara**: 442 baris listing + 132 baris master (×2 file) diubah. Model terdampak: 1 (Nissan Navara).
- **Lazada Opsi A**: **7.976 baris diberi akhiran `_<tag>`** → **SKU kembar tersisa = 0** di kedua file Lazada. Aturan yg harus diset user di BigSeller: **Ignore Suffix, delimiter `_`, kemunculan ke-1 (dari kanan)**.

**SETTING BIGSELLER TERBUKTI BENAR (screenshot user 2026-07-27):** menu *Aturan Hubungan Pemetaan SKU* → centang "Jika SKU Toko Diproses Berdasarkan Aturan dan Sama Dengan Nomor SKU…" → radio **"Abaikan Akhiran"** → sub-opsi ke-3 **"Abaikan Karakter Pemisah Tetap dan Akhiran"**, pemisah **`_`**, *Saat Ada Beberapa Karakter Pemisah, Gunakan Pemisah* = **1**.
- **Jebakan yg sempat terjadi**: user awalnya mengisi angka **2** → kolom "Tes Aturan" menampilkan hasil TIDAK berubah (`HND-CTY-UA-P-G1-SLV_G1` tetap utuh) karena sistem mencari pemisah ke-2 sedangkan SKU kita cuma punya satu `_`. Setelah diubah ke **1**, hasil tes benar → `HND-CTY-UA-P-G1-SLV`.
- Sub-opsi lain di halaman itu: "Abaikan Akhiran N Karakter" (butuh panjang seragam — TIDAK cocok utk kita) dan "Abaikan Akhiran Karakter". JANGAN isi pemisah dgn `-` (SKU dasar punya 5 tanda `-`).
- Halaman itu punya kolom **"Tes Aturan"** — pakai utk membuktikan SKU Shopee/TikTok (tanpa `_`) tetap utuh sebelum Simpan.

## SKU MOTOR FINAL dibuat (2026-07-27) — `build_motor_sku.py`

Format final (Opsi B pilihan user): **`MEREK-MODEL-TOKO-KATEGORI-MTR-WARNA`** (6 segmen), mis. `HND-VAR125-UA-R-MTR-ABU`.
- Kategori: R=Reguler polos, S=Strip(Elite), P=Premium. Warna: ABU/HTM/MRH/BRU/GRN; Elite: EAB/EBR/EGR/EMR. Toko selalu `UA` (motor cuma dijual di Undercover Autocare).
- **Premium → selalu `P` + `ABU`** (varian di listing kosong/"Default" krn Premium tak punya pilihan warna; user konfirmasi warnanya Abu).
- **'Maxi' di-skip** (`SKIP_MODELS`) sesuai instruksi user.
- Nama model disatukan lewat nomor CM lama (`CM0*(\d+)`) supaya ejaan berbeda ('Aerox' vs 'Yamaha Aerox') jadi satu model.
- Generator kode model sama dgn rancangan sebelumnya: token angka utuh, token campur huruf-angka s/d 7 char, huruf murni 3 char, total ≤10, tabrakan diberi suffix angka.
- **HASIL: 3.234 baris, 227 model unik, 1.785 SKU unik, 0 baris gagal.**
- **BELUM di-apply ke file listing** — baru dibuat daftarnya utk direview user (`SKU_MOTOR_Final_2026-07-27.xlsx`, 4 sheet: Ringkasan, Daftar SKU Motor, Peta Kode Model, SKU Unik). Jalankan `python3 build_motor_sku.py --apply` kalau user sudah ACC.

**JAWABAN USER 2026-07-27 (lanjutan):**
- **SKU motor DISETUJUI** ("motor sudah sesuai") → `build_motor_sku.py --apply` dijalankan.
- **Nissan X-Trail vs XTrail = mobil yg SAMA**, typo di judul listing. **DICEK: sebenarnya TIDAK ADA MASALAH SKU** — master cuma punya SATU entri `Nissan X-Trail` → kode `XTR` (330 baris), dan SEMUA variasi ejaan di listing (XTrail / X-Trail / Xtrail) sudah mengarah ke `XTR`. Jadi typo-nya murni kosmetik di judul produk marketplace, tidak mempengaruhi SKU. Satu-satunya sisa: 3 baris "Nissan X-Trail Transparan" SKU-nya masih non-master (gap terpisah).
- **Suzuki Carry Futura**: user → "kalau tidak ada di listing e-commerce tidak perlu di input". Jadi CRF **tidak usah diurus/diinput**, biarkan saja di master (tidak dipakai).
- User minta **fokus bikin file siap upload dulu**; pertanyaan sisa menyusul.

## FILE LISTING BARU di Drive (diupload user 2026-07-27) — INVENTARIS LENGKAP

User upload export listing TERBARU ke folder BARU di dalam `List Produk SKU`
(`1GG8ZHvJjIF5oTfBHDB1iOgPrsdNux_MF`). Dibuat oleh akun **chandraadyasta@gmail.com**
(bukan under.covermobil), 2026-07-27 ~12:37-12:41. **Struktur & fileId:**

- **`Under Cover`** `178LjcV8_eDLjdIGjKROOGzbcK6tSSQ-T`
  - `Shopee UC` `19W-wPkhVrK3QIlHr2HFNNO0Bd5IN6-mq`: 1.xlsx `1k0d7PyRFeyHXfAtOkaJy_Kviyy06rRcc` (346KB), 2.xlsx `1e3c50KJXy6KePp27e79T8FUxEEOk3Vms` (345KB), 3.xlsx `1PvkGbnxQGoQuiw9OB13Vi14t585sUX9Y` (338KB), 4.xlsx `15dMvryqnn1RaP0Ft0nCbjXycc9f1simT` (376KB), 5.xlsx `1lbq2I9_hoQxsowdTDS-Iv3KWHE53p4ZM` (156KB)
  - `Tiktok UC` `1qRXmmKYj_jckCX_wctIr2o5b7-0TKZc6`: template_1 `1jamQV1YV1_5wkBhvpMoiepBcifTOvc05` (22KB), template_2 `1bo6SpIwvKoTIlA_IoiNqcnwBrjyvkdXM` (25KB), template_3 `1JYyIbScLFEO-gb9MNypo8BwidOBs5Clq` (5,76MB)
  - `Lazada UC.xlsx` `1xnlJ8glIRumWt0irCvoS33yc-SFCwgqz` (2,09MB)
- **`Smartprotection`** `1Puv1j93LV1MTVQZkiienQTd2qpOQ_ZPw`
  - `Shopee STP` `1hMwhHtR-garF6v1OzRsL5D5fe45BxymD`: 1.xlsx `1lwj4vcFCCQ9f5PwwOVdn9SgY5VFE-mWf` (377KB), 2.xlsx `1O4r8sdqn8izzoPP0UGIuz9V6vj_lHWZA` (164KB)
  - `Tiktok STP.xlsx` `10mWZLXsqY7AV5eanh4p9aSlfEawO3vsi` (4,07MB) | `Lazada STP.xlsx` `1BwvIAGqj5WwIGq3BXy7LU6Yz2yCQxwef` (760KB)
- **`Otoprotection`** `1kfrsCGC3HzO2WI9fu-tbDrXTUsiB8dMX`
  - `Shopee OTP` `1bv7eDt6q9p7SfR0-EZu3f1Z4XKxDM7H9`: 1.xlsx `1WjBI45XobHDAge0CuCFsedBMb_rcy7bo` (350KB), 2.xlsx `16VZ4Dwz6zqTvNx3KEMmFIvhcqcaq0aDj` (77KB)
  - `TikTok OTP` `1I_cwe4L8Y_3ELtDkekOMTueQgtDhFDqJ`: template_1 `1E5z1fmuBMcwNIFfoiRAQJZRTML-sLHSi` (2,77MB), template_2 `1X-sMkv-LUn_rYmtDEaltYesKzkzFyRvZ` (4,29MB)
  - (tanpa Lazada — konsisten, OP memang tidak jualan di Lazada)
- **`Otonation`** `1I3olV8d5XZm05eOh-hxbkBwAXa7Qu3KD`
  - `Shopee Otonation` `1dY3_VrqvZc1LWrVM5h-JTatS8XrpSBeC`: 1.xlsx `10-8qu6D8c2L8oklPkYWIWLqDYLMkTJBK` (337KB), 2.xlsx `1k-7HZAs3iHNZaRYnBCR5c0rBTItEx4WA` (322KB)
  - (tanpa TikTok/Lazada — konsisten, OT Shopee-only)

Total **19 file**. Cakupan channel COCOK dgn 17 file kerja yg sudah ada (+2 file TikTok UC kecil).
**`Mini Cooper` ada di 4 file** (dicek pakai `fullText contains`): `1.xlsx` di masing-masing folder Shopee UC / Shopee STP / Shopee OTP / Shopee Otonation.

**KENDALA TEKNIS PENTING (diuji 2026-07-27, jangan buang waktu mengulang):**
- `mcp__Google_Drive__download_file_content` **BERHASIL** utk file kecil — file 22KB terunduh utuh sbg base64. Jadi mekanismenya jalan.
- TAPI base64 ≈ 1,33× ukuran file, dan hasilnya masuk ke context. File 340KB → ~460KB base64 (~115rb token); file 5,76MB → ~7,7MB. **TIDAK MUNGKIN** ditarik lewat MCP tanpa menghabiskan context.
- `read_file_content` (representasi teks) juga berisiko sama utk file ratusan KB, dan dokumentasinya menyatakan konten bisa terpotong utk file besar.
- **JALUR YG TERBUKTI: minta user melampirkan file langsung di chat** → mendarat di `/root/.claude/uploads/…` dan bisa dibaca openpyxl secara lokal TANPA biaya context. Ini yg dipakai utk `Mobil_Terlaris.xlsx` & `Data_Mobil_Lebih_dari_1_Formula.xlsx` dan lancar.
- Catatan: ini melengkapi keterbatasan lama di [[project-undercover-git-drive-setup]] (upload besar ke Drive gagal) — sekarang terbukti **download besar dari Drive juga tidak praktis**.

## FILE BARU DITERIMA LEWAT LAMPIRAN CHAT (2026-07-27) — 19/19 LENGKAP

User melampirkan SEMUA 19 file ke chat (ukuran cocok persis dgn inventaris Drive), mendarat di
`/root/.claude/uploads/77f87f91-.../`. **Jalur lampiran chat TERBUKTI bisa utk file besar** (sampai 5,76MB) —
beda dgn konektor Drive yg mentok. Catat: ini cara yg dipakai ke depan.

**TEMUAN PALING PENTING — file baru ini BUKAN berisi hasil kerjaku, tapi EXPORT MENTAH dari marketplace:**
- Toyota Kijang di UC4 masih `{G1:17, G2:17, G3:17, G4:17}` → skema formula (semua→G1) **BELUM masuk**.
- Produk motor masih pakai kode `CM…` lama (UC1=8, UC3=1.055, UC4=364 baris) → format `MTR` **BELUM masuk**.
- Artinya: user belum meng-upload file hasil kerjaku ke marketplace, jadi export ini = **kondisi LIVE sekarang**.
- **KONSEKUENSI**: file hasil kerjaku (17 file lama) sudah usang dari sisi DAFTAR PRODUK. Yg benar:
  **jalankan ulang SEMUA pekerjaan SKU di atas file baru ini** (formula mobil, SKU motor MTR, akhiran `_` Lazada),
  supaya dapat daftar produk terkini + skema SKU baru sekaligus.

**Bug openpyxl yg ketemu**: file Shopee baru gagal dibaca dgn `load_workbook(read_only=True)` →
`ValueError: Value must be one of {'topLeft','bottomRight','topRight','bottomLeft'}` (atribut `activePane` tak lazim).
**Solusi yg dipakai**: parse XML mentah langsung dari zip (`xl/worksheets/sheet1.xml` + `xl/sharedStrings.xml`)
lewat `xml.etree`. Fungsi `rows_of()` sudah ditulis di scratchpad — pakai ulang kalau ketemu error sama.

## MINI COOPER — struktur varian akhirnya terlihat (dari file baru)

Varian Mini Cooper punya **2 sumbu**: `<warna ATAU tipe bodi>, <3 Pintu | 5 Pintu>`.
- **Undercover (Shopee UC 1, baris 412-451, 42 baris)**: baris berwarna PUNYA SKU, tapi segmen generasinya
  memakai NAMA TIPE BODI dan **TIDAK KONSISTEN dgn variannya**: varian "…,3 Pintu" → segmen `Roadster`;
  varian "…,5 Pintu" → segmen `Paceman`. (mis. `MNI-COO-UA-R-Roadster-BRU` utk "Biru Benhur,3 Pintu").
  Roadster & Paceman itu MODEL, bukan jumlah pintu → penamaan lama ini keliru.
  Baris yg sumbu-1-nya tipe bodi ("Paceman,3 Pintu", "Hatch,3 Pintu", "Roadster,5 Pintu", "Clubman,5 Pintu",
  "Countryman,5 Pintu") **SKU-nya KOSONG**.
- **Smartprotection (Shopee STP 1, baris 197-236, 40 baris)**: lebih masuk akal — "3 Pintu" → segmen
  `Hatch3Pintu`, "5 Pintu" → `Hatch5Pintu` (mis. `MNI-COO-SP-S-Hatch3Pintu-S3M`). Tapi segmennya kepanjangan &
  campur huruf besar-kecil, tidak sesuai konvensi (G1/J40/KTK/3P).
- **Tafsiran Claude (PERLU KONFIRMASI USER)**: Total Formula = 2 utk Mini Cooper = **3 Pintu vs 5 Pintu**
  (dua ukuran jahitan). 5 tipe bodi (Hatch/Clubman/Countryman/Roadster/Paceman) semuanya jatuh ke salah satu
  dari dua ukuran itu menurut jumlah pintunya. **Usul kode: `3P` dan `5P`** — konsisten dgn Suzuki Jimny yg
  sudah pakai 3P/5P. Hasil: `MNI-COO-UA-R-3P-ABU`, `MNI-COO-SP-S-5P-S1A`, dst.
- Yg masih harus ditanyakan: baris bertipe-bodi yg SKU-nya kosong — apakah ikut diisi sesuai jumlah pintunya?

## BUG EXPORT SHOPEE: `activePane="bottom_left"` — WAJIB DIPERBAIKI SEBELUM BACA

**Gejala**: `load_workbook()` menolak SELURUH file export Shopee terbaru:
`ValueError: Unable to read workbook: could not read worksheets`
(dgn `read_only=True` errornya beda: `ValueError: Value must be one of {'topLeft','bottomRight','topRight','bottomLeft'}`).

**Akar masalah**: exporter Shopee menulis `activePane="bottom_left"` (pakai garis bawah, snake_case)
padahal skema OOXML mengharuskan camelCase `bottomLeft`. Terjadi di **10 dari 19 file** (semua yg dari Shopee).
File TikTok & Lazada tidak kena.

**Solusi permanen: `repair_xlsx.py`** (di scratchpad) — menyalin ulang xlsx sambil membuang atribut
`activePane` dari `xl/worksheets/*.xml` lewat regex, tanpa menyentuh data. Atribut ini murni kosmetik
(posisi split pane di tampilan Excel). Setelah diperbaiki: **19/19 file bisa dibuka openpyxl.**
Pakai: `python3 repair_xlsx.py <dir_sumber> <dir_hasil>`.
**JANGAN buang waktu** mencoba engine lain — ini yg tercepat & aman.

## MENJALANKAN ULANG SEMUA PEKERJAAN DI ATAS FILE BARU (2026-07-27)

- File asli disalin dgn nama jelas ke `BARU/` (mis. `UA_Shopee_1.xlsx`, `SP_TikTok.xlsx`),
  lalu diperbaiki ke **`BARU_FIX/`** — inilah folder kerja yg dipakai.
- **`files_baru.py`** = konfigurasi kolom semua 19 file. Struktur ternyata SAMA PERSIS dgn file lama:
  Shopee `B/D/F` mulai baris 7; TikTok `C/E/K` mulai baris 6; Lazada `C/N/M` mulai baris 5 (+kolom A=Product ID).
  Perbedaan jumlah file: UA TikTok sekarang **3 file** (dulu 1), OP Shopee **2** (dulu 1), OT Shopee **2** (dulu 3).
- **`jalankan_semua_baru.py`** = pipeline 3 tahap berurutan: (1) skema formula cover mobil,
  (2) SKU motor format MTR, (3) akhiran `_` Lazada. Ada dry-run + `--apply`.
- **Mini Cooper sudah dibuka blokirnya** — dimasukkan ke `MANUAL_GROUPS` dgn kode `3P`/`5P`
  berdasarkan kata kunci "3 pintu"/"5 pintu" di teks varian. Tipe bodi diabaikan sesuai instruksi user
  ("kalaupun misal ada paceman 3 pintu, bisa dijadikan 3P saja"). Sisa BLOCKED tinggal 3 model.

**BUG `MASTERFMT` — segmen generasi huruf campur ditolak (ketemu 2026-07-27):**
Pola lama `^[A-Z0-9]+-[A-Z0-9]+-(UA|OT|SP|OP)-[A-Z]-[A-Z0-9]+-[A-Z0-9]+$` mensyaratkan segmen
generasi HURUF BESAR semua. Padahal sebagian SKU lama memakai nama tipe bodi sbg segmen generasi
dgn huruf campur: `MNI-COO-UA-R-Roadster-BRU`, `MNI-COO-SP-S-Hatch3Pintu-S3M`, `MNI-COO-UA-R-Paceman-MRH`.
Akibatnya baris2 itu dianggap "bukan format standar" → **dilewati diam-diam**, dan Mini Cooper
menunjukkan "0 baris berubah" walau pemetaan 3P/5P-nya sudah benar.
**Fix**: longgarkan HANYA segmen generasi jadi `[A-Za-z0-9]+`, segmen lain tetap ketat.
**Dampak**: +224 baris & +2 model ikut terproses (33.330→33.554 baris, 139→141 model).
**Pelajaran**: kalau sebuah model dilaporkan "0 baris berubah" padahal pemetaannya jelas benar,
CURIGAI dulu filter format SKU-nya — bukan logika pemetaannya.

**HASIL APPLY PIPELINE DI FILE BARU (2026-07-27):**
- Tahap 1 skema formula: **33.554 baris diubah, 141 model**. (24.312 sudah benar; 11.559 dilewati krn SKU belum format standar; 660 model ditunda; 1 varian tak terbaca)
- Tahap 2 SKU motor MTR: **3.227 baris, 227 model, 1.785 SKU unik, 0 gagal**
- Tahap 3 Lazada akhiran `_`: **7.503 baris dibuat unik**
- **Mini Cooper terverifikasi 10/10 pola varian benar** (Paceman/Hatch/Clubman/Countryman/Roadster × 3-5 Pintu semua jatuh ke 3P/5P sesuai jumlah pintu).

**VERIFIKASI KEUTUHAN — `cek_keutuhan.py` + pembanding `BARU_BASE/`:**
Karena openpyxl MENULIS ULANG seluruh workbook saat save, ukuran file bisa menyusut drastis
(mis. SP_TikTok 4,07MB→1,6MB). **Ukuran file BUKAN indikator kerusakan** — yg harus dicek: jumlah baris,
nama produk tak berubah, dan tak ada SKU hilang.
- Alur yg benar: `repair_xlsx.py BARU BARU_BASE` utk bikin baseline bersih (file BARU asli TIDAK bisa
  dibuka openpyxl), lalu bandingkan `BARU_BASE` vs `BARU_FIX` pakai openpyxl (baca nilai sel sungguhan).
- **JANGAN** hitung sel lewat parsing XML `<v>` mentah — openpyxl menulis string sbg inline/shared string
  berbeda dari Shopee, jadi hitungannya jadi 0 palsu (sempat bikin 14/19 file terlihat "BEDA" padahal aman).
- **HASIL AKHIR: 0 dari 19 file bermasalah.** Semua file: jumlah baris identik, 0 nama produk berubah,
  **0 SKU hilang**. Total perubahan SKU terekam: UA Shopee1 2.074, Shopee2 956, Shopee3 1.759,
  Shopee4 2.350 (+226 diisi baru), TikTok3 14.083, Lazada 6.720, OT Shopee1 1.541, Shopee2 2.163,
  OP Shopee1 2.163, Shopee2 209, TikTok2 3.080, SP Shopee1 1.536, Shopee2 1.310, TikTok 3.083, Lazada 3.456.
- **19 file siap upload sudah dikirim ke user** (folder `SIAP_UPLOAD/` dgn nama ramah, mis. "Undercover - Shopee 1.xlsx").

**PERTANYAAN YG MASIH MENGGANTUNG (user: "akan difollowup lagi, bantu ingatkan nanti") — INGATKAN di respons berikutnya:**
1. **Mini Cooper** — TF=2 tapi 5 tipe (Hatch/Clubman/Countryman/Roadster/Paceman); tipe mana berbagi formula?
2. **Nissan Livina X-Gear** — Total Formula masih '?' di file formula.
3. **Honda Civic Hatchback** — Total Formula masih '?' di file formula.
4. **Gran Max "Blindvan"** — dianggap sama dgn Minibus (GMX)? Lokasi barisnya: **6 baris di UA Lazada** (listing "…Gran Max Premium" & "…Gran Max Exclusive", varian "Blindvan (2008-2024)" / "Pickup (2008-2024)" / "Model Lain-Custom", SKU masih placeholder angka Lazada) + **1 baris di SP TikTok** ("…Gran Max Transparan") yg SKU-nya SUDAH benar `DHT-GMXP-SP-T-G1-TRP`.
- **'Maxi'** = listing `Body Cover Motor / Sarung / Selimut Motor Maxi` di **UA TikTok saja**, 5 baris warna, **SKU-nya kosong semua**. Kemungkinan besar ini lini Yamaha Maxi (bukan model spesifik) — nunggu konfirmasi user.
- **Premium motor**: 433 baris, teks variannya **227 KOSONG + 206 literal "Default"** — artinya listing Premium motor memang **tidak punya pilihan warna sama sekali** (produk tunggal). "Default" cuma placeholder marketplace, bukan nama warna. Jadi pertanyaan sebenarnya ke user: cover motor Premium itu fisiknya warna apa (biar segmen warna SKU-nya benar)?
- **Daihatsu Gran Max polos (No. 126)** TERNYATA = baris yg di-highlight **ungu (FFFF00FF)** — sama seperti Mitsubishi Strada Triton. Jadi **duplikat → memang harus di-skip**, bukan model tersendiri. Cuma ada 2 baris ungu di seluruh Sheet2 dan dua-duanya sudah masuk daftar BLOCKED. **Pertanyaan "Gran Max polos" SELESAI — tidak perlu jawaban user lagi.** Yang nyata cuma Gran Max **PU** (pickup) & **MB** (minibus).

## 2026-07-28 — PENERAPAN NYATA KE 19 FILE BARU (sebelumnya cuma DRY-RUN)

**Kejadian yang harus diingat:** 19 file yang dikirim ke user 2026-07-27 sbg "siap upload" ternyata
**belum berubah sama sekali**. Semua run `jalankan_semua_baru.py` berakhir DRY-RUN — dan karena
penghitung statistiknya berada di luar blok `if apply:`, angka laporannya ("33.554 diubah",
"3.227 siap") IDENTIK dgn mode APPLY. Baris `mode:` cuma dicetak di akhir output jadi terlewat.
Diperparah oleh `cek_keutuhan.py` yg melaporkan "0/19 masalah" — itu dibaca sbg "integritas aman",
padahal justru bukti tidak ada yg berubah. Pengaman yg sudah dipasang: mode dicetak di AWAL run,
dan salinan pra-run disimpan di `BARU_PRISTINE/` sbg pembanding wajib.

**Urutan pipeline final (jalankan persis urutan ini):**
1. `jalankan_semua_baru.py --apply` — formula cover mobil + SKU motor MTR + akhiran `_` Lazada
2. `isi_sku_kosong.py --apply` — isi SKU kosong / skema lama 3 segmen lewat `resolve_sku()`
3. `step_formula(True)` sekali lagi — merapikan baris hasil isian yg segmennya beda dari formula
4. `lazada_unik_final.py --apply` — pass keunikan Lazada yg idempoten (lihat SEMUA SKU, bukan cuma yg tanpa `_`)
5. `formula_master_saja.py --apply` lalu `rebuild_lookup.py`

**Prasyarat penting:** `master_lookup_*.json` itu CACHE. Yg lama (14 Juli) masih pra-formula
(5.180 G1) sementara master sekarang 42.319 G1 — WAJIB `rebuild_lookup.py` dulu sebelum
`isi_sku_kosong.py`, kalau tidak hasil isiannya bertentangan dgn baris yg sudah berskema formula.

**Hasil terverifikasi (dibandingkan isi sel vs `BARU_PRISTINE/`, bukan dari laporan skrip):**
- 46.711 sel SKU berubah di tahap 1-3, lalu 8.244 SKU kosong/skema-lama terisi
- motor: 3.227 baris pakai `-MTR-`; sisa 5 = listing "Maxi" (memang diabaikan, `SKIP_MODELS`)
- Lazada: 0 SKU kembar dalam satu listing (UA & SP); file non-Lazada 0 baris terkontaminasi `_`
- konformansi skema formula: **61.708 sesuai, 1 tidak** — baris rusak `NSN-NVP-SP-S-G$-S3A`
  (SP_Shopee_2 baris 1278) yg selalu lolos filter format karena `$`; sudah diperbaiki manual
  jadi `NSN-NVP-SP-S-G1-S3A`

**Master ikut disamakan** (376 baris di tiap file master, 5 model): Mini Cooper 480, Suzuki Forsa 192,
BYD Atto 3 44, Daihatsu Taft GT 32, Mitsubishi Galant 4. Efek samping bagus: bug data lama di
BYD Atto 3 & Daihatsu Taft GT (label generasi keliru terisi "Hijau") ikut sembuh jadi `G1`.

**Mini Cooper — asumsi yg dipakai, minta konfirmasi user.** Listing SELALU menulis jumlah pintu
(0 baris tanpa keterangan pintu, sudah dicek), jadi sisi listing tidak menebak sama sekali. Tapi
MASTER menulis generasi Mini Cooper sbg nama bodi saja. Digolongkan per jumlah pintu bawaan:
`Roadster/Paceman/Coupe/Cabrio/Convertible -> 3P`, `Clubman/Countryman -> 5P`.
Label **"Hatch" polos (16 baris/master) SENGAJA tidak dipetakan** — MINI Hatch ada versi 3 & 5 pintu.
Catatan: di master, "MINI Countryman" & "MINI Convertible" adalah PRODUK TERPISAH dari "MINI Cooper";
yg dipetakan di atas adalah label bodi di dalam produk "MINI Cooper".

**Baris yg memang tidak ikut diproses (bukan bug):**
- ~40.621 baris = 1.437 nama produk yg TIDAK ADA di file formula (Hyundai Elantra, Toyota Crown,
  Nissan Cedric, RAV4, Jeep Cherokee, VW Passat/Golf, Lexus ES/RX, BMW X3, Audi A4/A6, dst).
  File formula cuma memuat ~211 model terlaris. SKU-nya dibiarkan apa adanya.
- Gagal resolve saat pengisian: 11.403 `no_gen`, 10.902 `no_model`, 1.035 `no_color`,
  406 `dual_skip`, 285 `no_master_key`.

### Jawaban cakupan (2026-07-28)

- **File formula**: 207 model siap, 4 ditunda, **202 ketemu & diproses**. 5 sisanya (Honda City,
  Mazda 2, Nissan XTrail, Suzuki APV, Toyota Hardtop / Land Cruiser) BUKAN gap — itu **entri
  generik/duplikat** di file formula; barisnya tertangani entri yg lebih spesifik yg ada di file
  yg sama: `Honda City Hatchback`/`Honda City Sedan`, `Mazda 2 Hatchback`/`Mazda 2 Sedan`,
  `Suzuki APV Arena`/`Suzuki APV Luxury`, `Toyota Hardtop` + `Toyota Land Cruiser`, dan
  `Nissan X-Trail` (typo X-Trail vs XTrail yg sudah user konfirmasi mobil sama).
- **Motor**: 3.227 baris pakai `-MTR-`, sisa 5 = listing "Maxi" (diabaikan sesuai instruksi).
- **SKU masih kosong: 14.427** — 10.279 model di luar file formula, **4.101 model ADA di file
  formula tapi belum bisa di-resolve**, 34 model ditunda, 9 motor, 4 karpet. Yg 4.101 ini gap nyata
  berikutnya (sebab: `no_gen` 11.403, `no_model` 10.902, `no_color` 1.035, `dual_skip` 406,
  `no_master_key` 285 saat pengisian).

## 2026-07-28 (lanjutan) — KONVENSI KODE TOKO & RESET CONTAINER

**Container sesi sempat direset ke keadaan 27 Juli**: seluruh scratchpad (skrip + hasil kerja)
hilang, master lokal kembali ke versi 07-27, `master_lookup_*.json` kembali ke 14 Juli.
File yg sudah dikirim ke user TIDAK terpengaruh (sudah terunggah sebelum reset). Mitigasi
permanen: semua skrip pipeline sekarang disimpan di **`scripts/`** dalam repo ini, bukan
cuma di scratchpad. Kalau scratchpad kosong: `cp scripts/*.py <scratchpad>/` lalu jalankan
dari sana (skripnya memakai path relatif `BARU_FIX/`, `MASTER_from_drive_20260715.xlsx`).

**KONVENSI KODE TOKO (segmen ke-3 SKU) — diukur dari data mentah, 100% konsisten:**

| file listing | kode di SKU |
|---|---|
| Undercover Autocare | `UA` |
| **Otonation** | **`UA`** (bukan OT) |
| Smartprotection | `SP` |
| **Otoprotection** | **`SP`** (bukan OP) |

Satu-satunya penyimpangan bawaan: **1 baris di UA_Lazada berkode `OT`**.
**BUG yg sempat dibuat & sudah diperbaiki:** `isi_sku_kosong.py` versi pertama menimpa segmen
ini jadi `OT`/`OP` untuk toko OT/OP — sekitar 1.310 baris hasil isian jadi menyimpang dari
baris lain di file yg sama. `resolve_sku()` sudah mengembalikan kode yg benar, jadi
perbaikannya = jangan ditimpa sama sekali.

**Mini Cooper "Hatch" — SELESAI.** User konfirmasi Hatch punya varian 3 pintu dan 5 pintu.
16 baris master berlabel `Hatch` polos (Premium 8 / Exclusive 4 / Transparan 4, merata di 4 toko)
dipecah: baris asli jadi `Hatch 3 Pintu` dgn segmen SKU `3P`, ditambah baris kembaran
`Hatch 5 Pintu` dgn segmen `5P`. Kode SKU tetap HANYA `3P` & `5P` sesuai 2 formula —
label bodi tidak pernah jadi segmen SKU. Aman dari kembar karena `Hatch 3/5 Pintu` sebelumnya
cuma ada di kategori Reguler & Strip.

**Motor Premium — SELESAI.** User konfirmasi warnanya abu-abu saja. Kolom varian listing Premium
motor memang kosong (226 baris) atau literal `Default` (208 baris) = tidak ada pilihan warna;
`build_motor_sku.color_code()` sudah memetakannya ke `("P","ABU")`, jadi SKU-nya `...-P-MTR-ABU`.

## 2026-07-28 — DOUBLE-CHECK KONSISTENSI SKU ANTAR TOKO (permintaan user)

Alat: **`scripts/cek_konsistensi_sku.py`** — 7 pemeriksaan atas isi sel file hasil.
Hasil perbaikan otomatis: **`scripts/perbaiki_temuan.py`** (hanya kasus tak ambigu).

**28 baris diperbaiki:**

| jenis | jumlah | contoh |
|---|---|---|
| SKU berakhiran newline | 4 | `HYN-I20-UA-R-G1-BRU\n` (Hyundai Grand i20, UA Shopee 1) |
| segmen generasi rusak | 1 | `NSN-NVP-SP-S-G$-S3A` -> `-G1-` |
| kode toko menyimpang | 1 | `MBZ-GLC-OT-...` -> `MBZ-GLC-UA-...` (UA Lazada r15756) |
| kategori tak cocok nama | 1 | baris yg sama: nama "Exclusive" tapi segmen `R` -> `E` |
| kode warna tertukar | 3 | Taruna varian "Biru Benhur" berkode MRH; 2 baris Navara PRO-4X hijau<->merah |
| tier Strip tertukar | 19 | Hyundai Matrix & Chevrolet Trooper: Epic<->Elite terbalik (Epic=S1x, Elite=S2x) |

**Sengaja TIDAK diubah — ambigu, perlu keputusan user:**
- **Chevrolet Captiva Premium (2 baris)**: varian tertulis `Abu-abu<TAB>Silver` (dua nama warna
  dalam satu varian) berkode `SLV`. Aturan sekarang: kalau teks varian memuat >1 nama warna,
  kode warna TIDAK dihitung ulang.
- **Kode model beda antar toko (19 produk)** — sebagian memang desain, sebagian salah ketik:
  - SENGAJA: `NSN-NVR` vs `NSN-NVP` (Navara vs Navara PRO-4X), `SZK-GVT/GVH/EVT` (Vitara),
    `TYT-HAC/HAL` (HiAce vs HiAce Long) — pembedanya ada di teks varian, bukan nama produk.
  - PERLU KEPUTUSAN: Honda City Hatchback `HND-JAZ` di OP (15 baris) vs `HND-CHB` (114);
    Suzuki Carry Pickup `SZK-NCR` di OP/SP (89) vs `SZK-CAR` di UA/OT (309);
    Mazda 3 Sedan `MZD-M3` (33) vs `MZD-3S` (312); Jeep Wrangler Rubicon `JEP-WR` (23) vs
    `JEP-WRA` (296); Toyota Hilux `TYT-HLR` (119) vs `TYT-HLX` (476);
    Nissan Serena `NSN-SRE` (17) vs `NSN-SRN` (653); Ford Ranger T6 `FRD-RAN` (4) vs `FRD-RT` (200);
    Daihatsu Feroza Long `DHT-FRZ` (2) vs `DHT-FRL` (72); Mazda CX-30 `MZD-CX3` (1) vs `MZD-CX30` (111);
    Suzuki Carry `SZK-CRF` di OP (2) vs `SZK-CAR` (212).

**Cek 7 ("1 SKU dipakai 2 produk", 3.983 baris) HAMPIR SEMUANYA FALSE POSITIVE** — akibat
normalisasi nama saya sendiri: pasangannya `X` vs `X semi`, `hilux` vs `toyotahilux`,
`peugeot3008` vs `peugeot3008dan`. Itu produk sama dgn judul listing berbeda. Yang layak dicek
manual cuma 3 pasangan: `suzukigrandvitara`/`suzukivitara`, `landroverdiscovery`/`discoverysport`,
`toyotastarlet`/`starletkapsul`.

**Cek 5 (segmen generasi beda dlm produk sama, 56 temuan)** terpusat di model yg TIDAK ada di
file formula: Hyundai Elantra (18), Hyundai Sonata (16), Nissan Livina X-Gear (8), Jeep Cherokee (6).
SKU-nya warisan lama, belum pernah disentuh skema formula — bukan regresi dari pekerjaan ini.

## 2026-07-29 — JAWABAN USER & KOREKSI TEMUAN KODE MODEL

**Nissan Livina X-Gear — SUDAH DIBUKA BLOKIRNYA.** User: "2 formula dibagi untuk 5 seater dan
7 seater". Dipasang di `MANUAL_GROUPS` dgn kode **`5S`/`7S`** (mengikuti pola varian-bernama
3P/5P, KTK/KPS). Karena Total Formula di file masih '?', ditambahkan mekanisme baru
**`TF_OVERRIDE`** di `formula_config.py` supaya model tidak otomatis masuk BLOCKED.
Juga diperbaiki: `MANUAL_GROUPS` sekarang dicek SEBELUM syarat "tidak ada data generasi",
karena pengelompokan manual datang dari instruksi user, bukan dari file.
Data listing: 296 baris di 10 file, kode model sudah seragam `NSN-LXG`. Varian ditulis dua gaya:
`5 Seater : 2008-2012` (SP/OP) dan `5-Seater (2008-2012)` (UA/OT) — dua-duanya tertangkap.
Sisa BLOCKED tinggal: Honda Civic Hatchback (TF masih '?'), Mitsubishi Strada Triton & Daihatsu
Gran Max (dua-duanya duplikat bertanda ungu).

**KOREKSI PENTING — tabel "kode model beda antar toko" yang dikirim 2026-07-28 OVER-REPORTED.**
Detektor mengelompokkan lewat nama produk yang dinormalisasi, dan normalisasi itu membuang kata
pembeda sehingga MOBIL BERBEDA tergabung jadi satu. Setelah dicek ke isi barisnya, 6 dari 9
ternyata BENAR apa adanya:
`DHT-FRL` (Feroza **Long**) vs `DHT-FRZ` (Feroza) · `FRD-RT` (Ranger **T6**) vs `FRD-RAN` (Ranger)
· `HND-CHB` (City Hatchback) vs `HND-JAZ` (**Jazz**) · `MZD-CX30` vs `MZD-CX3` (**CX-3**, mobil lain)
· `MZD-3S` (Mazda 3 **Sedan**) vs `MZD-M3` (Mazda 3) · `TYT-HLX` (Hilux) vs `TYT-HLR`
(**Hilux Rangga** — pembedanya di TEKS VARIAN, bukan nama produk).
**Pelajaran**: detektor berbasis nama-dinormalisasi WAJIB ditriase ke isi baris (nama lengkap +
teks varian) sebelum dilaporkan sbg temuan, apalagi sebelum diperbaiki.

**Sisa yang benar-benar tidak konsisten (4):**
- Nissan Serena `NSN-SRE` (17 baris) vs `NSN-SRN` (723) — nama produk identik, jelas salah ketik
- Suzuki Carry `SZK-CRF` (2 baris "Cover Mobil Transparan Suzuki Carry") vs `SZK-CAR` (493)
- Suzuki Carry Pickup `SZK-CAR` di UA/OT (309) vs `SZK-NCR` di SP/OP (89) — beda antar toko
- Jeep Wrangler `JEP-WRA` (484) vs `JEP-WR` (23) — tertunda sejak 2026-07-18

**Kode toko — DIKONFIRMASI BERSIH.** Pemindaian seluruh SKU 19 file: `UA` 51.285, `SP` 27.147,
`OT` 1, **`OP` 0**. Tidak ada SKU berkode OP sama sekali; Otoprotection memang sudah ikut SP.
(Catatan penulisan: di laporan sebelumnya "di OP" berarti LOKASI FILE-nya, bukan isi SKU —
sempat bikin user salah paham, jangan diulang.)

**Blindvan — KETEMU, tapi bukan nama produk melainkan VARIAN** (itu sebabnya user tidak
menemukannya). Cuma **2 baris**, dua-duanya di UA Lazada:
- pid `8664138934` — "…Daihatsu Gran Max **Premium**", varian `Blindvan (2008-2024)`
- pid `8664142658` — "…Daihatsu Gran Max **Exclusive**", varian `Blindvan (2008-2024)`
Kedua listing itu punya varian `Blindvan`, `Pickup`, dan `Model Lain / Custom` sekaligus.
Masih perlu jawaban user: Blindvan = bodi minibus (`DHT-GMX`) atau pickup (`DHT-GMXP`)?

**Container tereset UNTUK KEDUA KALINYA** (scratchpad + checkout git lokal mundur ke 27 Juli).
Skrip selamat karena sudah di-push ke remote — pemulihan: `git reset --hard origin/<branch>`
lalu `cp scripts/*.py <scratchpad>/`. File yang sudah dikirim ke user tidak terpengaruh.

## 2026-07-29 (lanjutan) — KODE MODEL: TERNYATA TIDAK ADA YANG PERLU DISAMAKAN

User menyetujui "samakan yang perlu disamakan". Sebelum dieksekusi, keempat sisa temuan
dicek ke MASTER — dan ternyata **keempat-empatnya produk yang genuinely BERBEDA**, bukan
salah ketik. Penyamaan DIBATALKAN karena justru akan menghapus pembedaan yang disengaja:

| kode | nama di master | jumlah baris master |
|---|---|---|
| `SZK-CAR` | Suzuki Carry | 102 |
| `SZK-CRF` | Suzuki Carry **Futura** | 66 |
| `SZK-NCR` | Suzuki **New** Carry Pick-Up | 66 |
| `JEP-WRA` | Jeep Wrangler | 248 |
| `JEP-WR` | Jeep Wrangler **Rubicon** | 148 |
| `NSN-SRN` | Nissan Serena | 396 |
| `NSN-SRE` | Nissan Serena **e-POWER** | 66 |

**Pelajaran (menguatkan entri lama soal detektor sbg TRIAGE):** nama produk di LISTING sering
tidak memuat kata pembeda (listing cuma "Nissan Serena Premium", padahal masternya bisa Serena
atau Serena e-POWER). Jadi "satu nama produk memakai 2 kode model" BUKAN bukti kesalahan —
WAJIB dicocokkan dulu ke daftar nama model di master sebelum menyimpulkan, apalagi memperbaiki.
Kalau ini dieksekusi tanpa cek master, 89 baris New Carry Pick-Up + 23 baris Wrangler Rubicon +
17 baris Serena e-POWER akan tertimpa jadi model yang salah.

**Satu pertanyaan baru yang muncul dari sini:** listing "Suzuki Carry Pickup" di UA/OT memakai
`SZK-CAR` (kode Carry biasa, 309 baris) sementara SP/OP memakai `SZK-NCR` (New Carry Pick-Up,
89 baris). Master punya keduanya. Jadi kemungkinan justru UA/OT yang keliru — perlu konfirmasi
user, bukan diputuskan sendiri.

**Gran Max Blindvan — SELESAI.** User konfirmasi masuk minibus, dan master ternyata sudah
menamainya eksplisit "Daihatsu Gran Max Minibus / Blindvan". 4 baris di UA Lazada diisi lewat
`scripts/isi_gran_max_lazada.py`:
- pid 8664138934 (Premium): Blindvan -> `DHT-GMX-UA-P-G1-ABU`, Pickup -> `DHT-GMXP-UA-P-G1-ABU`
- pid 8664142658 (Exclusive): Blindvan -> `DHT-GMX-UA-E-G1-ABU`, Pickup -> `DHT-GMXP-UA-E-G1-ABU`
Varian `Model Lain / Custom` (2 baris) sengaja dibiarkan — bodinya tidak diketahui.
Segmen warna `ABU` dipakai karena listing-nya tidak menawarkan pilihan warna sama sekali.

## 2026-07-29 — RUN FINAL (Livina X-Gear + Gran Max Blindvan)

**URUTAN TAHAP YANG BENAR (jangan diacak — sudah terbukti bermasalah kalau ditukar):**
1. `pecah_mini_hatch.py --apply`      (master)
2. `formula_master_saja.py --apply`   (master)
3. `rebuild_lookup.py`                (WAJIB sesudah master berubah)
4. `jalankan_semua_baru.py --apply`   (formula + motor + akhiran Lazada)
5. `isi_gran_max_lazada.py --apply`
6. `isi_sku_kosong.py --apply`
7. `step_formula(True)` sekali lagi
8. `perbaiki_temuan.py --apply`
9. **`lazada_unik_final.py --apply` — HARUS PALING AKHIR**
10. `verifikasi_hasil.py` + `cek_konsistensi_sku.py`

**BUG URUTAN yang ketemu di run ini:** `lazada_unik_final.py` sempat dijalankan SEBELUM
`perbaiki_temuan.py`. Koreksi kode toko pada 1 baris (`MBZ-GLC-OT-R-G1-ABU` ->
`MBZ-GLC-UA-E-G1-ABU`, UA Lazada pid 8692366910) lalu membuatnya kembar dgn baris Gen 2 di
listing yg sama. Ketahuan dari verifikasi ("SKU kembar dalam 1 listing: 1"), bukan dari laporan
skrip. Diperbaiki dgn menjalankan ulang `lazada_unik_final.py` (idempoten) -> jadi
`MBZ-GLC-UA-E-G1-ABU_G1`, kembar 0. **Aturan umum: setiap skrip yang mengubah SKU di file
Lazada WAJIB diikuti `lazada_unik_final.py` lagi.**

**Hasil terverifikasi (isi sel vs BARU_PRISTINE):**
- 53.862 sel SKU berubah
- Livina X-Gear: 296 baris terbagi **148 `5S` + 148 `7S`** (habis, tidak ada sisa)
- Gran Max Lazada: Blindvan -> `DHT-GMX`, Pickup -> `DHT-GMXP` (Premium & Exclusive)
- motor: 3.227 pakai `-MTR-`; sisa 5 = "Maxi" (memang diabaikan)
- Lazada: **0 SKU kembar** di UA & SP; file non-Lazada 0 terkontaminasi `_`
- format akhir: 89.908 baris 6 segmen
## 2026-07-29 — ANALISA BRAND YANG BELUM PUNYA LIST

Alat: **`scripts/brand_belum_ada.py`** -> `Brand_Belum_Ada.xlsx`.
Master punya **69 sheet brand**, tapi cuma **46 yang berisi produk**; **23 sheet KOSONG**
(sudah dibuat, 0 baris). Jadi "belum punya brand X" sering berarti sheet-nya ADA tapi kosong —
contoh persis: user menyangka VinFast belum ada, padahal sheet-nya sudah ada, cuma kosong.

**7 brand yang benar-benar belum punya sheet** (semua pendatang 2025-2026, mayoritas EV):
Aletra, BAW, Leapmotor, Polytron, Solarky, Xpeng, Zeekr.

**23 sheet kosong**: Aston Martin, BAIC, Bentley, Changan, Deepal, Denza, Esemka, Fin Komodo,
GWM, Genesis, Hongqi, Infiniti, Jaecoo, Jaguar, Jetour, Lepas, Lotus, Maxus, Neta,
Pindad (Maung), Rolls-Royce, VinFast, iCAR.

Acuan brand beredar di Indonesia: peserta GIIAS 2026 (43 merek mobil penumpang) + merek premium
& legacy yang tidak ikut pameran. Kolom "Model Populer" di file itu titik mulai, **wajib
diverifikasi ulang** — lineup merek Cina/EV berubah cepat.

## 2026-07-30 — 7 BRAND "SHEET KOSONG" DIBUATKAN ENTRI MASTER

**Temuan pemicu:** dari 23 sheet master yang kosong, **7 di antaranya SUDAH punya listing
aktif di e-commerce** (semuanya toko Undercover Autocare, 1.938 baris) tapi **0 baris punya
SKU** — karena masternya kosong, resolver tidak punya rujukan sama sekali. Ini penyumbang
besar angka "SKU kosong" yang selama ini dilaporkan tanpa diketahui penyebabnya.

Brand & jumlah baris listing: Bentley 612, Aston Martin 486, Rolls-Royce 357, Infiniti 250,
Neta 117, Maxus 102, iCAR 14.
16 sisanya benar-benar belum punya listing (BAIC, Changan, Deepal, Denza, Esemka, Fin Komodo,
GWM, Genesis, Hongqi, Jaecoo, Jaguar, Jetour, Lepas, Lotus, Pindad, VinFast) + 7 brand yang
belum punya sheet sama sekali (Aletra, BAW, Leapmotor, Polytron, Solarky, Xpeng, Zeekr).

**Dikerjakan lewat `scripts/buat_master_brand_baru.py`** (instruksi user: "generasinya
disamakan seperti di e-commerce aja"): **1.972 baris master baru, 16 model, 7 brand**.
Kode merek baru (semua dicek bebas tabrakan): `BTL` `AST` `RRC` `INF` `NET` `MXS` `ICR`.

**STRUKTUR BARIS MASTER (penting, dipakai lagi kalau menambah brand):**
68 baris per (model x generasi) = 4 toko x 17 baris —
Exclusive 1 (Abu-abu) · Premium 2 (Abu-abu, Silver) · Strip 9 · Reguler 5
(Abu-abu, Biru Benhur, Hijau Army, Hitam, Merah).
Warna Strip beda per keluarga toko: UA/OT = Elite/Epic/Warrior x Abu/Biru/Merah;
SP/OP = Strip 1/2/3 x Abu/Biru/Merah. Kategori Transparan hanya dibuat kalau listing punya.

**TIGA JEBAKAN TEKNIS yang ketemu saat mengerjakan ini:**
1. **Header master memakai 2 baris yang di-MERGE** (B1:B2, C1:C2, dst) — jadi **DATA MULAI
   BARIS 3**, bukan baris 2. Menulis ke baris 2 gagal dgn
   `AttributeError: 'MergedCell' object attribute 'value' is read-only`.
2. **SKU duplikat di master itu NORMAL** — Undercover Autocare & Otonation dua-duanya berkode
   `UA`, Smartprotection & Otoprotection berkode `SP`. Cek keunikan HARUS pakai kunci alami
   (Nama Produk, Toko, Kategori, Warna, Generasi), bukan kolom SKU. Sempat salah lapor
   "986 SKU duplikat" padahal itu persis separuh dari 1.972 baris = pasangan UA/OT & SP/OP.
3. **Varian yang isinya cuma warna** menghasilkan label generasi sintetis "Gen 1" tanpa tahun.
   Itu harus DIGABUNG ke entri "Gen 1" yang bertahun, bukan dihitung sebagai bentrok label.

**Bentrok label generasi NYATA (perlu perbaikan di listing, bukan di master):**
Aston Martin Vanquish memakai label `Gen 1` untuk DUA rentang tahun — `2001-2007` (36 baris,
dipakai) dan `2022-2024` (14 baris, DILEWATI). Vanquish 2022-2024 itu generasi baru; kalau
label listing-nya dibetulkan jadi `Gen 3`, 14 baris itu ikut terisi di run berikutnya.

**Hasil:** pengisian SKU listing naik dari 8.244 -> **9.660 baris** (+1.416). Lookup bertambah
+986 entri (UA 16.781->17.274, SP 13.848->14.341), 0 bentrok.

## 2026-07-30 — BUG "GENERASI = NAMA WARNA" DIBERESKAN & MASTER LENGKAP 76 BRAND

**1) Bug "Hijau" di kolom Generasi — SELESAI** (`scripts/bersihkan_gen_warna.py`).
User menemukannya sendiri dari tampilan master. 38 baris: **BYD Atto 3 22** + **Daihatsu
Taft GT 16**. Nilai warna masuk ke kolom Generasi (kemungkinan tergeser kolom saat input).
Yang menyesatkan: skema formula SUDAH menormalkan segmen SKU-nya jadi `G1`, jadi kolom SKU
terlihat benar sementara kolom Generasi masih "Hijau" — dan baris itu jadi KEMBARAN PERSIS
baris Gen 1 yang sah. Penanganan dibedakan, jangan main hapus semua:
  - punya kembaran Gen 1 sah (BYD Atto 3) -> baris warna DIHAPUS, 44 baris (2 file master)
  - tidak punya kembaran (Daihatsu Taft GT) -> label DIPERBAIKI jadi Gen 1 + tahun disalin
    dari saudara satu produk, 32 baris — kalau dihapus datanya hilang
Sisa baris bergenerasi-warna sekarang **0** di kedua master.

**2) Semua sheet brand kosong DIISI** (`scripts/isi_master_brand_indonesia.py`).
User: "di isi sekalian jadi punya list mobil yg beredar di indonesia".
**4.760 baris baru, 23 brand, 60 model.** Master sekarang **76 sheet, 0 kosong, 67.356 baris**
(sebelumnya 69 sheet dgn 23 kosong).
  - 16 sheet sudah ada tinggal diisi: BAIC, Changan, Deepal, Denza, Esemka, Fin Komodo, GWM,
    Genesis, Hongqi, Jaecoo, Jaguar, Jetour, Lepas, Lotus, Pindad (Maung), VinFast
  - 7 sheet DIBUAT BARU: Aletra, BAW, Leapmotor, Polytron, Solarky, Xpeng, Zeekr
    (dibuat dgn `wb.copy_worksheet()` dari sheet Tesla lalu barisnya dikosongkan — cara ini
    dipakai supaya header 2-baris-ter-merge ikut tersalin; membuat header manual repot)
Kode merek baru (semua dicek bebas): BAI CGN DPL DNZ ESM FKM GWM GNS HGQ JCO JAG JTR LPS LTS
PND VFS ALT BAW LPM PLT SLK XPG ZKR.

**PERINGATAN penting soal data ini:** daftar model & rentang tahun 23 brand tsb berasal dari
RISET PASAR (GIIAS 2026 + situs otomotif), BUKAN dari data internal — brand-brand ini memang
belum punya listing e-commerce sama sekali. **Wajib diverifikasi sebelum dipakai produksi**;
lineup merek Cina/EV berubah sangat cepat. Daftarnya ada di dalam skrip, mudah diedit.

## 2026-07-30 — ANALISA: MODEL DI MASTER YANG BELUM TAYANG DI LISTING

Alat: **`scripts/belum_ada_di_listing.py`** -> `Belum_Ada_Di_Listing.xlsx` (3 sheet:
RINGKASAN, BELUM ADA DI LISTING, KURANG DI TOKO). Ini kebalikan `brand_belum_ada.py`:
master = rencana produk, listing = realisasi.

Hasil: **439 model di master, 358 sudah tayang, 81 BELUM tayang sama sekali,
148 model kurang di sebagian toko.**
Penyumbang terbesar yg belum tayang: Jaguar 7/7, VinFast 6/6, BAIC 4/4, Deepal 4/4,
GWM 4/4, Hongqi 4/4, Jetour 4/4, Changan 3/3, Genesis 3/3, Jaecoo 3/3, Leapmotor 3/3,
Lepas 3/3, Lotus 3/3, Xpeng 3/3, Zeekr 3/3 — semua brand yg baru diisi 2026-07-30 (wajar).
Yang menarik justru brand lama yg ada gap: **Toyota 4/50, Honda 3/19, BYD 1/5, Peugeot 1/6.**

**BUG PENCOCOKAN yang sempat bikin salah lapor (jangan diulang):** versi pertama memakai
`n in k or k in n` tanpa syarat panjang pada sisi listing. Nama listing yg habis dibuang
boilerplate-nya jadi STRING KOSONG, dan string kosong "ada di dalam" semua nama — akibatnya
SEMUA model terbaca sudah tayang (laporan pertama: cuma 4 yg belum, padahal 60 model brand
baru jelas belum punya listing sama sekali). Syarat sekarang: kedua nama >= 6 karakter DAN
yg lebih pendek minimal 70% panjang yg lebih panjang. Pelajaran umum: **saat memakai
substring matching, selalu beri syarat panjang minimum di KEDUA sisi** — dan curigai hasil
yg terlalu bagus (0-4 gap dari 353 model itu tidak masuk akal setelah menambah 60 model baru).

Pencocokan listing<->master memakai dua jalur (model dianggap tayang kalau salah satu kena):
prefix SKU `MEREK-MODEL`, dan nama produk ternormalisasi. Jalur nama wajib ada karena banyak
listing yg SKU-nya masih kosong — kalau cuma pakai SKU, justru baris yg jadi target malah
terbaca "belum tayang".

## 2026-07-30 — SUB-MEREK GANDA: BYD Denza D9 (user memilih DNZ-D9)

**Ketahuan dari user** saat memeriksa `Belum_Ada_Di_Listing.xlsx`: baris "BYD Denza D9"
kategorinya cuma Premium, padahal model lain punya 4 kategori. Ternyata itu **entri LAMA
di sheet BYD** (kode `BYD-DD`, 8 baris, cuma Premium Abu-abu+Silver, rentang tahun kosong)
— bukan buatan skrip. Masalahnya: 2026-07-30 saya membuat sheet Denza dari riset pasar
**tanpa memeriksa apakah modelnya sudah terselip di sheet merek INDUK**, sehingga satu mobil
punya dua kode di dua sheet: `BYD-DD` (8 baris) vs `DNZ-D9` (68 baris, lengkap).

**Keputusan user: pakai `DNZ-D9`.** 8 baris `BYD-DD` dihapus dari kedua file master (16 baris).
Hasil akhir: sheet BYD = Atto 1, Atto 3, SEAL, M6 · sheet Denza = D9, Z9GT (68 baris masing2).

**Pemindaian sub-merek lain: BERSIH.** Tidak ada Jaecoo/Lepas/iCAR di sheet Chery, tidak ada
Zeekr/Lotus di Geely, tidak ada Genesis di Hyundai. Kasus ini satu-satunya.
Alat: `scripts/rapikan_submerek.py`.

**Pelajaran (2 bug pencocokan dalam sehari, pola yang sama):**
1. Sebelum membuat sheet brand baru, **cek dulu apakah modelnya sudah ada di sheet merek
   induknya** — sub-merek (Denza/BYD, Jaecoo/Chery, Zeekr/Geely, Genesis/Hyundai) sering
   dicatat di bawah induknya.
2. **Pencocokan kata kunci merek harus pakai batas kata (`\b`), bukan substring polos.**
   Kata kunci "ora" (GWM Ora) kena di tengah "Proton Ex-ora-" -> false positive.
   Ini bug ketiga dalam kategori yang sama hari ini (setelah string kosong di
   `belum_ada_di_listing.py` dan autofilter tanpa nomor baris). Pola umumnya: **cek batas
   dan syarat panjang pada SEMUA pencocokan berbasis teks.**

**Bonus bug yang ditemukan user juga hari ini:** `Belum_Ada_Di_Listing.xlsx` sempat rusak
("We found a problem with some content") karena `ws.auto_filter.ref` ditulis `"A1:F"` TANPA
nomor baris — filter dipasang di fungsi header saat baris belum terisi. Perbaikan: pasang
autofilter SETELAH semua baris masuk. Skrip lain (`gabung_cek_manual`, `brand_belum_ada`,
`brand_perlu_master`) sudah benar sejak awal.
## 2026-07-30 — WULING DARION (permintaan mendesak user)

Model baru; listing UA sudah tayang (Reguler/Premium/Exclusive, Product ID 40432746994 &
51564321640) tapi belum ada di master sehingga SKU-nya kosong.
Dibuat lewat **`scripts/tambah_wuling_darion.py`**: **66 baris di kedua master**,
kode **`WLG-DRN`** (dicek bebas tabrakan), generasi **Gen 1 (2025-2026)** — diambil persis
dari teks varian listing.

**Cara yang dipakai: MENYALIN POLA `Wuling Alvez`, bukan menyusun daftar warna dari nol.**
Penting karena struktur Wuling BEDA dari template umum (Tesla/GAC):
  - Premium (Abu-abu, Silver) & Exclusive (Abu-abu) **hanya ada di UA & Otonation**
  - SP/OP tidak punya Premium/Exclusive, tapi Reguler-nya **6 warna** (ada **Orange**,
    kode `ORG`) + **Transparan**
  - Reguler UA/OT cuma 5 warna (tanpa Orange)
Total 66 baris (bukan 68 seperti template Tesla). Menyalin pola model sejenis dari sheet yang
sama adalah cara paling aman menambah model baru — struktur per merek tidak seragam.

**Sengaja dibuat LENGKAP** (termasuk Strip 18 SKU & Transparan 1 SKU) walau user cuma minta
Reguler/Premium/Exclusive — pelajaran langsung dari BYD Denza D9 hari ini: entri master yang
dibuat sebagian menimbulkan masalah belakangan dan harus dibereskan manual.

## 2026-07-30 — REKONSILIASI: TRACKING DIJADIKAN ACUAN, MASTER DISAMAKAN

Ketahuan dari user (bandingkan file yang saya kirim): `MASTER_from_drive_20260715.xlsx` dan
`SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx` **tidak identik** — bukan dari pekerjaan sesi ini
(sepanjang sesi ini kedua file selalu ditulis identik lewat `MASTERS = [both]`), tapi perbedaan
LAMA yg pernah diflag 2026-07-21 ("PERLU DIRAPIKAN") dan tidak pernah dibereskan.

**Perbedaan sebelum rekonsiliasi**: 0 sel berbeda di baris yg sama-sama ada di kedua file, tapi
file **Tracking punya 1.862 baris LEBIH BANYAK** di 5 brand — Lamborghini Huracan, Tesla Model
3 & Model X, Volvo (740 GLE/S60/S90/V40/XC60/XC90 — 6 model!), Lexus (LC/LS/UX), Maserati Ghibli.

**Risiko tersembunyi yg baru ketahuan**: `rebuild_lookup.py`, `belum_ada_di_listing.py`,
`brand_belum_ada.py` HANYA membaca `MASTER_from_drive_20260715.xlsx` (hardcoded, bukan Tracking).
Jadi SEMUA lookup & analisa gap yg dibuat sesi ini (termasuk `Belum_Ada_Di_Listing.xlsx`)
kemungkinan tidak lengkap utk 5 brand itu — listing Volvo/Lexus/Tesla/Lamborghini/Maserati yg
sebenarnya sudah punya SKU di master (via Tracking) bisa saja salah terbaca "belum tayang" atau
gagal di-resolve saat `isi_sku_kosong.py`.

**User memutuskan: file Tracking dijadikan acuan/patokan.** Ditangani dgn
**`scripts/samakan_master_tracking.py`** — BUKAN mengganti nama file di tiap skrip (banyak &
rawan kelewat satu), tapi menyamakan ISI kedua file jadi identik lewat kunci alami
(Nama Produk, Toko, Kategori, Warna, Generasi), dua arah. Hasil: 1.862 baris disalin dari
Tracking ke Master, **0 baris sebaliknya, 0 kunci dgn SKU bentrok**. Setelah rekonsiliasi:
kedua file **identik sempurna** (0 sheet berbeda baris, sheetnames sama).

**TINDAK LANJUT WAJIB sesudah rekonsiliasi ini** (belum tentu sudah dikerjakan — cek dulu):
1. `rebuild_lookup.py` ulang (otomatis ikut lengkap krn Master sudah superset)
2. `isi_sku_kosong.py` ulang — mungkin ada listing Volvo/Lexus/Tesla/Lamborghini/Maserati yg
   sekarang baru bisa ke-resolve
3. `belum_ada_di_listing.py` ulang — angka 81 "belum tayang" & 148 "kurang di toko" yg dilaporkan
   2026-07-30 PERLU DIKOREKSI utk 5 brand ini

**Pelajaran**: kalau ada 2 file yg "harusnya sama" tapi berasal dari sumber/skrip berbeda,
JANGAN asumsikan identik dari nama filenya — bandingkan isinya (sheet, baris, sel) secara
eksplisit sebelum salah satu dipakai sbg SATU-SATUNYA sumber baca oleh skrip analisa.

## 2026-07-30 (lanjutan) — DAMPAK REKONSILIASI: PIPELINE LISTING SEMPAT TERLEWAT

**Kesalahan proses yg ketahuan sendiri**: setelah rekonsiliasi Master+Tracking (1.862 baris),
saya cuma menjalankan `isi_sku_kosong.py` + `step_formula` ulang, TANPA menjalankan
`jalankan_semua_baru.py` (yg juga menulis MOTOR & tahap awal Lazada). Ketahuan dari angka
`step_formula` yg janggal (diubah=33.657, mendekati angka PERTAMA KALI ~33.554, bukan angka
konvergen ~69 yg biasa muncul di run susulan) — pola serupa `diubah` gede juga terlihat di
lazada. Verifikasi langsung: **motor 0% pakai `-MTR-`, semua masih format lama**. Penyebab:
sejak reset container sebelumnya, listing (`BARU_FIX/`) belum pernah diproses pipeline PENUH
di kontainer ini — saya loncat ke pekerjaan model spesifik (Darion/488 Spider/Kwid) tanpa
menjalankan `jalankan_semua_baru.py --apply` dulu. **Pelajaran: angka "diubah" yg jauh lebih
besar dari run sebelumnya WAJIB dicurigai sbg tanda ada tahap yg terlewat/urutan salah,
bukan cuma diterima sbg "makin banyak makin bagus".**

**Sudah dijalankan urutan lengkap & benar**: motor sekarang 3.227 pakai `-MTR-` (0 sisa CM lama),
Lazada 0 kembar, format akhir 91.816 baris 6 segmen.

**Laporan gap dikoreksi**: `Belum_Ada_Di_Listing.xlsx` (454 model, 376 tayang, **78 belum
tayang** [turun dari 81], **164 kurang di toko** [naik dari 148]). Ke-13 model dari 5 brand hasil
rekonsiliasi (Huracan, Model 3/X, 6 Volvo, LC/LS/UX, Ghibli) **semuanya masuk kategori "kurang
di toko"** — sudah tayang di UA, tinggal direplikasi ke OT/OP/SP. Bukan tercatat "belum ada"
sama sekali, jadi listingnya real & sekarang terhubung ke SKU yg benar.

## Konsolidasi SKU Xenia & Veloz -> Avanza (mulai 2026-08-06)

Instruksi user 2026-08-06: kode SKU Daihatsu Xenia dan Toyota Veloz disamakan dengan
Toyota Avanza (konsolidasi stok fisik — produknya diyakini identik secara fisik).

**Aturan final (dikonfirmasi user)**:
- Xenia Gen 1 (2003-2011) DAN Gen 2 (2011-2021) -> DUA-DUANYA pakai kode Avanza
  **"Gen 1 & 2"** (kode segmen `G1`) — karena Avanza TIDAK punya kode G2 terpisah,
  cuma G1 gabungan (2003-2021) dan G3 (2021-2026). Dikonfirmasi via AskUserQuestion.
- Veloz Gen 1 (2011-2021) DAN Gen 2 (2021-2026) -> DUA-DUANYA pakai kode Avanza **Gen 3**
  (kode segmen `G3`), sesuai instruksi eksplisit user ("semua gen Veloz = Avanza gen 3").
- **Hanya kolom SKU yang diubah.** Nama Produk/Kategori/Warna/Generasi/Rentang Tahun/
  Nama Produk Bigseller TETAP Xenia/Veloz apa adanya — produk tetap dijual dgn nama
  aslinya, cuma kode SKU-gudang-nya dikonsolidasi ke Avanza (shared inventory).
- Konsisten dgn aturan #7 (master tidak dedupe baris) — SKU yang sama boleh muncul di
  3 baris berbeda (Avanza asli + Xenia + Veloz), itu sudah preseden lama (UA/OT, SP/OP).

**Hasil pemetaan (dari master versi 14 Juli)**: 132 baris Xenia + 132 baris Veloz,
**100% cocok** (0 gagal) lewat lookup by (Toko, Kategori, Warna) ke SKU Avanza asli
(bukan direkonstruksi manual). Output: `MASTER_Xenia_Veloz_ke_Avanza.xlsx`
(scripts: `preview_xenia_veloz.py` bangun mapping, `terapkan_master_xenia_veloz.py`
terapkan + verifikasi). Warna sel oranye (konsolidasi) di 264 sel SKU yang berubah.

**PENTING — file master yang dipakai per 2026-08-06 adalah versi 14 Juli** (upload lama
yg masih tersisa di server setelah container reset berkali-kali sesi ini). Kemungkinan
BUKAN versi terkini — banyak kerja sesi-sesi berikutnya (23 brand baru, reconciliation
Master/Tracking 1.862 baris, dst, lihat entry-entry di atas). **Kalau user upload master
lebih baru, mapping ini WAJIB dijalankan ulang** (script sudah siap pakai, tinggal ganti
path SRC).

**Status**: mapping master SELESAI & sudah diverifikasi. Bagian kedua instruksi user
("buatkan format siap upload ke Shopee/TikTok/Lazada semua toko") BELUM dikerjakan —
butuh 19 file listing (sama seperti proyek BARU_FIX 27 Juli) untuk menerapkan SKU baru
Xenia/Veloz ke listing riil lalu di-generate jadi file per-marketplace siap upload.

## Xenia Gen 3 (2021-2026) ditambahkan, ikut Avanza G3 (2026-08-11)

Ketemu dari file "CATATAN UA - perlu keputusan (2026-08-07)": 51 baris listing UA
Xenia dgn varian "Gen 3 (2021-2026)"/"Gen 3 (2021-2024)" — generasi yg TIDAK ADA
di master (master lama cuma py Gen 1 & Gen 2 Xenia). User konfirmasi: Xenia Gen 3
ikut kode Avanza G3, sama seperti Veloz.

**Karena Xenia belum py baris Gen 3 di master sama sekali** (beda dgn Gen 1/2 yg
tinggal ditimpa), 66 baris BARU ditambahkan meniru pola Avanza Gen 3 persis
(toko/kategori/warna sama), SKU-nya langsung SKU Avanza Gen 3 (bukan kode baru).
Script: `scripts/tambah_xenia_gen3.py`, dijalankan SETELAH
`preview_xenia_veloz.py` + `terapkan_master_xenia_veloz.py`.

**Pemetaan final Xenia/Veloz -> Avanza (lengkap)**:
- Xenia Gen 1 (2003-2011) -> Avanza "Gen 1 & 2" (G1)
- Xenia Gen 2 (2011-2021) -> Avanza "Gen 1 & 2" (G1)
- Xenia Gen 3 (2021-2026) -> Avanza Gen 3 (G3) — BARU, 66 baris ditambah bukan ditimpa
- Veloz Gen 1 (2011-2021) -> Avanza Gen 3 (G3)
- Veloz Gen 2 (2021-2026) -> Avanza Gen 3 (G3)
Total: 330 baris master terpengaruh (132 Xenia G1/G2 + 66 Xenia G3 baru + 132 Veloz).
Output: `MASTER_Xenia_Veloz_ke_Avanza_v2.xlsx` (file scratchpad, tidak persisten).

**ANTRIAN BERIKUTNYA (user, 2026-08-11) — 5 pasangan model lain, formula sama,
konsolidasi SKU serupa Xenia/Veloz->Avanza**:
- Sigra ikut kode Calya
- Terios ikut kode Rush
- Rocky ikut kode Raize
- Vellfire ikut kode Alphard
- Agya ikut kode Ayla

(arah dikonfirmasi eksplisit oleh user — urutan penulisan di pesan aslinya TIDAK
konsisten menunjukkan arah, mis. "Alphard = Vellfire" tapi arahnya Vellfire->Alphard,
sedangkan "Sigra = Calya" arahnya Sigra->Calya; jangan menebak dari urutan tulisan).
**BELUM dikerjakan** — user minta fokus Avanza/Xenia/Veloz selesai dulu.

**Temuan terpisah dari file "gagal upload" (2026-08-11), DI LUAR scope Xenia/Veloz,
user minta ditunda dulu**: banyak model lain py SKU dobel dalam 1 listing krn varian
rentang-tahun lebih detail dari kode generasi master — OP: Hyundai Santa FE (15/30
baris dobel). SP: Mazda 3 Sedan/Hatchback (+Transparan), Mitsubishi Galant
(+Transparan), Hyundai Santa Fe Transparan, Toyota Corona Transparan, Mercedes Benz
C Class — semua py pola sama (dua rentang tahun beda -> satu kode gen -> SKU kembar).
Sebagian malah masih pakai skema SKU lama 3-segmen (mis. `CVR0038-STP-RTP` dipakai
9x utk Toyota Corona rentang 1960an-2000an). File sumber ada di Drive folder
"Cek gagal upload/{OP,SP}/..." — filenya "Retry Upload ... SKU belum sesuai".

## 5 pasangan model dikonsolidasi ke master (2026-08-11, lanjutan)

Dikerjakan setelah Avanza/Xenia/Veloz. User klarifikasi arah (urutan penulisan pesan
TIDAK konsisten menunjukkan arah, sudah dikonfirmasi eksplisit satu-satu):

| Sumber | Target | Baris |
|---|---|---|
| Daihatsu Sigra Gen1 (2016-2026) | Toyota Calya Gen1 (2016-2026) | 66 |
| Daihatsu Rocky Gen2/A200 (2021-2026) | Toyota Raize Gen1 (2021-2026) | 66 |
| Daihatsu Rocky F70/F300 (1984-2002) | **Daihatsu Feroza "Gen 1&2"** (1993-1996) | 66 |
| Toyota Vellfire Gen2/2F/3/3F (2008-2023) | Toyota Alphard "Gen 1-3" gabungan (2002-2022) | 264 (4x66) |
| Toyota Vellfire Gen4 (2023-2024) | Toyota Alphard Gen4 (2023-2026) | 66 |
| Toyota Agya Gen1 (2013-2023) | Daihatsu Ayla Gen1 dasar (2013-2023, BUKAN F1/F2) | 66 |
| Toyota Agya Gen2 (2023-2026) | Daihatsu Ayla Gen2 (2023-2026) | 66 |
| **Daihatsu Terios Gen1 (1997-2006)** | **Toyota Rush Gen1 (2006-2017)** | 66 |

**Total 726 baris (11 tugas), 100% cocok lewat lookup (Toko,Kategori,Warna) ke SKU
target asli** — sama metodologi Xenia/Veloz.

**Keputusan spesifik yg butuh diingat**:
- **Rocky generasi tua (F70/F300) BUKAN dibiarkan sendiri** — user: "Rocky Gen F70/F300
  = Feroza = Taft GT, kode SKU nya pakai yg SKU Feroza aja". Dipilih Feroza "Gen 1&2"
  (bukan "Gen 3") sbg default krn generasi pertama/utama — BELUM dikonfirmasi user
  scr eksplisit, kalau salah tinggal ganti target_feroza_g1 jadi lookup Gen 3.
- **Terios TETAP dikonsolidasi** (awalnya salah paham dianggap "dibiarkan sendiri"
  krn jawaban user "tetap pakai G1 aja karena formulanya cuma 1" — maksud
  sebenarnya: Terios cuma py 1 generasi jadi langsung disamakan ke Rush Gen 1
  TANPA perlu dipecah, bukan "biarkan kode sendiri". User mengoreksi langsung.
- **Agya Gen1 -> Ayla Gen1 dasar saja**, TIDAK dipecah ke Gen1F1(2017-2020)/
  Gen1F2(2020-2022) meski Ayla py label lebih detail.

**Bug proses yg ketemu (bukan bug logika, tapi keandalan sesi)**: `preview_5pasangan.py`
sempat dijalankan 2x scr berurutan (tanpa Terios, lalu dgn Terios ditambah via Edit)
dlm SATU pemanggilan Bash — hasil JSON yg tersimpan ternyata dari run PERTAMA (tanpa
Terios), padahal console print run KEDUA sudah menunjukkan Terios 66 cocok. Kemungkinan
container reset di tengah rangkaian command turut memutus konsistensi file. **Pelajaran:
setelah edit script yg akan dijalankan bertahap, verifikasi ulang isi JSON/output SEGERA
di panggilan Bash yg sama, jangan asumsikan run sebelumnya "sudah pasti oke" krn
consolenya kelihatan benar** — sempat nyaris terkirim file yg kurang 1 pasangan (660
bukan 726 baris) kalau tidak dicek ulang.

Output: `MASTER_5pasangan.xlsx` (scratchpad, tidak persisten). Scripts:
`preview_5pasangan.py`, `terapkan_5pasangan.py`.

**BELUM dikerjakan**: gabungkan hasil ini dgn `MASTER_Xenia_Veloz_ke_Avanza_v2.xlsx`
jadi SATU file master final (kedua-duanya modifikasi independen di atas source yg
sama, tinggal digabung); lalu terapkan ke 19 file listing utk hasil siap-upload
(masih menunggu file listing terbaru dari user, lihat entry sebelumnya).

## KOREKSI PENTING: master TIDAK bisa dipercaya soal berapa banyak kode generasi (2026-08-11)

User kirim 5 file sample listing Shopee UA riil (format sama sekali BUKA lewat repair_xlsx.py
lebih dulu, bug `activePane="bottom_left"` yg sama). Dari situ ketahuan: **segmen generasi di
SKU tidak selalu 1:1 dengan jumlah baris/label generasi di MASTER.**

**Bukti nyata** (semua dicek langsung dari kolom SKU listing riil, bukan tebakan):
- Alphard: variannya ada "Gen 1-3 (2002-2022)" DAN "Gen 4 (2023-2026)" di teks, tapi
  KEDUANYA pakai kode SKU **G1** (`TYT-ALP-UA-*-G1-*`) — TIDAK ADA kode G4 yang benar2
  dipakai, padahal master py baris terpisah utk "Gen 4".
- Sama persis polanya di: Feroza (Gen1&2 vs Gen3 -> G1 semua), Feroza Long (Gen3/Gen4/
  Model Lain -> G1 semua), Rocky (F70/F300 vs Gen2/A200 -> G1 semua, SEBELUM
  dikonsolidasi), Terios (Gen1 vs Gen2-3 -> G1 semua), Rush (Gen1 vs Gen2 -> G1 semua),
  **Ayla** (Gen1/1F1/1F2/**Gen2** -> G1 semua, termasuk yg TEKSNYA bilang "Gen 2
  2023-2026"!), Agya (Gen1 vs Gen2 -> G1 semua).
- **Avanza & Xenia PENGECUALIAN** — Avanza beneran py 2 kode berbeda di listing riil
  (G1 utk 2003-2020, G3 utk 2021-2026), jadi kerjaan Avanza/Xenia/Veloz sebelumnya
  **TETAP BENAR**, tidak perlu dikoreksi.

**Prinsip yg dikonfirmasi user**: "yg perlu disinkronisasi itu kode SKU-nya, bukan nama
varian gen-nya" — kalau fisik cover-nya cuma 1 formula, SKU-nya harus SATU KODE SERAGAM
(G1) apa pun label generasi di teks varian. Master BOLEH punya banyak baris/label
generasi (utk keperluan tracking/harga/dst), tapi itu TIDAK BOLEH diasumsikan berarti
ada banyak kode SKU berbeda — harus dicek ke listing riil.

**Akibat: 2 dari 11 pemetaan pasangan model (2026-08-11 sebelumnya) SALAH, sudah
diperbaiki**:
- ~~Agya Gen2 -> Ayla Gen2 (kode G2)~~ **-> Agya Gen2 -> Ayla G1** (66 baris)
- ~~Vellfire Gen4 -> Alphard Gen4 (kode G4)~~ **-> Vellfire Gen4 -> Alphard G1** (66 baris)
Total tetap 726 baris (11 tugas), tapi 2 tugas targetnya diganti.

**Pelajaran metodologi ke depan**: sebelum menyimpulkan sebuah model "punya N generasi
kode SKU berbeda" dari master, WAJIB cross-check ke sampel listing riil (kolom SKU
apa adanya) utk model yg SAMA — jangan asumsikan struktur baris master = struktur kode
SKU asli. Kalau ragu dan tidak ada sampel listing, lebih aman tanya user drpd menebak
dari master saja (persis kasus ini).

Script diperbarui: `preview_5pasangan.py` (2 baris target diganti), `terapkan_5pasangan.py`
(verifikasi nama produk diganti dari dict exact-match jadi pencocokan kata kunci, lebih
tahan perubahan label). Output `MASTER_5pasangan.xlsx` (sudah dikirim ulang versi benar).

## Script final siap-terap ke listing (2026-08-11)

`scripts/terapkan_listing_final.py` — transformasi SKU langsung (regex parse 6 segmen,
tukar prefix MEREK-MODEL, generasi ikut apa adanya KECUALI Veloz yg dipaksa G3 dan
Rocky yg rutenya dibaca dari teks varian bukan kode SKU). Berlaku utk Shopee/TikTok/
Lazada (auto-deteksi channel dari nama sheet). Belum sempat dipakai — file sample UA
Shopee yg diupload user (1-5.xlsx) ikut hilang krn reset container SEBELUM sempat
diproses, minta upload ulang.

Cara pakai: `python3 terapkan_listing_final.py <folder_masukan_xlsx> <folder_keluaran>`
— folder masukan berisi file .xlsx APA ADANYA (BUKAN hasil repair_xlsx.py; script ini
belum termasuk repair, jalankan repair_xlsx.py dulu kalau file dari export Shopee
langsung kena bug activePane).

## UA Shopee (5 file) SELESAI diproses & dikirim ke user (2026-08-12)

Setelah 2x file sample sempat hilang krn container reset (sekali chat-upload wiped,
sekali lagi bahkan Drive backup 27 Juli terbukti USANG/tidak boleh dipakai — lihat
entry di atas soal Rocky/Feroza/Ayla/Agya/Xenia/Veloz berubah drastis antara 27 Juli
vs 11 Agustus), user upload ulang 5 file UA Shopee segar (12 Agustus) dan berhasil diproses.

**`scripts/terapkan_listing_final.py` dijalankan, hasil (0 gagal di semua baris)**:

| Model sumber | Baris berubah | Target |
|---|---|---|
| Daihatsu Xenia | 51 | Toyota Avanza (G1 tetap G1, G3 tetap G3) |
| Toyota Veloz | 34 | Toyota Avanza (dipaksa G3) |
| Daihatsu Rocky | 34 (17+17) | Toyota Raize / Daihatsu Feroza (rute dari teks varian) |
| Toyota Agya | 34 | Daihatsu Ayla |
| Daihatsu Terios | 34 | Toyota Rush |
| Toyota Vellfire | 17 | Toyota Alphard |
| Daihatsu Sigra | 17 | Toyota Calya |
| **TOTAL** | **221 baris** | |

Diverifikasi: 5 file zip valid (tidak corrupt), Rocky terbukti kepecah 17/17 ke dua
target berbeda (bukan cuma 1 arah). File hasil dikirim ke user dgn nama jelas
`UA_Shopee_1.xlsx` s/d `UA_Shopee_5.xlsx`.

**PENTING — pelajaran soal keandalan file antar-sesi**: file upload chat TERBUKTI bisa
hilang 2x dalam 1 sesi ini krn container reset (bukan cuma scratchpad, folder
`/root/.claude/uploads/` sendiri ikut ke-reset ke snapshot lama). Backup di Google
Drive JUGA TERBUKTI BISA USANG (versi 27 Juli beda total dari versi 11 Agustus utk
7 dari 8 model yg dicek) — **JANGAN ASUMSIKAN backup Drive/upload lama = current**,
selalu minta versi terbaru & verifikasi via spot-check SKU riil dulu (pola/prinsip
yg sama dgn "jangan asumsikan path file dari memory lama masih benar" di CLAUDE.md,
skrng terbukti berlaku juga utk ISI file, bukan cuma lokasinya).

**UPDATE 2026-08-13/14 — sisa 4 toko selesai diproses & dikirim, plus 2 bug ketemu & fix**:

| Toko | Shopee | TikTok | Lazada |
|---|---|---|---|
| UA | 221 (0 gagal) | 221 (0 gagal, stlh fix bug kolom varian) | 221 (0 gagal, stlh fix bug regex underscore) |
| OT | 221 (0 gagal) | belum | belum |
| SP | 208 (0 gagal) | 208 (0 gagal) | 208 (0 gagal) |
| OP | 208 (0 gagal) | 193 (0 gagal, tapi lihat gap Vellfire) | belum |

Angka SP/OP lebih kecil dari 221 krn katalognya historisnya di-scope ke terlaris saja
(bukan bug — dicek `RE_SKU` tidak match=0 dan SKU kosong=0 di semua baris target-model
utk kedua toko, artinya semua yg ADA sudah tertangkap penuh).

File dikirim dgn nama `SIAP_UPLOAD_<TOKO>_<CHANNEL>.xlsx` (mulai OP/SP batch ini —
`saring_siap_upload.py` skrng terima argumen ke-4 opsional nama toko), isinya HANYA
baris yg SKU-nya berubah (bukan seluruh listing) tapi header/kolom asli platform
(Kode Produk/Kode Variasi dst) tetap utuh supaya bisa langsung diupload.

**Gap ketemu (bukan bug script, perlu tindakan manual user)**: 15 varian
"Toyota Vellfire" di TikTok Otoprotection SKU-nya KOSONG TOTAL (Reguler 6 warna +
Strip 1/2/3 masing 3 warna, baris ~3351-3365 di file `tiktok_2.xlsx` OP) — beda dari
Shopee OP yg sudah lengkap 208. Perlu diisi SKU dulu di TikTok sebelum bisa
dikonsolidasi ke Alphard.

**2 bug ditemukan & di-fix di `terapkan_listing_final.py`/`saring_siap_upload.py`
selama proses ini** (detail lengkap + cara deteksi di
[[feedback-undercover-sku-sync-lessons]] entri 2026-08-13):
1. Regex `RE_SKU` tolak karakter `_` → SKU berakhiran disambiguator `_G1`/`_G2`
   (Lazada, Xenia Gen1/Gen2 sama-sama kode G1) diam-diam ke-skip tanpa masuk log
   gagal. Ketahuan dari spot-check screenshot listing user, bukan dari laporan
   script sendiri. Sempat bikin file Lazada UA yg SUDAH dikirim ke user (136 baris)
   ternyata kurang 85 baris — dikirim ulang versi benar (221 baris).
2. Kolom teks varian TikTok salah ambil (baca `sku_id` kol E, seharusnya
   `variation_value` kol F) → 34 baris Rocky UA gagal deteksi rute Feroza/Raize.
   Ini kegagalan EKSPLISIT (masuk log gagal), beda dari bug #1 yg silent.

**Cara verifikasi wajib skrng sebelum kirim file ke user** (bukan cuma percaya
counter "diubah"/"gagal" dari script): scan ulang semua baris target-model, cek 3
hal terpisah — SKU kosong (gap master/listing), gagal match `RE_SKU` (kandidat
silent-skip), dan (khusus TikTok) kolom varian ke-baca benar. Ketiganya BEDA mode
kegagalan, salah satu bersih tidak menjamin yang lain.

**BELUM dikerjakan**: OT TikTok + OT Lazada, OP Lazada. Semua bisa pakai pipeline
yg sama: `repair_xlsx.py` -> `terapkan_listing_final.py` -> (cek silent-skip manual)
-> `saring_siap_upload.py <fix> <hasil> <out> <nama_toko>`.

## Bug BARU ditemukan (2026-08-14): varian catch-all "Model/Tahun Lain" SKU kosong

User spot-check produk Mazda MX-5 RF (UA Shopee): belasan varian "Model/Tahun Lain"
(per warna/tier) SKU-nya KOSONG, padahal varian generasi spesifik (Gen 1-4) di warna
yg SAMA semuanya pakai SKU IDENTIK (1 formula tunggal) — harusnya catch-all-nya bisa
ikut diisi kode yg sama. Scan sistemik (`scripts/scan_catchall_kosong.py`) ke SEMUA
file yg ada sesi ini (UA+OT+SP+OP, semua channel yg sudah diupload) ketemu pola ini
di skala BESAR:
- **866 baris AUTO_FIXABLE** (sibling 1 formula identik, aman diisi)
- **2.680 baris AMBIGU** (sibling formula beda-beda per generasi, mis. BMW M5 py 6
  kode chassis beda E28/E34/E39/E60/F10/F90 — TIDAK bisa ditebak, perlu keputusan)
- **2.175 baris TANPA_SIBLING** (produk itu sendiri belum py SKU sama sekali di
  varian manapun — beda masalah, gap master bukan gap catch-all)

**User kasih file referensi `Data_Mobil_Lebih_dari_1_Formula.xlsx` (sheet "Sheet2",
213 model) buat validasi** — kolom "Total Formula": =1 berarti SEMUA generasi model
itu pakai 1 kode SKU sama (termasuk yg blm ke-cover eksplisit), >1 berarti generasi
kebagi jadi beberapa formula (baca kolom "Generasi" & "Notes" per baris blok utk tau
batasnya). 196/213 model Total=1, 12 model Total>1 (perlu baca manual, garis rowsplit
tdk selalu = jumlah baris "Generasi"), 5 model "?" (tidak jelas).

**PENTING - "213 terlaris" scope != file terpisah**: user klarifikasi 213 model di
file referensi ITU SENDIRI adalah daftar produk prioritas ("213 terlaris") — bukan
perlu file ranking terpisah. 204/213 model referensi ADA sbg produk nyata di file
yg sudah dipunya sesi ini; SEBAGIAN BESAR (Calya/Ertiga/Rush/Agya/Ayla/Brio/Yaris/
Fortuner dll) ternyata **sudah bersih, TIDAK py baris catch-all sama sekali**
(kemungkinan model populer di-setup lebih rapi sejak awal, tanpa opsi "tahun lain").
Yg genuinely py catch-all-kosong dlm scope 213 cuma **217 baris** (BMW X5, Isuzu Mux,
Mitsubishi Mirage, Opel Blazer, Toyota Soluna/Nav1, Kia Seltos, Mazda MX-5 RF, dll —
model non-mainstream yg kebetulan msk daftar 213).

**Eksekusi 2026-08-14**: `scripts/isi_catchall_kosong.py` (mode `only_listed` = HANYA
isi kalau model eksplisit match referensi Total=1, model tak dikenal/formula>1
DILEWATI) dijalankan ke UA Shopee+TikTok+Lazada, OT Shopee, SP Shopee+TikTok+Lazada,
OP Shopee+TikTok. Hasil: **217/217 baris terisi** (UA Shopee 17, OT Shopee 128, SP
Shopee+TikTok 72, sisanya 0 krn tdk ada catch-all-kosong dlm scope di channel itu).
File dikirim: `SIAP_UPLOAD_{UA,OTONATION,SMARTPROTECTION}_CATCHALL_{SHOPEE,TIKTOK}.xlsx`.

**BELUM dikerjakan**: 649 baris AUTO_FIXABLE di LUAR scope 213 (kebanyakan mobil
niche/import: Land Rover, Range Rover, BMW iX/i3, Wuling EV, Lexus, dll) — valid
secara logika (sibling 1 formula) tapi belum divalidasi ke referensi resmi krn tidak
terdaftar di situ, ATAU belum ditentukan prioritasnya. 2.680 baris AMBIGU (perlu
keputusan default per model) & 2.175 baris TANPA_SIBLING (gap master) sama sekali
belum disentuh — user belum diminta keputusan.

**Jebakan teknis ditemukan sesi ini**: label file di laporan ringkas (`os.path.basename`
saja) BISA BENTROK antar toko krn banyak folder pakai nama generik sama
("1.xlsx"/"2.xlsx" dipakai UA DAN OT; "shopee_1.xlsx"/"tiktok_1.xlsx" dipakai SP DAN
OP) — sempat bikin estimasi awal (217) kelihatan meleset drastis (cuma dpt 145) pas
run pertama krn folder SP/OP kelupaan diproses (basename OT/SP/OP yg sama bikin ke-
skip dari asumsi "sudah kecover"). **How to apply**: kalau melaporkan/membandingkan
hasil per file lintas-folder (beda toko), SELALU pakai path relatif penuh (folder +
nama file) sbg label, JANGAN basename saja — dan re-run definisi lengkap di SEMUA
folder yg relevan drpd asumsi dari daftar ringkasan sebelumnya.

## Verifikasi UA Shopee pasca-upload (2026-08-15)

User upload ulang export UA Shopee terbaru untuk di-double-check setelah menerapkan
harga baru. Hasil audit 22.933 baris listing:

| Yang dicek | Hasil |
|---|---|
| Harga 10 produk teratas (308 baris) | SEMUA BENAR |
| Premium/Exclusive ikut tercemar harga baru? | TIDAK (0 baris) |
| Veloz→Avanza, Sigra→Calya, Terios→Rush, Vellfire→Alphard | SEMUA BENAR |
| Rocky→Feroza/Raize | BENAR, terbagi 17/17 |
| **SKU Xenia & Agya** | **70 baris TER-REVERT** (Xenia 42 `DHT-XNA-*`, Agya 28 `TYT-AGY-*`) |

**Kenapa persis 70 baris itu yang kena**: mereka adalah IRISAN dari "produk yang kena
konsolidasi SKU" DAN "produk yang masuk 10 teratas (dapat harga baru)". Cuma baris
irisan itu yang ikut terbawa di file update harga (yang keliru dibangun dari export
asli, kolom SKU-nya masih kode lama) sehingga tertulis balik. Model konsolidasi lain
(Veloz/Sigra/Terios/Vellfire/Rocky) selamat karena tidak masuk 10 teratas jadi tidak
ada di file harga sama sekali. Detail akar masalah: lihat entri 2026-08-15 di
[[feedback-undercover-sku-sync-lessons]].

Perbaikan dikirim: `SIAP_UPLOAD_UA_PERBAIKAN_SKU_SHOPEE.xlsx` (70 baris), dibangun
dari export TERBARU (bukan export 12 Agustus) sehingga kolom harganya sudah membawa
harga baru yang benar dan tidak me-revert harga.

**Pelajaran metode verifikasi**: script cek harga versi pertama melaporkan "BEDA (ada
385000, harusnya 385000)" untuk SEMUA baris — nilai identik tapi dinyatakan beda,
karena harga di sel tersimpan sbg TEKS sedangkan pembandingnya int. Kalau tidak
diperiksa, ini bisa memicu "perbaikan" 308 baris yang sebenarnya sudah benar. Selalu
normalkan `int(float(v))` sebelum membandingkan nilai sel numerik dari export
marketplace — tipe datanya tidak konsisten antar channel maupun antar export.
