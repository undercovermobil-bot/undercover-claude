#!/usr/bin/env python3
"""Verifikasi 'Harga Baru UC Top 100 (matriks).xlsx' - dibaca ulang dari disk.
Script sumbernya (harga_baru_matriks_ref.py) adalah salinan APA ADANYA dari
branch claude/repo-memory-access-4hthja (scripts/harga_baru_matriks.py) yang
sudah divalidasi user - verifikasi ini murni memastikan salinannya jalan benar
& hasilnya konsisten, bukan menguji ulang metodologinya dari nol."""
import math
import re
import sys
import zipfile
from collections import defaultdict

import openpyxl

SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/dddf20f5-DATA_UC_HPP_Top_100_Terlaris.xlsx"
OUT = "Harga Baru UC Top 100 (matriks).xlsx"
STEP, MAX_SPREAD, TAMBAHAN_STRIP = 1000, 5000, 43000

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def main():
    wb_src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = wb_src["HPP 12%"]
    model_sumber = [str(ws_src.cell(r, 1).value).strip() for r in range(2, ws_src.max_row + 1)
                     if ws_src.cell(r, 1).value]

    wb = openpyxl.load_workbook(OUT, data_only=True)
    ws = wb["Harga Baru"]
    baris = [tuple(r) for r in ws.iter_rows(min_row=2, max_col=8, values_only=True) if r[1]]

    cek("1. jumlah baris = 100", len(baris) == 100 == len(model_sumber))
    cek("2. semua nama model sumber ada di output", set(model_sumber) == {b[1] for b in baris})

    lantai = {}
    for r in range(2, ws_src.max_row + 1):
        nm = ws_src.cell(r, 1).value
        if not nm:
            continue
        pr = int(round(float(ws_src.cell(r, 3).value)))
        hjt = ws_src.cell(r, 29).value
        d = math.ceil(round(hjt, 4) / 1000) * 1000
        lantai.setdefault(pr, set()).add(d)
    cek("3. lantai konstan per Pcs/Roll", all(len(v) == 1 for v in lantai.values()),
        str({k: v for k, v in lantai.items() if len(v) > 1}))
    lantai = {k: next(iter(v)) for k, v in lantai.items()}

    luar_rentang, bukan_ribuan, strip_salah = [], [], []
    for no, nama, pr, kat, pj, mentah, baru, strip in baris:
        d = lantai[pr]
        if not (d <= baru <= d + MAX_SPREAD):
            luar_rentang.append((nama, d, baru))
        if baru % STEP != 0:
            bukan_ribuan.append((nama, baru))
        if strip != baru + TAMBAHAN_STRIP:
            strip_salah.append((nama, baru, strip))
    cek("4. harga baru dalam [lantai, lantai+5000]", not luar_rentang, str(luar_rentang[:5]))
    cek("5. harga baru kelipatan Rp1.000", not bukan_ribuan, str(bukan_ribuan[:5]))
    cek("6. harga Strip = Reguler + Rp43.000", not strip_salah, str(strip_salah[:5]))

    per_grup = defaultdict(list)
    for no, nama, pr, kat, pj, mentah, baru, strip in baris:
        per_grup[(pr, kat)].append((pj, baru, nama))
    tidak_monoton = []
    for key, lst in per_grup.items():
        lst.sort(key=lambda x: x[0])
        for i in range(1, len(lst)):
            if lst[i][1] < lst[i - 1][1]:
                tidak_monoton.append((key, lst[i - 1], lst[i]))
    cek("7. dalam 1 grup, panjang naik -> harga tidak pernah turun", not tidak_monoton,
        str(tidak_monoton[:3]))

    # patokan yang dicatat di memory: Fortuner Rp457rb, BR-V Rp385rb
    peta = {b[1]: b[6] for b in baris}
    cek("8. patokan memory: Toyota Fortuner = Rp457.000", peta.get("Toyota Fortuner") == 457000,
        str(peta.get("Toyota Fortuner")))
    cek("9. patokan memory: Honda BR-V = Rp385.000", peta.get("Honda BR-V") == 385000,
        str(peta.get("Honda BR-V")))

    with zipfile.ZipFile(OUT) as z:
        f_aneh = 0
        for n in z.namelist():
            if re.match(r"xl/worksheets/sheet\d+\.xml", n):
                f_aneh += len(re.findall(r"<f[ />]", z.read(n).decode("utf-8", "replace")))
    cek("10. tidak ada elemen formula di output", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
