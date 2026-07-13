"""
database.py — Lapisan SQLite.

Dua tabel:
  - products       : satu baris per produk (snapshot terbaru). Dedup via product_id.
  - price_history  : append-only. Satu baris tiap kali ada perubahan harga/diskon/
                     rating/terjual. Histori lama TIDAK PERNAH dihapus.

Identifier utama = product_id (di-derive dari URL Shopee bila perlu).
Jika produk sudah ada -> update kolom terbaru, jangan buat baris baru.
"""
from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from typing import Iterable

import config
from utils import get_logger, now_str, today_str

log = get_logger("database")

# Kolom yang dianggap "berubah" -> memicu snapshot histori baru.
_TRACKED_FIELDS = ("current_price", "original_price", "rating", "sold_count")


# --------------------------------------------------------------------------
# Koneksi
# --------------------------------------------------------------------------
@contextmanager
def get_connection():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Buat tabel & index jika belum ada. Idempotent."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id      TEXT PRIMARY KEY,
                shop_name       TEXT,
                product_name    TEXT,
                product_url     TEXT UNIQUE,
                current_price   INTEGER,
                original_price  INTEGER,
                rating          REAL,
                sold_count      INTEGER,
                is_mall         INTEGER DEFAULT 0,
                search_keyword  TEXT,
                first_seen_date TEXT,
                crawl_date      TEXT,
                updated_at      TEXT
            );

            CREATE TABLE IF NOT EXISTS price_history (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id     TEXT NOT NULL,
                current_price  INTEGER,
                original_price INTEGER,
                rating         REAL,
                sold_count     INTEGER,
                crawl_date     TEXT,
                recorded_at    TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            CREATE INDEX IF NOT EXISTS idx_products_keyword
                ON products(search_keyword);
            CREATE INDEX IF NOT EXISTS idx_history_product
                ON price_history(product_id);
            CREATE INDEX IF NOT EXISTS idx_history_date
                ON price_history(crawl_date);
            """
        )
    # Migrasi: tambah kolom is_mall jika belum ada (existing DB)
    with get_connection() as conn:
        try:
            conn.execute("ALTER TABLE products ADD COLUMN is_mall INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # kolom sudah ada

    log.info("Database siap di %s", config.DB_PATH)


# --------------------------------------------------------------------------
# Identifier
# --------------------------------------------------------------------------
def derive_product_id(product: dict) -> str | None:
    """
    Ambil product_id stabil. Prioritas:
    1. field 'product_id' yang sudah ada (mis. f"{shopid}_{itemid}").
    2. Pola URL Shopee: .../i.{shopid}.{itemid} atau ...-i.{shopid}.{itemid}.
    3. Fallback: URL penuh (dinormalkan).
    """
    pid = product.get("product_id")
    if pid:
        return str(pid)

    url = product.get("product_url") or ""
    m = re.search(r"i\.(\d+)\.(\d+)", url)
    if m:
        return f"{m.group(1)}_{m.group(2)}"

    return url or None


# --------------------------------------------------------------------------
# Upsert + histori
# --------------------------------------------------------------------------
def _record_snapshot(conn, product_id: str, p: dict) -> None:
    conn.execute(
        """
        INSERT INTO price_history
            (product_id, current_price, original_price, rating, sold_count,
             crawl_date, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_id,
            p.get("current_price"),
            p.get("original_price"),
            p.get("rating"),
            p.get("sold_count"),
            p.get("crawl_date") or today_str(),
            now_str(),
        ),
    )


def upsert_product(product: dict) -> str:
    """
    Insert produk baru atau update yang sudah ada.

    Mengembalikan salah satu: 'inserted' | 'updated' | 'unchanged'.
    - inserted  : produk baru -> tulis baris products + snapshot histori awal.
    - updated   : ada field tracked yang berubah -> update + snapshot histori baru.
    - unchanged : tidak ada perubahan tracked -> hanya refresh crawl_date.
    """
    product_id = derive_product_id(product)
    if not product_id:
        log.warning("Lewati produk tanpa identifier: %s", product.get("product_name"))
        return "unchanged"

    crawl_date = product.get("crawl_date") or today_str()

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()

        if existing is None:
            conn.execute(
                """
                INSERT INTO products
                    (product_id, shop_name, product_name, product_url,
                     current_price, original_price, rating, sold_count,
                     is_mall, search_keyword, first_seen_date, crawl_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    product.get("shop_name"),
                    product.get("product_name"),
                    product.get("product_url"),
                    product.get("current_price"),
                    product.get("original_price"),
                    product.get("rating"),
                    product.get("sold_count"),
                    1 if product.get("is_mall") else 0,
                    product.get("search_keyword"),
                    crawl_date,
                    crawl_date,
                    now_str(),
                ),
            )
            _record_snapshot(conn, product_id, {**product, "crawl_date": crawl_date})
            return "inserted"

        # Sudah ada -> cek perubahan field tracked
        changed = any(
            product.get(f) is not None and product.get(f) != existing[f]
            for f in _TRACKED_FIELDS
        )

        conn.execute(
            """
            UPDATE products SET
                shop_name      = COALESCE(?, shop_name),
                product_name   = COALESCE(?, product_name),
                current_price  = COALESCE(?, current_price),
                original_price = COALESCE(?, original_price),
                rating         = COALESCE(?, rating),
                sold_count     = COALESCE(?, sold_count),
                is_mall        = COALESCE(?, is_mall),
                search_keyword = COALESCE(?, search_keyword),
                crawl_date     = ?,
                updated_at     = ?
            WHERE product_id = ?
            """,
            (
                product.get("shop_name"),
                product.get("product_name"),
                product.get("current_price"),
                product.get("original_price"),
                product.get("rating"),
                product.get("sold_count"),
                1 if product.get("is_mall") else None,
                product.get("search_keyword"),
                crawl_date,
                now_str(),
                product_id,
            ),
        )

        if changed:
            _record_snapshot(conn, product_id, {**product, "crawl_date": crawl_date})
            return "updated"
        return "unchanged"


def bulk_upsert(products: Iterable[dict]) -> dict[str, int]:
    """Upsert banyak produk. Mengembalikan ringkasan jumlah per status."""
    summary = {"inserted": 0, "updated": 0, "unchanged": 0}
    for p in products:
        status = upsert_product(p)
        summary[status] = summary.get(status, 0) + 1
    return summary


# --------------------------------------------------------------------------
# Query
# --------------------------------------------------------------------------
def get_all_products(keyword: str | None = None) -> list[dict]:
    sql = "SELECT * FROM products"
    params: tuple = ()
    if keyword:
        sql += " WHERE search_keyword = ?"
        params = (keyword,)
    sql += " ORDER BY current_price ASC"
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def get_keywords_in_db() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT search_keyword FROM products "
            "WHERE search_keyword IS NOT NULL ORDER BY search_keyword"
        ).fetchall()
    return [r["search_keyword"] for r in rows]


def get_price_history(product_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM price_history WHERE product_id = ? "
            "ORDER BY recorded_at ASC",
            (product_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_latest_two_snapshots(product_id: str) -> list[dict]:
    """Dua snapshot histori terakhir — untuk hitung selisih vs sebelumnya."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM price_history WHERE product_id = ? "
            "ORDER BY recorded_at DESC LIMIT 2",
            (product_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_products() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
