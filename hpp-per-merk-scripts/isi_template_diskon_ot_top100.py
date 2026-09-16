#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isi template diskon Shopee (Kode Produk/Kode Variasi/Harga Awal/Harga
diskon) untuk 100 produk Otonation (OT) terlaris - dipetakan pakai PREFIX
SKU yang sama dgn "Harga Baru UC Top 100 (matriks).xlsx" (OT konsolidasi ke
stok UA, jadi target harganya sama dgn top-100 UC - sudah divalidasi lewat
`cek_harga_otonation.py`, 2026-08-26).

Hanya Reguler+Strip yg diisi (Premium/Exclusive tidak disentuh, konsisten
dgn seluruh batch harga proyek ini). "Batas Pembelian" sengaja dikosongkan
(opsional, tidak perlu batas).

Formula (2026-08-27, revisi dari versi awal yg cuma isi Harga diskon;
persentase diubah dari 3% ke 3,5% di hari yg sama - PERSEN bisa berubah
lagi kalau user minta, cek chat/memory terbaru sebelum pakai angka di sini):
    Harga Awal   = target resmi top-100 (BUKAN harga live di listing OT)
    Harga diskon = Harga Awal - 3,5% = harga_awal - (harga_awal*35)//1000
                   (integer, eksak - semua target kelipatan Rp1.000 jadi
                   3,5%-nya selalu kelipatan Rp35, no rounding)

Kenapa Harga Awal pakai target resmi bukan live: 2 masalah yg sempat
ketahuan waktu Harga diskon msh dihitung dari live (2026-08-26/27) -
- Brio & Jazz: live OT sempat pakai harga spread lama (335rb/378rb),
  padahal target resmi sudah dikoreksi ke plafon 332rb/375rb. Target resmi
  di file ini SUDAH mengandung plafon itu (`terapkan_override_brio_jazz.py`
  sudah nulis nilainya langsung ke "Harga Baru UC Top 100 (matriks).xlsx"),
  jadi baca_harga() otomatis kasih 332rb/375rb, tidak perlu override lagi
  di sini.
- Suzuki Carry (varian Gen 2F, 14 baris): live OT sempat stale di 315rb.
  User sudah perbaiki manual match ke harga Gen 2 (2026-08-27) - dgn Harga
  Awal dari target resmi, baris ini otomatis ikut benar juga.

Pemakaian:
    python3 isi_template_diskon_ot_top100.py <harga_file.xlsx> \
        <template_diskon_kosong.xlsx> <folder_listing_OT...> <out.xlsx>
"""
import sys
import openpyxl
from update_harga_per_sku import (baca_harga, urai_sku, ALIAS, KAT_KE_JENIS,
                                   KECUALI, is_outdoor_polos, resolve_cols)


def diskon35(harga):
    return harga - (harga * 35) // 1000


def main():
    harga_file = sys.argv[1]
    template_path = sys.argv[2]
    folders = sys.argv[3:-1]
    out_path = sys.argv[-1]

    target = baca_harga(harga_file, 1, 100)

    rows_out = []
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

            harga_awal = target[pfx_resolved][jenis]
            harga_diskon = diskon35(harga_awal)
            rows_out.append((
                pid, nm, None,
                wsv.cell(r, 3).value, wsv.cell(r, 4).value, sku,
                harga_awal, harga_diskon, None,
            ))

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    for i, row in enumerate(rows_out, start=2):
        for c, val in enumerate(row, start=1):
            ws.cell(i, c, val)
    wb.save(out_path)

    print(f'total baris: {len(rows_out)}')
    print(f'tersimpan: {out_path}')


if __name__ == '__main__':
    main()
