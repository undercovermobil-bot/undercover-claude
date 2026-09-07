# -*- coding: utf-8 -*-
"""
Buat SKU BARU untuk produk yang listing-nya belum py SKU sama sekali, lalu
hasilkan 3 file: impor SKU Gudang BigSeller + file siap-upload Shopee + TikTok.

Dipicu 2026-08-15: order Isuzu D-MAX & Nissan Latio gagal diproses di BigSeller
("Pesanan ini belum dihubungkan dengan SKU Gudang") karena kolom SKU di kedua
listing itu KOSONG di semua channel.

Keputusan formula (dikonfirmasi user):
- Isuzu D-MAX  -> BEDA per generasi (5 kode: G1/G2/G2F1/G2F2/G3). Preseden:
  Mazda BT-50 (rebadge fisik D-MAX) sudah pakai pola per-generasi.
- Nissan Latio -> SATU formula (semua generasi pakai G1). Preseden: mayoritas
  sedan sekelas (March, Teana, Vios, Mazda 2, Kia Rio) pakai 1 kode.

Format SKU mengikuti konvensi master: MEREK-MODEL-TOKO-KAT-GEN-WARNA
Prefix diturunkan dari konvensi merek yg sudah ada (ISZ-MUX/ISZ-PTH -> ISZ-DMX;
NSN-MCH/NSN-NOT/dst -> NSN-LAT).
"""
import sys, os, glob, copy
import openpyxl
from openpyxl.styles import PatternFill, Font

ORANGE = PatternFill('solid', fgColor='FFC000')

CFG = {
    'shopee': {'sheet': 'Sheet1',   'nama': 2, 'var': 4,  'sku': 6,  'start': 7},
    'tiktok': {'sheet': 'Template', 'nama': 3, 'var': 6,  'sku': 11, 'start': 6},
}

WARNA_DASAR = {  # teks varian -> kode warna (kategori R)
    'abu-abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
    'merah': 'MRH', 'hijau army': 'GRN',
}
WARNA_STRIP = {  # teks varian -> kode warna (kategori S)
    'elite abu': 'EAB', 'elite biru': 'EBR', 'elite merah': 'EMR',
    'epic abu': 'PAB', 'epic biru': 'PBR', 'epic merah': 'PMR',
    'warrior abu': 'WAB', 'warrior biru': 'WBR', 'warrior merah': 'WMR',
}
NAMA_WARNA = {  # kode -> nama utk judul BigSeller
    'ABU': 'Abu-abu', 'HTM': 'Hitam', 'BRU': 'Biru Benhur', 'MRH': 'Merah',
    'GRN': 'Hijau Army', 'EAB': 'Elite Abu', 'EBR': 'Elite Biru',
    'EMR': 'Elite Merah', 'PAB': 'Epic Abu', 'PBR': 'Epic Biru',
    'PMR': 'Epic Merah', 'WAB': 'Warrior Abu', 'WBR': 'Warrior Biru',
    'WMR': 'Warrior Merah',
}

PRODUK = {
    'isuzu d-max': {
        'prefix': 'ISZ-DMX',
        'nama_bigseller': 'Isuzu D-MAX',
        'multi_gen': True,
        'gen': {   # potongan teks generasi (huruf kecil) -> kode GEN
            'gen 1': 'G1',
            'gen 2f 1': 'G2F1',
            'gen 2f 2': 'G2F2',
            'gen 2': 'G2',
            'gen 3': 'G3',
        },
        # "Model/Tahun Lain" tidak bisa disimpulkan dari data (produk multi-formula)
        # -> diarahkan ke generasi TERBARU. Ditandai di laporan supaya user bisa koreksi.
        'gen_catchall': 'G3',
    },
    'nissan latio': {
        'prefix': 'NSN-LAT',
        'nama_bigseller': 'Nissan Latio',
        'multi_gen': False,
        'gen': {},
        'gen_catchall': 'G1',
    },
}


def deteksi_channel(wb):
    n = set(s.lower() for s in wb.sheetnames)
    if 'template' in n and 'brand' in n:
        return 'tiktok'
    if 'sheet1' in n:
        return 'shopee'
    return None


def cari_sheet(wb, ch):
    t = CFG[ch]['sheet']
    return wb[t] if t in wb.sheetnames else wb[wb.sheetnames[0]]


def cocok_produk(nama):
    """hanya listing REGULER dari produk target"""
    low = str(nama or '').lower()
    if 'reguler' not in low:
        return None
    for key, cfg in PRODUK.items():
        if key in low:
            return key
    return None


def urai_varian(var_text, cfg_produk):
    """teks varian -> (kat, kode_warna, kode_gen, label_gen, is_catchall) atau None"""
    bagian = [b.strip() for b in str(var_text or '').split(',')]
    kode_warna = kat = None
    label_gen = None
    for b in bagian:
        low = b.lower()
        if low in WARNA_STRIP:
            kode_warna, kat = WARNA_STRIP[low], 'S'
        elif low in WARNA_DASAR:
            kode_warna, kat = WARNA_DASAR[low], 'R'
        else:
            label_gen = b
    if not kode_warna:
        return None

    catchall = False
    if label_gen is None:
        kode_gen = cfg_produk['gen_catchall']
        catchall = True
        label_gen = '(tanpa label generasi)'
    else:
        low = label_gen.lower()
        if 'lain' in low or 'custom' in low:
            kode_gen = cfg_produk['gen_catchall']
            catchall = True
        elif not cfg_produk['multi_gen']:
            kode_gen = 'G1'
        else:
            kode_gen = None
            # cocokkan yg paling spesifik dulu ("gen 2f 1" sebelum "gen 2")
            for pola in sorted(cfg_produk['gen'], key=len, reverse=True):
                if pola in low:
                    kode_gen = cfg_produk['gen'][pola]
                    break
            if kode_gen is None:
                return None
    return kat, kode_warna, kode_gen, label_gen, catchall


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


def proses(folders, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sku_terpakai = {}      # sku -> (produk, kat, warna, gen, label_gen)
    catchall_rows = []
    per_channel = {}
    laporan = {}
    tak_terurai = []

    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=False)
        ch = deteksi_channel(wb)
        if ch is None:
            continue
        cfg = CFG[ch]
        ws = cari_sheet(wb, ch)
        wbv = openpyxl.load_workbook(path, data_only=True)
        wsv = cari_sheet(wbv, ch)

        baris = []
        for r in range(cfg['start'], wsv.max_row + 1):
            nm = wsv.cell(row=r, column=cfg['nama']).value
            key = cocok_produk(nm)
            if not key:
                continue
            p = PRODUK[key]
            hasil = urai_varian(wsv.cell(row=r, column=cfg['var']).value, p)
            if hasil is None:
                tak_terurai.append((ch, r, str(nm), wsv.cell(row=r, column=cfg['var']).value))
                continue
            kat, warna, gen, label_gen, catchall = hasil
            sku = f"{p['prefix']}-UA-{kat}-{gen}-{warna}"
            sel = ws.cell(row=r, column=cfg['sku'])
            sel.value = sku
            sel.fill = ORANGE
            baris.append(r)
            sku_terpakai.setdefault(sku, (p['nama_bigseller'], kat, warna, gen, label_gen))
            if catchall:
                catchall_rows.append((ch, key, sku, str(wsv.cell(row=r, column=cfg['var']).value)))

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

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, cfg['start'] + len(baris))
            laporan[ch] = 0
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(baris)):
                salin(ws, cfg['start'] + i, wso, r_out + i, n_kol)
            per_channel[ch] = (wo, wso, r_out + len(baris))
        laporan[ch] += len(baris)

    keluar = {}
    for ch, (wb_o, _, _) in per_channel.items():
        out = os.path.join(out_dir, f'UPLOAD_SKU_BARU_UA_{ch.upper()}.xlsx')
        wb_o.save(out)
        keluar[ch] = out
    return keluar, laporan, sku_terpakai, catchall_rows, tak_terurai


def tulis_bigseller(sku_terpakai, path_contoh, out_path):
    """tiru header & kolom file contoh impor SKU Gudang BigSeller"""
    wbc = openpyxl.load_workbook(path_contoh)
    wsc = wbc['SKU']
    header = [wsc.cell(row=1, column=c).value for c in range(1, wsc.max_column + 1)]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'SKU'
    for c, h in enumerate(header, start=1):
        sel = ws.cell(row=1, column=c, value=h)
        sel.font = Font(bold=True)
    # baris 2 dikosongkan, persis seperti file contoh
    r = 3
    for sku in sorted(sku_terpakai):
        nama_mobil, kat, warna, gen, label_gen = sku_terpakai[sku]
        judul = f'Undercover Autocare - Cover Mobil {nama_mobil} Reguler {NAMA_WARNA[warna]}'
        if label_gen and label_gen != '(tanpa label generasi)':
            # sertakan generasi hanya kalau produknya memang beda kode per generasi
            if len({v[3] for v in sku_terpakai.values() if v[0] == nama_mobil}) > 1:
                judul += f' {label_gen}'
        ws.cell(row=r, column=1, value=sku)
        ws.cell(row=r, column=2, value=judul)
        ws.cell(row=r, column=5, value='Default Warehouse')
        ws.cell(row=r, column=6, value=5)
        r += 1
    for col, w in zip('AB', [26, 72]):
        ws.column_dimensions[col].width = w
    wb.save(out_path)
    return r - 3


if __name__ == '__main__':
    out_dir = sys.argv[1]
    path_contoh = sys.argv[2]
    folders = sys.argv[3:]

    keluar, laporan, sku_terpakai, catchall, tak_terurai = proses(folders, out_dir)

    bs_path = os.path.join(out_dir, 'IMPOR_SKU_GUDANG_DMAX_LATIO.xlsx')
    n_sku = tulis_bigseller(sku_terpakai, path_contoh, bs_path)

    print(f'SKU unik dibuat: {n_sku}')
    per_produk = {}
    for sku, v in sku_terpakai.items():
        per_produk.setdefault(v[0], []).append(sku)
    for nm, lst in sorted(per_produk.items()):
        gens = sorted({s.split('-')[4] for s in lst})
        print(f'  {nm:16s} {len(lst):3d} SKU | generasi: {gens}')
    print(f'\nBigSeller -> {os.path.basename(bs_path)}')
    for ch, out in sorted(keluar.items()):
        print(f'{ch:7s}    {laporan[ch]:3d} baris -> {os.path.basename(out)}')
    if catchall:
        from collections import Counter
        c = Counter((k, sku) for _, k, sku, _ in catchall)
        print(f'\nBaris "Model/Tahun Lain" yg diarahkan (perlu konfirmasi): {len(catchall)}')
        for (k, sku), n in sorted(c.items()):
            print(f'  {k:14s} -> {sku}  ({n} baris)')
    if tak_terurai:
        print(f'\nTIDAK TERURAI: {len(tak_terurai)}')
        for x in tak_terurai[:10]:
            print('  ', x)
