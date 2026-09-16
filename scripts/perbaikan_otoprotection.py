# -*- coding: utf-8 -*-
"""
Perbaikan SKU + harga untuk Otoprotection (OP), sekali jalan gabung ke satu file
per channel (aturan sama: file SKU dan file harga tidak boleh dikirim terpisah,
lihat lesson 2026-08-15).

OP berbagi segmen toko "SP" dengan Smartprotection (aturan konsolidasi #1),
jadi kode MEREK-MODEL yang sudah dipastikan benar di SP (`samakan_sku_
smartprotection.kode_untuk` / `segmen_warna`) dipakai APA ADANYA di sini --
bukan ditebak ulang.

Yang DIKERJAKAN (aman, tidak butuh keputusan baru):
  1. Isi SKU kosong utk 7 model yang kodenya sudah dipastikan lewat kerja SP
     (BYD Seal, Chery Omoda 5, Feroza Long, Ford Ranger, Hyundai Getz,
     Mazda CX-7, Suzuki APV Luxury) + pisah Avega Hatchback (HYN-AVH) dari
     Avega Sedan (HYN-AVG) -- keduanya sudah py listing terpisah by NAMA,
     tinggal diarahkan ke kode yang benar (logic sama seperti gabung_
     perbaikan_sp.py: kode_untuk(nm) dipakai sbg OVERRIDE juga utk baris yg
     SKU-nya sudah format master tapi prefix-nya salah, bukan cuma utk kosong).
  2. HARGA_TETAP -- keputusan harga yang SUDAH diambil user utk SP (DHT-GMX,
     TYT-AVZ), diterapkan sama persis di OP krn sumber datanya satu (matriks
     SP-OP yang sama). TYT-COR (Toyota Corona) ditambah baru: Shopee vs
     TikTok Strip beda 50/50, jadi butuh target eksplisit, bukan modus.
  3. NORMALKAN_KE_MODUS -- baris nyasar krn duplikat listing/typo (Toyota
     Altis meniru harga lama Corolla G9, Nissan Latio 2 baris Orange
     kepasang harga Strip, Mazda 3 Sedan 1 baris "Biru Binhur" typo) --
     disamakan ke harga MAYORITAS baris lain di kode+kategori yang sama.

Yang SENGAJA TIDAK disentuh (dilaporkan, bukan ditebak):
  - DHT-FRZ (Feroza 370rb vs Daihatsu Rocky 324rb) -- sama seperti SP, masih
    menunggu keputusan user.
  - 730 baris SKU kosong utk model yang kodenya BELUM ada presedennya di SP
    (BMW Seri 7, Hyundai Kona, MG ZS Crossover, Mini Cooper, Geely EX2, DFSK
    Glory i-Auto, Lamborghini Aventador, Mitsubishi L300, Corolla Gen 1-4) --
    butuh master/keputusan user.
  - 14 baris SKU legacy kode toko "OTP" (CVR####-OTP-*) -- mayoritas model
    yang sama sekali belum py target harga (skema lama/tidak ada di matriks).
  - 12 model masih skema harga lama (selisih Strip-Reguler 30rb/40rb/60rb,
    bukan 43rb) -- menunggu Pcs/Roll seperti di SP.

Khusus TikTok: dua atribut wajib (Tahun=2026, 102755=16:9) diisi utk SETIAP
baris produk yang disentuh, mengikuti keputusan user 2026-09-11 di SP --
0 dari baris target yang sudah py atribut ini terisi, jadi WAJIB diisi supaya
tidak kena error "atribut produk is missing" seperti kasus SP.

Pemakaian:
  python3 perbaikan_otoprotection.py <folder_out> <folder_listing...>
"""
import sys, os, glob, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH
import samakan_sku_smartprotection as SK

ORANGE = PatternFill('solid', fgColor='FFC000')

HARGA_TETAP = {
    'DHT-GMX': {'R': 371000, 'S': 414000},   # sda keputusan user 2026-09-10 (SP)
    'TYT-AVZ': {'R': 370000, 'S': 413000},   # sda
    'TYT-COR': {'R': 371000, 'S': 414000},   # Toyota Corona: Shopee benar, TikTok stale
}
NORMALKAN_KE_MODUS = {'TYT-CRL', 'NSN-LAT', 'MZD-3S'}
ATRIBUT_TIKTOK_WAJIB = {'product_property/100530': '2026', 'product_property/102755': '16:9'}


def prefix_tier(sku):
    b = str(sku or '').strip().split('_')[0].split('-')
    if len(b) < 6 or b[3] not in ('R', 'S'):
        return None, None
    return '-'.join(b[:2]), b[3]


def modus_harga(berkas):
    m = defaultdict(Counter)
    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=True)
        ch = UH.deteksi_channel(wb)
        if ch is None:
            wb.close(); continue
        ws = UH.cari_sheet(wb, ch); col = UH.resolve_cols(ws, ch)
        for r in range(UH.STARTROW[ch], ws.max_row + 1):
            if not ws.cell(row=r, column=col['nama']).value:
                continue
            pfx, kat = prefix_tier(ws.cell(row=r, column=col['sku']).value)
            if not pfx:
                continue
            try:
                m[(pfx, kat)][int(float(ws.cell(row=r, column=col['harga']).value))] += 1
            except (TypeError, ValueError):
                pass
        wb.close()
    return {k: v.most_common(1)[0][0] for k, v in m.items()}


def proses(out_dir, folders):
    os.makedirs(out_dir, exist_ok=True)
    berkas = []
    for f in folders:
        berkas.extend(sorted(glob.glob(os.path.join(f, '*.xlsx'))))
    modus = modus_harga(berkas)

    per_channel = {}
    lap = Counter()

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
        if wsv.max_row < start:      # file placeholder kosong (TT_2)
            continue

        pid_c = None
        i_atr = {}
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
            sku_baru = None

            kode = SK.kode_untuk(nm)
            if kode:
                if lama and not SK.AUTO_LAZADA.match(lama) and SK.MASTERFMT.match(lama.split('_')[0]):
                    inti = lama.split('_')[0]
                    if not inti.startswith(kode + '-'):
                        sku_baru = '-'.join([kode.split('-')[0], kode.split('-')[1]]
                                            + inti.split('-')[2:])
                elif not lama:
                    var = str(wsv.cell(row=r, column=col['var']).value or '')
                    warna, kat = SK.segmen_warna(var, 'transparan' in nm.lower())
                    if warna:
                        gen = SK.GEN_KHUSUS.get(kode, 'G1')
                        sku_baru = f'{kode}-SP-{kat}-{gen}-{warna}'
            if sku_baru == lama:
                sku_baru = None
            if sku_baru and ch == 'lazada':
                dasar = sku_baru
                i = 2
                while sku_baru in terpakai[nm]:
                    sku_baru = f'{dasar}_G{i}'
                    i += 1
                terpakai[nm].add(sku_baru)

            pfx, kat = prefix_tier(sku_baru or lama)
            harga_baru = None
            if pfx:
                try:
                    cur = int(float(wsv.cell(row=r, column=col['harga']).value))
                except (TypeError, ValueError):
                    cur = None
                if cur is not None:
                    if pfx in HARGA_TETAP and kat in HARGA_TETAP[pfx]:
                        mau = HARGA_TETAP[pfx][kat]
                    elif pfx in NORMALKAN_KE_MODUS:
                        mau = modus.get((pfx, kat), cur)
                    else:
                        mau = cur
                    if mau != cur:
                        harga_baru = mau

            atr_baru = {}
            if ch == 'tiktok' and (sku_baru or harga_baru):
                for nmp, idx in i_atr.items():
                    if wsv.cell(row=r, column=idx).value in (None, ''):
                        atr_baru[idx] = ATRIBUT_TIKTOK_WAJIB[nmp]

            if sku_baru or harga_baru or atr_baru:
                ubah[r] = (sku_baru, harga_baru, atr_baru)
                if sku_baru:
                    lap[(ch, 'SKU')] += 1
                if harga_baru:
                    lap[(ch, 'harga')] += 1

        if not ubah:
            continue

        for r, (s, h, atr) in ubah.items():
            if s:
                sel = ws.cell(row=r, column=col['sku']); sel.value = s; sel.fill = ORANGE
            if h:
                sel = ws.cell(row=r, column=col['harga']); sel.value = h; sel.fill = ORANGE
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
                for c in range(1, n_kol + 1):
                    s = ws.cell(row=r, column=c); d = ws.cell(row=t, column=c)
                    d.value = s.value; d.fill = copy.copy(s.fill); d.number_format = s.number_format
        sisa = start + len(simpan)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(simpan))
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(simpan)):
                for c in range(1, n_kol + 1):
                    s = ws.cell(row=start + i, column=c); d = wso.cell(row=r_out + i, column=c)
                    d.value = s.value; d.fill = copy.copy(s.fill); d.number_format = s.number_format
            per_channel[ch] = (wo, wso, r_out + len(simpan))

    hasil = {}
    for ch, (wb_o, wso, r_out) in per_channel.items():
        out = os.path.join(out_dir, f'PERBAIKAN_OTOPROTECTION_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = (out, r_out - UH.STARTROW[ch])
    return hasil, lap


if __name__ == '__main__':
    hasil, lap = proses(sys.argv[1], sys.argv[2:])
    print('=== ringkasan perubahan ===')
    for (ch, jenis), n in sorted(lap.items()):
        print(f'  {ch:8s} {jenis:18s} {n:5d}')
    print()
    for ch, (p, n) in sorted(hasil.items()):
        print(f'[{ch:6s}] {n:5d} baris -> {os.path.basename(p)}')
