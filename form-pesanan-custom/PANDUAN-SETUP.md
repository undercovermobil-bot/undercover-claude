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
  **Belum diuji di Google Apps Script asli** — cek sekali setelah deploy.
