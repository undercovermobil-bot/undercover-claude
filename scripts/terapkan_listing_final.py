# -*- coding: utf-8 -*-
"""
Terapkan konsolidasi SKU (Avanza/Xenia/Veloz + 5 pasangan) ke file listing riil,
hasilkan file SIAP UPLOAD per marketplace. File asli tidak disentuh, output ke folder
terpisah dengan nama jelas.

Dasar aturan (SEMUA sudah diverifikasi ke SKU asli listing UA Shopee 2026-08-11,
bukan tebakan dari master -- lihat claude-memory/project-undercover-sku-sync-status.md):
  - Sebagian besar model TARGET (Avanza-G1/G3, Calya, Rush, Feroza, Raize, Alphard,
    Ayla) hanya pakai SATU kode generasi (G1) di listing riil, KECUALI Avanza yang
    genuinely py 2 kode (G1 & G3).
  - Xenia SUDAH memakai kode G1/G3 yang sama skemanya dengan Avanza di listing riil
    (G1 utk Gen1&2, G3 utk Gen3) -- jadi transformasinya cuma tukar prefix MEREK-MODEL,
    segmen lain (TOKO-KAT-GEN-WARNA) dibiarkan apa adanya.
  - Veloz di listing riil SELALU G1 (walau py 2 label gen berbeda), tapi HARUS
    dipaksa jadi G3 saat pindah ke Avanza (instruksi eksplisit user).
  - Rocky di listing riil SELALU G1 utk kedua era (F70/F300 lama & A200/Gen2 baru),
    jadi rutenya (ke Feroza atau ke Raize) HARUS dibaca dari TEKS VARIAN, bukan
    dari kode SKU (karena kodenya sama-sama G1).
  - Sigra/Terios/Vellfire/Agya sama sekali tidak perlu paksa generasi -- tukar
    prefix saja, generasi ikut apa adanya (semua toh G1).

Pemakaian: python3 terapkan_listing_final.py <folder_masukan> <folder_keluaran>
Struktur kolom per channel (startrow 1-based, sesuai files_baru.py):
  Shopee : Nama Produk kol B(2), Nama Variasi kol D(4), SKU kol F(6), mulai baris 7
  TikTok : product_name kol C(3), variation_value kol F(6), seller_sku kol K(11), mulai baris 6
  Lazada : Nama Produk kol C(3), Variations kol N(14), Seller SKU kol M(13), mulai baris 5
"""
import sys, re, glob, os
import openpyxl
from openpyxl.styles import PatternFill

ORANGE = PatternFill('solid', fgColor='FFC000')

# ---------- prefix MEREK-MODEL utk tiap model (dicek bebas tabrakan sebelumnya) ----------
PREFIX = {
    'xenia': 'DHT-XNA', 'avanza': 'TYT-AVZ', 'veloz': 'TYT-VLZ',
    'sigra': 'DHT-SGR', 'calya': 'TYT-CLY',
    'terios': 'DHT-TRS', 'rush': 'TYT-RSH',
    'rocky': 'DHT-RCK', 'raize': 'TYT-RZE', 'feroza': 'DHT-FRZ',
    'vellfire': 'TYT-VLF', 'alphard': 'TYT-ALP',
    'agya': 'TYT-AGY', 'ayla': 'DHT-AYL',
}
# model SUMBER (yg SKU-nya diganti) -> model TARGET (prefix baru), + paksa gen (None = ikut apa adanya)
KONSOLIDASI = {
    'xenia':    ('avanza', None),     # G1->G1, G3->G3 (skema sudah sama)
    'veloz':    ('avanza', 'G3'),     # SELALU dipaksa G3
    'sigra':    ('calya', None),
    'terios':   ('rush', None),
    'vellfire': ('alphard', None),
    'agya':     ('ayla', None),
    # rocky ditangani terpisah (butuh baca teks varian, lihat rute_rocky())
}
KATA_ROCKY_LAMA = ('f70', 'f300', '1984', '1985', '1986', '1987', '1988', '1989',
                   '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997',
                   '1998', '1999', '2000', '2001', '2002')
KATA_ROCKY_BARU = ('a200', 'gen 2', 'gen2', '2019', '2020', '2021', '2022', '2023',
                   '2024', '2025', '2026')

RE_SKU = re.compile(r'^([A-Z0-9]+-[A-Z0-9]+)-([A-Z]+)-([A-Za-z0-9]+)-([A-Za-z0-9$]+)-([A-Za-z0-9_]+)$')


def rute_rocky(varian_text):
    low = str(varian_text or '').lower()
    if any(k in low for k in KATA_ROCKY_LAMA):
        return 'feroza'
    if any(k in low for k in KATA_ROCKY_BARU):
        return 'raize'
    return None  # tidak bisa dipastikan -> jangan disentuh


def deteksi_model(nama_produk):
    low = str(nama_produk or '').lower()
    # urutan penting: 'feroza long' beda produk dari 'feroza', jangan ikut tersentuh
    if 'feroza long' in low or 'feroza panjang' in low:
        return None
    for m in list(KONSOLIDASI) + ['rocky']:
        if m in low:
            return m
    return None


def transform_sku(sku, model, varian_text):
    if not sku or not isinstance(sku, str):
        return None, None
    m = RE_SKU.match(sku.strip())
    if not m:
        return None, None
    merek_model, toko, kat, gen, warna = m.groups()

    if model == 'rocky':
        target = rute_rocky(varian_text)
        if target is None:
            return None, 'rocky: era tidak terdeteksi dari teks varian'
        prefix_baru = PREFIX[target]
        gen_baru = gen  # Rocky selalu G1, target jg selalu G1 -> tetap
    else:
        target, paksa_gen = KONSOLIDASI[model]
        prefix_baru = PREFIX[target]
        gen_baru = paksa_gen or gen

    baru = f'{prefix_baru}-{toko}-{kat}-{gen_baru}-{warna}'
    return baru, None


def proses_shopee(path_in, path_out):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    ws = wb['Sheet1'] if 'Sheet1' in wb.sheetnames else wb[wb.sheetnames[0]]
    diubah, gagal = 0, []
    for r in range(7, ws.max_row + 1):
        nm = ws.cell(row=r, column=2).value
        model = deteksi_model(nm)
        if not model:
            continue
        cell = ws.cell(row=r, column=6)
        sku = cell.value
        var = ws.cell(row=r, column=4).value
        baru, err = transform_sku(sku, model, var)
        if err:
            gagal.append((r, nm, sku, var, err))
            continue
        if baru and baru != sku:
            cell.value = baru
            cell.fill = ORANGE
            diubah += 1
    wb.save(path_out)
    return diubah, gagal


def proses_tiktok(path_in, path_out):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    ws = wb['Template'] if 'Template' in wb.sheetnames else wb[wb.sheetnames[0]]
    diubah, gagal = 0, []
    for r in range(6, ws.max_row + 1):
        nm = ws.cell(row=r, column=3).value
        model = deteksi_model(nm)
        if not model:
            continue
        cell = ws.cell(row=r, column=11)
        sku = cell.value
        var = ws.cell(row=r, column=6).value
        baru, err = transform_sku(sku, model, var)
        if err:
            gagal.append((r, nm, sku, var, err))
            continue
        if baru and baru != sku:
            cell.value = baru
            cell.fill = ORANGE
            diubah += 1
    wb.save(path_out)
    return diubah, gagal


def proses_lazada(path_in, path_out):
    wb = openpyxl.load_workbook(path_in, data_only=False)
    ws = wb['template'] if 'template' in wb.sheetnames else wb[wb.sheetnames[0]]
    diubah, gagal = 0, []
    for r in range(5, ws.max_row + 1):
        nm = ws.cell(row=r, column=3).value
        model = deteksi_model(nm)
        if not model:
            continue
        cell = ws.cell(row=r, column=13)
        sku = cell.value
        var = ws.cell(row=r, column=14).value
        baru, err = transform_sku(sku, model, var)
        if err:
            gagal.append((r, nm, sku, var, err))
            continue
        if baru and baru != sku:
            cell.value = baru
            cell.fill = ORANGE
            diubah += 1
    wb.save(path_out)
    return diubah, gagal


PROSES = {'shopee': proses_shopee, 'tiktok': proses_tiktok, 'lazada': proses_lazada}


def deteksi_channel(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    names = set(s.lower() for s in wb.sheetnames)
    wb.close()
    if 'template' in names and 'brand' in names:
        return 'tiktok'
    if 'sheet1' in names:
        return 'shopee'
    if any('template' == n for n in names):
        return 'lazada'
    return None


if __name__ == '__main__':
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(src_dir, '*.xlsx'))):
        chan = deteksi_channel(path)
        if chan is None:
            print(f'  ? {os.path.basename(path)}: channel tak terdeteksi, dilewati')
            continue
        out_path = os.path.join(out_dir, os.path.basename(path))
        diubah, gagal = PROSES[chan](path, out_path)
        print(f'  [{chan:6s}] {os.path.basename(path):30s} -> {diubah:4d} SKU diubah, {len(gagal)} gagal')
        for g in gagal[:5]:
            print('      GAGAL:', g)
