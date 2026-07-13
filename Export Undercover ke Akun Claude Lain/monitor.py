"""
monitor.py — Tahap 2: monitoring harian.

Ambil ulang data terbaru dengan menjalankan kembali pencarian untuk setiap
keyword yang sudah pernah dipakai (tersimpan di DB), lalu update harga / harga
diskon / rating / jumlah terjual. Perubahan harga otomatis tercatat ke
price_history (lihat database.upsert_product). Histori lama tidak pernah dihapus.

Kenapa pakai ulang pencarian (bukan endpoint detail per-produk):
  Shopee 2026 menggate hasil di balik login + anti-bot. Jalur pencarian sudah
  terbukti bekerja (dipakai discovery), jadi monitoring memakai jalur yang sama
  agar andal. Produk yang sudah keluar dari hasil pencarian tidak ter-update hari
  itu — datanya tetap tersimpan dengan crawl_date terakhir yang diketahui.
"""
from __future__ import annotations

import config
import database
from discovery import ShopeeBlocked, ShopeeScraper, _use_apify
from utils import get_logger, today_str

log = get_logger("monitor")


def run_monitor() -> dict[str, int]:
    database.init_db()
    if database.count_products() == 0:
        log.warning("DB kosong. Jalankan discovery dulu.")
        return {}

    keywords = database.get_keywords_in_db() or config.get_keywords()
    if not keywords:
        log.warning("Tidak ada keyword untuk di-monitor.")
        return {}

    log.info("Mulai monitoring %s keyword: %s", len(keywords), keywords)
    summary = {"inserted": 0, "updated": 0, "unchanged": 0}

    if _use_apify():
        import apify_backend
        log.info("Backend: Apify")
        for kw in keywords:
            try:
                products = apify_backend.search(kw, config.MAX_PRODUCTS_PER_KEYWORD)
            except Exception as e:
                log.error("Apify gagal untuk '%s': %s", kw, e)
                continue
            for p in products:
                p["crawl_date"] = today_str()
            result = database.bulk_upsert(products)
            log.info("Keyword '%s': %s", kw, result)
            for k, v in result.items():
                summary[k] = summary.get(k, 0) + v
    else:
        with ShopeeScraper() as scraper:
            for kw in keywords:
                try:
                    products = scraper.search(kw, config.MAX_PRODUCTS_PER_KEYWORD)
                except ShopeeBlocked as e:
                    log.error("%s", e)
                    break
                for p in products:
                    p["crawl_date"] = today_str()
                result = database.bulk_upsert(products)
                log.info("Keyword '%s': %s", kw, result)
                for k, v in result.items():
                    summary[k] = summary.get(k, 0) + v

    log.info("Monitoring selesai: %s", summary)
    return summary


if __name__ == "__main__":
    run_monitor()
