import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from tools.source_reconciliation import reconcile_records, reconcile_files

BASE = {
    "instrument_id": "FX.EURUSD.SPOT", "timeframe": "1m",
    "event_time": "2026-01-01T00:00:00.000000Z", "price_basis": "bid",
    "provider": "feed-a", "venue": "demo-a", "source_artifact_id": "artifact-a",
    "source_record_id": "row-a", "open": "1.1000", "high": "1.1010",
    "low": "1.0990", "close": "1.1005", "available_at": "2026-01-01T00:00:01Z",
    "recorded_at": "2026-01-01T00:00:02Z", "volume": "10", "volume_unit": "lots",
}

def row(provider, close="1.1005", **updates):
    value = dict(BASE, provider=provider, venue="venue-" + provider,
                 source_artifact_id="artifact-" + provider,
                 source_record_id="row-" + provider, close=close)
    value.update(updates)
    return value

class SourceReconciliationTests(unittest.TestCase):
    def test_exact_match(self):
        report = reconcile_records([("a", [row("a")]), ("b", [row("b")])], Decimal("0"))
        self.assertEqual(report["summary"]["all_within_tolerance"], 1)
        self.assertEqual(report["observations"][0]["status"], "all_within_tolerance")

    def test_tolerance_boundary_is_inclusive(self):
        report = reconcile_records([("a", [row("a")]), ("b", [row("b", close="1.1010")])], Decimal("0.0005"))
        self.assertEqual(report["summary"]["all_within_tolerance"], 1)

    def test_divergence(self):
        report = reconcile_records([("a", [row("a")]), ("b", [row("b", close="1.1020")])], Decimal("0.0001"))
        self.assertEqual(report["summary"]["divergent"], 1)
        self.assertEqual(report["observations"][0]["comparisons"][0]["price_status"], "divergent")

    def test_single_source_is_not_consensus(self):
        report = reconcile_records([("a", [row("a")])], Decimal("0"))
        self.assertEqual(report["summary"]["insufficient_sources"], 1)

    def test_duplicate_provider_is_ambiguous(self):
        report = reconcile_records([("a", [row("a"), row("a", close="1.1010")])], Decimal("1"))
        self.assertEqual(report["summary"]["ambiguous_duplicate_source"], 1)

    def test_volume_units_are_never_converted(self):
        report = reconcile_records([
            ("a", [row("a", volume_unit="lots")]),
            ("b", [row("b", volume_unit="contracts")]),
        ], Decimal("0"))
        self.assertEqual(report["observations"][0]["comparisons"][0]["volume_status"], "unit_mismatch_or_missing")

    def test_available_time_delta(self):
        report = reconcile_records([
            ("a", [row("a", available_at="2026-01-01T00:00:01Z")]),
            ("b", [row("b", available_at="2026-01-01T00:00:04Z")]),
        ], Decimal("0"))
        self.assertEqual(report["observations"][0]["comparisons"][0]["available_at_delta_seconds"], "3")

    def test_negative_tolerance_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            reconcile_records([], Decimal("-0.1"))

    def test_report_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, b, out = root/"a.jsonl", root/"b.jsonl", root/"report.json"
            a.write_text(json.dumps(row("a")) + "\n", encoding="utf-8")
            b.write_text(json.dumps(row("b")) + "\n", encoding="utf-8")
            result = reconcile_files([a, b], out, Decimal("0"))
            self.assertEqual(result["all_within_tolerance"], 1)
            with self.assertRaisesRegex(ValueError, "overwrite"):
                reconcile_files([a, b], out, Decimal("0"))

if __name__ == "__main__":
    unittest.main()
