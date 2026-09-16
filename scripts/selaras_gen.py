# -*- coding: utf-8 -*-
"""
Penyelaras label Gen & Warna ke kosakata laporan (sheet 'Detail Gen & Warna').

Laporan memakai label yg SUDAH dinormalisasi, mis:
  'Semua Gen (1 Formula)', 'Gen 1-2 (2003-2020)', 'Gen 3 (2021-2026)',
  'Gen 2 (Reborn)', 'Gen 3 (Zenix)', 'Model/Tahun Lain'
Data mentah marketplace pakai label asli listing, mis 'Gen 2 (2021-2026)', 'Gen 3F (2016-2022)'.
Modul ini memetakan yg mentah -> yg baku, per model.
"""
import re, collections

RE_TAHUN = re.compile(r'(\d{4})\s*[-–]\s*(\d{4})')
RE_TAHUN1 = re.compile(r'\((\d{4})\)')
NAMA_GEN = ("reborn", "zenix", "venturer", "facelift", "prefacelift")


def tahun(label):
    """ambil (awal, akhir) dari label gen; None kalau tidak ada tahun"""
    m = RE_TAHUN.search(str(label))
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (a, b) if a <= b else (b, a)
    m = RE_TAHUN1.search(str(label))
    if m:
        return (int(m.group(1)), int(m.group(1)))
    return None


def tumpang(r1, r2):
    """lebar irisan dua rentang tahun"""
    if not r1 or not r2:
        return 0
    return max(0, min(r1[1], r2[1]) - max(r1[0], r2[0]) + 1)


class Penyelaras:
    def __init__(self, ws_detail, hdr):
        """ws_detail = sheet 'Detail Gen & Warna' laporan; hdr = peta nama kolom -> index"""
        self.gen_model = collections.defaultdict(collections.Counter)
        self.warna_baku = collections.Counter()
        for r in range(4, ws_detail.max_row + 1):
            m = ws_detail.cell(row=r, column=hdr["Nama Mobil"]).value
            if not m:
                continue
            g = str(ws_detail.cell(row=r, column=hdr["Gen"]).value or "").strip()
            w = str(ws_detail.cell(row=r, column=hdr["Warna"]).value or "").strip()
            if g:
                self.gen_model[str(m).strip()][g] += 1
            if w:
                self.warna_baku[w] += 1
        # indeks warna baku utk pencocokan longgar
        self._wnorm = {self._nw(w): w for w in self.warna_baku}

    @staticmethod
    def _nw(s):
        return re.sub(r'[^a-z0-9]', '', str(s).lower())

    def gen(self, model, gen_mentah):
        """-> label gen baku utk model tsb"""
        opsi = self.gen_model.get(model)
        if not opsi:
            return str(gen_mentah).strip() or "Model/Tahun Lain"
        kandidat = [g for g in opsi if g != "Model/Tahun Lain"]
        if not kandidat:
            return "Model/Tahun Lain"
        # model dgn 1 formula: semua varian jatuh ke label tunggal itu
        if len(kandidat) == 1:
            return kandidat[0]
        gm = str(gen_mentah or "").strip()
        if not gm:
            return "Model/Tahun Lain"
        low = gm.lower()
        # 1) cocok persis
        for g in kandidat:
            if g.lower() == low:
                return g
        # 2) gen bernama (Reborn/Zenix/dst)
        for nm in NAMA_GEN:
            if nm in low:
                for g in kandidat:
                    if nm in g.lower():
                        return g
        # 3) tumpang tindih tahun terbesar
        rm = tahun(gm)
        if rm:
            skor = [(tumpang(rm, tahun(g)), g) for g in kandidat]
            skor = [x for x in skor if x[0] > 0]
            if skor:
                skor.sort(key=lambda x: (-x[0], x[1]))
                return skor[0][1]
        # 4) nomor gen sama
        mn = re.search(r'gen\s*([0-9]+)', low)
        if mn:
            for g in kandidat:
                gn = re.search(r'gen\s*([0-9]+)', g.lower())
                if gn and gn.group(1) == mn.group(1):
                    return g
        return "Model/Tahun Lain"

    def warna(self, w):
        """-> warna baku (kalau ada padanannya), kalau tidak kembalikan apa adanya"""
        w = str(w or "").strip()
        if not w:
            return ""
        if w in self.warna_baku:
            return w
        return self._wnorm.get(self._nw(w), w)
