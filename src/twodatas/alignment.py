from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterable

from .ingest import FileIngestResult
from .quality import parse_source_time

MINUTES = {
    "M1": 1, "M2": 2, "M3": 3, "M4": 4, "M5": 5, "M6": 6,
    "M10": 10, "M12": 12, "M15": 15, "M20": 20, "M30": 30,
    "H1": 60, "H2": 120, "H3": 180, "H4": 240, "H6": 360,
    "H8": 480, "H12": 720, "D1": 1440,
}
PAIRS = [
    ("M1", "M5"), ("M2", "M10"), ("M3", "M15"), ("M4", "M20"),
    ("M5", "M15"), ("M6", "M30"), ("M10", "M30"), ("M15", "M30"),
    ("M30", "H1"), ("H1", "H4"), ("H2", "H8"), ("H3", "H12"),
    ("H4", "D1"), ("H6", "D1"), ("H8", "D1"), ("H12", "D1"),
]


def audit_timeframe_alignment(results: Iterable[FileIngestResult]) -> dict:
    """Compare child bars inside each provider-native parent interval.

    Parent timestamps are treated as interval-start labels for this diagnostic only.
    Using each native parent timestamp avoids assuming that all brokers anchor H4/H1
    bars to midnight. Timezone and timestamp semantics are not inferred here.
    """
    by_instrument: dict[str, dict[str, FileIngestResult]] = defaultdict(dict)
    for result in results:
        instrument = result.rows[0].instrument if result.rows else "UNKNOWN"
        by_instrument[instrument][result.timeframe] = result

    comparisons = []
    for instrument, by_tf in sorted(by_instrument.items()):
        for child_tf, parent_tf in PAIRS:
            if child_tf not in by_tf or parent_tf not in by_tf:
                continue
            child = by_tf[child_tf].rows
            parent = by_tf[parent_tf].rows
            child_times = [parse_source_time(bar) for bar in child]
            parent_minutes = MINUTES[parent_tf]
            expected = parent_minutes // MINUTES[child_tf]
            overlap = full = partial = overfull = exact = 0
            mismatches = []

            for parent_bar in parent:
                parent_time = parse_source_time(parent_bar)
                interval_end = parent_time + timedelta(minutes=parent_minutes)
                start_idx = bisect_left(child_times, parent_time)
                end_idx = bisect_left(child_times, interval_end)
                bars = child[start_idx:end_idx]
                if not bars:
                    continue
                overlap += 1
                if len(bars) < expected:
                    partial += 1
                    continue
                if len(bars) > expected:
                    overfull += 1
                    continue
                full += 1
                aggregate = {
                    "open": bars[0].open,
                    "high": max(bar.high for bar in bars),
                    "low": min(bar.low for bar in bars),
                    "close": bars[-1].close,
                    "tick_volume": sum(bar.tick_volume for bar in bars),
                }
                actual = {
                    "open": parent_bar.open,
                    "high": parent_bar.high,
                    "low": parent_bar.low,
                    "close": parent_bar.close,
                    "tick_volume": parent_bar.tick_volume,
                }
                differing = [key for key in aggregate if aggregate[key] != actual[key]]
                if not differing:
                    exact += 1
                elif len(mismatches) < 20:
                    mismatches.append({
                        "parent_timestamp": parent_bar.source_timestamp,
                        "fields": differing,
                        "child_count": len(bars),
                    })

            comparisons.append({
                "instrument": instrument,
                "child_timeframe": child_tf,
                "parent_timeframe": parent_tf,
                "interval_hypothesis": "Each provider-native parent timestamp marks interval start; child bars are assigned by [parent_start, parent_start + parent_duration).",
                "expected_child_bars_per_parent": expected,
                "overlapping_parent_buckets": overlap,
                "complete_child_groups": full,
                "partial_child_groups": partial,
                "overfull_child_groups": overfull,
                "exact_ohlc_and_tick_volume_matches": exact,
                "complete_group_mismatches": full - exact,
                "exact_match_rate_complete_groups": (exact / full) if full else None,
                "mismatch_examples": mismatches,
            })

    return {
        "audit_version": "0.3.0",
        "method": "Aggregate child OHLC and tick volume within each provider-native parent interval; only complete groups enter exact-match rate.",
        "timezone": "UNKNOWN; source wall-clock only",
        "bar_timestamp_semantics": "Interval-start hypothesis for alignment diagnostics only; not proven by aggregation.",
        "comparisons": comparisons,
        "interpretation": "Exact aggregation supports internal timeframe consistency only. It does not prove timezone, broker identity, timestamp convention, licensing or tick-level path fidelity. Monthly and weekly alignment require calendar-aware source semantics and are not inferred here.",
    }
