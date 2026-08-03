#!/usr/bin/env python3
"""
Membuat workbook HPP per merk mobil.

Struktur: 1 sheet per merk (mengikuti sheet di "SKU, Price, Tracking Cover Mobil.xlsx"),
isi tiap sheet mengikuti format kolom Sheet3 "DATA_UC_HPP.xlsx" (A..AC + formulanya).

Sumber data:
  1. SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx -> daftar merk + model (Kategori Produk = "Reguler")
  2. Informasi Penjualan Shopee Undercover 1-5 (SYNCED v3).xlsx -> harga jual ACTUAL kolom J
     (diambil dari listing "... Reguler" toko Undercover Autocare, varian warna Reguler saja:
      Abu-abu / Hitam / Merah / Biru Benhur / Hijau Army)
  3. DATA_UC_HPP.xlsx Sheet3 baris "Avanza Reguler" -> nilai konstanta + format sel
"""
import collections
import json
import pickle
import re

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

SKU_SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/5337f5dd-SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"
SHOPEE_FILES = [f"shopee/uc{i}.xlsx" for i in range(1, 6)]
OUT = "DATA UC HPP per Merk (Reguler).xlsx"

# ---------------------------------------------------------------- 1. harga Shopee
WARNA_REGULER = {"Abu-abu", "Hitam", "Merah", "Biru Benhur", "Hijau Army"}
PREFIX = "Undercover Autocare - Cover Mobil "
SUFFIX = "Reguler"


def baca_harga_shopee():
    """model -> (harga modus, {harga: jumlah varian})"""
    hitung = collections.defaultdict(collections.Counter)
    for path in SHOPEE_FILES:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb[wb.sheetnames[0]]
        for r in ws.iter_rows(min_row=7, values_only=True):
            nama, varian, harga = r[1], r[3], r[6]
            if not nama or not harga:
                continue
            nama = nama.strip()
            if not (nama.startswith(PREFIX) and nama.endswith(SUFFIX)):
                continue
            model = nama[len(PREFIX):-len(SUFFIX)].strip()
            warna = (varian or "").split(",")[0].strip()
            if warna in WARNA_REGULER:
                hitung[model][int(harga)] += 1
        wb.close()
    return {m: (c.most_common(1)[0][0], dict(c)) for m, c in hitung.items()}


# ---------------------------------------------------------------- 2. daftar model
def baca_model_per_merk():
    wb = openpyxl.load_workbook(SKU_SRC, data_only=True, read_only=True)
    hasil = collections.OrderedDict()
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        next(it)  # header
        urut, sudah = [], set()
        for r in it:
            if len(r) < 4:
                continue
            nama, kategori = r[1], r[3]
            if not nama or not kategori or str(kategori).strip() != "Reguler":
                continue
            n = str(nama).strip()
            if n not in sudah:
                sudah.add(n)
                urut.append(n)
        hasil[ws.title] = urut
    wb.close()
    return hasil


# ---------------------------------------------------------------- 3. pencocokan nama
# Hanya padanan yang jelas. Yang meragukan sengaja dikosongkan (lihat MERAGUKAN).
ALIAS = {
    # Daihatsu — imbuhan "All New"/"New" & gabungan varian bodi
    "Daihatsu All New Ayla": "Daihatsu Ayla",
    "Daihatsu New Sirion": "Daihatsu Sirion",
    "Daihatsu All New Xenia": "Daihatsu Xenia",
    "Daihatsu Terios / New Terios": "Daihatsu Terios",
    "Daihatsu Gran Max Minibus / Blind Van": "Daihatsu Gran Max Minibus",
    # Honda — beda penulisan tanda hubung & embel-embel trim
    "Honda Brio Satya / RS": "Honda Brio",
    "Honda City Hatchback RS": "Honda City Hatchback",
    "Honda Civic Sedan": "Honda Civic",
    "Honda Civic Sedan / RS": "Honda Civic",
    "Honda WR-V": "Honda WRV",
    "Honda BR-V": "Honda BRV",
    "Honda HR-V / e:N1": "Honda HRV",
    "Honda CR-V": "Honda CRV",
    # Mazda
    "Mazda CX5": "Mazda CX-5",
    "Mazda 323 Interplay": "Mazda Mazda 323 Interplay",
    # Mitsubishi — nama produk di file SKU kedobelan "Mitsubishi Mitsubishi"
    "Mitsubishi Mitsubishi Kuda": "Mitsubishi Kuda",
    "Mitsubishi Mitsubishi Destinator": "Mitsubishi Destinator",
    "Mitsubishi Mitsubishi Xpander Cross": "Mitsubishi Xpander Cross",
    "Mitsubishi Mitsubishi Outlander": "Mitsubishi Outlander",
    # Nissan — embel-embel teknologi/trim
    "Nissan Livina / Grand Livina": "Nissan Grand Livina",
    "Nissan Serena e-POWER": "Nissan Serena",
    "Nissan Kicks e-POWER": "Nissan Kicks",
    "Nissan Navara PRO-4X": "Nissan Navara",
    # Suzuki
    "Suzuki All New Ertiga / Hybrid": "Suzuki Ertiga",
    "Suzuki XL7 / Hybrid": "Suzuki XL7",
    "Suzuki APV Arena / Blind Van": "Suzuki APV Arena",
    "Suzuki New Carry Pick-Up": "Suzuki Carry Pickup",
    # Toyota — Shopee memakai 1 listing "Toyota Kijang" untuk semua generasi
    "Toyota Kijang Buaya": "Toyota Kijang",
    "Toyota Kijang Doyok": "Toyota Kijang",
    "Toyota Kijang Super / Grand": "Toyota Kijang",
    "Toyota Kijang Kapsul (SGX)": "Toyota Kijang",
    "Toyota Kijang Kapsul (LGX/LSX)": "Toyota Kijang",
    "Toyota Hilux (D-Cab)": "Toyota Hilux",
    "Toyota HiAce Long": "Toyota HiAce",
    # Jeep — Rubicon = trim dari Wrangler
    "Jeep Wrangler Rubicon": "Jeep Wrangler",
}

# Sengaja TIDAK dicocokkan: nama mirip tapi bisa jadi model yang berbeda.
MERAGUKAN = {
    "Toyota Corolla Altis": "Shopee cuma punya 'Toyota Corolla' — beda nameplate",
    "Suzuki Grand Vitara": "Shopee cuma punya 'Suzuki Vitara' — beda model",
    "Suzuki Grand Vitara Hybrid": "Shopee cuma punya 'Suzuki Vitara' — beda model",
    "Suzuki e VITARA": "Shopee cuma punya 'Suzuki Vitara' — beda model",
    "Suzuki Carry Futura": "Shopee punya 'Suzuki Carry' & 'Suzuki Carry Pickup' — Futura tidak spesifik",
    "Kia Sedona": "Shopee cuma punya 'Kia Grand Sedona' — beda generasi",
    "Nissan Livina (All New)": "Shopee punya 'Nissan Grand Livina' & 'Nissan Livina X-Gear' — tidak spesifik",
}


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())


# ---------------------------------------------------------------- 4. gaya sel Sheet3
JUDUL = [
    "Nama Produk", "Harga Kain", "Pcs/Roll ACTUAL ", "Biaya Per PCS", "SDM",
    "Tali Rit Komponen lain ", "HPP ", "Iklan Roas 17", "Margin", "Harga Jual ACTUAL ",
    "% Adm", "Biaya Admin", "% GOE", "Gratis Ongkir Extra", "% PX", "Promo Xtra",
    "% SX", "SPaylater Xtra", "Affiliate", "Affliate", "%ET", "Event Toko",
    "Total Potongan Biaya ", "Cair MP", "HPP TOTAL ", "Margin Actual ", "Margin ",
    "Harga Jual Terbaru ", "Margin Bersih",
]

RP = '_-[$Rp-421]* #,##0.00_-;\\-[$Rp-421]* #,##0.00_-;_-[$Rp-421]* "-"??_-;_-@_-'
PERSEN = "0.00%"
BULAT = "0"

# format angka per kolom (mengikuti baris "Avanza Reguler" di Sheet3)
FMT = {
    "C": BULAT, "D": BULAT, "G": BULAT, "N": BULAT,
    "K": PERSEN, "M": PERSEN, "O": PERSEN, "Q": PERSEN, "S": PERSEN, "U": PERSEN,
    "W": RP, "X": RP, "Y": RP, "Z": RP, "AA": RP, "AB": RP, "AC": RP,
}

# kolom yang di Sheet3 tidak berbingkai
TANPA_BINGKAI = {"C", "D", "E", "F", "G"}

# konstanta dari baris contoh "Avanza Reguler"
KONST = {
    "B": 715000,     # Harga Kain
    "E": 16500,      # SDM
    "F": 20000,      # Tali Rit Komponen lain
    "H": 18000,      # Iklan Roas 17
    "K": 0.1045,     # % Adm
    "M": 0.055,      # % GOE
    "O": 0.045,      # % PX
    "Q": 0.025,      # % SX
    "S": 0.05,       # Affiliate
    "U": 0.055,      # %ET
}

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)
MED = Side(style="medium")
BINGKAI = Border(left=MED, right=MED, top=MED, bottom=MED)
KIRI_ATAS = Alignment(wrap_text=True, vertical="bottom")
KANAN = Alignment(wrap_text=True, horizontal="right", vertical="bottom")

LEBAR = {"A": 17.85546875, "F": 12.28515625, "J": 8.140625, "S": 14.0,
         "W": 13.7109375, "X": 13.7109375, "AC": 13.7109375}


def formula(kolom, n):
    """Formula Sheet3. D/G/Y/Z/AC dijaga agar tidak #DIV/0! saat kolom C kosong."""
    return {
        "D": f'=IFERROR(B{n}/C{n},"")',
        "G": f'=IF(D{n}="","",SUM(D{n}:F{n}))',
        "L": f"=J{n}*K{n}",
        "N": f"=M{n}*J{n}",
        "P": f"=J{n}*O{n}",
        "R": f"=Q{n}*J{n}",
        "T": f"=J{n}*S{n}",
        "V": f"=U{n}*J{n}",
        "W": f"=L{n}+N{n}+P{n}+R{n}+T{n}+V{n}",
        "X": f"=J{n}-W{n}",
        "Y": f'=IF(G{n}="","",G{n}+H{n}+W{n})',
        "Z": f'=IF(Y{n}="","",J{n}-Y{n})',
        "AA": f"=J{n}*10%",
        "AB": f"=J{n}+AA{n}",
        "AC": f'=IF(Y{n}="","",(J{n}+AA{n})-Y{n})',
    }.get(kolom)


def tulis_sheet(ws, model_list, harga_map):
    for i, judul in enumerate(JUDUL, start=1):
        c = ws.cell(1, i, judul)
        c.font = ARIAL
        c.alignment = KIRI_ATAS
        if get_column_letter(i) not in TANPA_BINGKAI:
            c.border = BINGKAI
        else:  # di Sheet3 header C..G tidak punya garis bawah
            c.border = Border(left=MED, right=MED, top=MED)
    ws.row_dimensions[1].height = 39.75

    for baris, model in enumerate(model_list, start=2):
        ws.row_dimensions[baris].height = 15.75
        for i in range(1, 30):
            kol = get_column_letter(i)
            c = ws.cell(baris, i)
            c.font = ARIAL
            c.alignment = KIRI_ATAS if kol == "A" else KANAN
            if kol not in TANPA_BINGKAI:
                c.border = BINGKAI
            if kol in FMT:
                c.number_format = FMT[kol]

            if kol == "A":
                c.value = model
            elif kol in KONST:
                c.value = KONST[kol]
            elif kol == "J":
                if model in harga_map:
                    c.value = harga_map[model]
            else:
                f = formula(kol, baris)
                if f:
                    c.value = f

    for kol, w in LEBAR.items():
        ws.column_dimensions[kol].width = w


def tulis_catatan(ws, ringkas, tanpa_harga, harga_ganda):
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 72
    baris = 1

    def tulis(a, b="", c="", tebal=False):
        nonlocal baris
        for kol, val in (("A", a), ("B", b), ("C", c)):
            sel = ws[f"{kol}{baris}"]
            sel.value = val
            sel.font = ARIAL_TEBAL if tebal else ARIAL
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris += 1

    tulis("CATATAN & ASUMSI", "", "", tebal=True)
    tulis("Dibuat", "2026-08-03")
    tulis("Isi", "1 sheet per merk mobil. 1 baris = 1 model (varian Reguler saja; "
                 "Premium / Exclusive / Transparan tidak dimasukkan).")
    tulis("Format kolom", "Mengikuti Sheet3 file DATA_UC_HPP.xlsx, kolom A s/d AC berikut formulanya.")
    tulis("")

    tulis("SUMBER DATA", "", "", tebal=True)
    tulis("Daftar merk & model", "SKU, Price, Tracking Cover Mobil.xlsx",
          "Baris dengan Kategori Produk = 'Reguler', diambil nama produk uniknya per sheet merk.")
    tulis("Harga Jual ACTUAL (kolom J)", "Informasi Penjualan Shopee Undercover 1-5 (SYNCED v3).xlsx",
          "Listing 'Undercover Autocare - Cover Mobil <model> Reguler', harga varian warna Reguler "
          "(Abu-abu / Hitam / Merah / Biru Benhur / Hijau Army). Varian Strip (Elite/Epic/Warrior) "
          "harganya lebih mahal ±Rp60.000 dan TIDAK dipakai.")
    tulis("Konstanta B, E, F, H + semua %", "DATA_UC_HPP.xlsx Sheet3, baris 'Avanza Reguler'",
          "Harga Kain 715.000 | SDM 16.500 | Tali Rit & komponen lain 20.000 | Iklan Roas 17 18.000 | "
          "Adm 10,45% | GOE 5,50% | PX 4,50% | SX 2,50% | Affiliate 5,00% | Event Toko 5,50%.")
    tulis("")

    tulis("YANG PERLU DIISI SENDIRI", "", "", tebal=True)
    tulis("Kolom C (Pcs/Roll ACTUAL)", "KOSONG di semua baris",
          "Sesuai permintaan. Begitu C diisi, kolom D (Biaya per PCS), G (HPP), Y (HPP Total), "
          "Z (Margin Actual) dan AC (Margin Bersih) langsung terhitung sendiri.")
    tulis("Kolom I (Margin)", "KOSONG", "Di Sheet3 aslinya juga kosong.")
    tulis("Kolom J tanpa harga", "KOSONG",
          "Berarti model itu belum/tidak ada di listing Shopee toko Undercover Autocare.")
    tulis("")

    tulis("PENYESUAIAN FORMULA", "", "", tebal=True)
    tulis("D", '=IFERROR(B/C,"")',
          "Aslinya =B/C. Karena C dikosongkan, formula asli akan menampilkan #DIV/0! di semua baris.")
    tulis("G", '=IF(D="","",SUM(D:F))',
          "Aslinya =SUM(D:F). Tanpa penjagaan, HPP akan tampil 36.500 (cuma SDM + tali rit) "
          "seolah-olah angka benar.")
    tulis("Y / Z / AC", '=IF(...="","",...)',
          "Ikut dijaga karena rantainya berasal dari G. Isi perhitungannya tidak diubah.")
    tulis("Kolom lain", "Sama persis dengan Sheet3",
          "L=J*K, N=M*J, P=J*O, R=Q*J, T=J*S, V=U*J, W=L+N+P+R+T+V, X=J-W, AA=J*10%, AB=J+AA.")
    tulis("")

    tulis("RINGKASAN", "", "", tebal=True)
    for k, v in ringkas:
        tulis(k, v)
    tulis("")

    tulis("MODEL TANPA HARGA (kolom J dikosongkan)", "", "", tebal=True)
    tulis("Merk", "Model", "Alasan", tebal=True)
    for merk, model, alasan in tanpa_harga:
        tulis(merk, model, alasan)
    tulis("")

    tulis("MODEL DENGAN HARGA REGULER TIDAK SERAGAM DI SHOPEE", "", "", tebal=True)
    tulis("Model", "Harga ditemukan", "Yang dipakai (harga terbanyak) — mohon dicek", tebal=True)
    for model, detail, dipakai in harga_ganda:
        tulis(model, detail, dipakai)


def main():
    harga_shopee = baca_harga_shopee()
    merk_model = baca_model_per_merk()
    norm_harga = {norm(k): (k, v) for k, v in harga_shopee.items()}

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    ws_catatan = wb.create_sheet("CATATAN")

    tanpa_harga = []
    n_model = n_ketemu = 0
    model_terpakai = set()

    for merk, models in merk_model.items():
        peta = {}
        for m in models:
            n_model += 1
            target = ALIAS.get(m, m)
            hit = norm_harga.get(norm(target))
            if hit:
                kunci_shopee, (harga_modus, _) = hit
                peta[m] = harga_modus
                model_terpakai.add(kunci_shopee)
                n_ketemu += 1
            else:
                alasan = MERAGUKAN.get(
                    m, "Tidak ada listing 'Reguler' untuk model ini di Shopee Undercover Autocare")
                tanpa_harga.append((merk, m, alasan))
        tulis_sheet(wb.create_sheet(merk), models, peta)

    harga_ganda = []
    for model in sorted(model_terpakai):
        _, rincian = harga_shopee[model]
        if len(rincian) > 1:
            detail = " | ".join(f"Rp{h:,} ({n} varian)".replace(",", ".")
                                for h, n in sorted(rincian.items()))
            dipakai = f"Rp{max(rincian, key=rincian.get):,}".replace(",", ".")
            harga_ganda.append((model, detail, dipakai))

    ringkas = [
        ("Jumlah sheet merk", len(merk_model)),
        ("Total model (baris)", n_model),
        ("Model dapat harga Shopee", n_ketemu),
        ("Model tanpa harga (J kosong)", n_model - n_ketemu),
        ("Listing Reguler Shopee terbaca", len(harga_shopee)),
    ]
    tulis_catatan(ws_catatan, ringkas, tanpa_harga, harga_ganda)

    wb.save(OUT)
    print("tersimpan:", OUT)
    for k, v in ringkas:
        print(f"  {k}: {v}")
    print("  model harga tidak seragam:", len(harga_ganda))


if __name__ == "__main__":
    main()
