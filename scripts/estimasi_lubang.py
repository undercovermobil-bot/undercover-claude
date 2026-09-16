# -*- coding: utf-8 -*-
"""Estimasi besar lubang data: TikTok 0 baris + UC Shopee Maret berupa .zip."""

# ukuran file mentah (bytes) dari Google Drive
SHOPEE = {
    "Undercover": {"Jan": 1638880, "Feb": 1345636, "Mar": None, "Apr": 1458230, "Mei": 1565993, "Jun": 1326583},
    "Otonation": {"Jan": 62653, "Feb": 54865, "Mar": 83017, "Apr": 66380, "Mei": 32815, "Jun": 25327},
    "Otopro":    {"Jan": 114717, "Feb": 94430, "Mar": 140783, "Apr": 116902, "Mei": 123234, "Jun": 62424},
    "Smartpro":  {"Jan": 164135, "Feb": 168630, "Mar": 312236, "Apr": 310761, "Mei": 263377, "Jun": 71538},
}
UC_MAR_ZIP = 1935961  # .zip -> hampir pasti TIDAK terbaca script
TIKTOK = {"Undercover": [1259944, 1887836, 1301617], "Otopro": [277629, 413851], "Smartpro": [235311, 420309]}
LAZADA = {"Undercover": [35649, 35733], "Smartpro": [12268, 10869]}

BARIS_SHOPEE_TERBACA = 33369
UNIT_TERHITUNG = 27229
HARI = 181

print("=" * 74)
print("A. UKURAN FILE MENTAH DI DRIVE")
print("=" * 74)
tot_shopee_dibaca = 0
for toko, bln in SHOPEE.items():
    s = sum(v for v in bln.values() if v)
    hilang = [k for k, v in bln.items() if v is None]
    tot_shopee_dibaca += s
    print(f"  Shopee {toko:12s}: {s:>10,} B   {sum(1 for v in bln.values() if v)}/6 bulan"
          + (f"   << {hilang} = .ZIP, tak terbaca" if hilang else ""))
print(f"  {'TOTAL Shopee terbaca':19s}: {tot_shopee_dibaca:>10,} B  -> {BARIS_SHOPEE_TERBACA:,} baris order")

tot_tt = sum(sum(v) for v in TIKTOK.values())
tot_lz = sum(sum(v) for v in LAZADA.values())
print(f"\n  TOTAL TikTok        : {tot_tt:>10,} B  -> 0 baris terbaca  << LUBANG UTAMA")
print(f"  TOTAL Lazada        : {tot_lz:>10,} B  -> 160 baris terbaca")
print(f"  UC Shopee Maret(zip): {UC_MAR_ZIP:>10,} B  -> 0 baris terbaca  << LUBANG KEDUA")

bytes_per_baris = tot_shopee_dibaca / BARIS_SHOPEE_TERBACA
unit_per_byte = UNIT_TERHITUNG / tot_shopee_dibaca
print(f"\n  kepadatan Shopee    : {bytes_per_baris:,.0f} B/baris order")
print(f"  hasil bersih        : {unit_per_byte*1e6:,.0f} unit mobil per MB file")

print()
print("=" * 74)
print("B. ESTIMASI KALAU LUBANG DITUTUP")
print("=" * 74)

# --- lubang 1: UC Shopee Maret ---
uc = SHOPEE["Undercover"]
uc_ada = [v for v in uc.values() if v]
uc_rata = sum(uc_ada) / len(uc_ada)
# file zip ~ terkompres lagi; pakai rata-rata bulan lain sbg proxy ukuran xlsx-nya
est_mar = uc_rata
est_unit_mar = est_mar * unit_per_byte
print(f"  [1] UC Shopee Maret hilang")
print(f"      rata2 bulan UC lain : {uc_rata:,.0f} B  -> estimasi +{est_unit_mar:,.0f} unit")

# --- lubang 2: TikTok ---
# TikTok export 'Semua pesanan' lebih lebar; pakai rentang konservatif 40%-100% kepadatan Shopee
for f, lbl in ((0.40, "konservatif 40%"), (0.70, "tengah 70%"), (1.00, "optimis 100%")):
    print(f"  [2] TikTok ({lbl:16s}) -> +{tot_tt*unit_per_byte*f:,.0f} unit")

print()
print("=" * 74)
print("C. DAMPAK KE ANGKA RATA-RATA / HARI")
print("=" * 74)
print(f"  {'skenario':38s} {'total unit':>12s} {'unit/hari':>11s}")
print(f"  {'-'*38} {'-'*12} {'-'*11}")
sk = [
    ("Apa adanya di file (sekarang)", UNIT_TERHITUNG),
    ("+ UC Shopee Maret", UNIT_TERHITUNG + est_unit_mar),
    ("+ Maret + TikTok 40%", UNIT_TERHITUNG + est_unit_mar + tot_tt * unit_per_byte * 0.40),
    ("+ Maret + TikTok 70%", UNIT_TERHITUNG + est_unit_mar + tot_tt * unit_per_byte * 0.70),
    ("+ Maret + TikTok 100%", UNIT_TERHITUNG + est_unit_mar + tot_tt * unit_per_byte * 1.00),
]
for lbl, u in sk:
    print(f"  {lbl:38s} {u:>12,.0f} {u/HARI:>11,.1f}")

print(f"\n  Target klaim 200/hari  = {200*HARI:,} unit dalam 181 hari")

print()
print("=" * 74)
print("D. SELISIH 'PENJUALAN' vs 'PRODUKSI' (yang belum masuk hitungan)")
print("=" * 74)
print("  - motor              : 767 baris order DILEWATI (bukan mobil) -> tetap diproduksi")
print("  - batal/refund       : 5.184 baris DILEWATI -> sebagian sudah terlanjur diproduksi")
print("  - retur penuh        : 438 baris DILEWATI")
print("  - produk non-cover   : shampoo dll TIDAK dihitung")
print("  - order luar marketplace (offline/reseller/WA) : TIDAK ADA di file sama sekali")
print("\n  => angka PRODUKSI secara struktural SELALU > angka PENJUALAN marketplace di file ini")
