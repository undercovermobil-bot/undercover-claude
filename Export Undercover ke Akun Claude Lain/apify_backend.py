"""
apify_backend.py — Backend scraping via Apify actor.

Actor: "Shopee Search & Category Scraper - Cheapest" (4nhvc7lTKzkDrk7bD)
Dipakai saat APIFY_TOKEN tersedia di .env.

Mapper dari output actor -> skema DB:
  shop_id + item_id  -> product_id
  name               -> product_name
  url                -> product_url
  price              -> current_price (sudah IDR, tidak perlu konversi)
  original_price     -> original_price (None jika actor tidak balikin; estimasi dari discount_pct)
  rating             -> rating
  sold_count         -> sold_count (None dari actor ini — actor tidak ambil detail page)
  location           -> shop_name (kota; shop_name tidak tersedia di actor ini)
"""
from __future__ import annotations

import math
import os
import re
from datetime import timedelta

import config
from utils import get_logger, today_str

log = get_logger("apify")

ACTOR_ID = "4nhvc7lTKzkDrk7bD"   # Shopee Search & Category Scraper - Cheapest
# Actor ini mensupport max_items minimum 1 (tidak ada minimum constraint seperti actor lain)
_DEFAULT_COUNTRY = "ID"


def _get_client():
    try:
        from apify_client import ApifyClient
    except ImportError:
        raise RuntimeError("apify-client belum terinstall. Jalankan: pip install apify-client")
    token = os.getenv("APIFY_TOKEN") or ""
    if not token:
        raise RuntimeError("APIFY_TOKEN tidak ditemukan di .env")
    return ApifyClient(token)


def _map_item(raw: dict, keyword: str) -> dict | None:
    """Map satu item output actor -> dict skema DB."""
    # Coba berbagai nama field (snake_case & camelCase)
    shop_id = (raw.get("shop_id") or raw.get("shopId") or raw.get("shopid")
               or raw.get("seller_id") or raw.get("sellerId"))
    item_id = (raw.get("item_id") or raw.get("itemId") or raw.get("itemid")
               or raw.get("product_id") or raw.get("productId"))

    # Fallback: ekstrak dari URL jika field ID tidak tersedia
    if not shop_id or not item_id:
        url_raw = raw.get("url") or raw.get("product_url") or raw.get("link") or ""
        m = re.search(r"i\.(\d+)\.(\d+)", url_raw)
        if m:
            shop_id, item_id = m.group(1), m.group(2)

    if not shop_id or not item_id:
        return None

    price = raw.get("price")
    # Hitung original_price dari discount_pct jika tidak tersedia langsung
    original_price = raw.get("original_price")
    if original_price is None:
        disc = raw.get("discount_pct")
        if disc and price and disc < 100:
            original_price = round(price / (1 - disc / 100))

    # shop_name: coba field nama toko dulu, fallback ke location (kota)
    shop_name = (
        raw.get("shop_name")
        or raw.get("shopName")
        or raw.get("seller_name")
        or raw.get("location")
        or ""
    )

    return {
        "product_id": f"{shop_id}_{item_id}",
        "shop_name": shop_name,
        "product_name": raw.get("name") or "",
        "product_url": raw.get("url") or "",
        "current_price": int(price) if price is not None else None,
        "original_price": int(original_price) if original_price is not None else None,
        "rating": raw.get("rating"),
        "sold_count": raw.get("sold_count"),
        "is_mall": bool(raw.get("is_mall") or raw.get("isMall") or raw.get("is_official")),
        "search_keyword": keyword,
        "crawl_date": today_str(),
    }


def search(keyword: str, max_products: int) -> list[dict]:
    """
    Jalankan actor Apify untuk satu keyword, kembalikan list dict produk.
    Memanggil API Apify secara sinkron (block sampai selesai).
    """
    client = _get_client()

    run_input = {
        "keyword": keyword,
        "maxItems": max_products,
        "countryCode": _DEFAULT_COUNTRY,
    }

    log.info("Apify run: keyword='%s' maxItems=%s actor=%s", keyword, max_products, ACTOR_ID)
    run = client.actor(ACTOR_ID).call(
        run_input=run_input,
        wait_duration=timedelta(seconds=600),  # batas tunggu 10 menit
    )

    if not run or run.status != "SUCCEEDED":
        raise RuntimeError(f"Apify run gagal: status={getattr(run,'status','?')}")

    items = list(client.dataset(run.default_dataset_id).iterate_items())
    log.info("Apify: %s item di dataset untuk '%s'", len(items), keyword)

    # Diagnostik sekali: tampilkan keys dari item pertama agar mudah debug field mapping
    if items:
        log.debug("Apify field keys contoh: %s", list(items[0].keys()))

    results = []
    skipped = 0
    for raw in items:
        mapped = _map_item(raw, keyword)
        if mapped:
            results.append(mapped)
        else:
            skipped += 1

    if skipped:
        log.warning("Apify: %s item di-skip (tidak punya ID/URL yang valid)", skipped)

    log.info("Apify: %s item valid untuk '%s'", len(results), keyword)
    return results[:max_products]
