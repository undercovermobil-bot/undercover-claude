"""Isi SKU penjual yang KOSONG pada export TikTok "all_information" Smartprotection (SP).

Hanya produk 100-terlaris yang SKU-nya kosong (lihat TARGET). Hanya baris yang berubah ditulis ke file keluaran,
dan hanya kolom K (seller_sku) yang diubah. Kode toko = SP (Otoprotection memakai kode yang sama).

Pakai:  py -3 -I isi_sku_kosong_tiktok_sp.py <export_sp.xlsx> <keluaran.xlsx>
Aturan SKU: MEREK-MODEL-SP-KAT-GEN-WARNA, KAT: R reguler, S strip, T transparan.
Warna: Abu-abu ABU, Hitam HTM, Biru(Benhur) BRU, Merah MRH, Hijau(Army) GRN, Orange ORG;
Strip: Epic = Strip 1 (S1x), Elite = Strip 2 (S2x), Warrior = Strip 3 (S3x), x = A/B/M; Transparan TRP.
"""
import json
import re
import sys
import zipfile

# pid TikTok -> (awalan model, cara menentukan kode generasi)
#   "gen"  : G<n> dari label "Gen n"      "fixed:X" : kode tetap X      "pintu" : 3P/5P dari label "3 Pintu"/"5 Pintu"
TARGET = {
    "1737516524914181679": ("MG-SE", "gen"),    # MG S5 EV Transparan
    "1737516543948260911": ("MG-SE", "gen"),    # MG S5 EV Reguler+Strip
    "1729826098287642159": ("TYT-CRL", "gen"),  # Toyota Corolla Reguler+Strip (hanya baris kosong, Gen 1-4)
    "1729975307479778863": ("MNI-COO", "pintu"),  # Mini Cooper Transparan
    "1737299175856506415": ("DHT-FRZ", "fixed:F70"),  # Taft GT Transparan
    "1737299182912374319": ("DHT-FRZ", "fixed:F70"),  # Taft GT Reguler+Strip
}
SOLID = {"abu-abu": ("R", "ABU"), "hitam": ("R", "HTM"), "merah": ("R", "MRH"), "hijau army": ("R", "GRN"),
         "orange": ("R", "ORG")}
TIER = {"epic": "1", "elite": "2", "eltie": "2", "warrior": "3", "warior": "3"}
SHADE = {"abu": "A", "biru": "B", "merah": "M"}


def color_code(token):
    """token warna (tanpa generasi) -> (kategori, akhiran)."""
    if token is None:
        return "T", "TRP"
    t = re.sub(r"\s+", " ", token.strip().lower())
    if t in SOLID:
        return SOLID[t]
    if t.startswith("biru b"):  # Biru Benhur dan salah ketiknya
        return "R", "BRU"
    m = re.match(r"^(epic|elite|eltie|warrior|warior)\s+(abu|biru|merah)$", t)
    if m:
        return "S", "S" + TIER[m.group(1)] + SHADE[m.group(2)]
    raise ValueError("warna tak dikenal: " + token)


def split_variation(v):
    """'Abu-abu, Gen 1 : 2025-Now' -> ('Abu-abu', 'Gen 1 : 2025-Now'); tanpa warna -> (None, label)."""
    parts = [p.strip() for p in v.split(", ", 1)]
    if len(parts) == 2 and not re.match(r"^(Gen\s*\d|F70|J\d|\d+\s*Pintu)", parts[0], re.I):
        return parts[0], parts[1]
    return None, v.strip()


def build_sku(prefix, how, color, label, cat_from_color):
    cat, suf = cat_from_color
    if how == "gen":
        m = re.match(r"^Gen\s*(\d+)", label)
        gen = "G" + m.group(1)
    elif how.startswith("fixed:"):
        gen = how.split(":", 1)[1]
    else:  # pintu
        m = re.search(r"(\d)\s*Pintu", label)
        gen = m.group(1) + "P"
    return f"{prefix}-SP-{cat}-{gen}-{suf}"


def main(src, dst):
    zin = zipfile.ZipFile(src)
    ss = [re.sub(r"<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", zin.read("xl/sharedStrings.xml").decode("utf8"), re.S)]
    x = zin.read("xl/worksheets/sheet1.xml").decode("utf8")
    head, rest = x.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)
    keep, changes = [], []
    for r in re.findall(r"<row .*?</row>", body, re.S):
        n = int(re.match(r'<row r="(\d+)"', r).group(1))
        if n <= 5:
            keep.append(r)
            continue

        def cell(col):
            m = re.search(r'<c r="%s%d"([^>]*?)(?:/>|>(.*?)</c>)' % (col, n), r, re.S)
            if not m:
                return None, None
            attrs, inner = m.group(1), m.group(2) or ""
            if 't="s"' in attrs:
                v = re.search(r"<v>(\d+)</v>", inner)
                return (ss[int(v.group(1))] if v else None), m.group(0)
            if 'inlineStr' in attrs:
                return re.sub(r"<[^>]+>", "", inner), m.group(0)
            v = re.search(r"<v>(.*?)</v>", inner)
            return (v.group(1) if v else None), m.group(0)

        pid, _ = cell("A")
        if pid not in TARGET:
            continue
        var, _ = cell("F")
        sku, kcell = cell("K")
        if sku or kcell is None or not var:
            continue  # hanya isi yang kosong
        prefix, how = TARGET[pid]
        color, label = split_variation(var)
        if how == "pintu":  # Mini Cooper Transparan: "Hatch, 3 Pintu" = sub-model + pintu, bukan warna
            color, label = None, var
        new = build_sku(prefix, how, color, label, color_code(color))
        sty = re.search(r's="(\d+)"', kcell)
        newcell = '<c r="K%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (n, (' s="%s"' % sty.group(1)) if sty else "", new)
        keep.append(r.replace(kcell, newcell))
        name, _ = cell("C")
        changes.append((n, pid, name, var, new))
    if not changes:
        raise SystemExit("Tidak ada SKU kosong pada produk target.")
    maxr = max(c[0] for c in changes)
    head = re.sub(r'<dimension ref="[^"]+">', '<dimension ref="A1:AV%d">' % maxr, head)
    newx = head + "<sheetData>" + "".join(keep) + "</sheetData>" + tail
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = newx.encode("utf8") if it.filename == "xl/worksheets/sheet1.xml" else zin.read(it.filename)
        zout.writestr(it, data, compress_type=zipfile.ZIP_DEFLATED)
    zout.close()
    json.dump(changes, open(dst + ".json", "w", encoding="utf8"), ensure_ascii=False)
    print("baris diisi:", len(changes))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
