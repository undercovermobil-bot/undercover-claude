# Aturan SKU (ringkasan; sumber resmi di vault)

Sumber resmi: vault `10 Projects/Undercover/SKU Sync/project-undercover-sku-sync-rules.md` dan
`project-undercover-bigseller-sync.md`. Ringkasan ini untuk bekerja cepat; bila beda, vault menang.

## Format
`MEREK-MODEL-TOKO-KAT-GEN[-WARNA]`, contoh `TYT-AVZ-SP-R-G1-ABU`.
- **Model** = 2 segmen pertama (`TYT-AVZ`); satu kode bisa mewakili beberapa nama mobil (Avanza/Xenia/Veloz).
- **TOKO**: kode toko dikonsolidasi: OT = UA, OP = SP. SKU gudang baru hanya untuk kode UA dan SP.
- **KAT**: R Reguler, S Strip, T Transparan, P Premium, E Exclusive. OP/SP umumnya R, S, T.
- **GEN**: `G1`, `G2`, ... (lihat Total Formula); beberapa model masih memakai kode sub-model lama.

## Warna (akhiran), terbukti 100% konsisten di data OP/SP
| Label listing | Akhiran |
|---|---|
| Abu-abu | `ABU` |
| Hitam | `HTM` |
| Biru / Biru Benhur (salah ketik: Benhru, Bnehur) | `BRU` |
| Merah | `MRH` |
| Hijau / Hijau Army | `GRN` |
| Orange | `ORG` |
| Transparan (tanpa warna) | `TRP` (KAT `T`) |

## Strip (KAT `S`)
`S<N><A|B|M>`: N = 1/2/3, A = Abu, B = Biru, M = Merah. **Strip 1 = Epic, Strip 2 = Elite, Strip 3 = Warrior.**
Listing OP memakai teks "Strip 1 Abu-abu" (TikTok) atau "Strip 1 Abu" (Shopee); listing SP/UA memakai "Epic Abu",
"Elite Biru", "Warrior Merah". Salah ketik yang ada: "Warior", "Eltie", "Benhru" - terima semuanya.

## Total Formula (aturan paling sering disalahpahami)
File: `G:\My Drive\E-commerce\Data Mobil Lebih dari 1 Formula.xlsx`, **Sheet2** (Sheet1 tidak lengkap). Kolom: Nama Mobil,
Generasi, Total Formula (TF).
- **TF = N berarti model hanya boleh memakai N kode generasi di SKU**, berapa pun generasi aslinya.
- TF = 1 -> semua generasi berbagi satu SKU (kode `G1`). Contoh: Brio (Gen 1 dan 2 -> hanya `G1`); **Land Cruiser TF=1** (J60..J300 satu SKU).
- Contoh TF > 1: Corolla TF=9 ("Gen 1-2" satu formula -> Gen 2 = `G1`; "Gen 9,10,12" -> `G9`); Mini Cooper TF=2 (3 pintu / 5 pintu).
- Jadi **beberapa label generasi memakai satu kode itu normal**. Jangan melaporkannya sebagai SKU kembar/salah tanpa membuka file formula.
- Model yang tidak ada di file formula (sekitar 135 per Agustus) belum punya keputusan; jangan menebak, tanyakan.

## Kode format lama (belum dikonversi ke `G1/G2`)
`J60`/`J40` (Land Cruiser/Hardtop), `F70` (Taft GT), `COM` (HiAce), `XOV` (SX4), `KTK`/`KPS` (Starlet), `3P`/`5P` (Mini, Jimny), `5S`/`7S`
(Livina X-Gear; ini sudah diputuskan sah karena TF ditentukan lewat jumlah kursi). Konversi ke `G1` hanya setelah SKU gudang
BigSeller `G1` ada, kalau tidak pemetaan stok listing-gudang putus. Keputusan user per kasus.

## Aturan lain
- Varian generik ("Tahun Lain", "Model Lain", "Custom") -> SKU dikosongkan, jangan ditebak.
- Stok warna Abu-abu pada Reguler dan tier-1 = 0 (aturan gudang).
- Produk luar scope: Karpet Mobil, Cover Motor `CM####`, produk custom.
- SKU lintas channel harus sama: produk yang sama di Shopee dan TikTok toko yang sama memakai SKU yang sama. OP memakai SKU yang sama dengan SP.
- **Master** `G:\My Drive\E-commerce\List Produk SKU\SKU, Price, Tracking Cover Mobil.xlsx` (satu sheet per merek). Bisa tertinggal dari
  file formula (Land Cruiser di master G1-G5, formula TF=1). Per 2026-11-12 sheet "MG (Morris Garages)" kosong (MG S5 EV belum ada).
  Untuk SKU listing, **file formula yang menentukan jumlah kode generasi**; master hanya daftar SKU.

## Daftar acuan 100 terlaris
- **Resmi**: `G:\My Drive\E-commerce\RANKING TOP 100 PER SKU.xlsx`, sheet "Peringkat Lengkap" (peringkat <= 100 = dipertahankan; 101-104 di luar) dan
  "Daftar Mobil Listing UA" (nama mobil -> kode -> status). Alias: peringkat 98 `SZK-VITARA` = listing `SZK-GVT` (Grand Vitara).
- "100 SKU" = 100 **grup kode**, bukan 100 nama; di sheet UA sekitar 110 nama mobil berstatus "Dipertahankan".
- `sistem-stok-gsheet/uji/daftar-urutan.js` (repo) adalah turunan untuk sheet stok (UC 100 model, STP 99 model tanpa Land Cruiser): **bukan acuan archive**.
