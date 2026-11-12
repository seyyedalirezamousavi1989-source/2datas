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
    partitions = list((tmp_path / "out" / "instrument=XAUUSD" / "timeframe=H1").glob("bars-*.csv.gz"))
    assert len(partitions) == 1
    partition = partitions[0]
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
    assert audit_file(result)["quality_status"] == "STRUCTURAL_PASS"


def test_alpari_candidate_does_not_silently_resolve_timezone():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile("alpari_mt5_candidate")
    utc_value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert utc_value is None
    assert status == "BROKER_PROFILE_NOT_VERIFIED"


def test_user_configured_timezone_resolves_and_dst_ambiguity_is_quarantined():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile(broker_name="ExampleBroker", server_name="Example-MT5", server_timezone="America/New_York",
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
    assert len(events) == len(source.rows) - 1  # newest potentially incomplete bar is excluded
    assert events[2]["swing_high_confirmed"] is False
    assert events[3]["swing_high_confirmed"] is True
    assert events[2]["fvg"]["type"] == "BULLISH_FVG"
    assert events[3]["swing_high_origin_index"] == 2
    assert events[0]["source_row_number"] == 2
    assert events[0]["source_sha256"] == source.source_sha256
    assert events[0]["feature_parameters"]["pivot_right"] == 1
    from twodatas.broker_profiles import resolve_profile
    profile = resolve_profile(server_timezone="America/New_York", bar_timestamp_convention="interval_start")
    timed = compute_price_action_features(source.rows, pivot_left=1, pivot_right=1, atr_period=2, broker_profile=profile)
    assert timed[0]["available_at_utc"] == "2024-01-01T15:01:00+00:00"
    assert timed[0]["availability_time_status"] == "RESOLVED_AT_INTERVAL_CLOSE"


def test_normalizer_records_configured_broker_time_contract(tmp_path):
    import csv
    import gzip
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.15", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("GOLD_M5_test.csv", (chr(9).join(header) + chr(10) + chr(9).join(row) + chr(10)).encode())
    manifest = normalize_archive(
        str(source), str(tmp_path / "normalized"),
        broker_name="ExampleBroker", server_name="Example-MT5", server_timezone="America/New_York",
        bar_timestamp_convention="interval_start",
    )
    partition = next((tmp_path / "normalized" / "instrument=GOLD" / "timeframe=M5").glob("bars-*.csv.gz"))
    with gzip.open(partition, "rt", encoding="utf-8", newline="") as handle:
        record = next(csv.DictReader(handle))
    assert record["timestamp_utc"] == "2024-01-15T15:00:00+00:00"
    assert record["timestamp_resolution_status"] == "RESOLVED_INTERVAL_START"
    assert record["server_name"] == "Example-MT5"
    assert manifest["broker_profile"]["server_name"] == "Example-MT5"
    assert manifest["broker_profile"]["status"] == "user_configured"


def test_fixed_offset_server_clock_is_supported_when_explicit():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile(
        broker_name="FixedOffsetBroker", server_name="MT5-Server",
        server_timezone="UTC+02:00", bar_timestamp_convention="interval_start",
    )
    utc_value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert utc_value == "2024-01-15T08:00:00+00:00"
    assert status == "RESOLVED_INTERVAL_START"


def test_alpari_profile_is_not_verified_from_account_or_server_name_alone():
    from twodatas.broker_profiles import resolve_profile, to_utc

    profile = resolve_profile("alpari_mt5_candidate", server_name="Any-Alpari-Server")
    assert profile.status == "candidate_unverified"
    winter, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert winter is None
    assert status == "BROKER_PROFILE_NOT_VERIFIED"


def test_broker_sidecar_does_not_require_account_or_server_identity(tmp_path):
    import json
    from twodatas.broker_profiles import resolve_profile_for_archive, to_utc

    archive = tmp_path / "generic_export.zip"
    archive.write_bytes(b"placeholder")
    (tmp_path / "generic_export.zip.broker.json").write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "server_timezone": "Europe/Helsinki",
        "bar_timestamp_convention": "interval_start",
    }))
    profile, _ = resolve_profile_for_archive(str(archive))
    assert profile.status == "user_configured"
    assert profile.server_name is None
    value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert value == "2024-01-15T08:00:00+00:00"
    assert status == "RESOLVED_INTERVAL_START"


def test_broker_sidecar_is_auto_discovered_and_hashed(tmp_path):
    import json
    from twodatas.broker_profiles import resolve_profile_for_archive, to_utc

    archive = tmp_path / "broker_export.zip"
    archive.write_bytes(b"placeholder")
    sidecar = tmp_path / "broker_export.zip.broker.json"
    sidecar.write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "broker_name": "Example Broker",
        "server_name": "Example-Live-02",
        "server_timezone": "America/New_York",
        "bar_timestamp_convention": "interval_start",
    }))
    profile, source = resolve_profile_for_archive(str(archive))
    assert profile.status == "user_configured"
    assert profile.server_name == "Example-Live-02"
    assert source["mode"] == "sidecar"
    assert source["sha256"]
    utc_value, status = to_utc("2024.01.15 10:00:00", "second", profile)
    assert utc_value == "2024-01-15T15:00:00+00:00"
    assert status == "RESOLVED_INTERVAL_START"


def test_broker_sidecar_conflicts_are_rejected(tmp_path):
    import json
    import pytest
    from twodatas.broker_profiles import resolve_profile_for_archive

    archive = tmp_path / "source.zip"
    archive.write_bytes(b"placeholder")
    (tmp_path / "source.zip.broker.json").write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "server_name": "Server-A",
        "server_timezone": "UTC+02:00",
        "bar_timestamp_convention": "interval_start",
    }))
    with pytest.raises(ValueError, match="Do not mix"):
        resolve_profile_for_archive(str(archive), server_name="Server-B")


def test_fvg_zone_tracks_partial_fill_and_invalidation_without_lookahead():
    from twodatas.ingest import read_mt5_csv
    from twodatas.price_action import compute_price_action_features

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    rows = [
        ["2024.01.01", "10:00:00", "10.0", "10.5", "9.8", "10.2", "10", "0", "1"],
        ["2024.01.01", "10:01:00", "10.2", "10.8", "10.1", "10.6", "11", "0", "1"],
        ["2024.01.01", "10:02:00", "11.8", "12.5", "11.5", "12.2", "12", "0", "1"],
        ["2024.01.01", "10:03:00", "12.2", "12.4", "11.8", "12.0", "13", "0", "1"],
        ["2024.01.01", "10:04:00", "11.4", "11.8", "11.0", "11.2", "14", "0", "1"],
        ["2024.01.01", "10:05:00", "10.8", "11.0", "10.2", "10.3", "15", "0", "1"],
        ["2024.01.01", "10:06:00", "10.3", "10.6", "10.1", "10.4", "16", "0", "1"],
    ]
    payload = (chr(10).join([chr(9).join(header)] + [chr(9).join(row) for row in rows]) + chr(10)).encode()
    source = read_mt5_csv(payload, "XAUUSD_M1_lifecycle.csv")
    events = compute_price_action_features(source.rows, atr_period=2)
    created = events[2]["fvg"]
    assert created["status"] == "ACTIVE"
    assert events[4]["fvg_zone_updates"][0]["status"] == "PARTIALLY_FILLED"
    assert events[4]["fvg_zone_updates"][0]["fill_fraction"] > 0
    assert events[5]["fvg_zone_updates"][0]["status"] == "INVALIDATED"
    assert events[5]["fvg_zone_updates"][0]["invalidated"] is True


def test_order_block_candidate_tracks_mitigation_and_invalidation():
    from twodatas.ingest import read_mt5_csv
    from twodatas.price_action import compute_price_action_features

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    rows = [
        ["2024.01.01", "10:00:00", "10.0", "10.8", "9.8", "10.4", "10", "0", "1"],
        ["2024.01.01", "10:01:00", "10.4", "11.2", "10.2", "11.0", "11", "0", "1"],
        ["2024.01.01", "10:02:00", "11.0", "13.5", "10.9", "13.0", "12", "0", "1"],
        ["2024.01.01", "10:03:00", "13.0", "13.1", "11.9", "12.2", "13", "0", "1"],
        ["2024.01.01", "10:04:00", "13.0", "14.2", "12.8", "14.0", "14", "0", "1"],
        ["2024.01.01", "10:05:00", "12.5", "12.8", "12.0", "12.6", "15", "0", "1"],
        ["2024.01.01", "10:06:00", "11.8", "12.0", "11.5", "11.7", "16", "0", "1"],
        ["2024.01.01", "10:07:00", "11.7", "11.9", "11.4", "11.6", "17", "0", "1"],
    ]
    payload = (chr(10).join([chr(9).join(header)] + [chr(9).join(row) for row in rows]) + chr(10)).encode()
    source = read_mt5_csv(payload, "XAUUSD_M1_ob.csv")
    events = compute_price_action_features(source.rows, pivot_left=1, pivot_right=1, atr_period=2)
    candidate = events[4]["order_block_candidate"]
    assert candidate["type"] == "BULLISH_ORDER_BLOCK_CANDIDATE"
    assert events[5]["order_block_updates"][0]["status"] == "MITIGATED"
    assert events[6]["order_block_updates"][0]["status"] == "INVALIDATED"


def test_mtf_snapshots_never_select_future_higher_timeframe_events():
    from twodatas.multi_timeframe import build_mtf_snapshots

    events = {
        "XAUUSD": {
            "M1": [
                {"instrument": "XAUUSD", "timeframe": "M1", "event_index": 0, "available_at_utc": "2024-01-01T10:01:00+00:00", "source_timestamp": "2024.01.01 10:00:00", "close": 2001.0},
                {"instrument": "XAUUSD", "timeframe": "M1", "event_index": 1, "available_at_utc": "2024-01-01T10:02:00+00:00", "source_timestamp": "2024.01.01 10:01:00", "close": 2002.0},
            ],
            "H1": [
                {"instrument": "XAUUSD", "timeframe": "H1", "event_index": 0, "available_at_utc": "2024-01-01T10:00:00+00:00", "source_timestamp": "2024.01.01 09:00:00", "structure_direction": "BULLISH"},
                {"instrument": "XAUUSD", "timeframe": "H1", "event_index": 1, "available_at_utc": "2024-01-01T11:00:00+00:00", "source_timestamp": "2024.01.01 10:00:00", "structure_direction": "BEARISH"},
            ],
        }
    }
    snapshots, stats = build_mtf_snapshots(events, decision_timeframes=["M1"])
    rows = snapshots["XAUUSD_M1"]
    assert rows[0]["context_by_timeframe"]["H1"]["features"]["structure_direction"] == "BULLISH"
    assert rows[1]["context_by_timeframe"]["H1"]["features"]["structure_direction"] == "BULLISH"
    assert rows[1]["context_by_timeframe"]["H1"]["available_at_utc"] == "2024-01-01T10:00:00+00:00"
    assert stats["snapshots_written"] == 2


def test_mtf_snapshots_exclude_unresolved_decision_events():
    from twodatas.multi_timeframe import build_mtf_snapshots

    events = {"GOLD": {"M5": [
        {"instrument": "GOLD", "timeframe": "M5", "event_index": 0, "available_at_utc": None},
        {"instrument": "GOLD", "timeframe": "M5", "event_index": 1, "available_at_utc": "2024-01-01T10:05:00+00:00"},
    ]}}
    snapshots, stats = build_mtf_snapshots(events, decision_timeframes=["M5"])
    assert len(snapshots["GOLD_M5"]) == 1
    assert stats["unresolved_decision_events"] == 1


def test_mtf_loader_verifies_feature_partition_checksum_and_lineage(tmp_path):
    import hashlib
    import json
    from twodatas.multi_timeframe import load_feature_events

    source_hash = "a" * 64
    event = {
        "feature_version": "price-action-0.3.0",
        "instrument": "XAUUSD",
        "timeframe": "M5",
        "event_index": 0,
        "source_sha256": source_hash,
        "available_at_utc": "2024-01-01T10:05:00+00:00",
    }
    partition = tmp_path / "XAUUSD_M5.jsonl"
    partition.write_text(json.dumps(event) + chr(10), encoding="utf-8")
    manifest = {
        "feature_version": "price-action-0.3.0",
        "partitions": [{
            "instrument": "XAUUSD", "timeframe": "M5",
            "source_sha256": source_hash, "events": 1,
            "output_path": str(partition),
            "output_sha256": hashlib.sha256(partition.read_bytes()).hexdigest(),
        }],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    loaded, _ = load_feature_events(str(tmp_path))
    assert len(loaded["XAUUSD"]["M5"]) == 1
    partition.write_text(partition.read_text() + chr(10), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_feature_events(str(tmp_path))


def test_broker_neutral_csv_delimiters_and_header_aliases():
    from twodatas.ingest import read_mt5_csv

    comma = (
        "date,time,open,high,low,close,tick_volume,real_volume,spread_points\n"
        "2024-01-01,10:05,2000,2002,1999,2001,120,0,12\n"
    ).encode()
    result = read_mt5_csv(comma, "GOLD_M5_export.csv")
    assert result.rows[0].source_timestamp == "2024.01.01 10:05:00"
    assert result.rows[0].tick_volume == 120
    assert result.rows[0].spread_points == 12

    semicolon = (
        "DATE;TIME;OPEN;HIGH;LOW;CLOSE;TICKVOL;VOL;SPREAD\n"
        "2024.01.01;10:05:00;2000;2002;1999;2001;120;0;12\n"
    ).encode()
    second = read_mt5_csv(semicolon, "XAUUSD_M5_export.csv")
    assert second.rows[0].close == 2001


def test_market_csv_does_not_guess_tick_volume_from_generic_volume():
    import pytest
    from twodatas.ingest import read_mt5_csv

    payload = (
        "date,time,open,high,low,close,volume,spread\n"
        "2024-01-01,10:05,2000,2002,1999,2001,120,12\n"
    ).encode()
    with pytest.raises(ValueError, match="TICKVOL"):
        read_mt5_csv(payload, "XAUUSD_M5_export.csv")


def test_broker_sidecar_symbol_alias_maps_gold_to_canonical_xauusd(tmp_path):
    import json
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.15", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    source = tmp_path / "gold_export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("GOLD_M5_test.csv", (chr(9).join(header) + chr(10) + chr(9).join(row) + chr(10)).encode())
    (tmp_path / "gold_export.zip.broker.json").write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "server_timezone": "Europe/Helsinki",
        "bar_timestamp_convention": "interval_start",
        "symbol_aliases": {"GOLD": "XAUUSD"},
        "instrument_specs": {"GOLD": {"canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01", "tick_size": "0.01", "contract_size": "100", "price_currency": "USD", "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count", "effective_from": "2024-01-01", "evidence": "Test fixture only; not broker facts."}},
    }))
    manifest = normalize_archive(str(source), str(tmp_path / "normalized"))
    assert manifest["instruments"] == ["XAUUSD"]
    assert manifest["instrument_specification_audit"]["status"] == "COMPLETE_FOR_OBSERVED_PERIODS"
    partition = next((tmp_path / "normalized" / "instrument=XAUUSD" / "timeframe=M5").glob("bars-*.csv.gz"))
    assert partition.is_file()
    import csv
    import gzip
    with gzip.open(partition, "rt", encoding="utf-8", newline="") as handle:
        record = next(csv.DictReader(handle))
    assert record["instrument"] == "XAUUSD"
    assert record["source_instrument"] == "GOLD"


def test_normalizer_never_overwrites_same_symbol_timeframe_source_files(tmp_path):
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    first = ["2024.01.01", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    second = ["2024.01.01", "10:05:00", "2001", "2003", "2000", "2002", "130", "0", "12"]
    source = tmp_path / "two_exports.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("XAUUSD_M5_part_a.csv", (chr(9).join(header) + chr(10) + chr(9).join(first) + chr(10)).encode())
        archive.writestr("XAUUSD_M5_part_b.csv", (chr(9).join(header) + chr(10) + chr(9).join(second) + chr(10)).encode())

    output = tmp_path / "normalized"
    manifest = normalize_archive(str(source), str(output))
    partition_dir = output / "instrument=XAUUSD" / "timeframe=M5"
    files = sorted(partition_dir.glob("bars-*.csv.gz"))
    assert len(files) == 2
    assert len(manifest["partitions"]) == 2
    assert {item["source_file"] for item in manifest["partitions"]} == {
        "XAUUSD_M5_part_a.csv", "XAUUSD_M5_part_b.csv"
    }
    assert sum(item["row_count"] for item in manifest["partitions"]) == 2


def test_instrument_spec_registry_validates_units_and_effective_dates():
    from twodatas.instrument_specs import validate_instrument_specs, audit_instrument_specs

    specs = validate_instrument_specs({
        "GOLD": {
            "canonical_instrument": "XAUUSD",
            "digits": 2,
            "point_size": "0.01",
            "tick_size": "0.01",
            "contract_size": "100",
            "price_currency": "USD",
            "profit_currency": "USD",
            "spread_unit": "points",
            "volume_semantics": "tick_count",
            "effective_from": "2024-01-01",
            "evidence": "Verified broker symbol specification document, revision 2024-01.",
        }
    })
    report = audit_instrument_specs(specs, source_symbols={"GOLD", "XAUUSD"})
    assert specs["GOLD"].canonical_instrument == "XAUUSD"
    assert report["status"] == "INCOMPLETE"
    assert report["missing_source_symbols"] == ["XAUUSD"]


def test_instrument_spec_registry_rejects_invalid_point_size_and_dates():
    import pytest
    from twodatas.instrument_specs import validate_instrument_spec

    raw = {
        "canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0",
        "tick_size": "0.01", "contract_size": "100", "price_currency": "USD",
        "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count",
        "effective_from": "2024-01-01", "effective_to": "2023-01-01", "evidence": "test",
    }
    with pytest.raises(ValueError):
        validate_instrument_spec("GOLD", raw)


def test_normalizer_manifest_reports_unconfigured_instrument_spec_registry(tmp_path):
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    row = ["2024.01.01", "10:00:00", "2000", "2002", "1999", "2001", "120", "0", "12"]
    source = tmp_path / "source.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("GOLD_M5_test.csv", (chr(9).join(header) + chr(10) + chr(9).join(row) + chr(10)).encode())
    manifest = normalize_archive(str(source), str(tmp_path / "normalized"))
    assert manifest["instrument_specification_audit"]["status"] == "NOT_CONFIGURED"
    assert manifest["instrument_specification_audit"]["missing_source_symbols"] == ["GOLD"]


def test_instrument_spec_history_rejects_overlapping_effective_periods():
    import pytest
    from twodatas.instrument_specs import validate_instrument_specs

    base = {
        "canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01",
        "tick_size": "0.01", "contract_size": "100", "price_currency": "USD",
        "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count",
        "evidence": "Test fixture only.",
    }
    with pytest.raises(ValueError, match="overlapping"):
        validate_instrument_specs({"GOLD": [
            {**base, "effective_from": "2020-01-01", "effective_to": "2024-01-01"},
            {**base, "effective_from": "2023-12-01"},
        ]})


def test_instrument_spec_history_detects_uncovered_observation_dates():
    from twodatas.instrument_specs import validate_instrument_specs, audit_instrument_specs

    base = {
        "canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01",
        "tick_size": "0.01", "contract_size": "100", "price_currency": "USD",
        "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count",
        "evidence": "Test fixture only.",
    }
    specs = validate_instrument_specs({"GOLD": [
        {**base, "effective_from": "2020-01-01", "effective_to": "2023-01-01"},
        {**base, "effective_from": "2024-01-01"},
    ]})
    report = audit_instrument_specs(
        specs, source_symbols={"GOLD"},
        observed_periods={"GOLD": ("2022-12-01", "2024-02-01")},
    )
    assert report["status"] == "INCOMPLETE"
    assert report["uncovered_observed_periods"][0]["uncovered_from"] == "2023-01-01"


def test_broker_sidecar_rejects_conflicting_symbol_alias_and_contract_identity(tmp_path):
    import json
    import pytest
    from twodatas.broker_profiles import resolve_profile_for_archive

    archive = tmp_path / "source.zip"
    archive.write_bytes(b"placeholder")
    sidecar = tmp_path / "source.zip.broker.json"
    sidecar.write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "server_timezone": "UTC+00:00",
        "bar_timestamp_convention": "interval_start",
        "symbol_aliases": {"GOLD": "XAUUSD"},
        "instrument_specs": {"GOLD": {
            "canonical_instrument": "GOLD",
            "digits": 2, "point_size": "0.01", "tick_size": "0.01",
            "contract_size": "100", "price_currency": "USD", "profit_currency": "USD",
            "spread_unit": "points", "volume_semantics": "tick_count",
            "effective_from": "2020-01-01", "evidence": "Test fixture only.",
        }},
    }))
    with pytest.raises(ValueError, match="must match its explicit symbol alias"):
        resolve_profile_for_archive(str(archive))


def test_point_in_time_instrument_spec_resolution_uses_inclusive_start_exclusive_end():
    from twodatas.instrument_specs import validate_instrument_specs, resolve_instrument_spec

    base = {
        "canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01",
        "tick_size": "0.01", "contract_size": "100", "price_currency": "USD",
        "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count",
        "evidence": "Test fixture only.",
    }
    specs = validate_instrument_specs({"GOLD": [
        {**base, "effective_from": "2020-01-01", "effective_to": "2024-01-01", "contract_size": "100"},
        {**base, "effective_from": "2024-01-01", "contract_size": "10"},
    ]})
    old, old_status, _ = resolve_instrument_spec(specs, "GOLD", "2023.12.31 23:59:00")
    new, new_status, _ = resolve_instrument_spec(specs, "GOLD", "2024.01.01 00:00:00")
    missing, missing_status, _ = resolve_instrument_spec(specs, "GOLD", "2019.12.31 23:59:00")
    assert old_status == new_status == "SPEC_MATCHED"
    assert old.contract_size == "100"
    assert new.contract_size == "10"
    assert missing is None
    assert missing_status == "NO_EFFECTIVE_SPEC_FOR_DATE"


def test_spread_conversion_uses_verified_units_and_never_guesses():
    from twodatas.instrument_specs import validate_instrument_specs, spec_values_for_bar

    base = {
        "canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01",
        "tick_size": "0.01", "contract_size": "100", "price_currency": "USD",
        "profit_currency": "USD", "volume_semantics": "tick_count",
        "effective_from": "2024-01-01", "evidence": "Test fixture only.",
    }
    points = validate_instrument_specs({"GOLD": {**base, "spread_unit": "points"}})
    price = validate_instrument_specs({"GOLD": {**base, "spread_unit": "price"}})
    unknown = validate_instrument_specs({"GOLD": {**base, "spread_unit": "unknown"}})
    point_result = spec_values_for_bar(points, "GOLD", "2024.01.01 10:00:00", 12)
    price_result = spec_values_for_bar(price, "GOLD", "2024.01.01 10:00:00", 0.12)
    unknown_result = spec_values_for_bar(unknown, "GOLD", "2024.01.01 10:00:00", 12)
    no_spec_result = spec_values_for_bar({}, "GOLD", "2024.01.01 10:00:00", 12)
    assert point_result["spread_points"] == "12"
    assert point_result["spread_price"] == "0.12"
    assert price_result["spread_points"] == ""
    assert price_result["spread_price"] == "0.12"
    assert unknown_result["spread_points"] == unknown_result["spread_price"] == ""
    assert no_spec_result["instrument_spec_status"] == "SPEC_NOT_CONFIGURED"
    assert no_spec_result["spread_raw"] == "12"
    assert no_spec_result["spread_price"] == ""


def test_normalizer_attaches_effective_contract_and_converts_spread_per_bar(tmp_path):
    import csv
    import gzip
    import json
    import zipfile
    from twodatas.normalize import normalize_archive

    header = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"]
    rows = [
        ["2023.12.31", "23:59:00", "2000", "2002", "1999", "2001", "120", "0", "12"],
        ["2024.01.01", "00:00:00", "2001", "2003", "2000", "2002", "130", "0", "12"],
    ]
    source = tmp_path / "effective_specs.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("GOLD_M1_test.csv", (chr(9).join(header) + chr(10) + chr(10).join(chr(9).join(row) for row in rows) + chr(10)).encode())
    (tmp_path / "effective_specs.zip.broker.json").write_text(json.dumps({
        "schema_version": "2datas-broker-clock-1",
        "server_timezone": "UTC+00:00",
        "bar_timestamp_convention": "interval_start",
        "symbol_aliases": {"GOLD": "XAUUSD"},
        "instrument_specs": {"GOLD": [
            {"canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01", "tick_size": "0.01", "contract_size": "100", "price_currency": "USD", "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count", "effective_from": "2020-01-01", "effective_to": "2024-01-01", "evidence": "Historical test fixture."},
            {"canonical_instrument": "XAUUSD", "digits": 2, "point_size": "0.01", "tick_size": "0.01", "contract_size": "10", "price_currency": "USD", "profit_currency": "USD", "spread_unit": "points", "volume_semantics": "tick_count", "effective_from": "2024-01-01", "evidence": "Current test fixture."},
        ]},
    }))
    output = tmp_path / "normalized"
    manifest = normalize_archive(str(source), str(output))
    partition = next((output / "instrument=XAUUSD" / "timeframe=M1").glob("bars-*.csv.gz"))
    with gzip.open(partition, "rt", encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert [row["contract_size"] for row in records] == ["100", "10"]
    assert [row["instrument_spec_status"] for row in records] == ["SPEC_MATCHED", "SPEC_MATCHED"]
    assert [row["spread_points"] for row in records] == ["12.0", "12.0"]
    assert [row["spread_price"] for row in records] == ["0.12", "0.12"]
    assert records[0]["instrument_spec_id"] != records[1]["instrument_spec_id"]
    assert manifest["schema_version"] == "market-bars-0.4.0"
