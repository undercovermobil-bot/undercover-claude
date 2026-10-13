"""Pemakaian: python3 isi_campaign_shopee.py <eligible_Product_list.xlsx> <template.xlsx> <prefix_out> <diskon_desimal, mis. 0.0633>
(file input sudah lewat repair_xlsx.py)

Isi template campaign Shopee dari eligible list: hanya produk 'Signature',
Harga Diskon = floor(Harga Awal x (1 - DISKON)), dipecah per produk (<= MAKS baris/file)."""
import sys, math, openpyxl
from openpyxl.styles import PatternFill
eligible, template, out_prefix, diskon = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
HANYA, MAKS = 'Signature', 2600
ORANGE = PatternFill('solid', fgColor='FFC000')
src = openpyxl.load_workbook(eligible).active
hdr = [src.cell(1, c).value for c in range(1, 16)]
C = {h: i for i, h in enumerate(hdr)}
per_produk, lewat = {}, 0
for r in range(4, src.max_row + 1):
    row = [src.cell(r, c).value for c in range(1, 16)]
    if not row[C['Kode Variasi']]:
        continue
    if HANYA not in str(row[C['Nama Produk']]):
        lewat += 1; continue
    awal = int(float(row[C['Harga Awal']]))
    row[C['Harga Diskon']] = math.floor(awal * (1 - diskon))
    per_produk.setdefault(str(row[C['Kode Produk']]), []).append(row)
total = sum(map(len, per_produk.values()))
n_file = -(-total // MAKS)
target = -(-total // n_file)
bagian, isi = [], []
for rows in per_produk.values():
    if isi and sum(map(len, isi)) + len(rows) > target + 80:
        bagian.append(isi); isi = []
    isi.append(rows)
bagian.append(isi)
print(f'dilewati (bukan {HANYA}): {lewat} varian | diisi: {len(per_produk)} produk, {total} varian -> {len(bagian)} file')
for k, isi in enumerate(bagian, 1):
    wb = openpyxl.load_workbook(template); ws = wb.active
    r = 4
    for rows in isi:
        for row in rows:
            for c, v in enumerate(row, 1):
                ws.cell(r, c).value = v
            ws.cell(r, 11).fill = ORANGE
            r += 1
    out = f'{out_prefix}_{k}.xlsx'
    wb.save(out)
    print(f'  {out.split("/")[-1]}: {len(isi)} produk, {r - 4} varian')
