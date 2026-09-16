"""Daftar kerja: brand yang SUDAH punya listing e-commerce tapi sheet master-nya KOSONG.

Ketemu 2026-07-29: 7 brand (Bentley, Aston Martin, Rolls-Royce, Infiniti, Neta,
Maxus, iCAR) punya total 1.938 baris listing di Undercover Autocare, tapi TIDAK SATU
PUN punya SKU 6 segmen — karena sheet master brand-nya kosong, resolver tidak punya
rujukan sama sekali.

Keluaran `Brand_Perlu_Master.xlsx`:
  RINGKASAN   - per brand: jumlah baris, listing unik, status SKU
  DAFTAR ISI MASTER - baris unik (brand, model, kategori, generasi, warna) yang perlu
                dibuat di master. Ini persis kolom yang dipakai master, jadi tinggal
                disalin ke sheet brand-nya.
  SEMUA BARIS - seluruh 1.938 baris listing + lokasinya, untuk cek manual
"""
import warnings, re
warnings.filterwarnings("ignore")
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from collections import defaultdict, Counter

import files_baru as FB

BRAND = {
    "Bentley": ["bentley"], "Aston Martin": ["aston martin"],
    "Rolls-Royce": ["rolls royce", "rolls-royce"], "Infiniti": ["infiniti"],
    "Neta": ["neta"], "Maxus": ["maxus"], "iCAR": ["icar"],
}
KAT = (("premium", "Premium"), ("exclusive", "Exclusive"),
       ("transparan", "Transparan"), ("strip", "Strip"), ("reguler", "Reguler"))
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
HDR_FONT = Font(color="FFFFFF", bold=True)
WARNA_KATA = ("abu-abu", "abu", "hitam", "merah", "biru benhur", "biru",
              "hijau army", "hijau", "silver", "putih", "transparan", "orange")


def kategori(nama):
    low = str(nama).lower()
    for k, v in KAT:
        if k in low:
            return v
    return "(tidak disebut)"


def model_dari(nama, brand):
    """buang boilerplate toko & kata kategori -> nama model"""
    s = re.sub(r'undercover autocare\s*-\s*|\s*-\s*undercover autocare', ' ', str(nama), flags=re.I)
    s = re.sub(r'cover mobil|selimut mobil|body cover|/', ' ', s, flags=re.I)
    for k, _ in KAT:
        s = re.sub(k, ' ', s, flags=re.I)
    for kk in BRAND[brand]:
        s = re.sub(kk, ' ', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip() or "(tanpa model)"


def pecah_varian(var):
    """teks varian -> (generasi, warna) sebisanya"""
    v = str(var or "").strip()
    if not v:
        return "", ""
    bagian = [b.strip() for b in v.split(",") if b.strip()]
    gen = warna = ""
    for b in bagian:
        low = b.lower()
        if re.search(r'\d{4}|gen\s*\d|model|tahun|custom', low):
            gen = gen or b
        elif any(w in low for w in WARNA_KATA):
            warna = warna or b
        else:
            gen = gen or b
    return gen, warna


def main():
    baris = []
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        ws = load_workbook(FB.path(f), data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = " " + str(nm).lower() + " "
            b = next((k for k, keys in BRAND.items() if any(x in low for x in keys)), None)
            if not b:
                continue
            sku = ws.cell(row=r, column=sc).value
            var = ws.cell(row=r, column=vc).value
            g, w = pecah_varian(var)
            baris.append({
                "brand": b, "model": model_dari(nm, b), "kat": kategori(nm),
                "gen": g, "warna": w, "nama": str(nm), "var": str(var or ""),
                "sku": "" if sku in (None, "") else str(sku),
                "store": store, "chan": chan, "file": f, "row": r,
            })

    wb = Workbook()
    wb.remove(wb.active)

    def head(ws, judul, lebar):
        ws.append(judul)
        for i, w in enumerate(lebar, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for c in range(1, len(judul) + 1):
            ws.cell(row=1, column=c).fill = HDR_FILL
            ws.cell(row=1, column=c).font = HDR_FONT
        ws.freeze_panes = "A2"

    ring = wb.create_sheet("RINGKASAN")
    head(ring, ["Brand", "Baris Listing", "Listing Unik", "Model Unik",
                "SKU Kosong", "SKU Non-standar", "SKU 6 Segmen"], [20, 15, 14, 13, 14, 17, 15])
    per = defaultdict(list)
    for x in baris:
        per[x["brand"]].append(x)
    for b in sorted(per, key=lambda k: -len(per[k])):
        g = per[b]
        ok = sum(1 for x in g if len(x["sku"].split("_")[0].split("-")) == 6 and x["sku"])
        kos = sum(1 for x in g if not x["sku"])
        ring.append([b, len(g), len({x["nama"] for x in g}), len({x["model"] for x in g}),
                     kos, len(g) - kos - ok, ok])
    ring.append([])
    ring.append(["TOTAL", len(baris), len({x["nama"] for x in baris}),
                 len({(x["brand"], x["model"]) for x in baris}),
                 sum(1 for x in baris if not x["sku"]), "", ""])
    ring.cell(row=ring.max_row, column=1).font = Font(bold=True)

    isi = wb.create_sheet("DAFTAR ISI MASTER")
    head(isi, ["Brand", "Nama Produk (model)", "Kategori", "Generasi", "Warna", "Jumlah Baris"],
         [18, 34, 16, 30, 20, 14])
    agg = Counter((x["brand"], x["model"], x["kat"], x["gen"], x["warna"]) for x in baris)
    for k, n in sorted(agg.items()):
        isi.append(list(k) + [n])
    isi.auto_filter.ref = f"A1:F{isi.max_row}"

    semua = wb.create_sheet("SEMUA BARIS")
    head(semua, ["Brand", "Nama Produk", "Varian", "SKU Sekarang", "Toko", "Channel",
                 "File", "Baris"], [16, 58, 34, 22, 8, 12, 20, 8])
    for x in sorted(baris, key=lambda y: (y["brand"], y["nama"], y["var"])):
        semua.append([x["brand"], x["nama"], x["var"], x["sku"], x["store"],
                      x["chan"], x["file"], x["row"]])
    semua.auto_filter.ref = f"A1:H{semua.max_row}"

    wb.save("Brand_Perlu_Master.xlsx")
    print(f"total baris          : {len(baris)}")
    print(f"listing unik         : {len({x['nama'] for x in baris})}")
    print(f"kombinasi utk master : {len(agg)}")
    print(f"SKU kosong           : {sum(1 for x in baris if not x['sku'])}")


if __name__ == "__main__":
    main()
