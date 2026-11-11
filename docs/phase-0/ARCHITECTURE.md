# Dataset Architecture and Causal Contract

## 1. Architecture

Keep the system layered so raw evidence, derived features, labels, and model-ready examples cannot be confused.

1. **Source registry** — provider, instrument definition, timezone, granularity, coverage, license, collection/version metadata, known limitations.
2. **Immutable raw layer** — source-faithful records; never silently overwrite original observations.
3. **Integrity layer** — timestamp normalization, duplicate detection, gap/outlier checks, OHLC/quote consistency, source reconciliation.
4. **Point-in-time feature layer** — only measurements computable from information available at the decision time.
5. **Target/label layer** — future-derived outcomes, label confirmation times, ambiguity and censoring states.
6. **Task-example layer** — compact task-specific examples referencing shared canonical observations/features rather than copying repeated context.
7. **Quality/evaluation layer** — schema, leakage, distribution, reproducibility, baseline, calibration, and robustness reports.
8. **Training export layer** — only accepted versions, with split manifests and provenance.

Raw observations, model inputs, labels, and generated explanations must be physically or logically separated with explicit references.

## 2. Task families

Task families are capabilities, not a mandate to create thirteen overlapping datasets. Merge tasks when they share the same input evidence and target semantics; split them only when objectives or evaluation differ.

| Family | Core learning objective | Key boundary |
|---|---|---|
| Market structure | Swings, trend/range, breaks, failures, invalidation | Confirmed vs provisional structures |
| Liquidity/SMC | Operationally defined sweeps, pools, displacement, imbalance | No claim of hidden institutional order access |
| Multi-timeframe | Context alignment/conflict across M1–D1 | Only bars known at decision time |
| Regime/volatility | Trend/range, expansion, contraction, transitions | Avoid redundant indicator copies |
| Forecasting | Probabilities for explicit future events/horizons | Outcome targets, not trade recommendations |
| Setup decision | LONG/SHORT/NO_TRADE/WATCH/WAIT | Policy label separate from realized outcome |
| Risk | Interpret verified risk/account/instrument outputs | Deterministic calculator is authoritative |
| Trade management | Conditional actions across lifecycle | Chronological event sequence |
| Execution | Spread, fills, slippage, rejects, costs | Candle-only limitations explicit |
| News/context | Point-in-time macro/fundamental evidence | Publication and availability time |
| Visual reasoning | Read synchronized, causally valid charts | No future candles or visual leakage |
| Explanation | Evidence, conflict, uncertainty, invalidation | Facts vs inference clearly marked |

## 3. Canonical time contract

All canonical timestamps use UTC while retaining original source timestamp, source timezone, and conversion metadata.

Each observation/feature must distinguish:
- `event_time`: when the market event occurred or bar ended;
- `available_at`: when the value was actually available to the system;
- `recorded_at`: when the project recorded/ingested it;
- `decision_timestamp`: the simulated or actual point at which a decision is made.

A feature is eligible only if `available_at <= decision_timestamp`. Event time alone is insufficient when data can arrive late or be revised.

Each target must define:
- `target_start` and target horizon/event condition;
- `label_confirmed_at`: when sufficient future evidence exists to determine the label;
- `label_status`: resolved, ambiguous, censored, unavailable, or invalid;
- exact target-definition version.

The label confirmation time must not be used as an input feature. A label can remain unresolved at dataset cutoff; do not silently discard or relabel it as a negative outcome.

## 4. Multi-timeframe synchronization

For every timeframe snapshot, record bar open/close, source availability, completion status, and whether the bar is partial. A higher-timeframe bar is not usable merely because its nominal interval overlaps the decision time.

Respect broker-specific bar construction, session boundaries, daylight-saving changes, late-arriving updates, and source corrections. Define a single as-of policy and test it against timestamp edge cases before freezing the schema.

## 5. Outcome targets vs policy targets

Maintain two separate target namespaces:

- **Outcome targets:** objectively defined future price/event outcomes (e.g. barrier hit, return, MFE/MAE, volatility regime transition) with horizon, costs, and ambiguity rules.
- **Policy targets:** actions a decision policy would take under a specified evidence set and risk constraints (LONG, SHORT, NO_TRADE, WATCH, WAIT). Record policy version, constraints, and rationale provenance.

Never infer that an action was correct solely because its eventual outcome was profitable. Evaluate policy quality separately from outcome forecasting.

## 6. Probabilities

A probability vector must identify the event space, horizon, and mutually exclusive/exhaustive outcomes. If outcomes do not form such a partition, do not force probabilities to sum to one.

Directional probabilities, barrier-touch probabilities, and trade-success probabilities are different quantities and must never share an ambiguous field such as `confidence`.

## 7. Risk and execution boundary

The model consumes verified, timestamped outputs from deterministic services. It may identify contradictions, explain risk, recommend abstention, or request recalculation. It must not fabricate:
- account balance/equity/free margin;
- contract size, tick size/value, volume step, leverage or broker rules;
- spread, commission, swap, fill price or execution status.

Position sizing must account for instrument/account currency conversion, stop distance, broker contract/tick specifications, commissions and other applicable costs, margin constraints, volume-step rounding, and post-rounding risk revalidation.

## 8. Efficient representation

Use canonical shared references for repeated market context. Store task-specific deltas and targets rather than duplicating the same candles, indicators, and prose across many examples. Keep raw time series in analytical formats (e.g. Parquet) and compact task examples in a structured instruction format (e.g. JSONL) only after schemas are frozen.

Do not create a field merely because it is easy to calculate. Retain it only when it is reliable, available at decision time, interpretable, and useful beyond existing fields.
