#!/usr/bin/env python3
"""
Harga jual baru untuk toko Smartprotection (SP) & Otoprotection (OP), varian Reguler.

Latar (instruksi user 2026-08-20):
  "Aku mau membuat harga produk baru seperti di toko undercover kemarin, harganya
   gunakan yg di sheet hpp 12% dan pakai yg kolom 'harga jual terbaru' yang aku
   warnai hijau, untuk harganya sesuaikan dengan ukuran mobilnya seperti undercover
   kemarin, dengan jarak maksimal 5rb dari harga terendahnya, untuk harga jual
   terbarunya bulatkan keatas paling dekat jadi nominal ribuan."

Diperjelas lewat AskUserQuestion:
  - Sebaran harga dalam 1 kelas ukuran: IKUT PERINGKAT harga UC (bukan proporsional,
    bukan rata) - "Ikut peringkat harga seperti di UC, tapi tetap menyesuaikan dengan
    pcs/rollnya sama dengan cara di UC" -> per kelas pcs/roll, tetap rank-based.
  - Kolom "Harga Jual ACTUAL" (kolom I) di file sumber DIABAIKAN - itu harga lama utk
    toko UC yg kebetulan tercampur di file, BUKAN acuan utk SP/OP. Acuan urutan/rank
    yang dipakai: harga jual Reguler ASLI dari listing Shopee toko Undercover Autocare
    (data yang sudah divalidasi berkali-kali sepanjang sesi ini), bukan kolom I.

Metodologi:
  1. "Harga Jual Terbaru" (kolom AC, sheet "HPP 12%") murni fungsi dari Pcs/Roll ACTUAL
     (kolom C) - dicek eksplisit, konstan sempurna per kelas pcs (565rb/443rb/370rb/
     322rb/287rb untuk pcs 3/4/5/6/7). Dibulatkan KE ATAS ke ribuan terdekat -> jadi
     "dasar" (harga TERENDAH yang boleh dipakai) untuk kelas ukuran itu.
  2. Plafon kelas = dasar + 5.000 (instruksi: "jarak maksimal 5rb dari harga terendahnya").
     Karena hasil akhir wajib kelipatan 1.000, tiap kelas cuma py 6 kemungkinan nilai
     (dasar+0 s.d. dasar+5.000).
  3. Tiap model dicari harga Reguler-nya di listing Shopee UC (via ALIAS yang sudah
     divalidasi di build_hpp_per_merk.py - bukan re-derive matching dari nol).
  4. Dalam 1 kelas pcs, model diurutkan berdasar harga UC, lalu disebar rata ke 6
     tingkat itu berdasar PERINGKAT (bukan proporsi rupiah) - model termurah di UC
     dapat harga dasar, termahal dapat dasar+5rb, sisanya interpolasi peringkat.
     Model dgn harga UC yang SAMA -> tingkat yang SAMA (tidak dipisah paksa).

PENTING - ini BARU membuat LIST HARGA (belum update ke listing SP/OP manapun).
User: "Buatkan dulu saja listnya di file baru, nanti untuk update ke ecommercenya
setelah aku berikan file list produk SP dan OP nya."
"""
import math
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, ".")
from build_hpp_per_merk import ALIAS, MERAGUKAN, baca_harga_shopee, norm

SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/21438ea2-HPP_STP_OTP_.xlsx"
SHEET_SRC = "HPP 12%"
OUT = "Harga Baru SP-OP (Reguler).xlsx"

KOL_NAMA, KOL_PCS, KOL_AC = 1, 3, 29
LONCATAN = 5  # jumlah tingkat kenaikan (Rp1.000 x LONCATAN = jarak maksimal 5rb)

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)
ARIAL_MIRING = Font(name="Arial", size=10, italic=True)
KUNING = PatternFill(start_color="FFFFFF00", end_color="FFFFFF00", fill_type="solid")
RP = '_-[$Rp-421]* #,##0_-;-[$Rp-421]* #,##0_-;_-[$Rp-421]* "-"??_-;_-@_-'


def dasar_kelas(ws):
    """pcs -> harga dasar kelas (Harga Jual Terbaru dibulatkan ke atas ke ribuan)."""
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


def peta_harga_uc():
    harga = baca_harga_shopee()  # nama -> (harga modus, {harga: jumlah varian})
    return {norm(k): v[0] for k, v in harga.items()}


def cocokkan_uc(nama, peta_norm):
    target = ALIAS.get(nama, nama)
    return peta_norm.get(norm(target))


def hitung_harga_baru(baris, dasar):
    """baris: list of (nama, pcs, harga_uc atau None). return {nama: (harga_baru, tingkat)}."""
    hasil = {}
    per_kelas = {}
    for nama, pcs, huc in baris:
        per_kelas.setdefault(pcs, []).append((nama, huc))

    for pcs, anggota in per_kelas.items():
        d = dasar[pcs]
        unik = sorted({huc for _, huc in anggota if huc is not None})
        for nama, huc in anggota:
            if huc is None:
                hasil[nama] = (d, None)  # tanpa acuan UC -> pakai dasar (aman, terendah), ditandai
                continue
            if len(unik) == 1:
                tingkat = 0
            else:
                idx = unik.index(huc)
                tingkat = round(idx / (len(unik) - 1) * LONCATAN)
            hasil[nama] = (d + tingkat * 1000, tingkat)
    return hasil


def tulis_catatan(ws, jumlah_model, per_pcs_n, tanpa_uc):
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 60
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
                     f"(Reguler). List produk untuk toko Smartprotection & Otoprotection.")
    tulis("Kolom 'Harga Jual ACTUAL' (I) di sumber", "DIABAIKAN atas konfirmasi user - itu "
          "harga lama toko UC yang kebetulan tercampur di file ini, bukan acuan untuk SP/OP.")
    tulis("Dasar harga per kelas ukuran (Pcs/Roll)", "'Harga Jual Terbaru' (kolom AC, hijau) "
          "dibulatkan KE ATAS ke ribuan terdekat. Dicek konstan sempurna per pcs.")
    for pcs, d in sorted(per_pcs_n.items()):
        tulis(f"  Pcs/Roll {pcs:.0f}", f"dasar Rp{d[0]:,.0f}".replace(",", ".") +
              f" - Rp{d[0] + LONCATAN * 1000:,.0f}".replace(",", ".") +
              f"  ({d[1]} model)")
    tulis("Sebaran dalam 1 kelas", "Ikut PERINGKAT harga Reguler UC (listing Shopee Undercover "
          "Autocare) - model termurah di UC = harga dasar, termahal = dasar+Rp5.000, sisanya "
          "interpolasi peringkat (bukan proporsi rupiah). Model dgn harga UC sama -> tingkat sama.")
    tulis("Pembulatan", "Harga akhir kelipatan Rp1.000 (otomatis, karena dasar & loncatan "
          "sudah kelipatan Rp1.000).")
    tulis("")

    if tanpa_uc:
        tulis(f"MODEL TANPA ACUAN HARGA UC ({len(tanpa_uc)}) - dipakai harga dasar (terendah, "
              "paling aman), PERLU DICEK MANUAL", "", tebal=True)
        for nama, alasan in tanpa_uc:
            tulis(nama, alasan)


def main():
    wb_src = openpyxl.load_workbook(SRC, data_only=True)
    ws_src = wb_src[SHEET_SRC]
    dasar = dasar_kelas(ws_src)
    peta_norm = peta_harga_uc()

    baris, tanpa_uc = [], []
    for r in range(2, ws_src.max_row + 1):
        nama = ws_src.cell(r, KOL_NAMA).value
        if not nama:
            continue
        nama = str(nama).strip()
        pcs = ws_src.cell(r, KOL_PCS).value
        huc = cocokkan_uc(nama, peta_norm)
        if huc is None:
            alasan = MERAGUKAN.get(nama, "tidak ketemu padanan di listing Shopee UC")
            tanpa_uc.append((nama, alasan))
        baris.append((nama, pcs, huc))

    hasil = hitung_harga_baru(baris, dasar)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Harga Baru SP-OP"
    judul = ["Nama Produk", "Pcs/Roll", "Harga Dasar Kelas", "Harga UC (acuan peringkat)",
             "Harga Baru SP/OP", "Selisih dari Dasar"]
    for c, t in enumerate(judul, 1):
        sel = ws.cell(1, c, t)
        sel.font = ARIAL_TEBAL

    rbaris = 2
    for nama, pcs, huc in baris:
        harga_baru, tingkat = hasil[nama]
        d = dasar[pcs]
        nilai = [nama, pcs, d, huc if huc is not None else "", harga_baru, harga_baru - d]
        for c, v in enumerate(nilai, 1):
            sel = ws.cell(rbaris, c, v)
            sel.font = ARIAL
            if c in (3, 4, 5, 6) and isinstance(v, (int, float)):
                sel.number_format = RP
            if huc is None and c == 5:
                sel.fill = KUNING
        rbaris += 1

    lebar = {"A": 38, "B": 10, "C": 18, "D": 22, "E": 18, "F": 16}
    for kol, w in lebar.items():
        ws.column_dimensions[kol].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:F{rbaris - 1}"

    per_pcs_n = {}
    for nama, pcs, huc in baris:
        d = dasar[pcs]
        per_pcs_n.setdefault(pcs, [d, 0])
        per_pcs_n[pcs][1] += 1

    ws_catatan = wb.create_sheet("CATATAN")
    tulis_catatan(ws_catatan, len(baris), per_pcs_n, tanpa_uc)

    wb.save(OUT)
    print("tersimpan:", OUT)
    print(f"total model         : {len(baris)}")
    print(f"model dgn acuan UC   : {len(baris) - len(tanpa_uc)}")
    print(f"model TANPA acuan UC : {len(tanpa_uc)}  -> {[n for n, _ in tanpa_uc]}")
    for pcs in sorted(dasar):
        n = sum(1 for _, p, _ in baris if p == pcs)
        print(f"  pcs={pcs:.0f}: dasar Rp{dasar[pcs]:,.0f}".replace(",", ".") +
              f"  plafon Rp{dasar[pcs]+LONCATAN*1000:,.0f}".replace(",", ".") +
              f"  ({n} model)")


if __name__ == "__main__":
    main()
