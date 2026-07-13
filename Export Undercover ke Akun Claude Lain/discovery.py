"""
discovery.py — Tahap 1: kumpulkan produk kompetitor per keyword.

Strategi (setelah tuning terhadap Shopee live 2026):
  Shopee menolak panggilan API langsung & sesi anonim (error 90309999 + login
  wall). Jadi:
    1. Muat sesi login tersimpan (storage_state.json) — WAJIB. Buat via
       `python main.py login`.
    2. Buka halaman hasil pencarian di browser asli (headed/headless) dan
       INTERCEPT response XHR `search_items` yang dibuat halaman itu sendiri,
       sehingga membawa semua header/anti-bot token yang di-generate JavaScript.

  Titik yang mungkin masih perlu disesuaikan terhadap Shopee live ditandai
  `# >>> TUNING`. Logika scraping diisolasi di ShopeeScraper agar mudah diganti
  ke backend lain (API berbayar) tanpa menyentuh database/dashboard/compare.
"""
from __future__ import annotations

import math
from urllib.parse import quote

import config
import database
from utils import get_logger, parse_price, parse_sold_count, polite_sleep, today_str

log = get_logger("discovery")

_PER_PAGE = 60  # Shopee menampilkan ~60 item per halaman pencarian
_STEALTH = "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
# Kode error anti-bot Shopee (sesi belum login / terdeteksi bot).
_BLOCK_ERROR_CODES = {90309999}


class ShopeeBlocked(RuntimeError):
    """Diangkat saat Shopee menolak request (login wall / anti-bot)."""


class ShopeeScraper:
    """
    Backend scraping berbasis Camoufox (Firefox stealth) + sesi login.
    Camoufox jauh lebih sulit dideteksi Shopee daripada Chromium/Playwright biasa.

        with ShopeeScraper() as s:
            items = s.search("cover mobil", max_products=120)
    """

    def __init__(self):
        self._camoufox = None
        self._browser  = None
        self._context  = None
        self._page     = None

    def __enter__(self) -> "ShopeeScraper":
        from camoufox.sync_api import Camoufox

        launch_kwargs: dict = {
            "headless": config.HEADLESS,
            "locale":   ["id-ID", "en-US"],
        }
        if config.PROXY_URL:
            launch_kwargs["proxy"] = {"server": config.PROXY_URL}

        # Muat sesi login tersimpan
        if config.SHOPEE_STORAGE_STATE.exists():
            import json
            state = json.loads(config.SHOPEE_STORAGE_STATE.read_text())
            launch_kwargs["addons"] = []          # placeholder
            self._camoufox = Camoufox(**launch_kwargs)
            self._browser  = self._camoufox.__enter__()
            ctx_kwargs = {
                "storage_state": state,
                "viewport": {"width": 1366, "height": 900},
            }
            log.info("Camoufox: memuat sesi login dari %s", config.SHOPEE_STORAGE_STATE)
        else:
            log.warning(
                "Sesi login (%s) tidak ditemukan. Jalankan `python main.py login` dulu.",
                config.SHOPEE_STORAGE_STATE,
            )
            self._camoufox = Camoufox(**launch_kwargs)
            self._browser  = self._camoufox.__enter__()
            ctx_kwargs = {"viewport": {"width": 1366, "height": 900}}

        launch_kwargs.pop("addons", None)
        self._context = self._browser.new_context(**ctx_kwargs)
        self._page    = self._context.new_page()
        self._page.set_default_timeout(config.PAGE_TIMEOUT_MS)
        log.info("Camoufox browser siap")
        return self

    def __exit__(self, *exc):
        for closer in (self._context, self._browser):
            try:
                if closer:
                    closer.close()
            except Exception:
                pass
        if self._camoufox:
            try:
                self._camoufox.__exit__(None, None, None)
            except Exception:
                pass

    # ----------------------------------------------------------------
    def _warmup(self):
        """Kunjungi homepage sekali agar session cookies & token ter-refresh."""
        if getattr(self, "_warmed_up", False):
            return
        import time as _t
        log.info("Warmup: memuat Shopee homepage untuk refresh session...")
        self._page.goto(config.SHOPEE_BASE_URL, wait_until="domcontentloaded")
        _t.sleep(3)
        self._warmed_up = True
        # Cek apakah sudah login
        cookies = {c["name"] for c in self._context.cookies()}
        logged_in = bool({"SPC_U", "SPC_ST", "SPC_EC"} & cookies)
        log.info("Session cookies: %s | Logged in: %s", cookies & {"SPC_U","SPC_F","SPC_EC","SPC_ST"}, logged_in)

    def _fetch_search_page(self, keyword: str, page_index: int) -> dict:
        """
        Intercept XHR search_items yang dibuat oleh Shopee sendiri.
        Baca body SEGERA di callback (fix timing bug 'No resource found').
        """
        import time as _t
        import json as _json

        self._warmup()

        url = f"{config.SHOPEE_BASE_URL}/search?keyword={quote(keyword)}&page={page_index}"
        captured: dict = {}

        def on_response(response):
            if "search_items" in response.url and "data" not in captured:
                try:
                    body = response.body()          # baca SEGERA sebelum freed
                    captured["data"] = _json.loads(body)
                except Exception as e:
                    captured["error"] = str(e)

        self._page.on("response", on_response)
        try:
            self._page.goto(url, wait_until="domcontentloaded")
            for _ in range(20):                     # tunggu max 20 detik
                if "data" in captured or "error" in captured:
                    break
                _t.sleep(1)
        finally:
            self._page.remove_listener("response", on_response)

        if "error" in captured:
            raise RuntimeError(f"Baca response gagal: {captured['error']}")
        if "data" not in captured:
            raise RuntimeError(f"Tidak ada XHR search_items dalam 20 detik untuk '{keyword}'")

        data = captured["data"]
        if not isinstance(data, dict):
            raise RuntimeError(f"Response bukan dict: {type(data)}")

        err = data.get("error")
        if err in _BLOCK_ERROR_CODES:
            raise ShopeeBlocked(
                f"Shopee menolak (error {err}) untuk '{keyword}'. "
                f"Sesi login mungkin kadaluarsa — jalankan `python main.py login`."
            )
        return data

    def search(self, keyword: str, max_products: int) -> list[dict]:
        """Kumpulkan hingga `max_products` produk untuk satu keyword."""
        pages_needed = math.ceil(max_products / _PER_PAGE)
        collected: list[dict] = []

        for page_index in range(pages_needed):
            if len(collected) >= max_products:
                break
            try:
                data = self._fetch_search_page(keyword, page_index)
            except ShopeeBlocked:
                raise  # hentikan total — percuma lanjut tanpa sesi valid
            except Exception as e:
                log.error("Gagal page %s '%s': %s", page_index, keyword, e)
                break

            items = _extract_items(data, keyword)
            if not items:
                log.info("Tidak ada item lagi untuk '%s' (page %s).", keyword, page_index)
                break

            collected.extend(items)
            log.info(
                "Keyword '%s' page %s: +%s (total %s/%s)",
                keyword, page_index, len(items), len(collected), max_products,
            )
            polite_sleep()

        return collected[:max_products]


# --------------------------------------------------------------------------
# Ekstraksi — satu-satunya tempat yang tahu bentuk JSON Shopee.
# >>> TUNING: sesuaikan nama field di sini jika struktur berubah (cek dengan
#     `scratchpad/probe.py` setelah login).
# --------------------------------------------------------------------------
def _extract_items(data: dict, keyword: str) -> list[dict]:
    if not isinstance(data, dict):
        return []
    raw_items = data.get("items") or []
    out: list[dict] = []
    for it in raw_items:
        basic = it.get("item_basic") or it.get("basic") or it
        itemid = basic.get("itemid")
        shopid = basic.get("shopid")
        if itemid is None or shopid is None:
            continue

        name = basic.get("name", "")
        slug = name.replace(" ", "-")[:80]
        url = f"{config.SHOPEE_BASE_URL}/{slug}-i.{shopid}.{itemid}"

        rating = None
        rating_obj = basic.get("item_rating") or {}
        if isinstance(rating_obj, dict):
            rating = rating_obj.get("rating_star")

        out.append(
            {
                "product_id": f"{shopid}_{itemid}",
                "shop_name": basic.get("shop_name") or basic.get("shop_location") or "",
                "product_name": name,
                "product_url": url,
                "current_price": parse_price(basic.get("price")),
                "original_price": parse_price(basic.get("price_before_discount")),
                "rating": round(rating, 2) if isinstance(rating, (int, float)) else None,
                "sold_count": parse_sold_count(
                    basic.get("historical_sold") or basic.get("sold")
                ),
                "search_keyword": keyword,
                "crawl_date": today_str(),
            }
        )
    return out


# --------------------------------------------------------------------------
# Orkestrasi tahap 1
# --------------------------------------------------------------------------
def _backend() -> str:
    """Tentukan backend aktif: 'scraperapi' | 'apify' | 'playwright'."""
    import os
    if os.getenv("SCRAPERAPI_KEY", "").strip():
        return "scraperapi"
    if os.getenv("APIFY_TOKEN", "").strip():
        return "apify"
    return "playwright"


def run_discovery(keywords: list[str] | None = None) -> dict[str, int]:
    """Scrape produk per keyword dan simpan ke DB."""
    database.init_db()
    keywords = keywords or config.get_keywords()
    if not keywords:
        log.warning("Tidak ada keyword. Isi KEYWORDS_FILE atau env KEYWORDS.")
        return {}

    log.info("Mulai discovery untuk %s keyword: %s", len(keywords), keywords)
    grand_total: dict[str, int] = {"inserted": 0, "updated": 0, "unchanged": 0}
    backend = _backend()
    log.info("Backend: %s", backend)

    if backend == "scraperapi":
        import scraperapi_backend as sa
        for kw in keywords:
            try:
                products = sa.search_keyword(kw, config.MAX_PRODUCTS_PER_KEYWORD)
            except Exception as e:
                log.error("ScraperAPI gagal untuk '%s': %s", kw, e)
                continue
            summary = database.bulk_upsert(products)
            log.info("Keyword '%s' selesai: %s", kw, summary)
            for k, v in summary.items():
                grand_total[k] = grand_total.get(k, 0) + v

    elif backend == "apify":
        import apify_backend
        log.info("Actor: %s", apify_backend.ACTOR_ID)
        for kw in keywords:
            try:
                products = apify_backend.search(kw, config.MAX_PRODUCTS_PER_KEYWORD)
            except Exception as e:
                log.error("Apify gagal untuk '%s': %s", kw, e)
                continue
            summary = database.bulk_upsert(products)
            log.info("Keyword '%s' selesai: %s", kw, summary)
            for k, v in summary.items():
                grand_total[k] = grand_total.get(k, 0) + v

    else:
        log.warning("Tidak ada backend tersedia. Mencoba Playwright (kemungkinan diblok Shopee).")
        with ShopeeScraper() as scraper:
            for kw in keywords:
                try:
                    products = scraper.search(kw, config.MAX_PRODUCTS_PER_KEYWORD)
                except ShopeeBlocked as e:
                    log.error("%s", e)
                    break
                summary = database.bulk_upsert(products)
                log.info("Keyword '%s' selesai: %s", kw, summary)
                for k, v in summary.items():
                    grand_total[k] = grand_total.get(k, 0) + v

    log.info("Discovery selesai. Total: %s", grand_total)
    return grand_total


def run_shop_discovery(shops: list[tuple[str, str]] | None = None) -> dict[str, int]:
    """
    Scrape semua produk dari toko kompetitor (per shop_id).
    Lebih lengkap dari keyword search — tangkap seluruh katalog toko.

    shops: list of (shop_id, brand_name). Jika None, baca dari shops.txt.
    """
    database.init_db()
    shops = shops or config.get_shops()
    if not shops:
        log.warning("Tidak ada toko di shops.txt.")
        return {}

    backend = _backend()
    if backend != "scraperapi":
        log.error("Shop scraping hanya tersedia via ScraperAPI. Set SCRAPERAPI_KEY di .env.")
        return {}

    import scraperapi_backend as sa

    log.info("Mulai shop discovery untuk %s toko via ScraperAPI", len(shops))
    grand_total: dict[str, int] = {"inserted": 0, "updated": 0, "unchanged": 0}

    for shop_id, brand_name in shops:
        log.info("Scraping toko: %s (%s)", brand_name, shop_id)
        try:
            products = sa.search_shop(shop_id, brand_name, config.MAX_PRODUCTS_PER_SHOP)
        except Exception as e:
            log.error("Shop %s (%s) gagal: %s", shop_id, brand_name, e)
            continue
        summary = database.bulk_upsert(products)
        log.info("Toko '%s' selesai: %s", brand_name, summary)
        for k, v in summary.items():
            grand_total[k] = grand_total.get(k, 0) + v

    log.info("Shop discovery selesai. Total: %s", grand_total)
    return grand_total


def run_discovery_via_cdp(
    keywords: list[str] | None = None,
    cdp_url: str = "http://localhost:9222",
) -> dict[str, int]:
    """
    Scrape via Chrome asli yang sudah login Shopee.

    Setup (sekali saja):
      1. Tutup semua jendela Chrome
      2. Buka Chrome dengan debugging:
           /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
             --remote-debugging-port=9222
      3. Login ke Shopee di Chrome tersebut
      4. Jalankan: python main.py discover-chrome

    Chrome yang sudah kamu pakai sehari-hari — Shopee tidak bisa bedakan dari
    browsing normal.
    """
    from playwright.sync_api import sync_playwright
    import time as _t

    database.init_db()
    keywords = keywords or config.get_keywords()
    if not keywords:
        log.warning("Tidak ada keyword.")
        return {}

    log.info("Connecting ke Chrome via CDP: %s", cdp_url)
    grand_total: dict[str, int] = {"inserted": 0, "updated": 0, "unchanged": 0}

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            log.error(
                "Tidak bisa connect ke Chrome (%s). "
                "Pastikan Chrome sudah dibuka dengan --remote-debugging-port=9222. "
                "Error: %s",
                cdp_url, e,
            )
            return {}

        contexts = browser.contexts
        ctx  = contexts[0] if contexts else browser.new_context()
        pages = ctx.pages
        page = pages[0] if pages else ctx.new_page()

        log.info("CDP terhubung. Warmup Shopee homepage...")
        page.goto(config.SHOPEE_BASE_URL, wait_until="domcontentloaded")
        _t.sleep(3)

        cookies = {c["name"] for c in ctx.cookies()}
        logged_in = bool({"SPC_U", "SPC_ST", "SPC_EC"} & cookies)
        log.info("Session cookies: %s | Logged in: %s", cookies & {"SPC_U","SPC_F","SPC_EC","SPC_ST"}, logged_in)
        if not logged_in:
            log.error("Belum login di Chrome. Login ke Shopee dulu lalu jalankan ulang.")
            return {}

        for kw in keywords:
            newest  = 0
            limit   = 60
            kw_total = 0

            while True:
                api_path = (
                    f"/api/v4/search/search_items"
                    f"?keyword={quote(kw)}&limit={limit}&newest={newest}"
                    f"&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
                )
                try:
                    data = page.evaluate(f"""async () => {{
                        const csrfToken = document.cookie.split(';')
                            .find(c => c.trim().startsWith('csrftoken='))
                            ?.split('=')[1] || '';
                        const r = await fetch("{api_path}", {{
                            credentials: "include",
                            headers: {{
                                "x-requested-with": "XMLHttpRequest",
                                "accept": "application/json",
                                "x-csrftoken": csrfToken
                            }}
                        }});
                        return await r.json();
                    }}""")
                except Exception as e:
                    log.error("CDP fetch gagal untuk '%s': %s", kw, e)
                    break

                if not isinstance(data, dict):
                    log.warning("Response bukan dict untuk '%s'", kw)
                    break

                err = data.get("error")
                if err in _BLOCK_ERROR_CODES:
                    log.error("Shopee menolak (error %s) untuk '%s'", err, kw)
                    break

                items = _extract_items(data, kw)
                if not items:
                    break

                products = []
                for raw in items:
                    basic = raw if "item_basic" not in raw else raw["item_basic"]
                    products.append(raw)  # _extract_items sudah map

                summary = database.bulk_upsert(items)
                kw_total += sum(summary.values())
                log.info("CDP keyword '%s' newest=%s: +%s", kw, newest, len(items))
                for k, v in summary.items():
                    grand_total[k] = grand_total.get(k, 0) + v

                if len(items) < limit:
                    break
                newest += limit
                polite_sleep()

            log.info("Keyword '%s' selesai (total produk baru: %s)", kw, kw_total)

    log.info("CDP discovery selesai. Total: %s", grand_total)
    return grand_total


if __name__ == "__main__":
    run_discovery()
