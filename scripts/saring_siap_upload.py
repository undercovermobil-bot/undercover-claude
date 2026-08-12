# -*- coding: utf-8 -*-
"""
Buat file SIAP UPLOAD (Shopee/TikTok/Lazada) yang HANYA berisi baris yang
SKU-nya berubah, digabung 1 file PER CHANNEL (channel beda struktur kolom,
tidak bisa digabung lintas channel), tapi struktur kolom & header asli
platform TETAP UTUH -- supaya file ini bisa langsung diupload, bukan cuma
laporan review.

Metadata baris boilerplate (search_condition dkk) sama di semua file sumber
per channel -- aman digabung jadi 1 sheet, header diambil dari file pertama
yg punya baris berubah.

Alur: repair_xlsx.py -> terapkan_listing_final.py (transform SKU) -> script ini
(saring baris yg berubah saja dari tiap file, gabung jadi 1 output per channel).
"""
import sys, os, glob, copy
import openpyxl

# konfigurasi kolom SKU & baris awal data per channel (harus sinkron dgn terapkan_listing_final.py)
CHANNEL_CFG = {
    'shopee': {'sheet_kw': ['sheet1'], 'sku_col': 6, 'start_row': 7},
    'tiktok': {'sheet_kw': ['template', 'brand'], 'sku_col': 11, 'start_row': 6},
    'lazada': {'sheet_kw': ['template'], 'sku_col': 13, 'start_row': 5},
}


def deteksi_channel(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    names = set(s.lower() for s in wb.sheetnames)
    wb.close()
    if 'template' in names and 'brand' in names:
        return 'tiktok'
    if 'sheet1' in names:
        return 'shopee'
    if 'template' in names:
        return 'lazada'
    return None


def cari_sheet(wb, channel):
    nama_target = {'shopee': 'Sheet1', 'tiktok': 'Template', 'lazada': 'template'}[channel]
    return wb[nama_target] if nama_target in wb.sheetnames else wb[wb.sheetnames[0]]


def salin_baris(ws_src, r_src, ws_dst, r_dst):
    for c in range(1, ws_src.max_column + 1):
        sel = ws_src.cell(row=r_src, column=c)
        dsel = ws_dst.cell(row=r_dst, column=c, value=sel.value)
        dsel.fill = copy.copy(sel.fill)
        dsel.number_format = sel.number_format


def proses_channel(channel, pasangan, out_path):
    cfg = CHANNEL_CFG[channel]
    sku_col, start_row = cfg['sku_col'], cfg['start_row']

    wb_out = None
    ws_out = None
    r_out = start_row
    total = 0
    per_file = []

    for f_lama, f_baru in pasangan:
        wb_lama = openpyxl.load_workbook(f_lama, data_only=True)
        ws_lama = cari_sheet(wb_lama, channel)
        wb_baru = openpyxl.load_workbook(f_baru, data_only=False)
        ws_baru = cari_sheet(wb_baru, channel)

        baris_berubah = []
        for r in range(start_row, ws_baru.max_row + 1):
            sku_lama = ws_lama.cell(row=r, column=sku_col).value
            sku_baru = ws_baru.cell(row=r, column=sku_col).value
            if sku_baru and sku_baru != sku_lama:
                baris_berubah.append(r)

        if not baris_berubah:
            continue

        if wb_out is None:
            wb_out = wb_baru
            ws_out = ws_baru
            semua_baris = set(range(start_row, ws_out.max_row + 1))
            dihapus = sorted(semua_baris - set(baris_berubah), reverse=True)
            for r in dihapus:
                ws_out.delete_rows(r, 1)
            r_out = start_row + len(baris_berubah)
        else:
            for r in baris_berubah:
                salin_baris(ws_baru, r, ws_out, r_out)
                r_out += 1

        total += len(baris_berubah)
        per_file.append((os.path.basename(f_baru), len(baris_berubah)))

    if wb_out is None:
        return 0, []

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    wb_out.save(out_path)
    return total, per_file


if __name__ == '__main__':
    FIX_DIR = sys.argv[1] if len(sys.argv) > 1 else 'fix'
    HASIL_DIR = sys.argv[2] if len(sys.argv) > 2 else 'hasil'
    OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else 'siap_upload'

    # peta nama file "fix" (sebelum transform) -> nama file "hasil" (sesudah transform), per channel
    per_channel = {}
    for p_baru in sorted(glob.glob(os.path.join(HASIL_DIR, '*.xlsx'))):
        nm = os.path.basename(p_baru)
        p_lama = os.path.join(FIX_DIR, nm)
        if not os.path.exists(p_lama):
            print(f'  ? {nm}: pasangan file fix tidak ditemukan, dilewati')
            continue
        chan = deteksi_channel(p_lama)
        if chan is None:
            print(f'  ? {nm}: channel tak terdeteksi, dilewati')
            continue
        per_channel.setdefault(chan, []).append((p_lama, p_baru))

    for chan, pasangan in per_channel.items():
        out_path = os.path.join(OUT_DIR, f'SIAP_UPLOAD_{chan.upper()}.xlsx')
        total, per_file = proses_channel(chan, pasangan, out_path)
        if total == 0:
            print(f'[{chan}] tidak ada baris berubah, tidak dibuat output')
            continue
        print(f'[{chan}] -> {out_path}')
        for nama, n in per_file:
            print(f'    {nama:30s} -> {n} baris')
        print(f'    total: {total} baris\n')
