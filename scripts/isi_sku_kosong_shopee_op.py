"""Isi SKU varian KOSONG pada export Shopee "Info Penjualan" (mass update sales info) Otoprotection (OP).

Hanya produk 100-terlaris yang SKU-nya kosong (lihat TARGET). Hanya baris yang berubah ditulis ke file keluaran
dan hanya kolom F (SKU) yang diubah. Kode toko = SP (OP memakai kode yang sama dengan Smartprotection).

Pakai:  py -3 -I isi_sku_kosong_shopee_op.py <export.xlsx> <keluaran.xlsx>   (jalankan per file export)
Warna: Abu-abu ABU, Hitam HTM, Biru(Benhur) BRU, Merah MRH, Hijau(Army) GRN, Orange ORG;
Strip N + Abu/Biru/Merah = S<N>A/B/M; Transparan = TRP.
"""
import re
import sys
import zipfile

# pid Shopee -> ("gen", awalan model)  atau  ("sku", SKU tetap untuk produk tanpa variasi)
TARGET = {
    "49467882039": ("gen", "MG-SE"),     # MG S5 EV Transparan
    "56417848002": ("gen", "MG-SE"),     # MG S5 EV Reguler + Strip
    # Hyundai Santa Fe Transparan (tanpa variasi, SKU Induk masih CVR0089-OTP-RTP); sama dengan TikTok OP.
    "24550732727": ("sku", "HYN-SFE-SP-T-G1-TRP"),
}
SOLID = {"abu-abu": "ABU", "hitam": "HTM", "merah": "MRH", "hijau army": "GRN", "orange": "ORG", "biru benhur": "BRU"}
SHADE = {"abu": "A", "abu-abu": "A", "biru": "B", "merah": "M"}


def sku_for(kind, arg, variation):
    if kind == "sku":
        return arg
    # "Strip 1 Biru,Gen 1 : 2025-Now" | "Biru Benhur,Gen 1 : 2025-Now" | "Gen 1 : 2025-Now"
    m = re.match(r"^(?:(.+?),\s*)?Gen\s*(\d+)\b", variation or "")
    if not m:
        raise ValueError("variasi tak dikenal: %r" % variation)
    col, gen = m.group(1), m.group(2)
    base = f"{arg}-SP-"
    if col is None:
        return f"{base}T-G{gen}-TRP"
    t = col.strip().lower()
    s = re.match(r"^strip\s*([123])\s+(abu-abu|abu|biru|merah)$", t)
    if s:
        return f"{base}S-G{gen}-S{s.group(1)}{SHADE[s.group(2)]}"
    if t in SOLID:
        return f"{base}R-G{gen}-{SOLID[t]}"
    raise ValueError("warna tak dikenal: %r" % col)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    ss = [re.sub(r"<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", zin.read("xl/sharedStrings.xml").decode("utf8"), re.S)]
    x = zin.read("xl/worksheets/sheet1.xml").decode("utf8")
    head, rest = x.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)
    keep, changes = [], []
    for r in re.findall(r"<row [^>]*>.*?</row>", body, re.S):
        n = int(re.search(r'\br="(\d+)"', re.match(r"<row [^>]*>", r).group(0)).group(1))
        if n <= 6:
            keep.append(r)
            continue

        def cell(col):
            m = re.search(r'<c r="%s%d"([^>]*?)(?:/>|>(.*?)</c>)' % (col, n), r, re.S)
            if not m:
                return None, None
            attrs, inner = m.group(1), m.group(2) or ""
            v = re.search(r"<v>(.*?)</v>", inner)
            if 't="s"' in attrs and v:
                return ss[int(v.group(1))], m.group(0)
            return (v.group(1) if v else None), m.group(0)

        pid, _ = cell("A")
        if pid not in TARGET:
            continue
        sku, fcell = cell("F")
        if sku or fcell is None:
            continue  # hanya isi yang kosong
        var, _ = cell("D")
        kind, arg = TARGET[pid]
        new = sku_for(kind, arg, var)
        sty = re.search(r's="(\d+)"', fcell)
        newcell = '<c r="F%d"%s t="inlineStr"><is><t>%s</t></is></c>' % (n, (' s="%s"' % sty.group(1)) if sty else "", new)
        keep.append(r.replace(fcell, newcell))
        name, _ = cell("B")
        changes.append((n, pid, name, var, new))
    if not changes:
        print("Tidak ada SKU kosong pada produk target di", src)
        return 0
    head = re.sub(r'<dimension ref="[^"]+">', '<dimension ref="A1:O%d">' % max(c[0] for c in changes), head)
    newx = head + "<sheetData>" + "".join(keep) + "</sheetData>" + tail
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = newx.encode("utf8") if it.filename == "xl/worksheets/sheet1.xml" else zin.read(it.filename)
        zout.writestr(it, data, compress_type=zipfile.ZIP_DEFLATED)
    zout.close()
    for c in changes:
        print(c)
    print("baris diisi:", len(changes))
    return len(changes)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
