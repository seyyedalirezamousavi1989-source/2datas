from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .ingest import Bar, FileIngestResult

EXPECTED_MINUTES = {"M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}


def parse_source_time(bar: Bar) -> datetime:
    fmt = "%Y.%m.%d %H:%M:%S" if bar.timestamp_precision == "second" else "%Y.%m.%d"
    return datetime.strptime(bar.source_timestamp, fmt)


def _percentile(values: list[float], p: float):
    if not values:
        return None
    idx = (len(values) - 1) * p
    lo, hi = int(idx), min(int(idx) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (idx - lo)


def audit_file(result: FileIngestResult) -> dict:
    rows = result.rows
    times = [parse_source_time(row) for row in rows]
    duplicate_count = len(times) - len(set(times))
    ordered = all(a < b for a, b in zip(times, times[1:]))
    bad_ohlc = sum(not (r.high >= max(r.open, r.close) and r.low <= min(r.open, r.close) and r.high >= r.low) for r in rows)
    nonpositive = sum(min(r.open, r.high, r.low, r.close) <= 0 for r in rows)
    zero_tick = sum(r.tick_volume == 0 for r in rows)
    negative_spread = sum(r.spread_points < 0 for r in rows)
    nonzero_real_volume = sum(r.real_volume != 0 for r in rows)
    spreads = sorted(r.spread_points for r in rows)

    gaps = []
    expected = EXPECTED_MINUTES[result.timeframe]
    for i, (a, b) in enumerate(zip(times, times[1:]), start=1):
        delta = (b - a).total_seconds() / 60
        if delta > expected:
            gaps.append({"after_timestamp": rows[i-1].source_timestamp, "before_timestamp": rows[i].source_timestamp, "elapsed_minutes": int(delta)})
    return {
        "source_file": result.source_file,
        "timeframe": result.timeframe,
        "source_sha256": result.source_sha256,
        "row_count": len(rows),
        "first_source_timestamp": rows[0].source_timestamp if rows else None,
        "last_source_timestamp": rows[-1].source_timestamp if rows else None,
        "timestamp_timezone": "UNKNOWN",
        "bar_timestamp_semantics": "UNKNOWN; source convention must be confirmed",
        "timestamp_ordered_strictly": ordered,
        "duplicate_timestamp_count": duplicate_count,
        "invalid_ohlc_count": bad_ohlc,
        "nonpositive_price_count": nonpositive,
        "zero_tick_volume_count": zero_tick,
        "negative_spread_count": negative_spread,
        "nonzero_real_volume_count": nonzero_real_volume,
        "spread_points": {
            "min": min(spreads) if spreads else None,
            "median": _percentile(spreads, .5),
            "p95": _percentile(spreads, .95),
            "max": max(spreads) if spreads else None,
            "zero_count": sum(v == 0 for v in spreads),
        },
        "interval_gap_count": len(gaps),
        "largest_gaps": sorted(gaps, key=lambda g: g["elapsed_minutes"], reverse=True)[:20],
        "quality_status": "STRUCTURAL_PASS" if rows and ordered and duplicate_count == 0 and bad_ohlc == 0 and nonpositive == 0 and zero_tick == 0 and negative_spread == 0 else "STRUCTURAL_FAIL",
        "admission_status": "PENDING_SOURCE_SEMANTICS_AND_RIGHTS_REVIEW",
        "limitations": [
            "Timezone is unknown; timestamps are preserved as source-local/naive values.",
            "MT5 bar timestamp convention is unconfirmed; no UTC conversion or bar shifting is applied.",
            "Spread values are preserved in source points; point size and broker contract specification are unknown.",
            "Real volume is not assumed to be meaningful; source values are reported without interpretation.",
            "Interval gaps are reported, not automatically filled; weekends/holidays/session closures are not classified yet.",
        ],
    }


def audit_archive(results: Iterable[FileIngestResult]) -> dict:
    files = [audit_file(item) for item in results]
    return {
        "dataset": "XAUUSD",
        "audit_version": "0.1.0",
        "source_format": "MetaTrader tab-delimited CSV inside ZIP",
        "files": files,
        "total_rows": sum(item["row_count"] for item in files),
        "overall_status": "STRUCTURAL_PASS_WITH_LIMITATIONS" if files and all(f["quality_status"] == "STRUCTURAL_PASS" for f in files) else "STRUCTURAL_REVIEW_REQUIRED",
        "dataset_admission_status": "NOT_ADMITTED_PENDING_SOURCE_SEMANTICS_AND_RIGHTS_REVIEW",
        "critical_unknowns": ["source timezone", "bar timestamp convention", "broker identity", "symbol contract/point size", "historical session calendar", "data license/redistribution rights"],
    }
