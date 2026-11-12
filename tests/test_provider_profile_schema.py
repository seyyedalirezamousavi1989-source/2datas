import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/ingestion/provider-profile.schema.json").read_text(encoding="utf-8"))


def profile():
    return {
        "schema_version": "1.0.0",
        "profile_id": "fixture.mt5.alpari.xauusd",
        "profile_version": 1,
        "provider_id": "fixture.provider",
        "feed_id": "fixture.mt5-server",
        "adapter_kind": "mt5_terminal",
        "instrument_mappings": [{
            "instrument_id": "METAL.XAUUSD.SPOT",
            "provider_symbol": "XAUUSD.a",
            "asset_class": "metal",
            "contract_specification_ref": None
        }],
        "timeframes": {
            "supported": ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1mo"],
            "native_only": True,
            "aggregation_allowed": False
        },
        "timestamp": {
            "source_timezone": "Europe/Helsinki",
            "timezone_kind": "iana",
            "timestamp_field_semantics": "bar_open",
            "ambiguous_dst_policy": "reject",
            "nonexistent_dst_policy": "reject",
            "precision": "second"
        },
        "bar_semantics": {
            "boundary": "left_closed_right_open",
            "session_calendar_ref": None,
            "partial_bar_policy": "preserve_flag",
            "correction_policy": "unknown"
        },
        "price_semantics": {
            "price_basis": "unknown",
            "quote_currency": "USD",
            "price_scale_policy": "provider_native"
        },
        "field_mapping": {
            "timestamp": "<DATE> <TIME>",
            "open": "<OPEN>",
            "high": "<HIGH>",
            "low": "<LOW>",
            "close": "<CLOSE>"
        },
        "volume_semantics": {"meaning": "tick_count", "unit": "ticks"},
        "spread_semantics": {"meaning": "points", "unit": "provider_points"},
        "capabilities": ["historical_ohlcv"],
        "limitations": ["Fixture only; not evidence of a real provider profile."],
        "evidence_refs": []
    }


class ProviderProfileSchemaTests(unittest.TestCase):
    def test_valid_profile_accepts_arbitrary_declared_timeframes(self):
        jsonschema.Draft202012Validator.check_schema(SCHEMA)
        jsonschema.validate(profile(), SCHEMA)

    def test_unknown_timezone_is_representable_but_not_implicitly_resolved(self):
        item = profile()
        item["timestamp"]["source_timezone"] = "unknown"
        item["timestamp"]["timezone_kind"] = "unknown"
        jsonschema.validate(item, SCHEMA)

    def test_invalid_dst_policy_is_rejected(self):
        item = profile()
        item["timestamp"]["nonexistent_dst_policy"] = "guess"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(item, SCHEMA)

    def test_unsupported_timeframe_syntax_is_rejected(self):
        item = profile()
        item["timeframes"]["supported"].append("H4")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(item, SCHEMA)

    def test_unregistered_fields_are_rejected(self):
        item = profile()
        item["silent_timezone_guess"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(item, SCHEMA)


if __name__ == "__main__":
    unittest.main()
