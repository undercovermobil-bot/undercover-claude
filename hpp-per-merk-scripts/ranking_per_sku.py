import os, sys, pickle, re
from collections import defaultdict
import openpyxl
S = os.environ.get("KERJA_DIR", ".")  # folder data: sku_map.pkl + MOBIL_TERLARIS_BIGSELLER.xlsx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sku_map_lib import base_name, norm

HARI = 169
d = pickle.load(open(f"{S}/sku_map.pkl", "rb"))
ua, spop = d['ua'], d['spop']

# nama laporan -> prefix, utk nama yg tidak ada di listing UA/SP/OP (penamaan lama / toko OT)
# dasar: rentang generasi di sheet Detail + nama model; lihat sheet Catatan di output
MANUAL = {
    'Honda Civic': ('HND-CVC', 'nama lama listing Civic Sedan; generasi Gen 1-11 = produk Civic Sedan'),
    'Daihatsu Gran Max PU': ('DHT-GMXP', 'PU = Pick Up'),
    'Daihatsu Gran Max MB': ('DHT-GMX', 'MB = Minibus'),
    'Honda City': ('HND-CTY', 'generasi Gen 4F-7 = City Sedan (City Hatchback listing terpisah)'),
    'Suzuki APV': ('SZK-APV', 'APV = APV Arena (SKU SZK-APV "APV Arena / Blind Van")'),
    'Mitsubishi Strada Triton': ('MTB-TRN', 'Strada Triton = Triton Gen 4-5 (2005-2022)'),
    'Mitsubishi Pajero': ('MTB-PJS', 'listing SP/OP bernama "Mitsubishi Pajero" ber-SKU MTB-PJS; generasi = Pajero Sport'),
    'Suzuki Carry PU': ('SZK-CRP', 'PU = Pick Up'),
    'Mercedes E Class': ('MBZ-ECL', 'penulisan lain Mercedes Benz E Class'),
    'Toyota Starlet Kapsul': ('TYT-STR', 'listing SP/OP "Starlet Kapsul" ber-SKU TYT-STR'),
    'Aion Hyptec HT': ('GAC-HH', 'penulisan lain GAC Aion Hyptec HT'),
    'Toyota Hardtop / Land Cruiser': ('TYT-HTP', 'Hardtop = Land Cruiser J40'),
    'Mazda 2': ('MZD-2H', 'dikonfirmasi user 2026-09-24: "Mazda 2" = Mazda 2 Hatchback'),
    'Suzuki Vitara': ('SZK-VITARA', 'satu listing berisi beberapa SKU (SZK-GVT/GVH/EVT)'),
    'Suzuki Grand Vitara': ('SZK-VITARA', 'listing sama dgn Suzuki Vitara (SKU SZK-GVT/GVH/EVT)'),
}
# pecah per generasi / per jenis bodi (qty diambil dari sheet Detail)
SPLIT = {
    'Daihatsu Rocky': [('TYT-RZE', 85, 'Rocky baru 2019+ (77 unit) + tanpa info gen (8 unit, ikut mayoritas) -> SKU Raize'),
                       ('DHT-FRZ', 5, 'Rocky lama F70 -> SKU Feroza')],
    'Daihatsu Gran Max': [('DHT-GMX', 9, 'listing gabungan Minibus+Pick Up, info bodi tidak ada -> dibagi rata'),
                          ('DHT-GMXP', 9, 'listing gabungan Minibus+Pick Up, info bodi tidak ada -> dibagi rata')],
}
# prefix sama tapi produk berbeda / tidak bisa dipastikan -> JANGAN digabung
TERPISAH = {
    'Nissan Grand Livina Custom Roofbox': 'produk terpisah (cover roofbox, harga beda) walau prefix NSN-LVN',
    'Toyota Vios Custom': 'produk custom terpisah',
    'Maserati GranTurismo Reguler CUSTOM SPOILER': 'produk custom terpisah',
    'Range Rover Velar': 'prefix LDR-RR sama dgn Range Rover, tapi mobil beda -> kemungkinan salah tag SKU',
    'Range Rover Sport': 'prefix LDR-RR sama dgn Range Rover, tapi mobil beda -> kemungkinan salah tag SKU',
    'Mazda 3': 'bodi tidak disebut (bisa Hatchback MZD-3H atau Sedan MZD-3S)',
    'Kia Rio': 'bodi tidak disebut (bisa Hatchback KIA-RIO atau Sedan KIA-RS)',
    'Suzuki Aerio': 'bodi tidak disebut (bisa Hatchback SZK-ARH atau Sedan SZK-ARS)',
}

def dominant(c):
    return c.most_common(1)[0][0] if c else None

wb = openpyxl.load_workbook(f"{S}/MOBIL_TERLARIS_BIGSELLER.xlsx", data_only=True)
ws = wb['Top Model Mobil']
rows = []
for r in range(6, ws.max_row):
    rank, nm, qty, rp = ws.cell(r,1).value, ws.cell(r,2).value, ws.cell(r,3).value, ws.cell(r,5).value
    if rank is None: continue
    rows.append((rank, nm, qty, rp))

groups = defaultdict(lambda: {'qty': 0, 'rp': 0.0, 'members': []})
basis = []
for rank, nm, qty, rp in rows:
    if nm in SPLIT:
        tot = sum(q for _, q, _ in SPLIT[nm])
        assert tot == qty, (nm, tot, qty)
        for key, q, why in SPLIT[nm]:
            g = groups[key]; g['qty'] += q; g['rp'] += rp * q / qty
            g['members'].append((rank, nm, q, f'sebagian: {why}'))
            basis.append((nm, rank, qty, key, f'DIPECAH {q} unit: {why}'))
        continue
    if nm in TERPISAH:
        key = 'NAMA:' + nm; why = TERPISAH[nm]
        basis.append((nm, rank, qty, '(berdiri sendiri)', 'TIDAK digabung: ' + why))
    elif nm in MANUAL:
        key, why = MANUAL[nm]
        basis.append((nm, rank, qty, key, 'manual: ' + why))
    else:
        b = norm(base_name(nm))
        if ua.get(b):
            key, why = dominant(ua[b]), 'SKU listing UA'
        elif spop.get(b):
            key, why = dominant(spop[b]), 'SKU listing SP/OP'
        else:
            key, why = 'NAMA:' + nm, 'tidak ada di listing, berdiri sendiri'
    g = groups[key]; g['qty'] += qty; g['rp'] += rp
    g['members'].append((rank, nm, qty, why))

# nama grup = anggota terlaris, kecuali nama itu penamaan lama/toko lain -> pakai nama listing UA
NAMA_GRUP = {'MZD-2H': 'Mazda 2 Hatchback', 'DHT-GMXP': 'Daihatsu Gran Max Pick Up', 'HND-CVC': 'Honda Civic Sedan'}
out = []
for key, g in groups.items():
    mem = sorted(g['members'], key=lambda m: -m[2])
    out.append({'key': key, 'nama': NAMA_GRUP.get(key, mem[0][1]), 'qty': g['qty'], 'rp': g['rp'],
                'members': sorted(g['members']), 'best_old': min(m[0] for m in g['members'])})
out.sort(key=lambda x: (-x['qty'], -x['rp'], x['best_old']))  # unit sama -> nilai penjualan (Rp) lebih besar di atas
for i, g in enumerate(out, 1):
    g['rank'] = i

pickle.dump({'out': out, 'basis': basis, 'rows': rows}, open(f"{S}/ranking_per_sku.pkl", "wb"))

print(f"Nama di laporan: {len(rows)}  ->  grup produk: {len(out)}")
print(f"Batas: #100 = {out[99]['nama']} ({out[99]['qty']} unit), #101 = {out[100]['nama']} ({out[100]['qty']} unit), #102 = {out[101]['nama']} ({out[101]['qty']})")
top_old = {nm for rank, nm, q, rp in rows if rank <= 100}
print("\nMASUK BARU (tidak ada anggotanya di top-100 lama):")
for g in out[:100]:
    if not any(m[1] in top_old for m in g['members']):
        print(f"   #{g['rank']:>3} {g['qty']:>4}  {g['nama']}  [{g['key']}]  anggota: {[(m[1], m[2]) for m in g['members']]}")
print("\nKELUAR (ada anggota di top-100 lama, grupnya sekarang di luar 100):")
for g in out[100:]:
    if any(m[1] in top_old for m in g['members']):
        print(f"   #{g['rank']:>3} {g['qty']:>4}  {g['nama']}  anggota: {[(m[1], m[0], m[2]) for m in g['members']]}")
print("\nGrup gabungan (>1 nama) di top-100 baru:")
for g in out[:100]:
    if len(g['members']) > 1:
        print(f"   #{g['rank']:>3} {g['qty']:>5}  [{g['key']}]  " + ' + '.join(f"{m[1]} (#{m[0]}, {m[2]})" for m in g['members']))
