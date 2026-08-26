import openpyxl, re
from collections import defaultdict

UPD = r"C:\Users\OWNER\Documents\Undercover\Undercover\Export Undercover ke Akun Claude Lain\List Produk SKU\Update via Claude"
BASE = r"C:\Users\OWNER\Documents\Undercover\Undercover\Export Undercover ke Akun Claude Lain\List Produk SKU"

# 1. master UA SKU set (also all-store set for reference)
wbm = openpyxl.load_workbook(UPD + r"\SKU, Price, Tracking Cover Mobil.xlsx", read_only=True)
master_skus = set()
for sh in wbm.sheetnames:
    ws = wbm[sh]
    for row in ws.iter_rows(min_row=3, values_only=True):
        if len(row) < 9: continue
        sku = row[8]
        if sku: master_skus.add(str(sku).strip())
print(f"master total distinct SKU: {len(master_skus)}")

# 2. top-331 set
wb = openpyxl.load_workbook(BASE + r"\MOBIL TERLARIS - Status Update SKU.xlsx", read_only=True)
ws = wb["COVER MOBIL"]
TERLARIS=set()
for row in ws.iter_rows(min_row=8, values_only=True):
    if row[1]: TERLARIS.add(str(row[1]).strip().lower())
def model_of(name):
    n=str(name)
    for p in ["Cover Mobil / Selimut Mobil ","Body Cover Mobil / Selimut Mobil ","Cover Mobil Transparan ","Cover Mobil ","Body Cover Mobil ","Cover Motor ","Body Cover Motor "]:
        if n.startswith(p): n=n[len(p):]; break
    n=re.sub(r'\s*\(J\)\s*$','',n); n=re.sub(r'\s*-\s*Undercover Autocare\s*$','',n)
    for t in [" Reguler"," Premium"," Exclusive"," Strip"]:
        if n.endswith(t): n=n[:-len(t)]
    return n.strip()
def is_top(m):
    ml=m.lower()
    return ml in TERLARIS or any(ml==t or ml.startswith(t) or t in ml for t in TERLARIS)

# 3. collect SKUs used in filled UA listing rows
files = [
 ("TikTok1", UPD + r"\List Produk Undercover\Tiktok Semua Informasi Undercover 1.xlsx","tiktok"),
 ("Shopee1", UPD + r"\List Produk Undercover\Informasi Penjualan Shopee Undercover 1.xlsx","shopee"),
 ("Shopee2", UPD + r"\List Produk Undercover\Informasi Penjualan Shopee Undercover 2.xlsx","shopee"),
 ("Shopee3", UPD + r"\List Produk Undercover\Informasi Penjualan Shopee Undercover 3.xlsx","shopee"),
 ("Shopee4", UPD + r"\List Produk Undercover\Informasi Penjualan Shopee Undercover 4.xlsx","shopee"),
 ("Shopee5", UPD + r"\List Produk Undercover\Informasi Penjualan Shopee Undercover 5.xlsx","shopee"),
 ("Lazada",  UPD + r"\List Produk Undercover\Stok & Harga Lazada Undercover.xlsx","lazada"),
]
def cols(fmt):
    if fmt=="tiktok": return ("Template",3,5,11,6)  # sheet, name, vari, sku, start
    if fmt=="shopee": return (None,2,4,6,7)
    return (None,2,None,13,5)  # lazada: name col2, sku col13

gap = {}  # sku -> (model, file, name, vari)
gap_skus_seen = set()
for label, path, fmt in files:
    try:
        wbf = openpyxl.load_workbook(path, read_only=True)
    except Exception as e:
        print(f"  skip {label}: {e}"); continue
    sheet,namei,varii,skui,start = cols(fmt)
    ws = wbf[sheet] if sheet else wbf[wbf.sheetnames[0]]
    for row in ws.iter_rows(min_row=start, values_only=True):
        if len(row) < skui: continue
        name = row[namei-1]; sku = row[skui-1]
        vari = row[varii-1] if varii and len(row)>=varii else None
        if not (name and sku and str(sku).strip()): continue
        sku=str(sku).strip()
        if sku in master_skus: continue
        if sku in gap_skus_seen: continue
        gap_skus_seen.add(sku)
        m = model_of(name)
        gap[sku] = (m, label, str(name), str(vari))

# 4. split by top-331 and by motor
gap_top = {s:v for s,v in gap.items() if is_top(v[0]) and 'Motor' not in v[2]}
gap_motor = {s:v for s,v in gap.items() if 'Motor' in v[2]}
gap_other = {s:v for s,v in gap.items() if s not in gap_top and s not in gap_motor}
print(f"\nSKU dipakai listing UA tapi TIDAK ada di master: {len(gap)}")
print(f"  - top-331 (mobil): {len(gap_top)}")
print(f"  - motor:           {len(gap_motor)}")
print(f"  - lain (non-top):  {len(gap_other)}")

# group top gaps by model
bymodel = defaultdict(list)
for s,(m,f,n,v) in gap_top.items():
    bymodel[m].append((s,f,v))
print(f"\n=== Model top-331 dgn SKU gap (jumlah SKU), sorted ===")
for m in sorted(bymodel, key=lambda x:-len(bymodel[x])):
    print(f"   {len(bymodel[m]):4}  {m}")

# 5. write review xlsx
out = openpyxl.Workbook()
wso = out.active; wso.title="Gap SKU Master (top-331)"
wso.append(["SKU (ada di listing, tidak di master)","Model","File listing","Contoh Variasi"])
for s,(m,f,n,v) in sorted(gap_top.items(), key=lambda x:(x[1][0], x[0])):
    wso.append([s, m, f, v])
ws2 = out.create_sheet("Gap lain (non-top & motor)")
ws2.append(["SKU","Model","File","Variasi","Kategori"])
for s,(m,f,n,v) in sorted(gap_other.items()):
    ws2.append([s,m,f,v,"non-top"])
for s,(m,f,n,v) in sorted(gap_motor.items()):
    ws2.append([s,m,f,v,"motor"])
outpath = UPD + r"\Gap SKU Master - dari Listing UA (2026-07-15).xlsx"
out.save(outpath)
print(f"\nReview file disimpan: {outpath}")
