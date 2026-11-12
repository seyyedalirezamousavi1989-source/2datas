# Causal Market Feature Engineering (Synthetic Foundation)

## Scope

This increment adds deterministic, offline feature extraction from already-normalized, ordered OHLC bars. It does not ingest data, build training examples, generate predictions, assign outcome labels, or issue trade signals. Tests use synthetic fixtures only.

## Features

- Swing highs/lows: strict unique extrema with configurable left/right bars. A pivot is published only after all right-side confirmation bars have closed and become available.
- BOS/CHoCH: close-based breaks of previously confirmed swing levels. A pivot cannot be used before confirmation; each level is broken at most once.
- Liquidity sweeps: wick-through and close-back conditions against confirmed swing levels.
- Three-candle FVG: bullish and bearish gaps emitted only at the third candle close/availability.
- True Range and simple rolling ATR with explicit warm-up.

Every event carries event time and availability time and is marked causal. Inputs must be chronological; duplicate or out-of-order bars fail closed. Bars not completed and available by the decision cutoff are excluded. No sorting, filling, interpolation, mutation or source selection occurs.

## Definition limits

These are explicit initial operational definitions, not universal market truths. Swing ties are ignored. BOS/CHoCH uses candle close crossing the last confirmed swing. A sweep requires wick beyond a confirmed level and close back inside. FVG uses a strict three-candle non-overlap gap. Definitions must be versioned and evaluated before supervised labels are generated.

Order Blocks are deliberately deferred: displacement threshold, candle selection, mitigation, invalidation, and timeframe context need explicit definitions before becoming training labels. No probability or trade recommendation is produced.

## Causality and safety

Bars are admitted only when interval_end and available_at are no later than the decision cutoff. Right-side pivot confirmation is causal because pivot event time differs from later availability. ATR is trailing. Fingerprints identify report content, not predictive value.

## Limitations

No broker calendar/DST reconstruction, resampling, cross-timeframe join, source-revision reconciliation, order blocks, premium/discount, forecasts, probabilities, entries/stops/targets, or trade signals. Not authorized for live market data or model training.

## Tests

`python -m unittest tests.test_market_features -v`
`python -m unittest discover -s tests -v`
