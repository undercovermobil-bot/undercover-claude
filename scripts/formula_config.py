"""Config skema SKU berbasis FORMULA (ukuran jahitan cover).

Aturan (dikonfirmasi user 2026-07-24):
  - Total Formula = 1            -> SEMUA generasi collapse jadi 1 kode = G1
                                    (dipaksa G1 walau master belum punya G1; master ikut diupdate)
  - Total Formula = jumlah grup  -> tiap grup 1 kode = nomor generasi PERTAMA di grup
  - Model bergenerasi-NAMA (bukan angka) tetap pakai nama (J40, KTK/KPS, 3P/5P, chassis BMW/Jeep)
"""
import re, json, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

FORMULA_XLSX = "/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/229eb2b0-Data_Mobil_Lebih_dari_1_Formula.xlsx"

# Model yg generasinya pakai NAMA/chassis, bukan angka -> JANGAN dipaksa G1.
# value = kode utk kasus collapse (TF=1); kalau per-row, kode diambil dari label grup.
NAMED_GEN = {
    "Toyota Hardtop": "J40",
    "Toyota HiAce": "COM",
    "Toyota Land Cruiser": "J60",
    "Toyota Starlet": None,     # per-row: Kotak->KTK, Kapsul->KPS
    "Suzuki Jimny": None,       # per-row: 3 Pintu->3P, 5 Pintu->5P
    "Suzuki SX4": None,         # X-Over / S-Cross
    "BMW M3": None,             # chassis E30/E36/...
    "Jeep Wrangler Rubicon": None,
    "Mini Cooper": None,        # DITUNDA - logic dari user belum ada
}
NAMED_LABEL_CODE = {
    "kotak": "KTK", "kapsul": "KPS",
    "3 pintu": "3P", "5 pintu": "5P",
    "commuter": "COM", "premio": "PRM",
    "x-over": "XOV", "s-cross": "SCR",
}

# Model yg BELUM bisa diproses (aturan belum lengkap) -> dilewati, dilaporkan ke user
BLOCKED = {
    "Nissan Livina X-Gear":   "Total Formula masih '?' di file",
    "Honda Civic Hatchback":  "Total Formula masih '?' di file",
    "Mitsubishi Strada Triton": "duplikat Mitsubishi Triton (ditandai ungu user)",
}

# Pengelompokan formula yang ditentukan user secara eksplisit, dipakai kalau daftar
# grup di file tidak sejumlah Total Formula.
#   nilai = daftar formula; tiap formula = (kode_SKU, [kata kunci yg dicari di teks varian])
# Nissan Navara (user 2026-07-27): formula 1 = Gen 1,2,3 ; formula 2 = PRO-4X.
#   PRO-4X di master sudah punya KODE MODEL sendiri (NVP) terpisah dari Navara (NVR),
#   jadi dua-duanya boleh memakai segmen G1 tanpa bertabrakan.
MANUAL_GROUPS = {
    "Nissan Navara": [
        ("G1", ["gen 1", "gen 2", "gen 3"]),
        ("G1", ["pro-4x", "pro 4x", "pro4x"]),
    ],
    # Mini Cooper (user 2026-07-27): "formula terbagi untuk 3 pintu dan 5 pintu saja,
    # kalau ada varian lain itu sama aja, kalaupun misal ada paceman 3 pintu bisa
    # dijadikan 3P saja". Jadi penentunya MURNI jumlah pintu; tipe bodi
    # (Hatch/Clubman/Countryman/Roadster/Paceman) diabaikan.
    # Kode 3P/5P konsisten dgn Suzuki Jimny yg sudah memakai konvensi sama.
    # Tipe bodi ikut didaftarkan karena FILE MASTER menulis generasi Mini Cooper
    # sbg nama bodi saja (Roadster/Paceman/Clubman/Countryman) tanpa jumlah pintu,
    # sementara LISTING selalu menulis "3 Pintu"/"5 Pintu". Tanpa ini master tidak
    # ikut tersamakan dan lookup-nya bertentangan dgn listing.
    # Penggolongan mengikuti jumlah pintu bawaan tiap bodi MINI:
    #   2-3 pintu -> 3P : Roadster, Coupe, Cabrio/Convertible, Paceman (contoh eksplisit user)
    #   5 pintu   -> 5P : Clubman, Countryman
    # Label "Hatch" polos TIDAK dipetakan di sini: user konfirmasi (2026-07-28) Hatch
    # punya versi 3 pintu MAUPUN 5 pintu, jadi satu baris master "Hatch" harus DIPECAH
    # jadi dua baris (3P & 5P) — ditangani `pecah_mini_hatch.py`, bukan oleh mapping ini.
    "Mini Cooper": [
        ("3P", ["3 pintu", "3pintu", "3-pintu",
                "roadster", "paceman", "coupe", "coupé", "cabrio", "convertible"]),
        ("5P", ["5 pintu", "5pintu", "5-pintu", "clubman", "countryman"]),
    ],
}

# Penyatuan nama yg merujuk produk sama (user: Gran Max dibedakan MB vs PU)
MERGE_NAME = {
    "Daihatsu Gran Max Pick Up": "Daihatsu Gran Max PU",
    "Daihatsu Gran Max Minibus": "Daihatsu Gran Max MB",
}

# Generasi tambahan yg ada di listing tapi belum tercatat di file formula.
# Hyundai Stargazer: TF=2, file cuma punya Gen 1 -> user konfirmasi ada Gen 2 (2025-2026).
EXTRA_GROUPS = {
    "Hyundai Stargazer": [{"label": "Gen 2 (2025-2026)", "nums": [2], "year": (2025, 2026), "code": "G2"}],
}


def _tfnum(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def _gen_nums(label):
    """nomor generasi dalam label grup: 'Gen 1-2'->[1,2], 'Gen 9,10,12'->[9,10,12]"""
    core = re.sub(r'\((?:19|20)\d{2}[^)]*\)', ' ', label)   # buang (tahun-tahun)
    m = re.search(r'gen\s*([0-9][0-9,\s&\-–]*)', core, re.I)
    if not m:
        return []
    nums = []
    for part in re.split(r'[,&\s]+', m.group(1)):
        rng = re.match(r'(\d+)\s*[-–]\s*(\d+)$', part)
        if rng:
            nums += list(range(int(rng.group(1)), int(rng.group(2)) + 1))
        elif part.isdigit():
            nums.append(int(part))
    return sorted(set(nums))


def _year(label):
    ys = [int(x) for x in re.findall(r'((?:19|20)\d{2})', label)]
    return (ys[0], ys[-1]) if ys else None


def _named_code(label):
    t = label.lower()
    for key, code in NAMED_LABEL_CODE.items():
        if key in t:
            return code
    m = re.match(r'\s*([A-Z]\d+|[A-Z]{2,3}\d*)\b', label)   # J40, E30, TJ, F70
    return m.group(1).upper() if m else None


def load(path=FORMULA_XLSX):
    wb = load_workbook(path, data_only=True)
    ws = wb["Sheet2"]
    last = 0
    for r in range(1, ws.max_row + 1):
        if any(ws.cell(row=r, column=c).value not in (None, "") for c in range(1, 7)):
            last = r

    raw = []
    cur = None
    for r in range(4, last + 1):
        nama = ws.cell(row=r, column=2).value
        gen = ws.cell(row=r, column=3).value
        tf = ws.cell(row=r, column=4).value
        if nama:
            cur = {"nama": str(nama).strip(), "gens": [], "tf": tf}
            raw.append(cur)
        if gen and cur is not None and str(gen).strip() != "-":
            cur["gens"].append(str(gen).strip())

    # gabung nama yg merujuk produk sama
    merged = {}
    for m in raw:
        nm = MERGE_NAME.get(m["nama"], m["nama"])
        if nm in merged:
            for g in m["gens"]:
                if g not in merged[nm]["gens"]:
                    merged[nm]["gens"].append(g)
            if _tfnum(merged[nm]["tf"]) is None:
                merged[nm]["tf"] = m["tf"]
        else:
            merged[nm] = {"nama": nm, "gens": list(m["gens"]), "tf": m["tf"]}

    config, blocked = {}, {}
    for nm, m in merged.items():
        if nm in BLOCKED:
            blocked[nm] = BLOCKED[nm]
            continue
        tf = _tfnum(m["tf"])
        if tf is None:
            blocked[nm] = f"Total Formula tidak terbaca ({m['tf']!r})"
            continue

        groups = []
        for g in m["gens"]:
            nums = _gen_nums(g)
            groups.append({"label": g, "nums": nums, "year": _year(g),
                           "code": f"G{nums[0]}" if nums else _named_code(g)})
        groups += EXTRA_GROUPS.get(nm, [])

        if not groups:
            # TF=1 tanpa daftar generasi -> tetap collapse ke G1
            if tf == 1:
                config[nm] = {"tf": 1, "collapse": True, "code": "G1", "groups": []}
            else:
                blocked[nm] = "tidak ada data generasi"
            continue

        if nm in MANUAL_GROUPS:
            config[nm] = {"tf": tf, "collapse": False, "code": None,
                          "groups": groups, "manual": MANUAL_GROUPS[nm]}
            continue

        if tf == 1:
            named = NAMED_GEN.get(nm, "MISSING")
            if named != "MISSING" and named:
                code = named                      # Hardtop->J40, HiAce->COM, LandCruiser->J60
            elif any(g["nums"] for g in groups):
                code = "G1"                       # user: collapse SELALU G1
            else:
                code = groups[0]["code"] or "G1"  # semua grup bernama -> pakai grup pertama
            config[nm] = {"tf": 1, "collapse": True, "code": code, "groups": groups}
        elif tf == len(groups):
            config[nm] = {"tf": tf, "collapse": False, "code": None, "groups": groups}
        else:
            blocked[nm] = f"TF={tf} tapi {len(groups)} grup - belum jelas grup mana berbagi formula"

    return config, blocked


def seg_for_variant(cfg, var):
    """segmen generasi baru utk sebuah teks varian; None kalau tak bisa ditentukan"""
    if cfg["collapse"]:
        return cfg["code"]
    v = var.lower()
    if cfg.get("manual"):                       # pengelompokan eksplisit dari user
        for code, keys in cfg["manual"]:
            if any(k in v for k in keys):
                return code
        return None
    for g in cfg["groups"]:                     # 1) label bernama (Kotak/Kapsul/3 Pintu/chassis)
        if not g["nums"] and g["code"]:
            key = g["label"].lower().split("(")[0].strip()
            if key and key in v:
                return g["code"]
    mg = re.search(r'gen\s*([0-9]+)', var, re.I)  # 2) nomor generasi di teks varian
    if mg:
        n = int(mg.group(1))
        for g in cfg["groups"]:
            if n in g["nums"]:
                return g["code"]
    ys = [int(x) for x in re.findall(r'((?:19|20)\d{2})', var)]  # 3) rentang tahun
    if ys:
        lo, hi = ys[0], ys[-1]
        best = None
        for g in cfg["groups"]:
            if g["year"] and max(lo, g["year"][0]) <= min(hi, g["year"][1]):
                ov = min(hi, g["year"][1]) - max(lo, g["year"][0])
                if best is None or ov > best[0]:
                    best = (ov, g["code"])
        if best:
            return best[1]
    return None


if __name__ == "__main__":
    cfg, blocked = load()
    print(f"model siap diproses : {len(cfg)}")
    print(f"model DITUNDA       : {len(blocked)}")
    for k, v in blocked.items():
        print(f"   - {k}: {v}")
    for nm in ["Toyota Kijang", "Toyota Avanza", "Toyota Corolla", "Toyota Vellfire",
               "Daihatsu Rocky", "Honda HRV", "Hyundai Stargazer", "Toyota Hardtop",
               "Daihatsu Gran Max PU", "Daihatsu Gran Max MB"]:
        c = cfg.get(nm)
        if c:
            print(f"\n{nm}  TF={c['tf']} collapse={c['collapse']} code={c['code']}")
            for g in c["groups"]:
                print(f"     {str(g['code']):5} <- {g['label'][:44]}")
