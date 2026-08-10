#!/usr/bin/env python3
"""Satukan SKU Xenia & Veloz ke SKU Avanza (Shopee UA).

Aturan user 2026-08-08:
  - Avanza punya 2 formula: Gen 1-2 (2003-2020)=G1, Gen 3 (2021-2026)=G3
  - Xenia ikut Avanza: Gen 1 & Gen 2 -> G1, Gen 3 -> G3
  - Veloz ikut Avanza: yang 2021-2026 -> G3 (setara Avanza Gen 3)

Pemetaan generasi dilakukan lewat RENTANG TAHUN varian, bukan nomor "Gen N" —
nomor gen ketiga model itu tidak sejajar (Avanza "Gen 1-2" = Xenia "Gen 1"+"Gen 2"
= Veloz "Gen 1"), jadi mencocokkan nomor akan salah.
"""
import glob
import re
import sys
from collections import defaultdict
from copy import copy

import openpyxl

sys.path.insert(0, "/home/user/undercover-claude/sku-sync-scripts")
from build_sku_gudang_import import load_workbook_safe  # noqa: E402

UPLOAD_DIR = "/root/.claude/uploads/66ce009a-e106-5952-b6fa-f52453a26c1b"
DATA_START = 7  # baris 1-6 = blok header sales_info Shopee
C_PID, C_NAMA, C_VARID, C_VARIAN, C_INDUK, C_SKU = 1, 2, 3, 4, 5, 6

AVANZA_MODEL = "TYT-AVZ"
# Formula Avanza: (tahun_awal, tahun_akhir) -> kode segmen generasi
AVANZA_FORMULA = [((2003, 2020), "G1"), ((2021, 2026), "G3")]

MODELS = {"toyota avanza": "Avanza", "daihatsu xenia": "Xenia", "toyota veloz": "Veloz"}


def model_of(nama):
    low = (nama or "").lower()
    for key, label in MODELS.items():
        if f"cover mobil {key}" in low:
            return label
    return None


def year_range(varian):
    m = re.findall(r"(\d{4})\s*-\s*(\d{4})", varian or "")
    return (int(m[0][0]), int(m[0][1])) if m else None


def avanza_gen_code(varian):
    """Kode generasi Avanza untuk rentang tahun varian ini."""
    yr = year_range(varian)
    if not yr:
        return None, "varian tanpa rentang tahun"
    start, end = yr
    for (lo, hi), code in AVANZA_FORMULA:
        if start >= lo and end <= hi:
            return code, None
    return None, f"rentang {start}-{end} tidak masuk formula Avanza mana pun"


def load_rows(path, fname):
    ws = load_workbook_safe(path).worksheets[0]
    out = []
    for r in range(DATA_START, ws.max_row + 1):
        pid = ws.cell(row=r, column=C_PID).value
        if pid in (None, ""):
            continue
        out.append(
            {
                "file": fname,
                "row": r,
                "pid": str(pid),
                "nama": ws.cell(row=r, column=C_NAMA).value or "",
                "varid": str(ws.cell(row=r, column=C_VARID).value or ""),
                "varian": ws.cell(row=r, column=C_VARIAN).value or "",
                "sku": ws.cell(row=r, column=C_SKU).value,
            }
        )
    return out


def main():
    paths = sorted(
        glob.glob(f"{UPLOAD_DIR}/*-[1-5].xlsx"),
        key=lambda p: int(re.search(r"-(\d)\.xlsx$", p).group(1)),
    )
    all_rows, src_by_file = [], {}
    for p in paths:
        fname = re.search(r"-(\d)\.xlsx$", p).group(1) + ".xlsx"
        src_by_file[fname] = p
        all_rows += load_rows(p, fname)

    target = [r for r in all_rows if model_of(r["nama"])]
    for r in target:
        r["model"] = model_of(r["nama"])

    # Himpunan SKU sah Avanza — setiap SKU tujuan wajib ada di sini.
    avanza_valid = {str(r["sku"]) for r in target if r["model"] == "Avanza" and r["sku"]}

    changes, problems = [], []
    for r in target:
        if r["model"] == "Avanza":
            continue  # Avanza sendiri tidak disentuh
        cur = str(r["sku"] or "")
        parts = cur.split("-")
        if len(parts) != 6:
            problems.append((r, f"SKU sekarang bukan 6 segmen: {cur!r}"))
            continue
        gen, err = avanza_gen_code(r["varian"])
        if err:
            problems.append((r, err))
            continue
        new = "-".join([AVANZA_MODEL] + [parts[2], parts[3], gen, parts[5]])
        if new not in avanza_valid:
            problems.append((r, f"SKU tujuan {new} tidak ada di daftar SKU Avanza"))
            continue
        if new != cur:
            r["baru"] = new
            changes.append(r)

    print(f"baris Avanza/Xenia/Veloz   : {len(target)}")
    print(f"SKU sah Avanza (acuan)     : {len(avanza_valid)}")
    print(f"baris berubah              : {len(changes)}")
    print(f"baris bermasalah           : {len(problems)}")
    for r, why in problems[:10]:
        print(f"   !! {r['model']} r{r['row']} {r['varian'][:32]!r}: {why}")

    per = defaultdict(int)
    for r in changes:
        per[(r["model"], r["nama"].split()[-1])] += 1
    for k in sorted(per):
        print(f"   {k[0]:7} {k[1]:10}: {per[k]} baris")

    files = {r["file"] for r in changes}
    if len(files) != 1:
        sys.exit(f"baris berubah tersebar di >1 file: {files} — perlu 1 file upload per file sumber")
    src_file = files.pop()

    out = f"Upload Shopee UA - Xenia & Veloz ikut SKU Avanza (2026-08-08).xlsx"
    write_upload(src_by_file[src_file], out, changes)
    print(f"\nditulis: {out}")
    write_report(changes, "Rekap Xenia-Veloz ikut Avanza (2026-08-08).xlsx")
    print("ditulis: Rekap Xenia-Veloz ikut Avanza (2026-08-08).xlsx")


def write_upload(src_path, out_path, changes):
    """Bangun file upload dari file ASLI — pertahankan 15 kolom, blok header
    baris 1-6, freeze pane, dan style tiap sel. Jangan pernah bikin workbook
    baru: Harga & Stok ikut ditulis sales_info dan keduanya "Wajib"."""
    wb = load_workbook_safe(src_path)
    ws = wb.worksheets[0]
    keep = {r["row"]: r["baru"] for r in changes}

    snap = []
    for r in sorted(keep):
        cells = []
        for c in range(1, ws.max_column + 1):
            src = ws.cell(row=r, column=c)
            cells.append((src.value, copy(src._style), src.number_format))
        snap.append((cells, keep[r]))

    ws.delete_rows(DATA_START, ws.max_row - DATA_START + 1)
    for i, (cells, new_sku) in enumerate(snap):
        row = DATA_START + i
        for c, (val, style, numfmt) in enumerate(cells, start=1):
            cell = ws.cell(row=row, column=c)
            cell.value = new_sku if c == C_SKU else val
            cell._style = style
            cell.number_format = numfmt
    wb.save(out_path)


def write_report(changes, out_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PERUBAHAN"
    ws.append(["Model", "Kategori", "Kode Produk", "Kode Variasi", "Nama Variasi",
               "SKU lama", "SKU baru", "File sumber", "Baris"])
    for r in changes:
        ws.append([r["model"], r["nama"].split()[-1], r["pid"], r["varid"], r["varian"],
                   str(r["sku"]), r["baru"], r["file"], r["row"]])
    for col, w in zip("ABCDEFGHI", (10, 11, 14, 14, 34, 24, 24, 11, 7)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    wb.save(out_path)


if __name__ == "__main__":
    main()
