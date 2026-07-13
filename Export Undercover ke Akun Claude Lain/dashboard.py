"""
dashboard.py — Undercover Market Intelligence Dashboard

Design: Industrial/Utilitarian dark mode.
  Background #0d1117 · Surface #161b22 · Accent #f0883e (oranye)
  Harga: JetBrains Mono (angka selalu sejajar vertikal)
  Tabs: Ranking | Pergerakan | Compare Produkku
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import config
import database
from compare import compare_products, load_my_products

# --------------------------------------------------------------------------
# Config & CSS
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Undercover",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');

    /* ── HTML Tables ──────────────────────────────── */
    .uc-scroll { overflow-y: auto; border: 1px solid #30363d; border-radius: 8px; }
    .uc-table { width: 100%; border-collapse: collapse; font-size: .83rem; }
    .uc-table th {
        background: #0d1117; color: #7d8590;
        font-family: 'Geist', sans-serif; font-size: .7rem;
        font-weight: 600; text-transform: uppercase; letter-spacing: .06em;
        padding: 8px 12px; text-align: left;
        border-bottom: 1px solid #30363d;
        position: sticky; top: 0; z-index: 1;
    }
    .uc-table td { padding: 7px 12px; border-bottom: 1px solid #21262d; color: #e6edf3; vertical-align: middle; }
    .uc-table tr:last-child td { border-bottom: none; }
    .uc-table tr:hover td { background: rgba(255,255,255,.04); }
    .uc-table .mono { font-family: 'JetBrains Mono', monospace; font-size: .82rem; }
    .uc-table .muted { color: #7d8590; font-size: .78rem; }
    .uc-table .num { text-align: right; }
    .uc-table a { color: #f0883e; text-decoration: none; font-weight: 500; }
    .uc-table a:hover { text-decoration: underline; }
    .uc-table .down { color: #3fb950; }
    .uc-table .up   { color: #f85149; }
    .uc-table .alert-row td:first-child { border-left: 3px solid #f85149; }

    /* ── Base ─────────────────────────────────────── */
    html, body, [data-testid="stApp"] {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stMainBlockContainer"] { padding-top: 1.5rem !important; }

    /* ── Header ───────────────────────────────────── */
    .uc-header {
        display: flex; align-items: baseline; gap: 12px;
        margin-bottom: 1.5rem;
    }
    .uc-title {
        font-family: 'Geist', sans-serif;
        font-size: 1.35rem; font-weight: 700;
        color: #e6edf3; letter-spacing: -.02em;
    }
    .uc-subtitle {
        font-size: .8rem; color: #7d8590;
        font-family: 'DM Sans', sans-serif;
    }

    /* ── KPI Cards ────────────────────────────────── */
    .kpi-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .kpi-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 14px 20px; flex: 1; min-width: 140px;
    }
    .kpi-label {
        font-family: 'Geist', sans-serif; font-size: .7rem;
        font-weight: 600; color: #7d8590; text-transform: uppercase;
        letter-spacing: .06em; margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem; font-weight: 500; color: #e6edf3;
        letter-spacing: -.02em;
    }
    .kpi-value.accent  { color: #f0883e; }
    .kpi-value.green   { color: #3fb950; }
    .kpi-value.red     { color: #f85149; }
    .kpi-sub {
        font-size: .72rem; color: #7d8590; margin-top: 4px;
    }

    /* ── Keyword pills ────────────────────────────── */
    .pill-row { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }

    /* ── Tables via st.dataframe ──────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] table { background: #161b22 !important; }
    [data-testid="stDataFrame"] th {
        background: #0d1117 !important;
        font-family: 'Geist', sans-serif !important;
        font-size: .72rem !important; font-weight: 600 !important;
        color: #7d8590 !important; text-transform: uppercase !important;
        letter-spacing: .06em !important;
    }
    [data-testid="stDataFrame"] td {
        font-family: 'DM Sans', sans-serif !important;
        font-size: .85rem !important; color: #e6edf3 !important;
        border-color: #21262d !important;
    }

    /* ── Tabs ─────────────────────────────────────── */
    [data-testid="stTabs"] button {
        font-family: 'Geist', sans-serif !important;
        font-size: .85rem !important; font-weight: 500 !important;
        color: #7d8590 !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #f0883e !important;
        border-bottom-color: #f0883e !important;
    }

    /* ── Alert box ────────────────────────────────── */
    .alert-box {
        background: rgba(248,81,73,.12); border: 1px solid #f85149;
        border-radius: 8px; padding: 12px 16px; margin-bottom: 14px;
        font-size: .85rem; color: #f85149;
        font-family: 'Geist', sans-serif; font-weight: 500;
    }
    .ok-box {
        background: rgba(63,185,80,.1); border: 1px solid #3fb950;
        border-radius: 8px; padding: 10px 16px; margin-bottom: 14px;
        font-size: .82rem; color: #3fb950;
        font-family: 'Geist', sans-serif;
    }

    /* ── Misc ─────────────────────────────────────── */
    [data-testid="stSelectbox"] > div { background: #161b22 !important; }
    div[data-testid="stMarkdownContainer"] p { color: #7d8590; font-size:.82rem; }
    hr { border-color: #21262d !important; }
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def rp(v) -> str:
    if v is None:
        return "—"
    try:
        return f"Rp{int(v):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


def delta_str(d) -> str:
    if d is None:
        return "—"
    prefix = "▲" if d > 0 else "▼"
    return f"{prefix} {rp(abs(d))}"


def kpi(label: str, value: str, cls: str = "", sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card">'
        f'  <div class="kpi-label">{label}</div>'
        f'  <div class="kpi-value {cls}">{value}</div>'
        f'  {sub_html}'
        f'</div>'
    )


def build_movements(keyword: str | None) -> pd.DataFrame:
    products = database.get_all_products(keyword=keyword)
    rows = []
    for p in products:
        snaps = database.get_latest_two_snapshots(p["product_id"])
        prev = snaps[1]["current_price"] if len(snaps) > 1 else None
        cur = p["current_price"]
        delta = (cur - prev) if (prev and cur) else None
        rows.append({
            "product_id": p["product_id"],
            "Produk": p["product_name"] or "",
            "URL": p["product_url"] or "",
            "Toko / Kota": p["shop_name"] or "—",
            "Harga": cur,
            "Harga Sebelumnya": prev,
            "Selisih": delta,
            "Rating": p["rating"],
            "Keyword": p["search_keyword"] or "",
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    total = database.count_products()

    # Header
    from utils import today_str
    st.markdown(
        f'<div class="uc-header">'
        f'  <span class="uc-title">Undercover</span>'
        f'  <span class="uc-subtitle">Shopee Market Intelligence · {today_str()}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if total == 0:
        st.markdown(
            '<div class="alert-box">Database kosong. Jalankan <code>python main.py discover</code> dulu.</div>',
            unsafe_allow_html=True,
        )
        return

    # KPI data (tanpa keyword filter — angka global)
    df_all = build_movements(None)
    turun_all = df_all[df_all["Selisih"].notna() & (df_all["Selisih"] < 0)]
    naik_all  = df_all[df_all["Selisih"].notna() & (df_all["Selisih"] > 0)]

    try:
        compare_rows = compare_products(keyword=None)
        alerts = sum(1 for r in compare_rows if r.get("is_alert"))
    except FileNotFoundError:
        compare_rows = []
        alerts = 0

    cheapest = df_all.loc[df_all["Harga"].idxmin()] if not df_all["Harga"].isna().all() else None

    # KPI strip
    kpis = (
        kpi("Total Produk Terpantau", str(total))
        + kpi("Turun Harga Hari Ini", str(len(turun_all)), "green" if turun_all.empty is False else "")
        + kpi("Naik Harga Hari Ini",  str(len(naik_all)),  "red"   if naik_all.empty  is False else "")
        + kpi("Gap Alert (>Rp20rb)",  str(alerts),          "accent" if alerts else "")
        + (kpi("Termurah Saat Ini",
                rp(cheapest["Harga"]) if cheapest is not None else "—",
                sub=str(cheapest["Toko / Kota"]) if cheapest is not None else "") if cheapest is not None else "")
    )
    st.markdown(f'<div class="kpi-row">{kpis}</div>', unsafe_allow_html=True)

    # Keyword filter
    keywords_db = database.get_keywords_in_db()
    kw_options = ["Semua Keyword"] + keywords_db
    selected_kw = st.selectbox("Filter keyword", kw_options, label_visibility="collapsed")
    keyword = None if selected_kw == "Semua Keyword" else selected_kw

    df = build_movements(keyword)

    # Tab navigation — tanpa emoji
    tab_rank, tab_move, tab_compare = st.tabs(["Ranking Harga", "Pergerakan", "Compare Produkku"])

    # ── Tab 1: Ranking ──────────────────────────────────────────────────
    with tab_rank:
        rank_df = df.sort_values("Harga").copy().reset_index(drop=True)

        rows_html = ""
        for i, row in rank_df.iterrows():
            url = row.get("URL", "")
            link = f'<a href="{url}" target="_blank" rel="noopener">Buka</a>' if url else "—"
            rating = f"{row['Rating']:.1f}" if pd.notna(row.get("Rating")) else "—"
            rows_html += (
                f'<tr>'
                f'<td class="num muted">{i+1}</td>'
                f'<td>{row["Produk"]}</td>'
                f'<td>{link}</td>'
                f'<td class="muted">{row["Toko / Kota"]}</td>'
                f'<td class="mono num">{rp(row["Harga"])}</td>'
                f'<td class="num muted">{rating}</td>'
                f'<td class="muted">{row["Keyword"]}</td>'
                f'</tr>'
            )
        html = (
            '<div class="uc-scroll" style="max-height:520px">'
            '<table class="uc-table"><thead><tr>'
            '<th>#</th><th>Produk</th><th>Link</th>'
            '<th>Toko / Kota</th><th>Harga (Rp)</th><th>Rating</th><th>Keyword</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table></div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    # ── Tab 2: Pergerakan ───────────────────────────────────────────────
    with tab_move:
        turun = df[df["Selisih"].notna() & (df["Selisih"] < 0)].sort_values("Selisih")
        naik  = df[df["Selisih"].notna() & (df["Selisih"] > 0)].sort_values("Selisih", ascending=False)

        def _movement_table(data: pd.DataFrame, direction: str) -> str:
            rows_html = ""
            for _, row in data.iterrows():
                url  = row.get("URL", "")
                link = f'<a href="{url}" target="_blank" rel="noopener">Buka</a>' if url else "—"
                sel  = row["Selisih"]
                cls  = "down" if sel < 0 else "up"
                sign = f'▼ {rp(abs(sel))}' if sel < 0 else f'▲ {rp(abs(sel))}'
                rows_html += (
                    f'<tr>'
                    f'<td>{row["Produk"]}</td>'
                    f'<td>{link}</td>'
                    f'<td class="muted">{row["Toko / Kota"]}</td>'
                    f'<td class="mono">{rp(row["Harga Sebelumnya"])}</td>'
                    f'<td class="mono">{rp(row["Harga"])}</td>'
                    f'<td class="mono {cls}">{sign}</td>'
                    f'<td class="muted">{row["Keyword"]}</td>'
                    f'</tr>'
                )
            return (
                '<div class="uc-scroll" style="max-height:280px">'
                '<table class="uc-table"><thead><tr>'
                '<th>Produk</th><th>Link</th><th>Toko / Kota</th>'
                '<th>Sebelumnya</th><th>Sekarang</th><th>Selisih</th><th>Keyword</th>'
                f'</tr></thead><tbody>{rows_html}</tbody></table></div>'
            )

        if not turun.empty:
            st.markdown("#### Turun Harga")
            st.markdown(_movement_table(turun, "down"), unsafe_allow_html=True)
        else:
            st.markdown('<div class="ok-box">Belum ada penurunan harga terdeteksi hari ini. Butuh minimal 2 snapshot — jalankan monitor besok.</div>', unsafe_allow_html=True)

        st.markdown("---")

        if not naik.empty:
            st.markdown("#### Naik Harga")
            st.markdown(_movement_table(naik, "up"), unsafe_allow_html=True)
        else:
            st.markdown('<div class="ok-box">Tidak ada kenaikan harga terdeteksi hari ini.</div>', unsafe_allow_html=True)

    # ── Tab 3: Compare ──────────────────────────────────────────────────
    with tab_compare:
        if not compare_rows:
            st.markdown(
                '<div class="alert-box">File <code>my_products.csv</code> belum ada atau kosong. '
                'Jalankan <code>python main.py generate-products</code> untuk generate dari xlsx.</div>',
                unsafe_allow_html=True,
            )
        else:
            cdf = pd.DataFrame(compare_rows)
            alert_count = int(cdf["is_alert"].sum())
            matched_df  = cdf[cdf["matched_competitor"].notna() & (cdf["matched_competitor"] != "—")].copy()

            if alert_count:
                st.markdown(
                    f'<div class="alert-box">{alert_count} produk dengan selisih harga '
                    f'&gt; {rp(config.PRICE_GAP_ALERT_THRESHOLD)} vs kompetitor termurah</div>',
                    unsafe_allow_html=True,
                )

            if matched_df.empty:
                st.markdown('<div class="ok-box">Belum ada produk yang match. Tambahkan lebih banyak keyword lalu jalankan discover.</div>', unsafe_allow_html=True)
            else:
                rows_html = ""
                for _, row in matched_df.sort_values("price_gap", ascending=False, na_position="last").iterrows():
                    url  = row.get("competitor_url") or ""
                    link = f'<a href="{url}" target="_blank" rel="noopener">Buka</a>' if url else "—"
                    gap  = row.get("price_gap")
                    gap_html = f'<span class="up">+{rp(gap)}</span>' if (pd.notna(gap) and gap > 0) else (f'<span class="down">{rp(abs(gap))}</span>' if (pd.notna(gap) and gap < 0) else "—")
                    score = row.get("match_score")
                    score_html = f"{score:.0f}%" if pd.notna(score) else "—"
                    alert_cls = "alert-row" if row.get("is_alert") else ""
                    rows_html += (
                        f'<tr class="{alert_cls}">'
                        f'<td class="muted">{row.get("sku","")}</td>'
                        f'<td>{row.get("my_product_name","")}</td>'
                        f'<td class="mono">{rp(row.get("my_price"))}</td>'
                        f'<td>{row.get("matched_competitor","—")}</td>'
                        f'<td>{link}</td>'
                        f'<td class="mono">{rp(row.get("competitor_lowest_price"))}</td>'
                        f'<td class="mono">{gap_html}</td>'
                        f'<td class="muted">{score_html}</td>'
                        f'</tr>'
                    )
                html = (
                    f'<div class="uc-scroll" style="max-height:500px">'
                    f'<table class="uc-table"><thead><tr>'
                    f'<th>SKU</th><th>Produk Saya</th><th>Harga Saya</th>'
                    f'<th>Match Kompetitor</th><th>Link</th>'
                    f'<th>Komp. Termurah</th><th>Gap</th><th>Match %</th>'
                    f'</tr></thead><tbody>{rows_html}</tbody></table></div>'
                )
                st.markdown(html, unsafe_allow_html=True)
                st.markdown(f'<div class="kpi-sub" style="margin-top:8px">Menampilkan {len(matched_df)} produk yang match dari total {len(cdf)} produk kamu.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
