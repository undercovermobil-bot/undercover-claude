"""Verifikasi file archive marketplace terhadap daftar 100 SKU terlaris.

Memeriksa (baca-saja, tidak mengubah file):
  1. Integritas: antara file asli dan file *_ARCHIVE hanya kolom nama yang berbeda, dan format
     nama baru = nama lama + " (Archive)".
  2. Isi: produk yang di-archive tidak boleh punya SKU model top-100; produk yang dipertahankan harus
     punya minimal satu SKU model top-100; daftar produk dipertahankan yang SKU-nya kosong.

Model = 2 segmen pertama SKU (mis. TYT-AVZ). Top-100 = peringkat <= 100 di sheet "Peringkat Lengkap"
file RANKING TOP 100 PER SKU.xlsx (alias SZK-VITARA -> SZK-GVT).

Pakai (semua argumen opsional kecuali --ranking; ulangi --tiktok bila ada beberapa template):
  py -3 -I verify_archive_top100.py --ranking "G:\\My Drive\\E-commerce\\RANKING TOP 100 PER SKU.xlsx" \
      --tiktok asli_1.xlsx arch_1.xlsx --tiktok asli_2.xlsx arch_2.xlsx \
      --shopee asli_basic_info.xlsx arch_basic_info.xlsx --sales info_penjualan_1.xlsx info_penjualan_2.xlsx
Tanpa --sales, produk Shopee hanya dicek integritasnya (basic info tidak punya SKU).
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_zip import load_xlsx  # noqa: E402

LIMIT = 30


def top100(ranking, alias):
    rows = load_xlsx(ranking)["Peringkat Lengkap"]
    rank = {v[2]: int(v[0]) for r, v in rows if r >= 5 and v and len(v) > 2 and v[0] and str(v[0]).isdigit()}
    top = {m for m, r in rank.items() if r <= 100}
    for a, b in alias.items():
        if a in top:
            top.discard(a)
            top.add(b)
    return top, rank


def model(sku):
    return "-".join(sku.split("-")[:2])


def pad(v, n):
    return v + [None] * (n - len(v))


def show(title, items):
    print(f"{title}: {len(items)}")
    for x in items[:LIMIT]:
        print("   ", x)
    if len(items) > LIMIT:
        print(f"    ... +{len(items) - LIMIT} lainnya")


BY_ID = False  # --by-id: pasangkan baris lewat id produk (export baru urutannya berbeda), bukan nomor baris
KEY_SHOPEE = lambda v: v[0]  # noqa: E731
KEY_TIKTOK = lambda v: (v[0], v[4])  # noqa: E731  (product_id, sku_id)


def integrity(orig, arch, start_row, name_col, width, label, key=None):
    """Bandingkan sel per sel; hanya kolom nama yang boleh berbeda, dan harus + ' (Archive)'.
    key=None: pasangkan per nomor baris (file archive hasil edit dari file asli).
    key=fungsi: pasangkan per id (file kedua = export baru dari marketplace, urutan baris bisa berubah)."""
    if key is not None:
        o = {key(pad(v, width)): v for r, v in orig if r >= start_row and v and v[0]}
        a = {key(pad(v, width)): v for r, v in arch if r >= start_row and v and v[0]}
        is_data = lambda k: True  # noqa: E731
    else:
        o, a = dict(orig), dict(arch)
        is_data = lambda r: r >= start_row  # noqa: E731
    only = set(o) ^ set(a)
    other, badfmt, renamed = collections.Counter(), [], set()
    for r in sorted(set(o) & set(a)):
        x, y = pad(o[r], width), pad(a[r], width)
        for c in range(width):
            if x[c] == y[c]:
                continue
            if c == name_col and is_data(r):
                renamed.add(x[0])
                if y[c] != (x[c] or "") + " (Archive)":
                    badfmt.append((r, x[c], y[c]))
            else:
                other[c] += 1
    print(f"[{label}] baris asli {len(o)} / archive {len(a)} / nomor baris beda {len(only)}")
    print(f"   produk di-rename: {len(renamed)} | format bukan 'nama + (Archive)': {len(badfmt)} | sel lain yang berbeda: {sum(other.values())} {dict(other) or ''}")
    return renamed


def tiktok(pairs, top):
    for orig_f, arch_f in pairs:
        o = load_xlsx(orig_f)["Template"]
        a = load_xlsx(arch_f)["Template"]
        renamed = integrity(o, a, 6, 2, 48, "TikTok " + os.path.basename(orig_f).replace("Tiktoksellercenter_batchedit_", "")[:42],
                            KEY_TIKTOK if BY_ID else None)
        prods = collections.OrderedDict()
        for r, v in o:
            if r >= 6 and v and v[0]:
                v = pad(v, 48)
                p = prods.setdefault(v[0], {"name": v[2], "skus": [], "n": 0})
                p["n"] += 1
                if v[10]:
                    p["skus"].append(v[10])
        arch = [p for pid, p in prods.items() if pid in renamed]
        keep = [p for pid, p in prods.items() if pid not in renamed]
        print(f"   produk {len(prods)}: di-archive {len(arch)}, dipertahankan {len(keep)}")
        show("   [A] di-archive tapi punya SKU model top-100 (HARUSNYA 0)",
             [p["name"] for p in arch if {model(s) for s in p["skus"]} & top])
        show("   [B] dipertahankan tapi semua SKU di luar top-100 (HARUSNYA 0)",
             [(p["name"], sorted({model(s) for s in p["skus"]})[:4]) for p in keep if p["skus"] and not {model(s) for s in p["skus"]} & top])
        show("   [C] dipertahankan dengan varian SKU kosong (isi SKU!)",
             [(p["name"], p["n"] - len(p["skus"]), p["n"]) for p in keep if len(p["skus"]) < p["n"]])
        print(f"   [D] di-archive tanpa SKU sama sekali (tak bisa dicek lewat SKU): {sum(1 for p in arch if not p['skus'])}")


def sheet1(path):
    return load_xlsx(path)["Sheet1"]


def shopee(pair, sales, top):
    o, a = sheet1(pair[0]), sheet1(pair[1])
    renamed = integrity(o, a, 7, 2, 5, "Shopee basic info", KEY_SHOPEE if BY_ID else None)
    names = {v[0]: v[2] for r, v in o if r >= 7 and v and v[0]}
    print(f"   produk {len(names)}: di-archive {len(renamed)}, dipertahankan {len(names) - len(renamed)}")
    if not sales:
        print("   (tanpa --sales: kecocokan dengan top-100 tidak dicek untuk Shopee)")
        return
    by = collections.OrderedDict()
    for f in sales:
        for r, v in sheet1(f):
            if r >= 7 and v and v[0]:
                by.setdefault(v[0], []).append(pad(v, 15))
    print(f"   produk di file Info Penjualan: {len(by)} | sama dengan basic info: {set(by) == set(names)}")
    A, B, C = [], [], []
    for pid, vs in by.items():
        sk = [v[5] for v in vs if v[5]]
        pr = {model(s) for s in sk}
        nm = names.get(pid) or vs[0][1]
        if pid in renamed and pr & top:
            A.append(nm)
        if pid not in renamed:
            if sk and not pr & top:
                B.append((nm, sorted(pr)[:4]))
            blanks = sum(1 for v in vs if not v[5])
            if blanks:
                C.append((nm, blanks, len(vs), "SKU Induk: %s" % vs[0][4]))
    show("   [A] di-archive tapi punya SKU model top-100 (HARUSNYA 0)", A)
    show("   [B] dipertahankan tapi semua SKU di luar top-100 (HARUSNYA 0)", B)
    show("   [C] dipertahankan dengan varian SKU kosong (isi SKU!)", C)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranking", required=True)
    ap.add_argument("--tiktok", nargs=2, action="append", default=[], metavar=("ASLI", "ARCHIVE"))
    ap.add_argument("--shopee", nargs=2, metavar=("ASLI", "ARCHIVE"))
    ap.add_argument("--sales", nargs="+", default=[])
    ap.add_argument("--alias", action="append", default=["SZK-VITARA=SZK-GVT"], help="KODE_RANKING=KODE_LISTING")
    ap.add_argument("--by-id", action="store_true",
                    help="file kedua = EXPORT BARU dari marketplace (urutan baris berubah): pasangkan per id produk, bukan per nomor baris")
    args = ap.parse_args()
    global BY_ID
    BY_ID = args.by_id
    top, _ = top100(args.ranking, dict(x.split("=") for x in args.alias))
    print(f"Top-100 (peringkat <= 100, setelah alias): {len(top)} model")
    if args.tiktok:
        tiktok(args.tiktok, top)
    if args.shopee:
        shopee(args.shopee, args.sales, top)


if __name__ == "__main__":
    main()
