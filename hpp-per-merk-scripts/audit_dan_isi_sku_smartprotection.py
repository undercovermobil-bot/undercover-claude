#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit kelengkapan SKU utk 291 produk yang ada di "Harga Baru SP-OP
(matriks) FINAL.xlsx", terhadap listing Shopee Smartprotection (SP) riil
(2 file, format 'sales_info': Kode Produk/Nama Produk/Kode Variasi/Nama
Variasi/SKU/Harga, data mulai baris 7) - lalu USULKAN SKU utk baris yang
kosong, TANPA menebak generasi (hormati aturan #9 Total Formula, lihat
project-undercover-sku-sync-rules.md).

Pencocokan nama produk -> target pakai alias 2-arah (bukan cuma "target
adalah prefix listing" tapi juga sebaliknya) krn nama listing riil sering
BEDA dari nama di file harga: brand didrop ("Feroza" tanpa "Daihatsu"),
atau trim/suffix didrop ("Mitsubishi Pajero" utk "Mitsubishi Pajero
Sport"). User (2026-08-27) menunjukkan 2 contoh ini via screenshot Shopee
setelah laporan audit pertama salah bilang "tidak ditemukan" utk keduanya.

**Fallback fuzzy (typo brand)**: setelah itu user tunjukkan LAGI kasus
"Mitsubishi Grandis" tidak ketemu padahal ADA di listing - ternyata listing
riilnya typo "Mistubishi Grandis" (huruf ketuker). Ditambah fallback
Levenshtein KHUSUS kata pertama (brand), WAJIB kata lain SAMA PERSIS & JUMLAH
KATA SAMA (jangan cuma "kata pertama mirip" - awalnya sempat false-positive
cocokkan "Ford Fusion" ke target "Suzuki Forsa" krn alias brand-didrop
"Forsa" cuma 1 kata vs listing 2 kata, tidak divalidasi panjang kata sama).
Threshold: jarak edit <=2, panjang kata brand asli >=5 huruf. Ditandai
"[FUZZY]" di kolom produk-matched output - hasil MASIH perlu spot-check
manual krn ini bukan match pasti 100%, beda dari alias exact.

Cara ngisi SKU kosong (URUTAN prioritas, TANPA nebak):
1. **"Tahun Lain"/"Model Lain"** -> SENGAJA dilewati, TETAP kosong (aturan
   #4 sku-sync-rules.md, bukan bug).
2. **Sibling sama produk, sama tier (Reguler/Strip), sama teks-setelah-koma
   (tahun/generasi)** yang SUDAH py SKU -> pakai kode generasinya, ganti
   cuma segmen warna. Keyakinan TINGGI (data asli, bukan tebakan).
3. **Fallback TF=1 seragam**: kalau SEMUA baris produk itu yang sudah
   terisi cuma pakai 1 kode generasi bersih ("G<n>", bukan kode bucket
   "GB..." atau campuran), maka baris kosong (termasuk yang generasi
   real-nya beda dari yang sudah keisi) ikut kode yang sama itu. Ini
   VALID krn TF=1 berarti SEMUA generasi asli memang wajib 1 kode -
   sudah terbukti sendiri dari data produk itu (bukan tebakan generik).
4. **TIDAK DIISI kalau**: (a) produk 0 SKU sama sekali (prefix + skema
   generasi keduanya tidak diketahui), atau (b) kode generasi yang sudah
   ada CAMPUR/tidak seragam (indikasi bug "skema generasi ganda" yang
   sudah pernah didokumentasikan 2026-07-18 - WAJIB tarik dari master
   69-sheet asli, bukan ditebak dari file listing SP saja).

Tabel kode warna (dipakai di langkah 2&3, diverifikasi puluhan contoh riil
lintas-brand di file listing): Reguler (bare warna) - Abu-abu=ABU,
Hitam=HTM, Biru Benhur=BRU, Merah=MRH, Hijau Army=GRN, Orange=ORG. Strip
(tier+warna) - Epic=S1, Elite=S2, Warior=S3, dikombinasi Abu=A/Biru=B/
Merah=M (mis. "Epic Biru"->S1B).

Pemakaian: python3 audit_dan_isi_sku_smartprotection.py
    (path target/listing di-hardcode di bawah - sesuaikan sebelum run ulang)
"""
import json
import re
from collections import Counter, defaultdict

import openpyxl

TARGET_PATH = "Harga Baru SP-OP (matriks) FINAL.xlsx"
LISTING_FILES = ["sp_sku_fixed/1.xlsx", "sp_sku_fixed/2.xlsx"]

PREFIX_RE = re.compile(
    r'^(Body\s+)?(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut\s+Mobil)'
    r'(\s*/\s*(Cover\s+Mobil|Sarung(\s+Mobil)?|Selimut\s+Mobil))*\s+', re.IGNORECASE)
SUFFIX_TRANSPARAN_RE = re.compile(r'\s+Transparan$', re.IGNORECASE)

WARNA_REGULER = {'abu-abu': 'ABU', 'hitam': 'HTM', 'biru benhur': 'BRU',
                  'merah': 'MRH', 'hijau army': 'GRN', 'orange': 'ORG'}
TIER_STRIP = {'epic': 'S1', 'elite': 'S2', 'warior': 'S3'}
WARNA_STRIP = {'abu': 'A', 'biru': 'B', 'merah': 'M'}


def normalize(s):
    s = s.lower().replace('-', '').replace('/', ' ').replace(':', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def levenshtein(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[lb]


def tier_dan_warna(variant):
    color_part = variant.split(',')[0].strip().lower()
    if color_part in WARNA_REGULER:
        return 'R', WARNA_REGULER[color_part]
    words = color_part.split()
    if len(words) == 2 and words[0] in TIER_STRIP and words[1] in WARNA_STRIP:
        return 'S', f"{TIER_STRIP[words[0]]}{WARNA_STRIP[words[1]]}"
    return None, None


def gen_text_key(variant):
    parts = variant.split(',', 1)
    return parts[1].strip() if len(parts) > 1 else None


def build_alias_map(targets):
    key_to_target = {}
    for t in targets:
        key_to_target[normalize(t)] = t  # nama asli WAJIB menang (pass 1)

    def add_alias(key, target):
        nk = normalize(key)
        if nk and nk not in key_to_target:
            key_to_target[nk] = target

    for t in targets:
        words = t.split()
        if len(words) >= 3 and words[0] == words[1]:
            add_alias(' '.join([words[0]] + words[2:]), t)
        if ' / ' in t:
            parts = [p.strip() for p in t.split(' / ')]
            brand = t.split()[0]
            add_alias(parts[0], t)
            p0words = parts[0].split()
            if len(p0words) > 2:
                add_alias(' '.join(p0words[:2]), t)
            for p in parts[1:]:
                add_alias(p, t)
                if p.split()[0].lower() != brand.lower():
                    add_alias(f"{brand} {p}", t)
        if len(words) >= 2:
            add_alias(' '.join(words[1:]), t)       # brand didrop (Feroza)
        if len(words) >= 3:
            add_alias(' '.join(words[:-1]), t)       # trim terakhir didrop (Pajero)
    return key_to_target


def match_target(base_name_norm, key_to_target, keys_sorted):
    good = [k for k in keys_sorted
            if base_name_norm == k or (base_name_norm.startswith(k) and base_name_norm[len(k):len(k) + 1] == ' ')]
    return key_to_target[max(good, key=len)] if good else None


def match_fuzzy(base_name_norm, key_to_target, keys_sorted):
    """Fallback typo-brand: kata pertama boleh beda tipis (edit distance<=2,
    panjang asli>=5), kata SISANYA + JUMLAH KATA wajib sama persis - jangan
    longgarkan ini, gampang false-positive (mis. 'Ford Fusion' sempat
    kepancing ke alias 1-kata 'Forsa' sebelum syarat jumlah-kata ditambah)."""
    bwords = base_name_norm.split()
    best = None
    for k in keys_sorted:
        kwords = k.split()
        if len(kwords) != len(bwords) or kwords[1:] != bwords[1:]:
            continue
        d = levenshtein(kwords[0], bwords[0])
        if len(kwords[0]) >= 5 and 0 < d <= 2:
            if best is None or len(k) > len(best[0]):
                best = (k, key_to_target[k], d)
    return best


def audit():
    ws = openpyxl.load_workbook(TARGET_PATH, data_only=True)['Harga Baru SP-OP']
    targets = [ws.cell(r, 2).value for r in range(2, ws.max_row + 1) if ws.cell(r, 2).value]
    key_to_target = build_alias_map(targets)
    keys_sorted = sorted(key_to_target.keys(), key=len, reverse=True)

    per_target = defaultdict(lambda: {'rows': 0, 'sku_ok': 0, 'sku_kosong': 0,
                                        'produk_matched': set(), 'blank_rows_detail': []})
    unmatched_names = Counter()

    for path in LISTING_FILES:
        wsl = openpyxl.load_workbook(path, data_only=True)['Sheet1']
        for r in range(7, wsl.max_row + 1):
            nm = wsl.cell(r, 2).value
            if not nm:
                continue
            is_transparan = bool(SUFFIX_TRANSPARAN_RE.search(nm))
            base = PREFIX_RE.sub('', SUFFIX_TRANSPARAN_RE.sub('', nm)).strip()
            if is_transparan:
                continue
            bn = normalize(base)
            t = match_target(bn, key_to_target, keys_sorted)
            via_fuzzy = False
            if t is None:
                fz = match_fuzzy(bn, key_to_target, keys_sorted)
                if fz:
                    t = fz[1]
                    via_fuzzy = True
            if t is None:
                unmatched_names[nm] += 1
                continue
            sku = wsl.cell(r, 6).value
            d = per_target[t]
            d['rows'] += 1
            d['produk_matched'].add(nm + (' [FUZZY]' if via_fuzzy else ''))
            if sku and str(sku).strip():
                d['sku_ok'] += 1
            else:
                d['sku_kosong'] += 1
                d['blank_rows_detail'].append([path, r, nm, wsl.cell(r, 1).value,
                                                wsl.cell(r, 3).value, wsl.cell(r, 4).value])
    return targets, per_target, unmatched_names


def usulkan_sku(per_target):
    sheets = {p: openpyxl.load_workbook(p, data_only=True)['Sheet1'] for p in LISTING_FILES}
    ok, gagal, skip_tahun_lain = [], [], 0

    for target, d in per_target.items():
        for path, r, nm, pid, varid, variant in d['blank_rows_detail']:
            if not variant:
                gagal.append((target, path, r, variant, "teks varian kosong")); continue
            if 'tahun lain' in variant.lower():
                skip_tahun_lain += 1
                continue
            kat, warna = tier_dan_warna(variant)
            if kat is None:
                gagal.append((target, path, r, variant, "pola warna tidak dikenali")); continue

            wsl = sheets[path]
            gtext = gen_text_key(variant)
            prefix2 = toko = gcode_same = None
            gcodes_all = set()
            for rr in range(7, wsl.max_row + 1):
                if wsl.cell(rr, 1).value != pid:
                    continue
                sku2 = wsl.cell(rr, 6).value
                if not sku2:
                    continue
                segs = str(sku2).split('-')
                if len(segs) != 6:
                    continue
                if prefix2 is None:
                    prefix2, toko = '-'.join(segs[:2]), segs[2]
                gcodes_all.add(segs[4])
                v2 = wsl.cell(rr, 4).value
                if v2:
                    kat2, _ = tier_dan_warna(v2)
                    if kat2 == kat and gen_text_key(v2) == gtext:
                        gcode_same = segs[4]

            if prefix2 is None:
                gagal.append((target, path, r, variant, "produk 0 SKU sama sekali")); continue
            if gcode_same:
                ok.append((target, path, r, pid, varid, variant,
                           f"{prefix2}-{toko}-{kat}-{gcode_same}-{warna}", "sibling sama-tier sama-tahun"))
                continue
            clean = [g for g in gcodes_all if re.fullmatch(r'G\d+', g)]
            if len(gcodes_all) == 1 and len(clean) == 1:
                ok.append((target, path, r, pid, varid, variant,
                           f"{prefix2}-{toko}-{kat}-{clean[0]}-{warna}", f"TF=1 seragam ({clean[0]})"))
            else:
                gagal.append((target, path, r, variant, f"skema generasi campuran: {gcodes_all}"))
    return ok, gagal, skip_tahun_lain


if __name__ == '__main__':
    targets, per_target, unmatched = audit()
    full_ok = [t for t in targets if t in per_target and per_target[t]['sku_kosong'] == 0 and per_target[t]['sku_ok'] > 0]
    partial = [t for t in targets if t in per_target and per_target[t]['sku_ok'] > 0 and per_target[t]['sku_kosong'] > 0]
    all_kosong = [t for t in targets if t in per_target and per_target[t]['sku_ok'] == 0]
    zero_found = [t for t in targets if t not in per_target]
    print(f"Total target: {len(targets)}  Lengkap: {len(full_ok)}  Sebagian kosong: {len(partial)}  "
          f"Semua kosong: {len(all_kosong)}  Tidak ditemukan: {len(zero_found)}")

    ok, gagal, skip = usulkan_sku(per_target)
    print(f"\nSKU diusulkan: {len(ok)}  |  'Tahun Lain' (sengaja skip): {skip}  |  Gagal/butuh info: {len(gagal)}")
