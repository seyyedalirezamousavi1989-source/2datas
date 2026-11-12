# Temporal Integrity and Multi-Timeframe Alignment Engine

## Status and scope

Implemented as a deterministic, read-only metadata engine. It selects normalized bar references as-of explicit decision timestamps. It does not acquire, parse, normalize, aggregate, repair, interpolate, sort, or write market data. Tests use synthetic in-memory records only. It is not connected to a broker, provider, acquisition adapter, raw artifact store, dataset builder, or model trainer.

This implementation operationalizes a narrow subset of the existing provisional temporal contracts. It does not supersede `POINT_IN_TIME_INTERVAL_AND_SNAPSHOT_REVISION_CONTRACT.md` or `MULTI_TIMEFRAME_AND_MARKET_STRUCTURE.md`.

## Input contract

Each record must include unique `record_id`, `instrument_id`, `provider`, `price_basis`, `timeframe`, normalized `interval_start` and `interval_end`, `available_at`, `completion_status` (`COMPLETE` or `PARTIAL`), and `source_revision_id`.

All timestamps must include an explicit timezone and are compared as UTC instants. Intervals are half-open. The implementation currently supports fixed-duration m/h/d/w intervals only and verifies the declared interval duration. Session-aware daily/weekly bars, holidays and DST-dependent boundaries require a separately verified calendar adapter and are deliberately rejected rather than guessed.

A COMPLETE bar is eligible only when both `interval_end <= decision_timestamp` and `available_at <= decision_timestamp`. A PARTIAL bar never replaces a completed bar; it is returned separately only when explicitly enabled and the decision cutoff lies inside the interval.

## Selection and fail-closed behavior

Selections remain partitioned by instrument, provider and timeframe. Price basis is reported and incompatible sources are not collapsed. The latest eligible completed bar is selected per partition. Missing and stale inputs are explicit. Duplicate intervals within a partition are marked ambiguous and withheld. Input-order regressions are reported; input records are not sorted or mutated. Late arrivals remain unavailable at earlier cutoffs.

A SHA-256 fingerprint is computed over each deterministic decision snapshot's canonical JSON representation. It identifies the report content, not its correctness.

## Known limitations

- The engine validates fixed elapsed durations, not exchange/broker session calendars.
- It does not reconcile source revisions or decide which revision is authoritative.
- It does not infer source latency or historical availability; `available_at` must already be defensible.
- It reports out-of-order input but does not repair it.
- It does not create higher-timeframe bars from lower-timeframe bars.
- It does not compute technical indicators, market structure, order blocks, liquidity, FVGs, forecasts, probabilities or trade signals.
- It does not authorize training or real-data processing.

## Running tests

```bash
python -m unittest tests.test_temporal_alignment -v
python -m unittest discover -s tests -v
```

## Promotion gates

Before any live source integration, separately verify source timestamp semantics, interval construction, completion and availability evidence, revision history, and session/calendar behavior. A future adapter must preserve raw source timestamps and must not manufacture historical availability. DST transitions must be tested against the actual source calendar; fixed UTC durations are not a substitute for session-aware bars.
