# -*- coding: utf-8 -*-
"""
Finalisasi TikTok Undercover (2026-10-28): deskripsi generasi/tahun + file upload.

Menggabungkan:
  1. judul "untuk" + deskripsi dari judul_kompatibel_tiktok_ua.py (file basic_information
     keluaran script itu = BASE)
  2. update tahun akhir ke 2026 untuk model yang masih dijual (update_tahun_generasi_tiktok_ua.UPDATE)
  3. keputusan user 2026-10-28:
       - Toyota Camry: daftar generasi dibenahi (semua tipe sama) + Gen 9 2024-2026
       - Hyundai Palisade: Gen 1 2018-2024, Gen 2 2024-2026 (semua tipe)
       - Daihatsu Ayla: Gen 1 2013-2023, Gen 2 2023-2026 (sama dgn variasi)
       - Daihatsu Feroza: Gen 3 1985-1995, Gen 4 1996-2007 (semua tipe)
       - Toyota Innova: baris Gen 2 Facelift (Reborn) ikut diperpanjang ke 2026
       - Wuling Almaz & model lain yang tidak disebut: tidak diubah
       - produk yang deskripsinya TIDAK punya daftar generasi: dibuat dari nama variasi listing
  4. 275 produk yang gagal upload basic_information (atribut Tahun kosong) -> file
     all_information (semua baris varian) dgn atribut Tahun/Bile/Garansi terisi
  5. produk lain yang deskripsinya berubah -> file basic_information

Pemakaian:
  python3 finalkan_tiktok_ua.py <base_basic.xlsx> <hasil_gagal.xlsx> <out_dir> <all_info.xlsx...>
Semua input sudah lewat repair_xlsx.py.
"""
import sys, os, re, copy, html, openpyxl
from collections import defaultdict, Counter
from openpyxl.styles import PatternFill, Font

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update_tahun_generasi_tiktok_ua as U

ORANGE = PatternFill('solid', fgColor='FFC000')
HEADER_BLOK = 'Keterangan Generasi Mobil dan Tahun:'

OVERRIDE = {
    'Toyota Camry': ['Gen 1: Tahun 1982-1986', 'Gen 2: Tahun 1987-1991', 'Gen 3: Tahun 1990-1996',
                     'Gen 4: Tahun 1996-2002', 'Gen 5: Tahun 2002-2006', 'Gen 6: Tahun 2006-2011',
                     'Gen 7: Tahun 2012-2018', 'Gen 8: Tahun 2018-2024', 'Gen 9: Tahun 2024-2026'],
    'Hyundai Palisade': ['Gen 1: Tahun 2018-2024', 'Gen 2: Tahun 2024-2026'],
    'Daihatsu Ayla': ['Gen 1: Tahun 2013-2023', 'Gen 2: Tahun 2023-2026'],
    'Daihatsu Feroza': ['Gen 3: Tahun 1985-1995', 'Gen 4: Tahun 1996-2007'],
}
RE_WARNA = re.compile(
    r'^(abu-abu|abu|hitam|biru benhur|biru benhru|biru|merah|hijau army|hijau amry|hijau|orange|silver|'
    r'transparan|default|(epic|elite|eltie|eite|elita|warior|warrior|wrior|strip ?\d?) ?\w*)$', re.I)
RE_VAR = re.compile(r'^(?P<lab>.*?)[\s:]*\(?\s*(?P<a>(?:19|20)\d{2})\s*[-–]+\s*(?P<b>(?:19|20)\d{2}|[Ss]ekarang|now)\s*\)?\s*$')


def baris_blok(d):
    pos = U.blok_html(d)
    if not pos:
        return None
    segs = re.split(r'(<br\s*/?>|</p>|<p[^>]*>)', d[pos[0]:pos[1]])
    return [U.teks(s).strip() for k, s in enumerate(segs) if k % 2 == 0 and U.teks(s).strip()][1:]


def set_blok(d, lines):
    """ganti isi blok generasi dgn `lines` (tanpa bullet); kalau belum ada, sisipkan."""
    lines = [f'• {l}' for l in lines]
    pos = U.blok_html(d)
    if pos:
        i, j = pos
        segs = re.split(r'(<br\s*/?>|</p>|<p[^>]*>)', d[i:j])
        idx_teks = [k for k, s in enumerate(segs) if k % 2 == 0 and U.teks(s).strip()]
        h, last = idx_teks[0], idx_teks[-1]
        def delim(a, b):
            return ''.join(segs[a + 1:b])
        hdr_sep = delim(h, idx_teks[1]) if len(idx_teks) > 1 else '<br>'
        line_sep = delim(idx_teks[1], idx_teks[2]) if len(idx_teks) > 2 else hdr_sep
        tail = ''.join(segs[last + 1:]) if last > h else ''.join(segs[h + 1:])
        return d[:i] + segs[h] + hdr_sep + line_sep.join(lines) + tail + d[j:]
    marker = 'Untuk Order' if 'Untuk Order' in d else 'Bonus:'
    k = d.find(marker)
    if k < 0:
        return d
    m = re.search(r'<p[^>]*>$', d[:k])
    if m:                                          # gaya <p>
        pre = d[:m.start()]
        blok = '<p>' + HEADER_BLOK + '</p>' + ''.join(f'<p>{html.escape(l)}</p>' for l in lines)
        blok += '<br>' if marker == 'Untuk Order' else '<p><br></p>'
        return pre + blok + d[m.start():]
    blok = HEADER_BLOK + '<br>' + '<br>'.join(html.escape(l) for l in lines) + '<br><br>'
    return d[:k] + blok + d[k:]


def ubah_baris(d, label_re, tahun_baru):
    """ubah tahun akhir baris generasi yang labelnya cocok `label_re` (mis. Reborn)."""
    pos = U.blok_html(d)
    if not pos:
        return d
    i, j = pos
    segs = re.split(r'(<br\s*/?>|</p>|<p[^>]*>)', d[i:j])
    for k, s in enumerate(segs):
        if k % 2:
            continue
        m = U.RE_BARIS.match(U.teks(s))
        if m and re.search(label_re, m.group('lab')):
            new = re.sub(r'(?<!\d)((?:19|20)\d{2}\s*[-–]+\s*)(?:19|20)\d{2}(?!\d)', rf'\g<1>{tahun_baru}', s, count=1)
            if new != s:
                segs[k] = new
                return d[:i] + ''.join(segs) + d[j:]
    return d


def baris_dari_varian(varian):
    """nama variasi listing -> baris generasi ('Gen 1: Tahun 2017-2021', 'F70: Tahun 1985-1995', '3 Pintu')"""
    hasil = {}
    for v in varian:
        for bag in str(v or '').split(','):
            p = re.sub(r'[\s\xa0\t]+', ' ', bag).strip()
            if not p or p == 'None' or RE_WARNA.match(p) or p.lower() in ('tahun lain', 'model lain'):
                continue
            m = RE_VAR.match(p)
            if m:
                lab = m.group('lab').strip(' :(')
                b = m.group('b'); b = 'Sekarang' if not b.isdigit() else b
                hasil[(int(m.group('a')), lab)] = f"{lab}: Tahun {m.group('a')}-{b}" if lab else f"Tahun {m.group('a')}-{b}"
            else:
                hasil[(9999, p)] = p
    return [t for _, t in sorted(hasil.items())]


def final_deskripsi(base_desc, model, varian):
    d = base_desc
    if model in OVERRIDE:
        d = set_blok(d, OVERRIDE[model])
    elif model in U.UPDATE:
        d = U.ubah_deskripsi(d, U.UPDATE[model])[0]
    if model == 'Toyota Innova':
        d = ubah_baris(d, r'Gen 2 Facelift', 2026)
    if baris_blok(d) is None:
        lines = baris_dari_varian(varian)
        if lines:
            d = set_blok(d, lines)
    return d


def main(base_path, gagal_path, out_dir, all_paths):
    os.makedirs(out_dir, exist_ok=True)
    wg = openpyxl.load_workbook(gagal_path)['Template']
    gagal = {str(wg.cell(row=r, column=2).value) for r in range(6, wg.max_row + 1) if wg.cell(row=r, column=2).value}
    # base
    wb = openpyxl.load_workbook(base_path)
    wsb = wb['Template']
    hb = {str(wsb.cell(row=1, column=c).value): c for c in range(1, wsb.max_column + 1)}
    base = {}
    for r in range(6, wsb.max_row + 1):
        pid = wsb.cell(row=r, column=1).value
        if pid:
            base[str(pid)] = dict(row=r, nama=str(wsb.cell(row=r, column=hb['product_name']).value),
                                  desk=str(wsb.cell(row=r, column=hb['product_description']).value or ''),
                                  merek=wsb.cell(row=r, column=hb['brand']).value)
    # export all_information -> varian, deskripsi live
    varian, live, wbs = defaultdict(list), {}, {}
    for p in all_paths:
        w = openpyxl.load_workbook(p)
        ws = w['Template']
        h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
        wbs[p] = (w, ws, h)
        for r in range(6, ws.max_row + 1):
            pid = ws.cell(row=r, column=1).value
            if pid:
                varian[str(pid)].append(ws.cell(row=r, column=h['variation_value']).value)
                live.setdefault(str(pid), str(ws.cell(row=r, column=h['product_description']).value or ''))
    final, lap = {}, []
    for pid, b in base.items():
        m = U.RE_JUDUL.match(b['nama'])
        if not m or not b['nama'].startswith('Cover Mobil'):
            continue
        model = m.group(2).strip()
        d = final_deskripsi(b['desk'], model, varian.get(pid, []))
        final[pid] = d
        lama = baris_blok(live.get(pid, b['desk']))
        baru = baris_blok(d)
        berubah = lama != baru
        lap.append((pid, model, m.group(1), '; '.join(lama or ['(tidak ada blok)']),
                    '; '.join(baru or ['(tidak ada blok)']), 'GAGAL-atribut' if pid in gagal else 'lolos', berubah))
    ubah_lolos = [x for x in lap if x[6] and x[5] == 'lolos']
    # ---- 1. basic_information: produk lolos yang deskripsinya berubah
    ids = {x[0] for x in ubah_lolos}
    keep = [info['row'] for pid, info in base.items() if pid in ids]
    for pid in ids:
        sel = wsb.cell(row=base[pid]['row'], column=hb['product_description'])
        sel.value = final[pid]; sel.fill = ORANGE
    n_kol = wsb.max_column
    for k, r in enumerate(sorted(keep)):
        t = 6 + k
        if t != r:
            for c in range(1, n_kol + 1):
                s, d_ = wsb.cell(row=r, column=c), wsb.cell(row=t, column=c)
                d_.value = s.value; d_.fill = copy.copy(s.fill)
    if 6 + len(keep) <= wsb.max_row:
        wsb.delete_rows(6 + len(keep), wsb.max_row - (6 + len(keep)) + 1)
    wb.save(os.path.join(out_dir, 'UA_TIKTOK_DESKRIPSI_basic_information.xlsx'))
    # ---- 2. all_information: 275 produk gagal
    n_baris = n_atr = 0
    for p, (w, ws, h) in wbs.items():
        target = gagal | ids          # gagal atribut + produk lolos yg deskripsinya berubah (1 upload saja)
        rows_gagal = [r for r in range(6, ws.max_row + 1) if str(ws.cell(row=r, column=1).value) in target]
        if not rows_gagal:
            continue
        c_nama, c_desk, c_merek = h['product_name'], h['product_description'], h['brand']
        c_th, c_bile, c_gar = h['product_property/100530'], h['product_property/102755'], h['product_property/100107']
        garansi = {}
        for r in rows_gagal:
            v = ws.cell(row=r, column=c_gar).value
            if v not in (None, ''):
                garansi.setdefault(str(ws.cell(row=r, column=1).value), v)
        for r in rows_gagal:
            pid = str(ws.cell(row=r, column=1).value)
            b = base[pid]
            sel = ws.cell(row=r, column=c_nama); sel.value = b['nama']; sel.fill = ORANGE
            sel = ws.cell(row=r, column=c_desk); sel.value = final.get(pid, b['desk']); sel.fill = ORANGE
            if b['merek'] and ws.cell(row=r, column=c_merek).value != b['merek']:
                sel = ws.cell(row=r, column=c_merek); sel.value = b['merek']; sel.fill = ORANGE
            for c, nilai in ((c_th, '2026'), (c_bile, '16:9'), (c_gar, garansi.get(pid, 'Garansi Toko'))):
                if ws.cell(row=r, column=c).value in (None, ''):
                    sel = ws.cell(row=r, column=c); sel.value = nilai; sel.fill = ORANGE
                    n_atr += 1
        n_kol = ws.max_column
        for k, r in enumerate(rows_gagal):
            t = 6 + k
            if t != r:
                for c in range(1, n_kol + 1):
                    s, d_ = ws.cell(row=r, column=c), ws.cell(row=t, column=c)
                    d_.value = s.value; d_.fill = copy.copy(s.fill)
        sisa = 6 + len(rows_gagal)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)
        n_baris += len(rows_gagal)
        w.save(os.path.join(out_dir, 'UA_TIKTOK_ALL_INFORMATION_semua_perubahan.xlsx'))
    # ---- 3. laporan
    lw = openpyxl.Workbook(); ls = lw.active; ls.title = 'Perubahan Generasi'
    for c, v in enumerate(['ID Produk', 'Model', 'Tipe', 'Generasi lama', 'Generasi baru', 'Status upload', 'Berubah'], 1):
        ls.cell(row=1, column=c, value=v).font = Font(bold=True)
    for i, x in enumerate(sorted(lap, key=lambda x: (x[1], x[2])), 2):
        for c, v in enumerate(x, 1):
            ls.cell(row=i, column=c, value='ya' if v is True else ('' if v is False else v))
    for col, wd in zip('ABCDEFG', (21, 28, 11, 80, 80, 14, 9)):
        ls.column_dimensions[col].width = wd
    ls.freeze_panes = 'A2'
    lw.save(os.path.join(out_dir, 'LAPORAN_FINAL_TIKTOK_UA.xlsx'))
    return lap, ubah_lolos, n_baris, n_atr


if __name__ == '__main__':
    lap, ubah_lolos, n_baris, n_atr = main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
    print(f'produk cover mobil diproses: {len(lap)} | deskripsi generasi berubah: {sum(x[6] for x in lap)}')
    print(f'  basic_information (lolos & berubah): {len(ubah_lolos)} produk')
    print(f'  all_information (gagal atribut Tahun): {sum(1 for x in lap if x[5] == "GAGAL-atribut")} produk mobil, {n_baris} baris, {n_atr} sel atribut diisi')
