# -*- coding: utf-8 -*-
"""
v2: gabungkan penjualan TikTok ke laporan MOBIL_TERLARIS.
Output FILE BARU: MOBIL_TERLARIS_v2_plus_TikTok.xlsx (file asli tidak disentuh).
"""
import openpyxl, datetime, re, collections, math
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from nama_tiktok import bersih, norm, bangun_index, cocokkan

LAP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx'
TT = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/3f5f928f-Semua_pesanan2026080513_44.xlsx'
OUT = 'MOBIL_TERLARIS_v2_plus_TikTok.xlsx'
HARI = 181
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")
TYPO = {"undervover": "Undercover", "exxclusive": "Exclusive", "regular": "Reguler",
        "autocar ": "Autocare", "otoprotecion": "Otoprotection"}


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
    gen = ""
    mg = re.search(r'(Gen\s*[^,]*)', v, flags=re.I)
    if mg:
        gen = mg.group(1).strip()
    w = re.split(r',', v)[0].strip()
    if re.match(r'gen', w, flags=re.I):
        w = ""
    return w, gen


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

# ---------- TikTok ----------
wb = openpyxl.load_workbook(TT, data_only=True)
ws = wb["OrderSKUList"]
h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}

tt_model = collections.Counter(); tt_rp = collections.Counter()
tt_detail = collections.Counter(); tt_detail_rp = collections.Counter()
tt_jenis = collections.Counter(); chan = collections.Counter()
bulan = collections.Counter(); sku_isi = collections.Counter(); sku_tot = collections.Counter()
typo_ket = collections.Counter()
baru = collections.Counter()
n_motor = n_lain = n_tolak = 0
u_motor = 0.0

for r in range(3, ws.max_row + 1):
    nm = ws.cell(row=r, column=h["Product Name"]).value
    if nm is None:
        continue
    st = (str(ws.cell(row=r, column=h["Order Status"]).value or "") + " " +
          str(ws.cell(row=r, column=h["Order Substatus"]).value or "")).lower()
    if any(t in st for t in TOLAK):
        n_tolak += 1
        continue
    q = num(ws.cell(row=r, column=h["Quantity"]).value) - num(ws.cell(row=r, column=h["Sku Quantity of return"]).value)
    if q <= 0:
        continue
    nama = str(nm)
    low = nama.lower()
    for t in TYPO:
        if t in low:
            typo_ket[(t, TYPO[t])] += q
    if re.search(r'\b(cover|sarung|selimut)\b.*\bmotor\b', low) or "sepeda motor" in low:
        n_motor += 1; u_motor += q
        continue
    if "mobil" not in low and "car cover" not in low:
        n_lain += 1
        continue

    v = num(ws.cell(row=r, column=h["SKU Subtotal After Discount"]).value)
    mentah, tier = bersih(nama)
    kunci = cocokkan(mentah, penuh, tm)
    if kunci is None:
        kunci = mentah if mentah else "(tanpa nama)"
        baru[kunci] += q
    jenis = jenis_dari_tier(tier)
    warna, gen = pecah_var(ws.cell(row=r, column=h["Variation"]).value)

    tt_model[kunci] += q; tt_rp[kunci] += v
    tt_jenis[jenis] += q
    tt_detail[(kunci, jenis, gen, warna)] += q
    tt_detail_rp[(kunci, jenis, gen, warna)] += v
    chan[str(ws.cell(row=r, column=h["Purchase Channel"]).value or "")] += q
    d = tgl(ws.cell(row=r, column=h["Created Time"]).value)
    if d:
        k = f"{d.year}-{d.month:02d}"
        bulan[k] += q; sku_tot[k] += 1
        if str(ws.cell(row=r, column=h["Seller SKU"]).value or "").strip():
            sku_isi[k] += 1

U_TT = sum(tt_model.values()); R_TT = sum(tt_rp.values())

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
s1["A1"] = "MOBIL TERLARIS v2 — Shopee + Lazada + TikTok/Tokopedia (1 Jan – 30 Jun 2026, 181 hari)"
s1["A1"].font = H1
s1["A2"] = f"TOTAL {TOT_U:,.0f} unit  |  Rp {TOT_R:,.0f}  |  {TOT_U/HARI:,.1f} unit/hari   (v1: 27.229 unit, 150,4/hari)"
s1["A2"].font = MERAH
COLS = ["No", "Nama Mobil", "Unit Shopee+Lazada", "Unit TikTok", "TOTAL Unit", "% Kuantitas",
        "Nilai Shopee+Lazada (Rp)", "Nilai TikTok (Rp)", "TOTAL Nilai (Rp)",
        "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan", "Estimasi Stok (7 hari)", "Sumber"]
hdr(s1, 4, COLS, F1)
for i, (nm, q1, r1_, q2, r2_, qt, rt) in enumerate(baris, 1):
    rr = i + 4; d = qt / HARI
    src = "Shopee+TikTok" if q1 > 0 and q2 > 0 else ("TikTok saja (BARU)" if q2 > 0 else "Shopee+Lazada")
    for c, v in enumerate([i, nm, q1, q2, qt, qt / TOT_U, r1_, r2_, rt, d, d * 7, d * 30, math.ceil(d * 7), src], 1):
        s1.cell(row=rr, column=c, value=v)
    if q2 > 0:
        s1.cell(row=rr, column=4).font = MERAH
    if q1 == 0:
        s1.cell(row=rr, column=14).font = MERAH
rr = len(baris) + 5
s1.cell(row=rr, column=2, value="TOTAL").font = Font(bold=True)
for c, v in ((3, sum(b[1] for b in baris)), (4, U_TT), (5, TOT_U), (6, 1),
             (7, sum(b[2] for b in baris)), (8, R_TT), (9, TOT_R),
             (10, TOT_U / HARI), (11, TOT_U / HARI * 7), (12, TOT_U / HARI * 30)):
    s1.cell(row=rr, column=c, value=v).font = Font(bold=True)
fmt(s1, 5, rr, (6,), "0.000%"); fmt(s1, 5, rr, (3, 4, 5, 7, 8, 9, 13), "#,##0")
fmt(s1, 5, rr, (10, 11, 12), "#,##0.00")
s1.freeze_panes = "C5"; s1.auto_filter.ref = f"A4:N{rr-1}"

s2 = out.create_sheet("Detail TikTok")
s2["A1"] = "Rincian penjualan TikTok/Tokopedia per model / jenis cover / gen / warna"; s2["A1"].font = H1
hdr(s2, 3, ["Nama Mobil", "Jenis Cover", "Gen", "Warna", "Kuantitas", "Nilai (Rp)",
            "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan", "Estimasi Stok (7 hari)"], F2)
det = sorted(tt_detail.items(), key=lambda x: -x[1])
for i, ((m, j, g, w), q) in enumerate(det, 1):
    d = q / HARI
    for c, v in enumerate([m, j, g, w, q, tt_detail_rp[(m, j, g, w)], d, d * 7, d * 30, math.ceil(d * 7)], 1):
        s2.cell(row=i + 3, column=c, value=v)
fmt(s2, 4, len(det) + 3, (5, 6, 10), "#,##0"); fmt(s2, 4, len(det) + 3, (7, 8, 9), "#,##0.00")
s2.freeze_panes = "A4"; s2.auto_filter.ref = f"A3:J{len(det)+3}"

s3 = out.create_sheet("Ringkasan & Catatan")
s3["A1"] = "RINGKASAN PERUBAHAN v1 → v2"; s3["A1"].font = H1
T = [
    "", "SUMBER DATA",
    f"  v1 (Shopee 33.369 baris + Lazada 160 baris) : 27.229 unit | Rp 8.022.510.728 | 150,4/hari",
    f"  TikTok Undercover (BARU)                    : {U_TT:,.0f} unit | Rp {R_TT:,.0f} | {U_TT/HARI:,.1f}/hari",
    f"  GABUNGAN v2                                 : {TOT_U:,.0f} unit | Rp {TOT_R:,.0f} | {TOT_U/HARI:,.1f}/hari",
    f"  Kenaikan: +{U_TT/27229*100:.1f}% unit, +{R_TT/8022510728*100:.1f}% nilai",
    "", "PERIODE",
    "  1 Jan – 30 Jun 2026 = 181 hari. Terkonfirmasi dari Created Time file TikTok:",
    "  rentang 2026-01-01 s/d 2026-06-30, NOL baris di luar periode.",
    "", "ATURAN (sama persis dgn Metodologi v1)",
    "  - status dikeluarkan: batal/cancel/belum bayar/return/refund/gagal/lost",
    "  - Kuantitas = Quantity − Sku Quantity of return",
    "  - Nilai = SKU Subtotal After Discount (NET setelah diskon)",
    "  - hanya COVER MOBIL; motor & produk lain dikecualikan",
    f"  Dilewati dari file TikTok: {n_tolak:,} baris batal/refund, {n_motor:,} baris motor ({u_motor:,.0f} unit), {n_lain:,} baris produk lain",
    "", "TEMUAN PENTING",
    "  1. TikTok Seller Center MENCAKUP TOKOPEDIA:",
]
for k, v in chan.most_common():
    T.append(f"       {k:12s} {v:6,.0f} unit ({v/U_TT*100:.1f}%)")
T += [
    "     Tokopedia selama ini TIDAK PERNAH masuk laporan sama sekali.",
    "  2. Kolom 'Product Category' TikTok TIDAK BISA DIPERCAYA:",
    "     'Kursi & Sarung Kursi' berisi Body Cover Motor NMAX; 'Radiator...' berisi",
    "     Cover Motor Benelli. File ini memilah pakai NAMA PRODUK, bukan kategori.",
    "  3. Kelengkapan Seller SKU pada order TikTok (membaik tajam):",
]
for k in sorted(sku_tot):
    T.append(f"       {k}: {sku_isi[k]:4,}/{sku_tot[k]:4,} = {sku_isi[k]/sku_tot[k]*100:5.1f}%")
T += [
    "     Lonjakan Mei–Juni = hasil kerja SKU Sync. Order menyimpan SKU saat transaksi,",
    "     jadi angka bulan lama tidak bisa diperbaiki surut.",
    "  4. TYPO ditemukan di nama listing TikTok:",
]
for (a, b), q in typo_ket.most_common():
    T.append(f"       '{a}' seharusnya '{b}'  — {q:,.0f} unit terdampak")
T += [
    f"  5. {len(baru)} model TikTok tidak ada di Top 300 v1 ({sum(baru.values()):,.0f} unit) — ditandai",
    "     'TikTok saja (BARU)' di kolom Sumber. Ini bagian 'ekor panjang' 446 model.",
    "", "YANG MASIH BELUM MASUK (lubang tersisa)",
    "  - TikTok Otoprotection & Smartprotection (4 file ada di Drive, belum di-export ulang)",
    "  - Undercover/Shopee bulan Maret (masih .zip, tidak terbaca script v1)",
    "  - Lazada Otonation & Otoprotection (folder tidak ada di Drive)",
    "", "PROYEKSI KALAU SEMUA LUBANG DITUTUP",
    "  ~40.400 unit → ~223 unit/hari.",
    "  Klaim 'rata-rata produksi 200/hari' = 36.200 unit per 181 hari: MASUK AKAL.",
    "", "CATATAN: angka ini PENJUALAN, bukan PRODUKSI. Produksi lebih besar karena motor,",
    "  order batal yang terlanjur dibuat, produk non-cover, dan order di luar marketplace",
    "  tidak dihitung di sini.",
]
for i, t in enumerate(T, 2):
    c = s3.cell(row=i, column=1, value=t)
    if t and not t.startswith(" "):
        c.font = Font(bold=True)
s3.column_dimensions["A"].width = 100

for sh, w in ((s1, [5, 32, 17, 12, 11, 11, 20, 18, 20, 13, 15, 14, 17, 18]),
              (s2, [32, 13, 24, 16, 11, 16, 13, 15, 14, 18])):
    for i, x in enumerate(w, 1):
        sh.column_dimensions[get_column_letter(i)].width = x

out.save(OUT)
print(f"-> {OUT}")
print(f"   model gabungan {len(baris)} | detail TikTok {len(det)} baris | model BARU {len(baru)}")
print(f"   TikTok  : {U_TT:,.0f} unit | Rp {R_TT:,.0f}")
print(f"   GABUNGAN: {TOT_U:,.0f} unit | Rp {TOT_R:,.0f} | {TOT_U/HARI:,.1f}/hari")
