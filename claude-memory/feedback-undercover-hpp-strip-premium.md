---
name: feedback-undercover-hpp-strip-premium
description: "HPP variasi strip (Elite/Epic/Warior) = HPP warna dasar + Rp20.000 (Alphard +26.000, HiAce +31.000), pakai sheet STRIP 1; jangan menganggap premium punya HPP sama dengan warna dasar"
type: feedback
tags: [hpp, margin, strip, premium, shopee, campaign]
updated: 2026-11-19
---

# HPP strip tidak sama dengan warna dasar

**Aturan:** variasi Elite/Epic/Warior (Strip 1/2/3) selalu dihitung dengan HPP warna dasar **+Rp20.000** (Alphard +Rp26.000, HiAce +Rp31.000). Sumber: kolom `HPP` sheet **STRIP 1** di `DATA UC HPP Top 100 Terlaris.xlsx` (Drive; salinan `G:\My Drive\Finance\Copy of DATA UC HPP Top 100 Terlaris.xlsx`). Abaikan sheet STRIP 2 (keputusan user 2026-11-19).

**Why:** pada 2026-11-18/19 saya menghitung diskon campaign Shopee Smartprotection dengan HPP strip = HPP dasar. User mengoreksi. Dampaknya besar: premium kelihatan aman sampai diskon ±20% dan impas ±26–28%, padahal sebenarnya sama dengan warna dasar (aman ±10–12%, impas ±18–20% di ROAS 5,9x). Saran "ikut Produk Favorit hanya variasi premium di harga rekomendasi ±18%" ternyata impas (laba ≈0%) dan dicabut.

**How to apply:**
- Setiap hitungan margin/diskon per variasi: pisahkan warna dasar dan Elite/Epic/Warior; HPP premium = dasar + 20rb.
- Di skrip `Undercover\tools`: `margin_all.STRIP_ADD` dan `line_hpp(label, variant, hpp)` sudah menambahkannya; pakai `line_hpp`, jangan `hpp[label]` langsung (celah itu ada di `discount_capacity.py` dan `fee_margin.py` sampai 2026-11-19, sudah diperbaiki). Motor tidak ditambah.
- `data\hpp_models.json` hanya berisi HPP polos; tambahan strip hanya ada di kode.
- Sebelum bilang "skrip belum memodelkan X", baca dulu kodenya (saya keliru soal ini 2026-11-19).

Terkait: [[project-undercover-margin]], [[hpp-per-merk-README]], [[2026-11-18 Audit Shopee Smartprotection iklan campaign affiliate]].
