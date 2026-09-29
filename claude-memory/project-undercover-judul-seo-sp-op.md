---
name: project-undercover-judul-seo-sp-op
description: "Formula judul SEO final Smartprotection/Otoprotection (Signature/Transparan), alasan pemilihan kata, dan status penerapan"
metadata:
  node_type: memory
  type: project
---

**Formula final (diskusi SEO 2026-09, diterapkan SP 2026-09-29)**, satu judul SAMA untuk Shopee & TikTok:
```
Body Cover Mobil {Model} Signature Waterproof - {Toko} - Selimut Sarung Mobil
Body Cover Mobil {Model} Transparan Anti Air - {Toko} - Selimut Sarung Mobil
```
Script: `scripts/optimasi_judul_sp_op.py <Toko> <out> <shopee_basic> <tiktok_basic>` (template Shopee "mass_update_basic_info", TikTok "basic_information").

- **"Signature"** = nama lini non-Transparan (setara "Reguler"). Yang GUGUR: Classic (usulan awal, diganti), Prime & Deluxe (= nama tier CoverSuper, kompetitor besar), Premium (tabrakan dgn tier UA), Elite (kosakata strip internal), Parasut (penanda grade termurah), Standar (kesan murah). Kata tier tidak punya volume pencarian; kriterianya "tidak membawa risiko".
- **Aturan panjang**: Shopee maks 120 (resmi); tampil di HP ±80 karakter pertama; TikTok tidak menghukum panjang, tapi menghukum PENGULANGAN kata. Bagian elegan (s/d nama toko) harus selesai sebelum ±80; ekor "Selimut Sarung Mobil" = ruang kata kunci. Pemisah selalu ` - ` (spasi), bukan `-` nempel. Dilarang: kata promosi, harga, HURUF BESAR SEMUA.
- **Klaim terverifikasi dari deskripsi SP**: non-Transparan "kain waterproof Taffeta import Korea" (deskripsi juga bilang "anti air hingga 70%"), Transparan "PE tebal / LDPE 80 micron, full waterproof".
- Hasil SP 29 Sep: 482 Shopee + 474 TikTok, panjang 83–104, toko selesai di karakter 60–81 (hanya 4 judul Gran Max Signature di 81). 42 judul dibetulkan nama modelnya, termasuk SALAH MEREK yang diverifikasi lewat SKU: "Honda Fortuner"→Toyota (TYT-FTN), "Mitsubishi Lantis"→Mazda, "Mitsubishi Pajero"→Pajero Sport (MTB-PJS, Gen 1-3 1996-2026), "Kia Sedona / Carnival"→Kia Sedona.
- Deskripsi SP BELUM dioptimasi (usulan struktur plain text + emoji bullet ada di diskusi; Shopee kemungkinan tidak mendukung bold/bullet).
- **OP belum diterapkan** — pakai script yang sama dengan Toko=Otoprotection begitu user kirim export basic info OP.

Why: user minta judul elegan (tidak "semua value produk ditaruh di judul") tapi tetap SEO, dan disamakan Shopee–TikTok.

How to apply: jangan usulkan ulang Classic/Prime/Deluxe; kalau ada model baru, cek ejaan ke katalog UA & SKU sebelum masuk judul. Saran awal (belum dijalankan user): uji 20–30 produk trafik tertinggi dulu 2–3 minggu sebelum massal — tidak ada data kata kunci asli (iklan SP/UA semua mode otomatis).
