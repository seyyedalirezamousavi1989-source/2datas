from __future__ import annotations

import csv
import hashlib
import io
import math
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Iterator

TF_PATTERN = re.compile(
    r"(?P<symbol>[A-Za-z0-9.]+)_(?P<timeframe>Daily|MN\d+|W\d+|D1|H\d+|M\d+)(?=_|$)",
    re.IGNORECASE,
)
REQUIRED = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE", "TICKVOL", "VOL", "SPREAD"}
HEADER_ALIASES = {
    "DATE": {"DATE", "<DATE>"},
    "TIME": {"TIME", "<TIME>"},
    "OPEN": {"OPEN", "<OPEN>"},
    "HIGH": {"HIGH", "<HIGH>"},
    "LOW": {"LOW", "<LOW>"},
    "CLOSE": {"CLOSE", "<CLOSE>"},
    "TICKVOL": {"TICKVOL", "<TICKVOL>", "TICK_VOLUME", "TICK VOLUME"},
    "VOL": {"VOL", "<VOL>", "REAL_VOLUME", "REAL VOLUME"},
    "SPREAD": {"SPREAD", "<SPREAD>", "SPREAD_POINTS", "SPREAD POINTS"},
}


def _detect_delimiter(text: str) -> str:
    first = next((line for line in text.splitlines() if line.strip()), "")
    counts = {delimiter: first.count(delimiter) for delimiter in ("\\t", ",", ";")}
    delimiter = max(counts, key=counts.get)
    if counts[delimiter] == 0:
        raise ValueError("Could not detect CSV delimiter (expected tab, comma or semicolon)")
    return delimiter


def _canonicalize_header(header: list[str], source: str) -> tuple[list[str], dict[str, str]]:
    actual_by_canonical: dict[str, str] = {}
    for actual in header:
        normalized = (actual or "").strip().upper().replace(" ", "_")
        for canonical, aliases in HEADER_ALIASES.items():
            normalized_aliases = {alias.upper().replace(" ", "_") for alias in aliases}
            if normalized in normalized_aliases:
                if canonical in actual_by_canonical:
                    raise ValueError(f"{source}: duplicate columns map to {canonical}")
                actual_by_canonical[canonical] = actual
                break
    missing = REQUIRED.difference(actual_by_canonical)
    if missing:
        raise ValueError(f"{source}: missing required columns after header normalization: {sorted(missing)}")
    return list(actual_by_canonical), actual_by_canonical


@dataclass(frozen=True)
class Bar:
    instrument: str
    timeframe: str
    source_file: str
    source_timestamp: str
    timestamp_precision: str
    timestamp_timezone: str
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    real_volume: float
    spread_points: float


@dataclass
class FileIngestResult:
    source_file: str
    timeframe: str
    source_sha256: str
    rows: list[Bar]
    header: list[str]


def _parse_float(value: str, field: str, source: str, line: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{source}:{line}: invalid numeric {field}={value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"{source}:{line}: non-finite {field}")
    return result


def _timestamp(row: dict[str, str]) -> tuple[str, str]:
    date = (row.get("<DATE>") or "").strip()
    time = (row.get("<TIME>") or "").strip()
    if time:
        datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S")
        return f"{date} {time}", "second"
    datetime.strptime(date, "%Y.%m.%d")
    return date, "day"


def read_mt5_csv(
    payload: bytes,
    source_file: str,
    *,
    instrument: str | None = None,
    timeframe: str | None = None,
) -> FileIngestResult:
    """Read MT5-style market-bar CSV exports with tab/comma/semicolon delimiters.\n\n    Header aliases are normalized conservatively; volume fields retain their source\n    semantics and broker clock rules are never inferred from the file values.\n    """
    stem = PurePosixPath(source_file).stem
    match = TF_PATTERN.search(stem)
    if timeframe is None and match is None:
        raise ValueError(f"Cannot infer timeframe from filename; provide an override: {source_file}")
    inferred_timeframe = timeframe or (match.group("timeframe") if match else None)
    normalized_timeframe = "D1" if inferred_timeframe.lower() == "daily" else inferred_timeframe.upper()
    inferred_instrument = match.group("symbol").upper() if match else None
    normalized_instrument = (instrument or inferred_instrument or "").upper()
    if not normalized_instrument:
        raise ValueError(f"Cannot infer instrument from filename; provide an explicit instrument: {source_file}")

    text = payload.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    header = list(reader.fieldnames or [])
    missing = REQUIRED.difference(header)
    if missing:
        raise ValueError(f"{source_file}: missing required columns: {sorted(missing)}")

    rows: list[Bar] = []
    for line, raw in enumerate(reader, start=2):
        stamp, precision = _timestamp(raw)
        values = {
            key: _parse_float(raw[key], key, source_file, line)
            for key in ("<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>")
        }
        tick_volume = values["<TICKVOL>"]
        if tick_volume < 0 or not tick_volume.is_integer():
            raise ValueError(f"{source_file}:{line}: TICKVOL must be a non-negative integer")
        rows.append(Bar(
            instrument=normalized_instrument,
            timeframe=normalized_timeframe,
            source_file=source_file,
            source_timestamp=stamp,
            timestamp_precision=precision,
            timestamp_timezone="UNKNOWN",
            open=values["<OPEN>"],
            high=values["<HIGH>"],
            low=values["<LOW>"],
            close=values["<CLOSE>"],
            tick_volume=int(tick_volume),
            real_volume=values["<VOL>"],
            spread_points=values["<SPREAD>"],
        ))
    return FileIngestResult(
        source_file, normalized_timeframe, hashlib.sha256(payload).hexdigest(), rows, header
    )


def read_zip(
    path: str,
    *,
    instrument: str | None = None,
    timeframe_overrides: dict[str, str] | None = None,
) -> Iterator[FileIngestResult]:
    with zipfile.ZipFile(path) as archive:
        members = sorted(name for name in archive.namelist() if name.lower().endswith(".csv"))
        if not members:
            raise ValueError("Archive contains no CSV files")
        for member in members:
            override = (timeframe_overrides or {}).get(member)
            yield read_mt5_csv(
                archive.read(member), member, instrument=instrument, timeframe=override
            )
