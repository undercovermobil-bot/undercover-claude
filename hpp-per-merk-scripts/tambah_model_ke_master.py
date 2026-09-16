#!/usr/bin/env python3
"""
Menambahkan model yang ada di listing Shopee tapi BELUM tercatat di file master
"SKU, Price, Tracking Cover Mobil.xlsx".

Latar: audit balik 2026-08-03 (dipicu pertanyaan user "yang dari list produk
ecommerce sudah ada semua disitu?"). Dari 414 model Reguler unik di listing Shopee
toko Undercover Autocare, 62 tidak ketemu padanan di master. 2 di antaranya ternyata
cuma beda penulisan yang sudah tercakup ALIAS (Honda City Hatchback, Mazda 323
Interplay), jadi bersihnya 60 model.

PENTING - aturan repo (CLAUDE.md): file master ASLI tidak boleh diedit langsung.
Script ini menulis ke COPY di folder "Update via Claude/".

Penghubung listing<->master memakai KODE SKU, bukan nama produk. Ini krusial:
lewat SKU ketahuan listing Shopee "Suzuki Vitara" sebenarnya = master "Suzuki Grand
Vitara" (SZK-GVT), padahal secara nama kelihatan seperti model yang berbeda.
Lihat feedback-undercover-sku-sync-lessons.md soal bahaya cocok-nama.
"""
import collections
import json
import re
import shutil

import openpyxl

MASTER_SRC = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/5337f5dd-SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"
MASTER_OUT = "SKU, Price, Tracking Cover Mobil - TAMBAHAN MODEL SHOPEE.xlsx"
SHOPEE_FILES = [f"shopee/uc{i}.xlsx" for i in range(1, 6)]

PREFIX = "Undercover Autocare - Cover Mobil "
TIERS = ("Reguler", "Premium", "Exclusive")

# Listing "Custom" = pesanan khusus, bukan model katalog reguler. Aturan bisnis #4
# (varian generik/Custom -> SKU jangan ditebak) & #6 (produk luar-scope dikecualikan).
# Sengaja TIDAK dibuatkan entri master; dilaporkan ke user sebagai keputusan terpisah.
SKIP_CUSTOM = {
    "Honda Civic FD Custom",
    "Nissan Grand Livina Custom Roofbox",
    "Toyota Vios Custom",
}

# Model yang listing-nya cuma 1 dimensi varian (warna saja, tanpa label generasi).
# 14 varian = 5 warna Reguler + 9 warna Strip = pas 1 generasi, jadi diperlakukan
# single-generation "Gen 1" tanpa rentang tahun (preseden: Geely EX2 di master juga
# Gen 1 tanpa tahun). Bukan tebakan generasi - memang listing-nya tidak punya dimensi itu.
TANPA_LABEL_GENERASI = {"Hyundai Grand i20", "Kia Cerato", "Proton Suprima S"}

GENERIK = re.compile(r"model\s*lain|tahun\s*lain|custom|semua", re.I)
TAHUN = re.compile(r"(\d{4})\s*[-–]\s*(\d{4}|now|Now|NOW)")

# Label generasi yang sah. Listing Shopee ada yang isinya rusak/kepotong
# (mis. Isuzu D-MAX punya "Gen Gen 2F 1 (2015-2") - jangan diteruskan ke master.
LABEL_SAH = re.compile(r"^(Gen\s+\d+[A-Za-z]?(\s+\d+)?|B\d+)$", re.I)

# Label yang bentuknya sah tapi ISINYA janggal - hampir pasti salah input di listing
# Shopee (rentang tahun tidak mungkin utk model itu). Dikecualikan dari master DAN
# dilaporkan ke user supaya listing-nya yang dibetulkan, bukan datanya ikut menular.
SUSPEK_GENERASI = {
    ("Mercedes Benz EQA", "Gen 1F"): "EQA baru rilis 2021, tapi listing menulis 2017-2022",
    ("Mercedes Benz EQB", "Gen 1F"): "EQB baru rilis 2021, tapi listing menulis 2017-2022",
    ("Porsche Macan", "Gen 4"): "Macan tidak punya Gen 4; 2016-2024 sama persis dgn 718 Cayman",
}

# Kode model hasil generate otomatis kadang tidak konsisten dgn saudara sesheet.
# Override di bawah mengikuti pola tetangganya di master (alasan ditulis per baris).
KODE_MANUAL = {
    "Audi RS4 Avant": "RS4",              # sejajar AUD-A4 / AUD-A8
    "Audi TT Coupe": "TT",
    "DFSK Glory E3": "GE3",               # sejajar DFSK-GL5 / DFSK-G5 / DFSK-GI
    "DFSK Mini EV": "MEV",                # sejajar DFSK-SE
    "Ferrari 488 GTB": "488G",            # Ferrari TIDAK pakai awalan M (lih. FER-488S)
    "Ferrari 488 Pista": "488P",
    "Ferrari 812 Superfast": "812S",
    "Hyundai Grand i20": "I20",           # sejajar HYN-I10 (Hyundai Grand i10)
    "Hyundai Ioniq 6": "IQ6",             # sejajar HYN-IQ5 (Hyundai Ioniq 5)
    "Isuzu D-MAX": "DMX",                 # sejajar ISZ-MUX / ISZ-PTH
    "Land Rover Discovery Sport": "DSP",  # LDR-DIS sudah dipakai Land Rover Discovery
    "Range Rover Sport": "RRS",           # sejajar LDR-RR / LDR-RRE
    "Range Rover Velar": "RRV",
    "Mclaren 720S": "720",                # sejajar MCL-570 (McLaren 570S)
    "Mclaren 720S Spider": "720S",
    "Mercedes Benz AMG GT": "AMG",
    "Mercedes Benz V Class": "VCL",       # sejajar MBZ-BCL / MBZ-ECL / MBZ-GCL
    "Nissan Z Proto": "ZPR",              # sejajar NSN-CED / NSN-ELG (3 huruf)
    "Porsche 718 Cayman": "M718",         # sejajar POR-M911
    "Proton Suprima S": "SUP",
    "Volkswagen New Beetle": "NBT",
}


# ---------------------------------------------------------------- baca listing Shopee
def baca_listing():
    """model -> {tier: [(varian, sku)]}"""
    hasil = collections.defaultdict(lambda: collections.defaultdict(list))
    for path in SHOPEE_FILES:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb[wb.sheetnames[0]]
        for r in ws.iter_rows(min_row=7, values_only=True):
            nama, varian, sku = r[1], r[3], r[5]
            if not nama:
                continue
            nama = nama.strip()
            if not nama.startswith(PREFIX):
                continue
            sisa = nama[len(PREFIX):].strip()
            tier = next((t for t in TIERS if sisa.endswith(t)), None)
            if not tier:
                continue
            model = sisa[:-len(tier)].strip()
            hasil[model][tier].append((varian, sku))
        wb.close()
    return hasil


def ambil_generasi(tier_map, model, ditolak):
    """Kumpulkan label generasi unik dari semua tier sebuah model.

    Urutan potongan varian TIDAK diasumsikan: listing Reguler nulis "Warna,Generasi"
    tapi listing Premium sering kebalikannya "Generasi,Warna" (pelajaran 2026-07-10).
    Jadi bagian generasi dideteksi dari pola tahun / kata "Gen", bukan dari posisinya.
    """
    labels = {}
    for tier, isi in tier_map.items():
        for varian, _ in isi:
            for bag in (varian or "").split(","):
                bag = bag.strip()
                if not bag or GENERIK.search(bag):
                    continue
                m = TAHUN.search(bag)
                if not m and not re.match(r"^(gen\b|B\d)", bag, re.I):
                    continue
                label = TAHUN.sub("", bag).strip(" ()").strip()
                label = re.sub(r"\s+", " ", label)
                if not label:
                    continue
                if not LABEL_SAH.match(label):
                    ditolak.append((model, bag, "format label rusak"))
                    continue
                if (model, label) in SUSPEK_GENERASI:
                    ditolak.append((model, bag, SUSPEK_GENERASI[(model, label)]))
                    continue
                mulai = int(m.group(1)) if m else 9999
                rentang = f"{m.group(1)}-{m.group(2)}" if m else None
                if label not in labels or (rentang and not labels[label][1]):
                    labels[label] = (mulai, rentang)
    return sorted(((lbl, thn) for lbl, (_, thn) in labels.items()),
                  key=lambda x: labels[x[0]][0])


def kode_generasi(label):
    """'Gen 1' -> G1 | 'Gen 1F' -> G1F | 'Gen 2F 1' -> G2F1 | 'B5' -> GB5"""
    sisa = re.sub(r"^gen\s*", "", label, flags=re.I)
    sisa = re.sub(r"[^A-Za-z0-9]", "", sisa).upper()
    return "G" + (sisa or "1")


# ---------------------------------------------------------------- kode model utk SKU
def buat_kode_model(nama, brand_prefix, terpakai):
    """Bangkitkan kode model 2-5 karakter, deterministik, lalu cek tabrakan.

    Konvensi diturunkan dari pola master yang ada (master sendiri TIDAK 100% konsisten -
    mis. MBZ-ECL 'E Class' tapi MBZ-CC 'C Class'; PEU-M206 tapi FER-488S - jadi kode
    hasil generate ini WAJIB direview user, bukan dianggap final).
    """
    if nama in KODE_MANUAL:
        kode = KODE_MANUAL[nama]
        if f"{brand_prefix}-{kode}" in terpakai:
            raise AssertionError(f"kode manual {brand_prefix}-{kode} utk {nama} sudah dipakai")
        return kode

    inti = nama
    for kata_merk in ("Mercedes Benz", "Land Rover", "Range Rover", "Volkswagen", "Mclaren",
                      "Chevrolet", "Hyundai", "Peugeot", "Porsche", "Renault", "Ferrari",
                      "Citroen", "Proton", "Subaru", "Toyota", "Nissan", "Isuzu", "Audi",
                      "Chery", "DFSK", "Jeep", "MINI", "MG", "Kia"):
        if inti.startswith(kata_merk + " "):
            inti = inti[len(kata_merk):].strip()
            break

    kata = inti.split()
    if len(kata) == 1:
        k = re.sub(r"[^A-Za-z0-9]", "", kata[0]).upper()
        kode = k if len(k) <= 4 else k[:3]
    else:
        gabung = re.sub(r"[^A-Za-z0-9]", "", "".join(kata)).upper()
        if len(gabung) <= 4:
            kode = gabung
        else:
            # inisial tiap kata; kalau kata pertama alfanumerik pendek, pertahankan utuh
            k0 = re.sub(r"[^A-Za-z0-9]", "", kata[0]).upper()
            sisa = "".join(re.sub(r"[^A-Za-z0-9]", "", w)[:1].upper() for w in kata[1:])
            kode = (k0 if len(k0) <= 3 else k0[:3]) + sisa

    if kode and kode[0].isdigit():
        kode = "M" + kode          # preseden master: PEU-M206, POR-M911

    dasar, n = kode, 2
    while f"{brand_prefix}-{kode}" in terpakai:
        kode = f"{dasar}{n}"       # tabrakan -> suffix angka, tetap deterministik
        n += 1
    return kode


# ---------------------------------------------------------------- template baris master
WARNA_STRIP_UA = ["Elite Abu", "Elite Biru", "Elite Merah", "Epic Abu", "Epic Biru",
                  "Epic Merah", "Warrior Abu", "Warrior Biru", "Warrior Merah"]
WARNA_STRIP_SP = ["Strip 1 Abu", "Strip 1 Biru", "Strip 1 Merah", "Strip 2 Abu",
                  "Strip 2 Biru", "Strip 2 Merah", "Strip 3 Abu", "Strip 3 Biru",
                  "Strip 3 Merah"]
KODE_WARNA = {
    "Elite Abu": "EAB", "Elite Biru": "EBR", "Elite Merah": "EMR",
    "Epic Abu": "PAB", "Epic Biru": "PBR", "Epic Merah": "PMR",
    "Warrior Abu": "WAB", "Warrior Biru": "WBR", "Warrior Merah": "WMR",
    "Strip 1 Abu": "S1A", "Strip 1 Biru": "S1B", "Strip 1 Merah": "S1M",
    "Strip 2 Abu": "S2A", "Strip 2 Biru": "S2B", "Strip 2 Merah": "S2M",
    "Strip 3 Abu": "S3A", "Strip 3 Biru": "S3B", "Strip 3 Merah": "S3M",
    "Abu-abu": "ABU", "Biru Benhur": "BRU", "Hijau Army": "GRN", "Hitam": "HTM",
    "Merah": "MRH", "Orange": "ORG", "Silver": "SLV",
}
KODE_KAT = {"Strip": "S", "Reguler": "R", "Premium": "P", "Exclusive": "E"}
KODE_TOKO = {"Undercover Autocare": "UA", "Otonation": "UA",
             "Smartprotection": "SP", "Otoprotection": "SP"}   # aturan #1: konsolidasi
URUT_TOKO = ["Undercover Autocare", "Otonation", "Smartprotection", "Otoprotection"]


def template_sheet(ws):
    """Ambil pola (toko, kategori) -> daftar warna dari model yang SUDAH ada di sheet ini.

    Sibling-based: baris baru mengikuti pola saudara sesheet, bukan pola global -
    komposisi kategori/warna beda-beda antar merk (mis. sebagian sheet punya
    Transparan, sebagian Reguler SP/OP-nya punya Orange).
    """
    it = ws.iter_rows(values_only=True)
    next(it)
    per_model = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in it:
        if len(r) < 9 or not r[1]:
            continue
        per_model[str(r[1]).strip()][(r[2], r[3])].add(r[4])
    if not per_model:
        return None
    pola = collections.Counter()
    for model, tk in per_model.items():
        kunci = tuple(sorted((t, k, tuple(sorted(w, key=str))) for (t, k), w in tk.items()))
        pola[kunci] += 1
    return pola.most_common(1)[0][0]


def main():
    listing = baca_listing()
    audit = json.load(open("audit_balik.json"))
    hilang = [m for m, _ in audit["hilang"]
              if m not in ("Honda City Hatchback", "Mazda Mazda 323 Interplay")]

    # sheet tujuan per model: dari sheet master yang namanya cocok prefix merk
    wb = openpyxl.load_workbook(MASTER_SRC)
    sheet_of = {}
    SHEET_MERK = {
        "Audi": "Audi", "Chery": "Chery", "Chevrolet": "Chevrolet", "Citroen": "Citroen",
        "DFSK": "DFSK", "Ferrari": "Ferrari", "Honda": "Honda", "Hyundai": "Hyundai",
        "Isuzu": "Isuzu", "Jeep": "Jeep", "Kia": "Kia", "Land Rover": "Land Rover",
        "Range Rover": "Land Rover", "MG": "MG (Morris Garages)", "MINI": "MINI",
        "Mclaren": "McLaren", "Mercedes Benz": "Mercedes-Benz", "Nissan": "Nissan",
        "Peugeot": "Peugeot", "Porsche": "Porsche", "Proton": "Proton",
        "Renault": "Renault", "Subaru": "Subaru", "Toyota": "Toyota",
        "Volkswagen": "Volkswagen",
    }
    for m in hilang:
        for pfx in sorted(SHEET_MERK, key=len, reverse=True):
            if m.startswith(pfx):
                sheet_of[m] = SHEET_MERK[pfx]
                break

    # kode SKU yang sudah terpakai (global) supaya kode baru tidak nabrak
    terpakai = set()
    brand_of_sheet = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        next(it)
        for r in it:
            if len(r) < 9 or not r[8] or not isinstance(r[8], str):
                continue
            p = r[8].split("-")
            if len(p) >= 2:
                terpakai.add(f"{p[0]}-{p[1]}")
                brand_of_sheet.setdefault(ws.title, collections.Counter())[p[0]] += 1
    brand_of_sheet = {s: c.most_common(1)[0][0] for s, c in brand_of_sheet.items()}

    laporan, dilewati, gen_ditolak = [], [], []
    total_baris = 0

    for model in hilang:
        if model in SKIP_CUSTOM:
            dilewati.append((model, "listing 'Custom' - aturan #4/#6, SKU jangan ditebak"))
            continue
        sheet = sheet_of.get(model)
        if not sheet or sheet not in wb.sheetnames:
            dilewati.append((model, f"sheet merk tidak ketemu ({sheet})"))
            continue
        ws = wb[sheet]
        pola = template_sheet(ws)
        if not pola:
            dilewati.append((model, "sheet kosong, tidak ada pola sibling"))
            continue

        if model in TANPA_LABEL_GENERASI:
            generasi = [("Gen 1", None)]
        else:
            generasi = ambil_generasi(listing.get(model, {}), model, gen_ditolak)
        if not generasi:
            dilewati.append((model, "tidak ada label generasi di listing"))
            continue

        brand = brand_of_sheet.get(sheet)
        if not brand:
            dilewati.append((model, "brand code sheet tidak diketahui"))
            continue
        kode_m = buat_kode_model(model, brand, terpakai)
        terpakai.add(f"{brand}-{kode_m}")

        nomor = max((r[0] for r in ws.iter_rows(min_row=2, values_only=True)
                     if r and isinstance(r[0], int)), default=0) + 1

        n_baris = 0
        for label, rentang in generasi:
            gcode = kode_generasi(label)
            for toko, kat, warna_list in pola:
                for warna in warna_list:
                    if warna is None:
                        continue
                    kw = KODE_WARNA.get(warna)
                    kk = KODE_KAT.get(kat)
                    if not kw or not kk:
                        continue
                    sku = f"{brand}-{kode_m}-{KODE_TOKO[toko]}-{kk}-{gcode}-{kw}"
                    ws.append([nomor, model, toko, kat, warna, label, rentang,
                               f"{model}-{toko}-{kat}-{warna}-{label}", sku])
                    n_baris += 1
        total_baris += n_baris
        laporan.append((sheet, model, f"{brand}-{kode_m}",
                        [g[0] for g in generasi], n_baris))

    wb.save(MASTER_OUT)

    print(f"tersimpan: {MASTER_OUT}")
    print(f"model ditambahkan : {len(laporan)}")
    print(f"total baris baru  : {total_baris}")
    print(f"dilewati          : {len(dilewati)}")
    print()
    print(f"{'SHEET':<22}{'MODEL':<34}{'KODE SKU':<12}{'BARIS':>6}  GENERASI")
    for sheet, model, kode, gens, n in laporan:
        print(f"{sheet:<22}{model:<34}{kode:<12}{n:>6}  {', '.join(gens)}")
    print()
    print("MODEL DILEWATI:")
    for m, alasan in dilewati:
        print(f"  {m} - {alasan}")

    if gen_ditolak:
        print()
        print("LABEL GENERASI DITOLAK (data listing Shopee perlu dibetulkan):")
        for m, bag, alasan in sorted(set(gen_ditolak)):
            print(f"  {m} | {bag!r} - {alasan}")

    json.dump({"ditambahkan": laporan, "dilewati": dilewati,
               "gen_ditolak": sorted(set(gen_ditolak)), "total_baris": total_baris},
              open("laporan_tambah_master.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
