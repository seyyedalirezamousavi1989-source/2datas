from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

from .ingest import FileIngestResult
from .quality import parse_source_time

MINUTES = {"M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
PAIRS = [("M5", "M15"), ("M15", "M30"), ("M30", "H1"), ("H1", "H4"), ("H4", "D1")]


def _floor_time(value: datetime, minutes: int) -> datetime:
    if minutes == 1440:
        return value.replace(hour=0, minute=0, second=0, microsecond=0)
    total = value.hour * 60 + value.minute
    floored = (total // minutes) * minutes
    return value.replace(hour=floored // 60, minute=floored % 60, second=0, microsecond=0)


def audit_timeframe_alignment(results: Iterable[FileIngestResult]) -> dict:
    """Test child-to-parent OHLC/tick-volume aggregation on naive source clock buckets."""
    by_tf = {result.timeframe: result for result in results}
    comparisons = []
    for child_tf, parent_tf in PAIRS:
        if child_tf not in by_tf or parent_tf not in by_tf:
            continue
        child = by_tf[child_tf].rows
        parent = by_tf[parent_tf].rows
        expected = MINUTES[parent_tf] // MINUTES[child_tf]
        groups: dict[datetime, list] = defaultdict(list)
        for bar in child:
            groups[_floor_time(parse_source_time(bar), MINUTES[parent_tf])].append(bar)
        parent_by_time = {parse_source_time(bar): bar for bar in parent}
        overlap = full = partial = overfull = exact = 0
        mismatches = []
        for bucket, bars in groups.items():
            target = parent_by_time.get(bucket)
            if target is None:
                continue
            overlap += 1
            bars.sort(key=lambda b: parse_source_time(b))
            if len(bars) < expected:
                partial += 1
                continue
            if len(bars) > expected:
                overfull += 1
                continue
            full += 1
            aggregate = {
                "open": bars[0].open,
                "high": max(b.high for b in bars),
                "low": min(b.low for b in bars),
                "close": bars[-1].close,
                "tick_volume": sum(b.tick_volume for b in bars),
            }
            actual = {
                "open": target.open,
                "high": target.high,
                "low": target.low,
                "close": target.close,
                "tick_volume": target.tick_volume,
            }
            differing = [key for key in aggregate if aggregate[key] != actual[key]]
            if not differing:
                exact += 1
            elif len(mismatches) < 20:
                mismatches.append({"parent_timestamp": target.source_timestamp, "fields": differing, "child_count": len(bars)})
        comparisons.append({
            "child_timeframe": child_tf,
            "parent_timeframe": parent_tf,
            "clock_bucket_hypothesis": "Treat source timestamps as interval-start clock labels; no timezone conversion or shift applied.",
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
        "audit_version": "0.1.0",
        "method": "Aggregate child OHLC and tick volume into parent clock buckets, compare against provider-native parent bars; only complete child groups are used for exact-match rate.",
        "timezone": "UNKNOWN; source wall-clock only",
        "bar_timestamp_semantics": "Not proven by this test; clock-bucket hypothesis only",
        "comparisons": comparisons,
        "interpretation": "Exact aggregation supports internal timeframe consistency but does not prove timezone, broker identity, bar open/close semantics, licensing or tick-level path fidelity. Partial groups are reported and not automatically treated as missing-data defects.",
    }
