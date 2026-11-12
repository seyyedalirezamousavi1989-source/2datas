from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
from datetime import datetime

from .broker_profiles import resolve_profile_for_archive, to_utc
from .ingest import read_zip
from .quality import audit_file
from .instrument_specs import validate_instrument_specs, audit_instrument_specs, spec_values_for_bar

SCHEMA_VERSION = "market-bars-0.4.0"
FIELDS = [
    "schema_version", "instrument", "source_instrument", "timeframe", "source_file", "source_sha256",
    "source_row_number", "source_timestamp", "timestamp_precision", "timestamp_timezone",
    "timestamp_utc", "timestamp_resolution_status", "broker_profile_id", "broker_name", "server_name",
    "server_timezone", "bar_timestamp_convention",
    "instrument_spec_status", "instrument_spec_id", "instrument_spec_effective_from",
    "instrument_spec_effective_to", "instrument_digits", "point_size", "tick_size",
    "contract_size", "price_currency", "profit_currency", "spread_unit", "spread_raw",
    "spread_points", "spread_price", "volume_semantics", "tick_value", "tick_value_currency",
    "open", "high", "low", "close", "tick_volume", "real_volume",
]

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_archive(
    archive_path: str,
    output_dir: str,
    *,
    broker_config_path: str | None = None,
    broker_profile_id: str | None = None,
    broker_name: str | None = None,
    server_name: str | None = None,
    server_timezone: str | None = None,
    bar_timestamp_convention: str | None = None,
) -> dict:
    """Write deterministic partitions; UTC is emitted only with explicit time semantics."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    partitions = []
    source_symbols: set[str] = set()
    source_periods: dict[str, tuple[str, str]] = {}
    specs = validate_instrument_specs(broker_config.get("instrument_specs", {}))
    profile, broker_config = resolve_profile_for_archive(
        archive_path, config_path=broker_config_path, profile_id=broker_profile_id,
        broker_name=broker_name, server_name=server_name, server_timezone=server_timezone,
        bar_timestamp_convention=bar_timestamp_convention,
    )

    for result in read_zip(archive_path, symbol_aliases=broker_config.get("symbol_aliases", {})):
        for row in result.rows:
            symbol = row.source_instrument
            source_symbols.add(symbol)
            source_date = datetime.strptime(row.source_timestamp.split()[0], "%Y.%m.%d").date().isoformat()
            if symbol not in source_periods:
                source_periods[symbol] = (source_date, source_date)
            else:
                first, last = source_periods[symbol]
                source_periods[symbol] = (min(first, source_date), max(last, source_date))
        audit = audit_file(result)
        instrument = result.rows[0].instrument if result.rows else "UNKNOWN"
        target_dir = root / f"instrument={instrument}" / f"timeframe={result.timeframe}"
        target_dir.mkdir(parents=True, exist_ok=True)
        source_key = hashlib.sha256((result.source_file + result.source_sha256).encode("utf-8")).hexdigest()[:12]
        target = target_dir / f"bars-{source_key}.csv.gz"

        spec_status_counts: dict[str, int] = {}
        with target.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                import io
                text = io.TextIOWrapper(compressed, encoding="utf-8", newline="")
                writer = csv.DictWriter(text, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                for row_number, bar in enumerate(result.rows, start=2):
                    timestamp_utc, timestamp_status = to_utc(
                        bar.source_timestamp, bar.timestamp_precision, profile
                    )
                    spec_fields = spec_values_for_bar(\n                        specs, bar.source_instrument, bar.source_timestamp, bar.spread_points\n                    )\n                    spec_status_counts[spec_fields["instrument_spec_status"]] = spec_status_counts.get(spec_fields["instrument_spec_status"], 0) + 1\n                    writer.writerow({
                        "schema_version": SCHEMA_VERSION,
                        "instrument": bar.instrument,
                        "source_instrument": bar.source_instrument,
                        "timeframe": bar.timeframe,
                        "source_file": bar.source_file,
                        "source_sha256": result.source_sha256,
                        "source_row_number": row_number,
                        "source_timestamp": bar.source_timestamp,
                        "timestamp_precision": bar.timestamp_precision,
                        "timestamp_timezone": profile.server_timezone if timestamp_utc else "UNKNOWN",
                        "timestamp_utc": timestamp_utc or "",
                        "timestamp_resolution_status": timestamp_status,
                        "broker_profile_id": profile.profile_id,
                        "broker_name": profile.broker_name,
                        "server_name": profile.server_name or "",
                        "server_timezone": profile.server_timezone or "",
                        "bar_timestamp_convention": profile.bar_timestamp_convention or "",
                        "open": repr(bar.open),
                        "high": repr(bar.high),
                        "low": repr(bar.low),
                        "close": repr(bar.close),
                        "tick_volume": bar.tick_volume,
                        "real_volume": repr(bar.real_volume),
                        **spec_fields,
                    })
                text.flush()
                text.detach()

        partitions.append({
            "instrument": instrument,
            "timeframe": result.timeframe,
            "path": target.relative_to(root).as_posix(),
            "row_count": len(result.rows),
            "source_file": result.source_file,
            "source_sha256": result.source_sha256,
            "normalized_sha256": _sha256(target),
            "quality_status": audit["quality_status"],
            "admission_status": audit["admission_status"],
            "instrument_spec_status_counts": dict(sorted(spec_status_counts.items())),
            "timezone": profile.server_timezone or "UNKNOWN",
            "bar_timestamp_semantics": profile.bar_timestamp_convention or "UNKNOWN",
        })

    instruments = sorted({p["instrument"] for p in partitions})
    specs = validate_instrument_specs(broker_config.get("instrument_specs", {}))
    specification_audit = audit_instrument_specs(specs, source_symbols=source_symbols, observed_periods=source_periods)
    manifest = {
        "dataset": instruments[0] if len(instruments) == 1 else "multi-instrument",
        "instruments": instruments,
        "schema_version": SCHEMA_VERSION,
        "normalizer_version": "0.4.0",
        "source_archive_sha256": _sha256(Path(archive_path)),
        "broker_config": broker_config,
        "instrument_specification_audit": specification_audit,
        "broker_profile": {
            "profile_id": profile.profile_id,
            "broker_name": profile.broker_name,
            "server_name": profile.server_name,
            "server_timezone": profile.server_timezone,
            "bar_timestamp_convention": profile.bar_timestamp_convention,
            "status": profile.status,
            "evidence": profile.evidence,
        },
        "timestamp_policy": (
            "Preserve raw source timestamp. UTC is populated only when both timezone and "
            "bar timestamp convention are explicitly configured; ambiguous/nonexistent DST "
            "wall times remain unresolved."
        ),
        "partitions": partitions,
        "total_rows": sum(p["row_count"] for p in partitions),
        "limitations": [
            "No missing intervals were imputed.",
            "No features, labels, synthetic samples or trading decisions were generated by normalization.",
            "Instrument specifications are attached only when an exact source-symbol and source-local effective-date match exists.",
            "spread_price is derived only when the broker-declared spread unit is points or price; unknown units remain unresolved.",
            "Broker profile status is not proof of provider documentation or licensing.",
            "Source row references and archive/file hashes preserve traceability.",
        ],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest
