import openpyxl, sys, json, datetime
# Ekstrak sheet "Stok Cover UC" & "Stok Cover STP" dari file unduhan Google Sheet ke JSON fixture uji.
wb = openpyxl.load_workbook(sys.argv[1])
out = {}
for nama in ('Stok Cover UC', 'Stok Cover STP'):
    ws = wb[nama]
    cells = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=40):
        for c in row:
            v = c.value
            if v is None: continue
            if isinstance(v, datetime.datetime): v = v.isoformat()
            cells[f'{c.row},{c.column}'] = v
    out[nama] = cells
json.dump(out, open(sys.argv[2], 'w'))
print({k: len(v) for k, v in out.items()})
