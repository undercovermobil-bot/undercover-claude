---
name: project-undercover-sku-sync-rules
description: "Format SKU, kosakata tier/toko, dan 9 aturan bisnis final untuk SKU Sync — jangan didesain ulang tanpa instruksi eksplisit"
metadata: 
  node_type: memory
  type: project
  originSessionId: ca643b54-9c86-4cb3-9ab5-8314c2b1cb44
---

**Format & kosakata dasar**: sumber kebenaran = master `SKU, Price, Tracking Cover Mobil.xlsx` (1 sheet per merek mobil, 64 sheet). Format SKU: `MEREK-MODEL-TOKO-KAT-GEN-WARNA`. Kategori: Reguler/Premium/Exclusive. Tier warna Strip1/2/3 (kode SP/OP) = Elite/Epic/Warrior (istilah UA/OT) — 2 skema penamaan, tier konsep sama, jangan tertukar. Warna sel status di semua file hasil: hijau=benar, biru=diisi dari kosong, oranye=migrasi/auto-koreksi/konsolidasi, merah=perlu cek manual.

**9 aturan bisnis final** (sudah divalidasi berkali-kali dengan user, jangan didesain ulang tanpa instruksi eksplisit baru):

1. **Konsolidasi toko**: stok fisik OT=UA, OP=SP. `TARGET_STORE = {UA:UA, OT:UA, OP:SP, SP:SP}`. Sejak 2026-07-08 di-bake langsung ke MASTER (bukan cuma saat build listing) — akibatnya persentase "SKU duplikat" di master melonjak ke ~98,5% baris by design; exclude pasangan UA↔OT dan SP↔OP dari hitungan "duplikat genuine".
2. **Judul BigSeller/SKU Gudang**: prioritas dari Nama Produk listing ASLI toko (Undercover→fallback Otonation untuk kode UA; Smartprotection→fallback Otoprotection untuk kode SP), fallback terakhir "Nama Produk Bigseller" master. Final setelah 3x dibolak-balik user.
3. **SKU Gudang baru** hanya kode UA & SP (skip OT/OP) — konsisten kebijakan konsolidasi.
4. **Varian generik** ("Tahun Lain"/"Model Lain"/"Custom") → SKU dikosongkan, jangan ditebak, walau model single-generasi.
5. **Stok warna Abu-abu pada Reguler & tier-1 (Strip1/Elite/S1A/EAB) = 0** — aturan gudang, berlaku ke SELURUH katalog. Filter berbasis kode SKU gampang jebol karena 2 skema tier pakai kode beda (S1A/S2A/S3A di SP/OP vs EAB/PAB/WAB di UA/OT) — selalu cross-check ke teks varian asli, jangan cuma pola kode.
6. **Produk luar-scope** (Karpet Mobil, Cover Motor CM####, Travel Pouch TikTok3-Undercover) HARUS dikecualikan dari pencocokan model, atau judul yang kebetulan menyebut nama mobil ikut ke-match salah.
7. **Master TIDAK dedupe baris Toko** — tetap 4 baris terpisah per model meski kode SKU sama antar pasangan (poin 1); kolom teks "Toko" tidak dihapus.
8. **(2026-08-20, dikoreksi 2026-08-20) Mobil kembar (badge engineering) BERBAGI 1 SKU**, bukan punya SKU sendiri-sendiri. **BUKAN "Toyota selalu menang"** — arah tiap grup mengikuti riwayat kerja nyata 2026-08-11 (branch `claude/repo-memory-access-4hthja`, sekarang sudah digabung): Avanza+Xenia+Veloz→`TYT-AVZ`, **Agya+Ayla→`DHT-AYL`** (Daihatsu menang, bukan Toyota), Calya+Sigra→`TYT-CLY`, Rush+Terios→`TYT-RSH`, Raize+Rocky baru (A200)→`TYT-RZE`, Alphard+Vellfire→`TYT-ALP`, **Rocky lawas (F70/F300)+Taft GT→`DHT-FRZ`** (ikut Feroza, bukan `DHT-RCK`). **Daihatsu Feroza Long TIDAK ikut** (harga listing 295rb vs 288rb = ukuran cover beda). Verifikasi independen yang murah: harga listing Reguler termurah harus SAMA PERSIS antar anggota grup.
   - **PENGECUALIAN khusus Otoprotection (2026-09-11), TIDAK berlaku ke UA**: instruksi eksplisit user "kalo varian yg rocky samakan dengan sku yg rocky juga" — di toko OP, Rocky lawas (F70/F300) DIPISAH dari Feroza, pakai kode baru sendiri `DHT-RCK` (bukan ikut `DHT-FRZ`), harga TETAP punya Rocky (324rb/367rb/168rb, TIDAK ikut harga Feroza 370rb/413rb/188rb). Taft GT tetap ikut `DHT-FRZ` (harganya di listing OP memang sudah sama persis dgn Feroza, bukan sama dgn Rocky). Alasan pemisahan: selisih harga Rocky-lawas vs Feroza di OP (46rb) jauh lebih besar drpd kasus UA dulu (cuma 4rb, waktu itu diduga cuma salah input listing) — verifikasi murah "harga Reguler termurah harus sama" dari rule ini sendiri yang justru menunjukkan mereka BUKAN benar-benar kembar di toko ini. Rocky **modern** (A200, Gen 2 : 2019-2026) TIDAK terpengaruh, tetap `TYT-RZE` seperti biasa. Kalau nanti muncul kasus serupa (SKU sama tapi harga listing beda jauh antar anggota grup kembar), **tanyakan/pisahkan per toko** — jangan asumsikan keputusan UA otomatis berlaku ke OP/SP atau sebaliknya.
9. **(2026-08-20) Jumlah kode generasi di SKU dibatasi "Total Formula" (TF)** di Sheet2 `Data_Mobil_Lebih_dari_1_Formula_2.xlsx` — TF=N berarti model itu hanya boleh memakai N kode generasi, berapa pun generasi aslinya. TF=1 + 1 kode untuk semua generasi itu **BENAR by design**, bukan bug. Sheet1 file itu (13 model) BUKAN acuan.

Why: aturan-aturan ini masing-masing hasil dari koreksi eksplisit user, bukan desain awal — sudah beberapa kali dibolak-balik sebelum ketemu bentuk final ini (terutama aturan #2). Mengubahnya lagi tanpa instruksi baru berisiko mengulang siklus revisi yang sama.

How to apply: kalau butuh evidence "SKU ini beneran real/terpakai" (bukan cuma valid-secara-teori di master), selalu cross-check ke data operasional riil (file `Hasil Sinkronisasi SKU/`, export BigSeller), jangan asumsikan "valid di master" = "aman dipakai tim ops" — lihat [[project-undercover-sku-sync-status]] untuk contoh (deliverable 100 Mobil Terlaris).
