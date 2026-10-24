# Retail Sales & Customer Analytics — Portfolio Case Study

**Project type:** Independent analytics study with a real, published historical dataset. **Not paid client work.**

## Business context

Retail invoice records are often stored as rows of individual items. A stakeholder wants an honest overview of transaction activity by month, product, and geography, without confusing product lines with orders or positive sales with actual cash collected.

## Data

- Source: Chen (2015), UCI Online Retail (CC BY 4.0), DOI 10.24432/C5BW33.
- 1 December 2010 to 9 December 2011; an anonymized, UK-based online retailer.
- 541,909 original lines in the published source; values in GBP.
- Dimensions: invoice number and timestamp, stock code and item description, quantity, unit price, customer ID (partially missing), country.

## Method

1. Preserve invoice-line grain and identify exact duplicate rows.
2. Separate positive sale lines, cancellation lines (`InvoiceNo` begins with `C`), and other records.
3. Audit row counts, missing customer IDs, and value calculations.
4. Create a consistent analytics layer for sales, distinct invoices, average invoice value, units, products, geography and partial-month flags.
5. Present interactive filters, clear chart disclosures, downloadable aggregated CSVs, and a Markdown report.
6. Use automated unit tests and a data consistency check before publication.

## Audited example from first local UCI processing run

The user's first local pipeline run reported: **541,909 raw rows**, **5,268 exact duplicate rows removed**, **524,878 sale lines**, **9,251 cancellation lines**, **2,512 other/invalid lines**, **132,186 sale lines missing customer IDs**, and **£10,642,110.80 positive recorded sales**. These numbers are pipeline outputs, **not verified net revenue**. Rerun `python -m scripts.validate` before publishing final figures.

The earlier dashboard screenshot for United Kingdom showed **about £9.00 million positive recorded sales**, **18,019 distinct invoices**, and an **average invoice value of £499.57** across the selected dates (rounded screenshot values). This descriptive result does not establish profitability or causal business impact.

## What a client can learn from the method

- How to prioritize investigation of high-value merchandise candidates using stock-code rankings.
- Whether a company's observed recorded-sales mix is concentrated in one country.
- Why missing customer IDs limit customer-level analysis without invalidating all sales lines.
- Why partial-month comparisons and unreconciled cancellations need special care.

## Limitations and next work

The dataset lacks COGS, inventory positions, marketing spend, cash settlement, and a ledger linking every cancellation to the original invoice. Product filters use a heuristic, not a validated merchandise catalogue. December 2011 is incomplete. These limits rule out honest net profit, validated retention/CLV, and causal uplift calculations.

**Next step:** use the UCI data as a reproducible public-data demonstration; for real paid projects, request an anonymized sample, align KPI definitions with stakeholders, and perform source-system reconciliations.

## Stack

Python, Pandas, Plotly, Streamlit, pytest, Excel, Git/GitHub.

## Attribution

Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33 · CC BY 4.0.
