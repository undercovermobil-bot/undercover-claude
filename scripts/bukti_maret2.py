# -*- coding: utf-8 -*-
"""
Uji tegas tahap 2: granularitas (model, jenis cover, gen, warna) dari sheet Detail.
Kalau Maret UC saja > angka laporan pada kombinasi mana pun, Maret pasti belum masuk.
"""
import openpyxl, re, collections
from nama_tiktok import bersih, norm, bangun_index, cocokkan
from bukti_maret import angka  # reuse parser angka Indonesia

UP = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/'
LAP = UP + 'fbc7083b-MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx'
MAR = [UP + '490ea489-Order.all.20260301_20260331_part_1_of_2.xlsx',
       UP + '9febc200-Order.all.20260301_20260331_part_2_of_2.xlsx']
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")

wl = openpyxl.load_workbook(LAP, data_only=True)

# --- daftar model laporan ---
wt = wl["Top 300 Mobil"]
lap_model = {}
for r in range(6, wt.max_row + 1):
    no = wt.cell(row=r, column=1).value
    nm = wt.cell(row=r, column=2).value
    if isinstance(no, (int, float)) and nm:
        lap_model[str(nm).strip()] = angka(wt.cell(row=r, column=3).value)
penuh, tm = bangun_index(list(lap_model))

# --- sheet Detail: (model, jenis, gen, warna) ---
wd = wl["Detail Gen & Warna"]
hd = {str(wd.cell(row=3, column=c).value).strip(): c for c in range(1, wd.max_column + 1)}
lap_det = collections.Counter()
lap_mw = collections.Counter()      # (model, warna)
lap_mg = collections.Counter()      # (model, gen)
vocab_gen = collections.defaultdict(collections.Counter)
vocab_warna = collections.defaultdict(collections.Counter)
vocab_jenis = collections.Counter()
for r in range(4, wd.max_row + 1):
    m = wd.cell(row=r, column=hd["Nama Mobil"]).value
    if not m:
        continue
    m = str(m).strip()
    j = str(wd.cell(row=r, column=hd["Jenis Cover"]).value or "").strip()
    g = str(wd.cell(row=r, column=hd["Gen"]).value or "").strip()
    w = str(wd.cell(row=r, column=hd["Warna"]).value or "").strip()
    q = angka(wd.cell(row=r, column=hd["Kuantitas"]).value)
    lap_det[(m, j, g, w)] += q
    lap_mw[(m, w)] += q
    lap_mg[(m, g)] += q
    vocab_gen[m][g] += q
    vocab_warna[m][w] += q
    vocab_jenis[j] += q

print("KOSAKATA LAPORAN (sheet Detail)")
print(f"  jenis cover : {dict(vocab_jenis)}")
print(f"  contoh Gen Toyota Avanza  : {list(vocab_gen.get('Toyota Avanza', {}))}")
print(f"  contoh Warna Toyota Avanza: {list(vocab_warna.get('Toyota Avanza', {}))[:14]}")

# --- baca Maret UC dgn granularitas sama ---
TIERS = [("Exclusive", r"ex+clusive"), ("Premium", r"premium"), ("Reguler", r"regul[ae]r"),
         ("Transparan", r"transparan"), ("Elite", r"elite"), ("Epic", r"epic"), ("Warrior", r"warrior")]


def jenis_dari(nama, warna):
    s = (nama + " " + warna).lower()
    for lab, pat in TIERS:
        if re.search(r'\b' + pat + r'\b', s):
            return "Strip" if lab in ("Elite", "Epic", "Warrior") else lab
    if re.search(r'\bstrip\s*[123]\b', s):
        return "Strip"
    return "Reguler"


mar_det = collections.Counter()
mar_mw = collections.Counter()
mar_model = collections.Counter()
mar_gen_mentah = collections.Counter()
mar_warna_mentah = collections.Counter()

for path in MAR:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["orders"]
    h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=h["Nama Produk"]).value
        if nm is None:
            continue
        st = (str(ws.cell(row=r, column=h["Status Pesanan"]).value or "") + " " +
              str(ws.cell(row=r, column=h["Status Pembatalan/ Pengembalian"]).value or "")).lower()
        if any(x in st for x in TOLAK):
            continue
        q = angka(ws.cell(row=r, column=h["Jumlah"]).value) - angka(ws.cell(row=r, column=h["Returned quantity"]).value)
        if q <= 0:
            continue
        nama = str(nm)
        low = nama.lower()
        if re.search(r'\b(cover|sarung|selimut)\b.*\bmotor\b', low) or "sepeda motor" in low:
            continue
        if "mobil" not in low and "car cover" not in low:
            continue
        var = str(ws.cell(row=r, column=h["Nama Variasi"]).value or "")
        bag = [x.strip() for x in var.split(",")]
        warna = bag[0] if bag else ""
        gen = ""
        for b in bag[1:]:
            if re.match(r'gen|model|tahun', b, flags=re.I):
                gen = b
                break
        mentah, tier = bersih(nama)
        k = cocokkan(mentah, penuh, tm) or mentah
        j = jenis_dari(nama, warna)
        mar_det[(k, j, gen, warna)] += q
        mar_mw[(k, warna)] += q
        mar_model[k] += q
        mar_gen_mentah[gen] += q
        mar_warna_mentah[warna] += q

print()
print("=" * 76)
print("UJI TEGAS: kombinasi (model, jenis, gen, warna)")
print("=" * 76)
langgar = [(k, v, lap_det[k]) for k, v in mar_det.items() if k in lap_det and v > lap_det[k]]
langgar.sort(key=lambda x: -(x[1] - x[2]))
hilang = [(k, v) for k, v in mar_det.items() if k not in lap_det]
print(f"  kombinasi Maret        : {len(mar_det):,}")
print(f"  ada di laporan         : {sum(1 for k in mar_det if k in lap_det):,}")
print(f"  MELANGGAR (Maret>v1)   : {len(langgar)}  ({sum(a-b for _,a,b in langgar):,.0f} unit kelebihan)")
print(f"  TIDAK ADA di laporan   : {len(hilang)}  ({sum(v for _,v in hilang):,.0f} unit)")
print()
if langgar:
    print(f"  {'model / jenis / gen / warna':52s} {'Mar':>6s} {'v1':>6s}")
    for (m, j, g, w), a, b in langgar[:20]:
        print(f"  {(m+' | '+j+' | '+g+' | '+w)[:52]:52s} {a:6,.0f} {b:6,.0f}")
    print()
    print("  >> TERBUKTI: Maret TIDAK termasuk di laporan v1.")
else:
    print("  >> tidak ada pelanggaran pada granularitas ini.")

print()
print("=" * 76)
print("UJI (model, warna)")
print("=" * 76)
l2 = [(k, v, lap_mw[k]) for k, v in mar_mw.items() if k in lap_mw and v > lap_mw[k]]
l2.sort(key=lambda x: -(x[1] - x[2]))
print(f"  MELANGGAR: {len(l2)}")
for (m, w), a, b in l2[:15]:
    print(f"    {(m+' | '+w)[:46]:46s} Maret {a:5,.0f} > v1 {b:5,.0f}")

print()
print("KOSAKATA MARET (utk penyelarasan format nanti)")
print(f"  Gen (10 teratas)  : {[g for g,_ in mar_gen_mentah.most_common(10)]}")
print(f"  Warna (14 teratas): {[w for w,_ in mar_warna_mentah.most_common(14)]}")
