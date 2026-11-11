# Evaluation Protocol — Phase 0

## 1. Purpose

Define how future dataset/model claims will be tested without leakage, cherry-picking, or mistaking market luck for skill. This is a protocol design document; no benchmark or market-data evaluation has been run.

## 2. Evaluate capabilities separately

Do not collapse all performance into one accuracy or profitability number.

| Capability | Primary evaluation |
|---|---|
| Market-state classification | Per-class precision/recall/F1, balanced accuracy, confusion matrix |
| Structure/event detection | Event precision/recall, timing tolerance, reproducibility, annotation agreement |
| Multi-timeframe synthesis | Consistency with as-of snapshots, contradiction handling, missing/partial-bar correctness |
| Probabilistic forecasts | Brier score, log loss, reliability curves, calibration error with uncertainty |
| Scenario assessment | Event-specific calibration, activation/invalidation correctness, stability |
| Setup policy | Net outcomes after costs, abstention quality, decision coverage, constraint compliance |
| Risk interpretation | Exact agreement with deterministic outputs, zero fabricated critical values |
| Trade management | Event-level decision quality, policy compliance, risk path, realized net outcomes |
| Execution | Fill/cost error, rejection/partial-fill handling, slippage and latency realism |
| News/visual tasks | Point-in-time correctness, evidence traceability, incremental value over structured inputs |

A narrative-quality score is secondary and cannot substitute for objective task metrics.

## 3. Baselines

Freeze relevant baselines before comparing candidate models:
- always NO_TRADE;
- majority-class and prevalence forecast;
- naive persistence;
- simple momentum and mean-reversion rules;
- simple trend-following rule;
- deterministic setup logic;
- current approved AURORA QUANT components, only after separate access/compatibility authorization.

Baselines must use the same information cutoff, costs, target definition, and evaluation period as the candidate. Do not compare a model with costs against a baseline without costs.

## 4. Temporal split design

Use chronological, preferably walk-forward evaluation:
- training period precedes validation;
- validation supports feature/model selection;
- final test is later and untouched until protocol and choices are frozen.

Exact date boundaries must be chosen only after source coverage and target horizons are known. Do not assume a universal 60/20/20 ratio.

Apply:
- purging for overlapping target/event windows;
- embargo for residual temporal dependence and delayed label confirmation;
- duplicate/near-duplicate grouping before split;
- preprocessing fit on training only;
- point-in-time source/version controls;
- strict isolation of final test data.

For multiple horizons, split and purge according to the longest relevant dependency, or maintain rigorously separated target-specific protocols.

## 5. Statistical uncertainty and sample adequacy

Report sample count and effective independent sample size, not just row count. Overlapping windows reduce independence.

Where relevant, report:
- confidence intervals for metrics and net expectancy;
- block/bootstrap methods that respect time dependence;
- performance by year, session, volatility/regime and source;
- stability and dispersion across walk-forward folds;
- sensitivity to costs, spread, slippage, and execution assumptions.

Do not select a model from a single favorable period or one point estimate.

## 6. Probability quality

Evaluate calibration separately from discrimination. Report Brier score/log loss and reliability by horizon/event class, along with sample counts and uncertainty. Calibrate only on validation data, never on the final test set.

Distinguish directional probabilities from barrier-touch and net-profitable-trade probabilities. A high confidence score is not calibrated merely because the model sounds certain.

## 7. Trading-policy evaluation

A policy simulation must include:
- executable bid/ask conventions;
- spread, commission, swap, slippage and latency assumptions;
- broker volume/stop/margin restrictions;
- partial fills, rejects, gaps and stop execution limitations where data permits;
- position overlap, concurrency and exposure constraints;
- daily loss/drawdown/trade limits;
- deterministic sizing and risk gates.

Report net expectancy in R, drawdown, profit factor, average win/loss, win rate, trade count, exposure, turnover, cost sensitivity, and uncertainty intervals. Report abstention rate and performance conditional on taking a trade; neither metric is meaningful alone.

A candle-only backtest must clearly state that intrabar ordering and actual execution may be unknown.

## 8. Incremental-value tests

For each proposed feature/task/modality:
1. Establish a simple baseline.
2. Add only the candidate feature/task.
3. Evaluate on the same chronological folds.
4. Measure incremental improvement and uncertainty.
5. Check stability across regimes/time.
6. Check whether complexity and source fragility justify the gain.
7. Retain, revise, or remove with a recorded decision.

For chart images and news, compare against an otherwise identical structured-data system. Do not include expensive modalities because they appear sophisticated.

## 9. Failure and safety metrics

Explicitly measure:
- future-data leakage incidents;
- fabricated or unsupported account/instrument/execution facts;
- violations of deterministic risk constraints;
- incorrect use of partial or stale bars;
- failure to abstain under missing/conflicting evidence;
- order/position state mismatch handling;
- ambiguous-label rate and forced-label errors.

Critical safety violations block acceptance regardless of aggregate predictive score.

## 10. Reporting standard

Every evaluation report must include:
- dataset, source, feature, label, policy and model versions;
- split manifest and evaluation code/config hashes;
- metrics with sample counts and uncertainty;
- baselines and cost assumptions;
- per-period/regime results;
- failed runs and negative findings;
- leakage/QC results;
- known limitations and unresolved risks.

Do not claim a universal win-rate threshold. Acceptance requires evidence appropriate to the target and use case, plus explicit independent review.
