# -*- coding: utf-8 -*-
"""
Buat file siap-upload yang BENAR di DUA kolom sekaligus: SKU (hasil konsolidasi)
DAN Harga (harga baru). Menggantikan pendekatan dua file terpisah.

MASALAH YANG DIPERBAIKI (ditemukan user 2026-08-15 dari screenshot Shopee):
File update harga sebelumnya dibangun dari folder `fix/` (export ASLI), sehingga
kolom SKU-nya masih kode lama (mis. DHT-XNA-... untuk Xenia). Begitu diupload,
marketplace menulis balik kolom SKU itu dan KONSOLIDASI SKU YANG SUDAH DITERAPKAN
JADI TER-REVERT. Sebaliknya, file konsolidasi SKU dibangun sebelum harga baru ada,
jadi kolom harganya masih harga lama -- upload file itu akan menghapus harga baru.
Dua file itu saling menimpa. Karena itu keduanya digabung di sini.

Prinsip: basis = folder `hasil/` (SKU sudah dikonsolidasi), lalu harga baru
ditimpakan di atasnya. Baris yang diikutkan = yang BERBEDA dari `fix/` (export
asli) pada kolom SKU ATAU kolom harga -- itulah yang perlu dikirim balik ke
marketplace.

Pemakaian:
  python3 gabung_sku_harga.py <file_harga_baru.xlsx> <out_dir> <toko>:<folder_fix>:<folder_hasil> [...]
  contoh: ... UA:/x/ua/fix:/x/ua/hasil OT:/y/ot/fix:/y/ot/hasil
Harga baru hanya diterapkan ke toko yang disebut di HARGA_UNTUK_TOKO.
"""
import sys, os, glob, copy
import openpyxl
from openpyxl.styles import PatternFill

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harga_baru_matriks import TAMBAHAN_STRIP

ORANGE = PatternFill('solid', fgColor='FFC000')

# harga baru sementara hanya untuk toko Undercover Autocare (instruksi user);
# toko lain cukup ikut perbaikan SKU-nya saja
HARGA_UNTUK_TOKO = {'UA'}

CFG = {
    'shopee': {'sheet': 'Sheet1',   'nama': 2, 'sku': 6,  'harga': 7, 'start': 7},
    'tiktok': {'sheet': 'Template', 'nama': 3, 'sku': 11, 'harga': 9, 'start': 6},
    'lazada': {'sheet': 'template', 'nama': 3, 'sku': 13, 'harga': 9, 'start': 5},
}

PETA_MODEL = {
    'Toyota Avanza':                'toyota avanza',
    'Honda Brio Satya / RS':        'honda brio',
    'Toyota Innova':                'toyota innova',
    'Honda Jazz':                   'honda jazz',
    'Suzuki Ertiga':                'suzuki ertiga',
    'Honda HR-V / e:N1':            'honda hrv',
    'Toyota Agya':                  'toyota agya',
    'Daihatsu Ayla':                'daihatsu ayla',
    'Daihatsu Xenia':               'daihatsu xenia',
    'Nissan Livina / Grand Livina': 'nissan grand livina',
}
KECUALI = ('x-gear', 'xgear', 'custom', 'roofbox')
OVERRIDE_REGULER = {'Honda Brio Satya / RS': 332000, 'Honda Jazz': 332000}


def deteksi_channel(wb):
    n = set(s.lower() for s in wb.sheetnames)
    if 'template' in n and 'brand' in n:
        return 'tiktok'
    if 'sheet1' in n:
        return 'shopee'
    if 'template' in n:
        return 'lazada'
    return None


def cari_sheet(wb, ch):
    t = CFG[ch]['sheet']
    return wb[t] if t in wb.sheetnames else wb[wb.sheetnames[0]]


def segmen_kat(sku):
    if not sku or not isinstance(sku, str):
        return None
    b = sku.strip().split('-')
    return b[3].upper() if len(b) >= 6 else None


def cocok_model(nama):
    low = str(nama or '').lower()
    if any(k in low for k in KECUALI):
        return None
    for nm, pola in PETA_MODEL.items():
        if pola in low:
            return nm
    return None


def baca_harga(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Harga Baru']
    h = {}
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=2).value
        if nm in PETA_MODEL:
            h[nm] = {'R': ws.cell(row=r, column=7).value,
                     'S': ws.cell(row=r, column=8).value}
    for nm, reg in OVERRIDE_REGULER.items():
        if nm in h:
            h[nm] = {'R': reg, 'S': reg + TAMBAHAN_STRIP}
    return h


def sama(a, b):
    """bandingkan nilai sel yg bisa tersimpan sbg angka ATAU teks (Lazada)"""
    if a is None or b is None:
        return a is b
    try:
        return int(float(a)) == int(float(b))
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        # JANGAN pakai cell(..., value=s.value): openpyxl mengabaikan value=None,
        # jadi sel tujuan yang sudah terisi TIDAK ikut dikosongkan dan baris hasil
        # membawa nilai sisa baris yang digeser (terbukti 2026-09-07: kolom
        # "Min. Jumlah Pembelian" Shopee ikut kebawa). Set .value eksplisit.
        d = ws_d.cell(row=r_d, column=c)
        d.value = s.value
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def proses_toko(toko, dir_fix, dir_hasil, harga, out_dir):
    hasil_out = {}
    stat = {}
    for path_hasil in sorted(glob.glob(os.path.join(dir_hasil, '*.xlsx'))):
        nama_file = os.path.basename(path_hasil)
        path_fix = os.path.join(dir_fix, nama_file)
        if not os.path.exists(path_fix):
            print(f'  ? {toko}/{nama_file}: pasangan fix tidak ada, dilewati')
            continue

        wb = openpyxl.load_workbook(path_hasil, data_only=False)
        ch = deteksi_channel(wb)
        if ch is None:
            continue
        cfg = CFG[ch]
        ws = cari_sheet(wb, ch)

        wbh = openpyxl.load_workbook(path_hasil, data_only=True)
        wsh = cari_sheet(wbh, ch)
        wbf = openpyxl.load_workbook(path_fix, data_only=True)
        wsf = cari_sheet(wbf, ch)

        n_sku, n_harga, baris = 0, 0, []
        for r in range(cfg['start'], wsh.max_row + 1):
            sku_asli = wsf.cell(row=r, column=cfg['sku']).value
            sku_baru = wsh.cell(row=r, column=cfg['sku']).value
            harga_asli = wsf.cell(row=r, column=cfg['harga']).value

            sku_berubah = sku_baru and not sama(sku_asli, sku_baru)
            harga_berubah = False

            if toko in HARGA_UNTUK_TOKO:
                target = cocok_model(wsh.cell(row=r, column=cfg['nama']).value)
                kat = segmen_kat(sku_baru)
                if target and kat in ('R', 'S'):
                    ht = harga[target][kat]
                    if not sama(harga_asli, ht):
                        sel = ws.cell(row=r, column=cfg['harga'])
                        sel.value = ht
                        sel.fill = ORANGE
                        harga_berubah = True

            if sku_berubah or harga_berubah:
                baris.append(r)
                n_sku += 1 if sku_berubah else 0
                n_harga += 1 if harga_berubah else 0

        if not baris:
            continue

        n_kol = ws.max_column
        for i, r in enumerate(baris):
            t = cfg['start'] + i
            if t != r:
                salin(ws, r, ws, t, n_kol)
        sisa = cfg['start'] + len(baris)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        key = ch
        if key not in hasil_out:
            hasil_out[key] = (wb, ws, cfg['start'] + len(baris))
            stat[key] = [0, 0, 0]
        else:
            wo, wso, r_out = hasil_out[key]
            for i in range(len(baris)):
                salin(ws, cfg['start'] + i, wso, r_out + i, n_kol)
            hasil_out[key] = (wo, wso, r_out + len(baris))
        stat[key][0] += len(baris)
        stat[key][1] += n_sku
        stat[key][2] += n_harga

    keluar = {}
    for ch, (wb_o, _, _) in hasil_out.items():
        out = os.path.join(out_dir, f'UPLOAD_{toko}_{ch.upper()}.xlsx')
        wb_o.save(out)
        keluar[ch] = (out, stat[ch])
    return keluar


if __name__ == '__main__':
    path_harga = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    harga = baca_harga(path_harga)

    print('Harga baru yg dipakai (khusus toko UA):')
    for nm, v in harga.items():
        print(f'  {nm:32s} R Rp{v["R"]:,}  S Rp{v["S"]:,}')
    print()

    for arg in sys.argv[3:]:
        toko, dir_fix, dir_hasil = arg.split(':')
        keluar = proses_toko(toko, dir_fix, dir_hasil, harga, out_dir)
        for ch, (out, st) in sorted(keluar.items()):
            print(f'[{toko} {ch:6s}] {st[0]:4d} baris '
                  f'(SKU berubah {st[1]}, harga berubah {st[2]}) -> {os.path.basename(out)}')
