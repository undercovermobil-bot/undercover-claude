# -*- coding: utf-8 -*-
"""
SALINAN VERBATIM dari branch `claude/repo-memory-access-4hthja`
(scripts/harga_baru_matriks.py, versi final setelah revisi TAMBAHAN_STRIP
56rb->43rb) - dibawa masuk 2026-08-20 atas petunjuk user, TIDAK diubah sama
sekali supaya hasilnya identik dgn yang sudah divalidasi user sebelumnya.
Dipakai ke DATA_UC_HPP_Top_100_Terlaris.xlsx -> lihat
project-undercover-harga-referensi.md untuk konteks lengkap & patokan
verifikasi (Fortuner Rp457rb, BR-V Rp385rb).

Hitung harga jual baru dgn matriks: Pcs/Roll (primer) -> kategori bodi (sekunder)
-> urutan ukuran fisik mobil di dalam grup itu (tersier).

Aturan (instruksi user 2026-08-15, revisi dari versi pertama):
1. Pcs/Roll menentukan LANTAI harga: lantai = ceil('Harga Jual Terbaru' mentah / 1000) * 1000.
   Tiap tier Pcs/Roll py lantai sendiri & TIDAK saling menumpuk -- mobil di tier
   4 pcs/roll tetap mulai dari lantainya sendiri (mis. Fortuner 457rb), bukan
   melanjutkan tangga dari tier 5 pcs/roll.
2. Di dalam tiap (Pcs/Roll x kategori), mobil diurutkan dari ukuran fisik TERKECIL.
   Yang terkecil dapat harga lantai; yang lebih besar naik bertahap.
3. Kenaikan kelipatan Rp1.000, TOTAL rentang dalam 1 grup maksimal Rp5.000.
   Mobil berukuran mirip boleh dapat harga sama.
4. Kolom Strip (Elite/Epic/Warrior) = harga Reguler + TAMBAHAN_STRIP.

CATATAN TEKNIS: file asli TIDAK ditulis ulang. openpyxl membuang cached value
semua formula saat menyimpan workbook yg py formula (terbukti: 0 dari ~8.200
formula menyisakan nilai), sehingga file hasil tampak "banyak yg kosong" sampai
Excel menghitung ulang. Karena itu output ditulis sbg workbook BARU berisi nilai
statis saja.

Pemakaian: python3 harga_baru_matriks.py <file_sumber.xlsx> <file_keluaran.xlsx>
"""
import sys, math
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from collections import defaultdict

STEP = 1000         # kelipatan kenaikan
MAX_SPREAD = 5000   # rentang maksimal dalam 1 grup
MM_PER_STEP = 100   # tiap 100mm selisih panjang bodi = naik 1 langkah (Rp1.000)
# selisih harga varian Strip (Elite/Epic/Warrior) di atas harga Reguler.
# Direvisi user 2026-08-15: semula Rp56.000 -> jadi Rp43.000.
TAMBAHAN_STRIP = 43000

# kategori bodi per produk (dipertahankan sama dgn pembahasan sebelumnya supaya
# konsisten dgn cara user menyebut kelas mobilnya, mis. BR-V & Fortuner dua-duanya
# "SUV besar" walau beda tier Pcs/Roll)
KATEGORI = {
    'Toyota Avanza': 'MPV keluarga', 'Honda Brio Satya / RS': 'City Car',
    'Toyota Innova': 'MPV besar', 'Honda Jazz': 'Hatchback',
    'Suzuki Ertiga': 'MPV keluarga', 'Honda HR-V / e:N1': 'SUV besar',
    'Toyota Agya': 'City Car', 'Daihatsu Ayla': 'City Car',
    'Daihatsu Xenia': 'MPV keluarga', 'Nissan Livina / Grand Livina': 'MPV keluarga',
    'Toyota Vios': 'Sedan', 'Toyota Fortuner': 'SUV besar',
    'Honda BR-V': 'SUV besar', 'Toyota Calya': 'MPV keluarga',
    'Toyota Rush': 'SUV besar', 'Toyota Yaris': 'Hatchback',
    'Toyota Kijang': 'MPV besar', 'Honda CR-V': 'SUV besar',
    'Honda Mobilio': 'MPV keluarga', 'Honda Civic': 'Sedan',
    'Daihatsu Terios': 'SUV besar', 'Mitsubishi Xpander': 'MPV keluarga',
    'Toyota Camry': 'Sedan', 'Honda Accord': 'Sedan',
    'Toyota Corolla': 'Sedan', 'Suzuki APV Arena / Blind Van': 'MPV keluarga',
    'Toyota Raize': 'SUV compact', 'Isuzu Panther': 'MPV besar',
    'Mitsubishi Pajero Sport': 'SUV besar', 'Daihatsu Sigra': 'MPV keluarga',
    'Suzuki Baleno': 'Hatchback', 'Suzuki Fronx': 'SUV compact',
    'Honda Freed': 'MPV keluarga', 'Toyota Hilux': 'Pickup',
    'Suzuki Swift': 'Hatchback', 'Suzuki Karimun': 'City Car',
    'Mitsubishi Triton': 'Pickup', 'Honda City Sedan': 'Sedan',
    'Suzuki XL7': 'MPV keluarga', 'Nissan March': 'City Car',
    'Toyota HiAce': 'MPV besar', 'Mazda 2 Sedan': 'Sedan',
    'Toyota Hardtop': 'SUV besar', 'Suzuki Jimny': 'SUV compact',
    'Suzuki Ignis': 'City Car', 'BMW Seri 3': 'Sedan',
    'Kia Picanto': 'City Car', 'Daihatsu Sirion': 'Hatchback',
    'Daihatsu Feroza': 'SUV compact', 'Toyota Veloz': 'MPV keluarga',
    'Toyota Alphard': 'MPV besar', 'Toyota Starlet': 'Hatchback',
    'Daihatsu Luxio': 'MPV keluarga', 'Toyota Etios Valco': 'Hatchback',
    'Honda WR-V': 'SUV compact', 'Suzuki Splash': 'City Car',
    'Daihatsu Gran Max Pick Up': 'Pickup', 'Daihatsu Rocky': 'SUV compact',
    'Nissan Juke': 'SUV compact', 'Toyota Vellfire': 'MPV besar',
    'Ford Fiesta': 'Hatchback', 'MINI Cooper': 'Hatchback',
    'Toyota Land Cruiser': 'SUV besar', 'Honda Odyssey': 'MPV besar',
    'Toyota Voxy': 'MPV besar', 'Mercedes Benz E Class': 'Sedan',
    'Suzuki Carry': 'Pickup', 'Nissan Evalia': 'MPV keluarga',
    'Mitsubishi Mitsubishi Kuda': 'MPV besar', 'Nissan X-Trail': 'SUV besar',
    'Suzuki SX4': 'SUV compact', 'Daihatsu Taruna': 'SUV compact',
    'Mitsubishi Mitsubishi Xpander Cross': 'MPV keluarga', 'Toyota Sienta': 'MPV keluarga',
    'Mitsubishi Mitsubishi Destinator': 'SUV compact', 'Honda City Hatchback RS': 'Hatchback',
    'Datsun Go Plus': 'MPV keluarga', 'BYD Atto 1': 'City Car',
    'Nissan Terrano': 'SUV besar', 'Hyundai Creta': 'SUV compact',
    'Mitsubishi Mirage': 'City Car', 'Mercedes Benz S Class': 'Sedan',
    'Hyundai Stargazer': 'MPV keluarga', 'Chevrolet Spin': 'MPV keluarga',
    'Mazda CX5': 'SUV besar', 'Wuling Air EV': 'City Car',
    'BMW Seri 5': 'Sedan', 'Toyota Harrier': 'SUV besar',
    'Wuling Almaz': 'SUV besar', 'Mercedes Benz C Class': 'Sedan',
    'Kia Rio Sedan': 'Sedan', 'Suzuki S-Presso': 'City Car',
    'Datsun Go': 'City Car', 'Toyota Soluna': 'Sedan',
    'Mitsubishi Mitsubishi Outlander': 'SUV besar', 'Suzuki Aerio Hatchback': 'Hatchback',
    'Hyundai Palisade': 'SUV besar', 'Timor': 'Sedan',
    'Mazda 2 Hatchback': 'Hatchback', 'Wuling Confero': 'MPV keluarga',
}

# panjang bodi (mm) sbg dasar urutan ukuran dalam grup. Dipakai HANYA utk mengurutkan
# di dalam (Pcs/Roll x kategori) yg sama, bukan utk menghitung harga langsung.
PANJANG_MM = {
    'Wuling Air EV': 2974, 'Suzuki S-Presso': 3565, 'Kia Picanto': 3595,
    'Suzuki Karimun': 3600, 'Suzuki Splash': 3715, 'BYD Atto 1': 3780,
    'Datsun Go': 3785, 'Honda Brio Satya / RS': 3815, 'Nissan March': 3825,
    'Mitsubishi Mirage': 3845, 'Suzuki Ignis': 3700, 'Toyota Agya': 3760,
    'Daihatsu Ayla': 3760,
    'Daihatsu Sirion': 3710, 'Toyota Starlet': 3730, 'Toyota Etios Valco': 3775,
    'Suzuki Swift': 3840, 'MINI Cooper': 3850, 'Toyota Yaris': 3945,
    'Ford Fiesta': 3950, 'Mazda 2 Hatchback': 4065, 'Suzuki Aerio Hatchback': 4145,
    'Honda City Hatchback RS': 4349, 'Suzuki Baleno': 3995, 'Honda Jazz': 4045,
    'Toyota Soluna': 4180, 'Timor': 4365, 'Honda City Sedan': 4553,
    'Mazda 2 Sedan': 4340, 'Kia Rio Sedan': 4370, 'Toyota Vios': 4425,
    'Toyota Corolla': 4630, 'Honda Civic': 4648, 'Mercedes Benz C Class': 4751,
    'BMW Seri 3': 4709, 'Toyota Camry': 4885, 'Honda Accord': 4901,
    'BMW Seri 5': 4963, 'Mercedes Benz E Class': 4935, 'Mercedes Benz S Class': 5179,
    'Datsun Go Plus': 3995, 'Daihatsu Sigra': 4070, 'Toyota Sienta': 4235,
    'Toyota Calya': 4070, 'Daihatsu Luxio': 4165, 'Honda Freed': 4215,
    'Suzuki APV Arena / Blind Van': 4230, 'Chevrolet Spin': 4360,
    'Honda Mobilio': 4386, 'Suzuki Ertiga': 4395, 'Daihatsu Xenia': 4395,
    'Toyota Avanza': 4395, 'Nissan Evalia': 4400,
    'Nissan Livina / Grand Livina': 4420, 'Suzuki XL7': 4450,
    'Hyundai Stargazer': 4460, 'Toyota Veloz': 4475, 'Wuling Confero': 4530,
    'Mitsubishi Xpander': 4595, 'Mitsubishi Mitsubishi Xpander Cross': 4595,
    'Toyota Kijang': 4400, 'Mitsubishi Mitsubishi Kuda': 4450,
    'Isuzu Panther': 4485, 'Toyota Innova': 4735, 'Honda Odyssey': 4840,
    'Toyota Voxy': 4695, 'Toyota Alphard': 4945, 'Toyota Vellfire': 4945,
    'Toyota HiAce': 5265,
    'Suzuki Jimny': 3645, 'Daihatsu Rocky': 3995, 'Toyota Raize': 3995,
    'Suzuki Fronx': 3995, 'Daihatsu Taruna': 4030, 'Honda WR-V': 4060,
    'Nissan Juke': 4135, 'Suzuki SX4': 4135, 'Daihatsu Feroza': 3765,
    'Hyundai Creta': 4315, 'Mitsubishi Mitsubishi Destinator': 4680,
    'Toyota Hardtop': 3840, 'Honda HR-V / e:N1': 4330, 'Nissan Terrano': 4415,
    'Daihatsu Terios': 4435, 'Toyota Rush': 4435, 'Honda BR-V': 4456,
    'Mazda CX5': 4575, 'Wuling Almaz': 4655, 'Nissan X-Trail': 4690,
    'Mitsubishi Mitsubishi Outlander': 4695, 'Honda CR-V': 4703,
    'Toyota Harrier': 4740, 'Toyota Fortuner': 4795,
    'Mitsubishi Pajero Sport': 4825, 'Toyota Land Cruiser': 4950,
    'Hyundai Palisade': 4995,
    'Suzuki Carry': 4195, 'Daihatsu Gran Max Pick Up': 4195,
    'Mitsubishi Triton': 5300, 'Toyota Hilux': 5325,
}


def ceil1000(x):
    return int(math.ceil(x / 1000.0) * 1000)


def hitung_langkah(panjang_terurut):
    """Petakan daftar panjang -> offset harga dari si terkecil di grup.

    Dua tahap, supaya adil di grup sempit MAUPUN grup lebar:
    (1) LEBAR spread grup dari skala ABSOLUT: tiap MM_PER_STEP mm selisih
        panjang terkecil-terbesar = Rp1.000, dibatasi MAX_SPREAD. Ini menjaga
        grup yg ukurannya mirip-mirip tidak dipaksa menyebar penuh Rp5.000
        (mis. Ignis vs Agya/Ayla cuma beda 60mm -> cukup Rp1.000).
    (2) POSISI tiap mobil di dalam spread itu proporsional terhadap panjangnya.
        Ini mencegah efek "satu mobil kekecilan bikin sisanya mentok sama semua"
        (mis. Toyota Hardtop 3840mm di SUV besar bikin 11 mobil lain kena cap
        Rp387.000 kalau pakai skala absolut murni).
    Mobil dgn panjang sama selalu dapat offset sama."""
    unik = sorted(set(panjang_terurut))
    lo, hi = unik[0], unik[-1]
    rentang = hi - lo
    if rentang == 0:
        return {lo: 0}
    spread = min(int(math.floor(rentang / MM_PER_STEP + 0.5)) * STEP, MAX_SPREAD)
    if spread == 0:
        return {p: 0 for p in unik}
    n_langkah = spread // STEP
    peta = {}
    for p in unik:
        rasio = (p - lo) / rentang
        peta[p] = int(math.floor(rasio * n_langkah + 0.5)) * STEP
    return peta


def main(src, out):
    wb = openpyxl.load_workbook(src, data_only=True)
    ws = wb['HPP 12%']

    produk = []
    for r in range(2, ws.max_row + 1):
        nm = ws.cell(row=r, column=1).value
        if not nm:
            continue
        pr = ws.cell(row=r, column=3).value
        hjt = ws.cell(row=r, column=29).value
        if nm not in KATEGORI:
            raise SystemExit(f'BELUM ada kategori utk: {nm}')
        if nm not in PANJANG_MM:
            raise SystemExit(f'BELUM ada data panjang utk: {nm}')
        # Pcs/Roll bisa tersimpan sbg float (6.0) tergantung versi file yg diekspor
        # user -- normalkan ke int supaya pengelompokan tier tidak pecah antara
        # 6 dan 6.0, dan outputnya tidak tampil "6.0"
        pr = int(round(float(pr)))
        produk.append({'row': r, 'nama': nm, 'pcsroll': pr, 'hjt': hjt,
                       'kat': KATEGORI[nm], 'panjang': PANJANG_MM[nm]})

    # lantai harga per tier Pcs/Roll
    lantai = {}
    for p in produk:
        lantai.setdefault(p['pcsroll'], ceil1000(p['hjt']))

    # kelompokkan (pcsroll, kategori)
    grup = defaultdict(list)
    for p in produk:
        grup[(p['pcsroll'], p['kat'])].append(p)

    for (pr, kat), anggota in grup.items():
        panjangs = [a['panjang'] for a in anggota]
        peta = hitung_langkah(sorted(panjangs))
        for a in anggota:
            a['harga_baru'] = lantai[pr] + peta[a['panjang']]
            a['harga_strip'] = a['harga_baru'] + TAMBAHAN_STRIP

    # ---- tulis workbook BARU (nilai statis, tanpa formula) ----
    wbo = openpyxl.Workbook()
    HDR = PatternFill('solid', fgColor='FFC000')
    HIJAU = PatternFill('solid', fgColor='C6EFCE')
    BIRU = PatternFill('solid', fgColor='DDEBF7')
    BOLD = Font(bold=True)

    ws1 = wbo.active
    ws1.title = 'Harga Baru'
    kolom = ['No', 'Nama Produk', 'Pcs/Roll', 'Tipe Mobil', 'Panjang (mm)',
             'Harga Jual Terbaru (mentah)', 'Harga Baru (Reguler)',
             'Harga Baru (Strip: Elite/Epic/Warrior)']
    for i, h in enumerate(kolom, start=1):
        c = ws1.cell(row=1, column=i, value=h)
        c.fill = HDR
        c.font = BOLD
        c.alignment = Alignment(wrap_text=True, vertical='center')

    for i, p in enumerate(produk, start=1):
        r = i + 1
        ws1.cell(row=r, column=1, value=i)
        ws1.cell(row=r, column=2, value=p['nama'])
        ws1.cell(row=r, column=3, value=p['pcsroll'])
        ws1.cell(row=r, column=4, value=p['kat'])
        ws1.cell(row=r, column=5, value=p['panjang'])
        ws1.cell(row=r, column=6, value=round(p['hjt']))
        c7 = ws1.cell(row=r, column=7, value=p['harga_baru']); c7.fill = HIJAU
        c8 = ws1.cell(row=r, column=8, value=p['harga_strip']); c8.fill = BIRU

    for col, w in zip('ABCDEFGH', [5, 34, 9, 15, 12, 16, 15, 18]):
        ws1.column_dimensions[col].width = w
    ws1.freeze_panes = 'A2'

    # ---- sheet matriks: urut Pcs/Roll (besar->kecil) lalu kategori lalu ukuran ----
    ws2 = wbo.create_sheet('Matriks')
    for i, h in enumerate(['Pcs/Roll', 'Tipe Mobil', 'Nama Produk', 'Panjang (mm)',
                           'Harga Baru (Reguler)', 'Harga Baru (Strip)'], start=1):
        c = ws2.cell(row=1, column=i, value=h)
        c.fill = HDR
        c.font = BOLD

    r = 2
    for pr in sorted(set(p['pcsroll'] for p in produk), reverse=True):
        kats = sorted(set(p['kat'] for p in produk if p['pcsroll'] == pr))
        for kat in kats:
            anggota = sorted([p for p in produk if p['pcsroll'] == pr and p['kat'] == kat],
                             key=lambda x: (x['panjang'], x['nama']))
            for p in anggota:
                ws2.cell(row=r, column=1, value=pr)
                ws2.cell(row=r, column=2, value=kat)
                ws2.cell(row=r, column=3, value=p['nama'])
                ws2.cell(row=r, column=4, value=p['panjang'])
                c5 = ws2.cell(row=r, column=5, value=p['harga_baru']); c5.fill = HIJAU
                c6 = ws2.cell(row=r, column=6, value=p['harga_strip']); c6.fill = BIRU
                r += 1
            r += 1  # baris kosong antar grup

    for col, w in zip('ABCDEF', [10, 15, 34, 12, 15, 15]):
        ws2.column_dimensions[col].width = w
    ws2.freeze_panes = 'A2'

    wbo.save(out)

    # ---- laporan konsol ----
    for pr in sorted(set(p['pcsroll'] for p in produk), reverse=True):
        print(f'\n===== {pr} pcs/roll -> lantai Rp{lantai[pr]:,} =====')
        for kat in sorted(set(p['kat'] for p in produk if p['pcsroll'] == pr)):
            anggota = sorted([p for p in produk if p['pcsroll'] == pr and p['kat'] == kat],
                             key=lambda x: x['panjang'])
            hs = [a['harga_baru'] for a in anggota]
            print(f'  [{kat}] Rp{min(hs):,} - Rp{max(hs):,} (rentang Rp{max(hs)-min(hs):,})')
            for a in anggota:
                print(f'      {a["panjang"]:>5}mm  Rp{a["harga_baru"]:>8,}  {a["nama"]}')
    print(f'\nOutput: {out}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
