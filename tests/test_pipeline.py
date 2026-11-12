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
