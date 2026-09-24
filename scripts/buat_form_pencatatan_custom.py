#!/usr/bin/env python3
"""
Membuat workbook "Form Pencatatan Pesanan Custom" untuk admin/operasional.

Konteks (2026-09-24): user merampingkan listing Undercover — model di luar 100
terlaris dijual lewat LINK CUSTOM (pembeli diskusi varian dengan admin dulu).
Admin perlu mencatat mobil apa yang dibeli. Workbook ini:

  - Sheet "Input Pesanan"  : tempat admin mencatat. Kolom Mobil pakai 1 dropdown
                             gabungan "Model | Generasi | Tahun" (bisa diketik
                             untuk mencari di Google Sheets / Excel 365).
                             Merek, Model, Generasi, Tahun, SKU Gudang terisi
                             otomatis. Kolom Cek memberi peringatan kalau
                             kombinasi Kategori/Warna tidak ada di master.
  - Sheet "Rekap per Model": total qty custom per model (SUMIFS), plus status
                             Top 100 / Custom.
  - Sheet "Daftar Mobil"   : sumber dropdown (dari master).
  - Sheet "Master SKU"     : tabel kunci -> SKU (dari master).
  - Sheet "Pengaturan"     : daftar Admin/Toko/Marketplace/Status (bisa diedit).
  - Sheet "Cara Pakai"

Aturan bisnis yang dipakai (lihat claude-memory/project-undercover-sku-sync-rules.md):
  - Konsolidasi toko: OT pakai SKU UA, OP pakai SKU SP (aturan #1).
  - Tier Strip: Strip 1 = Epic, Strip 2 = Elite, Strip 3 = Warrior
    (dikonfirmasi user utk OT, diverifikasi ulang dari SKU existing SP 07-15;
    lihat project-undercover-smartprotection-status.md). Grup UA menyimpan
    warna Strip sbg Elite/Epic/Warrior, grup SP sbg Strip 1/2/3 — rumus Kunci
    menormalkan dua arah, jadi admin boleh pilih ejaan mana pun.

Semua rumus hanya INDEX/MATCH/COUNTIFS/SUMIFS/SUBSTITUTE/IFERROR supaya jalan
sama di Excel lama, Excel 365, dan Google Sheets (tanpa XLOOKUP/FILTER).

Pemakaian:
  python3 buat_form_pencatatan_custom.py MASTER.xlsx RANKING_BIGSELLER.xlsx OUT.xlsx [label_versi_master]
"""
import re
import sys
from collections import OrderedDict

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

N_BARIS_INPUT = 3000
TOP_N = 100

TOKO_GRUP = OrderedDict([
    ("Undercover Autocare", "UA"),
    ("Otonation", "UA"),
    ("Smartprotection", "SP"),
    ("Otoprotection", "SP"),
])
TOKO_SUMBER_MASTER = {"UA": "Undercover Autocare", "SP": "Smartprotection"}

KATEGORI = ["Reguler", "Premium", "Exclusive", "Strip", "Transparan"]
WARNA = [
    "Abu-abu", "Hitam", "Merah", "Biru Benhur", "Hijau Army", "Biru", "Hijau",
    "Orange", "Silver", "Transparan",
    "Epic Abu", "Epic Biru", "Epic Merah",
    "Elite Abu", "Elite Biru", "Elite Merah",
    "Warrior Abu", "Warrior Biru", "Warrior Merah",
    "Strip 1 Abu", "Strip 1 Biru", "Strip 1 Merah",
    "Strip 2 Abu", "Strip 2 Biru", "Strip 2 Merah",
    "Strip 3 Abu", "Strip 3 Biru", "Strip 3 Merah",
]
MARKETPLACE = ["Shopee", "TikTok", "Tokopedia", "Lazada", "WhatsApp", "Lainnya"]
STATUS = ["Baru", "Diproses", "Dikirim", "Selesai", "Batal", "Retur"]
ADMIN_CONTOH = ["Admin 1", "Admin 2", "Admin 3"]

# Nama di ranking BigSeller (dari judul listing) != nama master, model FISIK sama.
# Diambil dari RESOLUSI_MANUAL hpp-per-merk-scripts/build_top100_terlaris.py
# (sudah diverifikasi rentang tahun/generasi di sesi 2026-08) + ejaan master 07-03.
ALIAS_RANKING = {
    "Honda Brio": "Honda Brio Satya / RS",
    "Honda HRV": "Honda HR-V / e:N1",
    "Honda BRV": "Honda BR-V",
    "Honda CRV": "Honda CR-V",
    "Honda WRV": "Honda WR-V",
    "Nissan Grand Livina": "Nissan Livina / Grand Livina",
    "Mitsubishi Kuda": "Mitsubishi Mitsubishi Kuda",
    "Mitsubishi Xpander Cross": "Mitsubishi Mitsubishi Xpander Cross",
    "Mitsubishi Destinator": "Mitsubishi Mitsubishi Destinator",
    "Honda City Hatchback": "Honda City Hatchback RS",
    "Suzuki Carry Pickup": "Suzuki Carry",
    "Daihatsu Gran Max PU": "Daihatsu Gran Max Pick Up",
    "Mitsubishi Strada Triton": "Mitsubishi Triton",
    "Suzuki APV Arena": "Suzuki APV Arena / Blind Van",
    "Suzuki APV": "Suzuki APV Arena / Blind Van",
    "Honda City": "Honda City Sedan",
    "Mazda 2": "Mazda 2 Sedan",
    "Kia Rio": "Kia Rio Sedan",
    "Mitsubishi Pajero": "Mitsubishi Pajero Sport",
    "Nissan XTrail": "Nissan X-Trail",
    "Daihatsu Gran Max MB": "Daihatsu Gran Max Minibus / Blind Van",
    "Daihatsu Gran Max": "Daihatsu Gran Max Minibus / Blind Van",
    "Daihatsu Gran Max Minibus": "Daihatsu Gran Max Minibus / Blind Van",
    "Toyota Hardtop / Land Cruiser": "Toyota Land Cruiser",
    "Mazda CX-5": "Mazda CX5",
    "Isuzu MU-X": "Isuzu Mux",
    "Nissan Kicks": "Nissan Kicks e-POWER",
    "Daihatsu Terios": "Daihatsu Terios / New Terios",
}

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")
AUTO_FILL = PatternFill("solid", fgColor="EDEDED")
INPUT_FILL = PatternFill("solid", fgColor="FFFFFF")
WARN_FILL = PatternFill("solid", fgColor="F8CBAD")
OK_FILL = PatternFill("solid", fgColor="C6EFCE")
TIPIS = Side(style="thin", color="BFBFBF")
BORDER = Border(left=TIPIS, right=TIPIS, top=TIPIS, bottom=TIPIS)


def norm(s):
    # "Mitsubishi Mitsubishi Outlander" (typo merek dobel di master) == "Mitsubishi Outlander"
    s = re.sub(r"^(\w+) \1 ", r"\1 ", str(s).strip(), flags=re.I)
    return re.sub(r"[^a-z0-9]", "", s.lower())


def bersih(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def baca_master(path):
    """Kembalikan (daftar_label, sku_by_key, bentrok).

    daftar_label: OrderedDict label -> dict(merek, model, gen, tahun)
    sku_by_key  : {"UA|label|Kategori|Warna": SKU}
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    # Kunci pilihan = (model, generasi, rentang tahun), bukan (model, generasi) saja:
    # master 07-03 punya label generasi sama utk 2 rentang tahun beda SKU
    # (Toyota GR 86 "Gen 2" = 2012-2020 -> G1 DAN 2021-2026 -> G2).
    label_by_mg = OrderedDict()   # (model, gen, tahun) -> dict
    baris = []
    for ws in wb.worksheets:
        merek = ws.title
        for r in ws.iter_rows(min_row=3, values_only=True):
            if len(r) < 9 or not r[1] or not r[8]:
                continue
            model, toko, kat, warna, gen, tahun, sku = (
                bersih(r[1]), bersih(r[2]), bersih(r[3]), bersih(r[4]),
                bersih(r[5]), bersih(r[6]), bersih(r[8]))
            mg = (model, gen, tahun)
            if mg not in label_by_mg:
                label_by_mg[mg] = {"merek": merek, "model": model, "gen": gen, "tahun": tahun}
            baris.append((mg, toko, kat, warna, sku))
    wb.close()

    daftar = OrderedDict()
    label_of = {}
    for mg, d in label_by_mg.items():
        label = f"{d['model']} | {d['gen']}" + (f" | {d['tahun']}" if d["tahun"] else "")
        daftar[label] = d
        label_of[mg] = label

    sku_by_key = {}
    bentrok = []
    for mg, toko, kat, warna, sku in baris:
        for grup, sumber in TOKO_SUMBER_MASTER.items():
            if toko != sumber:
                continue
            key = f"{grup}|{label_of[mg]}|{kat}|{warna}"
            if key in sku_by_key and sku_by_key[key] != sku:
                bentrok.append((key, sku_by_key[key], sku))
                continue
            sku_by_key.setdefault(key, sku)
    return daftar, sku_by_key, bentrok


def baca_top(path, model_master):
    """Top N model mobil dari 'MOBIL TERLARIS BIGSELLER.xlsx' sheet pertama.

    Baris non-mobil (Headlamp Restorer, Glass Polish, dst) dilewati.
    Return (top_models_master:set, tak_cocok:list[(rank, nama)], ranking:list).
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    ranking = []
    for r in ws.iter_rows(values_only=True):
        if r and isinstance(r[0], (int, float)) and r[1]:
            nama = bersih(r[1])
            if " - " in nama or "Undercover Autocare" in nama:
                continue  # produk non-mobil
            ranking.append((int(r[0]), nama, r[2]))
    wb.close()
    idx = {norm(m): m for m in model_master}
    top, tak_cocok = set(), []
    for rank, nama, _ in ranking[:TOP_N]:
        target = ALIAS_RANKING.get(nama, nama)
        m = idx.get(norm(target)) or idx.get(norm(nama))
        if m:
            top.add(m)
        else:
            tak_cocok.append((rank, nama))
    return top, tak_cocok, ranking


def gaya_header(ws, headers, widths):
    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=1, column=i, value=h)
        c.fill, c.font, c.border = HEADER_FILL, HEADER_FONT, BORDER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "A2"


def tulis_list(ws, col, judul, items):
    ws.cell(row=1, column=col, value=judul)
    for i, v in enumerate(items, start=2):
        ws.cell(row=i, column=col, value=v)
    return f"Pengaturan!${get_column_letter(col)}$2:${get_column_letter(col)}${len(items) + 1 + 20}"


def buat(master_path, ranking_path, out_path, versi_master):
    daftar, sku_by_key, bentrok = baca_master(master_path)
    model_master = list(OrderedDict.fromkeys(d["model"] for d in daftar.values()))
    top, tak_cocok, ranking = baca_top(ranking_path, model_master)

    wb = openpyxl.Workbook()

    # ---------------- Input Pesanan ----------------
    ws = wb.active
    ws.title = "Input Pesanan"
    kolom = [
        # (header, lebar, jenis) jenis: in = diisi admin, auto = rumus
        ("Tanggal", 12, "in"),                      # A
        ("Admin", 12, "in"),                        # B
        ("Toko", 20, "in"),                         # C
        ("Marketplace", 12, "in"),                  # D
        ("No. Pesanan", 22, "in"),                  # E
        ("Username / Nama Pembeli", 22, "in"),      # F
        ("Mobil (Model | Generasi | Tahun)\nketik utk cari", 46, "in"),  # G
        ("Tahun Mobil Pembeli", 11, "in"),          # H
        ("Kategori", 12, "in"),                     # I
        ("Warna", 15, "in"),                        # J
        ("Qty", 6, "in"),                           # K
        ("Harga Jual / pcs (Rp)", 14, "in"),        # L
        ("Status", 11, "in"),                       # M
        ("Catatan", 28, "in"),                      # N
        ("Merek", 16, "auto"),                      # O
        ("Model", 26, "auto"),                      # P
        ("Generasi", 12, "auto"),                   # Q
        ("Rentang Tahun", 14, "auto"),              # R
        ("SKU Gudang", 26, "auto"),                 # S
        ("Status Model", 12, "auto"),               # T
        ("Cek", 30, "auto"),                        # U
        ("Kunci (sistem)", 10, "auto"),             # V
        ("Subtotal (sistem)", 10, "auto"),          # W
    ]
    gaya_header(ws, [k[0] for k in kolom], [k[1] for k in kolom])
    for i, k in enumerate(kolom, start=1):
        if k[2] == "auto":
            ws.cell(row=1, column=i).fill = PatternFill("solid", fgColor="595959")
    ws.column_dimensions["V"].hidden = True
    ws.column_dimensions["W"].hidden = True
    ws.auto_filter.ref = f"A1:U{N_BARIS_INPUT + 1}"

    n_daftar = len(daftar)
    D_LABEL = f"'Daftar Mobil'!$A$2:$A${n_daftar + 1}"
    def D(col):
        return f"'Daftar Mobil'!${col}$2:${col}${n_daftar + 1}"
    n_sku = len(sku_by_key)
    M_KEY = f"'Master SKU'!$A$2:$A${n_sku + 1}"
    M_SKU = f"'Master SKU'!$B$2:$B${n_sku + 1}"

    for r in range(2, N_BARIS_INPUT + 2):
        m = f"MATCH($G{r},{D_LABEL},0)"
        ws[f"O{r}"] = f'=IF($G{r}="","",IFERROR(INDEX({D("B")},{m}),""))'
        ws[f"P{r}"] = f'=IF($G{r}="","",IFERROR(INDEX({D("C")},{m}),""))'
        ws[f"Q{r}"] = f'=IF($G{r}="","",IFERROR(INDEX({D("D")},{m}),""))'
        ws[f"R{r}"] = f'=IF($G{r}="","",IFERROR(INDEX({D("E")},{m}),""))'
        ws[f"T{r}"] = f'=IF($G{r}="","",IFERROR(INDEX({D("F")},{m}),""))'
        # Grup SKU: UA/OT -> UA, SP/OP -> SP. Warna Strip dinormalkan per grup.
        grup = f'IF(OR($C{r}="Smartprotection",$C{r}="Otoprotection"),"SP","UA")'
        w_ke_sp = (f'SUBSTITUTE(SUBSTITUTE(SUBSTITUTE($J{r},"Epic","Strip 1"),'
                   f'"Elite","Strip 2"),"Warrior","Strip 3")')
        w_ke_ua = (f'SUBSTITUTE(SUBSTITUTE(SUBSTITUTE($J{r},"Strip 1","Epic"),'
                   f'"Strip 2","Elite"),"Strip 3","Warrior")')
        ws[f"V{r}"] = (f'=IF(OR($G{r}="",$I{r}="",$J{r}=""),"",{grup}&"|"&$G{r}&"|"&$I{r}&"|"&'
                       f'IF({grup}="SP",{w_ke_sp},{w_ke_ua}))')
        ws[f"S{r}"] = f'=IF($V{r}="","",IFERROR(INDEX({M_SKU},MATCH($V{r},{M_KEY},0)),""))'
        ws[f"W{r}"] = f'=IF(AND(ISNUMBER($K{r}),ISNUMBER($L{r})),$K{r}*$L{r},0)'
        ws[f"U{r}"] = (
            f'=IF(COUNTA($A{r}:$N{r})=0,"",'
            f'IF($C{r}="","Isi Toko",'
            f'IF($G{r}="","Isi Mobil",'
            f'IF($O{r}="","Mobil tidak ada di daftar",'
            f'IF(OR($I{r}="",$J{r}=""),"Isi Kategori & Warna",'
            f'IF($S{r}="","Kombinasi tdk ada di master - cek",'
            f'IF($K{r}="","Isi Qty","OK")))))))'
        )
        for c in range(1, len(kolom) + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORDER
            if kolom[c - 1][2] == "auto":
                cell.fill = AUTO_FILL
        ws[f"A{r}"].number_format = "dd/mm/yyyy"
        ws[f"L{r}"].number_format = "#,##0"

    ws.conditional_formatting.add(
        f"U2:U{N_BARIS_INPUT + 1}",
        FormulaRule(formula=['AND($U2<>"",$U2<>"OK")'], fill=WARN_FILL))
    ws.conditional_formatting.add(
        f"U2:U{N_BARIS_INPUT + 1}", FormulaRule(formula=['$U2="OK"'], fill=OK_FILL))

    # ---------------- Pengaturan ----------------
    wp = wb.create_sheet("Pengaturan")
    ref_toko = tulis_list(wp, 1, "Toko", list(TOKO_GRUP))
    ref_mp = tulis_list(wp, 2, "Marketplace", MARKETPLACE)
    ref_admin = tulis_list(wp, 3, "Admin (edit nama di sini)", ADMIN_CONTOH)
    ref_status = tulis_list(wp, 4, "Status", STATUS)
    ref_kat = tulis_list(wp, 5, "Kategori", KATEGORI)
    ref_warna = tulis_list(wp, 6, "Warna", WARNA)
    for i in range(1, 7):
        c = wp.cell(row=1, column=i)
        c.fill, c.font = HEADER_FILL, HEADER_FONT
        wp.column_dimensions[get_column_letter(i)].width = 24
    wp.freeze_panes = "A2"

    def dv(ref, rng, strict=True, prompt=None):
        v = DataValidation(type="list", formula1=ref, allow_blank=True,
                           showErrorMessage=strict)
        v.error = "Pilih dari daftar (dropdown)."
        v.errorStyle = "stop" if strict else "warning"
        if prompt:
            v.prompt, v.showInputMessage = prompt, True
        ws.add_data_validation(v)
        v.add(rng)

    last = N_BARIS_INPUT + 1
    dv(ref_admin, f"B2:B{last}", strict=False)
    dv(ref_toko, f"C2:C{last}")
    dv(ref_mp, f"D2:D{last}")
    dv(D_LABEL, f"G2:G{last}", prompt="Ketik nama mobil (mis. 'Xenia'), lalu pilih generasi.")
    dv(ref_kat, f"I2:I{last}")
    dv(ref_warna, f"J2:J{last}")
    dv(ref_status, f"M2:M{last}")
    tgl = DataValidation(type="date", operator="greaterThan", formula1="DATE(2026,1,1)",
                         allow_blank=True)
    tgl.error = "Isi tanggal (dd/mm/yyyy)."
    ws.add_data_validation(tgl)
    tgl.add(f"A2:A{last}")
    qty = DataValidation(type="whole", operator="between", formula1="1", formula2="100",
                         allow_blank=True)
    qty.error = "Qty angka bulat 1-100."
    ws.add_data_validation(qty)
    qty.add(f"K2:K{last}")
    harga = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0",
                           allow_blank=True)
    harga.error = "Harga diisi angka saja (tanpa 'Rp' / 'rb')."
    ws.add_data_validation(harga)
    harga.add(f"L2:L{last}")

    # ---------------- Rekap per Model ----------------
    wr = wb.create_sheet("Rekap per Model")
    gaya_header(wr, ["Merek", "Model", "Status Model", "Qty Tercatat (tanpa Batal/Retur)",
                     "Jumlah Pesanan", "Omzet (Rp)"], [18, 34, 12, 16, 12, 16])
    INP = "'Input Pesanan'"
    rng = lambda c: f"{INP}!${c}$2:${c}${last}"
    r = 2
    for model in model_master:
        merek = next(d["merek"] for d in daftar.values() if d["model"] == model)
        wr.cell(row=r, column=1, value=merek)
        wr.cell(row=r, column=2, value=model)
        wr.cell(row=r, column=3, value="Top 100" if model in top else "Custom")
        wr.cell(row=r, column=4, value=(
            f'=SUMIFS({rng("K")},{rng("P")},$B{r})'
            f'-SUMIFS({rng("K")},{rng("P")},$B{r},{rng("M")},"Batal")'
            f'-SUMIFS({rng("K")},{rng("P")},$B{r},{rng("M")},"Retur")'))
        wr.cell(row=r, column=5, value=(
            f'=COUNTIFS({rng("P")},$B{r})-COUNTIFS({rng("P")},$B{r},{rng("M")},"Batal")'
            f'-COUNTIFS({rng("P")},$B{r},{rng("M")},"Retur")'))
        wr.cell(row=r, column=6, value=(
            f'=SUMIFS({rng("W")},{rng("P")},$B{r})'
            f'-SUMIFS({rng("W")},{rng("P")},$B{r},{rng("M")},"Batal")'
            f'-SUMIFS({rng("W")},{rng("P")},$B{r},{rng("M")},"Retur")'))
        wr.cell(row=r, column=6).number_format = "#,##0"
        r += 1
    wr.auto_filter.ref = f"A1:F{r - 1}"

    # ---------------- Daftar Mobil ----------------
    wd = wb.create_sheet("Daftar Mobil")
    gaya_header(wd, ["Pilihan Dropdown (Model | Generasi | Tahun)", "Merek", "Model",
                     "Generasi", "Rentang Tahun", "Status Model"], [52, 18, 30, 14, 18, 12])
    for i, (label, d) in enumerate(daftar.items(), start=2):
        wd.cell(row=i, column=1, value=label)
        wd.cell(row=i, column=2, value=d["merek"])
        wd.cell(row=i, column=3, value=d["model"])
        wd.cell(row=i, column=4, value=d["gen"])
        wd.cell(row=i, column=5, value=d["tahun"])
        wd.cell(row=i, column=6, value="Top 100" if d["model"] in top else "Custom")
    wd.auto_filter.ref = f"A1:F{n_daftar + 1}"

    # ---------------- Master SKU ----------------
    wm = wb.create_sheet("Master SKU")
    gaya_header(wm, ["Kunci (Grup|Mobil|Kategori|Warna)", "SKU Gudang"], [90, 28])
    for i, (k, v) in enumerate(sku_by_key.items(), start=2):
        wm.cell(row=i, column=1, value=k)
        wm.cell(row=i, column=2, value=v)

    # ---------------- Cara Pakai ----------------
    wc = wb.create_sheet("Cara Pakai", 0)
    wc.column_dimensions["A"].width = 110
    teks = [
        ("FORM PENCATATAN PESANAN CUSTOM - UNDERCOVER", True),
        (f"Sumber daftar mobil & SKU: master {versi_master} "
         f"({len(model_master)} model, {n_daftar} pilihan generasi).", False),
        (f"Status Top 100: ranking BigSeller (Shopee+TikTok) 1 Apr - 16 Sep 2026. "
         f"Ubah manual di sheet 'Daftar Mobil' & 'Rekap per Model' kolom Status Model kalau perlu.", False),
        ("", False),
        ("CARA MENCATAT (sheet 'Input Pesanan', 1 baris = 1 varian dalam 1 pesanan)", True),
        ("1. Isi Tanggal, Admin, Toko, Marketplace, No. Pesanan, Username pembeli.", False),
        ("2. Kolom Mobil: klik dropdown lalu KETIK nama mobil (mis. 'xenia') -> pilih generasi yg cocok dgn tahun mobil pembeli.", False),
        ("3. Isi Tahun Mobil Pembeli (tahun asli mobilnya, utk cek ulang generasi).", False),
        ("4. Pilih Kategori & Warna, isi Qty & Harga.", False),
        ("5. Kolom abu-abu terisi otomatis (Merek, Model, Generasi, Tahun, SKU Gudang). JANGAN diketik manual.", False),
        ("6. Lihat kolom 'Cek': hijau OK = lengkap & SKU ketemu. Oranye = ada yg kurang / kombinasi tidak dijual di master.", False),
        ("7. Pembeli beli 2 varian beda -> 2 baris, No. Pesanan sama.", False),
        ("8. Pesanan batal/retur: ubah kolom Status (jangan hapus baris) -> otomatis tidak dihitung di Rekap.", False),
        ("", False),
        ("CATATAN WARNA STRIP", True),
        ("Strip 1 = Epic, Strip 2 = Elite, Strip 3 = Warrior. Boleh pilih ejaan mana pun, SKU otomatis menyesuaikan toko.", False),
        ("Toko Otonation memakai SKU Undercover (UA); Otoprotection memakai SKU Smartprotection (SP) - aturan konsolidasi stok.", False),
        ("", False),
        ("PENTING", True),
        ("Jangan tambah/hapus kolom di 'Input Pesanan'. Tambah nama admin di sheet 'Pengaturan'.", False),
        ("Daftar mobil & SKU diperbarui dengan membuat ulang file dari master terbaru "
         "(script scripts/buat_form_pencatatan_custom.py di repo), lalu salin baris Input lama.", False),
    ]
    for i, (t, tebal) in enumerate(teks, start=1):
        c = wc.cell(row=i, column=1, value=t)
        c.font = Font(bold=tebal, size=12 if tebal else 11)
        c.alignment = Alignment(wrap_text=True, vertical="top")

    wb.active = wb.sheetnames.index("Input Pesanan")
    wb.save(out_path)

    print(f"master: {len(model_master)} model, {n_daftar} pilihan, {n_sku} kunci SKU, bentrok kunci {len(bentrok)}")
    for b in bentrok[:10]:
        print("  bentrok:", b)
    print(f"top{TOP_N} model mobil: {len(top)} cocok ke master, {len(tak_cocok)} tak ada di master:")
    for rank, nama in tak_cocok:
        print(f"  #{rank} {nama}")
    print("tersimpan:", out_path)
    return daftar, sku_by_key, top, tak_cocok


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    buat(sys.argv[1], sys.argv[2], sys.argv[3],
         sys.argv[4] if len(sys.argv) > 4 else "(tanpa label)")
