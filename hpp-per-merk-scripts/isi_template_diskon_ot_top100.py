#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi template diskon Shopee (kolom Kode Produk/Kode Variasi/Harga diskon)
untuk 100 produk Otonation (OT) terlaris - dipetakan pakai PREFIX SKU yang
sama dgn "Harga Baru UC Top 100 (matriks).xlsx" (OT konsolidasi ke stok UA,
jadi target harganya sama dgn top-100 UC - sudah divalidasi lewat
`cek_harga_otonation.py`, 2026-08-26).

Hanya Reguler+Strip yg diisi (Premium/Exclusive tidak disentuh, konsisten
dgn seluruh batch harga proyek ini). "Harga Awal" & "Batas Pembelian"
sengaja dikosongkan (opsional di template, biar Shopee pakai harga listing
saat ini scr otomatis).

PENTING: kolom "Harga diskon" diisi dgn TARGET RESMI dari file harga
(bukan harga live di listing OT), supaya tidak ikut membawa 2 masalah yg
sudah diketahui ke kampanye diskon baru:
  - Brio & Jazz (56 baris): listing OT masih pakai harga spread lama
    (335rb/378rb), padahal sudah dikoreksi ke plafon 332rb/375rb.
  - Suzuki Carry (14 baris, varian Gen 2F): listing OT masih 315rb,
    stale dari sebelum batch harga diterapkan sama sekali.
Kalau target harga berubah lagi nanti, cek ulang perbedaan live-vs-target
before generate ulang - JANGAN asumsikan otomatis semua sudah sinkron.

Pemakaian:
    python3 isi_template_diskon_ot_top100.py <harga_file.xlsx> \
        <template_diskon_kosong.xlsx> <folder_listing_OT...> <out.xlsx>
"""
import sys
import openpyxl
from update_harga_per_sku import (baca_harga, urai_sku, ALIAS, KAT_KE_JENIS,
                                   KECUALI, is_outdoor_polos, resolve_cols)


def main():
    harga_file = sys.argv[1]
    template_path = sys.argv[2]
    folders = sys.argv[3:-1]
    out_path = sys.argv[-1]

    target = baca_harga(harga_file, 1, 100)

    rows_out = []
    mismatch = []
    import glob, os
    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wsv = openpyxl.load_workbook(path, data_only=True)['Sheet1']
        col = resolve_cols(wsv, 'shopee')
        for r in range(7, wsv.max_row + 1):
            pid = wsv.cell(r, 1).value
            if pid is None:
                continue
            sku = wsv.cell(r, col['sku']).value
            pfx, kat = urai_sku(sku)
            pfx_resolved = ALIAS.get(pfx, pfx)
            if pfx_resolved not in target:
                continue
            nm = str(wsv.cell(r, col['nama']).value or '')
            if any(k in nm.lower() for k in KECUALI):
                continue
            if is_outdoor_polos(nm):
                continue
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue

            harga_diskon = target[pfx_resolved][jenis]
            harga_live = wsv.cell(r, col['harga']).value
            try:
                if int(float(harga_live)) != harga_diskon:
                    mismatch.append((pfx_resolved, jenis, nm, sku, harga_live, harga_diskon))
            except (TypeError, ValueError):
                pass

            rows_out.append((
                pid, nm, None,
                wsv.cell(r, 3).value, wsv.cell(r, 4).value, sku,
                None, harga_diskon, None,
            ))

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    for i, row in enumerate(rows_out, start=2):
        for c, val in enumerate(row, start=1):
            ws.cell(i, c, val)
    wb.save(out_path)

    print(f'total baris: {len(rows_out)}')
    print(f'tersimpan: {out_path}')
    if mismatch:
        print(f'\n! {len(mismatch)} baris beda dgn harga live OT saat ini (dipakai target resmi, bukan live):')
        from collections import Counter
        by_prefix = Counter(m[0] for m in mismatch)
        for pfx, n in by_prefix.most_common():
            print(f'  {pfx}: {n} baris')


if __name__ == '__main__':
    main()
