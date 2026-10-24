# Changelog

## V2 — 23 October 2026

- Split analytics from the Streamlit UI for reproducibility and unit testing.
- Added monthly chart coverage labels for incomplete calendar months.
- Changed default country filter to UK, with a control to compare all countries.
- Rank candidate merchandise by stock code and separate common adjustment codes heuristically.
- Added filtered observations, data-quality tab, downloadable Markdown and aggregate CSV reports.
- Added `scripts.validate` for live, processed-data consistency checks.
- Added regression tests, case study, offers, and QA checklist.
- Preserved V1 data preparation and source/license attribution.

**Open:** Validate the updated Streamlit UI against the user's full local UCI data; configure a public host data source; publish a demo URL; add final screenshots to portfolio.
