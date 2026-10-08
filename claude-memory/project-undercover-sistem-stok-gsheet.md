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

## Solusi yang dibuat (2026-10-08)
`sistem-stok-gsheet/Kode.gs` + `PANDUAN.md` + `uji/` (mock SpreadsheetApp Node).
- Formula murni tidak bisa (STOK=STOK+IN melingkar) → **Apps Script, trigger installable onEdit** `prosesInputStok` (sengaja BUKAN `onEdit` supaya tidak dobel).
- Menu "📦 Sistem Stok": 1) migrasi → sheet baru **"Stok UC Sistem"** (STOK|IN|OUT per 16 warna, D..AY; Value AZ..BD; TOTAL STOK baris 198; MASUK/KELUAR HARI INI baris 199 via SUMIFS ke Log) — sheet lama tidak diubah; 2) pasang trigger; 3) kunci kolom STOK (hanya IN/OUT bebas).
- Ketik IN/OUT + Enter → STOK berubah, sel dikosongkan, baris masuk sheet **"Log Stok"**. OUT > stok ditolak (sel merah + note). Edit langsung STOK = log `KOREKSI`.
- Nilai dibaca ulang setelah LockService → trigger ganda tidak menghitung dobel.
- Uji: 82/82 lulus di mock; formula hasil migrasi dihitung ulang LibreOffice, total unit 1.161 & value per baris identik dgn sheet lama.

## Temuan data (dilaporkan ke user, belum dikonfirmasi)
- Baris 40 & 41 formula Value Premium rusak (`=AF40*AM4441128`).
- 14 baris tanpa formula Value: 50,58,68,69,70,82,83,94,118,140,190,191,192,194.
- File unduhan punya 46 sel OUT masih terisi → migrasi sebaiknya akhir hari.
- Baris 19 "Toyota Swift" (SKU SZK-SWF) kemungkinan typo "Suzuki Swift".

## Belum diverifikasi
- Trigger dari aplikasi Sheets HP (tidak ada pernyataan resmi Google) — user diminta tes.
- Status pemasangan di Sheet asli user: belum ada konfirmasi.
- Sheet "Stok Cover STP" belum dibuat sistemnya (struktur sama, tinggal tambah entri KONFIG.SISTEM).
