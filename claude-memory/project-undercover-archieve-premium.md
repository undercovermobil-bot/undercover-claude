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
- **Hasil top-10** (n_row = total baris varian gabungan 3 channel): Toyota
  Crown (96, 1 dari sedikit yang genuinely tercatat 0 di sales file,
  bukan cuma "tidak ada data"), Honda Civic Sedan (66), Nissan Cedric
  (60), Toyota RAV4 (60), Hyundai Sonata (58), Mitsubishi Galant (54),
  BMW Seri 5 (50), Volkswagen Passat (48), BMW Seri 7 (44), Kia Sportage
  (42) — total **578 baris** (188 Shopee + 190 Lazada + 200 TikTok).
- **Rename**: tambah `" archieve"` di akhir judul (title-case asli
  dipertahankan, cuma nambah suffix, idempotent — cek dulu kalau sudah
  berakhiran "archieve" biar tidak dobel kalau script dijalankan ulang).
  SKU, harga, dan kolom lain SAMA SEKALI tidak disentuh.
- **Output ikut aturan "mass-upload hanya baris berubah"**: tiap file
  keluaran cuma berisi baris Premium dari 10 model ini (bukan full
  katalog), header/struktur template dipertahankan (sheet TikTok
  `Instruction`/`HiddenAttr`/`Brand`/dst tetap utuh, cuma sheet `Template`
  yang isinya di-trim+rename).

## File hasil (dikirim ke user 2026-09-20, TIDAK di-commit ke git sesuai
kebijakan data besar)

`ARCHIEVE_PREMIUM_SHOPEE_1..4.xlsx` (14+54+16+104=188 baris),
`ARCHIEVE_PREMIUM_TIKTOK_tiktok_2.xlsx` (200 baris, dari 3 file TikTok yg
diupload 18 Sept — cuma file ke-2/katalog utama yang punya baris Premium
dari 10 model ini), `ARCHIEVE_PREMIUM_LAZADA_file_4.xlsx` (190 baris).
Sumber listing: file UA Shopee/TikTok/Lazada yang diupload user 18-20
September (sudah diperbaiki dari bug XML `activePane` via
`repair_xlsx.py`, lihat `project-undercover-harga-referensi.md` bagian
2026-09-18 audit).

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
