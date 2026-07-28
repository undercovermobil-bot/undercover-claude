"""Perbaiki temuan cek_konsistensi_sku.py yang SUDAH PASTI salah.

Hanya menyentuh kasus yang tidak ambigu — sisanya (kode model beda antar toko)
sengaja dibiarkan karena itu keputusan bisnis, bukan salah ketik.

Yang diperbaiki:
  1. SKU berakhiran/berawalan spasi atau newline  -> di-strip
  2. Segmen generasi rusak `G$`                    -> G1
  3. Kode toko menyimpang dari konvensi file       -> disamakan (OT->UA, OP->SP)
  4. Kode warna tidak cocok teks varian            -> dihitung ulang dari varian
  5. Tier Strip tertukar (Epic<->Elite)            -> Epic=S1x, Elite=S2x, Warrior=S3x

Catatan tier (konvensi proyek, dikonfirmasi berulang):
  UA/OT menulis "Epic/Elite/Warrior"  -> kode P**/E**/W**
  SP/OP menulis "Strip 1/2/3"         -> kode S1*/S2*/S3*
  Epic == Strip 1, Elite == Strip 2, Warrior == Strip 3.

SENGAJA TIDAK DIPERBAIKI: varian yang teksnya memuat DUA nama warna sekaligus
(mis. "Abu-abu<TAB>Silver" pada Chevrolet Captiva Premium) — di situ kode SLV bisa
jadi memang benar, butuh konfirmasi user.
"""
import warnings, sys, re, json
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from collections import Counter

import files_baru as FB

APPLY = "--apply" in sys.argv
KODE_BENAR = {"UA": "UA", "OT": "UA", "SP": "SP", "OP": "SP"}
WARNA = (("abu", "ABU"), ("hitam", "HTM"), ("merah", "MRH"),
         ("biru", "BRU"), ("hijau", "GRN"))
# Kata warna lain yang TIDAK punya kode di WARNA. Kalau salah satunya ikut muncul di
# teks varian, varian itu menyebut lebih dari satu warna (kasus nyata: Chevrolet
# Captiva Premium bervarian "Abu-abu<TAB>Silver") sehingga kode warnanya tidak bisa
# disimpulkan otomatis — biarkan, laporkan ke user.
WARNA_LAIN = ("silver", "putih", "coklat", "gold", "krem", "kuning", "orange", "ungu")
TIER_UA = {"epic": "P", "elite": "E", "warrior": "W"}
TIER_SP = {"epic": "1", "elite": "2", "warrior": "3"}
# "Strip N" (tulisan SP/OP) dan Epic/Elite/Warrior (tulisan UA/OT) itu tier yang sama
SAMA_TIER = {"strip 1": "epic", "strip 2": "elite", "strip 3": "warrior"}
# Strip UA/OT memakai singkatan 2 huruf, bukan huruf pertama saja: EAB/EBR/EMR.
SINGKAT = {"ABU": "AB", "BRU": "BR", "MRH": "MR", "GRN": "GR", "HTM": "HT"}
# Kategori yang bisa dipastikan dari nama produk. "Reguler" sengaja TIDAK dipakai:
# listing Reguler boleh memuat tier Strip, jadi huruf S di situ sah.
KAT_DARI_NAMA = (("premium", "P"), ("exclusive", "E"), ("transparan", "T"))


def warna_dasar(var):
    low = str(var).lower()
    ada = [(low.index(k), k, c) for k, c in WARNA if k in low]
    if len(ada) != 1:          # 0 atau >1 nama warna -> ambigu, jangan disentuh
        return None, None
    if any(w in low for w in WARNA_LAIN):
        return None, None      # varian menyebut warna lain juga -> ambigu
    _, kata, kode = ada[0]
    tier = None
    for t in ("epic", "elite", "warrior", "strip 1", "strip 2", "strip 3"):
        if re.search(t + r'\s+' + kata, low):
            tier = t
            break
    return kode, tier


def kode_warna_harusnya(store, kat, var):
    dasar, tier = warna_dasar(var)
    if dasar is None:
        return None
    if kat != "S":
        return dasar if tier is None else None
    if tier is None:
        return None                     # Strip tanpa tier -> tidak bisa dipastikan
    tier = SAMA_TIER.get(tier, tier)
    if store in ("UA", "OT"):
        t = TIER_UA.get(tier)
        return None if (not t or dasar not in SINGKAT) else t + SINGKAT[dasar]
    t = TIER_SP.get(tier)
    return None if not t else f"S{t}{dasar[0]}"


def run(apply):
    stat = Counter()
    log = []
    for store, chan, f, sheet, nc, vc, sc, sr, listc in FB.LISTINGS:
        fn = FB.path(f)
        wbk = load_workbook(fn, data_only=False)
        ws = wbk[sheet]
        touched = False
        for r in range(sr, ws.max_row + 1):
            s = ws.cell(row=r, column=sc).value
            if not isinstance(s, str) or not s.strip():
                continue
            asli = s
            s2 = s.strip()
            if s2 != s:
                stat["1_spasi_newline"] += 1
            base, _, akhiran = s2.partition("_")
            p = base.split("-")
            if len(p) == 6:
                if "$" in p[4]:
                    p[4] = "G1"
                    stat["2_generasi_rusak"] += 1
                if p[2] != KODE_BENAR[store]:
                    p[2] = KODE_BENAR[store]
                    stat["3_kode_toko"] += 1
                nama_low = str(ws.cell(row=r, column=nc).value or "").lower()
                for kata, kode in KAT_DARI_NAMA:
                    if kata in nama_low and p[3] != kode:
                        p[3] = kode
                        stat["6_kategori_tak_cocok_nama"] += 1
                        break
                harus = kode_warna_harusnya(store, p[3], ws.cell(row=r, column=vc).value)
                if harus and harus != p[5]:
                    stat["5_tier_strip" if p[3] == "S" else "4_kode_warna"] += 1
                    p[5] = harus
                base = "-".join(p)
            baru = base + ("_" + akhiran if akhiran else "")
            if baru != asli:
                if apply:
                    ws.cell(row=r, column=sc, value=baru)
                touched = True
                log.append([f, r, asli, baru,
                            str(ws.cell(row=r, column=vc).value)[:40],
                            str(ws.cell(row=r, column=nc).value)[:50]])
        if apply and touched:
            wbk.save(fn)
    return stat, log


if __name__ == "__main__":
    print("MODE:", "APPLY (file DITULIS)" if APPLY else "DRY-RUN")
    stat, log = run(APPLY)
    for k, v in sorted(stat.items()):
        print(f"   {v:5}  {k}")
    print(f"\ntotal baris disentuh: {len(log)}")
    for x in log[:40]:
        print("   ", x)
    json.dump(log, open("_perbaikan_temuan.json", "w"), ensure_ascii=False)
