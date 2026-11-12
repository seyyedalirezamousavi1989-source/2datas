import tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from tools.ingestion_planner import build_plan, write_new_plan
from tools.source_registry import evaluate_source

def source(**updates):
    item={"schema_version":"1.0.0","source_id":"synthetic.feed","revision":2,
      "provider":{"name":"Synthetic Provider","organization":"Test Fixture"},"feed_id":"ohlcv-demo","source_type":"internal_synthetic",
      "modalities":["ohlcv","synthetic"],"asset_classes":["FX"],"instruments":[{"instrument_id":"FX.EURUSD.SPOT","provider_symbol":"EURUSD.TEST"}],
      "supported_timeframes":["1m","5m"],"price_basis":"bid","volume_semantics":{"meaning":"tick_volume","unit":"ticks"},
      "timestamp_convention":{"timezone":"UTC","timestamp_field_semantics":"bar_open","bar_boundary":"open_inclusive_close_exclusive"},
      "availability":{"latency_claim":None,"latency_evidence_type":"unknown"},
      "license":{"reference":"internal://synthetic","permissions":{"research":"allowed","model_training":"unknown","redistribution":"prohibited","commercial":"unknown"}},
      "status":"approved","provenance":{"registered_at":"2026-01-01T00:00:00Z","evidence_refs":[{"artifact_id":"synthetic.evidence","claim_type":"technical_metadata","verification_status":"source_reported"}],"operator_id":"test","reviewer_id":"test","source_document_refs":["internal://fixture"]}}
    item.update(updates); return item

def decision_for(s):
    return evaluate_source({"schema_version":"1.0.0","sources":[s]},s["source_id"],"research",
      now=datetime(2026,1,2,tzinfo=timezone.utc),reviewer_id="test-reviewer")

def request(**updates):
    value={"plan_id":"plan.synthetic.001","created_at":"2026-01-03T00:00:00Z","source_id":"synthetic.feed","source_revision":2,
      "instrument_id":"FX.EURUSD.SPOT","timeframe":"1m","start":"2026-01-01T00:00:00Z","end":"2026-01-02T00:00:00Z"}
    value.update(updates); return value

class IngestionPlannerTests(unittest.TestCase):
    def plan(self,s=None,d=None,r=None):
        s=s or source(); return build_plan({"schema_version":"1.0.0","sources":[s]},d or decision_for(s),r or request())
    def test_valid_plan_is_planned_only(self):
        p=self.plan(); self.assertEqual(p["execution"]["status"],"planned_only")
        for key in ("acquisition_authorized","network_access","market_data_read","dataset_written"): self.assertFalse(p["execution"][key])
    def test_requires_admitted_decision(self):
        s=source(); d=decision_for(s); d["decision"]="needs_review"
        with self.assertRaisesRegex(ValueError,"admitted research-use"): self.plan(s,d)
    def test_requires_research_decision(self):
        s=source(); d=evaluate_source({"schema_version":"1.0.0","sources":[s]},s["source_id"],"model_training",now=datetime(2026,1,1,tzinfo=timezone.utc),reviewer_id="test")
        with self.assertRaisesRegex(ValueError,"admitted research-use"): self.plan(s,d)
    def test_registry_revision_must_match(self):
        with self.assertRaisesRegex(ValueError,"revision"): self.plan(r=request(source_revision=1))
    def test_decision_revision_must_match(self):
        s=source(); d=decision_for(s); d["source_revision"]=1
        with self.assertRaisesRegex(ValueError,"decision does not match"): self.plan(s,d)
    def test_non_approved_source_blocked(self):
        with self.assertRaisesRegex(ValueError,"approved"): self.plan(source(status="suspended"))
    def test_expired_source_blocked(self):
        with self.assertRaisesRegex(ValueError,"expired"): self.plan(source(valid_until="2026-01-02T12:00:00Z"))
    def test_instrument_mapping_required(self):
        with self.assertRaisesRegex(ValueError,"mapping"): self.plan(r=request(instrument_id="FX.GBPUSD.SPOT"))
    def test_timeframe_must_be_supported(self):
        with self.assertRaisesRegex(ValueError,"timeframe"): self.plan(r=request(timeframe="1h"))
    def test_ohlcv_modality_required(self):
        s=source(modalities=["quotes"]); d=decision_for(s)
        with self.assertRaisesRegex(ValueError,"OHLCV"): self.plan(s,d)
    def test_time_range_order(self):
        with self.assertRaisesRegex(ValueError,"start must precede"): self.plan(r=request(start="2026-01-02T00:00:00Z",end="2026-01-01T00:00:00Z"))
    def test_output_no_overwrite(self):
        p=self.plan()
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"plan.json"; write_new_plan(p,output)
            with self.assertRaisesRegex(ValueError,"overwrite"): write_new_plan(p,output)
    def test_deterministic(self): self.assertEqual(self.plan(),self.plan())

if __name__=="__main__": unittest.main()
