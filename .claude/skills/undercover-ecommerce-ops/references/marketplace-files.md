# File marketplace (Shopee, TikTok) dan cara membacanya

## TikTok - `Tiktoksellercenter_batchedit_<tgl>_all_information_template[_N].xlsx`
- Sheet `Template`; baris 1-5 header (baris 1 kunci tersembunyi, 3 label, 4 wajib/opsional, 5 petunjuk); **data mulai baris 6**, satu baris per varian.
- Kolom (indeks 0): A `product_id`, C `product_name`, E `sku_id`, F `variation_value`, I harga ritel, **K `seller_sku` (indeks 10)**, total 48 kolom.
- `_1`, `_2` = pecahan per kategori produk (mis. `_2` berisi satu produk kategori Golf). Satu produk = satu `product_id`.
- Label varian: `Abu-abu, Gen 1 : 2025-Now`, `Strip 1 Biru, ...`; Transparan tanpa warna: `Gen 1 : 2025-Now` atau `Default`.
- Sheet terproteksi (sheetProtection) tetapi edit sel diizinkan; XML sheet1 bisa ~28 MB (aman diproses).
- SKU "kosong" bisa berupa sel dengan shared string kosong (bukan sel tak ada).
- Export lain yang sering ikut: `..._media_information_*` (bukan untuk SKU).

## Shopee - `mass_update_basic_info_<idToko>_<timestamp>.xlsx` (nama, deskripsi)
- Sheet1; baris 1-3 header (baris 2 berisi JSON kondisi pencarian), **data mulai baris 7**.
- Kolom: A Kode Produk, B SKU Induk, C Nama Produk, D Deskripsi, E Alasan Gagal. **Tidak ada varian/SKU varian.**
- Dipakai untuk rename (archive). Id toko: OP 476733837, SP 473932094, UA 361186752.

## Shopee - Info Penjualan (`mass_update_sales_info`; user menamai `1.xlsx`, `2.xlsx`)
- Sheet1; header baris 1-6 (baris 3 label), **data mulai baris 7**, satu baris per varian.
- Kolom: A Kode Produk, B Nama Produk, C Kode Variasi, D Nama Variasi, E SKU Induk, **F SKU**, G Harga, H GTIN, I **Stok**, J.. batas beli.
- Export dipecah beberapa file: pengalaman OP: `1` = produk Reguler/Strip, `2` = Transparan. Gabungkan semua file saat menganalisis.
- Label varian Shopee **tanpa spasi setelah koma**: `Strip 1 Biru,Gen 1 : 2025-Now`; Strip ditulis "Strip 1 Abu" (bukan Abu-abu).
- Produk tanpa variasi: Nama Variasi kosong; SKU Induk bisa masih legacy `CVR####-OTP-...` dengan kolom SKU kosong (kasus Santa Fe Transparan OP).
- Membawa harga dan stok terkini: upload di hari export.

## Membaca
- **openpyxl gagal** pada export Shopee (`activePane` tidak valid). Pakai `scripts/xlsx_zip.py` (zip + XML).
- Jalankan `py -3 -I`; tidak ada pandas; tidak ada LibreOffice (rumus tidak bisa dihitung ulang).

## Menulis (mengubah sel) - edit XML mentah, jangan simpan ulang lewat library
Alasan: library menghilangkan validasi/proteksi/gaya template; upload bisa ditolak. Resep:
1. Buka zip, ambil `xl/worksheets/sheet1.xml` dan `xl/sharedStrings.xml`.
2. Pecah `<sheetData>`; ambil hanya baris header + baris yang berubah. **Tag `<row>` urutan atributnya bervariasi** (`<row r="7">` atau
   `<row customHeight ht r="7">`): cari dengan `\br="N"`.
3. Sel kosong bisa `<c r="F4318" s="3"></c>` (Shopee) atau `<c r="K7457" s="16" t="s"><v>135</v></c>` (TikTok, string kosong).
   Ganti dengan `<c r="F4318" s="3" t="inlineStr"><is><t>SKU</t></is></c>`; pertahankan atribut `s`.
4. Perbarui `<dimension ref=...>`; tulis zip baru dengan `ZipInfo` entri asli (semua file lain disalin apa adanya).
5. Baca ulang dengan `xlsx_zip.py` dan bandingkan sel per sel dengan file asli.
Contoh kerja: `Undercover-Repo\scripts\isi_sku_kosong_tiktok_sp.py` dan `isi_sku_kosong_shopee_op.py`.

## Urutan upload (TikTok)
Upload file `_ARCHIVE` (rename) **sebelum** file SKU untuk produk yang sama: file archive membawa SKU kosong untuk produk yang belum
diisi dan bisa menimpa SKU baru bila diupload belakangan. Setelah rename, produk bertanda "(Archive)" dihapus manual lewat UI marketplace.

## Baris data harus berurutan (wajib)
Marketplace memproses **0 baris** bila file mass-upload punya baris bolong. File yang hanya berisi sebagian produk harus direnumerasi: data berurutan
mulai baris data pertama (**Shopee 7, TikTok 6, Lazada 5**). Pakai `scripts/compact_rows.py <file> <jumlah_baris_header>` (Shopee 6, TikTok 5); skrip pengisi SKU
di repo memanggilnya otomatis. Ini sempat terlewat pada file SKU 11-12 Nov dan diperbaiki sebelum diupload.

## File hasil upload (`Result_shopee_mass_update_basic_info_*.xlsx`)
- Hanya memuat baris yang **gagal**; kolom E "Alasan Gagal". Baris yang berhasil tidak tercantum.
- Mass update basic info memproses **semua** baris file; produk yang namanya tidak berubah pun bisa gagal (alasan sama) - tidak perlu diulang.
- Alasan yang sudah terjadi: "Deskripsi produk mengandung karakter yang tidak valid [X]" (karakter `➤` U+27A4 dan `✔` U+2714 ada di deskripsi lama OP).
  Perbaikan: buat file ulang hanya untuk produk yang perlu berubah dan hapus karakter itu dari deskripsi (`scripts/shopee_retry_failed.py`).
- Sel hasil edit di file buatan skrip bisa berupa `inlineStr` (bukan shared string); pembaca kustom harus menangani keduanya.
