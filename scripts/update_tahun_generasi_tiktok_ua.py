# -*- coding: utf-8 -*-
"""
Perbarui tahun akhir generasi TERAKHIR di deskripsi cover mobil Undercover
TikTok ("Keterangan Generasi Mobil dan Tahun") untuk model yang MASIH dijual /
diproduksi di 2026. Deskripsi lama ditulis saat "sekarang" = 2024, jadi 82 dari
111 model berhenti di 2024 padahal banyak yang masih beredar (mis. Honda Brio).

Aturan (instruksi user 2026-10-27): kalau mobilnya memang sampai 2026 -> 2026;
kalau mentok di 2024 (sudah tidak dijual) -> biarkan 2024.
Hanya BARIS GENERASI TERAKHIR (start tahun terbesar) yang diubah; baris lain
dan teks lain tidak disentuh. Dasar keputusan per model: riset web 2026-10-27
(daftar harga Oto/Moladin/Otodriver/Suzuki.co.id Sep-Okt 2026, GIIAS/IIMS 2026,
Katadata soal discontinue) -- lihat UPDATE di bawah.

Pemakaian:
  python3 update_tahun_generasi_tiktok_ua.py <basic_info_terbaru.xlsx> <hasil_gagal.xlsx|-> <folder_out>
  basic_info_terbaru = keluaran judul_kompatibel_tiktok_ua.py (judul "untuk").
  hasil_gagal = file *_result.xlsx dari upload TikTok sebelumnya (daftar produk
  yang GAGAL karena atribut Tahun kosong); '-' kalau tidak ada.
Keluaran:
  UA_TIKTOK_UPDATE_TAHUN_siap_upload.xlsx  produk yang deskripsinya berubah DAN
      tidak ada di daftar gagal (aman lewat basic_information)
  UA_TIKTOK_UPDATE_TAHUN_butuh_all_information.xlsx  daftar produk gagal (atribut
      Tahun kosong): harus lewat template all_information
  LAPORAN_UPDATE_TAHUN_UA.xlsx  per model & per produk
"""
import sys, os, re, html, copy, openpyxl
from openpyxl.styles import PatternFill, Font

ORANGE = PatternFill('solid', fgColor='FFC000')

# model (nama di judul) -> tahun akhir baru generasi terakhir
UPDATE = {
    # Honda
    'Honda Brio': 2026, 'Honda BRV': 2026, 'Honda CRV': 2026, 'Honda HRV': 2026, 'Honda WRV': 2026,
    'WRV': 2026, 'Honda Accord': 2026, 'Honda Civic Hatchback': 2026,
    'Honda Civic Sedan': 2026,           # disamakan dgn tipe Reguler yg sudah 2026
    'Honda City Hatchback': 2025,        # supply ke dealer berhenti Agustus 2025
    # Toyota
    'Toyota Avanza': 2026, 'Toyota Veloz': 2026, 'Toyota Agya': 2026, 'Toyota Calya': 2026, 'Toyota Raize': 2026,
    'Toyota Rush': 2026, 'Toyota Innova': 2026, 'Toyota Fortuner': 2026, 'Toyota Vios': 2026,
    'Toyota Alphard': 2026, 'Toyota Vellfire': 2026, 'Toyota Voxy': 2026, 'Toyota Land Cruiser': 2026,
    'Toyota HiAce': 2026, 'Toyota Hilux': 2026,
    # Daihatsu
    'Daihatsu Xenia': 2026, 'Daihatsu Terios': 2026, 'Daihatsu Sigra': 2026, 'Daihatsu Rocky': 2026,
    'Daihatsu Sirion': 2026, 'Daihatsu Luxio': 2026, 'Daihatsu Gran Max Minibus': 2026,
    'Daihatsu Gran Max Pick Up': 2026,
    # Mitsubishi
    'Mitsubishi Xpander': 2026, 'Mitsubishi Xpander Cross': 2026, 'Mitsubishi Pajero Sport': 2026,
    'Mitsubishi Triton': 2026, 'Mitsubishi Destinator': 2026,
    # Suzuki
    'Suzuki Ertiga': 2026, 'Suzuki XL7': 2026, 'Suzuki APV Arena': 2026, 'Suzuki Carry Pickup': 2026,
    'Suzuki Jimny': 2026, 'Suzuki S-Presso': 2026, 'Suzuki Fronx': 2026,
    # Nissan
    'Nissan Grand Livina': 2026, 'Nissan Serena': 2026, 'Nissan X-Trail': 2026,
    # Hyundai / Kia / Mazda / Wuling
    'Hyundai Creta': 2026, 'Hyundai Santa Fe': 2026, 'Kia Sonet': 2026,
    'Mazda 2 Hatchback': 2026, 'Mazda CX-5': 2026,
    'Wuling Cortez': 2026, 'Wuling Confero': 2026, 'Wuling Air EV': 2026,
    # Premium
    'Mercedes Benz C Class': 2026, 'Mercedes Benz E Class': 2026, 'BMW Seri 3': 2026, 'BMW Seri 5': 2026,
    'Mini Cooper': 2026,
    # satu tahun saja ("Tahun 2025") -> rentang
    'BYD Atto 1': 2026,
}
# TIDAK diubah, belum pasti (ditanyakan ke user): Toyota Camry, Honda City Sedan, Wuling Almaz,
# Suzuki APV Luxury, Suzuki Swift, Suzuki Vitara, Suzuki Baleno, Hyundai Palisade, Hyundai Avega,
# Daihatsu Ayla, Toyota Yaris. Tidak diubah (tidak ada di lineup 2026): Honda Freed/Mobilio/Odyssey/
# Stream/Jazz, Toyota Sienta/Corolla/Harrier, Suzuki Ignis/Karimun/SX4, Nissan Juke, Kia Picanto,
# Chevrolet Captiva/Spin, Ford Everest, dst.

RE_JUDUL = re.compile(r'^Cover Mobil (Reguler|Premium|Exclusive) untuk (.+?) - ')
RE_BARIS = re.compile(r'^\s*[•·\-]?\s*(?P<lab>.*?)[\s:]*(?:Tahun|Taun|Tahum)?\s*:?\s*'
                      r'(?P<a>(?:19|20)\d{2})(?:\s*[-–]+\s*(?P<b>(?:19|20)\d{2}\d?|now|Now|sekarang|Sekarang))?'
                      r'\s*(?P<ket>\(.*\))?\s*\.?\s*$')
AKHIR_BLOK = ('Untuk Order', 'Bonus:', 'Deskripsi Produk', '!PERHATIAN', 'Spesifikasi')


def teks(seg):
    return html.unescape(re.sub(r'<[^>]+>', '', seg))


def blok_html(d):
    i = d.find('Keterangan Generasi')
    if i < 0:
        return None
    end = len(d)
    for k in AKHIR_BLOK:
        j = d.find(k, i + 20)
        if j > 0:
            end = min(end, j)
    # mundur sampai awal tag penutup baris supaya tag tidak terpotong
    return i, end


def ubah_deskripsi(d, tahun_baru):
    """-> (deskripsi_baru, (baris_lama, baris_baru)) atau (d, None) bila tak berubah"""
    pos = blok_html(d)
    if not pos:
        return d, None
    i, j = pos
    blok = d[i:j]
    segs = re.split(r'(<br\s*/?>|</p>|<p[^>]*>)', blok)
    kandidat = []
    for k, s in enumerate(segs):
        if k % 2:                       # delimiter
            continue
        m = RE_BARIS.match(teks(s))
        if m:
            kandidat.append((int(m.group('a')), k, m))
    if not kandidat:
        return d, None
    start, k, m = max(kandidat, key=lambda x: x[0])
    seg = segs[k]
    b = m.group('b')
    if b is None:                       # satu tahun saja
        baru = re.sub(rf'(?<!\d){start}(?!\d)', f'{start}-{tahun_baru}', seg, count=1)
    else:
        if b.isdigit() and int(b[:4]) >= tahun_baru and len(b) == 4:
            return d, None              # sudah sama / lebih baru
        if not b.isdigit() and b.lower() in ('now', 'sekarang'):
            return d, None
        baru = re.sub(rf'((?<!\d){start}\s*[-–]+\s*)(?:19|20)\d{{2}}\d?(?!\d)', rf'\g<1>{tahun_baru}', seg, count=1)
    if baru == seg:
        return d, None
    segs[k] = baru
    return d[:i] + ''.join(segs) + d[j:], (teks(seg).strip(), teks(baru).strip())


def main(src, hasil_gagal, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    gagal = set()
    if hasil_gagal != '-':
        wg = openpyxl.load_workbook(hasil_gagal)['Template']
        for r in range(6, wg.max_row + 1):
            v = wg.cell(row=r, column=2).value
            if v:
                gagal.add(str(v))
    wb = openpyxl.load_workbook(src)
    ws = wb['Template']
    h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
    c_id, c_nama, c_desk = h['product_id'], h['product_name'], h['product_description']
    lap, diubah = [], []
    for r in range(6, ws.max_row + 1):
        pid = ws.cell(row=r, column=c_id).value
        if not pid:
            continue
        nama = str(ws.cell(row=r, column=c_nama).value or '')
        m = RE_JUDUL.match(nama)
        if not m or 'Cover Mobil' not in nama[:12]:
            continue
        model = m.group(2).strip()
        if model not in UPDATE:
            continue
        d = str(ws.cell(row=r, column=c_desk).value or '')
        d2, info = ubah_deskripsi(d, UPDATE[model])
        if info:
            sel = ws.cell(row=r, column=c_desk); sel.value = d2; sel.fill = ORANGE
            diubah.append(r)
            lap.append((str(pid), model, m.group(1), info[0], info[1], 'GAGAL-atribut' if str(pid) in gagal else 'siap'))
    # tulis file "siap upload" (produk berubah & tidak gagal) dan file "butuh all_information"
    def tulis(rows, out):
        wb2 = openpyxl.load_workbook(src)
        w2 = wb2['Template']
        # salin nilai deskripsi yang sudah diubah dari wb ke wb2 lalu rapatkan baris
        keep = []
        for r in rows:
            for c in range(1, w2.max_column + 1):
                w2.cell(row=r, column=c).value = ws.cell(row=r, column=c).value
            keep.append(r)
        n_kol = w2.max_column
        for i, r in enumerate(keep):
            t = 6 + i
            if t != r:
                for c in range(1, n_kol + 1):
                    d_, s_ = w2.cell(row=t, column=c), w2.cell(row=r, column=c)
                    d_.value = s_.value
                    d_.fill = copy.copy(s_.fill)
        sisa = 6 + len(keep)
        if sisa <= w2.max_row:
            w2.delete_rows(sisa, w2.max_row - sisa + 1)
        wb2.save(out)
    siap = [r for r in diubah if str(ws.cell(row=r, column=c_id).value) not in gagal]
    butuh = [r for r in range(6, ws.max_row + 1)
             if ws.cell(row=r, column=c_id).value and str(ws.cell(row=r, column=c_id).value) in gagal]
    tulis(siap, os.path.join(out_dir, 'UA_TIKTOK_UPDATE_TAHUN_siap_upload.xlsx'))
    if butuh:
        tulis(butuh, os.path.join(out_dir, 'UA_TIKTOK_UPDATE_TAHUN_butuh_all_information.xlsx'))
    lw = openpyxl.Workbook(); ls = lw.active; ls.title = 'Per Model'
    per = {}
    for pid, model, tier, lama, baru, st in lap:
        per.setdefault(model, [lama, baru, 0])[2] += 1
    for c, v in enumerate(['Model', 'Baris generasi terakhir (lama)', 'Baru', 'Jumlah produk (tipe)'], 1):
        ls.cell(row=1, column=c, value=v).font = Font(bold=True)
    for i, (mo, (lama, baru, n)) in enumerate(sorted(per.items()), 2):
        for c, v in enumerate([mo, lama, baru, n], 1):
            ls.cell(row=i, column=c, value=v)
    l2 = lw.create_sheet('Per Produk')
    for c, v in enumerate(['ID Produk', 'Model', 'Tipe', 'Lama', 'Baru', 'Status upload'], 1):
        l2.cell(row=1, column=c, value=v).font = Font(bold=True)
    for i, x in enumerate(sorted(lap, key=lambda x: (x[1], x[2])), 2):
        for c, v in enumerate(x, 1):
            l2.cell(row=i, column=c, value=v)
    l3 = lw.create_sheet('Gagal Atribut Tahun')
    for c, v in enumerate(['ID Produk', 'Judul', 'Jenis', 'Tipe', 'Deskripsi berubah (tahun)?'], 1):
        l3.cell(row=1, column=c, value=v).font = Font(bold=True)
    berubah_id = {x[0] for x in lap}
    for i, r in enumerate(butuh, 2):
        n_ = str(ws.cell(row=r, column=c_nama).value or '')
        mm = re.match(r'Cover (Mobil|Motor) (Reguler|Premium|Exclusive)', n_)
        for c, v in enumerate([str(ws.cell(row=r, column=c_id).value), n_, mm.group(1) if mm else '',
                               mm.group(2) if mm else '', 'ya' if str(ws.cell(row=r, column=c_id).value) in berubah_id else ''], 1):
            l3.cell(row=i, column=c, value=v)
    for col, wd in zip('ABCDE', (21, 100, 8, 11, 24)):
        l3.column_dimensions[col].width = wd
    for w_, ws_ in ((ls, (30, 38, 38, 20)), (l2, (21, 30, 11, 38, 38, 16))):
        for col, wd in zip('ABCDEF', ws_):
            w_.column_dimensions[col].width = wd
    lw.save(os.path.join(out_dir, 'LAPORAN_UPDATE_TAHUN_UA.xlsx'))
    return lap, siap, butuh, gagal


if __name__ == '__main__':
    lap, siap, butuh, gagal = main(*sys.argv[1:4])
    print(f'{len(lap)} produk deskripsinya berubah ({len({x[1] for x in lap})} model)')
    print(f'  siap upload (basic_information): {len(siap)} | butuh all_information (atribut Tahun kosong): '
          f'{sum(1 for x in lap if x[5] != "siap")} berubah, {len(butuh)} total gagal di file hasil')
