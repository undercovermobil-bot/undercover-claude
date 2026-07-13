"""
main.py — Entry point CLI.

Contoh:
    python main.py init                  # buat tabel DB
    python main.py discover              # Scrape per keyword (ScraperAPI/Apify)
    python main.py discover-shops        # Scrape seluruh katalog toko kompetitor
    python main.py monitor               # Refresh harian + histori harga
    python main.py generate-products     # Generate my_products.csv dari xlsx
    python main.py compare               # Bandingkan vs my_products.csv
    python main.py generate-report       # Buat report.html comparison statis
    python main.py dashboard             # Buka dashboard Streamlit
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from utils import get_logger

log = get_logger("main")


def cmd_init(_args):
    import database
    database.init_db()
    print("✓ Database diinisialisasi.")


def cmd_login(_args):
    from auth import capture_login
    capture_login()


def cmd_discover(_args):
    from discovery import run_discovery
    summary = run_discovery()
    print(f"✓ Discovery selesai: {summary}")


def cmd_discover_shops(_args):
    from discovery import run_shop_discovery
    summary = run_shop_discovery()
    print(f"✓ Shop discovery selesai: {summary}")


def cmd_discover_chrome(args):
    from discovery import run_discovery_via_cdp
    cdp = getattr(args, "cdp", "http://localhost:9222")
    summary = run_discovery_via_cdp(cdp_url=cdp)
    print(f"✓ CDP discovery selesai: {summary}")


def cmd_monitor(_args):
    from monitor import run_monitor
    summary = run_monitor()
    print(f"✓ Monitoring selesai: {summary}")


def cmd_compare(_args):
    from compare import compare_products
    rows = compare_products()
    if not rows:
        print("Tidak ada hasil. Pastikan DB terisi & my_products.csv ada.")
        return
    for r in rows:
        flag = "  🚨 ALERT" if r["is_alert"] else ""
        print(
            f"{r['sku']:<12} {str(r['my_product_name'])[:35]:<35} "
            f"my={r['my_price']} comp={r['competitor_lowest_price']} "
            f"gap={r['price_gap']}{flag}"
        )


def cmd_generate_products(_args):
    from generate_products import extract_products, write_csv
    import config
    from pathlib import Path
    shopee_dir = config.BASE_DIR / "List Produk Undercover" / "List Produk Shopee"
    out_path   = config.MY_PRODUCTS_CSV
    products = extract_products(shopee_dir)
    n = write_csv(products, out_path)
    print(f"✓ {n} produk → {out_path}")


def cmd_generate_report(args):
    from generate_report import generate_html
    from pathlib import Path
    out = Path(args.out) if getattr(args, "out", None) else None
    path = generate_html(out)
    print(f"✓ Report disimpan: {path}")


def cmd_dashboard(_args):
    # Streamlit perlu dijalankan via CLI-nya sendiri.
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Undercover — Shopee market intelligence")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Inisialisasi database").set_defaults(func=cmd_init)
    sub.add_parser("login", help="Tangkap sesi login Shopee (wajib sebelum discover)").set_defaults(func=cmd_login)
    sub.add_parser("discover", help="Scrape produk per keyword").set_defaults(func=cmd_discover)
    sub.add_parser("discover-shops", help="Scrape seluruh katalog toko kompetitor (shops.txt)").set_defaults(func=cmd_discover_shops)
    chrome_p = sub.add_parser("discover-chrome", help="Scrape via Chrome asli yang sudah login Shopee (anti-bot bypass)")
    chrome_p.add_argument("--cdp", default="http://localhost:9222", help="CDP URL Chrome (default: localhost:9222)")
    chrome_p.set_defaults(func=cmd_discover_chrome)
    sub.add_parser("monitor", help="Tahap 2: refresh harian + histori").set_defaults(func=cmd_monitor)
    sub.add_parser("generate-products", help="Generate my_products.csv dari xlsx").set_defaults(func=cmd_generate_products)
    sub.add_parser("compare", help="Tahap 4: bandingkan vs my_products.csv").set_defaults(func=cmd_compare)
    rpt = sub.add_parser("generate-report", help="Buat report.html comparison statis")
    rpt.add_argument("--out", default=None, help="Path output (default: report.html)")
    rpt.set_defaults(func=cmd_generate_report)
    sub.add_parser("dashboard", help="Buka dashboard Streamlit").set_defaults(func=cmd_dashboard)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nDibatalkan.")
    except Exception as e:
        log.exception("Perintah gagal: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
