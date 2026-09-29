# -*- coding: utf-8 -*-
"""
Optimasi judul listing Smartprotection / Otoprotection (hasil diskusi SEO
2026-09, lihat claude-memory/project-undercover-judul-seo-sp-op.md).

Formula (satu judul dipakai SAMA di Shopee & TikTok), pola "cover" (default,
revisi 2026-09-29):
    Cover Mobil {Model} Signature Waterproof - {Toko} - Body Cover Selimut Sarung Mobil
    Cover Mobil {Model} Transparan Anti Air - {Toko} - Body Cover Selimut Sarung Mobil
Pola "body" (versi pertama): "Body Cover Mobil {Model} ... - {Toko} - Selimut Sarung Mobil".

Kenapa pola "cover": simulasi render kartu hasil pencarian (2 baris) cuma
menampilkan ±40-55 karakter (HP 360dp ±48, TikTok ±44). "Body " di depan
memakan 5 karakter di zona itu -> di HP 360dp nama model terpotong di 18-28
judul dan kata Signature/Transparan hilang di 101 (Shopee) / 179 (TikTok)
judul. Kata "Body Cover" tetap ada di ekor, jadi pencarian "body cover mobil
{model}" tetap cocok. Nama toko TIDAK pernah terlihat di kartu pencarian
(pola mana pun) -- hanya di halaman detail produk.

- "Signature" = nama lini non-Transparan (pengganti "Reguler"; Classic/Prime/
  Deluxe/Premium/Elite gugur -- lihat memory).
- Yang terlihat di kartu pencarian = model + tipe; ekor setelah nama toko =
  ruang kata kunci. Shopee maks 120 karakter.
- Klaim sesuai deskripsi toko: kain "waterproof Taffeta" (non-Transparan),
  "PE tebal, full waterproof" (Transparan).

Nama model diambil dari judul lama lalu dibetulkan lewat KOREKSI_MODEL
(ejaan/merek salah -- diverifikasi lewat SKU di export SP 2026-09-12).

Pemakaian:
  python3 optimasi_judul_sp_op.py <Toko> <folder_out> <shopee_basic.xlsx> <tiktok_basic.xlsx> [cover|body]
File input harus sudah lewat repair_xlsx.py.
"""
import sys, os, re, warnings

warnings.filterwarnings('ignore')

import openpyxl
from openpyxl.styles import PatternFill, Font

ORANGE = PatternFill('solid', fgColor='FFC000')
MERAH = PatternFill('solid', fgColor='FF9999')
BATAS_SHOPEE = 120

RE_JUDUL_LAMA = re.compile(
    r'^(?:Body\s+)?Cover Mobil\s*/\s*(?:Sarung\s*/\s*)?Selimut Mobil\s+(.+?)(?:\s+(Transparan))?\s*$', re.I)

KOREKSI_MODEL = {
    # salah merek (dicek lewat kode SKU / tahun varian)
    'Honda Fortuner': 'Toyota Fortuner',            # SKU TYT-FTN
    'Mitsubishi Lantis': 'Mazda Lantis',            # tahun 1993-1998 = Mazda Lantis
    'Mitsubishi Pajero': 'Mitsubishi Pajero Sport', # SKU MTB-PJS, Gen 1-3 1996-2026
    'Kia Sedona / Carnival': 'Kia Sedona',          # SKU KIA-SED
    # merek hilang
    'Feroza': 'Daihatsu Feroza',
    'Feroza Long': 'Daihatsu Feroza Long',
    'Taft GT': 'Daihatsu Taft GT',
    # salah ketik
    'Honda Civic Hatcback': 'Honda Civic Hatchback',
    'Kia Grand Carnaval': 'Kia Grand Carnival',
    'Mistubishi Grandis': 'Mitsubishi Grandis',
    'Volswagen Polo': 'Volkswagen Polo',
    # ejaan resmi / huruf besar (disamakan dgn katalog UA)
    'Datsun Go': 'Datsun GO',
    'Datsun Go Plus': 'Datsun GO Plus',
    'Hyundai Santa FE': 'Hyundai Santa Fe',
    'Isuzu Mux': 'Isuzu MU-X',
    'isuzu Panther': 'Isuzu Panther',
    'Mazda CX3': 'Mazda CX-3',
    'Mazda CX9': 'Mazda CX-9',
    'Mercedes Benz Glc Class': 'Mercedes Benz GLC Class',
    'Mercedes Benz Gls Class': 'Mercedes Benz GLS Class',
    'Nissan XTrail': 'Nissan X-Trail',
    'Nissan Xtrail': 'Nissan X-Trail',
}


def urai(nama):
    """judul lama -> (model, transparan?) atau (None, None)"""
    n = re.sub(r'\s+', ' ', str(nama or '')).strip()
    m = RE_JUDUL_LAMA.match(n)
    if not m:
        return None, None
    return m.group(1), bool(m.group(2))


POLA = {
    'cover': ('Cover Mobil', 'Body Cover Selimut Sarung Mobil'),
    'body': ('Body Cover Mobil', 'Selimut Sarung Mobil'),
}
POLA_AKTIF = 'cover'


def judul_baru(model, transparan, toko):
    model = KOREKSI_MODEL.get(model, model)
    tipe = 'Transparan Anti Air' if transparan else 'Signature Waterproof'
    depan, ekor = POLA[POLA_AKTIF]
    etalase = f'{depan} {model} {tipe} - {toko}'
    return f'{etalase} - {ekor}', len(etalase), model


def proses(ch, path, out, sheet, start, c_id, c_nama, toko, laporan):
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    n = 0
    for r in range(start, ws.max_row + 1):
        pid = ws.cell(row=r, column=c_id).value
        if not pid:
            continue
        lama = str(ws.cell(row=r, column=c_nama).value or '').strip()
        model, trn = urai(lama)
        sel = ws.cell(row=r, column=c_nama)
        if model is None:
            sel.fill = MERAH
            laporan.append((ch, str(pid), lama, '', None, None, '', 'POLA JUDUL TIDAK DIKENAL - tidak diubah'))
            continue
        baru, p_etalase, model_fix = judul_baru(model, trn, toko)
        cat = []
        if model_fix != model:
            cat.append(f'model dibetulkan: "{model}" -> "{model_fix}"')
        if len(baru) > BATAS_SHOPEE:
            cat.append(f'LEWAT {BATAS_SHOPEE} KARAKTER')
        sel.value = baru
        sel.fill = ORANGE
        n += 1
        laporan.append((ch, str(pid), lama, baru, len(baru), p_etalase,
                        'Transparan' if trn else 'Signature', '; '.join(cat)))
    wb.save(out)
    return n


def kolom(ws, baris, nama):
    for c in range(1, ws.max_column + 1):
        if str(ws.cell(row=baris, column=c).value).strip() == nama:
            return c
    raise SystemExit(f'kolom "{nama}" tidak ketemu -- template berubah?')


def tulis_laporan(laporan, out):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Judul Baru'
    hdr = ['Channel', 'ID Produk', 'Judul Lama', 'Judul Baru', 'Panjang',
           'Toko selesai di karakter', 'Tipe', 'Catatan']
    for c, v in enumerate(hdr, 1):
        ws.cell(row=1, column=c, value=v).font = Font(bold=True)
    for r, x in enumerate(sorted(laporan, key=lambda x: (x[0], x[3])), 2):
        for c, v in enumerate(x, 1):
            ws.cell(row=r, column=c, value=v)
        if x[7]:
            ws.cell(row=r, column=8).fill = ORANGE
    for col, wd in zip('ABCDEFGH', (8, 21, 60, 95, 9, 12, 11, 60)):
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = 'A2'
    wb.save(out)


if __name__ == '__main__':
    toko, out_dir, shopee, tiktok = sys.argv[1:5]
    if len(sys.argv) > 5:
        POLA_AKTIF = sys.argv[5]
    os.makedirs(out_dir, exist_ok=True)
    lap = []
    kode = toko.upper()
    wb = openpyxl.load_workbook(shopee)
    n_s = proses('shopee', shopee, os.path.join(out_dir, f'JUDUL_{kode}_SHOPEE.xlsx'), None, 7, 1,
                 kolom(wb.worksheets[0], 1, 'et_title_product_name'), toko, lap)
    wb = openpyxl.load_workbook(tiktok)
    n_t = proses('tiktok', tiktok, os.path.join(out_dir, f'JUDUL_{kode}_TIKTOK.xlsx'), 'Template', 6, 1,
                 kolom(wb['Template'], 1, 'product_name'), toko, lap)
    tulis_laporan(lap, os.path.join(out_dir, f'LAPORAN_JUDUL_{kode}.xlsx'))
    ok = [x for x in lap if x[3]]
    print(f'shopee {n_s} judul, tiktok {n_t} judul, gagal pola {len(lap) - len(ok)}')
    print(f'panjang {min(x[4] for x in ok)}-{max(x[4] for x in ok)}, '
          f'toko selesai di karakter {min(x[5] for x in ok)}-{max(x[5] for x in ok)}')
    print('lewat 120:', sum(x[4] > BATAS_SHOPEE for x in ok))
    print('model dibetulkan:', sum('dibetulkan' in x[7] for x in ok))
