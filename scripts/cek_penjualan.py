# -*- coding: utf-8 -*-
"""
Verifikasi angka rata-rata di MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx
- Apakah Rata-rata/Hari = Kuantitas / 181 ?
- Apakah Minggu = Hari x 7, Bulan = Hari x 30 ?
- Berapa total unit terjual & rata-rata unit/hari sebenarnya (semua toko x semua ecommerce)?
- Bandingkan dengan klaim "rata-rata produksi 200/hari"
"""
import openpyxl

SRC = "/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx"

wb = openpyxl.load_workbook(SRC, data_only=True)
print("SHEETS:", wb.sheetnames)
print("=" * 78)

# ---------- 1. Metodologi lengkap ----------
ws = wb["Metodologi"]
print("\n### METODOLOGI (lengkap) ###")
for r in range(1, ws.max_row + 1):
    vals = [str(c.value) for c in ws[r] if c.value not in (None, "")]
    if vals:
        print(f"  r{r}: " + " | ".join(vals))

# ---------- 2. Top 300 Mobil ----------
ws = wb["Top 300 Mobil"]
print("\n" + "=" * 78)
print("### SHEET 'Top 300 Mobil' ###")
hdr = {}
for c in range(1, ws.max_column + 1):
    v = ws.cell(row=5, column=c).value
    if v:
        hdr[str(v).strip()] = c
print("  header r5 (20 pertama):", list(hdr.items())[:20])

c_nama = hdr.get("Nama Mobil")
c_qty = hdr.get("Total Kuantitas")
c_pct = hdr.get("% Kuantitas")
c_rp = hdr.get("Total Penjualan (Rp)")
c_pctn = hdr.get("% Nilai")
c_hari = hdr.get("Rata-rata Terjual/Hari")

tot_qty = 0
tot_rp = 0.0
nrow = 0
bad_hari = []
rows_top = []
for r in range(6, ws.max_row + 1):
    nm = ws.cell(row=r, column=c_nama).value
    q = ws.cell(row=r, column=c_qty).value
    if not nm or q is None:
        continue
    nrow += 1
    q = float(q)
    rp = ws.cell(row=r, column=c_rp).value or 0
    h = ws.cell(row=r, column=c_hari).value
    tot_qty += q
    tot_rp += float(rp)
    rows_top.append((nm, q, float(rp), h))
    if h is not None:
        exp = q / 181.0
        if abs(float(h) - exp) > 1e-6:
            bad_hari.append((r, nm, q, float(h), exp))

print(f"  jumlah baris model : {nrow}")
print(f"  TOTAL KUANTITAS    : {tot_qty:,.0f} unit")
print(f"  TOTAL PENJUALAN    : Rp {tot_rp:,.0f}")
print(f"  baris dgn Rata2/Hari != Qty/181 : {len(bad_hari)}")
for b in bad_hari[:10]:
    print("    ", b)

# cek % kuantitas konsisten dengan total
r6q = ws.cell(row=6, column=c_qty).value
r6p = ws.cell(row=6, column=c_pct).value
if r6p:
    implied = float(r6q) / (float(r6p) / 100.0)
    print(f"  total tersirat dari % baris-1 : {implied:,.1f} unit  (vs {tot_qty:,.0f} di sheet ini)")

# ---------- 3. Detail Gen & Warna ----------
ws = wb["Detail Gen & Warna"]
print("\n" + "=" * 78)
print("### SHEET 'Detail Gen & Warna' ###")
h2 = {}
for c in range(1, ws.max_column + 1):
    v = ws.cell(row=3, column=c).value
    if v:
        h2[str(v).strip()] = c
print("  header r3:", h2)

cq = h2.get("Kuantitas")
cd = h2.get("Rata-rata/Hari")
cw = h2.get("Rata-rata/Minggu")
cm = h2.get("Rata-rata/Bulan")
cs = h2.get("Estimasi Stok (buffer 7 hari)")
cnm = h2.get("Nama Mobil")
crp = h2.get("Total Penjualan (Rp)")
cjc = h2.get("Jenis Cover")

bad_d, bad_w, bad_m, bad_s = [], [], [], []
tot_q2 = 0
tot_rp2 = 0.0
n2 = 0
per_cover = {}
for r in range(4, ws.max_row + 1):
    q = ws.cell(row=r, column=cq).value
    if q is None:
        continue
    n2 += 1
    q = float(q)
    tot_q2 += q
    tot_rp2 += float(ws.cell(row=r, column=crp).value or 0)
    jc = ws.cell(row=r, column=cjc).value
    per_cover[jc] = per_cover.get(jc, 0) + q
    d = ws.cell(row=r, column=cd).value
    w = ws.cell(row=r, column=cw).value
    m = ws.cell(row=r, column=cm).value
    s = ws.cell(row=r, column=cs).value
    if d is None:
        continue
    d = float(d)
    if abs(d - q / 181.0) > 1e-6:
        bad_d.append((r, q, d, q / 181.0))
    if w is not None and abs(float(w) - d * 7) > 1e-6:
        bad_w.append((r, d, float(w), d * 7))
    if m is not None and abs(float(m) - d * 30) > 1e-6:
        bad_m.append((r, d, float(m), d * 30))
    if s is not None:
        import math
        if abs(float(s) - math.ceil(d * 7)) > 1e-6 and abs(float(s) - round(d * 7)) > 1e-6:
            bad_s.append((r, d, float(s), d * 7))

print(f"  jumlah baris detail : {n2}")
print(f"  TOTAL KUANTITAS     : {tot_q2:,.0f} unit")
print(f"  TOTAL PENJUALAN     : Rp {tot_rp2:,.0f}")
print(f"  Rata2/Hari salah    : {len(bad_d)}")
print(f"  Rata2/Minggu salah  : {len(bad_w)}")
print(f"  Rata2/Bulan salah   : {len(bad_m)}")
print(f"  Estimasi Stok beda  : {len(bad_s)}")
for lbl, arr in (("HARI", bad_d), ("MINGGU", bad_w), ("BULAN", bad_m), ("STOK", bad_s)):
    for b in arr[:5]:
        print(f"    {lbl}", b)

print("\n  Kuantitas per Jenis Cover:")
for k, v in sorted(per_cover.items(), key=lambda x: -x[1]):
    print(f"    {str(k):20s} {v:10,.0f}  ({v/tot_q2*100:5.2f}%)")

# ---------- 4. Ringkasan kecepatan jual ----------
print("\n" + "=" * 78)
print("### RINGKASAN KECEPATAN JUAL ###")
HARI = 181
for lbl, tq in (("Top 300 Mobil", tot_qty), ("Detail Gen&Warna", tot_q2)):
    print(f"  [{lbl}]")
    print(f"    total unit          : {tq:,.0f}")
    print(f"    rata-rata / hari    : {tq/HARI:,.2f} unit")
    print(f"    rata-rata / minggu  : {tq/HARI*7:,.1f} unit")
    print(f"    rata-rata / bulan   : {tq/HARI*30:,.1f} unit")
    print(f"    utk capai 200/hari  : butuh {200*HARI:,.0f} unit  (sekarang {tq/(200*HARI)*100:.1f}%)")

# ---------- 5. Top 15 ----------
print("\n  TOP 15 MODEL:")
for i, (nm, q, rp, h) in enumerate(rows_top[:15], 1):
    print(f"    {i:2d}. {str(nm):28s} {q:7,.0f} unit  {q/181:6.2f}/hari  Rp {rp:>15,.0f}")

# ---------- 6. Cek apakah ada baris "sisa" di luar top 300 ----------
print("\n  selisih total Top300 vs Detail:", f"{tot_qty - tot_q2:,.0f} unit")
