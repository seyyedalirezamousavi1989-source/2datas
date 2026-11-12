# 2datas — XAUUSD Research Dataset

Independent research project for building a high-information, causal, reproducible XAUUSD dataset. This repository is separate from the unrelated `datas` repository and from AURORA QUANT application code.

## Current implementation

The first executable component is a non-destructive MT5-export ingestion and integrity-audit package. It reads tab-delimited CSV files from a ZIP archive, preserves original timestamps and source values, calculates source hashes, checks OHLC/timestamp integrity, and reports gaps and spread distributions.

It deliberately does **not** guess timezone, broker, bar timestamp convention, spread point size, session calendar, or real-volume semantics. It does not fill missing bars, synthesize ticks, create labels, or train a model.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[test]"
pytest
2datas audit path/to/XAUUSD.zip --output reports/source_audit.json
2datas normalize path/to/XAUUSD.zip --output-dir data/processed/xauusd
```

The normalizer writes one deterministic gzip CSV partition per timeframe and a manifest with source/output hashes and row-level source references. Generated data remains local and is not committed to Git.\n\nOr run without installation:

```bash
PYTHONPATH=src python -m twodatas audit path/to/XAUUSD.zip
```

## Source-data contract

- Input: MT5 tab-delimited CSV exports in a ZIP.
- Supported timeframes: M5, M15, M30, H1, H4 and Daily.
- Required source columns: date, OHLC, tick volume, real volume and spread.
- Original timestamp representation is retained; timezone and bar timestamp semantics remain explicitly unknown until verified with the provider/broker.
- Raw source archives and generated data/reports are excluded from Git by default.

## Next implementation milestones

1. Source provenance and broker/session convention resolution.
2. Canonical normalized storage with immutable source lineage.
3. Cross-timeframe synchronization using only information available at each decision cutoff.
4. Causal feature computation with feature registry and redundancy/ablation tests.
5. Outcome target generation, ambiguity/censoring rules and episode-aware temporal splits.
6. Dataset materialization, QC reports and baseline evaluation.

A milestone is not considered complete merely because code exists; tests and data-specific acceptance checks are required.
