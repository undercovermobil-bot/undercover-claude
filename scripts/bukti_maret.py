# -*- coding: utf-8 -*-
"""
UJI TEGAS: apakah UC Shopee Maret sudah masuk laporan v1 atau belum?

Logika: laporan v1 mencakup SEMUA toko x SEMUA bulan. Kalau Maret UC ikut,
maka untuk setiap model, kuantitas laporan HARUS >= kuantitas Maret UC saja.
Kalau ada model yang Maret-nya saja SUDAH MELEBIHI angka laporan,
berarti Maret jelas TIDAK ikut terhitung.
"""
import openpyxl, re, collections, datetime
from nama_tiktok import bersih, norm, bangun_index, cocokkan

UP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/'
LAP = UP + 'fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx'
MAR = [UP + '490ea489-Order.all.20260301_20260331_part_1_of_2.xlsx',
       UP + '9febc200-Order.all.20260301_20260331_part_2_of_2.xlsx']
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")


def angka(v):
    """parser angka format Indonesia: '298.000' -> 298000 ; '1.234,56' -> 1234.56"""
    if v is None or v == "":
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif s.count(".") >= 1:
        bag = s.split(".")
        if all(len(b) == 3 for b in bag[1:]):        # 298.000 / 1.234.567
            s = "".join(bag)
    try:
        return float(s)
    except ValueError:
        return 0.0


# ---------- laporan ----------
wl = openpyxl.load_workbook(LAP, data_only=True)
wt = wl["Top 300 Mobil"]
lap = {}
for r in range(6, wt.max_row + 1):
    no = wt.cell(row=r, column=1).value
    nm = wt.cell(row=r, column=2).value
    if isinstance(no, (int, float)) and nm:
        lap[str(nm).strip()] = angka(wt.cell(row=r, column=3).value)
penuh, tm = bangun_index(list(lap))

# ---------- Maret UC ----------
mar = collections.Counter()
mar_rp = collections.Counter()
n_baris = n_tolak = n_motor = n_lain = 0
unit = 0.0
nilai = 0.0
tmin = tmax = None
tak_cocok = collections.Counter()

for path in MAR:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["orders"]
    h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=h["Nama Produk"]).value
        if nm is None:
            continue
        n_baris += 1
        t = str(ws.cell(row=r, column=h["Waktu Pesanan Dibuat"]).value or "")[:10]
        try:
            d = datetime.date(*[int(x) for x in t.split("-")])
            tmin = d if tmin is None or d < tmin else tmin
            tmax = d if tmax is None or d > tmax else tmax
        except Exception:
            pass
        st = (str(ws.cell(row=r, column=h["Status Pesanan"]).value or "") + " " +
              str(ws.cell(row=r, column=h["Status Pembatalan/ Pengembalian"]).value or "")).lower()
        if any(x in st for x in TOLAK):
            n_tolak += 1
            continue
        q = angka(ws.cell(row=r, column=h["Jumlah"]).value) - angka(ws.cell(row=r, column=h["Returned quantity"]).value)
        if q <= 0:
            continue
        nama = str(nm)
        low = nama.lower()
        if re.search(r'\b(cover|sarung|selimut)\b.*\bmotor\b', low) or "sepeda motor" in low:
            n_motor += 1
            continue
        if "mobil" not in low and "car cover" not in low:
            n_lain += 1
            continue
        v = angka(ws.cell(row=r, column=h["Subtotal Pesanan"]).value)
        mentah, tier = bersih(nama)
        k = cocokkan(mentah, penuh, tm)
        if k is None:
            tak_cocok[mentah] += q
            k = mentah
        mar[k] += q
        mar_rp[k] += v
        unit += q
        nilai += v

P = print
P("=" * 76)
P("ISI FILE UC SHOPEE MARET")
P("=" * 76)
P(f"  baris total      : {n_baris:,}")
P(f"  rentang tanggal  : {tmin} s/d {tmax}")
P(f"  batal/refund     : {n_tolak:,}")
P(f"  motor            : {n_motor:,}")
P(f"  produk lain      : {n_lain:,}")
P(f"  >> UNIT MOBIL    : {unit:,.0f}")
P(f"  >> NILAI         : Rp {nilai:,.0f}")
P(f"  model tak cocok  : {len(tak_cocok)} ({sum(tak_cocok.values()):,.0f} unit)")

P()
P("=" * 76)
P("UJI: adakah model yang MARET SAJA sudah melebihi TOTAL laporan v1?")
P("=" * 76)
langgar = []
for m, q in mar.items():
    if m in lap and q > lap[m]:
        langgar.append((m, q, lap[m]))
langgar.sort(key=lambda x: -(x[1] - x[2]))
P(f"  model dicek         : {len([m for m in mar if m in lap])}")
P(f"  MELANGGAR (Mar>v1)  : {len(langgar)}")
P()
if langgar:
    P(f"  {'model':30s} {'Maret saja':>11s} {'total v1':>10s} {'selisih':>9s}")
    P(f"  {'-'*30} {'-'*11} {'-'*10} {'-'*9}")
    for m, q, l in langgar[:25]:
        P(f"  {m[:30]:30s} {q:11,.0f} {l:10,.0f} {q-l:9,.0f}")
    P()
    P("  >> KESIMPULAN: Maret TIDAK MUNGKIN sudah termasuk di laporan v1.")
    P("     Mustahil satu bulan melebihi total 6 bulan seluruh toko.")
else:
    P("  >> tidak ada pelanggaran -> uji ini TIDAK membuktikan Maret hilang.")
    P("     perlu metode lain.")

# uji tambahan: rasio Maret thd total laporan per model
P()
P("=" * 76)
P("UJI KEDUA: porsi Maret terhadap angka laporan (kalau >1/6, mencurigakan)")
P("=" * 76)
rat = [(m, mar[m] / lap[m]) for m in mar if m in lap and lap[m] > 0]
rat.sort(key=lambda x: -x[1])
tinggi = [x for x in rat if x[1] > 1 / 6]
P(f"  model dgn porsi Maret > 16,7% (1 dari 6 bulan): {len(tinggi)} dari {len(rat)}")
for m, x in rat[:12]:
    P(f"    {m[:32]:32s} Maret {mar[m]:5,.0f} / v1 {lap[m]:6,.0f} = {x*100:5.1f}%")
P(f"\n  total Maret {unit:,.0f} vs total v1 27.229 = {unit/27229*100:.1f}%")
P("  (kalau Maret sudah termasuk, porsinya wajar sekitar 1/6 = 16,7% utk SATU toko")
P("   dari EMPAT toko, jadi seharusnya jauh di bawah itu, sekitar 4%)")
