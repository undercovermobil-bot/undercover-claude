---
type: project
tags: [stok, opname, bigseller, operasional]
updated: 2026-11-18
description: "Audit 2026-11-18 selisih stok sheet Stock Opname vs BigSeller vs gudang: akar masalah (stok masuk ditimpa manual, jam/hari input beda, stok awal BigSeller tak pernah diopname) + usulan SOP"
---

# Diskrepansi stok: sheet Stock Opname vs BigSeller vs gudang

Masalah user (2026-11-18): stok di [Stock Opname](https://docs.google.com/spreadsheets/d/1O-AHnVK62suXiBPREqSkKzBfQMNe6kw1_JC6l__rFz8/edit#gid=606163079), BigSeller (Pergudangan > Rincian Stok) dan fisik gudang sering beda, bahkan sebelum ada BigSeller (opname tiap Sabtu tetap menyisakan selisih).
Sistem sheet: [[project-undercover-sistem-stok-gsheet]]. Sync ke listing: [[project-undercover-stock-sync-status]].

## Data yang dibaca (read-only)
- Sheet: `Log Stok UC` 4.661 baris (23 Okt–18 Nov 2026), `Rekap Harian UC/STP`, `Stok Cover UC` (snapshot 18 Nov pagi).
- BigSeller: riwayat mutasi stok `POST /api/v1/inventory/inout/record/pageList.json` (8.600 mutasi sejak 1 Okt), lihat [[bigseller-pull-snippets]].
- Perbandingan Undercover **Reguler** (SKU `-UA-R-`), 24 Okt–17 Nov.

## Temuan (angka)
| # | Temuan | Bukti |
|---|---|---|
| 1 | **OUT sudah cocok**, bukan sumber utama | OUT sheet 2.037 vs penjualan BigSeller 2.086 unit untuk SKU yang sama (98%). Brio Abu 161/151, Avanza Abu 114/114, Jazz Abu 64/64 |
| 2 | **Kolom IN sudah tidak ada**; stok masuk dicatat dengan **mengetik ulang angka STOK** | Layout sheet sekarang STOK \| OUT \| OUT HARI INI. Masuk (IN) = 0 tiap hari sejak 24 Okt; 2.567 entri KOREKSI. Restock tiap hari kerja ±70–200 unit, jam 13–15 |
| 3 | Timpa angka = salah hitung lalu dibatalkan | 4 Nov 13:10 Brio Abu 15→30, 13:14 30→15, 13:20 15→20. Koreksi minus total −328 unit, kebanyakan kelipatan 5/10 (pembatalan input restock, bukan barang hilang) |
| 4 | **Barang masuk dicatat walau fisiknya tidak ada / salah tempat** | CRV (4 warna) & Swift: +5 di BigSeller 13 Nov 13.00 dan di sheet 13 Nov 15:36; opname Sabtu 14 Nov sheet −5 semua warna; BigSeller **tidak** dikoreksi |
| 5 | **Jam & hari input beda** antara dua sistem | Scan masuk BigSeller pagi (08–11) dan siang (13–16); sheet sore (13–15) dalam batch. Brio Abu: sheet +13 tgl 14 Nov, BigSeller scan +10 baru 18 Nov 09.00. Ertiga Abu: BigSeller scan 10 unit Minggu 25 Okt & 10 unit Minggu 1 Nov; sheet tidak pernah diisi hari Minggu → masuk BigSeller 50 vs sheet 30 |
| 6 | **Stok awal BigSeller tidak pernah diopname** | Snapshot 18 Nov: dari 412 SKU-warna Reguler yang bisa dibandingkan hanya 104 (25%) sama; total sheet 1.293 vs BigSeller 2.485. Fast mover cocok, slow mover BigSeller lebih tinggi (mis. Alphard Biru 4 vs 11, Pajero Biru 5 vs 10). 20 SKU-warna masih placeholder ±100 (Civic semua generasi, Kijang LGX 187–199). Total stok BigSeller 271.636 unit |
| 7 | Opname hanya mengoreksi sheet; BigSeller dikoreksi belakangan lewat Pengurangan Manual besar | Fitur **Penghitungan Stok BigSeller tidak pernah dipakai** (0 transaksi). Pengurangan manual 28 Okt 1.754 unit, 9 Nov 1.309 unit (bersih-bersih placeholder, mis. Yaris Hitam 319) |
| 8 | Satu akun untuk semua orang | Semua entri sheet dari satu akun Google, semua mutasi BigSeller dari satu akun → tidak bisa tahu siapa yang salah input |
| 9 | Retur tidak punya jalur di sheet | BigSeller "Hasil Retur" 79 unit Reguler UA; sheet `Riwayat Return` terakhir diisi Okt 2024; retur masuk sheet lewat koreksi tanpa keterangan |
| 10 | STP & Strip hampir tidak dicatat di sheet | Sejak 24 Okt BigSeller: penjualan Smartprotection 267 unit, Strip UA 519 unit; Log STP hanya ±5 entri, OUT Strip di sheet ±30. **Tanya user**: memang dibuat per pesanan (tidak distok)? |
| 11 | Penyapuan otomatis 31% OUT (651 entri) | Tidak terbukti dobel: OUT per SKU cocok dengan BigSeller. Aman |

## Akar masalah (kesimpulan)
Dua pencatatan **manual paralel** tanpa titik rekonsiliasi: BigSeller (scan, pagi) dan sheet (ketik angka akhir, sore). Selisih muncul dari **stok masuk**, bukan stok keluar: (a) angka STOK ditimpa manual sehingga salah hitung, (b) jam/hari input berbeda (termasuk Minggu), (c) barang dicatat masuk sebelum dipastikan fisiknya ada di rak, (d) opname Sabtu hanya mengoreksi sheet, BigSeller tidak, (e) stok awal BigSeller slow mover tidak pernah dihitung. Jam scan seragam membantu (selisih karena jeda hilang), tapi **tidak cukup** sendirian.

## Usulan SOP (disampaikan ke user 2026-11-18, belum diputuskan)
1. **Satu sumber kebenaran: BigSeller** (OUT otomatis dari pesanan, sudah 98% cocok). Sheet jadi alat bantu & lembar opname; setelah 2–3 Sabtu cocok, input OUT manual di sheet bisa dihentikan.
2. **Barang masuk = satu momen, satu dokumen**: hitung fisik → taruh di rak → scan BigSeller (Penambahan Stok Manual, catatan = no. surat jalan/batch jahit) → sheet diisi **jumlah tambahan** (kembalikan kolom IN; jangan ketik angka STOK baru) oleh orang yang sama, saat itu juga.
3. **Jam penerimaan tetap** (usul 2 slot, mis. 10.00 dan 15.00). Di luar slot / hari Minggu: barang ditahan di area "belum masuk", tidak di-scan.
4. **Kunci kolom STOK** (menu 3 sistem stok): koreksi angka STOK hanya admin, hanya saat opname, wajib alasan.
5. **Opname Sabtu**: setelah semua pesanan dikirim, sebelum barang masuk baru; freeze scan selama hitung; koreksi **kedua** sistem; BigSeller lewat **Penghitungan Stok** supaya selisih tercatat; catat alasan per selisih (salah warna, salah rak, retur, rusak).
6. **Retur**: BigSeller "Hasil Retur" + sheet IN keterangan retur, di hari barang diterima.
7. **Akun per orang** (sub-akun BigSeller, akun Google sendiri di sheet) supaya log menunjukkan siapa.
8. **Opname awal penuh** slow mover (±300 SKU-warna yang tidak cocok) + nolkan 20 placeholder ±100 di BigSeller.
9. **Laporan selisih harian otomatis** sheet vs BigSeller per SKU (Claude bisa membuat, BigSeller tetap read-only).

## Jawaban user (2026-11-18)
- **Strip dijahit per pesanan**; masuk stok hanya kalau ada retur/kelebihan jahit (jarang). Temuan #10 untuk Strip bukan masalah.
- **Cakupan sinkron hanya 20 produk baris kuning** di Stok Cover UC (baris 4–23, 5 warna Reguler = 100 sel stok). Baris lain dan STP memang belum disinkronkan → temuan #6 (25% cocok, slow mover) di luar cakupan untuk sekarang.
- Peran: **Nabila** = admin pengisi Google Sheet; **Doni** = admin stok/inventory (scan BigSeller); **Candra** (user) = pengecek, termasuk BigSeller. Selama ini kalau beda, Candra **menyamakan BigSeller mengikuti sheet** → kesalahan sheet ikut terbawa ke BigSeller; usulan: hitung fisik dulu (aturan D).
- Banner baris 1 sheet sekarang: "Stok masuk: ketik jumlah stok".

## SOP versi tim
Halaman untuk tim (artifact privat, perlu di-share user): [Alur Stok Gudang](https://claude.ai/artifact/XBCYASvpNhwaCtkiepxX71). Isi: 4 aturan (scan hanya barang yang dipegang — Doni scan sambil tempel barcode, scan = hitung, SEBELUM masuk rak (koreksi user 2026-11-18), lalu cocokkan dengan nota jahit; catat jumlah masuk bukan total; scan & sheet di jam sama dari satu Lembar Barang Masuk; beda → hitung fisik dulu), peran Doni/Nabila/Candra, jadwal (masuk 10.00 & 15.00, cek 16.30, Minggu tidak scan), opname Sabtu 6 langkah (koreksi dua sisi, BigSeller lewat Penghitungan Stok), tabel penyebab selisih.

## Catatan teknis kolom IN
`bacaPeta_` di `Kode.gs` memetakan kolom lewat label baris 3: kolom berlabel `IN`/`OUT` maksimal 2 kolom setelah `STOK`. Layout sekarang STOK | OUT | OUT HARI INI → menyisipkan kolom `IN` tepat setelah STOK (STOK | IN | OUT | OUT HARI INI) seharusnya dikenali lagi tanpa migrasi ulang. **Belum diuji**; validasi (`c+1 IN, c+2 OUT`, baris ±1719) dan rumus OUT HARI INI perlu dicek di salinan file dulu.

## Laporan selisih harian
User (2026-11-18): tarik BigSeller lewat fetch di Chrome profil Undercover (yang login BigSeller). Dibuat halaman dashboard privat **[Cek Selisih Stok Harian](https://claude.ai/artifact/1RXNrcq9SnQVKdquuBdBnD)** (tipe Data; data = file JSON upload, tidak mengubah sheet/BigSeller).
- Cara tarik: sheet `Stok Cover UC` A4:R23 kolom STOK D/G/J/M/P (ABU/HTM/BRU/MRH/GRN) via JSONP gviz; BigSeller = `newOnhand` mutasi terakhir per SKU dari `inout/record/pageList.json` (19 halaman × 200 cukup untuk 100 SKU); log sheet `Log Stok UC` gid 784311928. Detail di [[bigseller-pull-snippets]].
- **Hasil pertama 18 Nov ±12.50**: 87/100 cocok, 13 beda, semuanya BigSeller lebih tinggi, total +37 unit (Ayla Abu 10/21, CRV Abu 6/11, Mobilio Abu 5/9 & Hitam 4/8, CRV Hitam 5/8, HRV Hitam 10/12, Ayla Hijau 5/7, sisanya ±1). Mobilio Abu/Hitam & Ayla Hijau = persis scan pagi ini yang belum diisi sheet.
- Pagi 18 Nov banyak Penambahan/Pengurangan Manual di BigSeller yang membuat sel sama dengan sheet (mis. BRV Hitam +12, Zenix Abu −8, Swift/CRV −5 = temuan #4 sudah dikoreksi). Karena satu akun, scan barang masuk dan penyamaan ke sheet tidak bisa dibedakan → alasan tambahan untuk akun per orang / catatan wajib di Penambahan Stok.
- Belum otomatis: tugas terjadwal 16.30 belum dibuat (perlu izin user; komputer + Chrome profil BigSeller harus menyala).
