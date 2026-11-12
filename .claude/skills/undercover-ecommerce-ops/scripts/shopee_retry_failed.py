"""Buat file ulang (retry) untuk produk yang GAGAL pada mass update basic info Shopee.

Input : file yang diupload (mis. *_ARCHIVE.xlsx) dan file hasil Shopee (Result_shopee_mass_update_basic_info_*.xlsx).
Aturan: hanya produk yang gagal DAN namanya berakhiran " (Archive)" (produk yang memang perlu diubah); karakter yang
        dilaporkan Shopee sebagai "tidak valid" dibuang dari deskripsi; baris direnumerasi berurutan mulai baris 7.
Catatan: hasil Shopee juga memuat produk yang tidak diubah (nama sama) tetapi gagal karena deskripsinya - itu tidak perlu diulang.

Pakai:  py -3 -I shopee_retry_failed.py --archive ARCHIVE.xlsx --result RESULT.xlsx --out RETRY.xlsx
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compact_rows import SHEET, renumber_row, row_number, set_dimension, split_sheet, write_zip  # noqa: E402
from xlsx_zip import load_xlsx  # noqa: E402
import zipfile  # noqa: E402

HEADER_ROWS = 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--suffix", default=" (Archive)")
    a = ap.parse_args()

    failed, flagged = {}, set()
    for r, v in load_xlsx(a.result)["Sheet1"]:
        if r >= 7 and v and v[0]:
            reason = (v + [None] * 5)[4] or ""
            failed[v[0]] = reason
            for m in re.finditer(r"karakter yang tidak valid \[(.+?)\]", reason):
                flagged.update(m.group(1))
    print(f"produk gagal: {len(failed)} | karakter dilaporkan tidak valid: {sorted(flagged)}")
    print("alasan lain (bukan karakter):", collections.Counter(re.sub(r"\[.*?\]", "[..]", x) for x in failed.values()
                                                                if "karakter yang tidak valid" not in x) or "tidak ada")

    zin = zipfile.ZipFile(a.archive)
    ss = [re.sub(r"<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", zin.read("xl/sharedStrings.xml").decode("utf8"), re.S)]
    head, rows, tail = split_sheet(zin.read(SHEET).decode("utf8"))

    def text(row, col):
        m = re.search(r'<c r="%s\d+"([^>]*?)(?:/>|>(.*?)</c>)' % col, row, re.S)
        if not m or not m.group(2):
            return None, None
        if "inlineStr" in m.group(1):  # sel yang diedit (mis. nama "(Archive)") berupa inline string
            return re.sub(r"<[^>]+>", "", m.group(2)), m.group(0)
        v = re.search(r"<v>(\d+)</v>", m.group(2))
        return (ss[int(v.group(1))] if 't="s"' in m.group(1) and v else None), m.group(0)

    kept, cleaned, nxt = [], 0, HEADER_ROWS + 1
    for r in rows:
        n = row_number(r)
        if n <= HEADER_ROWS:
            kept.append(r)
            continue
        pid, _ = text(r, "A")
        name, _ = text(r, "C")
        if pid not in failed or not (name or "").endswith(a.suffix):
            continue
        desc, cell = text(r, "D")
        if desc is not None and any(ch in desc for ch in flagged):
            new = "".join(ch for ch in desc if ch not in flagged)
            sty = re.search(r's="(\d+)"', cell)
            newcell = '<c r="D%d"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (
                n, (' s="%s"' % sty.group(1)) if sty else "", new)
            r = r.replace(cell, newcell)
            cleaned += 1
        kept.append(renumber_row(r, nxt))
        nxt += 1
    new_xml = set_dimension(head, nxt - 1) + "<sheetData>" + "".join(kept) + "</sheetData>" + tail
    write_zip(a.archive, a.out, new_xml)
    print(f"baris ulang: {nxt - 1 - HEADER_ROWS} produk | deskripsi dibersihkan: {cleaned} | ditulis ke {a.out}")


if __name__ == "__main__":
    main()
