#!/usr/bin/env python3
"""Verifikasi 'Harga Baru SP-OP (matriks).xlsx' - dibaca ulang dari disk."""
import math
import re
import sys
import zipfile
from collections import defaultdict

import openpyxl

from harga_baru_sp_op_matriks import (KATEGORI, KATEGORI_TAMBAHAN, MAX_SPREAD,
                                       OUT, PANJANG_MM, SHEET_SRC, SRC, STEP)

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def main():
    wb_src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = wb_src[SHEET_SRC]
    model_sumber = [str(ws_src.cell(r, 1).value).strip() for r in range(2, ws_src.max_row + 1)
                     if ws_src.cell(r, 1).value]

    wb = openpyxl.load_workbook(OUT, data_only=True)
    ws = wb["Harga Baru SP-OP"]
    baris = [tuple(r) for r in ws.iter_rows(min_row=2, max_col=8, values_only=True) if r[1]]

    cek("1. jumlah baris = jumlah model sumber", len(baris) == len(model_sumber) == 200,
        f"{len(baris)} vs {len(model_sumber)}")
    cek("2. semua nama model sumber ada di output", set(model_sumber) == {b[1] for b in baris})
    cek("3. semua model py kategori & panjang terdaftar",
        all(b[1] in KATEGORI and b[1] in PANJANG_MM for b in baris))

    lantai = {}
    for r in range(2, ws_src.max_row + 1):
        nm = ws_src.cell(r, 1).value
        if not nm:
            continue
        pr = int(round(float(ws_src.cell(r, 3).value)))
        hjt = ws_src.cell(r, 29).value
        d = math.ceil(round(hjt, 4) / 1000) * 1000
        lantai.setdefault(pr, set()).add(d)
    tak_konstan = {k: v for k, v in lantai.items() if len(v) > 1}
    cek("4. lantai (dasar) konstan per Pcs/Roll", not tak_konstan, str(tak_konstan))
    lantai = {k: next(iter(v)) for k, v in lantai.items()}

    salah_lantai, luar_rentang, bukan_ribuan = [], [], []
    for no, nama, pr, kat, pj, mentah, baru, flag in baris:
        d = lantai[pr]
        if baru < d or baru > d + MAX_SPREAD:
            luar_rentang.append((nama, d, baru))
        if baru % STEP != 0:
            bukan_ribuan.append((nama, baru))
    cek("5. harga baru dalam [lantai, lantai+5000]", not luar_rentang, str(luar_rentang[:5]))
    cek("6. harga baru kelipatan Rp1.000", not bukan_ribuan, str(bukan_ribuan[:5]))

    per_grup = defaultdict(list)
    for no, nama, pr, kat, pj, mentah, baru, flag in baris:
        per_grup[(pr, kat)].append((pj, baru, nama))
    tidak_monoton, beda_panjang_sama_harga_paksa = [], []
    for (pr, kat), lst in per_grup.items():
        lst.sort(key=lambda x: x[0])
        for i in range(1, len(lst)):
            if lst[i][1] < lst[i - 1][1]:
                tidak_monoton.append(((pr, kat), lst[i - 1], lst[i]))
        by_pj = defaultdict(set)
        for pj, baru, nama in lst:
            by_pj[pj].add(baru)
        for pj, s in by_pj.items():
            if len(s) > 1:
                beda_panjang_sama_harga_paksa.append(((pr, kat), pj, s))
    cek("7. dalam 1 grup, panjang naik -> harga tidak pernah turun", not tidak_monoton,
        str(tidak_monoton[:3]))
    cek("8. panjang sama persis -> harga sama persis (dalam 1 grup)",
        not beda_panjang_sama_harga_paksa, str(beda_panjang_sama_harga_paksa[:5]))

    kelas_tanpa_lantai = []
    for (pr, kat), lst in per_grup.items():
        d = lantai[pr]
        if not any(baru == d for _, baru, _ in lst):
            kelas_tanpa_lantai.append((pr, kat))
    cek("9. tiap grup py minimal 1 model di harga lantai", not kelas_tanpa_lantai,
        str(kelas_tanpa_lantai))

    flag_baru = {b[1] for b in baris if b[7]}
    cek("10. kolom 'Klasifikasi Baru?' persis menandai 100 model KATEGORI_TAMBAHAN",
        flag_baru == set(KATEGORI_TAMBAHAN), f"selisih: {flag_baru ^ set(KATEGORI_TAMBAHAN)}")

    with zipfile.ZipFile(OUT) as z:
        f_aneh = 0
        for n in z.namelist():
            if re.match(r"xl/worksheets/sheet\d+\.xml", n):
                f_aneh += len(re.findall(r"<f[ />]", z.read(n).decode("utf-8", "replace")))
    cek("11. tidak ada elemen formula di output", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
