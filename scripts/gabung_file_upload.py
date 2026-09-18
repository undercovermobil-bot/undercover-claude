# -*- coding: utf-8 -*-
"""
Gabungkan dua file upload SEJENIS (channel & toko & template sama) jadi satu.

Dipakai kalau satu pekerjaan terpaksa dijalankan beberapa kali -- mis.
`update_harga_per_sku.py` cuma menerima satu rentang nomor produk, padahal yang
mau diupdate rentang 1-60 DITAMBAH satu produk bernomor jauh (Mazda 2 Hatchback
#99). Daripada menaikkan rentang (ikut menyeret produk 61-98), jalankan
terpisah lalu gabung di sini.

Aman karena diperiksa dulu: header identik dan tidak ada baris yang sama
(kunci per channel) muncul di kedua file.

Pemakaian:
  python3 gabung_file_upload.py <channel> <file_out.xlsx> <file1.xlsx> <file2.xlsx> ...
"""
import sys, os, copy, warnings

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
import update_harga_per_sku as UH


def kunci_baris(ws, ch, r):
    if ch == 'shopee':
        return (str(ws.cell(row=r, column=1).value), str(ws.cell(row=r, column=3).value))
    if ch == 'lazada':
        return str(ws.cell(row=r, column=5).value)
    h = {str(ws.cell(row=1, column=c).value).strip().lower(): c
         for c in range(1, ws.max_column + 1)}
    return str(ws.cell(row=r, column=h['sku_id']).value)


if __name__ == '__main__':
    ch, out_path = sys.argv[1], sys.argv[2]
    berkas = sys.argv[3:]
    start = UH.STARTROW[ch]

    wb = openpyxl.load_workbook(berkas[0])
    ws = UH.cari_sheet(wb, ch)
    n_kol = ws.max_column
    hdr = [str(ws.cell(row=1, column=c).value) for c in range(1, n_kol + 1)]

    ada = set()
    r_out = start
    for r in range(start, ws.max_row + 1):
        if ws.cell(row=r, column=UH.resolve_cols(ws, ch)['nama']).value is None:
            continue
        ada.add(kunci_baris(ws, ch, r))
        r_out = r + 1

    total = len(ada)
    for p in berkas[1:]:
        wb2 = openpyxl.load_workbook(p, data_only=False)
        ws2 = UH.cari_sheet(wb2, ch)
        h2 = [str(ws2.cell(row=1, column=c).value) for c in range(1, ws2.max_column + 1)]
        if h2 != hdr:
            raise SystemExit(f'header {os.path.basename(p)} beda -- tidak boleh digabung')
        col2 = UH.resolve_cols(ws2, ch)
        for r in range(start, ws2.max_row + 1):
            if ws2.cell(row=r, column=col2['nama']).value is None:
                continue
            k = kunci_baris(ws2, ch, r)
            if k in ada:
                raise SystemExit(f'baris {k} muncul di dua file -- irisan harus 0')
            ada.add(k)
            for c in range(1, n_kol + 1):
                s = ws2.cell(row=r, column=c)
                d = ws.cell(row=r_out, column=c)
                d.value = s.value                 # bukan cell(..., value=) -- None harus ikut
                d.fill = copy.copy(s.fill)
                d.number_format = s.number_format
            r_out += 1
        wb2.close()

    wb.save(out_path)
    print(f'{len(berkas)} file digabung -> {r_out - start} baris ({os.path.basename(out_path)})')
