# -*- coding: utf-8 -*-
"""
Tambahkan model-model baru (yang kode SKU-nya dibuat oleh `isi_sku_massal.py`)
ke file MASTER, mengikuti persis pola penulisan model yang sudah ada di sana.

Pola master (diverifikasi dari Audi A4, 408 baris):
  - per GENERASI per TOKO = 17 baris:
        Exclusive 1 warna (Abu-abu)
        Premium   2 warna (Abu-abu, Silver)
        Reguler   5 warna (Abu-abu, Hitam, Biru Benhur, Merah, Hijau Army)
        Strip     9 warna (Elite/Epic/Warrior x Abu/Biru/Merah)
  - 4 baris TOKO per kombinasi (aturan #7: master tidak dedupe baris toko)
  - segmen TOKO di SKU mengikuti aturan konsolidasi #1:
        Undercover Autocare & Otonation      -> UA
        Smartprotection    & Otoprotection   -> SP
  - kolom "Nama Produk Bigseller" = "{Model}-{Toko}-{Kategori}-{Warna}-{Generasi}"

Generasi & rentang tahun diambil dari TEKS VARIAN di listing e-commerce --
itu satu-satunya sumber yang ada untuk model yang memang belum pernah masuk
master. Artinya cakupan generasinya sebatas yang dijual di listing; kalau ada
generasi lain yang belum pernah dilisting, itu tetap harus ditambah manual.

File master ASLI tidak disentuh -- hasilnya ditulis sebagai file BARU
(aturan kerja: jangan pernah mengedit master/listing asli langsung).

Pemakaian:
  python3 tambah_model_baru_ke_master.py <master.xlsx> <kode_baru.xlsx> \
      <file_out.xlsx> <folder_listing...>
"""
import sys, os, re, glob, warnings
from collections import defaultdict, OrderedDict

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH

BIRU = PatternFill('solid', fgColor='9DC3E6')      # penanda baris baru

# urutan & isi persis seperti model yang sudah ada di master
MATRIKS = [
    ('Exclusive', [('Abu-abu', 'E', 'ABU')]),
    ('Premium',   [('Abu-abu', 'P', 'ABU'), ('Silver', 'P', 'SLV')]),
    ('Reguler',   [('Abu-abu', 'R', 'ABU'), ('Biru Benhur', 'R', 'BRU'),
                   ('Hijau Army', 'R', 'GRN'), ('Hitam', 'R', 'HTM'),
                   ('Merah', 'R', 'MRH')]),
    ('Strip',     [('Elite Abu', 'S', 'EAB'), ('Elite Biru', 'S', 'EBR'),
                   ('Elite Merah', 'S', 'EMR'), ('Epic Abu', 'S', 'PAB'),
                   ('Epic Biru', 'S', 'PBR'), ('Epic Merah', 'S', 'PMR'),
                   ('Warrior Abu', 'S', 'WAB'), ('Warrior Biru', 'S', 'WBR'),
                   ('Warrior Merah', 'S', 'WMR')]),
]
# aturan konsolidasi #1: stok fisik OT=UA, OP=SP
TOKO = [('Undercover Autocare', 'UA'), ('Otonation', 'UA'),
        ('Smartprotection', 'SP'), ('Otoprotection', 'SP')]

TIER_RE = re.compile(r'\b(reguler|regular|premium|exclusive|transparan)\b', re.I)
BOIL_RE = re.compile(r'(undercover\s+aut[o]?care|undercover|autocare|autcare|'
                     r'body cover|cover mobil|selimut mobil|\bmobil\b|\bbody\b|/|-)', re.I)


def model_key(nm):
    s = BOIL_RE.sub(' ', TIER_RE.sub(' ', str(nm)))
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', s.lower()).split())


def nama_rapi(nm):
    """nama produk untuk kolom master, dari nama listing"""
    s = BOIL_RE.sub(' ', TIER_RE.sub(' ', str(nm)))
    s = re.sub(r'\s+', ' ', s).strip(' -')
    return ' '.join(w if (w.isupper() and len(w) <= 4) else w.capitalize()
                    for w in s.split())


def generasi_dari_listing(folders, target_keys):
    """kumpulkan (kode generasi, label, rentang tahun) per model dari teks varian"""
    hasil = defaultdict(dict)      # model_key -> {kode: (label, tahun)}
    nama = {}
    for f in folders:
        for path in sorted(glob.glob(os.path.join(f, '*.xlsx'))):
            wb = openpyxl.load_workbook(path, data_only=True)
            ch = UH.deteksi_channel(wb)
            if ch is None:
                continue
            ws = UH.cari_sheet(wb, ch)
            col = UH.resolve_cols(ws, ch)
            for r in range(UH.STARTROW[ch], ws.max_row + 1):
                nm = ws.cell(row=r, column=col['nama']).value
                if not nm:
                    continue
                mk = model_key(nm)
                if mk not in target_keys:
                    continue
                nama.setdefault(mk, nama_rapi(nm))
                var = str(ws.cell(row=r, column=col['var']).value or '')
                mg = re.search(r'gen\s*([0-9]+)\s*(f|facelift)?', var, re.I)
                if mg:
                    kode = f'G{mg.group(1)}' + ('F' if mg.group(2) else '')
                    label = f'Gen {mg.group(1)}' + (' Facelift' if mg.group(2) else '')
                else:
                    ms = re.search(r'(?<![A-Za-z0-9])([A-Z]{1,2}\d{1,3})(?![A-Za-z0-9])', var)
                    if not ms:
                        continue
                    kode = label = ms.group(1).upper()
                th = re.findall(r'((?:19|20)\d{2})', var)
                tahun = f'{th[0]}-{th[-1]}' if len(th) >= 2 else (th[0] if th else '')
                lama = hasil[mk].get(kode)
                if not lama or (not lama[1] and tahun):
                    hasil[mk][kode] = (label, tahun)
            wb.close()
    return hasil, nama


def urut_gen(k):
    m = re.match(r'G(\d+)(F?)$', k)
    return (0, int(m.group(1)), m.group(2)) if m else (1, 0, k)


if __name__ == '__main__':
    master_path, kode_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    folders = sys.argv[4:]

    # 1) baca daftar kode baru
    wbk = openpyxl.load_workbook(kode_path, data_only=True)
    wsk = wbk.active
    kode = OrderedDict()
    for r in range(2, wsk.max_row + 1):
        k = wsk.cell(row=r, column=1).value
        m = wsk.cell(row=r, column=2).value
        if k and m:
            kode[model_key(m)] = str(k).strip()
    wbk.close()
    print(f'kode model baru dibaca: {len(kode)}')

    # 2) generasi tiap model dari listing
    gens, nama = generasi_dari_listing(folders, set(kode))
    tanpa_gen = [mk for mk in kode if not gens.get(mk)]
    print(f'model yang generasinya ketemu: {len(kode) - len(tanpa_gen)}/{len(kode)}')
    if tanpa_gen:
        print('  tanpa generasi (dilewati):', ', '.join(tanpa_gen[:6]))

    # 3) tulis ke salinan master
    wb = openpyxl.load_workbook(master_path)
    # peta kode merek -> nama sheet, dari SKU yang sudah ada
    sheet_merek = {}
    for sn in wb.sheetnames:
        ws = wb[sn]
        mulai = False
        for row in ws.iter_rows(values_only=True):
            if not mulai:
                if row and any(str(v).strip() == 'Nama Produk' for v in row if v):
                    mulai = True
                continue
            if row and len(row) > 8 and isinstance(row[8], str):
                b = row[8].split('-')
                if len(b) >= 6:
                    sheet_merek.setdefault(b[0], sn)
                    break
        # cukup ambil satu contoh per sheet

    ditambah = defaultdict(int)
    lewat = []
    for mk, pfx in kode.items():
        g = gens.get(mk)
        if not g:
            lewat.append((mk, 'tidak ada generasi di listing'))
            continue
        merek_kode = pfx.split('-')[0]
        sn = sheet_merek.get(merek_kode)
        if not sn:
            lewat.append((mk, f'sheet merek {merek_kode} tidak ketemu'))
            continue
        ws = wb[sn]
        r = ws.max_row + 1
        no = None
        # nomor urut: lanjutkan dari nomor terakhir di sheet itu
        for rr in range(ws.max_row, 1, -1):
            v = ws.cell(row=rr, column=1).value
            if v not in (None, ''):
                try:
                    no = int(float(v)) + 1
                except (TypeError, ValueError):
                    no = None
                break
        if no is None:
            no = 1
        for toko, kode_toko in TOKO:
            for kat, warna_list in MATRIKS:
                for warna, kat_kode, warna_kode in warna_list:
                    for gk in sorted(g, key=urut_gen):
                        label, tahun = g[gk]
                        sku = f'{pfx}-{kode_toko}-{kat_kode}-{gk}-{warna_kode}'
                        nilai = [no, nama[mk], toko, kat, warna, label, tahun,
                                 f'{nama[mk]}-{toko}-{kat}-{warna}-{label}', sku]
                        for c, v in enumerate(nilai, start=1):
                            sel = ws.cell(row=r, column=c, value=v)
                            sel.fill = BIRU
                        r += 1
                        ditambah[mk] += 1

    wb.save(out_path)
    print(f'\nmodel ditambahkan : {len(ditambah)}')
    print(f'baris ditambahkan : {sum(ditambah.values()):,}')
    if lewat:
        print(f'dilewati          : {len(lewat)}')
        for mk, alasan in lewat[:8]:
            print(f'   {mk[:40]:42s} {alasan}')
    print(f'\n-> {os.path.basename(out_path)}')
