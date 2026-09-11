# -*- coding: utf-8 -*-
"""
Samakan kode SKU Smartprotection ke konvensi yang dipakai Undercover.

Dua jenis pekerjaan, dari hasil perbandingan katalog UA vs SP (2026-09-09):

A. GANTI PREFIX -- model yang SKU-nya sudah ada tapi kodenya beda dari UA.
   Segmen lain (toko/kategori/generasi/warna) TIDAK disentuh, cuma MEREK-MODEL.

B. ISI SKU -- model yang di SP listingnya ada tapi SKU-nya kosong (di Lazada
   terlihat "terisi" karena Lazada mengarang ID sendiri bergaya
   8890956509-1788758253245-10; itu setara kosong).

Kosakata SP BEDA dari UA dan diambil dari data SP sendiri, bukan disalin dari
UA (dicek 2026-09-09 di ekspor SP):
  - warna dasar : ABU HTM BRU MRH GRN + ORG (Orange, tidak ada di UA)
  - strip       : Epic=S1, Elite=S2, Warrior=S3, lalu A/B/M utk Abu/Biru/Merah
                  (UA memakai PAB/EAB/WAB - JANGAN dipakai di sini)
  - transparan  : TRP
  - tier Premium/Exclusive TIDAK ADA di SP (cuma R, S, T)

Semua model di grup B ber-Total-Formula 1 (diverifikasi lewat file formula),
jadi seluruh generasi memakai satu kode: G1 -- kecuali Jeep yang memang
bergenerasi-nama dan di SP sudah konsisten memakai YJ.

Khusus LAZADA: SKU wajib unik per listing, sedangkan skema di atas sengaja
membuat beberapa varian berbagi kode. Dipakai akhiran pembeda `_G2`, `_G3`, ...
mengikuti konvensi yang SUDAH ada di data SP.

Pemakaian:
  python3 samakan_sku_smartprotection.py <folder_out> <folder_listing...>
"""
import sys, os, re, glob, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH

ORANGE = PatternFill('solid', fgColor='FFC000')
AUTO_LAZADA = re.compile(r'^\d{6,}-\d{6,}-\d+$')
MASTERFMT = re.compile(r'^[A-Z0-9]+-[A-Z0-9]+-(UA|SP)-[RSPET]-[A-Z0-9]+-[A-Z0-9]+$')

# --- A. ganti prefix saja -------------------------------------------------
GANTI = {
    'MZD-MZ2': 'MZD-2H',    # Mazda 2 Hatchback, kode UA sudah jadi standar
    'WLG-DAR': 'WLG-DRN',   # Wuling Darion
    'JEP-WR':  'JEP-WRA',   # Wrangler Rubicon: di SP sendiri sudah campur WR & WRA
}

# --- B. isi SKU: kata kunci nama listing -> kode MEREK-MODEL ---------------
# urutan penting: yang lebih spesifik didahulukan
ISI = [
    ('mazda 2 hatchback',      'MZD-2H'),
    ('avega hatchback',        'HYN-AVH'),   # di SP masih memakai HYN-AVG,
                                             # bentrok dgn "Avega Sedan"
    ('feroza long',            'DHT-FRL'),
    ('apv luxury',             'SZK-AL'),
    ('cx-7',                   'MZD-CX7'),
    ('byd seal',               'BYD-SEA'),
    ('chery omoda 5',          'CHR-O5'),
    ('hyundai getz',           'HYN-GET'),
    ('ford ranger',            'FRD-RAN'),
    ('wuling darion',          'WLG-DRN'),
]
GEN_KHUSUS = {'JEP-WRA': 'YJ'}      # sisanya TF=1 -> G1

# Ejaan di listing SP tidak konsisten -- dipindai dari data (2026-09-09):
# "Warior" (tanpa satu R) dipakai 1.367 baris, "Elita"/"Elite  Merah"/huruf
# besar-kecil campur juga ada. Semua varian ejaan harus ikut, kalau tidak
# barisnya diam-diam dilewati sebagai "warna tak terbaca".
# Daftar ini HARUS dipindai ulang dari data tiap kali dipakai di toko lain.
# Ejaan yang sudah terbukti ada di SP: Warior, Wrior, Elita, Eltie, Eite,
# "Elite  Merah" (spasi ganda), huruf besar-kecil campur. Kalau ada ejaan yang
# tidak masuk daftar, barisnya TIDAK error -- dia jatuh ke pencocokan warna
# dasar ("Eltie Biru" -> "biru") dan menghasilkan SKU kategori R padahal
# seharusnya Strip. Bug diam-diam, ketahuan 2026-09-11 lewat 2 baris di
# BYD Seal & Suzuki Ciaz.
WARNA_STRIP = [
    (('epic', 'epik', 'strip 1'),                        'S1'),
    (('elite', 'elita', 'eltie', 'eite', 'elit', 'strip 2'), 'S2'),
    (('warrior', 'warior', 'wrior', 'strip 3'),          'S3'),
]
NUANSA = [(('abu',), 'A'), (('biru',), 'B'), (('merah',), 'M')]
WARNA_DASAR = [(('abu-abu', 'abu abu'), 'ABU'), (('hitam',), 'HTM'),
               (('biru benhur', 'biru'), 'BRU'), (('merah',), 'MRH'),
               (('hijau army', 'hijau'), 'GRN'), (('orange', 'oranye'), 'ORG')]


def segmen_warna(var, transparan):
    """-> (kode warna, kategori R/S/T) atau (None, None) kalau tak terbaca.

    Strip diputuskan lewat BUKTI POSITIF -- angka 1/2/3 di segmen pertama
    (penanda paling stabil, independen dari ejaan kata "Strip"-nya sendiri:
    Warior/Wrior/Eltie/Eite/Elita/Srip/Srtip/Stirp semua terbukti dipakai di
    SP & OP) ATAU kata Epic/Elite/Warrior (+ typo-nya). Kalau tak ada bukti
    strip sama sekali, DEFAULT ke pencocokan warna polos (perilaku asli,
    lenient thd typo warna spt "Biru Binhur"/"Biru Bnehur") -- supaya baris
    yg sudah lama valid tidak ikut kesenggol regresi.
    """
    v = ' '.join(str(var).lower().replace(',', ' , ').split())
    if transparan:
        return 'TRP', 'T'
    segmen = v.split(',')[0].strip()
    n = None
    m = re.search(r'[123]', segmen)                     # cakup jg "Strip1" tanpa spasi
    if m:
        n = {'1': 'S1', '2': 'S2', '3': 'S3'}[m.group(0)]
    else:
        for kata, kode in WARNA_STRIP:
            if any(k in segmen for k in kata):
                n = kode
                break
    if n:
        for kata2, nu in NUANSA:
            if any(k in v for k in kata2):
                return n + nu, 'S'
        return None, None
    for kata, kode in WARNA_DASAR:
        if any(k in v for k in kata):
            return kode, 'R'
    return None, None


def kode_untuk(nama):
    n = str(nama).lower()
    for kw, kode in ISI:
        if kw in n:
            return kode
    return None


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        d = ws_d.cell(row=r_d, column=c)
        d.value = s.value
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def proses(out_dir, folders):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = Counter()
    contoh = []

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

        terpakai = defaultdict(set)          # utk keunikan Lazada per listing
        if ch == 'lazada':
            for r in range(start, wsv.max_row + 1):
                s = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
                nm = str(wsv.cell(row=r, column=col['nama']).value or '')
                if s and not AUTO_LAZADA.match(s):
                    terpakai[nm].add(s)

        ubah = []
        for r in range(start, wsv.max_row + 1):
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if not nm:
                continue
            lama = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
            b = lama.split('-')
            baru = None

            if len(b) >= 6 and b[0] + '-' + b[1] in GANTI:      # A. ganti prefix
                baru = '-'.join([GANTI[b[0] + '-' + b[1]].split('-')[0],
                                 GANTI[b[0] + '-' + b[1]].split('-')[1]] + b[2:])
                jenis = 'ganti prefix'
            else:                                               # B. isi SKU
                kode = kode_untuk(nm)
                if not kode:
                    continue
                if lama and not AUTO_LAZADA.match(lama) and MASTERFMT.match(lama):
                    inti = lama.split('_')[0]
                    if inti.startswith(kode + '-'):
                        continue                                # sudah benar
                    baru = '-'.join([kode.split('-')[0], kode.split('-')[1]]
                                    + inti.split('-')[2:])
                    jenis = 'ganti prefix'
                else:
                    var = str(wsv.cell(row=r, column=col['var']).value or '')
                    warna, kat = segmen_warna(var, 'transparan' in nm.lower())
                    if not warna:
                        laporan[(ch, 'warna tak terbaca')] += 1
                        continue
                    gen = GEN_KHUSUS.get(kode, 'G1')
                    baru = f'{kode}-SP-{kat}-{gen}-{warna}'
                    jenis = 'isi kosong'

            if baru == lama:
                continue
            if ch == 'lazada':
                dasar = baru
                i = 2
                while baru in terpakai[nm]:
                    baru = f'{dasar}_G{i}'
                    i += 1
                terpakai[nm].add(baru)
            ubah.append((r, baru))
            laporan[(ch, jenis)] += 1
            if len(contoh) < 12:
                contoh.append((ch, nm[:38], str(wsv.cell(row=r, column=col['var']).value)[:24],
                               lama[:28], baru))

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
        out = os.path.join(out_dir, f'SAMAKAN_SKU_SMARTPROTECTION_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan, contoh


if __name__ == '__main__':
    hasil, laporan, contoh = proses(sys.argv[1], sys.argv[2:])
    print('=== ringkasan ===')
    for (ch, jenis), n in sorted(laporan.items()):
        print(f'  {ch:8s} {jenis:22s} {n:5d}')
    print(f'  TOTAL {sum(laporan.values()):,}')
    print('\ncontoh:')
    for c in contoh:
        print(f'  [{c[0]:6s}] {c[1]:40s} {c[2]:26s} {c[3]!r:30} -> {c[4]}')
    print()
    for ch, p in sorted(hasil.items()):
        print(f'[{ch}] -> {os.path.basename(p)}')
