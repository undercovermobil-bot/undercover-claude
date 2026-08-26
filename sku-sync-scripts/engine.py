import openpyxl, re
from collections import defaultdict, Counter

UPD = r"C:\Users\OWNER\Documents\Undercover\Undercover\Export Undercover ke Akun Claude Lain\List Produk SKU\Update via Claude"
BASE = r"C:\Users\OWNER\Documents\Undercover\Undercover\Export Undercover ke Akun Claude Lain\List Produk SKU"

# ---------- load top-331 ----------
wb = openpyxl.load_workbook(BASE + r"\MOBIL TERLARIS - Status Update SKU.xlsx", read_only=True)
ws = wb["COVER MOBIL"]
TERLARIS = set()
for row in ws.iter_rows(min_row=8, values_only=True):
    if row[1]: TERLARIS.add(str(row[1]).strip().lower())

# ---------- build master UA lookup ----------
wbm = openpyxl.load_workbook(UPD + r"\SKU, Price, Tracking Cover Mobil.xlsx", read_only=True)

def gen_numbers(label):
    """set of generation numbers implied by a master gen label."""
    s = str(label)
    nums = set(int(x) for x in re.findall(r'\d+', s))
    return nums

def norm_color_master(w):
    return str(w).strip()

# lookup[(model_lower, kat, warna)] = list of dicts {gen_label, gen_nums, facelift, years, sku}
lookup = defaultdict(list)
model_names = set()
for sh in wbm.sheetnames:
    wsm = wbm[sh]
    for row in wsm.iter_rows(min_row=3, values_only=True):
        if len(row) < 9: continue
        nama, toko, kat, warna, gen, rt, _, sku = row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
        if not (nama and toko == "Undercover Autocare" and sku): continue
        m = str(nama).strip().lower()
        model_names.add(m)
        years = None
        if rt:
            yy = re.findall(r'(19|20)\d{2}', str(rt))
            if yy:
                allnums = re.findall(r'((?:19|20)\d{2})', str(rt))
                years = (int(allnums[0]), int(allnums[-1]))
        lookup[(m, kat, norm_color_master(warna))].append({
            'gen_label': str(gen), 'gen_nums': gen_numbers(gen),
            'facelift': ('F' in str(gen) or 'acelift' in str(gen)),
            'years': years, 'sku': sku })

# ---------- aliases (model name TikTok -> master) ----------
ALIAS = {
 'suzuki carry pu': 'suzuki carry pick-up',
 'honda brv':'honda br-v','honda crv':'honda cr-v','honda hrv':'honda hr-v','honda wrv':'honda wr-v',
 'hyundai santa fe':'hyundai santa fe','mini cooper':'mini cooper',
 'nissan xtrail':'nissan x-trail','nissan x trail':'nissan x-trail',
}
def map_model(m):
    ml = m.lower().strip()
    if ml in ALIAS: return ALIAS[ml]
    return ml

# ---------- parse TikTok variation ----------
PRE = ["Cover Mobil / Selimut Mobil ","Body Cover Mobil / Selimut Mobil ","Cover Mobil Transparan ",
       "Cover Mobil ","Body Cover Mobil ","Cover Motor ","Body Cover Motor "]
TIERS = ["Reguler","Premium","Exclusive","Strip"]
def parse_name(name):
    n = str(name)
    is_motor = 'Cover Motor' in n or 'Body Cover Motor' in n
    for p in PRE:
        if n.startswith(p): n = n[len(p):]; break
    n = re.sub(r'\s*\(J\)\s*$','',n)
    n = re.sub(r'\s*-\s*Undercover Autocare\s*$','',n)
    name_tier = None
    for t in TIERS:
        if n.endswith(' '+t):
            name_tier = t; n = n[:-(len(t)+1)]; break
    return n.strip(), name_tier, is_motor

STRIP_PFX = ['Elite','Epic','Warrior','Warior']
def norm_strip_color(tok):
    tok = tok.replace('Warior','Warrior')
    tok = tok.replace('Abu-abu','Abu')
    return tok.strip()

def parse_variation(vari, name_tier):
    """return (kat, warna) or (None,None); plus gen_token."""
    if vari is None: return None, None, None
    parts = [p.strip() for p in str(vari).split(',')]
    color_tok = None; gen_tok = None
    for p in parts:
        if re.search(r'Gen|\b(19|20)\d{2}\b|^[A-Z]\d', p) and not any(p.startswith(s) for s in STRIP_PFX):
            if gen_tok is None: gen_tok = p
        else:
            if color_tok is None: color_tok = p
    # fallback: if two parts and one looks like gen
    if color_tok is None and parts: color_tok = parts[0]
    if color_tok is None: return None, None, gen_tok
    ct = color_tok.strip()
    # category
    if any(ct.startswith(s) for s in STRIP_PFX):
        kat = 'Strip'; warna = norm_strip_color(ct)
    elif ct.lower() == 'transparan':
        kat='Transparan'; warna='Transparan'
    elif ct.lower() == 'silver':
        kat='Premium'; warna='Silver'
    else:
        if name_tier == 'Premium': kat='Premium'
        elif name_tier == 'Exclusive': kat='Exclusive'
        else: kat='Reguler'
        warna = ct
    return kat, warna, gen_tok

def parse_gen_token(tok):
    if tok is None: return None, None, None
    s=str(tok)
    facelift = ('acelift' in s) or bool(re.search(r'\bF\b|F\d|\dF', s))
    m = re.search(r'Gen\s*(\d+)', s)
    num = int(m.group(1)) if m else None
    yrs = re.findall(r'((?:19|20)\d{2})', s)
    years = (int(yrs[0]), int(yrs[-1])) if yrs else None
    return num, facelift, years

def match(name, vari):
    model_raw, name_tier, is_motor = parse_name(name)
    if is_motor: return None, 'motor'
    model = map_model(model_raw)
    kat, warna, gen_tok = parse_variation(vari, name_tier)
    if kat is None: return None, 'no_color'
    cands = lookup.get((model, kat, warna))
    if not cands:
        # try alias-free / minor fixes
        return None, f'no_key({model}|{kat}|{warna})'
    if len(cands) == 1:
        return cands[0]['sku'], 'single'
    gnum, gfl, gyears = parse_gen_token(gen_tok)
    # match by gen number
    hits = [c for c in cands if gnum is not None and gnum in c['gen_nums']]
    if len(hits) == 1: return hits[0]['sku'], 'gennum'
    if len(hits) > 1:
        # tie-break by facelift flag
        hf = [c for c in hits if c['facelift']==gfl]
        if len(hf)==1: return hf[0]['sku'],'gennum+fl'
        # tie-break by year overlap
        if gyears:
            hy=[c for c in hits if c['years'] and not (gyears[1]<c['years'][0] or gyears[0]>c['years'][1])]
            if len(hy)==1: return hy[0]['sku'],'gennum+yr'
        return None, 'ambig_gen'
    # no gennum hit: try year overlap across all cands
    if gyears:
        hy=[c for c in cands if c['years'] and not (gyears[1]<c['years'][0] or gyears[0]>c['years'][1])]
        if len(hy)==1: return hy[0]['sku'],'year'
    return None, f'nogen({gen_tok})'

def is_top(model_raw):
    ml = model_raw.lower()
    return ml in TERLARIS or any(ml==t or ml.startswith(t) or t in ml for t in TERLARIS)

# ---------- VALIDATION against filled rows ----------
wt = openpyxl.load_workbook(UPD + r"\List Produk Undercover\Tiktok Semua Informasi Undercover 1.xlsx", read_only=True)
wst = wt["Template"]
val_total=val_match=val_mismatch=val_unres=0
mism_samples=[]; unres_reason=Counter()
blank_total=blank_fillable=0; blank_reason=Counter()
fill_samples=[]
for row in wst.iter_rows(min_row=6, values_only=True):
    if len(row)<11: continue
    name,vari,sku=row[2],row[4],row[10]
    if not name: continue
    model_raw,_,is_motor = parse_name(name)
    if is_motor: continue
    if not is_top(model_raw): continue
    if sku and str(sku).strip():
        val_total+=1
        computed,how = match(name,vari)
        if computed is None:
            val_unres+=1; unres_reason[how.split('(')[0]]+=1
        elif str(computed)==str(sku):
            val_match+=1
        else:
            val_mismatch+=1
            if len(mism_samples)<20: mism_samples.append((name,vari,sku,computed,how))
    else:
        blank_total+=1
        computed,how=match(name,vari)
        if computed is not None:
            blank_fillable+=1
            if len(fill_samples)<15: fill_samples.append((name,vari,computed,how))
        else:
            blank_reason[how.split('(')[0]]+=1

print("========== VALIDATION (top-331 FILLED rows) ==========")
print(f"total filled checked = {val_total}")
print(f"  MATCH   (computed==actual) = {val_match}  ({100*val_match//max(val_total,1)}%)")
print(f"  MISMATCH(computed!=actual) = {val_mismatch}")
print(f"  UNRESOLVED (couldn't compute) = {val_unres}")
print(f"  unresolved reasons: {dict(unres_reason)}")
print("\n  --- MISMATCH samples (BUGS to fix) ---")
for name,vari,actual,comp,how in mism_samples:
    print(f"   {name[:50]!r} | {vari!r}")
    print(f"       actual={actual}  computed={comp} ({how})")

print("\n========== DRY-RUN (top-331 BLANK rows) ==========")
print(f"blank top-331 = {blank_total}")
print(f"  FILLABLE = {blank_fillable}  ({100*blank_fillable//max(blank_total,1)}%)")
print(f"  not fillable reasons: {dict(blank_reason)}")
print("\n  --- sample proposed fills ---")
for name,vari,comp,how in fill_samples:
    print(f"   {name[:50]!r} | {vari!r} -> {comp} ({how})")
