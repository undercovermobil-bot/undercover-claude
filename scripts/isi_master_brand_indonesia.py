"""Isi master untuk brand yang beredar di Indonesia tapi sheet-nya masih kosong.

Instruksi user 2026-07-30: "di isi sekalian jadi punya list mobil yg beredar di
indonesia". Berbeda dari `buat_master_brand_baru.py` (yang menarik model & generasi
dari listing e-commerce), brand di sini BELUM punya listing sama sekali — jadi daftar
modelnya berasal dari riset pasar Indonesia, bukan dari data internal.

!! DAFTAR MODEL & RENTANG TAHUN DI BAWAH WAJIB DIVERIFIKASI SEBELUM DIPAKAI PRODUKSI.
   Lineup merek Cina/EV berubah sangat cepat; ini titik mulai, bukan data final.

Dua kelompok:
  A. sheet sudah ada tapi kosong  -> tinggal diisi
  B. sheet belum ada sama sekali  -> sheet dibuat dgn menyalin struktur header
     (header master memakai 2 baris ter-merge, jadi disalin, bukan dibuat manual)

Struktur baris sama persis dgn brand lain: 68 baris per (model x generasi)
= 4 toko x 17 baris. Lihat `buat_master_brand_baru.py` untuk rinciannya.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict

APPLY = "--apply" in sys.argv
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]
SHEET_CONTOH = "Tesla"          # dipakai sbg cetakan header saat membuat sheet baru

# (nama_sheet, kode_merek, sheet_sudah_ada, [(model, kode_model, generasi, tahun), ...])
BRAND = [
    # ---------- A. sheet sudah ada, masih kosong ----------
    ("BAIC", "BAI", True, [
        ("BJ40 Plus", "BJ40", "Gen 1", "2022-2026"),
        ("BJ80", "BJ80", "Gen 1", "2019-2026"),
        ("X55", "X55", "Gen 1", "2021-2026"),
        ("U5 Plus", "U5", "Gen 1", "2021-2026")]),
    ("Changan", "CGN", True, [
        ("CS55 Plus", "CS55", "Gen 1", "2023-2026"),
        ("Alsvin", "ALV", "Gen 1", "2021-2026"),
        ("Hunter", "HNT", "Gen 1", "2023-2026")]),
    ("Deepal", "DPL", True, [
        ("S07", "S07", "Gen 1", "2025-2026"),
        ("S05", "S05", "Gen 1", "2025-2026"),
        ("E07", "E07", "Gen 1", "2025-2026"),
        ("L07", "L07", "Gen 1", "2024-2026")]),
    ("Denza", "DNZ", True, [
        ("D9", "D9", "Gen 1", "2025-2026"),
        ("Z9GT", "Z9GT", "Gen 1", "2025-2026")]),
    ("Esemka", "ESM", True, [
        ("Bima 1.2", "BM12", "Gen 1", "2022-2026"),
        ("Bima 1.3", "BM13", "Gen 1", "2023-2026"),
        ("Garuda", "GRD", "Gen 1", "2024-2026")]),
    ("Fin Komodo", "FKM", True, [
        ("KD 250 AT", "KD25", "Gen 1", "2010-2026")]),
    ("GWM (Great Wall Motor)", "GWM", True, [
        ("Tank 300", "TK30", "Gen 1", "2023-2026"),
        ("Tank 500", "TK50", "Gen 1", "2024-2026"),
        ("Haval Jolion", "HJL", "Gen 1", "2023-2026"),
        ("Ora 03", "OR03", "Gen 1", "2023-2026")]),
    ("Genesis", "GNS", True, [
        ("G80", "G80", "Gen 1", "2021-2026"),
        ("GV70", "GV70", "Gen 1", "2021-2026"),
        ("GV80", "GV80", "Gen 1", "2021-2026")]),
    ("Hongqi", "HGQ", True, [
        ("E-HS9", "EHS9", "Gen 1", "2022-2026"),
        ("H9", "H9", "Gen 1", "2022-2026"),
        ("HS3", "HS3", "Gen 1", "2024-2026"),
        ("EH7", "EH7", "Gen 1", "2025-2026")]),
    ("Jaecoo", "JCO", True, [
        ("J7", "J7", "Gen 1", "2025-2026"),
        ("J5", "J5", "Gen 1", "2025-2026"),
        ("J8", "J8", "Gen 1", "2025-2026")]),
    ("Jaguar", "JAG", True, [
        ("F-Pace", "FPC", "Gen 1", "2016-2024"),
        ("E-Pace", "EPC", "Gen 1", "2018-2024"),
        ("XE", "XE", "Gen 1", "2015-2024"),
        ("XF", "XF", "Gen 2", "2016-2024"),
        ("I-Pace", "IPC", "Gen 1", "2018-2024"),
        ("XJ", "XJ", "Gen 4", "2010-2019"),
        ("F-Type", "FTP", "Gen 1", "2013-2024")]),
    ("Jetour", "JTR", True, [
        ("Dashing", "DSH", "Gen 1", "2024-2026"),
        ("X70 Plus", "X70", "Gen 1", "2024-2026"),
        ("X90 Plus", "X90", "Gen 1", "2024-2026"),
        ("T2", "T2", "Gen 1", "2025-2026")]),
    ("Lepas", "LPS", True, [
        ("L8", "L8", "Gen 1", "2025-2026"),
        ("L6", "L6", "Gen 1", "2025-2026"),
        ("L4", "L4", "Gen 1", "2026-2026")]),
    ("Lotus", "LTS", True, [
        ("Emira", "EMR", "Gen 1", "2022-2026"),
        ("Eletre", "ELT", "Gen 1", "2023-2026"),
        ("Emeya", "EMY", "Gen 1", "2024-2026")]),
    ("Pindad (Maung)", "PND", True, [
        ("Maung MV3", "MV3", "Gen 1", "2022-2026"),
        ("Maung MV1", "MV1", "Gen 1", "2020-2026")]),
    ("VinFast", "VFS", True, [
        ("VF3", "VF3", "Gen 1", "2024-2026"),
        ("VF5", "VF5", "Gen 1", "2024-2026"),
        ("VF6", "VF6", "Gen 1", "2025-2026"),
        ("VF7", "VF7", "Gen 1", "2025-2026"),
        ("VF e34", "VFE34", "Gen 1", "2024-2026"),
        ("Limo Green", "LMG", "Gen 1", "2025-2026")]),
    # ---------- B. sheet belum ada, harus dibuat ----------
    ("Aletra", "ALT", False, [
        ("L8", "L8", "Gen 1", "2024-2026")]),
    ("BAW", "BAW", False, [
        ("212", "212", "Gen 1", "2025-2026")]),
    ("Leapmotor", "LPM", False, [
        ("C10", "C10", "Gen 1", "2026-2026"),
        ("B10", "B10", "Gen 1", "2026-2026"),
        ("T03", "T03", "Gen 1", "2026-2026")]),
    ("Polytron", "PLT", False, [
        ("G3", "G3", "Gen 1", "2025-2026"),
        ("G3+", "G3P", "Gen 1", "2025-2026")]),
    ("Solarky", "SLK", False, [
        ("sunV", "SUNV", "Gen 1", "2026-2026")]),
    ("Xpeng", "XPG", False, [
        ("G6", "G6", "Gen 1", "2025-2026"),
        ("X9", "X9", "Gen 1", "2025-2026"),
        ("P7", "P7", "Gen 1", "2026-2026")]),
    ("Zeekr", "ZKR", False, [
        ("009", "009", "Gen 1", "2026-2026"),
        ("7X", "7X", "Gen 1", "2026-2026"),
        ("X", "X", "Gen 1", "2026-2026")]),
]

TOKO = [("Undercover Autocare", "UA"), ("Otonation", "UA"),
        ("Smartprotection", "SP"), ("Otoprotection", "SP")]
KODE_KAT = {"Reguler": "R", "Strip": "S", "Premium": "P", "Exclusive": "E"}
WARNA_KODE = {
    "Abu-abu": "ABU", "Silver": "SLV", "Hitam": "HTM", "Merah": "MRH",
    "Biru Benhur": "BRU", "Hijau Army": "GRN",
    "Elite Abu": "EAB", "Elite Biru": "EBR", "Elite Merah": "EMR",
    "Epic Abu": "PAB", "Epic Biru": "PBR", "Epic Merah": "PMR",
    "Warrior Abu": "WAB", "Warrior Biru": "WBR", "Warrior Merah": "WMR",
    "Strip 1 Abu": "S1A", "Strip 1 Biru": "S1B", "Strip 1 Merah": "S1M",
    "Strip 2 Abu": "S2A", "Strip 2 Biru": "S2B", "Strip 2 Merah": "S2M",
    "Strip 3 Abu": "S3A", "Strip 3 Biru": "S3B", "Strip 3 Merah": "S3M",
}
REGULER = ["Abu-abu", "Biru Benhur", "Hijau Army", "Hitam", "Merah"]
STRIP_UA = ["Elite Abu", "Elite Biru", "Elite Merah", "Epic Abu", "Epic Biru",
            "Epic Merah", "Warrior Abu", "Warrior Biru", "Warrior Merah"]
STRIP_SP = ["Strip 1 Abu", "Strip 1 Biru", "Strip 1 Merah", "Strip 2 Abu", "Strip 2 Biru",
            "Strip 2 Merah", "Strip 3 Abu", "Strip 3 Biru", "Strip 3 Merah"]


def baris_untuk(brand_sheet, bkode, model, mkode, gen, tahun, nomor):
    nama_produk = f"{brand_sheet.split(' (')[0]} {model}".strip()
    if brand_sheet == "Pindad (Maung)":
        nama_produk = f"Pindad {model}"
    seg = gen.replace(" ", "").replace("Gen", "G")
    out = []
    for toko, tkode in TOKO:
        rencana = [("Exclusive", ["Abu-abu"]),
                   ("Premium", ["Abu-abu", "Silver"]),
                   ("Strip", STRIP_UA if tkode == "UA" else STRIP_SP),
                   ("Reguler", REGULER)]
        for kat, warnas in rencana:
            for w in warnas:
                out.append([
                    nomor, nama_produk, toko, kat, w, gen, tahun,
                    f"{nama_produk}-{toko}-{kat}-{w}-{gen}",
                    f"{bkode}-{mkode}-{tkode}-{KODE_KAT[kat]}-{seg}-{WARNA_KODE[w]}",
                ])
    return out


def main():
    rencana = defaultdict(list)
    for sheet, bkode, ada, models in BRAND:
        for i, (model, mkode, gen, tahun) in enumerate(models, start=1):
            rencana[sheet] += baris_untuk(sheet, bkode, model, mkode, gen, tahun, i)

    # cek tabrakan ke master lama + antar baris baru
    wb = load_workbook(MASTERS[0], data_only=True)
    lama = set()
    for s in wb.sheetnames:
        ws = wb[s]
        for r in range(3, ws.max_row + 1):
            v = ws.cell(row=r, column=9).value
            if isinstance(v, str):
                lama.add(v)
    baru = [r[8] for rows in rencana.values() for r in rows]
    kunci = [(r[1], r[2], r[3], r[4], r[5]) for rows in rencana.values() for r in rows]
    bentrok = sorted(set(baru) & lama)

    print("=== RENCANA ===")
    tot = 0
    for sheet, bkode, ada, models in BRAND:
        n = len(rencana[sheet])
        tot += n
        tanda = "" if ada else "  [SHEET BARU]"
        print(f"  {sheet:26} {n:4} baris  {len(models)} model{tanda}")
        print(f"      {', '.join(m[0] for m in models)}")
    print(f"\nTOTAL baris baru : {tot}")
    print(f"SKU bentrok lama : {len(bentrok)}  {bentrok[:5]}")
    print(f"baris kembar     : {len(kunci) - len(set(kunci))}")

    if not APPLY:
        print("\nmode: DRY-RUN (master TIDAK ditulis)")
        return
    if bentrok or len(kunci) != len(set(kunci)):
        print("\nDIBATALKAN: ada tabrakan, perbaiki dulu.")
        return

    for mf in MASTERS:
        wbm = load_workbook(mf)
        for sheet, bkode, ada, models in BRAND:
            if sheet not in wbm.sheetnames:
                # salin struktur header dari sheet contoh lalu kosongkan datanya
                src = wbm[SHEET_CONTOH]
                ws = wbm.copy_worksheet(src)
                ws.title = sheet
                if ws.max_row >= 3:
                    ws.delete_rows(3, ws.max_row - 2)
            else:
                ws = wbm[sheet]
            mulai = max(ws.max_row + 1, 3)
            for i, row in enumerate(rencana[sheet]):
                for c, v in enumerate(row, start=1):
                    ws.cell(row=mulai + i, column=c, value=v)
        wbm.save(mf)
        print(f"  ditulis ke {mf}")
    print("\nmode: APPLY (master DITULIS)")


if __name__ == "__main__":
    main()
