import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "training" / "sft-record.schema.json"
DATASET_PATHS = [
    ROOT / "dataset" / "seed" / "identity.jsonl",
    ROOT / "dataset" / "seed" / "forex_knowledge.jsonl",
    ROOT / "dataset" / "seed" / "strategy_selection.jsonl",
    ROOT / "dataset" / "seed" / "advanced_market_reasoning.jsonl",
]


class SeedDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_all_jsonl_records_match_schema_and_have_unique_ids(self):
        seen = set()
        total = 0
        for path in DATASET_PATHS:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    errors = sorted(self.validator.iter_errors(record), key=lambda e: list(e.path))
                    self.assertEqual([], [e.message for e in errors], f"{path}:{line_number}")
                    self.assertNotIn(record["id"], seen)
                    seen.add(record["id"])
                    total += 1
        self.assertGreaterEqual(total, 80)

    def test_identity_facts_are_consistent(self):
        records = []
        for path in DATASET_PATHS:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        identity_text = "\n".join(
            message["content"]
            for record in records if record["metadata"]["domain"] == "identity"
            for message in record["messages"]
        )
        for expected in [
            "AURORA QUANT", "LocalChat", "Qwen3.5:4B",
            "Alireza Mousavi", "AURORA AI Research Group"
        ]:
            self.assertIn(expected, identity_text)
        self.assertIn("سید علیرضا موسوی", identity_text)

    def test_seed_records_do_not_claim_market_data(self):
        for path in DATASET_PATHS:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                self.assertIs(record["metadata"]["contains_market_data"], False)
                self.assertEqual("initial_curated", record["metadata"]["review_status"])

    def test_required_learning_domains_are_present(self):
        domains = set()
        for path in DATASET_PATHS:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    domains.add(json.loads(line)["metadata"]["domain"])
        for required in [
            "identity", "forex_fundamentals", "technical_analysis",
            "multi_timeframe", "strategy_research", "quantitative_analysis",
            "risk_management", "fundamental_analysis", "analytical_reasoning",
            "trade_review", "forex_data_access", "adaptive_strategy_selection"
        ]:
            self.assertIn(required, domains)

    def test_strategy_selection_corpus_is_broker_and_timeframe_agnostic(self):
        path = ROOT / "dataset" / "seed" / "strategy_selection.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(records), 20)
        text = "\n".join(message["content"] for record in records for message in record["messages"]).lower()
        self.assertIn("without assuming a broker", text)
        self.assertIn("no trade", text)
        self.assertIn("trend-following", text)
        self.assertIn("mean-reversion", text)
        self.assertIn("multi-timeframe", text)


    def test_advanced_reasoning_corpus_has_breadth_and_complete_answers(self):
        path = ROOT / "dataset" / "seed" / "advanced_market_reasoning.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(records), 30)
        tasks = {record["metadata"]["task"] for record in records}
        for required in [
            "regime-001", "breakout-001", "mtf-001", "structure-001",
            "risk-001", "no-trade-001", "forecast-001", "data-001",
            "posttrade-001", "overfit-001", "probability-001"
        ]:
            self.assertIn(required, tasks)
        for record in records:
            self.assertGreater(len(record["messages"][2]["content"]), 180)
            self.assertTrue(record["metadata"]["split_group"].startswith("advanced_reasoning_"))

    def test_forex_tab_access_contract_and_market_manifest(self):
        identity_records = [
            json.loads(line)
            for line in (ROOT / "dataset" / "seed" / "identity.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        access_records = [
            record
            for record in identity_records
            if record["metadata"]["domain"] == "forex_data_access"
        ]
        self.assertGreaterEqual(len(access_records), 5)
        combined = "\n".join(
            message["content"]
            for record in identity_records
            for message in record["messages"]
        )
        self.assertIn("Forex tab", combined)
        self.assertIn("not exposed", combined)
        manifest = json.loads((ROOT / "dataset" / "market_data" / "xauusd_source_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(681227, manifest["total_records"])
        self.assertEqual(["M5", "M15", "M30", "H1", "H4", "D1"], manifest["timeframes"])
        self.assertEqual("unknown", manifest["source"]["source_timezone"])
        self.assertEqual("unknown_bar_open_or_close", manifest["source"]["timestamp_semantics"])


if __name__ == "__main__":
    unittest.main()
