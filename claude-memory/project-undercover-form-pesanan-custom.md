---
name: project-undercover-form-pesanan-custom
description: "Form pencatatan pesanan LINK CUSTOM (model di luar Top 100) utk admin — xlsx/Google Sheet dari master, mulai 2026-09-24"
metadata:
  node_type: memory
  type: project
---

**Konteks (2026-09-24)**: user merampingkan listing Undercover — model di luar 100 terlaris dijual via **link custom** (pembeli diskusi varian dgn admin). Admin/ops perlu mencatat mobil apa yg dibeli. User tanya Excel/Sheet vs HTML; rekomendasi: **Google Sheet** (upload xlsx ke Drive -> buka sbg Google Sheets) krn data tersimpan di file itu sendiri, multi-admin, gampang direkap. HTML statis tidak punya tempat simpan data; kalau mau HTML harus pakai backend (Apps Script -> Sheet, atau artifact dgn database) — belum dibuat.

**Script**: `scripts/buat_form_pencatatan_custom.py MASTER.xlsx RANKING_BIGSELLER.xlsx OUT.xlsx "label versi"`. Output 6 sheet: Cara Pakai, Input Pesanan (3.000 baris siap isi), Pengaturan (list Admin/Toko/Marketplace/Status/Kategori/Warna — editable), Rekap per Model (SUMIFS qty/pesanan/omzet, Batal+Retur dikecualikan), Daftar Mobil (sumber dropdown), Master SKU (kunci -> SKU).

Desain yg sudah diputuskan:
- **1 dropdown gabungan "Model | Generasi | Tahun"** (bisa diketik utk cari di Google Sheets & Excel 365), bukan dropdown bertingkat Merek->Model — dropdown dependen via OFFSET/INDIRECT tidak didukung validasi Google Sheets. Merek/Model/Generasi/Tahun/SKU terisi otomatis.
- Pilihan dikunci per **(model, generasi, rentang tahun)**, bukan (model, generasi): master 07-03 punya "Toyota GR 86 Gen 2" utk 2 rentang tahun dgn SKU beda (2012-2020 -> G1, 2021-2026 -> G2) — bug label master, belum dilaporkan/dibetulkan di master.
- SKU: OT pakai kode UA, OP pakai kode SP (aturan konsolidasi #1). Warna Strip dinormalkan 2 arah: **Strip 1=Epic, Strip 2=Elite, Strip 3=Warrior** (sumber: status OT & SP, terverifikasi dari SKU existing). CATATAN: `project-undercover-sku-sync-rules.md` baris "Strip1/2/3 = Elite/Epic/Warrior" urutannya beda — yg dipakai adalah urutan Epic/Elite/Warrior.
- Rumus cuma INDEX/MATCH/COUNTIFS/SUMIFS/SUBSTITUTE/IFERROR (tanpa XLOOKUP/FILTER; omzet via kolom Subtotal tersembunyi + SUMIFS, bukan SUMPRODUCT+IFERROR yg butuh CSE di Excel lama). `formula1` DataValidation openpyxl TANPA awalan "=".
- Status "Top 100": ranking `MOBIL TERLARIS BIGSELLER.xlsx` (Drive, dibuat 09-17, Shopee+TikTok 1 Apr–16 Sep 2026, Lazada tidak termasuk), baris non-mobil (judul mengandung " - ") dilewati. `Mobil Terlaris.xlsx` (Drive) TIDAK dipakai — diagnostiknya TikTok 0 baris.

**Diuji** (LibreOffice Calc recalc, 10 kasus): konsolidasi OT/OP, Elite Abu SP -> `...-S2A`, Strip 1 Merah OP -> `...-S1M`, Strip 2 Biru UA -> `...-EBR`, GR 86 G1/G2, peringatan kombinasi tak ada/Toko kosong/mobil salah ketik, rekap mengecualikan Batal. Validasi dropdown selamat round-trip. BELUM diuji langsung di Google Sheets.

**STATUS: baru DEMO dari master Drive 03-07-2026 (181 model, 445 pilihan).** Master ini JAUH ketinggalan: dari 268 model ranking #101+ (calon link custom), ±200 tidak ada di master 03-07 (Mercedes cuma 3 model, MINI kosong, tanpa Evalia/Harrier/Carry/Mazda 2 Sedan); 7 model Top 100 juga tak ada. Juga belum ada aturan kembar (Xenia masih `DHT-XNA`), rename 07-21, dsb. Google Sheet master bersama (owner ahmadazhaarrii, 07-07) isinya sama 181 model. **Master terbaru (69+ sheet, 353+ model) cuma ada di PC user** -> perlu dilampirkan ke chat lalu jalankan ulang script. File demo: `Form Pencatatan Pesanan Custom (DEMO master 03-07).xlsx` (gitignored).

**Temuan teknis Drive (2026-09-24, mengoreksi catatan 07-27 "download besar tidak praktis")**: `mcp__Google_Drive__download_file_content` utk file besar (diuji s/d 1,77MB xlsx = 2,36jt karakter base64) TIDAK masuk context — harness menyimpan hasilnya ke `tool-results/mcp-Google_Drive-download_file_content-*.txt` (JSON `{content: base64,...}`), tinggal `json.load` + `base64.b64decode` lokal. Jadi file Drive BISA diambil tanpa minta lampiran, selama ID-nya ketemu lewat `search_files`.

## REVISI 2026-09-25 — versi ringkas (menggantikan desain di atas)

User: desain lama "terlalu ribet"; cukup **Merek -> Model -> Generasi/Tahun** (dropdown bertingkat), visual ringkas utk admin. Desain SKU/kategori/warna/Top-100 di atas DIBUANG dari form (logikanya masih tercatat di atas kalau nanti dibutuhkan lagi).

- Master dipakai: `MASTER_SKU_Price_Tracking.xlsx` (lampiran user 09-25, 4MB, **76 sheet, 504 model, 1.234 generasi**) — ini master terbaru, bukan versi Drive 03-07.
- Script `scripts/buat_form_pencatatan_custom.py MASTER.xlsx OUT.xlsx` (ditulis ulang). Output `Form Pesanan Custom.xlsx`: sheet Input (Tanggal, No. Pesanan, Merek▼, Model▼, Generasi/Tahun▼, Catatan; 2.000 baris), Rekap (jumlah pesanan per model), Cara Pakai; Data & Bantu disembunyikan.
- Dropdown bertingkat = sheet Bantu 1 baris bantu per baris Input (INDEX/MATCH/COUNTIF) + validasi per baris ke range baris itu. Alasan: validasi dropdown Google Sheets tidak menerima INDIRECT/OFFSET. Kolom tersembunyi G/H + conditional format -> sel Model/Generasi merah kalau tidak cocok (mis. Merek diganti belakangan).
- Nama model dipendekkan (buang awalan merek: "Toyota Avanza" -> "Avanza", "Mercedes Benz E Class" -> "E Class"); 0 bentrok nama.
- Label generasi = "Gen X (tahun)" dari baris toko **Undercover Autocare** (semua 504 model punya baris UA). Master tidak konsisten: 108 generasi punya >1 rentang tahun di baris UA sendiri (153 kalau lintas toko) -> dipakai yg paling sering. Janggal: **GAC Aion Hyptec HT Gen 1 = "1994-Now"** (14 baris) padahal mobil listrik baru — data master perlu dicek.
- Diuji LibreOffice: Toyota->50 model, Daihatsu->20, Avanza->2 gen, Merek salah/gen salah -> merah, Rekap benar. Batas: jika >2.000 baris, buat file baru (validasi per baris tidak otomatis ikut kalau baris ditambah). BELUM diuji langsung di Google Sheets.
