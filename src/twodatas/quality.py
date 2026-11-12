from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .ingest import Bar, FileIngestResult

EXPECTED_MINUTES = {
    "M1": 1, "M2": 2, "M3": 3, "M4": 4, "M5": 5, "M6": 6,
    "M10": 10, "M12": 12, "M15": 15, "M20": 20, "M30": 30,
    "H1": 60, "H2": 120, "H3": 180, "H4": 240, "H6": 360,
    "H8": 480, "H12": 720, "D1": 1440, "W1": 10080,
}


def timeframe_minutes(timeframe: str) -> int | None:
    value = timeframe.upper()
    if value in EXPECTED_MINUTES:
        return EXPECTED_MINUTES[value]
    # Calendar months have variable duration; do not estimate them as fixed minutes.
    return None


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
    bad_ohlc = sum(
        not (r.high >= max(r.open, r.close) and r.low <= min(r.open, r.close) and r.high >= r.low)
        for r in rows
    )
    nonpositive = sum(min(r.open, r.high, r.low, r.close) <= 0 for r in rows)
    zero_tick = sum(r.tick_volume == 0 for r in rows)
    negative_spread = sum(r.spread_points < 0 for r in rows)
    nonzero_real_volume = sum(r.real_volume != 0 for r in rows)
    spreads = sorted(r.spread_points for r in rows)

    gaps = []
    expected = timeframe_minutes(result.timeframe)
    if expected is not None:
        for i, (left, right) in enumerate(zip(times, times[1:]), start=1):
            delta = (right - left).total_seconds() / 60
            if delta > expected:
                gaps.append({
                    "after_timestamp": rows[i-1].source_timestamp,
                    "before_timestamp": rows[i].source_timestamp,
                    "elapsed_minutes": int(delta),
                })

    return {
        "source_file": result.source_file,
        "instrument": rows[0].instrument if rows else None,
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
            "zero_count": sum(value == 0 for value in spreads),
        },
        "interval_gap_count": len(gaps),
        "largest_gaps": sorted(gaps, key=lambda gap: gap["elapsed_minutes"], reverse=True)[:20],
        "quality_status": (
            "STRUCTURAL_PASS"
            if rows and ordered and duplicate_count == 0 and bad_ohlc == 0
            and nonpositive == 0 and zero_tick == 0 and negative_spread == 0
            else "STRUCTURAL_FAIL"
        ),
        "admission_status": "PENDING_SOURCE_SEMANTICS_AND_RIGHTS_REVIEW",
        "limitations": [
            "Timezone is unknown; timestamps are preserved as source-local/naive values.",
            "MT5 bar timestamp convention is unconfirmed; no UTC conversion or bar shifting is applied.",
            "Spread values are preserved in source points; point size and broker contract specification are unknown.",
            "Real volume is reported without assuming it is exchange-traded volume.",
            "Interval gaps are reported, not automatically filled; closures and holidays are not classified yet.",
            "Calendar-month intervals are not assessed using a fixed-minute gap threshold.",
        ],
    }


def audit_archive(results: Iterable[FileIngestResult]) -> dict:
    files = [audit_file(item) for item in results]
    instruments = sorted({item["instrument"] for item in files if item["instrument"]})
    return {
        "dataset": instruments[0] if len(instruments) == 1 else "multi-instrument",
        "instruments": instruments,
        "audit_version": "0.2.0",
        "source_format": "MetaTrader tab-delimited CSV inside ZIP",
        "files": files,
        "total_rows": sum(item["row_count"] for item in files),
        "overall_status": (
            "STRUCTURAL_PASS_WITH_LIMITATIONS"
            if files and all(item["quality_status"] == "STRUCTURAL_PASS" for item in files)
            else "STRUCTURAL_REVIEW_REQUIRED"
        ),
        "dataset_admission_status": "NOT_ADMITTED_PENDING_SOURCE_SEMANTICS_AND_RIGHTS_REVIEW",
        "critical_unknowns": [
            "source timezone", "bar timestamp convention", "broker/server identity",
            "symbol contract/point size", "historical session calendar", "data license/redistribution rights",
        ],
    }
