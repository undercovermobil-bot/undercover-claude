# Undercover — Shopee Market Intelligence

Aplikasi internal untuk memonitor harga kompetitor di Shopee: kumpulkan produk per
keyword, simpan histori harga, bandingkan dengan produk sendiri, dan tampilkan
dashboard sederhana.

## Arsitektur Modul

| File | Tahap | Tanggung jawab |
|------|-------|----------------|
| `config.py` | — | Baca semua konfigurasi dari `.env` (tanpa hardcode) |
| `utils.py` | — | Logging, retry+backoff, jeda acak, parsing harga/angka |
| `database.py` | — | SQLite: tabel `products` & `price_history`, anti-duplikasi, histori |
| `discovery.py` | 1 | Scrape produk per keyword (Playwright) → DB |
| `monitor.py` | 2 | Refresh harian seluruh produk + catat perubahan harga |
| `dashboard.py` | 3 | Dashboard Streamlit (turun/naik harga, ranking, seller termurah) |
| `compare.py` | 4 | Fuzzy match `my_products.csv` vs kompetitor + alert selisih |
| `main.py` | — | CLI orkestrator semua tahap |

## Setup

```bash
# 1. Virtual env
python3 -m venv .venv && source .venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Konfigurasi
cp .env.example .env        # lalu sesuaikan isinya
```

## Pemakaian

```bash
python main.py init         # buat tabel DB
python main.py discover     # Tahap 1: kumpulkan produk per keyword
python main.py monitor      # Tahap 2: jalankan harian (lihat cron di bawah)
python main.py compare      # Tahap 4: bandingkan vs my_products.csv
python main.py dashboard    # Tahap 3: buka dashboard
```

### Jadwal harian (cron) — contoh

```cron
# Setiap hari jam 06:00, refresh harga
0 6 * * * cd /path/ke/Undercover && .venv/bin/python main.py monitor
```

## Konfigurasi (.env)

Semua perilaku diatur lewat `.env` — lihat `.env.example` untuk daftar lengkap.
Yang penting:

- `KEYWORDS_FILE` / `KEYWORDS` — daftar keyword
- `MAX_PRODUCTS_PER_KEYWORD` — default 200
- `PROXY_URL` — sangat disarankan untuk Shopee (anti-bot)
- `REQUEST_DELAY_MIN/MAX` — jeda acak antar request
- `PRICE_GAP_ALERT_THRESHOLD` — default Rp20.000
- `FUZZY_MATCH_THRESHOLD` — ambang kemiripan nama (0–100, default 80)

## ⚠️ Catatan soal scraping Shopee

Scraping langsung itu **rapuh**. Shopee punya anti-bot agresif (CAPTCHA,
rate-limit, blokir IP). Tiga titik yang hampir pasti perlu disesuaikan terhadap
Shopee live ditandai `# >>> TUNING` di `discovery.py`:

1. Path & query endpoint pencarian (`_SEARCH_API`)
2. Struktur JSON di `_extract_items()`
3. Header/cookie anti-bot (kemungkinan butuh proxy + cookie nyata)

Logika scraping sengaja diisolasi di class `ShopeeScraper`, jadi bila nanti pindah
ke API resmi/berbayar (mis. ScraperAPI/Apify), cukup ganti backend itu tanpa
menyentuh database/dashboard/compare.

## Skema Database

**products** (snapshot terbaru, 1 baris/produk):
`product_id` (PK), `shop_name`, `product_name`, `product_url` (unique),
`current_price`, `original_price`, `rating`, `sold_count`, `search_keyword`,
`first_seen_date`, `crawl_date`, `updated_at`

**price_history** (append-only, tidak pernah dihapus):
`id`, `product_id` (FK), `current_price`, `original_price`, `rating`,
`sold_count`, `crawl_date`, `recorded_at`

Snapshot histori baru hanya ditulis saat ada perubahan harga/diskon/rating/terjual.
