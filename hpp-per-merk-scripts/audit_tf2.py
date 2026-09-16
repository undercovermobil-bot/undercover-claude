"""Audit ulang Total Formula (Sheet2) - kali ini dikelompokkan PER ENTRI FORMULA,
bukan per nama model di master. Audit sebelumnya salah: 'Daihatsu Xenia' dianggap
melanggar padahal kode G3-nya dipegang baris bernama 'Daihatsu All New Xenia'."""
import json, re
from collections import defaultdict
from master_lib import muat

f = json.load(open("formula_sheet2.json"))


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


# nama entri formula, panjang dulu supaya "Toyota Corolla Cross" menang atas "Toyota Corolla"
entri = sorted(f, key=lambda e: -len(str(e["nama"])))
nama_entri = [(norm(e["nama"]), e) for e in entri]

# varian penulisan di master yang menunjuk model yang sama
def kandidat(nama):
    n = norm(nama)
    out = [n]
    for pola in (r"^(\w+) all new ", r"^(\w+) new "):
        m = re.match(pola, n)
        if m:
            out.append(re.sub(pola, r"\1 ", n))
    return out


d = muat()
pakai = defaultdict(lambda: defaultdict(set))   # entri -> nama master -> {kode gen}
tak_cocok = defaultdict(set)

for sheet, rows in d.items():
    for r in rows[2:]:
        if not r or not r[1] or not r[8]:
            continue
        sku = str(r[8])
        p = sku.split("-")
        if len(p) < 6:
            continue
        kode = p[4]
        cocok = None
        for ne, e in nama_entri:
            if any(k == ne or k.startswith(ne + " ") or k.startswith(ne + "/") for k in kandidat(r[1])):
                cocok = e
                break
        if cocok is None:
            tak_cocok[r[1]].add(kode)
        else:
            pakai[cocok["nama"]][r[1]].add(kode)

def tf_int(e):
    try:
        return int(e["tf"])
    except (TypeError, ValueError):
        return None


langgar = []
tf_kosong = []
for e in f:
    nm = e["nama"]
    if nm not in pakai:
        continue
    if tf_int(e) is None:
        tf_kosong.append(nm)
        continue
    kode = set()
    for s in pakai[nm].values():
        kode |= s
    if len(kode) > tf_int(e):
        langgar.append((nm, tf_int(e), sorted(kode), sorted(pakai[nm])))

print(f"entri formula Sheet2      : {len(f)}")
print(f"entri yang ketemu di master: {len(pakai)}")
print(f"PELANGGARAN (kode > TF)   : {len(langgar)}")
for nm, tf, kode, nama in langgar:
    print(f"  - {nm}: TF={tf} tapi pakai {len(kode)} kode {kode}")
    for x in nama:
        print(f"      * {x} -> {sorted(pakai[nm][x])}")

print()
print("--- cek 7 'pelanggaran' dari audit lama ---")
for nm in ["Daihatsu Xenia", "Honda Civic", "Hyundai Stargazer", "Nissan Navara",
           "Toyota Corolla"]:
    e = next((x for x in f if x["nama"] == nm), None)
    if not e or tf_int(e) is None:
        print(f"  {nm}: TIDAK ADA di Sheet2 / TF kosong")
        continue
    kode = set()
    for s in pakai[nm].values():
        kode |= s
    status = "OK" if len(kode) <= tf_int(e) else "LANGGAR"
    print(f"  {nm}: TF={tf_int(e)}, dipakai {len(kode)} kode {sorted(kode)} -> {status}")
    for x in sorted(pakai[nm]):
        print(f"      * {x} -> {sorted(pakai[nm][x])}")

json.dump({"langgar": langgar,
           "tak_terdaftar": {k: sorted(v) for k, v in tak_cocok.items() if len(v) > 1}},
          open("audit_tf2.json", "w"), ensure_ascii=False, indent=1)
print()
print("model di luar Sheet2 yang pakai >1 kode generasi:",
      sum(1 for v in tak_cocok.values() if len(v) > 1))
print("entri Sheet2 dengan TF kosong/'?':", tf_kosong)
