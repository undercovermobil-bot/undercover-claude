# -*- coding: utf-8 -*-
"""Parser nama produk TikTok + pencocokan ke daftar model laporan. Dipakai gabung_tiktok2.py"""
import re, collections

TOKO_KATA = ("undercover", "undervover", "autocare", "autocar", "otonation", "otoprotection",
             "otopro", "smartprotection", "smartpro")
TIER_KATA = [("Exclusive", r"ex+clusive"), ("Premium", r"premium"), ("Reguler", r"regul[ae]r"),
             ("Transparan", r"transparan"), ("Elite", r"elite"), ("Epic", r"epic"),
             ("Warrior", r"warrior"), ("Strip 1", r"strip\s*1"), ("Strip 2", r"strip\s*2"),
             ("Strip 3", r"strip\s*3")]
# frasa pembuka yg harus dibuang (urut dari yg terpanjang)
PREFIX = [
    r"body\s*cover\s*mobil\s*/\s*sarung\s*/\s*selimut\s*mobil",
    r"cover\s*mobil\s*/\s*sarung\s*/\s*selimut\s*mobil",
    # pola Otopro/Smartpro: "Cover Mobil / Selimut Mobil <model>" (tanpa 'Sarung')
    r"cover\s*mobil\s*/\s*selimut\s*mobil",
    r"body\s*cover\s*mobil\s*/\s*selimut\s*mobil",
    r"sarung\s*/\s*selimut\s*mobil",
    r"body\s*cover\s*mobil", r"cover\s*mobil", r"selimut\s*mobil", r"sarung\s*mobil",
    r"car\s*cover",
]
BUANG = [r"\bmobil\b", r"\bbody\b", r"\bcover\b", r"\bsarung\b", r"\bselimut\b",
         r"\bwaterproof\b", r"\banti\s*air\b", r"\bpremium\s*quality\b", r"\bmurah\b",
         r"\bterlaris\b", r"\bbaru\b", r"\bnew\b", r"\bready\b", r"\bstock\b"]


def bersih(nama):
    """nama produk TikTok -> (model_mentah, tier)"""
    s = str(nama)
    # potong bagian setelah ' - ' kalau mengandung nama toko
    bagian = re.split(r'\s+[-–|]\s+', s)
    simpan = [b for b in bagian if not any(t in b.lower() for t in TOKO_KATA)]
    s = " ".join(simpan) if simpan else bagian[0]
    # buang sisa kata toko yg nempel
    for t in TOKO_KATA:
        s = re.sub(r'\b' + t + r'\b', ' ', s, flags=re.I)
    tier = ""
    for label, pat in TIER_KATA:
        m = re.search(r'\b' + pat + r'\b', s, flags=re.I)
        if m:
            tier = label
            s = s[:m.start()] + " " + s[m.end():]
            break
    for p in PREFIX:
        s2 = re.sub(r'^\s*' + p, ' ', s, flags=re.I)
        if s2 != s:
            s = s2
            break
    for b in BUANG:
        s = re.sub(b, ' ', s, flags=re.I)
    s = re.sub(r'[/|,]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip(" -–")
    return s, tier


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def bangun_index(model_laporan):
    """index: normalisasi penuh + tanpa merek (kalau tidak ambigu)"""
    penuh, tanpa_merek = {}, collections.defaultdict(set)
    for m in model_laporan:
        penuh[norm(m)] = m
        bag = str(m).split()
        if len(bag) >= 2:
            tanpa_merek[norm(" ".join(bag[1:]))].add(m)
    # buang yg ambigu (satu nama model dipakai >1 merek)
    tm = {k: list(v)[0] for k, v in tanpa_merek.items() if len(v) == 1 and len(k) >= 3}
    return penuh, tm


def cocokkan(model_mentah, penuh, tanpa_merek):
    n = norm(model_mentah)
    if not n:
        return None
    if n in penuh:
        return penuh[n]
    if n in tanpa_merek:
        return tanpa_merek[n]
    # coba buang kata terakhir (mis. 'Toyota Fortuner Exxclusive' sisa 'exxclusive')
    bag = str(model_mentah).split()
    for potong in range(1, min(3, len(bag))):
        n2 = norm(" ".join(bag[:-potong]))
        if n2 in penuh:
            return penuh[n2]
        if n2 in tanpa_merek and len(n2) >= 3:
            return tanpa_merek[n2]
    return None
