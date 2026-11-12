import unittest
from tools.temporal_alignment import align_as_of


def bar(record_id, start, end, available=None, tf="1h", status="COMPLETE",
        provider="feed-a", instrument="EURUSD", basis="mid", revision="r1"):
    return {
        "record_id": record_id, "instrument_id": instrument, "provider": provider,
        "price_basis": basis, "timeframe": tf, "interval_start": start,
        "interval_end": end, "available_at": available or end,
        "completion_status": status, "source_revision_id": revision,
    }


class TemporalAlignmentTests(unittest.TestCase):
    def test_completed_bar_is_selected_only_after_close_and_availability(self):
        rows = [bar("h1", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z",
                    "2026-01-01T11:00:05Z")]
        before = align_as_of(rows, ["2026-01-01T11:00:03Z"])
        after = align_as_of(rows, ["2026-01-01T11:00:05Z"])
        self.assertEqual(before["snapshots"][0]["selections"][0]["status"], "MISSING")
        self.assertEqual(after["snapshots"][0]["selections"][0]["selected_record_id"], "h1")

    def test_future_higher_timeframe_bar_is_not_lookahead_eligible(self):
        rows = [bar("h4", "2026-01-01T08:00:00Z", "2026-01-01T12:00:00Z",
                    tf="4h")]
        result = align_as_of(rows, ["2026-01-01T10:30:00Z"])
        self.assertEqual(result["snapshots"][0]["selections"][0]["status"], "MISSING")

    def test_late_arrival_does_not_backdate_availability(self):
        rows = [bar("late", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z",
                    "2026-01-01T11:07:00Z")]
        result = align_as_of(rows, ["2026-01-01T11:05:00Z", "2026-01-01T11:08:00Z"])
        self.assertEqual(result["snapshots"][0]["selections"][0]["status"], "MISSING")
        self.assertEqual(result["snapshots"][1]["selections"][0]["selected_record_id"], "late")

    def test_partial_bar_is_separate_and_opt_in(self):
        rows = [bar("partial", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z",
                    "2026-01-01T10:30:00Z", status="PARTIAL")]
        denied = align_as_of(rows, ["2026-01-01T10:30:00Z"])
        allowed = align_as_of(rows, ["2026-01-01T10:30:00Z"], allow_partial=True)
        self.assertIsNone(denied["snapshots"][0]["selections"][0]["partial_record_id"])
        self.assertEqual(allowed["snapshots"][0]["selections"][0]["partial_record_id"], "partial")
        self.assertEqual(allowed["snapshots"][0]["selections"][0]["status"], "MISSING")

    def test_duplicate_interval_fails_closed(self):
        rows = [bar("a", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z"),
                bar("b", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z")]
        result = align_as_of(rows, ["2026-01-01T11:01:00Z"])
        self.assertEqual(result["snapshots"][0]["selections"][0]["status"], "AMBIGUOUS_DUPLICATE")
        self.assertIsNone(result["snapshots"][0]["selections"][0]["selected_record_id"])

    def test_out_of_order_is_reported_without_sorting_input(self):
        rows = [bar("later", "2026-01-01T11:00:00Z", "2026-01-01T12:00:00Z"),
                bar("earlier", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z")]
        result = align_as_of(rows, ["2026-01-01T12:01:00Z"])
        self.assertTrue(result["snapshots"][0]["selections"][0]["input_order_violation"])
        self.assertEqual([r["record_id"] for r in rows], ["later", "earlier"])

    def test_staleness_is_explicit(self):
        rows = [bar("old", "2026-01-01T09:00:00Z", "2026-01-01T10:00:00Z")]
        result = align_as_of(rows, ["2026-01-01T12:00:00Z"],
                             max_staleness_seconds={"1h": 1800})
        self.assertEqual(result["snapshots"][0]["selections"][0]["status"], "STALE")

    def test_timezone_offsets_are_normalized_to_utc(self):
        rows = [bar("offset", "2026-01-01T05:00:00-05:00", "2026-01-01T06:00:00-05:00")]
        result = align_as_of(rows, ["2026-01-01T11:00:00Z"])
        self.assertEqual(result["snapshots"][0]["selections"][0]["interval_end"], "2026-01-01T11:00:00Z")

    def test_rejects_naive_timestamp_and_inconsistent_interval(self):
        with self.assertRaisesRegex(ValueError, "explicit timezone"):
            align_as_of([bar("bad", "2026-01-01T10:00:00", "2026-01-01T11:00:00Z")],
                        ["2026-01-01T12:00:00Z"])
        with self.assertRaisesRegex(ValueError, "interval duration"):
            align_as_of([bar("bad", "2026-01-01T10:00:00Z", "2026-01-01T12:00:00Z")],
                        ["2026-01-01T12:00:00Z"])

    def test_incompatible_sources_are_not_collapsed(self):
        rows = [bar("a", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z", provider="feed-a"),
                bar("b", "2026-01-01T10:00:00Z", "2026-01-01T11:00:00Z", provider="feed-b", basis="bid")]
        result = align_as_of(rows, ["2026-01-01T11:01:00Z"])
        self.assertEqual(len(result["snapshots"][0]["selections"]), 2)

    def test_rejects_duplicate_decision_cutoffs(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            align_as_of([], ["2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"])


if __name__ == "__main__":
    unittest.main()
