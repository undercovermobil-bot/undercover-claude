"""Tahap 5 (terakhir): pastikan Seller SKU Lazada unik per listing.

Dijalankan SETELAH isi_sku_kosong.py, karena pengisian SKU baru bisa memunculkan
kembar baru di dalam satu listing. Beda dari step_lazada di pipeline: pass ini
melihat SEMUA SKU dalam listing (termasuk yg sudah punya akhiran '_'), jadi aman
dijalankan berulang (idempoten) dan tidak akan membuat tabrakan baru.

Aturan Lazada: "Nilai SKU tidak dapat digandakan dalam bentuk keseluruhan" —
kembar hanya dilarang di dalam SATU listing, antar listing boleh sama.
Pemisah '_' dipilih supaya BigSeller bisa memotongnya lewat mode delimiter
(Ignore Suffix, pemisah '_', kemunculan ke-1) tanpa bergantung panjang karakter.
"""
import warnings, sys, re
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import defaultdict, Counter

import files_baru as FB

APPLY = "--apply" in sys.argv


def tag_of(var):
    m = re.search(r'gen\s*([0-9]+)', var, re.I)
    if m:
        return "G" + m.group(1)
    m = re.match(r'\s*([A-Za-z0-9]{1,6})', var)
    return re.sub(r'[^A-Z0-9]', '', m.group(1).upper())[:4] if m else ""


def run(apply):
    stat = Counter()
    for fn, sheet, listc, varc, skuc, sr in FB.LAZADA:
        wbk = load_workbook(fn, data_only=False)
        ws = wbk[sheet]
        per_listing = defaultdict(list)
        for r in range(sr, ws.max_row + 1):
            lst = ws.cell(row=r, column=listc).value
            sku = ws.cell(row=r, column=skuc).value
            if lst in (None, "") or not isinstance(sku, str) or not sku.strip():
                continue
            per_listing[lst].append(r)
        touched = False
        for lst, rows in per_listing.items():
            dipakai = set()
            for r in rows:
                sku = str(ws.cell(row=r, column=skuc).value).strip()
                if sku not in dipakai:
                    dipakai.add(sku)
                    continue
                base = sku.split("_")[0]
                tag = tag_of(str(ws.cell(row=r, column=varc).value or ""))
                cand = f"{base}_{tag}" if tag else f"{base}_2"
                i = 2
                while cand in dipakai:
                    cand = f"{base}_{tag}{i}" if tag else f"{base}_{i}"
                    i += 1
                dipakai.add(cand)
                if apply:
                    ws.cell(row=r, column=skuc, value=cand)
                touched = True
                stat[fn.split("/")[-1]] += 1
        if apply and touched:
            wbk.save(fn)
    return stat


if __name__ == "__main__":
    print("MODE:", "APPLY (file DITULIS)" if APPLY else "DRY-RUN (file TIDAK ditulis)")
    stat = run(APPLY)
    print("=== LAZADA: dibuat unik ===")
    for k, v in stat.most_common():
        print(f"   {v:6}  {k}")
    if not stat:
        print("   (tidak ada kembar tersisa)")
