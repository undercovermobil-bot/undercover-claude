# -*- coding: utf-8 -*-
"""
Samakan kode MEREK-MODEL untuk mobil kembar / model yang kodenya belum seragam.

Dua sasaran sekaligus:

A. MASTER -- model kembar yang di master punya kode SENDIRI padahal semua
   listing memakai kode model INDUK-nya (cover-nya memang sama). Kode master
   yang tidak terpakai itu jadi jebakan: begitu ada toko yang listingnya kosong,
   pengisian otomatis jatuh ke master dan menghasilkan kode yang salah (persis
   yang terjadi pada Daihatsu Taft GT di Otonation).

C. LISTING -- model yang kodenya beda antar toko/channel. Dibuatkan file
   siap-upload untuk baris yang menyimpang saja.

Semua pemetaan di bawah DIVERIFIKASI dulu: kode induk harus benar-benar milik
model induk di master, dan set generasi anak harus tercakup oleh induk (dicek
2026-09-04: keenam pasangan grup A semuanya cuma G1, induknya punya G1).

Pemakaian:
  python3 samakan_kode_kembar.py <master.xlsx> <folder_out> <nama_toko> <folder_listing...>

CATATAN: jalankan TERPISAH per toko. UA dan Otonation sama-sama channel Shopee,
kalau folder keduanya dicampur dalam satu run, barisnya masuk ke SATU file dan
tidak bisa diupload (tiap toko punya akun & product_id sendiri).
"""
import sys, os, glob, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH

ORANGE = PatternFill('solid', fgColor='FFC000')

# --- A. mobil kembar: kode master -> kode induk yang dipakai listing ---------
# (nama model di master, kode lama, kode induk, nama induk)
KEMBAR_MASTER = [
    ('Daihatsu Terios',  'DHT-TRS', 'TYT-RSH', 'Toyota Rush'),
    ('Toyota Veloz',     'TYT-VLZ', 'TYT-AVZ', 'Toyota Avanza'),
    ('Daihatsu Sigra',   'DHT-SGR', 'TYT-CLY', 'Toyota Calya'),
    ('Toyota Vellfire',  'TYT-VLF', 'TYT-ALP', 'Toyota Alphard'),
    ('Daihatsu Luxio',   'DHT-LXO', 'DHT-GMX', 'Daihatsu Gran Max Minibus'),
    ('Daihatsu Taft GT', 'DHT-TG',  'DHT-FRZ', 'Daihatsu Feroza'),
    # bukan mobil kembar -- murni menyamakan kode ke yang dipakai Undercover
    ('Mazda 2 Hatchback', 'MZD-MZ2', 'MZD-2H', 'kode Undercover (pasangan MZD-2S)'),
]

# --- C. kode yang belum seragam antar toko/channel ---------------------------
# kata kunci nama listing -> (kode yang menyimpang, kode tujuan, alasan)
SERAGAM_LISTING = [
    ('xenia',             'DHT-XNA', 'TYT-AVZ',
     'kembaran Avanza; Shopee & TikTok sudah TYT-AVZ, hanya Lazada berbeda'),
    ('agya',              'TYT-AGY', 'DHT-AYL',
     'kembaran Ayla; Shopee & TikTok sudah DHT-AYL, hanya Lazada berbeda'),
    # User memilih MZD-2H (dipakai Undercover) -- lebih rapi karena berpasangan
    # dengan MZD-2S untuk Mazda 2 Sedan. Jadi yang diubah justru master &
    # Otonation, bukan Undercover.
    ('mazda 2 hatchback', 'MZD-MZ2', 'MZD-2H',
     'user memilih kode Undercover; berpasangan dengan MZD-2S (Mazda 2 Sedan)'),
]


def ganti_prefix(sku, kode_baru):
    b = sku.split('-')
    return '-'.join([kode_baru.split('-')[0], kode_baru.split('-')[1]] + b[2:])


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


def sku_sah(master_path, listing_rows):
    """semua SKU yang benar-benar ada (master + listing) -- untuk validasi"""
    ada = set()
    wb = openpyxl.load_workbook(master_path, data_only=True, read_only=True)
    for sn in wb.sheetnames:
        ws = wb[sn]
        mulai = False
        for row in ws.iter_rows(values_only=True):
            if not mulai:
                if row and any(str(v).strip() == 'Nama Produk' for v in row if v):
                    mulai = True
                continue
            if row and len(row) > 8 and isinstance(row[8], str):
                ada.add(row[8].strip())
    wb.close()
    for sku in listing_rows:
        ada.add(sku)
    return ada


def perbaiki_master(master_path, out_path):
    wb = openpyxl.load_workbook(master_path)
    ubah = Counter()
    for sn in wb.sheetnames:
        ws = wb[sn]
        kol = None
        for r in range(1, ws.max_row + 1):
            if any(str(ws.cell(row=r, column=c).value).strip() == 'Nama Produk'
                   for c in range(1, min(ws.max_column, 12) + 1)):
                kol = r
                break
        if kol is None:
            continue
        for r in range(kol + 1, ws.max_row + 1):
            nama = ws.cell(row=r, column=2).value
            sku = ws.cell(row=r, column=9).value
            if not nama or not isinstance(sku, str):
                continue
            for m_nama, lama, baru, _ in KEMBAR_MASTER:
                # Dicocokkan lewat KODE, bukan nama persis: master bisa punya
                # lebih dari satu entri untuk model yang sama (terbukti
                # "Daihatsu Terios" DAN "Daihatsu Terios / New Terios", dua-duanya
                # DHT-TRS). Aman karena sudah diverifikasi tiap kode lama hanya
                # dipakai modelnya sendiri.
                if sku.startswith(lama + '-'):
                    sel = ws.cell(row=r, column=9)
                    sel.value = ganti_prefix(sku, baru)
                    sel.fill = ORANGE
                    ubah[m_nama] += 1
    wb.save(out_path)
    return ubah


def perbaiki_listing(out_dir, folders, sah, nama_toko='UA'):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = Counter()
    gagal = []

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

        ubah = []
        for r in range(start, wsv.max_row + 1):
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if not nm:
                continue
            s = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
            if not s:
                continue
            inti = s.split('_')[0]
            for kw, lama, baru, _ in SERAGAM_LISTING:
                if kw in nm.lower() and inti.startswith(lama + '-'):
                    sku_baru = ganti_prefix(inti, baru)
                    if sku_baru not in sah:
                        gagal.append((nm[:40], s, sku_baru))
                        break
                    # pertahankan akhiran pembeda Lazada kalau ada
                    if '_' in s:
                        sku_baru += '_' + s.split('_', 1)[1]
                    ubah.append((r, sku_baru))
                    laporan[(ch, kw)] += 1
                    break

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
        out = os.path.join(out_dir, f'FIX_KODE_SERAGAM_{nama_toko}_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan, gagal


if __name__ == '__main__':
    master_path, out_dir, nama_toko = sys.argv[1], sys.argv[2], sys.argv[3]
    folders = sys.argv[4:]
    os.makedirs(out_dir, exist_ok=True)

    # kumpulkan SKU listing utk validasi
    listing_sku = set()
    for f in folders:
        for p in sorted(glob.glob(os.path.join(f, '*.xlsx'))):
            wb = openpyxl.load_workbook(p, data_only=True)
            ch = UH.deteksi_channel(wb)
            if ch is None:
                continue
            ws = UH.cari_sheet(wb, ch)
            col = UH.resolve_cols(ws, ch)
            for r in range(UH.STARTROW[ch], ws.max_row + 1):
                s = str(ws.cell(row=r, column=col['sku']).value or '').strip()
                if s:
                    listing_sku.add(s.split('_')[0])
            wb.close()
    sah = sku_sah(master_path, listing_sku)

    out_master = os.path.join(out_dir, 'MASTER_kode_kembar_diseragamkan.xlsx')
    ubah = perbaiki_master(master_path, out_master)
    print('=== A. MASTER: kode kembar diarahkan ke kode induk ===')
    for m_nama, lama, baru, induk in KEMBAR_MASTER:
        print(f'  {m_nama:20s} {lama:9s} -> {baru:9s} ({induk}) : {ubah.get(m_nama,0):4d} baris')
    print(f'  TOTAL {sum(ubah.values()):,} baris  -> {os.path.basename(out_master)}')

    hasil, laporan, gagal = perbaiki_listing(out_dir, folders, sah, nama_toko)
    print('\n=== C. LISTING: kode diseragamkan ===')
    for (ch, kw), n in sorted(laporan.items()):
        print(f'  {ch:7s} {kw:20s} {n:4d} baris')
    print(f'  TOTAL {sum(laporan.values()):,} baris')
    if gagal:
        print(f'\n  DILEWATI (SKU tujuan tidak ada): {len(gagal)}')
        for x in gagal[:6]:
            print('   ', x)
    print()
    for ch, p in sorted(hasil.items()):
        print(f'[{ch}] -> {os.path.basename(p)}')
