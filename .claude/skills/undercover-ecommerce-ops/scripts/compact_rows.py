"""Rapatkan nomor baris data sebuah file mass-upload (Shopee/TikTok/Lazada) supaya BERURUTAN mulai dari baris data pertama.

Kenapa: marketplace memproses 0 baris bila file mass-upload berisi baris bolong (mis. header lalu langsung baris 4318).
File yang hanya berisi sebagian produk HARUS direnumerasi: Shopee data mulai baris 7, TikTok baris 6, Lazada baris 5.

Pakai:  py -3 -I compact_rows.py <file.xlsx> <jumlah_baris_header>            (menimpa file itu)
        py -3 -I compact_rows.py <file.xlsx> <jumlah_baris_header> <keluaran.xlsx>
Sebagai modul:  from compact_rows import compact, renumber_row
"""
import os
import re
import shutil
import sys
import zipfile

SHEET = "xl/worksheets/sheet1.xml"
ROW_TAG = r"<row [^>]*?/?>"


def row_number(row_xml):
    return int(re.search(r'\br="(\d+)"', re.match(ROW_TAG, row_xml).group(0)).group(1))


def renumber_row(row_xml, new):
    """Ubah nomor baris dan semua referensi sel (A12 -> A<new>) di dalam satu elemen <row>."""
    old = row_number(row_xml)
    tag = re.match(ROW_TAG, row_xml).group(0)
    tag2 = re.sub(r'(\br=")%d(")' % old, r"\g<1>%d\2" % new, tag, count=1)
    rest = row_xml[len(tag):]
    rest = re.sub(r'(<c r="[A-Z]+)%d(")' % old, r"\g<1>%d\2" % new, rest)
    return tag2 + rest


def split_sheet(xml):
    head, rest = xml.split("<sheetData>", 1)
    body, tail = rest.split("</sheetData>", 1)
    rows = re.findall(r"<row [^>]*?/>|<row [^>]*>.*?</row>", body, re.S)
    return head, rows, tail


def set_dimension(head, last_row):
    return re.sub(r'(<dimension ref="[A-Z]+\d+:[A-Z]+)\d+(")', r"\g<1>%d\2" % last_row, head, count=1)


def write_zip(src, dst, new_sheet_xml):
    zin = zipfile.ZipFile(src)
    tmp = dst + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = new_sheet_xml.encode("utf8") if it.filename == SHEET else zin.read(it.filename)
            zout.writestr(it, data, compress_type=zipfile.ZIP_DEFLATED)
    zin.close()
    shutil.move(tmp, dst)


def compact(path, header_rows, out=None):
    xml = zipfile.ZipFile(path).read(SHEET).decode("utf8")
    head, rows, tail = split_sheet(xml)
    kept, nxt, changed = [], header_rows + 1, 0
    for r in rows:
        n = row_number(r)
        if n <= header_rows:
            kept.append(r)
            continue
        if n != nxt:
            r = renumber_row(r, nxt)
            changed += 1
        kept.append(r)
        nxt += 1
    new = set_dimension(head, nxt - 1) + "<sheetData>" + "".join(kept) + "</sheetData>" + tail
    write_zip(path, out or path, new)
    return nxt - 1 - header_rows, changed


if __name__ == "__main__":
    n, c = compact(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None)
    print(f"baris data: {n}, baris yang dinomori ulang: {c}")
