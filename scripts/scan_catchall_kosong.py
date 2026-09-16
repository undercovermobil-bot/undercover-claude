# -*- coding: utf-8 -*-
"""
Scan listing utk pola: varian "catch-all" (mis. "Model/Tahun Lain", "Model Lain/Custom")
yang SKU-nya KOSONG, padahal varian generasi spesifik (Gen 1/2/3/dst) dgn warna yg SAMA
di produk yg SAMA semuanya pakai SKU formula yg SAMA (identik) -- artinya mobil itu cuma
py 1 formula, jadi catch-all-nya SEHARUSNYA bisa diisi kode yg sama juga.

Dipicu oleh temuan user: Mazda MX-5 RF (UA Shopee) py pola persis ini.

Klasifikasi tiap catch-all row:
  AUTO_FIXABLE : semua sibling (gen spesifik, warna sama, produk sama) py SKU IDENTIK -> aman diisi
  AMBIGU       : sibling py SKU BEDA-BEDA (multi-formula) -> jangan auto-isi, perlu keputusan
  TANPA_SIBLING: tidak ada sibling gen spesifik dgn warna sama & SKU terisi -> tidak bisa disimpulkan

Pemakaian: python3 scan_catchall_kosong.py <folder1> [folder2] ...
Tiap folder berisi file .xlsx yg SUDAH di-repair (hasil repair_xlsx.py).
"""
import sys, os, glob, re
import openpyxl
from collections import defaultdict

CATCHALL_RE = re.compile(r'model.*lain|lain.*model|tahun\s*lain|model.*custom', re.IGNORECASE)
GEN_RE = re.compile(r'gen\s*\d+|\(\s*\d{4}\s*-\s*\d{4}\s*\)|\d{4}\s*-\s*\d{4}', re.IGNORECASE)

CHANNEL_CFG = {
    'shopee': {'sheet_kw': ['sheet1'], 'pid_col': 1, 'nama_col': 2, 'var_col': 4, 'sku_col': 6, 'start_row': 7},
    'tiktok': {'sheet_kw': ['template', 'brand'], 'pid_col': 1, 'nama_col': 3, 'var_col': 6, 'sku_col': 11, 'start_row': 6},
    'lazada': {'sheet_kw': ['template'], 'pid_col': 1, 'nama_col': 3, 'var_col': 14, 'sku_col': 13, 'start_row': 5},
}


def deteksi_channel(wb):
    names = set(s.lower() for s in wb.sheetnames)
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


def signature_warna(var_text):
    """pisahkan bagian 'warna' dari teks varian, buang bagian generasi/catch-all -> jadi kunci grouping"""
    parts = [p.strip() for p in str(var_text or '').split(',')]
    sisa = [p for p in parts if not GEN_RE.search(p) and not CATCHALL_RE.search(p)]
    return ' '.join(sorted(sisa)).lower()


def is_catchall(var_text):
    return bool(CATCHALL_RE.search(str(var_text or '')))


def scan_file(path, label):
    wb = openpyxl.load_workbook(path, data_only=True)
    chan = deteksi_channel(wb)
    if chan is None:
        print(f'  ? {label}: channel tak terdeteksi, dilewati')
        return []
    cfg = CHANNEL_CFG[chan]
    ws = cari_sheet(wb, chan)

    # kumpulkan semua baris per (pid, signature_warna)
    grup = defaultdict(list)
    for r in range(cfg['start_row'], ws.max_row + 1):
        pid = ws.cell(row=r, column=cfg['pid_col']).value
        nm = ws.cell(row=r, column=cfg['nama_col']).value
        var = ws.cell(row=r, column=cfg['var_col']).value
        sku = ws.cell(row=r, column=cfg['sku_col']).value
        if pid is None or not var:
            continue
        sig = signature_warna(var)
        grup[(pid, sig)].append({'row': r, 'nama': nm, 'var': var, 'sku': sku, 'catchall': is_catchall(var)})

    hasil = []
    for (pid, sig), rows in grup.items():
        catchall_kosong = [x for x in rows if x['catchall'] and not x['sku']]
        if not catchall_kosong:
            continue
        siblings_terisi = [x['sku'] for x in rows if not x['catchall'] and x['sku']]
        for cr in catchall_kosong:
            if not siblings_terisi:
                status = 'TANPA_SIBLING'
                target = None
            elif len(set(siblings_terisi)) == 1:
                status = 'AUTO_FIXABLE'
                target = siblings_terisi[0]
            else:
                status = 'AMBIGU'
                target = sorted(set(siblings_terisi))
            hasil.append({
                'file': label, 'channel': chan, 'row': cr['row'], 'nama': cr['nama'],
                'var': cr['var'], 'status': status, 'target': target,
                'n_siblings': len(siblings_terisi),
            })
    return hasil


if __name__ == '__main__':
    semua = []
    for folder in sys.argv[1:]:
        for path in sorted(glob.glob(os.path.join(folder, '*.xlsx'))):
            label = os.path.relpath(path)
            semua.extend(scan_file(path, label))

    auto = [x for x in semua if x['status'] == 'AUTO_FIXABLE']
    ambigu = [x for x in semua if x['status'] == 'AMBIGU']
    tanpa = [x for x in semua if x['status'] == 'TANPA_SIBLING']

    print(f'\n=== RINGKASAN ===')
    print(f'AUTO_FIXABLE (aman diisi, sibling 1 formula identik): {len(auto)}')
    print(f'AMBIGU (sibling formula beda-beda, perlu keputusan): {len(ambigu)}')
    print(f'TANPA_SIBLING (tidak ada sibling terisi, tak bisa disimpulkan): {len(tanpa)}')

    # ringkas per produk (nama) biar tidak flood per-baris/per-warna
    from collections import Counter
    print(f'\n--- AUTO_FIXABLE per produk (top 30) ---')
    cnt = Counter((x['file'], x['nama']) for x in auto)
    for (f, nm), n in cnt.most_common(30):
        print(f'  [{n:3d}] {f:30s} {nm}')

    if ambigu:
        print(f'\n--- AMBIGU per produk (semua) ---')
        cnt2 = Counter((x['file'], x['nama']) for x in ambigu)
        for (f, nm), n in cnt2.most_common(50):
            contoh = next(x for x in ambigu if x['file'] == f and x['nama'] == nm)
            print(f'  [{n:3d}] {f:30s} {nm} | contoh target beda: {contoh["target"]}')
