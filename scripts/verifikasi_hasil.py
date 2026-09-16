"""Verifikasi hasil akhir di BARU_FIX/ vs salinan pristine BARU_PRISTINE/.

Dipakai SETELAH seluruh pipeline. Menjawab 3 hal yg pernah salah dilaporkan:
  1. apakah file benar-benar BERUBAH (bukan cuma laporan dry-run),
  2. apakah motor sudah pakai format MTR & tidak ada sisa CM####,
  3. apakah SKU Lazada sudah unik per listing, dan Shopee/TikTok TIDAK ikut kena '_'.

JANGAN pernah menyimpulkan keberhasilan dari laporan skrip yg punya flag --apply:
angkanya identik di mode dry-run maupun apply.
"""
import warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter, defaultdict
import files_baru as FB

MTR = 0
CM = 0
print("=== A) FILE BERUBAH ATAU TIDAK ===")
tot_beda = 0
for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
    try:
        a = load_workbook(f"BARU_PRISTINE/{f}", data_only=True)[sheet]
    except FileNotFoundError:
        print(f"   {f:20} (tidak ada salinan pristine — lewati)")
        continue
    b = load_workbook(FB.path(f), data_only=True)[sheet]
    beda = 0
    for r in range(sr, max(a.max_row, b.max_row) + 1):
        if a.cell(row=r, column=sc).value != b.cell(row=r, column=sc).value:
            beda += 1
    tot_beda += beda
    print(f"   {f:20} {beda:6} sel SKU berubah")
print(f"   TOTAL sel SKU berubah: {tot_beda}")

print("\n=== B) MOTOR ===")
sisa_cm = []
for store, chan, fn, sheet, nc, vc, sc, sr in FB.MOTOR:
    ws = load_workbook(fn, data_only=True)[sheet]
    for r in range(sr, ws.max_row + 1):
        nm = ws.cell(row=r, column=nc).value
        if not nm or "cover motor" not in str(nm).lower():
            continue
        s = ws.cell(row=r, column=sc).value
        if isinstance(s, str) and "-MTR-" in s:
            MTR += 1
        else:
            CM += 1
            if len(sisa_cm) < 15:
                sisa_cm.append((fn.split("/")[-1], r, str(s), str(nm)[:50]))
print(f"   baris cover motor pakai -MTR- : {MTR}")
print(f"   belum                          : {CM}")
for x in sisa_cm:
    print("      ", x)

print("\n=== C) LAZADA UNIK + NON-LAZADA BERSIH ===")
for fn, sheet, listc, varc, skuc, sr in FB.LAZADA:
    ws = load_workbook(fn, data_only=True)[sheet]
    c = defaultdict(Counter)
    und = 0
    for r in range(sr, ws.max_row + 1):
        lst = ws.cell(row=r, column=listc).value
        s = ws.cell(row=r, column=skuc).value
        if lst in (None, "") or s in (None, ""):
            continue
        c[lst][s] += 1
        if "_" in str(s):
            und += 1
    dup = sum(1 for l in c for s, n in c[l].items() if n > 1)
    print(f"   {fn.split('/')[-1]:16} SKU kembar dalam 1 listing: {dup:5}   pakai '_': {und}")

kotor = 0
for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
    if chan == "Lazada":
        continue
    ws = load_workbook(FB.path(f), data_only=True)[sheet]
    n = sum(1 for r in range(sr, ws.max_row + 1)
            if isinstance(ws.cell(row=r, column=sc).value, str)
            and "_" in ws.cell(row=r, column=sc).value)
    if n:
        print(f"   !! {f} ada {n} SKU pakai '_' (harusnya 0)")
    kotor += n
print(f"   baris non-Lazada yg terkontaminasi '_': {kotor}")

print("\n=== D) FORMAT SKU AKHIR ===")
bad = Counter()
for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
    ws = load_workbook(FB.path(f), data_only=True)[sheet]
    for r in range(sr, ws.max_row + 1):
        s = ws.cell(row=r, column=sc).value
        if not isinstance(s, str) or not s.strip():
            continue
        base = s.split("_")[0]
        bad["6 segmen (benar)" if len(base.split("-")) == 6 else f"{len(base.split('-'))} segmen"] += 1
for k, v in bad.most_common():
    print(f"   {v:7}  {k}")
