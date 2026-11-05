---
name: project-undercover-photo-shopee-audit
description: "Audit foto sampul Undercover Autocare selesai 2026-07-06 — hasil, pola, dan keterbatasan metode"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
  modified: 2026-08-01T07:17:55.157Z
---

Audit foto sampul yang belum diupdate ke template branding (logo+badge+ikon bahan) di 3 platform toko Undercover Autocare. Hasil: 74 baris mentah → 45 produk unik (Shopee 38, TikTok 21, Lazada 15). Pola: mobil klasik/niche (jarang laku) atau brand EV Tiongkok baru (BYD/Chery/MG/GAC Aion/Geely — sample fisik cover mungkin belum diproduksi).

Why dicatat: metode deteksi (dimensi foto 1024×1024 Shopee, 1080×1080 TikTok) TIDAK 100% reliable — beberapa foto stock kebetulan pas ukuran "normal," ketahuan lewat scan visual penuh via contact-sheet Lazada. Kalau audit serupa diulang, jangan cuma andalkan dimensi file.

How to apply: scope yang BELUM dicek: foto per varian warna. Output 6 Juli: `List Produk SKU/Audit Foto Produk Belum Update - Undercover 6 Juli 2026.xlsx` — **file ini sudah TIDAK ADA lagi** per 1 Agustus 2026 (dicari di seluruh `Documents\Undercover` + `Downloads`, nihil).

## Audit lanjutan 2026-08-01 — metode BARU yang jauh lebih murah

**Tanggal unggah tiap foto bisa didekode dari URL-nya, tanpa mengunduh gambar sama sekali.** ID gambar Shopee `https://cf.shopee.co.id/file/id-11134207-<prefix>-<id>`: **8 karakter pertama `<id>` adalah timestamp base36 dalam milidetik**. Contoh `m7kflzyz` → `int(...,36)/1000` → 25 Feb 2025. Berlaku untuk 9.852 dari 9.896 URL; 44 sisanya (10 produk) memakai skema ID lama (`sg-11134201-…` atau hash heksadesimal polos) — itu sendiri penanda foto sangat lama. **Ini menggantikan metode dimensi-foto yang dulu dipakai** (tidak perlu unduh, tidak perlu jaringan).

**Titik refresh template baru = 20 Januari 2025.** Ada celah tegas di data: foto sampul tertua berurutan berhenti 26 Des 2024 lalu melompat ke 20 Jan 2025, tanggal saat **470 foto sampul diunggah massal**. Produk bersampul lebih tua dari itu = belum ikut refresh.

**DUA KOREKSI dari spot-check user (Chery Tiggo 8 Exclusive, pid 26127396565) — jangan ulangi:**

1. **Cara menghitung foto: Shopee menghitung SAMPUL + GALERI**, bukan galeri saja. Di Seller Center tampil `(5/9)` untuk produk bersampul + 4 galeri. Menghitung galeri saja menghasilkan 80 produk "kurang dari 5" yang sebagian besar KELIRU; hitungan yang benar cuma **4 produk** (L300 Pickup 1 foto, Bahan Kain Suprena / Logo Custom / Tas Portable masing-masing 3).
2. **Batas tanggal mutlak untuk mendeteksi sampul lama TIDAK JALAN.** Batas 20 Jan 2025 melewatkan Tiggo 8 Exclusive yang sampulnya 2 Feb 2025 tapi desainnya masih lama. **Sinyal yang benar: bandingkan tanggal sampul vs tanggal galeri.** Kalau sampul jauh lebih baru → sampul pernah DIGANTI terpisah (ikut kampanye ganti desain: 246 produk Jan 2025, 53 Feb, 45 Mar). Kalau sampul satu batch dgn galeri → sampul masih ASLI dari awal, kemungkinan besar desain lama. Tiggo 8 Exclusive: sampul & galeri sama-sama 2 Feb 2025 13:21 → tidak pernah diganti.

Hasil dgn sinyal yang dikoreksi: **1.288 produk sampulnya belum pernah diganti** (43 prioritas-1 pra-2025/ID lama, 969 prioritas-2, 276 prioritas-3 dibuat setelah kampanye), **375 produk sampulnya sudah diganti terpisah di 2025+**.

**Batas metode yang tidak bisa ditembus: file ekspor TIDAK memuat informasi desain gambar sama sekali** — hanya riwayat waktu unggah. Empat sinyal metadata sudah diuji dan SEMUANYA gagal memisahkan desain: batas tanggal mutlak, foto galeri template bersama, riwayat ganti sampul, sampul dibagi antar tier. Jangan buang waktu mengulang keempatnya.

## Pemeriksaan visual 2026-08-01 — inilah metode yang benar-benar jalan

User memberi izin mengunduh; 1.012 sampul (Prioritas 1 & 2) diunduh dari `cf.shopee.co.id` lalu diperiksa. **Unduhan berhasil 1.010/1.012 percobaan pertama** (2 URLError, berhasil saat diulang). Butuh `pip install Pillow` (tidak terpasang); `requests` juga tidak ada — pakai `urllib.request` + `ThreadPoolExecutor(12)`.

**Beda visualnya tegas dan mudah dilihat.** Sampul BERDESAIN selalu punya, di bagian ATAS gambar: logo `UNDERCOVER AUTOCARE`, banner biru diagonal, badge `REGULER`/`PREMIUM`/`EXCLUSIVE`, dan baris ikon bahan. Sampul POLOS hanya foto mobil stok di latar putih — **strip atas gambar kosong total**.

**Pemilah otomatis yang terbukti:** ukur porsi piksel pada strip **13% teratas** — (a) biru-merek (`b>90 and b-r>35 and b-g>20`), (b) gelap (`r,g,b < 120`), (c) non-putih. Pada 72 gambar berlabel manual pemisahannya **SEMPURNA**: seluruh sampul polos = **0,000** di ketiga ukuran; seluruh sampul berdesain ≥0,018 biru dan ≥0,028 gelap. Foto mobil stok ternyata selalu dipadding putih ke rasio 1:1, itu sebabnya strip atasnya bersih. Diverifikasi ulang: ke-29 hasil "polos" benar semua, sampel acak 36 dari kelompok "berdesain" 0 salah.

**HASIL FINAL (yang berlaku, gantikan angka-angka di atas):**
- **29 produk URGENT — sampul masih foto mobil polos tanpa desain.** 23 dari Prioritas 1, 6 dari Prioritas 2. Termasuk **ketiga listing Chery Tiggo 8** (Exclusive/Reguler/Premium), Neta V, GAC Aion Hyptec HT, Proton Gen 2/Suprima/Exora, Daihatsu Ceria/Espass/Taft GT, Mercedes SLK (3 listing), Kia Pride/Cerato, Hyundai Getz/Grand i20, Volvo 850, Mazda 323, Daewoo Ssangyong Musso, Mitsubishi L300 Pickup.
- **982 produk** sampul sudah berdesain, hanya masih dari batch unggah awal — prioritas lebih rendah.
- **1 kasus khusus** (Tas Portable — bukan cover, template standar tak berlaku).
- **276 Prioritas 3** tidak diunduh atas pilihan user, status belum pasti.
- **375** sampul sudah diganti terpisah 2025+, dinilai dari riwayat saja.

Output final: `Documents\Undercover\Cek gagal upload\Audit Foto Shopee UA - 1 Agustus 2026.xlsx` (6 sheet + Metode).

Angka versi awal (sebelum koreksi) dari `mass_update_media_info_361186752_20260801105306.xlsx` (1.663 produk aktif Shopee UA):
- **A: 43 produk** sampul belum format baru (termasuk 7 produk ber-ID skema lama). Profilnya sama persis dgn audit 6 Juli — mobil klasik/niche (Timor, Opel Blazer, Hummer H1, Kia Pride, Proton, Daihatsu Ceria/Espass/Taft GT, Mercedes SLK, Volvo 850) + EV Tiongkok (Neta V) + 2 cover motor. Audit lama dapat 38 di Shopee, metode ini 43 → konsisten, metode lama memang diketahui melewatkan sebagian.
- **B: 80 produk** foto galeri < 5 (standar toko: 5 galeri + 1 sampul). Rincian: 1 produk 0 foto, 3 produk 2 foto, 76 produk 4 foto. Irisan dgn A = 19.
- **C: 347 produk** sampul sudah baru (Jan–Mar 2025) tapi SELURUH galerinya masih 2024 — refresh Januari 2025 ternyata **hanya menyentuh foto sampul, galeri tidak ikut**. Tiap produk galerinya diunggah sekali batch (tanggal min = maks).

Output: `Documents\Undercover\Cek gagal upload\Audit Foto Shopee UA - 1 Agustus 2026.xlsx` (sheet A/B/C + sheet Metode).

**Keterkaitan dgn sub-proyek SKU:** pid `27755059717` (Mitsubishi L300 Pickup Reguler) ternyata punya **0 foto galeri, hanya sampul** — itulah sebab konkret kegagalan unggah SKU-nya di Shopee (*"Jumlah gambar produk harus antara 3 dan 9"*, lihat [[project-undercover-bigseller-sync]]). Tambah minimal 3 foto galeri dulu, baru SKU-nya bisa diunggah.

**Keterbatasan yang tetap ada:** ini proksi TANGGAL UNGGAH, bukan pemeriksaan visual. Foto lama yang kebetulan sudah sesuai template ikut keflag; foto yang diunggah ulang setelah Jan 2025 tapi desainnya masih lama tidak terdeteksi. Tetap sarankan spot-check visual sebelum eksekusi massal.

**Lanjutan 2026-11-05:** penggantian foto produk dan foto per varian warna Smartprotection ke marketplace dicatat di [[project-undercover-foto-smartprotection-marketplace]].
