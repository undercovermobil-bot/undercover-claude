# -*- coding: utf-8 -*-
"""
Lengkapi file upload TikTok supaya tiap produk memuat SELURUH variannya.

Template `all_information` TikTok memperlakukan file sebagai DAFTAR VARIAN
LENGKAP per produk: varian yang tidak ikut dikirim dibaca sebagai permintaan
HAPUS, dan uploadnya gagal dengan "sku not allow delete" (terbukti 2026-09-04).
Script pembuat file update (mis. `update_harga_per_sku.py`) hanya menulis baris
yang BERUBAH, jadi kalau satu listing cuma sebagian variannya berubah, sisanya
harus ditambahkan kembali APA ADANYA (nilai dari ekspor, tidak diubah).

Baris tambahan sengaja TIDAK diberi warna -- supaya tetap kelihatan mana yang
benar-benar diubah dan mana yang cuma pelengkap.

Pemakaian:
  python3 lengkapi_varian_tiktok.py <file_update.xlsx> <ekspor_sumber.xlsx> <file_out.xlsx>
"""
import sys, os, copy, warnings

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
import update_harga_per_sku as UH

START = UH.STARTROW['tiktok']


def peta_kolom(ws):
    h = {str(ws.cell(row=1, column=c).value).strip().lower(): c
         for c in range(1, ws.max_column + 1)}
    for w in ('product_id', 'sku_id'):
        if w not in h:
            raise SystemExit(f'kolom {w} tidak ketemu -- template TikTok berubah?')
    return h['product_id'], h['sku_id']


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        # JANGAN pakai cell(..., value=s.value): openpyxl mengabaikan value=None,
        # jadi sel tujuan yang sudah terisi TIDAK ikut dikosongkan dan baris hasil
        # membawa nilai sisa baris yang digeser (terbukti 2026-09-07: kolom
        # "Min. Jumlah Pembelian" Shopee ikut kebawa). Set .value eksplisit.
        d = ws_d.cell(row=r_d, column=c)
        d.value = s.value
        d.number_format = s.number_format


if __name__ == '__main__':
    f_upd, f_src, f_out = sys.argv[1], sys.argv[2], sys.argv[3]

    wb_u = openpyxl.load_workbook(f_upd)
    ws_u = UH.cari_sheet(wb_u, 'tiktok')
    wb_s = openpyxl.load_workbook(f_src, data_only=True)
    ws_s = UH.cari_sheet(wb_s, 'tiktok')

    # tata letak kolom WAJIB sama -- penyalinan di bawah berbasis nomor kolom
    hu = [str(ws_u.cell(row=1, column=c).value) for c in range(1, ws_u.max_column + 1)]
    hs = [str(ws_s.cell(row=1, column=c).value) for c in range(1, ws_s.max_column + 1)]
    if hu != hs:
        raise SystemExit('header file update dan ekspor sumber BEDA -- '
                         'jangan disalin per nomor kolom')

    pid_u, sku_u = peta_kolom(ws_u)
    pid_s, sku_s = peta_kolom(ws_s)

    ada = {}          # product_id -> set(sku_id) yang sudah ada di file update
    for r in range(START, ws_u.max_row + 1):
        p = ws_u.cell(row=r, column=pid_u).value
        if p is None:
            continue
        ada.setdefault(str(p), set()).add(str(ws_u.cell(row=r, column=sku_u).value))

    tambah = []       # baris sumber yang perlu disalin
    for r in range(START, ws_s.max_row + 1):
        p = ws_s.cell(row=r, column=pid_s).value
        if p is None or str(p) not in ada:
            continue
        if str(ws_s.cell(row=r, column=sku_s).value) not in ada[str(p)]:
            tambah.append(r)

    n_kol = ws_u.max_column
    r_out = ws_u.max_row + 1
    for i, r in enumerate(tambah):
        salin(ws_s, r, ws_u, r_out + i, n_kol)

    wb_u.save(f_out)
    print(f'produk di file update : {len(ada)}')
    print(f'baris pelengkap       : {len(tambah)}')
    print(f'total baris sekarang  : {ws_u.max_row - START + 1}')
    print(f'-> {os.path.basename(f_out)}')
