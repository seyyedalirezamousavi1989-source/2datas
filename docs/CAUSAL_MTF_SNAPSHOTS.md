# Causal multi-timeframe snapshot contract

Version: 0.1.0

## Purpose

Build a point-in-time context for a decision candle using the latest completed feature event from each available timeframe. A snapshot is not a conventional resample: it is a causal join over feature availability timestamps.

## Selection rule

For a decision event at timestamp \(T\), select at most one event per timeframe:

\[
\operatorname{selected}(TF,T)=\arg\max_{e}\{e.available\_at\_utc \mid e.available\_at\_utc \le T\}
\]

- Equality is allowed: a higher-timeframe bar that closes exactly at the decision timestamp is available.
- An event with unresolved availability time is never selected.
- Each selected context includes its age in minutes and source file/hash/row lineage.
- The decision candle itself is included only after its close availability timestamp.
- The snapshot stores compact, persistent structure state, active FVG zones, active order-block zones, volatility state and recent price-action events.
- No forward fill from future bars, no interpolation and no synthetic candles.

## Supported timeframes and limitations

Intraday timeframes with resolved server-clock semantics can be joined automatically. D1/W1/MN1 need a verified trading-session/calendar close rule; they are excluded when the feature event has no resolved availability timestamp. This is intentional, not missing-data imputation.

All timeframes in one run must come from the same instrument and source-clock profile. Cross-broker joins are not allowed merely because timestamps look similar. Normalize each archive with its own verified broker sidecar, then compare or combine only after canonical UTC and instrument specifications are validated.

## Command

After generating features:

```bash
2datas mtf data/features/price_action --output-dir data/features/mtf --decision-timeframes M5,M15,M30,H1,H4
```

The output is one JSONL partition per instrument/decision timeframe plus a manifest containing the source feature-manifest hash, broker profile, selected timeframes, counts and admission status.

## Validation before training

Test boundary equality, no-future selection, missing higher-timeframe bars, DST transitions, gaps, stale context age, duplicate availability timestamps, mixed-source rejection and reproducibility. Then compare MTF snapshots with single-timeframe baselines and ablate each context timeframe. A timeframe is retained only if it adds stable out-of-sample value.
