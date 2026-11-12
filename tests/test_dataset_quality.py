import unittest
from tools.dataset_quality import audit_records

def row(ts="2026-01-01T00:00:00Z",**kw):
    x={"instrument_id":"DEMO","timeframe":"M1","event_time":ts,"open":100,"high":105,"low":95,"close":102,"volume":10}; x.update(kw); return x
class QualityTests(unittest.TestCase):
    def codes(self,r): return {x["code"] for x in r["issues"]}
    def test_valid(self): self.assertEqual(audit_records([row(),row("2026-01-01T00:01:00Z")])["status"],"passed")
    def test_ohlc(self): self.assertIn("OHLC_INVARIANT_VIOLATION",self.codes(audit_records([row(high=99)])))
    def test_timezone_required(self): self.assertIn("TIMESTAMP_INVALID_OR_NAIVE",self.codes(audit_records([row("2026-01-01T00:00:00")])))
    def test_duplicate_key(self): self.assertIn("DUPLICATE_CANONICAL_KEY",self.codes(audit_records([row(),row()])))
    def test_order(self): self.assertIn("TIMESTAMP_NOT_INCREASING",self.codes(audit_records([row("2026-01-01T00:01:00Z"),row()])))
    def test_gap_needs_cadence(self):
        rows=[row(),row("2026-01-01T00:03:00Z")]
        self.assertEqual(audit_records(rows)["summary"]["scheduled_gaps"],0)
        self.assertEqual(audit_records(rows,expected_interval_seconds=60)["summary"]["scheduled_gaps"],1)
    def test_volume(self): self.assertIn("VOLUME_INVALID",self.codes(audit_records([row(volume=-1)])))
    def test_disable_key(self): self.assertNotIn("DUPLICATE_CANONICAL_KEY",self.codes(audit_records([row(),row()],key_fields=())))
if __name__=="__main__": unittest.main()
