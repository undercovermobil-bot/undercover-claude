"""Bandingkan brand yang sudah ada di master vs brand yang beredar di Indonesia.

Sumber daftar brand Indonesia: peserta GIIAS 2026 (43 merek mobil penumpang) +
merek yang beredar/dijual di Indonesia tapi tidak ikut pameran (premium, legacy,
dan merek yang unitnya masih banyak di jalan meski APM-nya sudah tutup).

Keluaran: `Brand_Belum_Ada.xlsx` dengan 4 sheet
  RINGKASAN     - hitungan per status
  BELUM ADA     - brand beredar di Indonesia yg tidak punya sheet sama sekali
  SHEET KOSONG  - brand yg sheet-nya sudah dibuat tapi 0 produk
  SUDAH ADA     - brand yg sudah berisi produk (+jumlah baris & model)

Kolom "Model Populer" = model yg dijual/banyak beredar di Indonesia, sebagai
titik mulai pembuatan listing. WAJIB diverifikasi ulang sebelum dipakai produksi —
lineup merek Cina/EV berubah cepat.
"""
import warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

MASTER = "MASTER_from_drive_20260715.xlsx"
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
HDR_FONT = Font(color="FFFFFF", bold=True)

# brand beredar di Indonesia -> (kategori pasar, model populer)
INDONESIA = {
    # --- pendatang baru / sedang naik (prioritas tinggi: volume tumbuh) ---
    "VinFast":      ("EV pendatang baru", "VF3, VF5, VF6, VF7, VF e34, Limo Green"),
    "Aletra":       ("EV lokal baru", "L8, L8 Ultimate"),
    "BAW":          ("Cina pendatang baru", "BAW 212"),
    "Leapmotor":    ("EV Cina baru (Indomobil)", "C10, B10, T03"),
    "Polytron":     ("EV lokal baru", "G3, G3+"),
    "Solarky":      ("EV lokal baru", "(cek lineup terbaru)"),
    "Xpeng":        ("EV Cina", "G6, X9, P7"),
    "Zeekr":        ("EV premium (Geely)", "009, 7X, X"),
    "GWM":          ("Cina SUV", "Tank 300, Tank 500, Haval Jolion, Ora 03"),
    "BAIC":         ("Cina SUV", "BJ40 Plus, BJ80, X55, U5 Plus"),
    "Changan":      ("Cina", "CS55 Plus, Alsvin, Hunter"),
    "Deepal":       ("EV Cina (Changan)", "S07, S05, E07, L07"),
    "Denza":        ("EV premium (BYD)", "D9, Z9GT"),
    "Jaecoo":       ("Cina SUV (Chery)", "J7, J5, J8"),
    "Jetour":       ("Cina SUV", "Dashing, X70 Plus, X90 Plus, T2"),
    "iCAR":         ("EV Cina (Chery)", "03, V23"),
    "Lepas":        ("Cina SUV (Chery)", "L8, L6, L4"),
    "Maxus":        ("Cina MPV/pikap", "MIFA 9, MIFA 7, T60"),
    "Neta":         ("EV Cina", "V, V-II, X, S"),
    "Hongqi":       ("Cina premium", "E-HS9, H9, HS3, EH7"),
    # --- premium / mewah (volume kecil, harga cover tinggi) ---
    "Genesis":      ("Premium (Hyundai)", "G80, GV70, GV80"),
    "Jaguar":       ("Premium", "F-Pace, E-Pace, XE, XF, I-Pace"),
    "Lotus":        ("Sport premium", "Emira, Eletre, Emeya"),
    "Aston Martin": ("Super luxury", "DB11, DB12, DBX, Vantage"),
    "Bentley":      ("Super luxury", "Continental GT, Bentayga, Flying Spur"),
    "Rolls-Royce":  ("Super luxury", "Ghost, Cullinan, Phantom, Spectre"),
    "Infiniti":     ("Premium (sudah jarang)", "QX50, Q50, QX80"),
    # --- lokal ---
    "Esemka":       ("Lokal", "Bima 1.2, Bima 1.3, Garuda"),
    "Fin Komodo":   ("Lokal off-road", "KD 250 AT"),
    "Pindad (Maung)": ("Lokal taktis", "MV3, MV1"),
}


def main():
    wb = load_workbook(MASTER, data_only=True)
    isi, kosong = {}, set()
    for s in wb.sheetnames:
        ws = wb[s]
        n = sum(1 for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=2).value)
        m = len({str(ws.cell(row=r, column=2).value).strip()
                 for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=2).value})
        if n:
            isi[s] = (n, m)
        else:
            kosong.add(s)

    def cocok(brand):
        """cari nama sheet yg merujuk brand yg sama (GWM vs 'GWM (Great Wall Motor)')"""
        k = brand.lower().replace("-", "").replace(" ", "")
        for s in wb.sheetnames:
            t = s.lower().replace("-", "").replace(" ", "")
            if t == k or t.startswith(k) or k in t:
                return s
        return None

    belum, sheet_kosong = [], []
    for brand, (kat, model) in sorted(INDONESIA.items()):
        s = cocok(brand)
        if s is None:
            belum.append([brand, kat, model, "belum ada sheet di master"])
        elif s in kosong:
            sheet_kosong.append([s, kat, model, "sheet sudah ada, 0 produk"])

    out = Workbook()
    out.remove(out.active)

    ring = out.create_sheet("RINGKASAN")
    ring.append(["Status", "Jumlah Brand", "Keterangan"])
    ring.append(["Sudah ada + berisi produk", len(isi), "tidak perlu tindakan"])
    ring.append(["Sheet kosong (0 produk)", len(sheet_kosong),
                 "sheet sudah disiapkan, tinggal diisi model + SKU"])
    ring.append(["Belum ada sheet sama sekali", len(belum),
                 "perlu dibuat sheet baru di master"])
    ring.append([])
    ring.append(["Total brand di master", len(wb.sheetnames), ""])

    def tulis(nama, judul, rows):
        ws = out.create_sheet(nama)
        ws.append(judul)
        for r in rows:
            ws.append(r)
        for i, w in enumerate([26, 30, 58, 32], start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for c in range(1, len(judul) + 1):
            ws.cell(row=1, column=c).fill = HDR_FILL
            ws.cell(row=1, column=c).font = HDR_FONT
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(judul))}{ws.max_row}"
        for r in range(2, ws.max_row + 1):
            ws.cell(row=r, column=3).alignment = Alignment(wrap_text=True)

    tulis("BELUM ADA", ["Brand", "Kategori Pasar", "Model Populer di Indonesia", "Status"], belum)
    tulis("SHEET KOSONG", ["Brand (nama sheet)", "Kategori Pasar", "Model Populer di Indonesia", "Status"], sheet_kosong)

    ws = out.create_sheet("SUDAH ADA")
    ws.append(["Brand", "Jumlah Baris", "Jumlah Model"])
    for s, (n, m) in sorted(isi.items(), key=lambda x: -x[1][0]):
        ws.append([s, n, m])
    for i, w in enumerate([30, 16, 16], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in range(1, 4):
        ws.cell(row=1, column=c).fill = HDR_FILL
        ws.cell(row=1, column=c).font = HDR_FONT
    ws.freeze_panes = "A2"

    for c in range(1, 4):
        ring.cell(row=1, column=c).fill = HDR_FILL
        ring.cell(row=1, column=c).font = HDR_FONT
    for i, w in enumerate([34, 16, 52], start=1):
        ring.column_dimensions[get_column_letter(i)].width = w

    out.save("Brand_Belum_Ada.xlsx")
    print(f"BELUM ADA SHEET  : {len(belum)}")
    for b in belum:
        print(f"   - {b[0]:16} {b[1]:28} {b[2]}")
    print(f"\nSHEET KOSONG     : {len(sheet_kosong)}")
    for b in sheet_kosong:
        print(f"   - {b[0]:20} {b[1]:28} {b[2]}")
    print(f"\nSUDAH BERISI     : {len(isi)}")


if __name__ == "__main__":
    main()
