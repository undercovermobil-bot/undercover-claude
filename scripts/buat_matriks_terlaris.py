#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buat_matriks_terlaris.py
========================
Bangun matriks penjualan MOBIL TERLARIS (Top 300) sampai detail GEN & WARNA,
dari data order mentah Shopee / TikTok / Lazada untuk SEMUA toko
(Undercover, Otonation, Otopro/Otoprotection, Smartpro/Smartprotection),
periode Jan - Jun 2026.

Kenapa berbentuk script (bukan file jadi):
    File order mentahnya puluhan @1-2 MB. Sesuai CLAUDE.md proyek ini, file besar
    TIDAK bisa ditarik lewat tool/MCP (mentok batas ukuran konten). Jadi
    pemrosesan dilakukan lokal di komputermu tempat folder Drive tersinkron.
    Bonus: bisa dipakai ulang tiap bulan.

Cara pakai (Windows / Mac / Linux):
    1. Pastikan Python 3 + openpyxl terpasang:
           pip install openpyxl
    2. Jalankan (arahkan ke folder 'Data Sales Jan - Jun 2026'):
           python buat_matriks_terlaris.py "C:\\path\\ke\\Data Sales Jan - Jun 2026"
       atau taruh script ini DI DALAM folder itu lalu jalankan tanpa argumen:
           python buat_matriks_terlaris.py
    3. Output default: MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx (buka di Excel/Google Sheets).

Argumen opsional:
    python buat_matriks_terlaris.py "<folder data>" "<nama output.xlsx>"

Isi output (4 sheet):
    1. "Top 300 Mobil"       -> ranking per model (gaya file MOBIL TERLARIS lama)
    2. "Detail Gen & Warna"  -> tiap baris = Model + Jenis Cover + Gen + Warna (qty & nilai)
    3. "Matriks Warna"       -> crosstab: baris Model-Gen, kolom Warna, isi = kuantitas
    4. "Metodologi"          -> definisi, filter, sumber, diagnostik (jumlah baris per marketplace)

Asumsi/definisi (bisa diubah di bagian KONFIGURASI di bawah):
    - Hanya MOBIL (Cover Mobil); motor diabaikan untuk ranking.
    - Pesanan BATAL / BELUM BAYAR / REFUND / RETUR dikeluarkan (tidak dihitung penjualan).
    - "Total Penjualan" = nilai NET setelah diskon (subtotal item setelah diskon).
    - Kuantitas = qty terjual dikurangi qty diretur.
    - Model digabung lintas toko & marketplace (Toyota Avanza dari toko mana pun = 1 model).
"""

import sys
import os
import re
import glob
import zipfile
import tempfile
import datetime
from collections import defaultdict, Counter

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# =====================================================================
#  KONFIGURASI  (ubah di sini kalau perlu)
# =====================================================================
TOP_N = 300                      # jumlah model teratas di sheet ringkasan
SATUAN = "PCS"
OUTPUT_DEFAULT = "MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx"

# Status yang DIKELUARKAN (dianggap bukan penjualan). Dicocokkan sebagai substring, huruf kecil.
STATUS_EXCLUDE = [
    "batal", "cancel", "belum bayar", "unpaid", "belum dibayar",
    "return", "retur", "refund", "pengembalian", "failed", "gagal", "lost",
]

# Kata penanda TIPE COVER dari token warna (mengikuti pola sku-sync-scripts/engine.py)
STRIP_PREFIX = ["Elite", "Epic", "Warrior", "Warior"]  # -> cover Strip
TIER_WORDS = ["Exclusive", "Premium", "Reguler", "Strip"]  # tier di akhir nama produk
# Prefix nama produk yang perlu dibuang untuk dapat nama model (Shopee/TikTok/Lazada/antar toko)
NAME_PREFIXES = [
    "Cover Mobil / Selimut Mobil ", "Body Cover Mobil / Selimut Mobil ",
    "Cover Mobil Transparan ", "Cover Mobil Transparant ",
    "Body Cover Mobil ", "Cover Mobil ",
    "Cover Motor / Selimut Motor ", "Body Cover Motor ", "Cover Motor ",
]

# Sinonim warna (huruf kecil -> bentuk kanonik) supaya tidak terpecah karena beda penulisan
WARNA_CANON = {
    "abu-abu": "Abu-abu", "abu abu": "Abu-abu", "abu": "Abu-abu",
    "hitam": "Hitam", "merah": "Merah", "biru": "Biru", "putih": "Putih",
    "silver": "Silver", "hijau army": "Hijau Army", "hijau": "Hijau",
    "coklat": "Coklat", "cream": "Cream", "krem": "Cream",
}

# Peta kode warna pada SKU baru (fallback kalau variasi kosong), mis. ...-G1-ABU
SKU_WARNA_CODE = {
    "ABU": "Abu-abu", "HTM": "Hitam", "MRH": "Merah", "BRU": "Biru",
    "PUT": "Putih", "SLV": "Silver", "SIL": "Silver", "HJA": "Hijau Army",
    "HJU": "Hijau", "CKL": "Coklat", "CRM": "Cream",
}

# =====================================================================
#  UTIL: parsing angka format Indonesia / internasional
# =====================================================================
def to_num(x):
    """Konversi nilai sel ke float. Menangani:
       - angka asli openpyxl (int/float) -> dipakai apa adanya
       - teks '307.490'  (titik = ribuan)      -> 307490
       - teks '287000.00'(titik = desimal 2)   -> 287000
       - teks '1.326.583'(titik ribuan ganda)  -> 1326583
       - teks '289,06'   (koma = desimal)       -> 289.06
    """
    if x is None:
        return 0.0
    if isinstance(x, bool):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", " ").replace(" ", "")
    if s in ("", "-", "--"):
        return 0.0
    # buang simbol mata uang / huruf di ekor (mis. 'gr', 'Rp')
    s = re.sub(r"[^0-9.,\-]", "", s)
    if s in ("", "-", "."):
        return 0.0
    if "," in s and "." in s:
        # format campuran -> titik ribuan, koma desimal
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    else:
        # hanya titik (atau tidak ada)
        if s.count(".") == 1:
            after = s.split(".")[1]
            if len(after) == 3:      # 3 digit di belakang -> ribuan (mis. 9.510)
                s = s.replace(".", "")
            # 1-2 digit -> anggap desimal, biarkan
        elif s.count(".") > 1:
            s = s.replace(".", "")   # titik ribuan ganda
    try:
        return float(s)
    except ValueError:
        return 0.0


def to_int(x):
    return int(round(to_num(x)))


def norm(s):
    """Normalisasi teks header/sel ke huruf kecil, rapikan spasi."""
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())


# =====================================================================
#  UTIL: parsing nama produk -> (model, tier, is_motor)
# =====================================================================
def parse_name(name):
    """Ambil nama model mobil dari nama produk listing.
       Mengembalikan (model, tier_dari_nama, is_motor).
       Contoh: 'Undercover Autocare - Cover Mobil Toyota Avanza Reguler'
               -> ('Toyota Avanza', 'Reguler', False)
    """
    if name is None:
        return None, None, False
    n = str(name).strip()
    low = n.lower()
    is_motor = ("cover motor" in low) or ("selimut motor" in low)

    # Buang segala prefix TOKO / brand di depan sampai frasa 'Cover Mobil/Motor'.
    # Cari kemunculan TERAKHIR dari frasa cover, ambil sisanya.
    m = None
    for mm in re.finditer(r"(?:body\s+)?cover\s+(?:mobil|motor)(?:\s*/\s*selimut\s+(?:mobil|motor))?", n, re.I):
        m = mm
    if m:
        n = n[m.end():]
    else:
        # fallback: buang prefix yang diketahui
        for p in NAME_PREFIXES:
            idx = n.lower().find(p.lower())
            if idx != -1:
                n = n[idx + len(p):]
                break

    n = n.strip(" -/")
    # buang penanda transparan yang mungkin nyangkut di depan
    n = re.sub(r"^(transparan|transparant)\s+", "", n, flags=re.I)
    # buang ekor pemasaran umum: '(J)', '- Undercover Autocare', dsb.
    n = re.sub(r"\s*\((?:j|jj)\)\s*$", "", n, flags=re.I)
    n = re.sub(r"\s*-\s*(undercover autocare|undercover|otonation|otoprotection|otopro|smartprotection|smartpro)\s*$", "", n, flags=re.I)

    # deteksi & buang tier di akhir
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


# =====================================================================
#  UTIL: parsing variasi -> (warna, gen, tier_dari_variasi)
# =====================================================================
def _looks_like_gen(tok):
    t = tok.lower()
    if "gen" in t or "model/tahun" in t or "tahun lain" in t:
        return True
    if re.search(r"\(\s*(?:19|20)\d{2}", tok):   # ada tahun dalam kurung
        return True
    if re.match(r"^[A-Za-z]?\d+[A-Za-z]?(\s*-\s*\d+)?$", tok.strip()):  # 'G1', '1F', '1-3'
        return True
    return False


def parse_variation(vari):
    """Pisahkan token variasi menjadi (warna, gen, tier_dari_warna).
       Menangani 3 format:
         Shopee : 'Abu-abu,Gen 1-3 (2002-2022)'  atau  'Gen 1F (2016-2018),Silver'
         Lazada : 'Warna:Abu-abu, Model:Gen 1 (2012-2023)'
         TikTok : sama-sama berbentuk 'warna,gen' atau berlabel
       tier_dari_warna: 'Strip' bila warna berawalan Elite/Warrior/Epic,
                        'Premium' bila 'Silver', 'Transparan' bila 'Transparan', else None.
    """
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
        # semua terlihat seperti gen; ambil yang pertama sebagai warna cadangan
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
    g = re.sub(r"\s*\(.*?\)\s*", " ", str(g))     # buang '(2002-2022)'
    g = re.sub(r"\s+", " ", g).strip()
    return g if g else "(tanpa gen)"


def warna_and_tier_from_sku(sku):
    """Fallback: ambil (warna, gen) dari SKU baru BRAND-MODEL-TOKO-TIER-G#-WARNA."""
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
#  DETEKSI MARKETPLACE + PEMETAAN KOLOM
# =====================================================================
FIELD_MAP = {
    "shopee": {
        "status": ["status pesanan"],
        "product": ["nama produk"],
        "variation": ["nama variasi"],
        "qty": ["jumlah"],
        "returned": ["returned quantity"],
        "value": ["subtotal pesanan"],
        "sku": ["nomor referensi sku", "sku induk"],
    },
    "tiktok": {
        "status": ["order status"],
        "product": ["product name"],
        "variation": ["variation"],
        "qty": ["quantity"],
        "returned": ["sku quantity of return"],
        "value": ["sku subtotal after discount"],
        "sku": ["seller sku"],
    },
    "lazada": {
        "status": ["status"],
        "product": ["itemname"],
        "variation": ["variation"],
        "qty": [],                 # 1 baris = 1 item
        "returned": [],
        "value": ["paidprice"],
        "sku": ["sellersku"],
    },
}


def detect_market_and_columns(header_cells):
    """Terima daftar sel header (sudah dinormalisasi lower), tentukan marketplace
       dan indeks kolom untuk tiap field. Return (market, colmap) atau None."""
    hs = [norm(c) for c in header_cells]
    hset = set(hs)

    def find(candidates, exact=True):
        for cand in candidates:
            if exact:
                for i, h in enumerate(hs):
                    if h == cand:
                        return i
            else:
                for i, h in enumerate(hs):
                    if cand in h:
                        return i
        # fallback contains
        for cand in candidates:
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
#  BACA SATU FILE ORDER
# =====================================================================
def get(row, idx):
    if idx is None or idx >= len(row):
        return None
    return row[idx]


def process_workbook(path, agg, diag, source_label):
    """Baca 1 file xlsx order, akumulasi ke `agg`. Update `diag` (Counter statistik)."""
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        diag["file_error"] += 1
        diag.setdefault("_errors", []).append(f"{os.path.basename(path)}: {e}")
        return

    for ws in wb.worksheets:
        market = None
        colmap = None
        header_found = False
        for row in ws.iter_rows(values_only=True):
            if not header_found:
                res = detect_market_and_columns(list(row))
                if res:
                    market, colmap = res
                    header_found = True
                continue

            product = get(row, colmap["product"])
            if product is None or str(product).strip() == "":
                continue
            diag[f"rows_{market}"] += 1
            diag["rows_total"] += 1

            # --- filter status ---
            status = norm(get(row, colmap["status"])) if colmap.get("status") is not None else ""
            if any(bad in status for bad in STATUS_EXCLUDE):
                diag["skip_status"] += 1
                continue

            # --- nama model & kategori ---
            model, tier_name, is_motor = parse_name(product)
            if is_motor:
                diag["rows_motor"] += 1
                continue
            if not model:
                diag["skip_no_model"] += 1
                if len(diag.setdefault("_sample_no_model", [])) < 15:
                    diag["_sample_no_model"].append(str(product)[:70])
                continue

            # --- warna, gen, tier ---
            warna_raw, gen_raw, tier_w = parse_variation(get(row, colmap["variation"]))
            if warna_raw is None and gen_raw is None:
                w2, g2 = warna_and_tier_from_sku(get(row, colmap.get("sku")))
                warna_raw = warna_raw or w2
                gen_raw = gen_raw or g2
            warna = canon_warna(warna_raw)
            gen = canon_gen(gen_raw)

            # tipe cover: prioritas penanda warna (Strip/Premium/Transparan), lalu tier nama
            tipe = tier_w or tier_name or "Reguler"

            # --- kuantitas & nilai ---
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
                value = value * net_qty / qty     # sesuaikan nilai bila ada retur sebagian

            sku = get(row, colmap.get("sku"))
            sku_key = str(sku).strip() if sku else f"{model}|{tipe}|{gen}|{warna}"

            # --- akumulasi ---
            rec = agg[(model, tipe, gen, warna)]
            rec["qty"] += net_qty
            rec["value"] += value
            rec["skus"].add(sku_key)
            rec["markets"].add(market)
            diag["rows_counted"] += 1
    wb.close()


# =====================================================================
#  KUMPULKAN SEMUA FILE (termasuk ekstrak .zip)
# =====================================================================
def gather_files(root):
    """Kembalikan daftar (path_xlsx, label_sumber). Ekstrak .zip ke folder temp."""
    files = []
    tmpdirs = []
    for dirpath, _dirs, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            low = fn.lower()
            if low.startswith("~$"):
                continue
            if low.endswith(".xlsx") or low.endswith(".xls"):
                files.append((full, rel))
            elif low.endswith(".zip"):
                try:
                    td = tempfile.mkdtemp(prefix="ordzip_")
                    tmpdirs.append(td)
                    with zipfile.ZipFile(full) as zf:
                        for member in zf.namelist():
                            if member.lower().endswith((".xlsx", ".xls")) and not member.startswith("__"):
                                zf.extract(member, td)
                                files.append((os.path.join(td, member), rel + " (zip)"))
                except Exception as e:
                    print(f"  ! Gagal buka zip {fn}: {e}")
    return files, tmpdirs


# =====================================================================
#  PENULISAN OUTPUT XLSX (berformat)
# =====================================================================
FONT = "Arial"
HEAD_FILL = PatternFill("solid", fgColor="1F4E78")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT, bold=True, size=14)
SUB_FONT = Font(name=FONT, italic=True, size=9, color="555555")
BASE_FONT = Font(name=FONT, size=10)
BOLD_FONT = Font(name=FONT, bold=True, size=10)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOTAL_FILL = PatternFill("solid", fgColor="D9E1F2")
IDR_FMT = "#,##0"
PCT_FMT = "0.0%"


def style_header_row(ws, row_idx, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def build_output(agg, diag, out_path, root):
    # ---------- agregasi turunan ----------
    # per model: total qty, value, set tipe cover, set sku
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

    wb = openpyxl.Workbook()

    # =============================================================
    #  SHEET 1: Top 300 Mobil
    # =============================================================
    ws1 = wb.active
    ws1.title = "Top 300 Mobil"
    ws1["A1"] = f"MOBIL TERLARIS - Top {TOP_N} Model (Detail Gen & Warna)"
    ws1["A1"].font = TITLE_FONT
    ws1["A2"] = ("Sumber: data order Shopee/TikTok/Lazada semua toko, Jan-Jun 2026. "
                 "Hanya pesanan sukses (batal/belum bayar/refund dikeluarkan). "
                 "Nilai = net setelah diskon. Lihat sheet 'Metodologi'.")
    ws1["A2"].font = SUB_FONT
    ws1.merge_cells("A2:I2")

    headers1 = ["No", "Nama Mobil", "Satuan", "Total Kuantitas", "% Kuantitas",
                "Total Penjualan (Rp)", "% Nilai", "Jenis Cover Digabung", "Jumlah Varian/SKU"]
    hrow = 4
    for j, h in enumerate(headers1, start=1):
        ws1.cell(row=hrow, column=j, value=h)
    style_header_row(ws1, hrow, len(headers1))

    r = hrow + 1
    first_data = r
    for i, model in enumerate(top_models, start=1):
        ws1.cell(row=r, column=1, value=i)
        ws1.cell(row=r, column=2, value=model)
        ws1.cell(row=r, column=3, value=SATUAN)
        ws1.cell(row=r, column=4, value=model_qty[model])
        ws1.cell(row=r, column=5, value=(model_qty[model] / grand_qty) if grand_qty else 0)
        ws1.cell(row=r, column=6, value=round(model_val[model]))
        ws1.cell(row=r, column=7, value=(model_val[model] / grand_val) if grand_val else 0)
        ws1.cell(row=r, column=8, value=", ".join(sorted(model_types[model])))
        ws1.cell(row=r, column=9, value=len(model_skus[model]))
        r += 1
    tot_row = r

    # baris total (nilai hasil hitung, bukan formula -> tampil di semua viewer)
    ws1.cell(row=tot_row, column=2, value="TOTAL (semua model, termasuk di luar Top %d)" % TOP_N)
    ws1.cell(row=tot_row, column=4, value=grand_qty)
    ws1.cell(row=tot_row, column=5, value=1.0 if grand_qty else 0)
    ws1.cell(row=tot_row, column=6, value=round(grand_val))
    ws1.cell(row=tot_row, column=7, value=1.0 if grand_val else 0)
    for c in range(1, len(headers1) + 1):
        cell = ws1.cell(row=tot_row, column=c)
        cell.font = BOLD_FONT
        cell.fill = TOTAL_FILL

    # format & border
    for rr in range(first_data, tot_row + 1):
        for cc in range(1, len(headers1) + 1):
            cell = ws1.cell(row=rr, column=cc)
            if cell.font is BASE_FONT or cell.font.name != FONT:
                cell.font = BOLD_FONT if rr == tot_row else BASE_FONT
            cell.border = BORDER
            if cc in (4,):
                cell.number_format = "#,##0"
            elif cc == 6:
                cell.number_format = IDR_FMT
            elif cc in (5, 7):
                cell.number_format = PCT_FMT
            elif cc == 9:
                cell.number_format = "#,##0"
    widths1 = [5, 26, 7, 15, 11, 20, 9, 34, 14]
    for j, w in enumerate(widths1, start=1):
        ws1.column_dimensions[get_column_letter(j)].width = w
    ws1.freeze_panes = ws1.cell(row=first_data, column=1)

    # =============================================================
    #  SHEET 2: Detail Gen & Warna  (long format)
    # =============================================================
    ws2 = wb.create_sheet("Detail Gen & Warna")
    ws2["A1"] = "Detail Penjualan per Model + Jenis Cover + Gen + Warna (Top %d model)" % TOP_N
    ws2["A1"].font = TITLE_FONT
    headers2 = ["Peringkat", "Nama Mobil", "Jenis Cover", "Gen", "Warna",
                "Kuantitas", "% dari Model", "Total Penjualan (Rp)", "Jumlah SKU"]
    hrow2 = 3
    for j, h in enumerate(headers2, start=1):
        ws2.cell(row=hrow2, column=j, value=h)
    style_header_row(ws2, hrow2, len(headers2))

    # baris detail hanya untuk model Top N, urut peringkat model lalu qty desc
    detail_rows = []
    for (model, tipe, gen, warna), rec in agg.items():
        if model in top_set:
            detail_rows.append((rank_of[model], model, tipe, gen, warna,
                                rec["qty"], rec["value"], len(rec["skus"])))
    detail_rows.sort(key=lambda x: (x[0], -x[5], -x[6]))

    r = hrow2 + 1
    for (rank, model, tipe, gen, warna, qty, val, nsku) in detail_rows:
        ws2.cell(row=r, column=1, value=rank)
        ws2.cell(row=r, column=2, value=model)
        ws2.cell(row=r, column=3, value=tipe)
        ws2.cell(row=r, column=4, value=gen)
        ws2.cell(row=r, column=5, value=warna)
        ws2.cell(row=r, column=6, value=qty)
        # % dari total model = qty baris / total qty model (nilai hasil hitung)
        ws2.cell(row=r, column=7, value=(qty / model_qty[model]) if model_qty[model] else 0)
        ws2.cell(row=r, column=8, value=round(val))
        ws2.cell(row=r, column=9, value=nsku)
        for cc in range(1, len(headers2) + 1):
            cell = ws2.cell(row=r, column=cc)
            cell.font = BASE_FONT
            cell.border = BORDER
            if cc == 6:
                cell.number_format = "#,##0"
            elif cc == 7:
                cell.number_format = PCT_FMT
            elif cc == 8:
                cell.number_format = IDR_FMT
        r += 1
    widths2 = [10, 24, 13, 16, 16, 12, 12, 20, 11]
    for j, w in enumerate(widths2, start=1):
        ws2.column_dimensions[get_column_letter(j)].width = w
    ws2.freeze_panes = ws2.cell(row=hrow2 + 1, column=1)
    ws2.auto_filter.ref = f"A{hrow2}:I{r-1}"

    # =============================================================
    #  SHEET 3: Matriks Warna (crosstab Model-Gen x Warna)
    # =============================================================
    ws3 = wb.create_sheet("Matriks Warna")
    ws3["A1"] = "Matriks Kuantitas: baris = Model + Gen, kolom = Warna (Top %d model)" % TOP_N
    ws3["A1"].font = TITLE_FONT

    # kumpulan warna sebagai kolom (urut total qty desc)
    warna_tot = defaultdict(int)
    cell_qty = defaultdict(int)          # (model, gen) x warna
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

    hrow3 = 3
    ws3.cell(row=hrow3, column=1, value="Nama Mobil")
    ws3.cell(row=hrow3, column=2, value="Gen")
    for j, w in enumerate(warna_cols, start=3):
        ws3.cell(row=hrow3, column=j, value=w)
    ws3.cell(row=hrow3, column=3 + len(warna_cols), value="Total")
    style_header_row(ws3, hrow3, 3 + len(warna_cols))

    r = hrow3 + 1
    ncol_total = 3 + len(warna_cols)
    col_totals = defaultdict(int)     # total per kolom warna + grand total
    for rk in rowkeys:
        model, gen = rk
        ws3.cell(row=r, column=1, value=model)
        ws3.cell(row=r, column=2, value=gen)
        row_total = 0
        for j, w in enumerate(warna_cols, start=3):
            q = cell_qty.get((rk, w), 0)
            ws3.cell(row=r, column=j, value=(q if q else None))
            row_total += q
            col_totals[j] += q
        # total baris = nilai hasil hitung
        ws3.cell(row=r, column=ncol_total, value=row_total)
        col_totals[ncol_total] += row_total
        for cc in range(1, ncol_total + 1):
            cell = ws3.cell(row=r, column=cc)
            cell.font = BASE_FONT
            cell.border = BORDER
            if cc >= 3:
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="center")
        r += 1
    # baris total kolom (nilai hasil hitung)
    ws3.cell(row=r, column=1, value="TOTAL")
    for j in range(3, ncol_total + 1):
        ws3.cell(row=r, column=j, value=col_totals.get(j, 0))
    for cc in range(1, ncol_total + 1):
        cell = ws3.cell(row=r, column=cc)
        cell.font = BOLD_FONT
        cell.fill = TOTAL_FILL
        cell.border = BORDER
        if cc >= 3:
            cell.number_format = "#,##0"
    ws3.column_dimensions["A"].width = 24
    ws3.column_dimensions["B"].width = 16
    for j in range(3, ncol_total + 1):
        ws3.column_dimensions[get_column_letter(j)].width = 11
    ws3.freeze_panes = ws3.cell(row=hrow3 + 1, column=3)

    # =============================================================
    #  SHEET 4: Metodologi & Diagnostik
    # =============================================================
    ws4 = wb.create_sheet("Metodologi")
    lines = [
        ("MOBIL TERLARIS - Metodologi & Diagnostik", TITLE_FONT),
        (f"Dibuat: {datetime.datetime.now():%Y-%m-%d %H:%M}", SUB_FONT),
        (f"Folder sumber: {root}", SUB_FONT),
        ("", None),
        ("DEFINISI", BOLD_FONT),
        ("- Cakupan: semua toko (Undercover/Otonation/Otopro/Smartpro) x Shopee/TikTok/Lazada.", BASE_FONT),
        ("- Periode: sesuai file di folder (Jan-Jun 2026).", BASE_FONT),
        ("- Hanya MOBIL (Cover Mobil). Motor tidak masuk ranking.", BASE_FONT),
        ("- Status dikeluarkan (bukan penjualan): " + ", ".join(STATUS_EXCLUDE) + ".", BASE_FONT),
        ("- Kuantitas = qty terjual - qty diretur.", BASE_FONT),
        ("- Total Penjualan = nilai NET setelah diskon (Shopee: Subtotal Pesanan; "
         "TikTok: SKU Subtotal After Discount; Lazada: paidPrice).", BASE_FONT),
        ("- Model digabung lintas toko/marketplace berdasarkan nama model pada listing.", BASE_FONT),
        ("- Tipe cover ditentukan dari penanda warna (Elite/Warrior->Strip, Silver->Premium, "
         "Transparan->Transparan) lalu tier di nama produk.", BASE_FONT),
        ("", None),
        ("DIAGNOSTIK (silakan cek kewajaran angka)", BOLD_FONT),
        (f"- Total baris order terbaca: {diag.get('rows_total',0):,}", BASE_FONT),
        (f"    Shopee: {diag.get('rows_shopee',0):,} | TikTok: {diag.get('rows_tiktok',0):,} | "
         f"Lazada: {diag.get('rows_lazada',0):,}", BASE_FONT),
        (f"- Baris dihitung (mobil, sukses): {diag.get('rows_counted',0):,}", BASE_FONT),
        (f"- Baris motor (dilewati): {diag.get('rows_motor',0):,}", BASE_FONT),
        (f"- Dilewati krn status batal/refund/belum bayar: {diag.get('skip_status',0):,}", BASE_FONT),
        (f"- Dilewati krn qty net <= 0 (retur penuh): {diag.get('skip_returned',0):,}", BASE_FONT),
        (f"- Dilewati krn nama model tidak terbaca: {diag.get('skip_no_model',0):,}", BASE_FONT),
        (f"- Jumlah model mobil unik: {len(model_qty):,}", BASE_FONT),
        (f"- Total kuantitas semua model: {grand_qty:,}", BASE_FONT),
        (f"- Total nilai semua model: Rp {round(grand_val):,}", BASE_FONT),
    ]
    rr = 1
    for text, font in lines:
        c = ws4.cell(row=rr, column=1, value=text)
        if font:
            c.font = font
        rr += 1
    if diag.get("_sample_no_model"):
        ws4.cell(row=rr + 1, column=1, value="Contoh nama produk yang model-nya tidak terbaca:").font = BOLD_FONT
        rr += 2
        for s in diag["_sample_no_model"]:
            ws4.cell(row=rr, column=1, value="   " + s).font = BASE_FONT
            rr += 1
    if diag.get("_errors"):
        rr += 1
        ws4.cell(row=rr, column=1, value="File gagal dibaca:").font = BOLD_FONT
        rr += 1
        for s in diag["_errors"]:
            ws4.cell(row=rr, column=1, value="   " + s).font = BASE_FONT
            rr += 1
    ws4.column_dimensions["A"].width = 110

    wb.save(out_path)
    return len(model_qty), grand_qty, grand_val


# =====================================================================
#  MAIN
# =====================================================================
def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DEFAULT
    if not os.path.isdir(root):
        print(f"ERROR: folder tidak ditemukan: {root}")
        sys.exit(1)

    print(f"Memindai folder: {os.path.abspath(root)}")
    files, tmpdirs = gather_files(root)
    print(f"Menemukan {len(files)} file order (xlsx/zip).")
    if not files:
        print("Tidak ada file order. Pastikan folder benar.")
        sys.exit(1)

    agg = defaultdict(lambda: {"qty": 0, "value": 0.0, "skus": set(), "markets": set()})
    diag = Counter()

    for i, (path, label) in enumerate(files, start=1):
        print(f"  [{i}/{len(files)}] {label} :: {os.path.basename(path)}")
        process_workbook(path, agg, diag, label)

    if not agg:
        print("Tidak ada baris penjualan mobil yang terbaca. Cek sheet Metodologi/diagnostik.")
    print("Menulis output ...")
    nmodel, gq, gv = build_output(agg, diag, out_path, os.path.abspath(root))
    print(f"SELESAI. Model unik: {nmodel}, total qty: {gq:,}, total nilai: Rp {round(gv):,}")
    print(f"File output: {os.path.abspath(out_path)}")

    # bersihkan temp zip
    import shutil
    for td in tmpdirs:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    main()
