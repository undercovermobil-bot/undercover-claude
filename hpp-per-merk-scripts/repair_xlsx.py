"""Perbaiki file xlsx export Shopee supaya bisa dibuka openpyxl.

Masalah: export Shopee memuat atribut `activePane` dengan nilai di luar daftar yang
diizinkan skema OOXML ({topLeft, topRight, bottomLeft, bottomRight}), sehingga
openpyxl menolak seluruh workbook:
    ValueError: Unable to read workbook: could not read worksheets

Solusi: buang atribut `activePane` (dan `pane` yang kosong) dari XML worksheet.
Atribut ini murni kosmetik (posisi split pane di tampilan Excel), tidak memengaruhi data.
"""
import re, sys, shutil, zipfile, os


def bad_values(path):
    """kumpulkan nilai activePane yang tidak sah, buat pelaporan"""
    found = set()
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.startswith("xl/worksheets/") and n.endswith(".xml"):
                for m in re.finditer(rb'activePane="([^"]*)"', z.read(n)):
                    v = m.group(1).decode()
                    if v not in ("topLeft", "topRight", "bottomLeft", "bottomRight"):
                        found.add(v)
    return found


def repair(src, dst):
    """salin xlsx sambil membuang atribut activePane dari sheet XML"""
    n_fixed = 0
    with zipfile.ZipFile(src) as zin:
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                    new = re.sub(rb'\s*activePane="[^"]*"', b'', data)
                    if new != data:
                        n_fixed += 1
                    data = new
                zout.writestr(item, data)
    return n_fixed


if __name__ == "__main__":
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "BARU"
    dst_dir = sys.argv[2] if len(sys.argv) > 2 else "BARU_FIX"
    os.makedirs(dst_dir, exist_ok=True)
    for f in sorted(os.listdir(src_dir)):
        if not f.endswith(".xlsx"):
            continue
        s, d = os.path.join(src_dir, f), os.path.join(dst_dir, f)
        bad = bad_values(s)
        n = repair(s, d)
        tag = f"nilai tak sah={sorted(bad)}" if bad else ""
        print(f"  {f:22} sheet diperbaiki={n:3}  {tag}")
    print(f"\nhasil di: {dst_dir}/")
