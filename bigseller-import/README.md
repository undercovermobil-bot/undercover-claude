# Impor SKU Gudang ke Big Seller

Sub-proyek: menyiapkan file impor "membuat SKU Gudang" untuk Big Seller dari
data ekspor SKU Gudang. Dimulai 2026-07-17.

## Ringkas kejadian 2026-07-17

User mengirim 8 file:
- 1 template kosong `impor_untuk_membuat_sku_gudang` (40 kolom, hanya berisi
  1 baris contoh ilustrasi satuan/masa-berlaku — **bukan** default yang dipakai).
- 7 file `SKU_Gudang…0221–0227`.

**Temuan:** ke-7 file `SKU_Gudang` itu **satu ekspor Big Seller yang utuh**,
terpotong per 5.000 baris (kolom `Kode Produk` berurutan menyambung dari file 1
ke file 7). Gabungan = **32.156 SKU, semuanya unik, 0 duplikat**. Jadi file-file
itu = **isi Big Seller saat ini**, bukan daftar sumber terpisah.

Sebaran per toko (segmen ke-3 SKU): **UA 15.382 · SP 11.292 · OT 2.762 · OP 2.720**.

Kondisi field di ekspor: `Modal Referensi`, `Harga Jual Referensi`, `Berat`,
`Panjang/Lebar/Tinggi` **semua 0**; `GTIN` kosong semua; `Tautan Gambar` terisi
25.961 (6.195 tanpa gambar); semua `Jenis SKU = SKU Tunggal`.

## Yang dihasilkan

`build_import.py` menggabungkan 7 ekspor → dedup Nomor SKU → memetakan ke 40
kolom template, mengisi hanya field yang berdata (**Nomor SKU, Judul, Kategori,
GTIN kalau ada, Tautan Gambar**) dan mengosongkan sisanya (harga/stok/berat/
dimensi/satuan/masa-berlaku diatur belakangan di Big Seller). Output:
- 1 file gabungan (32.156 baris)
- 7 file `Part n dari 7` (@≤5.000 baris) — mengikuti batas per-file platform.

File `.xlsx` tidak di-commit (lihat `.gitignore`) — dikirim langsung ke user &
disimpan di Google Drive. Yang di-commit hanya skrip + catatan ini.

Reproduksi:
```
python bigseller-import/build_import.py "<folder berisi SKU_Gudang*.xlsx>" "<folder output>"
```

## Catatan penting / belum dipastikan (untuk sesi berikutnya)

- **"Produk yang belum ada di Big Seller" butuh daftar acuan pembanding.**
  Ke-7 file yang diberikan = isi Big Seller sekarang, bukan acuan. Untuk
  benar-benar menghitung selisih "belum ada", perlu salah satu dari: (a) master
  katalog `SKU, Price, Tracking Cover Mobil.xlsx`, atau (b) ekspor listing
  hidup per toko, atau (c) ekspor Big Seller akun/gudang tujuan (kalau ini
  migrasi ke akun lain). Per sesi ini user memilih memproses **hanya dengan 8
  file yang diberikan**, jadi output = seluruh 32.156 SKU dalam format impor;
  Big Seller sendiri akan melewati SKU yang sudah ada saat impor mode "buat".
- Batas 5.000 baris/impor **diasumsikan** dari pola potongan ekspor — belum
  dikonfirmasi sebagai batas impor resmi.
