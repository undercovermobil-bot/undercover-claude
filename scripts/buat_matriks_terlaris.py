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
    3 sheet:
      1. "Top 300 Mobil"       -> ranking per model + MATRIKS WARNA POLOS terintegrasi
                                  (kolom tiap warna diurut terlaris, baris TOTAL & % tiap warna)
      2. "Detail Gen & Warna"  -> tiap baris = Model + Jenis Cover + Gen + Warna
      3. "Metodologi"          -> definisi, filter, diagnostik (jumlah baris per marketplace)

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
import math
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
BUFFER_DAYS = 7   # siklus restock (hari) dipakai utk estimasi stok ideal = rata2/hari x BUFFER_DAYS
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

# --- Keluarga warna POLOS untuk kolom warna di sheet Top 300 ---
# Strip (Elite/Epic/Warrior/Strip-N) DIKELUARKAN; gen-bocor/junk DIBUANG.
# Premium/Exclusive/Transparan tetap ikut (Silver = warna Premium).
COLOR_FAMILIES = [
    ("Abu-abu", ["abu"]), ("Hitam", ["hitam"]), ("Hijau", ["hijau"]),
    ("Merah", ["merah"]), ("Biru", ["biru"]), ("Silver", ["silver"]),
    ("Putih", ["putih"]), ("Transparan", ["transparan", "transparant"]),
    ("Orange", ["orange", "oranye"]), ("Coklat", ["coklat", "cokelat"]),
    ("Kuning", ["kuning"]), ("Gold", ["gold", "emas"]),
]
STRIP_MARK = ("elite", "epic", "warrior", "warior", "strip")


def is_junk_warna(w):
    """True kalau token 'warna' sebetulnya gen bocor / bukan warna (mis. 'Gen 3 (2007-2012)', '500ml')."""
    s = (w or "").strip().lower()
    if s in ("", "(tanpa warna)"):
        return True
    if s.startswith("gen ") or "tahun" in s or "model lain" in s or "custom" in s or "reborn" in s:
        return True
    if re.search(r"\b(19|20)\d{2}\b", s):
        return True
    if re.search(r"\d+\s*(ml|l|liter)\b", s):
        return True
    if re.fullmatch(r"[\d\s./-]+", s or "x"):
        return True
    return False


def color_family(w):
    """Petakan token warna ke keluarga warna polos, atau None kalau tak dikenal."""
    s = (w or "").strip().lower()
    for fam, keys in COLOR_FAMILIES:
        if any(k in s for k in keys):
            return fam
    return None


STRIP_LEVEL_WORD = {"epic": 1, "elite": 2, "warrior": 3, "warior": 3}


def canon_strip_variant(w):
    """Label kanonik varian Strip: satukan brand lama ke level Strip 1/2/3
    (Epic=Strip 1, Elite=Strip 2, Warrior=Strip 3) - sudah dipakai bergantian
    dgn label 'Strip N' di data lama, jadi digabung jadi satu skema. Warna
    ekornya diseragamkan sama seperti warna polos (Abu -> Abu-abu, dst)."""
    s = re.sub(r"\s+", " ", str(w or "").strip())
    if not s:
        return "(strip lain)"
    m = re.match(r"^(epic|elite|warrior|warior)\b\s*(.*)$", s, re.I)
    if m:
        level = STRIP_LEVEL_WORD[m.group(1).lower()]
        color_part = m.group(2).strip()
    else:
        m = re.match(r"^strip\b\s*(\d+)?\s*(.*)$", s, re.I)
        if m:
            level = int(m.group(1)) if m.group(1) else None
            color_part = m.group(2).strip()
        else:
            level = None
            color_part = s
    if level is not None:
        return "Strip %d %s" % (level, canon_warna(color_part))
    if not color_part:
        return "(strip lain)"
    return "Strip %s" % canon_warna(color_part)


def sort_strip_cols(strip_tot):
    """Urutkan kolom Strip: kelompokkan per WARNA dulu (warna terlaris duluan),
    di dalam tiap warna urut level 1/2/3 - supaya tidak keliatan acak."""
    color_tot = defaultdict(int)
    parsed = {}
    for label, qty in strip_tot.items():
        m = re.match(r"^Strip (\d+) (.*)$", label)
        if m:
            level, color = int(m.group(1)), m.group(2)
        else:
            level, color = 99, label
        parsed[label] = (level, color)
        color_tot[color] += qty
    color_rank = {c: i for i, (c, _) in enumerate(sorted(color_tot.items(), key=lambda x: (-x[1], x[0])))}
    return sorted(strip_tot.keys(), key=lambda l: (color_rank[parsed[l][1]], parsed[l][0]))

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
# frasa cover di depan nama produk: cover/sarung/selimut (rantai '/' boleh) + mobil/motor
_COVER_RE = re.compile(
    r"(?:body\s+)?(?:cover|sarung|selimut)(?:\s*/\s*(?:cover|sarung|selimut))*\s+(?:mobil|motor)", re.I)


def parse_name(name):
    if name is None:
        return None, None, False
    n = str(name).strip()
    low = n.lower()
    is_motor = False
    m = None
    for mm in _COVER_RE.finditer(n):
        m = mm
    if m:
        is_motor = "motor" in m.group().lower()
        n = n[m.end():]
    else:
        is_motor = ("cover motor" in low) or ("selimut motor" in low) or ("sarung motor" in low)
        for p in NAME_PREFIXES:
            idx = n.lower().find(p.lower())
            if idx != -1:
                n = n[idx + len(p):]
                break
    n = n.strip(" -/")
    n = re.sub(r"^(transparan|transparant)\s+", "", n, flags=re.I)
    n = re.sub(r"\s*\((?:j|jj)\)\s*$", "", n, flags=re.I)
    n = re.sub(r"\s*-\s*(undercover autocare|undercover|otonation|otoprotection|otopro|smartprotection|smartpro)\s*$", "", n, flags=re.I)

    _TIER_W = ("transparant", "transparan", "exclusive", "premium", "reguler", "strip")
    _COVER_W = ("indoor", "outdoor", "extreme", "semi", "dan")   # kata cakupan/penghubung
    tier = None
    # 1) potong di ' - <tier/cakupan>' pertama, mis.
    #    'Sigra - Reguler - Indoor dan Outdoor' -> 'Sigra' ; catat tier bila ada
    cut = re.search(r"\s+[-–]\s+(?=(?:" + "|".join(_TIER_W + _COVER_W) + r")\b)", n, re.I)
    if cut:
        suffix = n[cut.start():]
        n = n[:cut.start()]
        mt = re.search(r"\b(" + "|".join(_TIER_W) + r")\b", suffix, re.I)
        if mt:
            w = mt.group(1).lower()
            tier = "Transparan" if w.startswith("transparan") else mt.group(1).title()
    # 2) buang kata tier/cakupan yang menempel di akhir (berulang); catat tier pertama
    for _ in range(6):
        m2 = re.search(r"[\s/(-]*\b(" + "|".join(_TIER_W + _COVER_W) + r")\b\s*\)?\s*$", n, re.I)
        if not m2:
            break
        w = m2.group(1).lower()
        if tier is None and w in _TIER_W:
            tier = "Transparan" if w.startswith("transparan") else m2.group(1).title()
        n = n[:m2.start()].rstrip(" -/(")
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
        # fallback HANYA kalau token pertama bukan gen (hindari gen bocor jadi warna)
        if not _looks_like_gen(parts[0]):
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
        "date": ["waktu pesanan dibuat"],
    },
    "tiktok": {
        "status": ["order status"], "product": ["product name"],
        "variation": ["variation"], "qty": ["quantity"],
        "returned": ["sku quantity of return"],
        "value": ["sku subtotal after discount"], "sku": ["seller sku"],
        "date": ["created time"],
    },
    "lazada": {
        "status": ["status"], "product": ["itemname"],
        "variation": ["variation"], "qty": [], "returned": [],
        "value": ["paidprice"], "sku": ["sellersku"],
        "date": ["createtime"],
    },
}

_BULAN_ID = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6,
             "jul": 7, "agu": 8, "aug": 8, "sep": 9, "okt": 10, "oct": 10,
             "nov": 11, "des": 12, "dec": 12}


def parse_date_any(s):
    """Parse tanggal order dari berbagai format (Shopee/TikTok/Lazada) -> datetime.date atau None."""
    if s is None:
        return None
    if isinstance(s, datetime.datetime):
        return s.date()
    if isinstance(s, datetime.date):
        return s
    txt = str(s).strip()
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", txt)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", txt)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})", txt)
    if m:
        mo = _BULAN_ID.get(m.group(2)[:3].lower())
        if mo:
            try:
                return datetime.date(int(m.group(3)), mo, int(m.group(1)))
            except ValueError:
                return None
    return None


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


# =====================================================================
#  ACUAN VARIAN UNDERCOVER (file mass-update) -> penyetaraan GEN
#  Gen historis yg beragam (Gen 1F, Gen 2F, tahun, dll) disamakan dengan
#  gen di listing Undercover TERKINI (mis. Avanza -> Gen 1-2 / Gen 3).
# =====================================================================
def _gen_years(s):
    ys = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", str(s or ""))]
    return (min(ys), max(ys)) if ys else None


def _gen_nums(label):
    gp = re.sub(r"\(.*?\)", "", str(label or ""))
    return frozenset(int(d) for d in re.findall(r"\d+", gp) if int(d) < 20)


def _sku_gcode(sku):
    for t in re.split(r"[-_]", str(sku or "").upper()):
        m = re.match(r"^G(\d+)$", t)
        if m:
            return int(m.group(1))
    return None


def _gen_words(label):
    gp = re.sub(r"\(.*?\)", " ", str(label or "")).lower()
    return set(re.findall(r"[a-z]{4,}", gp)) - {"gen", "model", "tahun", "lain",
                                                "facelift", "sekarang"}


def is_reference_header(row):
    """True bila baris ini header file mass-update (daftar varian), bukan order."""
    low = set(norm(c) for c in row)
    return ("nama variasi" in low and ("sku induk" in low or "kode produk" in low)
            and "status pesanan" not in low and "order status" not in low)


def reference_columns(row):
    low = [norm(c) for c in row]

    def idx(name):
        return low.index(name) if name in low else None
    return {"product": idx("nama produk"), "variation": idx("nama variasi"), "sku": idx("sku")}


def accumulate_canonical(rows, hidx, cols, canon_reg, canon_all):
    if cols.get("product") is None or cols.get("variation") is None:
        return
    for row in rows[hidx + 1:]:
        p = get(row, cols["product"])
        v = get(row, cols["variation"])
        sku = get(row, cols.get("sku"))
        if not (p and v):
            continue
        model, tier, is_motor = parse_name(p)
        if is_motor or not model:
            continue
        _w, gen_raw, _t = parse_variation(v)
        if not gen_raw:
            continue
        label = re.sub(r"\s+", " ", str(gen_raw)).strip()
        tgt = canon_reg if tier == "Reguler" else canon_all
        d = tgt[model].setdefault(label, {"label": label, "years": _gen_years(label),
                                          "nums": _gen_nums(label), "words": _gen_words(label),
                                          "code": None})
        c = _sku_gcode(sku)
        if c is not None and d["code"] is None:
            d["code"] = c


def finalize_canonical(canon_reg, canon_all):
    """Per model: pakai gen dari listing Reguler (yg sudah diringkas) kalau ada,
    kalau tidak baru dari tipe cover lain."""
    out = {}
    for model in set(canon_reg) | set(canon_all):
        gens = canon_reg.get(model) or canon_all.get(model)
        if gens:
            out[model] = list(gens.values())
    return out


# =====================================================================
#  ACUAN FORMULA COVER (mobil beda gen tapi 1 formula/pola fisik yang sama)
#  File referensi: "Nama Mobil | Generasi | Total Formula". Kalau Total
#  Formula == 1 utk suatu model (walau ada >1 baris Generasi tercantum),
#  gen model itu digabung jadi 1 - krn secara fisik memang 1 SKU/pola cover
#  yang sama dipakai lintas gen tsb.
# =====================================================================
GEN_MERGE_LABEL = "Semua Gen (1 Formula)"


def is_formula_header(row):
    low = set(norm(c) for c in row)
    return "nama mobil" in low and "total formula" in low and ("generasi" in low or "formula" in low)


def formula_columns(row):
    low = [norm(c) for c in row]

    def idx(*names):
        for n in names:
            if n in low:
                return low.index(n)
        return None
    return {"no": idx("no"), "nama": idx("nama mobil"), "gen": idx("generasi", "formula"),
            "total": idx("total formula")}


def accumulate_formula_simple(rows, hidx, cols, simple_models):
    """Parse blok per-model (baris dgn 'No' terisi = mulai blok baru; baris
    berikutnya tanpa 'No' masih bagian model yg sama). Kalau Total Formula==1
    utk blok itu, tandai model tsb sbg gen-agnostic (>=1 baris Generasi)."""
    if cols.get("nama") is None or cols.get("total") is None:
        return
    cur_model = None
    cur_total = None
    cur_gens = 0

    def flush():
        # cuma berlaku kalau memang ada >1 baris Generasi yg DIGABUNG jadi 1 formula -
        # kalau cuma 1 baris gen & total=1, tidak ada yg perlu disederhanakan
        if cur_model and cur_total == 1 and cur_gens > 1:
            key = re.sub(r"\s+", " ", str(cur_model)).strip().lower()
            if key:
                simple_models.add(key)
    for row in rows[hidx + 1:]:
        no = get(row, cols.get("no"))
        nama = get(row, cols["nama"])
        gen = get(row, cols.get("gen"))
        total = get(row, cols["total"])
        if no not in (None, ""):
            flush()
            cur_model, cur_total, cur_gens = nama, None, 0
        if cur_model is None:
            continue
        if total not in (None, ""):
            try:
                cur_total = int(float(total))
            except (TypeError, ValueError):
                pass
        if gen not in (None, "", "-"):
            cur_gens += 1
    flush()


def map_gen(model, gen_raw, sku, canonical):
    """Petakan gen historis -> gen kanonik Undercover (urut: kode SKU, kata khas,
    tahun, nomor gen, lalu fallback)."""
    cgs = canonical.get(model)
    if not cgs:
        return canon_gen(gen_raw)
    c = _sku_gcode(sku)
    if c is not None:
        h = [g for g in cgs if g["code"] == c]
        if len(h) == 1:
            return h[0]["label"]
    sw = _gen_words(gen_raw)
    if sw:
        h = [g for g in cgs if g["words"] & sw]
        if len(h) == 1:
            return h[0]["label"]
    yr = _gen_years(gen_raw)
    if yr:
        h = [g for g in cgs if g["years"] and not (yr[1] < g["years"][0] or yr[0] > g["years"][1])]
        if len(h) == 1:
            return h[0]["label"]
        if len(h) > 1:
            h.sort(key=lambda g: -(min(yr[1], g["years"][1]) - max(yr[0], g["years"][0])))
            return h[0]["label"]
    ns = _gen_nums(gen_raw)
    if ns:
        h = [g for g in cgs if ns & g["nums"]]
        if len(h) == 1:
            return h[0]["label"]
        if len(h) > 1:
            h.sort(key=lambda g: -len(ns & g["nums"]))
            return h[0]["label"]
    if len(cgs) == 1:
        return cgs[0]["label"]
    return "Model/Tahun Lain"


# =====================================================================
#  PROSES 1 ITEM ORDER
# =====================================================================
def _net_qty_value(market, qty_raw, ret_raw, value_raw):
    """Qty net (terjual - retur) & nilai net proporsional. None kalau net_qty<=0."""
    if market == "lazada":
        qty = 1
    else:
        qty = to_int(qty_raw) if qty_raw is not None else 1
        if qty <= 0:
            qty = 1
    ret = to_int(ret_raw) if ret_raw is not None else 0
    net_qty = qty - ret
    if net_qty <= 0:
        return None, None
    value = to_num(value_raw)
    if ret and qty:
        value = value * net_qty / qty
    return net_qty, value


def count_item(market, status_raw, product, variation, qty_raw, ret_raw, value_raw, sku,
               date_raw, agg, diag, canonical, period, simple_models):
    diag["rows_%s" % market] += 1
    diag["rows_total"] += 1
    status = norm(status_raw)
    if any(bad in status for bad in STATUS_EXCLUDE):
        diag["skip_status"] += 1
        return
    model, tier_name, is_motor = parse_name(product)
    if is_motor:
        diag["rows_motor"] += 1
        # Motor sengaja di luar cakupan ranking Top 300 (cover MOBIL), tapi
        # qty/nilainya tetap direkap di sini supaya % kontribusi motor vs
        # mobil bisa dilihat di sheet Metodologi (dulu cuma jumlah baris,
        # bukan qty/nilai riil - tidak bisa dipakai hitung persentase).
        net_qty, value = _net_qty_value(market, qty_raw, ret_raw, value_raw)
        if net_qty is not None:
            diag["motor_qty"] += net_qty
            diag["motor_value"] += value
        return
    if not model:
        diag["skip_no_model"] += 1
        if len(diag.setdefault("_sample_no_model", [])) < 15:
            diag["_sample_no_model"].append(str(product)[:70])
        return
    warna_raw, gen_raw, tier_w = parse_variation(variation)
    if warna_raw is None or gen_raw is None:
        # fallback ke kode SKU utk sisi yg belum ketemu (mis. produk Exclusive:
        # variasi cuma berisi Gen krn cuma 1 warna tetap, warnanya ada di ekor SKU)
        w2, g2 = warna_and_tier_from_sku(sku)
        warna_raw = warna_raw or w2
        gen_raw = gen_raw or g2
    warna = canon_warna(warna_raw)
    gen = map_gen(model, gen_raw, sku, canonical)      # <- disetarakan ke gen Undercover
    if model.strip().lower() in simple_models:
        gen = GEN_MERGE_LABEL                          # <- 1 formula fisik, gen tak dibedakan
        diag["gen_merged"] += 1
    tipe = tier_w or tier_name or "Reguler"

    net_qty, value = _net_qty_value(market, qty_raw, ret_raw, value_raw)
    if net_qty is None:
        diag["skip_returned"] += 1
        return

    sku_key = str(sku).strip() if sku else "%s|%s|%s|%s" % (model, tipe, gen, warna)
    rec = agg[(model, tipe, gen, warna)]
    rec["qty"] += net_qty
    rec["value"] += value
    rec["skus"].add(sku_key)
    diag["rows_counted"] += 1

    d = parse_date_any(date_raw)
    if d:
        if period.get("min") is None or d < period["min"]:
            period["min"] = d
        if period.get("max") is None or d > period["max"]:
            period["max"] = d


def scan_workbook(path, canon_reg, canon_all, simple_models, order_items, diag):
    """Baca 1 file. Kalau file acuan mass-update -> bangun gen kanonik. Kalau
    file acuan formula cover -> bangun simple_models. Kalau file order ->
    kumpulkan item minimal ke order_items. Return 'ref'/'formula'/'order'/None."""
    try:
        sheets = read_xlsx_rows(path)
    except Exception as e:
        diag["file_error"] += 1
        diag.setdefault("_errors", []).append("%s: %s" % (os.path.basename(path), e))
        return None
    kind = None
    for _sf, rows in sheets:
        mode = None
        hidx = None
        market = None
        colmap = None
        refcols = None
        formcols = None
        for i, row in enumerate(rows[:20]):
            if is_reference_header(row):
                mode = "ref"
                hidx = i
                refcols = reference_columns(row)
                break
            if is_formula_header(row):
                mode = "formula"
                hidx = i
                formcols = formula_columns(row)
                break
            res = detect_market_and_columns(row)
            if res:
                mode = "order"
                hidx = i
                market, colmap = res
                break
        if mode == "ref":
            accumulate_canonical(rows, hidx, refcols, canon_reg, canon_all)
            kind = kind or "ref"
        elif mode == "formula":
            accumulate_formula_simple(rows, hidx, formcols, simple_models)
            kind = kind or "formula"
        elif mode == "order":
            kind = "order"
            for row in rows[hidx + 1:]:
                product = get(row, colmap["product"])
                if product is None or str(product).strip() == "":
                    continue
                order_items.append((
                    market, get(row, colmap.get("status")), product,
                    get(row, colmap["variation"]), get(row, colmap.get("qty")),
                    get(row, colmap.get("returned")), get(row, colmap.get("value")),
                    get(row, colmap.get("sku")), get(row, colmap.get("date"))))
    return kind


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
S_DEC2, S_TDEC2, S_GHEAD = 14, 15, 16

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
    '<cellXfs count="17">'
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
    '<xf numFmtId="2" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyNumberFormat="1" applyAlignment="1">'
    '<alignment horizontal="center"/></xf>'                                                                                                           # 14 decimal 2 (center)
    '<xf numFmtId="2" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyNumberFormat="1" applyAlignment="1">'
    '<alignment horizontal="center"/></xf>'                                                                                                           # 15 total decimal 2
    '<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
    '<alignment horizontal="center" vertical="center" wrapText="1"/></xf>'                                                                            # 16 group header (merged)
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
    merges = sheet.get("merges")
    if merges:
        mc = "".join('<mergeCell ref="%s%d:%s%d"/>' % (_col_letter(c1 - 1), r1, _col_letter(c2 - 1), r2)
                     for (r1, c1, r2, c2) in merges)
        out.append('<mergeCells count="%d">%s</mergeCells>' % (len(merges), mc))
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


def canonicalize_model_casing(agg):
    """Gabungkan model yang cuma beda huruf besar/kecil (mis. 'Toyota HiAce' vs
    'Toyota Hiace') jadi satu nama. Casing pemenang = yang qty totalnya lebih
    besar (menang suara), biar tidak perlu daftar kamus per-brand."""
    qty_per_form = defaultdict(lambda: defaultdict(int))
    for (model, tipe, gen, warna), rec in agg.items():
        qty_per_form[model.lower()][model] += rec["qty"]
    canon = {}
    for _low, forms in qty_per_form.items():
        if len(forms) <= 1:
            continue
        winner = max(forms.items(), key=lambda x: (x[1], x[0]))[0]
        for form in forms:
            if form != winner:
                canon[form] = winner
    if not canon:
        return agg
    new_agg = defaultdict(lambda: {"qty": 0, "value": 0.0, "skus": set()})
    for (model, tipe, gen, warna), rec in agg.items():
        model2 = canon.get(model, model)
        dst = new_agg[(model2, tipe, gen, warna)]
        dst["qty"] += rec["qty"]
        dst["value"] += rec["value"]
        dst["skus"] |= rec["skus"]
    return new_agg


# =====================================================================
#  BANGUN OUTPUT (3 sheet)
# =====================================================================
def build_output(agg, diag, out_path, root, period_days=None):
    agg = canonicalize_model_casing(agg)
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

    # ---------- data WARNA POLOS per model (untuk kolom warna di Top 300) ----------
    # Strip/Elite/Epic/Warrior DIKELUARKAN; gen-bocor/junk dibuang.
    # Premium/Exclusive/Transparan ikut (Silver=Premium). Kolom diurut warna terlaris.
    fam_tot = defaultdict(int)
    fam_cell = defaultdict(int)      # (model, family) -> qty
    for (model, tipe, gen, warna), rec in agg.items():
        if model not in top_set:
            continue
        wl = (warna or "").strip().lower()
        if tipe == "Strip" or wl.startswith(STRIP_MARK):
            continue
        if tipe == "Transparan":
            # Produk Transparan biasanya tak punya varian warna asli - field
            # "warna"-nya sering kepakai utk gen/tahun/"Default" dsb, yg lolos
            # is_junk_warna tapi tak dikenal color_family -> dulu diam-diam
            # KEHILANGAN qty-nya (tak masuk blok manapun). Kalau memang ada
            # warna asli yg dikenali (bukan Silver), tetap pakai itu; kalau
            # tidak, masukkan ke kolom "Transparan" sendiri.
            fam = color_family(warna)
            if fam is None or fam == "Silver":
                fam = "Transparan"
        else:
            if is_junk_warna(warna):
                continue
            fam = color_family(warna)
            if fam is None:
                continue
            if fam == "Silver":
                continue  # Silver = penanda tier Premium itu sendiri, bukan warna polos
                          # yg tersedia lintas tier spt Abu-abu/Hitam/dll - lihat Detail Premium
        fam_tot[fam] += rec["qty"]
        fam_cell[(model, fam)] += rec["qty"]
    fam_cols = [f for f, _ in sorted(fam_tot.items(), key=lambda x: (-x[1], x[0]))]
    grand_fam = sum(fam_tot.values())

    # ---------- data DETAIL Strip / Premium / Exclusive (kolom tambahan Top 300) ----------
    # Strip: label apa adanya (Elite Abu, Epic Merah, dst) - TIDAK termasuk di warna polos.
    # Premium/Exclusive: dipecah per warna polos - SUDAH termasuk (subset) di warna polos.
    strip_tot = defaultdict(int); strip_cell = defaultdict(int)
    prem_tot = defaultdict(int); prem_cell = defaultdict(int)
    excl_tot = defaultdict(int); excl_cell = defaultdict(int)
    for (model, tipe, gen, warna), rec in agg.items():
        if model not in top_set:
            continue
        wl = (warna or "").strip().lower()
        if tipe == "Strip" or wl.startswith(STRIP_MARK):
            label = canon_strip_variant(warna)
            strip_tot[label] += rec["qty"]
            strip_cell[(model, label)] += rec["qty"]
            continue
        if is_junk_warna(warna):
            continue
        fam = color_family(warna)
        if fam is None:
            continue
        if tipe == "Premium":
            prem_tot[fam] += rec["qty"]
            prem_cell[(model, fam)] += rec["qty"]
        elif tipe == "Exclusive":
            excl_tot[fam] += rec["qty"]
            excl_cell[(model, fam)] += rec["qty"]
    strip_cols = sort_strip_cols(strip_tot)
    prem_cols = [f for f, _ in sorted(prem_tot.items(), key=lambda x: (-x[1], x[0]))]
    excl_cols = [f for f, _ in sorted(excl_tot.items(), key=lambda x: (-x[1], x[0]))]

    def velocity(qty):
        return (qty / period_days) if period_days else None

    sheets = []

    # ---------- Sheet 1: Top 300 Mobil (+ matriks warna & detail varian terintegrasi) ----------
    NBASE = 10  # No..Jumlah Varian/SKU (9) + Rata-rata/Hari (1)
    rows1 = []
    rows1.append([("MOBIL TERLARIS - Top %d Model (Detail Gen & Warna)" % TOP_N, S_TITLE)])
    rows1.append([("Sumber: order Shopee/TikTok/Lazada semua toko. Hanya pesanan sukses "
                   "(batal/belum bayar/refund dikeluarkan). Nilai = net setelah diskon. "
                   "'Warna Polos' = gabungan Reguler+Premium+Exclusive+Transparan tanpa Strip, "
                   "TANPA Silver (Silver = penanda tier Premium itu sendiri, lihat Detail Premium). "
                   "Blok 'Detail Premium/Exclusive' adalah RINCIAN yang sudah termasuk di Warna "
                   "Polos (jangan dijumlahkan lagi, kecuali Silver yg memang di luar Warna Polos); "
                   "blok 'Detail Strip' terpisah (tidak masuk Warna Polos). Semua '% <label>' "
                   "dihitung dari TOTAL PENJUALAN MODEL ITU (semua tier & warna) - bukan dari "
                   "total blok itu sendiri. Rata-rata/Hari = estimasi kecepatan jual, lihat "
                   "'Metodologi'.", S_SUB)])
    rows1.append([])

    # setiap blok warna (Warna Polos, Strip, Premium, Exclusive) dapat struktur
    # yang sama: qty per label -> Total -> % per label -> Rata-rata/Hari per label
    def block_spec(raw_keys, disp_labels, cell_dict, tot_dict):
        return {"raw": raw_keys, "disp": disp_labels, "cell": cell_dict, "tot": tot_dict,
                "grand": sum(tot_dict.values())}

    blocks = []
    if fam_cols:
        blocks.append(("WARNA POLOS (Reguler+Premium+Exclusive+Transparan, tanpa Strip)", "Warna Polos",
                       block_spec(fam_cols, fam_cols, fam_cell, fam_tot)))
    if strip_cols:
        blocks.append(("DETAIL STRIP 1/2/3 (Epic=1,Elite=2,Warrior=3; di luar Warna Polos)", "Strip",
                       block_spec(strip_cols, strip_cols, strip_cell, strip_tot)))
    if prem_cols:
        blocks.append(("DETAIL PREMIUM (subset dari Warna Polos)", "Premium",
                       block_spec(prem_cols, ["Premium " + f for f in prem_cols], prem_cell, prem_tot)))
    if excl_cols:
        blocks.append(("DETAIL EXCLUSIVE (subset dari Warna Polos)", "Exclusive",
                       block_spec(excl_cols, ["Exclusive " + f for f in excl_cols], excl_cell, excl_tot)))

    headers1 = ["No", "Nama Mobil", "Satuan", "Total Kuantitas", "% Kuantitas",
                "Total Penjualan (Rp)", "% Nilai", "Jenis Cover Digabung", "Jumlah Varian/SKU",
                "Rata-rata Terjual/Hari"]
    for _title, name, spec in blocks:
        headers1 += spec["disp"] + ["Total " + name] + ["% " + d for d in spec["disp"]] \
            + ["Rata-rata/Hari " + d for d in spec["disp"]]

    # baris grup (merged) di atas header kolom
    grouprow = [""] * len(headers1)
    merges = []

    def add_group(col, label, span):
        grouprow[col - 1] = label
        if span > 1:
            merges.append((GROW, col, GROW, col + span - 1))
        return col + span

    col = NBASE + 1  # 1-indexed kolom pertama blok pertama (row grup = row 4, header = row 5)
    GROW = 4
    HROW = 5
    for title, _name, spec in blocks:
        n = len(spec["raw"])
        span = n + 1 + n + n  # qty + total + % + rata2/hari
        col = add_group(col, title, span)
    rows1.append([(g, S_GHEAD) for g in grouprow])
    rows1.append([(h, S_HEAD) for h in headers1])

    for i, model in enumerate(top_models, start=1):
        row = [
            (i, S_INT), (model, S_TXT), (SATUAN, S_TXT),
            (model_qty[model], S_INT),
            ((model_qty[model] / grand_qty) if grand_qty else 0, S_PCT),
            (round(model_val[model]), S_IDR),
            ((model_val[model] / grand_val) if grand_val else 0, S_PCT),
            (", ".join(sorted(model_types[model])), S_TXT),
            (len(model_skus[model]), S_INT),
        ]
        v = velocity(model_qty[model])
        row.append((v if v is not None else "", S_DEC2))
        mtot = model_qty[model]  # basis % = seluruh penjualan model ini (semua tier/warna)
        for _title, _name, spec in blocks:
            qtys = [spec["cell"].get((model, k), 0) for k in spec["raw"]]
            rtot = sum(qtys)
            for q in qtys:
                row.append((q if q else "", S_CINT))
            row.append((rtot, S_CINT))
            for q in qtys:
                row.append(((q / mtot) if mtot else 0, S_PCT))
            for q in qtys:
                vq = velocity(q)
                row.append((vq if vq is not None else "", S_DEC2))
        rows1.append(row)

    # baris TOTAL
    totrow = [
        ("", S_TTXT), ("TOTAL (semua model, termasuk di luar Top %d)" % TOP_N, S_TTXT),
        ("", S_TTXT), (grand_qty, S_TINT), (1.0 if grand_qty else 0, S_TPCT),
        (round(grand_val), S_TIDR), (1.0 if grand_val else 0, S_TPCT),
        ("", S_TTXT), ("", S_TTXT),
    ]
    vg = velocity(grand_qty)
    totrow.append((vg if vg is not None else "", S_TDEC2))
    for _title, _name, spec in blocks:
        grand = spec["grand"]
        for k in spec["raw"]:
            totrow.append((spec["tot"][k], S_TINT))
        totrow.append((grand, S_TINT))
        for k in spec["raw"]:
            totrow.append(((spec["tot"][k] / grand_qty) if grand_qty else 0, S_TPCT))
        for k in spec["raw"]:
            vf = velocity(spec["tot"][k])
            totrow.append((vf if vf is not None else "", S_TDEC2))
    rows1.append(totrow)

    widths1 = [5, 26, 7, 15, 11, 20, 9, 34, 14, 12]
    for _title, _name, spec in blocks:
        n = len(spec["raw"])
        widths1 += [11] * n + [13] + [10] * n + [13] * n
    sheets.append({"name": "Top 300 Mobil", "rows": rows1, "widths": widths1,
                   "freeze": (HROW + 1, 3), "merges": merges})

    # ---------- Sheet 2: Detail Gen & Warna ----------
    rows2 = []
    rows2.append([("Detail Penjualan per Model + Jenis Cover + Gen + Warna (Top %d model)" % TOP_N, S_TITLE)])
    rows2.append([("Rata-rata/Hari-Minggu-Bulan = estimasi kecepatan jual varian ini (qty terjual / "
                   "jumlah hari periode data). Estimasi Stok = rata-rata/hari x %d hari (buffer restock). "
                   "Lihat 'Metodologi' untuk definisi & keterbatasannya." % BUFFER_DAYS, S_SUB)])
    headers2 = ["Peringkat", "Nama Mobil", "Jenis Cover", "Gen", "Warna",
                "Kuantitas", "% dari Model", "Total Penjualan (Rp)", "Jumlah SKU",
                "Rata-rata/Hari", "Rata-rata/Minggu", "Rata-rata/Bulan",
                "Estimasi Stok (buffer %d hari)" % BUFFER_DAYS]
    rows2.append([(h, S_HEAD) for h in headers2])
    detail = []
    for (model, tipe, gen, warna), rec in agg.items():
        if model in top_set:
            detail.append((rank_of[model], model, tipe, gen, warna,
                           rec["qty"], rec["value"], len(rec["skus"])))
    detail.sort(key=lambda x: (x[0], -x[5], -x[6]))
    for (rank, model, tipe, gen, warna, qty, val, nsku) in detail:
        v = velocity(qty)
        row = [
            (rank, S_INT), (model, S_TXT), (tipe, S_TXT), (gen, S_TXT), (warna, S_TXT),
            (qty, S_INT), ((qty / model_qty[model]) if model_qty[model] else 0, S_PCT),
            (round(val), S_IDR), (nsku, S_INT),
        ]
        if v is None:
            row += [("", S_DEC2), ("", S_DEC2), ("", S_DEC2), ("", S_INT)]
        else:
            row += [(v, S_DEC2), (v * 7, S_DEC2), (v * 30, S_DEC2),
                    (math.ceil(v * BUFFER_DAYS), S_INT)]
        rows2.append(row)
    last2 = len(rows2)
    sheets.append({"name": "Detail Gen & Warna", "rows": rows2,
                   "widths": [10, 24, 13, 16, 16, 12, 12, 20, 11, 11, 12, 12, 16],
                   "freeze": (4, 1), "autofilter": "A3:M%d" % last2})

    # ---------- Sheet 3: Metodologi ----------
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
        "- Kolom warna di sheet 'Top 300 Mobil': hanya warna POLOS. "
        "Strip/Elite/Epic/Warrior dikeluarkan; Premium/Exclusive/Transparan ikut, "
        "TAPI Silver DIKELUARKAN dari Warna Polos (Silver = penanda tier Premium itu "
        "sendiri, bukan warna yg tersedia lintas tier spt Abu-abu/Hitam/dll - lihat "
        "Detail Premium). Warna gen-bocor/junk dibuang. Kolom diurut warna terlaris; "
        "ada blok jumlah + blok '% <warna>' + blok 'Rata-rata/Hari <warna>'.",
        "- GEN disetarakan dgn list Undercover terkini bila ada file acuan "
        "mass-update (daftar varian) di folder: gen historis (Gen 1F/2F/tahun/dll) "
        "dipetakan ke gen listing Reguler Undercover (mis. Avanza -> Gen 1-2 / Gen 3) "
        "via kode SKU / tahun / nomor gen. Tanpa file acuan, gen dibiarkan apa adanya.",
        "- GEN DIGABUNG jadi '%s' utk model yg secara fisik cuma pakai 1 formula/pola "
        "cover walau listing-nya punya >1 pilihan gen (mis. Honda Brio Gen 1 & Gen 2 = "
        "bentuk cover sama). Ini dari file acuan TERPISAH (\"Nama Mobil | Generasi | "
        "Total Formula\", Total Formula==1 meski >1 baris Generasi tercantum -> gen "
        "model itu digabung). Model dgn Total Formula>1 atau tak terdaftar di file itu "
        "TIDAK diubah (tetap pakai gen kanonik biasa)." % GEN_MERGE_LABEL,
        "- Sheet 'Top 300 Mobil' - blok 'DETAIL STRIP' (kolom Strip 1/2/3 <warna>): "
        "brand lama Elite/Epic/Warrior DISATUKAN ke skema Strip 1/2/3 (Epic=Strip 1, "
        "Elite=Strip 2, Warrior=Strip 3 - keduanya dipakai bergantian di data lama utk "
        "tier yg sama). TIDAK termasuk di 'Warna Polos' - jangan dijumlahkan lagi dgn "
        "blok itu.",
        "- Sheet 'Top 300 Mobil' - blok 'DETAIL PREMIUM' & 'DETAIL EXCLUSIVE': rincian per "
        "warna KHUSUS tier Premium/Exclusive. Ini SUBSET dari 'Warna Polos' (sudah ikut "
        "dihitung di sana) - disediakan cuma utk lihat kontribusi tier itu per warna, "
        "bukan angka tambahan baru.",
        "- Setiap blok warna (Warna Polos, Strip, Premium, Exclusive) punya struktur sama: "
        "qty per label -> 'Total <blok>' (jumlah blok itu saja) -> '% <label>' -> "
        "'Rata-rata/Hari <label>'. PENTING: basis '% <label>' BUKAN total blok itu, tapi "
        "TOTAL PENJUALAN MODEL ITU (semua tier & warna digabung) - jadi % Strip, % Premium, "
        "% Exclusive, dan % warna polos semuanya bisa dibandingkan langsung krn basisnya "
        "sama. Di baris model: qty label / Total Kuantitas model itu. Di baris TOTAL: "
        "total label di semua model / grand total kuantitas semua model.",
        "- RATA-RATA TERJUAL/HARI = estimasi kecepatan jual = qty terjual / jumlah hari "
        "periode data (dideteksi otomatis dari tanggal order paling awal s/d paling akhir "
        "di file order; kalau tanggal tidak terbaca, kolom ini dikosongkan). Dihitung di "
        "level model (sheet 'Top 300 Mobil') dan level varian penuh Model+Tipe+Gen+Warna "
        "(sheet 'Detail Gen & Warna', + versi /Minggu dan /Bulan).",
        ("- ESTIMASI STOK (buffer {0} hari) = Rata-rata/Hari x {0}, dibulatkan ke atas. Ini "
         "REKOMENDASI KASAR asumsi permintaan rata-rata konstan sepanjang periode data - "
         "BUKAN perhitungan inventory-turnover baku (yg butuh data stok riil, yang belum "
         "ada karena sistem produksi saat ini on-demand). Ubah BUFFER_DAYS di KONFIGURASI "
         "script kalau siklus restock/produksi sebenarnya beda. Varian baru yang baru "
         "diluncurkan di tengah periode akan under-estimate (belum terjual sepanjang periode)."
         ).format(BUFFER_DAYS),
    ]:
        L.append((t, S_DEFAULT))
    L.append(("", S_DEFAULT))
    L.append(("DIAGNOSTIK (cek kewajaran angka)", S_BOLD))
    for t in [
        "- File acuan varian (mass-update) terbaca: {:,} | model punya gen kanonik: {:,}".format(
            diag.get("ref_files", 0), diag.get("ref_models", 0)),
        "- File acuan formula cover terbaca: {:,} | model gen-agnostic (1 formula, gen "
        "digabung): {:,} | baris order yg gennya digabung: {:,}".format(
            diag.get("formula_files", 0), diag.get("formula_models", 0), diag.get("gen_merged", 0)),
        "- Periode data terdeteksi: {} s/d {} ({} hari) -> dipakai utk Rata-rata/Hari".format(
            diag.get("period_min", "-"), diag.get("period_max", "-"), diag.get("period_days", "-")),
        "- Total baris order terbaca: {:,}".format(diag.get("rows_total", 0)),
        "    Shopee: {:,} | TikTok: {:,} | Lazada: {:,}".format(
            diag.get("rows_shopee", 0), diag.get("rows_tiktok", 0), diag.get("rows_lazada", 0)),
        "- Baris dihitung (mobil, sukses): {:,}".format(diag.get("rows_counted", 0)),
        "- Baris motor (di luar ranking Top {:d}, tidak masuk mobil di atas): {:,} baris, "
        "{:,} pcs, Rp {:,} ({:.2%} dari total pcs mobil+motor)".format(
            TOP_N, diag.get("rows_motor", 0), diag.get("motor_qty", 0),
            round(diag.get("motor_value", 0)),
            (diag.get("motor_qty", 0) / (grand_qty + diag.get("motor_qty", 0)))
            if (grand_qty + diag.get("motor_qty", 0)) else 0),
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
    print("Menemukan %d file (xlsx/zip)." % len(files))
    if not files:
        print("Tidak ada file .xlsx/.zip. Pastikan folder benar.")
        sys.exit(1)

    # Fase 1: baca semua file -> bangun acuan gen kanonik (mass-update) +
    #         kumpulkan item order.
    canon_reg = defaultdict(dict)
    canon_all = defaultdict(dict)
    simple_models = set()
    order_items = []
    diag = Counter()
    nref = 0
    nform = 0
    for i, (path, label) in enumerate(files, start=1):
        print("  [%d/%d] %s :: %s" % (i, len(files), label, os.path.basename(path)))
        kind = scan_workbook(path, canon_reg, canon_all, simple_models, order_items, diag)
        if kind == "ref":
            nref += 1
        elif kind == "formula":
            nform += 1
    canonical = finalize_canonical(canon_reg, canon_all)
    diag["ref_files"] = nref
    diag["ref_models"] = len(canonical)
    diag["formula_files"] = nform
    diag["formula_models"] = len(simple_models)
    if nref:
        print("File acuan varian: %d | model dgn gen kanonik: %d (gen disetarakan)" % (nref, len(canonical)))
    else:
        print("Tidak ada file acuan mass-update -> gen dibiarkan apa adanya.")
    if nform:
        print("File acuan formula cover: %d | model gen-agnostic (1 formula): %d" % (nform, len(simple_models)))

    # Fase 2: proses tiap item order (pakai acuan gen), sekaligus lacak
    # tanggal order paling awal/akhir utk hitung rata-rata terjual/hari.
    agg = defaultdict(lambda: {"qty": 0, "value": 0.0, "skus": set()})
    period = {}
    for it in order_items:
        count_item(it[0], it[1], it[2], it[3], it[4], it[5], it[6], it[7], it[8],
                   agg, diag, canonical, period, simple_models)

    period_days = None
    if period.get("min") and period.get("max"):
        period_days = (period["max"] - period["min"]).days + 1
        print("Periode data terdeteksi: %s s/d %s (%d hari) -> dipakai utk rata-rata/hari"
              % (period["min"], period["max"], period_days))
    else:
        print("Tanggal order tidak terbaca dari data -> kolom rata-rata/hari dikosongkan.")
    diag["period_min"] = period.get("min")
    diag["period_max"] = period.get("max")
    diag["period_days"] = period_days

    print("Menulis output ...")
    nmodel, gq, gv = build_output(agg, diag, out_path, os.path.abspath(root), period_days)
    print("SELESAI. Model unik: %d, total qty: %s, total nilai: Rp %s"
          % (nmodel, format(gq, ","), format(round(gv), ",")))
    print("File output: %s" % os.path.abspath(out_path))

    for td in tmpdirs:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    main()
