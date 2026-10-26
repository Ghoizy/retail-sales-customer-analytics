# Retail Sales & Customer Analytics

**A reproducible retail analytics dashboard built with Python, Pandas, Plotly, and Streamlit.**

[**Live dashboard**](https://retail-sales-ghoizy.streamlit.app/) · [**Case study**](docs/CASE_STUDY.md) · [**Data source**](https://archive.ics.uci.edu/dataset/352/online-retail)

> **Independent portfolio case study, not commissioned client work.** Based on the public **UCI Online Retail** dataset, a historical UK online retail dataset covering **1 Dec 2010–9 Dec 2011**. Monetary values are **GBP (£)**. The dashboard does not represent live business activity.

## Business problem

Retail transaction exports contain invoice-line records, cancellations, missing customer identifiers, and incomplete time periods. Simply summing spreadsheet rows can produce misleading reports.

This project demonstrates a repeatable workflow to **clean and validate invoice-line data**, define business KPIs, analyze performance across **products, months, and countries**, and export the results for stakeholders.

## Dashboard capabilities

- **Sales overview:** recorded sales, distinct invoices, average invoice value, units recorded, and monthly trends.
- **Product analysis:** stock-code rankings with an optional heuristic to exclude known non-merchandise codes.
- **Markets:** country-level breakdown and comparisons.
- **Data quality:** audit results, missing customer IDs, cancellations, and limitations.
- **Interactive filters:** date range and country selection.
- **Export reports:** written Markdown summary plus monthly, product, and country CSVs.
- **Reproducibility:** data preparation scripts, analytics module, validation script, and automated tests.

## Highlights from the complete dataset

| Measure | Result |
|---|---:|
| Original invoice-line records | 541,909 |
| Exact duplicate rows removed | 5,268 |
| Positive sale lines after processing | 524,878 |
| Cancellation lines classified separately | 9,251 |
| Other/invalid lines | 2,512 |
| Recorded sales from positive sale lines | £10,642,110.80 |
| Distinct invoices in sale lines | 19,960 |
| Sale lines missing CustomerID | 132,186 |

**Descriptive findings:** United Kingdom accounts for approximately **84.6%** of recorded sales. **November 2011** has the highest monthly recorded sales in this extract (approximately **£1.50 million**). **December 2011 ends on the 9th**, so its total cannot be compared directly with full calendar months. Around **25.2% of positive sale lines** lack a CustomerID.

These are **pipeline outputs and descriptive findings**, not audited accounting figures, net revenue, profit, or estimates of business uplift.

## Analytics methodology

1. **Ingest** the official UCI workbook and check required columns and record structure.
2. **Classify** exact duplicates, positive sale lines, cancellation lines, and other/invalid records.
3. **Calculate** recorded sales as \`Quantity × UnitPrice\` only for positive non-cancelled invoice lines; count distinct \`InvoiceNo\` values for invoice-based KPIs.
4. **Aggregate** metrics by month, stock code, and country; label incomplete calendar periods.
5. **Validate** counts, country roll-ups, product sorting, and consistency with the data-quality audit.
6. **Present** filtered insights in Streamlit and provide downloadable summaries.

### Important limitations

- **Recorded sales ≠ verified net revenue or cash received.** Cancellations have not been matched back to originating invoices.
- **Profit, margin, retention, customer lifetime value, and ROI cannot be calculated reliably** from this dataset alone.
- Missing customer IDs restrict customer-level analysis.
- Product/merchandise filtering uses heuristics and needs manual review for production accounting.
- Historical data from **2010–2011** should not be presented as current market performance.

## Tech stack

**Python, Pandas, Plotly, Streamlit, openpyxl, pytest, Git/GitHub.**

## Run locally

Tested locally with **Python 3.12**. Clone this repository, set up a virtual environment, and install the requirements:

\`\`\`powershell
git clone https://github.com/Ghoizy/retail-sales-customer-analytics.git
cd retail-sales-customer-analytics
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
\`\`\`

The original workbook and processed CSVs are intentionally **not committed**. To reproduce the dataset locally, download **Online Retail.xlsx** from [UCI](https://archive.ics.uci.edu/dataset/352/online-retail) into \`data/raw/\`, then run:

\`\`\`powershell
.\.venv\Scripts\python.exe -m scripts.prepare
.\.venv\Scripts\python.exe -m scripts.validate
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
\`\`\`

You can also run the Streamlit app directly without the workbook; the cloud bootstrap attempts to download the official public dataset and prepare it. This requires internet access and a working UCI endpoint. Processing the full workbook can be resource-intensive on the first run.

## Project structure

\`\`\`text
app.py                     # Streamlit dashboard + report downloads
scripts/prepare.py         # UCI source cleaning, record classifications, audit
scripts/analytics.py       # Filters, KPI logic, groupings, reports
scripts/validate.py        # Cross-file consistency checks
scripts/cloud_bootstrap.py # First-run UCI data preparation
tests/                     # Unit tests
docs/CASE_STUDY.md         # Case study narrative
docs/SERVICE_OFFER.md      # Example freelance services (not client results)
docs/CLOUD_DEPLOYMENT.md   # Cloud setup notes
data/raw/                  # Local raw data (excluded from Git)
data/processed/            # Generated datasets (excluded from Git)
\`\`\`

## Deployment & quality assurance

**Live:** https://retail-sales-ghoizy.streamlit.app/

The application was deployed on Streamlit Community Cloud and checked for:
- Correct core dashboard KPI values for UK and all countries.
- Filter changes reflected in reported metrics and descriptive insights.
- CSV and Markdown exports matching the chosen filters.
- Public dashboard access through a browser's incognito mode.
- **8 passing automated tests** in the local development environment.

These checks do not prove reconciliation to the original retailer's accounting ledger or guaranteed future cloud uptime. The cloud app may need to re-fetch the UCI data on a fresh server.

## Source and attribution

Chen, D. (2015). **Online Retail**. UCI Machine Learning Repository. [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33). **CC BY 4.0.**

This is an **independent public-data demonstration**. It does not imply an engagement with, endorsement by, or access to private data from the original retailer.
