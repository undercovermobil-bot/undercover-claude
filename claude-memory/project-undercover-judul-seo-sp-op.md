---
name: project-undercover-judul-seo-sp-op
description: "Formula judul SEO final Smartprotection/Otoprotection (Signature/Transparan), alasan pemilihan kata, dan status penerapan"
metadata:
  node_type: memory
  type: project
---

**Formula (diskusi SEO 2026-09)**, satu judul SAMA untuk Shopee & TikTok. Versi 1 (file SP 29 Sep pertama): `Body Cover Mobil {Model} Signature Waterproof - {Toko} - Selimut Sarung Mobil`. **Revisi 2026-09-29 (usulan, default script, menunggu pilihan user)**:
```
Cover Mobil {Model} Signature Waterproof - {Toko} - Body Cover Selimut Sarung Mobil
Cover Mobil {Model} Transparan Anti Air - {Toko} - Body Cover Selimut Sarung Mobil
```
**KOREKSI klaim lama "±80 karakter tampil di HP / brand terlihat"**: itu SALAH untuk kartu hasil pencarian. Simulasi render Chromium (Roboto, kartu 2 kolom, 2 baris): HP 360dp Shopee ±48 karakter (39–53), TikTok ±44, HP 412dp/desktop ±56. Nama toko TIDAK PERNAH terlihat di kartu pencarian (0/482 judul, pola apa pun), hanya di halaman detail. Sumber web (Everpro) juga menyebut 40–50 karakter di HP. Dengan "Body " di depan, di HP 360dp model terpotong di 18 (Shopee)/28 (TikTok) judul & kata tipe hilang di 101/179 judul; pola "Cover Mobil" depan = model utuh 482/482. "Body Cover" dipindah ke ekor -> pencarian "body cover mobil {model}" tetap cocok (token lengkap + frasa "body cover" utuh). Volume "cover mobil" vs "body cover mobil" TIDAK terverifikasi (Shopee/Google suggest diblokir proxy); keduanya terbukti istilah pencarian nyata (Tokopedia /find/cover-mobil & /find/body-cover-mobil-{avanza,innova,agya,ertiga}, Shopee /list/Cover/Mobil & /list/Body/Cover/Mobil).
Script: `scripts/optimasi_judul_sp_op.py <Toko> <out> <shopee_basic> <tiktok_basic> [cover|body]` (template Shopee "mass_update_basic_info", TikTok "basic_information").

- **"Signature"** = nama lini non-Transparan (setara "Reguler"). Yang GUGUR: Classic (usulan awal, diganti), Prime & Deluxe (= nama tier CoverSuper, kompetitor besar), Premium (tabrakan dgn tier UA), Elite (kosakata strip internal), Parasut (penanda grade termurah), Standar (kesan murah). Kata tier tidak punya volume pencarian; kriterianya "tidak membawa risiko".
- **Aturan panjang**: Shopee maks 120 (resmi); kartu pencarian cuma ±40–55 karakter (lihat koreksi di atas) -> model + tipe harus di depan; TikTok tidak menghukum panjang, tapi menghukum PENGULANGAN kata. Bagian elegan (s/d nama toko) harus selesai sebelum ±80; ekor "Selimut Sarung Mobil" = ruang kata kunci. Pemisah selalu ` - ` (spasi), bukan `-` nempel. Dilarang: kata promosi, harga, HURUF BESAR SEMUA.
- **Klaim terverifikasi dari deskripsi SP**: non-Transparan "kain waterproof Taffeta import Korea" (deskripsi juga bilang "anti air hingga 70%"), Transparan "PE tebal / LDPE 80 micron, full waterproof".
- Hasil SP 29 Sep: 482 Shopee + 474 TikTok, panjang 83–104, toko selesai di karakter 60–81 (hanya 4 judul Gran Max Signature di 81). 42 judul dibetulkan nama modelnya, termasuk SALAH MEREK yang diverifikasi lewat SKU: "Honda Fortuner"→Toyota (TYT-FTN), "Mitsubishi Lantis"→Mazda, "Mitsubishi Pajero"→Pajero Sport (MTB-PJS, Gen 1-3 1996-2026), "Kia Sedona / Carnival"→Kia Sedona.
- Deskripsi SP BELUM dioptimasi (usulan struktur plain text + emoji bullet ada di diskusi; Shopee kemungkinan tidak mendukung bold/bullet).
- **OP belum diterapkan** — pakai script yang sama dengan Toko=Otoprotection begitu user kirim export basic info OP.

Why: user minta judul elegan (tidak "semua value produk ditaruh di judul") tapi tetap SEO, dan disamakan Shopee–TikTok.

How to apply: jangan usulkan ulang Classic/Prime/Deluxe; kalau ada model baru, cek ejaan ke katalog UA & SKU sebelum masuk judul. Saran awal (belum dijalankan user): uji 20–30 produk trafik tertinggi dulu 2–3 minggu sebelum massal — tidak ada data kata kunci asli (iklan SP/UA semua mode otomatis).
