# -*- coding: utf-8 -*-
"""
Reader order TikTok (format 'Semua pesanan' / OrderSKUList) — dibuat 2026-08-05.
Aturan disamakan PERSIS dgn sheet Metodologi di MOBIL_TERLARIS:
 - status dikeluarkan: batal/cancel/belum bayar/unpaid/return/retur/refund/gagal/lost dll
 - Kuantitas = Quantity - Sku Quantity of return
 - Nilai      = SKU Subtotal After Discount
 - hanya MOBIL (motor dilewati)
 - periode dibatasi 1 Jan - 30 Jun 2026 supaya sebanding dgn laporan
"""
import openpyxl, datetime, re, json, collections, sys

F = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/3f5f928f-Semua_pesanan2026080513_44.xlsx'

TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")

AWAL = datetime.date(2026, 1, 1)
AKHIR = datetime.date(2026, 6, 30)


def tgl(v):
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    s = str(v).strip()
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)      # DD/MM/YYYY
    if m:
        d, mo, y = (int(x) for x in m.groups())
        try:
            return datetime.date(y, mo, d)
        except ValueError:
            return None
    return None


def num(v):
    if v is None or v == "":
        return 0.0
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return 0.0


wb = openpyxl.load_workbook(F, data_only=True)
ws = wb["OrderSKUList"]
hdr = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}

C_STAT = hdr["Order Status"]
C_SUB = hdr["Order Substatus"]
C_SKU = hdr["Seller SKU"]
C_NAMA = hdr["Product Name"]
C_VAR = hdr["Variation"]
C_QTY = hdr["Quantity"]
C_RET = hdr["Sku Quantity of return"]
C_NET = hdr["SKU Subtotal After Discount"]
C_TGL = hdr["Created Time"]
C_KAT = hdr["Product Category"]
C_CHAN = hdr["Purchase Channel"]

stat_ct = collections.Counter()
kat_ct = collections.Counter()
chan_ct = collections.Counter()
bulan_ct = collections.Counter()
toko_ct = collections.Counter()

tot_rows = 0
n_luar_periode = 0
n_tolak_status = 0
n_motor = 0
n_qty0 = 0
n_hitung = 0
unit = 0.0
nilai = 0.0
per_model = collections.Counter()
per_model_rp = collections.Counter()
per_toko_unit = collections.Counter()
tgl_min, tgl_max = None, None
sku_kosong = 0

for r in range(3, ws.max_row + 1):
    nm = ws.cell(row=r, column=C_NAMA).value
    q = ws.cell(row=r, column=C_QTY).value
    if nm is None and q is None:
        continue
    tot_rows += 1

    st = str(ws.cell(row=r, column=C_STAT).value or "")
    sb = str(ws.cell(row=r, column=C_SUB).value or "")
    kat = str(ws.cell(row=r, column=C_KAT).value or "")
    chan = str(ws.cell(row=r, column=C_CHAN).value or "")
    sku = str(ws.cell(row=r, column=C_SKU).value or "").strip()
    nama = str(nm or "")
    d = tgl(ws.cell(row=r, column=C_TGL).value)

    stat_ct[st] += 1
    kat_ct[kat] += 1
    chan_ct[chan] += 1
    if d:
        tgl_min = d if tgl_min is None or d < tgl_min else tgl_min
        tgl_max = d if tgl_max is None or d > tgl_max else tgl_max
        bulan_ct[f"{d.year}-{d.month:02d}"] += 1

    # toko dari nama produk
    low = nama.lower()
    if "otonation" in low:
        tk = "Otonation"
    elif "otoprotection" in low or "otopro" in low:
        tk = "Otoprotection"
    elif "smartprotection" in low or "smartpro" in low:
        tk = "Smartprotection"
    elif "undercover" in low:
        tk = "Undercover"
    else:
        tk = "(tak dikenali)"
    toko_ct[tk] += 1

    # ---- filter ----
    if d is None or not (AWAL <= d <= AKHIR):
        n_luar_periode += 1
        continue
    blob = (st + " " + sb).lower()
    if any(t in blob for t in TOLAK):
        n_tolak_status += 1
        continue
    if "motor" in low or "motor" in kat.lower():
        n_motor += 1
        continue
    qn = num(ws.cell(row=r, column=C_QTY).value) - num(ws.cell(row=r, column=C_RET).value)
    if qn <= 0:
        n_qty0 += 1
        continue

    n_hitung += 1
    unit += qn
    nilai += num(ws.cell(row=r, column=C_NET).value)
    if not sku:
        sku_kosong += 1
    # nama model = buang embel-embel tier & toko
    mdl = re.sub(r'\s*-\s*(Undercover|Otonation|Otoprotection|Smartprotection).*$', '', nama, flags=re.I)
    mdl = re.sub(r'^\s*Cover Mobil\s*', '', mdl, flags=re.I)
    mdl = re.sub(r'\s*(Reguler|Premium|Exclusive|Elite|Epic|Warrior|Strip\s*\d|Transparan)\b.*$', '', mdl, flags=re.I).strip()
    per_model[mdl] += qn
    per_model_rp[mdl] += num(ws.cell(row=r, column=C_NET).value)
    per_toko_unit[tk] += qn

P = print
P("=" * 76)
P("A. ISI FILE TIKTOK (apa adanya)")
P("=" * 76)
P(f"  total baris data      : {tot_rows:,}")
P(f"  rentang Created Time  : {tgl_min}  s/d  {tgl_max}")
P("\n  sebaran per bulan:")
for k in sorted(bulan_ct):
    tanda = "  <-- DI LUAR Jan-Jun" if not (k.startswith("2026-0") and k[-2:] in ("01","02","03","04","05","06")) else ""
    P(f"    {k} : {bulan_ct[k]:6,} baris{tanda}")
P("\n  Order Status:")
for k, v in stat_ct.most_common():
    P(f"    {str(k)[:38]:38s} {v:6,}")
P("\n  Purchase Channel:")
for k, v in chan_ct.most_common(8):
    P(f"    {str(k)[:38]:38s} {v:6,}")
P("\n  Product Category (5 teratas):")
for k, v in kat_ct.most_common(5):
    P(f"    {str(k)[:38]:38s} {v:6,}")
P("\n  Toko (dari nama produk):")
for k, v in toko_ct.most_common():
    P(f"    {str(k)[:38]:38s} {v:6,}")

P()
P("=" * 76)
P("B. SETELAH FILTER (aturan sama dgn Metodologi, periode 1 Jan - 30 Jun 2026)")
P("=" * 76)
P(f"  dilewati krn di luar periode      : {n_luar_periode:,}")
P(f"  dilewati krn status batal/refund  : {n_tolak_status:,}")
P(f"  dilewati krn motor                : {n_motor:,}")
P(f"  dilewati krn qty net <= 0         : {n_qty0:,}")
P(f"  BARIS DIHITUNG                    : {n_hitung:,}")
P(f"  Seller SKU kosong (dari yg dihitung): {sku_kosong:,}")
P()
P(f"  >> TOTAL UNIT MOBIL TikTok  : {unit:,.0f}")
P(f"  >> TOTAL NILAI TikTok       : Rp {nilai:,.0f}")
P(f"  >> rata-rata harga/unit     : Rp {nilai/unit:,.0f}" if unit else "")
P(f"  >> per hari (181 hari)      : {unit/181:,.2f} unit")
P("\n  unit per toko:")
for k, v in per_toko_unit.most_common():
    P(f"    {str(k)[:38]:38s} {v:8,.0f}")

P("\n  TOP 15 model di TikTok:")
for i, (m, v) in enumerate(per_model.most_common(15), 1):
    P(f"    {i:2d}. {str(m)[:34]:34s} {v:6,.0f} unit   Rp {per_model_rp[m]:>13,.0f}")

json.dump({"unit": unit, "nilai": nilai, "baris": n_hitung,
           "per_model": dict(per_model), "per_model_rp": dict(per_model_rp),
           "per_toko": dict(per_toko_unit)},
          open("tiktok_hasil.json", "w"), ensure_ascii=False)
P("\n  -> disimpan ke tiktok_hasil.json")
