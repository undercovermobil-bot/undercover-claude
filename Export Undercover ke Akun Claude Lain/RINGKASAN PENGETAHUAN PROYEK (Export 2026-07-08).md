# Undercover — Ringkasan Pengetahuan Proyek

> Dibuat 2026-07-08 sebagai paket "seed context" supaya sesi Claude baru (akun lain / mesin lain) bisa langsung paham proyek ini tanpa mengulang riset atau bug yang sudah pernah ditemukan. Tempel isi file ini sebagai pesan pertama di percakapan baru, atau upload filenya kalau kliennya mendukung upload.
>
> Detail penuh (kronologis, tiap bug, tiap keputusan) ada di memory asli — lihat bagian "Sumber" di akhir dokumen.

## Apa ini

**Undercover** = kerja pemeliharaan katalog produk untuk sebuah jaringan toko "cover mobil" (car body cover) yang jualan di Shopee/TikTok/Lazada lewat 4 toko: **Undercover Autocare (UA)**, **Otonation (OT)**, **Otoprotection (OP)**, **Smartprotection (SP)**. Ada 2 sub-proyek independen di dalam satu folder:

1. **Shopee Price Monitor** — aplikasi Python kecil untuk memantau harga kompetitor. Berhenti berkembang, lihat status di bawah.
2. **SKU Sync** (workstream utama, jauh lebih besar) — menyamakan SKU semua listing e-commerce dengan 1 database master, lalu membuat file siap-upload per toko/channel. Ini yang paling banyak makan waktu & paling bernilai untuk dilanjutkan.
3. **Audit Foto Produk** — audit sekali-jalan, sudah selesai & delivered, kemungkinan kecil dilanjutkan tapi dicatat untuk konteks.

---

## Sub-Proyek 1: Shopee Price Monitor

Python modular (`config`/`utils`/`database`/`discovery`/`monitor`/`compare`/`dashboard` + `main.py` CLI), SQLite, dashboard Streamlit.

**Status: mentok, sudah di-pivot.** Shopee 2026 punya anti-bot agresif yang mendeteksi Chromium yang dikontrol Playwright itu sendiri — bukan soal login/headless. Diuji 5 konfigurasi (headless/headed × dengan/tanpa login), semua kena block (`90309999` / halaman error). Login berhasil (`storage_state.json`) tapi begitu dipakai automation tetap diblok. `curl` polos ke API → 403.

**Kesimpulan yang sudah divalidasi — jangan diulang risetnya:** vanilla Playwright + stealth ringan TIDAK cukup untuk Shopee. Kalau mau jalan beneran, dua opsi: (a) API scraping berbayar (ScraperAPI/Apify — sudah ada backend `apify_backend.py`/`scraperapi_backend.py` siap pakai), atau (b) browser anti-deteksi + proxy residensial. **Sudah pernah berhasil**: pivot ke Apify actor `4nhvc7lTKzkDrk7bD` (Shopee Search & Category Scraper), tes 3 keyword → 97 produk asli masuk DB, dashboard jalan di localhost:8501. Backend scraping diisolasi di class `ShopeeScraper` (`discovery.py`) — tinggal swap tanpa sentuh DB/dashboard/compare.

Belum dikerjakan: jadwal cron harian, perluasan keyword per tipe mobil spesifik.

---

## Sub-Proyek 2: SKU Sync (workstream utama)

### Konsep dasar

- Sumber kebenaran = `List Produk SKU/SKU, Price, Tracking Cover Mobil.xlsx` — 1 sheet per merek mobil (64 sheet), format SKU **`MEREK-MODEL-TOKO-KAT-GEN-WARNA`**.
- Tujuan: file per toko/channel dalam **format e-commerce asli** (siap mass-upload), bukan file gabungan.
- Kategori: Reguler / Premium / Exclusive (istilah umum) — plus tier warna **Strip 1/2/3** (kode toko SP/OP) yang di UA/OT disebut **Elite/Epic/Warrior** (istilah beda, tier sama). Jangan tertukar — ini 2 gaya penamaan untuk konsep yang sama.
- Warna sel status (dipakai di semua file hasil): 🟩 **hijau**=benar, 🟦 **biru**=diisi dari kosong, 🟧 **oranye**=migrasi-legacy/auto-koreksi/konsolidasi, 🟥 **merah**=perlu cek manual.

### Aturan bisnis yang WAJIB diikuti (sudah final, jangan didesain ulang)

1. **Konsolidasi toko** — stok fisik Otonation = Undercover Autocare, stok fisik Otoprotection = Smartprotection. `TARGET_STORE = {"UA":"UA","OT":"UA","OP":"SP","SP":"SP"}`. Sejak **2026-07-08 ini SUDAH di-bake langsung ke MASTER** (sebelumnya cuma diterapkan saat build file listing) — akibatnya "SKU duplikat" di master melonjak ke ~98,5% baris (by design, exclude pasangan UA↔OT dan SP↔OP dari perhitungan "duplikat genuine").
2. **Judul BigSeller/SKU Gudang** — prioritas dari Nama Produk **listing asli toko** (Undercover→fallback Otonation untuk kode UA; Smartprotection→fallback Otoprotection untuk kode SP), fallback terakhir baru "Nama Produk Bigseller" master. (Ini keputusan final setelah 3x dibolak-balik user — jangan diubah lagi tanpa instruksi eksplisit.)
3. **SKU Gudang baru** hanya pakai kode **UA & SP** (skip OT/OP) — konsisten kebijakan konsolidasi.
4. **Varian generik** ("Tahun Lain"/"Model Lain"/"Custom") → SKU dikosongkan, jangan ditebak, walau modelnya single-generasi.
5. **Stok warna Abu-abu pada Reguler & tier-1 (Strip1/Elite/S1A/EAB)** = **0** — aturan gudang, berlaku ke SELURUH katalog (bukan cuma batch yang sedang dikerjakan). ⚠️ Filter berbasis kode SKU gampang jebol kalau ada 2 skema tier (Strip-N vs Elite/Epic/Warrior — kode warna Abu: `S1A/S2A/S3A` di SP/OP, tapi `EAB/PAB/WAB` di UA/OT). Selalu cross-check ke teks varian asli, jangan cuma pola kode SKU.
6. **Produk luar-scope** (Karpet Mobil, Cover Motor `CM####`, Travel Pouch TikTok3-Undercover) HARUS dikecualikan dari pencocokan model — kalau tidak, judul yang kebetulan menyebut nama model mobil (mis. "Karpet Honda Accord") ikut ke-match salah.
7. **Master TIDAK dedupe baris Toko** — tetap 4 baris terpisah per model (1 per toko) meski kode SKU-nya sekarang sama antar pasangan (lihat poin 1). Kolom teks "Toko" juga tidak dihapus.
8. Kalau butuh evidence "SKU ini beneran real/terpakai" (bukan cuma valid-secara-teori di master) — SELALU cross-check ke data operasional riil (13 file `Hasil Sinkronisasi SKU/`, export BigSeller, dll), jangan asumsikan "valid di master" = "aman dipakai tim ops."

### Status saat ini (checkpoint 2026-07-08)

**Selesai & terverifikasi:**
- Rollout 63 merek + pilot Toyota + audit data-quality + audit kepatuhan aturan (0 pelanggaran).
- Revisi taksonomi generasi besar-besaran (master disesuaikan ke pola listing Undercover Shopee sebagai patokan).
- Fix bug sistemik "bare-variant" (produk dengan varian 1-dimensi diam-diam terbuang dari file lama) — **+3.646 baris** dikembalikan lintas 9 kombinasi toko/channel.
- Fix 18 model gap generasi, fix konvensi "Outdoor" khusus Otonation, fix duplikasi SKU Lazada generasi-tunggal (44 produk Crown-family, 30 resolved).
- Fix stok Abu-abu=0 diperluas ke seluruh katalog (2 lapis bug filter, sudah 0 sisa di semua toko).
- **Konsolidasi kode toko di-bake ke MASTER** (OT→UA, OP→SP permanen) — 29.145 sel berubah di 46 sheet.
- Deliverable "100 Mobil Terlaris" — 18.358 baris teoretis → divalidasi ke data real (31.224 SKU real dikumpulkan dari 82 file operasional) → **16.672 (90,8%) terkonfirmasi real**, sisanya ditandai "Belum Terkonfirmasi". File: `~/Downloads/SKU Produk - 100 Mobil Terlaris.xlsx`.

**Belum selesai / sengaja ditunda:**
1. Gap Transparan-Otonation (master tidak punya SKU kategori Transparan untuk Otonation/Undercover).
2. ~51 model + ribuan baris "bare-color-only" di Otoprotection/Smartprotection-TikTok — listing cuma punya 1 dimensi varian (warna), tanpa pilihan generasi → tak bisa dipastikan otomatis. List: `Model Perlu Update Manual (Otoprotection & Smartprotection-TikTok).xlsx`.
3. 14 produk Crown-family-like yang generasinya genuinely butuh riset manual (Chevrolet Aveo/Cruze, Dodge Journey, Kia Sedona/Carnival, Mazda 3/3 Sedan, Nissan Teana, Toyota CHR/Corona/Nav1/Previa, VW Golf, Suzuki Forsa).
4. 26 produk di luar folder "166 Model Baru" dengan bug sama (generasi tunggal Lazada) tapi master sudah lengkap — tinggal eksekusi mekanis kalau mau lanjut.
5. 132 SKU duplikat pre-existing (Daihatsu Ayla, Wuling BAO — sengaja 1 SKU untuk 2 generasi, butuh keputusan user) + 180 SKU invalid pre-existing di Smartprotection — belum diaudit.
6. 47 sheet merek di master masih KOSONG TOTAL (Volkswagen, Lexus, Jeep, Land Rover, Peugeot, Volvo, Porsche, Audi, Ferrari, dll) — akar penyebab utama baris yang "belum bisa dapat SKU". Isi master untuk merek volume tinggi dulu kalau mau naikkan coverage.
7. Belum cross-verify file listing e-commerce lama vs kode toko master yang baru saja dikonsolidasi (poin 1 di atas) — kemungkinan besar sudah konsisten (karena TARGET_STORE sudah lama dipakai di situ) tapi belum dicek eksplisit.

### Pelajaran berulang (paling penting untuk yang lanjutkan)

- **Pertanyaan spesifik user tentang 1 produk konkret** ("kenapa produk X ini SKU-nya kosong?") adalah cara PALING ampuh menemukan bug sistemik yang jauh lebih besar dari yang ditanyakan — terjadi berkali-kali (typo Xpander Cross 144 baris, alias Honda 1.623 baris, bare-variant 3.646 baris, dll). Kalau user cek manual sebelum minta "selesai" dianggap final, ambil serius.
- **Master itu shared lintas toko** — begitu master diperluas untuk 1 toko/channel yang jadi trigger investigasi, WAJIB cek SEMUA channel lain yang pakai kode toko sama, jangan asumsikan cuma yang jadi trigger yang butuh update.
- **Filter berbasis kode SKU rapuh** kalau ada >1 skema penamaan (lihat aturan #5 di atas). Cross-check ke teks varian asli.
- **Precondition eksplisit dari user itu mengikat**, bukan saran — jangan anggap selesai dari verifikasi parsial (pernah kejadian: promote draft ke master sebelum verifikasi selesai, harus di-revert).
- **Penghapusan data operasional/bisnis-kritis** (mis. SKU duplikat pre-existing) harus dikonfirmasi langsung ke user, tidak boleh lewat proses background/otomatis walau cuma "flagging."
- Setiap kali proses "tambah/gabung baris ke file yang sudah ada" dijalankan >1 kali (multi-pass), WAJIB cek duplikasi row-identity di akhir.
- Kalau script menambah baris baru ke template e-commerce, WAJIB copy semua field level-produk (gambar, deskripsi, dimensi paket) dari baris sibling — bukan cuma kolom yang sedang diperbaiki.

### ⚠️ Script/engine TIDAK ikut ter-export — harus dibuat ulang

Semua logic pemrosesan (`engine.py`, `build_all.py`/`build_pilot.py`, `gen_word_all.py`, `xlsx_loader.py`, `split_files.py`, dll) hidup di **scratchpad sementara**, bukan di folder proyek — dan sudah berkali-kali hilang antar sesi sepanjang proyek ini (harus direkonstruksi ulang dari deskripsi memory / diff backup master tiap kali lanjut). Cek per 2026-07-08: hanya 1 fragmen (`xlsx_loader.py`) yang masih bertahan di sebuah folder temp, dan itupun bisa hilang kapan saja. **Anggap semua script ini tidak ada** — sesi baru yang mau lanjutkan SKU sync perlu membuat ulang enginenya dari nol, mengikuti aturan bisnis & konvensi di dokumen ini + `CATATAN Sinkronisasi SKU - Semua Merek.docx` (bagian "Cara Kerja" & "Catatan Teknis").

---

## Sub-Proyek 3: Audit Foto Produk (selesai, 2026-07-06)

Audit foto sampul yang belum diupdate ke template branding (logo+badge+ikon bahan) di 3 platform toko Undercover Autocare. Hasil: **74 baris mentah → 45 produk unik** (Shopee 38, TikTok 21, Lazada 15). Pola: mobil klasik/niche (jarang laku) atau brand EV Tiongkok baru (BYD/Chery/MG/GAC Aion/Geely — sample fisik cover mungkin belum diproduksi). Metode dimensi-foto (1024×1024 Shopee, 1080×1080 TikTok) **tidak 100% reliable** — beberapa foto stock kebetulan pas ukuran "normal", ketahuan lewat scan visual penuh via contact-sheet Lazada. Scope belum cek: galeri foto 1-8 & foto per varian warna (baru cek sampul/thumbnail).

Output: `List Produk SKU/Audit Foto Produk Belum Update - Undercover 6 Juli 2026.xlsx`.

---

## Lokasi file penting

| File/Folder | Isi |
|---|---|
| `List Produk SKU/SKU, Price, Tracking Cover Mobil.xlsx` | **Master** — sumber kebenaran SKU |
| `List Produk SKU/Hasil Sinkronisasi SKU/<Toko>/` | 13 file listing tersinkron (mass-upload ready) + 2 dokumen CATATAN (.docx) |
| `List Produk SKU/Update SKU 166 Model Baru 2026-07-06/` | File update terbaru (166 model gap + fix Crown-family + Abu-abu=0) |
| `List Produk SKU/Impor SKU Gudang/` , `Ekspor SKU Gudang/` | State sinkron BigSeller |
| `List Produk SKU/List Produk <Toko> 6 Juli 2026/` | Raw export native per-platform (baseline terbaru) |
| `~/Downloads/SKU Produk - 100 Mobil Terlaris.xlsx` | Deliverable terbaru untuk tim ops (di LUAR folder proyek!) |
| `Undercover.md` (vault note) | Log progress lengkap kronologis |

## Sumber (kalau butuh detail penuh)

- `CATATAN Sinkronisasi SKU - Semua Merek.docx` (13 bagian) & `CATATAN Sinkronisasi SKU - Toyota (Pilot).docx` — narasi resmi lengkap.
- Memory asli (kalau sesi baru punya akses ke memory Claude Code yang sama): `project-undercover-sku-sync.md`, `project-undercover-shopee-antibot.md`, `project-undercover-photo-shopee-audit.md`.
