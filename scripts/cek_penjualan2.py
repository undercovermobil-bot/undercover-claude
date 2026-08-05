# -*- coding: utf-8 -*-
"""Lanjutan: cari baris TOTAL, hitung cakupan Top300 vs 446 model, cek liputan Detail."""
import openpyxl

SRC = "/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx"
wb = openpyxl.load_workbook(SRC, data_only=True)

ws = wb["Top 300 Mobil"]
print("### Baris awal & akhir sheet 'Top 300 Mobil' ###")
for r in list(range(1, 9)) + list(range(ws.max_row - 8, ws.max_row + 1)):
    vals = [ws.cell(row=r, column=c).value for c in range(1, 9)]
    print(f"  r{r}: {vals}")

print("\n### Baris tanpa 'No' (kemungkinan TOTAL / catatan) ###")
for r in range(6, ws.max_row + 1):
    no = ws.cell(row=r, column=1).value
    nm = ws.cell(row=r, column=2).value
    q = ws.cell(row=r, column=3).value
    if q is not None and (no is None or not isinstance(no, (int, float))):
        print(f"  r{r}: No={no!r} Nama={nm!r} Qty={q!r}")

# hitung ulang HANYA baris yang punya nomor urut
tot = 0
n = 0
maxno = 0
for r in range(6, ws.max_row + 1):
    no = ws.cell(row=r, column=1).value
    q = ws.cell(row=r, column=3).value
    if isinstance(no, (int, float)) and q is not None:
        n += 1
        maxno = max(maxno, int(no))
        tot += float(q)
print(f"\n  baris model bernomor : {n} (No maks = {maxno})")
print(f"  total qty model      : {tot:,.0f}")

# -------- Detail sheet: berapa model unik --------
ws2 = wb["Detail Gen & Warna"]
models = {}
for r in range(4, ws2.max_row + 1):
    nm = ws2.cell(row=r, column=2).value
    q = ws2.cell(row=r, column=6).value
    if nm and q is not None:
        models[nm] = models.get(nm, 0) + float(q)
print(f"\n  model unik di Detail : {len(models)}")
print(f"  total qty Detail     : {sum(models.values()):,.0f}")

# -------- silang: apakah qty per model sama di dua sheet? --------
top = {}
for r in range(6, ws.max_row + 1):
    no = ws.cell(row=r, column=1).value
    nm = ws.cell(row=r, column=2).value
    q = ws.cell(row=r, column=3).value
    if isinstance(no, (int, float)) and nm and q is not None:
        top[nm] = float(q)

beda = []
for nm, q in top.items():
    q2 = models.get(nm)
    if q2 is None:
        beda.append((nm, q, "TIDAK ADA di Detail"))
    elif abs(q - q2) > 1e-6:
        beda.append((nm, q, q2))
print(f"\n  model di Top300 yg qty-nya beda/absen di Detail: {len(beda)}")
for b in beda[:20]:
    print("   ", b)

hanya_detail = [m for m in models if m not in top]
print(f"\n  model yang hanya ada di Detail: {len(hanya_detail)}")
print("   ", hanya_detail[:20])

print(f"\n  TOTAL RESMI (Metodologi r24) : 27,229 unit")
print(f"  tercakup di Top300           : {tot:,.0f} ({tot/27229*100:.2f}%)")
print(f"  tercakup di Detail           : {sum(models.values()):,.0f} ({sum(models.values())/27229*100:.2f}%)")
print(f"  sisa 'ekor panjang' (446-{len(top)} model) : {27229-tot:,.0f} unit")

# -------- kecepatan jual resmi --------
H = 181
print("\n### KECEPATAN JUAL RESMI (27.229 unit / 181 hari) ###")
print(f"  per hari   : {27229/H:,.2f} unit")
print(f"  per minggu : {27229/H*7:,.1f} unit")
print(f"  per bulan  : {27229/H*30:,.1f} unit")
print(f"  klaim 200/hari -> {200*H:,.0f} unit dlm 181 hari; aktual {27229:,} = {27229/(200*H)*100:.1f}% dari klaim")

# -------- sanity: nilai rupiah --------
print("\n### NILAI ###")
print(f"  Total nilai (Metodologi) : Rp 8,022,510,728")
print(f"  Rata-rata harga/unit     : Rp {8022510728/27229:,.0f}")
print(f"  Omzet rata-rata/hari     : Rp {8022510728/H:,.0f}")
print(f"  Omzet rata-rata/bulan    : Rp {8022510728/H*30:,.0f}")

# -------- diagnostik marketplace --------
print("\n### CATATAN PENTING DARI DIAGNOSTIK ###")
print("  Shopee: 33.369 baris | TikTok: 0 baris | Lazada: 160 baris")
print("  -> TikTok NOL. Data TikTok tidak ikut terbaca sama sekali.")
