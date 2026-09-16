import json, ast, re, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

fwd_ua = {ast.literal_eval(k): v for k, v in json.load(open("master_lookup_full.json")).items()}
fwd_sp = {ast.literal_eval(k): v for k, v in json.load(open("master_lookup_sp.json")).items()}

def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())
FILLER = re.compile(r'benz|body|thenew|allnew|new\b')
def nm2(s): return re.sub(r'[^a-z0-9]', '', FILLER.sub('', str(s).lower()))
def dedup_brand(s):
    parts = str(s).split(); out = []
    for p in parts:
        if not out or out[-1].lower() != p.lower():
            out.append(p)
    return " ".join(out)
def canon_key(s): return nm2(dedup_brand(s))

# ---- master structure: gen-year per canonical model, gens present, model norm map ----
wbm = load_workbook("MASTER_from_drive_20260715.xlsx", data_only=True)
mgen_year = defaultdict(dict)          # canon_norm -> {gen: (ylo,yhi)}  (model-wide, legacy fallback)
mgen_year_kat = defaultdict(dict)      # (canon_norm, kategori) -> {gen: (ylo,yhi)}  (category-aware)
canon_of_norm = {}
for sn in wbm.sheetnames:
    ws = wbm[sn]
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=2).value
        kat = ws.cell(row=r, column=4).value
        gen = ws.cell(row=r, column=6).value
        yr = ws.cell(row=r, column=7).value
        if nm and gen:
            cn = canon_key(nm)
            canon_of_norm.setdefault(cn, str(nm).strip())
            if yr:
                ys = [int(x) for x in re.findall(r'((?:19|20)\d{2})', str(yr))]
                if ys:
                    mgen_year[cn].setdefault(str(gen).strip(), (ys[0], ys[-1]))
                    if kat:
                        mgen_year_kat[(cn, kat)].setdefault(str(gen).strip(), (ys[0], ys[-1]))

# canonical master model names from lookups (authoritative for keys)
canon_models = set(k[0] for k in list(fwd_ua) + list(fwd_sp))
canon_norms = {canon_key(m): m for m in canon_models}
canon_norm_list = sorted(canon_norms.keys(), key=lambda x: -len(x))

# --- token-based model matching (handles master name longer than listing, e.g.
#     master "Honda Brio Satya / RS" vs listing "Honda Brio") ---
BOILER = set((
    "undercover autocare otonation otoprotection smartprotection ottonation "
    "cover mobil selimut karpet body sarung reguler regular premium exclusive "
    "strip transparan outdoor indoor extreme out the all"
).split())
def _mtoks(name):
    s = FILLER.sub("", str(name).lower())
    # strip year-RANGES and parenthesized years only — a bare number can be the model
    # itself (Peugeot 2008/3008!), so never strip standalone 4-digit numbers
    s = re.sub(r'\(?(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|now)\)?', ' ', s)
    s = re.sub(r'\((?:19|20)\d{2}\)', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return [t for t in s.split() if t not in BOILER]
def model_sig(name):
    """concat of model tokens; handles hyphenation (HRV==HR-V)."""
    return "".join(_mtoks(name))
canon_sig = {m: model_sig(m) for m in canon_models}
canon_tok = {m: set(_mtoks(m)) for m in canon_models}

def master_model_of(name):
    q = model_sig(name)
    qt = set(_mtoks(name))
    if len(q) < 4:
        return None
    # combine two signals: concat-substring (hyphenation) + token-subset (word insertion,
    # e.g. listing "Toyota Altis" vs master "Toyota Corolla Altis")
    cands = []
    for m in canon_models:
        cs = canon_sig[m]; ct = canon_tok[m]
        if not cs:
            continue
        if cs == q or ct == qt:
            cands.append((3, 0, len(cs), m))                      # exact
        elif q in cs or qt <= ct:                                 # listing explained by canon
            extra = (len(cs) - len(q)) if q in cs else sum(len(t) for t in ct - qt)
            cands.append((2, -extra, len(cs), m))                 # prefer closest
        elif cs in q or ct <= qt:                                 # canon subset of listing
            cands.append((1, len(cs), len(cs), m))                # prefer most specific
    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0][3]

def gen_sig(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower().replace("facelift", "f"))

# gens available in the lookup for a canon model (per store)
gens_ua = defaultdict(set); gens_sp = defaultdict(set)
for (m, kat, g, c) in fwd_ua: gens_ua[m].add(g)
for (m, kat, g, c) in fwd_sp: gens_sp[m].add(g)
# same, but CATEGORY-specific: a gen label only "counts" for a (model,kategori) if the
# master actually has a combo for it -- fixes false matches like Sonata Transparan
# picking Reguler's "Gen 2" label (which has no Transparan combo at all)
gens_ua_kat = defaultdict(set); gens_sp_kat = defaultdict(set)
for (m, kat, g, c) in fwd_ua: gens_ua_kat[(m, kat)].add(g)
for (m, kat, g, c) in fwd_sp: gens_sp_kat[(m, kat)].add(g)

# ---- parsing ----
PLAIN = [("abu-abu","Abu-abu"),("abu abu","Abu-abu"),("biru benhur","Biru Benhur"),
         ("hijau army","Hijau Army"),("hijau","Hijau"),("biru","Biru"),("merah","Merah"),
         ("hitam","Hitam"),("orange","Orange"),("silver","Silver"),("abu","Abu-abu"),
         ("transparan","Transparan"),("mocha","Mocha"),("coffee","Coffee"),("coklat","Coklat")]
TIER_UA = {"epic":"Epic","elite":"Elite","warrior":"Warrior","warior":"Warrior"}
BASE = {"abu":"Abu","biru":"Biru","merah":"Merah"}

def _base_of(cl):
    for b in ["merah", "biru", "abu"]:
        if b in cl:
            return {"abu": "Abu", "biru": "Biru", "merah": "Merah"}[b]
    return None
EPIC_RE = re.compile(r'\b(epic|epik|epi)\b')
ELITE_RE = re.compile(r'\b(elite|elit|elita|eite|elt|elie)\b')
WAR_RE = re.compile(r'\b(warrior|warior|warror|wrior|wrrior|warri|warr)\b')

def parse_color(v, store):
    # color part = comma-segments WITHOUT a gen/year token
    segs = [s.strip() for s in re.split(r'[,]', v) if s.strip()]
    colorsegs = [s for s in segs if not re.search(r'gen ?\d|(?:19|20)\d{2}|\d{4}', s.lower())]
    cl = " ".join(colorsegs).lower() if colorsegs else v.lower()
    if "transparan" in cl:
        return "Transparan", "Transparan", "any"
    base = _base_of(cl)
    if base:
        # canonical strip tier number (1=Epic/Strip1, 2=Elite/Strip2, 3=Warrior/Strip3),
        # parsed from EITHER naming style (variant naming is independent of SKU scheme)
        tier_n = None
        ms = re.search(r'(?:strip|strp|srtip|stip|srip)\s*([123])', cl)
        if ms:
            tier_n = int(ms.group(1))
        elif EPIC_RE.search(cl):  tier_n = 1
        elif ELITE_RE.search(cl): tier_n = 2
        elif WAR_RE.search(cl):   tier_n = 3
        if tier_n:
            if store in ("UA", "OT"):
                color = f"{ {1:'Epic',2:'Elite',3:'Warrior'}[tier_n] } {base}".replace("  ", " ")
            else:
                color = f"Strip {tier_n} {base}"
            return "Strip", color, store
    for key, val in PLAIN:
        if key in cl and val != "Transparan":
            return "PLAIN", val, "any"
    return None, None, None

def parse_kat_from_name(name):
    nl = name.lower()
    if "exclusive" in nl: return "Exclusive"
    if "premium" in nl: return "Premium"
    if "reguler" in nl or "regular" in nl: return "Reguler"
    return None

def is_dual_scheme(gens):
    """gen set mixes 'Gen N' labels with non-'Gen' labels (chassis/named) -> ambiguous, skip auto"""
    has_genN = any(gen_sig(g).startswith("gen") for g in gens)
    has_nonGen = any(not gen_sig(g).startswith("gen") for g in gens)
    return has_genN and has_nonGen

def parse_gen(v, canon, store, kat=None):
    """return (gen_label, confidence) ; confidence: exact / year / single / None"""
    gens = None
    if kat is not None:
        gens = gens_ua_kat[(canon, kat)] if store in ("UA", "OT") else gens_sp_kat[(canon, kat)]
        if not gens:
            gens = gens_ua_kat[(canon, kat)] or gens_sp_kat[(canon, kat)]
    if not gens:
        # fall back to model-wide gens (old behaviour) if this category has no data of its own
        gens = gens_ua[canon] if store in ("UA", "OT") else gens_sp[canon]
        if not gens: gens = gens_ua[canon] or gens_sp[canon]
    if not gens:
        return None, None
    # dual-scheme models (both 'Gen N' and chassis/named gens) are too ambiguous -> skip
    if is_dual_scheme(gens):
        return None, "dual_skip"
    # extract gen phrase: prefer "Gen ..." token, else the token before "(year)"
    gphrase = None
    m = re.search(r'(gen[\w ]*?)(?:\(|,|$)', v, re.I)
    if m:
        gphrase = m.group(1).strip()
    else:
        m2 = re.search(r'([A-Za-z0-9/]+)\s*\((?:19|20)\d{2}', v)
        if m2:
            gphrase = m2.group(1).strip()
    has_explicit = bool(re.search(r'gen ?\d', v, re.I)) or bool(re.search(r'(?:19|20)\d{2}', v))
    # 1) YEAR-RANGE match FIRST — authoritative, because listings number generations
    #    on a different scale than the master (e.g. listing "Gen 2 (1988-1993)" == master Gen 6).
    ckey = canon_key(canon)
    ys = [int(x) for x in re.findall(r'((?:19|20)\d{2})', v)]
    yr_table = mgen_year_kat.get((ckey, kat)) if kat is not None else None
    if not yr_table:
        yr_table = mgen_year.get(ckey)  # fallback: category had no year data of its own
    if len(ys) >= 2 and yr_table:
        ylo, yhi = ys[0], ys[-1]
        avail = [(g, a, b) for g, (a, b) in yr_table.items() if g in gens]
        # (a) exact start+end
        exact = [g for g, a, b in avail if a == ylo and b == yhi]
        if len(exact) == 1:
            return exact[0], "year"
        # (b) exact START year (generations are keyed by their start year; handles
        #     numbering mismatch AND combined ranges -> earliest gen wins by its start)
        starts = [g for g, a, b in avail if a == ylo]
        if len(starts) == 1:
            return starts[0], "year"
        # (c) combined range ("Gen 1-3", "Gen 1&2", or span covering >=2 gens) -> earliest
        combined = bool(re.search(r'gen\s*\d+\s*[-&]\s*\d+', v, re.I))
        overlapping = [(a, g) for g, a, b in avail if max(ylo, a) <= min(yhi, b)]
        if combined and overlapping:
            overlapping.sort()
            return overlapping[0][1], "year"
        # (d) best-overlap fallback (safe: per-model trust gate rejects any model this misfires on)
        scored = sorted(((min(yhi, b) - max(ylo, a), g) for g, a, b in avail
                         if max(ylo, a) <= min(yhi, b)), reverse=True)
        if len(scored) == 1 or (len(scored) >= 2 and scored[0][0] > scored[1][0]):
            return scored[0][1], "year"
        # (e) no confident year match -> skip
    # 2) exact gen-signature match (only when NO year range to rely on)
    if gphrase and not (len(ys) >= 2):
        gsig = gen_sig(gphrase)
        exact = [g for g in gens if gen_sig(g) == gsig]
        if len(exact) == 1:
            return exact[0], "exact"
    # 3) single gen product — ONLY if variant gives no explicit gen/year clue
    if len(gens) == 1 and not has_explicit:
        return next(iter(gens)), "single"
    return None, None

def resolve_sku(store, name, var):
    """return (sku, status). status: ok / no_model / no_gen / no_color / no_master_key / derived"""
    canon = master_model_of(name)
    if canon is None:
        return None, "no_model"
    kat_c, color, scheme = parse_color(var, store)
    if color is None and "transparan" in name.lower():
        # listing name itself says Transparan (unambiguous, no color choice) but the
        # variant text only has "Gen N (years)" with no repeated color/category word
        kat_c, color, scheme = "Transparan", "Transparan", "any"
    if color is None:
        return None, "no_color"
    if kat_c == "PLAIN":
        kat = parse_kat_from_name(name) or "Reguler"
    else:
        kat = kat_c  # Strip / Transparan
    gen, conf = parse_gen(var, canon, store, kat)
    if gen is None:
        return None, ("dual_skip" if conf == "dual_skip" else "no_gen")
    if store in ("UA", "OT"):
        sku = fwd_ua.get((canon, kat, gen, color))
        return (sku, "ok:" + conf) if sku else (None, "no_master_key")
    else:  # SP / OP
        sku = fwd_sp.get((canon, kat, gen, color))
        if sku:
            return sku, "ok:" + conf
        # derive from UA if SP lookup lacks it
        if kat == "Strip":
            m = re.match(r'Strip (\d) (\w+)', color)
            if m:
                tier = {"1": "Epic", "2": "Elite", "3": "Warrior"}[m.group(1)]
                ua_color = f"{tier} {m.group(2)}"
                ua = fwd_ua.get((canon, "Strip", gen, ua_color))
                if ua:
                    parts = ua.split("-"); parts[2] = "SP"
                    parts[-1] = f"S{m.group(1)}{m.group(2)[0]}"
                    return "-".join(parts), "derived:" + conf
        else:
            ua = fwd_ua.get((canon, kat, gen, color))
            if ua:
                parts = ua.split("-"); parts[2] = "SP"
                return "-".join(parts), "derived"
        return None, "no_master_key"

# ================= VALIDATION: reproduce existing valid SKUs =================
FILES = [
    ("UA", "Sheet1", "Informasi Penjualan Shopee Undercover 1 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("UA", "Sheet1", "Informasi Penjualan Shopee Undercover 2 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("UA", "Sheet1", "Informasi Penjualan Shopee Undercover 3 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("UA", "Sheet1", "Informasi Penjualan Shopee Undercover 4 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("UA", "Sheet1", "Informasi Penjualan Shopee Undercover 5 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("UA", "Template", "Tiktok Semua Informasi Undercover 1 - SYNCED v3.xlsx", 3, 5, 11, 6),
    ("OT", "Sheet1", "Informasi Penjualan Shopee Otonation 1 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("OT", "Sheet1", "Informasi Penjualan Shopee Otonation 2 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("OT", "Sheet1", "Informasi Penjualan Shopee Otonation 3 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("SP", "Sheet1", "Informasi Penjualan Shopee Smartpro 1 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("SP", "Sheet1", "Informasi Penjualan Shopee Smartpro 2 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("SP", "Template", "Semua Informasi TikTok Smartpro - SYNCED v3.xlsx", 3, 5, 11, 6),
    ("OP", "Sheet1", "Informasi Penjualan Shopee Otoprotection 1 - SYNCED v3.xlsx", 2, 4, 6, 7),
    ("OP", "Template", "Semua Informasi TikTok Otoprotection 2 - SYNCED v3.xlsx", 3, 5, 11, 6),
]
MASTERFMT = re.compile(r'^[A-Z]{2,5}-[A-Z0-9]+-(UA|SP)-[RSPET]-[A-Za-z0-9]+-[A-Z0-9]+$')
GENERIC = re.compile(r'lain|custom|default', re.I)

if __name__ == "__main__":
    match = 0; mismatch = 0; couldnt = 0
    mism_ex = []
    for store, sheet, fn, nc, vc, sc, sr in FILES:
        wb = load_workbook(fn, data_only=True); ws = wb[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm or "motor" in str(nm).lower() or "karpet" in str(nm).lower(): continue
            var = str(ws.cell(row=r, column=vc).value or "")
            sku = ws.cell(row=r, column=sc).value
            if GENERIC.search(var): continue
            if not (isinstance(sku, str) and MASTERFMT.match(sku)): continue  # only validate on already-valid
            got, st = resolve_sku(store, str(nm), var)
            if got == sku:
                match += 1
            elif got is None:
                couldnt += 1
            else:
                mismatch += 1
                if len(mism_ex) < 25:
                    mism_ex.append((store, str(nm)[:34], var[:30], sku, got, st))
    tot = match + mismatch + couldnt
    print(f"VALIDATION on already-valid rows: total={tot}")
    print(f"  MATCH (reproduced exactly): {match}  ({100*match//max(tot,1)}%)")
    print(f"  MISMATCH (WRONG sku!):      {mismatch}  ({100*mismatch//max(tot,1)}%)")
    print(f"  couldn't resolve:           {couldnt}  ({100*couldnt//max(tot,1)}%)")
    print()
    print("=== MISMATCH examples (these would be BUGS) ===")
    for e in mism_ex:
        print(f"  [{e[0]}] {e[1]:34} | {e[2]:30} | actual={e[3]} got={e[4]} ({e[5]})")
