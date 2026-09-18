# -*- coding: utf-8 -*-
"""
LAPORAN v5 — struktur PERSIS seperti MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx asli,
tapi angkanya sudah GABUNGAN (Shopee + Lazada + TikTok/Tokopedia 3 toko).
Tidak ada pemisahan kolom per marketplace.

Sheet: 'Top 300 Mobil' (66 kolom) | 'Detail Gen & Warna' (12 kolom) | 'Metodologi'
"""
import openpyxl, re, collections, math, datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from nama_tiktok import bersih, bangun_index, cocokkan
from selaras_gen import Penyelaras

UP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/'
LAP = UP + 'fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx'
TT_FILES = [(UP + '3f5f928f-Semua_pesanan2026080513_44.xlsx', 'Undercover'),
            (UP + 'bd590f02-Semua_pesanan2026080514_02_Otopro.xlsx', 'Otoprotection'),
            (UP + '76aed148-Semua_pesanan2026080514_04_Smartpro.xlsx', 'Smartprotection')]
OUT = 'MOBIL_TERLARIS_GABUNGAN_v5.xlsx'
HARI = 181
AWAL, AKHIR = datetime.date(2026, 1, 1), datetime.date(2026, 6, 30)
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")


def rapikan_warna_strip(w):
    """'Elite Abu-abu' -> 'Elite Abu' ; 'Strip 1 Abu-abu' -> 'Strip 1 Abu' (konvensi laporan)"""
    s_ = str(w).strip()
    low = s_.lower()
    tier = None
    for t in ("elite", "epic", "warrior"):
        if t in low:
            tier = t.capitalize(); break
    if tier is None:
        m = re.search(r'strip\s*([123])', low)
        if m:
            tier = "Strip " + m.group(1)
    if tier is None:
        return s_
    for c in ("abu", "merah", "biru"):
        if c in low:
            return f"{tier} {c.capitalize()}"
    return s_


def jenis_cover(nama_produk, warna, tier_nama):
    """URUTAN SESUAI METODOLOGI v1: penanda WARNA dulu, baru tier di nama produk.
    Listing sering diberi nama 'Reguler' padahal variannya warna Strip."""
    w = str(warna).lower()
    if any(k in w for k in ("elite", "epic", "warrior")) or re.search(r'strip\s*[123]', w):
        return "Strip"
    if "transparan" in w:
        return "Transparan"
    if "silver" in w:
        return "Premium"
    if tier_nama in ("Elite", "Epic", "Warrior") or str(tier_nama).startswith("Strip"):
        return "Strip"
    if tier_nama in ("Reguler", "Premium", "Exclusive", "Transparan"):
        return tier_nama
    return "Reguler"


def numf(v):
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


# ============ 1. BASIS: sheet Detail laporan v1 (Shopee + Lazada) ============
wl = openpyxl.load_workbook(LAP, data_only=True)
wt = wl["Top 300 Mobil"]
urutan_v1 = []
lama_model = {}
for r in range(6, wt.max_row + 1):
    no = wt.cell(row=r, column=1).value
    nm = wt.cell(row=r, column=2).value
    if isinstance(no, (int, float)) and nm:
        nm = str(nm).strip()
        urutan_v1.append(nm)
        lama_model[nm] = numf(wt.cell(row=r, column=3).value)
# baris TOTAL v1 -> ekor panjang yg tidak dirinci
V1_TOTAL_U = numf(wt.cell(row=wt.max_row, column=3).value)
V1_TOTAL_R = numf(wt.cell(row=wt.max_row, column=5).value)

wd = wl["Detail Gen & Warna"]
hd = {str(wd.cell(row=3, column=c).value).strip(): c for c in range(1, wd.max_column + 1)}
SEL = Penyelaras(wd, hd)

detail = collections.Counter()      # (model, jenis, gen, warna) -> unit
detail_rp = collections.Counter()
v1_u = v1_r = 0.0
for r in range(4, wd.max_row + 1):
    m = wd.cell(row=r, column=hd["Nama Mobil"]).value
    if not m:
        continue
    k = (str(m).strip(),
         str(wd.cell(row=r, column=hd["Jenis Cover"]).value or "").strip(),
         str(wd.cell(row=r, column=hd["Gen"]).value or "").strip(),
         str(wd.cell(row=r, column=hd["Warna"]).value or "").strip())
    q = numf(wd.cell(row=r, column=hd["Kuantitas"]).value)
    detail[k] += q
    detail_rp[k] += numf(wd.cell(row=r, column=hd["Total Penjualan (Rp)"]).value)
    v1_u += q
    v1_r += numf(wd.cell(row=r, column=hd["Total Penjualan (Rp)"]).value)

EKOR_U = V1_TOTAL_U - v1_u          # model di luar Top 300 yg tak dirinci
EKOR_R = V1_TOTAL_R - v1_r
print(f"v1 detail: {v1_u:,.0f} unit | ekor tak dirinci: {EKOR_U:,.0f} unit")

penuh, tm = bangun_index(urutan_v1)

# ============ 2. TAMBAH TikTok ============
TIERS = [("Exclusive", r"ex+clusive"), ("Premium", r"premium"), ("Reguler", r"regul[ae]r"),
         ("Transparan", r"transparan"), ("Elite", r"elite"), ("Epic", r"epic"), ("Warrior", r"warrior")]
tt_u = tt_r = 0.0
tt_per_toko = collections.Counter()
diag = {}
for path, toko in TT_FILES:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["OrderSKUList"]
    h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}
    d_ = dict(baris=0, tolak=0, motor=0, lain=0, hitung=0)
    for r in range(3, ws.max_row + 1):
        nm = ws.cell(row=r, column=h["Product Name"]).value
        if nm is None:
            continue
        d_["baris"] += 1
        st = (str(ws.cell(row=r, column=h["Order Status"]).value or "") + " " +
              str(ws.cell(row=r, column=h["Order Substatus"]).value or "")).lower()
        if any(t in st for t in TOLAK):
            d_["tolak"] += 1; continue
        dt = tgl(ws.cell(row=r, column=h["Created Time"]).value)
        if dt is None or not (AWAL <= dt <= AKHIR):
            continue
        q = numf(ws.cell(row=r, column=h["Quantity"]).value) - numf(ws.cell(row=r, column=h["Sku Quantity of return"]).value)
        if q <= 0:
            continue
        nama = str(nm); low = nama.lower()
        if re.search(r'\b(cover|sarung|selimut)\b.*\bmotor\b', low) or "sepeda motor" in low:
            d_["motor"] += 1; continue
        if "mobil" not in low and "car cover" not in low:
            d_["lain"] += 1; continue
        v = numf(ws.cell(row=r, column=h["SKU Subtotal After Discount"]).value)
        mentah, tier = bersih(nama)
        model = cocokkan(mentah, penuh, tm) or (mentah or "(tanpa nama)")
        var = str(ws.cell(row=r, column=h["Variation"]).value or "")
        mg = re.search(r'(Gen\s*[^,]*)', var, flags=re.I)
        gen_m = mg.group(1).strip() if mg else ""
        w = re.split(r',', var)[0].strip()
        if re.match(r'gen', w, flags=re.I):
            w = ""
        jenis = jenis_cover(nama, w, tier)
        gen = SEL.gen(model, gen_m) or "(tanpa gen)"
        warna = SEL.warna(rapikan_warna_strip(w)) or "(tanpa warna)"
        detail[(model, jenis, gen, warna)] += q
        detail_rp[(model, jenis, gen, warna)] += v
        tt_u += q; tt_r += v; tt_per_toko[toko] += q
        d_["hitung"] += 1
    diag[toko] = d_
    print(f"  {toko:16s} +{d_['hitung']:5,} baris")

print(f"TikTok: {tt_u:,.0f} unit | Rp {tt_r:,.0f}")

# ============ 3. AGREGAT PER MODEL ============
per_model = collections.Counter()
per_model_rp = collections.Counter()
jenis_model = collections.defaultdict(set)
for (m, j, g, w), q in detail.items():
    per_model[m] += q
    per_model_rp[m] += detail_rp[(m, j, g, w)]
    if q > 0:
        jenis_model[m].add(j)

MODEL_U = sum(per_model.values())
MODEL_R = sum(per_model_rp.values())
GRAND_U = MODEL_U + EKOR_U
GRAND_R = MODEL_R + EKOR_R
print(f"\nmodel dirinci : {MODEL_U:,.0f} unit | Rp {MODEL_R:,.0f}")
print(f"GRAND TOTAL   : {GRAND_U:,.0f} unit | Rp {GRAND_R:,.0f} | {GRAND_U/HARI:,.2f}/hari")

peringkat = sorted(per_model, key=lambda m: (-per_model[m], m))
rank = {m: i + 1 for i, m in enumerate(peringkat)}

# ============ 4. PEMETAAN WARNA UNTUK BLOK-BLOK ============
POLOS = [("Abu-abu", r'^abu[\s-]*abu$'), ("Hitam", r'^hitam$'), ("Hijau", r'^hijau'),
         ("Merah", r'^merah$'), ("Biru", r'^biru'), ("Orange", r'^orange$')]
TIER_STRIP = [("1", ("epic", "strip 1")), ("2", ("elite", "strip 2")), ("3", ("warrior", "strip 3"))]
WARNA_STRIP = [("Abu-abu", ("abu",)), ("Merah", ("merah",)), ("Biru", ("biru",))]


def polos_kol(w):
    s = str(w).strip().lower()
    for lab, pat in POLOS:
        if re.match(pat, s):
            return lab
    return None


def strip_kol(w):
    s = str(w).strip().lower()
    t = c = None
    for lab, kata in TIER_STRIP:
        if any(k in s for k in kata):
            t = lab; break
    for lab, kata in WARNA_STRIP:
        if any(k in s for k in kata):
            c = lab; break
    return (t, c) if t and c else (None, None)


agg_polos = collections.defaultdict(collections.Counter)     # model -> warna
agg_strip = collections.defaultdict(collections.Counter)     # model -> '1|Abu-abu'
agg_prem = collections.defaultdict(collections.Counter)      # model -> warna (Premium)
agg_excl = collections.defaultdict(collections.Counter)      # model -> warna (Exclusive)
for (m, j, g, w), q in detail.items():
    if q <= 0:
        continue
    if j == "Strip":
        t, c = strip_kol(w)
        if t:
            agg_strip[m][f"{t}|{c}"] += q
    else:
        pk = polos_kol(w)
        if pk:
            agg_polos[m][pk] += q
        if j == "Premium":
            agg_prem[m][str(w).strip()] += q
        elif j == "Exclusive":
            agg_excl[m][str(w).strip()] += q

# ============ 5. TULIS FILE ============
out = openpyxl.Workbook()
JUD = Font(bold=True, size=14)
SUB = Font(italic=True, size=9, color="555555")
HB = Font(bold=True, color="FFFFFF", size=10)
FBIRU = PatternFill("solid", fgColor="1F4E79")
FSTRIP = PatternFill("solid", fgColor="C00000")
FPREM = PatternFill("solid", fgColor="7030A0")
FEXCL = PatternFill("solid", fgColor="BF8F00")
FBLOK = PatternFill("solid", fgColor="2F5597")
TENGAH = Alignment(horizontal="center", vertical="center", wrap_text=True)

# ---------- Sheet 1: Top 300 Mobil ----------
s = out.active
s.title = "Top 300 Mobil"
s["A1"] = "MOBIL TERLARIS - Top 300 Model (Detail Gen & Warna) — GABUNGAN Shopee + Lazada + TikTok/Tokopedia"
s["A1"].font = JUD
s["A2"] = (f"Periode 1 Jan – 30 Jun 2026 (181 hari) · semua toko (Undercover/Otonation/Otopro/Smartpro) "
           f"· {GRAND_U:,.0f} unit · Rp {GRAND_R:,.0f} · {GRAND_U/HARI:,.1f} unit/hari")
s["A2"].font = SUB

KOL = (["No", "Nama Mobil", "Total Kuantitas", "% Kuantitas", "Total Penjualan (Rp)", "% Nilai",
        "Jenis Cover Digabung", "Rata-rata Terjual/Hari"]
       + [w for w, _ in POLOS] + ["Total Warna Polos"]
       + [f"% {w}" for w, _ in POLOS] + [f"Rata-rata/Hari {w}" for w, _ in POLOS])
STRIP_KOL = [(t, c) for c in ("Abu-abu", "Merah", "Biru") for t in ("1", "2", "3")]
KOL += [f"Strip {t} {c}" for t, c in STRIP_KOL] + ["Total Strip"]
KOL += [f"% Strip {t} {c}" for t, c in STRIP_KOL] + [f"Rata-rata/Hari Strip {t} {c}" for t, c in STRIP_KOL]
PREM_W = ["Abu-abu", "Silver"]
KOL += [f"Premium {w}" for w in PREM_W] + ["Total Premium"] + [f"% Premium {w}" for w in PREM_W] \
    + [f"Rata-rata/Hari Premium {w}" for w in PREM_W]
EXCL_W = ["Abu-abu"]
KOL += [f"Exclusive {w}" for w in EXCL_W] + ["Total Exclusive"] + [f"% Exclusive {w}" for w in EXCL_W] \
    + [f"Rata-rata/Hari Exclusive {w}" for w in EXCL_W]

# 8 kolom dasar | POLOS 6+1+6+6=19 | STRIP 9+1+9+9=28 | PREMIUM 2+1+2+2=7 | EXCLUSIVE 1+1+1+1=4
i_polos = 9
i_strip = i_polos + 19          # 28
i_prem = i_strip + 28           # 56
i_excl = i_prem + 7             # 63
assert len(KOL) == 66, f"harusnya 66 kolom, dapat {len(KOL)}"
assert (i_strip, i_prem, i_excl) == (28, 56, 63)
for c1, c2, lab, fill in ((i_polos, i_strip - 1, "WARNA POLOS (Reguler+Premium+Exclusive+Transparan, tanpa Strip)", FBLOK),
                          (i_strip, i_prem - 1, "DETAIL STRIP 1/2/3 (Epic=1, Elite=2, Warrior=3)", FSTRIP),
                          (i_prem, i_excl - 1, "DETAIL PREMIUM (subset dari Warna Polos)", FPREM),
                          (i_excl, len(KOL), "DETAIL EXCLUSIVE (subset dari Warna Polos)", FEXCL)):
    s.merge_cells(start_row=4, start_column=c1, end_row=4, end_column=c2)
    cc = s.cell(row=4, column=c1, value=lab)
    cc.font = HB; cc.fill = fill; cc.alignment = TENGAH
for i, k in enumerate(KOL, 1):
    cc = s.cell(row=5, column=i, value=k)
    cc.font = HB; cc.alignment = TENGAH
    cc.fill = FBIRU if i < i_strip else (FSTRIP if i < i_prem else (FPREM if i < i_excl else FEXCL))

for i, m in enumerate(peringkat, 1):
    r = i + 5
    q = per_model[m]; rp = per_model_rp[m]
    pol = agg_polos[m]; tpol = sum(pol.get(w, 0) for w, _ in POLOS)
    st_ = agg_strip[m]; tst = sum(st_.values())
    pr = agg_prem[m]; tpr = sum(pr.values())
    ex = agg_excl[m]; tex = sum(ex.values())
    baris = [i, m, q, q / GRAND_U, rp, rp / GRAND_R,
             ", ".join(sorted(jenis_model[m])), q / HARI]
    baris += [pol.get(w, 0) for w, _ in POLOS] + [tpol]
    baris += [pol.get(w, 0) / q if q else 0 for w, _ in POLOS]
    baris += [pol.get(w, 0) / HARI for w, _ in POLOS]
    baris += [st_.get(f"{t}|{c}", 0) for t, c in STRIP_KOL] + [tst]
    baris += [st_.get(f"{t}|{c}", 0) / q if q else 0 for t, c in STRIP_KOL]
    baris += [st_.get(f"{t}|{c}", 0) / HARI for t, c in STRIP_KOL]
    baris += [pr.get(w, 0) for w in PREM_W] + [tpr] + [pr.get(w, 0) / q if q else 0 for w in PREM_W] \
        + [pr.get(w, 0) / HARI for w in PREM_W]
    baris += [ex.get(w, 0) for w in EXCL_W] + [tex] + [ex.get(w, 0) / q if q else 0 for w in EXCL_W] \
        + [ex.get(w, 0) / HARI for w in EXCL_W]
    for c, v in enumerate(baris, 1):
        s.cell(row=r, column=c, value=v)

rT = len(peringkat) + 6
s.cell(row=rT, column=2, value="TOTAL (semua model, termasuk di luar Top 300)").font = Font(bold=True)
for c, v in ((3, GRAND_U), (4, 1), (5, GRAND_R), (6, 1), (8, GRAND_U / HARI)):
    s.cell(row=rT, column=c, value=v).font = Font(bold=True)
for c in range(i_polos, len(KOL) + 1):
    k = KOL[c - 1]
    if k.startswith("%") or k.startswith("Rata"):
        continue
    tot = sum(s.cell(row=r, column=c).value or 0 for r in range(6, rT))
    s.cell(row=rT, column=c, value=tot).font = Font(bold=True)

for c in range(1, len(KOL) + 1):
    k = KOL[c - 1]
    f = "0.000%" if k.startswith("%") else ("#,##0.00" if k.startswith("Rata") else "#,##0")
    if c in (1, 2, 7):
        f = None
    if f:
        for r in range(6, rT + 1):
            s.cell(row=r, column=c).number_format = f
s.freeze_panes = "C6"
s.auto_filter.ref = f"A5:{get_column_letter(len(KOL))}{rT-1}"
for c, w in ((1, 5), (2, 30), (3, 13), (4, 11), (5, 19), (6, 10), (7, 30), (8, 13)):
    s.column_dimensions[get_column_letter(c)].width = w
for c in range(9, len(KOL) + 1):
    s.column_dimensions[get_column_letter(c)].width = 13

# ---------- Sheet 2: Detail Gen & Warna ----------
d = out.create_sheet("Detail Gen & Warna")
d["A1"] = "Detail Penjualan per Model + Jenis Cover + Gen + Warna (Top 300 model) — GABUNGAN"
d["A1"].font = JUD
d["A2"] = ("Gen sudah disetarakan dgn list Undercover terkini. Rata-rata/Hari-Minggu-Bulan = estimasi "
           "kecepatan jual (periode 181 hari, lihat Metodologi). Estimasi Stok = Rata-rata/Hari x 7 hari "
           "(buffer restock). Angka sudah termasuk TikTok/Tokopedia.")
d["A2"].font = SUB
DK = ["Peringkat", "Nama Mobil", "Jenis Cover", "Gen", "Warna", "Kuantitas", "% dari Model",
      "Total Penjualan (Rp)", "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan",
      "Estimasi Stok (buffer 7 hari)"]
for i, k in enumerate(DK, 1):
    cc = d.cell(row=3, column=i, value=k)
    cc.font = HB; cc.fill = FBIRU; cc.alignment = TENGAH

rows = [(rank[m], m, j, g, w, q, detail_rp[(m, j, g, w)]) for (m, j, g, w), q in detail.items() if q > 0]
rows.sort(key=lambda x: (x[0], -x[5], x[2], x[3], x[4]))
for i, (pk, m, j, g, w, q, rp) in enumerate(rows):
    r = i + 4
    hh = q / HARI
    for c, v in enumerate([pk, m, j, g, w, q, q / per_model[m] if per_model[m] else 0, rp,
                           hh, hh * 7, hh * 30, math.ceil(hh * 7)], 1):
        d.cell(row=r, column=c, value=v)
n = len(rows)
for c, f in ((6, "#,##0"), (7, "0.0%"), (8, "#,##0"), (9, "#,##0.00"), (10, "#,##0.00"),
             (11, "#,##0.00"), (12, "#,##0")):
    for r in range(4, n + 4):
        d.cell(row=r, column=c).number_format = f
d.freeze_panes = "B4"
d.auto_filter.ref = f"A3:L{n+3}"
for c, w in ((1, 10), (2, 28), (3, 13), (4, 24), (5, 16), (6, 11), (7, 11), (8, 18),
             (9, 12), (10, 14), (11, 13), (12, 20)):
    d.column_dimensions[get_column_letter(c)].width = w

# ---------- Sheet 3: Metodologi ----------
mt = out.create_sheet("Metodologi")
mt["A1"] = "MOBIL TERLARIS (GABUNGAN) - Metodologi & Diagnostik"
mt["A1"].font = JUD
T = [f"Dibuat: {datetime.datetime.now():%Y-%m-%d %H:%M}",
     "Sumber: laporan v1 (Shopee+Lazada) + 3 file order TikTok Seller Center (UA/OP/SP)", "",
     "DEFINISI",
     "- Cakupan: semua toko (Undercover/Otonation/Otopro/Smartpro) x Shopee/TikTok/Tokopedia/Lazada.",
     "- Periode: 1 Jan - 30 Jun 2026 = 181 hari (terkonfirmasi dari Created Time file TikTok",
     "  dan nama file order Shopee Order.all.20260101_20260131 s/d 20260601_20260630).",
     "- Hanya MOBIL (Cover Mobil). Motor tidak masuk ranking.",
     "- Status dikeluarkan: batal, cancel, belum bayar, unpaid, return, retur, refund,",
     "  pengembalian, failed, gagal, lost.",
     "- Kuantitas = qty terjual - qty diretur.",
     "- Total Penjualan = nilai NET setelah diskon (Shopee: Subtotal Pesanan;",
     "  TikTok: SKU Subtotal After Discount; Lazada: paidPrice).",
     "- Model digabung lintas toko/marketplace berdasarkan nama model pada listing.", "",
     "ANGKA UTAMA",
     f"- Total kuantitas semua model : {GRAND_U:,.0f} unit",
     f"- Total nilai semua model     : Rp {GRAND_R:,.0f}",
     f"- Rata-rata terjual per hari  : {GRAND_U/HARI:,.2f} unit",
     f"- Rata-rata per minggu        : {GRAND_U/HARI*7:,.1f} unit",
     f"- Rata-rata per bulan         : {GRAND_U/HARI*30:,.1f} unit",
     f"- Harga rata-rata per unit    : Rp {GRAND_R/GRAND_U:,.0f}",
     f"- Model dirinci di sheet ini  : {len(peringkat):,} model ({MODEL_U:,.0f} unit)",
     f"- Ekor panjang tak dirinci    : {EKOR_U:,.0f} unit (model di luar Top 300 laporan v1)", "",
     "KONTRIBUSI TIKTOK/TOKOPEDIA (baru, belum ada di laporan v1)"]
for tk, u in tt_per_toko.most_common():
    T.append(f"- {tk:16s}: {u:6,.0f} unit")
T += [f"- TikTok TOTAL    : {tt_u:,.0f} unit | Rp {tt_r:,.0f} | {tt_u/HARI:,.1f} unit/hari",
      "- Catatan: TikTok Seller Center MENCAKUP order Tokopedia (±39% dari unit TikTok).",
      "  Tokopedia tidak pernah terhitung di laporan v1.", "",
      "DIAGNOSTIK FILE TIKTOK"]
for tk, d_ in diag.items():
    T.append(f"- {tk}: {d_['baris']:,} baris | batal/refund {d_['tolak']:,} | motor {d_['motor']:,} | "
             f"produk lain {d_['lain']:,} | dihitung {d_['hitung']:,}")
T += ["", "CATATAN PEMBACAAN",
      "- Blok Detail Strip = qty per label Strip apa adanya, DI LUAR Warna Polos.",
      "- Blok Detail Premium/Exclusive = rincian per warna KHUSUS tier itu,",
      "  SUBSET dari Warna Polos (jangan dijumlah dobel).",
      "- Total Warna Polos = jumlah 6 kolom warna yg ditampilkan saja (Silver dll tidak masuk).",
      "- Semua % dihitung terhadap Total Kuantitas model ybs.",
      "- Estimasi Stok = Rata-rata/Hari x 7, dibulatkan ke atas. Asumsi permintaan konstan,",
      "  BUKAN inventory-turnover baku.", "",
      "UC SHOPEE MARET SUDAH TERMASUK",
      "- Diuji dgn file Maret asli (5.881 baris, 4.479 unit): 0 pelanggaran pada uji (model)",
      "  dan (model, warna); uji musiman & ekstrapolasi baris motor/batal semuanya konsisten",
      "  dgn Maret SUDAH terhitung di v1. Maret TIDAK ditambahkan lagi agar tidak dobel.", "",
      "YANG MASIH BELUM MASUK",
      "- Lazada Otonation & Otoprotection (folder tidak ada di Drive).",
      "- TikTok Otonation (folder tidak ada di Drive).",
      "- Lazada umumnya hanya 160 baris order di v1 - kemungkinan export belum lengkap.",
      "- Angka ini PENJUALAN, bukan PRODUKSI (motor, order batal yang terlanjur dibuat,",
      "  produk non-cover, dan order di luar marketplace tidak dihitung)."]
for i, t in enumerate(T, 2):
    cc = mt.cell(row=i, column=1, value=t)
    if t and not t.startswith(("-", " ")):
        cc.font = Font(bold=True)
mt.column_dimensions["A"].width = 100

out.save(OUT)
print(f"\n-> {OUT}")
print(f"   Top 300 Mobil     : {len(peringkat)} model x {len(KOL)} kolom")
print(f"   Detail Gen & Warna: {n:,} baris")
print(f"   GRAND TOTAL       : {GRAND_U:,.0f} unit | {GRAND_U/HARI:,.2f}/hari")
