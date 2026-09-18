#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch harga UC = rank 1-40 + grup Rocky lawas/Feroza/Taft GT (DHT-FRZ, rank 49,
di luar 40 tapi diminta user eksplisit 2026-08-26 karena SKU-nya nyambung ke
Rocky yang sudah diproses).

target dibangun dari 2 pemanggilan baca_harga() (bukan 1 rentang lebar 1-51)
supaya rank 41-50 (HiAce/Mazda2/Hardtop/Jimny/Ignis/BMW3/Picanto/Sirion) yang
BELUM diminta user TIDAK ikut ke-update - cuma Feroza (rank 49) yang ditambahkan
secara eksplisit.
"""
import sys

from update_harga_per_sku import baca_harga, proses

HARGA_FILE = "Harga Baru UC Top 100 (matriks).xlsx"


def main():
    out_dir, folder = sys.argv[1], sys.argv[2]
    target = baca_harga(HARGA_FILE, 1, 40)
    target_feroza = baca_harga(HARGA_FILE, 49, 49)
    assert set(target_feroza) == {"DHT-FRZ"}, target_feroza
    target.update(target_feroza)
    print(f"target gabungan: {len(target)} prefix "
          f"(1-40 + Feroza #51 [{target['DHT-FRZ']}])")

    hasil, laporan, kena_model = proses(target, out_dir, [folder], "UA")
    for ch, rows in laporan.items():
        print(f"\n[{ch}] {len(rows)} baris -> {hasil[ch]}")
        ringkas = {}
        for label, jenis, lama, baru in rows:
            k = (label, jenis)
            ringkas.setdefault(k, [0, lama, baru])
            ringkas[k][0] += 1
        for (label, jenis), (n, lama, baru) in sorted(ringkas.items()):
            try:
                s_lama = f"Rp{int(float(lama)):,}"
            except (TypeError, ValueError):
                s_lama = f"{lama!r}"
            print(f"    {label:26s} {jenis:8s} {n:4d} baris  {s_lama:>12s} -> Rp{baru:,}")


if __name__ == "__main__":
    main()
