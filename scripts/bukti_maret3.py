# -*- coding: utf-8 -*-
"""
Uji tahap 3 — pakai musiman TikTok Undercover sbg pembanding.
Hipotesis A: Maret SUDAH termasuk di v1.  Hipotesis B: Maret BELUM termasuk.
"""
import openpyxl, re, collections, datetime
from nama_tiktok import bersih, norm, bangun_index, cocokkan
from bukti_maret import angka

UP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/'
V1_TOTAL = 27229.0
MAR_UNIT = 4479.0

# musiman TikTok Undercover (unit per bulan), dari analisa sebelumnya
TT_UC = {"01": 1053, "02": 1056, "03": 1673, "04": 1168, "05": 1004, "06": 942}
share_mar = TT_UC["03"] / sum(TT_UC.values())

print("=" * 78)
print("MUSIMAN UNDERCOVER (acuan: TikTok UC, 6 bulan penuh, toko yg sama)")
print("=" * 78)
for k, v in TT_UC.items():
    print(f"    2026-{k}: {v:5,}  ({v/sum(TT_UC.values())*100:5.1f}%)")
print(f"  porsi Maret thd 6 bulan UC = {share_mar*100:.1f}%   <- Maret memang bulan puncak")

# porsi UC thd seluruh penjualan: pakai rasio toko dari TikTok + ukuran file Shopee
UC_SHARE_TT = 6896 / (6896 + 1210 + 1122)
BYTES = {"UC": 7335322 + 1467064, "OT": 325057, "OP": 652490, "SP": 1290677}
UC_SHARE_BYTE = BYTES["UC"] / sum(BYTES.values())
print(f"\n  porsi UC dari TikTok (3 toko)      : {UC_SHARE_TT*100:.1f}%")
print(f"  porsi UC dari ukuran file Shopee   : {UC_SHARE_BYTE*100:.1f}%")
UC_SHARE = (UC_SHARE_TT + UC_SHARE_BYTE) / 2
print(f"  dipakai (rata-rata)                : {UC_SHARE*100:.1f}%")

print()
print("=" * 78)
print("UJI HIPOTESIS")
print("=" * 78)
# --- Hipotesis A: Maret sudah termasuk ---
# maka UC 6 bulan = UC_SHARE * V1_TOTAL, dan Maret = share_mar * itu
predA = share_mar * UC_SHARE * V1_TOTAL
print(f"  [A] Maret SUDAH termasuk")
print(f"      UC 6 bulan diperkirakan  = {UC_SHARE*V1_TOTAL:,.0f} unit")
print(f"      Maret diperkirakan       = {predA:,.0f} unit")
print(f"      Maret sebenarnya         = {MAR_UNIT:,.0f} unit")
print(f"      selisih                  = {abs(predA-MAR_UNIT):,.0f} unit ({abs(predA-MAR_UNIT)/MAR_UNIT*100:.1f}%)")

# --- Hipotesis B: Maret belum termasuk ---
# maka v1 memuat UC 5 bulan; UC 6 bulan = v1_UC_5bln + Maret
# UC 5 bulan = UC_SHARE_B * V1_TOTAL ; dan Maret/(UC5+Maret) harus = share_mar
totalB = V1_TOTAL + MAR_UNIT
predB = share_mar * UC_SHARE * totalB
print(f"\n  [B] Maret BELUM termasuk")
print(f"      total jadi               = {totalB:,.0f} unit")
print(f"      UC 6 bulan diperkirakan  = {UC_SHARE*totalB:,.0f} unit")
print(f"      Maret diperkirakan       = {predB:,.0f} unit")
print(f"      Maret sebenarnya         = {MAR_UNIT:,.0f} unit")
print(f"      selisih                  = {abs(predB-MAR_UNIT):,.0f} unit ({abs(predB-MAR_UNIT)/MAR_UNIT*100:.1f}%)")

print()
menang = "A (SUDAH termasuk)" if abs(predA - MAR_UNIT) < abs(predB - MAR_UNIT) else "B (BELUM termasuk)"
print(f"  >> lebih cocok: hipotesis {menang}")

# ---------- uji silang: baris motor ----------
print()
print("=" * 78)
print("UJI SILANG: baris motor")
print("=" * 78)
print("  Laporan v1 diagnostik: 767 baris motor (SEMUA Shopee+Lazada, 6 bln, 4 toko)")
print("  UC Shopee Maret saja : 140 baris motor")
print("  Dari data TikTok: motor HANYA ada di Undercover (OP=0, SP=0 baris motor),")
print("  jadi 767 itu praktis milik UC sendiri.")
est_uc_motor = 140 / share_mar
print(f"  Kalau Maret=140 dan porsi Maret {share_mar*100:.1f}%, UC 6 bln = {est_uc_motor:,.0f} baris motor")
print(f"  Laporan mencatat 767. Selisih {abs(est_uc_motor-767):,.0f}.")
if abs(est_uc_motor - 767) < 767 * 0.35:
    print("  >> KONSISTEN dgn Maret SUDAH termasuk.")
else:
    print("  >> TIDAK konsisten; condong ke Maret BELUM termasuk.")

# ---------- uji silang: baris batal ----------
print()
print("=" * 78)
print("UJI SILANG: baris batal/refund")
print("=" * 78)
print("  Laporan v1: 5.184 baris batal/refund (semua toko, 6 bulan)")
print("  UC Shopee Maret saja: 1.058 baris")
est = 1058 / share_mar / UC_SHARE
print(f"  Ekstrapolasi ke semua toko 6 bulan = {est:,.0f} baris")
print(f"  Laporan mencatat 5.184. Selisih {abs(est-5184):,.0f} ({abs(est-5184)/5184*100:.0f}%).")
if abs(est - 5184) < 5184 * 0.35:
    print("  >> KONSISTEN dgn Maret SUDAH termasuk.")
else:
    print("  >> TIDAK konsisten.")

print()
print("=" * 78)
print("CATATAN PENTING")
print("=" * 78)
print("  Klaim awal 'Maret belum masuk' bersandar pada file di GOOGLE DRIVE berformat .zip.")
print("  Tapi script user jalan dari folder LOKAL C:\\Users\\OWNER\\Downloads\\Sales —")
print("  bukan dari Drive. Sangat mungkin di lokal file-nya sudah ter-extract jadi .xlsx.")
print("  Jadi ekstensi .zip di Drive BUKAN bukti tentang apa yang dibaca script.")
