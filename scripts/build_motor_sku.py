"""Bangun SKU baru produk MOTOR (format final, keputusan user 2026-07-27).

Format : MEREK-MODEL-TOKO-KATEGORI-MTR-WARNA   (6 segmen, penanda 'MTR')
Contoh : HND-VAR125-UA-R-MTR-ABU

Keputusan user:
  - Opsi B dipilih -> 6 segmen, ada penanda 'MTR' (bentuknya seragam dgn SKU mobil)
  - Premium motor warnanya ABU ("sama seperti premiumnya cover mobil")
  - Produk 'Maxi' diabaikan dulu
  - Motor hanya dijual di Undercover Autocare -> segmen toko selalu 'UA'

Kategori : R=Reguler(polos)  S=Strip(Elite)  P=Premium
Warna    : ABU HTM MRH BRU GRN | Elite: EAB EBR EGR EMR
"""
import re, sys, json, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

APPLY = "--apply" in sys.argv

BRAND_CODE = {
    "Honda": "HND", "Suzuki": "SZK", "BMW": "BMW",          # sama dgn mobil
    "Yamaha": "YMH", "Kawasaki": "KWS", "Benelli": "BNL", "Ducati": "DCT",
    "Vespa": "VSP", "KTM": "KTM", "Aprilia": "APR", "Cleveland": "CLV",
    "BF Goodrich": "BFG", "Alrendo": "ALR", "Bajaj": "BJJ",
}
BRANDS = sorted(BRAND_CODE, key=len, reverse=True)
SKIP_MODELS = {"Maxi"}          # user: abaikan dulu

FILES = [
    ("UA", "Shopee3", "Informasi Penjualan Shopee Undercover 3 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7),
    ("UA", "Shopee4", "Informasi Penjualan Shopee Undercover 4 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7),
    ("UA", "TikTok",  "Tiktok Semua Informasi Undercover 1 - SYNCED v3.xlsx", "Template", 3, 5, 11, 6),
]
CM_RE = re.compile(r'^CM0*(\d+)-')
KAT_RE = re.compile(r'\b(reguler|regular|premium|exclusive|transparan)\b', re.I)
BOIL = re.compile(r'undercover autocare|otonation|otoprotection|smartprotection'
                  r'|(body\s+)?cover|sarung|selimut|motor|\((j|jumbo|xl|l|m|s)\)', re.I)


def parse_name(nm):
    """-> (nama_model, kategori)"""
    s = str(nm)
    mk = KAT_RE.search(s)
    kat = mk.group(1).capitalize().replace("Regular", "Reguler") if mk else "Reguler"
    s = KAT_RE.sub(" ", s)
    s = BOIL.sub(" ", s)
    s = re.sub(r'[-/]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip(" -/"), kat


def split_brand(name):
    for b in BRANDS:
        if name.lower().startswith(b.lower()):
            return b, name[len(b):].strip()
    return None, name


STOP = {"the", "new", "all", "i", "get"}


def _tok(t):
    if t.isdigit():
        return t
    if re.search(r'\d', t):
        return t.upper()[:7]          # CB150, KLX150SM, R15, H2
    return t[:3].upper()              # Ninja -> NIN


def model_code(rest):
    toks = [t for t in re.split(r'[^A-Za-z0-9]+', rest) if t and t.lower() not in STOP]
    out = ""
    for t in toks:
        p = _tok(t)
        if out and len(out) + len(p) > 10:
            break
        out += p
    return out or "XXX"


def color_code(var):
    """-> (kode_kategori, kode_warna) atau (None, None)"""
    t = var.strip().lower()
    if not t or t == "default":
        return "P", "ABU"                     # Premium: satu-satunya, user konfirmasi ABU
    base = None
    for k, c in (("abu", "ABU"), ("hitam", "HTM"), ("merah", "MRH"),
                 ("biru", "BRU"), ("hijau", "GRN")):
        if k in t:
            base = c
            break
    if base is None:
        return None, None
    if re.search(r'elite|elit|eite', t):
        return "S", {"ABU": "EAB", "BRU": "EBR", "GRN": "EGR", "MRH": "EMR"}[base]
    return "R", base


def build():
    """kumpulkan katalog motor + tetapkan kode model unik per merek"""
    rows = []
    for store, chan, fn, sheet, nc, vc, sc, sr in FILES:
        ws = load_workbook(fn, data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm or "cover motor" not in str(nm).lower():
                continue
            model, kat = parse_name(nm)
            if not model or model in SKIP_MODELS:
                continue
            sku = ws.cell(row=r, column=sc).value
            m = CM_RE.match(str(sku or ""))
            rows.append({"store": store, "chan": chan, "fn": fn, "row": r,
                         "listing": str(nm), "model": model, "kat": kat,
                         "var": str(ws.cell(row=r, column=vc).value or ""),
                         "old": sku, "cm": int(m.group(1)) if m else None})

    # satukan ejaan nama lewat nomor CM (mis. 'Aerox' & 'Yamaha Aerox' -> satu nama)
    by_cm = defaultdict(Counter)
    for x in rows:
        if x["cm"] is not None:
            by_cm[x["cm"]][x["model"]] += 1

    def score(n):
        return (1 if any(n.lower().startswith(b.lower()) for b in BRANDS) else 0, len(n))

    canon_by_cm = {cm: sorted(c, key=score, reverse=True)[0] for cm, c in by_cm.items()}
    canon_names = set(canon_by_cm.values())
    idx = {re.sub(r'[^a-z0-9]', '', n.lower()): n for n in canon_names}

    def canon(x):
        if x["cm"] is not None:
            return canon_by_cm[x["cm"]]
        k = re.sub(r'[^a-z0-9]', '', x["model"].lower())
        if k in idx:
            return idx[k]
        c = [n for kk, n in idx.items() if k and (kk.endswith(k) or k in kk)]
        return sorted(c, key=len)[0] if c else x["model"]

    for x in rows:
        x["canon"] = canon(x)

    codes = defaultdict(dict)
    for name in sorted({x["canon"] for x in rows}):
        b, rest = split_brand(name)
        if b is None:
            continue
        c = model_code(rest)
        used = set(codes[b].values())
        if c in used:
            i = 2
            while f"{c}{i}" in used:
                i += 1
            c = f"{c}{i}"
        codes[b][name] = c

    for x in rows:
        b, _ = split_brand(x["canon"])
        if b is None:
            x["new"] = None
            continue
        kc, cc = color_code(x["var"])
        x["new"] = f"{BRAND_CODE[b]}-{codes[b][x['canon']]}-UA-{kc}-MTR-{cc}" if kc else None
    return rows, codes


def run(apply=False):
    rows, codes = build()
    stat = Counter()
    for x in rows:
        stat["siap" if x["new"] else "tak_bisa_ditentukan"] += 1
    if apply:
        for fn in {x["fn"] for x in rows}:
            wbk = load_workbook(fn, data_only=False)
            meta = next(f for f in FILES if f[2] == fn)
            ws = wbk[meta[3]]
            n = 0
            for x in rows:
                if x["fn"] == fn and x["new"]:
                    ws.cell(row=x["row"], column=meta[6], value=x["new"])
                    n += 1
            if n:
                wbk.save(fn)
    uniq = {x["new"] for x in rows if x["new"]}
    print("=== SKU MOTOR (format 6 segmen + MTR) ===")
    for k, v in stat.most_common():
        print(f"  {v:6}  {k}")
    print(f"  model unik : {sum(len(v) for v in codes.values())}")
    print(f"  SKU unik   : {len(uniq)}")
    json.dump([{k: v for k, v in x.items() if k != 'fn'} for x in rows],
              open("_motor_new_sku.json", "w"), ensure_ascii=False)
    json.dump({b: dict(v) for b, v in codes.items()},
              open("_motor_codes.json", "w"), ensure_ascii=False)
    print("mode:", "APPLY" if apply else "DRY-RUN")
    return rows, codes


if __name__ == "__main__":
    run(apply=APPLY)
