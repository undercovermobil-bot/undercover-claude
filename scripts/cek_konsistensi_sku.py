"""Double-check penulisan SKU + kecocokan antar toko (permintaan user 2026-07-28).

Enam pemeriksaan, semuanya dijalankan atas isi sel file hasil (BARU_FIX/), bukan
atas laporan skrip lain:

  1. BENTUK      — harus 6 segmen; kode toko sah; kode kategori 1 huruf; tidak ada
                   karakter aneh (kasus nyata: `NSN-NVP-SP-S-G$-S3A`).
  2. KODE TOKO   — segmen ke-3 harus sesuai konvensi file: Otonation memakai kode UA,
                   Otoprotection memakai kode SP (by design, lihat master).
  3. KODE MODEL  — satu produk (nama dinormalisasi) harus memakai segmen merek+model
                   yang SAMA di semua toko/channel.
  4. KATEGORI    — huruf kategori harus cocok dgn kata di nama produk
                   (Reguler->R, Premium->P, Exclusive->E, Transparan->T, Strip->S).
  5. GENERASI    — produk+label generasi yang sama harus memakai segmen generasi yang
                   sama di semua toko.
  6. WARNA       — kata warna yang sama harus memakai kode warna yang sama
                   (dibandingkan DALAM keluarga toko: UA/OT memakai Epic/Elite/Warrior,
                   SP/OP memakai Strip 1/2/3, jadi lintas keluarga tidak dibandingkan).

Keluaran ditulis ke `_cek_konsistensi.json` supaya bisa dijadikan lampiran Excel.
"""
import warnings, re, json
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter, defaultdict

import files_baru as FB
import apply_formula_sku as AF

SAH_TOKO = {"UA", "OT", "SP", "OP"}
# Konvensi kode toko per file, diukur dari data MENTAH 2026-07-28 dan 100% konsisten:
#   UA -> UA, Otonation -> UA, SP -> SP, Otoprotection -> SP.
# Sengaja ketat: kalau ada baris berkode OT/OP, itu memang menyimpang dan harus muncul.
KODE_HARAP = {"UA": {"UA"}, "OT": {"UA"}, "SP": {"SP"}, "OP": {"SP"}}
KELUARGA = {"UA": "UA/OT", "OT": "UA/OT", "SP": "SP/OP", "OP": "SP/OP"}
KAT_DARI_NAMA = [("premium", "P"), ("exclusive", "E"), ("transparan", "T"), ("reguler", "R"), ("regular", "R")]
SEGMEN_OK = re.compile(r'^[A-Za-z0-9]+$')
WARNA_KATA = ("abu", "hitam", "merah", "biru", "hijau", "silver", "putih", "transparan")


def norm_nama(nm):
    return "".join(AF._toks(AF._prenorm(nm)))


def gen_label(var):
    """ambil bagian teks varian yang menyatakan generasi/tipe, bukan warna"""
    bagian = [b.strip() for b in str(var).split(",")]
    for b in bagian:
        low = b.lower()
        if re.search(r'\d{4}|gen\s*\d|pintu|kotak|kapsul|model|tahun|custom', low):
            return re.sub(r'\s+', " ", low)
    return None


def warna_kata(var):
    low = str(var).lower()
    for w in WARNA_KATA:
        if w in low:
            m = re.search(r'((?:elite|epic|warrior|strip\s*[123])\s+)?' + w + r'[a-z]*', low)
            return re.sub(r'\s+', " ", m.group(0)).strip() if m else w
    return None


def main():
    baris = []
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        ws = load_workbook(FB.path(f), data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = str(nm).lower()
            if "motor" in low or "karpet" in low:
                continue
            s = ws.cell(row=r, column=sc).value
            if not isinstance(s, str) or not s.strip():
                continue
            baris.append({"toko": store, "file": f, "row": r, "nama": str(nm),
                          "var": str(ws.cell(row=r, column=vc).value or ""),
                          "sku": s.split("_")[0], "sku_penuh": s})

    temuan = defaultdict(list)

    # ---- 1 & 2: bentuk + kode toko
    for b in baris:
        p = b["sku"].split("-")
        if len(p) != 6:
            temuan["1_bentuk_bukan_6_segmen"].append([b["file"], b["row"], b["sku"], b["nama"][:55]])
            continue
        if not all(SEGMEN_OK.match(x) for x in p):
            temuan["1_karakter_aneh"].append([b["file"], b["row"], b["sku"], b["nama"][:55]])
        if p[2] not in SAH_TOKO:
            temuan["1_kode_toko_tidak_sah"].append([b["file"], b["row"], b["sku"], b["nama"][:55]])
        elif p[2] not in KODE_HARAP[b["toko"]]:
            temuan["2_kode_toko_salah"].append([b["file"], b["row"], b["sku"],
                                                f"harusnya {'/'.join(sorted(KODE_HARAP[b['toko']]))}", b["nama"][:55]])
        if len(p[3]) != 1:
            temuan["1_kategori_bukan_1_huruf"].append([b["file"], b["row"], b["sku"], b["nama"][:55]])

    valid = [b for b in baris if len(b["sku"].split("-")) == 6]

    # ---- 3: kode model konsisten antar toko
    per_nama = defaultdict(lambda: defaultdict(Counter))
    for b in valid:
        p = b["sku"].split("-")
        per_nama[norm_nama(b["nama"])][f"{p[0]}-{p[1]}"][b["toko"]] += 1
    for nama, kodes in per_nama.items():
        if len(kodes) > 1:
            rinci = {k: dict(v) for k, v in kodes.items()}
            temuan["3_kode_model_beda_antar_toko"].append([nama, rinci])

    # ---- 4: kategori vs nama produk
    for b in valid:
        p = b["sku"].split("-")
        low = b["nama"].lower()
        harap = None
        for kata, kode in KAT_DARI_NAMA:
            if kata in low:
                harap = kode
                break
        if harap and p[3] != harap:
            # listing "Reguler" boleh berisi tier Strip -> kategori S masih sah
            if not (harap == "R" and p[3] == "S"):
                temuan["4_kategori_tidak_cocok_nama"].append(
                    [b["file"], b["row"], b["sku"], f"nama bilang {harap}", b["nama"][:55]])

    # ---- 5: generasi konsisten antar toko
    per_gen = defaultdict(lambda: defaultdict(Counter))
    for b in valid:
        g = gen_label(b["var"])
        if not g:
            continue
        p = b["sku"].split("-")
        per_gen[(norm_nama(b["nama"]), f"{p[0]}-{p[1]}", p[3], g)][p[4]][b["toko"]] += 1
    for key, segs in per_gen.items():
        if len(segs) > 1:
            temuan["5_segmen_generasi_beda_antar_toko"].append(
                [list(key), {k: dict(v) for k, v in segs.items()}])

    # ---- 6: warna konsisten (dalam keluarga toko)
    per_warna = defaultdict(lambda: defaultdict(Counter))
    for b in valid:
        w = warna_kata(b["var"])
        if not w:
            continue
        p = b["sku"].split("-")
        per_warna[(KELUARGA[b["toko"]], p[3], w)][p[5]][b["toko"]] += 1
    for key, kodes in per_warna.items():
        if len(kodes) > 1:
            temuan["6_kode_warna_beda"].append([list(key), {k: dict(v) for k, v in kodes.items()}])

    # ---- 7: satu SKU dipakai oleh >1 PRODUK berbeda (tabrakan kode model)
    #        Kembar dalam satu produk itu wajar (varian beda kolaps ke 1 formula),
    #        tapi SKU yg sama dipakai dua produk berbeda = kode model bertabrakan.
    per_sku = defaultdict(set)
    for b in valid:
        per_sku[b["sku"]].add(norm_nama(b["nama"]))
    for sku, namas in per_sku.items():
        if len(namas) > 1:
            temuan["7_satu_sku_dipakai_beda_produk"].append([sku, sorted(namas)])

    print(f"total baris cover mobil ber-SKU: {len(baris)}   (bentuk 6 segmen: {len(valid)})")
    print()
    for k in sorted(temuan):
        print(f"=== {k}: {len(temuan[k])} ===")
        for x in temuan[k][:12]:
            print("   ", x)
        if len(temuan[k]) > 12:
            print(f"    ... dan {len(temuan[k]) - 12} lagi")
        print()
    if not temuan:
        print("TIDAK ADA TEMUAN — semua konsisten.")
    json.dump({k: v for k, v in temuan.items()}, open("_cek_konsistensi.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
