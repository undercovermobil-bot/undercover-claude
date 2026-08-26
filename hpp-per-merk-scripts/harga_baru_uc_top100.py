#!/usr/bin/env python3
"""
!!! SUPERSEDED 2026-08-20 - JANGAN PAKAI SCRIPT INI SEBAGAI ACUAN METODE !!!
Metode di file ini (sebar harga ikut PERINGKAT Harga Jual ACTUAL) TERNYATA SALAH.
Yang benar sudah dikerjakan & divalidasi user SEBELUMNYA (2026-08-14/15/18) di
branch `claude/repo-memory-access-4hthja` - metode MATRIKS Pcs/Roll x kategori
bodi x panjang fisik mobil (`scripts/harga_baru_matriks.py`,
`project-undercover-harga-referensi.md`). File ini dibuat SEBELUM riwayat itu
ketemu. Pakai `harga_baru_matriks.py` (salinan resmi dari branch tsb) sebagai
gantinya - hasilnya cocok dgn patokan yang tercatat di memory (Fortuner
Rp457rb, BR-V Rp385rb), sedangkan hasil script INI TIDAK. Docstring asli di
bawah dipertahankan apa adanya untuk riwayat, bukan acuan.

Harga jual baru untuk toko Undercover Autocare (UC), 100 model terlaris, Reguler.

Latar (instruksi user 2026-08-20): "List harganya seperti di file ini [...], harusnya
masih ada memorynya karena kemarin sudah membuat total 23 an list produk yg sudah di
upload di ecommerce, listnya ada di sheet 'hpp 12%' [...] rules penulisan harganya
masih sama seperti sebelumnya."

CATATAN PENTING: memory soal "~23 produk yang sudah diupload" TIDAK ketemu di
claude-memory/ (git) maupun folder memory native sesi ini - kemungkinan dikerjakan di
device/sesi lain yang belum sinkron ke repo (lihat CLAUDE.md soal memory lintas
device). User sudah diberi tahu; script ini menghitung ULANG dari nol untuk SEMUA
100 model dengan metodologi yang SAMA seperti yang baru dipakai di harga_baru_sp_op.py
(dikonfirmasi user "rules penulisan harganya masih sama seperti sebelumnya") - bukan
menebak/melanjutkan 23 yang sudah ada. User perlu cross-check ke listing live sebelum
menimpa harga yang mungkin sudah diupdate.

Beda dgn kasus SP/OP: file ini UNTUK toko UC sendiri, jadi kolom "Harga Jual ACTUAL"
(kolom I, sheet HPP 12%) dipakai LANGSUNG sbg acuan peringkat (dicek: 100/100 baris
cocok persis dgn snapshot listing Shopee UA yang sudah divalidasi sepanjang sesi ini -
BEDA dgn file HPP_STP_OTP_.xlsx yang kolom I-nya kedapatan basi/tidak reliable).

Metodologi (identik harga_baru_sp_op.py):
  1. "Harga Jual Terbaru" (kolom AC) dibulatkan ke atas ke ribuan -> dasar kelas ukuran
     (per Pcs/Roll ACTUAL, kolom C) - dicek konstan sempurna per kelas.
  2. Plafon kelas = dasar + Rp5.000 (6 kemungkinan nilai, kelipatan Rp1.000).
  3. Dalam 1 kelas pcs, model diurutkan berdasar "Harga Jual ACTUAL" (kolom I - harga
     UC saat ini, bukan file eksternal), disebar rata ke 6 tingkat berdasar PERINGKAT.
     Harga ACTUAL yang sama persis -> tingkat yang sama.
"""
import math
import sys

import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/dddf20f5-DATA_UC_HPP_Top_100_Terlaris.xlsx"
SHEET_SRC = "HPP 12%"
OUT = "Harga Baru UC Top 100 (Reguler).xlsx"

KOL_NAMA, KOL_PCS, KOL_ACTUAL, KOL_AC = 1, 3, 9, 29
LONCATAN = 5

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)
ARIAL_MIRING = Font(name="Arial", size=10, italic=True)
RP = '_-[$Rp-421]* #,##0_-;-[$Rp-421]* #,##0_-;_-[$Rp-421]* "-"??_-;_-@_-'


def dasar_kelas(ws):
    per_pcs = {}
    for r in range(2, ws.max_row + 1):
        nama = ws.cell(r, KOL_NAMA).value
        if not nama:
            continue
        pcs = ws.cell(r, KOL_PCS).value
        ac = ws.cell(r, KOL_AC).value
        d = math.ceil(round(ac, 4) / 1000) * 1000
        per_pcs.setdefault(pcs, set()).add(d)
    tak_konstan = {k: v for k, v in per_pcs.items() if len(v) > 1}
    if tak_konstan:
        raise AssertionError(f"dasar harga TIDAK konstan per kelas pcs: {tak_konstan}")
    return {k: next(iter(v)) for k, v in per_pcs.items()}


def hitung_harga_baru(baris, dasar):
    hasil = {}
    per_kelas = {}
    for nama, pcs, actual in baris:
        per_kelas.setdefault(pcs, []).append((nama, actual))

    for pcs, anggota in per_kelas.items():
        d = dasar[pcs]
        unik = sorted({a for _, a in anggota})
        for nama, actual in anggota:
            if len(unik) == 1:
                tingkat = 0
            else:
                idx = unik.index(actual)
                tingkat = round(idx / (len(unik) - 1) * LONCATAN)
            hasil[nama] = (d + tingkat * 1000, tingkat)
    return hasil


def tulis_catatan(ws, jumlah_model, per_pcs_n):
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 66
    baris = [1]

    def tulis(a, b="", tebal=False, miring=False):
        r = baris[0]
        for kol, val in (("A", a), ("B", b)):
            if val in ("", None):
                continue
            sel = ws[f"{kol}{r}"]
            sel.value = val
            if isinstance(val, str) and val.startswith("="):
                sel.data_type = "s"
            sel.font = ARIAL_TEBAL if tebal else (ARIAL_MIRING if miring else ARIAL)
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris[0] += 1

    tulis("CATATAN", "", tebal=True)
    tulis("Sumber", f"'{SRC.rsplit('/', 1)[-1]}', sheet '{SHEET_SRC}' - {jumlah_model} model "
                     "terlaris toko Undercover Autocare (Reguler).")
    tulis("PENTING - soal '23 model sudah diupload'", "Memory tentang ini TIDAK ketemu di "
          "claude-memory/ (git) maupun folder memory native sesi ini - kemungkinan dikerjakan "
          "di device/sesi Claude lain yang belum sinkron ke repo. Semua 100 model di sini "
          "DIHITUNG ULANG dari nol dengan metodologi yang sama, BUKAN melanjutkan 23 yang "
          "sudah ada. Cross-check ke harga yang sudah live di Shopee sebelum menimpa - kalau "
          "ada yang beda, kemungkinan itu salah satu dari 23 yang sudah diupdate manual.")
    tulis("Acuan peringkat", "Kolom 'Harga Jual ACTUAL' (I) - dicek 100/100 baris cocok persis "
          "dengan snapshot listing Shopee Undercover Autocare yang sudah divalidasi sepanjang "
          "sesi ini, jadi dipakai langsung (beda dgn file SP/OP yang kolom I-nya basi).")
    tulis("Dasar harga per kelas ukuran (Pcs/Roll)", "'Harga Jual Terbaru' (kolom AC) "
          "dibulatkan KE ATAS ke ribuan terdekat. Dicek konstan sempurna per pcs.")
    for pcs, d in sorted(per_pcs_n.items()):
        tulis(f"  Pcs/Roll {pcs:.0f}", f"dasar Rp{d[0]:,.0f}".replace(",", ".") +
              f" - Rp{d[0] + LONCATAN * 1000:,.0f}".replace(",", ".") +
              f"  ({d[1]} model)")
    tulis("Sebaran dalam 1 kelas", "Ikut PERINGKAT Harga Jual ACTUAL (kolom I) - model termurah "
          "= harga dasar, termahal = dasar+Rp5.000, sisanya interpolasi peringkat. Harga ACTUAL "
          "sama persis -> tingkat sama.")
    tulis("Pembulatan", "Harga akhir kelipatan Rp1.000 (otomatis).")


def main():
    wb_src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = wb_src[SHEET_SRC]
    dasar = dasar_kelas(ws_src)

    baris = []
    for r in range(2, ws_src.max_row + 1):
        nama = ws_src.cell(r, KOL_NAMA).value
        if not nama:
            continue
        nama = str(nama).strip()
        pcs = ws_src.cell(r, KOL_PCS).value
        actual = ws_src.cell(r, KOL_ACTUAL).value
        baris.append((nama, pcs, actual))

    hasil = hitung_harga_baru(baris, dasar)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Harga Baru UC Top 100"
    judul = ["Nama Produk", "Pcs/Roll", "Harga Dasar Kelas", "Harga Jual ACTUAL (acuan peringkat)",
             "Harga Baru UC", "Selisih dari Dasar"]
    for c, t in enumerate(judul, 1):
        ws.cell(1, c, t).font = ARIAL_TEBAL

    rbaris = 2
    for nama, pcs, actual in baris:
        harga_baru, tingkat = hasil[nama]
        d = dasar[pcs]
        nilai = [nama, pcs, d, actual, harga_baru, harga_baru - d]
        for c, v in enumerate(nilai, 1):
            sel = ws.cell(rbaris, c, v)
            sel.font = ARIAL
            if c in (3, 4, 5, 6) and isinstance(v, (int, float)):
                sel.number_format = RP
        rbaris += 1

    lebar = {"A": 38, "B": 10, "C": 18, "D": 26, "E": 16, "F": 16}
    for kol, w in lebar.items():
        ws.column_dimensions[kol].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:F{rbaris - 1}"

    per_pcs_n = {}
    for nama, pcs, actual in baris:
        d = dasar[pcs]
        per_pcs_n.setdefault(pcs, [d, 0])
        per_pcs_n[pcs][1] += 1

    ws_catatan = wb.create_sheet("CATATAN")
    tulis_catatan(ws_catatan, len(baris), per_pcs_n)

    wb.save(OUT)
    print("tersimpan:", OUT)
    print(f"total model: {len(baris)}")
    for pcs in sorted(dasar):
        n = sum(1 for _, p, _ in baris if p == pcs)
        print(f"  pcs={pcs:.0f}: dasar Rp{dasar[pcs]:,.0f}".replace(",", ".") +
              f"  plafon Rp{dasar[pcs]+LONCATAN*1000:,.0f}".replace(",", ".") +
              f"  ({n} model)")


if __name__ == "__main__":
    main()
