# 2datas — Broker-independent XAUUSD research dataset

An independent, auditable research dataset project. This repository does not modify or depend on the separate `datas` repository or AURORA QUANT.

## Current implementation

- MT5-style tab/comma/semicolon CSV ingestion with conservative header aliases and symbol/timeframe inference from filenames.
- Structural OHLC, timestamp, duplicate, volume and spread checks.
- Deterministic compressed partitions with source hashes and row-level lineage.
- Broker profile contract with explicit timezone/DST handling. Unknown or ambiguous times are never silently shifted.
- Cross-timeframe OHLC/tick-volume consistency audit.
- Initial causal price-action event engine: ATR, confirmed swings, BOS/CHoCH, FVG lifecycle, equal-high/low liquidity candidates, wick sweeps, order-block mitigation/invalidation, displacement, relative volatility and material open/close discontinuities.
- Point-in-time multi-timeframe snapshots that join only completed events available at or before each decision timestamp.
- Pytest and GitHub Actions workflow.

The initial feature definitions are operational hypotheses. Order blocks are not proof of institutional orders; OHLC sweeps are not evidence of actual resting orders; session-gap classification needs verified broker calendar/time semantics.

## Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[test]"
pytest -q
```

## Commands

```bash
2datas audit path/to/export.zip --output reports/source_audit.json
2datas normalize path/to/export.zip --output-dir data/processed
2datas alignment path/to/export.zip --output reports/timeframe_alignment.json
2datas features path/to/export.zip --output-dir data/features/price_action
2datas mtf data/features/price_action --output-dir data/features/mtf --decision-timeframes M5,M15,M30,H1,H4
```

The parser supports MT5 timeframe tokens such as M1/M5/M15/M30, H1/H4, D1, W1 and MN1, provided the filename identifies the timeframe unambiguously. Symbol aliases such as XAUUSD, GOLD or broker-suffixed names are preserved as source instrument identifiers.

## Broker clock configuration

Broker clock metadata is source-specific. The preferred automatic path is a sidecar next to each export. Create `XAUUSD.zip.broker.json` (or `XAUUSD.broker.json`) using the schema in [examples/alpari-mt5.broker.example.json](examples/alpari-mt5.broker.example.json), then run:

```bash
2datas normalize XAUUSD.zip --output-dir data/processed/alpari
2datas features XAUUSD.zip --output-dir data/features/price_action
```

The CLI auto-discovers the sidecar, validates its schema, records its SHA-256 in each manifest and applies the configured server timezone plus interval-start/interval-end convention. A generic sidecar needs only `server_timezone` and `bar_timestamp_convention`; `broker_name` and `server_name` are optional descriptive metadata. No account number, account owner or Demo/Real account type is required. For Alpari, `Europe/Helsinki` is a candidate seasonal clock based on the documented GMT+2/GMT+3 schedule, but it must pass historical export validation before being treated as verified. Other brokers use their documented IANA timezone or fixed UTC offset and timestamp convention.

A broker brand alone is not enough to infer a server clock. Account type and account identity are irrelevant to dataset ingestion. If no sidecar or explicit configuration is available, timestamps remain unresolved. Conflicting sidecars or simultaneous sidecar/CLI settings fail closed. Multiple servers and historical DST policies may differ even within one broker. Ambiguous/nonexistent DST wall times are quarantined rather than guessed. See [BROKER_TIME_NORMALIZATION.md](docs/BROKER_TIME_NORMALIZATION.md).

## Quality and epistemic boundaries

- Raw source timestamps and original source files/hashes remain traceable.
- UTC is populated only when timezone and interval-start/interval-end convention are explicitly configured.
- No missing bars are fabricated.
- Tick volume is not relabeled as exchange traded volume.
- Broker spread points are not converted to price without symbol point-size metadata.
- Price-action features are available only at the bar close/confirmation time; future-confirmed pivots are not backdated into earlier snapshots. The newest potentially incomplete candle is excluded by default.
- FVG, OB, liquidity pools and sweeps are versioned candidate definitions, not universal truths.
- No model training, live trading or broker order placement is implemented.

## Next milestones

1. Confirm the exact Alpari MT5 server and validate its historical clock/DST, symbol specification and session calendar.
2. Validate automatic broker sidecars against Alpari and at least two other broker/server clock configurations; add effective-dated profiles for historical clock changes.
3. Run the unit suite and validate MTF boundary, DST, freshness, lineage and no-future guarantees in a real Python environment.
4. Run an explicitly approved small sample, then assess feature redundancy, annotation agreement, temporal stability and chronological ablation.
5. Freeze compact market-outcome targets, ambiguity/censoring and episode-aware chronological splits.
6. Only after approval, materialize candidate datasets and perform independent QC and baseline evaluation.

No feature is admitted to the training dataset merely because it has been implemented.
