# -*- coding: utf-8 -*-
"""
Perbaiki SKU Mini Cooper di listing UA (Shopee/TikTok/Lazada):
  1. Segmen generasi yang salah  -> disesuaikan ke 3P/5P menurut JUMLAH PINTU
  2. SKU yang masih kosong        -> diisi lengkap

Aturan generasi diambil dari `formula_config.MANUAL_GROUPS['Mini Cooper']`
(instruksi user: "penentunya MURNI jumlah pintu, tipe bodi diabaikan"), bukan
ditulis ulang di sini -- jadi kalau aturannya direvisi, script ini ikut.

Segmen KATEGORI & WARNA diturunkan dari pola SKU Mini Cooper yang SUDAH ADA di
listing Shopee Reguler (dipakai sbg contoh acuan), bukan dikarang:
    MNI-COO-UA-R-{3P|5P}-{ABU,BRU,HTM,MRH,GRN}     <- warna dasar
    MNI-COO-UA-S-{3P|5P}-{EAB,EBR,EMR,PAB,...}     <- warna strip
    MNI-COO-UA-P-{3P|5P}-{ABU,SLV}                 <- Premium
    MNI-COO-UA-E-{3P|5P}-ABU                       <- Exclusive

Khusus LAZADA: SKU wajib unik per varian, sedangkan skema ini sengaja membuat
beberapa varian berbagi kode (mis. Hatch/Paceman/Roadster 3 Pintu di listing
Exclusive semuanya MNI-COO-UA-E-3P-ABU). Karena itu, kalau kode yang dihasilkan
bentrok di dalam satu listing Lazada, ditambahkan akhiran pembeda `_G2`, `_G3`,
... mengikuti konvensi yang SUDAH dipakai di data Lazada mereka.

Pemakaian:
  python3 fix_sku_mini_cooper.py <file_formula.xlsx> <folder_out> <folder_listing...>
"""
import sys, os, glob, copy, re, warnings
from collections import defaultdict

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import formula_config as FC
FORMULA_PATH = sys.argv[1]
FC.FORMULA_XLSX = FORMULA_PATH
FC.load.__defaults__ = (FORMULA_PATH,)

import update_harga_per_sku as UH
import apply_formula_sku as AF

CFG, _ = FC.load(FORMULA_PATH)
MINI = CFG['Mini Cooper']
MASTERFMT = AF.MASTERFMT
ORANGE = PatternFill('solid', fgColor='FFC000')

PREFIX = 'MNI-COO-UA'

WARNA_DASAR = {
    'abu-abu': 'ABU', 'abu abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
    'merah': 'MRH', 'hijau army': 'GRN', 'silver': 'SLV',
}
WARNA_STRIP = {
    'elite abu': 'EAB', 'elite biru': 'EBR', 'elite merah': 'EMR',
    'epic abu': 'PAB', 'epic biru': 'PBR', 'epic merah': 'PMR',
    'warrior abu': 'WAB', 'warrior biru': 'WBR', 'warrior merah': 'WMR',
}
# strip dicek duluan: "Elite Abu" mengandung "abu" juga, kalau warna dasar
# dicek lebih dulu bisa salah jadi ABU
SUFFIX_LZ = re.compile(r'_[A-Za-z0-9]+$')


def kategori(nama_listing):
    n = nama_listing.lower()
    if 'exclusive' in n:
        return 'E'
    if 'premium' in n:
        return 'P'
    return None          # Reguler -> tergantung warnanya (R atau S)


def bagian_warna(var):
    v = ' '.join(str(var).lower().replace(',', ' , ').split())
    for teks, kode in WARNA_STRIP.items():
        if teks in v:
            return kode, 'S'
    for teks, kode in WARNA_DASAR.items():
        if teks in v:
            return kode, 'R'
    return None, None


def sku_seharusnya(nama_listing, var):
    """SKU lengkap yang benar utk baris ini; None kalau tak bisa ditentukan"""
    gen = FC.seg_for_variant(MINI, var)
    if not gen:
        return None
    kat = kategori(nama_listing)
    warna, kat_warna = bagian_warna(var)
    if kat == 'E':
        # Exclusive: varian cuma tipe bodi + pintu, tanpa warna -> selalu ABU
        return f'{PREFIX}-E-{gen}-ABU'
    if kat == 'P':
        return f'{PREFIX}-P-{gen}-{warna or "ABU"}'
    if warna is None:
        return None
    return f'{PREFIX}-{kat_warna}-{gen}-{warna}'


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


def proses(out_dir, folders):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = []

    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=False)
        ch = UH.deteksi_channel(wb)
        if ch is None:
            continue
        ws = UH.cari_sheet(wb, ch)
        wbv = openpyxl.load_workbook(path, data_only=True)
        wsv = UH.cari_sheet(wbv, ch)
        col = UH.resolve_cols(wsv, ch)
        start = UH.STARTROW[ch]

        # utk Lazada: kode yg sudah terpakai per listing, supaya akhiran pembeda
        # tidak menabrak baris yang sudah ada
        terpakai = defaultdict(set)
        if ch == 'lazada':
            for r in range(start, wsv.max_row + 1):
                nm = str(wsv.cell(row=r, column=col['nama']).value or '')
                s = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
                if 'mini cooper' in nm.lower() and s:
                    terpakai[nm].add(s)

        ubah = []
        for r in range(start, wsv.max_row + 1):
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if 'mini cooper' not in nm.lower():
                continue
            var = str(wsv.cell(row=r, column=col['var']).value or '')
            lama = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
            benar = sku_seharusnya(nm, var)
            if not benar:
                continue

            lama_inti = SUFFIX_LZ.sub('', lama) if lama and not MASTERFMT.match(lama) else lama
            if lama_inti == benar:
                continue                      # sudah benar

            baru = benar
            if ch == 'lazada':
                # jaga keunikan: pakai akhiran kalau kode dasarnya sudah dipakai
                if baru in terpakai[nm]:
                    i = 2
                    while f'{benar}_G{i}' in terpakai[nm]:
                        i += 1
                    baru = f'{benar}_G{i}'
                terpakai[nm].discard(lama)
                terpakai[nm].add(baru)

            jenis = 'isi kosong' if not lama or not MASTERFMT.match(lama_inti) else 'koreksi segmen'
            ubah.append((r, baru))
            laporan.append((ch, os.path.basename(path), nm, var, lama, baru, jenis))

        if not ubah:
            continue

        for r, baru in ubah:
            sel = ws.cell(row=r, column=col['sku'])
            sel.value = baru
            sel.fill = ORANGE

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
        out = os.path.join(out_dir, f'FIX_SKU_MINI_COOPER_UA_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan


if __name__ == '__main__':
    out_dir = sys.argv[2]
    folders = sys.argv[3:]
    hasil, laporan = proses(out_dir, folders)

    from collections import Counter
    c = Counter((ch, j) for ch, _, _, _, _, _, j in laporan)
    print(f'Total baris diperbaiki: {len(laporan)}')
    for (ch, j), n in sorted(c.items()):
        print(f'  {ch:7s} {j:16s} {n:3d}')

    print('\nContoh perubahan:')
    for ch, fn, nm, var, lama, baru, j in laporan[:14]:
        print(f'  [{ch}] {var[:24]:26s} {lama!r:34} -> {baru}   ({j})')

    print()
    for ch, p in sorted(hasil.items()):
        print(f'[{ch}] -> {os.path.basename(p)}')
