"""Samakan MASTER_from_drive_20260715.xlsx dengan SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx.

Latar: user memutuskan file **Tracking dijadikan acuan/patokan**, setelah ditemukan
file itu punya 5 brand dengan model TAMBAHAN yang tidak ada di file Master
(Lamborghini Huracan, Tesla Model 3/X, Volvo 6 model, Lexus LC/LS/UX, Maserati Ghibli).
Ini perbedaan LAMA (dari sebelum sesi ini), bukan dari pekerjaan hari ini — sepanjang
sesi ini kedua file selalu ditulis identik.

PENTING: beberapa skrip (`rebuild_lookup.py`, `belum_ada_di_listing.py`,
`brand_belum_ada.py`) HANYA membaca `MASTER_from_drive_20260715.xlsx`. Kalau file itu
kekurangan model, lookup & analisa gap yang dibuat skrip2 itu ikut salah/kurang
lengkap tanpa disadari. Solusinya BUKAN mengganti nama file di tiap skrip (banyak &
rawan salah satu terlewat), tapi menyamakan ISI kedua file jadi identik — supaya
`MASTER_from_drive_20260715.xlsx` otomatis sudah lengkap utk skrip mana pun yg membacanya.

Metode: kunci alami (Nama Produk, Toko, Kategori, Warna, Generasi) dicocokkan DUA ARAH.
  - baris ada di Tracking, tidak di Master -> disalin ke Master
  - baris ada di Master, tidak di Tracking -> disalin ke Tracking
  - kunci sama tapi SKU beda -> DILAPORKAN, TIDAK ditimpa otomatis (butuh keputusan user)
"""
import warnings, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

APPLY = "--apply" in sys.argv
MASTER = "MASTER_from_drive_20260715.xlsx"
TRACKING = "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"


def baca(fn):
    """-> {sheet: {key: (row_values, sku)}}"""
    wb = load_workbook(fn, data_only=True)
    out = {}
    for s in wb.sheetnames:
        ws = wb[s]
        d = {}
        for r in range(3, ws.max_row + 1):
            nm = ws.cell(row=r, column=2).value
            if not nm:
                continue
            key = (str(nm).strip(), str(ws.cell(row=r, column=3).value or "").strip(),
                   str(ws.cell(row=r, column=4).value or "").strip(),
                   str(ws.cell(row=r, column=5).value or "").strip(),
                   str(ws.cell(row=r, column=6).value or "").strip())
            row = [ws.cell(row=r, column=c).value for c in range(1, 10)]
            d[key] = row
        out[s] = d
    return out


def main():
    m = baca(MASTER)
    t = baca(TRACKING)

    hanya_t, hanya_m, beda_sku = [], [], []
    for s in set(m) | set(t):
        km, kt = m.get(s, {}), t.get(s, {})
        for key in kt:
            if key not in km:
                hanya_t.append((s, key, kt[key]))
            elif str(km[key][8]) != str(kt[key][8]):
                beda_sku.append((s, key, km[key][8], kt[key][8]))
        for key in km:
            if key not in kt:
                hanya_m.append((s, key, km[key]))

    print(f"baris hanya di TRACKING (akan disalin ke Master)  : {len(hanya_t)}")
    print(f"baris hanya di MASTER   (akan disalin ke Tracking) : {len(hanya_m)}")
    print(f"kunci sama, SKU BEDA (perlu keputusan, TIDAK diapa2kan): {len(beda_sku)}")
    if beda_sku:
        print("\n=== SKU BERBEDA UTK KUNCI SAMA (dilaporkan saja) ===")
        for s, key, skum, skut in beda_sku[:15]:
            print(f"   [{s}] {key} -> master={skum!r} tracking={skut!r}")

    print("\n=== rincian per sheet: hanya di Tracking ===")
    from collections import Counter
    c = Counter(x[0] for x in hanya_t)
    for s, n in c.most_common():
        print(f"   {s:20} {n:4} baris")

    if not APPLY:
        print("\nmode: DRY-RUN (file TIDAK ditulis)")
        return

    wbm = load_workbook(MASTER)
    for s, key, row in hanya_t:
        ws = wbm[s]
        r = ws.max_row + 1
        for c, v in enumerate(row, start=1):
            ws.cell(row=r, column=c, value=v)
    wbm.save(MASTER)

    wbt = load_workbook(TRACKING)
    for s, key, row in hanya_m:
        ws = wbt[s]
        r = ws.max_row + 1
        for c, v in enumerate(row, start=1):
            ws.cell(row=r, column=c, value=v)
    wbt.save(TRACKING)

    print(f"\nditulis: {len(hanya_t)} baris ke {MASTER}, {len(hanya_m)} baris ke {TRACKING}")
    print("mode: APPLY (kedua file DITULIS, sekarang identik)")


if __name__ == "__main__":
    main()
