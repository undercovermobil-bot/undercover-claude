#!/usr/bin/env python3
"""Verifikasi formula workbook hasil build_hpp_per_merk.py.

LibreOffice tidak jalan di lingkungan ini (soffice gagal memuat file apa pun,
termasuk xlsx 3 sel), jadi recalc.py tidak bisa dipakai. Gantinya:

  1. Baca formula APA ADANYA dari file hasil, lalu evaluasi sendiri.
  2. Skenario A (C kosong, seperti file dikirim) -> pastikan tidak ada #DIV/0!
     dan kolom turunan (D/G/Y/Z/AC) benar-benar kosong.
  3. Skenario B (C diisi 5) -> hasilnya harus sama persis dengan baris
     'Avanza Reguler' Sheet3 DATA_UC_HPP.xlsx yang nilainya sudah diketahui.
"""
import re
import sys
import zipfile

import openpyxl

WB = "DATA UC HPP per Merk (Reguler).xlsx"
KOLOM = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["AA", "AB", "AC"]

# nilai baris 2 Sheet3 DATA_UC_HPP.xlsx ('Avanza Reguler'), J=295000 & C=5
SHEET3_AVANZA = {
    "D": 143000, "G": 179500, "L": 30827.5, "N": 16225, "P": 13275, "R": 7375,
    "T": 14750, "V": 16225, "W": 98677.5, "X": 196322.5, "Y": 296177.5,
    "Z": -1177.5, "AA": 29500, "AB": 324500, "AC": 28322.5,
}
KOSONG = ""


def evaluasi(formula, nilai, baris):
    """Evaluator mini untuk pola formula yang dipakai di workbook ini.

    Sengaja tidak generik: tiap pola dicocokkan persis, dan referensi selnya
    diambil dari teks formula (bukan diasumsikan), supaya salah baris ketahuan.
    """
    f = formula[1:]  # buang '='

    def sel(ref):
        kol, brs = re.match(r"([A-Z]+)(\d+)$", ref).groups()
        assert int(brs) == baris, f"referensi {ref} bukan baris {baris}"
        return nilai.get(kol, KOSONG)

    def angka(v):
        return 0 if v == KOSONG or v is None else v

    m = re.fullmatch(r'IFERROR\((\w+)/(\w+),""\)', f)
    if m:
        a, b = sel(m.group(1)), sel(m.group(2))
        if b in (KOSONG, None, 0):
            return KOSONG
        return a / b

    m = re.fullmatch(r'IF\((\w+)="","",SUM\((\w+):(\w+)\)\)', f)
    if m:
        if sel(m.group(1)) == KOSONG:
            return KOSONG
        k0 = re.match(r"([A-Z]+)", m.group(2)).group(1)
        k1 = re.match(r"([A-Z]+)", m.group(3)).group(1)
        sel(m.group(2)), sel(m.group(3))  # cek barisnya
        i0, i1 = KOLOM.index(k0), KOLOM.index(k1)
        return sum(angka(nilai.get(k, KOSONG)) for k in KOLOM[i0:i1 + 1])

    m = re.fullmatch(r'IF\((\w+)="","",(\w+)-(\w+)\)', f)
    if m:
        if sel(m.group(1)) == KOSONG:
            return KOSONG
        return angka(sel(m.group(2))) - angka(sel(m.group(3)))

    m = re.fullmatch(r'IF\((\w+)="","",(\w+)\+(\w+)\+(\w+)\)', f)
    if m:
        if sel(m.group(1)) == KOSONG:
            return KOSONG
        return sum(angka(sel(g)) for g in m.groups()[1:])

    m = re.fullmatch(r'IF\((\w+)="","",\((\w+)\+(\w+)\)-(\w+)\)', f)
    if m:
        if sel(m.group(1)) == KOSONG:
            return KOSONG
        return (angka(sel(m.group(2))) + angka(sel(m.group(3)))) - angka(sel(m.group(4)))

    m = re.fullmatch(r"(\w+)\*(\w+)", f)
    if m:
        return angka(sel(m.group(1))) * angka(sel(m.group(2)))

    m = re.fullmatch(r"(\w+)\*10%", f)
    if m:
        return angka(sel(m.group(1))) * 0.10

    m = re.fullmatch(r"(\w+)-(\w+)", f)
    if m:
        return angka(sel(m.group(1))) - angka(sel(m.group(2)))

    m = re.fullmatch(r"(\w+)\+(\w+)", f)
    if m:
        return angka(sel(m.group(1))) + angka(sel(m.group(2)))

    m = re.fullmatch(r"(\w+)\+(\w+)\+(\w+)\+(\w+)\+(\w+)\+(\w+)", f)
    if m:
        return sum(angka(sel(g)) for g in m.groups())

    raise AssertionError(f"pola formula tak dikenal: {formula}")


URUTAN_HITUNG = ["D", "G", "L", "N", "P", "R", "T", "V", "W", "X", "Y", "Z", "AA", "AB", "AC"]


def hitung_baris(ws, baris, isi_c=None):
    nilai = {}
    for i, kol in enumerate(KOLOM, start=1):
        v = ws.cell(baris, i).value
        nilai[kol] = KOSONG if v is None else v
    if isi_c is not None:
        nilai["C"] = isi_c
    for kol in URUTAN_HITUNG:
        f = nilai[kol]
        assert isinstance(f, str) and f.startswith("="), f"{ws.title}!{kol}{baris} bukan formula: {f!r}"
        nilai[kol] = evaluasi(f, nilai, baris)
    return nilai


def cek_catatan_tanpa_formula():
    """CATATAN cuma berisi teks/angka dokumentasi - kalau ada string yang diawali '='
    (mis. deskripsi formula sebagai teks), openpyxl bisa salah anggap itu formula
    sungguhan (Cell._bind_value: value.startswith("=") -> data_type='f') dan
    menulis elemen <f> yang cacat (karena bukan referensi sel valid). Excel lalu
    membuang elemen itu saat 'repair'. Ini kejadian nyata sekali - cek eksplisit."""
    wb_formula = openpyxl.load_workbook(WB)  # tanpa data_only: value asli string formula terlihat
    idx = wb_formula.sheetnames.index("CATATAN")
    z = zipfile.ZipFile(WB)
    sheet_xml = z.read(f"xl/worksheets/sheet{idx + 1}.xml").decode()
    n_formula = sheet_xml.count("<f>") + sheet_xml.count("<f ")
    if n_formula:
        raise AssertionError(
            f"CATATAN (sheet{idx + 1}.xml) punya {n_formula} elemen <f> (formula) - "
            "seharusnya nol, sheet ini cuma teks/angka dokumentasi")


def cek_tidak_ada_duplikat_generasi():
    """User pernah menemukan 'Daihatsu Ayla' & 'Daihatsu All New Ayla' sebagai 2 baris
    terpisah padahal model yang sama (sumbernya menulis nama beda per era generasi).
    Deteksi generik: buang kata 'all new'/'new'/'facelift', kalau 2 nama produk di
    sheet yang sama jadi identik setelah itu -> berarti masih ada duplikat yang
    kelolosan (mis. sumber data berubah / ada brand lain kena pola sama)."""
    import re as _re
    filler = _re.compile(r"\b(all new|new|facelift)\b", _re.I)

    def core(merk, s):
        s2 = filler.sub("", s)
        s2 = _re.sub(r"\s+", " ", s2).strip()
        parts = [p.strip() for p in _re.split(r"\s*/\s*", s2) if p.strip()]
        fixed = [p if p.lower().startswith(merk.lower()) else f"{merk} {p}" for p in parts]
        return tuple(sorted(dict.fromkeys(p.lower() for p in fixed)))

    wb = openpyxl.load_workbook(WB)
    galat = []
    for nama in wb.sheetnames:
        if nama == "CATATAN":
            continue
        ws = wb[nama]
        grup = {}
        for baris in range(2, ws.max_row + 1):
            v = ws.cell(baris, 1).value
            if v is None:
                continue
            k = core(nama, v)
            if k in grup:
                galat.append(f"{nama}: {grup[k]!r} & {v!r} kemungkinan model yang sama")
            grup[k] = v
    if galat:
        raise AssertionError("kemungkinan duplikat model:\n  " + "\n  ".join(galat))


def main():
    cek_tidak_ada_duplikat_generasi()
    cek_catatan_tanpa_formula()
    wb = openpyxl.load_workbook(WB)
    sheets = [s for s in wb.sheetnames if s != "CATATAN"]
    print(f"sheet merk: {len(sheets)}")

    total_baris = n_harga = 0
    galat = []

    for nama in sheets:
        ws = wb[nama]
        for baris in range(2, ws.max_row + 1):
            if ws.cell(baris, 1).value is None:
                continue
            total_baris += 1
            n = hitung_baris(ws, baris)

            # skenario A: C kosong
            for kol in ("D", "G", "Y", "Z", "AC"):
                if n[kol] != KOSONG:
                    galat.append(f"{nama}!{kol}{baris} harusnya kosong, dapat {n[kol]!r}")

            j = ws.cell(baris, KOLOM.index("J") + 1).value
            if j is not None:
                n_harga += 1
                if not isinstance(j, int) or not (99 <= j <= 10_000_000):
                    galat.append(f"{nama}!J{baris} harga janggal: {j!r}")
                # potongan biaya harus 33,45% dari harga jual (10,45+5,5+4,5+2,5+5+5,5 = 33,45)
                harap = round(j * 0.3345, 6)
                if round(n["W"], 6) != harap:
                    galat.append(f"{nama}!W{baris} = {n['W']}, harusnya {harap}")
                if round(n["X"], 6) != round(j - harap, 6):
                    galat.append(f"{nama}!X{baris} salah: {n['X']}")
                if round(n["AB"], 6) != round(j * 1.1, 6):
                    galat.append(f"{nama}!AB{baris} salah: {n['AB']}")
            else:
                for kol in ("L", "N", "P", "R", "T", "V", "W", "X", "AA", "AB"):
                    if n[kol] != 0:
                        galat.append(f"{nama}!{kol}{baris} harusnya 0 saat J kosong, dapat {n[kol]}")

    # skenario B: uji silang dengan baris 'Avanza Reguler' Sheet3 (C=5, J=295000)
    ws = wb["Toyota"]
    baris_avanza = next(b for b in range(2, ws.max_row + 1)
                        if ws.cell(b, 1).value == "Toyota Avanza")
    j_asli = ws.cell(baris_avanza, KOLOM.index("J") + 1).value
    ws.cell(baris_avanza, KOLOM.index("J") + 1).value = 295000
    uji = hitung_baris(ws, baris_avanza, isi_c=5)
    ws.cell(baris_avanza, KOLOM.index("J") + 1).value = j_asli
    for kol, harap in SHEET3_AVANZA.items():
        if round(uji[kol], 6) != harap:
            galat.append(f"uji-silang Sheet3: {kol} = {uji[kol]}, harusnya {harap}")

    print(f"total baris model : {total_baris}")
    print(f"baris ada harga J : {n_harga}")
    print(f"uji silang Sheet3 : {'COCOK' if not any(g.startswith('uji-silang') for g in galat) else 'GAGAL'}"
          f" (C=5, J=295000 -> HPP {uji['G']:.0f}, Cair MP {uji['X']:.1f}, Margin Bersih {uji['AC']:.1f})")
    if galat:
        print(f"\nGALAT: {len(galat)}")
        for g in galat[:40]:
            print("  ", g)
        sys.exit(1)
    print("\nOK - tidak ada #DIV/0!, semua formula konsisten.")


if __name__ == "__main__":
    main()
