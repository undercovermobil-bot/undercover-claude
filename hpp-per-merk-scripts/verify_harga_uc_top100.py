#!/usr/bin/env python3
"""Verifikasi 'Harga Baru UC Top 100 (Reguler).xlsx' - dibaca ulang dari disk."""
import math
import re
import sys
import zipfile

import openpyxl

from harga_baru_uc_top100 import LONCATAN, OUT, SHEET_SRC, SRC

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
    ws = wb["Harga Baru UC Top 100"]
    baris = [tuple(r) for r in ws.iter_rows(min_row=2, max_col=6, values_only=True) if r[0]]

    cek("1. jumlah baris = jumlah model sumber", len(baris) == len(model_sumber),
        f"{len(baris)} vs {len(model_sumber)}")
    cek("2. semua nama model sumber ada di output", set(model_sumber) == {b[0] for b in baris})

    luar_rentang, bukan_ribuan = [], []
    for nama, pcs, dasar, actual, baru, selisih in baris:
        if not (dasar <= baru <= dasar + LONCATAN * 1000):
            luar_rentang.append((nama, dasar, baru))
        if baru % 1000 != 0:
            bukan_ribuan.append((nama, baru))
    cek("3. harga baru dalam [dasar, dasar+5000]", not luar_rentang, str(luar_rentang[:5]))
    cek("4. harga baru kelipatan Rp1.000", not bukan_ribuan, str(bukan_ribuan[:5]))

    dasar_asli = {}
    for r in range(2, ws_src.max_row + 1):
        nama = ws_src.cell(r, 1).value
        if not nama:
            continue
        pcs = ws_src.cell(r, 3).value
        ac = ws_src.cell(r, 29).value
        d = math.ceil(round(ac, 4) / 1000) * 1000
        dasar_asli.setdefault(pcs, set()).add(d)
    salah_dasar = []
    peta_baris = {b[0]: b for b in baris}
    for r in range(2, ws_src.max_row + 1):
        nama = ws_src.cell(r, 1).value
        if not nama:
            continue
        nama = str(nama).strip()
        pcs_sumber = ws_src.cell(r, 3).value
        dasar_output = peta_baris[nama][2]
        dasar_benar = next(iter(dasar_asli[pcs_sumber]))
        if dasar_output != dasar_benar:
            salah_dasar.append((nama, dasar_output, dasar_benar))
    cek("5. dasar kelas di output = ceil(AC sumber /1000)*1000", not salah_dasar,
        str(salah_dasar[:5]))

    per_kelas = {}
    for nama, pcs, dasar, actual, baru, selisih in baris:
        per_kelas.setdefault(pcs, []).append((actual, baru, nama))
    tidak_monoton = []
    for pcs, lst in per_kelas.items():
        lst.sort(key=lambda x: x[0])
        for i in range(1, len(lst)):
            if lst[i][1] < lst[i - 1][1]:
                tidak_monoton.append((pcs, lst[i - 1], lst[i]))
    cek("6. dalam 1 kelas, harga ACTUAL naik -> harga baru tidak pernah turun", not tidak_monoton,
        str(tidak_monoton[:5]))

    tidak_sama = []
    for pcs, lst in per_kelas.items():
        by_actual = {}
        for actual, baru, nama in lst:
            by_actual.setdefault(actual, set()).add(baru)
        for actual, s in by_actual.items():
            if len(s) > 1:
                tidak_sama.append((pcs, actual, s))
    cek("7. harga ACTUAL sama -> harga baru sama (dalam 1 kelas)", not tidak_sama,
        str(tidak_sama[:5]))

    kelas_tanpa_dasar = []
    for pcs in {b[1] for b in baris}:
        anggota = [b for b in baris if b[1] == pcs]
        d = anggota[0][2]
        if not any(b[4] == d for b in anggota):
            kelas_tanpa_dasar.append(pcs)
    cek("8. tiap kelas py minimal 1 model di harga dasar", not kelas_tanpa_dasar,
        str(kelas_tanpa_dasar))

    with zipfile.ZipFile(OUT) as z:
        f_aneh = 0
        for n in z.namelist():
            if re.match(r"xl/worksheets/sheet\d+\.xml", n):
                f_aneh += len(re.findall(r"<f[ />]", z.read(n).decode("utf-8", "replace")))
    cek("9. tidak ada elemen formula di output", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
