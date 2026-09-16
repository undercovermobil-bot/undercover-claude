# -*- coding: utf-8 -*-
"""
Pemetaan SKU utk 5 pasangan model (Terios dikecualikan atas keputusan user):
- Sigra Gen1 (2016-2026)                          -> Calya Gen1 (2016-2026)
- Rocky Gen2/A200 (2021-2026)                      -> Raize Gen1 (2021-2026)
- Rocky F70/F300 (1984-2002)                       -> Feroza "Gen 1&2 " (1993-1996) [DEFAULT, tanya user]
- Vellfire Gen2/2F/3/3F (2008-2023)                -> Alphard "Gen 1 - 3" (2002-2022)
- Vellfire Gen4 (2023-2024)                        -> Alphard Gen4 (2023-2026)
- Agya Gen1 (2013-2023)                            -> Ayla Gen1 (2013-2023) [dasar saja, bukan F1/F2]
- Agya Gen2 (2023-2026)                            -> Ayla Gen2 (2023-2026)

Semua dicocokkan lewat (Toko, Kategori, Warna) -> ambil SKU TARGET asli persis.
"""
import openpyxl, json, collections

SRC = '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/6d869641-SKU_Price_Tracking_Cover_Mobil.xlsx'

wb = openpyxl.load_workbook(SRC, data_only=False)
C_NAMA, C_TOKO, C_KAT, C_WARNA, C_GEN, C_THN, C_SKU = 2, 3, 4, 5, 6, 7, 9


def lookup(sheet_name, nama_model, gen_label):
    ws = wb[sheet_name]
    d = {}
    for r in range(3, ws.max_row + 1):
        if ws.cell(row=r, column=C_NAMA).value != nama_model:
            continue
        if str(ws.cell(row=r, column=C_GEN).value or '').strip() != gen_label.strip():
            continue
        key = (ws.cell(row=r, column=C_TOKO).value, ws.cell(row=r, column=C_KAT).value,
               ws.cell(row=r, column=C_WARNA).value)
        d[key] = ws.cell(row=r, column=C_SKU).value
    return d


def sumber_rows(sheet_name, nama_model, gen_label):
    ws = wb[sheet_name]
    out = []
    for r in range(3, ws.max_row + 1):
        if ws.cell(row=r, column=C_NAMA).value != nama_model:
            continue
        if str(ws.cell(row=r, column=C_GEN).value or '').strip() != gen_label.strip():
            continue
        key = (ws.cell(row=r, column=C_TOKO).value, ws.cell(row=r, column=C_KAT).value,
               ws.cell(row=r, column=C_WARNA).value)
        out.append((sheet_name, r, key, ws.cell(row=r, column=C_SKU).value))
    return out


# ---------- target lookups ----------
target_calya = lookup('Toyota', 'Toyota Calya', 'Gen 1')
target_raize = lookup('Toyota', 'Toyota Raize', 'Gen 1')
target_feroza_g1 = lookup('Daihatsu', 'Daihatsu Feroza', 'Gen 1&2')
target_alphard_1_3 = lookup('Toyota', 'Toyota Alphard', 'Gen 1 - 3')
target_alphard_4 = lookup('Toyota', 'Toyota Alphard', 'Gen 4')
target_ayla_g1 = lookup('Daihatsu', 'Daihatsu Ayla', 'Gen 1')
target_ayla_g2 = lookup('Daihatsu', 'Daihatsu Ayla', 'Gen 2')
target_rush_g1 = lookup('Toyota', 'Toyota Rush', 'Gen 1')

print('target sizes:', {k: len(v) for k, v in dict(
    calya=target_calya, raize=target_raize, feroza_g1=target_feroza_g1,
    alphard_1_3=target_alphard_1_3, alphard_4=target_alphard_4,
    ayla_g1=target_ayla_g1, ayla_g2=target_ayla_g2, rush_g1=target_rush_g1).items()})

# ---------- bangun daftar tugas (sumber -> lookup target) ----------
TUGAS = [
    ('Sigra->Calya',        'Daihatsu', 'Daihatsu Sigra',   'Gen 1',        target_calya),
    ('Rocky A200->Raize',   'Daihatsu', 'Daihatsu Rocky',   'Gen 2 (A200)', target_raize),
    ('Rocky F70->Feroza',   'Daihatsu', 'Daihatsu Rocky',   'F70/F300',     target_feroza_g1),
    ('Vellfire 2-3F->Alphard1-3', 'Toyota', 'Toyota Vellfire', 'Gen 2',     target_alphard_1_3),
    ('Vellfire 2F->Alphard1-3',   'Toyota', 'Toyota Vellfire', 'Gen 2F',    target_alphard_1_3),
    ('Vellfire 3->Alphard1-3',    'Toyota', 'Toyota Vellfire', 'Gen 3',     target_alphard_1_3),
    ('Vellfire 3F->Alphard1-3',   'Toyota', 'Toyota Vellfire', 'Gen 3F',    target_alphard_1_3),
    ('Vellfire 4->Alphard1-3 [FIX: Alphard nyatanya G1 semua]', 'Toyota', 'Toyota Vellfire', 'Gen 4', target_alphard_1_3),
    ('Agya G1->Ayla G1',    'Toyota',   'Toyota Agya',      'Gen 1',        target_ayla_g1),
    ('Agya G2->Ayla G1 [FIX: Ayla nyatanya G1 semua]', 'Toyota', 'Toyota Agya', 'Gen 2', target_ayla_g1),
    ('Terios->Rush G1',     'Daihatsu', 'Daihatsu Terios',  'Gen 1',        target_rush_g1),
]

hasil = collections.defaultdict(list)
gagal = collections.defaultdict(list)
for label, sheet, model, gen, target in TUGAS:
    rows = sumber_rows(sheet, model, gen)
    for sh, r, key, lama in rows:
        baru = target.get(key)
        if baru is None:
            gagal[label].append((r, key, lama))
        else:
            hasil[label].append((sh, r, key, lama, baru))

print()
for label, sheet, model, gen, target in TUGAS:
    n_ok = len(hasil[label])
    n_gagal = len(gagal[label])
    print(f'  {label:26s} : {n_ok:3d} cocok, {n_gagal:2d} GAGAL')
    for g in gagal[label][:3]:
        print('     GAGAL:', g)

print()
print('=== contoh hasil (2 tiap tugas) ===')
for label in hasil:
    for h in hasil[label][:2]:
        print(f'  [{label}] {h[2]} : {h[3]} -> {h[4]}')

json.dump({k: v for k, v in hasil.items()}, open(
    '/tmp/claude-0/-home-user-undercover-claude/77f87f91-8d04-58ac-abe6-16778a83e499/scratchpad/mapping_5pasangan.json', 'w'
), ensure_ascii=False)
print('\n-> disimpan ke mapping_5pasangan.json')
