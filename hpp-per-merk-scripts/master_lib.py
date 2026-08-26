import openpyxl, pickle, os
MASTER = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/5337f5dd-SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"
CACHE = "master_rows.pkl"

def muat():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    wb = openpyxl.load_workbook(MASTER, data_only=True, read_only=True)
    data = {}
    for ws in wb.worksheets:
        rows = []
        for r in ws.iter_rows(values_only=True):
            rows.append(r)
        data[ws.title] = rows
    wb.close()
    pickle.dump(data, open(CACHE, "wb"))
    return data

if __name__ == "__main__":
    d = muat()
    print("sheet:", list(d.keys())[:100])
    for k, v in list(d.items())[:2]:
        print(k, len(v))
        for r in v[:4]:
            print("  ", r)
