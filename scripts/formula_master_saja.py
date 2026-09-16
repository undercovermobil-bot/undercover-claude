"""Terapkan skema FORMULA ke FILE MASTER saja (listing ditangani pipeline lain).

Perlu dijalankan ulang setiap kali `formula_config.py` bertambah aturannya. Contoh
konkret: Mini Cooper baru dibuka blokirnya (3P/5P) SETELAH master diproses, jadi
master masih memakai segmen lama (Roadster/Paceman/Hatch3Pintu/G1/G2/G3) padahal
listing sudah 3P/5P. Kalau tidak disamakan, `rebuild_lookup.py` akan menghasilkan
lookup yg bertentangan dgn listing.

Kolom master: 2=Nama Produk 3=Toko 4=Kategori 5=Warna 6=Generasi 7=Rentang Tahun 9=SKU
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter

import formula_config as FC
import apply_formula_sku as AF

APPLY = "--apply" in sys.argv
CFG, BLOCKED = FC.load()
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]


def run(apply):
    stat = Counter()
    per_model = Counter()
    contoh = []
    for mf in MASTERS:
        try:
            wbm = load_workbook(mf, data_only=False)
        except FileNotFoundError:
            stat["file_hilang"] += 1
            continue
        touched = False
        for sn in wbm.sheetnames:
            ws = wbm[sn]
            for r in range(2, ws.max_row + 1):
                nm = ws.cell(row=r, column=2).value
                sku = ws.cell(row=r, column=9).value
                if not nm or not isinstance(sku, str) or not AF.MASTERFMT.match(sku):
                    continue
                model, tag = AF.match_model(nm)
                if model is None or tag == "blocked":
                    continue
                gen = ws.cell(row=r, column=6).value
                yr = ws.cell(row=r, column=7).value
                newseg = FC.seg_for_variant(CFG[model], f"{gen or ''} ({yr or ''})")
                if not newseg:
                    stat["varian_tak_terbaca"] += 1
                    continue
                p = sku.split("-")
                if p[4] == newseg:
                    stat["sudah_benar"] += 1
                    continue
                new = "-".join(p[:4] + [newseg] + p[5:])
                if apply:
                    ws.cell(row=r, column=9, value=new)
                touched = True
                stat[f"diubah[{mf[:14]}]"] += 1
                per_model[model] += 1
                if len(contoh) < 10:
                    contoh.append((mf[:14], model, str(gen), sku, new))
        if apply and touched:
            wbm.save(mf)
    return stat, per_model, contoh


if __name__ == "__main__":
    print("MODE:", "APPLY (master DITULIS)" if APPLY else "DRY-RUN")
    stat, per_model, contoh = run(APPLY)
    for k, v in stat.most_common():
        print(f"   {v:7}  {k}")
    print(f"\nmodel terdampak: {len(per_model)}")
    for m, n in per_model.most_common(15):
        print(f"   {n:6}  {m}")
    print("\ncontoh:")
    for c in contoh:
        print("   ", c)
