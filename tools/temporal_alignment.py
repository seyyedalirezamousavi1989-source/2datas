"""Read-only point-in-time temporal alignment for canonical OHLCV metadata."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Iterable
import hashlib, json, re

_TIMEFRAME = re.compile(r"^([1-9][0-9]*)(m|h|d|w)$")
_ALLOWED_STATUS = {"COMPLETE", "PARTIAL"}

def _instant(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include an explicit timezone")
    return parsed.astimezone(timezone.utc)

def _timeframe_seconds(value: str) -> int:
    match = _TIMEFRAME.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise ValueError("timeframe must use a positive integer followed by m, h, d, or w")
    amount, unit = int(match.group(1)), match.group(2)
    return amount * {"m": 60, "h": 3600, "d": 86400, "w": 604800}[unit]

def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")

def align_as_of(records: Iterable[dict[str, Any]], decision_timestamps: Iterable[str], *,
                max_staleness_seconds: dict[str, int] | None = None,
                allow_partial: bool = False) -> dict[str, Any]:
    """Select completed bar references as-of cutoffs; never mutate or repair inputs."""
    rows = list(records)
    decisions = [_instant(v, "decision_timestamp") for v in decision_timestamps]
    if not decisions:
        raise ValueError("at least one decision timestamp is required")
    if len(set(decisions)) != len(decisions):
        raise ValueError("decision timestamps must be unique")
    stale = max_staleness_seconds or {}
    for tf, seconds in stale.items():
        _timeframe_seconds(tf)
        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < 0:
            raise ValueError("max staleness values must be non-negative integers")

    parsed, seen_ids = [], set()
    input_order: dict[tuple[str, str, str, str], list[datetime]] = {}
    duplicate_counts: dict[tuple, int] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError("each record must be an object")
        required = ("record_id", "instrument_id", "provider", "price_basis", "timeframe",
                    "interval_start", "interval_end", "available_at", "completion_status",
                    "source_revision_id")
        if any(not isinstance(row.get(k), str) or not row[k] for k in required):
            raise ValueError(f"record {index} is missing required string metadata")
        if row["record_id"] in seen_ids:
            raise ValueError("record_id values must be unique")
        seen_ids.add(row["record_id"])
        duration = _timeframe_seconds(row["timeframe"])
        start, end = _instant(row["interval_start"], "interval_start"), _instant(row["interval_end"], "interval_end")
        available = _instant(row["available_at"], "available_at")
        if end <= start:
            raise ValueError("interval_end must be later than interval_start")
        if int((end - start).total_seconds()) != duration:
            raise ValueError("interval duration does not match declared timeframe; session/calendar bars require a separately verified calendar adapter")
        if row["completion_status"] not in _ALLOWED_STATUS:
            raise ValueError("completion_status must be COMPLETE or PARTIAL")
        if row["completion_status"] == "COMPLETE" and available < end:
            raise ValueError("a completed bar cannot be available before its interval_end")
        # Price basis is part of the partition: bid/ask/mid observations must never collapse.
        key = (row["instrument_id"], row["provider"], row["price_basis"], row["timeframe"])
        input_order.setdefault(key, []).append(start)
        dup_key = (*key, start, end)
        duplicate_counts[dup_key] = duplicate_counts.get(dup_key, 0) + 1
        parsed.append({**row, "_start": start, "_end": end, "_available": available,
                       "_partition": key, "_duplicate_key": dup_key})

    out_of_order = {key for key, starts in input_order.items()
                    if any(starts[i] < starts[i-1] for i in range(1, len(starts)))}
    duplicates = {key for key, count in duplicate_counts.items() if count > 1}
    partitions: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in parsed:
        partitions.setdefault(row["_partition"], []).append(row)

    snapshots = []
    for cutoff in decisions:
        selections = []
        for key in sorted(partitions):
            instrument, provider, price_basis, timeframe = key
            candidates = partitions[key]
            eligible = [r for r in candidates if r["completion_status"] == "COMPLETE"
                        and r["_end"] <= cutoff and r["_available"] <= cutoff]
            eligible.sort(key=lambda r: (r["_end"], r["_available"], r["record_id"]))
            selected = eligible[-1] if eligible else None
            ambiguous = bool(selected and selected["_duplicate_key"] in duplicates)
            age = int((cutoff - selected["_end"]).total_seconds()) if selected else None
            max_age = stale.get(timeframe)
            is_stale = bool(selected and max_age is not None and age > max_age)
            partial = None
            if allow_partial:
                partials = [r for r in candidates if r["completion_status"] == "PARTIAL"
                            and r["_start"] <= cutoff < r["_end"] and r["_available"] <= cutoff]
                if len(partials) == 1:
                    partial = partials[0]
            status = "AMBIGUOUS_DUPLICATE" if ambiguous else ("MISSING" if selected is None else ("STALE" if is_stale else "AVAILABLE"))
            selections.append({
                "instrument_id": instrument, "provider": provider, "price_basis": price_basis,
                "timeframe": timeframe, "status": status,
                "selected_record_id": selected["record_id"] if selected and not ambiguous else None,
                "interval_start": _iso(selected["_start"]) if selected and not ambiguous else None,
                "interval_end": _iso(selected["_end"]) if selected and not ambiguous else None,
                "available_at": _iso(selected["_available"]) if selected and not ambiguous else None,
                "age_seconds_from_interval_end": age,
                "partial_record_id": partial["record_id"] if partial else None,
                "input_order_violation": key in out_of_order,
                "duplicate_interval_detected": bool(selected and selected["_duplicate_key"] in duplicates)
            })
        canonical = {"decision_timestamp": _iso(cutoff), "selections": selections}
        fp = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        snapshots.append({**canonical, "alignment_fingerprint": fp})
    return {
        "schema_version": "1.0.0", "engine": "temporal_alignment",
        "mode": "read_only_metadata_alignment", "network_access": False,
        "market_data_written": False, "records_mutated": False, "snapshots": snapshots,
        "diagnostics": {"input_record_count": len(rows), "decision_count": len(decisions),
            "duplicate_interval_count": len(duplicates), "out_of_order_partition_count": len(out_of_order),
            "calendar_session_adapter_used": False,
            "note": "Fixed-duration UTC intervals only. Session-aware daily/weekly bars and DST-specific boundaries require a separately verified calendar adapter."}
    }
