"""
config.py — Pusat konfigurasi.

Semua nilai dibaca dari environment / file .env (via python-dotenv).
TIDAK ADA hardcode value bisnis di sini — hanya default aman jika env kosong.
Import `config` lalu akses sebagai atribut, mis. `config.DB_PATH`.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Muat .env dari root project (folder file ini)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key, str(default)).strip().lower()
    return val in {"1", "true", "yes", "on"}


def _resolve(path_str: str) -> Path:
    """Jadikan path absolut relatif terhadap root project."""
    p = Path(path_str)
    return p if p.is_absolute() else (BASE_DIR / p)


# --- Database ---
DB_PATH: Path = _resolve(_get("DB_PATH", "data/undercover.db"))

# --- Discovery / Monitoring ---
KEYWORDS_FILE: Path = _resolve(_get("KEYWORDS_FILE", "keywords.txt"))
SHOPS_FILE: Path    = _resolve(_get("SHOPS_FILE", "shops.txt"))
MAX_PRODUCTS_PER_KEYWORD: int = _get_int("MAX_PRODUCTS_PER_KEYWORD", 200)
MAX_PRODUCTS_PER_SHOP: int    = _get_int("MAX_PRODUCTS_PER_SHOP", 500)

# --- Scraping backends ---
SCRAPERAPI_KEY: str = _get("SCRAPERAPI_KEY", "")


def get_shops() -> list[tuple[str, str]]:
    """
    Baca shops.txt. Kembalikan list (shop_id, brand_name).
    Format per baris: shop_id | brand_name
    """
    if not SHOPS_FILE.exists():
        return []
    shops = []
    for ln in SHOPS_FILE.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [p.strip() for p in ln.split("|", 1)]
        if len(parts) == 2 and parts[0].isdigit():
            shops.append((parts[0], parts[1]))
    return shops


def get_keywords() -> list[str]:
    """
    Ambil daftar keyword. Prioritas:
    1. Isi KEYWORDS_FILE (satu keyword per baris) jika file ada & tidak kosong.
    2. Fallback ke env KEYWORDS (comma-separated).
    """
    if KEYWORDS_FILE.exists():
        lines = [
            ln.strip()
            for ln in KEYWORDS_FILE.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        if lines:
            return lines
    raw = _get("KEYWORDS", "")
    return [k.strip() for k in raw.split(",") if k.strip()]


# --- Scraping (Playwright) ---
SHOPEE_BASE_URL: str = _get("SHOPEE_BASE_URL", "https://shopee.co.id").rstrip("/")
HEADLESS: bool = _get_bool("HEADLESS", True)
REQUEST_DELAY_MIN: float = _get_float("REQUEST_DELAY_MIN", 2.0)
REQUEST_DELAY_MAX: float = _get_float("REQUEST_DELAY_MAX", 5.0)
PAGE_TIMEOUT_MS: int = _get_int("PAGE_TIMEOUT_MS", 30000)
MAX_RETRIES: int = _get_int("MAX_RETRIES", 3)
RETRY_BACKOFF_BASE: float = _get_float("RETRY_BACKOFF_BASE", 2.0)
PROXY_URL: str = _get("PROXY_URL", "")
USER_AGENT: str = _get(
    "USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
)
# Sesi login tersimpan (cookies) hasil `python main.py login`.
# WAJIB: Shopee menolak hasil pencarian untuk sesi anonim.
SHOPEE_STORAGE_STATE: Path = _resolve(_get("SHOPEE_STORAGE_STATE", "storage_state.json"))

# --- Compare ---
MY_PRODUCTS_CSV: Path = _resolve(_get("MY_PRODUCTS_CSV", "my_products.csv"))
PRICE_GAP_ALERT_THRESHOLD: int = _get_int("PRICE_GAP_ALERT_THRESHOLD", 20000)
FUZZY_MATCH_THRESHOLD: int = _get_int("FUZZY_MATCH_THRESHOLD", 80)

# --- Logging ---
LOG_LEVEL: str = _get("LOG_LEVEL", "INFO").upper()
LOG_FILE: Path = _resolve(_get("LOG_FILE", "logs/undercover.log"))
