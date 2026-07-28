"""Jalankan SELURUH pekerjaan SKU di atas file listing TERBARU (BARU_FIX/).

Urutan (penting — jangan diacak):
  1. Skema FORMULA utk cover mobil  (collapse->G1 / per-generasi; Mini Cooper->3P/5P)
  2. SKU MOTOR format baru          (MEREK-MODEL-UA-KAT-MTR-WARNA)
  3. Akhiran '_' utk Lazada         (supaya Seller SKU unik per listing)

Dijalankan dgn `--apply` utk menulis; tanpa itu = dry-run.
"""
import re, sys, json, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

import formula_config as FC
import files_baru as FB
import apply_formula_sku as AF          # dipakai utk match_model + MASTERFMT
import build_motor_sku as BM
import fix_motor_warna as FW

APPLY = "--apply" in sys.argv
CFG, BLOCKED = FC.load()
MASTERFMT = AF.MASTERFMT


# ---------------------------------------------------------------- 1) FORMULA
def step_formula(apply):
    stat = Counter()
    changes = []
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        fn = FB.path(f)
        wbk = load_workbook(fn, data_only=False)
        ws = wbk[sheet]
        touched = False
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = str(nm).lower()
            if "karpet" in low or "motor" in low:
                continue
            model, tag = AF.match_model(nm)
            if model is None:
                continue
            if tag == "blocked":
                stat["dilewati_model_ditunda"] += 1
                continue
            sku = ws.cell(row=r, column=sc).value
            if not (isinstance(sku, str) and MASTERFMT.match(sku)):
                stat["dilewati_sku_belum_standar"] += 1
                continue
            newseg = FC.seg_for_variant(CFG[model], str(ws.cell(row=r, column=vc).value or ""))
            if not newseg:
                stat["varian_tak_terbaca"] += 1
                continue
            p = sku.split("-")
            if p[4] == newseg:
                stat["sudah_benar"] += 1
                continue
            new = "-".join(p[:4] + [newseg] + p[5:])
            if apply:
                ws.cell(row=r, column=sc, value=new)
            touched = True
            stat["diubah"] += 1
            changes.append([model, store, chan, sku, new])
        if apply and touched:
            wbk.save(fn)
    return stat, changes


# ------------------------------------------------------------------ 2) MOTOR
def step_motor(apply):
    """pakai logika build_motor_sku tapi pada file baru"""
    rows = []
    for store, chan, fn, sheet, nc, vc, sc, sr in FB.MOTOR:
        ws = load_workbook(fn, data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm or "cover motor" not in str(nm).lower():
                continue
            model, kat = BM.parse_name(nm)
            if not model or model in BM.SKIP_MODELS:
                continue
            sku = ws.cell(row=r, column=sc).value
            m = BM.CM_RE.match(str(sku or ""))
            rows.append({"fn": fn, "sheet": sheet, "col": sc, "row": r,
                         "model": model, "kat": kat,
                         "var": str(ws.cell(row=r, column=vc).value or ""),
                         "old": sku, "cm": int(m.group(1)) if m else None})
    # satukan ejaan nama lewat nomor CM
    by_cm = defaultdict(Counter)
    for x in rows:
        if x["cm"] is not None:
            by_cm[x["cm"]][x["model"]] += 1

    def score(n):
        return (1 if any(n.lower().startswith(b.lower()) for b in BM.BRANDS) else 0, len(n))

    canon_by_cm = {cm: sorted(c, key=score, reverse=True)[0] for cm, c in by_cm.items()}
    idx = {re.sub(r'[^a-z0-9]', '', n.lower()): n for n in set(canon_by_cm.values())}

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
        b, rest = BM.split_brand(name)
        if b is None:
            continue
        c = BM.model_code(rest)
        used = set(codes[b].values())
        if c in used:
            i = 2
            while f"{c}{i}" in used:
                i += 1
            c = f"{c}{i}"
        codes[b][name] = c
    for x in rows:
        b, _ = BM.split_brand(x["canon"])
        if b is None:
            x["new"] = None
            continue
        kc, cc = BM.color_code(x["var"])
        x["new"] = f"{BM.BRAND_CODE[b]}-{codes[b][x['canon']]}-UA-{kc}-MTR-{cc}" if kc else None

    if apply:
        for fn in {x["fn"] for x in rows}:
            wbk = load_workbook(fn, data_only=False)
            grp = [x for x in rows if x["fn"] == fn and x["new"]]
            if not grp:
                continue
            ws = wbk[grp[0]["sheet"]]
            for x in grp:
                ws.cell(row=x["row"], column=x["col"], value=x["new"])
            wbk.save(fn)
    return rows, codes


# ----------------------------------------------------------------- 3) LAZADA
def step_lazada(apply):
    stat = Counter()
    for fn, sheet, listc, varc, skuc, sr in FB.LAZADA:
        wbk = load_workbook(fn, data_only=False)
        ws = wbk[sheet]
        groups = defaultdict(list)
        for r in range(sr, ws.max_row + 1):
            lst = ws.cell(row=r, column=listc).value
            sku = ws.cell(row=r, column=skuc).value
            if lst in (None, "") or not isinstance(sku, str) or not MASTERFMT.match(sku):
                continue
            groups[(lst, sku)].append(r)
        touched = False
        for (lst, sku), rr in groups.items():
            if len(rr) < 2:
                continue
            used = {sku}
            for r in rr[1:]:
                tag = FLZ_tag(str(ws.cell(row=r, column=varc).value or ""))
                cand = f"{sku}_{tag}" if tag else f"{sku}_2"
                i = 2
                while cand in used:
                    cand = f"{sku}_{tag}{i}" if tag else f"{sku}_{i}"
                    i += 1
                used.add(cand)
                if apply:
                    ws.cell(row=r, column=skuc, value=cand)
                touched = True
                stat["dibuat_unik"] += 1
        if apply and touched:
            wbk.save(fn)
    return stat


def FLZ_tag(var):
    m = re.search(r'gen\s*([0-9]+)', var, re.I)
    if m:
        return "G" + m.group(1)
    m = re.match(r'\s*([A-Za-z0-9]{1,6})', var)
    return re.sub(r'[^A-Z0-9]', '', m.group(1).upper())[:4] if m else None


if __name__ == "__main__":
    # Cetak mode di AWAL, bukan cuma di akhir. Pernah kejadian (2026-07-27): laporan
    # dibaca sbg bukti file sudah diperbarui, padahal run-nya DRY-RUN dan tidak menulis
    # apa pun. Angka "diubah/siap" identik di kedua mode karena penghitungnya di luar
    # blok `if apply:`, jadi laporan skrip TIDAK BOLEH dipakai sbg bukti — verifikasi
    # selalu lewat verifikasi_hasil.py yang membaca isi sel.
    print("*" * 60)
    print("MODE:", "APPLY (file DITULIS)" if APPLY else "DRY-RUN (file TIDAK ditulis)")
    print("*" * 60)
    print("=== 1) SKEMA FORMULA (cover mobil) ===")
    s1, ch1 = step_formula(APPLY)
    for k, v in s1.most_common():
        print(f"   {v:7}  {k}")
    bym = Counter(c[0] for c in ch1)
    print(f"   model terdampak: {len(bym)}")
    for m, n in bym.most_common(10):
        print(f"      {n:5}  {m}")

    print("\n=== 2) SKU MOTOR (format MTR) ===")
    rows, codes = step_motor(APPLY)
    print(f"   baris motor: {len(rows)}   siap: {sum(1 for x in rows if x['new'])}")
    print(f"   model unik : {sum(len(v) for v in codes.values())}")
    print(f"   SKU unik   : {len({x['new'] for x in rows if x['new']})}")

    print("\n=== 3) LAZADA (akhiran '_') ===")
    s3 = step_lazada(APPLY)
    for k, v in s3.most_common():
        print(f"   {v:7}  {k}")

    json.dump({"formula": ch1[:20000]}, open("_baru_hasil.json", "w"), ensure_ascii=False)
    print("\nmode:", "APPLY" if APPLY else "DRY-RUN")
