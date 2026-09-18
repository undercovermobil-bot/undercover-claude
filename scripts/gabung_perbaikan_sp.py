# -*- coding: utf-8 -*-
"""
Satu file upload per channel untuk Smartprotection, berisi SEMUA perbaikan
sekaligus: kode SKU + harga.

Kenapa digabung: file update marketplace menimpa SEMUA kolom yang ada di
dalamnya. Kalau perbaikan SKU dan perbaikan harga dikirim sebagai dua file,
upload yang belakangan akan mengembalikan kolom yang sudah dibetulkan file
sebelumnya (pelajaran 2026-08-15).

Isi perbaikan:
  1. SKU  -- lihat `samakan_sku_smartprotection.py` (ganti prefix + isi kosong)
  2. Harga A -- 18 baris TikTok yang tertinggal karena typo teks varian,
     disamakan ke harga modus model+tier-nya
  3. Harga B -- dua kode yang satu SKU-nya dipakai dua listing dengan harga
     berbeda; angka final ditentukan user 2026-09-10:
        DHT-GMX (Luxio + Gran Max Minibus) -> R 371.000 / S 414.000
        TYT-AVZ (Avanza + Xenia + Veloz)   -> R 370.000 / S 413.000

DHT-FRZ (Feroza vs Daihatsu Rocky, selisih Rp46.000) SENGAJA TIDAK disentuh --
belum ada keputusan angka dari user.

Pemakaian:
  python3 gabung_perbaikan_sp.py <folder_out> <folder_listing...>
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

HARGA_TETAP = {                      # keputusan user 2026-09-10
    'DHT-GMX': {'R': 371000, 'S': 414000},
    'TYT-AVZ': {'R': 370000, 'S': 413000},
}
# Normalisasi "samakan ke harga modus" HANYA untuk model yang memang disepakati
# (7 model kelompok C -- baris yang tertinggal karena typo teks varian).
#
# JANGAN dibalik jadi daftar-pengecualian: begitu sebuah model baru dapat SKU,
# baris-barisnya tiba-tiba masuk grup (kode, tier) dan ikut "dinormalkan" tanpa
# pernah diminta. Terbukti 2026-09-10: Hyundai Getz Shopee mau diubah
# 322rb->365rb dan Chery Omoda 5 Lazada 413rb->415rb, dua-duanya di luar
# permintaan user.
NORMALKAN_KE_MODUS = {
    'ISZ-PTH',   # Isuzu Panther      "Biru Benhru"
    'MTB-OUT',   # Mitsubishi Outlander
    'TYT-STR',   # Toyota Starlet
    'TYT-VOX',   # Toyota Voxy
    'SZK-CIA',   # Suzuki Ciaz        "Eltie Merah"
    'TYT-CMY',   # Toyota Camry       "Eltie Biru"
    'DTN-DGP',   # Datsun Go Plus     "Wrior Merah"
}


def prefix_tier(sku):
    b = str(sku or '').strip().split('_')[0].split('-')
    if len(b) < 6 or b[3] not in ('R', 'S'):
        return None, None
    return '-'.join(b[:2]), b[3]


def modus_harga(berkas):
    """harga yang dipakai MAYORITAS baris per (kode model, tier)"""
    m = defaultdict(Counter)
    for path in berkas:
        wb = openpyxl.load_workbook(path, data_only=True)
        ch = UH.deteksi_channel(wb)
        if ch is None:
            wb.close()
            continue
        ws = UH.cari_sheet(wb, ch)
        col = UH.resolve_cols(ws, ch)
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

        pid_c = None
        if ch == 'tiktok':
            h = {str(wsv.cell(row=1, column=c).value).strip().lower(): c
                 for c in range(1, wsv.max_column + 1)}
            pid_c = h['product_id']

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

            # --- 1. SKU ---
            b = lama.split('-')
            if len(b) >= 6 and b[0] + '-' + b[1] in SK.GANTI:
                k = SK.GANTI[b[0] + '-' + b[1]]
                sku_baru = '-'.join([k.split('-')[0], k.split('-')[1]] + b[2:])
            else:
                kode = SK.kode_untuk(nm)
                if kode:
                    if lama and not SK.AUTO_LAZADA.match(lama) and SK.MASTERFMT.match(lama):
                        inti = lama.split('_')[0]
                        if not inti.startswith(kode + '-'):
                            sku_baru = '-'.join([kode.split('-')[0], kode.split('-')[1]]
                                                + inti.split('-')[2:])
                    else:
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

            # --- 2. harga (pakai SKU FINAL supaya kode baru ikut dipertimbangkan) ---
            pfx, kat = prefix_tier(sku_baru or lama)
            harga_baru = None
            if pfx:
                try:
                    cur = int(float(wsv.cell(row=r, column=col['harga']).value))
                except (TypeError, ValueError):
                    cur = None
                if cur is not None:
                    if pfx in HARGA_TETAP:
                        mau = HARGA_TETAP[pfx][kat]
                    elif pfx in NORMALKAN_KE_MODUS:
                        mau = modus.get((pfx, kat), cur)
                    else:
                        mau = cur
                    if mau != cur:
                        harga_baru = mau

            if sku_baru or harga_baru:
                ubah[r] = (sku_baru, harga_baru)
                if sku_baru:
                    lap[(ch, 'SKU')] += 1
                if harga_baru:
                    lap[(ch, 'harga')] += 1

        if not ubah:
            continue

        for r, (s, h) in ubah.items():
            if s:
                sel = ws.cell(row=r, column=col['sku'])
                sel.value = s
                sel.fill = ORANGE
            if h:
                sel = ws.cell(row=r, column=col['harga'])
                sel.value = h
                sel.fill = ORANGE

        # TikTok: template all_information -> tiap produk harus lengkap variannya
        if ch == 'tiktok':
            produk = {str(wsv.cell(row=r, column=pid_c).value) for r in ubah}
            simpan = [r for r in range(start, wsv.max_row + 1)
                      if wsv.cell(row=r, column=col['nama']).value
                      and str(wsv.cell(row=r, column=pid_c).value) in produk]
            lap[(ch, 'baris pelengkap')] = len(simpan) - len(ubah)
        else:
            simpan = sorted(ubah)

        n_kol = ws.max_column
        for i, r in enumerate(simpan):
            t = start + i
            if t != r:
                for c in range(1, n_kol + 1):
                    s = ws.cell(row=r, column=c)
                    d = ws.cell(row=t, column=c)
                    d.value = s.value
                    d.fill = copy.copy(s.fill)
                    d.number_format = s.number_format
        sisa = start + len(simpan)
        if sisa <= ws.max_row:
            ws.delete_rows(sisa, ws.max_row - sisa + 1)

        if ch not in per_channel:
            per_channel[ch] = (wb, ws, start + len(simpan))
        else:
            wo, wso, r_out = per_channel[ch]
            for i in range(len(simpan)):
                for c in range(1, n_kol + 1):
                    s = ws.cell(row=start + i, column=c)
                    d = wso.cell(row=r_out + i, column=c)
                    d.value = s.value
                    d.fill = copy.copy(s.fill)
                    d.number_format = s.number_format
            per_channel[ch] = (wo, wso, r_out + len(simpan))

    hasil = {}
    for ch, (wb_o, wso, r_out) in per_channel.items():
        out = os.path.join(out_dir, f'PERBAIKAN_SP_{ch.upper()}.xlsx')
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
