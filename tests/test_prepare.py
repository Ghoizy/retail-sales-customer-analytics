import pandas as pd
from scripts.prepare import transform


def test_invoice_grain_cancellations_duplicates_and_missing_customer():
    d = pd.DataFrame([
        {"InvoiceNo":"101","StockCode":"SKU1","Description":"Pen","Quantity":2,"InvoiceDate":"2011-01-01","UnitPrice":2.5,"CustomerID":None,"Country":"UK"},
        {"InvoiceNo":"101","StockCode":"SKU2","Description":"Book","Quantity":1,"InvoiceDate":"2011-01-01","UnitPrice":10,"CustomerID":"42","Country":"UK"},
        {"InvoiceNo":"101","StockCode":"SKU2","Description":"Book","Quantity":1,"InvoiceDate":"2011-01-01","UnitPrice":10,"CustomerID":"42","Country":"UK"},  # exact duplicate
        {"InvoiceNo":"C102","StockCode":"SKU1","Description":"Pen","Quantity":-2,"InvoiceDate":"2011-01-02","UnitPrice":2.5,"CustomerID":"42","Country":"UK"},
        {"InvoiceNo":"103","StockCode":"SKU1","Description":"Pen","Quantity":-3,"InvoiceDate":"2011-01-02","UnitPrice":2.5,"CustomerID":"42","Country":"UK"},
    ])
    sales, cancels, quality = transform(d)
    assert len(sales) == 2
    assert sales["InvoiceNo"].nunique() == 1
    assert len(cancels) == 1
    assert quality["exact_duplicate_rows_removed"] == 1
    assert quality["other_or_invalid_rows"] == 1
    assert quality["sale_rows_missing_customer_id"] == 1
    assert quality["recorded_sales_value_gbp"] == 15.0
