from datetime import date
import math
import pandas as pd
from scripts.analytics import (
    filter_lines, summarize_sales, monthly_sales, product_ranking, country_ranking,
    build_insights, make_markdown_report,
)


def sample():
    return pd.DataFrame([
        {"InvoiceNo":"100", "StockCode":"A", "Description":"Blue mug", "Quantity":2, "UnitPrice":10., "line_value_gbp":20., "CustomerID":"001", "Country":"United Kingdom", "InvoiceDate":"2011-11-05"},
        {"InvoiceNo":"100", "StockCode":"SKU-B", "Description":"Notebook", "Quantity":3, "UnitPrice":5., "line_value_gbp":15., "CustomerID":"001", "Country":"United Kingdom", "InvoiceDate":"2011-11-05"},
        {"InvoiceNo":"101", "StockCode":"A", "Description":"BLUE MUG", "Quantity":1, "UnitPrice":10., "line_value_gbp":10., "CustomerID":None, "Country":"United Kingdom", "InvoiceDate":"2011-12-05"},
        {"InvoiceNo":"102", "StockCode":"POST", "Description":"Postage", "Quantity":1, "UnitPrice":2., "line_value_gbp":2., "CustomerID":"002", "Country":"France", "InvoiceDate":"2011-12-05"},
        {"InvoiceNo":"103", "StockCode":"SKU-C", "Description":"Bag", "Quantity":2, "UnitPrice":20., "line_value_gbp":40., "CustomerID":"003", "Country":"France", "InvoiceDate":"2011-12-12"},
    ])


def test_filter_inclusive_dates_and_countries():
    actual = filter_lines(sample(), ["United Kingdom"], date(2011, 11, 5), date(2011, 12, 5))
    assert len(actual) == 3
    assert math.isclose(actual["line_value_gbp"].sum(), 45.)
    assert filter_lines(sample(), [], date(2011,11,1), date(2011,12,31)).empty


def test_kpis_are_invoice_based_not_line_based():
    summary = summarize_sales(filter_lines(sample(), ["United Kingdom"], date(2011,11,1), date(2011,12,31)))
    assert summary["invoices"] == 2
    assert summary["sale_lines"] == 3
    assert summary["identified_customers"] == 1
    assert summary["sale_lines_missing_customer_id"] == 1
    assert summary["units_recorded"] == 6
    assert summary["recorded_sales_gbp"] == 45
    assert summary["average_invoice_value_gbp"] == 22.5


def test_month_coverage_partial_flags_and_product_grouping():
    d = sample()
    mo = monthly_sales(d, date(2011,11,1), date(2011,12,31), date(2011,11,1), date(2011,12,12))
    assert mo["partial_period"].tolist() == [False, True]
    assert mo["recorded_sales_gbp"].tolist() == [35, 52]
    rank = product_ranking(d)
    assert "POST" not in rank["StockCode"].to_list()
    a = rank.loc[rank["StockCode"] == "A"].iloc[0]
    assert a["recorded_sales_gbp"] == 30
    assert a["invoices"] == 2
    assert len(rank) == 3  # A, B, C
    including = product_ranking(d, exclude_adjustment_codes=False)
    assert "POST" in including["StockCode"].tolist()


def test_geography_shares_and_report_respect_filter():
    df = sample()
    geo = country_ranking(df)
    assert math.isclose(geo["share_of_selected_sales_pct"].sum(), 100.0)
    mo = monthly_sales(df, date(2011,11,1), date(2011,12,31), date(2011,11,1), date(2011,12,12))
    prods = product_ranking(df)
    insights = build_insights(df, geo, prods, mo)
    assert any("Partial" in x for x in insights)
    report = make_markdown_report(
        {"countries":"United Kingdom, France", "start":"2011-11-01", "end":"2011-12-31"},
        summarize_sales(df), mo, prods, geo, insights, 2,
    )
    assert "£87.00" in report
    assert "NOT reconciled" in report
    assert "2011-12" in report and "partial calendar period" in report
