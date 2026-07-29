"""Isi SKU 2 listing Gran Max di UA Lazada yang variannya bodi, bukan warna.

Kedua listing (Premium pid 8664138934, Exclusive pid 8664142658) memakai varian
`Blindvan (2008-2024)` / `Pickup (2008-2024)` / `Model Lain / Custom` dan TIDAK punya
pilihan warna sama sekali. Karena nama produknya cuma "…Gran Max Premium/Exclusive",
pencocok model biasa menjatuhkannya ke "Daihatsu Gran Max" yang DITUNDA (duplikat ungu),
sehingga barisnya selalu terlewat.

User konfirmasi 2026-07-29: **Blindvan masuk minibus**. Master pun menamainya eksplisit
"Daihatsu Gran Max Minibus / Blindvan" -> `DHT-GMX`; pickup -> `DHT-GMXP`.

Segmen warna diambil `ABU`: master menyediakan ABU (& SLV utk Premium), sementara listing
tidak menawarkan pilihan warna, jadi dipakai warna utama. `Model Lain / Custom` sengaja
TIDAK diisi — bodinya tidak diketahui.
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter

APPLY = "--apply" in sys.argv
FILE = "BARU_FIX/UA_Lazada.xlsx"
SHEET, PIDC, NAMAC, SKUC, VARC, SR = "template", 1, 3, 13, 14, 5

# pid -> huruf kategori
KAT = {"8664138934": "P", "8664142658": "E"}
# kata kunci di varian -> kode model
BODI = (("blindvan", "DHT-GMX"), ("blind van", "DHT-GMX"), ("pickup", "DHT-GMXP"),
        ("pick up", "DHT-GMXP"), ("pick-up", "DHT-GMXP"))


def run(apply):
    wb = load_workbook(FILE, data_only=False)
    ws = wb[SHEET]
    stat = Counter()
    log = []
    for r in range(SR, ws.max_row + 1):
        pid = str(ws.cell(row=r, column=PIDC).value or "")
        if pid not in KAT:
            continue
        var = str(ws.cell(row=r, column=VARC).value or "").lower()
        kode = next((k for kata, k in BODI if kata in var), None)
        if kode is None:
            stat["dilewati_bodi_tidak_jelas"] += 1
            continue
        baru = f"{kode}-UA-{KAT[pid]}-G1-ABU"
        lama = ws.cell(row=r, column=SKUC).value
        if str(lama) == baru:
            stat["sudah_benar"] += 1
            continue
        if apply:
            ws.cell(row=r, column=SKUC, value=baru)
        stat["diisi"] += 1
        log.append([r, pid, str(lama), baru, str(ws.cell(row=r, column=VARC).value)])
    if apply and stat["diisi"]:
        wb.save(FILE)
    return stat, log


if __name__ == "__main__":
    print("MODE:", "APPLY (file DITULIS)" if APPLY else "DRY-RUN")
    stat, log = run(APPLY)
    for k, v in stat.most_common():
        print(f"   {v:4}  {k}")
    for x in log:
        print("   ", x)
