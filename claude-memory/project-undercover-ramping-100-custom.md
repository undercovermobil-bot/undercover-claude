---
name: project-undercover-ramping-100-custom
description: "Perampingan katalog UA (2026-09): hanya 100 model terlaris punya link fix, sisanya diarsip + 3 link custom per ukuran (Subcompact..Jumbo)"
metadata:
  node_type: memory
  type: project
---

**Rencana user (2026-09)**: toko Undercover Autocare (UA) dirampingkan. Hanya **100 model terlaris** yang tetap punya link fix (acuan: `Daftar_100_Produk_Terlaris_Undercover.docx`, penjualan 1 Apr–16 Sep 2026 gabungan 4 toko, dievaluasi ulang tiap kuartal). Model lain dilayani lewat **3 link custom** "Body Cover Mobil {Reguler|Premium|Exclusive} Custom Semua Merek ...", varian ukuran **Subcompact / Compact / Midsize / Large / Jumbo** (= Pcs/Roll 7/6/5/4/3).

- **Harga custom (rumus, sudah live di Shopee 26 Sep)**: Reguler 301/337/387/462/583rb; Strip +43rb; Premium = Reguler+414rb; Exclusive = Premium+400rb.
- **SKU custom**: `CST-{SBC|CMP|MID|LRG|JMB}-UA-{R|S|P|E}-G1-{WARNA}` (85 SKU: Reguler 70 = 5 polos + 9 strip × 5 ukuran; Premium 10 ABU/SLV; Exclusive 5 ABU). Per 26 Sep kolom SKU di Shopee masih kosong, belum diupload.
- **Tanda arsip (2026-09-26)**: listing di luar 100 diberi akhiran nama **" [Archived]"** (di BELAKANG, pilihan user) lewat `scripts/arsipkan_produk_undercover.py`. Hasil: Shopee 891, TikTok 883, Lazada 853 produk. Keputusan user: HANYA cover mobil (cover motor/cairan/karpet/tas/bahan kain/Logo Custom tidak disentuh); model mirip beda cover (Feroza Long, Vitara Brezza, Civic Type R, Yaris Cross, Corolla Cross, Avega Hatchback, MINI Hatch, Datsun GO Plus) ikut diarsip; listing ganda model yang ada di daftar diarsip (TikTok: yang lebih baru). Twin model (Avanza/Xenia/Veloz dst.) tetap listing terpisah, semua dipertahankan.
- Honda Civic Sedan Premium (No.18) sempat tidak ada di TikTok UA; user sudah listing ulang (2026-09-28).
- **Verifikasi ulang 2026-09-28** (diminta user): (1) teks 100 nomor di docx dibaca ulang per sel = daftar di script, 0 beda; (2) cek silang pakai prefix SKU (Shopee 1.188 + TikTok 1.178 produk cover mobil) cocok semua, beda hanya 4 listing ganda yang memang sengaja diarsip; 57 listing tanpa SKU valid semuanya model di luar daftar; (3) Lazada (tanpa SKU) keputusannya sama persis dgn Shopee per model+tipe; (4) isi 3 file upload = persis daftar arsip. Model mirip yg diarsip: Feroza Long, Gran Max (tanpa label), Datsun GO Plus, Avega Hatchback, Grand Livina Custom Roofbox, **Nissan Terra (beda dari Terrano)**, Vitara Brezza, Corolla Cross, Yaris Cross.

Why: user khawatir pembeli tidak baca deskripsi → kanibalisasi link fix vs custom; usulan turunkan harga 29 link fix Premium/Exclusive ke level custom masih menunggu keputusan user.

How to apply: pertanyaan "produk X masih aktif/tidak" → cek daftar 100 dulu; jangan tambah link fix baru untuk model di luar daftar tanpa instruksi.
