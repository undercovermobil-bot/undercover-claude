# -*- coding: utf-8 -*-
"""
Perbaiki SKU yang salah tag segmen di listing OT kategori "Outdoor" POLOS.

Konteks: "Outdoor" polos di Otonation setara tier PREMIUM UA (bukan Reguler),
dikonfirmasi user 2026-08-19. Investigasi update harga menemukan 31 baris di
15 model yang hidup di listing itu tapi SKU-nya bersegmen 'R' (Reguler)
padahal produknya Premium -- harganya SENDIRI sudah benar Premium (Rp700rb-
1,06jt), cuma kode SKU-nya yang keliru.

Diverifikasi ke data master UA sebelum eksekusi: SETIAP kombinasi
prefix+gen+warna yang dihasilkan dari mengganti segmen R->P sudah ada persis
sebagai SKU master resmi (termasuk kasus yang kelihatan janggal, mis. Toyota
Corolla Gen 5 -- ternyata memang generasi Premium yang sah, cuma kebetulan
OT tidak py baris Premium G5 lain sbg pembanding). Jadi perbaikan ini BUKAN
menciptakan SKU baru, hanya membetulkan segmen yang salah ketik/salah proses
supaya sama dengan kode yang sudah ada di master.

Perbaikan ini HANYA mengubah kolom SKU, TIDAK menyentuh harga (harganya sudah
benar dari awal).

Pemakaian:
  python3 fix_sku_outdoor_polos.py <folder_out> <folder_listing_ot...>
"""
import sys, os, glob, copy
import openpyxl
from openpyxl.styles import PatternFill

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_harga_per_sku import (deteksi_channel, cari_sheet, resolve_cols,
                                   STARTROW, urai_sku, is_outdoor_polos)

ORANGE = PatternFill('solid', fgColor='FFC000')


def sku_baru(sku):
    """ganti segmen ke-4 (R/S) jadi P, sisanya tetap"""
    b = sku.strip().split('-')
    b[3] = 'P'
    return '-'.join(b)


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        d = ws_d.cell(row=r_d, column=c, value=s.value)
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def proses(out_dir, folders, nama_toko='OT'):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = []

    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=False)
        ch = deteksi_channel(wb)
        if ch is None:
            continue
        ws = cari_sheet(wb, ch)
        wbv = openpyxl.load_workbook(path, data_only=True)
        wsv = cari_sheet(wbv, ch)
        col = resolve_cols(wsv, ch)
        start = STARTROW[ch]

        ubah = []
        for r in range(start, wsv.max_row + 1):
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if not is_outdoor_polos(nm):
                continue
            sku_lama = wsv.cell(row=r, column=col['sku']).value
            pfx, kat = urai_sku(sku_lama)
            if kat not in ('R', 'S'):
                continue
            sku_new = sku_baru(sku_lama)
            ubah.append((r, sku_lama, sku_new, nm,
                         wsv.cell(row=r, column=col['var']).value))

        if not ubah:
            continue

        for r, lama, baru, nm, var in ubah:
            sel = ws.cell(row=r, column=col['sku'])
            sel.value = baru
            sel.fill = ORANGE
            laporan.append((os.path.basename(path), lama, baru, nm, var))

        n_kol = ws.max_column
        baris = [u[0] for u in ubah]
        for i, r in enumerate(baris):
            t = start + i
            if t != r:
                salin(ws, r, ws, t, n_kol)
        sisa = start + len(baris)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(baris))
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(baris)):
                salin(ws, start + i, wso, r_out + i, n_kol)
            per_channel[ch] = (wo, wso, r_out + len(baris))

    hasil = {}
    for ch, (wb_o, _, _) in per_channel.items():
        out = os.path.join(out_dir, f'FIX_SKU_OUTDOOR_{nama_toko}_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan


if __name__ == '__main__':
    out_dir = sys.argv[1]
    folders = sys.argv[2:]

    hasil, laporan = proses(out_dir, folders)

    print(f'Total baris diperbaiki: {len(laporan)}')
    for fn, lama, baru, nm, var in laporan:
        print(f'  {fn:8s} {lama:24s} -> {baru:24s}  {nm}  [{var}]')

    print()
    for ch, path in hasil.items():
        print(f'[{ch}] -> {os.path.basename(path)}')
