"""Buat baris MASTER untuk brand yang listing-nya sudah ada tapi sheet master-nya kosong.

Konteks (2026-07-29): 7 brand — Bentley, Aston Martin, Rolls-Royce, Infiniti, Neta,
Maxus, iCAR — punya 1.938 baris listing di Undercover Autocare tapi TIDAK SATU PUN
punya SKU, karena sheet master-nya kosong sehingga resolver tidak punya rujukan.

Instruksi user: "buatkan listing produknya di master, yg sudah ada di e-commerce
generasinya disamakan seperti di e-commerce aja" -> label generasi & rentang tahun
diambil PERSIS dari teks varian listing, bukan dikarang.

Template baris mengikuti brand kecil yang sudah ada (Tesla/GAC Aion/Geely):
68 baris per (model x generasi) = 4 toko x 17 baris
    Exclusive : 1  (Abu-abu)
    Premium   : 2  (Abu-abu, Silver)
    Strip     : 9  (UA/OT: Elite/Epic/Warrior x Abu/Biru/Merah;
                    SP/OP: Strip 1/2/3 x Abu/Biru/Merah)
    Reguler   : 5  (Abu-abu, Biru Benhur, Hijau Army, Hitam, Merah)
Kategori Transparan hanya dibuat kalau listing brand itu memang punya Transparan.

Kode toko di SKU mengikuti konvensi proyek: Undercover Autocare & Otonation -> UA,
Smartprotection & Otoprotection -> SP.
"""
import warnings, re, sys
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

import files_baru as FB

APPLY = "--apply" in sys.argv
MASTERS = ["MASTER_from_drive_20260715.xlsx", "SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"]

BRAND = {
    "Bentley": (["bentley"], "BTL"),
    "Aston Martin": (["aston martin"], "AST"),
    "Rolls-Royce": (["rolls royce", "rolls-royce"], "RRC"),
    "Infiniti": (["infiniti"], "INF"),
    "Neta": (["neta"], "NET"),
    "Maxus": (["maxus"], "MXS"),
    "iCAR": (["icar"], "ICR"),
}
# nama sheet di master (beda tulisan dgn nama brand di listing)
SHEET = {"Bentley": "Bentley", "Aston Martin": "Aston Martin", "Rolls-Royce": "Rolls-Royce",
         "Infiniti": "Infiniti", "Neta": "Neta", "Maxus": "Maxus", "iCAR": "iCAR"}

KATA_KAT = (("premium", "Premium"), ("exclusive", "Exclusive"),
            ("transparan", "Transparan"), ("strip", "Strip"), ("reguler", "Reguler"))
TOKO = [("Undercover Autocare", "UA"), ("Otonation", "UA"),
        ("Smartprotection", "SP"), ("Otoprotection", "SP")]
KODE_KAT = {"Reguler": "R", "Strip": "S", "Premium": "P", "Exclusive": "E", "Transparan": "T"}
WARNA_KODE = {
    "Abu-abu": "ABU", "Silver": "SLV", "Hitam": "HTM", "Merah": "MRH",
    "Biru Benhur": "BRU", "Hijau Army": "GRN", "Transparan": "TRP",
    "Elite Abu": "EAB", "Elite Biru": "EBR", "Elite Merah": "EMR",
    "Epic Abu": "PAB", "Epic Biru": "PBR", "Epic Merah": "PMR",
    "Warrior Abu": "WAB", "Warrior Biru": "WBR", "Warrior Merah": "WMR",
    "Strip 1 Abu": "S1A", "Strip 1 Biru": "S1B", "Strip 1 Merah": "S1M",
    "Strip 2 Abu": "S2A", "Strip 2 Biru": "S2B", "Strip 2 Merah": "S2M",
    "Strip 3 Abu": "S3A", "Strip 3 Biru": "S3B", "Strip 3 Merah": "S3M",
}
REGULER = ["Abu-abu", "Biru Benhur", "Hijau Army", "Hitam", "Merah"]
# label generasi yang dipakai >1 rentang tahun di listing -> dilaporkan, tidak dibuat
BENTROK_LABEL = []
STRIP_UA = ["Elite Abu", "Elite Biru", "Elite Merah", "Epic Abu", "Epic Biru",
            "Epic Merah", "Warrior Abu", "Warrior Biru", "Warrior Merah"]
STRIP_SP = ["Strip 1 Abu", "Strip 1 Biru", "Strip 1 Merah", "Strip 2 Abu", "Strip 2 Biru",
            "Strip 2 Merah", "Strip 3 Abu", "Strip 3 Biru", "Strip 3 Merah"]


def kategori(nama):
    low = str(nama).lower()
    for k, v in KATA_KAT:
        if k in low:
            return v
    return None


def nama_model(nama, brand):
    s = re.sub(r'undercover autocare\s*-\s*|\s*-\s*undercover autocare', ' ', str(nama), flags=re.I)
    s = re.sub(r'cover mobil|selimut mobil|body cover|/', ' ', s, flags=re.I)
    for k, _ in KATA_KAT:
        s = re.sub(k, ' ', s, flags=re.I)
    for kk in BRAND[brand][0]:
        s = re.sub(kk, ' ', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip()


def kode_model(model, dipakai):
    """kode 2-4 huruf dari nama model, unik dalam satu brand"""
    kata = [w for w in re.split(r'[^A-Za-z0-9]+', model) if w]
    if not kata:
        return "X"
    if len(kata) == 1:
        w = kata[0]
        c = (w[:3] if len(w) <= 4 else re.sub(r'[AEIOUaeiou]', '', w)[:3] or w[:3]).upper()
    else:
        c = "".join(w[0] for w in kata)[:4].upper()
    base, i = c, 2
    while c in dipakai:
        c = f"{base}{i}"
        i += 1
    return c


def pisah_gen(teks):
    """'Gen 1 (2019-2024)' -> ('Gen 1', '2019-2024'); 'Gen 1 : 2019-2024' juga"""
    t = str(teks).strip()
    th = ""
    m = re.search(r'((?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|now|sekarang))', t, re.I)
    if m:
        th = re.sub(r'\s*[-–]\s*', '-', m.group(1))
    label = re.sub(r'\s*[:(]\s*(?:19|20)\d{2}[^)]*\)?', '', t).strip(" :,-()")
    return (label or "Gen 1"), th


def baca_listing():
    """-> {(brand, model): {(gen_label, tahun): (jumlah, set(kategori))}}

    Kunci memakai (label, tahun) — BUKAN label saja — karena ada listing yang memberi
    label sama untuk rentang tahun berbeda (nyata: Aston Martin Vanquish punya
    'Gen 1 (2001-2007)' DAN 'Gen 1 (2022-2024)'). Kalau digabung, satu di antaranya
    hilang diam-diam.
    """
    data = defaultdict(lambda: defaultdict(lambda: [0, set()]))
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        ws = load_workbook(FB.path(f), data_only=True)[sheet]
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = " " + str(nm).lower() + " "
            brand = next((b for b, (ks, _) in BRAND.items() if any(x in low for x in ks)), None)
            if not brand:
                continue
            kat = kategori(nm)
            if not kat:
                continue
            model = nama_model(nm, brand)
            if not model:
                continue
            var = str(ws.cell(row=r, column=vc).value or "")
            bagian = [p.strip() for p in var.split(",") if p.strip()]
            gpart = [p for p in bagian
                     if re.search(r'\d{4}|gen\s*\d', p.lower())
                     and not re.search(r'model lain|custom|tahun lain', p.lower())]
            if not gpart:
                gpart = ["Gen 1"]
            for g in gpart:
                label, th = pisah_gen(g)
                slot = data[(brand, model)][(label, th)]
                slot[0] += 1
                slot[1].add(kat)
    return data


def bangun(data):
    """-> {sheet_master: [baris 9 kolom]}"""
    out = defaultdict(list)
    kode_per_brand = defaultdict(dict)
    for (brand, model) in sorted(data):
        dipakai = set(kode_per_brand[brand].values())
        kode_per_brand[brand][model] = kode_model(model, dipakai)

    for (brand, model) in sorted(data):
        bkode = BRAND[brand][1]
        mkode = kode_per_brand[brand][model]
        nama_produk = f"{brand} {model}".replace("  ", " ").strip()
        no = len(out[SHEET[brand]]) // 68 + 1

        # Satu label generasi hanya boleh punya SATU rentang tahun, kalau tidak segmen
        # SKU-nya bertabrakan. Kalau listing memberi label sama untuk 2 rentang tahun,
        # yang dipakai adalah yang barisnya paling banyak; sisanya DILAPORKAN, tidak
        # ditebak sendiri — perbaikannya harus di label listing-nya.
        terpilih, per_label = {}, defaultdict(list)
        for (label, th), (n, kats) in data[(brand, model)].items():
            per_label[label].append((n, th, kats))
        for label, kandidat in per_label.items():
            kandidat.sort(reverse=True)
            terpilih[label] = (kandidat[0][1], kandidat[0][2])
            for n, th, _ in kandidat[1:]:
                BENTROK_LABEL.append([brand, model, label, kandidat[0][1], th, n])

        for gen_label in sorted(terpilih):
            tahun, kats = terpilih[gen_label]
            for toko, tkode in TOKO:
                rencana = [("Exclusive", ["Abu-abu"]),
                           ("Premium", ["Abu-abu", "Silver"]),
                           ("Strip", STRIP_UA if tkode == "UA" else STRIP_SP),
                           ("Reguler", REGULER)]
                if "Transparan" in kats:
                    rencana.append(("Transparan", ["Transparan"]))
                for kat, warnas in rencana:
                    for w in warnas:
                        sku = f"{bkode}-{mkode}-{tkode}-{KODE_KAT[kat]}-{gen_label.replace(' ', '').replace('Gen', 'G')}-{WARNA_KODE[w]}"
                        out[SHEET[brand]].append([
                            no, nama_produk, toko, kat, w, gen_label, tahun,
                            f"{nama_produk}-{toko}-{kat}-{w}-{gen_label}", sku,
                        ])
    return out


def main():
    data = baca_listing()
    out = bangun(data)

    print("=== RENCANA BARIS MASTER BARU ===")
    tot = 0
    for sheet in sorted(out):
        n = len(out[sheet])
        tot += n
        model = sorted({r[1] for r in out[sheet]})
        print(f"  {sheet:16} {n:5} baris  {len(model)} model")
        for m in model:
            gens = sorted({r[5] for r in out[sheet] if r[1] == m})
            contoh = next(r[8] for r in out[sheet] if r[1] == m)
            print(f"      {m:34} gen: {', '.join(gens)}   contoh SKU: {contoh}")
    print(f"\nTOTAL baris baru: {tot}")

    if BENTROK_LABEL:
        print(f"\n!! LABEL GENERASI DIPAKAI >1 RENTANG TAHUN ({len(BENTROK_LABEL)}) — "
              f"yang barisnya lebih sedikit TIDAK dibuat, perbaiki label di listing:")
        for b in BENTROK_LABEL:
            print(f"   {b[0]} {b[1]} — label '{b[2]}': dipakai {b[3]} (dipilih) "
                  f"dan {b[4]} ({b[5]} baris, dilewati)")

    # cek tabrakan SKU dgn yg sudah ada
    wb = load_workbook(MASTERS[0], data_only=True)
    ada = set()
    for s in wb.sheetnames:
        ws = wb[s]
        for r in range(2, ws.max_row + 1):
            v = ws.cell(row=r, column=9).value
            if isinstance(v, str):
                ada.add(v)
    baru = [r[8] for rows in out.values() for r in rows]
    bentrok = [s for s in baru if s in ada]
    print(f"SKU bentrok dgn master lama : {len(bentrok)}")
    print(f"SKU baru duplikat internal  : {len(baru) - len(set(baru))}")
    if bentrok:
        print("  contoh:", bentrok[:5])

    if not APPLY:
        print("\nmode: DRY-RUN (master TIDAK ditulis)")
        return
    if bentrok or len(baru) != len(set(baru)):
        print("\nDIBATALKAN: ada tabrakan SKU, perbaiki dulu.")
        return

    for mf in MASTERS:
        wbm = load_workbook(mf)
        for sheet, rows in out.items():
            ws = wbm[sheet]
            mulai = ws.max_row + 1
            # sheet kosong: baris 1 header, baris 2 kosong -> mulai dari baris 2
            if all(ws.cell(row=r, column=2).value is None for r in range(2, ws.max_row + 1)):
                mulai = 2
            for i, row in enumerate(rows):
                for c, v in enumerate(row, start=1):
                    ws.cell(row=mulai + i, column=c, value=v)
        wbm.save(mf)
        print(f"  ditulis ke {mf}")
    print("\nmode: APPLY (master DITULIS)")


if __name__ == "__main__":
    main()
