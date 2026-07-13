"""
generate_report.py — Generate HTML comparison report statis.

Membandingkan my_products.csv vs harga kompetitor di DB.
Output: report.html — file mandiri, tidak butuh server.

Pemakaian:
    python main.py generate-report
    python main.py generate-report --out custom.html
"""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

import config
from compare import compare_products
from utils import get_logger

log = get_logger("report")


def _rp(v) -> str:
    if v is None:
        return "—"
    try:
        return f"Rp{int(v):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


def _gap_str(gap) -> tuple[str, str]:
    """Kembalikan (teks, css-class)."""
    if gap is None:
        return "—", ""
    try:
        g = int(gap)
    except (ValueError, TypeError):
        return "—", ""
    if g > 0:
        return f"+{_rp(g)}", "gap-up"
    if g < 0:
        return f"-{_rp(abs(g))}", "gap-down"
    return "Sama", ""


TIER_LABEL = {"1-layer": "Reguler (1 Layer)", "3-layer": "Premium (3 Layer)", "4-layer": "Exclusive (4 Layer)"}
TIER_ORDER = ["4-layer", "3-layer", "1-layer"]


def _group_by_tier(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        if r.get("competitor_lowest_price") is None:
            continue
        tier = r.get("tier") or "unknown"
        groups.setdefault(tier, []).append(r)
    for tier in groups:
        groups[tier].sort(key=lambda x: (x.get("price_gap") or 0), reverse=True)
    return groups


def _rows_html(rows: list[dict]) -> str:
    parts = []
    for r in rows:
        name = html.escape(r.get("my_product_name") or "—")
        car  = html.escape(r.get("car_model") or "—")
        comp = html.escape(r.get("matched_competitor") or "—")
        shop = html.escape(r.get("competitor_brand") or r.get("competitor_shop") or "—")
        url  = r.get("competitor_url") or ""
        score = r.get("match_score")
        score_txt = f"{score:.0f}%" if score is not None else "—"

        my_p  = _rp(r.get("my_price"))
        com_p = _rp(r.get("competitor_lowest_price"))
        gap_txt, gap_cls = _gap_str(r.get("price_gap"))
        alert = r.get("is_alert", False)

        link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">Buka</a>' if url else "—"
        row_cls = "alert" if alert else ""

        parts.append(f"""
        <tr class="{row_cls}">
          <td class="car">{car}</td>
          <td class="name">{name}</td>
          <td class="price my">{my_p}</td>
          <td class="price">{com_p}</td>
          <td class="price {gap_cls}">{gap_txt}</td>
          <td class="comp">{comp}</td>
          <td class="shop">{shop}</td>
          <td class="score">{score_txt}</td>
          <td class="link">{link}</td>
        </tr>""")
    return "\n".join(parts)


def _section(tier: str, rows: list[dict]) -> str:
    label = TIER_LABEL.get(tier, tier)
    alerts = sum(1 for r in rows if r.get("is_alert"))
    rows_html = _rows_html(rows)
    return f"""
    <section class="tier-section">
      <div class="tier-header">
        <h2>{html.escape(label)}</h2>
        <div class="tier-meta">
          <span>{len(rows)} produk</span>
          <span class="badge-alert">{alerts} alert</span>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Tipe Mobil</th>
              <th>Produk Saya</th>
              <th>Harga Saya</th>
              <th>Harga Kompetitor</th>
              <th>Selisih</th>
              <th>Produk Kompetitor</th>
              <th>Brand</th>
              <th>Match</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </section>"""


def generate_html(out_path: Path | None = None) -> Path:
    out_path = out_path or (config.BASE_DIR / "report.html")

    log.info("Menjalankan compare...")
    all_rows = compare_products()

    matched   = [r for r in all_rows if r.get("competitor_lowest_price") is not None]
    unmatched = len(all_rows) - len(matched)
    alerts    = sum(1 for r in matched if r.get("is_alert"))
    groups    = _group_by_tier(matched)

    # Hitung 4-layer yang tidak punya match (butuh data kompetitor lebih)
    no_comp_4layer = sum(
        1 for r in all_rows
        if r.get("tier") == "4-layer" and r.get("competitor_lowest_price") is None
    )
    no_comp_note = ""
    if no_comp_4layer:
        no_comp_note = f"""
    <div class="notice">
      Produk Exclusive (4-layer): {no_comp_4layer:,} produk belum ada kompetitor setara di database.
      Jalankan <code>python main.py discover</code> setelah data Fusion R / Coversuper / Autocover
      tersedia untuk mendapatkan perbandingan yang akurat.
    </div>"""

    sections_html = "\n".join(
        _section(tier, groups[tier])
        for tier in TIER_ORDER
        if tier in groups
    )
    if "unknown" in groups:
        sections_html += _section("unknown", groups["unknown"])

    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")

    html_doc = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Undercover — Laporan Harga {generated_at}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:         #0d1117;
    --surface:    #161b22;
    --border:     #30363d;
    --border-sub: #21262d;
    --text:       #e6edf3;
    --muted:      #7d8590;
    --accent:     #f0883e;
    --green:      #3fb950;
    --red:        #f85149;
    --yellow:     #d29922;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Geist', -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.5;
  }}

  /* ── Header ─────────────────────────────── */
  .page-header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 24px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 10;
  }}
  .page-header h1 {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: .02em;
  }}
  .page-header .meta {{
    font-size: .78rem;
    color: var(--muted);
  }}

  /* ── KPI strip ───────────────────────────── */
  .kpi-strip {{
    display: flex;
    gap: 16px;
    padding: 20px 32px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }}
  .kpi {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 20px;
    min-width: 140px;
  }}
  .kpi .label {{ font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }}
  .kpi .value {{ font-size: 1.6rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }}
  .kpi .value.red   {{ color: var(--red); }}
  .kpi .value.green {{ color: var(--green); }}
  .kpi .value.amber {{ color: var(--yellow); }}

  /* ── Main content ────────────────────────── */
  main {{ padding: 24px 32px; }}

  /* ── Tier sections ───────────────────────── */
  .tier-section {{ margin-bottom: 40px; }}
  .tier-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }}
  .tier-header h2 {{ font-size: .95rem; font-weight: 600; }}
  .tier-meta {{ display: flex; gap: 12px; font-size: .78rem; color: var(--muted); }}
  .badge-alert {{ color: var(--red); font-weight: 500; }}

  /* ── Table ───────────────────────────────── */
  .table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: .82rem;
  }}
  thead th {{
    background: var(--bg);
    color: var(--muted);
    font-size: .68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 57px;
    white-space: nowrap;
    text-align: left;
  }}
  tbody tr {{ transition: background .1s; }}
  tbody tr:hover {{ background: rgba(255,255,255,.03); }}
  tbody td {{
    padding: 7px 12px;
    border-bottom: 1px solid var(--border-sub);
    vertical-align: middle;
  }}
  tbody tr:last-child td {{ border-bottom: none; }}

  /* alert row */
  tbody tr.alert td:first-child {{ border-left: 3px solid var(--red); padding-left: 9px; }}
  tbody tr.alert .gap-up {{ color: var(--red); font-weight: 600; }}

  /* column-specific */
  td.car   {{ font-weight: 500; white-space: nowrap; }}
  td.name  {{ color: var(--muted); font-size: .78rem; max-width: 200px; }}
  td.price {{ font-family: 'JetBrains Mono', monospace; font-size: .82rem; white-space: nowrap; }}
  td.my    {{ color: var(--text); font-weight: 500; }}
  td.gap-up   {{ color: var(--red); }}
  td.gap-down {{ color: var(--green); }}
  td.comp  {{ color: var(--muted); font-size: .77rem; max-width: 180px; }}
  td.shop  {{ color: var(--muted); font-size: .77rem; white-space: nowrap; }}
  td.score {{ color: var(--muted); font-size: .77rem; }}
  td.link a {{
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
    font-size: .78rem;
  }}
  td.link a:hover {{ text-decoration: underline; }}

  /* ── Footer ──────────────────────────────── */
  footer {{
    padding: 20px 32px;
    border-top: 1px solid var(--border);
    font-size: .75rem;
    color: var(--muted);
  }}

  /* ── Notice ─────────────────────────────── */
  .notice {{
    background: rgba(210,153,34,.1);
    border: 1px solid rgba(210,153,34,.4);
    border-left: 3px solid var(--yellow);
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 24px;
    font-size: .83rem;
    color: #c9a227;
    line-height: 1.6;
  }}
  .notice code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: .8rem;
    background: rgba(255,255,255,.08);
    padding: 1px 5px;
    border-radius: 3px;
    color: var(--accent);
  }}

  @media print {{
    .page-header {{ position: static; }}
    thead th {{ position: static; }}
    .table-wrap {{ overflow: visible; border: none; }}
  }}
</style>
</head>
<body>

<header class="page-header">
  <h1>Undercover — Laporan Harga Kompetitor</h1>
  <span class="meta">Dibuat: {generated_at}</span>
</header>

<div class="kpi-strip">
  <div class="kpi">
    <div class="label">Total Produk</div>
    <div class="value">{len(all_rows):,}</div>
  </div>
  <div class="kpi">
    <div class="label">Berhasil Dicocokkan</div>
    <div class="value amber">{len(matched):,}</div>
  </div>
  <div class="kpi">
    <div class="label">Alert Harga</div>
    <div class="value red">{alerts:,}</div>
  </div>
  <div class="kpi">
    <div class="label">Tidak Cocok</div>
    <div class="value">{unmatched:,}</div>
  </div>
</div>

<main>
{no_comp_note}
{sections_html}
</main>

<footer>
  Undercover — internal market intelligence tool &nbsp;·&nbsp;
  Data kompetitor dari Shopee via Apify &nbsp;·&nbsp;
  {generated_at}
</footer>

</body>
</html>"""

    out_path.write_text(html_doc, encoding="utf-8")
    log.info("Report disimpan: %s", out_path)
    return out_path
