#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versi 3 -- 2 perubahan dari v2 atas permintaan user (2026-08-27):

1. **Kalibrasi rentang-panjang DIKUNCI dari 200 model LAMA saja**, bukan
   dihitung ulang dari SELURUH anggota grup (lama+baru) tiap kali ada
   tambahan model. Masalah di v2: nambah 92 model baru ke grup (Pcs/Roll x
   Kategori) yang sudah ada bikin 33 harga dari 200 model lama ikut geser
   +-Rp1.000-3.000, krn rentang minimal-maksimal dihitung ulang dari
   anggota grup SAAT ITU JUGA (bukan tetap). User: "nanti tiap ada mobil
   baru yang dimasukkan bakal geser terus dong?" -- benar, itu bug desain.

   Perbaikan: kalibrasi (lo, rentang, n_langkah) per grup (Pcs/Roll x
   Kategori) DIHITUNG SEKALI dari anggota LAMA (200 model, penanda
   `baru_di_sp_op=False`), lalu DIPAKAI ULANG utk memposisikan SEMUA
   anggota (lama maupun baru) di grup itu -- lihat `kalibrasi_grup()` +
   `posisi()`. Anggota lama otomatis dapat harga PERSIS SAMA seperti v1
   (diverifikasi 0 selisih utk yg BUKAN top-10 floor, lihat poin 2).
   Anggota baru yang panjangnya di luar rentang lama tetap dipetakan pakai
   skala yg sama (linear), tapi DIBATASI 0..Rp5.000 (tidak pernah
   negatif/tidak pernah > cap spread lama) supaya tidak ekstrem.
   Grup yang SAMA SEKALI tidak py anggota lama (cuma 1 kombinasi:
   Pcs/Roll=6 x SUV besar, isinya cuma Chery Tiggo 8 baru) dihitung dari
   anggota barunya sendiri sbg baseline (tidak ada yg lain utk dikunci).
   **Konsekuensi ke depan**: skema ini permanen -- kalau nanti ada
   tambahan model LAGI, kalibrasi tetap dikunci dari 200 model original
   ini (bukan 292 model saat ini), supaya tidak ada drift lebih lanjut.

2. **10 produk terlaris pertama pakai HARGA TERENDAH (lantai Pcs/Roll)**,
   bukan harga hasil spread. Contoh dari user: Honda Brio -> Rp322.000
   (bukan Rp326.000 hasil spread), Toyota Avanza -> Rp370.000 (bukan
   Rp373.000). Daftar 10: Avanza, Brio, Innova, Jazz, Ertiga, HR-V, Agya,
   Ayla, Xenia, Livina (urutan No.1-10 di file, sama seperti dipakai di
   batch UC top-100 sebelumnya).

Pemakaian: python3 harga_baru_sp_op_matriks_v3.py
"""
import math
from collections import defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

from harga_baru_sp_op_matriks_v2 import (
    DIKECUALIKAN, KATEGORI, KATEGORI_TAMBAHAN2, PANJANG_MM, SHEET_SRC, SRC,
    ceil1000,
)

OUT = "Harga Baru SP-OP (matriks) v3.xlsx"
STEP = 1000
MAX_SPREAD = 5000
MM_PER_STEP = 100

TOP10_FLOOR = {
    'Toyota Avanza', 'Honda Brio Satya / RS', 'Toyota Innova', 'Honda Jazz',
    'Suzuki Ertiga', 'Honda HR-V / e:N1', 'Toyota Agya', 'Daihatsu Ayla',
    'Daihatsu Xenia', 'Nissan Livina / Grand Livina',
}

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)
ARIAL_MIRING = Font(name="Arial", size=10, italic=True)
HDR = PatternFill('solid', fgColor='FFC000')
HIJAU = PatternFill('solid', fgColor='C6EFCE')
BIRU = PatternFill('solid', fgColor='BDD7EE')
RP = '_-[$Rp-421]* #,##0_-;-[$Rp-421]* #,##0_-;_-[$Rp-421]* "-"??_-;_-@_-'


def kalibrasi_grup(panjang_list):
    """(lo, rentang, n_langkah) dari sekumpulan panjang -- bisa dipakai
    memposisikan mobil MANA PUN (bukan cuma yg ada di panjang_list),
    beda dari hitung_langkah() versi lama yg cuma bikin peta utk titik yg
    sudah diketahui semua."""
    unik = sorted(set(panjang_list))
    lo, hi = unik[0], unik[-1]
    rentang = hi - lo
    if rentang == 0:
        return lo, 0, 0
    spread = min(int(math.floor(rentang / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
    n_langkah = spread // STEP
    return lo, rentang, n_langkah


def posisi(panjang, kalib):
    lo, rentang, n_langkah = kalib
    if rentang == 0:
        return 0
    mentah = int(math.floor((panjang - lo) / rentang * n_langkah + 0.5)) * STEP
    return max(0, min(mentah, MAX_SPREAD))


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb[SHEET_SRC]

    produk = []
    dilewati = []
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=1).value
        if not nm:
            continue
        nm = str(nm).strip()
        if nm in DIKECUALIKAN:
            dilewati.append(nm)
            continue
        pr = ws.cell(row=r, column=3).value
        hjt = ws.cell(row=r, column=29).value
        if nm not in KATEGORI or nm not in PANJANG_MM:
            raise SystemExit(f"BELUM ada klasifikasi utk: {nm}")
        if pr is None or hjt is None:
            raise SystemExit(f"Data Pcs/Roll atau harga kosong utk: {nm} (baris {r})")
        pr = int(round(float(pr)))
        produk.append({"nama": nm, "pcsroll": pr, "hjt": hjt,
                        "kat": KATEGORI[nm], "panjang": PANJANG_MM[nm],
                        "baru_di_sp_op": nm in KATEGORI_TAMBAHAN2})

    lantai = {}
    for p in produk:
        lantai.setdefault(p["pcsroll"], ceil1000(p["hjt"]))

    grup_lama = defaultdict(list)
    grup_semua = defaultdict(list)
    for p in produk:
        grup_semua[(p["pcsroll"], p["kat"])].append(p)
        if not p["baru_di_sp_op"]:
            grup_lama[(p["pcsroll"], p["kat"])].append(p["panjang"])

    kalib_per_grup = {}
    grup_tanpa_anggota_lama = []
    for key, anggota in grup_semua.items():
        if key in grup_lama:
            kalib_per_grup[key] = kalibrasi_grup(grup_lama[key])
        else:
            kalib_per_grup[key] = kalibrasi_grup([a["panjang"] for a in anggota])
            grup_tanpa_anggota_lama.append(key)

    for key, anggota in grup_semua.items():
        kalib = kalib_per_grup[key]
        for a in anggota:
            a["harga_baru"] = lantai[a["pcsroll"]] + posisi(a["panjang"], kalib)
            a["floor_top10"] = False

    for p in produk:
        if p["nama"] in TOP10_FLOOR:
            p["harga_baru"] = lantai[p["pcsroll"]]
            p["floor_top10"] = True

    wb2 = openpyxl.Workbook()
    ws1 = wb2.active
    ws1.title = "Harga Baru SP-OP"
    kolom = ["No", "Nama Produk", "Pcs/Roll", "Tipe Mobil", "Panjang (mm)",
             "Harga Jual Terbaru (mentah)", "Harga Baru (Reguler)", "Keterangan"]
    for i, h in enumerate(kolom, 1):
        c = ws1.cell(1, i, h)
        c.fill = HDR
        c.font = ARIAL_TEBAL
        c.alignment = Alignment(wrap_text=True, vertical="center")

    for i, p in enumerate(produk, 1):
        r = i + 1
        ws1.cell(r, 1, i)
        ws1.cell(r, 2, p["nama"])
        ws1.cell(r, 3, p["pcsroll"])
        ws1.cell(r, 4, p["kat"])
        ws1.cell(r, 5, p["panjang"])
        c6 = ws1.cell(r, 6, round(p["hjt"]))
        c6.number_format = RP
        c7 = ws1.cell(r, 7, p["harga_baru"])
        c7.number_format = RP
        ket = []
        if p["floor_top10"]:
            ket.append("Top-10 - pakai harga terendah")
            c7.fill = BIRU
        else:
            c7.fill = HIJAU
        if p["baru_di_sp_op"]:
            ket.append("Model baru (ronde 2, 2026-08-27)")
        ws1.cell(r, 8, "; ".join(ket))
        for c in range(1, 9):
            ws1.cell(r, c).font = ARIAL

    for col, w in zip("ABCDEFGH", [5, 40, 9, 15, 12, 20, 16, 34]):
        ws1.column_dimensions[col].width = w
    ws1.freeze_panes = "A2"
    ws1.auto_filter.ref = f"A1:H{len(produk)+1}"

    ws2 = wb2.create_sheet("Matriks")
    for i, h in enumerate(["Pcs/Roll", "Tipe Mobil", "Nama Produk", "Panjang (mm)",
                            "Harga Baru (Reguler)"], 1):
        c = ws2.cell(1, i, h)
        c.fill = HDR
        c.font = ARIAL_TEBAL
    r = 2
    for pr in sorted({p["pcsroll"] for p in produk}, reverse=True):
        for kat in sorted({p["kat"] for p in produk if p["pcsroll"] == pr}):
            anggota = sorted([p for p in produk if p["pcsroll"] == pr and p["kat"] == kat],
                              key=lambda x: (x["panjang"], x["nama"]))
            for p in anggota:
                ws2.cell(r, 1, pr).font = ARIAL
                ws2.cell(r, 2, kat).font = ARIAL
                ws2.cell(r, 3, p["nama"]).font = ARIAL
                ws2.cell(r, 4, p["panjang"]).font = ARIAL
                c5 = ws2.cell(r, 5, p["harga_baru"])
                c5.number_format = RP
                c5.fill = BIRU if p["floor_top10"] else HIJAU
                c5.font = ARIAL
                r += 1
            r += 1
    for col, w in zip("ABCDE", [10, 15, 40, 12, 16]):
        ws2.column_dimensions[col].width = w
    ws2.freeze_panes = "A2"

    ws3 = wb2.create_sheet("CATATAN")
    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 70
    baris = [1]

    def tulis(a, b="", tebal=False, miring=False):
        r_ = baris[0]
        for kol, val in (("A", a), ("B", b)):
            if val in ("", None):
                continue
            sel = ws3[f"{kol}{r_}"]
            sel.value = val
            sel.font = ARIAL_TEBAL if tebal else (ARIAL_MIRING if miring else ARIAL)
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris[0] += 1

    tulis("CATATAN v3 (2026-08-27)", "", tebal=True)
    tulis("Perubahan #1 - kalibrasi dikunci", "Rentang panjang-bodi (lo/hi/skala "
          "Rp-per-100mm) per grup (Pcs/Roll x Kategori) SEKARANG DIKUNCI dari 200 "
          "model LAMA saja, bukan dihitung ulang dari seluruh anggota tiap kali ada "
          "tambahan. Ini nyegah 200 harga lama ikut geser tiap kali ada model baru "
          "ditambahkan ke kategori yang sama (bug yg ketemu di v2). Model baru yang "
          "panjangnya di luar rentang lama tetap dipetakan pakai skala yang sama, "
          "dibatasi 0-Rp5.000 dari lantai.")
    tulis("Perubahan #2 - top-10 pakai harga terendah", "10 produk terlaris pertama "
          "(Avanza, Brio, Innova, Jazz, Ertiga, HR-V, Agya, Ayla, Xenia, Livina) "
          "SENGAJA diisi harga TERENDAH (lantai Pcs/Roll-nya), bukan hasil spread - "
          "permintaan eksplisit user. Ditandai fill BIRU + kolom Keterangan.")
    if grup_tanpa_anggota_lama:
        tulis("Grup tanpa anggota lama", "Kombinasi (Pcs/Roll x Kategori) berikut "
              "TIDAK py anggota di 200 model lama, jadi kalibrasinya dihitung dari "
              "anggota barunya sendiri (jadi baseline baru utk grup ini ke depan): " +
              ", ".join(f"Pcs/Roll={k[0]} x {k[1]}" for k in grup_tanpa_anggota_lama))
    if dilewati:
        tulis("DIKECUALIKAN dari perhitungan ini", ", ".join(dilewati) +
              " - data Pcs/Roll & HPP kosong di sumber. Minta user lengkapi dulu di "
              "sheet HPP 12%, baru dihitung menyusul.")
    tulis("PALING PERLU DIKOREKSI", "'Holden' - nama generik tanpa model spesifik "
          "(Commodore/Kingswood/dll beda ukuran jauh). Dipakai asumsi sedan besar "
          "ala Commodore (~4900mm) sbg placeholder - tolong konfirmasi/koreksi model "
          "persisnya.")
    tulis("")
    tulis("92 MODEL RONDE 2 (perlu direview)", "", tebal=True)
    tulis("Nama Produk", "Kategori (baru)", tebal=True)
    for nm in sorted(KATEGORI_TAMBAHAN2):
        tulis(nm, f"{KATEGORI[nm]}, {PANJANG_MM[nm]}mm")

    wb2.save(OUT)

    print(f"tersimpan: {OUT}")
    print(f"total model dihitung: {len(produk)} (dilewati: {dilewati})")
    print(f"grup tanpa anggota lama: {grup_tanpa_anggota_lama}")
    print("\n10 produk floor:")
    for p in produk:
        if p["floor_top10"]:
            print(f"  {p['nama']:30s} Rp{p['harga_baru']:,}".replace(",", "."))


if __name__ == "__main__":
    main()
