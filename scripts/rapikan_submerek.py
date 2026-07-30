"""Rapikan sub-merek yang terselip di sheet merek induk.

Latar: 2026-07-30 dibuat 23 sheet brand baru berdasarkan riset pasar, TANPA memeriksa
apakah modelnya sudah pernah dicatat di sheet merek INDUK-nya. Ketahuan dari user:
"BYD Denza D9" sudah ada di sheet BYD (kode `BYD-DD`, 8 baris, cuma kategori Premium),
sementara skrip membuat lagi "Denza D9" di sheet Denza (kode `DNZ-D9`, 68 baris, lengkap).
Jadi satu mobil punya dua kode di dua sheet.

Skrip ini:
  1. MENGHAPUS entri lama yang sudah diputuskan user untuk dibuang (lihat `HAPUS`).
     User memilih `DNZ-D9` (sheet Denza) karena datanya lengkap dan Denza kini dipasarkan
     sebagai merek terpisah di Indonesia.
  2. MELAPORKAN calon kasus serupa: nama produk yang memuat nama sub-merek tapi berada
     di sheet lain. Hanya dilaporkan, TIDAK dihapus otomatis — penggabungan merek itu
     keputusan bisnis.
"""
import warnings, sys, re
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict

APPLY = "--apply" in sys.argv
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]

# (sheet asal, kata kunci di Nama Produk) yang harus dibuang — sudah dikonfirmasi user
HAPUS = [("BYD", "denza")]

# sub-merek -> sheet yang seharusnya menampung. Dipakai untuk mendeteksi entri nyasar.
SUB_MEREK = {
    "denza": "Denza", "deepal": "Deepal", "jaecoo": "Jaecoo", "lepas": "Lepas",
    "icar": "iCAR", "zeekr": "Zeekr", "lotus": "Lotus", "genesis": "Genesis",
    "maxus": "Maxus", "jetour": "Jetour", "hongqi": "Hongqi", "vinfast": "VinFast",
    "leapmotor": "Leapmotor", "xpeng": "Xpeng", "polytron": "Polytron",
    "aletra": "Aletra", "solarky": "Solarky", "jaguar": "Jaguar", "baic": "BAIC",
    "changan": "Changan", "esemka": "Esemka", "haval": "GWM (Great Wall Motor)",
    "tank": "GWM (Great Wall Motor)", "ora": "GWM (Great Wall Motor)",
    "bentley": "Bentley", "aston martin": "Aston Martin", "infiniti": "Infiniti",
    "neta": "Neta", "rolls": "Rolls-Royce",
}


def main():
    print("MODE:", "APPLY (master DITULIS)" if APPLY else "DRY-RUN")
    total_hapus = 0
    laporan = defaultdict(list)

    for mf in MASTERS:
        wb = load_workbook(mf)
        for sheet_asal, kata in HAPUS:
            if sheet_asal not in wb.sheetnames:
                continue
            ws = wb[sheet_asal]
            buang = [r for r in range(3, ws.max_row + 1)
                     if ws.cell(row=r, column=2).value
                     and kata in str(ws.cell(row=r, column=2).value).lower()]
            if buang:
                contoh = ws.cell(row=buang[0], column=9).value
                print(f"   HAPUS {mf[:14]} sheet {sheet_asal}: {len(buang)} baris "
                      f"'{ws.cell(row=buang[0], column=2).value}' (contoh SKU {contoh})")
                for r in sorted(buang, reverse=True):
                    if APPLY:
                        ws.delete_rows(r)
                total_hapus += len(buang)
        if APPLY:
            wb.save(mf)

    # deteksi calon kasus serupa (dibaca setelah penghapusan)
    wb = load_workbook(MASTERS[0], data_only=True)
    for s in wb.sheetnames:
        ws = wb[s]
        for r in range(3, ws.max_row + 1):
            nm = ws.cell(row=r, column=2).value
            if not nm:
                continue
            low = str(nm).lower()
            for kata, seharusnya in SUB_MEREK.items():
                # Cocokkan sbg KATA UTUH. Substring polos bikin false positive: kata
                # kunci "ora" (GWM Ora) kena di tengah "Proton Ex-ora-", dan "tank"
                # bisa kena nama lain. Batas kata mencegah itu.
                if re.search(r'\b' + re.escape(kata) + r'\b', low) and s != seharusnya:
                    sku = ws.cell(row=r, column=9).value
                    laporan[(s, str(nm).strip(), seharusnya)].append(
                        "-".join(str(sku).split("-")[:2]) if sku else "")
                    break

    print(f"\nbaris dihapus: {total_hapus}")
    print(f"\n=== CALON SUB-MEREK NYASAR (dilaporkan saja, tidak dihapus) ===")
    if not laporan:
        print("   tidak ada")
    for (s, nm, seharusnya), skus in sorted(laporan.items()):
        print(f"   sheet '{s}' berisi '{nm}' ({len(skus)} baris, kode {sorted(set(skus))}) "
              f"-> mungkin milik sheet '{seharusnya}'")


if __name__ == "__main__":
    main()
