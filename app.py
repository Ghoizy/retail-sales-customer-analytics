"""Retail Sales & Customer Analytics — V3 Clean Modern Business.

Independent UCI Online Retail case study. All business calculations come from
scripts.analytics; visual redesign does not change the analytics policy.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scripts.analytics import (
    build_insights,
    country_ranking,
    filter_lines,
    make_markdown_report,
    monthly_sales,
    product_ranking,
    summarize_sales,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
SALES_PATH = DATA / "sales_lines.csv"
CANCEL_PATH = DATA / "cancellation_lines.csv"
QUALITY_PATH = DATA / "data_quality.json"
ACCENT = "#5547D8"
INK = "#16213C"
MUTED = "#718096"

st.set_page_config(
    page_title="Retail Sales Analytics | Portfolio Case Study",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* V3: contemporary, restrained business analytics design */
:root { color-scheme: light; }
.stApp { background: #F8FAFD; color: #16213C; }
[data-testid="stAppViewContainer"] > .main { background: #F8FAFD; }
.block-container { max-width: 1510px; padding: 2.1rem 2.2rem 3.3rem; }
header[data-testid="stHeader"] { background: rgba(248,250,253,.82); }
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
h1, h2, h3, h4 { color: #16213C; letter-spacing: -.028em; }
[data-testid="stSidebar"] { background: #F3F5FB; border-right: 1px solid #E5E9F2; }
[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
[data-testid="stSidebar"] hr { border-color:#DFE5EF; margin: 1.35rem 0; }
[data-testid="stSidebar"] label { font-size: .88rem; color: #37445B; }
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div { border-radius: 10px; background: white; border-color: #E4E8F1; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background:#EAE7FD; color:#4938B5; border-radius:6px; }
[data-testid="stSidebar"] [data-baseweb="tag"] span { color:#4938B5; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#748095; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .4rem; border-bottom:1px solid #E3E7F0; }
[data-testid="stTabs"] [role="tab"] { padding: 12px 16px; border-radius: 9px 9px 0 0; font-size:.91rem; font-weight:600; color:#65748B; }
[data-testid="stTabs"] [aria-selected="true"] { color:#5547D8; background:rgba(85,71,216,.055); }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background:#5547D8; height:3px; border-radius:3px 3px 0 0; }
[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] { border-color: #E4EAF3; }
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #E4E9F2; padding: 17px 19px; border-radius:15px; box-shadow:0 3px 12px rgba(18,32,61,.025); }
[data-testid="stMetricLabel"] { color:#718096; font-size:.88rem; }
[data-testid="stMetricValue"] { font-size:1.7rem; letter-spacing:-.04em; color:#16213C; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border-radius:12px; overflow:hidden; }
[data-testid="stDownloadButton"] button { background:#fff; border:1px solid #D9DFED; border-radius:10px; color:#3D35A2; font-weight:600; min-height:45px; }
[data-testid="stDownloadButton"] button:hover { border-color:#5547D8; background:#F1EFFF; color:#4938B5; }
[data-testid="stExpander"] { border:1px solid #E3E8F1; border-radius:12px; background:#fff; }
[data-testid="stAlert"] { border-radius:12px; }
/* Custom semantic components */
.v3-brand {display:flex;align-items:center;gap:11px;padding:3px 0 6px;}
.v3-brand-logo {width:40px;height:40px;border-radius:12px;background:#5144D4;color:#fff;display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:800;box-shadow:0 8px 18px rgba(82,66,205,.14);}
.v3-brand-name {font-size:1.04rem;font-weight:780;letter-spacing:-.035em;color:#18233C;line-height:1.2;}
.v3-brand-sub {font-size:.72rem;color:#78869B;margin-top:3px;}
.v3-sidebar-heading {font-size:.7rem;font-weight:750;letter-spacing:.12em;text-transform:uppercase;color:#8791A3;margin: 6px 0 12px;}
.v3-sidebar-info {font-size:.79rem;line-height:1.65;color:#66748A;background:#FFF;border:1px solid #E5E9F2;padding:14px;border-radius:13px;}
.v3-sidebar-info strong {color:#25314A;}
.v3-sidebar-info a {color:#5144D4;text-decoration:none;font-weight:650;}
.v3-eyebrow {display:inline-flex;align-items:center;gap:8px;font-weight:700;font-size:.7rem;letter-spacing:.082em;color:#5144D4;background:#F0EDFE;border:1px solid #E6E1FD;padding:8px 11px;border-radius:100px;text-transform:uppercase;}
.v3-dot {width:7px;height:7px;display:inline-block;border-radius:100px;background:#31A58A;}
.v3-hero {display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin:6px 0 19px;flex-wrap:wrap;}
.v3-title {font-size:clamp(1.85rem,3.2vw,2.6rem);font-weight:790;letter-spacing:-.055em;line-height:1.13;margin:12px 0 8px;color:#14203A;}
.v3-description {font-size:.94rem;color:#6E7B8F;margin:0;line-height:1.55;}
.v3-hero-links a {font-size:.84rem;text-decoration:none;color:#4337B5;font-weight:650;background:#FFF;border:1px solid #E1E6F0;border-radius:9px;padding:9px 13px;margin-left:6px;white-space:nowrap;}
.v3-hero-links a:hover {background:#F0EEFF;border-color:#C8C1F5;}
.v3-meta-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:10px 0 14px;}
.v3-meta {background:#fff;border:1px solid #E6EAF2;border-radius:11px;padding:12px 15px;min-width:0;}
.v3-meta-label {font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:#8A96A7;font-weight:730;margin-bottom:6px;}
.v3-meta-value {font-size:.85rem;color:#25334C;font-weight:670;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.v3-note {background:#F0F2FF;border:1px solid #E1E3FB;border-left:3px solid #7970DD;color:#535D87;padding:12px 16px;border-radius:10px;font-size:.8rem;line-height:1.65;margin:0 0 19px;}
.v3-note strong {color:#374271;}
.v3-kpi-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:22px;}
.v3-kpi {position:relative;overflow:hidden;background:#FFF;border:1px solid #E3E8F1;border-radius:16px;padding:20px 20px 14px;min-height:152px;box-shadow:0 4px 16px rgba(25,38,66,.025);}
.v3-kpi-top {display:flex;align-items:center;gap:11px;margin-bottom:13px;}
.v3-kpi-icon {display:flex;align-items:center;justify-content:center;width:33px;height:33px;border-radius:10px;background:#EFEDFF;color:#5144D4;font-size:16px;font-weight:750;flex-shrink:0;}
.v3-kpi-label {font-size:.7rem;font-weight:740;letter-spacing:.075em;text-transform:uppercase;color:#778498;line-height:1.3;}
.v3-kpi-value {font-size:clamp(1.36rem,2.25vw,1.91rem);font-weight:780;letter-spacing:-.045em;color:#172340;white-space:nowrap;line-height:1.12;}
.v3-kpi-foot {font-size:.69rem;color:#8995A7;margin-top:13px;line-height:1.4;}
.v3-kpi-spark {position:absolute;right:17px;bottom:15px;width:96px;height:35px;opacity:.92;}
.v3-section-head {display:flex;justify-content:space-between;gap:14px;align-items:flex-start;margin:0 0 12px;}
.v3-section-title {font-size:1.05rem;font-weight:770;letter-spacing:-.025em;color:#1A2740;}
.v3-section-desc {font-size:.76rem;color:#8490A2;margin-top:3px;line-height:1.5;}
.v3-chip {border-radius:7px;padding:6px 9px;background:#F2F4FA;color:#728098;font-size:.71rem;font-weight:650;white-space:nowrap;}
.v3-insights {background:#FFF;border:1px solid #E3E8F1;border-radius:15px;padding:20px 19px;box-shadow:0 4px 16px rgba(25,38,66,.025);}
.v3-insight {display:flex;align-items:flex-start;gap:11px;margin:12px 0 0;padding:13px 12px;background:#F8F9FC;border:1px solid #EEF1F6;border-radius:11px;}
.v3-insight-num {flex:0 0 25px;height:25px;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:760;color:#5547D8;background:#EAE7FD;border-radius:8px;}
.v3-insight-text {font-size:.79rem;line-height:1.55;color:#42516A;overflow-wrap:anywhere;}
.v3-insights-foot {font-size:.72rem;color:#8390A4;line-height:1.55;margin:15px 2px 2px;}
.v3-card-label {font-size:.72rem;color:#7D899D;margin-bottom:12px;}
.v3-gap {height:9px;}
.v3-footer {border-top:1px solid #E5EAF2;color:#8792A2;font-size:.73rem;padding-top:17px;margin-top:28px;line-height:1.6;}
@media(max-width:1160px){.v3-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.v3-meta-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media(max-width:720px){.block-container{padding:1.1rem 1rem 2rem}.v3-hero{display:block}.v3-title{font-size:1.9rem}.v3-hero-links{margin-top:16px}.v3-hero-links a{margin:0 5px 0 0;display:inline-block}.v3-kpi-grid{gap:9px}.v3-kpi{padding:15px 12px;min-height:138px}.v3-kpi-value{font-size:1.38rem}.v3-kpi-icon{display:none}.v3-kpi-spark{width:60px;right:8px;opacity:.4}.v3-meta-grid{gap:8px}.v3-meta{padding:10px}}
</style>
    """,
    unsafe_allow_html=True,
)


def gbp(value: float, decimals: int = 0) -> str:
    return f"£{value:,.{decimals}f}"


def style_figure(fig: go.Figure, *, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=6, r=9, t=28, b=15),
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", color=INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", font=dict(color=INK)),
        hovermode="x unified",
        showlegend=True,
    )
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="#EDF0F6", zeroline=False, tickfont=dict(color=MUTED))
    return fig


def sparkline(values: list[float], color: str = "#5547D8") -> str:
    """Tiny visual of real monthly figures, not a fabricated decorative chart."""
    if len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    spread = (hi - lo) or 1.0
    points = [(3 + i * 90 / (len(values) - 1), 30 - 25 * (v - lo) / spread) for i, v in enumerate(values)]
    path = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(points))
    return f'<svg class="v3-kpi-spark" viewBox="0 0 96 35" aria-hidden="true"><path d="{path}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" /></svg>'


def kpi_card(label: str, value: str, foot: str, glyph: str, values: list[float], tint: str = "#5547D8") -> str:
    return (
        '<div class="v3-kpi">'
        f'<div class="v3-kpi-top"><span class="v3-kpi-icon">{escape(glyph)}</span>'
        f'<span class="v3-kpi-label">{escape(label)}</span></div>'
        f'<div class="v3-kpi-value">{escape(value)}</div>'
        f'<div class="v3-kpi-foot">{escape(foot)}</div>'
        f'{sparkline(values, tint)}</div>'
    )


def section_head(title: str, description: str, chip: str = "") -> None:
    extra = f'<span class="v3-chip">{escape(chip)}</span>' if chip else ""
    st.markdown(
        f'<div class="v3-section-head"><div><div class="v3-section-title">{escape(title)}</div>'
        f'<div class="v3-section-desc">{escape(description)}</div></div>{extra}</div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Loading audited transactions...")
def load_processed(sales_mtime: int, quality_mtime: int, cancellation_mtime: int):
    sales_df = pd.read_csv(
        SALES_PATH, parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string", "Country": "string"},
    )
    cancels_df = pd.read_csv(
        CANCEL_PATH, parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string", "Country": "string"},
    )
    audit = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    return sales_df, cancels_df, audit


if any(not p.exists() for p in (SALES_PATH, CANCEL_PATH, QUALITY_PATH)):
    from scripts.cloud_bootstrap import ensure_prepared_data

    @st.cache_resource(show_spinner=False)
    def initialize_source_data():
        return ensure_prepared_data()

    try:
        with st.spinner("Preparing official UCI Online Retail data for this server..."):
            initialize_source_data()
    except Exception as exc:
        st.error("Unable to prepare official UCI dataset for this server.")
        st.caption("Official data download may fail if the source is unavailable or cloud resources are insufficient.")
        st.code(f"{type(exc).__name__}: {exc}")
        st.stop()

sales, cancellations, quality = load_processed(
    SALES_PATH.stat().st_mtime_ns, QUALITY_PATH.stat().st_mtime_ns, CANCEL_PATH.stat().st_mtime_ns
)
source_start = sales["InvoiceDate"].min().date()
source_end = sales["InvoiceDate"].max().date()
all_countries = sorted(sales["Country"].dropna().unique().tolist())

# A cleaner all-markets mode: don't show ~38 multiselect tags at once.
with st.sidebar:
    st.markdown(
        '<div class="v3-brand"><div class="v3-brand-logo">R</div><div>'
        '<div class="v3-brand-name">Retail Intelligence</div>'
        '<div class="v3-brand-sub">DATA ANALYTICS WORKSPACE</div></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="v3-sidebar-heading">Analysis filters</div>', unsafe_allow_html=True)
    show_all = st.checkbox(
        "Compare all countries", value=False, key="compare_all_v3",
        help="Include every country without crowding the filter with selected tags.",
    )
    if show_all:
        selected_countries = all_countries
        st.caption(f"All {len(all_countries)} markets included. Uncheck to choose individual countries.")
    else:
        selected_countries = st.multiselect(
            "Countries", options=all_countries,
            default=["United Kingdom"] if "United Kingdom" in all_countries else all_countries[:1],
            key="selected_countries_v3",
        )
    chosen = st.date_input(
        "Invoice date range", value=(source_start, source_end),
        min_value=source_start, max_value=source_end,
    )
    st.caption("Dates include both endpoints. Source coverage is partial in December 2011.")
    st.divider()
    st.markdown('<div class="v3-sidebar-heading">Dataset & provenance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="v3-sidebar-info"><strong>UCI Online Retail</strong><br>'
        '541,909 published invoice lines<br>Dec 2010 – Dec 2011 · GBP (£)<br>'
        'Chen (2015) · CC BY 4.0<br>'
        '<a href="https://archive.ics.uci.edu/dataset/352/online-retail" target="_blank">Source dataset ↗</a>'
        '</div>',
        unsafe_allow_html=True,
    )

if not isinstance(chosen, (list, tuple)) or len(chosen) != 2:
    st.warning("Select both a start and end date to view analytics.")
    st.stop()
from_date, to_date = chosen
if not selected_countries:
    st.warning("Select at least one country in the sidebar.")
    st.stop()
filtered = filter_lines(sales, selected_countries, from_date, to_date)
if filtered.empty:
    st.warning("No positive recorded sales match those countries and dates. Adjust the filters.")
    st.stop()
filtered_cancels = filter_lines(cancellations, selected_countries, from_date, to_date)
kpis = summarize_sales(filtered)
monthly = monthly_sales(filtered, from_date, to_date, source_start, source_end)
all_products = product_ranking(filtered, exclude_adjustment_codes=True)
geo = country_ranking(filtered)
insights = build_insights(filtered, geo, all_products, monthly)

scope_label = (
    f"All {len(all_countries)} countries" if show_all else
    (selected_countries[0] if len(selected_countries) == 1 else f"{len(selected_countries)} selected countries")
)
period_label = f"{from_date:%b %Y} – {to_date:%b %Y}"

st.markdown(
    '<div class="v3-eyebrow"><span class="v3-dot"></span> Independent portfolio case study</div>'
    '<div class="v3-hero"><div>'
    '<div class="v3-title">Retail Sales &amp; Customer Analytics</div>'
    '<p class="v3-description">From historical invoice lines to clear, filterable business insights.</p>'
    '</div><div class="v3-hero-links">'
    '<a href="https://github.com/Ghoizy/retail-sales-customer-analytics" target="_blank">↗ Source code</a>'
    '<a href="https://doi.org/10.24432/C5BW33" target="_blank">↗ Data citation</a>'
    '</div></div>',
    unsafe_allow_html=True,
)
metadata = [
    ("Dataset", "UCI Online Retail"),
    ("Period", period_label),
    ("Market scope", scope_label),
    ("Currency", "GBP (£)"),
]
st.markdown(
    '<div class="v3-meta-grid">' + ''.join(
        f'<div class="v3-meta"><div class="v3-meta-label">{escape(k)}</div>'
        f'<div class="v3-meta-value">{escape(v)}</div></div>' for k, v in metadata
    ) + '</div>'
    '<div class="v3-note"><strong>Data interpretation:</strong> Historical public data—not paid client work. '
    'Recorded sales sum positive, non-cancelled invoice lines. '
    'They are <strong>not verified net revenue, profit, or cash receipts</strong>; returns require reconciliation.</div>',
    unsafe_allow_html=True,
)

# Small trend traces come from the SAME filtered invoice-line dataset.
monthly_sales_values = monthly["recorded_sales_gbp"].astype(float).tolist()
monthly_invoices = monthly["invoices"].astype(float).tolist()
monthly_aiv = (monthly["recorded_sales_gbp"] / monthly["invoices"].clip(lower=1)).astype(float).tolist()
monthly_units = (
    filtered.groupby(filtered["InvoiceDate"].dt.to_period("M"), sort=True)["Quantity"]
    .sum().astype(float).tolist()
)
kpi_definitions = [
    ("Recorded sales", gbp(kpis["recorded_sales_gbp"]), "Positive invoice lines · GBP", "£", monthly_sales_values, "#5547D8"),
    ("Distinct invoices", f"{kpis['invoices']:,}", "Unique InvoiceNo values", "▣", monthly_invoices, "#249B86"),
    ("Avg. invoice value", gbp(kpis["average_invoice_value_gbp"], 2), "Recorded sales / invoices", "↗", monthly_aiv, "#4079DA"),
    ("Recorded units", f"{kpis['units_recorded']:,}", "Positive item quantities", "◈", monthly_units, "#A47D40"),
]
st.markdown(
    '<div class="v3-kpi-grid">' + ''.join(kpi_card(*args) for args in kpi_definitions) + '</div>',
    unsafe_allow_html=True,
)

sales_tab, products_tab, markets_tab, quality_tab, exports_tab = st.tabs(
    ["Sales overview", "Products", "Markets", "Data quality", "Download report"]
)

with sales_tab:
    chart_col, insight_col = st.columns([1.8, 1], gap="medium")
    with chart_col:
        with st.container(border=True):
            section_head("Monthly recorded sales", "Positive sales invoice lines by month · GBP", "Includes partial periods")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly["month"], y=monthly["recorded_sales_gbp"],
                name="Recorded sales", mode="lines+markers",
                line=dict(color=ACCENT, width=3.2, shape="spline", smoothing=.35),
                marker=dict(size=7, color="#FFFFFF", line=dict(color=ACCENT, width=2.5)),
                fill="tozeroy", fillcolor="rgba(85,71,216,0.075)",
                customdata=monthly[["period_note", "invoices"]].to_numpy(),
                hovertemplate="%{x|%b %Y}<br>Recorded sales: £%{y:,.2f}<br>Invoices: %{customdata[1]:,}<br>%{customdata[0]}<extra></extra>",
            ))
            partial_months = monthly.loc[monthly["partial_period"]]
            if not partial_months.empty:
                fig.add_trace(go.Scatter(
                    x=partial_months["month"], y=partial_months["recorded_sales_gbp"],
                    mode="markers", name="Partial calendar period",
                    marker=dict(color="#D79244", size=12, symbol="circle-open", line=dict(width=2.7)),
                    hovertemplate="%{x|%b %Y}: partial calendar period<extra></extra>",
                ))
            fig.update_yaxes(tickprefix="£", tickformat="~s")
            fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-.16, x=0))
            st.plotly_chart(style_figure(fig, height=380), width="stretch", config={"displaylogo": False})
            st.caption("Partial calendar periods are flagged. December 2011 includes records only through 9 Dec.")
    with insight_col:
        cards = ''.join(
            '<div class="v3-insight"><span class="v3-insight-num">'
            f'{i}</span><span class="v3-insight-text">{escape(item)}</span></div>'
            for i, item in enumerate(insights, 1)
        )
        st.markdown(
            '<div class="v3-insights">'
            '<div class="v3-section-title">Executive summary</div>'
            '<div class="v3-section-desc">Evidence-based observations for the current selection</div>'
            f'{cards}'
            '<div class="v3-insights-foot">Descriptive findings only. Not proof of profitability, '
            'causation, or growth opportunities.</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="v3-gap"></div>', unsafe_allow_html=True)
    cust_col, missing_col = st.columns(2, gap="medium")
    with cust_col:
        st.metric("Identified customers", f"{kpis['identified_customers']:,}")
        st.caption("Unique identified customers in filtered lines, excluding missing IDs.")
    with missing_col:
        missing_pct = (kpis["sale_lines_missing_customer_id"] / kpis["sale_lines"] * 100) if kpis["sale_lines"] else 0
        st.metric("Sales lines with missing CustomerID", f"{missing_pct:.1f}%")
        st.caption("Their positive sales values remain part of recorded sales.")

with products_tab:
    section_head("Product performance", "Highest-value merchandise candidates · using stock-code aggregation", "Filtered selection")
    product_toggle = st.checkbox(
        "Exclude common shipping/adjustment codes (heuristic)", value=True,
        help="Affects only the product view. Headline recorded sales is unchanged; validate this classification for real client work.",
    )
    prods = product_ranking(filtered, exclude_adjustment_codes=product_toggle)
    if prods.empty:
        st.info("No product candidates remain after these filters.")
    else:
        with st.container(border=True):
            section_head("Top 12 merchandise candidates", "Ranked by positive recorded sales", "GBP")
            top = prods.head(12).iloc[::-1]
            fig = px.bar(top, x="recorded_sales_gbp", y="display_name", orientation="h",
                         labels={"recorded_sales_gbp": "Recorded sales (£)", "display_name": "Stock code · description"},
                         color_discrete_sequence=[ACCENT])
            fig.update_traces(marker_line_width=0, hovertemplate="%{y}<br>Recorded sales £%{x:,.2f}<extra></extra>")
            fig.update_xaxes(tickprefix="£", tickformat="~s", showgrid=True, gridcolor="#EDF0F6")
            fig.update_yaxes(showgrid=False, automargin=True)
            st.plotly_chart(style_figure(fig, height=485), width="stretch", config={"displaylogo": False})
            st.caption("Shares use included product-analysis lines, not necessarily all recorded sales. Product exclusions are heuristic.")
        section_head("Product detail", "Top 30 stock codes in the filtered selection")
        st.dataframe(prods.head(30).rename(columns={
            "StockCode": "Stock code", "Description": "Description", "units": "Units", "invoices": "Invoices",
            "recorded_sales_gbp": "Recorded sales (£)", "share_of_shown_sales_pct": "Share (%)",
        }).drop(columns=["display_name"]), hide_index=True, width="stretch")

with markets_tab:
    section_head("Market performance", "Country-level mix of positive recorded sales", scope_label)
    with st.container(border=True):
        if len(geo) == 1:
            st.info("Only one market is selected. Enable ‘Compare all countries’ to compare geographic contributions.")
        top_countries = geo.head(15).iloc[::-1]
        fig = px.bar(top_countries, x="recorded_sales_gbp", y="Country", orientation="h",
                     color_discrete_sequence=[ACCENT], labels={"recorded_sales_gbp": "Recorded sales (£)"})
        fig.update_traces(hovertemplate="%{y}<br>Recorded sales £%{x:,.2f}<extra></extra>")
        fig.update_xaxes(tickprefix="£", tickformat="~s", showgrid=True, gridcolor="#EDF0F6")
        fig.update_yaxes(showgrid=False, automargin=True)
        st.plotly_chart(style_figure(fig, height=410), width="stretch", config={"displaylogo": False})
    section_head("Market breakdown", "Shares are within the selected countries and dates")
    st.dataframe(geo.rename(columns={"recorded_sales_gbp": "Recorded sales (£)",
                                   "invoices": "Invoices", "share_of_selected_sales_pct": "Share of selection (%)"}),
                 hide_index=True, width="stretch")

with quality_tab:
    section_head("Data quality & definitions", "Auditable preparation choices and limitations")
    q1, q2, q3 = st.columns(3, gap="medium")
    q1.metric("Raw invoice lines", f"{quality.get('raw_rows', 0):,}")
    q2.metric("Exact duplicates removed", f"{quality.get('exact_duplicate_rows_removed', 0):,}")
    q3.metric("Cancellation lines (selection)", f"{len(filtered_cancels):,}")
    st.info("Cancellation lines are counted separately; they have not been reconciled to originating sales and cannot be used here to claim net revenue.")
    with st.container(border=True):
        section_head("Interpretation and limitations", "What the source data can—and cannot—support")
        st.markdown("""
- **Data grain:** one record is an invoice **line**, not a whole order or invoice.
- **Missing customer identifiers:** do not invalidate valid positive line values, but limit customer-level analysis.
- **Exact duplicates:** removed consistently, but identical records could occasionally represent genuine lines; this is a documented assumption.
- **Cancellations:** are isolated using invoice numbers beginning with `C`; no full matched-return ledger is available.
- **Unavailable metrics:** profit, margin, cash receipts, inventory status, marketing performance, and lifetime value.
- **Incomplete period:** December 2011 ends on the 9th and is not a full-month comparison.
        """)
    with st.expander("View complete data preparation audit (JSON)"):
        st.json(quality, expanded=False)

with exports_tab:
    section_head("Download analysis", "Share a reproducible summary or aggregated data tables", "Respects filters")
    st.caption("All reports use the selected countries and inclusive date range. Aggregated exports omit CustomerID and invoice-line records.")
    report = make_markdown_report(
        {"countries": ", ".join(selected_countries), "start": from_date.isoformat(), "end": to_date.isoformat()},
        kpis, monthly, all_products, geo, insights, len(filtered_cancels),
    )
    a, b = st.columns(2, gap="medium")
    with a:
        st.download_button("↓ Download written report (.md)", data=report.encode("utf-8"),
                           file_name="retail_analysis_report.md", mime="text/markdown", width="stretch")
        st.download_button("↓ Download product ranking (.csv)",
                           data=all_products.drop(columns=["display_name"]).to_csv(index=False).encode("utf-8"),
                           file_name="product_ranking.csv", mime="text/csv", width="stretch")
    with b:
        st.download_button("↓ Download monthly trends (.csv)",
                           data=monthly.to_csv(index=False).encode("utf-8"),
                           file_name="monthly_recorded_sales.csv", mime="text/csv", width="stretch")
        st.download_button("↓ Download geographic breakdown (.csv)",
                           data=geo.to_csv(index=False).encode("utf-8"),
                           file_name="country_recorded_sales.csv", mime="text/csv", width="stretch")
    with st.expander("Preview complete written report"):
        st.markdown(report)

st.markdown(
    '<div class="v3-footer">Independent historical analysis · UCI Online Retail (Chen, 2015) · '
    '<a href="https://doi.org/10.24432/C5BW33" target="_blank">DOI: 10.24432/C5BW33</a> · '
    'CC BY 4.0 · Not commissioned client work · Not current business performance</div>',
    unsafe_allow_html=True,
)
