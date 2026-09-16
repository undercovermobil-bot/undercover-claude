"""Terapkan skema SKU berbasis FORMULA ke LISTING + MASTER.

Jalankan dry-run dulu:  python3 apply_formula_sku.py
Baru apply         :    python3 apply_formula_sku.py --apply
"""
import re, sys, json, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

import formula_config as FC

APPLY = "--apply" in sys.argv

CFG, BLOCKED = FC.load()

# ---------- pencocokan nama listing/master -> nama model di file formula ----------
FILLER = re.compile(r'benz|body|thenew|allnew|new\b')
BOILER = set((
    "undercover autocare otonation otoprotection smartprotection ottonation "
    "cover mobil selimut karpet body sarung reguler regular premium exclusive "
    "strip transparan outdoor indoor extreme out the all"
).split())


def _toks(name):
    s = FILLER.sub("", str(name).lower())
    s = re.sub(r'\(?(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|now|sekarang)\)?', ' ', s)
    s = re.sub(r'\((?:19|20)\d{2}\)', ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return [t for t in s.split() if t and t not in BOILER]


def _sig(name):
    return "".join(_toks(name))


CFG_SIG = {m: _sig(m) for m in CFG}
CFG_TOK = {m: set(_toks(m)) for m in CFG}
# nama yg DITUNDA juga dikenali, supaya barisnya sengaja dilewati (bukan salah match ke model lain)
BLK_SIG = {m: _sig(m) for m in BLOCKED}
BLK_TOK = {m: set(_toks(m)) for m in BLOCKED}

_cache = {}

# Nama tipe badan yg ditulis beda antara listing dan file formula.
# Tanpa ini, "Gran Max Minibus" tidak ketemu "Gran Max MB" lalu jatuh ke
# base "Daihatsu Gran Max" yg DITUNDA -> barisnya kelewat, tidak ikut diproses.
ALIAS_RE = [
    (re.compile(r'gran\s*max\s+minibus', re.I), "Gran Max MB"),
    (re.compile(r'gran\s*max\s+pick\s*-?\s*up', re.I), "Gran Max PU"),
    (re.compile(r'carry\s+pick\s*-?\s*up', re.I), "Carry Pickup"),
    (re.compile(r'carry\s+pu\b', re.I), "Carry Pickup"),
]


def _prenorm(name):
    s = str(name)
    for rx, rep in ALIAS_RE:
        s = rx.sub(rep, s)
    return s


def match_model(name):
    """-> (nama_model, 'ok'|'blocked') atau (None, None)"""
    key = str(name)
    if key in _cache:
        return _cache[key]
    name = _prenorm(name)
    q, qt = _sig(name), set(_toks(name))
    res = (None, None)
    if len(q) >= 4:
        cands = []
        for src, sigs, toks, tag in ((CFG, CFG_SIG, CFG_TOK, "ok"), (BLOCKED, BLK_SIG, BLK_TOK, "blocked")):
            for m in src:
                cs, ct = sigs[m], toks[m]
                if not cs:
                    continue
                if cs == q or ct == qt:
                    cands.append((3, 0, len(cs), m, tag))
                elif q in cs or qt <= ct:
                    extra = (len(cs) - len(q)) if q in cs else sum(len(t) for t in ct - qt)
                    cands.append((2, -extra, len(cs), m, tag))
                elif cs in q or ct <= qt:
                    cands.append((1, len(cs), len(cs), m, tag))
        if cands:
            cands.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
            res = (cands[0][3], cands[0][4])
    _cache[key] = res
    return res


# Segmen GENERASI (ke-5) sengaja dibolehkan huruf besar-kecil campur: sebagian SKU lama
# memakai nama tipe bodi sbg segmen generasi (mis. MNI-COO-UA-R-Roadster-BRU,
# MNI-COO-SP-S-Hatch3Pintu-S3M). Kalau dipaksa huruf besar semua, baris2 itu ditolak
# sbg "bukan format standar" lalu TIDAK ikut diperbaiki. Segmen lain tetap ketat.
MASTERFMT = re.compile(r'^[A-Z0-9]+-[A-Z0-9]+-(UA|OT|SP|OP)-[A-Z]-[A-Za-z0-9]+-[A-Z0-9]+$')

LISTINGS = [
    ("UA", "Shopee1", "Informasi Penjualan Shopee Undercover 1 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("UA", "Shopee2", "Informasi Penjualan Shopee Undercover 2 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("UA", "Shopee3", "Informasi Penjualan Shopee Undercover 3 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("UA", "Shopee4", "Informasi Penjualan Shopee Undercover 4 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("UA", "Shopee5", "Informasi Penjualan Shopee Undercover 5 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("UA", "TikTok",  "Tiktok Semua Informasi Undercover 1 - SYNCED v3.xlsx", "Template", 3, 5, 11, 6, None),
    ("UA", "Lazada",  "Stok & Harga Lazada Undercover - SYNCED v3.xlsx", "template", 3, 14, 13, 5, 1),
    ("OT", "Shopee1", "Informasi Penjualan Shopee Otonation 1 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("OT", "Shopee2", "Informasi Penjualan Shopee Otonation 2 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("OT", "Shopee3", "Informasi Penjualan Shopee Otonation 3 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("OP", "Shopee1", "Informasi Penjualan Shopee Otoprotection 1 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("OP", "TikTok1", "Semua Informasi TikTok Otoprotection 1 - SYNCED v3.xlsx", "Template", 3, 5, 11, 6, None),
    ("OP", "TikTok2", "Semua Informasi TikTok Otoprotection 2 - SYNCED v3.xlsx", "Template", 3, 5, 11, 6, None),
    ("SP", "Shopee1", "Informasi Penjualan Shopee Smartpro 1 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("SP", "Shopee2", "Informasi Penjualan Shopee Smartpro 2 - SYNCED v3.xlsx", "Sheet1", 2, 4, 6, 7, None),
    ("SP", "TikTok",  "Semua Informasi TikTok Smartpro - SYNCED v3.xlsx", "Template", 3, 5, 11, 6, None),
    ("SP", "Lazada",  "Stok & Harga Lazada Smartpro - SYNCED v3.xlsx", "template", 3, 14, 13, 5, 1),
]
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]


def run(apply=False):
    stat = Counter()
    changes = []
    lazada_dupes = []

    # ---------------- LISTING ----------------
    for store, chan, fn, sheet, nc, vc, sc, sr, listc in LISTINGS:
        try:
            wbk = load_workbook(fn, data_only=(not apply))
            ws = wbk[sheet]
        except FileNotFoundError:
            stat["file_hilang"] += 1
            continue
        touched = False
        pending = []
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = str(nm).lower()
            if "karpet" in low or "motor" in low:
                continue
            model, tag = match_model(nm)
            if model is None:
                continue
            if tag == "blocked":
                stat["dilewati_model_ditunda"] += 1
                continue
            sku = ws.cell(row=r, column=sc).value
            if not (isinstance(sku, str) and MASTERFMT.match(sku)):
                stat["dilewati_sku_belum_standar"] += 1
                continue
            var = str(ws.cell(row=r, column=vc).value or "")
            newseg = FC.seg_for_variant(CFG[model], var)
            if not newseg:
                stat["varian_tak_terbaca"] += 1
                continue
            parts = sku.split("-")
            if parts[4] == newseg:
                stat["sudah_benar"] += 1
                continue
            newsku = "-".join(parts[:4] + [newseg] + parts[5:])
            pending.append((r, sku, newsku, model,
                            ws.cell(row=r, column=listc).value if listc else None))

        if listc:  # cek tabrakan SKU Lazada (1 listing tidak boleh punya SKU kembar)
            after = defaultdict(Counter)
            for r in range(sr, ws.max_row + 1):
                lst = ws.cell(row=r, column=listc).value
                cur = ws.cell(row=r, column=sc).value
                if cur not in (None, ""):
                    after[lst][cur] += 1
            for (r, old, new, model, lst) in pending:
                after[lst][old] -= 1
                after[lst][new] += 1
            for lst, c in after.items():
                for s, n in c.items():
                    if n > 1:
                        lazada_dupes.append([fn, str(lst), s, n])

        for (r, old, new, model, lst) in pending:
            if apply:
                ws.cell(row=r, column=sc, value=new)
            touched = True
            stat["listing_diubah"] += 1
            changes.append([model, store, chan, old, new])
        if apply and touched:
            wbk.save(fn)

    # ---------------- MASTER ----------------
    for mf in MASTERS:
        try:
            wbm = load_workbook(mf, data_only=False)
        except FileNotFoundError:
            continue
        touched = False
        for sn in wbm.sheetnames:
            ws = wbm[sn]
            for r in range(2, ws.max_row + 1):
                nm = ws.cell(row=r, column=2).value
                gen = ws.cell(row=r, column=6).value
                yr = ws.cell(row=r, column=7).value
                sku = ws.cell(row=r, column=9).value
                if not nm or not isinstance(sku, str) or not MASTERFMT.match(sku):
                    continue
                model, tag = match_model(nm)
                if model is None or tag == "blocked":
                    continue
                vartext = f"{gen or ''} ({yr or ''})"
                newseg = FC.seg_for_variant(CFG[model], vartext)
                if not newseg:
                    continue
                parts = sku.split("-")
                if parts[4] == newseg:
                    continue
                ws.cell(row=r, column=9, value="-".join(parts[:4] + [newseg] + parts[5:]))
                touched = True
                stat[f"master_diubah[{mf[:12]}]"] += 1
        if apply and touched:
            wbm.save(mf)

    print("=== HASIL ===")
    for k, v in stat.most_common():
        print(f"  {v:7}  {k}")
    bym = Counter(c[0] for c in changes)
    print(f"\nmodel terdampak (listing): {len(bym)}")
    for m, n in bym.most_common(20):
        print(f"  {n:6}  {m}")
    print(f"\nSKU kembar di Lazada setelah perubahan: {len(lazada_dupes)}")
    for d in lazada_dupes[:8]:
        print(f"   {d[1][:44]:44} {d[2]} x{d[3]}")
    json.dump({"changes": changes, "lazada_dupes": lazada_dupes, "blocked": BLOCKED},
              open("_formula_apply_result.json", "w"), ensure_ascii=False)
    print("\nmode:", "APPLY" if apply else "DRY-RUN")
    return stat, changes, lazada_dupes


if __name__ == "__main__":
    run(apply=APPLY)
