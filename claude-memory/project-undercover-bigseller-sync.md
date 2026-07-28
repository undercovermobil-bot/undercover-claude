---
name: project-undercover-bigseller-sync
description: "Sub-proyek sync SKU listing (skema formula baru) ke SKU Gudang Big Seller — mulai 2026-07-28, keputusan user + jebakan teknis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9235e50b-3311-43ed-a15e-4665c26b7c5e
  modified: 2026-07-28T08:32:14.950Z
---

Sub-proyek **Sync SKU Gudang Big Seller**, mulai 2026-07-28. Beda dari [[project-undercover-sku-sync-status]] (yang menyamakan SKU antar listing) dan [[project-undercover-stock-sync-status]] (yang sync kuantitas): ini menyamakan **daftar SKU listing → SKU Gudang di Big Seller**.

## Lokasi & jenis file (verifikasi ulang tiap sesi, bisa pindah)

Input ada di `C:\Users\OWNER\Documents\Undercover\SKU Gudang Big Seller\` — **di luar repo git**, satu level di atasnya. Tiga jenis:
- **18 file listing** (`UA_Shopee_1.xlsx` dst) — sudah berisi SKU skema formula baru, hasil sesi cloud 07-27/28.
- **`SKU_Gudang…(1..7).xlsx`** = daftar SKU yang ADA di Big Seller (33.295 SKU). Menjawab "sudah ada / belum".
- **`SKU_Match…(28)(1..29).xlsx`** = **pemetaan** listing↔SKU gudang (86.915 baris; kolom `Nomor SKU Gudang`, `Marketplace`, `Nama Produk`, `ID Produk`, `SKU Toko`, `Variasi ID`). Menjawab "listing mana tertaut ke SKU gudang mana" + mendeteksi pemetaan yang akan putus.

## Jebakan teknis (jangan buang waktu mengulang)

- **`SKU_Gudang`/`SKU_Match` menyimpan dimension palsu `A1:A1`.** `load_workbook(read_only=True)` berhenti di baris 1 dan mengembalikan **0 baris tanpa error** — gejalanya diam, bukan exception. Baca file itu dengan `read_only=False`. File listing tidak kena.
- Bug `activePane="bottom_left"` pada export Shopee tetap berlaku — lihat [[project-undercover-sku-sync-status]].
- **Format SKU motor = `MEREK-MODEL-UA-KAT-MTR-WARNA`** — `MTR` ada di segmen **generasi** (ke-5), bukan segmen toko. Regex yang menganggap `MTR` di segmen ke-3 akan menghasilkan 0 motor secara diam-diam.
- Konvensi judul di Big Seller **tidak seragam**: 25.316 SKU `Model-Toko-Kategori-Warna-Gen`, 4.448 `Cover Mobil <model> <kat> <warna>`, 3.403 lain, 128 `Cover Motor …`.

## Keputusan user 2026-07-28 (jangan didesain ulang)

1. **Varian `_` Lazada** (9.322 SKU, mis. `…-ABU_G3`) → dipetakan ke **SKU gudang base**, tidak dibuatkan SKU gudang sendiri. Barangnya fisik sama; akhiran `_` cuma syarat keunikan Lazada. **User sudah membuat rules pemetaannya sendiri di Big Seller**, jadi tidak perlu impor pemetaan manual.
2. **Segmen OT/OP dikoreksi ke UA/SP** sebelum dibuat (aturan konsolidasi #1 & #3). Ternyata menurunkan "belum ada" dari 4.389 → 3.614: 775 SKU sebenarnya sudah ada begitu segmennya dikonsolidasi.
3. **SKU listing bermasalah dilewati**, tidak dibuatkan SKU gudang — hanya dilaporkan.
4. **SKU gudang yatim dibiarkan** di Big Seller (histori pesanan lama utuh), hanya didaftar.
5. **Judul mobil**: `Model-Toko-Kategori-Warna-Gen`. **Judul motor**: `Model-Toko-Kategori-Warna-Motor` — penanda `Motor` mengisi segmen generasi yang kosong supaya motor tetap terbedakan di inventory.

## Konteks penting dari user

**128 SKU motor `CM####` yang dibuat 2026-07-28 adalah tambalan dadakan**, bukan pilihan skema — dibuat karena sistem Big Seller mewajibkan ada SKU gudang supaya barang bisa keluar dari inventory. Skema yang benar tetap `MTR`. Jadi ke-128 itu masuk daftar yatim.

## Hasil batch pertama

Dari 16.303 SKU listing layak-gudang: **12.689 sudah ada (77,8%), 3.614 belum ada (22,2%)** — 1.829 mobil + 1.785 motor (seluruh SKU motor skema baru memang belum ada). Yatim 20.606. Output di `…\SKU Gudang Big Seller\Hasil Sync 2026-07-28\`: `Impor SKU Gudang Baru.xlsx` (template 40 kolom, hanya kolom Nomor SKU + Judul diisi) dan `Laporan Sinkronisasi SKU Gudang 2026-07-28.xlsx` (7 sheet).

**Urutan eksekusi yang disarankan ke user: impor SKU gudang dulu, baru upload listing ke marketplace.** 9.490 SKU Toko lama akan hilang saat listing di-upload → 33.332 baris pemetaan putus; kalau urutannya terbalik ada jendela waktu di mana pesanan masuk tanpa SKU gudang dan stok tidak terpotong.

## Sisa pekerjaan

- 9.616 baris SKU listing perlu dibenahi (7.007 placeholder angka Lazada, sisanya skema lama `CVR####` + 239 baris ber-SKU literal `"SKU"`).
- 14.412 baris listing masih tanpa SKU sama sekali.
- Typo `Warior` (seharusnya `Warrior`) di teks varian listing SP/OP — dinormalkan di judul, tapi **sumbernya di listing belum diperbaiki**.
