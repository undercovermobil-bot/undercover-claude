"""Daftar file listing TERBARU (export marketplace 2026-07-27) + struktur kolomnya.

Semua file sudah dilewatkan `repair_xlsx.py` lebih dulu karena export Shopee memuat
atribut `activePane="bottom_left"` yang melanggar skema OOXML dan bikin openpyxl
menolak workbook-nya. Hasil perbaikan ada di folder BARU_FIX/.

Kolom (1-based):
  Shopee : B=Nama Produk(2)  D=Nama Variasi(4)  F=SKU(6)      data mulai baris 7
  TikTok : C=product_name(3) E=variation_value(5) K=seller_sku(11)  data mulai baris 6
  Lazada : C=Nama Produk(3)  N=Variations(14)  M=Seller SKU(13)  data mulai baris 5
           (kolom A=Product ID dipakai sbg pengenal listing utk cek keunikan)
"""
DIR = "BARU_FIX"

# (toko, channel, namafile, sheet, kol_nama, kol_varian, kol_sku, baris_awal, kol_listing)
LISTINGS = [
    ("UA", "Shopee1", "UA_Shopee_1.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("UA", "Shopee2", "UA_Shopee_2.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("UA", "Shopee3", "UA_Shopee_3.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("UA", "Shopee4", "UA_Shopee_4.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("UA", "Shopee5", "UA_Shopee_5.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("UA", "TikTok1", "UA_TikTok_1.xlsx", "Template", 3, 5, 11, 6, None),
    ("UA", "TikTok2", "UA_TikTok_2.xlsx", "Template", 3, 5, 11, 6, None),
    ("UA", "TikTok3", "UA_TikTok_3.xlsx", "Template", 3, 5, 11, 6, None),
    ("UA", "Lazada",  "UA_Lazada.xlsx",   "template", 3, 14, 13, 5, 1),
    ("OT", "Shopee1", "OT_Shopee_1.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("OT", "Shopee2", "OT_Shopee_2.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("OP", "Shopee1", "OP_Shopee_1.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("OP", "Shopee2", "OP_Shopee_2.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("OP", "TikTok1", "OP_TikTok_1.xlsx", "Template", 3, 5, 11, 6, None),
    ("OP", "TikTok2", "OP_TikTok_2.xlsx", "Template", 3, 5, 11, 6, None),
    ("SP", "Shopee1", "SP_Shopee_1.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("SP", "Shopee2", "SP_Shopee_2.xlsx", "Sheet1",   2, 4, 6, 7, None),
    ("SP", "TikTok",  "SP_TikTok.xlsx",   "Template", 3, 5, 11, 6, None),
    ("SP", "Lazada",  "SP_Lazada.xlsx",   "template", 3, 14, 13, 5, 1),
]

LAZADA = [(f"{DIR}/{f}", sheet, listc, varc, skuc, sr)
          for (st, ch, f, sheet, nc, varc, skuc, sr, listc) in LISTINGS if ch == "Lazada"]

MOTOR = [(st, ch, f"{DIR}/{f}", sheet, nc, vc, sc, sr)
         for (st, ch, f, sheet, nc, vc, sc, sr, lc) in LISTINGS
         if ch.startswith("Shopee") or ch.startswith("TikTok")]


def path(f):
    return f"{DIR}/{f}"
