#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bikin versi "reupload" dari 8 file final - HANYA baris produk Transparan
(+ baris non-Transparan yg sempat gagal/ke-skip di laporan upload
sebelumnya) - 2026-08-31. User: produk lain (Reguler/Strip) sudah
berhasil diupload duluan, jadi tidak perlu diupload ulang; cukup baris
Transparan (yg baru saja diperbaiki SKU-nya) + baris error lama supaya
tidak ketinggalan.

Baris "error lama" yg dimaksud (dari 2 laporan upload user):
- Lazada SP: 43 baris non-Transparan yg statusnya "Data no change, not
  update" (Hyundai Matrix Gen1 x15, Mitsubishi Lantis x28) - baris ini
  TIDAK ada perbaikan baru (base product-nya di luar 291 target harga),
  disertakan apa adanya sesuai permintaan user, bukan berarti sudah
  diperbaiki.
- TikTok: 7 baris error "atribut Model belum diisi" SEMUANYA produk
  Transparan (Mercedes Benz), jadi otomatis kebawa oleh filter
  Transparan - tidak perlu daftar tambahan.

Metode: hapus baris (openpyxl `delete_rows`, dari bawah ke atas supaya
index tidak bergeser) utk baris yg BUKAN Transparan dan BUKAN di
daftar "extra error rows" - baris header/instruksi template TIDAK
disentuh sama sekali.

Pemakaian: python3 buat_file_reupload_transparan.py
"""
import pickle

import openpyxl

import audit_dan_isi_sku_otoprotection as op_audit

FILES = [
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_1.xlsx", "REUPLOAD_TRANSPARAN_SMARTPROTECTION_1.xlsx", "Sheet1", 2, 7, None),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_2.xlsx", "REUPLOAD_TRANSPARAN_SMARTPROTECTION_2.xlsx", "Sheet1", 2, 7, None),
    ("UPDATE_SKU_HARGA_OTOPROTECTION_1.xlsx", "REUPLOAD_TRANSPARAN_OTOPROTECTION_1.xlsx", "Sheet1", 2, 7, None),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_LAZADA.xlsx", "REUPLOAD_TRANSPARAN_SMARTPROTECTION_LAZADA.xlsx",
     "template", 3, 5, "lazada_extra_error_rows.pkl"),
    ("UPDATE_SKU_HARGA_SMARTPROTECTION_TIKTOK.xlsx", "REUPLOAD_TRANSPARAN_SMARTPROTECTION_TIKTOK.xlsx",
     "Template", 3, 6, None),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_1.xlsx", "REUPLOAD_TRANSPARAN_OTOPROTECTION_TIKTOK_1.xlsx",
     "Template", 3, 6, None),
    ("UPDATE_SKU_OTOPROTECTION_TIKTOK_2.xlsx", "REUPLOAD_TRANSPARAN_OTOPROTECTION_TIKTOK_2.xlsx",
     "Template", 3, 6, None),
]
# UPDATE_SKU_HARGA_OTOPROTECTION_2.xlsx sengaja TIDAK diikutkan - 0 baris
# Transparan sama sekali di file itu (dicek 2026-08-31), tidak ada yg
# perlu di-reupload.


def to_ranges(rows):
    """Gabungkan list nomor baris berurutan jadi (start, count) - openpyxl
    delete_rows(start, count) SEKALI utk 1 blok jauh lebih cepat drpd
    delete_rows(r, 1) satu-satu per baris (O(n^2) kalau dipanggil ribuan
    kali krn tiap panggilan geser SEMUA baris di bawahnya)."""
    ranges = []
    start = prev = None
    for r in rows:
        if start is None:
            start = r
        elif r != prev + 1:
            ranges.append((start, prev - start + 1))
            start = r
        prev = r
    if start is not None:
        ranges.append((start, prev - start + 1))
    return ranges


def main():
    for src, dst, sheet, namecol, startrow, extra_pkl in FILES:
        wb = openpyxl.load_workbook(src, data_only=False)
        ws = wb[sheet]
        extra = pickle.load(open(extra_pkl, 'rb')) if extra_pkl else set()

        to_delete = []
        kept_transparan = 0
        kept_extra = 0
        for r in range(startrow, ws.max_row + 1):
            nm = ws.cell(r, namecol).value
            if nm and op_audit.is_transparan_product(nm):
                kept_transparan += 1
                continue
            if r in extra:
                kept_extra += 1
                continue
            to_delete.append(r)

        for start, count in reversed(to_ranges(to_delete)):
            ws.delete_rows(start, count)

        wb.save(dst)
        print(f"{dst}: transparan={kept_transparan} extra_error={kept_extra} "
              f"dihapus={len(to_delete)}")


if __name__ == '__main__':
    main()
