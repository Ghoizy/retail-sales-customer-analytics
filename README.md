# Retail Sales & Customer Analytics — Version 2

**An independent, reproducible portfolio case study based on real UCI Online Retail invoice lines (2010–2011). Not a paid client engagement.**

This project turns historical invoice lines into a filterable dashboard, auditable business metrics, descriptive insights, and downloadable reports. Monetary values remain in **GBP**, because the source is a UK retail dataset. No fabricated retailer name, profit, margin, or live financial figures.

## What's new in V2

- Clean dashboard UI; by default, the view is **United Kingdom** instead of a long list of selected countries.
- All KPI calculations shared and testable in `scripts/analytics.py`.
- Period-aware monthly chart highlights **partial months** (the dataset ends 9 December 2011).
- Products ranked by **StockCode**, with an optional, clearly labeled heuristic to exclude shipping/adjustment codes.
- Descriptive business observations with explicit limitations.
- Download **Markdown analysis**, monthly CSV, product ranking CSV, and market breakdown CSV — respects selected **country/date** filters.
- Automated unit tests and a consistency audit for the actual processed UCI data.

## Data source & license

- Dataset: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online-retail) / Chen, D. (2015), [DOI 10.24432/C5BW33](https://doi.org/10.24432/C5BW33)
- Licensed CC BY 4.0; attribution is kept in the app and exports.
- Published dataset has 541,909 invoice-line records; **invoice lines are not invoices/orders**.
- Some transactions have missing `CustomerID`, and invoice numbers beginning `C` signal cancellations. Our cleaning decisions are logged.
- **Source workbook and processed individual transaction records are not included in Git/this ZIP.**

## Getting started in the user's existing VS Code project

If you already ran V1, **use the V2 patch ZIP** instead of extracting a new full project. The patch only replaces app/docs and adds analytics, validation, and tests. Your existing `data/raw/Online Retail.xlsx`, `data/processed/`, and `.venv` stay in place.

Your existing nested Windows folder layout is likely:

```text
D:\NOUVAL PROJECTS\retail_sales_real_case_study\
├── .venv\
└── retail_sales_real_case_study\       <--- open this inner folder in VS Code
    ├── app.py
    ├── requirements.txt
    ├── data\raw\Online Retail.xlsx
    └── data\processed\...
```

Extract `retail_sales_v2_patch.zip` directly into **the inner folder containing app.py**, allowing replacement of app.py/README/docs. Do not extract it into the outer folder.

From the *inner* folder, in PowerShell:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m scripts.validate
..\.venv\Scripts\python.exe -m streamlit run app.py
```

If the data is missing, first rerun:

```powershell
..\.venv\Scripts\python.exe -m scripts.prepare
```

**You do not need to install a new virtual environment, redo UCI downloads, or regenerate the dataset just because of this patch.** If you use a regular standalone folder with `.venv` inside it, remove the `..` at the start of the path in the above commands.

## How to verify the result

1. Default is UK. Sales should be close to **£9,001,744**, invoices **18,019**, and average invoice value **£499.57**, based on the user's earlier V1 dashboard screenshot (rounded figures).
2. Select **Compare all countries**. Full-source recorded sales should be **£10,642,110.80** for the previously processed data as reported in V1 (full precision shown by validation script).
3. Go to **Products** and compare stock-code rankings; toggle the heuristic filter to understand why results may change while headline recorded sales stays constant.
4. Go to **Download report** and export Markdown/CSV. Change a country/date filter; exports should change consistently.
5. Go to **Data quality** to see how missing IDs and cancellations are treated.

These are regression checks against *previously reported local outputs*, not claims that the full Excel workbook was accessible to the assistant for a new independent audit.

## Definitions and limitations

| Metric | Definition |
|---|---|
| Recorded sales | Sum of positive, non-cancelled, non-exact-duplicate invoice lines (`Quantity * UnitPrice`). **Not reconciled net sales or revenue**. |
| Distinct invoices | Count of distinct `InvoiceNo`, **not** line count. |
| Avg. invoice value | Recorded sales / distinct invoices in current selection. |
| Recorded units | Sum of `Quantity` over selected positive sale lines. |
| Identified customers | Unique non-null `CustomerID` count in selected lines. |
| Product ranking | Group sale lines by StockCode; optional heuristic excludes certain known non-merchandise-like codes. |
| Cancellations | Counted in separate file, **not** linked to originating invoices. |

**Do not claim profit, gross margin, net revenue, customer lifetime value, or causal effects.** This dataset does not have accounting cost, cash, inventory, or marketing channel detail. The raw file ends on 9 December 2011, making Dec 2011 unsuitable for a full-month comparison.

## File map

```text
app.py                        # interactive dashboard and CSV/Markdown downloads
scripts/prepare.py            # original data cleaning and source audit (unchanged in patch)
scripts/analytics.py          # reproducible metrics/filtering/insights
scripts/validate.py           # run consistency checks on processed real data
scripts/__init__.py
tests/test_prepare.py         # original transformation fixtures
tests/test_analytics.py       # KPI, filtering, products, report regression tests
docs/CASE_STUDY.md            # portfolio narrative / findings
 docs/SERVICE_OFFER.md        # ready-to-adapt freelance service packages
 docs/QA_CHECKLIST.md         # publication checklist
 data/raw/                    # official UCI XLSX downloaded by the user, never push to Git
 data/processed/              # CSV and quality JSON created by user, never push to Git
```

## Deployment status

**Local app is ready to validate. Public deployment is NOT completed yet.** The app requires the UCI-generated `data/processed` outputs, which are gitignored. A future public deployment must include a reproducible, appropriately attributed data-loading approach (or a separate, approved published demo dataset). Pushing only this source code to Streamlit Community Cloud without arranging data access will produce the file-missing message.

## Portfolio ethics

Publish this as an **independent public-data case study**, not as a client project. With actual client work, obtain permission for data storage and disclosures, confirm retention/security rules, and agree on reconciliation definitions before quoting metrics.


## Deploy the public dashboard (cloud bootstrap)

Source records and processed files are excluded from Git. When the app runs on a new
Streamlit Community Cloud instance, it downloads the **official UCI ZIP** and
rebuilds processed datasets automatically; existing local data is reused.

See [Cloud deployment guide](docs/CLOUD_DEPLOYMENT.md) for installation,
Python 3.12 selection, deployment, and resource limitations.
