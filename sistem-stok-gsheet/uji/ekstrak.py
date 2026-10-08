import openpyxl, sys, json, datetime
wb = openpyxl.load_workbook(sys.argv[1])
ws = wb['Stok Cover UC']
cells = {}
for r in range(1, 200):
    for c in range(1, 41):
        v = ws.cell(r, c).value
        if v is None: continue
        if isinstance(v, datetime.datetime): v = v.isoformat()
        cells[f'{r},{c}'] = v
json.dump(cells, open(sys.argv[2], 'w'))
print(len(cells))
