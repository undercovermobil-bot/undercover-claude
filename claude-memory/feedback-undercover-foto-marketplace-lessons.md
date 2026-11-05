---
type: feedback
tags: [undercover, foto, shopee, lazada, tiktok, pelajaran]
updated: 2026-11-05
description: "Pelajaran dan jebakan saat mengganti foto produk lewat file mass update Shopee/Lazada/TikTok (hosting gambar, baris berurutan, batch, verifikasi isi)"
---

# Pelajaran: ganti foto lewat mass update marketplace

Konteks proyek: [[project-undercover-foto-smartprotection-marketplace]].

## Sebelum membuat link (folder foto)
- **Cek tulisan di gambar, bukan hanya nama file.** Di tiap gambar variasi ada caption seri + warna ("Elite Biru Benhur"); HOME memuat nama merek+model. Ketemu: label seri bergeser (Kijang, Panther: file "EPIC" sebenarnya Elite; Picanto: "ELITE" sebenarnya Warrior), HOME salah tulis ("Suzuki X-Trail" seharusnya Nissan, "Izuzu", "Taff GT" seharusnya Taft GT), foto warna tidak cocok caption (Triton Epic Merah berwarna biru).
- Cocokkan ejaan model dengan katalog marketplace ("Gran Max", "Taft GT", "Luxio"), dan cek **nama file ganda antar folder** (set APV 31–60 bentrok dengan set 1–30 padahal isinya beda).
- File kembar (hash sama) sengaja; hosting (Postimg, ibb) menggabungkannya jadi satu link, jadi jumlah link < jumlah file.

## Hosting gambar & penolakan
- **TikTok menolak sampul dari `i.ibb.co`** untuk 30/30 produk ("Tautan gambar ini gagal diproses… coba tautan lain"); Postimg diterima. Cadangan: `i.ibb.co.com` (isi sama persis; sudah diterima Shopee & Lazada pada Triton/Livina). Foto bersama dari CDN TikTok sendiri aman.
- Hosting gambar tanpa akun: Postimages (`postimages.org`) bisa diunggah lewat Claude in Chrome: `find` input file → `file_upload` (maks 10 MB per panggilan, jadi 15 gambar per batch) → halaman galeri memuat semua link `i.postimg.cc` (ambil dari atribut `src` gambar). Nama file dipertahankan (kecuali kejanggalan seperti "SWIFT" → "SW-IFT"). Dari jaringan ini `i.postimg.cc` sering tidak bisa dibuka (error page di Chrome), sehingga verifikasi piksel tidak bisa; Chrome juga memblokir pembacaan canvas lintas-origin.
- Mengunggah ulang file yang sama ke ibb mengembalikan link lama yang sama (deduplikasi), bukan link baru.
- **Lazada** menerima Postimg; 3 dari 20 sampul gagal sementara ("Fail to migrate third party CDN main images") dan berhasil setelah diunggah ulang. Hasil Lazada "Data no change in file" untuk produk lain = wajar.
- **Lazada varian**: gagal per produk, bukan per SKU. File hasil punya sheet `template` berisi SKU gagal dengan kolom "Keterangan Error"; pesan `thirdErrorCode 530 ... DOWNLOAD_RESOURCE_IO_EXCEPTION` menyebut gambar mana yang gagal diunduh (1–2 gambar per produk, ukuran file biasa, jadi sementara). Satu gambar gagal → semua SKU produk itu ditandai gagal. Unggah ulang hanya produk itu (baris berurutan dari baris 5).
- **Shopee**: unggah 20 produk sekaligus → 17 gagal ("server gagal upload beberapa foto"). Pecah jadi batch 4–6 produk.

## Struktur file
- **File dengan baris bolong → 0 diproses.** Kalau menyisakan sebagian produk, buat baris berurutan mulai dari baris data pertama (Shopee 7, Lazada 5, TikTok 6) dan nomor baris + referensi sel disesuaikan. Hasil Shopee sendiri berbentuk begitu.
- Perubahan SKU induk lewat mass update media diabaikan Shopee.
- Edit dengan **menambal XML langsung** (sharedStrings/inlineStr), jangan `openpyxl.save`: template Shopee/TikTok/Lazada punya proteksi, validasi, dan string bersama yang rusak/hilang. openpyxl gagal membuka Shopee/TikTok karena `activePane="bottom_left"` → buat salinan baca tanpa atribut itu.
- Kunci pencocokan: Product ID (Shopee/Lazada/TikTok) atau `sku.skuId` (Lazada varian), bukan nomor baris.

## Verifikasi isi gambar (jalan)
Shell tidak punya internet. Cara yang berhasil: server lokal `http.server` (127.0.0.1) + built-in browser; halaman memuat gambar dengan `crossOrigin='anonymous'` (cf.shopee, slatic, ibyteimg, postimg, ibb semua mengizinkan CORS), menggambar ke canvas 48×48, lalu membandingkan tiap foto di platform dengan file sumber (nilai terdekat dari semua kandidat). Cek 1.200+ gambar dalam ±1 menit; bedakan Epic/Elite/Warrior dari margin jarak. Pane browser kecil → screenshot tidak terbaca; pakai JS, bukan screenshot. WebFetch menyimpan gambar biner ke folder tool-results (berguna untuk contact sheet via System.Drawing).

- **Postimages: ambil "Direct link", bukan `src` gambar di galeri.** `src` di halaman galeri adalah thumbnail (ID lain, ±180×180, 7 KB) → TikTok menolak ("Panjang dan lebar gambar min. 300:300"). Di galeri pilih dropdown `embed_box` = `code_direct` ("Direct link"), lalu baca textarea kode (ID-nya beda dari thumbnail). Direct link ±94–107 KB, 800 px. TikTok juga menyalin gambar ke CDN-nya sehingga hasil galat memuat ID `tos-alisg-i-aphluv4xwc-sg/<id>`; gambar yang benar-benar diterima TikTok bisa dilihat di `https://p16-oec-sg.ibyteimg.com/tos-alisg-i-aphluv4xwc-sg/<id>~tplv-aphluv4xwc-origin-jpeg.jpeg`.
