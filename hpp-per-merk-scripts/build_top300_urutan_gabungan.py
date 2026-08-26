#!/usr/bin/env python3
"""
Gabungkan urutan 2 sumber ranking, sesuai instruksi user 2026-08-19:

  "Sesuaikan urutan di 100 pertamanya pakai yg terlaris 100 ini, kemudian
   selanjutnya hingga 300 an pakai file yg sebelumnya aku kirim, kalau ada
   list produk yg urutannya berbeda dengan 100 terlaris, taruh di setelah
   urutan nomor 100"

Artinya:
  - Posisi 1-100  : urutan PERSIS dari "DATA UC HPP Top 100 Terlaris.xlsx" (dikirim
    user balik 2026-08-19, sumber lama "Mobil Terlaris.xlsx" 217 model) - dikunci.
  - Posisi 101+   : sisa model dari list GABUNGAN (build_top300_terlaris.py, sumber
    "MOBIL_TERLARIS_GABUNGAN.xlsx" 321 model), diurutkan sesuai rank di situ,
    MINUS 100 model yang sudah dipakai di posisi 1-100 (jangan didobel).

Diverifikasi eksplisit sebelum digabung: semua 100 model di file top-100 ternyata
ADA di list GABUNGAN juga (overlap 100%, 0 yang hilang) - jadi penggabungan ini
bersih, tidak ada model top-100 yang harus "dikarang" datanya.

Data (harga, formula) diambil dari pipeline SAAT INI (build_hpp_per_merk.py /
build_top300_terlaris.py), BUKAN nilai beku di file top-100 lama - supaya semua
baris konsisten dgn perbaikan/koreksi yang sudah dilakukan sepanjang sesi ini.
"""
import openpyxl
from openpyxl.styles import Alignment, Font

from build_hpp_per_merk import tulis_sheet
from build_top300_terlaris import N_TARGET, norm, peta_harga_untuk, resolusi_ranking

TOP100_LOCK_SRC = "terlaris/top100_urutan_final.xlsx"
TOP100_LOCK_SHEET = "Top 100 Terlaris"
OUT = "DATA UC HPP Top 300 Terlaris (urutan gabungan).xlsx"
SHEET_DATA = "Top 300 Terlaris"

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)


def baca_urutan_lock():
    wb = openpyxl.load_workbook(TOP100_LOCK_SRC, data_only=True)
    ws = wb[TOP100_LOCK_SHEET]
    urutan = [ws.cell(r, 1).value for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value]
    wb.close()
    return urutan


def tulis_catatan_gabungan(ws, urutan_lock, hilang_dari_300, dipakai, dilewati, tanpa_harga):
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 66
    baris = 1

    def tulis(a, b="", c="", tebal=False):
        nonlocal baris
        for kol, val in (("A", a), ("B", b), ("C", c)):
            if val in ("", None):
                continue
            sel = ws[f"{kol}{baris}"]
            sel.value = val
            if isinstance(val, str) and val.startswith("="):
                sel.data_type = "s"
            sel.font = ARIAL_TEBAL if tebal else ARIAL
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris += 1

    tulis("CATATAN", "", "", tebal=True)
    tulis("Isi", "Gabungan 2 urutan sumber, sesuai instruksi user 2026-08-19: posisi "
                 "1-100 dikunci dari 'DATA UC HPP Top 100 Terlaris.xlsx' (dikirim user "
                 "balik), posisi 101+ lanjut dari ranking GABUNGAN (321 model, "
                 "Shopee+Lazada+TikTok/Tokopedia).")
    tulis("Verifikasi overlap", f"Semua {len(urutan_lock)} model di file top-100 "
                                 f"dicek ADA di list GABUNGAN juga "
                                 f"({'100% cocok, 0 hilang' if not hilang_dari_300 else f'{len(hilang_dari_300)} TIDAK ketemu, lihat di bawah'}).")
    tulis("Sumber data", "Harga & formula diambil dari pipeline SAAT INI (bukan nilai "
                          "beku di file top-100 lama) - supaya konsisten dgn semua "
                          "koreksi yang sudah dilakukan sepanjang sesi.")
    tulis("")

    if hilang_dari_300:
        tulis("MODEL DI TOP-100 TAPI TIDAK KETEMU DI LIST GABUNGAN", "", "", tebal=True)
        for m in hilang_dari_300:
            tulis("", m, "Tetap dipakai di posisi top-100 (data dari pipeline saat "
                          "ini), tapi tidak ikut proses dedup thd list 101+ krn tidak "
                          "ketemu paritas di GABUNGAN.")
        tulis("")

    tulis("POSISI 1-100 (dikunci, urutan dari file top-100)", "", "", tebal=True)
    tulis("Posisi", "Model", tebal=True)
    for i, m in enumerate(urutan_lock, start=1):
        tulis(i, m)
    tulis("")

    tulis("POSISI 101+ (lanjut dari ranking GABUNGAN, model yg blm dipakai)", "", "", tebal=True)
    tulis("Posisi", "Model", "Rank asli di GABUNGAN", tebal=True)
    for i, (rank, nama_ranking, target) in enumerate(dipakai, start=len(urutan_lock) + 1):
        ket = f"#{rank} {nama_ranking!r}" if norm(nama_ranking) != norm(target) else f"#{rank}"
        tulis(i, target, ket)
    tulis("")

    tulis("DILEWATI DARI RANKING GABUNGAN (bukan mobil / duplikat / gap / ambigu)",
          "", "", tebal=True)
    tulis("Rank", "Nama di ranking", "Alasan", tebal=True)
    for rank, nama_ranking, alasan in dilewati:
        tulis(rank, nama_ranking, alasan)
    tulis("")

    if tanpa_harga:
        tulis("HARGA KOSONG (kolom J)", "", "", tebal=True)
        tulis("Model", "Alasan", tebal=True)
        for nama, alasan in tanpa_harga:
            tulis(nama, alasan)


def main():
    urutan_lock = baca_urutan_lock()
    dipakai_300, dilewati_300, _ = resolusi_ranking(N_TARGET)

    terpakai_di_300 = {target for _, _, target in dipakai_300}
    hilang_dari_300 = [m for m in urutan_lock if m not in terpakai_di_300]
    if hilang_dari_300:
        print("PERINGATAN: model top-100 tidak ketemu di list GABUNGAN:", hilang_dari_300)

    ekor = [d for d in dipakai_300 if d[2] not in set(urutan_lock)]

    model_list = urutan_lock + [target for _, _, target in ekor]
    assert len(model_list) == len(set(model_list)), "ada model dobel setelah digabung!"

    peta_harga, tanpa_harga = peta_harga_untuk(model_list)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet(SHEET_DATA)
    tulis_sheet(ws, model_list, peta_harga)

    ws_catatan = wb.create_sheet("CATATAN")
    tulis_catatan_gabungan(ws_catatan, urutan_lock, hilang_dari_300, ekor, dilewati_300, tanpa_harga)

    wb.save(OUT)
    print("tersimpan:", OUT)
    print(f"total baris      : {len(model_list)}")
    print(f"  posisi 1-100   : {len(urutan_lock)} (dikunci)")
    print(f"  posisi 101+    : {len(ekor)} (dari GABUNGAN)")
    print(f"model ada harga  : {len(peta_harga)}")
    print(f"model tanpa harga: {len(tanpa_harga)}")


if __name__ == "__main__":
    main()
