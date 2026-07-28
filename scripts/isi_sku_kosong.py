"""Tahap 4: isi SKU yang KOSONG / masih skema lama di file listing baru.

Sasaran (hasil analisa 2026-07-28 pada file mentah):
   6.015 baris kolom SKU kosong
   5.376 baris skema lama 3 segmen (CVR0033-UC-RSWA)
     153 baris berisi literal teks "SKU"
      14 baris 4 segmen
       1 baris rusak (NSN-NVP-SP-S-G$-S3A)

Sumber kebenaran: resolver_sync.resolve_sku() terhadap master yg SUDAH berskema
formula. Lookup WAJIB dibangun ulang dulu lewat rebuild_lookup.py — kalau tidak,
SKU hasil isian akan memakai segmen generasi lama.

Baris motor & karpet dilewati. Baris yg sudah 6 segmen tidak disentuh.
Jalankan dry-run dulu, baru `--apply`.

CATATAN URUTAN: setelah skrip ini, jalankan step_formula sekali lagi — sebagian
baris hasil isian memakai generasi versi master yg berbeda dari pengelompokan
formula (kasus Toyota Corolla "Gen 5 (1983-1987)" -> master G6, formula G5).
"""
import warnings, sys, json, re
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter, defaultdict

import files_baru as FB
import resolver_sync as RS

APPLY = "--apply" in sys.argv
OK6 = re.compile(r'^[A-Z0-9]+-[A-Z0-9]+-(UA|OT|SP|OP)-[A-Z]-[A-Za-z0-9]+-[A-Z0-9]+$')


def run(apply):
    stat = Counter()
    contoh = defaultdict(list)
    isi = []
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        fn = FB.path(f)
        wbk = load_workbook(fn, data_only=False)
        ws = wbk[sheet]
        touched = False
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            low = str(nm).lower()
            if "motor" in low or "karpet" in low:
                continue
            sku = ws.cell(row=r, column=sc).value
            if isinstance(sku, str) and OK6.match(sku.split("_")[0]):
                continue                      # sudah benar, jangan disentuh
            var = str(ws.cell(row=r, column=vc).value or "")
            got, st = RS.resolve_sku(store, str(nm), var)
            if got is None:
                stat["gagal:" + st] += 1
                if len(contoh[st]) < 3:
                    contoh[st].append((f, r, str(nm)[:46], var[:34]))
                continue
            # JANGAN menimpa segmen kode toko. Konvensi yg dipakai master & seluruh
            # listing (dicek 2026-07-28, 100% konsisten di data mentah): toko Otonation
            # memakai kode SKU **UA**, toko Otoprotection memakai kode **SP**. Versi
            # sebelumnya menimpanya jadi OT/OP dan itu membuat ~1.310 baris hasil isian
            # tidak cocok dgn baris lain di file yg sama. resolve_sku() sudah
            # mengembalikan kode yg benar — biarkan apa adanya.
            if apply:
                ws.cell(row=r, column=sc, value=got)
            touched = True
            stat["terisi"] += 1
            isi.append([f, r, str(sku), got, str(nm)[:60], var[:40]])
        if apply and touched:
            wbk.save(fn)
    return stat, contoh, isi


if __name__ == "__main__":
    print("MODE:", "APPLY (file DITULIS)" if APPLY else "DRY-RUN (file TIDAK ditulis)")
    stat, contoh, isi = run(APPLY)
    print("=== ISI SKU KOSONG / SKEMA LAMA ===")
    for k, v in stat.most_common():
        print(f"   {v:7}  {k}")
    print("\ncontoh yg masih gagal:")
    for st, ex in contoh.items():
        print(f"  [{st}]")
        for e in ex:
            print("      ", e)
    json.dump(isi, open("_isi_sku_kosong.json", "w"), ensure_ascii=False)
