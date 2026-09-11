# -*- coding: utf-8 -*-
"""
Gabungan `perbaikan_otoprotection.py` + `perbaikan_otoprotection2.py` jadi
SATU pass. Wajib begini (bukan digabung belakangan dgn `gabung_file_upload.py`)
krn ada produk TikTok yang kena SEKALIGUS oleh dua aturan (mis. Toyota
Corolla: harga G9/Altis dibetulkan oleh aturan pertama, SKU kosong Gen 1-4
diisi oleh aturan kedua) -- kalau diproses 2x terpisah lalu digabung,
completeness-pass TikTok masing-masing bakal menghasilkan baris duplikat yang
NILAINYA BEDA (salah satu versi lama). Satu pass, satu keputusan per baris.
"""
import sys, os, re, glob, copy, warnings
from collections import defaultdict, Counter

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import PatternFill

import update_harga_per_sku as UH
import samakan_sku_smartprotection as SK
import perbaikan_otoprotection as OP1
import perbaikan_otoprotection2 as OP2

ORANGE = PatternFill('solid', fgColor='FFC000')

RE_MERCEDES_MODEL = re.compile(r'mercedes\s*benz\s+(.+)$', re.I)


def hitung_atribut(nm, wsv, r, i_atr):
    """Atribut wajib TikTok utk 1 baris: 2 nilai TETAP (Tahun/aspect-ratio,
    dari OP1.ATRIBUT_TIKTOK_WAJIB) + 1 nilai DINAMIS khusus brand Mercedes-
    Benz (Model, 100177 -- ditemukan lewat produk Mercedes lain yg sudah
    lolos: nilainya persis teks setelah "Mercedes Benz " di nama produk,
    mis. "B Class"/"CLS Class"/"GLE Class"). Cuma isi yg masih kosong.
    """
    atr = {}
    for nmp, idx in i_atr.items():
        if nmp == 'product_property/100177':
            continue
        if wsv.cell(row=r, column=idx).value in (None, ''):
            atr[idx] = OP1.ATRIBUT_TIKTOK_WAJIB[nmp]
    idx177 = i_atr.get('product_property/100177')
    if idx177 and wsv.cell(row=r, column=idx177).value in (None, ''):
        m = RE_MERCEDES_MODEL.search(nm)
        if m:
            atr[idx177] = m.group(1).strip()
    return atr


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
    modus = OP1.modus_harga(berkas)

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
            for nmp in list(OP1.ATRIBUT_TIKTOK_WAJIB) + ['product_property/100177']:
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
            var = str(wsv.cell(row=r, column=col['var']).value or '')
            sku_baru = None

            # --- ATURAN 1 (perbaikan_otoprotection.py): kode_untuk override,
            # isi-kosong 7 model SP, atau format sudah master tapi prefix salah
            kode1 = SK.kode_untuk(nm)
            if kode1:
                if lama and not SK.AUTO_LAZADA.match(lama) and SK.MASTERFMT.match(lama.split('_')[0]):
                    inti = lama.split('_')[0]
                    if not inti.startswith(kode1 + '-'):
                        sku_baru = '-'.join([kode1.split('-')[0], kode1.split('-')[1]]
                                            + inti.split('-')[2:])
                elif not lama:
                    warna, kat = SK.segmen_warna(var, 'transparan' in nm.lower())
                    if warna:
                        gen = SK.GEN_KHUSUS.get(kode1, 'G1')
                        sku_baru = f'{kode1}-SP-{kat}-{gen}-{warna}'

            # --- ATURAN 3 (khusus Rocky lawas, instruksi user 2026-09-11):
            # listing "Daihatsu Rocky" berisi 2 chassis beda dalam SATU produk
            # -- lawas (F70/F300 : 1984-2002) nyasar ikut kode Feroza DHT-FRZ
            # (harga 324rb/367rb, BEDA jauh dari Feroza 370rb/413rb), modern
            # (A200, Gen 2 : 2019-2026) SUDAH benar kode TYT-RZE (kembar
            # Raize). User: harga Feroza+Taft GT tetap satu kode DHT-FRZ
            # (Taft GT memang kembar chassis F70 dgn Feroza, harganya di data
            # SUDAH sama dgn Feroza jadi tidak perlu diubah -- cuma perlu
            # diisi kodenya, sudah ditangani ATURAN 2/KODE_BARU). Rocky lawas
            # dipisah ke kode SENDIRI (`DHT-RCK`, baru, belum dipakai model
            # lain) supaya harganya TIDAK ikut ketarik ke harga Feroza --
            # ini KOREKSI thd aturan #8 lama (2026-08-20) yang dulu
            # menggabungkan Rocky lawas ke DHT-FRZ; koreksi ini KHUSUS utk
            # grup Otoprotection krn selisih harganya jauh lebih besar
            # (46rb, vs UA dulu cuma 4rb yg diduga salah input).
            if sku_baru is None and 'rocky' in nm.lower() \
                    and lama.startswith('DHT-FRZ-') and '1984-2002' in var:
                sku_baru = 'DHT-RCK-' + '-'.join(lama.split('-')[2:])
                lap[(ch, 'Rocky lawas -> DHT-RCK sendiri')] += 1

            # --- ATURAN 2 (perbaikan_otoprotection2.py): legacy CVR-OTP atau
            # kosong tanpa match aturan 1 -- pakai KODE_BARU/SIBLING_GEN_TUNGGAL
            legacy = lama.startswith('CVR') and '-OTP-' in lama
            if sku_baru is None and (legacy or (not lama and not kode1)):
                kode2, gen = OP2.kode_dan_gen(nm, var)
                if kode2 and gen:
                    kat, gen2, warna = OP2.segmen(nm, var, gen)
                    if kat:
                        cand = f'{kode2}-SP-{kat}-{gen2}-{warna}'
                        if cand != lama:
                            sku_baru = cand
                            lap[(ch, 'legacy->baru' if legacy else 'isi kosong (baru)')] += 1
                if sku_baru is None and not lama:
                    lewat[nm[:50]] += 1

            if sku_baru == lama:
                sku_baru = None
            if sku_baru and ch == 'lazada':
                dasar = sku_baru; i = 2
                while sku_baru in terpakai[nm]:
                    sku_baru = f'{dasar}_G{i}'; i += 1
                terpakai[nm].add(sku_baru)

            # --- harga (HARGA_TETAP / NORMALKAN_KE_MODUS, dari aturan 1) ---
            pfx, kat_h = OP1.prefix_tier(sku_baru or lama)
            harga_baru = None
            if pfx:
                try:
                    cur = int(float(wsv.cell(row=r, column=col['harga']).value))
                except (TypeError, ValueError):
                    cur = None
                if cur is not None:
                    if pfx in OP1.HARGA_TETAP and kat_h in OP1.HARGA_TETAP[pfx]:
                        mau = OP1.HARGA_TETAP[pfx][kat_h]
                    elif pfx in OP1.NORMALKAN_KE_MODUS:
                        mau = modus.get((pfx, kat_h), cur)
                    else:
                        mau = cur
                    if mau != cur:
                        harga_baru = mau

            atr_baru = {}
            if ch == 'tiktok' and (sku_baru or harga_baru):
                atr_baru = hitung_atribut(nm, wsv, r, i_atr)

            if sku_baru or harga_baru or atr_baru:
                ubah[r] = (sku_baru, harga_baru, atr_baru)
                if sku_baru and (ch, 'legacy->baru' if legacy else 'isi kosong (baru)') not in [(ch, k) for k in ()]:
                    pass  # sudah dicatat di atas utk jalur aturan-2
                if sku_baru and not legacy and kode1:
                    lap[(ch, 'SKU (aturan-1)')] += 1
                if harga_baru:
                    lap[(ch, 'harga')] += 1

        if not ubah:
            continue

        # --- lengkapi atribut wajib TikTok utk SEMUA baris produk yg
        # tersentuh, bukan cuma baris yg SKU/harganya berubah (2026-09-11,
        # ketahuan dari upload gagal: TikTok tolak SELURUH produk kalau ADA
        # 1 baris saja atribut wajibnya kosong -- baris "pelengkap" yg cuma
        # dibawa krn kelengkapan varian TAPI atributnya kosong di sumber
        # ikut bikin produk gagal walau baris itu sendiri tidak diubah).
        if ch == 'tiktok' and pid_c and i_atr:
            produk_tersentuh = {str(wsv.cell(row=r, column=pid_c).value) for r in ubah}
            for r in range(start, wsv.max_row + 1):
                if r in ubah:
                    continue
                nm_r = str(wsv.cell(row=r, column=col['nama']).value or '')
                if not nm_r:
                    continue
                if str(wsv.cell(row=r, column=pid_c).value) not in produk_tersentuh:
                    continue
                atr_extra = hitung_atribut(nm_r, wsv, r, i_atr)
                if atr_extra:
                    ubah[r] = (None, None, atr_extra)
                    lap[(ch, 'atribut baris sibling (baru)')] += 1

        for r, (s, hh, atr) in ubah.items():
            if s:
                sel = ws.cell(row=r, column=col['sku']); sel.value = s; sel.fill = ORANGE
            if hh:
                sel = ws.cell(row=r, column=col['harga']); sel.value = hh; sel.fill = ORANGE
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
        out = os.path.join(out_dir, f'PERBAIKAN_OTOPROTECTION_{ch.upper()}.xlsx')
        wb_o.save(out)
        hasil[ch] = (out, r_out - UH.STARTROW[ch])
    return hasil, lap, lewat


if __name__ == '__main__':
    hasil, lap, lewat = proses(sys.argv[1], sys.argv[2:])
    print('=== ringkasan ===')
    for (ch, jenis), n in sorted(lap.items()):
        print(f'  {ch:8s} {jenis:24s} {n:5d}')
    print(f'\nmasih dilewati ({sum(lewat.values())} baris, genuinely tidak ada preseden):')
    for nm, n in lewat.most_common(20):
        print(f'   {n:4d}  {nm}')
    print()
    for ch, (p, n) in sorted(hasil.items()):
        print(f'[{ch:6s}] {n:5d} baris -> {os.path.basename(p)}')
