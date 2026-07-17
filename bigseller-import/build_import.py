#!/usr/bin/env python3
"""
Build a Big Seller "impor untuk membuat SKU Gudang" file from Big Seller
SKU-Gudang export files.

Konteks (2026-07-17):
- Ekspor SKU Gudang dari Big Seller keluar terpotong per <=5.000 baris/file.
  Beberapa file berurutan (kolom "Kode Produk" nyambung) = 1 ekspor utuh.
- Skrip ini menggabungkan semua file ekspor itu, buang duplikat Nomor SKU,
  lalu memetakannya ke 40 kolom template resmi
  "impor_untuk_membuat_sku_gudang".
- Field harga/modal/berat/dimensi di ekspor semuanya 0 dan GTIN kosong, jadi
  dibiarkan kosong (diatur nanti di Big Seller). Yang diisi: Nomor SKU, Judul,
  Kategori, GTIN (kalau ada), Tautan Gambar.
- Output dipecah per <=5.000 baris (match batas ekspor platform) + 1 versi
  gabungan.

Catatan: file .xlsx TIDAK di-commit (lihat .gitignore) — hidup di Google Drive.
Skrip ini yang di-commit supaya reproducible lintas device.

Pakai:
    python build_import.py <folder_ekspor> [folder_output]

<folder_ekspor> = folder berisi file "SKU_Gudang*.xlsx" hasil ekspor Big Seller.
"""
import sys, os, glob, math
import pandas as pd

# 40 header persis template "impor untuk membuat SKU gudang" (urutan wajib sama)
TEMPLATE_HEADERS = [
    '*Nomor SKU (Wajib Diisi)', '*Judul (Wajib)', 'Kategori', 'GTIN', 'Gudang',
    'Stok', 'Modal', 'Modal Referensi', 'Harga Jual Referensi',
    'Tanggal Mulai Penjualan', 'Berat (g)', 'Panjang (cm)', 'Lebar (cm)',
    'Tinggi (cm)', 'Tautan Gambar', 'Pengelolaan Masa Berlaku',
    'Jumlah Hari Masa Berlaku', 'Jumlah Hari Peringatan Sebelum Kedaluwarsa',
    'Catatan SKU Gudang', 'Satuan Dasar', 'Satuan Tambahan 1', 'Aturan Konversi 1',
    'Barcode 1', 'Satuan Tambahan 2', 'Aturan Konversi 2', 'Barcode 2',
    'Satuan Tambahan 3', 'Aturan Konversi 3', 'Barcode 3', 'Satuan Tambahan 4',
    'Aturan Konversi 4', 'Barcode 4', 'Satuan Tambahan 5', 'Aturan Konversi 5',
    'Barcode 5', 'Satuan Pembelian', 'Aktifkan Distribusi', 'Harga Jual Dasar',
    'Harga Jual Terendah Distribusi', 'Pengelolaan Nomor Seri',
]

CHUNK = 5000  # batas baris per file impor (ikut batas ekspor platform)


def load_exports(folder):
    files = sorted(glob.glob(os.path.join(folder, "SKU_Gudang*.xlsx")))
    if not files:
        files = sorted(glob.glob(os.path.join(folder, "*.xlsx")))
    if not files:
        raise SystemExit(f"Tidak ada file .xlsx di {folder}")
    frames = []
    for f in files:
        df = pd.read_excel(f, sheet_name="SKU", header=0, dtype=str)
        frames.append(df)
        print(f"  baca {os.path.basename(f)}: {len(df)} baris")
    exp = pd.concat(frames, ignore_index=True)
    exp["Nomor SKU"] = exp["Nomor SKU"].astype(str).str.strip()
    before = len(exp)
    exp = exp.drop_duplicates(subset=["Nomor SKU"], keep="first").reset_index(drop=True)
    print(f"  gabungan {before} baris -> {len(exp)} SKU unik (buang {before-len(exp)} duplikat)")
    return exp


def to_template(exp):
    out = pd.DataFrame("", index=range(len(exp)), columns=TEMPLATE_HEADERS)
    out['*Nomor SKU (Wajib Diisi)'] = exp['Nomor SKU'].values
    out['*Judul (Wajib)'] = exp.get('Judul', "").fillna("").values
    out['Kategori'] = exp.get('Kategori', "").fillna("").values
    if 'GTIN' in exp:
        out['GTIN'] = exp['GTIN'].fillna("").values
    if 'Tautan Gambar' in exp:
        out['Tautan Gambar'] = exp['Tautan Gambar'].fillna("").values
    # Harga/modal/berat/dimensi = 0 di sumber -> biarkan kosong.
    # Stok per-gudang diatur di Big Seller setelah SKU dibuat.
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)

    exp = load_exports(src)
    out = to_template(exp)
    assert list(out.columns) == TEMPLATE_HEADERS

    n = len(out)
    full = os.path.join(outdir, f"Impor SKU Gudang BigSeller - {n} SKU.xlsx")
    out.to_excel(full, sheet_name="SKU", index=False)
    print(f"tulis gabungan: {full} ({n} baris)")

    parts = math.ceil(n / CHUNK)
    for i in range(parts):
        sub = out.iloc[i*CHUNK:(i+1)*CHUNK]
        fn = os.path.join(outdir, f"Impor SKU Gudang BigSeller - Part {i+1} dari {parts} ({len(sub)} SKU).xlsx")
        sub.to_excel(fn, sheet_name="SKU", index=False)
        print(f"  part {i+1}/{parts}: {len(sub)} baris")


if __name__ == "__main__":
    main()
