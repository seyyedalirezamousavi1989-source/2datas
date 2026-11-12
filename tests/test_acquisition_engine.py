import unittest
from tools.acquisition_engine import SyntheticAdapter,collect_fixture_pages,classify_error,inspect_bar,request_fingerprint,simulate,utc_timestamp
class Loop:
    network_enabled=False
    def fetch_page(self,cursor,page_size): return [], "again"
class Tests(unittest.TestCase):
    def test_fixture_deterministic_and_preserves_incomplete(self):
        a,p=collect_fixture_pages(SyntheticAdapter()); b,q=collect_fixture_pages(SyntheticAdapter())
        self.assertEqual((a,p),(b,q)); self.assertEqual(len(a),4)
        self.assertIn("bar_incomplete",inspect_bar(a[2])); self.assertEqual(a[2]["completeness"],"incomplete")
    def test_loop_and_page_limit(self):
        with self.assertRaisesRegex(ValueError,"loop"): collect_fixture_pages(Loop())
        with self.assertRaisesRegex(ValueError,"limit"): collect_fixture_pages(SyntheticAdapter(),1,1)
    def test_error_classes(self):
        self.assertEqual(classify_error("timeout"),"transient")
        self.assertEqual(classify_error("rate_limit"),"rate_limited")
        self.assertEqual(classify_error("auth_required"),"auth_required")
        self.assertEqual(classify_error("unsupported"),"unsupported")
    def test_utc(self):
        self.assertEqual(utc_timestamp("2025-01-01T03:30:00","Asia/Tehran"),"2025-01-01T00:00:00Z")
        with self.assertRaisesRegex(ValueError,"naive"): utc_timestamp("2025-01-01T00:00:00")
    def test_fingerprint(self):
        self.assertEqual(request_fingerprint({"a":1,"b":2}),request_fingerprint({"b":2,"a":1}))
    def test_manifest_is_hard_disabled(self):
        plan={"plan_id":"p","execution":{"status":"planned_only","acquisition_authorized":False}}
        m=simulate(plan,SyntheticAdapter(),"r","2025-01-01T00:00:00Z")
        self.assertEqual(m["records_seen"],4); self.assertFalse(any(m["execution"].values()))
        self.assertEqual(m["mode"],"offline_fixture_only")
    def test_rejects_authorized_plan(self):
        with self.assertRaisesRegex(ValueError,"metadata-only"):
            simulate({"plan_id":"p","execution":{"status":"ready","acquisition_authorized":True}},SyntheticAdapter(),"r","2025-01-01T00:00:00Z")
if __name__=="__main__": unittest.main()
