#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buat_matriks_terlaris.py  (versi NO-INSTALL / tanpa pip)
=========================================================
Bangun matriks penjualan MOBIL TERLARIS (Top 300) sampai detail GEN & WARNA,
dari data order mentah Shopee / TikTok / Lazada untuk SEMUA toko
(Undercover, Otonation, Otopro/Otoprotection, Smartpro/Smartprotection).

>>> HANYA butuh Python (>=3.7). TIDAK perlu 'pip install' apa pun. <<<
    Script ini membaca & menulis .xlsx pakai library BAWAAN Python
    (zipfile + xml), jadi tidak butuh openpyxl / pandas.

Kenapa berbentuk script (bukan file jadi):
    File order mentahnya puluhan @1-2 MB. File sebesar itu tidak bisa ditarik
    lewat asisten/cloud, jadi pemrosesan dilakukan lokal di komputermu tempat
    file berada. Bonus: bisa dipakai ulang tiap bulan.

CARA PAKAI (Windows):
    Opsi A - dobel klik file  jalankan_matriks.bat  (paling gampang).
    Opsi B - lewat Command Prompt / PowerShell:
        python buat_matriks_terlaris.py "C:\\Users\\OWNER\\Downloads\\Sales"
      atau (kalau 'python' tak dikenali):
        py buat_matriks_terlaris.py "C:\\Users\\OWNER\\Downloads\\Sales"

    Cek Python ada:  buka Command Prompt, ketik:  python --version
    (kalau muncul "Python 3.x" berarti siap; kalau tidak, install dari
     Microsoft Store: cari "Python 3", 1 klik, gratis.)

Argumen opsional:
    python buat_matriks_terlaris.py "<folder data>" "<nama output.xlsx>"

Output default: MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx  (buka di Excel / Google Sheets)
    4 sheet:
      1. "Top 300 Mobil"       -> ranking per model (gaya file MOBIL TERLARIS lama)
      2. "Detail Gen & Warna"  -> tiap baris = Model + Jenis Cover + Gen + Warna
      3. "Matriks Warna"       -> crosstab: baris Model-Gen, kolom Warna, isi kuantitas
      4. "Metodologi"          -> definisi, filter, diagnostik (jumlah baris per marketplace)

Asumsi (bisa diubah di bagian KONFIGURASI di bawah):
    - Hanya MOBIL (Cover Mobil); motor diabaikan untuk ranking.
    - Pesanan BATAL / BELUM BAYAR / REFUND / RETUR dikeluarkan.
    - "Total Penjualan" = nilai NET setelah diskon.
    - Kuantitas = qty terjual - qty diretur.
    - Model digabung lintas toko & marketplace.
"""

import sys
import os
import re
import zipfile
import tempfile
import shutil
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

# =====================================================================
#  KONFIGURASI
# =====================================================================
TOP_N = 300
SATUAN = "PCS"
OUTPUT_DEFAULT = "MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx"
DEFAULT_FOLDER = r"C:\Users\OWNER\Downloads\Sales"   # dipakai kalau tak ada argumen

STATUS_EXCLUDE = [
    "batal", "cancel", "belum bayar", "unpaid", "belum dibayar",
    "return", "retur", "refund", "pengembalian", "failed", "gagal", "lost",
]
STRIP_PREFIX = ["Elite", "Epic", "Warrior", "Warior"]
TIER_WORDS = ["Exclusive", "Premium", "Reguler", "Strip"]
NAME_PREFIXES = [
    "Cover Mobil / Selimut Mobil ", "Body Cover Mobil / Selimut Mobil ",
    "Cover Mobil Transparan ", "Cover Mobil Transparant ",
    "Body Cover Mobil ", "Cover Mobil ",
    "Cover Motor / Selimut Motor ", "Body Cover Motor ", "Cover Motor ",
]
WARNA_CANON = {
    "abu-abu": "Abu-abu", "abu abu": "Abu-abu", "abu": "Abu-abu",
    "hitam": "Hitam", "merah": "Merah", "biru": "Biru", "putih": "Putih",
    "silver": "Silver", "hijau army": "Hijau Army", "hijau": "Hijau",
    "coklat": "Coklat", "cream": "Cream", "krem": "Cream",
}
SKU_WARNA_CODE = {
    "ABU": "Abu-abu", "HTM": "Hitam", "MRH": "Merah", "BRU": "Biru",
    "PUT": "Putih", "SLV": "Silver", "SIL": "Silver", "HJA": "Hijau Army",
    "HJU": "Hijau", "CKL": "Coklat", "CRM": "Cream",
}

# =====================================================================
#  UTIL parsing angka / teks
# =====================================================================
def to_num(x):
    if x is None or isinstance(x, bool):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", "").replace(" ", "")
    if s in ("", "-", "--"):
        return 0.0
    s = re.sub(r"[^0-9.,\-]", "", s)
    if s in ("", "-", "."):
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    else:
        if s.count(".") == 1:
            after = s.split(".")[1]
            if len(after) == 3:
                s = s.replace(".", "")
        elif s.count(".") > 1:
            s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def to_int(x):
    return int(round(to_num(x)))


def norm(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())


# =====================================================================
#  UTIL parsing nama produk & variasi  (sama seperti versi openpyxl)
# =====================================================================
def parse_name(name):
    if name is None:
        return None, None, False
    n = str(name).strip()
    low = n.lower()
    is_motor = ("cover motor" in low) or ("selimut motor" in low)
    m = None
    for mm in re.finditer(r"(?:body\s+)?cover\s+(?:mobil|motor)(?:\s*/\s*selimut\s+(?:mobil|motor))?", n, re.I):
        m = mm
    if m:
        n = n[m.end():]
    else:
        for p in NAME_PREFIXES:
            idx = n.lower().find(p.lower())
            if idx != -1:
                n = n[idx + len(p):]
                break
    n = n.strip(" -/")
    n = re.sub(r"^(transparan|transparant)\s+", "", n, flags=re.I)
    n = re.sub(r"\s*\((?:j|jj)\)\s*$", "", n, flags=re.I)
    n = re.sub(r"\s*-\s*(undercover autocare|undercover|otonation|otoprotection|otopro|smartprotection|smartpro)\s*$", "", n, flags=re.I)
    tier = None
    for t in sorted(TIER_WORDS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(t) + r"\b\s*$", n, re.I):
            tier = t
            n = re.sub(r"\s*\b" + re.escape(t) + r"\b\s*$", "", n, flags=re.I)
            break
    n = re.sub(r"\s+", " ", n).strip(" -/")
    if not n:
        return None, tier, is_motor
    return n, tier, is_motor


def _looks_like_gen(tok):
    t = tok.lower()
    if "gen" in t or "model/tahun" in t or "tahun lain" in t:
        return True
    if re.search(r"\(\s*(?:19|20)\d{2}", tok):
        return True
    if re.match(r"^[A-Za-z]?\d+[A-Za-z]?(\s*-\s*\d+)?$", tok.strip()):
        return True
    return False


def parse_variation(vari):
    if vari is None:
        return None, None, None
    parts = [p.strip() for p in str(vari).split(",") if p.strip() != ""]
    warna = None
    gen = None
    for p in parts:
        low = p.lower()
        if low.startswith("warna:") or low.startswith("colour:") or low.startswith("color:"):
            warna = p.split(":", 1)[1].strip()
        elif low.startswith("model:") or low.startswith("gen:") or low.startswith("generasi:"):
            gen = p.split(":", 1)[1].strip()
        elif _looks_like_gen(p):
            if gen is None:
                gen = p
        else:
            if warna is None:
                warna = p
    if warna is None and parts:
        warna = parts[0]
    tier_w = None
    if warna:
        w0 = warna.strip()
        if any(w0.lower().startswith(s.lower()) for s in STRIP_PREFIX):
            tier_w = "Strip"
        elif w0.lower() == "silver":
            tier_w = "Premium"
        elif w0.lower() in ("transparan", "transparant"):
            tier_w = "Transparan"
    return warna, gen, tier_w


def canon_warna(w):
    if not w:
        return "(tanpa warna)"
    w = re.sub(r"\s+", " ", str(w).strip()).replace("Warior", "Warrior")
    return WARNA_CANON.get(w.lower(), w)


def canon_gen(g):
    if not g:
        return "(tanpa gen)"
    g = re.sub(r"\s*\(.*?\)\s*", " ", str(g))
    g = re.sub(r"\s+", " ", g).strip()
    return g if g else "(tanpa gen)"


def warna_and_tier_from_sku(sku):
    if not sku:
        return None, None
    toks = re.split(r"[-_]", str(sku).strip().upper())
    warna = None
    gen = None
    for t in toks:
        if re.match(r"^G\d+[A-Z]?\d*$", t):
            gen = "Gen " + t[1:]
        if t in SKU_WARNA_CODE:
            warna = SKU_WARNA_CODE[t]
    return warna, gen


# =====================================================================
#  DETEKSI MARKETPLACE + KOLOM
# =====================================================================
FIELD_MAP = {
    "shopee": {
        "status": ["status pesanan"], "product": ["nama produk"],
        "variation": ["nama variasi"], "qty": ["jumlah"],
        "returned": ["returned quantity"], "value": ["subtotal pesanan"],
        "sku": ["nomor referensi sku", "sku induk"],
    },
    "tiktok": {
        "status": ["order status"], "product": ["product name"],
        "variation": ["variation"], "qty": ["quantity"],
        "returned": ["sku quantity of return"],
        "value": ["sku subtotal after discount"], "sku": ["seller sku"],
    },
    "lazada": {
        "status": ["status"], "product": ["itemname"],
        "variation": ["variation"], "qty": [], "returned": [],
        "value": ["paidprice"], "sku": ["sellersku"],
    },
}


def detect_market_and_columns(header_cells):
    hs = [norm(c) for c in header_cells]
    hset = set(hs)

    def find(cands):
        for cand in cands:
            for i, h in enumerate(hs):
                if h == cand:
                    return i
        for cand in cands:
            for i, h in enumerate(hs):
                if cand in h:
                    return i
        return None

    if "itemname" in hset and "sellersku" in hset and "variation" in hset:
        market = "lazada"
    elif "nama produk" in hset and "nama variasi" in hset:
        market = "shopee"
    elif "product name" in hset and "variation" in hset:
        market = "tiktok"
    else:
        return None
    colmap = {}
    for field, cands in FIELD_MAP[market].items():
        colmap[field] = find(cands) if cands else None
    if colmap.get("product") is None or colmap.get("variation") is None:
        return None
    return market, colmap


# =====================================================================
#  PEMBACA .xlsx PAKAI LIBRARY BAWAAN (zipfile + xml)
# =====================================================================
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _col_to_idx(ref):
    letters = ""
    for ch in ref:
        if ch.isalpha():
            letters += ch
        else:
            break
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def _cell_value(c, shared):
    t = c.get("t")
    if t == "s":
        v = c.find(NS + "v")
        if v is not None and v.text is not None:
            try:
                return shared[int(v.text)]
            except (ValueError, IndexError):
                return None
        return None
    if t == "inlineStr":
        is_ = c.find(NS + "is")
        if is_ is not None:
            return "".join(tt.text or "" for tt in is_.iter(NS + "t"))
        return None
    if t == "str":
        v = c.find(NS + "v")
        return v.text if v is not None else None
    if t == "b":
        v = c.find(NS + "v")
        return (v is not None and v.text == "1")
    v = c.find(NS + "v")
    if v is None or v.text is None:
        return None
    s = v.text
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        return s


def read_xlsx_rows(path):
    """Kembalikan list of (nama_sheet_file, rows). rows = list of list nilai sel."""
    result = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            with z.open("xl/sharedStrings.xml") as fh:
                for ev, el in ET.iterparse(fh, events=("end",)):
                    if el.tag == NS + "si":
                        shared.append("".join(t.text or "" for t in el.iter(NS + "t")))
                        el.clear()
        sheet_files = sorted(
            [n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)],
            key=lambda n: int(re.search(r"sheet(\d+)\.xml", n).group(1)),
        )
        if not sheet_files:
            sheet_files = sorted(n for n in names if re.match(r"xl/worksheets/.*\.xml$", n))
        for sf in sheet_files:
            rows = []
            with z.open(sf) as fh:
                for ev, el in ET.iterparse(fh, events=("end",)):
                    if el.tag == NS + "row":
                        rowvals = {}
                        maxc = -1
                        auto = 0
                        for c in el.findall(NS + "c"):
                            ref = c.get("r") or ""
                            if any(ch.isalpha() for ch in ref):
                                ci = _col_to_idx(ref)
                            else:
                                ci = auto
                            auto = ci + 1
                            rowvals[ci] = _cell_value(c, shared)
                            if ci > maxc:
                                maxc = ci
                        rows.append([rowvals.get(i) for i in range(maxc + 1)])
                        el.clear()
            result.append((sf, rows))
    return result


# =====================================================================
#  PROSES 1 FILE
# =====================================================================
def get(row, idx):
    if idx is None or idx >= len(row):
        return None
    return row[idx]


def process_workbook(path, agg, diag):
    try:
        sheets = read_xlsx_rows(path)
    except Exception as e:
        diag["file_error"] += 1
        diag.setdefault("_errors", []).append(f"{os.path.basename(path)}: {e}")
        return
    for _sf, rows in sheets:
        colmap = None
        market = None
        header_found = False
        for row in rows:
            if not header_found:
                res = detect_market_and_columns(row)
                if res:
                    market, colmap = res
                    header_found = True
                continue
            product = get(row, colmap["product"])
            if product is None or str(product).strip() == "":
                continue
            diag["rows_%s" % market] += 1
            diag["rows_total"] += 1

            status = norm(get(row, colmap["status"])) if colmap.get("status") is not None else ""
            if any(bad in status for bad in STATUS_EXCLUDE):
                diag["skip_status"] += 1
                continue

            model, tier_name, is_motor = parse_name(product)
            if is_motor:
                diag["rows_motor"] += 1
                continue
            if not model:
                diag["skip_no_model"] += 1
                if len(diag.setdefault("_sample_no_model", [])) < 15:
                    diag["_sample_no_model"].append(str(product)[:70])
                continue

            warna_raw, gen_raw, tier_w = parse_variation(get(row, colmap["variation"]))
            if warna_raw is None and gen_raw is None:
                w2, g2 = warna_and_tier_from_sku(get(row, colmap.get("sku")))
                warna_raw = warna_raw or w2
                gen_raw = gen_raw or g2
            warna = canon_warna(warna_raw)
            gen = canon_gen(gen_raw)
            tipe = tier_w or tier_name or "Reguler"

            if market == "lazada":
                qty = 1
            else:
                qty = to_int(get(row, colmap["qty"])) if colmap.get("qty") is not None else 1
                if qty <= 0:
                    qty = 1
            ret = to_int(get(row, colmap["returned"])) if colmap.get("returned") is not None else 0
            net_qty = qty - ret
            if net_qty <= 0:
                diag["skip_returned"] += 1
                continue
            value = to_num(get(row, colmap["value"])) if colmap.get("value") is not None else 0.0
            if ret and qty:
                value = value * net_qty / qty

            sku = get(row, colmap.get("sku"))
            sku_key = str(sku).strip() if sku else "%s|%s|%s|%s" % (model, tipe, gen, warna)

            rec = agg[(model, tipe, gen, warna)]
            rec["qty"] += net_qty
            rec["value"] += value
            rec["skus"].add(sku_key)
            diag["rows_counted"] += 1
    return


def gather_files(root):
    files = []
    tmpdirs = []
    for dirpath, _dirs, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            low = fn.lower()
            if low.startswith("~$"):
                continue
            if low.endswith(".xlsx"):
                files.append((full, rel))
            elif low.endswith(".zip"):
                try:
                    td = tempfile.mkdtemp(prefix="ordzip_")
                    tmpdirs.append(td)
                    with zipfile.ZipFile(full) as zf:
                        for member in zf.namelist():
                            if member.lower().endswith(".xlsx") and not member.startswith("__"):
                                zf.extract(member, td)
                                files.append((os.path.join(td, member), rel + " (zip)"))
                except Exception as e:
                    print("  ! Gagal buka zip %s: %s" % (fn, e))
    return files, tmpdirs


# =====================================================================
#  PENULIS .xlsx PAKAI LIBRARY BAWAAN
# =====================================================================
# Indeks style (harus cocok dgn urutan cellXfs di STYLES_XML)
S_DEFAULT, S_TITLE, S_SUB, S_HEAD, S_TXT, S_INT, S_PCT, S_IDR = 0, 1, 2, 3, 4, 5, 6, 7
S_TTXT, S_TINT, S_TPCT, S_TIDR, S_CINT, S_BOLD = 8, 9, 10, 11, 12, 13

STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<numFmts count="1"><numFmt numFmtId="164" formatCode="0.0%"/></numFmts>'
    '<fonts count="5">'
    '<font><sz val="10"/><name val="Arial"/></font>'
    '<font><b/><sz val="10"/><name val="Arial"/></font>'
    '<font><b/><sz val="14"/><name val="Arial"/></font>'
    '<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>'
    '<font><i/><sz val="9"/><color rgb="FF555555"/><name val="Arial"/></font>'
    '</fonts>'
    '<fills count="4">'
    '<fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/></patternFill></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFD9E1F2"/></patternFill></fill>'
    '</fills>'
    '<borders count="2">'
    '<border><left/><right/><top/><bottom/><diagonal/></border>'
    '<border>'
    '<left style="thin"><color rgb="FFBFBFBF"/></left>'
    '<right style="thin"><color rgb="FFBFBFBF"/></right>'
    '<top style="thin"><color rgb="FFBFBFBF"/></top>'
    '<bottom style="thin"><color rgb="FFBFBFBF"/></bottom>'
    '<diagonal/></border>'
    '</borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="14">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'                                                                                  # 0 default
    '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'                                                                    # 1 title
    '<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1"/>'                                                                    # 2 subtitle
    '<xf numFmtId="0" fontId="3" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
    '<alignment horizontal="center" vertical="center" wrapText="1"/></xf>'                                                                            # 3 header
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/>'                                                                  # 4 data text
    '<xf numFmtId="3" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyNumberFormat="1"/>'                                            # 5 int
    '<xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyNumberFormat="1"/>'                                          # 6 percent
    '<xf numFmtId="3" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyNumberFormat="1"/>'                                            # 7 idr
    '<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>'                                      # 8 total text
    '<xf numFmtId="3" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyNumberFormat="1"/>'                # 9 total int
    '<xf numFmtId="164" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyNumberFormat="1"/>'              # 10 total pct
    '<xf numFmtId="3" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyNumberFormat="1"/>'                # 11 total idr
    '<xf numFmtId="3" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyNumberFormat="1" applyAlignment="1">'
    '<alignment horizontal="center"/></xf>'                                                                                                           # 12 center int
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'                                                                    # 13 bold
    '</cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _esc_attr(s):
    return _esc(s).replace('"', "&quot;")


def _col_letter(idx):
    s = ""
    idx += 1
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        s = chr(65 + rem) + s
    return s


def _sheet_xml(sheet):
    rows = sheet["rows"]
    max_col = max((len(r) for r in rows), default=0)
    max_row = len(rows)
    dim_ref = "A1:%s%d" % (_col_letter(max(max_col, 1) - 1), max(max_row, 1))

    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    out.append('<dimension ref="%s"/>' % dim_ref)
    freeze = sheet.get("freeze")
    if freeze:
        fr, fc = freeze
        ys, xs = fr - 1, fc - 1
        tl = _col_letter(fc - 1) + str(fr)
        out.append('<sheetViews><sheetView workbookViewId="0"><pane xSplit="%d" ySplit="%d" '
                   'topLeftCell="%s" activePane="bottomRight" state="frozen"/>'
                   '<selection pane="bottomRight"/></sheetView></sheetViews>' % (xs, ys, tl))
    else:
        out.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
    out.append('<sheetFormatPr defaultRowHeight="15"/>')
    widths = sheet.get("widths")
    if widths:
        cols = "".join('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (j + 1, j + 1, w)
                       for j, w in enumerate(widths) if w)
        out.append("<cols>%s</cols>" % cols)
    out.append("<sheetData>")
    for ri, row in enumerate(sheet["rows"], start=1):
        cells = []
        for ci, cell in enumerate(row):
            if cell is None:
                continue
            val, st = cell
            ref = _col_letter(ci) + str(ri)
            if isinstance(val, bool):
                val = str(val)
            if isinstance(val, (int, float)):
                num = int(val) if float(val).is_integer() else val
                cells.append('<c r="%s" s="%d"><v>%s</v></c>' % (ref, st, num))
            elif val is None or val == "":
                cells.append('<c r="%s" s="%d"/>' % (ref, st))
            else:
                cells.append('<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                             % (ref, st, _esc(val)))
        out.append('<row r="%d">%s</row>' % (ri, "".join(cells)))
    out.append("</sheetData>")
    af = sheet.get("autofilter")
    if af:
        out.append('<autoFilter ref="%s"/>' % af)
    out.append("</worksheet>")
    return "".join(out)


def write_xlsx(path, sheets):
    parts = {}
    overrides = "".join(
        '<Override PartName="/xl/worksheets/sheet%d.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1)
        for i in range(len(sheets)))
    parts["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        + overrides + "</Types>")
    parts["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>')

    now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    parts["docProps/core.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:creator>Undercover</dc:creator><cp:lastModifiedBy>Undercover</cp:lastModifiedBy>'
        '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
        '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
        '</cp:coreProperties>' % (now_iso, now_iso))
    titles = "".join('<vt:lpstr>%s</vt:lpstr>' % _esc(s["name"]) for s in sheets)
    parts["docProps/app.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Microsoft Excel</Application><DocSecurity>0</DocSecurity>'
        '<ScaleCrop>false</ScaleCrop>'
        '<HeadingPairs><vt:vector size="2" baseType="variant">'
        '<vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
        '<vt:variant><vt:i4>%d</vt:i4></vt:variant></vt:vector></HeadingPairs>'
        '<TitlesOfParts><vt:vector size="%d" baseType="lpstr">%s</vt:vector></TitlesOfParts>'
        '<LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc>'
        '<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0300</AppVersion>'
        '</Properties>' % (len(sheets), len(sheets), titles))

    sheets_xml = "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>'
                         % (_esc_attr(s["name"]), i + 1, i + 1) for i, s in enumerate(sheets))
    parts["xl/workbook.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="20000" windowHeight="12000"/></bookViews>'
        '<sheets>%s</sheets>'
        '<calcPr calcId="0"/>'
        '</workbook>' % sheets_xml)
    rels = "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>'
                   % (i + 1, i + 1) for i in range(len(sheets)))
    rels += ('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
             % (len(sheets) + 1))
    parts["xl/_rels/workbook.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>' % rels)
    parts["xl/styles.xml"] = STYLES_XML
    for i, s in enumerate(sheets):
        parts["xl/worksheets/sheet%d.xml" % (i + 1)] = _sheet_xml(s)

    # Urutan penulisan entri zip: [Content_Types].xml duluan (konvensi OPC/Excel).
    order = ["[Content_Types].xml", "_rels/.rels", "docProps/core.xml", "docProps/app.xml",
             "xl/workbook.xml", "xl/_rels/workbook.xml.rels", "xl/styles.xml"]
    order += ["xl/worksheets/sheet%d.xml" % (i + 1) for i in range(len(sheets))]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in order:
            z.writestr(name, parts[name])


# =====================================================================
#  BANGUN OUTPUT (4 sheet)
# =====================================================================
def build_output(agg, diag, out_path, root):
    model_qty = defaultdict(int)
    model_val = defaultdict(float)
    model_types = defaultdict(set)
    model_skus = defaultdict(set)
    for (model, tipe, gen, warna), rec in agg.items():
        model_qty[model] += rec["qty"]
        model_val[model] += rec["value"]
        model_types[model].add(tipe)
        model_skus[model] |= rec["skus"]

    ranked = sorted(model_qty.keys(), key=lambda m: (-model_qty[m], -model_val[m], m))
    top_models = ranked[:TOP_N]
    top_set = set(top_models)
    rank_of = {m: i + 1 for i, m in enumerate(top_models)}
    grand_qty = sum(model_qty.values())
    grand_val = sum(model_val.values())

    sheets = []

    # ---------- Sheet 1: Top 300 Mobil ----------
    rows1 = []
    rows1.append([("MOBIL TERLARIS - Top %d Model (Detail Gen & Warna)" % TOP_N, S_TITLE)])
    rows1.append([("Sumber: order Shopee/TikTok/Lazada semua toko. Hanya pesanan sukses "
                   "(batal/belum bayar/refund dikeluarkan). Nilai = net setelah diskon. "
                   "Lihat sheet 'Metodologi'.", S_SUB)])
    rows1.append([])
    headers1 = ["No", "Nama Mobil", "Satuan", "Total Kuantitas", "% Kuantitas",
                "Total Penjualan (Rp)", "% Nilai", "Jenis Cover Digabung", "Jumlah Varian/SKU"]
    rows1.append([(h, S_HEAD) for h in headers1])
    for i, model in enumerate(top_models, start=1):
        rows1.append([
            (i, S_INT), (model, S_TXT), (SATUAN, S_TXT),
            (model_qty[model], S_INT),
            ((model_qty[model] / grand_qty) if grand_qty else 0, S_PCT),
            (round(model_val[model]), S_IDR),
            ((model_val[model] / grand_val) if grand_val else 0, S_PCT),
            (", ".join(sorted(model_types[model])), S_TXT),
            (len(model_skus[model]), S_INT),
        ])
    rows1.append([
        ("", S_TTXT), ("TOTAL (semua model, termasuk di luar Top %d)" % TOP_N, S_TTXT),
        ("", S_TTXT), (grand_qty, S_TINT), (1.0 if grand_qty else 0, S_TPCT),
        (round(grand_val), S_TIDR), (1.0 if grand_val else 0, S_TPCT),
        ("", S_TTXT), ("", S_TTXT),
    ])
    sheets.append({"name": "Top 300 Mobil", "rows": rows1,
                   "widths": [5, 26, 7, 15, 11, 20, 9, 34, 14], "freeze": (5, 1)})

    # ---------- Sheet 2: Detail Gen & Warna ----------
    rows2 = []
    rows2.append([("Detail Penjualan per Model + Jenis Cover + Gen + Warna (Top %d model)" % TOP_N, S_TITLE)])
    rows2.append([])
    headers2 = ["Peringkat", "Nama Mobil", "Jenis Cover", "Gen", "Warna",
                "Kuantitas", "% dari Model", "Total Penjualan (Rp)", "Jumlah SKU"]
    rows2.append([(h, S_HEAD) for h in headers2])
    detail = []
    for (model, tipe, gen, warna), rec in agg.items():
        if model in top_set:
            detail.append((rank_of[model], model, tipe, gen, warna,
                           rec["qty"], rec["value"], len(rec["skus"])))
    detail.sort(key=lambda x: (x[0], -x[5], -x[6]))
    for (rank, model, tipe, gen, warna, qty, val, nsku) in detail:
        rows2.append([
            (rank, S_INT), (model, S_TXT), (tipe, S_TXT), (gen, S_TXT), (warna, S_TXT),
            (qty, S_INT), ((qty / model_qty[model]) if model_qty[model] else 0, S_PCT),
            (round(val), S_IDR), (nsku, S_INT),
        ])
    last2 = len(rows2)
    sheets.append({"name": "Detail Gen & Warna", "rows": rows2,
                   "widths": [10, 24, 13, 16, 16, 12, 12, 20, 11],
                   "freeze": (4, 1), "autofilter": "A3:I%d" % last2})

    # ---------- Sheet 3: Matriks Warna ----------
    warna_tot = defaultdict(int)
    cell_qty = defaultdict(int)
    rowkey_tot = defaultdict(int)
    rowkey_rank = {}
    for (model, tipe, gen, warna), rec in agg.items():
        if model not in top_set:
            continue
        warna_tot[warna] += rec["qty"]
        rk = (model, gen)
        cell_qty[(rk, warna)] += rec["qty"]
        rowkey_tot[rk] += rec["qty"]
        rowkey_rank[rk] = rank_of[model]
    warna_cols = [w for w, _ in sorted(warna_tot.items(), key=lambda x: (-x[1], x[0]))]
    rowkeys = sorted(rowkey_tot.keys(), key=lambda rk: (rowkey_rank[rk], -rowkey_tot[rk], rk[1]))

    rows3 = []
    rows3.append([("Matriks Kuantitas: baris = Model + Gen, kolom = Warna (Top %d model)" % TOP_N, S_TITLE)])
    rows3.append([])
    hdr3 = [("Nama Mobil", S_HEAD), ("Gen", S_HEAD)] + [(w, S_HEAD) for w in warna_cols] + [("Total", S_HEAD)]
    rows3.append(hdr3)
    col_tot = defaultdict(int)
    for rk in rowkeys:
        model, gen = rk
        r = [(model, S_TXT), (gen, S_TXT)]
        rtot = 0
        for w in warna_cols:
            q = cell_qty.get((rk, w), 0)
            r.append((q if q else "", S_CINT))
            rtot += q
            col_tot[w] += q
        r.append((rtot, S_CINT))
        col_tot["__grand__"] += rtot
        rows3.append(r)
    trow = [("TOTAL", S_TTXT), ("", S_TTXT)]
    for w in warna_cols:
        trow.append((col_tot[w], S_TINT))
    trow.append((col_tot["__grand__"], S_TINT))
    rows3.append(trow)
    widths3 = [24, 16] + [11] * len(warna_cols) + [11]
    sheets.append({"name": "Matriks Warna", "rows": rows3, "widths": widths3, "freeze": (4, 3)})

    # ---------- Sheet 4: Metodologi ----------
    L = []
    L.append(("MOBIL TERLARIS - Metodologi & Diagnostik", S_TITLE))
    L.append(("Dibuat: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), S_SUB))
    L.append(("Folder sumber: %s" % root, S_SUB))
    L.append(("", S_DEFAULT))
    L.append(("DEFINISI", S_BOLD))
    for t in [
        "- Cakupan: semua toko (Undercover/Otonation/Otopro/Smartpro) x Shopee/TikTok/Lazada.",
        "- Periode: sesuai file di folder.",
        "- Hanya MOBIL (Cover Mobil). Motor tidak masuk ranking.",
        "- Status dikeluarkan (bukan penjualan): " + ", ".join(STATUS_EXCLUDE) + ".",
        "- Kuantitas = qty terjual - qty diretur.",
        "- Total Penjualan = nilai NET setelah diskon (Shopee: Subtotal Pesanan; "
        "TikTok: SKU Subtotal After Discount; Lazada: paidPrice).",
        "- Model digabung lintas toko/marketplace berdasarkan nama model pada listing.",
        "- Tipe cover dari penanda warna (Elite/Warrior->Strip, Silver->Premium, "
        "Transparan->Transparan) lalu tier di nama produk.",
    ]:
        L.append((t, S_DEFAULT))
    L.append(("", S_DEFAULT))
    L.append(("DIAGNOSTIK (cek kewajaran angka)", S_BOLD))
    for t in [
        "- Total baris order terbaca: {:,}".format(diag.get("rows_total", 0)),
        "    Shopee: {:,} | TikTok: {:,} | Lazada: {:,}".format(
            diag.get("rows_shopee", 0), diag.get("rows_tiktok", 0), diag.get("rows_lazada", 0)),
        "- Baris dihitung (mobil, sukses): {:,}".format(diag.get("rows_counted", 0)),
        "- Baris motor (dilewati): {:,}".format(diag.get("rows_motor", 0)),
        "- Dilewati krn status batal/refund/belum bayar: {:,}".format(diag.get("skip_status", 0)),
        "- Dilewati krn qty net <= 0 (retur penuh): {:,}".format(diag.get("skip_returned", 0)),
        "- Dilewati krn nama model tidak terbaca: {:,}".format(diag.get("skip_no_model", 0)),
        "- Jumlah model mobil unik: {:,}".format(len(model_qty)),
        "- Total kuantitas semua model: {:,}".format(grand_qty),
        "- Total nilai semua model: Rp {:,}".format(round(grand_val)),
    ]:
        L.append((t, S_DEFAULT))
    if diag.get("_sample_no_model"):
        L.append(("", S_DEFAULT))
        L.append(("Contoh nama produk yang model-nya tidak terbaca:", S_BOLD))
        for s in diag["_sample_no_model"]:
            L.append(("   " + s, S_DEFAULT))
    if diag.get("_errors"):
        L.append(("", S_DEFAULT))
        L.append(("File gagal dibaca:", S_BOLD))
        for s in diag["_errors"]:
            L.append(("   " + s, S_DEFAULT))
    rows4 = [[(t, st)] for (t, st) in L]
    sheets.append({"name": "Metodologi", "rows": rows4, "widths": [115]})

    write_xlsx(out_path, sheets)
    return len(model_qty), grand_qty, grand_val


# =====================================================================
#  MAIN
# =====================================================================
def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FOLDER
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DEFAULT
    if not os.path.isdir(root):
        print("ERROR: folder tidak ditemukan: %s" % root)
        print("Jalankan: python buat_matriks_terlaris.py \"<folder data sales>\"")
        sys.exit(1)

    print("Memindai folder: %s" % os.path.abspath(root))
    files, tmpdirs = gather_files(root)
    print("Menemukan %d file order (xlsx/zip)." % len(files))
    if not files:
        print("Tidak ada file .xlsx/.zip. Pastikan folder benar.")
        sys.exit(1)

    agg = defaultdict(lambda: {"qty": 0, "value": 0.0, "skus": set()})
    diag = Counter()
    for i, (path, label) in enumerate(files, start=1):
        print("  [%d/%d] %s :: %s" % (i, len(files), label, os.path.basename(path)))
        process_workbook(path, agg, diag)

    print("Menulis output ...")
    nmodel, gq, gv = build_output(agg, diag, out_path, os.path.abspath(root))
    print("SELESAI. Model unik: %d, total qty: %s, total nilai: Rp %s"
          % (nmodel, format(gq, ","), format(round(gv), ",")))
    print("File output: %s" % os.path.abspath(out_path))

    for td in tmpdirs:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    main()
