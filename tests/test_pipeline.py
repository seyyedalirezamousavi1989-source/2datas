from twodatas.ingest import read_mt5_csv
from twodatas.quality import audit_file


def _payload(header, row):
    sep = chr(9)
    return (sep.join(header) + chr(10) + sep.join(row) + chr(10)).encode()


def test_mt5_tab_export_is_read_and_timezone_not_guessed():
    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    result = read_mt5_csv(_payload(header, row), "XAUUSD_H1_test.csv")
    assert result.timeframe == "H1"
    assert result.rows[0].source_timestamp == "2024.01.01 10:00:00"
    assert result.rows[0].timestamp_timezone == "UNKNOWN"
    assert audit_file(result)["quality_status"] == "PASS"


def test_bad_ohlc_is_flagged_by_audit():
    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "2000", "1998", "1999", "2001", "120", "0", "12"]
    result = read_mt5_csv(_payload(header, row), "XAUUSD_H1_test.csv")
    assert audit_file(result)["invalid_ohlc_count"] == 1
    assert audit_file(result)["quality_status"] == "REVIEW_REQUIRED"


def test_daily_export_without_time_column():
    header = ["<DATE>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "2000", "2002", "1999", "2001", "120", "0", "12"]
    result = read_mt5_csv(_payload(header, row), "XAUUSD_Daily_test.csv")
    assert result.timeframe == "D1"
    assert result.rows[0].timestamp_precision == "day"


def test_normalizer_writes_partition_and_lineage(tmp_path):
    import csv
    import gzip
    import json
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("XAUUSD_H1_test.csv", (chr(9).join(header) + "\n" + chr(9).join(row) + "\n").encode())
    manifest = normalize_archive(str(source), str(tmp_path / "out"))
    assert manifest["total_rows"] == 1
    partition = tmp_path / "out" / "instrument=XAUUSD" / "timeframe=H1" / "bars.csv.gz"
    with gzip.open(partition, "rt", encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert records[0]["source_row_number"] == "2"
    assert records[0]["source_timestamp"] == "2024.01.01 10:00:00"
    assert records[0]["timestamp_timezone"] == "UNKNOWN"
    saved = json.loads((tmp_path / "out" / "manifest.json").read_text())
    assert saved["partitions"][0]["source_sha256"]
