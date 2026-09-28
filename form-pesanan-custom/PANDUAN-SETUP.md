# Form Pesanan Custom — Panduan Setup (sekali saja, ±10 menit)

Admin cukup membuka **satu link** yang tampilannya seperti website, lalu mengisi 3 kolom
(Merek → Model → Generasi/Tahun) dan klik **Simpan**. Setiap pesanan otomatis masuk ke
Google Sheet. Kalau model mobilnya tidak ada di daftar, admin cukup mengetik manual.
Model itu otomatis ditambahkan ke daftar, jadi pesanan berikutnya sudah muncul di dropdown.

## Isi folder

| File | Fungsi |
|---|---|
| `Code.gs` | Kode server (menyimpan ke Sheet, menambah model baru ke daftar) |
| `Index.html` | Halaman form yang dilihat admin |
| `Form Pesanan Custom - Google Sheet.xlsx` | Data awal: sheet **Daftar Mobil** (76 merek, 504 model dari master) + sheet **Rekap Pesanan** kosong. File ini tidak masuk git; dibuat dengan `scripts/buat_form_pencatatan_custom.py MASTER.xlsx OUT.xlsx` |

## Langkah setup

1. **Upload ke Google Drive**: upload `Form Pesanan Custom - Google Sheet.xlsx`,
   buka dengan Google Sheets, lalu **File → Simpan sebagai Google Spreadsheet**.
   Pakai file hasil simpan itu (menu Apps Script hanya ada di Google Sheet asli, bukan xlsx).
2. Di Google Sheet itu: **Ekstensi → Apps Script**.
3. Di editor Apps Script:
   - Buka file `Code.gs` bawaan, hapus isinya, lalu tempel isi `Code.gs` dari folder ini.
   - Klik **+ → HTML**, beri nama `Index` (tanpa `.html`), lalu tempel isi `Index.html`.
   - Klik **Simpan** (ikon disket).
4. **Jalankan setup sekali**: pilih fungsi `siapkan` di dropdown atas, lalu klik **Jalankan**.
   - Google akan minta izin. Klik **Tinjau izin → pilih akun → Lanjutan → Buka (tidak aman) → Izinkan**.
     Peringatan ini normal untuk script buatan sendiri.
   - Setelah selesai, muncul sheet **Ringkasan** (jumlah pesanan per model & per generasi).
5. **Deploy**: **Terapkan → Deployment baru → ikon roda gigi → Aplikasi web**.
   - *Jalankan sebagai*: **Saya** (akun under.covermobil)
   - *Yang memiliki akses*: **Siapa saja yang memiliki Akun Google**
     (admin cukup login Gmail masing-masing, tidak perlu akses edit ke Sheet).
   - Klik **Terapkan**, lalu salin **URL aplikasi web** (berakhiran `/exec`).
6. Bagikan URL itu ke admin dan minta mereka menyimpannya sebagai bookmark atau shortcut di layar HP.

## Cara admin mengisi

1. Klik kolom **Merek**, lalu ketik sebagian nama (mis. `toy`) → pilih **Toyota** (klik / Enter).
2. **Model** hanya menampilkan model merek itu. Ketik `avan` → **Avanza**.
3. **Generasi / Tahun** hanya menampilkan generasi model itu → pilih.
4. Klik **Simpan**. Muncul pesan hijau "Tersimpan", lalu form kosong lagi untuk pesanan berikutnya.

Mobil tidak ada di daftar: ketik lengkap, lalu pilih **"+ Tambah baru: …"**. Muncul label
kuning **Baru**. Setelah disimpan, mobil itu otomatis masuk **Daftar Mobil** (Sumber = Manual).

Catatan:
- Waktu pesanan dicatat otomatis (tidak perlu isi tanggal).
- Huruf besar/kecil tidak masalah: `toyota avanza` tetap tersimpan sebagai `Toyota Avanza`,
  tidak jadi model dobel.
- Model baru yang ditambahkan admin lain baru muncul setelah halaman di-refresh.
- Salah ketik yang terlanjur masuk daftar: hapus barisnya langsung di sheet **Daftar Mobil**.

## Edit / revisi langsung di sheet "Rekap Pesanan"

Kolom **Merek, Model, Generasi / Tahun** di Rekap Pesanan punya dropdown bertingkat
(dipasang otomatis tiap pesanan tersimpan). Kalau admin merevisi langsung di sheet:
- Ganti **Merek** → Model & Generasi baris itu dikosongkan (kalau model lama bukan milik merek baru),
  dan dropdown Model langsung berisi model merek baru.
- Ganti **Model** → Generasi dikosongkan (kalau tidak cocok), dropdown Generasi menyesuaikan.
- Ketik huruf kecil (`avanza`) → otomatis jadi ejaan resmi (`Avanza`), jadi Ringkasan tidak terpecah.
- Ketik mobil yang tidak ada di daftar → tetap diterima (muncul segitiga peringatan kecil). Setelah Merek, Model,
  dan Generasi lengkap, mobil itu otomatis masuk **Daftar Mobil** (Sumber = "Manual (edit sheet)").
- **Waktu** tidak berubah saat baris diedit. Sheet **Ringkasan** langsung ikut terhitung ulang.
- Hapus baris pesanan (klik kanan → Hapus baris) aman, Ringkasan ikut berkurang.
- Kalau dropdown hilang (mis. setelah copy-paste dari luar): menu **Form Pesanan → Pasang ulang dropdown di Rekap Pesanan**.

Otomatisasi ini hanya jalan kalau edit dilakukan di Google Sheets (bukan di file xlsx yang diunduh).

## Ukuran & harga (Subcompact / Compact / Midsize / Large / Jumbo)

Setelah Model dipilih, kolom **Ukuran** terisi otomatis dan kartu harga 4 tipe muncul
(Reguler / Strip / Premium / Exclusive). Ukuran tetap bisa diganti untuk pesanan itu.

| Ukuran | Pcs/Roll | Reguler | Strip | Premium | Exclusive |
|---|---|---|---|---|---|
| Subcompact | 7 | Rp301.000 | Rp344.000 | Rp715.000 | Rp1.115.000 |
| Compact | 6 | Rp337.000 | Rp380.000 | Rp751.000 | Rp1.151.000 |
| Midsize | 5 | Rp387.000 | Rp430.000 | Rp801.000 | Rp1.201.000 |
| Large | 4 | Rp462.000 | Rp505.000 | Rp876.000 | Rp1.276.000 |
| Jumbo | 3 | Rp583.000 | Rp626.000 | Rp997.000 | Rp1.397.000 |

- Sumber harga: `Judul Deskripsi Harga Custom UA.txt` (Drive, 25-09-2026).
- Ukuran per model = tier Pcs/Roll di `DATA UC HPP Top 100 Terlaris.xlsx` (290 model).
  Dikonfirmasi user 28-09: Honda Jazz = **Compact**, Suzuki Ignis = **Compact**, Daihatsu Sigra = **Midsize**.
- Model tanpa data ukuran (214 model) → admin wajib pilih ukuran. Setelah disimpan, ukuran itu tercatat
  di sheet **Ukuran Mobil** (Sumber = Manual), jadi pesanan berikutnya terisi otomatis.
- Sheet baru (dibuat `siapkan`): **Matriks Harga** (ubah harga di sini → form langsung ikut) dan
  **Ukuran Mobil** (ubah ukuran model di sini). Rekap Pesanan dapat kolom **F = Ukuran** (ada dropdown),
  Ringkasan dapat tabel jumlah pesanan per ukuran (kolom J).
- Ganti Model di sheet Rekap → Ukuran ikut data model baru (dikosongkan kalau belum ada datanya).

### Update dari versi sebelumnya (sheet sudah terpasang)
1. Ganti isi `Code.gs` dan `Index.html` di editor Apps Script, lalu Ctrl+S.
2. Pilih fungsi `siapkan` → Run (data lama tidak terhapus; sheet Matriks Harga & Ukuran Mobil dibuat kalau belum ada).
3. Deploy → Manage deployments → pensil → Version: **New version** → Deploy (link tetap sama).

## Isi Google Sheet

| Sheet | Isi |
|---|---|
| **Rekap Pesanan** | 1 baris per pesanan: Waktu, Merek, Model, Generasi/Tahun, Model Baru? |
| **Ringkasan** | Jumlah pesanan per model (kiri) dan per generasi (kanan), urut terbanyak |
| **Daftar Mobil** | Sumber dropdown. Baris `Master` dari master SKU, `Manual` dari admin |

## Kalau kode diubah

Setelah mengubah kode: **Terapkan → Kelola deployment → ikon pensil → Versi: Versi baru → Terapkan**.
URL tetap sama. Kalau memilih "Deployment baru", URL-nya berubah.

## Catatan teknis

- Label generasi = `Gen X (tahun)` diambil dari baris toko Undercover Autocare di master. Ada 108 generasi
  yang rentang tahunnya tidak konsisten di master; dipakai yang paling sering muncul.
- Penyimpanan memakai `LockService`, jadi aman walau beberapa admin menyimpan bersamaan.
- Teks yang diawali `=`, `+`, `-`, `@` dipaksa jadi teks biasa (tidak dijalankan sebagai rumus).
- Sudah diuji lokal (Chromium + tiruan Google Sheet): alur pilih-simpan, ketik manual → masuk daftar →
  muncul di dropdown, ejaan disamakan, merek baru, ganti merek mereset model, tampilan HP 390px.
  edit langsung di Rekap (ganti merek/model/generasi, ejaan, model baru, paste 1 baris, hapus isi).
  **Belum diuji di Google Apps Script asli** — cek sekali setelah deploy.
