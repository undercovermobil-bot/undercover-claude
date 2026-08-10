#!/usr/bin/env python3
"""Satukan SKU Xenia & Veloz ke SKU Avanza — Shopee, Lazada, dan TikTok.

Aturan user 2026-08-08:
  - Avanza/Xenia/Veloz mobil kembar -> satu set SKU, memakai kode Avanza.
  - Avanza punya 2 formula: Gen 1-2 (2003-2020)=G1, Gen 3 (2021-2026)=G3.

Pemetaan generasi lewat RENTANG TAHUN varian, bukan nomor "Gen N" — penomoran
ketiga listing tidak sejajar (Avanza "Gen 1-2" = Xenia "Gen 1"+"Gen 2" = Veloz
"Gen 1"; Avanza "Gen 3" = Xenia "Gen 3" = Veloz "Gen 2").

Tiga channel, tiga aturan berbeda — jangan disamaratakan:
  Shopee  boleh mengirim baris berubah saja; SKU kembar dalam 1 listing boleh.
  Lazada  boleh mengirim baris berubah saja; TAPI Seller SKU wajib UNIK per
          listing, jadi peleburan generasi butuh sufiks `_G{gen asli}`.
  TikTok  WAJIB mengirim SELURUH SKU tiap produk terdampak — SKU yang tidak
          ikut dianggap permintaan hapus dan ditolak (`sku not allow delete`).

Pakai --probe dulu untuk memastikan tiap file kebaca benar sebelum menulis.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import tempfile
import zipfile
from collections import defaultdict
from copy import copy

import openpyxl

AVANZA_MODEL = "TYT-AVZ"
AVANZA_FORMULA = [((2003, 2020), "G1"), ((2021, 2026), "G3")]
MODELS = {"toyota avanza": "Avanza", "daihatsu xenia": "Xenia", "toyota veloz": "Veloz"}

# Sufiks keunikan Lazada: _G3, _MERA — bukan bagian identitas barang.
LAZADA_SUFFIX = re.compile(r"_[A-Z0-9]{1,4}$")

# Kolom per channel dicari lewat NAMA di baris header, tidak pernah di-hardcode:
# posisi kolom TikTok terbukti bergeser antar ekspor (seller_sku pernah pindah
# dari kolom 11 ke 10 saat header `quantity` hilang).
SPEC = {
    "shopee": {
        "sheet": None,
        "data_start": 7,
        "cols": {
            "pid": ["kode produk"],
            "varid": ["kode variasi"],
            "nama": ["nama produk"],
            "varian": ["nama variasi"],
            "sku": ["sku"],
        },
    },
    "lazada": {
        "sheet": "template",
        "data_start": 5,
        "cols": {
            "pid": ["product_id", "productid", "item id", "itemid"],
            "varid": ["sku.skuid", "skuid"],
            "nama": ["product_name", "nama produk", "name"],
            "varian": ["sku.variation", "variation", "nama variasi"],
            "sku": ["seller sku", "sellersku", "seller_sku"],
        },
    },
    "tiktok": {
        "sheet": "Template",
        "data_start": 6,
        "cols": {
            "pid": ["product_id"],
            "varid": ["sku_id"],
            "nama": ["product_name"],
            "varian": ["variation_value"],
            "sku": ["seller_sku"],
        },
    },
}


# --------------------------------------------------------------------------- #
def load_workbook_safe(path):
    """Muat workbook, tambal bug activePane ekspor Shopee bila perlu.

    openpyxl membungkus penyebab aslinya di ValueError generik, jadi jangan
    cocokkan teks pesannya — langsung coba tambal lalu muat ulang. Hasil
    tambalan ditulis ke direktori sementara supaya folder sumber tidak kotor.
    """
    try:
        return openpyxl.load_workbook(path)
    except ValueError:
        pass
    patched = os.path.join(tempfile.mkdtemp(prefix="xlsxfix-"), os.path.basename(path))
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(patched, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                data = data.replace(b'activePane="bottom_left"', b'activePane="topLeft"')
            dst.writestr(item, data)
    return openpyxl.load_workbook(patched)


def detect_channel(wb):
    names = {n.lower() for n in wb.sheetnames}
    if "template" in names and len(wb.sheetnames) >= 6:
        return "tiktok"
    if "template" in names:
        return "lazada"
    return "shopee"


def resolve_cols(ws, spec):
    """Cari baris header + peta peran->indeks kolom."""
    for row in range(1, spec["data_start"]):
        present = {}
        for col in range(1, ws.max_column + 1):
            val = ws.cell(row=row, column=col).value
            if isinstance(val, str) and val.strip():
                present[val.strip().lower()] = col
        got = {}
        for role, cands in spec["cols"].items():
            for cand in cands:
                if cand in present:
                    got[role] = present[cand]
                    break
        if "sku" in got and "varid" in got:
            return row, got
    raise SystemExit(f"header tidak dikenali di sheet {ws.title!r} — cek SPEC")


def pick_sheet(wb, spec):
    if spec["sheet"] is None:
        return wb.worksheets[0]
    for ws in wb.worksheets:
        if ws.title.lower() == spec["sheet"].lower():
            return ws
    return wb.worksheets[0]


def read_rows(path):
    wb = load_workbook_safe(path)
    channel = detect_channel(wb)
    spec = SPEC[channel]
    ws = pick_sheet(wb, spec)
    hrow, cols = resolve_cols(ws, spec)
    rows = []
    for r in range(spec["data_start"], ws.max_row + 1):
        get = lambda role: (ws.cell(row=r, column=cols[role]).value if role in cols else None)
        if get("varid") in (None, ""):
            continue
        rows.append(
            {
                "file": os.path.basename(path),
                "path": path,
                "channel": channel,
                "row": r,
                "pid": str(get("pid") or ""),
                "varid": str(get("varid")),
                "nama": get("nama") or "",
                "varian": get("varian") or "",
                "sku": get("sku"),
            }
        )
    return channel, ws, cols, spec, rows


# --------------------------------------------------------------------------- #
def model_of(nama):
    low = (nama or "").lower()
    for key, label in MODELS.items():
        if key in low:
            return label
    return None


def year_range(text):
    m = re.findall(r"(\d{4})\s*-\s*(\d{4})", text or "")
    return (int(m[0][0]), int(m[0][1])) if m else None


def gen_number(text):
    """Nomor generasi asli baris ini — dipakai sebagai sufiks keunikan Lazada."""
    m = re.search(r"gen\s*(\d+)", (text or ""), re.I)
    return m.group(1) if m else None


def avanza_gen_code(varian):
    yr = year_range(varian)
    if not yr:
        return None, "varian tanpa rentang tahun"
    start, end = yr
    for (lo, hi), code in AVANZA_FORMULA:
        if start >= lo and end <= hi:
            return code, None
    return None, f"rentang {start}-{end} di luar formula Avanza"


def base_sku(sku):
    return LAZADA_SUFFIX.sub("", str(sku or ""))


def plan_changes(rows):
    """Hitung SKU tujuan untuk baris Xenia & Veloz. Avanza tidak disentuh."""
    for r in rows:
        r["model"] = model_of(r["nama"])
    target = [r for r in rows if r["model"]]
    valid = {base_sku(r["sku"]) for r in target if r["model"] == "Avanza" and r["sku"]}

    changes, problems = [], []
    for r in target:
        if r["model"] == "Avanza":
            continue
        parts = base_sku(r["sku"]).split("-")
        if len(parts) != 6:
            problems.append((r, f"SKU sekarang bukan 6 segmen: {r['sku']!r}"))
            continue
        gen, err = avanza_gen_code(r["varian"])
        if err:
            problems.append((r, err))
            continue
        new = "-".join([AVANZA_MODEL, parts[2], parts[3], gen, parts[5]])
        if new not in valid:
            problems.append((r, f"SKU tujuan {new} tidak ada di daftar SKU Avanza"))
            continue
        r["baru"] = new
        if new != str(r["sku"] or ""):
            changes.append(r)
    return target, valid, changes, problems


def apply_lazada_uniqueness(changes, all_rows):
    """Lazada menolak Seller SKU kembar DALAM SATU listing.

    Peleburan generasi membuat beberapa baris jatuh ke SKU dasar yang sama
    (mis. Xenia Gen 1 & Gen 2 -> ...-G1-ABU). Konvensi UA: anggota generasi
    TERENDAH memakai kode polos, sisanya disufiks `_G{nomor gen asli}`.
    """
    by_listing = defaultdict(list)
    for r in changes:
        by_listing[r["pid"]].append(r)

    # SKU yang sudah dipakai baris lain di listing yang sama dan tidak diubah
    taken = defaultdict(set)
    ubah = {(r["pid"], r["varid"]) for r in changes}
    for r in all_rows:
        if (r["pid"], r["varid"]) not in ubah and r["sku"]:
            taken[r["pid"]].add(str(r["sku"]))

    for pid, rows in by_listing.items():
        groups = defaultdict(list)
        for r in rows:
            groups[r["baru"]].append(r)
        for base, members in groups.items():
            members.sort(key=lambda r: (int(gen_number(r["varian"]) or 99), r["varid"]))
            for i, r in enumerate(members):
                if i == 0 and base not in taken[pid]:
                    final = base
                else:
                    gn = gen_number(r["varian"])
                    final = f"{base}_G{gn}" if gn else f"{base}_{i + 1}"
                    n = 2
                    while final in taken[pid]:
                        final = f"{base}_{gn or ''}{n}"
                        n += 1
                r["baru"] = final
                taken[pid].add(final)


def expand_tiktok_products(changes, all_rows):
    """TikTok memperlakukan baris yang diunggah sebagai daftar SKU LENGKAP
    produk itu; SKU yang tidak ikut dianggap dihapus. Jadi setiap produk yang
    tersentuh harus dikirim utuh, termasuk baris yang tidak berubah."""
    pids = {r["pid"] for r in changes}
    baru = {(r["pid"], r["varid"]): r["baru"] for r in changes}
    out = []
    for r in all_rows:
        if r["pid"] in pids:
            r["baru"] = baru.get((r["pid"], r["varid"]), str(r["sku"] or ""))
            out.append(r)
    return out


# --------------------------------------------------------------------------- #
def write_upload(src_path, out_path, kirim):
    """Bangun file upload dari file ASLI — semua sheet, kolom, blok header,
    freeze pane, dan style per sel ikut terbawa. Jangan pernah membuat
    workbook baru (user menolak itu dua kali: 08-03 dan 08-07)."""
    wb = load_workbook_safe(src_path)
    channel = detect_channel(wb)
    spec = SPEC[channel]
    ws = pick_sheet(wb, spec)
    _, cols = resolve_cols(ws, spec)
    c_sku = cols["sku"]
    start = spec["data_start"]

    keep = {r["row"]: r["baru"] for r in kirim}
    snap = []
    for r in sorted(keep):
        snap.append(
            (
                [
                    (ws.cell(row=r, column=c).value, copy(ws.cell(row=r, column=c)._style),
                     ws.cell(row=r, column=c).number_format)
                    for c in range(1, ws.max_column + 1)
                ],
                keep[r],
            )
        )

    if ws.max_row >= start:
        ws.delete_rows(start, ws.max_row - start + 1)
    for i, (cells, sku) in enumerate(snap):
        row = start + i
        for c, (val, style, numfmt) in enumerate(cells, start=1):
            cell = ws.cell(row=row, column=c)
            cell.value = sku if c == c_sku else val
            cell._style = style
            cell.number_format = numfmt

    if channel == "tiktok":
        # 180rb+ aturan dataValidation per-baris jadi basi setelah delete_rows
        # dan bikin Excel minta "repair". Validasi asli TikTok terjadi di server.
        ws.data_validations.dataValidation = []
    # Lazada: JANGAN dikosongkan — cuma 6 aturan, cakupannya se-kolom, dan
    # validasi kolom Seller SKU (COUNTIF=1) justru berguna sebagai cek mandiri.

    wb.save(out_path)
    return channel


def write_report(kirim, changes, out_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PERUBAHAN"
    ws.append(["Model", "Channel", "Kode Produk", "Kode Variasi", "Varian",
               "SKU lama", "SKU baru", "Berubah?", "File", "Baris"])
    ubah = {(r["pid"], r["varid"]) for r in changes}
    for r in kirim:
        ws.append([r.get("model") or "", r["channel"], r["pid"], r["varid"], r["varian"],
                   str(r["sku"] or ""), r["baru"],
                   "ya" if (r["pid"], r["varid"]) in ubah else "tidak (ikut demi produk utuh)",
                   r["file"], r["row"]])
    for col, w in zip("ABCDEFGHIJ", (10, 9, 16, 16, 32, 24, 26, 28, 12, 7)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    wb.save(out_path)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing", required=True, help="glob file ekspor 1 channel")
    ap.add_argument("--out", help="nama file upload (default otomatis)")
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.listing))
    if not paths:
        sys.exit(f"tidak ada file cocok: {args.listing}")

    all_rows, channel = [], None
    for p in paths:
        ch, _, _, _, rows = read_rows(p)
        channel = channel or ch
        if ch != channel:
            sys.exit(f"campur channel dalam satu run: {channel} vs {ch} — jalankan terpisah")
        print(f"  {os.path.basename(p)} [{ch}]: {len(rows)} baris varian")
        all_rows += rows

    target, valid, changes, problems = plan_changes(all_rows)
    if not valid:
        # Tanpa acuan Avanza, setiap SKU tujuan lolos tanpa diuji — kegagalan
        # senyap. Listing Avanza bisa berada di file lain (Shopee UA: Xenia &
        # Veloz di 2.xlsx, Avanza di 4.xlsx), jadi sertakan SEMUA file channel.
        sys.exit("listing Avanza tidak ada di file yang diberikan — "
                 "sertakan semua file channel ini supaya SKU tujuan bisa divalidasi")
    print(f"\nchannel                 : {channel}")
    print(f"baris Avanza/Xenia/Veloz: {len(target)}")
    print(f"SKU sah Avanza (acuan)  : {len(valid)}")
    print(f"baris berubah           : {len(changes)}")
    print(f"baris bermasalah        : {len(problems)}")
    for r, why in problems[:10]:
        print(f"   !! {r.get('model')} r{r['row']} {r['varian'][:30]!r}: {why}")

    if channel == "lazada":
        apply_lazada_uniqueness(changes, all_rows)
        kirim = changes
    elif channel == "tiktok":
        kirim = expand_tiktok_products(changes, all_rows)
        print(f"baris dikirim (produk utuh): {len(kirim)}")
    else:
        kirim = changes

    per = defaultdict(int)
    for r in changes:
        per[(r["model"], r["nama"].split()[-1])] += 1
    for k in sorted(per):
        print(f"   {k[0]:7} {k[1]:12}: {per[k]} baris")

    if channel == "lazada":
        dup = defaultdict(list)
        for r in kirim:
            dup[(r["pid"], r["baru"])].append(r["varid"])
        bentrok = {k: v for k, v in dup.items() if len(v) > 1}
        print(f"duplikat Seller SKU per listing: {len(bentrok)} (harus 0)")
        if bentrok:
            sys.exit("masih ada duplikat — Lazada akan menolak, perbaiki dulu")

    if args.probe:
        print("\n(--probe: tidak ada file ditulis)")
        return

    files = {r["path"] for r in kirim}
    if len(files) != 1:
        sys.exit(f"baris tersebar di >1 file sumber: {sorted(os.path.basename(f) for f in files)}")
    src = files.pop()
    out = args.out or f"Upload {channel.title()} UA - Xenia & Veloz ikut SKU Avanza.xlsx"
    write_upload(src, out, kirim)
    write_report(kirim, changes, out.replace(".xlsx", " - REKAP.xlsx"))
    print(f"\nditulis: {out}")
    print(f"ditulis: {out.replace('.xlsx', ' - REKAP.xlsx')}")


if __name__ == "__main__":
    main()
