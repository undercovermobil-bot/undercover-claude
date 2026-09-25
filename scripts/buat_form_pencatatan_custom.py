#!/usr/bin/env python3
"""
Form pencatatan pesanan LINK CUSTOM (model di luar Top 100) untuk admin.

Versi ringkas (revisi user 2026-09-25): admin cukup pilih 3 dropdown bertingkat
  Merek  ->  Model (hanya model merek itu)  ->  Generasi / Tahun (hanya generasi model itu)
ditambah Tanggal, No. Pesanan, Catatan. Tidak ada SKU/kategori/warna.

Sheet:
  - "Input"     : tempat admin mengisi (N_BARIS baris siap pakai).
  - "Rekap"     : jumlah pesanan per model (COUNTIFS).
  - "Cara Pakai"
  - "Data", "Bantu" (tersembunyi): daftar dari master + daftar dropdown per baris.

Kenapa dropdown bertingkat dibuat dengan sheet "Bantu" (1 baris bantu per baris
input) dan bukan INDIRECT/OFFSET: validasi dropdown Google Sheets hanya menerima
range biasa, bukan rumus. Range per baris jalan sama di Excel dan Google Sheets.
Rumus hanya INDEX/MATCH/COUNTIF/COUNTIFS (jalan di Excel lama & Google Sheets).

Sumber generasi/tahun: baris toko Undercover Autocare di master (link custom = toko
Undercover). Kalau model tidak punya baris UA, pakai toko lain. Kalau 1 generasi
punya >1 rentang tahun di toko yang sama, dipakai yang paling sering muncul.

Pemakaian:
  python3 buat_form_pencatatan_custom.py MASTER.xlsx OUT.xlsx
"""
import re
import sys
from collections import Counter, OrderedDict, defaultdict

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

N_BARIS = 2000
URUTAN_TOKO = ["Undercover Autocare", "Otonation", "Smartprotection", "Otoprotection"]

FONT = Font(name="Arial", size=11)
FONT_HDR = Font(name="Arial", size=11, bold=True, color="FFFFFF")
FILL_HDR = PatternFill("solid", fgColor="1F4E78")
FILL_PILIH = PatternFill("solid", fgColor="FFF9E6")   # kolom dropdown
FILL_BAND = PatternFill("solid", fgColor="F2F6FA")
FILL_SALAH = PatternFill("solid", fgColor="F8CBAD")
GARIS = Side(style="thin", color="D0D7DE")
BORDER = Border(left=GARIS, right=GARIS, top=GARIS, bottom=GARIS)


def bersih(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def tahun(v):
    return re.sub(r"\s*-\s*", "-", bersih(v))


def nama_pendek(merek, model):
    """'Toyota Avanza' -> 'Avanza'; 'Mercedes Benz E Class' (sheet Mercedes-Benz) -> 'E Class'.

    Buang awalan merek (termasuk typo merek dobel 'Mitsubishi Mitsubishi Kuda').
    Kalau sisanya kosong / bukan awalan merek (mis. 'Range Rover' di Land Rover), biarkan.
    """
    kandidat = {re.sub(r"\s*\(.*?\)", "", merek).replace("-", " ").lower(),
                merek.split()[0].replace("-", " ").lower()}
    s = model
    ubah = True
    while ubah:
        ubah = False
        for k in sorted(kandidat, key=len, reverse=True):
            if s.lower().startswith(k + " ") and len(s) > len(k) + 1:
                s = s[len(k) + 1:].strip()
                ubah = True
    return s


def baca_master(path):
    """Return OrderedDict merek -> OrderedDict model_pendek -> [label generasi]."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    # (merek, model) -> toko -> gen -> Counter(tahun); urutan generasi ikut master
    data = OrderedDict()
    for ws in wb.worksheets:
        for r in ws.iter_rows(min_row=3, values_only=True):
            if len(r) < 7 or not r[1] or not r[5]:
                continue
            key = (ws.title, bersih(r[1]))
            d = data.setdefault(key, defaultdict(OrderedDict))
            d[bersih(r[2])].setdefault(bersih(r[5]), Counter())[tahun(r[6])] += 1
    wb.close()

    hasil = OrderedDict()
    laporan = {"tahun_ganda": [], "sumber_non_ua": [], "nama_bentrok": []}
    for (merek, model), per_toko in data.items():
        toko = next((t for t in URUTAN_TOKO if t in per_toko), next(iter(per_toko)))
        if toko != URUTAN_TOKO[0]:
            laporan["sumber_non_ua"].append((model, toko))
        labels = []
        for gen, cnt in per_toko[toko].items():
            isi = [(t, n) for t, n in cnt.most_common() if t]
            if len(isi) > 1:
                laporan["tahun_ganda"].append((model, gen, dict(cnt)))
            th = isi[0][0] if isi else ""
            labels.append(f"{gen} ({th})" if th else gen)
        pendek = nama_pendek(merek, model)
        m = hasil.setdefault(merek, OrderedDict())
        if pendek in m:
            laporan["nama_bentrok"].append((merek, pendek, model))
            pendek = model
        m[pendek] = labels
    hasil = OrderedDict(sorted(hasil.items(), key=lambda kv: kv[0].lower()))
    for merek in hasil:
        hasil[merek] = OrderedDict(sorted(hasil[merek].items(), key=lambda kv: kv[0].lower()))
    return hasil, laporan


def buat(master_path, out_path):
    daftar, lap = baca_master(master_path)
    n_merek = len(daftar)
    maks_model = max(len(m) for m in daftar.values())
    maks_gen = max(len(g) for m in daftar.values() for g in m.values())

    wb = openpyxl.Workbook()
    wi = wb.active
    wi.title = "Input"
    wr = wb.create_sheet("Rekap")
    wc = wb.create_sheet("Cara Pakai")
    wd = wb.create_sheet("Data")
    wbnt = wb.create_sheet("Bantu")

    # ---------- Data (tersembunyi) ----------
    # A: Merek list | C: Merek, D: Model (urut per merek) | F: Kunci merek|model, G: Generasi
    wd["A1"], wd["C1"], wd["D1"], wd["F1"], wd["G1"] = "Merek", "Merek", "Model", "Kunci", "Generasi"
    rm = rg = 2
    for i, merek in enumerate(daftar, start=2):
        wd.cell(row=i, column=1, value=merek)
        for model, gens in daftar[merek].items():
            wd.cell(row=rm, column=3, value=merek)
            wd.cell(row=rm, column=4, value=model)
            rm += 1
            for g in gens:
                wd.cell(row=rg, column=6, value=f"{merek}|{model}")
                wd.cell(row=rg, column=7, value=g)
                rg += 1
    last_m, last_g = rm - 1, rg - 1
    R_MEREK = f"Data!$A$2:$A${n_merek + 1}"
    R_MM, R_MODEL = f"Data!$C$2:$C${last_m}", f"Data!$D$2:$D${last_m}"
    R_KUNCI, R_GEN = f"Data!$F$2:$F${last_g}", f"Data!$G$2:$G${last_g}"

    # ---------- Bantu (tersembunyi): 1 baris per baris Input ----------
    # A: awal model, B: jumlah model, C..: daftar model | lalu awal gen, jumlah gen, daftar gen
    c_m0 = 3
    c_ga = c_m0 + maks_model
    c_gn = c_ga + 1
    c_g0 = c_ga + 2
    for r in range(2, N_BARIS + 2):
        wbnt[f"A{r}"] = f'=IF(Input!$C{r}="","",MATCH(Input!$C{r},{R_MM},0))'
        wbnt[f"B{r}"] = f'=IF(Input!$C{r}="",0,COUNTIF({R_MM},Input!$C{r}))'
        for k in range(1, maks_model + 1):
            wbnt.cell(row=r, column=c_m0 + k - 1,
                      value=f'=IF({k}>$B{r},"",INDEX({R_MODEL},$A{r}+{k - 1}))')
        kunci = f'Input!$C{r}&"|"&Input!$D{r}'
        wbnt.cell(row=r, column=c_ga,
                  value=f'=IF(Input!$D{r}="","",IFERROR(MATCH({kunci},{R_KUNCI},0),""))')
        wbnt.cell(row=r, column=c_gn,
                  value=f'=IF(Input!$D{r}="",0,COUNTIF({R_KUNCI},{kunci}))')
        for k in range(1, maks_gen + 1):
            wbnt.cell(row=r, column=c_g0 + k - 1,
                      value=f'=IF({k}>${L(c_gn)}{r},"",INDEX({R_GEN},${L(c_ga)}{r}+{k - 1}))')
    # ---------- Input ----------
    kolom = [("Tanggal", 12), ("No. Pesanan", 22), ("Merek ▼", 18), ("Model ▼", 26),
             ("Generasi / Tahun ▼", 26), ("Catatan", 34)]
    for i, (h, w) in enumerate(kolom, start=1):
        c = wi.cell(row=1, column=i, value=h)
        c.font, c.fill, c.border = FONT_HDR, FILL_HDR, BORDER
        c.alignment = Alignment(horizontal="center", vertical="center")
        wi.column_dimensions[L(i)].width = w
    wi.row_dimensions[1].height = 26
    wi.freeze_panes = "A2"
    wi.sheet_view.zoomScale = 110
    # G, H tersembunyi: 1 = pilihan Model / Generasi tidak cocok (mis. Merek diganti setelahnya)
    wi["G1"], wi["H1"] = "cek model", "cek gen"
    wi.column_dimensions["G"].hidden = True
    wi.column_dimensions["H"].hidden = True

    for r in range(2, N_BARIS + 2):
        for c in range(1, 7):
            cell = wi.cell(row=r, column=c)
            cell.font, cell.border = FONT, BORDER
            cell.alignment = Alignment(vertical="center")
            if c in (3, 4, 5):
                cell.fill = FILL_PILIH
        wi[f"A{r}"].number_format = "dd/mm/yyyy"
        wi[f"B{r}"].number_format = "@"
        wi[f"G{r}"] = (f'=IF($D{r}="",0,IF(COUNTIF(Bantu!${L(c_m0)}${r}:${L(c_ga - 1)}${r},$D{r})=0,1,0))')
        wi[f"H{r}"] = (f'=IF($E{r}="",0,IF(COUNTIF(Bantu!${L(c_g0)}${r}:'
                       f'${L(c_g0 + maks_gen - 1)}${r},$E{r})=0,1,0))')

        dv_m = DataValidation(type="list", allow_blank=True,
                              formula1=f"Bantu!${L(c_m0)}${r}:${L(c_ga - 1)}${r}")
        dv_g = DataValidation(type="list", allow_blank=True,
                              formula1=f"Bantu!${L(c_g0)}${r}:${L(c_g0 + maks_gen - 1)}${r}")
        for dv, col in ((dv_m, "D"), (dv_g, "E")):
            dv.error, dv.errorTitle = "Pilih dari dropdown. Isi Merek dulu.", "Tidak ada di daftar"
            wi.add_data_validation(dv)
            dv.add(f"{col}{r}")

    last = N_BARIS + 1
    dv_merek = DataValidation(type="list", formula1=R_MEREK, allow_blank=True)
    dv_merek.error, dv_merek.errorTitle = "Pilih merek dari dropdown.", "Tidak ada di daftar"
    wi.add_data_validation(dv_merek)
    dv_merek.add(f"C2:C{last}")
    dv_tgl = DataValidation(type="date", operator="greaterThan", formula1="DATE(2026,1,1)",
                            allow_blank=True)
    dv_tgl.error = "Isi tanggal, contoh 25/09/2026."
    wi.add_data_validation(dv_tgl)
    dv_tgl.add(f"A2:A{last}")

    wi.conditional_formatting.add(f"D2:D{last}", FormulaRule(formula=["$G2=1"], fill=FILL_SALAH))
    wi.conditional_formatting.add(f"E2:E{last}", FormulaRule(formula=["$H2=1"], fill=FILL_SALAH))
    wi.conditional_formatting.add(f"A2:B{last}", FormulaRule(formula=["ISEVEN(ROW())"], fill=FILL_BAND))
    wi.conditional_formatting.add(f"F2:F{last}", FormulaRule(formula=["ISEVEN(ROW())"], fill=FILL_BAND))
    wi.auto_filter.ref = f"A1:F{last}"

    # ---------- Rekap ----------
    for i, (h, w) in enumerate([("Merek", 20), ("Model", 30), ("Jumlah Pesanan", 16)], start=1):
        c = wr.cell(row=1, column=i, value=h)
        c.font, c.fill, c.border = FONT_HDR, FILL_HDR, BORDER
        c.alignment = Alignment(horizontal="center")
        wr.column_dimensions[L(i)].width = w
    r = 2
    for merek, models in daftar.items():
        for model in models:
            wr.cell(row=r, column=1, value=merek).font = FONT
            wr.cell(row=r, column=2, value=model).font = FONT
            wr.cell(row=r, column=3, value=(f'=COUNTIFS(Input!$C$2:$C${last},$A{r},'
                                            f'Input!$D$2:$D${last},$B{r})')).font = FONT
            r += 1
    wr.freeze_panes = "A2"
    wr.auto_filter.ref = f"A1:C{r - 1}"
    wr.conditional_formatting.add(f"C2:C{r - 1}", FormulaRule(formula=["$C2>0"],
                                  fill=PatternFill("solid", fgColor="C6EFCE")))

    # ---------- Cara Pakai ----------
    wc.column_dimensions["A"].width = 90
    teks = [
        ("CARA MENCATAT PESANAN CUSTOM", True),
        ("1. Isi Tanggal dan No. Pesanan.", False),
        ("2. Pilih Merek (dropdown), lalu Model, lalu Generasi / Tahun. Isi berurutan dari kiri.", False),
        ("3. Model & Generasi hanya muncul setelah kolom sebelumnya diisi.", False),
        ("4. Kolom merah = pilihan tidak cocok (biasanya Merek diganti setelah Model dipilih). Pilih ulang.", False),
        ("5. Catatan bebas: warna, jumlah, permintaan khusus, dll.", False),
        ("6. Sheet 'Rekap' = jumlah pesanan per model (filter kolom Jumlah untuk lihat yang terisi).", False),
        ("", False),
        (f"Sumber daftar: master SKU ({n_merek} merek, {sum(len(m) for m in daftar.values())} model). "
         "Jangan ubah sheet tersembunyi 'Data' dan 'Bantu'.", False),
    ]
    for i, (t, b) in enumerate(teks, start=1):
        c = wc.cell(row=i, column=1, value=t)
        c.font = Font(name="Arial", size=13 if b else 11, bold=b)

    wd.sheet_state = "hidden"
    wbnt.sheet_state = "hidden"
    wb.active = 0
    wb.save(out_path)

    print(f"{n_merek} merek, {sum(len(m) for m in daftar.values())} model, "
          f"{last_g - 1} generasi | maks model/merek {maks_model}, maks gen/model {maks_gen}")
    print(f"model tanpa baris UA (pakai toko lain): {len(lap['sumber_non_ua'])}")
    print(f"generasi dgn >1 rentang tahun di toko sumber: {len(lap['tahun_ganda'])}")
    for x in lap["tahun_ganda"][:15]:
        print("   ", x)
    print(f"nama pendek bentrok: {lap['nama_bentrok']}")
    print("tersimpan:", out_path)
    return daftar, lap


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    buat(sys.argv[1], sys.argv[2])
