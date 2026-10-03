# -*- coding: utf-8 -*-
"""
Judul + deskripsi SEO untuk listing Smartprotection (bisa dipakai OP dengan
Toko=Otoprotection setelah fakta produknya dicek), satu sumber konten untuk
Shopee (teks biasa), TikTok (HTML <p>) dan Lazada (HTML lzd-article + Sorotan
Produk). Diminta user 2026-10-03.

Judul: pola "cover" dari optimasi_judul_sp_op.py (termasuk KOREKSI_MODEL).

Deskripsi -- hasil riset 2026-10-03 (lihat memory project-undercover-judul-seo-sp-op):
  - kata kunci utama (Cover Mobil {Model} {Tipe} + nama toko) di kalimat
    pertama / 100 karakter awal; variasi kata kunci (body cover, selimut,
    sarung, penutup mobil) masing-masing muncul wajar, bukan ditumpuk
  - teks bersih TANPA emoji (revisi user 2026-10-03): judul bagian huruf besar
    singkat, poin "- ", bagian SPESIFIKASI, tagline toko (SP: Pintar Melindungi)
  - tanpa link, nomor HP, nama marketplace/toko lain (larangan Shopee & TikTok)
  - TikTok disarankan >= 500 karakter; Shopee & Lazada maks 3.000
  - Lazada: Sorotan Produk = daftar poin (faktor ranking kedua setelah judul)
  - generasi & tahun mobil dicantumkan dari data varian listing itu sendiri
    (kata kunci tahun, mis. "cover mobil avanza 2015")
Fakta produk HANYA dari deskripsi toko yang sudah ada:
  Signature : bahan Polyester New Tech Grade S+ (ganti dari 'Taffeta import Korea',
              instruksi user 2026-10-03), anti air hingga 70%,
              anti debu, tahan UV, tali elastis keliling, bisa dicuci/laundry,
              bonus tas, garansi ukuran & warna, produksi sendiri, ready stock
  Transparan: PE/LDPE 80 mikron, 1,5x lebih tebal, full waterproof 100%, pola
              dipress, karet keliling, kancing klip ke roda, tidak luntur,
              aman untuk semua warna cat
Warna TIDAK diurutkan satu per satu (stok Abu-abu Reguler/strip tier-1 = 0,
aturan bisnis #5) -> cukup "pilih warna yang tersedia di varian".

Pemakaian:
  python3 konten_seo_sp_op.py <Toko> <folder_out> <shopee_basic.xlsx>
      <tiktok_all_information.xlsx> <lazada_basic.xlsx>
      [--var-shopee a.xlsx,b.xlsx] [--var-lazada c.xlsx]
--var-*: export penjualan (sales info) yang memuat nama varian, untuk daftar
generasi/tahun di deskripsi Shopee/Lazada (TikTok pakai variannya sendiri).
"""
import sys, os, re, html, argparse, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill, Font

import optimasi_judul_sp_op as JUDUL
from perbaikan_otoprotection_final import hitung_atribut

ORANGE = PatternFill('solid', fgColor='FFC000')
MAKS_DESKRIPSI = 3000

# ---------------------------------------------------------------- generasi
RE_BUKAN_GEN = re.compile(
    r'^(abu-abu|abu|hitam|biru benhur|biru benhru|biru|merah|hijau army|hijau amry|hijau|orange|silver|transparan|default|'
    r'(epic|elite|eltie|eite|elita|warior|warrior|wrior|strip ?\d?) ?\w*|tahun lain|model lain.*|custom)$', re.I)
# label opsional (Gen 1 / F70/F300 / JK / E30 / 5 Seater) + rentang tahun
RE_RENTANG = re.compile(r'^(.*?)\s*[:(]?\s*(\d{4})\s*-+\s*(\d{4}|sekarang|now)\s*\)?\s*(.*)$', re.I)


def normal_token(p):
    """'Gen 1 : 2017-2026' -> 'Gen 1 (2017–2026)'; betulkan salah ketik
    tahun 5 digit di nama varian listing (mis. '20012-2017' -> 2012)"""
    p = re.sub(r'\b(19|20)0(\d{2})\b', r'\1\2', p)
    p = re.sub(r'(\d)\s*-\s*(\d)\b(?!\d)', r'\1-\2', p)      # 'Gen 1 -3' -> 'Gen 1-3'
    m = RE_RENTANG.match(p)
    if not m:
        return re.sub(r'\s*:\s*', ' ', p), (1, 0)
    label, a, b, sisa = m.groups()
    b = b if b.isdigit() else 'sekarang'
    label = label.strip(' :(')
    if b.isdigit() and (int(b) > TAHUN_MAKS or int(b) < int(a)) or int(a) < 1930:
        # tahun mustahil = salah ketik di nama varian listing (mis. '1972-2979',
        # '2013-2029') -> jangan tampilkan tahunnya, catat utk dibetulkan user
        TAHUN_JANGGAL.append(p)
        return (label or None), (0, int(a))
    teks = f'{label} ({a}–{b})' if label else f'{a}–{b}'
    if sisa.strip(' )'):
        teks += f' {sisa.strip()}'
    return teks, (0, int(a))


TAHUN_MAKS = 2027
TAHUN_JANGGAL = []      # diisi normal_token(), dikosongkan per produk di siapkan()


def daftar_generasi(varian):
    """nama-nama varian -> baris generasi/tahun terurut; buang warna"""
    hasil = {}
    for v in varian:
        for bag in re.split(r'[,;]', str(v or '')):
            p = re.sub(r'\s+', ' ', bag).strip()
            if not p or p == 'None' or RE_BUKAN_GEN.match(p):
                continue
            teks, kunci = normal_token(p)
            if teks:
                hasil[teks] = kunci + (teks,)
    return [t for t, _ in sorted(hasil.items(), key=lambda x: x[1])]


def generasi_dari_deskripsi(desk):
    """blok 'Keterangan Generasi Mobil dan Tahun' yang ditulis manual
    (mis. Stargazer: nama Cartenz) -> dipakai apa adanya"""
    t = teks_polos(desk)
    if 'Keterangan Generasi' not in t:
        return None
    baris = [re.sub(r'\s+', ' ', l.strip('•· ').strip()) for l in t.split('\n') if l.strip().startswith('•')]
    return [t for t in (normal_token(b)[0] for b in baris) if t] or None


def teks_polos(d):
    d = re.sub(r'<br\s*/?>|</p>|</li>|</h\d>', '\n', str(d or ''))
    return html.unescape(re.sub(r'<[^>]+>', '', d))


# ---------------------------------------------------------------- konten
# tagline resmi per toko (SP: dipilih user 2026-10-03). Toko lain: kosong dulu.
TAGLINE = {'Smartprotection': 'Pintar Melindungi'}
# bahan lini Signature (user 2026-10-03; sebelumnya 'kain Taffeta waterproof import Korea')
BAHAN_SIGNATURE = 'Polyester New Tech Grade S+'


def konten(model, transparan, toko, generasi):
    """-> (pembuka[list], bagian[list of (judul, [baris])], penutup[list], sorotan[list])
    Format "clean" (revisi user 2026-10-03): tanpa emoji, judul bagian huruf
    besar singkat, poin pakai "- ", ada bagian SPESIFIKASI yang menjelaskan
    produk; tagline toko di kalimat pembuka."""
    tag = TAGLINE.get(toko)
    merek = f'{toko}, {tag}' if tag else toko
    if generasi:
        gen = [f'- {g}' for g in generasi]
        gen.append('Pilih generasi/tahun mobil di pilihan varian. Untuk tahun lain, '
                   'tulis tahun mobil di catatan pembelian.')
    else:
        gen = ['Ukuran disesuaikan dengan tipe dan tahun mobil. Mohon tulis tahun mobil '
               'di catatan pembelian.']
    if not transparan:
        pembuka = [
            f'Cover Mobil {model} Signature dari {merek}.',
            f'Body cover berbahan {BAHAN_SIGNATURE}, dibuat mengikuti '
            f'bentuk {model} sehingga pas di bodi, bukan ukuran all size. Selimut mobil ini '
            f'melindungi cat dari debu, air hujan, dan terik matahari, sehingga mobil tetap '
            f'bersih dan warna cat tidak cepat pudar.',
        ]
        bagian = [
            ('KEUNGGULAN', [
                '- Melindungi cat dari debu, air hujan, dan sinar matahari (UV)',
                '- Kain halus, tidak kasar di permukaan cat',
                f'- Ukuran pas mengikuti bentuk bodi {model}, bukan all size',
                '- Tidak mudah terbang tertiup angin berkat tali elastis di sekeliling bagian bawah',
                '- Mudah dirawat, bisa dicuci dan di-laundry',
                '- Praktis disimpan, sudah termasuk tas penyimpanan',
            ]),
            ('SPESIFIKASI', [
                'Tipe: Signature',
                f'Bahan: {BAHAN_SIGNATURE}',
                'Ketahanan air: hingga 70%',
                'Perlindungan: anti debu dan tahan sinar matahari (UV)',
                'Pengikat: tali elastis di sekeliling bagian bawah, tinggal diserut',
                'Warna: sesuai pilihan varian',
                f'Isi paket: 1 cover mobil {model} dan 1 tas penyimpanan',
            ]),
            (f'COCOK UNTUK {model.upper()}', gen),
            ('GARANSI DAN LAYANAN', [
                '- Garansi ukuran (kekecilan atau kebesaran)',
                '- Garansi warna jika tidak sesuai pesanan',
                f'- Diproduksi sendiri oleh {toko}, bukan reseller',
                '- Barang ready stock dan dikirim secepatnya',
            ]),
        ]
        penutup = [
            'Tips: tutup mobil dalam keadaan bersih dan kering agar cat tetap terjaga.',
            f'Cocok sebagai sarung mobil, selimut mobil, maupun penutup mobil {model} untuk '
            f'parkir di rumah, garasi, atau carport.',
        ]
        sorotan = [
            f'Bahan {BAHAN_SIGNATURE}, halus di permukaan cat',
            'Anti air hingga 70%, anti debu, tahan sinar matahari (UV)',
            f'Ukuran pas mengikuti bentuk {model}, bukan all size',
            'Tali elastis keliling bagian bawah, tidak mudah terbang tertiup angin',
            'Bisa dicuci dan di-laundry',
            'Termasuk tas penyimpanan',
            'Garansi ukuran dan garansi warna',
            f'Diproduksi sendiri oleh {toko}, ready stock',
        ]
    else:
        pembuka = [
            f'Cover Mobil {model} Transparan dari {merek}.',
            f'Body cover plastik PE tebal yang full waterproof, dibuat mengikuti pola {model} '
            f'yang beredar di Indonesia. Selimut mobil transparan ini praktis untuk parkir di '
            f'luar ruangan, melindungi mobil dari air hujan dan debu tanpa menutupi tampilannya.',
        ]
        bagian = [
            ('KEUNGGULAN', [
                '- Full waterproof: potongan pola dipress, bukan dijahit jarum, sehingga tidak ada '
                'celah tempat air merembes',
                '- Bahan 1,5x lebih tebal dibanding cover mobil plastik sejenis di pasaran',
                '- Aman dari angin di luar ruangan berkat karet keliling dan kancing klip di setiap roda',
                '- Tidak meninggalkan bercak luntur saat terkena hujan',
                '- Aman untuk semua warna cat mobil',
            ]),
            ('SPESIFIKASI', [
                'Tipe: Transparan',
                'Bahan: plastik PE (LDPE) 80 mikron',
                'Ketahanan air: full waterproof 100%',
                'Pengikat: karet keliling dan kancing klip ke setiap roda (lock system ke velg)',
                f'Isi paket: 1 cover mobil {model} Transparan',
            ]),
            (f'COCOK UNTUK {model.upper()}', gen),
        ]
        penutup = [
            'Tips: pastikan mobil dalam keadaan kering sebelum ditutup.',
            f'Cocok sebagai sarung mobil, selimut mobil, maupun penutup mobil {model} anti air '
            f'untuk parkir outdoor.',
        ]
        sorotan = [
            'Full waterproof 100%, plastik PE (LDPE) 80 mikron',
            'Bahan 1,5x lebih tebal dari cover plastik sejenis',
            'Potongan pola dipress, tidak ada celah air merembes',
            'Karet keliling dan kancing klip di setiap roda',
            'Aman dari angin saat dipakai di luar ruangan',
            'Tidak meninggalkan bercak luntur saat hujan',
            'Aman untuk semua warna cat mobil',
            f'Pola mengikuti {model} yang beredar di Indonesia',
        ]
    return pembuka, bagian, penutup, sorotan


def ke_baris(pembuka, bagian, penutup):
    """struktur -> daftar baris ('' = baris kosong, ('h', teks) = judul bagian)"""
    out = []
    for p in pembuka:
        out += [p, '']
    for judul, isi in bagian:
        out.append(('h', judul))
        out += isi
        out.append('')
    for p in penutup:
        out += [p, '']
    while out and out[-1] == '':
        out.pop()
    return out


def render_polos(baris):
    return '\n'.join(b[1] if isinstance(b, tuple) else b for b in baris)


def render_html(baris):
    parts = []
    for b in baris:
        if isinstance(b, tuple):
            parts.append(f'<p><strong>{html.escape(b[1])}</strong></p>')
        elif b == '':
            parts.append('<p><br></p>')
        else:
            parts.append(f'<p>{html.escape(b)}</p>')
    return ''.join(parts)


def render_sorotan(sorotan):
    return '<ul>' + ''.join(f'<li>{html.escape(s)}</li>' for s in sorotan) + '</ul>'


# ---------------------------------------------------------------- I/O
def varian_dari_export(paths, c_id, c_var, start, header=None):
    d = defaultdict(list)
    for p in paths:
        ws = openpyxl.load_workbook(p).worksheets[0]
        if header:
            hh = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
            c_var = hh[header]
        for r in range(start, ws.max_row + 1):
            pid = ws.cell(row=r, column=c_id).value
            if pid:
                d[str(pid)].append(ws.cell(row=r, column=c_var).value)
    return d


def siapkan(ch, pid, nama_lama, desk_lama, varian, toko, laporan):
    """-> (judul, desk_polos, baris, sorotan) atau None kalau bukan cover mobil SP"""
    model, trn = JUDUL.urai(nama_lama)
    if model is None:
        laporan.append((ch, pid, nama_lama, '', '', 'bukan pola cover mobil - tidak diubah'))
        return None
    judul, _, model_fix = JUDUL.judul_baru(model, trn, toko)
    TAHUN_JANGGAL.clear()
    gen = generasi_dari_deskripsi(desk_lama) or daftar_generasi(varian or [])
    janggal = sorted(set(TAHUN_JANGGAL))
    pembuka, bagian, penutup, sorotan = konten(model_fix, trn, toko, gen)
    baris = ke_baris(pembuka, bagian, penutup)
    polos = render_polos(baris)
    cat = []
    if model_fix != model:
        cat.append(f'model dibetulkan: {model} -> {model_fix}')
    if not gen:
        cat.append('tanpa daftar generasi (data varian tidak ada)')
    if janggal:
        cat.append(f'tahun varian janggal (tidak ditampilkan, betulkan nama varian): {janggal}')
    lama_t = teks_polos(desk_lama)
    if re.search(r'otoprotection', lama_t, re.I):
        cat.append('deskripsi lama menyebut Otoprotection')
    if not trn and 'PE Tebal Transparan' in lama_t:
        cat.append('deskripsi lama salah (isi Transparan di listing Signature)')
    if len(polos) > MAKS_DESKRIPSI:
        cat.append(f'DESKRIPSI {len(polos)} > {MAKS_DESKRIPSI}')
    laporan.append((ch, pid, nama_lama, judul, polos, '; '.join(cat)))
    return judul, polos, baris, sorotan


def tandai(sel, nilai):
    sel.value = nilai
    sel.fill = ORANGE


def proses_shopee(path, out, toko, var, laporan):
    wb = openpyxl.load_workbook(path)
    ws = wb.worksheets[0]
    h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
    c_nama, c_desk = h['et_title_product_name'], h['et_title_product_description']
    simpan = []
    for r in range(7, ws.max_row + 1):
        pid = ws.cell(row=r, column=1).value
        if not pid:
            continue
        hasil = siapkan('shopee', str(pid), ws.cell(row=r, column=c_nama).value,
                        ws.cell(row=r, column=c_desk).value, var.get(str(pid)), toko, laporan)
        if hasil:
            tandai(ws.cell(row=r, column=c_nama), hasil[0])
            tandai(ws.cell(row=r, column=c_desk), hasil[1])
            simpan.append(r)
    JUDUL_pindah(ws, simpan, 7)
    wb.save(out)
    return len(simpan)


def proses_lazada(path, out, toko, var, laporan):
    wb = openpyxl.load_workbook(path)
    ws = wb['template']
    h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
    c_nama, c_desk, c_sor = h['Nama Produk'], h['Deskripsi Utama'], h['Sorotan Produk']
    simpan = []
    for r in range(5, ws.max_row + 1):
        pid = ws.cell(row=r, column=1).value
        if not pid:
            continue
        hasil = siapkan('lazada', str(pid), ws.cell(row=r, column=c_nama).value,
                        ws.cell(row=r, column=c_desk).value, var.get(str(pid)), toko, laporan)
        if hasil:
            tandai(ws.cell(row=r, column=c_nama), hasil[0])
            tandai(ws.cell(row=r, column=c_desk),
                   '<article class="lzd-article">' + render_html(hasil[2]) + '</article>')
            tandai(ws.cell(row=r, column=c_sor), render_sorotan(hasil[3]))
            simpan.append(r)
    JUDUL_pindah(ws, simpan, 5)
    wb.save(out)
    return len(simpan)


def proses_tiktok(path, out, toko, laporan):
    """all_information: semua baris varian ikut (template wajib lengkap) +
    atribut wajib yang kosong diisi (pelajaran OP/SP 2026-09)"""
    wb = openpyxl.load_workbook(path)
    ws = wb['Template']
    h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
    c_nama, c_desk, c_var = h['product_name'], h['product_description'], h['variation_value']
    i_atr = {k: v for k, v in h.items()
             if k in ('product_property/100530', 'product_property/102755')}
    c_garansi = h.get('product_property/100107')
    per_produk = defaultdict(list)
    for r in range(6, ws.max_row + 1):
        pid = ws.cell(row=r, column=1).value
        if pid:
            per_produk[str(pid)].append(r)
    simpan, n_atr = [], 0
    for pid, rows in per_produk.items():
        varian = [ws.cell(row=r, column=c_var).value for r in rows]
        hasil = siapkan('tiktok', pid, ws.cell(row=rows[0], column=c_nama).value,
                        ws.cell(row=rows[0], column=c_desk).value, varian, toko, laporan)
        if not hasil:
            continue
        desk_html = render_html(hasil[2])
        for r in rows:
            tandai(ws.cell(row=r, column=c_nama), hasil[0])
            tandai(ws.cell(row=r, column=c_desk), desk_html)
            atr = hitung_atribut(hasil[0], ws, r, i_atr)
            if c_garansi and ws.cell(row=r, column=c_garansi).value in (None, ''):
                atr[c_garansi] = 'Tanpa Garansi'
            for idx, val in atr.items():
                tandai(ws.cell(row=r, column=idx), val)
                n_atr += 1
        simpan.extend(rows)
    JUDUL_pindah(ws, sorted(simpan), 6)
    wb.save(out)
    return len(per_produk), len(simpan), n_atr


def JUDUL_pindah(ws, simpan, start):
    """rapatkan baris yang diubah ke atas, buang sisanya"""
    import copy
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


def tulis_laporan(laporan, out):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Judul & Deskripsi'
    for c, v in enumerate(['Channel', 'ID Produk', 'Judul Lama', 'Judul Baru',
                           'Deskripsi Baru (teks)', 'Catatan'], 1):
        ws.cell(row=1, column=c, value=v).font = Font(bold=True)
    for r, x in enumerate(sorted(laporan, key=lambda x: (x[0], x[3])), 2):
        for c, v in enumerate(x, 1):
            ws.cell(row=r, column=c, value=v)
        if x[5]:
            ws.cell(row=r, column=6).fill = ORANGE
    for col, wd in zip('ABCDEF', (8, 21, 50, 80, 90, 50)):
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = 'A2'
    wb.save(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('toko')
    ap.add_argument('out')
    ap.add_argument('shopee')
    ap.add_argument('tiktok')
    ap.add_argument('lazada')
    ap.add_argument('--var-shopee', default='')
    ap.add_argument('--var-lazada', default='')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    kode = a.toko.upper()
    v_sh = varian_dari_export([p for p in a.var_shopee.split(',') if p], 1, 4, 7)
    v_lz = varian_dari_export([p for p in a.var_lazada.split(',') if p], 1, None, 4,
                              header='Variations Combo') if a.var_lazada else {}
    lap = []
    n_s = proses_shopee(a.shopee, os.path.join(a.out, f'{kode}_SHOPEE_JUDUL_DESKRIPSI.xlsx'), a.toko, v_sh, lap)
    n_l = proses_lazada(a.lazada, os.path.join(a.out, f'{kode}_LAZADA_JUDUL_DESKRIPSI.xlsx'), a.toko, v_lz, lap)
    n_t = proses_tiktok(a.tiktok, os.path.join(a.out, f'{kode}_TIKTOK_JUDUL_DESKRIPSI.xlsx'), a.toko, lap)
    tulis_laporan(lap, os.path.join(a.out, f'LAPORAN_JUDUL_DESKRIPSI_{kode}.xlsx'))
    ok = [x for x in lap if x[3]]
    print(f'shopee {n_s} produk | lazada {n_l} produk | tiktok {n_t[0]} produk / {n_t[1]} baris, '
          f'{n_t[2]} sel atribut diisi')
    print('dilewati (bukan cover mobil):', [x[2] for x in lap if not x[3]])
    L = [len(x[4]) for x in ok]
    print(f'panjang deskripsi teks {min(L)}-{max(L)} karakter')
    print('catatan:', Counter(c.split(':')[0] for x in ok for c in x[5].split('; ') if c))
