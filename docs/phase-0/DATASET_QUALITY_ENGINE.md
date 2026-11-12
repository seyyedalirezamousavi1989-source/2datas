# Dataset Quality Audit Engine

## Safety and scope
Read-only audit of one explicitly selected CSV, JSONL, or NDJSON file. No market data is fetched, no directory is recursively scanned, and no source data is modified. Tests use synthetic fixtures only. No model training or release creation occurs.

## Contract and checks
Requires OHLC columns and an ISO-8601 timestamp with explicit timezone (default field: event_time). Duplicate identity defaults to instrument_id + timeframe + event_time and is configurable. Add source/feed, price basis, revision, and broker mapping when they distinguish observations. Optional volume must be finite and non-negative; its economic meaning is source-specific.

Checks required fields, finite OHLC values, high >= max(open, close), low <= min(open, close), high >= low, optional volume, timestamp validity/order per instrument-timeframe stream, configured duplicate keys, and observed coverage. Gap warnings require an explicitly supplied expected cadence. No session, holiday, or DST calendar is inferred, so a gap is not proof of missing market data.

## Split leakage
This first version does not infer episode/group membership. Existing split-manifest validation remains responsible for declared groups, clusters, interval overlap, purge, and embargo. This tool does not claim to prove absence of leakage.

## CLI
`python tools/dataset_quality.py --input path/to/bars.csv`

`python tools/dataset_quality.py --input path/to/bars.jsonl --expected-interval-seconds 60 --report reports/quality.json`

`python tools/dataset_quality.py --input path/to/bars.csv --key-fields instrument_id,timeframe,event_time,source_id,price_basis`

JSON status: passed, passed_with_warnings, or failed. Exit codes: 0 pass (warnings allowed), 1 quality failures, 2 fatal/configuration error. Report parent directory must exist.

## Limitations
No canonical physical OHLC schema is frozen here. No deduplication, sorting, interpolation, outlier removal, calendar inference, split assignment, or remediation. Structural checks cannot establish source authenticity, licensing, causal availability, semantic correctness, or training suitability.
