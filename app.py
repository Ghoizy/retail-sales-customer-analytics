"""Retail Sales & Customer Analytics: independently reproducible UCI case study.

Run after: python -m scripts.prepare
Then:      python -m streamlit run app.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from scripts.analytics import (
    build_insights, country_ranking, filter_lines, make_markdown_report,
    monthly_sales, product_ranking, summarize_sales,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
SALES_PATH = DATA / "sales_lines.csv"
CANCEL_PATH = DATA / "cancellation_lines.csv"
QUALITY_PATH = DATA / "data_quality.json"
ACCENT = "#6158D8"
INK = "#192033"

st.set_page_config(
    page_title="Retail Sales Intelligence | Historical Case Study",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {color-scheme:light}
.block-container {max-width:1390px; padding-top:1.2rem; padding-bottom:3rem}
h1, h2, h3 {letter-spacing:-.035em !important; color:#192033}
[data-testid="stMetric"] {padding:19px 20px; border-radius:16px; background:#fff;
    border:1px solid #E8EAF1; box-shadow:0 2px 8px rgba(32,34,78,.025)}
[data-testid="stMetricLabel"] {color:#727B8F}
[data-testid="stMetricValue"] {font-size:1.75rem; letter-spacing:-.04em}
[data-testid="stSidebar"] {border-right:1px solid #E7E9F2}
[data-testid="stTabs"] [role="tab"] {font-size:.97rem}
.hero-tag {display:inline-block; color:#6158D8; border:1px solid #E4DFFE;
    padding:6px 11px; border-radius:24px; font-size:12px; font-weight:650; letter-spacing:.045em}
.hero-title {font-size:2.35rem; font-weight:780; color:#192033; letter-spacing:-.05em;
    margin:13px 0 2px; line-height:1.17}
.hero-sub {color:#727B8F; font-size:14px; margin-bottom:14px}
.note {border:1px solid #E6E4FB; background:#F7F6FF; padding:12px 15px;
    border-radius:12px; font-size:13px; color:#4B5180; margin:8px 0 20px}
@media(max-width:768px){.hero-title{font-size:1.8rem}}
</style>
""", unsafe_allow_html=True)


def gbp(value: float, decimals: int = 0) -> str:
    return f"£{value:,.{decimals}f}"


def style_figure(fig: go.Figure, *, height: int = 385) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=28, b=16),
        font=dict(family="Arial, sans-serif", color=INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", font=dict(color=INK)),
    )
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="#E9ECF3", zeroline=False)
    return fig


@st.cache_data(show_spinner="Loading audited transactions...")
def load_processed(sales_mtime: int, quality_mtime: int, cancellation_mtime: int):
    # The modification timestamps invalidate Streamlit's cache after reprocessing.
    sales = pd.read_csv(
        SALES_PATH, parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string", "Country": "string"},
    )
    cancels = pd.read_csv(
        CANCEL_PATH, parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string", "Country": "string"},
    )
    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    return sales, cancels, quality


missing = [p.name for p in (SALES_PATH, CANCEL_PATH, QUALITY_PATH) if not p.exists()]
if missing:
    st.error("File hasil proses belum lengkap: " + ", ".join(missing))
    st.code("..\\.venv\\Scripts\\python.exe -m scripts.prepare", language="powershell")
    st.caption("Jalankan dari folder yang berisi app.py, setelah menaruh Online Retail.xlsx di data/raw/.")
    st.stop()

sales, cancellations, quality = load_processed(
    SALES_PATH.stat().st_mtime_ns, QUALITY_PATH.stat().st_mtime_ns, CANCEL_PATH.stat().st_mtime_ns
)

source_start = sales["InvoiceDate"].min().date()
source_end = sales["InvoiceDate"].max().date()
all_countries = sorted(sales["Country"].dropna().unique().tolist())
if "selected_countries" not in st.session_state:
    st.session_state["selected_countries"] = (["United Kingdom"] if "United Kingdom" in all_countries else all_countries[:1])

def sync_country_scope():
    st.session_state["selected_countries"] = (
        all_countries if st.session_state["compare_all"]
        else (["United Kingdom"] if "United Kingdom" in all_countries else all_countries[:1])
    )


with st.sidebar:
    st.markdown("### Sales Intelligence")
    st.caption("Independent retail case study · UCI 2010–2011")
    st.divider()
    st.markdown("#### Analysis filters")
    show_all = st.checkbox("Compare all countries", value=False, key="compare_all",
                           on_change=sync_country_scope,
                           help="Unchecked starts with United Kingdom to keep the first view focused.")
    selected_countries = st.multiselect("Countries", options=all_countries,
                                       key="selected_countries")
    chosen = st.date_input("Invoice dates", value=(source_start, source_end),
                           min_value=source_start, max_value=source_end)
    st.caption("Dates include both endpoints. First and last months may be incomplete.")
    st.divider()
    st.markdown("#### Provenance")
    st.markdown("[UCI Online Retail — Chen (2015)](https://archive.ics.uci.edu/dataset/352/online-retail)")
    st.caption("CC BY 4.0 · DOI: 10.24432/C5BW33 · GBP (£)")
    st.caption("No customer data is included in dashboard exports.")

st.markdown("""
<div class="hero-tag">DATA ANALYTICS · PORTFOLIO CASE STUDY</div>
<div class="hero-title">Retail Sales &amp; Customer Analytics</div>
<div class="hero-sub">Recorded invoice-line activity · United Kingdom &amp; global markets · Dec 2010–Dec 2011</div>
<div class="note"><b>Data interpretation:</b> Public, historical records—not a paid client engagement. Recorded sales includes positive sales lines and is <b>not</b> confirmed net revenue, profit, or cash receipts. Cancellations require reconciliation.</div>
""", unsafe_allow_html=True)

if not isinstance(chosen, (tuple, list)) or len(chosen) != 2:
    st.warning("Choose the start and end dates to view analytics.")
    st.stop()
from_date, to_date = chosen
filtered = filter_lines(sales, selected_countries, from_date, to_date)
if filtered.empty:
    st.warning("No recorded sales match the selected countries and dates. Change the filters.")
    st.stop()
filtered_cancels = filter_lines(cancellations, selected_countries, from_date, to_date)
kpis = summarize_sales(filtered)
monthly = monthly_sales(filtered, from_date, to_date, source_start, source_end)
all_product_ranking = product_ranking(filtered, exclude_adjustment_codes=True)
geo = country_ranking(filtered)
insights = build_insights(filtered, geo, all_product_ranking, monthly)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Recorded sales", gbp(kpis["recorded_sales_gbp"]))
m2.metric("Distinct invoices", f"{kpis['invoices']:,}")
m3.metric("Avg. invoice value", gbp(kpis["average_invoice_value_gbp"], 2))
m4.metric("Recorded units", f"{kpis['units_recorded']:,}")
st.caption("Invoice count = distinct InvoiceNo, not the number of line items. All KPIs reflect current filters.")

with st.expander("Key observations for the current selection", expanded=True):
    for item in insights:
        st.markdown(f"- {item}")
    st.caption("These are descriptive findings, not proof of causation, profitability, or growth opportunities.")

sales_tab, products_tab, markets_tab, quality_tab, exports_tab = st.tabs(
    ["Sales overview", "Products", "Markets", "Data quality", "Download report"]
)

with sales_tab:
    st.markdown("#### Monthly sales trend")
    st.caption("Partial calendar periods are identified; don't compare them directly against complete months.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["recorded_sales_gbp"],
        name="Recorded sales", mode="lines+markers", line=dict(color=ACCENT, width=3),
        marker=dict(size=8),
        customdata=monthly[["period_note", "invoices"]].to_numpy(),
        hovertemplate="%{x|%b %Y}<br>Recorded sales: £%{y:,.2f}<br>Invoices: %{customdata[1]:,}<br>%{customdata[0]}<extra></extra>",
    ))
    partial_months = monthly.loc[monthly["partial_period"]]
    if not partial_months.empty:
        fig.add_trace(go.Scatter(
            x=partial_months["month"], y=partial_months["recorded_sales_gbp"],
            mode="markers", name="Partial calendar period",
            marker=dict(color="#E98F43", size=13, symbol="circle-open", line=dict(width=3)),
            hovertemplate="%{x|%b %Y}: partial calendar period<extra></extra>",
        ))
    fig.update_yaxes(tickprefix="£", tickformat="~s")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.03, x=0))
    st.plotly_chart(style_figure(fig, height=405), width="stretch")
    summary_left, summary_right = st.columns(2)
    with summary_left:
        st.metric("Distinct identified customers", f"{kpis['identified_customers']:,}")
        st.caption("Excludes lines with missing CustomerID; don't treat as total real customers.")
    with summary_right:
        percent_missing = kpis["sale_lines_missing_customer_id"] / kpis["sale_lines"] * 100
        st.metric("Sales lines missing Customer ID", f"{percent_missing:.1f}%")
        st.caption("Sales from unidentified customers remain in the recorded sales total.")

with products_tab:
    st.markdown("#### Product performance")
    product_toggle = st.checkbox(
        "Exclude common shipping/adjustment codes (heuristic)", value=True,
        help="Applies only to this product analysis; the top dashboard KPI is unchanged. Manually verify the classification with a real client.",
    )
    prods = product_ranking(filtered, exclude_adjustment_codes=product_toggle)
    if prods.empty:
        st.info("No product candidate remains after these filters.")
    else:
        top = prods.head(12).iloc[::-1]
        fig = px.bar(top, x="recorded_sales_gbp", y="display_name", orientation="h",
                     labels={"recorded_sales_gbp":"Recorded sales (£)", "display_name":"Stock code · description"},
                     color_discrete_sequence=[ACCENT])
        fig.update_traces(hovertemplate="%{y}<br>Recorded sales: £%{x:,.2f}<extra></extra>")
        fig.update_xaxes(tickprefix="£", tickformat="~s", showgrid=True, gridcolor="#E9ECF3")
        fig.update_yaxes(showgrid=False, automargin=True)
        st.plotly_chart(style_figure(fig, height=485), width="stretch")
        st.caption("Product ranking groups by StockCode (not by description alone). Shares are of included product-analysis lines, not necessarily total business sales.")
        st.dataframe(prods.head(30).rename(columns={
            "StockCode":"Stock code", "Description":"Description", "units":"Units",
            "invoices":"Invoices", "recorded_sales_gbp":"Recorded sales (£)",
            "share_of_shown_sales_pct":"Share (%)",
        }).drop(columns=["display_name"]), hide_index=True, width="stretch")

with markets_tab:
    st.markdown("#### Geographic revenue concentration")
    st.caption("For meaningful comparisons between countries, select 'Compare all countries' in the sidebar.")
    top_countries = geo.head(15)
    fig = px.bar(top_countries, x="Country", y="recorded_sales_gbp",
                 color_discrete_sequence=[ACCENT],
                 labels={"recorded_sales_gbp":"Recorded sales (£)"})
    fig.update_traces(hovertemplate="%{x}<br>Recorded sales: £%{y:,.2f}<extra></extra>")
    fig.update_yaxes(tickprefix="£", tickformat="~s")
    st.plotly_chart(style_figure(fig, height=390), width="stretch")
    st.dataframe(geo.rename(columns={
        "Country":"Country", "recorded_sales_gbp":"Recorded sales (£)",
        "invoices":"Invoices", "share_of_selected_sales_pct":"Share of selection (%)"
    }), hide_index=True, width="stretch")

with quality_tab:
    st.markdown("#### Reliability & dataset audit")
    left, right, third = st.columns(3)
    left.metric("Raw invoice lines", f"{quality.get('raw_rows', 0):,}")
    right.metric("Exact duplicates removed", f"{quality.get('exact_duplicate_rows_removed', 0):,}")
    third.metric("Cancellation lines (selection)", f"{len(filtered_cancels):,}")
    st.caption("Filtered cancellations are counted separately. They are NOT matched to original invoice lines or subtracted to claim net revenue.")
    st.markdown("**Quality checks and caveats**")
    st.markdown("""
    - **Line-item grain:** one row represents an invoice line, not a whole invoice/order.
    - **Missing customers:** missing CustomerID does not invalidate line-level sales amounts.
    - **Exact duplicates:** removed by the preparation script, although identical invoice lines can sometimes be genuine; this is a reproducible assumption, not guaranteed reconciliation.
    - **Returns:** invoice numbers beginning C are isolated; source does not provide a full matched-return ledger.
    - **Not available:** costs, profit/margin, marketing channels, payment settlement, inventory availability.
    - **Historical:** December 2011 ends on the 9th; don't interpret the month's apparent decline as a full-month comparison.
    """)
    with st.expander("Show complete preparation audit JSON"):
        st.json(quality, expanded=False)

with exports_tab:
    st.markdown("#### Export analysis for a portfolio case study or review")
    st.caption("All reports below use the country and date filters currently selected. Aggregated downloads exclude CustomerID and invoice-level records.")
    report = make_markdown_report(
        {"countries": ", ".join(selected_countries), "start":from_date.isoformat(), "end":to_date.isoformat()},
        kpis, monthly, all_product_ranking, geo, insights, len(filtered_cancels),
    )
    a, b, c = st.columns(3)
    a.download_button("Download written report (.md)", data=report.encode("utf-8"),
                      file_name="retail_analysis_report.md", mime="text/markdown", width="stretch")
    b.download_button("Download monthly trends (.csv)",
                      data=monthly.to_csv(index=False).encode("utf-8"),
                      file_name="monthly_recorded_sales.csv", mime="text/csv", width="stretch")
    c.download_button("Download product ranking (.csv)",
                      data=all_product_ranking.drop(columns=["display_name"]).to_csv(index=False).encode("utf-8"),
                      file_name="product_ranking.csv", mime="text/csv", width="stretch")
    st.download_button("Download geographic breakdown (.csv)",
                       data=geo.to_csv(index=False).encode("utf-8"),
                       file_name="country_recorded_sales.csv", mime="text/csv")
    st.markdown("**Report preview**")
    st.code("\n".join(report.splitlines()[:17]), language="markdown")

st.divider()
st.caption("Independent historical analysis · UCI Online Retail (Chen, 2015) · CC BY 4.0 · DOI: 10.24432/C5BW33 · No performance claims for today's market")
