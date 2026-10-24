"""Convert official UCI Online Retail workbook into audited, analysis-ready files.

Run from repository root:
    python -m scripts.prepare

Source: Daqing Chen (2015), Online Retail, UCI ML Repository, CC BY 4.0.
https://doi.org/10.24432/C5BW33
"""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "Online Retail.xlsx"
OUT = ROOT / "data" / "processed"
EXPECTED = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}


def transform(source: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Categorize source records without inventing columns absent from dataset."""
    missing = EXPECTED - set(source.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = source.copy()
    original_rows = len(df)
    exact_duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype("string").str.strip()
    df["StockCode"] = df["StockCode"].astype("string").str.strip()
    df["Description"] = df["Description"].astype("string").str.strip()
    df["Country"] = df["Country"].astype("string").str.strip()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["CustomerID"] = df["CustomerID"].astype("string").str.replace(r"\.0$", "", regex=True)
    df["line_value_gbp"] = df["Quantity"] * df["UnitPrice"]
    df["is_cancellation"] = df["InvoiceNo"].str.upper().str.startswith("C", na=False)

    required_valid = (df["InvoiceNo"].notna() & df["InvoiceDate"].notna()
                      & df["Country"].notna() & df["StockCode"].notna())
    normal_sales = required_valid & (~df["is_cancellation"]) & (df["Quantity"] > 0) & (df["UnitPrice"] > 0)
    cancellations = required_valid & df["is_cancellation"] & (df["Quantity"] < 0) & (df["UnitPrice"] > 0)
    df["record_type"] = "other_or_invalid"
    df.loc[normal_sales, "record_type"] = "sale"
    df.loc[cancellations, "record_type"] = "cancellation"

    # IMPORTANT: Row grain = invoice line item. Multiple lines may share invoice number.
    sales = df.loc[df["record_type"] == "sale"].copy()
    cancelled = df.loc[df["record_type"] == "cancellation"].copy()
    other = df.loc[df["record_type"] == "other_or_invalid"].copy()
    report = {
        "source": "UCI Online Retail (Chen, 2015); 2010-12-01 to 2011-12-09; CC BY 4.0",
        "currency": "GBP",
        "raw_rows": original_rows,
        "exact_duplicate_rows_removed": exact_duplicate_count,
        "rows_after_dedup": len(df),
        "sale_line_rows": len(sales),
        "cancellation_line_rows": len(cancelled),
        "other_or_invalid_rows": len(other),
        "sale_rows_missing_customer_id": int(sales["CustomerID"].isna().sum()),
        "recorded_sales_value_gbp": round(float(sales["line_value_gbp"].sum()), 2),
        "cancellation_lines_absolute_value_gbp": round(float(cancelled["line_value_gbp"].abs().sum()), 2),
        "interpretation": (
            "Recorded sales value sums positive non-cancelled invoice lines. "
            "It is NOT confirmed net revenue, profit, or actual cash received. "
            "Cancellations are shown separately; matching cancellations to original sales "
            "requires additional reconciliation. Customer IDs can be missing."
        ),
    }
    return sales, cancelled, {**report, "other_rows": other}


def run() -> None:
    if not RAW_FILE.exists():
        raise SystemExit(
            "Dataset belum ada. Unduh 'Online Retail.xlsx' dari "
            "https://archive.ics.uci.edu/dataset/352/online-retail, "
            f"lalu simpan di: {RAW_FILE}"
        )
    OUT.mkdir(exist_ok=True, parents=True)
    source = pd.read_excel(RAW_FILE, dtype={"InvoiceNo": "string", "StockCode": "string"})
    sales, cancelled, bundle = transform(source)
    other = bundle.pop("other_rows")
    sales.to_csv(OUT / "sales_lines.csv", index=False)
    cancelled.to_csv(OUT / "cancellation_lines.csv", index=False)
    other.to_csv(OUT / "other_lines.csv", index=False)
    (OUT / "data_quality.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print("UCI dataset berhasil diproses.\n")
    for k, v in bundle.items():
        print(f"{k}: {v}")
    print(f"\nOutput ada di {OUT}")


if __name__ == "__main__":
    run()
