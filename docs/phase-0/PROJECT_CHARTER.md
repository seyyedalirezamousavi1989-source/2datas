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

## 3. Explicit exclusions

Until separate written approval:
- Do not inspect, extract, parse, or process the uploaded XAUUSD.zip.
- Do not acquire or download market/news data.
- Do not generate examples, labels, synthetic samples, or datasets.
- Do not implement a data pipeline or alter project code.
- Do not train, fine-tune, benchmark expensively, or select a final model.
- Do not modify AURORA QUANT, Stage 5, or any other repository/project.
- Do not merge, push to main, rewrite history, or delete existing repository assets.

The existing XAUUSD.zip in this repository is an uninspected source artifact. Its contents, validity, provenance, and suitability are unknown. Preserve it unchanged.

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

| Gate | Required evidence | Not authorized by passing |
|---|---|---|
| 0 Design | Approved scope, schemas, causal contract, QC and evaluation protocol | Data access or generation |
| 1 Compatibility | Independent inspection of accepted Stage 5 deliverables and documented non-overlap | Stage 5 modification |
| 2 Sources | Source inventory, point-in-time coverage, licensing, limitations | Download/processing |
| 3 Specification | Frozen schema/feature/label definitions and split protocol | Pipeline execution |
| 4 Pipeline design | Reviewed implementation plan and test strategy | Dataset generation |
| 5 Generation | Explicit approval, controlled run manifest | Training |
| 6 Integrity | Independent QC, leakage and provenance reports | Benchmark claims |
| 7 Baselines | Frozen protocol, baselines, uncertainty intervals | Training |
| 8 Acceptance | Independent review and signed acceptance | Training |
| 9 Readiness | Data/model interface, splits, constraints, reproducibility | Training |
| 10 Training | Separate explicit approval and run plan | Deployment |
| 11 Evaluation | Held-out results, calibration, robustness, limitations | Live trading |

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
