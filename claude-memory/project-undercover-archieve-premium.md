# Archive produk Premium tidak laris (mulai 2026-09-20)

## Konteks

User mau nonaktifkan produk-produk yang tidak laris secara massal, tapi
Shopee/TikTok/Lazada tidak punya cara bulk-deactivate langsung yang cepat.
**Workaround user**: ganti dulu judul produk supaya diakhiri kata
**`archieve`** (ejaan ini sengaja dipakai persis, bukan typo yang perlu
dibetulkan ke "archive") — nanti user search kata itu di masing-masing
ecommerce lalu nonaktifkan manual satu-satu dari hasil pencarian. Tugas
Claude cuma sampai menyiapkan file rename judul siap-upload, TIDAK ikut
menonaktifkan apa pun (itu manual oleh user di luar sesi ini).

**Trial pertama**: 10 produk tipe **Premium** (bukan Reguler/Strip/
Exclusive/Transparan) yang **paling tidak laris**, khusus toko
**Undercover Autocare (UA)**, di **semua 3 marketplace** (Shopee/TikTok/
Lazada) sekaligus.

## Sumber data & keterbatasan (PENTING kalau lanjut ke toko/tier lain)

- **Data penjualan**: `MOBIL_TERLARIS_GABUNGAN.xlsx` (sheet `Top 300
  Mobil`, kolom 58 = `Total Premium`), periode Jan-Jun 2026. **File ini
  GABUNGAN SEMUA 4 TOKO** (Undercover/Otonation/Otopro/Smartpro) — TIDAK
  ada kolom per-toko sama sekali (dicek eksplisit di sheet `Detail Gen &
  Warna` juga, sama-sama tidak ada kolom Toko). Dipakai sbg proxy "least
  selling UA" dengan asumsi UA dominan di volume (listing UA paling
  banyak & paling lama, sesuai `project-undercover-analisa-penjualan.md`)
  — TIDAK bisa dipisah murni per-toko dari file ini. Kalau user mau
  ranking yang benar-benar UA-only, perlu data order UA-only terpisah.
- Cuma 320 model yang tercatat di file (Top 300-an), sementara **UA
  sendiri punya 708 produk Premium unik** (gabungan nama dasar lintas 3
  channel) — jadi **mayoritas (>500) sama sekali tidak tercatat laku**
  (dianggap 0). Tidak mungkin ranking presisi di antara ratusan yang
  sama-sama "0" itu dari data penjualan saja.
- **Stok BUKAN sinyal pembeda** - dicek eksplisit: SEMUA 388 produk
  Premium UA di Shopee stok-nya 0 (beda dari Reguler yang stoknya
  bervariasi riil, mis. 95/2/89/102/65) — kemungkinan Premium memang
  dibuat-sesuai-pesanan/tidak di-stok, jadi stok tidak bisa dipakai
  tiebreak sama sekali.
- **Tiebreak yang dipakai**: di antara yang sama-sama "0/tidak tercatat",
  urutkan berdasar **jumlah baris varian (n_row) TERBANYAK** (gabungan 3
  channel) — makin banyak baris kembar produk itu, makin besar
  "pembersihan" listing yang didapat kalau diarsipkan, dan itu satu-
  satunya sinyal terukur yang tersisa. Ini heuristik, BUKAN data
  penjualan asli — kalau user mau kriteria lain (mis. harga termahal,
  brand paling exotic, umur listing), perlu instruksi eksplisit baru.

## Metode teknis

- **Deteksi tier Premium**: segmen ke-4 SKU = `P` (lewat `urai_sku()` dari
  `update_harga_per_sku.py`, sama seperti dipakai proyek harga).
- **Ekstraksi nama model dasar dari judul produk** — pola judul Premium
  TERNYATA beda-beda per channel (baru ketemu saat kasus ini, catat utk
  proyek lain juga):
  - Shopee & Lazada UA: `Undercover Autocare - Cover Mobil {Model}
    Premium` (toko di depan)
  - TikTok UA: `Cover Mobil {Model} Premium - Undercover Autocare` (toko
    di BELAKANG) atau `Body Cover Mobil {Model} Premium` (tanpa nama
    toko sama sekali)
  Fungsi baru `extract_base_premium()` (scratchpad `extract_base.py`)
  toleran ke ketiga pola ini sekaligus (strip "undercover autocare" di
  mana pun posisinya, strip prefix "(body )cover mobil", strip suffix
  "premium"). **Kalau nemu pola judul lain yang tidak ke-strip bersih,
  base name akan salah/aneh** — selalu spot-check hasil sebelum kirim.
- **Rename**: tambah `" archieve"` di akhir judul (title-case asli
  dipertahankan, cuma nambah suffix, idempotent — cek dulu kalau sudah
  berakhiran "archieve" biar tidak dobel kalau script dijalankan ulang).
  SKU, harga, dan kolom lain SAMA SEKALI tidak disentuh.
- **Output ikut aturan "mass-upload hanya baris berubah"**: tiap file
  keluaran cuma berisi baris Premium dari 10 model ini (bukan full
  katalog), header/struktur template dipertahankan (sheet TikTok
  `Instruction`/`HiddenAttr`/`Brand`/dst tetap utuh, cuma sheet `Template`
  yang isinya di-trim+rename).
- **Output digabung 1 file per channel** (bukan 1 file per file-sumber) —
  koreksi user 2026-09-20: awalnya Shopee dipecah 4 file (ikut jumlah
  file sumber `1.xlsx`-`5.xlsx`), user minta digabung jadi 1 file Shopee
  saja. Caranya: baris yang kena dari SEMUA file sumber per channel
  ditulis ke SATU workbook output (pakai file sumber pertama yg py baris
  kena sbg shell/template, sheet lain dipertahankan, baris data lama
  dihapus dulu baru diisi ulang gabungan).

## KOREKSI 2026-09-20: prioritaskan model DI LUAR Top-300, bukan cuma "0 Premium"

User koreksi cara ranking versi pertama: model yang **ADA** di daftar
Top-300 (berarti model itu genuinely laku di tier lain, cuma Premium-nya
yang sepi) **JANGAN didahulukan** dibanding model yang **SAMA SEKALI TIDAK
ADA** di Top-300 (berarti hampir tidak ada penjualan sama sekali, tier
apapun — sinyal "tidak laris" yang jauh lebih kuat). Versi pertama salah
mencampur keduanya jadi satu skala "tercatat 0 atau tidak tercatat = sama
saja" — padahal user melihat itu 2 level ketidaklarisan yang beda jauh.

**Urutan prioritas final**: (1) di LUAR Top-300 dulu (708 produk Premium
unik total, **428 di luar Top-300**, **105 di antaranya ada di ketiga
channel sekaligus**), (2) baru di dalamnya urut `n_row` terbanyak seperti
semula. Model yang ADA di Top-300 (Toyota Crown, Hyundai Sonata, dst dari
versi pertama) TIDAK dipakai lagi di top-10 final kecuali kandidat di
luar Top-300 habis (masih jauh dari habis, 428 >> 10).

## Hasil FINAL (v2, dikirim ke user 2026-09-20)

**Top-10** (n_row = total baris varian gabungan 3 channel, semua di LUAR
Top-300): Honda Civic Sedan (66), Nissan Cedric (60), Toyota RAV4 (60),
Volkswagen Passat (48), Range Rover Sport (36), Toyota Prius (36), Kia
Sorento (30), Ford Ranger T6 (30), Mazda 3 Hatchback (30), Mazda 3 Sedan
(30) — total **142 baris per channel** (sama persis di Shopee/TikTok/
Lazada, karena kesepuluhnya memang ada lengkap di ketiga channel).

**File dikirim** (TIDAK di-commit ke git sesuai kebijakan data besar):
`ARCHIEVE_PREMIUM_SHOPEE.xlsx` (142 baris, gabungan dari source
`1.xlsx`/`2.xlsx`/`4.xlsx` — `3.xlsx`/`5.xlsx` kebetulan 0 baris kena),
`ARCHIEVE_PREMIUM_TIKTOK.xlsx` (142 baris, dari `tiktok_2.xlsx` saja —
file 1/3 di luar scope/0 baris), `ARCHIEVE_PREMIUM_LAZADA.xlsx` (142
baris). Sumber listing: file UA Shopee/TikTok/Lazada yang diupload user
18-20 September (sudah diperbaiki dari bug XML `activePane` via
`repair_xlsx.py`, lihat `project-undercover-harga-referensi.md` bagian
2026-09-18 audit).

**File v1 (SUPERSEDED, jangan dipakai)**: `ARCHIEVE_PREMIUM_SHOPEE_1..
4.xlsx` + `..._TIKTOK_tiktok_2.xlsx` + `..._LAZADA_file_4.xlsx` (10 model
versi pertama, salah prioritas + Shopee masih terpecah 4 file) — sudah
dikirim ke user tapi digantikan v2 di atas, jangan dipakai kalau muncul
lagi di riwayat chat/file.

## Batas akurasi "di luar Top-300" — sudah ditanyakan, user OK pakai proxy

User tanya: bisa cek yang BENAR-BENAR 0 penjualan (bukan cuma "di luar
Top-300")? Dicek ke sheet `Metodologi`: **"di luar Top-300" BUKAN berarti
0 penjualan** — sheet `Top 300 Mobil` cuma merinci 321 model, sisanya
digabung jadi 1 baris "TOTAL ekor panjang" = **167 unit TIDAK DIRINCI per
model**. Jadi bisa saja ada model di luar Top-300 yang genuinely laku
1-2 unit, tercampur rata dengan yang betul-betul 0 — file rangkuman ini
tidak bisa membedakan. Untuk presisi itu perlu data order MENTAH (file
`Order.all.*.xlsx` Shopee / `Semua pesanan-*.xlsx` TikTok per toko, bukan
laporan yang sudah dirangkum), supaya bisa hitung sendiri quantity per
model termasuk yang di luar Top-300.

**Ditanyakan ke user (AskUserQuestion) — jawaban: cukup pakai proxy
"di luar Top-300" seperti sekarang, TIDAK perlu upload data order
mentah.** Jadi ranking v2 di atas (428 model di luar Top-300, tiebreak
n_row terbanyak) **tetap jadi acuan final** untuk kebutuhan archive ini.
Kalau nanti user berubah pikiran dan mau presisi 0-murni, itu perlu data
order mentah yang belum ada di sesi manapun sejauh ini.

## Next step kalau user lanjut

- Setelah user coba search+nonaktifkan manual pakai kata "archieve" dan
  konfirmasi workflow ini works, kemungkinan lanjut ke batch berikutnya
  (11-20 dst) atau toko lain (OT/OP/SP - masing-masing perlu listing
  fresh diupload dulu, belum ada di sesi ini per 2026-09-20).
- Kalau user kasih data penjualan yang BENAR-BENAR per-toko (bukan
  gabungan), rank ulang pakai itu — jangan asumsikan urutan 10 ini tetap
  sama, karena proxy gabungan-4-toko ini punya keterbatasan yang sudah
  dijelaskan di atas.
- Kalau user mau kriteria tiebreak lain (bukan n_row terbanyak), tanya
  eksplisit dulu sebelum ganti heuristik.
