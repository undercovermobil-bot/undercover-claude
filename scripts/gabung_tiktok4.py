# -*- coding: utf-8 -*-
"""
v3: gabungkan penjualan TikTok DARI 3 TOKO (Undercover, Otoprotection, Smartprotection)
ke laporan MOBIL_TERLARIS. Output FILE BARU, file asli tidak disentuh.
"""
import openpyxl, datetime, re, collections, math
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from nama_tiktok import bersih, norm, bangun_index, cocokkan
from selaras_gen import Penyelaras

UP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/'
LAP = UP + 'fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx'
TT_FILES = [
    (UP + '3f5f928f-Semua_pesanan2026080513_44.xlsx', 'Undercover'),
    (UP + 'bd590f02-Semua_pesanan2026080514_02_Otopro.xlsx', 'Otoprotection'),
    (UP + '76aed148-Semua_pesanan2026080514_04_Smartpro.xlsx', 'Smartprotection'),
]
OUT = 'MOBIL_TERLARIS_v4_final.xlsx'
HARI = 181
AWAL, AKHIR = datetime.date(2026, 1, 1), datetime.date(2026, 6, 30)
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")
TYPO = {"undervover": "Undercover", "exxclusive": "Exclusive", "otoprotecion": "Otoprotection"}


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


def pecah_var(variasi):
    v = str(variasi or "")
    mg = re.search(r'(Gen\s*[^,]*)', v, flags=re.I)
    gen = mg.group(1).strip() if mg else ""
    w = re.split(r',', v)[0].strip()
    return ("" if re.match(r'gen', w, flags=re.I) else w), gen


def jenis_dari_tier(t):
    if t in ("Elite", "Epic", "Warrior") or t.startswith("Strip"):
        return "Strip"
    return t if t in ("Reguler", "Premium", "Exclusive", "Transparan") else "Reguler"


# ---------- laporan lama ----------
wl = openpyxl.load_workbook(LAP, data_only=True)
wt = wl["Top 300 Mobil"]
lama = {}
for r in range(6, wt.max_row + 1):
    no = wt.cell(row=r, column=1).value
    nm = wt.cell(row=r, column=2).value
    if isinstance(no, (int, float)) and nm:
        lama[str(nm).strip()] = (num(wt.cell(row=r, column=3).value), num(wt.cell(row=r, column=5).value))
penuh, tm = bangun_index(list(lama))
wdet = wl["Detail Gen & Warna"]
hdet = {str(wdet.cell(row=3, column=c).value).strip(): c for c in range(1, wdet.max_column + 1)}
SEL = Penyelaras(wdet, hdet)
n_gen_lain = 0

# ---------- baca semua file TikTok ----------
tt_model = collections.Counter(); tt_rp = collections.Counter()
tt_detail = collections.Counter(); tt_detail_rp = collections.Counter()
toko_u = collections.Counter(); toko_rp = collections.Counter()
toko_bulan = collections.defaultdict(collections.Counter)
chan = collections.Counter(); jenis_ct = collections.Counter()
sku_isi = collections.Counter(); sku_tot = collections.Counter()
sku_isi_toko = collections.Counter(); sku_tot_toko = collections.Counter()
typo_ket = collections.Counter(); baru = collections.Counter()
model_toko = collections.defaultdict(collections.Counter)
diag = {}

for path, toko in TT_FILES:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["OrderSKUList"]
    h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}
    d_ = dict(baris=0, tolak=0, motor=0, lain=0, luar=0, qty0=0, hitung=0, unit=0.0, nilai=0.0,
              tmin=None, tmax=None)
    for r in range(3, ws.max_row + 1):
        nm = ws.cell(row=r, column=h["Product Name"]).value
        if nm is None:
            continue
        d_["baris"] += 1
        dt = tgl(ws.cell(row=r, column=h["Created Time"]).value)
        if dt:
            d_["tmin"] = dt if d_["tmin"] is None or dt < d_["tmin"] else d_["tmin"]
            d_["tmax"] = dt if d_["tmax"] is None or dt > d_["tmax"] else d_["tmax"]
        st = (str(ws.cell(row=r, column=h["Order Status"]).value or "") + " " +
              str(ws.cell(row=r, column=h["Order Substatus"]).value or "")).lower()
        if any(t in st for t in TOLAK):
            d_["tolak"] += 1; continue
        if dt is None or not (AWAL <= dt <= AKHIR):
            d_["luar"] += 1; continue
        q = num(ws.cell(row=r, column=h["Quantity"]).value) - num(ws.cell(row=r, column=h["Sku Quantity of return"]).value)
        if q <= 0:
            d_["qty0"] += 1; continue
        nama = str(nm); low = nama.lower()
        for t in TYPO:
            if t in low:
                typo_ket[(t, TYPO[t], toko)] += q
        if re.search(r'\b(cover|sarung|selimut)\b.*\bmotor\b', low) or "sepeda motor" in low:
            d_["motor"] += 1; continue
        if "mobil" not in low and "car cover" not in low:
            d_["lain"] += 1; continue

        v = num(ws.cell(row=r, column=h["SKU Subtotal After Discount"]).value)
        mentah, tier = bersih(nama)
        kunci = cocokkan(mentah, penuh, tm)
        if kunci is None:
            kunci = mentah if mentah else "(tanpa nama)"
            baru[kunci] += q
        jenis = jenis_dari_tier(tier)
        warna, gen = pecah_var(ws.cell(row=r, column=h["Variation"]).value)
        # SELARASKAN ke kosakata laporan (gambar 2): Gen baku per model + warna baku
        gen = SEL.gen(kunci, gen) or "(tanpa gen)"
        warna = SEL.warna(warna) or "(tanpa warna)"
        if gen == "Model/Tahun Lain":
            n_gen_lain += 1

        d_["hitung"] += 1; d_["unit"] += q; d_["nilai"] += v
        tt_model[kunci] += q; tt_rp[kunci] += v
        model_toko[kunci][toko] += q
        tt_detail[(kunci, jenis, gen, warna, toko)] += q
        tt_detail_rp[(kunci, jenis, gen, warna, toko)] += v
        toko_u[toko] += q; toko_rp[toko] += v
        jenis_ct[jenis] += q
        chan[str(ws.cell(row=r, column=h["Purchase Channel"]).value or "")] += q
        k = f"{dt.year}-{dt.month:02d}"
        toko_bulan[toko][k] += q
        sku_tot[k] += 1; sku_tot_toko[toko] += 1
        if str(ws.cell(row=r, column=h["Seller SKU"]).value or "").strip():
            sku_isi[k] += 1; sku_isi_toko[toko] += 1
    diag[toko] = d_
    print(f"{toko:16s} baris={d_['baris']:5,} tolak={d_['tolak']:5,} luar={d_['luar']:4,} "
          f"motor={d_['motor']:4,} lain={d_['lain']:4,} -> {d_['unit']:6,.0f} unit  "
          f"Rp {d_['nilai']:>14,.0f}  ({d_['tmin']} s/d {d_['tmax']})")

U_TT = sum(tt_model.values()); R_TT = sum(tt_rp.values())
print(f"\nTOTAL TikTok 3 toko: {U_TT:,.0f} unit | Rp {R_TT:,.0f} | {U_TT/HARI:,.2f}/hari")
print(f"model tidak ada di Top300 v1: {len(baru)} ({sum(baru.values()):,.0f} unit)")

# ---------- gabung ----------
gab = {nm: [q, rp, 0.0, 0.0] for nm, (q, rp) in lama.items()}
for m, q in tt_model.items():
    gab.setdefault(m, [0.0, 0.0, 0.0, 0.0])
    gab[m][2] += q; gab[m][3] += tt_rp[m]
baris = sorted(([nm] + v + [v[0] + v[2], v[1] + v[3]] for nm, v in gab.items()), key=lambda x: -x[5])
TOT_U = sum(b[5] for b in baris); TOT_R = sum(b[6] for b in baris)

# ---------- tulis ----------
out = openpyxl.Workbook()
H1 = Font(bold=True, size=14); HB = Font(bold=True, color="FFFFFF")
F1 = PatternFill("solid", fgColor="2F5597"); F2 = PatternFill("solid", fgColor="C00000")
MERAH = Font(bold=True, color="C00000")


def hdr(ws, row, cols, fill):
    for i, c in enumerate(cols, 1):
        x = ws.cell(row=row, column=i, value=c)
        x.font = HB; x.fill = fill
        x.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")


def fmt(ws, r1, r2, kol, f):
    for c in kol:
        for r in range(r1, r2 + 1):
            ws.cell(row=r, column=c).number_format = f


s1 = out.active; s1.title = "Top Model Gabungan"
s1["A1"] = "MOBIL TERLARIS v4 — Shopee + Lazada + TikTok/Tokopedia 3 toko (1 Jan – 30 Jun 2026, 181 hari)"
s1["A1"].font = H1
s1["A2"] = (f"TOTAL {TOT_U:,.0f} unit | Rp {TOT_R:,.0f} | {TOT_U/HARI:,.1f} unit/hari"
            f"     (v1: 27.229 unit / 150,4 per hari)")
s1["A2"].font = MERAH
COLS = ["No", "Nama Mobil", "Unit Shopee+Lazada", "Unit TikTok", "TOTAL Unit", "% Kuantitas",
        "Nilai Shopee+Lazada (Rp)", "Nilai TikTok (Rp)", "TOTAL Nilai (Rp)",
        "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan", "Estimasi Stok (7 hari)",
        "TikTok UA", "TikTok OP", "TikTok SP", "Sumber"]
hdr(s1, 4, COLS, F1)
for i, (nm, q1, r1_, q2, r2_, qt, rt) in enumerate(baris, 1):
    rr = i + 4; d = qt / HARI
    src = "Shopee+TikTok" if q1 > 0 and q2 > 0 else ("TikTok saja (BARU)" if q2 > 0 else "Shopee+Lazada")
    mt = model_toko.get(nm, {})
    for c, v in enumerate([i, nm, q1, q2, qt, qt / TOT_U, r1_, r2_, rt, d, d * 7, d * 30,
                           math.ceil(d * 7), mt.get("Undercover", 0), mt.get("Otoprotection", 0),
                           mt.get("Smartprotection", 0), src], 1):
        s1.cell(row=rr, column=c, value=v)
    if q2 > 0:
        s1.cell(row=rr, column=4).font = MERAH
    if q1 == 0:
        s1.cell(row=rr, column=17).font = MERAH
rr = len(baris) + 5
s1.cell(row=rr, column=2, value="TOTAL").font = Font(bold=True)
for c, v in ((3, sum(b[1] for b in baris)), (4, U_TT), (5, TOT_U), (6, 1),
             (7, sum(b[2] for b in baris)), (8, R_TT), (9, TOT_R),
             (10, TOT_U / HARI), (11, TOT_U / HARI * 7), (12, TOT_U / HARI * 30),
             (14, toko_u["Undercover"]), (15, toko_u["Otoprotection"]), (16, toko_u["Smartprotection"])):
    s1.cell(row=rr, column=c, value=v).font = Font(bold=True)
fmt(s1, 5, rr, (6,), "0.000%"); fmt(s1, 5, rr, (3, 4, 5, 7, 8, 9, 13, 14, 15, 16), "#,##0")
fmt(s1, 5, rr, (10, 11, 12), "#,##0.00")
s1.freeze_panes = "C5"; s1.auto_filter.ref = f"A4:Q{rr-1}"

s2 = out.create_sheet("Detail TikTok")
s2["A1"] = "Rincian penjualan TikTok/Tokopedia per toko / model / jenis cover / gen / warna"; s2["A1"].font = H1
hdr(s2, 3, ["Toko", "Nama Mobil", "Jenis Cover", "Gen", "Warna", "Kuantitas", "Nilai (Rp)",
            "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan", "Estimasi Stok (7 hari)"], F2)
det = sorted(tt_detail.items(), key=lambda x: -x[1])
for i, ((m, j, g, w, tk), q) in enumerate(det, 1):
    d = q / HARI
    for c, v in enumerate([tk, m, j, g, w, q, tt_detail_rp[(m, j, g, w, tk)], d, d * 7, d * 30,
                           math.ceil(d * 7)], 1):
        s2.cell(row=i + 3, column=c, value=v)
fmt(s2, 4, len(det) + 3, (6, 7, 11), "#,##0"); fmt(s2, 4, len(det) + 3, (8, 9, 10), "#,##0.00")
s2.freeze_panes = "B4"; s2.auto_filter.ref = f"A3:K{len(det)+3}"

s3 = out.create_sheet("Ringkasan per Toko")
s3["A1"] = "KONTRIBUSI TIKTOK PER TOKO"; s3["A1"].font = H1
hdr(s3, 3, ["Toko", "Unit", "Nilai (Rp)", "Unit/Hari", "Harga rata-rata", "% dari TikTok",
            "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "SKU terisi"], F1)
BLN = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
for i, (tk, u) in enumerate(toko_u.most_common(), 1):
    rr = i + 3
    pct = sku_isi_toko[tk] / sku_tot_toko[tk] if sku_tot_toko[tk] else 0
    vals = [tk, u, toko_rp[tk], u / HARI, toko_rp[tk] / u, u / U_TT] + [toko_bulan[tk][b] for b in BLN] + [pct]
    for c, v in enumerate(vals, 1):
        s3.cell(row=rr, column=c, value=v)
rr = len(toko_u) + 4
s3.cell(row=rr, column=1, value="TOTAL").font = Font(bold=True)
for c, v in ((2, U_TT), (3, R_TT), (4, U_TT / HARI), (5, R_TT / U_TT), (6, 1)):
    s3.cell(row=rr, column=c, value=v).font = Font(bold=True)
for i, b in enumerate(BLN):
    s3.cell(row=rr, column=7 + i, value=sum(toko_bulan[t][b] for t in toko_u)).font = Font(bold=True)
fmt(s3, 4, rr, (2, 3, 5, 7, 8, 9, 10, 11, 12), "#,##0"); fmt(s3, 4, rr, (4,), "#,##0.00")
fmt(s3, 4, rr, (6, 13), "0.0%")
for i, w in enumerate([20, 10, 18, 11, 15, 13, 9, 9, 9, 9, 9, 9, 11], 1):
    s3.column_dimensions[get_column_letter(i)].width = w

s4 = out.create_sheet("Ringkasan & Catatan")
s4["A1"] = "RINGKASAN PERUBAHAN v1 → v4"; s4["A1"].font = H1
T = ["", "SUMBER DATA",
     "  v1 (Shopee 33.369 baris + Lazada 160 baris) : 27.229 unit | Rp 8.022.510.728 | 150,4/hari"]
for tk, u in toko_u.most_common():
    T.append(f"  TikTok {tk:16s}: {u:6,.0f} unit | Rp {toko_rp[tk]:>14,.0f} | {u/HARI:5,.1f}/hari")
T += [f"  TikTok TOTAL 3 toko                         : {U_TT:,.0f} unit | Rp {R_TT:,.0f} | {U_TT/HARI:,.1f}/hari",
      f"  GABUNGAN v4                                 : {TOT_U:,.0f} unit | Rp {TOT_R:,.0f} | {TOT_U/HARI:,.1f}/hari",
      f"  Kenaikan dari v1: +{U_TT/27229*100:.1f}% unit, +{R_TT/8022510728*100:.1f}% nilai",
      "", "DIAGNOSTIK PER FILE TIKTOK"]
for tk, d_ in diag.items():
    T.append(f"  {tk}: {d_['baris']:,} baris | batal/refund {d_['tolak']:,} | luar periode {d_['luar']:,} | "
             f"motor {d_['motor']:,} | produk lain {d_['lain']:,} | dihitung {d_['hitung']:,}")
    T.append(f"      rentang tanggal: {d_['tmin']} s/d {d_['tmax']}")
T += ["", "PERIODE", "  1 Jan – 30 Jun 2026 = 181 hari, terkonfirmasi dari Created Time ketiga file.",
      "", "ATURAN (sama persis dgn Metodologi v1)",
      "  - status dikeluarkan: batal/cancel/belum bayar/return/refund/gagal/lost",
      "  - Kuantitas = Quantity − Sku Quantity of return",
      "  - Nilai = SKU Subtotal After Discount (NET setelah diskon)",
      "  - hanya COVER MOBIL; motor & produk lain dikecualikan",
      "", "TEMUAN PENTING", "  1. TikTok Seller Center MENCAKUP TOKOPEDIA:"]
for k, v in chan.most_common():
    T.append(f"       {k:12s} {v:6,.0f} unit ({v/U_TT*100:.1f}%)")
T += ["     Tokopedia selama ini TIDAK PERNAH masuk laporan sama sekali.",
      "  2. Kolom 'Product Category' TikTok TIDAK BISA DIPERCAYA ('Kursi & Sarung Kursi'",
      "     berisi Body Cover Motor NMAX). Pemilahan pakai NAMA PRODUK, bukan kategori.",
      "  3. Kelengkapan Seller SKU per bulan (gabungan 3 toko):"]
for k in sorted(sku_tot):
    T.append(f"       {k}: {sku_isi[k]:4,}/{sku_tot[k]:4,} = {sku_isi[k]/sku_tot[k]*100:5.1f}%")
T += ["     Lonjakan Mei–Juni = hasil kerja SKU Sync.", "  4. TYPO di nama listing TikTok:"]
for (a, b, tk), q in typo_ket.most_common():
    T.append(f"       '{a}' → '{b}' di {tk} — {q:,.0f} unit")
T += ["  5. Pola nama produk beda antar toko — parser harus tahan banting:",
      "       Undercover  : 'Cover Mobil <model> <tier> - Undercover Autocare'",
      "                     ada juga urutan terbalik 'Toyota Rush - Autocare Undercover'",
      "       OP/SP       : 'Cover Mobil / Selimut Mobil <model>' (tanpa nama toko)",
      f"  6. {len(baru)} model TikTok tidak ada di Top 300 v1 ({sum(baru.values()):,.0f} unit),",
      "     ditandai 'TikTok saja (BARU)' di kolom Sumber.",
      "", "LUBANG YANG MASIH TERSISA",
      "  - Undercover/Shopee bulan Maret (masih .zip, tidak terbaca script v1)  → ~4.160 unit",
      "  - Lazada Otonation & Otoprotection (folder tidak ada di Drive)",
      "  - TikTok Otonation (folder TikTok tidak ada di Drive)",
      "", "POSISI TERHADAP KLAIM 200/HARI",
      f"  Sekarang {TOT_U/HARI:,.1f}/hari. Klaim 200/hari = 36.200 unit per 181 hari.",
      f"  Sisa lubang terbesar (UC Shopee Maret ~4.160 unit) → ~{(TOT_U+4160)/HARI:,.1f}/hari.",
      "", "CATATAN: angka ini PENJUALAN, bukan PRODUKSI. Produksi lebih besar karena motor,",
      "  order batal yang terlanjur dibuat, produk non-cover, dan order di luar marketplace",
      "  tidak dihitung di sini."]
for i, t in enumerate(T, 2):
    c = s4.cell(row=i, column=1, value=t)
    if t and not t.startswith(" "):
        c.font = Font(bold=True)
s4.column_dimensions["A"].width = 105

for sh, w in ((s1, [5, 32, 17, 12, 11, 11, 20, 18, 20, 13, 15, 14, 17, 11, 11, 11, 18]),
              (s2, [17, 30, 13, 24, 16, 11, 16, 13, 15, 14, 18])):
    for i, x in enumerate(w, 1):
        sh.column_dimensions[get_column_letter(i)].width = x

out.save(OUT)
print(f"\n-> {OUT}")
print(f"   model gabungan {len(baris)} | detail {len(det)} baris")
print(f"   gen -> 'Model/Tahun Lain': {n_gen_lain:,} baris")
print(f"   GABUNGAN v4: {TOT_U:,.0f} unit | Rp {TOT_R:,.0f} | {TOT_U/HARI:,.1f}/hari")
