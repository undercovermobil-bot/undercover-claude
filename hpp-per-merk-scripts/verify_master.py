#!/usr/bin/env python3
"""Verifikasi hasil tambah_model_ke_master.py, dibaca ULANG dari disk.

Baca-ulang dari disk itu wajib, bukan opsional: openpyxl punya kasus di mana
wb.save() sukses tanpa error tapi diam-diam tidak melakukan yang diminta
(lihat feedback-undercover-sku-sync-lessons.md, bug ws.cell(value=None)).
"""
import collections
import json
import sys

import openpyxl

ASLI = "/root/.claude/uploads/15bc0cbc-d42f-5138-97d0-080caf164dfc/5337f5dd-SKU_Price_Tracking_Cover_Mobil_UPDATED.xlsx"
BARU = "SKU, Price, Tracking Cover Mobil - TAMBAHAN MODEL SHOPEE.xlsx"

KODE_TOKO_HARUS = {"Undercover Autocare": "UA", "Otonation": "UA",
                   "Smartprotection": "SP", "Otoprotection": "SP"}
KODE_KAT_HARUS = {"Strip": "S", "Reguler": "R", "Premium": "P",
                  "Exclusive": "E", "Transparan": "T"}


def muat(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    per_sheet = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        next(it)
        baris = [tuple(r[:9]) for r in it if len(r) >= 9 and r[1]]
        per_sheet[ws.title] = baris
    wb.close()
    return per_sheet


def main():
    lama, baru = muat(ASLI), muat(BARU)
    lap = json.load(open("laporan_tambah_master.json"))
    model_baru = {m for _, m, _, _, _ in lap["ditambahkan"]}
    galat = []

    if set(lama) != set(baru):
        galat.append(f"daftar sheet berubah: {set(lama) ^ set(baru)}")

    # 1. baris LAMA harus utuh, tidak tersentuh, dan tetap di urutan yang sama
    total_lama = total_baru = 0
    for sheet in lama:
        a, b = lama[sheet], baru.get(sheet, [])
        total_lama += len(a)
        total_baru += len(b)
        if b[:len(a)] != a:
            beda = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
            galat.append(f"{sheet}: baris lama BERUBAH di index {beda}\n"
                         f"     lama={a[beda] if beda is not None else '?'}\n"
                         f"     baru={b[beda] if beda is not None else '?'}")

    # 2. baris tambahan harus persis milik model baru
    tambahan = []
    for sheet in lama:
        for r in baru[sheet][len(lama[sheet]):]:
            tambahan.append((sheet, r))
            if str(r[1]).strip() not in model_baru:
                galat.append(f"{sheet}: baris tambahan bukan model baru: {r[1]!r}")
    if len(tambahan) != lap["total_baris"]:
        galat.append(f"jumlah baris tambahan {len(tambahan)} != laporan {lap['total_baris']}")

    # 3. tidak boleh ada baris identik ganda (proses multi-pass wajib dicek duplikasi)
    for sheet in baru:
        c = collections.Counter(baru[sheet])
        for row, n in c.items():
            if n > 1:
                galat.append(f"{sheet}: baris duplikat {n}x -> {row}")
                break

    # 4. SKU baru tidak boleh nabrak prefix model yang sudah ada
    pref_lama = collections.defaultdict(set)
    for sheet, rows in lama.items():
        for r in rows:
            if r[8] and isinstance(r[8], str):
                p = r[8].split("-")
                if len(p) >= 2:
                    pref_lama["-".join(p[:2])].add(str(r[1]).strip())
    for sheet, r in tambahan:
        p = r[8].split("-")
        pref = "-".join(p[:2])
        if pref in pref_lama:
            galat.append(f"{sheet}: prefix {pref} ({r[1]!r}) sudah dipakai model lama "
                         f"{pref_lama[pref]}")
            break

    # 5. aturan #1 konsolidasi toko + kode kategori benar di tiap baris tambahan
    for sheet, r in tambahan:
        _, nama, toko, kat, warna, gen, thn, bs, sku = r
        p = sku.split("-")
        if len(p) != 6:
            galat.append(f"{sheet}: format SKU salah: {sku}")
            break
        if p[2] != KODE_TOKO_HARUS[toko]:
            galat.append(f"{sheet}: {sku} toko={toko} harusnya kode {KODE_TOKO_HARUS[toko]}")
            break
        if p[3] != KODE_KAT_HARUS[kat]:
            galat.append(f"{sheet}: {sku} kategori={kat} harusnya kode {KODE_KAT_HARUS[kat]}")
            break
        if bs != f"{nama}-{toko}-{kat}-{warna}-{gen}":
            galat.append(f"{sheet}: Nama Produk Bigseller tidak sesuai pola: {bs!r}")
            break

    # 6. dalam 1 model+generasi, tiap (toko,kategori,warna) cuma boleh sekali
    per_key = collections.Counter()
    for sheet, r in tambahan:
        per_key[(r[1], r[5], r[2], r[3], r[4])] += 1
    ganda = [k for k, n in per_key.items() if n > 1]
    if ganda:
        galat.append(f"kombinasi (model,gen,toko,kat,warna) dobel: {ganda[:3]}")

    # 7. pasangan konsolidasi UA<->OT dan SP<->OP harus punya SKU identik
    by = collections.defaultdict(dict)
    for sheet, r in tambahan:
        by[(r[1], r[5], r[3], r[4])][r[2]] = r[8]
    for kunci, tk in by.items():
        for a, b in (("Undercover Autocare", "Otonation"), ("Smartprotection", "Otoprotection")):
            if a in tk and b in tk and tk[a] != tk[b]:
                galat.append(f"{kunci}: SKU {a} != {b} ({tk[a]} vs {tk[b]})")
                break

    print(f"sheet                 : {len(baru)}")
    print(f"baris master lama     : {total_lama}")
    print(f"baris master baru     : {total_baru}  (+{total_baru - total_lama})")
    print(f"model ditambahkan     : {len(model_baru)}")
    print(f"baris tambahan        : {len(tambahan)}")
    print(f"generasi ditolak      : {len(lap['gen_ditolak'])}")
    print(f"model dilewati        : {len(lap['dilewati'])}")

    if galat:
        print(f"\nGALAT: {len(galat)}")
        for g in galat[:20]:
            print("  -", g)
        sys.exit(1)
    print("\nOK - baris lama utuh, tidak ada duplikat/tabrakan SKU, "
          "konsolidasi toko & kode kategori benar.")


if __name__ == "__main__":
    main()
