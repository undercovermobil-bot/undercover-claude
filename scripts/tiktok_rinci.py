# -*- coding: utf-8 -*-
"""Pilah kategori TikTok supaya sebanding dgn laporan (yang hanya hitung COVER MOBIL)."""
import openpyxl, datetime, re, collections, json

F = '/root/.claude/uploads/77f87f91-8d04-58ac-abe6-16778a83e499/3f5f928f-Semua_pesanan2026080513_44.xlsx'
TOLAK = ("batal", "cancel", "belum bayar", "unpaid", "belum dibayar", "return", "retur",
         "refund", "pengembalian", "failed", "gagal", "lost")


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return 0.0


wb = openpyxl.load_workbook(F, data_only=True)
ws = wb["OrderSKUList"]
h = {str(ws.cell(row=1, column=c).value).strip(): c for c in range(1, ws.max_column + 1)}

kat_unit = collections.Counter()
kat_rp = collections.Counter()
kat_contoh = {}
sku_per_kat = collections.Counter()
sku_isi_per_kat = collections.Counter()

for r in range(3, ws.max_row + 1):
    nm = ws.cell(row=r, column=h["Product Name"]).value
    if nm is None:
        continue
    st = (str(ws.cell(row=r, column=h["Order Status"]).value or "") + " " +
          str(ws.cell(row=r, column=h["Order Substatus"]).value or "")).lower()
    if any(t in st for t in TOLAK):
        continue
    q = num(ws.cell(row=r, column=h["Quantity"]).value) - num(ws.cell(row=r, column=h["Sku Quantity of return"]).value)
    if q <= 0:
        continue
    kat = str(ws.cell(row=r, column=h["Product Category"]).value or "(kosong)")
    kat_unit[kat] += q
    kat_rp[kat] += num(ws.cell(row=r, column=h["SKU Subtotal After Discount"]).value)
    kat_contoh.setdefault(kat, str(nm)[:60])
    sku_per_kat[kat] += 1
    if str(ws.cell(row=r, column=h["Seller SKU"]).value or "").strip():
        sku_isi_per_kat[kat] += 1

print("=" * 78)
print("RINCIAN PER PRODUCT CATEGORY (sudah buang batal/refund, periode Jan-Jun)")
print("=" * 78)
print(f"  {'kategori':32s} {'unit':>7s} {'nilai (Rp)':>16s} {'SKU terisi':>12s}")
print(f"  {'-'*32} {'-'*7} {'-'*16} {'-'*12}")
tot_u = tot_r = 0
for k, v in kat_unit.most_common():
    pct = sku_isi_per_kat[k] / sku_per_kat[k] * 100 if sku_per_kat[k] else 0
    print(f"  {k[:32]:32s} {v:7,.0f} {kat_rp[k]:16,.0f} {pct:11.1f}%")
    print(f"      contoh: {kat_contoh[k]}")
    tot_u += v
    tot_r += kat_rp[k]
print(f"  {'TOTAL':32s} {tot_u:7,.0f} {tot_r:16,.0f}")

# --- yang setara dgn laporan: HANYA cover mobil ---
MOBIL = [k for k in kat_unit if "Cover & Shelter Mobil" in k]
u_mobil = sum(kat_unit[k] for k in MOBIL)
r_mobil = sum(kat_rp[k] for k in MOBIL)
print()
print("=" * 78)
print("ANGKA YANG SEBANDING DGN LAPORAN (kategori 'Cover & Shelter Mobil' saja)")
print("=" * 78)
print(f"  unit  : {u_mobil:,.0f}")
print(f"  nilai : Rp {r_mobil:,.0f}")
print(f"  /hari : {u_mobil/181:,.2f} unit")
print()
print("  Catatan: 'Kursi & Sarung Kursi' = sarung jok, produk BERBEDA dari cover bodi.")
print("           'Penutup & Sarung Sepeda Motor' = motor, memang dikecualikan laporan.")
