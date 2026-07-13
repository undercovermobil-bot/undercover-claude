"""
compare.py — Tahap 4: bandingkan produk saya vs kompetitor.

Strategi matching (urutan prioritas):
  1. Exact car_model match + tier match — paling akurat
  2. Car model fuzzy match + tier match
  3. Fallback fuzzy nama produk penuh (dengan price-ratio guard)

Tier produk kita (dari my_products.csv, diisi generate_products.py):
  Reguler  → 1-layer
  Premium  → 3-layer
  Exclusive → 4-layer

Tier kompetitor (dari _detect_competitor_tier):
  Dideteksi dari JUMLAH LAYER di nama produk, bukan keyword brand.
  "3 layer" / "3 lapis" → 3-layer
  "4 layer" / "4 lapis" → 4-layer
  Tafeta / tidak disebutkan → default 1-layer
"""
from __future__ import annotations

import csv
import re

from rapidfuzz import fuzz, process

import config
import database
from utils import get_logger, parse_price

log = get_logger("compare")

_BRAND_KW_MAP = {
    "fusion r":     "Fusion R",
    "h2r":          "H2R Cover",
    "coversuper":   "Coversuper",
    "autocover":    "Autocover Indonesia",
}

# Rasio harga minimum kompetitor vs produk kita — cegah false match antar tier
_MIN_PRICE_RATIO = 0.25

# Kata-kata bukan nama mobil yang perlu dibuang dari hasil ekstraksi
_NOISE_WORDS = re.compile(
    r"\b(?:anti|debu|uv|waterproof|tebal|tipis|body|cover|sarung|penutup"
    r"|pelindung|fusion|h2r|coversuper|autocover|waterproff|premium|exclusive|reguler)\b",
    re.IGNORECASE,
)
# Kata-kata yang menandakan segmen bukan nama mobil
_PRODUCT_WORDS = re.compile(
    r"\b(?:anti|debu|uv|waterproof|cover|sarung|body|penutup|mobil"
    r"|tipis|tebal|layer|lapis|ply|pelindung)\b",
    re.IGNORECASE,
)


def _brand_from_keyword(kw: str) -> str:
    lower = kw.lower()
    for token, brand in _BRAND_KW_MAP.items():
        if token in lower:
            return brand
    return ""


# ── Tier detection ────────────────────────────────────────────────────────────

def _detect_tier_from_name(name: str) -> str | None:
    """Tier dari nama produk KITA (Reguler/Premium/Exclusive = brand-specific)."""
    lower = name.lower()
    if "exclusive" in lower or re.search(r"\b4\s*(?:layer|lapis|ply)\b", lower):
        return "4-layer"
    if "premium" in lower or re.search(r"\b3\s*(?:layer|lapis|ply)\b", lower):
        return "3-layer"
    if "reguler" in lower or re.search(r"\b1\s*(?:layer|lapis|ply)\b", lower) or "tafeta" in lower:
        return "1-layer"
    return None


def _detect_competitor_tier(name: str) -> str:
    """
    Tier kompetitor dari jumlah layer — BUKAN keyword brand.
    Default 1-layer karena cover tanpa keterangan biasanya single layer / tafeta.
    """
    lower = name.lower()
    if re.search(r"\b4\s*(?:layer|lapis|ply)\b", lower):
        return "4-layer"
    if re.search(r"\b3\s*(?:layer|lapis|ply)\b", lower):
        return "3-layer"
    if re.search(r"\b2\s*(?:layer|lapis|ply)\b", lower):
        return "3-layer"  # 2-layer lebih dekat ke premium dari reguler
    return "1-layer"


# ── Car model extraction ──────────────────────────────────────────────────────

def _extract_car_model_from_name(name: str) -> str:
    """
    Ekstrak tipe mobil dari nama produk.
    Mendukung berbagai format:
      - "Cover Mobil Toyota Avanza Exclusive"          → Toyota Avanza
      - "Cover Mobil Toyota Avanza 4 Layer"            → Toyota Avanza
      - "Cover Mobil h2R - Cover Mobil Honda Jazz"     → Honda Jazz
      - "Fusion R Cover Sarung Mobil 4 Layer - Honda Brio"  → Honda Brio
    """
    # Pattern 1: "cover [sarung] mobil [car] [tier/layer]$"
    m = re.search(
        r"cover\s+(?:sarung\s+)?mobil\s+(.+?)"
        r"\s+(?:reguler|premium|exclusive|(?:\d+)\s+(?:layer|lapis|ply))\s*$",
        name, re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()

    # Pattern 2: cari "cover [sarung] mobil [car]" di tiap segmen (pisahkan tanda hubung)
    segments = re.split(r"\s*[-–]\s*", name)
    for seg in segments:
        m2 = re.search(
            r"cover\s+(?:sarung\s+)?mobil\s+(.+?)(?=\s*(?:\d+\s+(?:layer|lapis|ply)|$))",
            seg, re.IGNORECASE,
        )
        if m2:
            car = m2.group(1).split(",")[0].strip()
            # Buang layer count yang ikut terbawa ("4 Layer", "3 lapis", dll.)
            car = re.sub(r"\b\d+\s*(?:layer|lapis|ply)\b", "", car, flags=re.IGNORECASE)
            car = _NOISE_WORDS.sub("", car).strip()
            car = re.sub(r"\s{2,}", " ", car).strip()
            if car and len(car.split()) <= 6 and len(car) > 2:
                return car

    # Pattern 3: segmen terakhir yang terlihat seperti nama mobil
    # (tidak mengandung kata produk — untuk format "Brand Product - Car Model")
    for seg in reversed(segments[1:]):  # lewati segmen pertama (biasanya brand)
        seg_clean = seg.split(",")[0].strip()
        if not _PRODUCT_WORDS.search(seg_clean) and seg_clean:
            words = seg_clean.split()
            if 1 <= len(words) <= 5:
                return seg_clean

    return ""


# ── CSV loader ────────────────────────────────────────────────────────────────

def load_my_products(csv_path=None) -> list[dict]:
    """Baca my_products.csv. Kolom wajib: product_name, sku, price."""
    path = csv_path or config.MY_PRODUCTS_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"File produk saya tidak ditemukan: {path}. "
            f"Jalankan: python main.py generate-products"
        )
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = {h.strip() for h in (reader.fieldnames or [])}
        missing = {"product_name", "sku", "price"} - fieldnames
        if missing:
            raise ValueError(f"Kolom CSV kurang: {missing}")
        for r in reader:
            tier      = (r.get("tier") or "").strip() or _detect_tier_from_name(r.get("product_name", ""))
            car_model = (r.get("car_model") or "").strip() or _extract_car_model_from_name(r.get("product_name", ""))
            rows.append({
                "product_name": (r["product_name"] or "").strip(),
                "sku":          (r["sku"] or "").strip(),
                "price":        parse_price(r["price"]),
                "tier":         tier or None,
                "car_model":    car_model or None,
            })
    return rows


# ── Compare ───────────────────────────────────────────────────────────────────

def compare_products(keyword: str | None = None) -> list[dict]:
    """
    Untuk tiap produk kita, cari kompetitor termurah yang paling cocok.

    Tier kompetitor dideteksi dari LAYER COUNT (bukan keyword brand seperti
    premium/exclusive). Default 1-layer jika tidak ada keterangan layer.

    Mengembalikan list dict per produk:
      sku, my_product_name, my_price, tier, car_model,
      matched_competitor, competitor_brand, competitor_shop, competitor_url,
      match_score, competitor_lowest_price, price_gap, is_alert
    """
    my_products = load_my_products()
    competitors = database.get_all_products(keyword=keyword)
    if not competitors:
        log.warning("Tidak ada data kompetitor. Jalankan discovery dulu.")
        return []

    # Pra-proses kompetitor: tier dari layer count, bukan nama tier brand
    for c in competitors:
        c["_tier"]      = _detect_competitor_tier(c.get("product_name") or "")
        c["_car_model"] = _extract_car_model_from_name(c.get("product_name") or "")

    comp_names = [c["product_name"] or "" for c in competitors]
    results: list[dict] = []

    for mine in my_products:
        name    = mine["product_name"]
        my_tier = mine.get("tier")
        my_car  = (mine.get("car_model") or "").lower().strip()
        if not name:
            continue

        candidates: list[tuple[dict, float]] = []

        # 1. Exact car_model + tier
        if my_car and my_tier:
            exact = [
                c for c in competitors
                if c.get("current_price") is not None
                and c["_car_model"].lower() == my_car
                and c["_tier"] == my_tier
            ]
            for c in exact:
                candidates.append((c, 100.0))

        # 2. Fuzzy car_model + tier
        if not candidates and my_car and my_tier:
            tier_comps     = [c for c in competitors if c["_tier"] == my_tier]
            tier_car_names = [c["_car_model"] for c in tier_comps]
            if tier_car_names:
                fuzzy_hits = process.extract(
                    my_car,
                    tier_car_names,
                    scorer=fuzz.token_set_ratio,
                    score_cutoff=85,
                    limit=10,
                )
                for _, score, idx in fuzzy_hits:
                    c = tier_comps[idx]
                    if c.get("current_price") is not None:
                        candidates.append((c, float(score)))

        # 3. Fallback: fuzzy nama penuh + price-ratio guard
        if not candidates:
            min_price = (mine["price"] * _MIN_PRICE_RATIO) if mine["price"] else 0
            fallback = process.extract(
                name,
                comp_names,
                scorer=fuzz.token_set_ratio,
                score_cutoff=config.FUZZY_MATCH_THRESHOLD,
                limit=20,
            )
            for _, score, idx in fallback:
                c = competitors[idx]
                comp_price = c.get("current_price")
                if comp_price is None or comp_price < min_price:
                    continue
                candidates.append((c, float(score)))

        if not candidates:
            results.append({
                "sku":                     mine["sku"],
                "my_product_name":         name,
                "my_price":                mine["price"],
                "tier":                    my_tier,
                "car_model":               mine.get("car_model"),
                "matched_competitor":      None,
                "competitor_brand":        None,
                "competitor_shop":         None,
                "competitor_url":          None,
                "match_score":             None,
                "competitor_lowest_price": None,
                "price_gap":               None,
                "is_alert":                False,
            })
            continue

        # Pilih kompetitor harga terendah dari kandidat
        best_comp, best_score = min(candidates, key=lambda x: x[0]["current_price"])
        comp_price = best_comp["current_price"]
        my_price   = mine["price"]
        gap        = (my_price - comp_price) if my_price is not None else None
        is_alert   = gap is not None and abs(gap) > config.PRICE_GAP_ALERT_THRESHOLD

        comp_kw    = best_comp.get("search_keyword") or ""
        comp_brand = _brand_from_keyword(comp_kw) or best_comp.get("shop_name") or ""

        results.append({
            "sku":                     mine["sku"],
            "my_product_name":         name,
            "my_price":                my_price,
            "tier":                    my_tier,
            "car_model":               mine.get("car_model"),
            "matched_competitor":      best_comp["product_name"],
            "competitor_brand":        comp_brand,
            "competitor_shop":         best_comp.get("shop_name"),
            "competitor_url":          best_comp.get("product_url"),
            "match_score":             round(best_score, 1),
            "competitor_lowest_price": comp_price,
            "price_gap":               gap,
            "is_alert":                is_alert,
        })

    alerts = sum(1 for r in results if r["is_alert"])
    log.info(
        "Compare selesai: %s produk, %s alert (>Rp%s).",
        len(results), alerts, config.PRICE_GAP_ALERT_THRESHOLD,
    )
    return results


if __name__ == "__main__":
    for row in compare_products():
        if row["is_alert"]:
            print(
                f"ALERT  {row['sku']:<20} my={row['my_price']:>8}  "
                f"comp={row['competitor_lowest_price']:>8}  "
                f"gap={row['price_gap']:>8}  [{row['tier']} | {row['car_model']}]"
            )
