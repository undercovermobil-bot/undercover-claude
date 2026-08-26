#!/usr/bin/env python3
"""Verifikasi hasil samakan_sku_kembar.py - SEMUA dibaca ulang dari file di disk,
bukan dari objek di memori."""
import re
import sys
import zipfile
from collections import defaultdict

import openpyxl

from samakan_sku_kembar import GRUP, GRUP_DARI, MASTER_OUT, MASTER_SRC, PETA, bongkar, norm

KOL_NAMA, KOL_TOKO, KOL_KAT, KOL_WARNA, KOL_GEN, KOL_SKU = 2, 3, 4, 5, 6, 9

# prefix yang setelah penggabungan HARUS hilang total dari master
# (2026-08-20: TYT-AGY & DHT-RCK menggantikan DHT-AYL & DHT-FRZ di sini setelah
# koreksi arah pemenang Agya/Ayla & Rocky-lawas - lihat samakan_sku_kembar.py)
PREFIX_MATI = {"DHT-XNA", "TYT-VLZ", "TYT-AGY", "DHT-SGR", "DHT-TRS", "DHT-RCK",
               "DHT-TG", "TYT-VLF"}

# TF dari Sheet2 Data_Mobil_Lebih_dari_1_Formula_2.xlsx
TF_GRUP = {
    "Avanza + Xenia + Veloz (TF=2)": 2,
    "Agya + Ayla (TF=1)": 1,
    "Calya + Sigra (TF=1)": 1,
    "Rush + Terios (TF=1)": 1,
    "Raize + Rocky baru (TF=1)": 1,
    "Alphard + Vellfire (TF=1)": 1,
    "Rocky lawas + Feroza + Taft GT (TF=1)": 1,
}

galat = []


def cek(nama, kondisi, pesan=""):
    print(f"{'OK  ' if kondisi else 'GAGAL'} {nama}" + (f" - {pesan}" if pesan else ""))
    if not kondisi:
        galat.append(nama)


def baca(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    data = {ws.title: [tuple(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    wb.close()
    return data


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else MASTER_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else MASTER_OUT
    A, B = baca(src), baca(out)

    # 1. struktur tidak berubah
    cek("1. daftar sheet sama", list(A) == list(B))
    beda_baris = [(k, len(A[k]), len(B[k])) for k in A if len(A[k]) != len(B.get(k, []))]
    cek("2. jumlah baris tiap sheet sama", not beda_baris, str(beda_baris[:5]))

    # 2. HANYA kolom SKU yang boleh berubah
    lain_berubah = []
    sku_berubah = 0
    for k in A:
        for i, (ra, rb) in enumerate(zip(A[k], B[k])):
            n = max(len(ra), len(rb))
            for c in range(n):
                va = ra[c] if c < len(ra) else None
                vb = rb[c] if c < len(rb) else None
                if va == vb:
                    continue
                if c + 1 == KOL_SKU:
                    sku_berubah += 1
                else:
                    lain_berubah.append((k, i + 1, c + 1, va, vb))
    cek("3. tidak ada kolom selain SKU yang berubah", not lain_berubah, str(lain_berubah[:5]))
    # 2026-08-20: turun dari 1438 -> 1174 setelah koreksi arah Agya/Ayla & Rocky-lawas
    # (Ayla & Feroza sudah native jadi prefix pemenang, jadi baris mereka sendiri
    # tidak perlu berubah lagi - beda dgn versi sebelumnya yang keduanya harus diubah).
    cek("4. jumlah SKU berubah = 1174", sku_berubah == 1174, f"aktual {sku_berubah}")

    # 3. semua baris grup kembar sudah pakai prefix + kode generasi target
    salah = []
    ketemu = set()
    for k, rows in B.items():
        for r in rows[2:]:
            if not r or len(r) < KOL_SKU or not r[KOL_NAMA - 1]:
                continue
            kunci = (norm(r[KOL_NAMA - 1]), norm(r[KOL_GEN - 1]))
            if kunci not in PETA:
                continue
            ketemu.add(kunci)
            pre, toko, kat, gen, warna = bongkar(r[KOL_SKU - 1])
            if (pre, gen) != PETA[kunci]:
                salah.append((k, kunci, r[KOL_SKU - 1]))
    cek("5. semua baris kembar pakai prefix+gen target", not salah, str(salah[:5]))
    cek("6. semua kunci peta ketemu di master", ketemu == set(PETA),
        f"hilang {sorted(set(PETA) - ketemu)}")

    # 4. prefix lama benar-benar hilang
    masih = defaultdict(int)
    for k, rows in B.items():
        for r in rows[2:]:
            if not r or len(r) < KOL_SKU or not r[KOL_SKU - 1]:
                continue
            b = bongkar(r[KOL_SKU - 1])
            if b and b[0] in PREFIX_MATI:
                masih[(k, r[KOL_NAMA - 1], b[0])] += 1
    cek("7. prefix lama hilang total", not masih, str(dict(list(masih.items())[:5])))

    # 5. tiap grup: pasangan kembar menghasilkan SKU IDENTIK utk toko/kat/warna yg sama
    tidak_sinkron = []
    for nama_grup, isi in GRUP.items():
        per_model = defaultdict(dict)   # nama model -> (toko,kat,warna,gen_target) -> sku
        for k, rows in B.items():
            for r in rows[2:]:
                if not r or len(r) < KOL_SKU or not r[KOL_NAMA - 1]:
                    continue
                kunci = (norm(r[KOL_NAMA - 1]), norm(r[KOL_GEN - 1]))
                if GRUP_DARI.get(kunci) != nama_grup:
                    continue
                pre, toko, kat, gen, warna = bongkar(r[KOL_SKU - 1])
                per_model[kunci][(toko, kat, warna, gen)] = r[KOL_SKU - 1]
        # untuk tiap kombinasi, semua model harus punya SKU sama
        gabung = defaultdict(set)
        for kunci, m in per_model.items():
            for komb, sku in m.items():
                gabung[komb].add(sku)
        for komb, s in gabung.items():
            if len(s) > 1:
                tidak_sinkron.append((nama_grup, komb, sorted(s)))
    cek("8. kembar 1 grup -> SKU identik per toko/kat/warna", not tidak_sinkron,
        str(tidak_sinkron[:5]))

    # 6. Total Formula: jumlah kode generasi tiap grup <= TF
    langgar = []
    for nama_grup, tf in TF_GRUP.items():
        kode = {PETA[k][1] for k in PETA if GRUP_DARI[k] == nama_grup}
        if len(kode) > tf:
            langgar.append((nama_grup, tf, sorted(kode)))
    cek("9. jumlah kode generasi <= Total Formula", not langgar, str(langgar))

    # 7. tabrakan Rocky lawas vs Rocky baru selesai
    rocky = defaultdict(set)
    for r in B["Daihatsu"][2:]:
        if r and r[KOL_NAMA - 1] == "Daihatsu Rocky" and r[KOL_SKU - 1]:
            rocky[norm(r[KOL_GEN - 1])].add(bongkar(r[KOL_SKU - 1])[0])
    cek("10. Rocky lawas != Rocky baru", len(rocky) == 2 and not (
        rocky.get("F70/F300", set()) & rocky.get("Gen 2 (A200)", set())),
        str({k: sorted(v) for k, v in rocky.items()}))

    # 8. konsistensi toko: UA<->OT dan SP<->OP tetap sepasang
    TARGET = {"UA": "UA", "OT": "UA", "OP": "SP", "SP": "SP"}
    salah_toko = []
    for k, rows in B.items():
        for r in rows[2:]:
            if not r or len(r) < KOL_SKU or not r[KOL_SKU - 1]:
                continue
            b = bongkar(r[KOL_SKU - 1])
            if not b:
                continue
            toko = b[1]
            if toko not in TARGET.values():
                salah_toko.append((k, r[KOL_NAMA - 1], r[KOL_SKU - 1]))
    cek("11. kode toko di SKU hanya UA/SP", not salah_toko, str(salah_toko[:5]))

    # 9. XML sehat (tidak memicu dialog repair Excel)
    with zipfile.ZipFile(out) as z:
        nama_sheet = [n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n)]
        f_aneh = 0
        for n in nama_sheet:
            xml = z.read(n).decode("utf-8", "replace")
            f_aneh += len(re.findall(r"<f[ />]", xml))
    cek("12. tidak ada elemen formula di master", f_aneh == 0, f"{f_aneh} <f> ditemukan")

    print()
    print("SEMUA CEK LULUS" if not galat else f"ADA {len(galat)} CEK GAGAL: {galat}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
