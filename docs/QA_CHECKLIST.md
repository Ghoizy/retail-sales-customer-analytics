# V2 quality-control and delivery checklist

## Automated checks

From the inner folder that contains `app.py`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m scripts.validate
```

**Expected:** `5 passed` and 8 `PASS` results (with full UCI output files in `data/processed`). A failing check is a blocker to publication; do not merely ignore the warning.

## Manual dashboard check (5–10 minutes)

- [ ] App opens with United Kingdom selected (no wall of filter chips).
- [ ] KPI matches the previous UK screenshot (up to rounding).
- [ ] `Compare all countries` selects all countries and recorded sales matches the data audit.
- [ ] Changing date range changes KPIs and charts.
- [ ] December 2011 is visibly flagged as a partial calendar period in Sales overview.
- [ ] Product ranking displays real stock codes; optional adjustment-code filter can be toggled.
- [ ] Market chart shows multi-country breakdown when comparison mode is enabled.
- [ ] Data quality clearly describes missing CustomerID, exact duplicates, cancellation lines.
- [ ] Markdown and CSV exports reflect the selected countries/dates.
- [ ] No chart/title calls this *net revenue*, *profit*, or *margin*.
- [ ] At least one mobile/narrow browser screenshot is readable.

## Before public portfolio / client sharing

- [ ] Keep attribution to UCI + DOI and license.
- [ ] No raw customer-level invoices in repository or screenshots.
- [ ] No proprietary client names or fake ROI claims.
- [ ] Screenshot includes public-data case-study disclosure.
- [ ] Use measured findings from the app only, not guessed recommendations.
- [ ] For public hosting, finish data provisioning and verify deployed application.
