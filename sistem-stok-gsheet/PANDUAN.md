# Sistem Stok Otomatis — Google Sheets

Untuk file **Stock Opname** (Google Sheet), sheet **"Stok Cover UC"** baris 4–196 (193 produk).
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

Kolom **Value** (Reguler/Strip/Premium/Exclusive/Total) tetap memakai harga per baris dari formula lama, tapi sekarang menghitung dari kolom STOK.

## Kenapa butuh Apps Script

Formula biasa tidak bisa "menambah ke dirinya sendiri". `STOK = STOK + IN` adalah referensi melingkar. Jadi angka yang diketik lalu hilang (seperti alur sekarang) hanya bisa lewat script. Apps Script gratis, bawaan Google Sheets, tidak perlu install ekstensi.

## Pasang (sekali, oleh pemilik file)

1. **Backup dulu**: File → Buat salinan.
2. Buka Stock Opname → **Ekstensi → Apps Script**.
3. Project masih kosong (hanya `function myFunction() {}`): hapus isinya, tempel seluruh isi [`Kode.gs`](Kode.gs), klik **Simpan**.
   Sudah ada script lain: **jangan dihapus**. Klik **+ → Skrip**, beri nama `SistemStok`, tempel di situ. Kalau script lama juga punya `function onOpen`, gabungkan isinya jadi satu fungsi.
4. Kembali ke sheet, **refresh** halaman. Muncul menu **📦 Sistem Stok**.
5. Klik **📦 Sistem Stok → 1. Buat sheet sistem**.
   - Google minta izin ("Google belum memverifikasi aplikasi ini"): **Lanjutan → Buka (tidak aman) → Izinkan**. Wajar untuk script buatan sendiri.
   - Muncul ringkasan; klik **Ya**. Terbentuk sheet **"Stok UC Sistem"** dan **"Log Stok"**. Sheet lama tidak diubah.
6. Klik **2. Aktifkan input otomatis**.
7. Tes: ketik `1` di IN salah satu produk → Enter → STOK +1, IN kosong. Lalu `1` di OUT → kembali semula.
8. (Disarankan) **3. Kunci kolom STOK**: staf hanya bisa isi IN/OUT. Hanya pemilik yang bisa ubah STOK/Log. Admin lain bisa ditambahkan manual di Data → Sheet dan rentang yang dilindungi.

**Waktu migrasi terbaik: akhir hari**, setelah OUT dihapus dan IN sudah final. Script mengambil angka IN apa adanya sebagai STOK awal. Kalau ada OUT tersisa, script menampilkan daftarnya sebelum lanjut.

## Aturan pakai

- **Satu orang saja** yang menekan "Aktifkan input otomatis" (sebaiknya pemilik file). Trigger dari 2 akun tidak menghitung dobel, tapi bikin log penolakan/koreksi tercatat 2×.
- **Jangan buat fungsi bernama `onEdit`** di Apps Script. Bisa memicu proses ganda.
- **Jangan pakai Ctrl+Z** untuk membatalkan input stok. Koreksi dengan input kebalikan (salah IN 5 → OUT 5). Semua tercatat di Log.
- Tunggu sel IN/OUT kosong lagi (±1 detik) sebelum mengetik di **sel yang sama**.
- **Jangan ganti nama** sheet "Stok UC Sistem" / "Log Stok". Kalau perlu, ubah juga `KONFIG` di Kode.gs.
- Tambah produk baru: sisipkan baris di atas baris TOTAL STOK, isi nama + STOK, salin formula Value dari baris atas.
- Header baris 2 (nama warna) dan baris 3 (STOK/IN/OUT) jadi patokan script. Jangan diubah.

## Batasan yang perlu dites sendiri

- **Aplikasi Sheets di HP**: dokumentasi Google tidak menyebut beda perilaku trigger di HP, tapi juga tidak menjamin. Tes langkah 7 dari HP sebelum dipakai staf.
- Kolom **User** di Log bisa kosong. Untuk akun Gmail biasa, Google sering tidak memberikan email editor ke script.
- Kuota Google untuk trigger terbatas per hari. Satu input ±1 detik. Volume ratusan input per hari masih jauh di bawah batas.
- Butuh koneksi internet saat input. Input saat offline belum tentu diproses. Sel IN/OUT yang tetap terisi = belum diproses: hapus, ketik ulang.

## Temuan di data sekarang (perlu dicek manual)

- **Baris 40 (Gran Max/Luxio) & 41 (Fronx)**: formula Value Premium rusak: `=AF40*AM4441128`, `=AF41*AM4441129`. Harusnya `*harga`, tapi mengacu ke sel kosong, jadi value Premium selalu 0. Di sheet baru dikosongkan; isi harga yang benar manual.
- **14 baris tanpa formula Value**: 50, 58, 68, 69, 70, 82, 83, 94, 118, 140, 190, 191, 192, 194 (mis. Land Cruiser, Jimny 3P, Mazda Cx9). Value-nya tidak ikut total.
- **46 sel OUT masih terisi** di file yang diunduh. Pastikan IN sudah dikurangi sebelum migrasi.
- Baris 19 tertulis "Toyota Swift" (SKU `SZK-SWF-…`, No urut 3). Kemungkinan salah ketik "Suzuki Swift".

## Menambah sheet STP nanti

Struktur "Stok Cover STP" hampir sama, dengan 3 beda (dicek 2026-10-08):
- Warna ke-15 bernama **Transparan** (UC: Premium). Label kolom Value "Premium" di `GRUP_VALUE` perlu dibuat per sheet.
- Produk sampai **baris 107** (105 produk). Jadi `barisAkhir: 107`, bukan 104.
- Total lama di baris 109–110 hanya `SUM(...4:...104)`: X-Over, Soluna, C Class (baris 105–107, 3 unit) **tidak ikut total** sekarang.

Langkah: tambah entri `{ sumber: 'Stok Cover STP', tujuan: 'Stok STP Sistem', barisAwal: 4, barisAkhir: 107 }` di `KONFIG.SISTEM`,
fungsi `function migrasiStokSTP() { migrasi_(KONFIG.SISTEM[1]); }`, dan item menunya.

## Sheet lain di file

Dicek dari file unduhan 2026-10-08: 11 sheet, 1.443 formula, **0 formula yang merujuk sheet lain** (tidak ada `'Sheet'!A1`, IMPORTRANGE, QUERY, VLOOKUP, INDIRECT). Sheet lain aman dibiarkan; script hanya membaca/menulis sheet sistem + "Log Stok". Trigger tetap terpanggil saat sheet lain diedit, tapi langsung berhenti di baris pertama (cek nama sheet).

## Uji

`uji/` berisi simulasi Google Sheets (Node) untuk menguji Kode.gs dengan data asli:

```
cd sistem-stok-gsheet
python3 uji/ekstrak.py "Stock Opname.xlsx" uji/uc.json   # data tidak di-commit
node uji/uji.js Kode.gs
```

Hasil 2026-10-08: 82/82 lulus. Formula hasil migrasi juga dihitung ulang di LibreOffice: total unit (1.161) dan value per baris sama persis dengan sheet lama.
