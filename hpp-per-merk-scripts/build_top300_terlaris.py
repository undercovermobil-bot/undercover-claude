#!/usr/bin/env python3
"""
Membuat workbook HPP untuk N mobil terlaris SAJA, dalam 1 sheet.

Format kolom (A s/d AC + formula) identik dengan build_hpp_per_merk.py — script ini
reuse fungsi-fungsi itu langsung (tulis_sheet, ALIAS, baca_harga_shopee, dst) supaya
harga, penanganan Custom, dan penyesuaian formula tetap 100% konsisten dengan
"DATA UC HPP per Merk (Reguler).xlsx".

Sumber ranking: "MOBIL_TERLARIS_GABUNGAN.xlsx" (dikirim user 2026-08-19), sheet
"Top 300 Mobil" — ranking penjualan REAL gabungan Shopee+Lazada+TikTok/Tokopedia,
periode 1 Jan-30 Jun 2026 (181 hari, 36.457 unit, Rp 10,6 M), 321 model dirinci.
Lebih lengkap dari versi sebelumnya ("Mobil Terlaris.xlsx", cuma 217 model, Shopee+
sebagian Lazada saja - dipakai utk versi Top 100). Lihat sheet "Metodologi" di file
sumber utk definisi lengkap.

Baris diurutkan mengikuti rank penjualan (#1 = paling laris), BUKAN alfabetis.

Versi sebelumnya (build_top100_terlaris.py, N=100, sumber lama) TIDAK dihapus -
biarkan ada sbg riwayat/pembanding kalau perlu re-run versi 100 dgn sumber lama.
"""
import re

import openpyxl
from openpyxl.styles import Alignment, Font

from build_hpp_per_merk import (
    ALIAS, SKU_SRC, baca_harga_shopee, baca_model_per_merk, norm, tulis_sheet,
)

RANKING_SRC = "terlaris/mobil_terlaris_gabungan.xlsx"
N_TARGET = 300
OUT = f"DATA UC HPP Top {N_TARGET} Terlaris.xlsx"
SHEET_DATA = f"Top {N_TARGET} Terlaris"

ARIAL = Font(name="Arial", size=10)
ARIAL_TEBAL = Font(name="Arial", size=10, bold=True)

# Nama ranking (sisi kiri) != nama SKU tracker/master (sisi kanan) meski model FISIKNYA
# sama. Dikonfirmasi lewat 2 cara: (a) sudah ada bukti SKU dari audit sebelumnya
# (audit_balik.json), atau (b) cross-check rentang tahun/generasi di "Detail Gen & Warna"
# thd generasi master (lihat catatan per baris) - bukan tebakan nama.
RESOLUSI_MANUAL = {
    "Honda Brio": "Honda Brio Satya / RS",
    "Honda HRV": "Honda HR-V / e:N1",
    "Nissan Grand Livina": "Nissan Livina / Grand Livina",
    "Mitsubishi Kuda": "Mitsubishi Mitsubishi Kuda",
    "Mitsubishi Xpander Cross": "Mitsubishi Mitsubishi Xpander Cross",
    "Mitsubishi Destinator": "Mitsubishi Mitsubishi Destinator",
    "Honda City Hatchback": "Honda City Hatchback RS",
    "Suzuki Carry Pickup": "Suzuki Carry",
    "Daihatsu Gran Max PU": "Daihatsu Gran Max Pick Up",
    "Mitsubishi Strada Triton": "Mitsubishi Triton",
    # "Suzuki APV Arena" & "Suzuki APV" - 2 judul listing utk model SAMA (Detail Gen &
    # Warna: "Suzuki APV" punya literal value "Arena (2007-2022)" di kolom Gen-nya,
    # dan rentang tahun 2004-2007 identik dgn Gen 1 master Arena) -> 1 baris master.
    "Suzuki APV Arena": "Suzuki APV Arena / Blind Van",
    "Suzuki APV": "Suzuki APV Arena / Blind Van",
    # "Honda City" & "Honda City Sedan" - 2 judul listing, keduanya SEDAN (generasi
    # Gen4 2002-2004/Gen5F 2011-2013/Gen6F 2017-2020 di ranking TIDAK match Hatchback
    # RS yg cuma py 1 generasi 2021-2026; Hatchback punya ranking terpisah sendiri
    # dgn Gen 7 2019-2024) -> 1 baris master.
    "Honda City": "Honda City Sedan",
    "Honda City Sedan": "Honda City Sedan",
    # "Mazda 2" - generasi ranking (2002-2007, 2007-2010, 2014-2019) match PERSIS
    # "Mazda 2 Sedan" master (yg py split Gen2 2007-2010 & cutoff Gen3 2014-2019);
    # "Mazda 2 Hatchback" master TIDAK py split itu (Gen2-nya 2007-2014 nyambung).
    "Mazda 2": "Mazda 2 Sedan",
    # "Kia Rio" - generasi ranking (2005-2009, 2011-2016, 2016-2020) match PERSIS
    # "Kia Rio Sedan" master; "Kia Rio Hatchback" py cutoff beda (2005-2011, 2011-2017).
    "Kia Rio": "Kia Rio Sedan",
    # "Mitsubishi Pajero" - rentang tahun ranking (2008-2015, 2015-2026) = generasi
    # Pajero SPORT persis (Gen2 2008-2015, Gen3 2015-2026). Pajero klasik (bukan Sport)
    # produksinya berhenti ~2003 di Indonesia, tidak mungkin match tahun 2008-2026.
    "Mitsubishi Pajero": "Mitsubishi Pajero Sport",
    # Master row-nya "Nissan X-Trail" (dgn hubung) - norm() TIDAK menganggap "XTrail"
    # (tanpa hubung/spasi) sama dengan "X-Trail" (hubung -> jadi 2 token "x trail"),
    # dan ini bukan model lain, cuma satu-satunya X-Trail di master.
    "Nissan XTrail": "Nissan X-Trail",
    # "MB" = Minibus. Generasi ranking "Gen 1 (2007-2024)" match persis
    # "Daihatsu Gran Max Minibus / Blind Van" master (Gen 1, 2007-2026).
    "Daihatsu Gran Max MB": "Daihatsu Gran Max Minibus / Blind Van",
    # Rentang tahun ranking "2021-2022" cuma cocok Land Cruiser J300 (2021-2026).
    # "Toyota Hardtop" cuma py 1 generasi tunggal J40 (1960-1985) - sama sekali
    # tidak nyambung ke 2021-2022, jadi baris ranking ini murni Land Cruiser.
    "Toyota Hardtop / Land Cruiser": "Toyota Land Cruiser",
    "Toyota 86": "Toyota GR 86",
    "Mercedes E Class": "Mercedes Benz E Class",
    "Toyota Altis": "Toyota Corolla Altis",
    "Mitsubishi L300": "Mitsubishi L300 Pickup",
    "Volkkswagen Polo": "Volkswagen Polo",  # typo di file sumber ("Volkkswagen" 2x-k
    "Aion Hyptec HT": "GAC Aion Hyptec HT",
    "Mazda CX30": "Mazda CX-30",
    # Bug salah-brand YANG SUDAH DIKONFIRMASI sebelumnya di sesi lain (lihat
    # project-undercover-otoprotection-status.md: "2 kasus salah brand di listing SP,
    # Honda Fortuner harusnya Toyota") - listing-nya salah tag merek, mobilnya beneran
    # Toyota Fortuner (yang sudah py baris sendiri di ranking ini juga -> auto-collapse).
    "Honda Fortuner": "Toyota Fortuner",
}

# Nama ranking yang GENUINELY ambigu - datanya tidak cukup utk membedakan kandidat
# di master (rentang tahun identik persis / info generasi kosong total), jadi
# SENGAJA tidak dipetakan (bukan tebakan sepihak). Dilaporkan ke user di CATATAN,
# baris ranking-nya dilewati (backfill otomatis dari rank di bawahnya).
AMBIGU_PERLU_KEPUTUSAN = {
    "Suzuki Aerio": "Ranking tanpa info generasi sama sekali; master py 'Suzuki Aerio "
                     "Sedan' & 'Suzuki Aerio Hatchback' dgn rentang tahun IDENTIK "
                     "(Gen1 2001-2005, Gen1F 2005-2007) - tidak bisa dibedakan dari data ini.",
    "Daihatsu Gran Max": "Ranking nyaris tanpa info generasi ('2008-2022' doang); master "
                         "py 'Daihatsu Gran Max Minibus / Blind Van' & '... Pick Up' dgn "
                         "rentang tahun IDENTIK (Gen 1, 2007-2026) - tidak bisa dibedakan. "
                         "'Daihatsu Gran Max MB' (Minibus) & '... Pick Up' sudah py baris "
                         "sendiri di ranking lain, jadi entri generik ini kemungkinan cuma "
                         "variasi judul salah satunya, bukan model ke-3.",
}

# Model GENUINELY tidak ada di master sama sekali (bukan alias/typo) - sudah pernah
# divalidasi eksplisit di sesi audit OP/SP full-catalog sebelumnya (lihat
# project-undercover-otoprotection-status.md & -smartprotection-status.md), bukan
# temuan baru sesi ini. Dilaporkan ke user, bukan dipetakan paksa ke model lain yg
# namanya kebetulan mirip.
GAP_ASLI_TERVALIDASI = {
    "Chevrolet Estate Magnum": "Genuinely tidak ada di master - beda dari 'Chevrolet "
                                "Optra Magnum' yang ada. Sudah divalidasi di sesi audit "
                                "OP/SP sebelumnya (bukan temuan baru).",
    "Hyundai Verna": "Model Hyundai ini genuinely tidak tercatat di master sama sekali.",
    "Hummer H3": "Genuinely tidak ada di master - beda dari 'Hummer H1' yang ada. "
                 "Sudah divalidasi di sesi audit OP/SP sebelumnya.",
    "Toyota FJ Cruiser": "Genuinely tidak ada di master sama sekali. Sudah divalidasi "
                         "di sesi audit OP/SP sebelumnya.",
}

# Bukan mobil - produk perawatan/aksesori yang kebetulan ikut ke-rank di file sumber.
# Semua listing produk (bukan cover mobil) di toko ini judulnya diawali persis dgn
# nama toko ("Undercover Autocare - <nama produk>"), beda dari listing cover mobil yg
# formatnya "Undercover Autocare - Cover Mobil <model> <tier>" makanya nama MODEL di
# ranking (kolom "Nama Mobil") selalu pendek ("Toyota Avanza"), TIDAK diawali nama
# toko - kecuali utk baris non-mobil ini karena parsernya fallback ke judul penuh.
POLA_BUKAN_MOBIL = re.compile(r"^Undercover Autocare\b", re.I)


def baca_ranking():
    """Header ada di baris 5 (baris 4 = label gabungan "WARNA POLOS..."), data mulai
    baris 6. Beda 1 baris dari sumber lama (header baris 4, data mulai baris 5) -
    struktur kolom No/Nama Mobil di posisi 1/2 tetap sama, cuma barisnya geser."""
    wb = openpyxl.load_workbook(RANKING_SRC, data_only=True)
    ws = wb["Top 300 Mobil"]
    out = []
    for r in range(6, ws.max_row + 1):
        no, nama = ws.cell(r, 1).value, ws.cell(r, 2).value
        if no is None or not nama:
            continue
        out.append((int(no), nama.strip()))
    wb.close()
    return out


def resolusi_index(merk_model):
    """norm(nama) -> nama_master, dari SEMUA baris di semua sheet (post Custom-filter),
    DITAMBAH reverse-ALIAS (norm(nama gaya Shopee) -> nama master).

    ALIAS dipakai searah (master -> Shopee) utk lookup harga; ranking file ini juga
    banyak pakai penulisan gaya Shopee (mis. "Honda BRV" tanpa hubung, "Mazda CX-5"
    dgn hubung tapi master-nya "Mazda CX5" tanpa) - jadi arah kebalikannya dibutuhkan
    juga di sini, bukan cuma cocok ke nama master apa adanya.
    """
    idx = {}
    for models in merk_model.values():
        for m in models:
            idx.setdefault(norm(m), m)
    for master_name, shopee_name in ALIAS.items():
        idx.setdefault(norm(shopee_name), master_name)
    return idx


def resolusi_index_semua_kategori():
    """norm(nama) -> nama, dari SEMUA baris master TANPA filter Kategori Reguler.

    Dipakai cuma utk diagnostik: bedakan "genuinely tidak ada di master sama sekali"
    vs "ada di master tapi cuma kategori Strip/Premium/dst, tidak py Reguler" (mis.
    Volkswagen Kombi - ada, tapi cuma Strip, jadi wajar tidak match idx_master yg
    Reguler-only, dan bukan berarti modelnya tidak dikenal sama sekali)."""
    wb = openpyxl.load_workbook(SKU_SRC, data_only=True, read_only=True)
    idx = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        next(it)
        for r in it:
            if len(r) > 1 and r[1]:
                idx.setdefault(norm(str(r[1]).strip()), str(r[1]).strip())
    wb.close()
    return idx


def tulis_catatan(ws, dipakai, dilewati, tanpa_harga, n_target, n_ranking):
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 34
    ws.column_dimensions["D"].width = 62
    baris = 1

    def tulis(a, b="", c="", d="", tebal=False):
        nonlocal baris
        for kol, val in (("A", a), ("B", b), ("C", c), ("D", d)):
            if val in ("", None):
                continue
            sel = ws[f"{kol}{baris}"]
            sel.value = val
            if isinstance(val, str) and val.startswith("="):
                sel.data_type = "s"
            sel.font = ARIAL_TEBAL if tebal else ARIAL
            sel.alignment = Alignment(wrap_text=True, vertical="top")
        baris += 1

    tulis("CATATAN", "", "", "", tebal=True)
    tulis("", "Isi", f"1 sheet, {len(dipakai)} baris = model mobil terlaris (ranking "
                     "penjualan real, bukan asumsi), diurutkan dari #1 paling laris.")
    tulis("", "Sumber ranking", "MOBIL_TERLARIS_GABUNGAN.xlsx (dikirim user 2026-08-19), "
                                 "sheet 'Top 300 Mobil'. Gabungan Shopee+Lazada+"
                                 "TikTok/Tokopedia, periode 1 Jan-30 Jun 2026 (181 hari), "
                                 "36.457 unit, Rp 10,6 M. Metodologi: qty net (terjual - "
                                 "retur), exclude batal/cancel/refund/unpaid. "
                                 f"{n_ranking} baris terbaca dari sheet sumber.")
    if len(dipakai) < n_target:
        tulis("", "Target vs hasil", f"Diminta {n_target}, hasil {len(dipakai)} - sheet "
                                      "sumber cuma punya segitu model unik setelah "
                                      "dikurangi produk non-mobil & duplikat judul.")
    tulis("", "Format & formula", "Identik dengan DATA UC HPP per Merk (Reguler).xlsx "
                                   "(kolom A-AC, sama persis termasuk penyesuaian "
                                   "IFERROR/IF utk kolom C kosong).")
    tulis("")

    tulis("PERINGKAT -> BARIS (kolom A cocok yang mana)", "", "", "", tebal=True)
    tulis("Rank", "Nama di ranking", "Baris di sheet ini", tebal=True)
    for rank, nama_ranking, nama_master in dipakai:
        ket = "" if norm(nama_ranking) == norm(nama_master) else "(judul beda di ranking)"
        tulis(rank, nama_ranking, nama_master, ket)
    tulis("")

    tulis("DILEWATI DARI RANKING (bukan mobil / duplikat judul / sudah terwakili / ambigu)",
          "", "", "", tebal=True)
    tulis("Rank", "Nama di ranking", "Alasan", tebal=True)
    for rank, nama_ranking, alasan in dilewati:
        tulis(rank, nama_ranking, alasan)
    tulis("")

    if tanpa_harga:
        tulis(f"MASUK TOP {n_target} TAPI HARGA KOSONG (kolom J)", "", "", "", tebal=True)
        tulis("Model", "Alasan", tebal=True)
        for nama, alasan in tanpa_harga:
            tulis(nama, alasan)


def main():
    harga_shopee = baca_harga_shopee()
    merk_model = baca_model_per_merk()
    norm_harga = {norm(k): (k, v) for k, v in harga_shopee.items()}
    idx_master = resolusi_index(merk_model)
    idx_semua_kategori = resolusi_index_semua_kategori()

    ranking = baca_ranking()

    dipakai, dilewati, terpakai_nama = [], [], set()
    for rank, nama_ranking in ranking:
        if len(dipakai) >= N_TARGET:
            break
        if POLA_BUKAN_MOBIL.match(nama_ranking):
            dilewati.append((rank, nama_ranking, "bukan produk cover mobil (aksesori/perawatan)"))
            continue
        if nama_ranking in AMBIGU_PERLU_KEPUTUSAN:
            dilewati.append((rank, nama_ranking, AMBIGU_PERLU_KEPUTUSAN[nama_ranking]))
            continue
        if nama_ranking in GAP_ASLI_TERVALIDASI:
            dilewati.append((rank, nama_ranking, GAP_ASLI_TERVALIDASI[nama_ranking]))
            continue
        target = RESOLUSI_MANUAL.get(nama_ranking) or idx_master.get(norm(nama_ranking))
        if not target:
            non_reguler = idx_semua_kategori.get(norm(nama_ranking))
            if non_reguler:
                alasan = (f"ADA di master ({non_reguler!r}) tapi cuma kategori "
                         "non-Reguler (Strip/Premium/dst) - tidak punya varian Reguler "
                         "sama sekali, jadi tidak bisa masuk workbook ini (scope-nya "
                         "Reguler saja).")
            else:
                alasan = "TIDAK KETEMU padanan di SKU tracker sama sekali - perlu dicek manual."
            dilewati.append((rank, nama_ranking, alasan))
            continue
        if target in terpakai_nama:
            r_sumber, nm_sumber, _ = next(d for d in dipakai if d[2] == target)
            dilewati.append((rank, nama_ranking,
                             f"model sama dgn rank #{r_sumber} {nm_sumber!r} "
                             f"(-> {target!r}), tidak didobel"))
            continue
        terpakai_nama.add(target)
        dipakai.append((rank, nama_ranking, target))

    if len(dipakai) < N_TARGET:
        print(f"PERINGATAN: cuma dapat {len(dipakai)}/{N_TARGET} model unik dari "
              f"{len(ranking)} baris ranking yang tersedia - lanjut dgn yang ada.")

    model_list = [target for _, _, target in dipakai]

    peta_harga, tanpa_harga = {}, []
    for nama_ranking, target in ((r[1], r[2]) for r in dipakai):
        alias_target = ALIAS.get(target, target)
        hit = norm_harga.get(norm(alias_target))
        if hit:
            peta_harga[target] = hit[1][0]
        else:
            tanpa_harga.append((target, "tidak ada listing 'Reguler' di Shopee Undercover Autocare"))

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet(SHEET_DATA)
    tulis_sheet(ws, model_list, peta_harga)

    ws_catatan = wb.create_sheet("CATATAN")
    tulis_catatan(ws_catatan, dipakai, dilewati, tanpa_harga, N_TARGET, len(ranking))

    wb.save(OUT)
    print("tersimpan:", OUT)
    print(f"model terpakai   : {len(dipakai)} / target {N_TARGET}")
    print(f"model ada harga  : {len(peta_harga)}")
    print(f"model tanpa harga: {len(tanpa_harga)}")
    print(f"baris dilewati   : {len(dilewati)}")
    print(f"total baris ranking terbaca: {len(ranking)}")


if __name__ == "__main__":
    main()
