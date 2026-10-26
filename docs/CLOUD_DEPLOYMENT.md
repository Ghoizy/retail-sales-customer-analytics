# Deploying to Streamlit Community Cloud

This app uses the **official historical UCI Online Retail dataset** (Chen, 2015; CC BY 4.0; DOI: 10.24432/C5BW33).

The GitHub repository excludes raw and processed transaction data by design. If data files are absent on cloud boot, `app.py` calls `scripts.cloud_bootstrap.ensure_prepared_data()` to download the **official UCI ZIP** and process it using `scripts.prepare`.

## Push this cloud patch

Extract the provided patch into the project folder **containing app.py** (not the outer folder with `.venv`). Copy files into the existing folders, replace `app.py`, and preserve your local `data/` folder. No need to re-download the dataset locally.

From that folder, in VS Code terminal:

```powershell
git status --short
python -m pytest -q
python -m scripts.validate
git add .
git commit -m "Enable automatic UCI data preparation on cloud"
git push origin main
```

## Deploy

1. Go to https://share.streamlit.io/ and sign in with GitHub.
2. Create app → choose existing app/repository.
3. Repository: `Ghoizy/retail-sales-customer-analytics`; branch: `main`; main file: `app.py`.
4. In advanced settings select Python **3.12**, matching the local development environment.
5. Deploy. **The first boot can take longer than usual** because the instance downloads and parses a 22.6 MB Excel dataset. The cloud may re-download on restart because filesystem is ephemeral.
6. Verify KPI (default UK about £9,001,744; full selection £10,642,110.80), filtering and download.

## Troubleshooting

- `Unable to prepare official UCI dataset`: inspect cloud app logs. The UCI download may be blocked/unavailable, or cloud instance may run out of memory during Excel parsing. Do **not** claim live deployment succeeded until checked.
- `Memory limit reached`: don't repeatedly redeploy. Next step is a precomputed aggregate dataset for the public demo (not original invoice/customer rows). This is a potential alternative, not implemented by this patch.
- Locally, if data is already processed, `scripts.cloud_bootstrap` does not download anything. If files are missing and you have the original workbook, it processes the local file without downloading.
- No secrets or GitHub tokens should be added to Git.

This is an independent public-data case study, **not paid client work**. Values are recorded invoice-line sales, **not net revenue or profit**.
