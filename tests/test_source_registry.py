import tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from tools.source_registry import validate_registry, evaluate_source, write_new_decision

def source(**kw):
    s={"schema_version":"1.0.0","source_id":"synthetic.demo.feed","revision":1,
    "provider":{"name":"Synthetic Demo","organization":"Internal Test"},"feed_id":"demo","source_type":"internal_synthetic",
    "modalities":["ohlcv","synthetic"],"asset_classes":["FX"],
    "instruments":[{"instrument_id":"FX.EURUSD.SPOT","provider_symbol":"EURUSD","venue":"SIM"}],"supported_timeframes":["1m"],
    "price_basis":"bid","volume_semantics":{"meaning":"tick_volume","unit":"ticks"},
    "timestamp_convention":{"timezone":"UTC","timestamp_field_semantics":"bar_open","bar_boundary":"open_inclusive_close_exclusive"},
    "availability":{"latency_claim":None,"latency_evidence_type":"unknown"},
    "license":{"reference":"internal://synthetic-terms","permissions":{"research":"allowed","model_training":"allowed","redistribution":"prohibited","commercial":"unknown"}},
    "status":"approved","provenance":{"registered_at":"2026-01-01T00:00:00Z","evidence_refs":[{"artifact_id":"evidence.synthetic.1","claim_type":"technical_metadata","verification_status":"source_reported"}],"operator_id":"operator","reviewer_id":"reviewer","source_document_refs":["internal://spec"]}}
    s.update(kw); return s
def reg(s=None): return {"schema_version":"1.0.0","sources":[s or source()]}

class SourceRegistryTests(unittest.TestCase):
    now=datetime(2026,1,2,tzinfo=timezone.utc)
    def ev(self,s=None,use="model_training"): return evaluate_source(reg(s), "synthetic.demo.feed",use,now=self.now,reviewer_id="reviewer")
    def test_valid_registry(self): self.assertEqual(validate_registry(reg()),["synthetic.demo.feed"])
    def test_unknown_training_permission_review(self):
        s=source(); s["license"]["permissions"]["model_training"]="unknown"; self.assertEqual(self.ev(s)["decision"],"needs_review")
    def test_prohibited_use_rejected(self): self.assertEqual(self.ev(use="redistribution")["decision"],"rejected")
    def test_non_approved_lifecycle_blocked(self):
        for status in ("draft","under_review","rejected","suspended","retired"): self.assertEqual(self.ev(source(status=status))["decision"],"rejected")
    def test_unknown_timezone_review(self):
        s=source(); s["timestamp_convention"]["timezone"]="unknown"; self.assertEqual(self.ev(s)["decision"],"needs_review")
    def test_unknown_boundary_review(self):
        s=source(); s["timestamp_convention"]["bar_boundary"]="unknown"; self.assertEqual(self.ev(s)["decision"],"needs_review")
    def test_missing_mapping_review(self): self.assertEqual(self.ev(source(instruments=[]))["decision"],"needs_review")
    def test_unknown_price_basis_review(self): self.assertEqual(self.ev(source(price_basis="unknown"))["decision"],"needs_review")
    def test_expired_approval_review(self): self.assertEqual(self.ev(source(valid_until="2026-01-01T00:00:00Z"))["decision"],"needs_review")
    def test_missing_evidence_review(self):
        s=source(); s["provenance"]["evidence_refs"]=[]; self.assertEqual(self.ev(s)["decision"],"needs_review")
    def test_research_does_not_imply_training(self):
        s=source(); s["license"]["permissions"]["model_training"]="unknown"
        self.assertEqual(self.ev(s,"research")["decision"],"admitted"); self.assertEqual(self.ev(s)["decision"],"needs_review")
    def test_unknown_volume_review(self): self.assertEqual(self.ev(source(volume_semantics={"meaning":"unknown","unit":None}))["decision"],"needs_review")
    def test_output_no_overwrite(self):
        r=self.ev()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"decision.json"; write_new_decision(r,p)
            with self.assertRaisesRegex(ValueError,"overwrite"): write_new_decision(r,p)
    def test_duplicate_source_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate source_id"): validate_registry({"schema_version":"1.0.0","sources":[source(),source()]})
    def test_deterministic(self): self.assertEqual(self.ev(),self.ev())

if __name__=="__main__": unittest.main()
