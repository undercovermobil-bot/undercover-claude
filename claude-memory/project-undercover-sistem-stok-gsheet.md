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
- Layout baru: STOK|IN|OUT per 16 warna (D..AY; STOK warna k = kolom 4+3k), Value AZ..BD (label dari header lama: UC Premium, STP Transparan), TOTAL STOK & MASUK/KELUAR HARI INI (SUMIFS ke "Log Stok") di bawah produk.
- Ketik IN/OUT + Enter → STOK berubah, sel dikosongkan, tercatat di **"Log Stok"**. OUT > stok ditolak. Edit langsung STOK = log `KOREKSI`. Nilai dibaca ulang setelah LockService → trigger ganda tidak dobel.
- Uji: 117/117 lulus; LibreOffice recalc: UC 1.161 unit & value identik; STP 246 unit, value beda hanya di baris yg formula lamanya salah.
- Rencana user: **trial dulu** — upload xlsx unduhan → Simpan sebagai Google Spreadsheet (mode Office tidak bisa Apps Script) → pasang & tes → kalau sesuai baru pasang di Google Sheet asli.

## PENTING untuk sub-proyek Stock Sync ([[project-undercover-stock-sync-status]])
Setelah user migrasi, Stock_Opname yang diunduh punya layout BARU: kolom IN lama (4+2k) TIDAK berlaku lagi. Stok warna k ada di kolom **4+3k** (mis. Abu-abu k=0 → D, Elite Abu k=5 → S, Epic Abu k=8 → AB, Warior Abu k=11 → AK). Cek dulu baris 3 (STOK/IN/OUT) sebelum membaca. Data lama ada di sheet "(lama)".

## Temuan data (dilaporkan ke user, belum dikonfirmasi)
UC: baris 40 & 41 formula Value Premium rusak (`=AF40*AM4441128`); 14 baris tanpa formula Value (50,58,68,69,70,82,83,94,118,140,190,191,192,194); 46 sel OUT masih terisi; baris 19 "Toyota Swift" (SKU SZK-SWF) kemungkinan typo.
STP: total lama cuma SUM s/d baris 104 → X-Over (Hijau Army 1), Soluna & C Class (Transparan 1+1) tidak ikut (246 vs 243). Baris 5,6,7,8,11 (Strip tanpa Elite Abu & Warior Abu) dan baris 10 (Innova merujuk L9) → **user minta diperbaiki: migrasi otomatis membuat ulang formula standar** (catatan 'DIPERBAIKI'). **Smartprotection tidak jual Exclusive** (user 2026-10-08) → `tanpaValue: ['Exclusive']`, tidak dilaporkan.

## Belum diverifikasi
- Trigger dari aplikasi Sheets HP (tidak ada pernyataan resmi Google) — user diminta tes.
- Status pemasangan di Sheet asli user: belum ada konfirmasi.
- File unduhan 2026-10-08: 11 sheet, 0 formula lintas sheet → sheet lain aman dibiarkan.
