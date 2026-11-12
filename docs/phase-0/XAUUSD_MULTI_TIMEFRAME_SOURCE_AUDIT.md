# XAUUSD Six-Timeframe Source Audit

## Summary

The uploaded `XAUUSD.zip` contains six tab-delimited OHLC exports covering the calendar period 2020-11-11 through 2026-11-10 (six years), with 681,227 rows total.

| Timeframe | Rows | First source timestamp | Last source timestamp |
|---|---:|---|---|
| M5 | 422,274 | 2020-11-11 01:05 | 2026-11-10 23:50 |
| M15 | 141,767 | 2020-11-11 01:00 | 2026-11-10 23:45 |
| M30 | 70,896 | 2020-11-11 01:00 | 2026-11-10 23:30 |
| H1 | 35,464 | 2020-11-11 01:00 | 2026-11-10 23:00 |
| H4 | 9,278 | 2020-11-11 00:00 | 2026-11-10 20:00 |
| D1 | 1,548 | 2020-11-11 00:00 | 2026-11-10 00:00 |
| **Total** | **681,227** | | |

## Read-only checks performed

- All six files were parsed as tab-delimited text with the displayed OHLC headers.
- Source timestamps are strictly increasing within each file.
- No duplicate timestamps were found within any individual timeframe file.
- No OHLC invariant violations were found in the checked rows.
- Tick volume is present and non-zero in all rows.
- The `VOL` field is zero in every row of all six files.
- The `SPREAD` field is present, but its unit and exact meaning are not established.

These are structural checks only; they do not prove market-data correctness or that every expected trading interval is present. Multi-day gaps can include market closures and must be assessed against the actual trading calendar.

## Critical unresolved metadata

The CSVs do not establish:
- which broker/provider exported them;
- the timezone of the naive date/time fields;
- whether timestamps denote bar-open or bar-close time;
- whether prices are bid, ask, mid, last, or another basis;
- the unit/meaning of spread and tick volume.

The repository's canonical contract requires explicit timezone-aware timestamps. Therefore no UTC conversion, canonical normalized OHLCV release, or cross-timeframe point-in-time join has been produced yet. Guessing these values could shift candles, misalign timeframes, and create leakage.

## Integrity

- Uploaded archive SHA-256: `7458e5329bc827ff77aa9ec68d4be504451206226a74fd2cfa21f9e7f5516aa6`
- Archive size: 11,199,961 bytes.
- Per-file SHA-256 and row counts are recorded in `dataset/market_data/xauusd_source_manifest.json`.
- The raw archive itself is not committed to this repository; it remains the user's original upload.

## Next data gate

Before canonical normalization and generation of market-derived training samples, confirm:
1. Which broker/platform generated this export?
2. Which timezone do the CSV timestamps use (for example, MT5 server time / UTC offset, including whether DST changes apply)?
3. Does each row timestamp mark the candle's opening time or closing time?
4. Are OHLC values bid, ask, mid, or another quote basis?

Do not train on or publish derived directional labels until the temporal and price semantics are established.
