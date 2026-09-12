#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tulis harga baru Transparan ke listing SP aktual (Shopee 1-2, Lazada,
TikTok), 2026-09-12. HANYA kolom harga yang disentuh - SKU sama sekali
tidak diubah (sudah ditangani sesi sebelumnya).

Sumber tier & lantai harga: SAMA PERSIS dengan `harga_transparan_top100.py`
(196rb tingkat kecil / 431rb tingkat besar, ambang Toyota Fortuner
4795mm, Toyota Innova di-paksa tingkat besar per revisi user 2026-09-12).
Kalibrasi (lo, rentang, n_langkah) tiap tingkat DIKUNCI dari 100 model
Top-Terlaris (bukan dihitung ulang dari seluruh katalog SP) - preseden
`harga_baru_sp_op_matriks_v3.py`: nambah anggota baru ke grup TIDAK
BOLEH menggeser harga yang sudah dihitung utk anggota lama. Model baru
(di luar Top-100) diposisikan pakai skala yang sama, diklem 0..3000.

Model non-Top100 dicocokkan ke PANJANG_MM (291 model) via beberapa
lapis alias (persis, potong-brand-dobel, expand '/'-alias, prefix,
alias manual utk typo brand yang sudah dikonfirmasi) - lihat
`resolve_model()`. Yang genuinely tidak ketemu (0 referensi ukuran)
DILEWATI (harga lama dibiarkan), dilaporkan terpisah.

Pemakaian: python3 update_harga_transparan_sp.py
"""
import math
from collections import defaultdict

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit
import harga_baru_sp_op_matriks_v2 as m

LANTAI_KECIL = 196000
LANTAI_BESAR = 431000
AMBANG_MM = m.PANJANG_MM['Toyota Fortuner']
MAX_SPREAD = 3000
STEP = 1000
MM_PER_STEP = 100
PAKSA_BESAR = {'Toyota Innova'}

TOP100_SRC = "Copy_of_DATA_UC_HPP_Top_100_Terlaris.xlsx"

ALIAS_MANUAL = {
    # typo/mismatch merek yang sudah dikonfirmasi (bukan mobil beda)
    'honda fortuner': 'Toyota Fortuner',
    'suzuki agya': 'Toyota Agya',
    'suzuki vitara': 'Suzuki Grand Vitara',
    'toyota 86': 'Toyota GR 86',
    'honda civic hatcback': 'Honda Civic Hatchback',
    # nama listing pendek dari master yg py sufiks/gabungan '/' -
    # dicek dulu KATEGORI di PANJANG_MM utk pastikan body-style SAMA
    # (bukan cuma tebakan) sebelum dimasukkan ke sini
    'honda civic sedan': 'Honda Civic',                    # sama2 Sedan
    'mazda 3 sedan': 'Mazda 3',                             # 'Mazda 3' = Sedan
    'suzuki carry pickup': 'Suzuki Carry',                  # 'Suzuki Carry' = Pickup
    'mitsubishi xpander cross': 'Mitsubishi Mitsubishi Xpander Cross',
    'mitsubishi kuda': 'Mitsubishi Mitsubishi Kuda',
    'mitsubishi destinator': 'Mitsubishi Mitsubishi Destinator',
    'mitsubishi outlander': 'Mitsubishi Mitsubishi Outlander',
    'nissan grand livina': 'Nissan Livina / Grand Livina',
    'daihatsu gran max minibus': 'Daihatsu Gran Max Minibus / Blind Van',
    'honda city hatchback': 'Honda City Hatchback RS',
    'honda hrv': 'Honda HR-V / e:N1',
    'honda brio': 'Honda Brio Satya / RS',
    'suzuki apv arena': 'Suzuki APV Arena / Blind Van',
    'nissan kicks': 'Nissan Kicks e-POWER',
    'mitsubishi l300': 'Mitsubishi L300 Pickup',
    'hyundai avega sedan': 'Hyundai Avega',                 # 'Hyundai Avega' = Sedan
    # SENGAJA TIDAK dialiaskan (body-style beda, ada entri sendiri kalau
    # dipaksa disamakan bisa salah tingkat/harga): 'Mazda 3 Hatchback'
    # (beda dari 'Mazda 3'=Sedan, 4660mm vs Hatchback tak ada datanya),
    # 'Suzuki Aerio Sedan' (beda dari 'Suzuki Aerio Hatchback' yg ada).
}

FILES = [
    ("sp_src/1.xlsx", "SHOPEE_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 4, 6, 7, 7),
    ("sp_src/2.xlsx", "SHOPEE_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 4, 6, 7, 7),
    ("lazada_src.xlsx", "LAZADA_SMARTPROTECTION.xlsx", "template", 3, 14, 13, 9, 5),
    ("tiktok_src.xlsx", "TIKTOK_SMARTPROTECTION.xlsx", "Template", 3, 6, 11, 9, 6),
]


def kalibrasi_grup(panjang_list):
    unik = sorted(set(panjang_list))
    lo, hi = unik[0], unik[-1]
    rentang = hi - lo
    if rentang == 0:
        return lo, 0, 0
    spread = min(int(math.floor(rentang / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
    n_langkah = spread // STEP
    return lo, rentang, n_langkah


def posisi(panjang, kalib):
    lo, rentang, n_langkah = kalib
    if rentang == 0:
        return 0
    mentah = int(math.floor((panjang - lo) / rentang * n_langkah + 0.5)) * STEP
    return max(0, min(mentah, MAX_SPREAD))


def dedupe_brand(nm):
    words = nm.split()
    if len(words) >= 2 and words[0] == words[1]:
        return ' '.join(words[1:])
    return nm


def build_index():
    """norm(key-atau-bagian) -> nama_asli_di_PANJANG_MM, sudah termasuk
    expand '/'-alias & dedupe-brand-dobel (dua arah)."""
    idx = {}
    for k in m.PANJANG_MM:
        idx.setdefault(op_audit.norm(k), k)
        for part in k.split(' / '):
            idx.setdefault(op_audit.norm(part.strip()), k)
        deduped = dedupe_brand(k)
        if deduped != k:
            idx.setdefault(op_audit.norm(deduped), k)
        words = k.split()
        idx.setdefault(op_audit.norm(words[0] + ' ' + k), k)  # re-double
    return idx


def resolve_model(base_nm, idx):
    """SENGAJA TIDAK pakai prefix-match generik ('mazda 3 hatchback'
    ke-match 'Mazda 3' yg sebenarnya Sedan-only, beda body/panjang) -
    cuma exact/dedupe-brand/alias yg sudah divetting manual satu-satu
    (lihat ALIAS_MANUAL)."""
    bn = op_audit.norm(base_nm)
    if bn in idx:
        return idx[bn]
    bn2 = op_audit.norm(dedupe_brand(base_nm))
    if bn2 in idx:
        return idx[bn2]
    if bn in ALIAS_MANUAL:
        return ALIAS_MANUAL[bn]
    return None


def main():
    src = openpyxl.load_workbook(TOP100_SRC, data_only=True)
    ws_src = src['Top 100 Terlaris']
    top100 = [ws_src.cell(r, 1).value for r in range(2, ws_src.max_row + 1)
               if ws_src.cell(r, 1).value]
    kecil0 = [n for n in top100 if m.PANJANG_MM[n] < AMBANG_MM and n not in PAKSA_BESAR]
    besar0 = [n for n in top100 if m.PANJANG_MM[n] >= AMBANG_MM and n not in PAKSA_BESAR]
    kalib_kecil = kalibrasi_grup([m.PANJANG_MM[n] for n in kecil0])
    kalib_besar = kalibrasi_grup([m.PANJANG_MM[n] for n in besar0])
    print(f"Kalibrasi terkunci - kecil: {kalib_kecil}, besar: {kalib_besar}")

    idx = build_index()

    def harga_untuk(nama_panjang_mm_key):
        panjang = m.PANJANG_MM[nama_panjang_mm_key]
        if panjang >= AMBANG_MM or nama_panjang_mm_key in PAKSA_BESAR:
            return LANTAI_BESAR + posisi(panjang, kalib_besar)
        return LANTAI_KECIL + posisi(panjang, kalib_kecil)

    tidak_ketemu = defaultdict(int)
    ketemu_model = {}
    total_stats = defaultdict(int)

    for src_path, out_path, sheet, namecol, varcol, skucol, pricecol, startrow in FILES:
        wb = openpyxl.load_workbook(src_path, data_only=False)
        ws = wb[sheet]
        n_updated = 0
        n_skipped = 0
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if not nm or not op_audit.is_transparan_product(nm):
                continue
            base = op_audit.clean_base_transparan(nm)
            if base not in ketemu_model:
                ketemu_model[base] = resolve_model(base, idx)
            match = ketemu_model[base]
            if not match:
                tidak_ketemu[base] += 1
                n_skipped += 1
                continue
            harga = harga_untuk(match)
            ws.cell(r, pricecol).value = harga
            n_updated += 1
        wb.save(out_path)
        total_stats[out_path] = (n_updated, n_skipped)
        print(f"{out_path}: {n_updated} baris diupdate, {n_skipped} baris dilewati (model tak ketemu)")

    print(f"\nModel TIDAK ketemu referensi ukuran ({len(tidak_ketemu)} model, "
          f"{sum(tidak_ketemu.values())} baris):")
    for b, c in sorted(tidak_ketemu.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {b}")


if __name__ == '__main__':
    main()
