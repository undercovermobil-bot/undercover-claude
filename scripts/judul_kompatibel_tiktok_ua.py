# -*- coding: utf-8 -*-
"""
Judul TikTok Undercover Autocare sesuai aturan TikTok Shop "Produk yang
Kompatibel" (Seller University, 19/08/2026): merek mobil/motor tidak boleh
menempel langsung ke jenis produk; wajib kata penghubung
("untuk" / "kompatibel dengan" / "cocok untuk" / "digunakan untuk").

Format (pilihan user 2026-10-26: pola A + ekor kata kunci, penghubung "untuk"):
  Cover Mobil {Tipe} untuk {Merek Model} - Undercover Autocare - Body Cover Selimut Sarung Mobil {Atribut}
  Cover Motor {Tipe} untuk {Merek Model} - Undercover Autocare - Body Cover Selimut Sarung Motor {Atribut}
Atribut per tipe, dari klaim deskripsi toko sendiri:
  Reguler  : air 70%, UV 100%, lebih bagus indoor  -> "Anti UV Indoor" (motor: "Anti UV")
  Premium  : air >90%, 3 lapis, outdoor            -> "Waterproof 3 Lapis"
  Exclusive: air >95%, 4 lapis, outdoor            -> "Waterproof 4 Lapis"
Penanda "(J)" di judul lama dipertahankan di ujung judul.

Sekalian:
  - kolom Merek yang diisi merek lain (Daihatsu, TRK) -> Undercover Autocare
  - deskripsi "Untuk Order Cover Mobil {Model} Model Lain" -> "... Cover Mobil untuk {Model} ..."
Produk lain (custom semua merek, cairan, karpet, pouch) tidak disentuh.

Pemakaian: python3 judul_kompatibel_tiktok_ua.py <basic_information.xlsx> <out.xlsx> <laporan.xlsx>
(file input sudah lewat repair_xlsx.py)
"""
import sys, re, copy, openpyxl
from openpyxl.styles import PatternFill, Font

ORANGE = PatternFill('solid', fgColor='FFC000')
TOKO = 'Undercover Autocare'
MEREK_UA = 'Undercover Autocare (7398062051938748165)'
ATRIBUT = {
    ('Mobil', 'Reguler'): 'Anti UV Indoor',
    ('Mobil', 'Premium'): 'Waterproof 3 Lapis',
    ('Mobil', 'Exclusive'): 'Waterproof 4 Lapis',
    ('Motor', 'Reguler'): 'Anti UV',
    ('Motor', 'Premium'): 'Waterproof 3 Lapis',
    ('Motor', 'Exclusive'): 'Waterproof 4 Lapis',
}
# judul lama "Body Cover Motor / Sarung / Selimut Motor {X}" tanpa merek pabrikan
# (semua tipe Reguler menurut deskripsinya); Maxi dibiarkan tanpa merek (ambigu)
PABRIKAN_MOTOR = {'Vario': 'Honda Vario', 'NMAX': 'Yamaha NMAX', 'Supra X': 'Honda Supra X',
                  'PCX': 'Honda PCX', 'Beat': 'Honda Beat', 'Aerox': 'Yamaha Aerox',
                  'Scoopy': 'Honda Scoopy', 'Vega': 'Yamaha Vega', 'Maxi': 'Maxi'}

# model di judul lama yang tidak menyebut merek pabrikan
TAMBAH_MEREK = {'WRV': 'Honda WRV', 'CRF1100L Africa Twin': 'Honda CRF1100L Africa Twin'}

RE_STANDAR = re.compile(r'^(?:Body\s+)?Cover (Mobil|Motor) (.+?) (Reguler|Premium|Exclusive)\s*(?:-\s*.*)?$')
RE_UA_DEPAN = re.compile(r'^Undercover Autocare - Cover (Mobil|Motor) (.+?) (Reguler|Premium|Exclusive)$')
RE_MOTOR_LAMA = re.compile(r'^Body Cover Motor / Sarung / Selimut Motor (.+)$')
RE_DESK = re.compile(r'(Untuk Order Cover (?:Mobil|Motor)) (?!untuk )')


def urai(nama):
    """-> (jenis, model, tipe, suffix) atau None"""
    n = re.sub(r'\s+', ' ', str(nama or '')).strip()
    if 'Custom Semua Merek' in n:
        return None
    suffix = ' (J)' if re.search(r'\(J\)?\s*$', n) else ''
    n2 = re.sub(r'\s*\(J\)?\s*$', '', n)
    m = RE_UA_DEPAN.match(n2) or RE_STANDAR.match(n2)
    if m:
        model = m.group(2).strip()
        return m.group(1), TAMBAH_MEREK.get(model, model), m.group(3), suffix
    m = RE_MOTOR_LAMA.match(n2)
    if m and m.group(1).strip() in PABRIKAN_MOTOR:
        return 'Motor', PABRIKAN_MOTOR[m.group(1).strip()], 'Reguler', suffix
    return None


def judul(jenis, model, tipe, suffix):
    return (f'Cover {jenis} {tipe} untuk {model} - {TOKO} - Body Cover Selimut Sarung {jenis} '
            f'{ATRIBUT[(jenis, tipe)]}{suffix}')


def main(src, out, lap_out):
    wb = openpyxl.load_workbook(src)
    ws = wb['Template']
    h = {str(ws.cell(row=1, column=c).value): c for c in range(1, ws.max_column + 1)}
    c_nama, c_desk, c_merek = h['product_name'], h['product_description'], h['brand']
    lap, simpan = [], []
    for r in range(6, ws.max_row + 1):
        pid = ws.cell(row=r, column=1).value
        if not pid:
            continue
        lama = str(ws.cell(row=r, column=c_nama).value or '').strip()
        hasil = urai(lama)
        catat = []
        ubah = False
        if hasil:
            baru = judul(*hasil)
            sel = ws.cell(row=r, column=c_nama); sel.value = baru; sel.fill = ORANGE
            ubah = True
            if RE_MOTOR_LAMA.match(lama):
                catat.append('judul lama tanpa merek pabrikan')
            d = str(ws.cell(row=r, column=c_desk).value or '')
            d2, k = RE_DESK.subn(r'\1 untuk ', d)
            if k:
                sel = ws.cell(row=r, column=c_desk); sel.value = d2; sel.fill = ORANGE
                catat.append(f'deskripsi: {k} frasa "Model Lain" diberi "untuk"')
            merek = str(ws.cell(row=r, column=c_merek).value or '')
            if merek and merek != MEREK_UA:
                sel = ws.cell(row=r, column=c_merek); sel.value = MEREK_UA; sel.fill = ORANGE
                catat.append(f'merek "{merek.split(" (")[0]}" -> Undercover Autocare')
        else:
            baru = ''
            catat.append('tidak diubah (bukan cover per model)')
        lap.append((str(pid), lama, baru, len(baru) if baru else None, '; '.join(catat)))
        if ubah:
            simpan.append(r)
    # rapatkan baris yang diubah, buang sisanya
    n_kol = ws.max_column
    for i, r in enumerate(simpan):
        t = 6 + i
        if t != r:
            for c in range(1, n_kol + 1):
                s, d = ws.cell(row=r, column=c), ws.cell(row=t, column=c)
                d.value = s.value
                d.fill = copy.copy(s.fill)
    sisa = 6 + len(simpan)
    if sisa <= ws.max_row:
        ws.delete_rows(sisa, ws.max_row - sisa + 1)
    wb.save(out)
    lw = openpyxl.Workbook(); ls = lw.active; ls.title = 'Judul Baru'
    for c, v in enumerate(['ID Produk', 'Judul Lama', 'Judul Baru', 'Panjang', 'Catatan'], 1):
        ls.cell(row=1, column=c, value=v).font = Font(bold=True)
    for i, x in enumerate(lap, 2):
        for c, v in enumerate(x, 1):
            ls.cell(row=i, column=c, value=v)
    for col, wd in zip('ABCDE', (21, 65, 110, 9, 55)):
        ls.column_dimensions[col].width = wd
    ls.freeze_panes = 'A2'
    lw.save(lap_out)
    return lap, len(simpan)


if __name__ == '__main__':
    lap, n = main(*sys.argv[1:4])
    ok = [x for x in lap if x[2]]
    print(f'{n} produk diubah, {len(lap) - n} tidak diubah')
    print(f'panjang judul {min(x[3] for x in ok)}-{max(x[3] for x in ok)}, >120: {sum(x[3] > 120 for x in ok)}, >255: {sum(x[3] > 255 for x in ok)}')
