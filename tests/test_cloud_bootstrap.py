from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from scripts import cloud_bootstrap


def test_extracts_only_expected_workbook_from_official_shape(monkeypatch, tmp_path):
    contents = BytesIO()
    with ZipFile(contents, "w") as zf:
        zf.writestr("Online Retail.xlsx", b"fake-workbook-for-extraction-test")
        zf.writestr("other.txt", "unrelated")
    class FakeResponse(BytesIO):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.close()
    monkeypatch.setattr(cloud_bootstrap.urllib.request, "urlopen",
                        lambda *args, **kwargs: FakeResponse(contents.getvalue()))
    expected = tmp_path / "raw" / "Online Retail.xlsx"
    cloud_bootstrap._download_workbook(expected)
    assert expected.read_bytes() == b"fake-workbook-for-extraction-test"
    assert not (expected.parent / ".uci_online_retail_download.zip").exists()


def test_existing_processed_data_never_downloads(monkeypatch, tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    for filename in cloud_bootstrap.REQUIRED_OUTPUTS:
        (processed / filename).write_text("placeholder")
    monkeypatch.setattr(cloud_bootstrap.prepare, "OUT", processed)
    monkeypatch.setattr(cloud_bootstrap, "_download_workbook", lambda *_: 1 / 0)
    assert cloud_bootstrap.ensure_prepared_data() == "existing"


def test_downloaded_workbook_removed_after_processing(monkeypatch, tmp_path):
    raw = tmp_path / "raw" / "Online Retail.xlsx"
    processed = tmp_path / "processed"
    monkeypatch.setattr(cloud_bootstrap.prepare, "RAW_FILE", raw)
    monkeypatch.setattr(cloud_bootstrap.prepare, "OUT", processed)

    def download(file):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b"fake-workbook")

    def prepare_data():
        processed.mkdir(parents=True, exist_ok=True)
        for filename in cloud_bootstrap.REQUIRED_OUTPUTS:
            (processed / filename).write_text("placeholder")

    monkeypatch.setattr(cloud_bootstrap, "_download_workbook", download)
    monkeypatch.setattr(cloud_bootstrap.prepare, "run", prepare_data)
    assert cloud_bootstrap.ensure_prepared_data() == "generated"
    assert not raw.exists()
