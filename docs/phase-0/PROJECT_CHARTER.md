# Project Charter — AURORA XAUUSD Dataset

## 1. Mission

Create a statistically defensible, point-in-time-correct, reproducible dataset that improves a model's ability to reason about XAUUSD—not merely predict the next candle or imitate hindsight trade outcomes.

The dataset should teach the model to:
- describe market state and structure with evidence;
- reconcile higher- and lower-timeframe context;
- distinguish observation, interpretation, forecast, and action;
- express uncertainty and calibrated probabilities;
- construct and invalidate conditional trade scenarios;
- reason about risk, costs, execution constraints, and active trade management;
- choose NO_TRADE when evidence or conditions do not justify action.

The primary optimization target is **useful, validated information density**. More rows, indicators, labels, or prose are not success criteria.

## 2. In scope

Research and specification for:
1. Market structure and price action.
2. Liquidity and SMC concepts, treated as operational hypotheses rather than privileged knowledge of institutional orders.
3. Multi-timeframe context and synchronization.
4. Regime, volatility, and session context.
5. Probabilistic outcome forecasting.
6. Setup assessment and conditional trade planning.
7. Risk and position-sizing context.
8. Trade monitoring and lifecycle decisions.
9. Execution realism and transaction costs.
10. News/fundamental context where reliable point-in-time archives exist.
11. Chart-image reasoning only when images can be synchronized exactly to available source data.
12. Evidence-based explanations and uncertainty.

## 3. Current authorization and exclusions

The user has authorized active development of this independent 2datas dataset project, including inspection and processing of the user-provided XAUUSD.zip, implementation within this repository, structural source auditing, and creation of traceable normalized market-data artifacts.

Authorized within 2datas:
- Inspect, extract and process the supplied XAUUSD.zip.
- Implement ingestion, normalization, quality-control and provenance tooling.
- Create normalized base-market records and their manifests.
- Research source semantics and feasibility, then develop causal features, targets and dataset components when their definitions are sufficiently supported.
- Add tests and CI for this repository.

Still excluded unless separately approved:
- Modify the separate `datas` repository, AURORA QUANT, or any other external project.
- Purchase paid data, accept paid subscriptions, or use private credentials/accounts.
- Train/fine-tune models or run expensive benchmarks.
- Deploy a model, connect to live trading, or place/modify broker orders.
- Merge into `main`, rewrite Git history, or delete existing repository assets without review.

This project is self-contained and has no prerequisite compatibility gate against another repository or external project.

## 4. Design principles

### 4.1 Evidence before volume
Every field must have a defined consumer and decision purpose. Remove fields that are duplicated, weakly defined, unavailable at decision time, or not shown to add conditional value.

### 4.2 Causality
A model input may contain only information available at the decision timestamp. Future outcomes belong in isolated targets/labels, never in input features.

### 4.3 Separate truth types
Keep distinct:
- observed market facts;
- derived measurements;
- analyst interpretations;
- probabilistic forecasts;
- policy/action decisions;
- realized execution and outcomes.

A profitable trade in hindsight does not prove that the original action was justified. LONG/SHORT/NO_TRADE are policy decisions, not objective market labels.

### 4.4 Deterministic financial authority
Position sizing, account risk, contract/tick-value calculations, margin, volume rounding, daily loss limits, broker constraints, and execution validation must be computed and enforced by deterministic, tested components. A model may interpret verified outputs but must not invent or override them.

### 4.5 Honest uncertainty
Represent unavailable, unknown, not applicable, not yet observable, and ambiguous states separately. Do not coerce missing evidence into a confident label.

### 4.6 Reproducibility
Every eventual dataset version must be rebuildable from identified source versions, transformations, schemas, label definitions, and configuration, subject to licensing and source availability.

## 5. Acceptance gates

Each phase produces reviewable artifacts and an explicit go/no-go decision.

| Gate | Required evidence | Next boundary |
|---|---|---|
| 0 Scope and design baseline | Approved objective, task priorities, causal and quality contracts | Source admission |
| 1 Source feasibility | Provenance, rights, timezone/bar semantics, coverage and limitations | Canonical storage |
| 2 Canonical data foundation | Reproducible normalized records, immutable hashes, schema and QC tests | Feature engineering |
| 3 Feature and target specification | Causal feature registry, non-redundant target definitions and ambiguity rules | Controlled generation |
| 4 Dataset construction | Versioned features/targets, episode grouping and chronological split manifests | Independent QC |
| 5 Integrity and leakage audit | Reproducibility, point-in-time checks, source/label QC and split isolation | Baselines |
| 6 Baseline evaluation | Frozen baselines, calibration, uncertainty and cost-aware results | Acceptance review |
| 7 Dataset acceptance | Independent review, limitations and reproducible release | Training readiness |
| 8 Training readiness | Data/model interface, splits, constraints and reproducibility | Separate training approval |
| 9 Training | Separate explicit approval and run plan | Model evaluation |
| 10 Evaluation | Held-out results, calibration, robustness and limitations | No automatic deployment |

No gate advances automatically.

## 6. Success criteria

Success is not a predetermined win rate or an arbitrary record count. It requires:
- traceable source provenance and point-in-time availability;
- unambiguous, reproducible target definitions;
- no critical temporal or cross-split leakage;
- appropriate chronological evaluation and untouched test data;
- meaningful comparison with simple and existing deterministic baselines;
- calibrated uncertainty and confidence intervals;
- realistic cost and execution assumptions;
- robustness across time and market regimes;
- demonstrable incremental value from retained features/tasks;
- clear limitations and reproducible artifacts.

If no reliable edge is demonstrated, report that result rather than tuning the evaluation until it looks positive.
