# -*- coding: utf-8 -*-
"""
Isi SKU baris catch-all ("Model/Tahun Lain", "Model Lain/Custom") yang KOSONG,
TAPI HANYA utk kasus AUTO_FIXABLE: semua sibling (varian generasi spesifik,
warna sama, produk sama) di file itu pakai SKU IDENTIK -- dan produknya match
ke referensi "Data Mobil [dgn] Formula Yang Sama" dgn Total Formula=1 (atau
tidak terdaftar di referensi sama sekali, krn artinya tidak diketahui py >1
formula).

Ditemukan dari laporan user: Mazda MX-5 RF (UA Shopee) py belasan varian
"Model/Tahun Lain" per warna/tier yg SKU-nya kosong, padahal semua varian
generasi spesifik (Gen 1-4) di warna sama pakai kode G1 yg SAMA persis --
polanya sistemik, ditemukan jg di produk lain lintas toko (lihat
scan_catchall_kosong.py utk detail deteksi & AMBIGU/TANPA_SIBLING).

Pemakaian: python3 isi_catchall_kosong.py <folder_masukan> <folder_keluaran> <file_referensi_formula.xlsx> [nama_toko]
"""
import sys, os, glob, re
import openpyxl
from openpyxl.styles import PatternFill
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from scan_catchall_kosong import (
    CHANNEL_CFG, deteksi_channel, cari_sheet, signature_warna, is_catchall,
)

ORANGE = PatternFill('solid', fgColor='FFC000')


def norm(s):
    s = str(s or '').lower()
    s = re.sub(r'undercover autocare\s*-\s*', '', s)
    s = re.sub(r'cover mobil\s*/?\s*selimut mobil\s*', '', s)
    s = re.sub(r'cover mobil\s*', '', s)
    s = re.sub(r'\b(reguler|premium|exclusive|extreme|transparan|outdoor|semi|indoor|dan)\b', '', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
    return s


def baca_referensi(path_ref):
    wb = openpyxl.load_workbook(path_ref, data_only=True)
    ws = wb['Sheet2']
    blok = []
    cur = None
    for r in range(4, ws.max_row + 1):
        no = ws.cell(row=r, column=1).value
        nama = ws.cell(row=r, column=2).value
        gen = ws.cell(row=r, column=3).value
        total = ws.cell(row=r, column=4).value
        if no is not None:
            if cur:
                blok.append(cur)
            cur = {'nama': nama, 'total': total}
        if gen and cur and 'gens' not in cur:
            cur['gens'] = []
        if gen and cur:
            cur['gens'].append(gen)
    if cur:
        blok.append(cur)
    ref = {}
    for b in blok:
        if not b['nama']:
            continue
        toks = tuple(sorted(norm(b['nama']).split()))
        ref[toks] = b['total']
    return ref


def boleh_fix(nama_produk, ref, only_listed=False):
    """True kalau model terdaftar di referensi dgn Total Formula=1.
    only_listed=False (default): model yg TIDAK terdaftar di referensi jg diizinkan
    (asumsi aman krn tdk diketahui py >1 formula). only_listed=True: HARUS eksplisit
    match ke referensi Total=1 -- dipakai utk scope ketat (mis. "213 terlaris")."""
    toks = tuple(sorted(norm(nama_produk).split()))
    total = ref.get(toks)
    if total is None:
        return not only_listed
    if isinstance(total, (int, float)) and int(total) == 1:
        return True
    return False  # terdaftar dgn >1 formula ATAU nilai tak jelas ('?') -> jangan sentuh


def proses_file(path_in, path_out, ref, only_listed=False):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    chan = deteksi_channel(wb)
    if chan is None:
        return None, 0, 0
    cfg = CHANNEL_CFG[chan]
    ws = cari_sheet(wb, chan)

    wb_val = openpyxl.load_workbook(path_in, data_only=True)
    ws_val = cari_sheet(wb_val, chan)

    grup = defaultdict(list)
    for r in range(cfg['start_row'], ws_val.max_row + 1):
        pid = ws_val.cell(row=r, column=cfg['pid_col']).value
        nm = ws_val.cell(row=r, column=cfg['nama_col']).value
        var = ws_val.cell(row=r, column=cfg['var_col']).value
        sku = ws_val.cell(row=r, column=cfg['sku_col']).value
        if pid is None or not var:
            continue
        sig = signature_warna(var)
        grup[(pid, sig)].append({'row': r, 'nama': nm, 'var': var, 'sku': sku, 'catchall': is_catchall(var)})

    diisi = 0
    dilewati_multi_formula = 0
    for (pid, sig), rows in grup.items():
        catchall_kosong = [x for x in rows if x['catchall'] and not x['sku']]
        if not catchall_kosong:
            continue
        siblings_terisi = [x['sku'] for x in rows if not x['catchall'] and x['sku']]
        if not siblings_terisi or len(set(siblings_terisi)) != 1:
            continue
        target_sku = siblings_terisi[0]
        for cr in catchall_kosong:
            if not boleh_fix(cr['nama'], ref, only_listed):
                dilewati_multi_formula += 1
                continue
            cell = ws.cell(row=cr['row'], column=cfg['sku_col'])
            cell.value = target_sku
            cell.fill = ORANGE
            diisi += 1

    wb.save(path_out)
    return chan, diisi, dilewati_multi_formula


if __name__ == '__main__':
    FOLDER_IN = sys.argv[1]
    FOLDER_OUT = sys.argv[2]
    REF_PATH = sys.argv[3]
    ONLY_LISTED = len(sys.argv) > 4 and sys.argv[4] == 'only_listed'
    os.makedirs(FOLDER_OUT, exist_ok=True)

    ref = baca_referensi(REF_PATH)
    print(f'Referensi dimuat: {len(ref)} model' + (' (mode: HANYA yg terdaftar Total=1)' if ONLY_LISTED else ''))

    total_diisi = 0
    for path in sorted(glob.glob(os.path.join(FOLDER_IN, '*.xlsx'))):
        nm = os.path.basename(path)
        out_path = os.path.join(FOLDER_OUT, nm)
        chan, diisi, dilewati = proses_file(path, out_path, ref, ONLY_LISTED)
        if chan is None:
            print(f'  ? {nm}: channel tak terdeteksi, dilewati')
            continue
        total_diisi += diisi
        print(f'  [{chan:6s}] {nm:30s} -> {diisi:3d} baris catch-all diisi'
              + (f', {dilewati} dilewati (multi-formula/tak jelas)' if dilewati else ''))
    print(f'\nTotal baris catch-all diisi: {total_diisi}')
