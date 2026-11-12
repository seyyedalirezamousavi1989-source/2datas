# Causal price-action feature contract

Version: 0.1.0

This is a compact initial feature implementation, not a claim that SMC terminology is objectively standardized. Every concept is an operational hypothesis with explicit parameters and a named consumer. Definitions must be tested for stability, annotation agreement and incremental value before model admission.

## Implemented candidate events

- True range and rolling ATR (simple rolling mean; initial warm-up is null).
- Candle body, body/range, close location, one-bar return and range/body normalized by ATR.
- Confirmed swing highs/lows: a pivot is emitted only after the configured right-side bars have closed; event availability is the confirmation bar, not the pivot origin.
- BOS: close through the latest confirmed swing high/low.
- CHoCH: opposite-direction BOS after a previously observed BOS direction.
- Three-candle FVG: bullish when current low exceeds high two bars earlier; bearish when current high is below low two bars earlier. Minimum gap is ATR-scaled.
- Equal-high/equal-low liquidity-pool candidates: confirmed swing levels within ATR-scaled tolerance.
- Liquidity sweep: wick beyond a confirmed swing followed by close back through the level on the same candle. This is a price-action proxy, not evidence of actual resting orders.
- Order-block candidate: last opposite-colour candle within a fixed lookback before a close-through BOS. It is a heuristic zone, not proof of institutional activity.
- Price gap: current open differs from prior close. Session/weekend gap classification awaits broker calendar/timezone resolution.

## Explicit exclusions from first implementation

No future swing is exposed before confirmation; no "institutional order" is inferred; no unconfirmed FVG/OB is treated as validated support/resistance; no volume profile, true order-flow, liquidation, stop map or resting liquidity is fabricated from OHLCV. Tick/quote data is required for stronger spread, aggressor, depth and execution features.

## Admission policy

Store feature version, parameters, source lineage, origin time and availability time. Features with unresolved timestamps remain source-clock scoped and cannot enter cross-broker UTC alignment. Candidate feature families must pass redundancy, stability, ablation and chronological evaluation before inclusion in training data.
