"""
generate_products.py — Ekstrak my_products.csv dari xlsx Shopee.

Membaca semua file di 'List Produk Undercover/List Produk Shopee/*.xlsx',
mengambil produk unik (Kode Produk, Nama Produk, Harga terendah per produk),
dan menyimpan ke my_products.csv.

Tier otomatis dari nama produk:
  "Reguler"   → 1 layer
  "Premium"   → 3 layer
  "Exclusive" → 4 layer
"""
from __future__ import annotations

import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_TIER_MAP = {
    "exclusive": "4-layer",
    "premium":   "3-layer",
    "reguler":   "1-layer",
}


def _read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    strings: list[str] = []
    if "xl/sharedStrings.xml" in zf.namelist():
        tree = ET.parse(zf.open("xl/sharedStrings.xml"))
        for si in tree.getroot():
            t = "".join(
                c.text or ""
                for c in si.iter(f"{_NS}t")
            )
            strings.append(t)
    return strings


def _read_sheet_rows(zf: zipfile.ZipFile, sheet: str, strings: list[str]):
    tree = ET.parse(zf.open(sheet))
    for row in tree.getroot().iter(f"{_NS}row"):
        vals: list[str] = []
        for c in row:
            v = c.find(f"{_NS}v")
            t = c.get("t")
            if v is not None:
                vals.append(strings[int(v.text)] if t == "s" else (v.text or ""))
            else:
                vals.append("")
        yield vals


def _detect_tier(name: str) -> str:
    lower = name.lower()
    for key, label in _TIER_MAP.items():
        if key in lower:
            return label
    return "unknown"


def _extract_car_model(name: str) -> str:
    """Ekstrak nama mobil dari 'Undercover Autocare - Cover Mobil [CAR] [Tier]'."""
    m = re.search(
        r"cover mobil\s+(.+?)\s+(reguler|premium|exclusive)\s*$",
        name,
        re.IGNORECASE,
    )
    return m.group(1).strip() if m else name


def extract_products(shopee_dir: Path) -> dict[str, dict]:
    """
    Kembalikan dict product_name → {product_name, sku, price, tier, car_model}.
    Harga yang diambil adalah harga terendah per produk (dari semua variasi).
    """
    products: dict[str, dict] = {}

    for xlsx_path in sorted(shopee_dir.glob("*.xlsx")):
        try:
            with zipfile.ZipFile(xlsx_path) as zf:
                strings = _read_shared_strings(zf)
                sheet_names = [
                    n for n in zf.namelist()
                    if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")
                ]
                if not sheet_names:
                    continue
                sheet = sheet_names[0]

                header_found = False
                col_name = col_price = col_sku = -1

                for vals in _read_sheet_rows(zf, sheet, strings):
                    if not header_found:
                        # Cari baris header dengan kolom 'Nama Produk' / 'Harga'
                        row_lower = [v.lower() for v in vals]
                        if "nama produk" in row_lower and "harga" in row_lower:
                            col_name  = row_lower.index("nama produk")
                            col_price = row_lower.index("harga")
                            col_sku   = row_lower.index("sku") if "sku" in row_lower else -1
                            header_found = True
                        continue

                    name = vals[col_name].strip() if col_name < len(vals) else ""
                    price_raw = vals[col_price].strip() if col_price < len(vals) else ""
                    sku_val  = vals[col_sku].strip() if col_sku != -1 and col_sku < len(vals) else ""

                    if not name or "Undercover" not in name:
                        continue

                    try:
                        price = int(float(price_raw))
                    except (ValueError, TypeError):
                        continue
                    if price <= 0:
                        continue

                    if name not in products:
                        products[name] = {
                            "product_name": name,
                            "sku": sku_val or name[:20],
                            "price": price,
                            "tier": _detect_tier(name),
                            "car_model": _extract_car_model(name),
                        }
                    else:
                        # Simpan harga terendah (dari variasi termurah)
                        if price < products[name]["price"]:
                            products[name]["price"] = price
                            if sku_val:
                                products[name]["sku"] = sku_val
        except Exception as e:
            print(f"Skip {xlsx_path.name}: {e}", file=sys.stderr)

    return products


def write_csv(products: dict[str, dict], out_path: Path) -> int:
    rows = sorted(products.values(), key=lambda x: (x["tier"], x["car_model"]))
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["product_name", "sku", "price", "tier", "car_model"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    base = Path(__file__).parent
    shopee_dir = base / "List Produk Undercover" / "List Produk Shopee"
    out_path   = base / "my_products.csv"

    if not shopee_dir.exists():
        print(f"ERROR: Folder tidak ditemukan: {shopee_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Membaca dari: {shopee_dir}")
    products = extract_products(shopee_dir)

    if not products:
        print("Tidak ada produk ditemukan.", file=sys.stderr)
        sys.exit(1)

    n = write_csv(products, out_path)
    print(f"Selesai: {n} produk unik → {out_path}")

    # Preview
    tiers: dict[str, int] = {}
    for p in products.values():
        tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
    for tier, count in sorted(tiers.items()):
        print(f"  {tier}: {count} produk")


if __name__ == "__main__":
    main()
