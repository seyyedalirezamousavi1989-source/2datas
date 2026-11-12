import json
import tempfile
import unittest
from pathlib import Path

from tools.dataset_normalizer import normalize_record, normalize_file

MAPPING = {k: k for k in (
    "instrument_id venue provider symbol timeframe event_time available_at recorded_at "
    "open high low close price_basis source_artifact_id source_record_id"
).split()}
ROW = {
    "instrument_id": "FX.EURUSD.SPOT", "venue": "DEMO", "provider": "fixture",
    "symbol": "EURUSD", "timeframe": "1m", "event_time": "2026-01-01T00:00:00+02:00",
    "available_at": "2025-12-31T22:00:01Z", "recorded_at": "2025-12-31T22:00:02Z",
    "open": "1.10000", "high": "1.10100", "low": "1.09900", "close": "1.10050",
    "price_basis": "bid", "source_artifact_id": "artifact-demo", "source_record_id": "row-1",
    "volume": "12.500", "volume_unit": "lots",
}

class NormalizerTests(unittest.TestCase):
    def test_decimal_safe_and_utc(self):
        out = normalize_record(ROW, {**MAPPING, "volume": "volume", "volume_unit": "volume_unit"}, source_format="csv")
        self.assertEqual(out["event_time"], "2025-12-31T22:00:00.000000Z")
        self.assertEqual(out["open"], "1.1")
        self.assertEqual(out["volume"], "12.5")
        self.assertEqual(out["source"]["raw_payload"], ROW)

    def test_naive_timestamp_rejected(self):
        row = dict(ROW, event_time="2026-01-01T00:00:00")
        with self.assertRaisesRegex(ValueError, "timezone"):
            normalize_record(row, MAPPING, source_format="csv")

    def test_unknown_timeframe_rejected(self):
        with self.assertRaisesRegex(ValueError, "timeframe"):
            normalize_record(dict(ROW, timeframe="M1"), MAPPING, source_format="csv")

    def test_price_basis_required_and_explicit(self):
        with self.assertRaisesRegex(ValueError, "price_basis"):
            normalize_record(dict(ROW, price_basis=""), MAPPING, source_format="csv")

    def test_ohlc_invalid(self):
        with self.assertRaisesRegex(ValueError, "OHLC"):
            normalize_record(dict(ROW, high="1.09"), MAPPING, source_format="csv")

    def test_non_finite_decimal_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            normalize_record(dict(ROW, close="NaN"), MAPPING, source_format="csv")

    def test_volume_negative_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            normalize_record(dict(ROW, volume="-1"), {**MAPPING, "volume": "volume"}, source_format="csv")

    def test_missing_mapping_rejected(self):
        with self.assertRaisesRegex(ValueError, "mapping missing"):
            normalize_record(ROW, {"open": "open"}, source_format="csv")

    def test_file_conversion_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, mapping, dst = root/"source.jsonl", root/"map.json", root/"canonical.jsonl"
            src.write_text(json.dumps(ROW) + "\n", encoding="utf-8")
            mapping.write_text(json.dumps(MAPPING), encoding="utf-8")
            report = normalize_file(src, mapping, dst)
            self.assertEqual(report["records_written"], 1)
            self.assertTrue(json.loads(dst.read_text(encoding="utf-8"))["source"]["raw_payload"])
            with self.assertRaisesRegex(ValueError, "overwrite"):
                normalize_file(src, mapping, dst)

    def test_duplicate_observation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, mapping, dst = root/"source.jsonl", root/"map.json", root/"canonical.jsonl"
            src.write_text(json.dumps(ROW) + "\n" + json.dumps(dict(ROW, source_record_id="row-2")) + "\n", encoding="utf-8")
            mapping.write_text(json.dumps(MAPPING), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate canonical"):
                normalize_file(src, mapping, dst)

if __name__ == "__main__":
    unittest.main()
