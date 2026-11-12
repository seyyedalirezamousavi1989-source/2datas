# Causal price-action feature contract

Version: 0.1.0

This is a compact initial feature implementation, not a claim that SMC terminology is objectively standardized. The newest input candle is excluded by default because it may still be forming; inclusion requires the explicit `--include-last-bar` override and evidence that the bar is complete. Every concept is an operational hypothesis with explicit parameters and a named consumer. Definitions must be tested for stability, annotation agreement and incremental value before model admission.

## Implemented candidate events

- True range and rolling ATR (simple rolling mean; initial warm-up is null).
- Displacement candidate: body at least 1.5 ATR and body/range at least 0.65.
- Relative volatility candidate: current ATR versus median of up to 100 prior ATR values after a 20-value warm-up; expansion at 1.5x and contraction at 0.67x.
- Candle body, body/range, close location, one-bar return and range/body normalized by ATR.
- Confirmed swing highs/lows: a pivot is emitted only after the configured right-side bars have closed; event availability is the confirmation bar, not the pivot origin. Exact UTC availability is emitted only when the broker profile resolves the source timestamp and interval convention; interval-start intraday bars become available at the calculated close, while daily/weekly/monthly starts require a session calendar.
- BOS: close through the latest confirmed swing high/low.
- CHoCH: opposite-direction BOS after a previously observed BOS direction.
- Three-candle FVG: bullish when current low exceeds high two bars earlier; bearish when current high is below low two bars earlier. Minimum gap is ATR-scaled.
- Equal-high/equal-low liquidity-pool candidates: confirmed swing levels within ATR-scaled tolerance.
- Liquidity sweep: wick beyond a confirmed swing followed by close back through the level on the same candle. This is a price-action proxy, not evidence of actual resting orders.
- Order-block candidate: last opposite-colour candle within a fixed lookback before a close-through BOS. It is a heuristic zone, not proof of institutional activity.
- Material price discontinuity candidate: open/prior-close difference at least 0.10 current ATR. Session/weekend gap classification awaits broker calendar/timezone resolution.

## Explicit exclusions from first implementation

No future swing is exposed before confirmation; no "institutional order" is inferred; no unconfirmed FVG/OB is treated as validated support/resistance; no volume profile, true order-flow, liquidation, stop map or resting liquidity is fabricated from OHLCV. Tick/quote data is required for stronger spread, aggressor, depth and execution features.

## CLI

Run `2datas features path/to/export.zip --output-dir data/features/price_action` to create one JSONL feature-event file per source symbol/timeframe. Supply the same `--broker-profile` or explicit `--server-name`, `--server-timezone` and `--bar-timestamp-convention` options used for normalization to resolve feature availability. This is a candidate research artifact, not a training dataset.

## Admission policy

Store feature version, parameters, source lineage, origin time and availability time. Features with unresolved timestamps remain source-clock scoped and cannot enter cross-broker UTC alignment. Candidate feature families must pass redundancy, stability, ablation and chronological evaluation before inclusion in training data.
