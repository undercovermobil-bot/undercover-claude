# -*- coding: utf-8 -*-
"""
SALINAN VERBATIM dari branch `claude/repo-memory-access-4hthja`
(scripts/update_harga_per_sku.py) - dibawa masuk 2026-08-20, TIDAK diubah,
supaya PREFIX{}/ALIAS{}/is_outdoor_polos() dst tetap identik dgn yang sudah
diverifikasi ke data OT sebenarnya. Dipakai (bukan dijalankan __main__-nya)
oleh cek_harga_otonation.py untuk verifikasi read-only.
"""
"""
Update harga listing e-commerce (Shopee/TikTok/Lazada) berdasarkan PREFIX SKU,
bukan nama listing.

Kenapa berbasis SKU: beberapa model beda nama memakai cover yang SAMA PERSIS,
jadi SKU-nya identik -> stoknya satu barang -> harganya WAJIB satu angka.
Contoh terverifikasi di UA:
    TYT-RSH = Toyota Rush + Daihatsu Terios
    TYT-CLY = Toyota Calya + Daihatsu Sigra
    TYT-AVZ = Toyota Avanza + Daihatsu Xenia + Toyota Veloz
    DHT-AYL = Daihatsu Ayla + Toyota Agya
Pencocokan lewat nama listing (`update_harga_listing.py`, dipakai utk produk
1-10) akan MELEWATKAN pasangan seperti ini. Versi ini menyapu semua baris yang
prefix SKU-nya sama, jadi kembaran ikut otomatis.

Efek samping yg diinginkan: prefix SKU juga otomatis memisahkan model yg namanya
mirip tapi produknya beda -- Yaris (TYT-YRS) tidak menyeret Yaris Cross
(TYT-YRC) atau GR Yaris (TYT-GRY); Civic (HND-CVC) tidak menyeret Civic
Hatchback (HND-CVH) atau Civic Type R (HND-CTR).

Hanya tier REGULER yg disentuh (segmen ke-4 SKU: R = warna dasar, S = strip
Elite/Epic/Warrior). Premium (P), Exclusive (E), Transparan (T) tidak ikut,
karena harga HPP yg jadi dasar perhitungan memang tier Reguler.

Pemakaian:
  python3 update_harga_per_sku.py <file_harga.xlsx> <no_awal> <no_akhir> \
      <folder_out> <nama_toko> <folder_listing...>
"""
import sys, os, glob, copy
import openpyxl
from openpyxl.styles import PatternFill

ORANGE = PatternFill('solid', fgColor='FFC000')

# selisih harga tier Strip (Elite/Epic/Warrior) thd Reguler -- flat semua produk.
# Direvisi user 2026-08-15 dari Rp56.000 jadi Rp43.000.
TAMBAHAN_STRIP = 43000

# Kolom dicari lewat NAMA header di baris 1 (bukan nomor kolom tetap) --
# terbukti perlu 2026-08-18: TikTok mengirim varian template baru
# ("sales_information", kolom lebih sedikit) yg nomor kolomnya beda total dari
# varian lama ("all_information") yg dipakai sebelumnya, walau nama field di
# header r1 tetap sama. Kalau nomor kolom di-hardcode, ganti varian template =
# harga salah sasaran tanpa ketahuan.
SHEET = {'shopee': 'Sheet1', 'tiktok': 'Template', 'lazada': 'template'}
STARTROW = {'shopee': 7, 'tiktok': 6, 'lazada': 5}
HEADER_KEY = {
    'shopee': {'nama': 'et_title_product_name', 'var': 'et_title_variation_name',
               'sku': 'et_title_variation_sku', 'harga': 'et_title_variation_price'},
    'tiktok': {'nama': 'product_name', 'var': 'variation_value',
               'sku': 'seller_sku', 'harga': 'price'},
    'lazada': {'nama': 'nama produk', 'var': 'variations combo',
               'sku': 'seller sku', 'harga': 'harga'},
}

# Nama produk di file harga -> prefix SKU (2 segmen pertama: MEREK-MODEL).
# Diverifikasi langsung ke data listing (UA dan/atau OT), bukan tebakan. Kalau
# menambah produk baru WAJIB isi di sini -- script sengaja berhenti kalau ada
# yg belum terdaftar, supaya tidak diam-diam melewatkan produk.
#
# Produk 21-100 diverifikasi 2026-08-18 dari data OTONATION (OT) saat
# memproses batch harga toko itu -- prefix yg sama berlaku lintas toko krn
# desain SKU (`-UA-` di segmen ke-3 dipakai bersama semua toko, lihat
# project-undercover-otonation-status.md).
#
# Kasus yg BUKAN pemetaan langsung (perlu keputusan, dicatat di
# project-undercover-harga-referensi.md):
# - Toyota Hilux -> TYT-HLX (base) SAJA, BUKAN TYT-HLR (Hilux Rangga = produk
#   master terpisah, generasi sendiri, tidak termasuk top-100 ini).
# - Daihatsu Rocky -> TYT-RZE (kembar modern Toyota Raize, 2019-2026, harga di
#   file SAMA PERSIS dgn Raize: Rp336rb/379rb -- bukan kebetulan, memang 1
#   SKU). SKU F70/F300 (Rocky klasik 1984-2002, DHT-FRZ, kembar Feroza) sudah
#   otomatis kebagian harga lewat entri 'Daihatsu Feroza' sendiri -- tidak
#   perlu entri terpisah.
# - Toyota HiAce -> TYT-HAC (varian "Commuter") SAJA. Varian "Premio" (prefix
#   TYT-HAL, kemungkinan "HiAce Long") SENGAJA TIDAK disentuh -- beda dari
#   kasus Rush/Terios/Calya/Sigra (rebadge identik, kembar SEHARUSNYA sama
#   harga), Commuter vs Premio/Long bisa jadi beda ukuran fisik asli, harga
#   file cuma py 1 baris "Toyota HiAce" tanpa keterangan. Perlu konfirmasi
#   user kalau mau Premio ikut disamakan.
PREFIX = {
    'Toyota Avanza':                       'TYT-AVZ',
    'Honda Brio Satya / RS':               'HND-BRI',
    'Toyota Innova':                       'TYT-INV',
    'Honda Jazz':                          'HND-JAZ',
    'Suzuki Ertiga':                       'SZK-ERT',
    'Honda HR-V / e:N1':                   'HND-HRV',
    'Toyota Agya':                         'DHT-AYL',
    'Daihatsu Ayla':                       'DHT-AYL',
    'Daihatsu Xenia':                      'TYT-AVZ',
    'Nissan Livina / Grand Livina':        'NSN-LVN',
    'Toyota Vios':                         'TYT-VIS',
    'Toyota Fortuner':                     'TYT-FTN',
    'Honda BR-V':                          'HND-BRV',
    'Toyota Calya':                        'TYT-CLY',
    'Toyota Rush':                         'TYT-RSH',
    'Toyota Yaris':                        'TYT-YRS',
    'Toyota Kijang':                       'TYT-KJG',
    'Honda CR-V':                          'HND-CRV',
    'Honda Mobilio':                       'HND-MBL',
    'Honda Civic':                         'HND-CVC',
    'Daihatsu Terios':                     'TYT-RSH',
    'Mitsubishi Xpander':                  'MTB-XPN',
    'Toyota Camry':                        'TYT-CMY',
    'Honda Accord':                        'HND-ACD',
    'Toyota Corolla':                      'TYT-CRL',
    'Suzuki APV Arena / Blind Van':        'SZK-APV',
    'Toyota Raize':                        'TYT-RZE',
    'Isuzu Panther':                       'ISZ-PTH',
    'Mitsubishi Pajero Sport':             'MTB-PJS',
    'Daihatsu Sigra':                      'TYT-CLY',
    'Suzuki Baleno':                       'SZK-BLN',
    'Suzuki Fronx':                        'SZK-FRX',
    'Honda Freed':                         'HND-FRD',
    'Toyota Hilux':                        'TYT-HLX',
    'Suzuki Swift':                        'SZK-SWF',
    'Suzuki Karimun':                      'SZK-KRM',
    'Mitsubishi Triton':                   'MTB-TRN',
    'Honda City Sedan':                    'HND-CTY',
    'Suzuki XL7':                          'SZK-XL7',
    'Nissan March':                        'NSN-MCH',
    'Toyota HiAce':                        'TYT-HAC',
    'Mazda 2 Sedan':                       'MZD-2S',
    'Toyota Hardtop':                      'TYT-HTP',
    'Suzuki Jimny':                        'SZK-JMN',
    'Suzuki Ignis':                        'SZK-IGN',
    'BMW Seri 3':                          'BMW-S3',
    'Kia Picanto':                         'KIA-PIC',
    'Daihatsu Sirion':                     'DHT-SRN',
    'Daihatsu Feroza':                     'DHT-FRZ',
    'Toyota Veloz':                        'TYT-AVZ',
    'Toyota Alphard':                      'TYT-ALP',
    'Toyota Starlet':                      'TYT-STR',
    'Daihatsu Luxio':                      'DHT-LXO',
    'Toyota Etios Valco':                  'TYT-ETV',
    'Honda WR-V':                          'HND-WRV',
    'Suzuki Splash':                       'SZK-SPL',
    'Daihatsu Gran Max Pick Up':           'DHT-GMXP',
    'Daihatsu Rocky':                      'TYT-RZE',
    'Nissan Juke':                         'NSN-JUK',
    'Toyota Vellfire':                     'TYT-ALP',
    'Ford Fiesta':                         'FRD-FIE',
    'MINI Cooper':                         'MNI-COO',
    'Toyota Land Cruiser':                 'TYT-LCR',
    'Honda Odyssey':                       'HND-ODY',
    'Toyota Voxy':                         'TYT-VOX',
    'Mercedes Benz E Class':               'MBZ-ECL',
    'Suzuki Carry':                        'SZK-CAR',
    'Nissan Evalia':                       'NSN-EVA',
    'Mitsubishi Mitsubishi Kuda':          'MTB-KUD',
    'Nissan X-Trail':                      'NSN-XTR',
    'Suzuki SX4':                          'SZK-SX4',
    'Daihatsu Taruna':                     'DHT-TAR',
    'Mitsubishi Mitsubishi Xpander Cross': 'MTB-XPC',
    'Toyota Sienta':                       'TYT-SNT',
    'Mitsubishi Mitsubishi Destinator':    'MTB-DST',
    'Honda City Hatchback RS':             'HND-CHB',
    'Datsun Go Plus':                      'DTN-DGP',
    'BYD Atto 1':                          'BYD-AT1',
    'Nissan Terrano':                      'NSN-TER',
    'Hyundai Creta':                       'HYN-CRT',
    'Mitsubishi Mirage':                   'MTB-MIR',
    'Mercedes Benz S Class':               'MBZ-SS',
    'Hyundai Stargazer':                   'HYN-SGZ',
    'Chevrolet Spin':                      'CHV-SPN',
    'Mazda CX5':                           'MZD-CX5',
    'Wuling Air EV':                       'WLG-AEV',
    'BMW Seri 5':                          'BMW-S5',
    'Toyota Harrier':                      'TYT-HAR',
    'Wuling Almaz':                        'WLG-ALM',
    'Mercedes Benz C Class':               'MBZ-CC',
    'Kia Rio Sedan':                       'KIA-RS',
    'Suzuki S-Presso':                     'SZK-SPR',
    'Datsun Go':                           'DTN-DGO',
    'Toyota Soluna':                       'TYT-SOL',
    'Mitsubishi Mitsubishi Outlander':     'MTB-OUT',
    'Suzuki Aerio Hatchback':              'SZK-ARH',
    'Hyundai Palisade':                    'HYN-PLS',
    'Timor':                               'TIM-TIM',
    'Mazda 2 Hatchback':                   'MZD-MZ2',
    'Wuling Confero':                      'WLG-CNF',
}

# Prefix SKU yg BELUM sinkron ke master, dipetakan ke prefix induknya supaya
# mobil kembar tetap ikut naik harga walau SKU-nya masih beda antar channel.
# Terverifikasi 2026-08-18: Lazada belum ikut konsolidasi SKU kembar, dan TikTok
# baru sebagian (Agya & Xenia punya DUA prefix sekaligus di sana).
#   Sigra  DHT-SGR (Lazada)        <- TYT-CLY (Shopee/TikTok)
#   Terios DHT-TRS (Lazada)        <- TYT-RSH (Shopee/TikTok)
#   Veloz  TYT-VLZ (Lazada)        <- TYT-AVZ (Shopee/TikTok)
#   Xenia  DHT-XNA (Lazada+TikTok) <- TYT-AVZ (Shopee)
#   Agya   TYT-AGY (Lazada+TikTok) <- DHT-AYL (Shopee)
# Ini TAMBALAN harga, bukan perbaikan SKU -- konsolidasi SKU-nya perlu dikerjakan
# terpisah di proyek SKU Sync.
ALIAS = {
    'DHT-SGR': 'TYT-CLY',
    'DHT-TRS': 'TYT-RSH',
    'TYT-VLZ': 'TYT-AVZ',
    'DHT-XNA': 'TYT-AVZ',
    'TYT-AGY': 'DHT-AYL',
    # 2026-08-26: Daihatsu Taft GT belum ikut migrasi SKU kembar ke DHT-FRZ di
    # listing Shopee UA (masih pakai prefix lama DHT-TG) - diverifikasi
    # langsung ke listing riil. Rocky lawas (F70/F300) SUDAH DHT-FRZ, jadi
    # tidak perlu alias. Feroza sendiri prefix aslinya memang DHT-FRZ.
    'DHT-TG': 'DHT-FRZ',
}

# Listing yg namanya mengandung ini TIDAK ikut walau prefix SKU-nya sama --
# produk terpisah dgn harga sendiri. Terverifikasi: "Nissan Grand Livina Custom
# Roofbox Reguler" memakai prefix NSN-LVN yg sama dgn Livina biasa, tapi
# harganya Rp352.000 vs Rp385.000. Batch 11-20 tidak punya kasus begini
# (sudah dicek), tapi penjaganya tetap dipasang utk batch berikutnya.
KECUALI = ('x-gear', 'xgear', 'custom', 'roofbox')


def is_outdoor_polos(nm):
    """True kalau listing OT kategori 'Outdoor' POLOS (bukan Semi/Extreme/
    Indoor dan Outdoor). Dikonfirmasi user 2026-08-19: 'Outdoor' polos di OT
    setara tier PREMIUM UA, BUKAN Reguler -- 'Semi Outdoor' yg setara Reguler.
    31 baris ditemukan dgn segmen SKU R/S (harusnya P) tapi harga SUDAH benar
    Premium (Rp700rb-1.06jt) -- SKU-nya salah tag, bukan harganya yg salah.
    Guard ini nyegah baris begini ketimpa harga Reguler/Strip walau SKU-nya
    (keliru) bilang R/S."""
    low = ' '.join(str(nm or '').lower().split())
    if 'outdoor' not in low:
        return False
    return not any(k in low for k in ('semi outdoor', 'extreme outdoor', 'indoor dan outdoor'))


KAT_KE_JENIS = {'R': 'reguler', 'S': 'strip'}


def deteksi_channel(wb):
    n = set(s.lower() for s in wb.sheetnames)
    if 'sheet1' in n:
        return 'shopee'
    # 'template_hide' unik dipunyai Lazada -- dicek SEBELUM fallback 'template'
    # generik krn TikTok jg py sheet bernama 'Template' (beda kapital, tp
    # dibandingkan case-insensitive di sini jadi bisa bentrok kalau salah urutan)
    if 'template_hide' in n:
        return 'lazada'
    if 'saleplatform' in n or 'templateconfig' in n or ('template' in n and 'brand' in n):
        return 'tiktok'
    if 'template' in n:
        return 'lazada'
    return None


def cari_sheet(wb, ch):
    t = SHEET[ch]
    return wb[t] if t in wb.sheetnames else wb[wb.sheetnames[0]]


def resolve_cols(ws, ch):
    """cari nomor kolom lewat nama header di baris 1, bukan nomor tetap"""
    want = HEADER_KEY[ch]
    idx = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=1, column=c).value
        if not v:
            continue
        vs = str(v).strip().lower()
        for key, target in want.items():
            if vs == target:
                idx[key] = c
    hilang = [k for k in want if k not in idx]
    if hilang:
        raise SystemExit(f'[{ch}] kolom header tidak ketemu utk: {hilang} '
                          f'-- template mungkin berubah lagi, cek HEADER_KEY')
    return idx


def urai_sku(sku):
    """SKU MEREK-MODEL-TOKO-KAT-GEN-WARNA -> (prefix, kategori)"""
    if not sku or not isinstance(sku, str):
        return None, None
    b = sku.strip().split('-')
    if len(b) < 6:
        return None, None
    return '-'.join(b[:2]).upper(), b[3].upper()


def baca_harga(path, no_awal, no_akhir):
    """ambil harga produk bernomor no_awal..no_akhir -> {prefix: {...}}"""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Harga Baru']
    target = {}
    belum_terdaftar = []
    for r in range(2, ws.max_row + 1):
        no = ws.cell(row=r, column=1).value
        nm = ws.cell(row=r, column=2).value
        if not isinstance(no, int) or not (no_awal <= no <= no_akhir):
            continue
        if nm not in PREFIX:
            belum_terdaftar.append((no, nm))
            continue
        reg = int(ws.cell(row=r, column=7).value)
        pfx = PREFIX[nm]
        # harga strip selalu diturunkan dari reguler + TAMBAHAN_STRIP supaya tidak
        # pernah ada dua angka yg saling bertentangan kalau selisihnya direvisi
        info = {'reguler': reg, 'strip': reg + TAMBAHAN_STRIP, 'label': f'{no} {nm}'}
        if pfx in target and target[pfx]['reguler'] != reg:
            print(f'  ! BENTROK {pfx}: {target[pfx]["label"]} Rp{target[pfx]["reguler"]:,} '
                  f'vs {info["label"]} Rp{reg:,} -- pakai yg pertama')
            continue
        target.setdefault(pfx, info)
    if belum_terdaftar:
        print('PRODUK BELUM PUNYA PREFIX SKU di PREFIX{} -- lengkapi dulu:')
        for no, nm in belum_terdaftar:
            print(f'   #{no} {nm}')
        raise SystemExit(1)
    return target


def salin(ws_s, r_s, ws_d, r_d, n_kol):
    for c in range(1, n_kol + 1):
        s = ws_s.cell(row=r_s, column=c)
        d = ws_d.cell(row=r_d, column=c, value=s.value)
        d.fill = copy.copy(s.fill)
        d.number_format = s.number_format


def proses(target, out_dir, folders, nama_toko='UA'):
    os.makedirs(out_dir, exist_ok=True)
    per_channel = {}
    laporan = {}
    kena_model = {}

    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))

    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=False)
        ch = deteksi_channel(wb)
        if ch is None:
            continue
        ws = cari_sheet(wb, ch)
        wbv = openpyxl.load_workbook(path, data_only=True)
        wsv = cari_sheet(wbv, ch)
        col = resolve_cols(wsv, ch)
        start = STARTROW[ch]

        ubah = []
        for r in range(start, wsv.max_row + 1):
            pfx, kat = urai_sku(wsv.cell(row=r, column=col['sku']).value)
            pfx = ALIAS.get(pfx, pfx)
            if pfx not in target:
                continue
            nm = str(wsv.cell(row=r, column=col['nama']).value or '')
            if any(k in nm.lower() for k in KECUALI):
                continue
            if is_outdoor_polos(nm):
                continue
            jenis = KAT_KE_JENIS.get(kat)
            if not jenis:
                continue  # Premium/Exclusive/Transparan -> jangan disentuh
            baru = target[pfx][jenis]
            lama = wsv.cell(row=r, column=col['harga']).value
            try:
                if lama is not None and int(float(lama)) == baru:
                    continue  # sudah benar, tidak perlu ikut file update
            except (TypeError, ValueError):
                pass
            ubah.append((r, baru))
            kena_model.setdefault(target[pfx]['label'], {}).setdefault(nm, 0)
            kena_model[target[pfx]['label']][nm] += 1
            laporan.setdefault(ch, []).append((target[pfx]['label'], jenis, lama, baru))

        if not ubah:
            continue

        for r, baru in ubah:
            sel = ws.cell(row=r, column=col['harga'])
            sel.value = baru
            sel.fill = ORANGE

        n_kol = ws.max_column
        baris = [u[0] for u in ubah]
        for i, r in enumerate(baris):
            t = start + i
            if t != r:
                salin(ws, r, ws, t, n_kol)
        sisa = start + len(baris)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(baris))
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(baris)):
                salin(ws, start + i, wso, r_out + i, n_kol)
            per_channel[ch] = (wo, wso, r_out + len(baris))

    hasil = {}
    for ch, (wb_o, _, _) in per_channel.items():
        out = os.path.join(out_dir, f'UPDATE_HARGA_{nama_toko}_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = out
    return hasil, laporan, kena_model


if __name__ == '__main__':
    path_harga = sys.argv[1]
    no_awal, no_akhir = int(sys.argv[2]), int(sys.argv[3])
    out_dir = sys.argv[4]
    nama_toko = sys.argv[5]
    folders = sys.argv[6:]

    target = baca_harga(path_harga, no_awal, no_akhir)
    print(f'Target produk #{no_awal}-{no_akhir} ({len(target)} prefix SKU):')
    for pfx, v in sorted(target.items(), key=lambda x: int(x[1]['label'].split()[0])):
        print(f'  {v["label"]:26s} [{pfx}]  reguler Rp{v["reguler"]:,}  strip Rp{v["strip"]:,}')

    hasil, laporan, kena_model = proses(target, out_dir, folders, nama_toko)

    print('\n=== Listing yang kena (per produk) ===')
    for label in sorted(kena_model, key=lambda x: int(x.split()[0])):
        print(f'  {label}')
        for nm, n in sorted(kena_model[label].items()):
            print(f'      {n:4d} baris  {nm}')

    print()
    for ch in ['shopee', 'tiktok', 'lazada']:
        if ch not in laporan:
            print(f'[{ch}] tidak ada baris yg perlu diubah')
            continue
        rows = laporan[ch]
        print(f'[{ch}] {len(rows)} baris -> {os.path.basename(hasil[ch])}')
        ringkas = {}
        for label, jenis, lama, baru in rows:
            k = (label, jenis)
            ringkas.setdefault(k, [0, lama, baru])
            ringkas[k][0] += 1
        for (label, jenis), (n, lama, baru) in sorted(ringkas.items(), key=lambda x: (int(x[0][0].split()[0]), x[0][1])):
            try:
                s_lama = f'Rp{int(float(lama)):,}'
            except (TypeError, ValueError):
                s_lama = f'{lama!r}'
            print(f'    {label:26s} {jenis:8s} {n:4d} baris  {s_lama:>12s} -> Rp{baru:,}')
