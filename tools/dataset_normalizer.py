"""Explicit, deterministic, offline normalization into canonical OHLCV JSONL.

No provider access, guessing, sorting, filling, resampling, or in-place writes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

TIMEFRAME = re.compile(r"^[1-9][0-9]*(m|h|d|w)$")
PRICE_BASES = {"bid", "ask", "mid", "last", "mark", "index", "unknown"}
REQUIRED_MAP = {
    "instrument_id", "venue", "provider", "symbol", "timeframe",
    "event_time", "available_at", "recorded_at", "open", "high", "low",
    "close", "price_basis", "source_artifact_id", "source_record_id",
}
OPTIONAL_MAP = {"volume", "volume_unit"}


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: timestamp must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field}: invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}: timezone is mandatory; naive time is not inferred")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _decimal(value: Any, field: str, *, positive: bool = False) -> str:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field}: expected a decimal value")
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise ValueError(f"{field}: invalid decimal value") from exc
    if not number.is_finite() or (positive and number <= 0):
        raise ValueError(f"{field}: value must be finite" + (" and > 0" if positive else ""))
    rendered = format(number, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def normalize_record(source: dict[str, Any], mapping: dict[str, str], *, source_format: str) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise ValueError("source record must be an object")
    if not isinstance(mapping, dict) or not REQUIRED_MAP.issubset(mapping):
        missing = sorted(REQUIRED_MAP - set(mapping or {}))
        raise ValueError("explicit field mapping missing: " + ", ".join(missing))
    unknown = set(mapping) - REQUIRED_MAP - OPTIONAL_MAP
    if unknown:
        raise ValueError("unsupported mapping targets: " + ", ".join(sorted(unknown)))
    for target, source_field in mapping.items():
        if not isinstance(source_field, str) or not source_field:
            raise ValueError(f"mapping for {target} must name one source field")
        if source_field not in source:
            raise ValueError(f"source field {source_field!r} mapped to {target!r} is absent")

    def value(name: str) -> Any:
        return source[mapping[name]]

    strings = ("instrument_id", "venue", "provider", "symbol", "timeframe",
               "price_basis", "source_artifact_id", "source_record_id")
    out: dict[str, Any] = {"schema_version": "1.0.0"}
    for name in strings:
        v = value(name)
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"{name}: non-empty string required")
        out[name] = v.strip()
    if not TIMEFRAME.fullmatch(out["timeframe"]):
        raise ValueError("timeframe must use an unambiguous positive interval such as 1m, 5m, 1h, 1d")
    if out["price_basis"] not in PRICE_BASES:
        raise ValueError("price_basis must be one of " + ", ".join(sorted(PRICE_BASES)))
    for name in ("event_time", "available_at", "recorded_at"):
        out[name] = _timestamp(value(name), name)
    if out["available_at"] < out["event_time"]:
        raise ValueError("available_at cannot precede event_time")
    if out["recorded_at"] < out["available_at"]:
        raise ValueError("recorded_at cannot precede available_at")
    for name in ("open", "high", "low", "close"):
        out[name] = _decimal(value(name), name, positive=True)
    o, h, l, c = (Decimal(out[k]) for k in ("open", "high", "low", "close"))
    if h < max(o, c) or l > min(o, c) or h < l:
        raise ValueError("OHLC invariant violated")
    if "volume" in mapping:
        raw_volume = value("volume")
        if raw_volume not in (None, ""):
            out["volume"] = _decimal(raw_volume, "volume")
            if Decimal(out["volume"]) < 0:
                raise ValueError("volume must be non-negative")
    if "volume_unit" in mapping:
        unit = value("volume_unit")
        if unit not in (None, ""):
            if not isinstance(unit, str) or not unit.strip():
                raise ValueError("volume_unit must be a non-empty string when supplied")
            out["volume_unit"] = unit.strip()
    out["source"] = {
        "artifact_id": out["source_artifact_id"],
        "record_id": out["source_record_id"],
        "raw_payload_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest(),
        "raw_payload": source,
        "source_format": source_format,
    }
    return out


def read_records(path: Path) -> tuple[list[dict[str, Any]], str]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle)), "csv"
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError(f"line {line_no}: expected a JSON object")
                rows.append(item)
        return rows, "jsonl"
    raise ValueError("input must be .csv, .jsonl, or .ndjson")


def normalize_file(input_path: Path, mapping_path: Path, output_path: Path) -> dict[str, Any]:
    source = input_path.resolve(strict=True)
    mapping_file = mapping_path.resolve(strict=True)
    destination = output_path.absolute()
    if not source.is_file() or not mapping_file.is_file():
        raise ValueError("input and mapping must be regular files")
    if destination.exists():
        raise ValueError("output already exists; refusing overwrite")
    if destination.is_symlink():
        raise ValueError("output symlinks are not allowed")
    if source == destination or mapping_file == destination:
        raise ValueError("output must be a distinct file")
    mapping = json.loads(mapping_file.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        raise ValueError("mapping JSON must be an object")
    records, source_format = read_records(source)
    normalized = [normalize_record(row, mapping, source_format=source_format) for row in records]
    # Preserve source order and reject duplicate canonical observation identities.
    seen: set[tuple[str, ...]] = set()
    for index, record in enumerate(normalized, 1):
        key = tuple(record[k] for k in (
            "provider", "venue", "instrument_id", "timeframe", "event_time", "price_basis"
        ))
        if key in seen:
            raise ValueError(f"record {index}: duplicate canonical observation identity")
        seen.add(key)
    if not destination.parent.is_dir():
        raise ValueError("output parent directory must already exist")
    payload = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in normalized)
    # Exclusive create prevents a race from overwriting a file created after the check.
    with destination.open("x", encoding="utf-8", newline="") as handle:
        handle.write(payload)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {"status": "passed", "records_written": len(normalized), "output_sha256": digest,
            "output": str(destination), "read_only_source": True, "normalization_version": "1.0.0"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize one explicitly mapped source file to canonical OHLCV JSONL")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path, help="JSON mapping from canonical field names to source column names")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(normalize_file(args.input, args.mapping, args.output), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
