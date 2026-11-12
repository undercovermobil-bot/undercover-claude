"""Isi atribut wajib TikTok (Imported goods, Tahun, Model) pada file all_information, dan (opsional) hanya simpan produk "(Archive)".

Kenapa: TikTok menolak SELURUH baris file all_information bila produk di dalamnya belum punya atribut wajib kategorinya
("atribut produk is missing ... ID:102254 Imported goods", "ID:100530 Tahun", "ID:100177 Model"). Produk lama banyak yang belum
punya atribut itu, jadi file rename (archive) atau file SKU apa pun ikut gagal total. Skrip ini mengisi hanya sel yang KOSONG.

Pakai:
  py -3 -I tiktok_isi_atribut_wajib.py <asli.xlsx> <keluaran.xlsx> [--only-archive] [--imported Tidak] [--tahun 2026]
Aturan (empiris, dari file Result 12 Nov 2026):
  - Imported goods (product_property/102254): diisi semua baris yang kosong. Nilai harus ada di dropdown kategori (Ya/Tidak).
  - Tahun (100530): diisi bila kosong, hanya untuk kategori Cover & Shelter Mobil (931592) dan Radiator (813968).
    Sarung Setir / Bantal Alas Kursi tidak minta Tahun.
  - Model (100177): hanya kategori 813968 (Mercedes Transparan nyasar di kategori Radiator): diambil dari nama produk
    ("Mercedes Benz GLC Class" -> opsi dropdown "GLC-Class" / "GLC Class" / "GLC") bila kosong.
  - Kolom dicari lewat kunci baris 1 (product_property/<id>), BUKAN nomor kolom: posisi kolom berubah antar versi template
    (12 Nov 2026 UA punya kolom tambahan "Contains dangerous goods").
Keluaran: baris data berurutan dari baris 6; sel lain tidak diubah. Laporan perubahan dicetak; verifikasi otomatis di akhir.
"""
import argparse
import collections
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_zip import load_xlsx  # noqa: E402
from compact_rows import ROW_TAG, SHEET, renumber_row, row_number, set_dimension, split_sheet, write_zip  # noqa: E402

HEADER_ROWS = 5
TAHUN_CATS = {"931592", "813968"}
MODEL_CATS = {"813968"}
CELL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(/>|>.*?</c>)', re.S)


def letters(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def col_idx(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n - 1


def g(v, i):
    return "" if i is None or i >= len(v) or v[i] is None else str(v[i])


def set_cells(row_xml, values):
    """values {indeks_kolom: teks}. Ganti sel yang ada (pertahankan style) atau sisipkan sesuai urutan kolom."""
    tag = re.match(ROW_TAG, row_xml).group(0)
    n = row_number(row_xml)
    inner = row_xml[len(tag):-len("</row>")]
    cells = [(col_idx(m.group(1)), m.group(0)) for m in CELL.finditer(inner)]
    if "".join(c for _, c in cells) != inner:
        raise ValueError("isi baris %d tidak sepenuhnya berupa sel; tidak aman diedit" % n)
    cmap = dict(cells)
    inserted = False
    for idx, text in values.items():
        old = cmap.get(idx)
        style = re.search(r' s="(\d+)"', old).group(0) if old and re.search(r' s="(\d+)"', old) else ""
        cmap[idx] = '<c r="%s%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (letters(idx), n, style, escape(text))
        inserted = inserted or old is None
    if inserted:
        tag = re.sub(r' spans="[^"]*"', "", tag)
    return tag + "".join(cmap[i] for i in sorted(cmap)) + "</row>"


def dropdown_cols(sheet_xml_tail, col):
    """Dari dataValidation sel <col>6 -> (huruf kolom kategori, huruf kolom opsi) di sheet HiddenAttr; None bila tidak ada."""
    m = re.search(r'sqref="%s6"[^>]*>\s*<formula1>(.*?)</formula1>' % col, sheet_xml_tail, re.S)
    if not m:
        return None
    f = m.group(1)
    a = re.search(r"OFFSET\(HiddenAttr!\$([A-Z]+)\$1", f)
    b = re.search(r"MATCH\(\$B\$6,HiddenAttr!\$([A-Z]+)\$1", f)
    return (b.group(1), a.group(1)) if a and b else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--only-archive", action="store_true", help="simpan hanya produk yang namanya berakhiran ' (Archive)'")
    ap.add_argument("--imported", default="Tidak")
    ap.add_argument("--tahun", default="2026")
    a = ap.parse_args()

    wb = load_xlsx(a.src)
    t = wb["Template"]
    keys = dict(t[0][1] and [(k, i) for i, k in enumerate(t[0][1]) if k])
    need = ["product_id", "category", "product_name"]
    for k in need:
        if k not in keys:
            raise SystemExit("kunci baris 1 tidak ada: " + k)
    iP, iC, iN = keys["product_id"], keys["category"], keys["product_name"]
    iImp = keys.get("product_property/102254")
    iTah = keys.get("product_property/100530")
    iMod = keys.get("product_property/100177")
    data = {r: v for r, v in t if r > HEADER_ROWS}

    # dropdown per atribut -> {kategori: set(opsi)}
    xml = zipfile.ZipFile(a.src).read(SHEET).decode("utf8")
    head, rows, tail = split_sheet(xml)
    ha = wb.get("HiddenAttr", [])
    opts = {}
    for label, idx in (("imported", iImp), ("tahun", iTah), ("model", iMod)):
        if idx is None:
            continue
        cc = dropdown_cols(tail, letters(idx))
        if not cc:
            continue
        ci, oi = col_idx(cc[0]), col_idx(cc[1])
        d = collections.defaultdict(set)
        for _, v in ha:
            if g(v, ci) and g(v, oi):
                d[g(v, ci)].add(g(v, oi))
        opts[label] = d

    def cat_id(cat):
        m = re.search(r"\((\d+)\)\s*$", cat)
        return m.group(1) if m else ""

    sel_pids = None
    if a.only_archive:
        sel_pids = {g(v, iP) for v in data.values() if g(v, iN).endswith(" (Archive)")}

    changes, warns, per_attr = {}, [], collections.Counter()
    keep_rows = []
    for r, v in sorted(data.items()):
        if sel_pids is not None and g(v, iP) not in sel_pids:
            continue
        keep_rows.append(r)
        cat, cid, name = g(v, iC), cat_id(g(v, iC)), g(v, iN)
        fill = {}
        if iImp is not None and not g(v, iImp):
            if "imported" in opts and cat in opts["imported"] and a.imported not in opts["imported"][cat]:
                warns.append("r%d: '%s' tidak ada di dropdown Imported goods kategori %s" % (r, a.imported, cat))
            fill[iImp] = a.imported
            per_attr["Imported goods"] += 1
        if iTah is not None and not g(v, iTah) and cid in TAHUN_CATS:
            if "tahun" in opts and cat in opts["tahun"] and a.tahun not in opts["tahun"][cat]:
                warns.append("r%d: tahun '%s' tidak ada di dropdown kategori %s" % (r, a.tahun, cat))
            fill[iTah] = a.tahun
            per_attr["Tahun"] += 1
        if iMod is not None and not g(v, iMod) and cid in MODEL_CATS:
            m = re.search(r"Mercedes[- ]Benz\s+(.+?)\s+Class", name, re.I)
            options = opts.get("model", {}).get(cat, set())
            found = None
            if m:
                x = m.group(1).strip()
                for cand in ("%s-Class" % x, "%s Class" % x, x):
                    if cand in options:
                        found = cand
                        break
            if found:
                fill[iMod] = found
                per_attr["Model"] += 1
            else:
                warns.append("r%d: Model kosong, tidak ketemu opsi dropdown untuk '%s'" % (r, name[:60]))
        if fill:
            changes[r] = fill

    # tulis: header utuh, baris terpilih (diubah) dinomori ulang berurutan dari 6
    out_rows, nxt, keep_set = [], HEADER_ROWS + 1, set(keep_rows)
    for rx in rows:
        n = row_number(rx)
        if n <= HEADER_ROWS:
            out_rows.append(rx)
            continue
        if n not in keep_set:
            continue
        if n in changes:
            rx = set_cells(rx, changes[n])
        if n != nxt:
            rx = renumber_row(rx, nxt)
        out_rows.append(rx)
        nxt += 1
    new = set_dimension(head, nxt - 1) + "<sheetData>" + "".join(out_rows) + "</sheetData>" + tail
    write_zip(a.src, a.dst, new)

    # verifikasi: baca ulang, banding sel per sel dengan sumber
    chk = load_xlsx(a.dst)["Template"]
    out = {r: v for r, v in chk if r > HEADER_ROWS}
    src_rows = sorted(keep_rows)
    problems = []
    if len(out) != len(src_rows) or sorted(out) != list(range(HEADER_ROWS + 1, HEADER_ROWS + 1 + len(src_rows))):
        problems.append("nomor baris keluaran tidak berurutan / jumlah beda")
    allowed = {x for x in (iImp, iTah, iMod) if x is not None}
    diff_other = diff_allowed = 0
    for new_r, old_r in zip(sorted(out), src_rows):
        nv, ov = out[new_r], data[old_r]
        for i in range(max(len(nv), len(ov))):
            if g(nv, i) != g(ov, i):
                if i in allowed and not g(ov, i):
                    diff_allowed += 1
                else:
                    diff_other += 1
    for (r1, v1), (r2, v2) in zip(t[:HEADER_ROWS], chk[:HEADER_ROWS]):
        if v1 != v2:
            problems.append("header baris %d berbeda" % r1)
    blanks = collections.Counter()
    for v in out.values():
        if iImp is not None and not g(v, iImp):
            blanks["Imported goods"] += 1
        if iTah is not None and not g(v, iTah) and cat_id(g(v, iC)) in TAHUN_CATS:
            blanks["Tahun"] += 1
        if iMod is not None and not g(v, iMod) and cat_id(g(v, iC)) in MODEL_CATS:
            blanks["Model"] += 1
    prods = len({g(v, iP) for v in out.values()})
    print("keluaran:", a.dst)
    print("  produk %d | baris %d | sel diisi %s" % (prods, len(out), dict(per_attr)))
    print("  verifikasi: sel lain berubah %d (harus 0) | sel kosong terisi %d | atribut wajib masih kosong %s" % (diff_other, diff_allowed, dict(blanks) or 0))
    if a.only_archive:
        notarch = sum(1 for v in out.values() if not g(v, iN).endswith(" (Archive)"))
        print("  baris bukan '(Archive)' di keluaran: %d (harus 0)" % notarch)
    for w in warns:
        print("  PERINGATAN:", w)
    for p in problems:
        print("  MASALAH:", p)
    if diff_other or problems or warns:
        sys.exit(1)


if __name__ == "__main__":
    main()
