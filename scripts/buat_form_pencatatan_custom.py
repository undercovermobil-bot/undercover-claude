#!/usr/bin/env python3
"""
Membuat Google Sheet (xlsx) untuk FORM PESANAN CUSTOM (web app Apps Script).

Revisi user 2026-09-25 (ke-3): admin mengisi lewat halaman form bergaya website
(`form-pesanan-custom/Index.html` + `Code.gs`), cuma 3 kolom: Merek -> Model ->
Generasi/Tahun. Tanpa tanggal/no. pesanan (waktu dicatat otomatis). Hasil masuk ke
sheet "Rekap Pesanan". Model yang diketik manual (tidak ada di master) otomatis
ditambahkan ke "Daftar Mobil" sehingga muncul di dropdown berikutnya.

Workbook ini hanya menyiapkan data awal:
  - "Daftar Mobil"  : Merek | Model | Generasi / Tahun | Sumber | Ditambahkan  (dari master)
  - "Rekap Pesanan" : header saja (diisi web app)
  - "Ringkasan"     : dibuat oleh fungsi `siapkan` di Code.gs (rumus QUERY Google Sheets)

Sumber generasi/tahun: baris toko Undercover Autocare di master (link custom = toko
Undercover); kalau model tak punya baris UA, pakai toko lain. Kalau 1 generasi punya
>1 rentang tahun di toko yang sama, dipakai yang paling sering muncul.

Pemakaian:
  python3 buat_form_pencatatan_custom.py MASTER.xlsx OUT.xlsx
"""
import re
import sys
from collections import Counter, OrderedDict, defaultdict

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

URUTAN_TOKO = ["Undercover Autocare", "Otonation", "Smartprotection", "Otoprotection"]

FONT_HDR = Font(name="Arial", size=11, bold=True, color="FFFFFF")
FILL_HDR = PatternFill("solid", fgColor="1F4E78")


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


def header(ws, kolom):
    for i, (h, w) in enumerate(kolom, start=1):
        c = ws.cell(row=1, column=i, value=h)
        c.font, c.fill = FONT_HDR, FILL_HDR
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    ws.freeze_panes = "A2"


def buat(master_path, out_path):
    daftar, lap = baca_master(master_path)
    wb = openpyxl.Workbook()

    wd = wb.active
    wd.title = "Daftar Mobil"
    header(wd, [("Merek", 22), ("Model", 30), ("Generasi / Tahun", 26), ("Sumber", 10),
                ("Ditambahkan", 18)])
    r = 2
    for merek, models in daftar.items():
        for model, gens in models.items():
            for g in gens:
                for c, v in enumerate((merek, model, g, "Master"), start=1):
                    cell = wd.cell(row=r, column=c, value=v)
                    cell.number_format = "@"   # "5" (MG 5) / "2015-2020" tetap teks
                r += 1
    wd.auto_filter.ref = f"A1:E{r - 1}"

    wr = wb.create_sheet("Rekap Pesanan")
    header(wr, [("Waktu", 18), ("Merek", 22), ("Model", 30), ("Generasi / Tahun", 26),
                ("Model Baru?", 12)])

    wb.save(out_path)
    print(f"{len(daftar)} merek, {sum(len(m) for m in daftar.values())} model, {r - 2} baris generasi")
    print(f"model tanpa baris UA (pakai toko lain): {len(lap['sumber_non_ua'])}")
    print(f"generasi dgn >1 rentang tahun di toko sumber: {len(lap['tahun_ganda'])}")
    print(f"nama pendek bentrok: {lap['nama_bentrok']}")
    print("tersimpan:", out_path)
    return daftar, lap


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    buat(sys.argv[1], sys.argv[2])
