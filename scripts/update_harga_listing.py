# -*- coding: utf-8 -*-
"""
Buat file SIAP UPLOAD berisi UPDATE HARGA untuk listing e-commerce (Shopee/
TikTok/Lazada), hanya baris yang harganya berubah, tapi struktur & header asli
platform tetap utuh supaya bisa langsung diupload.

Sumber harga: kolom 'Harga Baru (Reguler)' & 'Harga Baru (Strip)' dari hasil
`harga_baru_matriks.py`. Hanya tier REGULER yang disentuh -- Premium (P),
Exclusive (E), Transparan (T) tidak ikut, karena harga HPP yang jadi dasar
perhitungan itu memang tier Reguler (diverifikasi: kolom 'Harga Jual ACTUAL'
di HPP == harga listing Reguler warna dasar saat ini, mis. Avanza Rp298.000,
Brio Rp284.000, Agya/Ayla Rp287.000).

Cara membedakan warna dasar vs warna strip: SEGMEN KE-4 SKU
(MEREK-MODEL-TOKO-KAT-GEN-WARNA), bukan parsing teks varian. Teks varian tidak
andal karena urutan bagiannya berubah-ubah antar listing ("Epic Abu,Gen 1" vs
"Gen 1,Abu-abu"), sedangkan segmen SKU konsisten: R=Reguler dasar, S=Strip
(Elite/Epic/Warrior), P=Premium, E=Exclusive, T=Transparan.

Pemakaian:
  python3 update_harga_listing.py <file_harga_baru.xlsx> <folder_out> <folder_listing...>
"""
import sys, os, re, glob, copy
import openpyxl
from openpyxl.styles import PatternFill

ORANGE = PatternFill('solid', fgColor='FFC000')

CFG = {
    'shopee': {'sheet': 'Sheet1',   'nama': 2, 'var': 4,  'sku': 6,  'harga': 7, 'start': 7},
    'tiktok': {'sheet': 'Template', 'nama': 3, 'var': 6,  'sku': 11, 'harga': 9, 'start': 6},
    'lazada': {'sheet': 'template', 'nama': 3, 'var': 14, 'sku': 13, 'harga': 9, 'start': 5},
}

# nama produk di file harga -> pola nama di listing (kata kunci model, huruf kecil)
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

# listing yg namanya mengandung ini TIDAK ikut walau modelnya cocok --
# produk terpisah dgn harga sendiri (varian bodi lain / custom)
KECUALI = ('x-gear', 'xgear', 'custom', 'roofbox')

KAT_KE_JENIS = {'R': 'reguler', 'S': 'strip'}


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
    target = CFG[ch]['sheet']
    return wb[target] if target in wb.sheetnames else wb[wb.sheetnames[0]]


def segmen_kategori(sku):
    """ambil segmen ke-4 (KAT) dari SKU MEREK-MODEL-TOKO-KAT-GEN-WARNA"""
    if not sku or not isinstance(sku, str):
        return None
    bagian = sku.strip().split('-')
    if len(bagian) < 6:
        return None
    return bagian[3].upper()


def cocok_model(nama_listing):
    """kembalikan nama produk di file harga kalau listing ini termasuk target"""
    low = str(nama_listing or '').lower()
    if any(k in low for k in KECUALI):
        return None
    for nama_harga, pola in PETA_MODEL.items():
        if pola in low:
            return nama_harga
    return None


def baca_harga_baru(path, override):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Harga Baru']
    harga = {}
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=2).value
        if not nm or nm not in PETA_MODEL:
            continue
        harga[nm] = {'reguler': ws.cell(row=r, column=7).value,
                     'strip': ws.cell(row=r, column=8).value}
    for nm, (reg, strip) in override.items():
        if nm in harga:
            harga[nm] = {'reguler': reg, 'strip': strip}
    return harga


def salin_baris(ws_src, r_src, ws_dst, r_dst, n_kolom):
    for c in range(1, n_kolom + 1):
        sel = ws_src.cell(row=r_src, column=c)
        d = ws_dst.cell(row=r_dst, column=c, value=sel.value)
        d.fill = copy.copy(sel.fill)
        d.number_format = sel.number_format


def proses(harga_baru, out_dir, folders):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = {}

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

        ubah = []
        for r in range(cfg['start'], wsv.max_row + 1):
            nm = wsv.cell(row=r, column=cfg['nama']).value
            target = cocok_model(nm)
            if not target:
                continue
            kat = segmen_kategori(wsv.cell(row=r, column=cfg['sku']).value)
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue  # Premium/Exclusive/Transparan/SKU tak terbaca -> jangan disentuh
            harga_lama = wsv.cell(row=r, column=cfg['harga']).value
            harga_target = harga_baru[target][jenis]
            try:
                sama = harga_lama is not None and int(float(harga_lama)) == int(harga_target)
            except (TypeError, ValueError):
                sama = False
            if sama:
                continue
            ubah.append((r, harga_target, target, jenis, harga_lama))

        if not ubah:
            continue

        # tulis harga baru ke workbook (in-memory)
        for r, harga_target, _, _, _ in ubah:
            sel = ws.cell(row=r, column=cfg['harga'])
            sel.value = harga_target
            sel.fill = ORANGE

        # padatkan hanya baris yg berubah ke atas, lalu hapus sisanya sekali panggil
        n_kolom = ws.max_column
        baris = [u[0] for u in ubah]
        for i, r in enumerate(baris):
            tgt = cfg['start'] + i
            if tgt != r:
                salin_baris(ws, r, ws, tgt, n_kolom)
        sisa = cfg['start'] + len(baris)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, cfg['start'] + len(baris))
            laporan[ch] = []
        else:
            wb_o, ws_o, r_out = per_channel[ch]
            for i in range(len(baris)):
                salin_baris(ws, cfg['start'] + i, ws_o, r_out + i, n_kolom)
            per_channel[ch] = (wb_o, ws_o, r_out + len(baris))

        for _, ht, tgt, jn, hl in ubah:
            laporan[ch].append((os.path.basename(path), tgt, jn, hl, ht))

    hasil = {}
    for ch, (wb_o, ws_o, _) in per_channel.items():
        out = os.path.join(out_dir, f'UPDATE_HARGA_UA_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan


if __name__ == '__main__':
    path_harga = sys.argv[1]
    out_dir = sys.argv[2]
    folders = sys.argv[3:]

    # instruksi eksplisit user 2026-08-15: Brio & Jazz dipatok Rp332.000 / strip Rp388.000
    OVERRIDE = {
        'Honda Brio Satya / RS': (332000, 388000),
        'Honda Jazz':            (332000, 388000),
    }

    harga_baru = baca_harga_baru(path_harga, OVERRIDE)
    print('Harga yg dipakai:')
    for nm, v in harga_baru.items():
        tanda = '  <- override' if nm in OVERRIDE else ''
        print(f'  {nm:32s} reguler Rp{v["reguler"]:,}  strip Rp{v["strip"]:,}{tanda}')

    hasil, laporan = proses(harga_baru, out_dir, folders)

    print()
    for ch in ['shopee', 'tiktok', 'lazada']:
        if ch not in laporan:
            print(f'[{ch}] tidak ada baris yg perlu diubah')
            continue
        rows = laporan[ch]
        print(f'\n[{ch}] {len(rows)} baris -> {hasil[ch]}')
        ringkas = {}
        for _, tgt, jn, hl, ht in rows:
            k = (tgt, jn)
            ringkas.setdefault(k, [0, hl, ht])
            ringkas[k][0] += 1
        for (tgt, jn), (n, hl, ht) in sorted(ringkas.items()):
            # harga lama bisa tersimpan sbg teks (Lazada) atau kosong -> jangan
            # diformat sbg angka mentah-mentah
            try:
                hl_str = f'Rp{int(float(hl)):,}'
            except (TypeError, ValueError):
                hl_str = f'{hl!r}'
            print(f'    {tgt:30s} {jn:8s} {n:3d} baris  {hl_str} -> Rp{ht:,}')
