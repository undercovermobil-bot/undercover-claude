"""Cari apa yang ADA DI MASTER tapi BELUM ADA DI LISTING e-commerce.

Kebalikan dari `brand_belum_ada.py` (yang membandingkan master vs pasar Indonesia).
Di sini: master dianggap rencana produk, listing dianggap realisasi. Dua jenis celah:

  1. BELUM ADA        - model sama sekali tidak muncul di listing toko mana pun
  2. KURANG DI TOKO   - model sudah tayang di sebagian toko, belum di toko lain
                        (peluang paling cepat: produknya sudah terbukti, tinggal
                        direplikasi ke toko yang belum punya)

Pencocokan listing<->master pakai DUA cara, model dianggap ada kalau salah satu kena:
  A. lewat SKU  - prefix `KODEMEREK-KODEMODEL` di kolom SKU listing. Paling akurat,
                  tapi gagal untuk baris yang SKU-nya masih kosong/legacy.
  B. lewat NAMA - nama produk listing dinormalisasi lalu dicocokkan ke nama model
                  master. Menangkap baris yang belum punya SKU.
Cara A saja tidak cukup: banyak listing yang justru belum ber-SKU — itu malah yang
sering jadi target. Cara B saja tidak cukup: penulisan nama antar toko beda-beda.
"""
import warnings, re
warnings.filterwarnings("ignore")
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from collections import defaultdict, Counter

import files_baru as FB

MASTER = "MASTER_from_drive_20260715.xlsx"
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
HDR_FONT = Font(color="FFFFFF", bold=True)
KUNING = PatternFill("solid", fgColor="FFEB9C")
MERAH = PatternFill("solid", fgColor="FFC7CE")
TOKO_KODE = {"Undercover Autocare": "UA", "Otonation": "OT",
             "Smartprotection": "SP", "Otoprotection": "OP"}
BOILER = set((
    "undercover autocare otonation otoprotection smartprotection ottonation "
    "cover mobil selimut karpet body sarung reguler regular premium exclusive "
    "strip transparan outdoor indoor extreme out the all new"
).split())


def norm(s):
    t = re.sub(r'\(?(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|now|sekarang)\)?', ' ', str(s).lower())
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return "".join(w for w in t.split() if w not in BOILER)


def baca_master():
    """-> {(sheet, nama_produk): {'prefix': set, 'toko': set, 'gen': set, 'kat': set}}"""
    wb = load_workbook(MASTER, data_only=True)
    d = defaultdict(lambda: {"prefix": set(), "toko": set(), "gen": set(), "kat": set()})
    for s in wb.sheetnames:
        ws = wb[s]
        for r in range(3, ws.max_row + 1):
            nm = ws.cell(row=r, column=2).value
            if not nm:
                continue
            e = d[(s, str(nm).strip())]
            tk = TOKO_KODE.get(str(ws.cell(row=r, column=3).value or "").strip())
            if tk:
                e["toko"].add(tk)
            g = ws.cell(row=r, column=6).value
            if g:
                e["gen"].add(str(g).strip())
            k = ws.cell(row=r, column=4).value
            if k:
                e["kat"].add(str(k).strip())
            sku = ws.cell(row=r, column=9).value
            if isinstance(sku, str) and sku.count("-") == 5:
                p = sku.split("-")
                e["prefix"].add(f"{p[0]}-{p[1]}")
    return d


def baca_listing():
    """-> (prefix_per_toko, nama_ternormalisasi_per_toko)"""
    pref = defaultdict(set)     # 'BTL-FS' -> {'UA','SP',...}
    nama = defaultdict(set)     # nama ternormalisasi -> {toko}
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        ws = load_workbook(FB.path(f), data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = str(nm).lower()
            if "motor" in low or "karpet" in low:
                continue
            nama[norm(nm)].add(store)
            sku = ws.cell(row=r, column=sc).value
            if isinstance(sku, str):
                p = sku.split("_")[0].split("-")
                if len(p) == 6:
                    pref[f"{p[0]}-{p[1]}"].add(store)
    return pref, nama


def main():
    master = baca_master()
    pref_listing, nama_listing = baca_listing()
    nama_keys = list(nama_listing)

    belum, kurang = [], []
    per_brand = defaultdict(lambda: [0, 0, 0])   # sheet -> [model, ada, belum]

    for (sheet, produk), e in sorted(master.items()):
        toko_ada = set()
        for p in e["prefix"]:
            toko_ada |= pref_listing.get(p, set())
        n = norm(produk)
        # Pencocokan nama harus KETAT. Versi longgar (`n in k or k in n` tanpa syarat
        # panjang pada k) salah besar: nama listing yang habis dibuang boilerplate-nya
        # jadi string KOSONG, dan string kosong itu "ada di dalam" semua nama — sehingga
        # SEMUA model terbaca sudah tayang. Nama pendek (mis. Zeekr "X" -> "zeekrx")
        # juga gampang nyangkut ke nama lain. Syarat sekarang: dua-duanya >= 6 karakter,
        # dan yang lebih pendek minimal 70% panjang yang lebih panjang.
        if len(n) >= 6:
            for k in nama_keys:
                if len(k) < 6:
                    continue
                if k == n:
                    toko_ada |= nama_listing[k]
                    continue
                pendek, panjang = (n, k) if len(n) <= len(k) else (k, n)
                if pendek in panjang and len(pendek) >= 0.7 * len(panjang):
                    toko_ada |= nama_listing[k]
        per_brand[sheet][0] += 1
        gen = ", ".join(sorted(e["gen"]))
        kat = ", ".join(sorted(e["kat"]))
        if not toko_ada:
            per_brand[sheet][2] += 1
            belum.append([sheet, produk, gen, kat, ", ".join(sorted(e["toko"])),
                          ", ".join(sorted(e["prefix"]))])
        else:
            per_brand[sheet][1] += 1
            kosong = sorted(e["toko"] - toko_ada)
            if kosong:
                kurang.append([sheet, produk, gen, ", ".join(sorted(toko_ada)),
                               ", ".join(kosong), len(kosong)])

    wb = Workbook()
    wb.remove(wb.active)

    def pasang_filter(ws, ncol):
        """dipanggil SETELAH semua baris terisi, supaya ref-nya lengkap dgn nomor baris"""
        if ws.max_row >= 1:
            ws.auto_filter.ref = f"A1:{get_column_letter(ncol)}{ws.max_row}"

    def head(ws, judul, lebar):
        ws.append(judul)
        for i, w in enumerate(lebar, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for c in range(1, len(judul) + 1):
            ws.cell(row=1, column=c).fill = HDR_FILL
            ws.cell(row=1, column=c).font = HDR_FONT
        ws.freeze_panes = "A2"
        # CATATAN: auto_filter.ref WAJIB memuat nomor baris ("A1:F120"), bukan cuma
        # kolom ("A1:F"). Tanpa nomor baris, xlsx-nya rusak dan Excel memunculkan
        # "We found a problem with some content". Karena barisnya baru diisi setelah
        # ini, filternya dipasang belakangan lewat `pasang_filter()`.

    ring = wb.create_sheet("RINGKASAN")
    head(ring, ["Brand", "Model di Master", "Sudah Tayang", "Belum Tayang", "% Tayang"],
         [28, 16, 15, 15, 12])
    for s in sorted(per_brand, key=lambda x: (-per_brand[x][2], x)):
        t, a, b = per_brand[s]
        ring.append([s, t, a, b, f"{100 * a // t if t else 0}%"])
        if b:
            ring.cell(row=ring.max_row, column=4).fill = MERAH
    tt = sum(v[0] for v in per_brand.values())
    ta = sum(v[1] for v in per_brand.values())
    ring.append([])
    ring.append(["TOTAL", tt, ta, tt - ta, f"{100 * ta // tt}%"])
    ring.cell(row=ring.max_row, column=1).font = Font(bold=True)

    ws1 = wb.create_sheet("BELUM ADA DI LISTING")
    head(ws1, ["Brand", "Model", "Generasi di Master", "Kategori Tersedia",
               "Toko di Master", "Prefix SKU"], [24, 34, 40, 34, 18, 22])
    for b in sorted(belum):
        ws1.append(b)
        ws1.cell(row=ws1.max_row, column=3).alignment = Alignment(wrap_text=True)

    ws2 = wb.create_sheet("KURANG DI TOKO")
    head(ws2, ["Brand", "Model", "Generasi", "Sudah Tayang di", "Belum Tayang di",
               "Jml Toko Kurang"], [24, 34, 40, 20, 20, 16])
    for k in sorted(kurang, key=lambda x: (-x[5], x[0], x[1])):
        ws2.append(k)
        ws2.cell(row=ws2.max_row, column=5).fill = KUNING

    pasang_filter(ring, 5)
    pasang_filter(ws1, 6)
    pasang_filter(ws2, 6)
    wb.save("Belum_Ada_Di_Listing.xlsx")

    print(f"model di master        : {tt}")
    print(f"sudah tayang           : {ta}")
    print(f"BELUM tayang sama sekali: {tt - ta}")
    print(f"kurang di sebagian toko : {len(kurang)}")
    print("\n=== brand dgn model belum tayang terbanyak ===")
    for s in sorted(per_brand, key=lambda x: -per_brand[x][2])[:20]:
        t, a, b = per_brand[s]
        if b:
            print(f"  {s:26} {b:4} belum / {t} model")


if __name__ == "__main__":
    main()
