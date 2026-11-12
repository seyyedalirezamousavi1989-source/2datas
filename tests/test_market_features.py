import unittest
from datetime import datetime,timedelta,timezone
from tools.market_features import extract_market_features

def make_bars(rows,delay=0):
    out=[]; base=datetime(2026,1,1,tzinfo=timezone.utc)
    for i,(o,h,l,c) in enumerate(rows):
        start=base+timedelta(hours=i); end=start+timedelta(hours=1)
        out.append({"record_id":f"b{i}","instrument_id":"EURUSD","provider":"fixture","price_basis":"mid","timeframe":"1h",
        "interval_start":start.isoformat().replace("+00:00","Z"),"interval_end":end.isoformat().replace("+00:00","Z"),
        "available_at":(end+timedelta(seconds=delay)).isoformat().replace("+00:00","Z"),"completion_status":"COMPLETE",
        "open":str(o),"high":str(h),"low":str(l),"close":str(c)})
    return out

class MarketFeatureTests(unittest.TestCase):
    def test_pivot_waits_for_right_confirmation(self):
        bars=make_bars([(1,2,0,1),(1,3,0,2),(2,5,1,3),(3,4,2,3),(3,4,2,3)])
        a=extract_market_features(bars[:4],decision_timestamp="2026-01-01T04:00:00Z",pivot_left=1,pivot_right=2)
        b=extract_market_features(bars,decision_timestamp="2026-01-01T05:00:00Z",pivot_left=1,pivot_right=2)
        self.assertFalse(any(e["event_type"]=="SWING_HIGH" for e in a["events"]))
        self.assertTrue(any(e["event_type"]=="SWING_HIGH" for e in b["events"]))
    def test_late_bar_is_not_admitted(self):
        bars=make_bars([(1,2,0,1),(1,3,0,2)],delay=120)
        r=extract_market_features(bars,decision_timestamp="2026-01-01T02:01:00Z")
        self.assertEqual(r["admitted_bar_count"],1)
    def test_bullish_fvg(self):
        bars=make_bars([(10,11,9,10),(12,14,12,13),(15,16,14,15)])
        r=extract_market_features(bars,decision_timestamp="2026-01-01T03:00:00Z")
        f=[e for e in r["events"] if e["event_type"]=="FVG_BULLISH"]
        self.assertEqual(len(f),1); self.assertEqual((f[0]["zone_low"],f[0]["zone_high"]),("11","14"))
    def test_bearish_fvg(self):
        bars=make_bars([(15,16,14,15),(12,13,11,12),(9,10,8,9)])
        r=extract_market_features(bars,decision_timestamp="2026-01-01T03:00:00Z")
        self.assertTrue(any(e["event_type"]=="FVG_BEARISH" for e in r["events"]))
    def test_rejects_out_of_order_and_duplicate(self):
        bars=make_bars([(1,2,0,1),(1,2,0,1)])
        with self.assertRaisesRegex(ValueError,"chronological"):
            extract_market_features(list(reversed(bars)),decision_timestamp="2026-01-01T03:00:00Z")
        with self.assertRaisesRegex(ValueError,"unique"):
            extract_market_features([bars[0],dict(bars[0])],decision_timestamp="2026-01-01T03:00:00Z")
    def test_rejects_naive_and_bad_ohlc(self):
        b=make_bars([(1,2,0,1)]); b[0]["interval_start"]="2026-01-01T00:00:00"
        with self.assertRaisesRegex(ValueError,"explicit timezone"): extract_market_features(b,decision_timestamp="2026-01-01T02:00:00Z")
        b=make_bars([(1,0,0,1)])
        with self.assertRaisesRegex(ValueError,"OHLC"): extract_market_features(b,decision_timestamp="2026-01-01T02:00:00Z")
    def test_atr_warmup(self):
        b=make_bars([(1,3,0,2),(2,4,1,3),(3,5,2,4)])
        r=extract_market_features(b,decision_timestamp="2026-01-01T03:00:00Z",atr_period=2)
        self.assertEqual(len(r["atr"]),2); self.assertEqual(r["atr"][0]["atr"],"3")
    def test_input_immutable_and_deterministic(self):
        b=make_bars([(1,2,0,1),(1,3,0,2),(2,5,1,3),(3,4,2,3),(3,4,2,3)])
        before=repr(b)
        a=extract_market_features(b,decision_timestamp="2026-01-01T05:00:00Z",pivot_left=1,pivot_right=2)
        c=extract_market_features(b,decision_timestamp="2026-01-01T05:00:00Z",pivot_left=1,pivot_right=2)
        self.assertEqual(repr(b),before); self.assertEqual(a["feature_fingerprint"],c["feature_fingerprint"])

if __name__=="__main__": unittest.main()
