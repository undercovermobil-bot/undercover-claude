# -*- coding: utf-8 -*-
"""
Isi SKU yang masih KOSONG dan perbaiki yang masih FORMAT LAMA di listing UA
(Shopee/TikTok/Lazada). Baris yang SUDAH memakai format master TIDAK disentuh.

Prinsip: JANGAN mengarang kode. Tiap segmen harus punya sumber:
  MEREK-MODEL : dipelajari dari baris LAIN model yang sama yang SKU-nya sudah
                benar (lintas tier & lintas channel). Model yang belum pernah
                punya SKU di mana pun -> DILEWATI (itu gap master, perlu kode
                model baru yang cuma boleh diputuskan dari file master).
  TOKO        : UA (semua file di sini milik Undercover).
  KATEGORI    : dari tier di nama listing + jenis warna varian
                (Reguler+warna dasar=R, Reguler+warna strip=S, Premium=P,
                 Exclusive=E, Transparan=T).
  GENERASI    : dari `formula_config` kalau modelnya terdaftar di daftar
                referensi 213 model (itu sumber kebenarannya); kalau tidak,
                dipelajari dari baris saudara dengan teks generasi yang SAMA.
                Tidak ketemu dua-duanya -> DILEWATI.
  WARNA       : dari teks varian.

Aturan bisnis yang dihormati:
  - #4 varian generik ("Tahun Lain"/"Model Lain"/"Custom") SKU-nya sengaja
    dikosongkan -> dilewati, tidak ditebak.
  - #6 produk luar cakupan (karpet/cover motor/travel pouch) dikecualikan.
  - Lazada wajib SKU unik -> yang bentrok diberi akhiran `_G2`, `_G3`, ...
    mengikuti konvensi yang sudah dipakai di data mereka.

Pemakaian:
  python3 isi_sku_massal.py <file_formula.xlsx> <folder_out> <folder_listing...>
"""
import sys, os, glob, re, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import formula_config as FC
FORMULA_PATH = sys.argv[1]
FC.FORMULA_XLSX = FORMULA_PATH
FC.load.__defaults__ = (FORMULA_PATH,)

import update_harga_per_sku as UH
import apply_formula_sku as AF
import audit_sku_format_formula as AUD   # normalisasi_sku, AUTO_ID_LAZADA

CFG, BLOCKED = FC.load(FORMULA_PATH)
AF.CFG, AF.BLOCKED = CFG, BLOCKED
AF.CFG_SIG = {m: AF._sig(m) for m in CFG}
AF.CFG_TOK = {m: set(AF._toks(m)) for m in CFG}
AF.BLK_SIG = {m: AF._sig(m) for m in BLOCKED}
AF.BLK_TOK = {m: set(AF._toks(m)) for m in BLOCKED}
AF._cache = {}

MASTERFMT = AF.MASTERFMT
ORANGE = PatternFill('solid', fgColor='FFC000')

LUAR_SCOPE = ('karpet', 'cover motor', 'travel pouch', 'pouch')
# varian custom/aksesori: produk terpisah dgn kode sendiri -- JANGAN dibuatkan
# kode model baru otomatis, laporkan saja supaya diputuskan manusia
CUSTOM_RE = re.compile(r'\b(custom|roofbox|logo|bumper|spoiler|besi)\b', re.I)
# aturan bisnis #4 -- varian generik sengaja dibiarkan kosong
GENERIK = ('tahun lain', 'model lain', 'model/tahun lain', 'custom', 'lainnya')

WARNA_STRIP = {
    'elite abu': 'EAB', 'elite biru': 'EBR', 'elite merah': 'EMR',
    'epic abu': 'PAB', 'epic biru': 'PBR', 'epic merah': 'PMR',
    'warrior abu': 'WAB', 'warrior biru': 'WBR', 'warrior merah': 'WMR',
    'strip 1 abu': 'PAB', 'strip 1 biru': 'PBR', 'strip 1 merah': 'PMR',
    'strip 2 abu': 'EAB', 'strip 2 biru': 'EBR', 'strip 2 merah': 'EMR',
    'strip 3 abu': 'WAB', 'strip 3 biru': 'WBR', 'strip 3 merah': 'WMR',
    # salah ketik yang ada di data listing mereka sendiri
    'warior abu': 'WAB', 'warior biru': 'WBR', 'warior merah': 'WMR',
}
WARNA_DASAR = {
    'abu-abu': 'ABU', 'abu abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
    'merah': 'MRH', 'hijau army': 'GRN', 'silver': 'SLV', 'transparan': 'TRP',
}

TIER_RE = re.compile(r'\b(reguler|regular|premium|exclusive|transparan)\b', re.I)
BOIL_RE = re.compile(r'(undercover\s+aut[o]?care|undercover|autocare|autcare|'
                     r'body cover|cover mobil|selimut mobil|\bmobil\b|\bbody\b|/|-)', re.I)
SUFFIX_LZ = re.compile(r'_[A-Za-z0-9]+$')


def model_key(nm):
    s = BOIL_RE.sub(' ', TIER_RE.sub(' ', str(nm)))
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', s.lower()).split())


def gen_key(var):
    """teks generasi dari varian, dinormalkan -- dipakai utk belajar dari saudara"""
    v = str(var).lower()
    v = re.sub(r'\s+', ' ', v)
    bagian = [b.strip() for b in v.replace(';', ',').split(',')]
    sisa = []
    for b in bagian:
        if b in WARNA_STRIP or b in WARNA_DASAR:
            continue
        sisa.append(b)
    return ' '.join(sisa).strip()


def tier(nm):
    n = str(nm).lower()
    if 'transparan' in n:
        return 'T'
    if 'exclusive' in n:
        return 'E'
    if 'premium' in n:
        return 'P'
    return 'R'          # Reguler (bisa jadi S kalau warnanya strip)


def warna_dari(var):
    v = ' '.join(str(var).lower().replace(',', ' , ').split())
    for teks, kode in WARNA_STRIP.items():
        if teks in v:
            return kode, True
    for teks, kode in WARNA_DASAR.items():
        if teks in v:
            return kode, False
    return None, False


def perlu_diproses(sku):
    s = str(sku or '').strip()
    if not s or AUD.AUTO_ID_LAZADA.match(s):
        return True, 'kosong'
    if MASTERFMT.match(AUD.normalisasi_sku(s)):
        return False, None
    return True, 'format lama'


def baca_master(path):
    """master -> (model_key->prefix, (model_key,teks generasi)->kode generasi,
    nama sheet merek->kode merek, semua prefix yang sudah terpakai)"""
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True, read_only=True)
    m2p, mg2g, b2c, dipakai = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), set()
    for sn in wb.sheetnames:
        ws = wb[sn]
        mulai = False
        for row in ws.iter_rows(values_only=True):
            if not mulai:
                # Sheet Suzuki kolom A-nya KOSONG di baris header, jadi syarat
                # row[0]=='No' membuat seluruh sheet (3.372 baris) terlewat --
                # bug lama yang sudah pernah tercatat. Kenali dari 'Nama Produk'.
                if row and any(str(v).strip() == 'Nama Produk' for v in row if v):
                    mulai = True
                continue
            if not row or len(row) < 9:
                continue
            nama, generasi, sku = row[1], row[5], row[8]
            if not (nama and sku and isinstance(sku, str)):
                continue
            b = sku.strip().split('-')
            if len(b) < 6:
                continue
            pfx = f'{b[0]}-{b[1]}'
            mk = model_key(nama)
            m2p[mk][pfx] += 1
            b2c[sn][b[0]] += 1
            dipakai.add(pfx)
            if generasi:
                mg2g[(mk, str(generasi).strip().lower())][b[4]] += 1
    wb.close()
    return m2p, mg2g, {k: v.most_common(1)[0][0] for k, v in b2c.items()}, dipakai


STOPWORD_MODEL = {'plus', 'new', 'all', 'the'}


def kode_model_baru(nama_listing, brand_code, terpakai, brand_name=None):
    """buat kode MEREK-MODEL baru mengikuti konvensi master:
    - penanda alfanumerik dipertahankan (A6, QX80, 2008, BJ40)
    - "Seri N" -> SN
    - kata biasa -> singkatan 3 huruf
    Ditolak kalau bentrok dgn kode yang sudah ada."""
    nm = TIER_RE.sub(' ', BOIL_RE.sub(' ', str(nama_listing)))
    kata = [w for w in re.sub(r'[^A-Za-z0-9]+', ' ', nm).split()
            if w.lower() not in STOPWORD_MODEL]
    # buang nama merek di depan secara eksplisit (kode merek sudah mewakilinya).
    # Sebelumnya ditebak dari posisi kata, akibatnya "MG ZS" jadi MZ (inisial
    # merek+model) bukan ZS.
    if brand_name:
        bw = [w for w in re.sub(r'[^A-Za-z0-9]+', ' ', re.split(r'[(/]', brand_name)[0]).split()]
        while bw and kata and kata[0].lower() == bw[0].lower():
            kata = kata[1:]
            bw = bw[1:]
    if not kata:
        return None
    if len(kata) >= 2 and kata[0].lower() in ('seri', 'series'):
        kand = f'S{kata[1]}'
    else:
        idx = next((i for i, w in enumerate(kata) if any(c.isdigit() for c in w)), None)
        if idx is not None:
            tok = kata[idx].upper()
            if tok.isdigit() and idx > 0:
                # angka telanjang ("Ioniq 6", "EV 6", "Tiggo 9") tidak informatif
                # sendirian -- gabungkan dgn awalan kata sebelumnya
                kand = kata[idx - 1][:2].upper() + tok
            else:
                kand = tok
            # kata sesudah angka jadi pembeda ("720S Spider" -> 720SS)
            if idx + 1 < len(kata):
                kand += kata[idx + 1][0].upper()
        elif len(kata) >= 2:
            kand = ''.join(w[0] for w in kata[:3]).upper()
        else:
            w = kata[0]
            kons = [c for c in w[1:] if c.lower() not in 'aeiou']
            kand = (w[0] + ''.join(kons[:2])).upper() if len(kons) >= 2 else w[:3].upper()
    kand = re.sub(r'[^A-Z0-9]', '', kand.upper())[:5]
    if not kand:
        return None
    pfx = f'{brand_code}-{kand}'
    if pfx in terpakai:                      # cegah tabrakan dgn kode yang sudah ada
        for i in range(2, 9):
            alt = f'{brand_code}-{kand}{i}'
            if alt not in terpakai:
                return alt
        return None
    return pfx


def kumpulkan(folders):
    from openpyxl import load_workbook
    out = []
    for f in folders:
        for path in sorted(glob.glob(os.path.join(f, '*.xlsx'))):
            wb = load_workbook(path, data_only=True)
            ch = UH.deteksi_channel(wb)
            if ch is None:
                continue
            ws = UH.cari_sheet(wb, ch)
            col = UH.resolve_cols(ws, ch)
            for r in range(UH.STARTROW[ch], ws.max_row + 1):
                nm = ws.cell(row=r, column=col['nama']).value
                if not nm:
                    continue
                out.append((ch, path, r, str(nm),
                            str(ws.cell(row=r, column=col['var']).value or ''),
                            ws.cell(row=r, column=col['sku']).value))
    return out


def bangun_pengetahuan(rows):
    """pelajari prefix per model & kode generasi per (model, teks generasi)"""
    m2p = defaultdict(Counter)
    mg2g = defaultdict(Counter)
    for ch, path, r, nm, var, sku in rows:
        s = str(sku or '').strip()
        if not s:
            continue
        norm = AUD.normalisasi_sku(s)
        if not MASTERFMT.match(norm):
            continue
        b = norm.split('-')
        mk = model_key(nm)
        m2p[mk][f'{b[0]}-{b[1]}'] += 1
        mg2g[(mk, gen_key(var))][b[4]] += 1
    return m2p, mg2g


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        d = ws_d.cell(row=r_d, column=c, value=s.value)
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def baris_di_extra(extra_files):
    """(channel, nama listing, teks varian) yang sudah ditangani file perbaikan
    terpisah -- supaya tidak diisi DUA KALI (file khusus lebih presisi, mis.
    Mini Cooper yang sekalian mengoreksi segmen, bukan cuma mengisi kosong)"""
    from openpyxl import load_workbook
    kunci = set()
    for xf in extra_files:
        wb = load_workbook(xf, data_only=True)
        ch = UH.deteksi_channel(wb)
        if ch is None:
            continue
        ws = UH.cari_sheet(wb, ch)
        col = UH.resolve_cols(ws, ch)
        for r in range(UH.STARTROW[ch], ws.max_row + 1):
            nm = ws.cell(row=r, column=col['nama']).value
            if nm:
                kunci.add((ch, str(nm),
                           str(ws.cell(row=r, column=col['var']).value or '')))
    return kunci


def proses(out_dir, folders, extra_files=(), master_path=None):
    os.makedirs(out_dir, exist_ok=True)
    semua = kumpulkan(folders)
    m2p, mg2g = bangun_pengetahuan(semua)
    sudah_ditangani = baris_di_extra(extra_files)

    # MASTER = sumber kebenaran. Dipakai sbg cadangan utk model yang belum punya
    # SKU di listing manapun. Tidak menimpa yang sudah ada di listing, karena
    # baris yang sudah benar memang tidak boleh disentuh.
    mm_p, mm_g, brand2code, prefix_terpakai = ({}, {}, {}, set())
    if master_path:
        mm_p, mm_g, brand2code, prefix_terpakai = baca_master(master_path)
    prefix_terpakai = set(prefix_terpakai)
    for c in m2p.values():
        prefix_terpakai.update(c)

    # merek diurut dari yang paling panjang supaya "Mercedes-Benz" menang atas "MG"
    brand_urut = sorted(brand2code, key=len, reverse=True)

    def _rata(t):
        return ' '.join(re.sub(r'[^a-z0-9]+', ' ', str(t).lower()).split())

    def cari_brand_name(nm):
        low = _rata(nm)
        for b in brand_urut:
            inti = _rata(re.split(r'[(/]', b)[0])
            if inti and re.search(rf'(?<![a-z0-9]){re.escape(inti)}(?![a-z0-9])', low):
                return b
        return None

    def cari_brand_code(nm):
        b = cari_brand_name(nm)
        return brand2code[b] if b else None

    kode_baru = {}          # model_key -> prefix yang baru dibuat
    asal_kode = Counter()

    # Pra-pass: tentukan dulu SEMUA model yang butuh kode baru, lalu berikan
    # kodenya urut dari nama TERPENDEK. Tanpa ini urutan pemberian kode
    # bergantung urutan baris, sehingga varian bisa merebut kode dasar milik
    # model induknya (mis. "Mclaren 720S Spider" dapat MCL-720S, lalu
    # "Mclaren 720S" terpaksa jadi MCL-720S2).
    butuh = {}
    for ch0, p0, r0, nm0, var0, sku0 in semua:
        ya, _ = perlu_diproses(sku0)
        if not ya:
            continue
        low0 = nm0.lower()
        if any(k in low0 for k in LUAR_SCOPE) or CUSTOM_RE.search(nm0):
            continue
        mk0 = model_key(nm0)
        if mk0 in m2p or mk0 in mm_p:
            continue
        butuh.setdefault(mk0, nm0)
    for mk0 in sorted(butuh, key=lambda k: (len(k.split()), len(k), k)):
        bc0 = cari_brand_code(butuh[mk0])
        if not bc0:
            continue
        pfx0 = kode_model_baru(butuh[mk0], bc0, prefix_terpakai, cari_brand_name(butuh[mk0]))
        if pfx0:
            kode_baru[mk0] = pfx0
            prefix_terpakai.add(pfx0)

    rencana = defaultdict(list)      # path -> [(row, sku_baru, alasan)]
    lewat = Counter()
    contoh_lewat = defaultdict(Counter)
    terpakai_lz = defaultdict(set)

    for ch, path, r, nm, var, sku in semua:
        s = str(sku or '').strip()
        if ch == 'lazada' and s:
            terpakai_lz[(path, nm)].add(s)

    for ch, path, r, nm, var, sku in semua:
        proses_ini, jenis = perlu_diproses(sku)
        if not proses_ini:
            continue
        if (ch, nm, var) in sudah_ditangani:
            continue          # ditangani file perbaikan terpisah
        low = nm.lower()
        if any(k in low for k in LUAR_SCOPE):
            lewat['produk luar cakupan'] += 1
            continue
        if any(k in str(var).lower() for k in GENERIK):
            # Aturan #4 melarang MENEBAK generasi utk varian generik. Tapi kalau
            # modelnya cuma punya SATU formula (collapse), tidak ada yang perlu
            # ditebak -- semua generasi memang satu kode. Preseden: eksekusi
            # 2026-08-14 (`isi_catchall_kosong.py` mode only_listed) yang mengisi
            # 217 baris catch-all persis dengan syarat ini.
            ref0, tag0 = AF.match_model(nm)
            aman = bool(ref0 and tag0 == 'ok'
                        and ref0 not in getattr(FC, 'DIKECUALIKAN', {})
                        and CFG[ref0]['collapse'])
            if not aman:
                lewat['varian generik, model >1 formula (tidak boleh ditebak)'] += 1
                continue

        mk = model_key(nm)
        kand = m2p.get(mk)
        sumber = 'listing'
        if not kand and mk in mm_p:          # 2) cari di MASTER
            kand = mm_p[mk]
            sumber = 'master'
        if not kand and mk in kode_baru:     # 3) kode baru yang sudah dibuat tadi
            kand = Counter({kode_baru[mk]: 1})
            sumber = 'kode baru'
        if not kand and CUSTOM_RE.search(nm):
            lewat['varian custom/aksesori (perlu kode sendiri, diputuskan manual)'] += 1
            contoh_lewat['custom'][nm] += 1
            continue
        if not kand:                         # 4) belum ada di mana pun -> buat kode baru
            bc = cari_brand_code(nm)
            pfx_baru = kode_model_baru(nm, bc, prefix_terpakai, cari_brand_name(nm)) if bc else None
            if not pfx_baru:
                lewat['merek tidak dikenal / kode baru gagal dibuat'] += 1
                contoh_lewat['tanpa kode'][nm] += 1
                continue
            kode_baru[mk] = pfx_baru
            prefix_terpakai.add(pfx_baru)
            kand = Counter({pfx_baru: 1})
            sumber = 'kode baru'
        if len(kand) > 1:
            # ambigu (mis. mobil kembar) -> pakai yg dipakai di listing ini sendiri
            lokal = Counter()
            for ch2, p2, r2, nm2, var2, sku2 in semua:
                if nm2 == nm and sku2:
                    n2 = AUD.normalisasi_sku(str(sku2).strip())
                    if MASTERFMT.match(n2):
                        b2 = n2.split('-')
                        lokal[f'{b2[0]}-{b2[1]}'] += 1
            if len(lokal) == 1:
                pfx = next(iter(lokal))
            else:
                lewat['prefix ambigu (mobil kembar)'] += 1
                contoh_lewat['ambigu'][nm] += 1
                continue
        else:
            pfx = next(iter(kand))
        asal_kode[sumber] += 1

        warna, is_strip = warna_dari(var)
        kat = tier(nm)
        if kat == 'R' and is_strip:
            kat = 'S'
        if kat == 'E':
            warna = warna or 'ABU'
        if kat == 'T':
            warna = 'TRP'
        if not warna:
            lewat['warna tidak terbaca dari teks varian'] += 1
            contoh_lewat['warna'][f'{nm[:40]} | {var[:30]}'] += 1
            continue

        # GENERASI: formula dulu (sumber kebenaran), baru belajar dari saudara
        gen = None
        model_ref, tag = AF.match_model(nm)
        if model_ref and tag == 'ok' and model_ref not in getattr(FC, 'DIKECUALIKAN', {}):
            gen = FC.seg_for_variant(CFG[model_ref], var)
        if not gen:
            c = mg2g.get((mk, gen_key(var)))
            if c and len(c) == 1:
                gen = next(iter(c))
        if not gen and mm_g:                  # dari MASTER (kolom Generasi)
            gk = gen_key(var)
            for (mk2, g2), cc in mm_g.items():
                if mk2 == mk and g2 and (g2 in gk or gk.startswith(g2)):
                    if len(cc) == 1:
                        gen = next(iter(cc))
                        break
        if not gen:
            # model di luar daftar 213 & tidak ada di master: pakai nomor
            # generasi yang tertulis di varian apa adanya
            mg = re.search(r'gen\s*([0-9]+)', var, re.I)
            if mg:
                gen = f'G{mg.group(1)}'
            else:
                # sebagian model Eropa memakai kode sasis sbg generasi
                # (Audi B5/B9, BMW E39, Mercedes W203) -- dipakai apa adanya,
                # konsisten dgn cara master menuliskannya
                ms = re.search(r'(?<![A-Za-z0-9])([A-Z]{1,2}\d{1,3})(?![A-Za-z0-9])', var)
                if ms:
                    gen = ms.group(1).upper()
        if not gen:
            lewat['kode generasi tak bisa ditentukan'] += 1
            contoh_lewat['generasi'][f'{nm[:40]} | {var[:30]}'] += 1
            continue

        baru = f'{pfx}-UA-{kat}-{gen}-{warna}'
        if ch == 'lazada':
            dipakai = terpakai_lz[(path, nm)]
            if baru in dipakai:
                i = 2
                while f'{baru}_G{i}' in dipakai:
                    i += 1
                baru = f'{baru}_G{i}'
            dipakai.discard(s)
            dipakai.add(baru)
        rencana[path].append((r, baru, jenis))

    # tulis file hasil
    per_channel = {}
    hasil_laporan = Counter()
    for path, items in rencana.items():
        wb = openpyxl.load_workbook(path, data_only=False)
        ch = UH.deteksi_channel(wb)
        ws = UH.cari_sheet(wb, ch)
        wbv = openpyxl.load_workbook(path, data_only=True)
        col = UH.resolve_cols(UH.cari_sheet(wbv, ch), ch)
        start = UH.STARTROW[ch]

        items.sort()
        for r, baru, jenis in items:
            sel = ws.cell(row=r, column=col['sku'])
            sel.value = baru
            sel.fill = ORANGE
            hasil_laporan[(ch, jenis)] += 1

        n_kol = ws.max_column
        baris = [it[0] for it in items]
        for i, r in enumerate(baris):
            t = start + i
            if t != r:
                salin(ws, r, ws, t, n_kol)
        sisa = start + len(baris)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(baris), col)
        else:
            wo, wso, r_out, col0 = per_channel[ch]
            for i in range(len(baris)):
                salin(ws, start + i, wso, r_out + i, n_kol)
            per_channel[ch] = (wo, wso, r_out + len(baris), col0)

    # gabungkan file perbaikan lain (mis. Mini Cooper) ke output channel yg sama
    for xf in extra_files:
        wbx = openpyxl.load_workbook(xf, data_only=False)
        chx = UH.deteksi_channel(wbx)
        wsx = UH.cari_sheet(wbx, chx)
        colx = UH.resolve_cols(UH.cari_sheet(openpyxl.load_workbook(xf, data_only=True), chx), chx)
        startx = UH.STARTROW[chx]
        n_x = 0
        if chx not in per_channel:
            per_channel[chx] = (wbx, wsx, startx, colx)
            n_x = wsx.max_row - startx + 1
        else:
            wo, wso, r_out, col0 = per_channel[chx]
            n_kol = wso.max_column
            for r in range(startx, wsx.max_row + 1):
                if not wsx.cell(row=r, column=colx['nama']).value:
                    continue
                salin(wsx, r, wso, r_out + n_x, n_kol)
                n_x += 1
            per_channel[chx] = (wo, wso, r_out + n_x, col0)
        hasil_laporan[(chx, 'gabungan Mini Cooper')] += n_x

    hasil = {}
    for ch, (wb_o, _, _, _) in per_channel.items():
        out = os.path.join(out_dir, f'SIAP_UPLOAD_SKU_UA_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, hasil_laporan, lewat, contoh_lewat, kode_baru, asal_kode


if __name__ == '__main__':
    out_dir = sys.argv[2]
    args = sys.argv[3:]
    folders = [a for a in args if os.path.isdir(a)]
    extra = [a for a in args if os.path.isfile(a)]

    master = None
    for a in list(extra):
        low = os.path.basename(a).lower()
        if 'master' in low or 'tracking' in low:
            master = a
            extra.remove(a)
    hasil, laporan, lewat, contoh, kode_baru, asal = proses(out_dir, folders, extra, master)

    print('=== DIISI / DIPERBAIKI ===')
    for (ch, jenis), n in sorted(laporan.items()):
        print(f'  {ch:7s} {jenis:28s} {n:5,}')
    print(f'  TOTAL {sum(laporan.values()):,}')

    print('\n=== ASAL KODE MEREK-MODEL ===')
    for k, n in asal.most_common():
        print(f'  {n:6,}  {k}')
    if kode_baru:
        print(f'\n=== KODE MODEL BARU DIBUAT: {len(kode_baru)} ===')
        for mk, pfx in sorted(kode_baru.items(), key=lambda x: x[1]):
            print(f'  {pfx:14s} <- {mk[:52]}')

    print('\n=== DILEWATI (beserta alasannya) ===')
    for alasan, n in lewat.most_common():
        print(f'  {n:6,}  {alasan}')

    for kunci, judul in [('gap master', 'Model tanpa SKU di mana pun (perlu kode model baru di master)'),
                         ('generasi', 'Kode generasi tak bisa ditentukan'),
                         ('warna', 'Warna tak terbaca'),
                         ('ambigu', 'Prefix ambigu')]:
        c = contoh.get(kunci)
        if c:
            print(f'\n  {judul} -- contoh terbanyak:')
            for nm, n in c.most_common(8):
                print(f'    {n:4d}x {nm[:74]}')

    print()
    for ch, p in sorted(hasil.items()):
        print(f'[{ch}] -> {os.path.basename(p)}')
