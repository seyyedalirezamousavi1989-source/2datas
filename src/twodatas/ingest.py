from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath
from typing import Iterator

TF_PATTERN = re.compile(r"(?:^|_)(Daily|MN\\d+|W\\d+|D1|H\\d+|M\\d+)(?=_|$)", re.IGNORECASE)
REQUIRED = {"<DATE>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"}


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


def _timeframe_from_name(name: str) -> str:
    match = TF_PATTERN.search(PurePosixPath(name).name)
    if not match:
        raise ValueError(f"Cannot infer supported timeframe from filename: {name}")
    value = match.group(1)
    return "D1" if value.lower() == "daily" else value.upper()


def _parse_float(value: str, field: str, source: str, line: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{source}:{line}: invalid numeric {field}={value!r}") from exc
    if result != result or result in (float("inf"), float("-inf")):
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


def read_mt5_csv(payload: bytes, source_file: str) -> FileIngestResult:
    """Read MT5 tab-delimited export without guessing timezone/bar timestamp semantics."""
    timeframe = _timeframe_from_name(source_file)
    text = payload.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=chr(9))
    header = list(reader.fieldnames or [])
    missing = REQUIRED.difference(header)
    if missing:
        raise ValueError(f"{source_file}: missing required columns: {sorted(missing)}")

    rows: list[Bar] = []
    for line, raw in enumerate(reader, start=2):
        stamp, precision = _timestamp(raw)
        values = {key: _parse_float(raw[key], key, source_file, line) for key in ("<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>")}
        tick_volume = values["<TICKVOL>"]
        if tick_volume < 0 or not tick_volume.is_integer():
            raise ValueError(f"{source_file}:{line}: TICKVOL must be a non-negative integer")
        rows.append(Bar(
            instrument=instrument, timeframe=timeframe, source_file=source_file,
            source_timestamp=stamp, timestamp_precision=precision,
            timestamp_timezone="UNKNOWN",
            open=values["<OPEN>"], high=values["<HIGH>"], low=values["<LOW>"], close=values["<CLOSE>"],
            tick_volume=int(tick_volume), real_volume=values["<VOL>"], spread_points=values["<SPREAD>"],
        ))
    return FileIngestResult(source_file, timeframe, hashlib.sha256(payload).hexdigest(), rows, header)


def read_zip(path: str, *, instrument: str | None = None, timeframe_overrides: dict[str, str] | None = None) -> Iterator[FileIngestResult]:
    with zipfile.ZipFile(path) as archive:
        members = sorted(n for n in archive.namelist() if n.lower().endswith(".csv"))
        if not members:
            raise ValueError("Archive contains no CSV files")
        for member in members:
            override = (timeframe_overrides or {}).get(member)\n            yield read_mt5_csv(archive.read(member), member, instrument=instrument, timeframe=override)
