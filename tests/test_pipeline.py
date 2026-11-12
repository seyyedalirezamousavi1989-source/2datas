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
    assert audit_file(result)["quality_status"] == "STRUCTURAL_PASS"


def test_bad_ohlc_is_flagged_by_audit():
    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "2000", "1998", "1999", "2001", "120", "0", "12"]
    result = read_mt5_csv(_payload(header, row), "XAUUSD_H1_test.csv")
    assert audit_file(result)["invalid_ohlc_count"] == 1
    assert audit_file(result)["quality_status"] == "STRUCTURAL_FAIL"


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
        archive.writestr("XAUUSD_H1_test.csv", (chr(9).join(header) + chr(10) + chr(9).join(row) + chr(10)).encode())
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


def test_timeframe_alignment_detects_exact_child_parent_aggregation():
    from twodatas.ingest import read_mt5_csv
    from twodatas.alignment import audit_timeframe_alignment

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    child_rows = [
        ["2024.01.01", "10:00:00", "2000", "2001", "1999", "2000.5", "10", "0", "10"],
        ["2024.01.01", "10:05:00", "2000.5", "2002", "2000", "2001.5", "12", "0", "10"],
        ["2024.01.01", "10:10:00", "2001.5", "2003", "2001", "2002.5", "13", "0", "10"],
    ]
    child_payload = (chr(10).join([chr(9).join(header)] + [chr(9).join(row) for row in child_rows]) + chr(10)).encode()
    parent_row = ["2024.01.01", "10:00:00", "2000", "2003", "1999", "2002.5", "35", "0", "10"]
    parent_payload = (chr(9).join(header) + chr(10) + chr(9).join(parent_row) + chr(10)).encode()
    child = read_mt5_csv(child_payload, "XAUUSD_M5_test.csv")
    parent = read_mt5_csv(parent_payload, "XAUUSD_M15_test.csv")
    comparison = audit_timeframe_alignment([child, parent])["comparisons"][0]
    assert comparison["complete_child_groups"] == 1
    assert comparison["exact_ohlc_and_tick_volume_matches"] == 1


def test_generic_symbol_and_timeframe_are_inferred():
    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "1.1", "1.2", "1.0", "1.15", "20", "0", "2"]
    result = read_mt5_csv(_payload(header, row), "EURUSD_M1_test.csv")
    assert result.rows[0].instrument == "EURUSD"
    assert result.timeframe == "M1"


def test_alpari_candidate_does_not_silently_resolve_timezone():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile("alpari_mt5_candidate")
    utc_value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert utc_value is None
    assert status == "UNRESOLVED_SOURCE_TIME"


def test_user_configured_timezone_resolves_and_dst_ambiguity_is_quarantined():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile(broker_name="ExampleBroker", server_timezone="America/New_York",
                              bar_timestamp_convention="interval_start")
    utc_value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert utc_value == "2024-01-15T15:00:00+00:00"
    assert status == "RESOLVED_INTERVAL_START"
    ambiguous, ambiguous_status = to_utc("2024.11.03 01:30:00", "second", profile)
    assert ambiguous is None
    assert ambiguous_status == "AMBIGUOUS_LOCAL_TIME"


def test_price_action_fvg_and_confirmed_swing_are_causal():
    from twodatas.price_action import compute_price_action_features

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    rows = [
        ["2024.01.01", "10:00:00", "10.0", "10.5", "9.8", "10.2", "10", "0", "1"],
        ["2024.01.01", "10:01:00", "10.3", "11.2", "10.2", "11.0", "11", "0", "1"],
        ["2024.01.01", "10:02:00", "12.0", "13.0", "11.5", "12.5", "12", "0", "1"],
        ["2024.01.01", "10:03:00", "12.4", "12.6", "11.8", "12.0", "13", "0", "1"],
        ["2024.01.01", "10:04:00", "11.9", "12.0", "10.8", "11.0", "14", "0", "1"],
    ]
    payload = (chr(10).join([chr(9).join(header)] + [chr(9).join(row) for row in rows]) + chr(10)).encode()
    source = read_mt5_csv(payload, "XAUUSD_M1_test.csv")
    events = compute_price_action_features(source.rows, pivot_left=1, pivot_right=1, atr_period=2)
    assert events[2]["swing_high_confirmed"] is False
    assert events[3]["swing_high_confirmed"] is True
    assert events[2]["fvg"]["type"] == "BULLISH_FVG"
    assert events[3]["swing_high_origin_index"] == 2
