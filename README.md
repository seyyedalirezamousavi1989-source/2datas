# 2datas — Broker-independent XAUUSD research dataset

An independent, auditable research dataset project. This repository does not modify or depend on the separate `datas` repository or AURORA QUANT.

## Current implementation

- MT5 tab-delimited ZIP ingestion with symbol/timeframe inference from filenames.
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
2datas mtf data/features/price_action --output-dir data/features/mtf --decision-timeframes M1,M5,M15,M30,H1,H4
```

The parser supports MT5 timeframe tokens such as M1/M5/M15/M30, H1/H4, D1, W1 and MN1, provided the filename identifies the timeframe unambiguously. Symbol aliases such as XAUUSD, GOLD or broker-suffixed names are preserved as source instrument identifiers.

## Broker clock configuration

Broker clock metadata is source-specific. The preferred automatic path is a sidecar next to each export. Create `XAUUSD.zip.broker.json` (or `XAUUSD.broker.json`) using the schema in [examples/alpari-mt5.broker.example.json](examples/alpari-mt5.broker.example.json), then run:

```bash
2datas normalize XAUUSD.zip --output-dir data/processed/alpari
2datas features XAUUSD.zip --output-dir data/features/price_action
```

The CLI auto-discovers the sidecar, validates its schema, records its SHA-256 in each manifest and applies the configured server timezone plus interval-start/interval-end convention. For the documented Alpari profile, `Alpari-MT5` and `Alpari-MT5-Demo` are recognized by the built-in profile when supplied as `--broker-profile alpari_mt5_candidate --server-name ...`; confirm your exact MT5 server before relying on it. For other brokers, create a sidecar containing the exact server, IANA timezone (or documented fixed offset such as `UTC+02:00`) and timestamp convention.

A broker brand alone is not enough to infer a server clock. If no sidecar or explicit configuration is available, timestamps remain unresolved. Conflicting sidecars or simultaneous sidecar/CLI settings fail closed. Multiple servers and historical DST policies may differ even within one broker. Ambiguous/nonexistent DST wall times are quarantined rather than guessed. See [BROKER_TIME_NORMALIZATION.md](docs/BROKER_TIME_NORMALIZATION.md).

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

1. Verify Alpari server clock, DST, timestamp convention, symbol specification and session calendar.
2. Add broker/server profile versioning and source metadata capture for additional providers.
3. Build causal multi-timeframe snapshots from resolved UTC intervals.
4. Validate and prune price-action features using redundancy, stability and chronological ablation.
5. Specify compact market-outcome targets, ambiguity/censoring and episode-aware splits.
6. Materialize high-quality task datasets and perform independent QC/baseline evaluation.

No feature is admitted to the training dataset merely because it has been implemented.
