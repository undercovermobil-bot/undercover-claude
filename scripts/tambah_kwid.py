"""Tambah model MULTI-GENERASI ke master, menyalin pola per-blok-generasi dari model lain.

Beda dari `tambah_model_dari_pola.py` (1 generasi saja): dipakai kalau model baru
punya >1 generasi dengan rentang tahun berbeda per generasi, tapi jumlah kategori/
warnanya sama dgn model pola. Tiap pasangan (label_pola, tahun_pola) dipetakan ke
(label_baru, tahun_baru) sendiri-sendiri.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]


def tambah(sheet, sumber, nama_baru, kode_baru, peta_gen, apply):
    """peta_gen: {(label_pola, tahun_pola): (label_baru, tahun_baru)}"""
    hasil = []
    for mf in MASTERS:
        wb = load_workbook(mf)
        ws = wb[sheet]

        sudah = [r for r in range(3, ws.max_row + 1)
                 if str(ws.cell(row=r, column=2).value or "").strip().lower() == nama_baru.lower()]
        if sudah:
            print(f"   {mf[:14]}: '{nama_baru}' sudah ada ({len(sudah)} baris) — dilewati")
            continue

        pola = [r for r in range(3, ws.max_row + 1)
                if str(ws.cell(row=r, column=2).value or "").strip() == sumber]
        if not pola:
            print(f"   {mf[:14]}: pola '{sumber}' tidak ketemu — DIBATALKAN")
            continue

        kode_sumber = str(ws.cell(row=pola[0], column=9).value or "").split("-")[1]
        nomor = max((ws.cell(row=r, column=1).value or 0)
                    for r in range(3, ws.max_row + 1)
                    if isinstance(ws.cell(row=r, column=1).value, int)) + 1
        tulis = ws.max_row + 1
        i = 0
        lewat = 0
        for r in pola:
            gen_pola = str(ws.cell(row=r, column=6).value or "").strip()
            thn_pola = str(ws.cell(row=r, column=7).value or "").strip()
            key = (gen_pola, thn_pola)
            if key not in peta_gen:
                lewat += 1
                continue
            gen_baru, thn_baru = peta_gen[key]
            toko = ws.cell(row=r, column=3).value
            kat = ws.cell(row=r, column=4).value
            warna = ws.cell(row=r, column=5).value
            sku_pola = str(ws.cell(row=r, column=9).value or "")
            seg_baru = gen_baru.replace(" ", "").replace("Gen", "G")
            p = sku_pola.split("-")
            sku = "-".join([kode_baru if x == kode_sumber else
                            (seg_baru if idx == 4 else x)
                            for idx, x in enumerate(p)])
            baris = [nomor, nama_baru, toko, kat, warna, gen_baru, thn_baru,
                     f"{nama_baru}-{toko}-{kat}-{warna}-{gen_baru}", sku]
            if apply:
                for c, v in enumerate(baris, start=1):
                    ws.cell(row=tulis + i, column=c, value=v)
            if mf == MASTERS[0]:
                hasil.append((str(toko), str(kat), str(warna), gen_baru, sku))
            i += 1
        if apply:
            wb.save(mf)
        print(f"   {mf[:14]}: {i} baris '{nama_baru}' ditulis (kode {kode_baru}, "
              f"{lewat} baris pola dilewati krn generasinya tidak dipetakan)")
    return hasil


def cetak(hasil):
    gens = sorted({h[3] for h in hasil})
    for gen in gens:
        print(f"\n=== {gen} ===")
        for kat in ("Exclusive", "Premium", "Reguler", "Strip", "Transparan"):
            baris = [h for h in hasil if h[1] == kat and h[3] == gen]
            if not baris:
                continue
            print(f"\n  --- {kat} ---")
            seen = set()
            for toko, k, warna, g, sku in baris:
                if sku in seen:
                    continue
                seen.add(sku)
                print(f"     {warna:16} {sku}")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    print("MODE:", "APPLY (master DITULIS)" if apply else "DRY-RUN")

    # Renault Kwid: Gen 1 (2015-2019) dan Gen 1F (2019-2024) sesuai teks varian listing.
    # Dipetakan dari pola Renault Koleos yg juga 2 generasi (Gen 1/Gen 2).
    peta = {
        ("Gen 1", "2006-2016"): ("Gen 1", "2015-2019"),
        ("Gen 2", "2016-2024"): ("Gen 1F", "2019-2024"),
    }
    h = tambah("Renault", "Renault Koleos", "Renault Kwid", "KWD", peta, apply)
    if h:
        cetak(h)
