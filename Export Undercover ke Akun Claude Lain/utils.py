"""
utils.py — Helper lintas-modul: logging, retry, jeda acak, parsing harga & tanggal.
"""
from __future__ import annotations

import logging
import random
import re
import time
from datetime import date, datetime

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import config

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
_LOGGERS_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Logger dengan output ke console + file (config.LOG_FILE)."""
    global _LOGGERS_CONFIGURED
    if not _LOGGERS_CONFIGURED:
        config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        root = logging.getLogger("undercover")
        root.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

        console = logging.StreamHandler()
        console.setFormatter(fmt)
        root.addHandler(console)

        file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)

        root.propagate = False
        _LOGGERS_CONFIGURED = True

    return logging.getLogger(f"undercover.{name}")


# --------------------------------------------------------------------------
# Retry — dipakai sebagai decorator pada fungsi fetch yang rapuh
# --------------------------------------------------------------------------
def with_retry(func):
    """
    Decorator retry dengan exponential backoff.
    Param diambil dari config (MAX_RETRIES, RETRY_BACKOFF_BASE).
    """
    log = get_logger("retry")

    def _log_retry(retry_state):
        log.warning(
            "Retry %s/%s untuk %s setelah error: %s",
            retry_state.attempt_number,
            config.MAX_RETRIES,
            func.__name__,
            retry_state.outcome.exception() if retry_state.outcome else "?",
        )

    wrapped = retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=config.RETRY_BACKOFF_BASE, min=1, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=_log_retry,
        reraise=True,
    )(func)
    return wrapped


# --------------------------------------------------------------------------
# Jeda acak — agar pola request tidak terlihat seperti bot
# --------------------------------------------------------------------------
def polite_sleep() -> None:
    delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
    time.sleep(delay)


# --------------------------------------------------------------------------
# Parsing harga & angka
# --------------------------------------------------------------------------
def parse_price(raw) -> int | None:
    """
    Ubah representasi harga jadi integer Rupiah.

    Shopee API biasanya mengembalikan harga dalam satuan * 100000
    (mis. 150000 ribu rupiah => 15000000000). Heuristik:
    - int besar (>= 100000 dan habis dibagi 1000) -> dibagi 100000.
    - string "Rp1.500.000" / "1500000" -> ambil digit.
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        val = int(raw)
        # Format API Shopee: harga sudah dikali 100000
        if val >= 100_000 and val % 1000 == 0:
            return val // 100_000
        return val
    # String
    digits = re.sub(r"[^\d]", "", str(raw))
    return int(digits) if digits else None


def parse_sold_count(raw) -> int:
    """
    '1,2rb terjual' / '10k' / '1.2K' / 1200 -> int.
    Mengembalikan 0 jika tidak bisa diparse.
    """
    if raw is None:
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    s = str(raw).lower().replace("terjual", "").replace("+", "").strip()
    s = s.replace(",", ".")
    mult = 1
    if "rb" in s or "k" in s:
        mult = 1000
        s = s.replace("rb", "").replace("k", "")
    m = re.search(r"[\d.]+", s)
    if not m:
        return 0
    try:
        return int(float(m.group()) * mult)
    except ValueError:
        return 0


def today_str() -> str:
    return date.today().isoformat()


def now_str() -> str:
    return datetime.now().isoformat(timespec="seconds")
