from __future__ import annotations

import json
import hashlib
from bisect import bisect_right
from datetime import datetime
from pathlib import Path
from typing import Iterable

SNAPSHOT_VERSION = "mtf-snapshot-0.1.0"
CONTEXT_FIELDS = (
    "open", "high", "low", "close", "tick_volume", "spread_points",
    "atr", "true_range", "range_to_atr", "body_to_atr", "body_to_range",
    "close_location", "return_1", "displacement", "volatility_ratio", "volatility_state",
    "structure_direction", "last_confirmed_swing_high", "last_confirmed_swing_low",
    "bos", "choch", "fvg", "fvg_zone_updates", "liquidity_sweep",
    "latest_equal_high_pool", "latest_equal_low_pool", "active_fvg_zones",
    "order_block_candidate", "order_block_updates", "active_order_block_zones",
)


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"MTF requires timezone-aware UTC availability timestamps: {value}")
    return parsed


def load_feature_events(features_dir: str) -> tuple[dict[str, dict[str, list[dict]]], dict]:
    root = Path(features_dir)
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Feature manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("feature_version") != "price-action-0.2.0":
        raise ValueError("Unsupported or missing feature manifest version")
    partitions = manifest.get("partitions")
    if not isinstance(partitions, list) or not partitions:
        raise ValueError("Feature manifest has no partitions")

    grouped: dict[str, dict[str, list[dict]]] = {}
    for partition in partitions:
        filename = Path(partition["output_path"]).name
        path = root / filename
        if not path.is_file():
            raise FileNotFoundError(f"Feature partition missing: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != partition.get("output_sha256"):
            raise ValueError(f"Feature partition checksum mismatch: {filename}")
        count = 0
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("feature_version") != manifest["feature_version"]:
                    raise ValueError(f"Feature version mismatch in {filename}:{line_number}")
                if event.get("instrument") != partition.get("instrument") or event.get("timeframe") != partition.get("timeframe"):
                    raise ValueError(f"Partition identity mismatch in {filename}:{line_number}")
                if event.get("source_sha256") != partition.get("source_sha256"):
                    raise ValueError(f"Source hash lineage mismatch in {filename}:{line_number}")
                grouped.setdefault(event["instrument"], {}).setdefault(event["timeframe"], []).append(event)
                count += 1
        if count != partition.get("events"):
            raise ValueError(f"Feature row count mismatch for {filename}: expected {partition.get('events')}, got {count}")

    for instrument, by_tf in grouped.items():
        for timeframe, events in by_tf.items():
            events.sort(key=lambda item: item.get("event_index", -1))
            seen = set()
            for event in events:
                stamp = event.get("available_at_utc")
                if stamp:
                    instant = _utc(stamp)
                    if instant in seen:
                        raise ValueError(f"Duplicate availability timestamp for {instrument}/{timeframe}: {stamp}")
                    seen.add(instant)
    return grouped, manifest

def build_mtf_snapshots(
    events_by_instrument: dict[str, dict[str, list[dict]]],
    *,
    decision_timeframes: Iterable[str],
) -> tuple[dict[str, list[dict]], dict]:
    outputs: dict[str, list[dict]] = {}
    stats = {"decision_events_seen": 0, "unresolved_decision_events": 0, "snapshots_written": 0}
    requested = tuple(dict.fromkeys(value.upper() for value in decision_timeframes))
    for instrument, by_tf in sorted(events_by_instrument.items()):
        indexed: dict[str, tuple[list[datetime], list[dict]]] = {}
        for timeframe, events in by_tf.items():
            valid = []
            instants = []
            for event in events:
                stamp = event.get("available_at_utc")
                if not stamp:
                    continue
                instant = _utc(stamp)
                if instants and instant <= instants[-1]:
                    raise ValueError(f"Non-increasing availability times for {instrument}/{timeframe}")
                instants.append(instant)
                valid.append(event)
            indexed[timeframe] = (instants, valid)

        for decision_tf in requested:
            base = by_tf.get(decision_tf, [])
            target_key = f"{instrument}_{decision_tf}"
            target = outputs.setdefault(target_key, [])
            for event in base:
                stats["decision_events_seen"] += 1
                decision_stamp = event.get("available_at_utc")
                if not decision_stamp:
                    stats["unresolved_decision_events"] += 1
                    continue
                decision_at = _utc(decision_stamp)
                context = {}
                for timeframe, (instants, candidates) in indexed.items():
                    pos = bisect_right(instants, decision_at) - 1
                    if pos < 0:
                        continue
                    selected = candidates[pos]
                    selected_at = instants[pos]
                    context[timeframe] = {
                        "source_timestamp": selected.get("source_timestamp"),
                        "source_file": selected.get("source_file"),
                        "source_sha256": selected.get("source_sha256"),
                        "source_row_number": selected.get("source_row_number"),
                        "available_at_utc": selected.get("available_at_utc"),
                        "age_minutes": round((decision_at - selected_at).total_seconds() / 60, 6),
                        "features": {key: selected.get(key) for key in CONTEXT_FIELDS if key in selected},
                    }
                target.append({
                    "snapshot_version": SNAPSHOT_VERSION,
                    "instrument": instrument,
                    "decision_timeframe": decision_tf,
                    "decision_timestamp": decision_stamp,
                    "decision_source_timestamp": event.get("source_timestamp"),
                    "decision_source_file": event.get("source_file"),
                    "decision_source_sha256": event.get("source_sha256"),
                    "decision_source_row_number": event.get("source_row_number"),
                    "context_by_timeframe": context,
                    "causal_policy": "For every timeframe, select only the latest feature event with available_at_utc <= decision_timestamp; unresolved events are excluded.",
                })
                stats["snapshots_written"] += 1
    return outputs, stats
