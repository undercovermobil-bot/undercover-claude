"""
scraperapi_backend.py — Backend scraping via ScraperAPI API endpoint mode.

ScraperAPI menjalankan Chrome headless di server mereka, menangani anti-bot
secara transparan, dan mempertahankan cookies dalam satu session.

Strategi:
  1. Kunjungi Shopee homepage dalam session → JS jalan → cookies ter-set
  2. Panggil Shopee API URL dalam session yang sama → cookies dikirim → dapat JSON

Free tier: 5.000 kredit/bulan (render=true = 5 kredit/request).
Daftar: https://www.scraperapi.com/
"""
from __future__ import annotations

import os
import time
from urllib.parse import quote

import requests

import config
from utils import get_logger, parse_price, parse_sold_count, today_str

log = get_logger("scraperapi")

_SCRAPERAPI_BASE = "https://api.scraperapi.com/"
_SHOPEE_BASE     = "https://shopee.co.id"
_SHOPEE_SEARCH   = f"{_SHOPEE_BASE}/api/v4/search/search_items"


def _get_key() -> str:
    key = os.getenv("SCRAPERAPI_KEY", "").strip()
    if not key:
        raise RuntimeError("SCRAPERAPI_KEY tidak ditemukan di .env")
    return key


def _init_session(session_id: int) -> bool:
    """
    Kunjungi Shopee homepage agar cookies anti-bot ter-set dalam session ini.
    Wajib dipanggil sekali sebelum request API dalam session yang sama.
    """
    log.info("Init session %s: kunjungi Shopee homepage...", session_id)
    try:
        resp = requests.get(
            _SCRAPERAPI_BASE,
            params={
                "api_key":        _get_key(),
                "url":            _SHOPEE_BASE + "/",
                "render":         "true",
                "country_code":   "id",
                "device_type":    "desktop",
                "session_number": session_id,
            },
            timeout=120,
        )
        ok = resp.status_code == 200
        log.info("Session %s init %s", session_id, "OK" if ok else f"gagal HTTP {resp.status_code}")
        return ok
    except Exception as e:
        log.warning("Session init error: %s", e)
        return False


def _get(url: str, session_id: int = 1, retries: int = 3) -> dict | None:
    """
    GET ke URL Shopee via ScraperAPI API mode dalam session tertentu.
    Mengembalikan parsed JSON atau None.
    """
    key = _get_key()
    for attempt in range(retries):
        try:
            resp = requests.get(
                _SCRAPERAPI_BASE,
                params={
                    "api_key":        key,
                    "url":            url,
                    "render":         "true",
                    "country_code":   "id",
                    "device_type":    "desktop",
                    "session_number": session_id,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, dict) and "error" not in data:
                        return data
                    err = data.get("error") if isinstance(data, dict) else "?"
                    log.warning("Shopee error response: %s", err)
                except Exception:
                    log.warning("Response bukan JSON (attempt %s) — mungkin HTML/blocked", attempt + 1)
                return None
            log.warning("ScraperAPI HTTP %s untuk %s (attempt %s)",
                        resp.status_code, url[:80], attempt + 1)
        except Exception as e:
            log.warning("Request gagal (attempt %s): %s", attempt + 1, e)

        if attempt < retries - 1:
            time.sleep(2 ** attempt)

    return None


def _map_item(raw: dict, search_keyword: str, shop_name: str = "") -> dict | None:
    """Map satu item JSON Shopee → skema DB."""
    basic = raw.get("item_basic") or raw.get("basic") or raw

    itemid = basic.get("itemid") or basic.get("item_id")
    shopid = basic.get("shopid") or basic.get("shop_id")
    if not itemid or not shopid:
        return None

    name = (basic.get("name") or "").strip()
    if not name:
        return None

    slug = name.replace(" ", "-")[:80]
    url  = f"{_SHOPEE_BASE}/{slug}-i.{shopid}.{itemid}"

    rating = None
    rating_obj = basic.get("item_rating") or {}
    if isinstance(rating_obj, dict):
        rating = rating_obj.get("rating_star")

    is_mall = bool(
        basic.get("item_type") == 2
        or basic.get("shoptype") in (1, 2)
        or basic.get("is_official_shop")
    )

    return {
        "product_id":     f"{shopid}_{itemid}",
        "shop_name":      shop_name or basic.get("shop_location") or "",
        "product_name":   name,
        "product_url":    url,
        "current_price":  parse_price(basic.get("price")),
        "original_price": parse_price(basic.get("price_before_discount")),
        "rating":         round(rating, 2) if isinstance(rating, (int, float)) else None,
        "sold_count":     parse_sold_count(basic.get("historical_sold") or basic.get("sold")),
        "is_mall":        is_mall,
        "search_keyword": search_keyword,
        "crawl_date":     today_str(),
    }


# ── Keyword search ────────────────────────────────────────────────────────────

def search_keyword(keyword: str, max_products: int | None = None) -> list[dict]:
    """Scrape Shopee search results untuk keyword tertentu via ScraperAPI."""
    max_products = max_products or config.MAX_PRODUCTS_PER_KEYWORD
    limit        = 60
    newest       = 0
    results: list[dict] = []

    # Session unik per keyword agar tidak konflik
    session_id = (abs(hash(keyword)) % 9000) + 1000
    _init_session(session_id)

    while len(results) < max_products:
        url = (
            f"{_SHOPEE_SEARCH}"
            f"?keyword={quote(keyword)}&limit={limit}&newest={newest}"
            f"&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
        )
        data = _get(url, session_id=session_id)
        if not data:
            break

        items = data.get("items") or []
        if not items:
            break

        batch = []
        for raw in items:
            mapped = _map_item(raw, search_keyword=keyword)
            if mapped:
                batch.append(mapped)

        results.extend(batch)
        log.info("Keyword '%s' newest=%s: +%s produk (total %s)",
                 keyword, newest, len(batch), len(results))

        if len(items) < limit:
            break
        newest += limit

    return results[:max_products]


# ── Shop scraping ─────────────────────────────────────────────────────────────

def search_shop(shop_id: str | int, brand_name: str = "", max_products: int = 500) -> list[dict]:
    """
    Scrape semua produk dari toko kompetitor berdasarkan shop_id Shopee.

    shop_id   : integer shop ID (dari URL toko atau product_id di DB)
    brand_name: nama brand untuk dashboard (mis. "Fusion R")
    """
    limit    = 60
    newest   = 0
    results: list[dict] = []
    kw       = f"shop:{shop_id}"

    session_id = (abs(hash(str(shop_id))) % 9000) + 1000
    _init_session(session_id)

    while len(results) < max_products:
        url = (
            f"{_SHOPEE_SEARCH}"
            f"?shopid={shop_id}&limit={limit}&newest={newest}"
            f"&order=desc&page_type=shop&scenario=PAGE_OTHERS"
        )
        data = _get(url, session_id=session_id)
        if not data:
            break

        items = data.get("items") or []
        if not items:
            break

        batch = []
        for raw in items:
            mapped = _map_item(raw, search_keyword=kw, shop_name=brand_name)
            if mapped:
                batch.append(mapped)

        results.extend(batch)
        log.info("Shop %s (%s) newest=%s: +%s produk (total %s)",
                 shop_id, brand_name or "?", newest, len(batch), len(results))

        if len(items) < limit:
            break
        newest += limit

    log.info("Shop %s selesai: %s produk total", shop_id, len(results))
    return results[:max_products]
