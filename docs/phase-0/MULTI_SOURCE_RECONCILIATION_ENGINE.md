# Multi-Source OHLCV Reconciliation Engine

## Purpose and authority

This is an offline diagnostic engine for comparing canonical OHLCV records from explicitly supplied files. It measures cross-source agreement and timing differences. It does **not** decide which provider is correct, create a preferred feed, merge records, or authorize source admission, release, or training.

This engine is distinct from the repository's canonical-field semantic reconciliation register: that register resolves schema/field ownership; this tool compares observations emitted by separate data sources.

No real market data is authorized or used. Tests use synthetic fixtures only. Stage 5 and AURORA QUANT remain outside scope.

## Observation identity

Records are grouped by the exact tuple:

- `instrument_id`
- `timeframe`
- `event_time`
- `price_basis`

Provider and venue are deliberately excluded from the grouping identity so different feeds can be compared. They remain part of each source identity and report. Different price bases are never compared as if they were equivalent. Symbol text is not used as instrument identity.

A group with fewer than two distinct providers is `insufficient_sources`. More than one record from the same provider for the same identity is `ambiguous_duplicate_source`; it is not silently collapsed.

## Comparison policy

The CLI requires an explicit absolute price tolerance. For every provider pair, it calculates exact Decimal absolute differences for open/high/low/close. A pair is within tolerance only when the maximum of the four differences is less than or equal to the declared threshold. Otherwise it is divergent.

This is an absolute tolerance, not a pip conversion, percentage, volatility adjustment, or universal FX threshold. It is user-supplied per run and must be chosen for the instrument's declared price scale and intended use. No threshold is silently recommended by the tool.

Volume is compared only when both values exist and their units are explicitly present and identical. The engine does not convert lots, contracts, base units, quote units, tick counts, or traded volume. Missing or mismatched units produce `unit_mismatch_or_missing`; absent volume produces `not_comparable`.

The report also records the absolute `available_at` difference in seconds. It does not infer provider latency, event timestamp accuracy, or which source arrived first in a causal sense beyond the supplied timestamps.

## Statuses and provider statistics

Observation statuses:
- `all_within_tolerance`: every pair passed the declared OHLC threshold.
- `divergent`: at least one pair exceeded the threshold.
- `insufficient_sources`: fewer than two providers were supplied for the identity.
- `ambiguous_duplicate_source`: a provider has multiple rows for the same identity.
- `unresolved`: reserved for a comparison state not classifiable by current rules.

Provider statistics count appearances and pair outcomes. They are descriptive counts only, **not a provider quality score or ranking**. Sample size, coverage, licensing, point-in-time correctness, instrument specification, feed independence, and source integrity are not inferred.

## Determinism and safety

- Inputs are explicit repeated `--input` paths; there is no directory scan or network access.
- Inputs are read-only. The report path must be new; exclusive creation prevents overwriting.
- Records are grouped and sorted deterministically; source pairs are deterministic.
- Decimal arithmetic is used; no binary float is used for prices, tolerances, volume, or price deltas.
- No source is selected, averaged, spliced, corrected, resampled, or deleted.
- A divergent group remains divergent; downstream code must not treat a report as a reconciled/approved dataset.
- Malformed records fail closed. Canonical records must contain the identity, source, price and availability fields required by the comparison.

## CLI

```bash
python tools/source_reconciliation.py \
  --input feed_a.canonical.jsonl \
  --input feed_b.canonical.jsonl \
  --absolute-price-tolerance 0.0001 \
  --report reports/source-reconciliation.json
```

The output is a JSON report containing policy, group counts, provider appearance/pair counts, each observation identity, source references, OHLC deltas, volume comparability and availability-time deltas. Exit code 0 means the report was produced, not that every source agreed. Exit code 2 means invalid input/configuration or an I/O failure.

## Required future gates

Before using this report for source admission or model data:
1. Establish source independence and licensing/rights separately.
2. Verify instrument identity mappings, venue/feed identifiers and contract specifications.
3. Establish source timestamp convention, bar interval boundaries, clock quality and availability-time evidence.
4. Define instrument-specific tolerance policy under version control and review; do not use one global threshold blindly.
5. Add independent source quality evidence and sufficient coverage/known outage windows.
6. Adjudicate divergences with documented evidence; preserve the decision and all original source artifacts.
7. Re-run artifact integrity, canonical quality, provenance and point-in-time leakage checks after any separately authorized transformation.

The engine is a comparison report generator only. It does not certify correctness, authenticity, completeness, causal usability, licensing, or suitability for training.
