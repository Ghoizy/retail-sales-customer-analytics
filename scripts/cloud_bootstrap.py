"""Bootstrap UCI Online Retail on an ephemeral Streamlit server.

Source: Chen (2015), UCI Online Retail (CC BY 4.0).
https://doi.org/10.24432/C5BW33

Only called when the already-prepared CSVs are absent; never overwrites a
complete local dataset. This is an on-demand online download, so the first
cloud visit may take longer and depends on the UCI host being available.
"""
from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path

from scripts import prepare

# Official direct link exposed by the Download button on the UCI dataset page.
DATASET_ZIP_URL = "https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip"
REQUIRED_OUTPUTS = ("sales_lines.csv", "cancellation_lines.csv", "data_quality.json")
MAX_ZIP_BYTES = 60 * 1024 * 1024
MAX_WORKBOOK_BYTES = 100 * 1024 * 1024


def _download_workbook(raw_file: Path, url: str = DATASET_ZIP_URL) -> None:
    """Download and extract only the expected workbook from the official ZIP."""
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    archive = raw_file.parent / ".uci_online_retail_download.zip"
    partial_workbook = raw_file.parent / ".online_retail_partial.xlsx"
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "RetailSalesPortfolio/1.0 (UCI attributed public dataset)"},
        )
        with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as target:
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ZIP_BYTES:
                    raise ValueError("Dataset archive exceeded expected size; refusing download")
                target.write(chunk)

        with zipfile.ZipFile(archive) as zf:
            members = [m for m in zf.infolist()
                       if not m.is_dir() and Path(m.filename).name == "Online Retail.xlsx"]
            if len(members) != 1:
                raise ValueError("Official archive does not contain one 'Online Retail.xlsx'")
            member = members[0]
            if member.file_size > MAX_WORKBOOK_BYTES:
                raise ValueError("Source workbook exceeds expected size")
            with zf.open(member) as source, partial_workbook.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            partial_workbook.replace(raw_file)
    finally:
        archive.unlink(missing_ok=True)
        partial_workbook.unlink(missing_ok=True)


def ensure_prepared_data() -> str:
    """Ensure app inputs exist; local processed data is always reused.

    Returns 'existing' or 'generated' to aid unit testing and debugging.
    """
    out = prepare.OUT
    if all((out / name).is_file() for name in REQUIRED_OUTPUTS):
        return "existing"

    raw = prepare.RAW_FILE
    downloaded_here = not raw.is_file()
    if downloaded_here:
        _download_workbook(raw)
    try:
        prepare.run()
        missing = [name for name in REQUIRED_OUTPUTS if not (out / name).is_file()]
        if missing:
            raise RuntimeError(f"Preparation ended without required files: {missing}")
        return "generated"
    finally:
        # Keep a manually provided workbook; remove only the automatic download.
        if downloaded_here:
            raw.unlink(missing_ok=True)


if __name__ == "__main__":
    print(ensure_prepared_data())
