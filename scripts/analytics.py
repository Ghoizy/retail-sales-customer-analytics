"""Pure, testable analytics functions for the historical UCI Online Retail case study.

Assumptions: sale rows are already classified by scripts.prepare; they represent
positive invoice lines, NOT net cash revenue, profit, or unique purchases.
"""
from __future__ import annotations

import calendar
from datetime import date
from typing import Any

import pandas as pd

# Heuristic codes usually associated with postage, discounts, corrections or
# other non-merchandise entries. They are NOT a verified product taxonomy.
NON_MERCHANDISE_CODES = frozenset({
    "POST", "DOT", "M", "D", "BANK CHARGES", "AMAZONFEE",
    "CRUK", "C2", "S", "PADS", "B", "ADJUST", "ADJUST2",
})


def filter_lines(
    df: pd.DataFrame,
    selected_countries: list[str],
    date_from: date,
    date_to: date,
) -> pd.DataFrame:
    """Apply user-selected date and country filters, inclusive of both dates."""
    if date_from > date_to or not selected_countries:
        return df.iloc[0:0].copy()
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    mask = (
        df["Country"].isin(selected_countries)
        & dates.ge(pd.Timestamp(date_from))
        & dates.lt(pd.Timestamp(date_to) + pd.Timedelta(days=1))
    )
    return df.loc[mask].copy()


def summarize_sales(df: pd.DataFrame) -> dict[str, int | float]:
    """All results use the SAME filtered frame and positive sales-line policy."""
    invoices = int(df["InvoiceNo"].nunique())
    sales = float(df["line_value_gbp"].sum())
    return {
        "recorded_sales_gbp": sales,
        "invoices": invoices,
        "average_invoice_value_gbp": sales / invoices if invoices else 0.0,
        "units_recorded": int(df["Quantity"].sum()),
        "identified_customers": int(df["CustomerID"].nunique()),
        "sale_lines": int(len(df)),
        "sale_lines_missing_customer_id": int(df["CustomerID"].isna().sum()),
    }


def monthly_sales(
    df: pd.DataFrame,
    date_from: date,
    date_to: date,
    source_start: date,
    source_end: date,
) -> pd.DataFrame:
    """Aggregate by invoice month, marking calendar months partly covered.

    This is calendar coverage, NOT proof that all invoices were collected.
    """
    cols = ["month", "recorded_sales_gbp", "invoices", "period_note", "partial_period"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    month_key = pd.to_datetime(df["InvoiceDate"]).dt.to_period("M").dt.to_timestamp()
    monthly = (
        df.assign(month=month_key)
        .groupby("month", as_index=False)
        .agg(recorded_sales_gbp=("line_value_gbp", "sum"), invoices=("InvoiceNo", "nunique"))
        .sort_values("month")
    )
    effective_start = max(date_from, source_start)
    effective_end = min(date_to, source_end)
    def note(month: pd.Timestamp) -> str:
        first = date(month.year, month.month, 1)
        last = date(month.year, month.month, calendar.monthrange(month.year, month.month)[1])
        return "Partial calendar period" if (effective_start > first or effective_end < last) else "Full calendar period in selected range"
    monthly["period_note"] = monthly["month"].apply(note)
    monthly["partial_period"] = monthly["period_note"].eq("Partial calendar period")
    return monthly[cols]


def product_ranking(df: pd.DataFrame, exclude_adjustment_codes: bool = True) -> pd.DataFrame:
    """Aggregate by StockCode, choose representative description per code.

    Exclusion is a heuristic VIEW filter for product analysis; dashboard-level
    KPI recorded sales deliberately retain all valid positive sale lines.
    """
    cols = ["StockCode", "Description", "units", "invoices", "recorded_sales_gbp", "share_of_shown_sales_pct", "display_name"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    source = df.copy()
    source["StockCode"] = source["StockCode"].astype("string").fillna("UNKNOWN")
    if exclude_adjustment_codes:
        source = source.loc[~source["StockCode"].str.upper().isin(NON_MERCHANDISE_CODES)].copy()
    if source.empty:
        return pd.DataFrame(columns=cols)
    source["Description"] = source["Description"].astype("string").fillna("No description")
    agg = (
        source.groupby("StockCode", dropna=False)
        .agg(
            units=("Quantity", "sum"),
            invoices=("InvoiceNo", "nunique"),
            recorded_sales_gbp=("line_value_gbp", "sum"),
            Description=("Description", lambda x: x.mode().iloc[0] if not x.mode().empty else "No description"),
        )
        .reset_index()
        .sort_values(["recorded_sales_gbp", "StockCode"], ascending=[False, True])
    )
    total = float(agg["recorded_sales_gbp"].sum())
    agg["share_of_shown_sales_pct"] = (agg["recorded_sales_gbp"] / total * 100) if total else 0.0
    agg["display_name"] = agg.apply(
        lambda x: f"{str(x['StockCode'])} · {str(x['Description'])[:48]}", axis=1
    )
    return agg[cols]


def country_ranking(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Country", "recorded_sales_gbp", "invoices", "share_of_selected_sales_pct"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    geo = (
        df.groupby("Country", as_index=False)
        .agg(recorded_sales_gbp=("line_value_gbp", "sum"), invoices=("InvoiceNo", "nunique"))
        .sort_values("recorded_sales_gbp", ascending=False)
    )
    total = float(geo["recorded_sales_gbp"].sum())
    geo["share_of_selected_sales_pct"] = (geo["recorded_sales_gbp"] / total * 100) if total else 0.0
    return geo[cols]


def build_insights(
    sales: pd.DataFrame,
    countries: pd.DataFrame,
    products: pd.DataFrame,
    monthly: pd.DataFrame,
) -> list[str]:
    """Grounded descriptive findings only: no causal or profit claims."""
    if sales.empty:
        return ["No recorded sales in current selection."]
    summary = summarize_sales(sales)
    findings = []
    if len(countries) > 1:
        leader = countries.iloc[0]
        findings.append(
            f"{leader['Country']} contributes {leader['share_of_selected_sales_pct']:.1f}% "
            "of recorded sales within the selected countries and dates."
        )
    if len(products):
        top = products.iloc[0]
        findings.append(
            f"Highest-value merchandise candidate: stock code {top['StockCode']} "
            f"(£{top['recorded_sales_gbp']:,.0f} recorded sales; "
            f"{top['share_of_shown_sales_pct']:.1f}% of included product-analysis lines)."
        )
    if summary["sale_lines"]:
        missing = 100 * summary["sale_lines_missing_customer_id"] / summary["sale_lines"]
        findings.append(
            f"{missing:.1f}% of included positive sales lines lack CustomerID. "
            "Customer-level conclusions should use only identified records."
        )
    if bool(monthly["partial_period"].any()):
        labels = ", ".join(monthly.loc[monthly["partial_period"], "month"].dt.strftime("%b %Y"))
        findings.append(f"Partial calendar periods in trend: {labels}; avoid treating their totals as full-month comparisons.")
    return findings


def make_markdown_report(
    filters: dict[str, Any],
    kpis: dict[str, int | float],
    monthly: pd.DataFrame,
    products: pd.DataFrame,
    countries: pd.DataFrame,
    insights: list[str],
    cancellations_count: int,
) -> str:
    fmt = lambda x: f"£{x:,.2f}"
    summary = [
        "# Retail Sales & Customer Analytics — Filtered Report",
        "", "**Independent historical public-data case study; not commissioned client work.**", "",
        f"- Countries: {filters['countries']}",
        f"- Invoice dates (inclusive): {filters['start']} to {filters['end']}",
        "- Source: Chen (2015), UCI Online Retail, CC BY 4.0, DOI: 10.24432/C5BW33",
        "", "## KPI summary", "",
        f"- Recorded sales (positive sale lines): {fmt(float(kpis['recorded_sales_gbp']))}",
        f"- Distinct invoices: {int(kpis['invoices']):,}",
        f"- Average invoice value: {fmt(float(kpis['average_invoice_value_gbp']))}",
        f"- Units recorded: {int(kpis['units_recorded']):,}",
        f"- Identified customers: {int(kpis['identified_customers']):,} (missing IDs excluded)",
        f"- Cancellation lines in matching filter: {cancellations_count:,} (NOT reconciled)",
        "", "## Descriptive findings", "",
        *(f"- {item}" for item in insights),
        "", "## Top merchandise candidates by recorded sales", "",
    ]
    for _, row in products.head(10).iterrows():
        summary.append(f"- {row['StockCode']} — {row['Description']}: {fmt(float(row['recorded_sales_gbp']))}")
    summary += ["", "## Top countries in selection", ""]
    for _, row in countries.head(10).iterrows():
        summary.append(f"- {row['Country']}: {fmt(float(row['recorded_sales_gbp']))} ({row['share_of_selected_sales_pct']:.1f}%)")
    summary += ["", "## Monthly recorded sales", ""]
    for _, row in monthly.iterrows():
        qualifier = " [partial calendar period]" if row["partial_period"] else ""
        summary.append(f"- {row['month']:%Y-%m}: {fmt(float(row['recorded_sales_gbp']))}{qualifier}")
    summary += [
        "", "## Limitations and next steps", "",
        "- The dataset records invoice lines, not confirmed receipts or reconciled net revenue.",
        "- Cancellations were not matched to their originating sales; do not interpret as net sales.",
        "- Product filtering omits selected non-merchandise codes using a heuristic (review exceptions manually).",
        "- Product shares use the subset shown in the Products analysis, not necessarily all recorded sales.",
        "- Dataset lacks costs and payment settlements. Profit, margin, ROI, and customer lifetime value are not calculated.",
        "- Historical coverage is 2010–2011; this report is not current business performance.",
        "- Suggested follow-up: validate product mapping, reconcile returns, and assess complete-period trends.",
        "",
    ]
    return "\n".join(summary)
