# Sistem Stok Otomatis — Google Sheets

Untuk file **Stock Opname** (Google Sheet), 2 sheet:

| Sheet | Produk | Total & rekap harian |
|---|---|---|
| **Stok Cover UC** | baris 4–196 (193 produk) | baris 198–199 |
| **Stok Cover STP** | baris 4–107 (104 produk), **+ warna Orange** | baris 109–110 |

Batas baris dicari otomatis saat migrasi (baris terakhir sebelum label "OUT"/"IN" di kolom B), jadi produk yang ditambah sebelum migrasi tetap ikut.
Kode: [`Kode.gs`](Kode.gs).

## Cara kerja

Tiap warna jadi 3 kolom: **STOK | IN | OUT**.

| Aksi staf | Hasil otomatis (±1 detik) |
|---|---|
| Ketik `5` di **IN**, Enter | STOK +5, sel IN kosong lagi, tercatat di "Log Stok" |
| Ketik `2` di **OUT**, Enter | STOK −2, sel OUT kosong lagi, tercatat |
| OUT lebih besar dari STOK | **Ditolak**: sel merah + catatan, STOK tidak berubah |
| Ketik huruf / desimal / minus | Ditolak oleh validasi sheet |
| Admin ketik langsung di **STOK** | Diterima, tercatat sebagai `KOREKSI` (untuk opname) |

Tidak ada lagi langkah "kurangi IN manual" dan "hapus OUT akhir hari".

Baris bawah tabel:
- **TOTAL STOK**: total per warna + total unit (kolom C) + total value.
- **MASUK / KELUAR HARI INI**: jumlah IN/OUT hari ini per warna, dari Log. Otomatis reset tiap ganti hari.

Kolom **Value** memakai harga per baris dari formula lama, tapi sekarang menghitung dari kolom STOK.

## Warna Orange (Stok Cover STP)

Orange = warna **Reguler** ke-6 Smartprotection (SKU `-R-…-ORG`). Sheet lama STP belum punya kolom Orange, jadi migrasi STP otomatis menambahkan blok **Orange: STOK | IN | OUT** tepat setelah Hijau Army:
- Stok awal kosong (0). Isi stok Orange yang ada lewat kolom IN, atau admin ketik langsung di STOK (tercatat `KOREKSI`).
- Value Orange ikut harga **Reguler** per baris (sama dengan Abu-abu, Hitam, dst.).
- Ikut TOTAL STOK, rekap harian, Log, validasi, dan kunci kolom.

Diatur di `KONFIG.SISTEM[1].warnaTambahan`. Warna baru lain bisa ditambah dengan pola yang sama **sebelum migrasi**, mis. `{ nama: 'Silver', setelah: 'Orange' }`. Menambah warna **setelah** sheet aktif dipakai belum didukung script; minta dibuatkan dulu.

## Nama sheet setelah migrasi

| Sebelum | Sesudah |
|---|---|
| Stok Cover UC (format IN/OUT) | **Stok Cover UC** = format baru STOK/IN/OUT, dipakai harian |
| | **Stok Cover UC (lama)** = sheet lama, isi utuh, termasuk Stok Reseller ASTA & ROBY (baris 201+) |
| Stok Cover STP | **Stok Cover STP** (baru) + **Stok Cover STP (lama)** |
| — | **Log Stok** (baru) |

Sheet lain (Resi Keluar Stok, Plan Stok, dll.) tidak disentuh.

## Kenapa butuh Apps Script

Formula biasa tidak bisa "menambah ke dirinya sendiri". `STOK = STOK + IN` adalah referensi melingkar. Angka yang diketik lalu hilang (seperti alur sekarang) hanya bisa lewat script. Apps Script gratis, bawaan Google Sheets, tidak perlu install ekstensi.

## Trial dulu di salinan, baru pasang di file asli

1. Upload `Stock_Opname.xlsx` ke Google Drive.
2. Buka dengan Google Sheets → **File → Simpan sebagai Google Spreadsheet**. File .xlsx yang dibuka langsung (mode Office) tidak bisa memakai Apps Script; menu Ekstensi → Apps Script baru muncul di versi Google Spreadsheet.
3. Di file hasil konversi itu, jalankan langkah **Pasang** di bawah. Coba semua skenario di tabel "Cara kerja".
4. Setelah puas: di file trial klik **Matikan input otomatis**, lalu ulangi langkah Pasang di Google Sheet asli. Script tidak ikut pindah; tempel ulang di file asli.

Migrasi di file asli memakai data saat itu, bukan data file trial.

## Pasang (sekali, oleh pemilik file)

1. **Backup dulu**: File → Buat salinan.
2. Buka Stock Opname → **Ekstensi → Apps Script**.
3. Project masih kosong (hanya `function myFunction() {}`): hapus isinya, tempel seluruh isi [`Kode.gs`](Kode.gs), klik **Simpan**.
   Sudah ada script lain: **jangan dihapus**. Klik **+ → Skrip**, beri nama `SistemStok`, tempel di situ. Kalau script lama juga punya `function onOpen`, gabungkan isinya jadi satu fungsi.
4. Kembali ke sheet, **refresh** halaman. Muncul menu **📦 Sistem Stok**.
5. Klik **1a. Ubah "Stok Cover UC"**.
   - Google minta izin ("Google belum memverifikasi aplikasi ini"): **Lanjutan → Buka (tidak aman) → Izinkan**. Wajar untuk script buatan sendiri.
   - Muncul ringkasan (jumlah produk, OUT yang masih terisi); klik **Ya**.
   - Muncul catatan formula Value yang bermasalah. Catat untuk dicek.
6. Klik **1b. Ubah "Stok Cover STP"**, sama seperti langkah 5.
7. Klik **2. Aktifkan input otomatis** (sekali, berlaku untuk kedua sheet).
8. Tes di kedua sheet: ketik `1` di IN → Enter → STOK +1, IN kosong. Lalu `1` di OUT → kembali semula.
9. (Disarankan) **3. Kunci kolom STOK**: staf hanya bisa isi IN/OUT. Hanya pemilik yang bisa ubah STOK/Log. Admin lain bisa ditambahkan manual di Data → Sheet dan rentang yang dilindungi.

**Waktu migrasi terbaik: akhir hari**, setelah OUT dihapus dan IN sudah final. Script mengambil angka IN apa adanya sebagai STOK awal.

Kalau migrasi error di tengah jalan, script mengembalikan sheet lama ke nama semula dan menghapus sheet setengah jadi.

## Aturan pakai

- **Satu orang saja** yang menekan "Aktifkan input otomatis" (sebaiknya pemilik file). Trigger dari 2 akun tidak menghitung dobel, tapi bikin log penolakan/koreksi tercatat 2×.
- **Jangan buat fungsi bernama `onEdit`** di Apps Script. Bisa memicu proses ganda.
- **Jangan pakai Ctrl+Z** untuk membatalkan input stok. Koreksi dengan input kebalikan (salah IN 5 → OUT 5). Semua tercatat di Log.
- Tunggu sel IN/OUT kosong lagi (±1 detik) sebelum mengetik di **sel yang sama**.
- **Jangan ganti nama** sheet "Stok Cover UC", "Stok Cover STP", "Log Stok", dan jangan hapus sheet "(lama)" (penanda sudah dimigrasi). Kalau perlu ganti nama, ubah juga `KONFIG` di Kode.gs.
- Staf jangan mengisi stok di sheet "(lama)". Isinya tidak lagi diupdate.
- Tambah produk baru: sisipkan baris di atas baris TOTAL STOK, isi nama + STOK, salin formula Value dari baris atas.
- Header baris 2 (nama warna) dan baris 3 (STOK/IN/OUT) jadi patokan script. Jangan diubah.

## Batasan yang perlu dites sendiri

- **Aplikasi Sheets di HP**: dokumentasi Google tidak menyebut beda perilaku trigger di HP, tapi juga tidak menjamin. Tes langkah 8 dari HP sebelum dipakai staf.
- Kolom **User** di Log bisa kosong. Untuk akun Gmail biasa, Google sering tidak memberikan email editor ke script.
- Kuota Google untuk trigger terbatas per hari. Satu input ±1 detik. Volume ratusan input per hari masih jauh di bawah batas.
- Butuh koneksi internet saat input. Input saat offline belum tentu diproses. Sel IN/OUT yang tetap terisi = belum diproses: hapus, ketik ulang.

## Temuan di data sekarang (dicek dari file unduhan 2026-10-08)

Stok Cover UC:
- **Baris 40 (Gran Max/Luxio) & 41 (Fronx)**: formula Value Premium rusak: `=AF40*AM4441128`, `=AF41*AM4441129`. Mengacu ke sel kosong, jadi value Premium selalu 0. Di sheet baru dikosongkan; isi harga manual.
- **14 baris tanpa formula Value**: 50, 58, 68, 69, 70, 82, 83, 94, 118, 140, 190, 191, 192, 194 (mis. Land Cruiser, Jimny 3P, Mazda Cx9).
- **46 sel OUT masih terisi**. Pastikan IN sudah dikurangi sebelum migrasi.
- Baris 19 tertulis "Toyota Swift" (SKU `SZK-SWF-…`). Kemungkinan salah ketik "Suzuki Swift".

Stok Cover STP:
- **Total lama (baris 109–110) hanya menjumlah sampai baris 104.** X-Over, Soluna, C Class (baris 105–107, 3 unit) tidak ikut total. Sheet baru menjumlah sampai 107: 246 unit (total lama 243).
- **Baris 5, 6, 7, 8, 11 — otomatis DIPERBAIKI saat migrasi**: formula Strip lama tidak menghitung Elite Abu & Warior Abu. Sheet baru menghitung semua 9 warna Strip seperti baris lain, harga tetap. Efek di data sekarang: Veloz (baris 6) value Strip 0 → 257.000.
- **Baris 10 (Innova) — otomatis DIPERBAIKI saat migrasi**: formula Reguler merujuk `L9` (Hijau Army baris 9) bukan `L10`. Sheet baru memakai baris sendiri: value Reguler Innova 514.000 → 0 (Innova memang tidak punya stok Reguler).
- **Exclusive**: Smartprotection tidak menjual varian Exclusive (konfirmasi user 2026-10-08). Kolomnya tetap ada tapi kosong; tidak dilaporkan sebagai masalah.
- Strip baris 4 dan Transparan baris 15 tidak punya harga; 8 baris tanpa formula Value sama sekali (47, 73, 91, 102, 103, 105, 106, 107).
- 1 sel OUT masih terisi (Honda Brio Hitam).

## Sheet lain di file

Dicek dari file unduhan: 11 sheet, 1.443 formula, **0 formula yang merujuk sheet lain** (tidak ada `'Sheet'!A1`, IMPORTRANGE, QUERY, VLOOKUP, INDIRECT). Sheet lain aman dibiarkan. Trigger tetap terpanggil saat sheet lain diedit, tapi langsung berhenti di baris pertama (cek nama sheet).

## Uji

`uji/` berisi simulasi Google Sheets (Node) untuk menguji Kode.gs dengan data asli:

```
cd sistem-stok-gsheet
python3 uji/ekstrak.py "Stock Opname.xlsx" uji/fixture.json   # data tidak di-commit
node uji/uji.js Kode.gs
```

Hasil 2026-10-08: 130/130 lulus. Formula hasil migrasi juga dihitung ulang di LibreOffice:
- UC: total unit 1.161, value per baris sama persis dengan sheet lama.
- STP (17 warna, + Orange): total unit 246; value per baris sama dengan sheet lama kecuali baris 6 dan 10 (formula lama salah, lihat Temuan). Tes IN Orange 4 di Brio: Value Reguler +924.000 (4 × 231.000), total 250.
