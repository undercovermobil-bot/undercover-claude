#!/usr/bin/env python3
"""Bangun file impor "SKU Gudang" Big Seller: SKU yang dipakai listing tapi
belum ada di gudang Big Seller.

Alur:
  1. baca ekspor gudang Big Seller  -> himpunan SKU yang SUDAH ada (+ stoknya)
  2. baca file listing e-commerce   -> semua SKU yang DIPAKAI listing
  3. selisihkan, konsolidasi toko (OT->UA, OP->SP), buang yang tidak layak
  4. tulis ke SALINAN template impor (format template dipertahankan apa adanya)

Jalankan `--probe` dulu untuk memastikan tiap file kebaca benar sebelum menulis
apa pun. Skrip ini tidak pernah menimpa file sumber.

Contoh:
    python build_sku_gudang_import.py --probe \
        --gudang "SKU Gudang Big Seller/SKU_Gudang*.xlsx" \
        --listing "SKU Gudang Big Seller/??_*.xlsx"

    python build_sku_gudang_import.py \
        --gudang "SKU Gudang Big Seller/SKU_Gudang*.xlsx" \
        --listing "SKU Gudang Big Seller/??_*.xlsx" \
        --master "SKU, Price, Tracking Cover Mobil.xlsx" \
        --template "impor_untuk_membuat_sku_gudang_in.xlsx" \
        --out "Impor SKU Gudang Baru.xlsx"
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import sys
import zipfile
from collections import defaultdict

import openpyxl

# Aturan konsolidasi #1/#3: stok fisik OT=UA dan OP=SP, SKU gudang hanya UA & SP.
TARGET_STORE = {"UA": "UA", "OT": "UA", "SP": "SP", "OP": "SP"}

# Sufiks keunikan Lazada (…-ABU_G3, …-HTM_MERA) bukan bagian identitas barang.
LAZADA_SUFFIX = re.compile(r"_[A-Z0-9]{1,4}$")

# SKU legacy / placeholder yang tidak boleh dibuatkan SKU gudang.
LEGACY_PREFIX = re.compile(r"^(CVR|CM)\d*", re.I)
PLACEHOLDER = {"SKU", "SKu", "sku", "-", "0"}


# --------------------------------------------------------------------------- #
# Pembacaan file
# --------------------------------------------------------------------------- #
def load_workbook_safe(path: str):
    """Buka workbook dengan menambal dua bug ekspor yang sudah dikenal.

    - Ekspor Shopee menulis activePane="bottom_left" yang invalid -> ValueError.
    - Ekspor SKU_Gudang/SKU_Match menyimpan dimension palsu A1:A1, sehingga
      read_only=True berhenti di baris 1 dan mengembalikan 0 baris TANPA error.
      Karena itu semua file dibuka dengan read_only=False.
    """
    try:
        return openpyxl.load_workbook(path, data_only=True)
    except ValueError as exc:
        if "activePane" not in str(exc):
            raise
    patched = path + ".patched.xlsx"
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(patched, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                data = data.replace(b'activePane="bottom_left"', b'activePane="topLeft"')
            dst.writestr(item, data)
    return openpyxl.load_workbook(patched, data_only=True)


def find_header_row(ws, wanted, max_scan=10):
    """Cari baris header + peta {nama_kolom_lower: index_1_based}.

    Header tidak pernah di baris yang sama antar channel (Shopee 3, TikTok 1,
    Lazada 4) dan posisi kolom bergeser antar ekspor, jadi selalu dideteksi —
    jangan pernah hardcode indeks kolom.
    """
    for row in range(1, max_scan + 1):
        cells = {}
        for col in range(1, ws.max_column + 1):
            val = ws.cell(row=row, column=col).value
            if isinstance(val, str) and val.strip():
                cells[val.strip().lower()] = col
        if any(w in cells for w in wanted):
            return row, cells
    return None, {}


def pick(cells, *candidates):
    """Ambil indeks kolom pertama yang cocok, exact dulu baru substring."""
    for cand in candidates:
        if cand in cells:
            return cells[cand]
    for cand in candidates:
        for name, idx in cells.items():
            if cand in name:
                return idx
    return None


def read_gudang(paths):
    """Ekspor gudang Big Seller -> {sku: stok}."""
    stock = {}
    for path in paths:
        wb = load_workbook_safe(path)
        ws = wb.worksheets[0]
        hrow, cells = find_header_row(ws, ["nomor sku", "nomor sku gudang", "sku"])
        if hrow is None:
            print(f"  !! header tidak ketemu: {os.path.basename(path)}", file=sys.stderr)
            continue
        c_sku = pick(cells, "nomor sku gudang", "nomor sku", "sku")
        c_stok = pick(cells, "stok", "stock", "kuantitas")
        found = 0
        for row in range(hrow + 1, ws.max_row + 1):
            sku = ws.cell(row=row, column=c_sku).value
            if not isinstance(sku, str) or not sku.strip():
                continue
            sku = sku.strip()
            qty = ws.cell(row=row, column=c_stok).value if c_stok else None
            qty = qty if isinstance(qty, (int, float)) else 0
            stock[sku] = max(stock.get(sku, 0), int(qty))
            found += 1
        print(f"  gudang  {os.path.basename(path)}: {found} SKU")
    return stock


def detect_channel(ws, cells):
    if "seller_sku" in cells or "sku penjual" in cells:
        return "TikTok"
    if any("sku.skuid" in n for n in cells) or "seller sku" in cells:
        return "Lazada"
    return "Shopee"


def read_listing(paths):
    """File listing e-commerce -> daftar dict baris varian."""
    rows = []
    for path in paths:
        base = os.path.basename(path)
        wb = load_workbook_safe(path)
        for ws in wb.worksheets:
            if ws.max_row < 2:
                continue
            hrow, cells = find_header_row(
                ws, ["seller_sku", "sku penjual", "seller sku", "sku", "kode variasi"]
            )
            if hrow is None:
                continue
            channel = detect_channel(ws, cells)
            c_sku = pick(cells, "seller_sku", "sku penjual", "seller sku", "sku")
            c_name = pick(cells, "product_name", "nama produk", "name")
            c_var = pick(cells, "variation_value", "nilai variasi", "nama variasi", "variation")
            c_pid = pick(cells, "product_id", "id produk", "kode produk", "sku.skuid")
            if c_sku is None:
                continue
            count = 0
            for row in range(hrow + 1, ws.max_row + 1):
                sku = ws.cell(row=row, column=c_sku).value
                if not isinstance(sku, str) or not sku.strip():
                    continue
                rows.append(
                    {
                        "file": base,
                        "sheet": ws.title,
                        "channel": channel,
                        "row": row,
                        "sku_raw": sku.strip(),
                        "product": (ws.cell(row=row, column=c_name).value if c_name else None),
                        "variant": (ws.cell(row=row, column=c_var).value if c_var else None),
                        "pid": (ws.cell(row=row, column=c_pid).value if c_pid else None),
                    }
                )
                count += 1
            if count:
                print(f"  listing {base} [{ws.title}/{channel}]: {count} baris ber-SKU")
            break  # sheet data pertama saja; sheet lain = Instruction/Hidden*
    return rows


def read_master(path):
    """Master -> {sku: (model, toko, kategori, warna, generasi)} untuk judul."""
    wb = load_workbook_safe(path)
    index = {}
    for ws in wb.worksheets:
        hrow, cells = find_header_row(ws, ["sku", "nama produk"])
        if hrow is None:
            continue
        c = {
            k: pick(cells, k)
            for k in ("sku", "nama produk", "toko", "kategori", "warna", "generasi")
        }
        if not c["sku"]:
            continue
        for row in range(hrow + 1, ws.max_row + 1):
            sku = ws.cell(row=row, column=c["sku"]).value
            if not isinstance(sku, str) or not sku.strip():
                continue
            index.setdefault(
                sku.strip(),
                tuple(
                    (ws.cell(row=row, column=c[k]).value if c[k] else None)
                    for k in ("nama produk", "toko", "kategori", "warna", "generasi")
                ),
            )
    print(f"  master  {os.path.basename(path)}: {len(index)} SKU terindeks")
    return index


# --------------------------------------------------------------------------- #
# Normalisasi & seleksi
# --------------------------------------------------------------------------- #
def canon_sku(raw: str):
    """SKU listing -> bentuk kanonik SKU gudang, atau None kalau tidak layak.

    Mengembalikan (sku_kanonik, alasan_ditolak). Hanya SKU berformat 6 segmen
    MEREK-MODEL-TOKO-KAT-GEN-WARNA yang layak dibuatkan SKU gudang.
    """
    sku = raw.strip()
    if not sku or sku in PLACEHOLDER:
        return None, "placeholder/kosong"
    if sku.isdigit():
        return None, "placeholder angka (auto Lazada)"
    if LEGACY_PREFIX.match(sku):
        return None, "format legacy CVR/CM"
    base = LAZADA_SUFFIX.sub("", sku)
    parts = base.split("-")
    if len(parts) != 6:
        return None, f"bukan 6 segmen ({len(parts)})"
    store = parts[2].upper()
    if store not in TARGET_STORE:
        return None, f"segmen toko tak dikenal ({store})"
    parts[2] = TARGET_STORE[store]  # konsolidasi OT->UA, OP->SP
    return "-".join(parts), None


def build_title(sku, master_index, fallback_product=None):
    """Judul SKU gudang: Model-Toko-Kategori-Warna-Gen (motor: …-Motor).

    Nama model bisa memuat tanda hubung (Nissan X-Trail), jadi judul TIDAK
    boleh dibongkar ulang dengan split('-'). Di sini judul hanya dirakit.
    """
    meta = master_index.get(sku)
    if meta:
        model, toko, kat, warna, gen = meta
        gen = gen or ("Motor" if "-MTR-" in sku else "")
        parts = [str(p).strip() for p in (model, toko, kat, warna, gen) if p]
        return "-".join(parts), "master"
    if fallback_product:
        return f"{str(fallback_product).strip()} [{sku}]", "listing (perlu dicek)"
    return sku, "SKU saja (perlu dicek)"


def inherit_stock(sku, gudang_stock):
    """Stok SKU baru = nilai TERTINGGI dari SKU pendahulu, kalau tidak ada -> 5.

    Pendahulu = SKU gudang dengan (merek, model, toko, kategori, warna) sama
    tapi segmen generasi berbeda — kasus peleburan generasi. MAX, bukan JUMLAH:
    80,5% SKU gudang berstok default 5, jadi menjumlahkan menggelembungkan stok
    barang yang secara fisik sama.
    """
    parts = sku.split("-")
    if len(parts) != 6:
        return 5, None
    prefix = tuple(parts[:4])
    best, src = 0, None
    for other, qty in gudang_stock.items():
        op = other.split("-")
        if len(op) == 6 and tuple(op[:4]) == prefix and op[5] == parts[5] and op[4] != parts[4]:
            if qty > best:
                best, src = qty, other
    return (best, src) if src else (5, None)


# --------------------------------------------------------------------------- #
# Penulisan
# --------------------------------------------------------------------------- #
def write_import(template, out_path, records):
    """Tulis ke SALINAN template — jangan pernah bikin workbook baru.

    Kolom yang benar-benar dipakai cuma 4: *Nomor SKU (1), *Judul (2),
    Gudang (5), Stok (6). Baris contoh bawaan template (Masa Berlaku/Satuan
    Tambahan) adalah ILUSTRASI, bukan default — dihapus, jangan ikut disalin.
    """
    shutil.copyfile(template, out_path)
    wb = openpyxl.load_workbook(out_path)
    ws = wb["SKU"] if "SKU" in wb.sheetnames else wb.worksheets[0]
    if ws.max_row >= 2:
        ws.delete_rows(2, ws.max_row - 1)
    for offset, rec in enumerate(records):
        row = 2 + offset
        ws.cell(row=row, column=1).value = rec["sku"]
        ws.cell(row=row, column=2).value = rec["judul"]
        ws.cell(row=row, column=5).value = "Default Warehouse"
        ws.cell(row=row, column=6).value = rec["stok"]
    wb.save(out_path)
    return out_path


def write_report(out_path, records, rejected):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SKU BARU"
    ws.append(["Nomor SKU", "Judul", "Sumber Judul", "Stok", "Diwarisi dari", "Contoh listing"])
    for rec in records:
        ws.append(
            [rec["sku"], rec["judul"], rec["judul_src"], rec["stok"], rec["stok_src"] or "", rec["contoh"]]
        )
    ws2 = wb.create_sheet("DILEWATI")
    ws2.append(["SKU listing", "Alasan", "Jumlah baris", "Contoh produk"])
    for (raw, reason), info in sorted(rejected.items(), key=lambda kv: -kv[1]["n"]):
        ws2.append([raw, reason, info["n"], info["contoh"]])
    wb.save(out_path)
    return out_path


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gudang", required=True, help="glob ekspor SKU_Gudang Big Seller")
    ap.add_argument("--listing", required=True, help="glob file listing e-commerce")
    ap.add_argument("--master", help="master SKU, Price, Tracking (untuk judul)")
    ap.add_argument("--template", help="template impor Big Seller")
    ap.add_argument("--out", default="Impor SKU Gudang Baru.xlsx")
    ap.add_argument("--report", default="Laporan SKU Gudang Baru.xlsx")
    ap.add_argument("--probe", action="store_true", help="hanya laporkan pembacaan, tidak menulis")
    args = ap.parse_args()

    gudang_files = sorted(glob.glob(args.gudang))
    listing_files = sorted(glob.glob(args.listing))
    if not gudang_files:
        sys.exit(f"tidak ada file gudang cocok: {args.gudang}")
    if not listing_files:
        sys.exit(f"tidak ada file listing cocok: {args.listing}")

    print(f"[1/4] baca {len(gudang_files)} file gudang")
    gudang_stock = read_gudang(gudang_files)
    print(f"      total {len(gudang_stock)} SKU gudang\n")

    print(f"[2/4] baca {len(listing_files)} file listing")
    listing_rows = read_listing(listing_files)
    print(f"      total {len(listing_rows)} baris ber-SKU\n")

    master_index = {}
    if args.master:
        print("[3/4] baca master")
        master_index = read_master(args.master)
        print()

    print("[4/4] selisihkan")
    needed, dipakai, rejected = {}, set(), defaultdict(lambda: {"n": 0, "contoh": ""})
    for row in listing_rows:
        sku, reason = canon_sku(row["sku_raw"])
        if reason:
            key = (row["sku_raw"], reason)
            rejected[key]["n"] += 1
            rejected[key]["contoh"] = rejected[key]["contoh"] or (row["product"] or "")
            continue
        dipakai.add(sku)
        if sku in gudang_stock:
            continue
        needed.setdefault(sku, row)

    records = []
    for sku, row in sorted(needed.items()):
        judul, judul_src = build_title(sku, master_index, row["product"])
        stok, stok_src = inherit_stock(sku, gudang_stock)
        records.append(
            {
                "sku": sku,
                "judul": judul,
                "judul_src": judul_src,
                "stok": stok,
                "stok_src": stok_src,
                "contoh": f"{row['file']} baris {row['row']} — {row['product'] or ''}",
            }
        )

    warisan = sum(1 for r in records if r["stok_src"])
    tanpa_master = sum(1 for r in records if r["judul_src"] != "master")
    print(f"      SKU gudang sudah ada : {len(gudang_stock)}")
    print(f"      SKU layak di listing : {len(dipakai)}")
    print(f"      PERLU DIBUAT         : {len(records)}")
    print(f"        - mewarisi stok    : {warisan} (sisanya default 5)")
    print(f"        - judul non-master : {tanpa_master} (perlu dicek manual)")
    print(f"      baris dilewati       : {sum(v['n'] for v in rejected.values())}")

    if args.probe:
        print("\n(--probe: tidak ada file ditulis)")
        return
    if not args.template:
        sys.exit("--template wajib diisi kalau bukan --probe")
    print(f"\nditulis: {write_import(args.template, args.out, records)}")
    print(f"ditulis: {write_report(args.report, records, rejected)}")


if __name__ == "__main__":
    main()
