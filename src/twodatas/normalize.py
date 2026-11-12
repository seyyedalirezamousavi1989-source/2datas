from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .ingest import read_zip
from .quality import audit_file

SCHEMA_VERSION = "market-bars-0.2.0"
FIELDS = [
    "schema_version", "instrument", "timeframe", "source_file", "source_sha256",
    "source_row_number", "source_timestamp", "timestamp_precision", "timestamp_timezone",
    "open", "high", "low", "close", "tick_volume", "real_volume", "spread_points",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_archive(archive_path: str, output_dir: str) -> dict:
    """Materialize deterministic gzip CSV partitions while preserving source time semantics."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    partitions = []

    for result in read_zip(archive_path):
        audit = audit_file(result)
        instrument = result.rows[0].instrument if result.rows else "UNKNOWN"
        target_dir = root / f"instrument={instrument}" / f"timeframe={result.timeframe}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "bars.csv.gz"
        with target.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                import io
                text = io.TextIOWrapper(compressed, encoding="utf-8", newline="")
                writer = csv.DictWriter(text, fieldnames=FIELDS, lineterminator="
")
                writer.writeheader()
                for row_number, bar in enumerate(result.rows, start=2):
                    writer.writerow({
                        "schema_version": SCHEMA_VERSION,
                        "instrument": bar.instrument,
                        "timeframe": bar.timeframe,
                        "source_file": bar.source_file,
                        "source_sha256": result.source_sha256,
                        "source_row_number": row_number,
                        "source_timestamp": bar.source_timestamp,
                        "timestamp_precision": bar.timestamp_precision,
                        "timestamp_timezone": bar.timestamp_timezone,
                        "open": repr(bar.open),
                        "high": repr(bar.high),
                        "low": repr(bar.low),
                        "close": repr(bar.close),
                        "tick_volume": bar.tick_volume,
                        "real_volume": repr(bar.real_volume),
                        "spread_points": repr(bar.spread_points),
                    })
                text.flush()
                text.detach()
        partitions.append({
            "timeframe": result.timeframe,
            "path": target.relative_to(root).as_posix(),
            "row_count": len(result.rows),
            "source_file": result.source_file,
            "source_sha256": result.source_sha256,
            "normalized_sha256": _sha256(target),
            "quality_status": audit["quality_status"],
            "admission_status": audit["admission_status"],
            "timezone": "UNKNOWN",
            "bar_timestamp_semantics": "UNKNOWN",
        })

    manifest = {
        "dataset": "multi-instrument",
        "instruments": sorted({p["path"].split("/")[0].split("=", 1)[-1] for p in partitions}),
        "schema_version": SCHEMA_VERSION,
        "normalizer_version": "0.1.0",
        "source_archive_sha256": _sha256(Path(archive_path)),
        "timestamp_policy": "Preserve source timestamp verbatim; do not infer timezone or open/close convention.",
        "partitions": partitions,
        "total_rows": sum(p["row_count"] for p in partitions),
        "limitations": [
            "No timezone conversion or timestamp shifting was applied.",
            "No missing intervals were imputed.",
            "No features, labels, synthetic samples or trading decisions were generated.",
            "Numeric source fields are parsed and serialized as canonical decimal text; original archive hash and source row references preserve traceability.",
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "
", encoding="utf-8")
    return manifest
