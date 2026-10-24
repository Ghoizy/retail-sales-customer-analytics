"""Validate processed data and metric consistency against the recorded audit.
Run: python -m scripts.validate
"""
from __future__ import annotations

import json
from pathlib import Path
import math
import pandas as pd
from scripts.analytics import country_ranking, summarize_sales, product_ranking

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def run() -> None:
    sales_file = PROCESSED / "sales_lines.csv"
    quality_file = PROCESSED / "data_quality.json"
    cancel_file = PROCESSED / "cancellation_lines.csv"
    if not all(p.exists() for p in (sales_file, quality_file, cancel_file)):
        raise SystemExit("File processed belum lengkap. Jalankan python -m scripts.prepare dahulu.")
    df = pd.read_csv(sales_file, dtype={"InvoiceNo":"string", "StockCode":"string", "CustomerID":"string"})
    cancels = pd.read_csv(cancel_file, dtype={"InvoiceNo":"string"})
    quality = json.loads(quality_file.read_text(encoding="utf-8"))
    kpis = summarize_sales(df)
    geography = country_ranking(df)
    products = product_ranking(df)

    checks = {
        "sale line count matches audit": len(df) == quality["sale_line_rows"],
        "cancellation line count matches audit": len(cancels) == quality["cancellation_line_rows"],
        "recorded sales value matches audit": math.isclose(
            kpis["recorded_sales_gbp"], quality["recorded_sales_value_gbp"], abs_tol=0.02),
        "missing CustomerID matches audit": kpis["sale_lines_missing_customer_id"] == quality["sale_rows_missing_customer_id"],
        "country totals equal recorded sales": math.isclose(geography["recorded_sales_gbp"].sum(),kpis["recorded_sales_gbp"],abs_tol=0.02),
        "only positive quantities and unit prices in sale records": bool((df["Quantity"] > 0).all() and (df["UnitPrice"] > 0).all()),
        "all record types labelled sale": bool(df["record_type"].eq("sale").all()),
        "product ranking sorted descending": bool(products["recorded_sales_gbp"].is_monotonic_decreasing),
    }
    print("\nRETAIL ANALYTICS — DATA VALIDATION\n")
    for label, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} | {label}")
    print(f"\nValidated sales: £{kpis['recorded_sales_gbp']:,.2f} | {kpis['invoices']:,} invoices | {len(df):,} sales lines")
    if not all(checks.values()):
        raise SystemExit("Some checks failed. Review dataset and prepare script before publication.")
    print("\nAll automated consistency checks PASSED. These do not prove reconciliation to accounting records.")


if __name__ == "__main__":
    run()
