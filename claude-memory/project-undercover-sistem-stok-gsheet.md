---
name: project-undercover-sistem-stok-gsheet
description: "Sub-proyek (mulai 2026-10-08) — sistem pencatatan stok otomatis STOK|IN|OUT di Google Sheet Stock Opname via Apps Script, kode di repo sistem-stok-gsheet/"
metadata:
  node_type: memory
  type: project
---

Beda dari [[project-undercover-stock-sync-status]] (sync angka stok ke listing marketplace). Ini soal **cara staf mencatat stok** di Google Sheet "Stock Opname" itu sendiri.

## Masalah awal (dari user)
Sheet "Stok Cover UC": tiap warna 2 kolom IN/OUT. **IN = stok tersedia** (diedit manual saat barang masuk). OUT ditulis saat barang keluar, lalu IN dikurangi manual, OUT dihapus akhir hari → rawan human error. Produk baris 4–196 (193 produk), total di 198–199. Section reseller ASTA mulai baris 201 (di luar scope).

## Solusi yang dibuat (2026-10-08, revisi sama hari)
`sistem-stok-gsheet/Kode.gs` + `PANDUAN.md` + `uji/` (mock SpreadsheetApp Node, fixture dari `uji/ekstrak.py`, tidak di-commit).
- Formula murni tidak bisa (STOK=STOK+IN melingkar) → **Apps Script, trigger installable onEdit** `prosesInputStok` (sengaja BUKAN `onEdit` supaya tidak dobel).
- **Berlaku untuk "Stok Cover UC" (produk 4–196) dan "Stok Cover STP" (produk 4–107, 104 produk).** Batas baris dideteksi otomatis (baris sebelum label OUT/IN di kolom B).
- Migrasi (menu 1a/1b): sheet lama di-rename jadi **"Stok Cover UC (lama)" / "Stok Cover STP (lama)"** (isi utuh, termasuk reseller ASTA/ROBY baris 201+), sheet baru memakai **nama asli** di posisi tab yang sama — permintaan user: tetap pakai nama "Stok Cover UC/STP". Rollback otomatis kalau error.
- **STP + warna Orange** (user 2026-10-08): Orange = Reguler ke-6 SP (SKU -R-…-ORG), disisip setelah Hijau Army saat migrasi via `warnaTambahan`, stok awal 0, value harga Reguler. STP jadi 17 warna: Orange = kolom S (19), Elite Abu bergeser ke V (22), Value mulai BC (55). Tambah warna SETELAH sheet aktif belum didukung.
- Layout baru UC: STOK|IN|OUT per 16 warna (D..AY; STOK warna k = kolom 4+3k), Value AZ..BD (label dari header lama: UC Premium, STP Transparan), TOTAL STOK & MASUK/KELUAR HARI INI (SUMIFS ke "Log Stok") di bawah produk.
- Ketik IN/OUT + Enter → STOK berubah, sel dikosongkan, tercatat di **"Log Stok"**. OUT > stok ditolak. Edit langsung STOK = log `KOREKSI`. Nilai dibaca ulang setelah LockService → trigger ganda tidak dobel.
- Uji: 117/117 lulus; LibreOffice recalc: UC 1.161 unit & value identik; STP 246 unit, value beda hanya di baris yg formula lamanya salah.
- Rencana user: **trial dulu** — upload xlsx unduhan → Simpan sebagai Google Spreadsheet (mode Office tidak bisa Apps Script) → pasang & tes → kalau sesuai baru pasang di Google Sheet asli.

- **Warna (user 2026-10-08)**: header + kolom STOK diwarnai per warna cover seperti sheet asli (abu #999999, hitam, biru #0000FF, merah #FF0000, hijau #38761D, orange #FF9900, Premium/Transparan/Exclusive abu muda); IN/OUT tanpa warna; nama produk & SKU tanpa warna (user tambah sendiri). `KONFIG.PALET` cocok by kata di nama warna.
- **Zona waktu**: bug nyata di trial user — jam Log tampil 21:12 padahal 11:12 WIB = file berzona Pacific (UTC-7, hasil konversi xlsx). Fix: jam Log ditulis sbg serial number WIB (`waktuSerial_`, Utilities.formatDate 'Asia/Jakarta') + migrasi set `setSpreadsheetTimeZone('Asia/Jakarta')` (disebut di dialog) + menu "Setel zona waktu file ke WIB". Rekap harian (SUMIFS ke TODAY()) bergantung zona waktu file.
- Jelaskan ke user "Kunci kolom STOK" (menu 3): staf hanya isi IN/OUT; STOK/Log/Total/Value terkunci; trigger jalan sbg pemilik; opsional.

- **Review independen (workflow 3 lensa + 2 skeptis, 2026-10-08)**: 22 kandidat → 9 terbukti, diperbaiki: (1) rekap TODAY() vs jam WIB di file zona Pacific → zona dipaksa WIB saat input diproses & saat aktifkan trigger; (2) sel IN/OUT kena format tanggal ("1/2") → `MAKS_QTY` 9999 di validasi & handler + setNumberFormat('0'); (3) ketikan susulan di sel sama terhapus → sel dicek ulang sebelum clearContent (batch, 1 getValues); (4/7) produk baru di bawah baris kosong tak masuk SUM → SUM sampai baris kosong, panduan: Insert row ABOVE baris kosong; (6) tryLock gagal → STOK ditandai 'belum tercatat'; (8) data lama dibaca ulang setelah dialog Yes; (9) `warnaTambahan` berantai (Silver setelah Orange). Ditolak skeptis: 13 (mis. e.oldValue undefined, atomicity paste besar).

- **Log per sheet & tampilan (user 2026-10-08)**: log dipisah — `Log Stok UC` / `Log Stok STP` (`cfg.log`); mutasi terbaru di baris 2 (`insertRowsBefore(2,n)` + clearFormat + format waktu); rekap harian per sheet tanpa kriteria kolom Sheet; menu 'Arsipkan log bulan lalu' (opsional) → sheet 'Arsip <log> <yyyy-MM>' terbaru di atas, Log sisakan bulan ini; kolom Waktu berformat tanggal → `getValues` mengembalikan Date → `waktuNomor_` normalkan. Filter manual aman (anjurkan **Filter views**, bukan Sort sheet). STOK 0 tampil kosong via `FORMAT_STOK '0;-0;;@'` (nilai tetap 0; baris TOTAL tetap tampil). Sheet 'Log Stok' lama (versi bersama) diabaikan, user hapus manual.

- **Review ke-2 (log/arsip, 16 kandidat → 9 terbukti, semua diperbaiki; workflow pertama gagal krn session limit, diulang)**: arsip tidak idempoten & gagal tengah jalan → `arsipkanLogBulanLalu` kini: rencana dibaca ulang setelah lock, cek `bisaEdit_` (canEdit proteksi) sebelum menulis, dedupe multiset (`kunciBaris_`), hapus hanya baris terarsip via `deleteRows` per grup bawah→atas (tidak rewrite Log), try/catch 'Aman diulang', waktu teks di arsip dipertahankan; `tulisLog_` sisip di baris 3 + `copyTo` baris 2 ke bawah (rentang staf berawal baris 2 ikut melebar; jam tidak dikonversi ulang) + batch dibalik (diproses terakhir di atas); `cekStatus` memperingatkan rekap yang masih merujuk log lama; PANDUAN bagian 'Memasang versi kode baru' (migrasi ulang hanya utk file trial). Uji 189 lulus.

## PENTING untuk sub-proyek Stock Sync ([[project-undercover-stock-sync-status]])
Setelah user migrasi, Stock_Opname yang diunduh punya layout BARU: kolom IN lama (4+2k) TIDAK berlaku lagi. Stok warna k ada di kolom **4+3k** (UC: Abu-abu k=0 → D, Elite Abu k=5 → S, Epic Abu k=8 → AB, Warior Abu k=11 → AK). **STP beda: ada Orange di k=5 (S), warna Strip bergeser +3 kolom.** Selalu baca nama warna baris 2 + label baris 3 (STOK/IN/OUT) sebelum membaca. Data lama ada di sheet "(lama)".

## Temuan data (dilaporkan ke user, belum dikonfirmasi)
UC: baris 40 & 41 formula Value Premium rusak (`=AF40*AM4441128`); 14 baris tanpa formula Value (50,58,68,69,70,82,83,94,118,140,190,191,192,194); 46 sel OUT masih terisi; baris 19 "Toyota Swift" (SKU SZK-SWF) kemungkinan typo.
STP: total lama cuma SUM s/d baris 104 → X-Over (Hijau Army 1), Soluna & C Class (Transparan 1+1) tidak ikut (246 vs 243). Baris 5,6,7,8,11 (Strip tanpa Elite Abu & Warior Abu) dan baris 10 (Innova merujuk L9) → **user minta diperbaiki: migrasi otomatis membuat ulang formula standar** (catatan 'DIPERBAIKI'). **Smartprotection tidak jual Exclusive** (user 2026-10-08) → `tanpaValue: ['Exclusive']`, tidak dilaporkan.

## Belum diverifikasi
- Trigger dari aplikasi Sheets HP (tidak ada pernyataan resmi Google) — user diminta tes.
- Status pemasangan di Sheet asli user: belum ada konfirmasi.
- File unduhan 2026-10-08: 11 sheet, 0 formula lintas sheet → sheet lain aman dibiarkan.
