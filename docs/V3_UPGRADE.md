# Retail Sales V3 — Clean Modern Business UI

This is a **presentation-only upgrade** of the public UCI Online Retail case study. It does not change `scripts/analytics.py`, `scripts/prepare.py`, `scripts/cloud_bootstrap.py`, source data, CSV export policies, or the recorded sales calculations.

## Visual changes

- Off-white canvas, soft-bordered white KPI cards, restrained indigo accents, consistent typography.
- Responsive four-KPI layout with mini sparklines built from the **current filtered transaction data**.
- Context header with selected scope, date range, source, and GBP currency.
- Compact market selection: “Compare all countries” no longer renders dozens of selected country tags.
- Monthly chart and executive insights side by side on desktop, stacked on small screens.
- Refined Products, Markets, Data Quality, and Download report tabs.
- Accessible business language and explicit historical-data/disclosure notes preserved.

## Apply this patch to your existing project (Windows PowerShell)

1. Before applying the patch, sync your local branch because the online README was updated directly on GitHub:

   ```powershell
   git status --short
   git pull --rebase origin main
   ```

   If `git status` shows uncommitted modifications, review/commit or stash them before pulling.

2. Stop Streamlit with `Ctrl+C` and back up `app.py` **outside the repository**:

   ```powershell
   Copy-Item .\app.py ..\app_before_v3.py
   ```

3. Extract the ZIP's **contents** into the *inner folder* that contains `app.py`:

   ```powershell
   Expand-Archive -Path "$env:USERPROFILE\Downloads\retail_sales_v3_clean_modern_patch.zip" -DestinationPath . -Force
   ```

4. Test using the already-active virtual environment:

   ```powershell
   python -m pytest -q
   python -m scripts.validate
   python -m streamlit run app.py
   ```

5. Check UK default KPIs and all-markets KPIs; test filtering and the 4 report download buttons. Then commit **only the updated files**:

   ```powershell
   git add app.py .streamlit/config.toml .gitignore docs/V3_UPGRADE.md
   git diff --cached --name-only
   git commit -m "Polish retail analytics dashboard with V3 clean business UI"
   git push origin main
   ```

The connected Streamlit Community Cloud app at https://retail-sales-ghoizy.streamlit.app/ should automatically redeploy after the push. If there is a deploy failure, check its logs. Verify cloud filters/exports again after deployment.

## References for regression checks

**UK filter**: Recorded sales ~£9,001,744, distinct invoices 18,019, avg invoice £499.57, units 4,646,906.

**All countries**: Recorded sales ~£10,642,111, distinct invoices 19,960, avg invoice £533.17, units 5,572,420.

The figures are historical positive invoice-line sums. They are not confirmed net revenue, profits, or cash receipts. Dec 2011 is incomplete. Source: UCI Online Retail (Chen 2015), DOI 10.24432/C5BW33, CC BY 4.0.
