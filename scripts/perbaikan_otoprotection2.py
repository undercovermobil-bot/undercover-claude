# -*- coding: utf-8 -*-
"""
Lanjutan `perbaikan_otoprotection.py`: isi SKU yang MASIH kosong / masih pakai
kode toko legacy "OTP", untuk kasus yang sekarang punya bukti kuat (bukan
tebakan) -- baik lewat SIBLING LISTING di dalam file OP itu sendiri, maupun
lewat kode yang sudah diverifikasi terpakai di Undercover (MEREK-MODEL
bersifat universal lintas toko, cuma segmen toko yang beda per aturan #1).

Sumber tiap kode WAJIB dicatat di KODE_BARU/KODE_SIBLING supaya bisa diaudit --
lihat komentar per baris.

Yang TETAP TIDAK disentuh (genuinely tidak ada presedennya di toko mana pun,
dicek 2026-07-11/07-15 dan sekarang): Hummer H3, Toyota FJ Cruiser, Lexus RZ,
"Custom tambah pengikat velg" (bukan model mobil). Juga varian catch-all
"Tahun Lain"/"Model Lain/Custom" model multi-generasi (Nissan Latio) --
aturan #4, tidak boleh ditebak generasinya. Dan listing Transparan model
multi-generasi yang barisnya cuma py 1 variant polos tanpa keterangan generasi
(Hyundai Santa Fe, Lexus NX/RX, Mercedes Benz GLA, Mitsubishi Delica) --
ambigu generasi mana yang dimaksud.

Pemakaian:
  python3 perbaikan_otoprotection2.py <folder_out> <folder_listing...>
"""
import sys, os, re, glob, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH
import samakan_sku_smartprotection as SK

ORANGE = PatternFill('solid', fgColor='FFC000')
MASTERFMT = re.compile(r'^[A-Z0-9]+-[A-Z0-9]+-SP-[RSPET]-[A-Z0-9]+-[A-Z0-9]+$')
ATRIBUT_TIKTOK_WAJIB = {'product_property/100530': '2026', 'product_property/102755': '16:9'}

# --- A. kode MEREK-MODEL baru, diverifikasi lewat kode yang SUDAH dipakai di
# export Undercover (dicek 2026-09-09, "beda katalog UA vs SP") -----------
KODE_BARU = {
    'bmw seri 7':            'BMW-S7',
    'hyundai kona':          'HYN-KON',
    'mg zs crossover':       'MG-ZC',
    'geely ex2':             'GEL-EX2',
    'dfsk glory i-auto':     'DFSK-GI',
    'dfsk glory i auto':     'DFSK-GI',
    'lamborghini aventador': 'LAM-AVE',
    'mitsubishi l300':       'MTB-LP',
    'mini cooper':           'MNI-COO',
    # kembar: Taft GT pakai kode Feroza (preseden 2026-08, sudah diterapkan
    # jg di Otonation) -- chassis-nya F70/F300 SAMA PERSIS milik Feroza.
    'daihatsu taft gt':      'DHT-FRZ',
    # Corolla generasi lama (1966-1983) blm py kode -- generasi asli TOYOTA
    # (bukan Total-Formula collapse), aman pakai literal Gen N->GN spt gen
    # 9-12 yg sudah ada. Kode sudah ada (bukan baru), tapi ekstraksi generasi
    # via clean_gen() -- jalur yg sama dgn model KODE_BARU lain.
    'toyota corolla':        'TYT-CRL',
}

# --- B. sibling code (SUDAH ada di file OP itu sendiri, untuk listing yg
# blank tapi py KODE model yg SAMA dgn listing lain -- 0 tebakan sama sekali,
# tinggal generasi tunggalnya dipastikan) ----------------------------------
SIBLING_GEN_TUNGGAL = {
    'daihatsu espass': ('DHT-ESP', 'G1'), 'ford fusion': ('FRD-FUS', 'G1'),
    'hyundai grand i10': ('HYN-I10', 'G1F'), 'kia sedona': ('KIA-SED', 'G1'),
    'lexus lx': ('LEX-LX', 'G1'), 'mazda cx9': ('MZD-CX9', 'G1'),
    'mercedes benz b class': ('MBZ-BCL', 'G2'), 'mercedes benz cls class': ('MBZ-CLS', 'G1'),
    'mercedes benz g class': ('MBZ-GCL', 'G1'), 'mitsubishi eclipse': ('MTB-ECL', 'G3'),
    'nissan cedric': ('NSN-CED', 'G1'), 'peugeot 3008': ('PEU-M3008', 'G1'),
    'peugeot 306': ('PEU-M306', 'F2'), 'timor': ('TIM-TIM', 'G1'),
    'toyota 86': ('TYT-G86', 'G1'), 'toyota crown': ('TYT-CRO', 'G1'),
    'volkswagen fox': ('VLK-FOX', 'G1'), 'volkswagen passat': ('VLK-PAS', 'B5'),
    'volkswagen kombi': ('VLK-KOM', 'G1'), 'mitsubishi l300': ('MTB-LP', 'G1'),
    'mazda cx30': ('MZD-CX30', 'G1'), 'mazda cx-30': ('MZD-CX30', 'G1'),
}

DOOR_MINI = [(re.compile(r'3\s*pintu', re.I), '3P'), (re.compile(r'5\s*pintu', re.I), '5P')]


def clean_gen(var):
    """'Gen 3 : Zenix'/'Gen 4 (2019-2026)'/'Gen 2'  ->  'G3'/'G4'/'G2' (literal)"""
    m = re.search(r'\bgen\s*(\d+)\s*(f)?\b', var, re.I)
    if not m:
        return None
    return f"G{m.group(1)}{'F' if m.group(2) else ''}"


def kode_dan_gen(nm, var):
    """-> (kode, gen) atau (None, None) kalau tidak yakin -- TIDAK PERNAH menebak"""
    low = nm.lower()
    if 'mini cooper' in low:
        for rx, kd in DOOR_MINI:
            if rx.search(var):
                return 'MNI-COO', kd
        return None, None                       # body-type tanpa jumlah pintu eksplisit
    for kw, kode in KODE_BARU.items():
        if kw in low:
            if kode == 'DHT-FRZ':                # Taft GT: chassis F70/F300 dari teks
                m = re.search(r'\bF\d{2,3}\b', var, re.I)
                return kode, (m.group(0).upper() if m else None)
            g = clean_gen(var)
            return kode, (g or 'G1')             # semua model KODE_BARU lain: TF diverifikasi 1
    for kw, (kode, gen) in SIBLING_GEN_TUNGGAL.items():
        if kw in low:
            return kode, gen
    return None, None


def segmen(nm, var, gen):
    low = nm.lower()
    if 'transparan' in low:
        return 'T', gen, 'TRP'
    warna, kat = SK.segmen_warna(var, False)
    if not warna:
        return None, None, None
    return kat, gen, warna


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        d = ws_d.cell(row=r_d, column=c)
        d.value = s.value
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def proses(out_dir, folders):
    os.makedirs(out_dir, exist_ok=True)
    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    per_channel = {}
    lap = Counter()
    lewat = Counter()

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
        if wsv.max_row < start:
            continue

        pid_c = None; i_atr = {}
        if ch == 'tiktok':
            h = {str(wsv.cell(row=1, column=c).value).strip().lower(): c
                 for c in range(1, wsv.max_column + 1)}
            pid_c = h.get('product_id')
            for nmp in ATRIBUT_TIKTOK_WAJIB:
                if nmp in h:
                    i_atr[nmp] = h[nmp]

        terpakai = defaultdict(set)
        if ch == 'lazada':
            for r in range(start, wsv.max_row + 1):
                s = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
                nm = str(wsv.cell(row=r, column=col['nama']).value or '')
                if s and not SK.AUTO_LAZADA.match(s):
                    terpakai[nm].add(s)

        ubah = {}
        for r in range(start, wsv.max_row + 1):
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if not nm:
                continue
            lama = str(wsv.cell(row=r, column=col['sku']).value or '').strip()
            legacy = lama.startswith('CVR') and '-OTP-' in lama
            if lama and MASTERFMT.match(lama.split('_')[0]) and not legacy:
                continue                          # sudah format master benar -- skip di script ini

            var = str(wsv.cell(row=r, column=col['var']).value or '')
            kode, gen = kode_dan_gen(nm, var)
            if not kode or not gen:
                lewat[nm[:50]] += 1
                continue
            kat, gen2, warna = segmen(nm, var, gen)
            if not kat:
                lewat[nm[:50]] += 1
                continue
            sku_baru = f'{kode}-SP-{kat}-{gen2}-{warna}'
            if sku_baru == lama:
                continue
            if ch == 'lazada':
                dasar = sku_baru; i = 2
                while sku_baru in terpakai[nm]:
                    sku_baru = f'{dasar}_G{i}'; i += 1
                terpakai[nm].add(sku_baru)

            atr_baru = {}
            if ch == 'tiktok':
                for nmp, idx in i_atr.items():
                    if wsv.cell(row=r, column=idx).value in (None, ''):
                        atr_baru[idx] = ATRIBUT_TIKTOK_WAJIB[nmp]

            ubah[r] = (sku_baru, atr_baru)
            lap[(ch, 'legacy->baru' if legacy else 'isi kosong')] += 1

        if not ubah:
            continue

        for r, (s, atr) in ubah.items():
            sel = ws.cell(row=r, column=col['sku']); sel.value = s; sel.fill = ORANGE
            for idx, val in atr.items():
                sel = ws.cell(row=r, column=idx); sel.value = val; sel.fill = ORANGE

        if ch == 'tiktok' and pid_c:
            produk = {str(wsv.cell(row=r, column=pid_c).value) for r in ubah}
            simpan = [r for r in range(start, wsv.max_row + 1)
                      if wsv.cell(row=r, column=col['nama']).value
                      and str(wsv.cell(row=r, column=pid_c).value) in produk]
            lap[(ch, 'baris pelengkap')] += len(simpan) - len(ubah)
        else:
            simpan = sorted(ubah)

        n_kol = ws.max_column
        for i, r in enumerate(simpan):
            t = start + i
            if t != r:
                salin(ws, r, ws, t, n_kol)
        sisa = start + len(simpan)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(simpan))
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(simpan)):
                salin(ws, start + i, wso, r_out + i, n_kol)
            per_channel[ch] = (wo, wso, r_out + len(simpan))

    hasil = {}
    for ch, (wb_o, wso, r_out) in per_channel.items():
        out = os.path.join(out_dir, f'LANJUTAN_OTOPROTECTION_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = (out, r_out - UH.STARTROW[ch])
    return hasil, lap, lewat


if __name__ == '__main__':
    hasil, lap, lewat = proses(sys.argv[1], sys.argv[2:])
    print('=== ringkasan ===')
    for (ch, jenis), n in sorted(lap.items()):
        print(f'  {ch:8s} {jenis:16s} {n:5d}')
    print(f'\nmasih dilewati ({sum(lewat.values())} baris, genuinely tidak ada preseden):')
    for nm, n in lewat.most_common(20):
        print(f'   {n:4d}  {nm}')
    print()
    for ch, (p, n) in sorted(hasil.items()):
        print(f'[{ch:6s}] {n:5d} baris -> {os.path.basename(p)}')
