"""Bangun ulang master_lookup_full.json (UA) & master_lookup_sp.json (SP) dari MASTER.

WAJIB dijalankan setiap kali master berubah. Lookup lama (14 Juli) dibuat SEBELUM
skema formula dipasang, jadi masih memetakan ke segmen generasi lama (G4 dst).
Kalau dipakai untuk mengisi SKU kosong, hasilnya akan bertentangan dgn skema formula.

Key  : (Nama Produk, Kategori, Generasi, Warna)
Value: SKU

Cek kesegaran cepat: bandingkan proporsi segmen 'G1' di lookup vs di master.
Kalau jauh berbeda, lookup-nya basi.
"""
import warnings, json
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter

MASTER = "MASTER_from_drive_20260715.xlsx"
TOKO_UA = {"Undercover Autocare", "Otonation"}
TOKO_SP = {"Smartprotection", "Otoprotection"}

wb = load_workbook(MASTER, data_only=True)
ua, sp = {}, {}
bentrok = Counter()
for sn in wb.sheetnames:
    ws = wb[sn]
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=2).value
        toko = ws.cell(row=r, column=3).value
        kat = ws.cell(row=r, column=4).value
        warna = ws.cell(row=r, column=5).value
        gen = ws.cell(row=r, column=6).value
        sku = ws.cell(row=r, column=9).value
        if not nm or not isinstance(sku, str) or sku.count("-") != 5:
            continue
        key = (str(nm).strip(), str(kat).strip() if kat else None,
               str(gen).strip() if gen else None,
               str(warna).strip() if warna else None)
        # toko OT memakai prefix SKU UA, toko OP memakai prefix SP (sesuai desain)
        tgt = ua if str(toko).strip() in TOKO_UA else (sp if str(toko).strip() in TOKO_SP else None)
        if tgt is None:
            continue
        if key in tgt and tgt[key] != sku:
            bentrok[key[0]] += 1
            continue          # pertahankan yg pertama, laporkan
        tgt[key] = sku

json.dump({str(k): v for k, v in ua.items()}, open("master_lookup_full.json", "w"), ensure_ascii=False)
json.dump({str(k): v for k, v in sp.items()}, open("master_lookup_sp.json", "w"), ensure_ascii=False)

cu = Counter(v.split("-")[4] for v in ua.values())
print(f"lookup UA : {len(ua)} entri   segmen gen teratas: {cu.most_common(6)}")
cs = Counter(v.split("-")[4] for v in sp.values())
print(f"lookup SP : {len(sp)} entri   segmen gen teratas: {cs.most_common(6)}")
print(f"key bentrok (SKU beda utk key sama): {sum(bentrok.values())} pada {len(bentrok)} model")
for m, n in bentrok.most_common(10):
    print(f"   {n:5}  {m}")
