# -*- coding: utf-8 -*-
"""
Tandai listing Undercover Autocare yang TIDAK termasuk "Daftar 100 Produk
Terlaris" (docx dari user, 2026-09-26) dengan akhiran " [Archived]" di nama
produk, supaya user bisa memilah & mengarsipkan listing itu di marketplace.

Keputusan user 2026-09-26:
  - yang diberi [Archived] HANYA cover mobil. Cover motor, cairan perawatan,
    karpet, tas, bahan kain, Logo Custom tidak disentuh.
  - model mirip tapi beda cover (Feroza Long, Vitara Brezza, Civic Type R,
    Yaris Cross, Corolla Cross, Avega Hatchback, MINI Hatch, Datsun GO Plus,
    dst.) ikut diarsip -- yang dipertahankan hanya model yang tertulis persis
    di daftar.
  - listing ganda untuk model yang ada di daftar ikut diarsip (sisa 1 listing
    per model per tipe). Duplikat TikTok: yang lebih BARU diarsip.
  - posisi kata: di belakang, "... [Archived]".
  - 3 produk "Custom Semua Merek" tetap aktif.

TikTok (template all_information): 1 produk harus dikirim lengkap semua baris
variannya, dan atribut wajib yang kosong ikut diisi: Tahun 2026, Bile 16:9,
Model Mercedes, Garansi "Tanpa Garansi". Kalau tidak, TikTok menolak SELURUH produk (pelajaran OP
2026-09-11, lihat perbaikan_otoprotection_final.py).

Pemakaian:
  python3 arsipkan_produk_undercover.py <folder_out> <shopee_basic.xlsx>
          <lazada_basic.xlsx> <tiktok_all_info.xlsx...>
File input harus sudah lewat repair_xlsx.py.
"""
import sys, os, re, copy, warnings
from collections import Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill, Font

from perbaikan_otoprotection_final import hitung_atribut

ORANGE = PatternFill('solid', fgColor='FFC000')
AKHIRAN = ' [Archived]'

# nomor di docx -> nama model seperti tertulis di judul listing UA
DAFTAR = {
    1: ['Toyota Avanza', 'Daihatsu Xenia', 'Toyota Veloz'], 2: ['Honda Brio'], 3: ['Toyota Innova'],
    4: ['Toyota Agya', 'Daihatsu Ayla'], 5: ['Honda Jazz'], 6: ['Honda HRV'],
    7: ['Toyota Rush', 'Daihatsu Terios'], 8: ['Suzuki Ertiga'], 9: ['Toyota Calya', 'Daihatsu Sigra'],
    10: ['Nissan Grand Livina'], 11: ['Toyota Vios'], 12: ['Honda BRV'], 13: ['Toyota Yaris'],
    14: ['Toyota Fortuner'], 15: ['Toyota Raize', 'Daihatsu Rocky'], 16: ['Suzuki APV Arena'],
    17: ['Honda CRV'], 18: ['Honda Civic Sedan'], 19: ['Toyota Alphard', 'Toyota Vellfire'],
    20: ['Toyota Camry'], 21: ['Mitsubishi Triton'], 22: ['Suzuki XL7'], 23: ['Toyota Kijang'],
    24: ['Honda Mobilio'], 25: ['Mitsubishi Pajero Sport'],
    26: ['Daihatsu Luxio', 'Daihatsu Gran Max Minibus'], 27: ['Mitsubishi Xpander'],
    28: ['Daihatsu Gran Max Pick Up'], 29: ['Honda Accord'], 30: ['Toyota Corolla'], 31: ['Honda Freed'],
    32: ['Suzuki Fronx'], 33: ['Daihatsu Feroza', 'Daihatsu Rocky', 'Daihatsu Taft GT'],
    34: ['Suzuki Baleno'], 35: ['Toyota Hilux'], 36: ['BMW Seri 3'], 37: ['Mazda 2 Hatchback'],
    38: ['Isuzu Panther'], 39: ['Suzuki Swift'], 40: ['Suzuki Jimny'], 41: ['Nissan March'],
    42: ['Suzuki Ignis'], 43: ['Daihatsu Sirion'], 44: ['Toyota Hardtop'], 45: ['Honda City Sedan'],
    46: ['Suzuki Karimun'], 47: ['Honda WRV'], 48: ['Kia Picanto'], 49: ['Nissan X-Trail'],
    50: ['Toyota HiAce'], 51: ['Toyota Land Cruiser'], 52: ['BYD Atto 1'], 53: ['Nissan Juke'],
    54: ['Suzuki Splash'], 55: ['Toyota Starlet'], 56: ['Toyota Etios Valco'], 57: ['Toyota Voxy'],
    58: ['Mitsubishi Destinator'], 59: ['Ford Fiesta'], 60: ['Hyundai Creta'],
    61: ['Suzuki Carry Pickup'], 62: ['Toyota Sienta'], 63: ['Honda Odyssey'], 64: ['Mazda CX-5'],
    65: ['Mini Cooper'], 66: ['Suzuki Carry'], 67: ['Honda City Hatchback'], 68: ['Suzuki APV Luxury'],
    69: ['Wuling Almaz'], 70: ['Suzuki S-Presso'], 71: ['Mitsubishi Xpander Cross'],
    72: ['Nissan Evalia'], 73: ['Suzuki SX4'], 74: ['Mercedes Benz E Class'], 75: ['Nissan Serena'],
    76: ['Wuling Air EV'], 77: ['Nissan Livina X-Gear'], 78: ['Nissan Terrano'],
    79: ['Chevrolet Captiva'], 80: ['Mitsubishi Kuda'], 81: ['Hyundai Stargazer'], 82: ['Datsun Go'],
    83: ['Toyota Harrier'], 84: ['Hyundai Santa Fe'], 85: ['Wuling Cortez'], 86: ['Wuling Confero'],
    87: ['Honda Stream'], 88: ['MG S5 EV'], 89: ['Mitsubishi Xforce'], 90: ['Honda Civic Hatchback'],
    91: ['Chevrolet Spin'], 92: ['Mercedes Benz C Class'], 93: ['Suzuki Aerio Hatchback'],
    94: ['Hyundai Palisade'], 95: ['Hyundai Avega'], 96: ['Kia Sonet'], 97: ['Daihatsu Taruna'],
    98: ['Suzuki Vitara'], 99: ['Ford Everest'], 100: ['BMW Seri 5'],
}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


KEEP = {norm(m): no for no, ms in DAFTAR.items() for m in ms}
ALIAS = {'wrv': 'hondawrv'}          # TikTok "Cover Mobil WRV Exclusive"

# listing ganda (model ADA di daftar) -- yang lebih baru diarsip, keputusan user
DUPLIKAT = {
    'tiktok': {
        '1731375818813637658',   # Datsun Go Reguler   (dipertahankan 1729574624459458586)
        '1731375828165821466',   # Datsun Go Exclusive (dipertahankan 1730173555151438874)
        '1731375828747322394',   # Suzuki Vitara Reguler (dipertahankan 1729572018172823578)
    },
}

RE_BUKAN_MOBIL = re.compile(r'cover motor|logo custom|bahan kain|karpet|pouch|\btas\b|shampoo|'
                            r'polish|restorer|black trim|glass care', re.I)
RE_MODEL = [
    re.compile(r'Cover (?:Mobil\s+)?(.+?)\s+(?:Reguler|Premium|Exclusive|Transparan|Outdoor)\b'),
    re.compile(r'Cover Mobil\s+(.+?)\s+-\s+Undercover'),
    re.compile(r'Selimut Mobil\s+(.+?)$'),
    re.compile(r'Cover Mobil\s+(.+?)$'),
]


def jenis(nama):
    """-> ('custom'|'nonmobil'|'mobil'|'lain', model)"""
    n = str(nama or '').strip()
    if 'Custom Semua Merek' in n:
        return 'custom', None
    if RE_BUKAN_MOBIL.search(n):
        return 'nonmobil', None
    for rx in RE_MODEL:
        m = rx.search(n)
        if m:
            return 'mobil', m.group(1).strip()
    return 'lain', None


def keputusan(ch, pid, nama):
    """-> (arsip?, alasan)"""
    j, model = jenis(nama)
    if str(nama or '').rstrip().endswith(AKHIRAN.strip()):
        return False, 'sudah [Archived]'
    if j != 'mobil':
        return False, {'custom': 'produk custom', 'nonmobil': 'bukan cover mobil',
                       'lain': 'bukan cover mobil'}[j]
    k = norm(model)
    k = ALIAS.get(k, k)
    if k not in KEEP:
        return True, f'model "{model}" tidak ada di daftar 100'
    if str(pid) in DUPLIKAT.get(ch, ()):
        return True, f'listing ganda No.{KEEP[k]} {model}'
    return False, f'No.{KEEP[k]}'


def model_mercedes(nama):
    """Atribut TikTok 'Model' (100177) wajib utk brand Mercedes-Benz. Regex
    versi OP (teks sesudah "Mercedes Benz" s/d akhir nama) salah utk judul UA
    yang masih diikuti tipe + nama toko -> ambil dari model hasil jenis():
    "Mercedes Benz A Class" / "Mercedes B Class" / "Mercedes Mercedes Benz
    GLC Class" -> "A Class" / "B Class" / "GLC Class"."""
    j, model = jenis(nama)
    if j != 'mobil' or not re.match(r'mercedes', model, re.I):
        return None
    return re.sub(r'^(mercedes\s+)+(benz\s+)?', '', model, flags=re.I).strip() or None


def pindah_baris(ws, simpan, start):
    """rapatkan baris `simpan` ke atas mulai `start`, buang sisanya"""
    n_kol = ws.max_column
    for i, r in enumerate(simpan):
        t = start + i
        if t != r:
            for c in range(1, n_kol + 1):
                s, d = ws.cell(row=r, column=c), ws.cell(row=t, column=c)
                d.value = s.value
                d.fill = copy.copy(s.fill)
                d.number_format = s.number_format
    sisa = start + len(simpan)
    if sisa <= ws.max_row:
        ws.delete_rows(sisa, ws.max_row - sisa + 1)


def kolom(ws, baris, nama):
    for c in range(1, ws.max_column + 1):
        if str(ws.cell(row=baris, column=c).value).strip() == nama:
            return c
    raise SystemExit(f'kolom "{nama}" tidak ketemu di {ws.title} -- template berubah?')


def proses_sederhana(ch, path, out, sheet, start, c_id, c_nama, laporan):
    """Shopee basic_info & Lazada basic: 1 baris = 1 produk"""
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    simpan = []
    for r in range(start, ws.max_row + 1):
        pid = ws.cell(row=r, column=c_id).value
        if not pid:
            continue
        nama = str(ws.cell(row=r, column=c_nama).value or '').strip()
        arsip, alasan = keputusan(ch, pid, nama)
        laporan.append((ch, str(pid), nama, nama + AKHIRAN if arsip else '', alasan))
        if arsip:
            sel = ws.cell(row=r, column=c_nama)
            sel.value = nama + AKHIRAN
            sel.fill = ORANGE
            simpan.append(r)
    pindah_baris(ws, simpan, start)
    wb.save(out)
    return len(simpan)


def proses_tiktok(paths, out, laporan):
    hasil = None
    n_prod = n_baris = n_atr = 0
    for path in paths:
        wb = openpyxl.load_workbook(path)
        ws = wb['Template']
        h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
        c_pid, c_nama = h['product_id'], h['product_name']
        i_atr = {k: v for k, v in h.items()
                 if k in ('product_property/100530', 'product_property/102755')}
        c_model = h.get('product_property/100177')
        c_garansi = h.get('product_property/100107')
        per_produk = {}
        for r in range(6, ws.max_row + 1):
            pid = ws.cell(row=r, column=c_pid).value
            if pid:
                per_produk.setdefault(str(pid), []).append(r)
        simpan = []
        for pid, rows in per_produk.items():
            nama = str(ws.cell(row=rows[0], column=c_nama).value or '').strip()
            arsip, alasan = keputusan('tiktok', pid, nama)
            laporan.append(('tiktok', pid, nama, nama + AKHIRAN if arsip else '', alasan))
            if not arsip:
                continue
            n_prod += 1
            for r in rows:
                sel = ws.cell(row=r, column=c_nama)
                sel.value = nama + AKHIRAN
                sel.fill = ORANGE
                atr = hitung_atribut(nama, ws, r, i_atr)
                m_mb = model_mercedes(nama)
                if c_model and m_mb and ws.cell(row=r, column=c_model).value in (None, ''):
                    atr[c_model] = m_mb
                # Garansi: preventif, pelajaran SP 2026-09-14 (TikTok lapor
                # atribut wajib satu per satu; "Tanpa Garansi" terbukti lolos)
                if c_garansi and ws.cell(row=r, column=c_garansi).value in (None, ''):
                    atr[c_garansi] = 'Tanpa Garansi'
                for idx, val in atr.items():
                    s2 = ws.cell(row=r, column=idx)
                    s2.value = val
                    s2.fill = ORANGE
                    n_atr += 1
            simpan.extend(rows)
        if not simpan:
            continue
        pindah_baris(ws, sorted(simpan), 6)
        n_baris += len(simpan)
        if hasil is None:
            hasil = (wb, ws)
        else:                                   # gabung ke file pertama
            wo, wso = hasil
            r_out = wso.max_row + 1
            for i in range(len(simpan)):
                for c in range(1, ws.max_column + 1):
                    s, d = ws.cell(row=6 + i, column=c), wso.cell(row=r_out + i, column=c)
                    d.value = s.value
                    d.fill = copy.copy(s.fill)
    if hasil:
        hasil[0].save(out)
    return n_prod, n_baris, n_atr


def tulis_laporan(laporan, out):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Archived'
    hdr = ['Channel', 'ID Produk', 'Nama Lama', 'Nama Baru', 'Alasan']
    for tab, isi in (('Archived', [x for x in laporan if x[3]]),
                     ('Dipertahankan', [x for x in laporan if not x[3]])):
        w = ws if tab == 'Archived' else wb.create_sheet(tab)
        for c, v in enumerate(hdr, 1):
            w.cell(row=1, column=c, value=v).font = Font(bold=True)
        for r, x in enumerate(sorted(isi), 2):
            for c, v in enumerate(x, 1):
                w.cell(row=r, column=c, value=v)
        for col, wd in zip('ABCDE', (9, 22, 70, 80, 45)):
            w.column_dimensions[col].width = wd
        w.freeze_panes = 'A2'
    wb.save(out)


if __name__ == '__main__':
    out_dir, shopee, lazada, *tiktok = sys.argv[1:]
    os.makedirs(out_dir, exist_ok=True)
    lap = []
    wb = openpyxl.load_workbook(shopee)
    n_s = proses_sederhana('shopee', shopee, os.path.join(out_dir, 'ARCHIVED_UA_SHOPEE.xlsx'),
                           None, 7, 1, kolom(wb.worksheets[0], 1, 'et_title_product_name'), lap)
    wb = openpyxl.load_workbook(lazada)
    n_l = proses_sederhana('lazada', lazada, os.path.join(out_dir, 'ARCHIVED_UA_LAZADA.xlsx'),
                           'template', 5, 1, kolom(wb['template'], 1, 'Nama Produk'), lap)
    n_t = proses_tiktok(tiktok, os.path.join(out_dir, 'ARCHIVED_UA_TIKTOK.xlsx'), lap)
    tulis_laporan(lap, os.path.join(out_dir, 'LAPORAN_ARCHIVED_UA.xlsx'))
    print(f'shopee : {n_s} produk diberi [Archived]')
    print(f'lazada : {n_l} produk diberi [Archived]')
    print(f'tiktok : {n_t[0]} produk / {n_t[1]} baris varian, {n_t[2]} sel atribut wajib diisi')
    print('ringkasan alasan:')
    for (ch, a), n in sorted(Counter((x[0], x[4].split(' "')[0].split(' No.')[0]
                                      if x[3] else x[4].split('.')[0]) for x in lap).items()):
        print(f'  {ch:7s} {a:40s} {n:5d}')
