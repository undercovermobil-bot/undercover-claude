# -*- coding: utf-8 -*-
"""Angka final TikTok: klasifikasi pakai NAMA PRODUK (kategori TikTok terbukti salah label)."""
import openpyxl, datetime, re, collections, json

F = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/3f5f928f-Semua_pesanan2026080513_44.xlsx'
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return 0.0


def tgl(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', str(v).strip())
    if m:
        d, mo, y = (int(x) for x in m.groups())
        try:
            return datetime.date(y, mo, d)
        except ValueError:
            return None
    return None


def jenis(nama):
    s = nama.lower()
    if re.search(r'\b(cover|sarung|selimut|body cover)\b.*\bmotor\b', s) or "sepeda motor" in s:
        return "MOTOR"
    if "cover mobil" in s or "car cover" in s:
        return "MOBIL"
    return "LAIN"


wb = openpyxl.load_workbook(F, data_only=True)
ws = wb["OrderSKUList"]
h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}

agg = collections.Counter()
rp = collections.Counter()
bulan_mobil = collections.Counter()
sku_bulan_isi = collections.Counter()
sku_bulan_tot = collections.Counter()
chan_mobil = collections.Counter()
per_model = collections.Counter()
per_model_rp = collections.Counter()
lain_contoh = collections.Counter()

for r in range(3, ws.max_row + 1):
    nm = ws.cell(row=r, column=h["Product Name"]).value
    if nm is None:
        continue
    st = (str(ws.cell(row=r, column=h["Order Status"]).value or "") + " " +
          str(ws.cell(row=r, column=h["Order Substatus"]).value or "")).lower()
    if any(t in st for t in TOLAK):
        continue
    q = num(ws.cell(row=r, column=h["Quantity"]).value) - num(ws.cell(row=r, column=h["Sku Quantity of return"]).value)
    if q <= 0:
        continue
    nama = str(nm)
    j = jenis(nama)
    v = num(ws.cell(row=r, column=h["SKU Subtotal After Discount"]).value)
    agg[j] += q
    rp[j] += v
    if j == "LAIN":
        lain_contoh[nama[:55]] += q
    if j != "MOBIL":
        continue
    d = tgl(ws.cell(row=r, column=h["Created Time"]).value)
    if d:
        bulan_mobil[f"{d.year}-{d.month:02d}"] += q
        sku_bulan_tot[f"{d.year}-{d.month:02d}"] += 1
        if str(ws.cell(row=r, column=h["Seller SKU"]).value or "").strip():
            sku_bulan_isi[f"{d.year}-{d.month:02d}"] += 1
    chan_mobil[str(ws.cell(row=r, column=h["Purchase Channel"]).value or "")] += q
    mdl = re.sub(r'\s*-\s*(Undercover|Otonation|Otoprotection|Smartprotection).*$', '', nama, flags=re.I)
    mdl = re.sub(r'^\s*Cover Mobil\s*', '', mdl, flags=re.I)
    mdl = re.sub(r'\s*(Reguler|Premium|Exclusive|Elite|Epic|Warrior|Strip\s*\d|Transparan)\b.*$', '', mdl, flags=re.I).strip()
    per_model[mdl] += q
    per_model_rp[mdl] += v

P = print
P("=" * 78)
P("KLASIFIKASI ULANG BERDASARKAN NAMA PRODUK")
P("=" * 78)
for k in ("MOBIL", "MOTOR", "LAIN"):
    P(f"  {k:6s}: {agg[k]:7,.0f} unit   Rp {rp[k]:>15,.0f}")
P("\n  isi 'LAIN' (5 teratas):")
for k, v in lain_contoh.most_common(5):
    P(f"    {v:4,.0f}x  {k}")

U, R = agg["MOBIL"], rp["MOBIL"]
P()
P("=" * 78)
P("ANGKA FINAL TIKTOK — COVER MOBIL, 1 Jan - 30 Jun 2026")
P("=" * 78)
P(f"  unit           : {U:,.0f}")
P(f"  nilai          : Rp {R:,.0f}")
P(f"  harga rata2    : Rp {R/U:,.0f}")
P(f"  per hari       : {U/181:,.2f} unit")

P("\n  per bulan:")
for k in sorted(bulan_mobil):
    P(f"    {k} : {bulan_mobil[k]:5,.0f} unit")

P("\n  per channel (TikTok Seller Center mencakup Tokopedia):")
for k, v in chan_mobil.most_common():
    P(f"    {k:12s} {v:6,.0f} unit  ({v/U*100:.1f}%)")

P("\n  kelengkapan Seller SKU per bulan:")
for k in sorted(sku_bulan_tot):
    pct = sku_bulan_isi[k] / sku_bulan_tot[k] * 100
    P(f"    {k} : {sku_bulan_isi[k]:4,}/{sku_bulan_tot[k]:4,} = {pct:5.1f}%")

# ---------- GABUNG DGN LAPORAN ----------
LAP_UNIT, LAP_RP, HARI = 27229, 8022510728, 181
P()
P("=" * 78)
P("GABUNGAN: LAPORAN LAMA + TIKTOK")
P("=" * 78)
P(f"  {'sumber':34s} {'unit':>9s} {'unit/hari':>10s} {'nilai (Rp)':>18s}")
P(f"  {'-'*34} {'-'*9} {'-'*10} {'-'*18}")
P(f"  {'Laporan lama (Shopee+Lazada)':34s} {LAP_UNIT:9,} {LAP_UNIT/HARI:10.1f} {LAP_RP:18,}")
P(f"  {'TikTok Undercover (BARU)':34s} {U:9,.0f} {U/HARI:10.1f} {R:18,.0f}")
P(f"  {'-'*34} {'-'*9} {'-'*10} {'-'*18}")
P(f"  {'SUBTOTAL':34s} {LAP_UNIT+U:9,.0f} {(LAP_UNIT+U)/HARI:10.1f} {LAP_RP+R:18,.0f}")
P(f"\n  kenaikan: +{U/LAP_UNIT*100:.1f}% unit, +{R/LAP_RP*100:.1f}% nilai")

P("\n  YANG MASIH BELUM MASUK:")
P("    - TikTok Otoprotection & Smartprotection (2+2 file di Drive, blm di-export ulang)")
P("    - Undercover/Shopee Maret (masih .zip)")
P("    - Lazada Otonation & Otoprotection (folder tidak ada)")

# estimasi kasar sisa TikTok dari ukuran file Drive
TT_UC, TT_OP, TT_SP = 4449397, 691480, 655620
est_op = U * (TT_OP / TT_UC)
est_sp = U * (TT_SP / TT_UC)
P(f"\n  estimasi TikTok OP (skala ukuran file): ~{est_op:,.0f} unit")
P(f"  estimasi TikTok SP (skala ukuran file): ~{est_sp:,.0f} unit")
uc_mar = 4160  # dari estimasi_lubang.py
tot_est = LAP_UNIT + U + est_op + est_sp + uc_mar
P(f"\n  PROYEKSI SEMUA LUBANG DITUTUP: {tot_est:,.0f} unit -> {tot_est/HARI:,.1f} unit/hari")
P(f"  (klaim 200/hari = {200*HARI:,} unit)")

json.dump({"unit": U, "nilai": R, "per_model": dict(per_model), "per_model_rp": dict(per_model_rp)},
          open("tiktok_final.json", "w"), ensure_ascii=False)
