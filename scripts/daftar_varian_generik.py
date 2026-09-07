# -*- coding: utf-8 -*-
"""
Daftar produk yang masih punya varian generik ("Model/Tahun Lain", "Model
Lain/Custom", dst) di listing e-commerce.

Varian generik itu bukan generasi mobil sungguhan -- pembeli memilihnya kalau
tahun/tipe mobilnya tidak ada di daftar. Aturan bisnis #4: SKU-nya dibiarkan
KOSONG kalau modelnya punya lebih dari satu formula (tidak mungkin tahu cover
mana yang dimaksud), tapi BOLEH diisi kalau modelnya cuma punya satu formula
(semua generasi memakai cover yang sama, jadi tidak ada ambiguitas).

Script ini cuma MELAPORKAN, tidak mengubah apa pun. Keluarannya satu file Excel
dua sheet: ringkasan per model + detail per baris.

Pemakaian:
  python3 daftar_varian_generik.py <file_out.xlsx> <folder_listing...>
  (opsional: <file_formula.xlsx> di antara argumen, utk kolom Total Formula)
"""
import sys, os, re, glob, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

import update_harga_per_sku as UH

# Delapan ejaan yang benar-benar ada di listing (dipindai 2026-09-07), bukan
# tebakan: 'Model/Tahun Lain', 'Model Lain/Custom', 'Model Lain / Custom',
# 'Model Lain', 'Model Lainnya', 'Custom', 'Model lain/Custom',
# 'Model Lain / Custome'. Polanya sengaja longgar supaya ejaan baru ikut kena.
POLA = re.compile(r'\b(model|tahun|type|tipe|varian)\b[^,]*\blain|'
                  r'\blain(nya)?\b|\bcustom(e)?\b', re.I)

# Lazada membuat sendiri "Seller SKU" bergaya 8663336150-1752049417990-1 kalau
# kolomnya dikosongkan. Isinya bukan SKU kita -- setara KOSONG, jangan dihitung
# sebagai sudah terisi (kalau tidak, Lazada selalu terlihat 100% beres).
AUTO_LAZADA = re.compile(r'^\d{6,}-\d{6,}-\d+$')

JUDUL = Font(bold=True, color='FFFFFF')
BIRU = PatternFill('solid', fgColor='4472C4')
KUNING = PatternFill('solid', fgColor='FFF2CC')


def prefix_sku(s):
    b = str(s or '').split('-')
    return '-'.join(b[:2]) if len(b) >= 6 else None


def nama_model(nm):
    """buang boilerplate toko & kata tier dari nama listing"""
    s = re.sub(r'undercover\s*autocare|undercover|cover\s*mobil|selimut\s*mobil|'
               r'sarung\s*mobil', ' ', str(nm), flags=re.I)
    s = re.sub(r'\b(reguler|regular|premium|exclusive|transparan|semi\s*outdoor|'
               r'extreme\s*outdoor|indoor\s*dan\s*outdoor|outdoor|indoor)\b', ' ',
               s, flags=re.I)
    return ' '.join(re.sub(r'[-/]+', ' ', s).split())


def kumpulkan(folders):
    baris = []                       # detail (baris generik saja)
    lain = defaultdict(int)          # kunci model -> jumlah baris NON-generik
    gen = defaultdict(Counter)       # kunci model -> kode generasi yg dipakai
    pfx_listing = defaultdict(Counter)   # (ch, nama listing) -> Counter(prefix)
    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=True)
        ch = UH.deteksi_channel(wb)
        if ch is None:
            wb.close()
            continue
        ws = UH.cari_sheet(wb, ch)
        col = UH.resolve_cols(ws, ch)
        mentah = []
        for r in range(UH.STARTROW[ch], ws.max_row + 1):
            nm = ws.cell(row=r, column=col['nama']).value
            if not nm:
                continue
            nm = str(nm)
            var = str(ws.cell(row=r, column=col['var']).value or '')
            sku = str(ws.cell(row=r, column=col['sku']).value or '').strip()
            p = prefix_sku(sku)
            if p:
                pfx_listing[(ch, nm)][p] += 1
            mentah.append((ch, os.path.basename(path), nm, var, sku,
                           ws.cell(row=r, column=col['harga']).value))
        wb.close()

        for ch_, fn, nm, var, sku, harga in mentah:
            label = next((b.strip() for b in var.split(',') if POLA.search(b)), None)
            if label:
                baris.append([ch_, fn, nm, var, label, sku, harga])
            else:
                p = prefix_sku(sku) or (pfx_listing[(ch_, nm)].most_common(1)[0][0]
                                        if pfx_listing[(ch_, nm)] else None)
                lain[p or nama_model(nm).lower()] += 1
            b = str(sku).split('-')
            if len(b) >= 6:
                p2 = prefix_sku(sku) or nama_model(nm).lower()
                gen[p2][b[4]] += 1
    return baris, pfx_listing, lain, gen


def total_formula(path):
    """{nama model (lowercase): Total Formula} dari file 'Lebih dari 1 Formula'"""
    if not path:
        return {}
    import formula_config as FC
    cfg, blocked = FC.load(path)
    hasil = {}
    for nm, c in cfg.items():
        hasil[nm.lower()] = len(c['groups']) if c.get('groups') else c.get('tf')
    for nm in blocked:
        hasil[nm.lower()] = '?'
    return hasil


if __name__ == '__main__':
    out_path = sys.argv[1]
    args = sys.argv[2:]
    formula = next((a for a in args if os.path.isfile(a)), None)
    folders = [a for a in args if os.path.isdir(a)]

    baris, pfx_listing, lain, gen = kumpulkan(folders)
    tf = total_formula(formula)

    # model = prefix SKU listing-nya (kalau ada), jatuh ke nama bersih kalau tidak
    per_model = defaultdict(lambda: {'baris': 0, 'ch': Counter(), 'label': Counter(),
                                     'isi': 0, 'kosong': 0, 'auto': 0, 'nama': Counter()})
    for ch, fn, nm, var, label, sku, harga in baris:
        p = prefix_sku(sku) or (pfx_listing[(ch, nm)].most_common(1)[0][0]
                                if pfx_listing[(ch, nm)] else None)
        kunci = p or nama_model(nm).lower()
        d = per_model[kunci]
        d['baris'] += 1
        d['ch'][ch] += 1
        d['label'][label] += 1
        d['nama'][nama_model(nm)] += 1
        if not sku:
            d['kosong'] += 1
        elif AUTO_LAZADA.match(sku):
            d['auto'] += 1
        else:
            d['isi'] += 1

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Ringkasan'
    hdr = ['Kode SKU', 'Model', 'Baris generik', 'Shopee', 'TikTok', 'Lazada',
           'SKU terisi', 'SKU kosong', 'SKU auto-Lazada', 'Baris varian asli',
           'Bentuk listing',
           'Kode generasi dipakai', 'Label varian', 'Total Formula',
           'Perlu ditinjau', 'Catatan']
    ws.append(hdr)
    for c in range(1, len(hdr) + 1):
        ws.cell(row=1, column=c).font = JUDUL
        ws.cell(row=1, column=c).fill = BIRU
    urut = sorted(per_model.items(), key=lambda x: -x[1]['baris'])
    for kunci, d in urut:
        nama = d['nama'].most_common(1)[0][0]
        n_tf = tf.get(nama.lower())
        if n_tf is None:
            cat = ('belum terdaftar di file formula -- kemungkinan 1 formula, '
                   'tapi harus dipastikan dulu sebelum SKU diisi')
        elif n_tf == '?':
            cat = 'Total Formula belum jelas -> tunggu keputusan'
        elif isinstance(n_tf, int) and n_tf <= 1:
            cat = '1 formula -> SKU boleh diisi'
        else:
            cat = f'{n_tf} formula -> SKU dibiarkan kosong (aturan #4)'
        n_lain = lain.get(kunci, 0)
        bentuk = ('HANYA varian generik' if n_lain == 0
                  else 'ada generasi asli + catch-all')
        kode_gen = sorted(gen.get(kunci, {}))
        # Catch-all ber-SKU cuma jadi masalah kalau modelnya benar-benar memakai
        # LEBIH DARI SATU kode generasi -- di situ kode yang dipilih pasti
        # sembarang. Kalau semua generasi toh memakai satu kode, isinya tidak
        # ambigu walaupun Total Formula > 1.
        tinjau = ('YA' if (isinstance(n_tf, int) and n_tf > 1
                           and len(kode_gen) > 1 and d['isi'] > 0) else '')
        belum = d['kosong'] + d['auto']
        r = [kunci if '-' in kunci else '', nama, d['baris'],
             d['ch'].get('shopee', 0), d['ch'].get('tiktok', 0), d['ch'].get('lazada', 0),
             d['isi'], d['kosong'], d['auto'], n_lain, bentuk,
             f"{len(kode_gen)}: {', '.join(kode_gen[:6])}",
             ' | '.join(sorted(d['label'])), str(n_tf) if n_tf is not None else '-',
             tinjau, cat]
        ws.append(r)
    for c, w in zip('ABCDEFGHIJKLMNOP', (11, 34, 13, 8, 8, 8, 10, 11, 15, 17, 26, 24, 30, 13, 13, 62)):
        ws.column_dimensions[c].width = w
    ws.freeze_panes = 'A2'

    ws2 = wb.create_sheet('Detail')
    hdr2 = ['Channel', 'File', 'Nama Listing', 'Varian', 'Label generik', 'SKU', 'Harga']
    ws2.append(hdr2)
    for c in range(1, len(hdr2) + 1):
        ws2.cell(row=1, column=c).font = JUDUL
        ws2.cell(row=1, column=c).fill = BIRU
    for b in sorted(baris, key=lambda x: (x[2], x[0], x[3])):
        ws2.append(b)
        if not b[5] or AUTO_LAZADA.match(str(b[5])):
            ws2.cell(row=ws2.max_row, column=6).fill = KUNING
    for c, w in zip('ABCDEFG', (9, 16, 58, 34, 20, 24, 10)):
        ws2.column_dimensions[c].width = w
    ws2.freeze_panes = 'A2'

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wb.save(out_path)
    print(f'model dgn varian generik : {len(per_model)}')
    print(f'total baris              : {len(baris):,}')
    print(f'  SKU terisi             : {sum(d["isi"] for d in per_model.values()):,}')
    print(f'  SKU kosong             : {sum(d["kosong"] for d in per_model.values()):,}')
    print(f'  SKU auto-Lazada (=kosong): {sum(d["auto"] for d in per_model.values()):,}')
    print(f'-> {os.path.basename(out_path)}')
