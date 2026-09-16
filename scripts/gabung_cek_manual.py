"""Gabungkan daftar produk 19 file listing jadi beberapa file CEK MANUAL.

Tujuan: user bisa memeriksa SKU tanpa membuka 19 file satu per satu.

Hasil: 4 file, satu per toko (UA/OT/OP/SP). Di dalam tiap file ada satu sheet per
e-commerce (Shopee/TikTok/Lazada) + sheet RINGKASAN. Jadi pembagiannya sesuai
permintaan: per toko DAN per e-commerce.

Kolom sengaja diringkas ke yang perlu dilihat saja — template marketplace aslinya
puluhan kolom dan bikin susah dibaca:
    Nama Produk | Varian | SKU | SKU Dasar | Status | Product ID | File Asal | Baris

  - SKU Dasar  : SKU tanpa akhiran '_' Lazada, supaya mudah dibandingkan antar toko
  - Status     : OK (6 segmen) / KOSONG / BELUM 6 SEGMEN
  - Product ID : hanya terisi untuk Lazada (dipakai mengecek keunikan per listing)

Baris diurutkan per Nama Produk lalu Varian supaya varian satu produk berkumpul.
Tiap sheet diberi autofilter + baris judul dibekukan.
"""
import warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from collections import defaultdict, Counter

import files_baru as FB

JUDUL = ["Nama Produk", "Varian", "SKU", "SKU Dasar", "Status", "Product ID", "File Asal", "Baris"]
LEBAR = [58, 34, 30, 26, 16, 14, 20, 8]
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
HDR_FONT = Font(color="FFFFFF", bold=True)
WARNA_STATUS = {
    "KOSONG": PatternFill("solid", fgColor="FFC7CE"),
    "BELUM 6 SEGMEN": PatternFill("solid", fgColor="FFEB9C"),
}


def status_of(sku):
    if sku in (None, ""):
        return "KOSONG"
    return "OK" if len(str(sku).split("_")[0].split("-")) == 6 else "BELUM 6 SEGMEN"


def kumpulkan():
    """-> {toko: {channel: [baris...]}}"""
    data = defaultdict(lambda: defaultdict(list))
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        ws = load_workbook(FB.path(f), data_only=True)[sheet]
        # UA_Shopee_1..5 digabung jadi satu sheet "Shopee"
        kanal = "".join(ch for ch in chan if not ch.isdigit()) or chan
        for r in range(sr, ws.max_row + 1):
            nm = ws.cell(row=r, column=nc).value
            if not nm:
                continue
            sku = ws.cell(row=r, column=sc).value
            data[store][kanal].append([
                str(nm),
                str(ws.cell(row=r, column=vc).value or ""),
                "" if sku in (None, "") else str(sku),
                "" if sku in (None, "") else str(sku).split("_")[0],
                status_of(sku),
                str(ws.cell(row=r, column=listc).value or "") if listc else "",
                f,
                r,
            ])
    return data


def tulis(store, per_kanal, nama_file):
    wb = Workbook()
    wb.remove(wb.active)

    ring = wb.create_sheet("RINGKASAN")
    ring.append(["E-commerce", "Jumlah Baris", "SKU OK", "SKU Kosong", "Belum 6 Segmen"])
    total = Counter()

    for kanal in sorted(per_kanal):
        baris = sorted(per_kanal[kanal], key=lambda x: (x[0].lower(), x[1].lower()))
        ws = wb.create_sheet(kanal[:31])
        ws.append(JUDUL)
        for b in baris:
            ws.append(b)
        for i, w in enumerate(LEBAR, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for c in range(1, len(JUDUL) + 1):
            sel = ws.cell(row=1, column=c)
            sel.fill = HDR_FILL
            sel.font = HDR_FONT
            sel.alignment = Alignment(vertical="center")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(JUDUL))}{ws.max_row}"
        # tandai baris yang perlu perhatian
        for r in range(2, ws.max_row + 1):
            f = WARNA_STATUS.get(ws.cell(row=r, column=5).value)
            if f:
                ws.cell(row=r, column=5).fill = f

        c = Counter(b[4] for b in baris)
        ring.append([kanal, len(baris), c["OK"], c["KOSONG"], c["BELUM 6 SEGMEN"]])
        total.update(c)
        total["baris"] += len(baris)

    ring.append([])
    ring.append(["TOTAL", total["baris"], total["OK"], total["KOSONG"], total["BELUM 6 SEGMEN"]])
    for c in range(1, 6):
        ring.cell(row=1, column=c).fill = HDR_FILL
        ring.cell(row=1, column=c).font = HDR_FONT
    ring.cell(row=ring.max_row, column=1).font = Font(bold=True)
    for i, w in enumerate([22, 16, 12, 14, 18], start=1):
        ring.column_dimensions[get_column_letter(i)].width = w
    ring.freeze_panes = "A2"

    wb.save(nama_file)
    return total


if __name__ == "__main__":
    data = kumpulkan()
    print("=== FILE CEK MANUAL ===")
    for store in ("UA", "OT", "OP", "SP"):
        if store not in data:
            continue
        nama = f"Cek_Manual_{store}.xlsx"
        t = tulis(store, data[store], nama)
        print(f"  {nama:24} {t['baris']:7} baris   OK={t['OK']:6}  kosong={t['KOSONG']:5}  belum6={t['BELUM 6 SEGMEN']:5}")
        print(f"      sheet: {', '.join(sorted(data[store]))}")
