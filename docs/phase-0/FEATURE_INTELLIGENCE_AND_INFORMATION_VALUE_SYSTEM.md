# Feature Intelligence and Information-Value System — Phase 0

## 1. Purpose, scope and status

Define a rigorous method for deciding which XAUUSD-derived features deserve to exist, how their semantics and dependencies are governed, and how their incremental value is tested.

The objective is not to create the largest indicator library. It is to retain the smallest reliable set that adds measurable, stable information to a named task at its actual decision time.

**Design only.** No market data was inspected or processed, no feature values were calculated, no formula was empirically validated, and no feature is approved for production or training by this document. The candidate families below are research hypotheses, not a feature shopping list. Stage 5 compatibility, source feasibility and explicit user approval remain mandatory gates.

## 2. Core principle: facts first, features second

Keep these information classes separate:

1. **Raw observations:** source-faithful OHLC, quotes, ticks, broker events and licensed macro records.
2. **Canonical representations:** validated returns, price distances, bar intervals and synchronized snapshots.
3. **Derived features:** deterministic, versioned calculations from eligible observations.
4. **Interpretations:** market-state, structure or regime assessments with explicit definitions.
5. **Forecasts:** estimates of future target events.
6. **Policy outputs:** scenarios, action classes and abstentions.
7. **Future outcomes:** labels derived only after the relevant future window/confirmation is available.

A derived feature must never be presented as a raw fact. A forecast or future label must never be embedded in the feature input snapshot. Every derived feature points to its dependencies and formula version.

## 3. Feature value is conditional, not intrinsic

A feature has value only relative to:
- a named task and decision cadence;
- a precise target and horizon, where prediction is involved;
- a baseline input set;
- a specific source/feed and point-in-time policy;
- an evaluation period and regime distribution;
- a cost/latency/maintenance budget.

A feature that helps T03 forecasting may add no value to T01 state description. A feature useful at H1 may be redundant at M5. A feature can be predictive in one period and unstable later.

Therefore, do not assign universal importance scores or declare a feature useful from correlation, visual intuition, indicator popularity, or one backtest.

## 4. Canonical feature registry

Every candidate and retained feature must have a versioned registry record with at least:

| Field | Required meaning |
|---|---|
| feature_id | Stable semantic identifier |
| feature_version | Version of formula and meaning |
| canonical_name | One unambiguous name |
| feature_family | Price, volatility, trend, structure, MTF, session, liquidity, macro, execution, etc. |
| claim_type | Observation-derived measurement or interpretation; never future outcome |
| intended_task_ids | Explicit consumers |
| decision_cadence | Context in which the value is evaluated |
| source_dependencies | Source/feed/instrument fields and versions |
| upstream_feature_ids | Exact derived dependencies |
| formula | Complete executable mathematical/rule definition at schema-freeze time |
| parameters | Explicit, versioned parameters; no hidden defaults |
| units_and_basis | Unit, scale, quote side, currency, timeframe |
| event_time_rule | Period/event represented by the value |
| available_at_rule | Earliest defensible time it can be consumed |
| lookback_and_warmup | Required history and behavior before sufficient history |
| bar_policy | Completed/partial bar treatment and as-of synchronization |
| missingness_policy | Typed absence and invalidity handling |
| quality_preconditions | Required source integrity and freshness |
| sensitivity_profile | Parameter/source/timeframe sensitivities to test |
| redundancy_group | Candidate features that may encode similar information |
| expected_consumer_action | What downstream behavior or analysis it can change |
| validation_protocol | Predeclared tests and baselines |
| validation_status | PROPOSED, SPECIFIED, TESTED, ACCEPTED, REJECTED, RETIRED |
| evidence_refs | Immutable experiment/report IDs supporting status |
| limitations | Known blind spots and unsupported claims |

The registry must distinguish **definition status** from **empirical admission status**. A mathematically specified feature is not automatically useful or accepted.

## 5. Candidate feature architecture

### 5.1 Raw price and return representation

Potential minimal candidates:
- point-in-time OHLC values with explicit quote basis and bar completion;
- one or a small number of causal returns over justified horizons;
- normalized price displacement relative to a declared scale;
- candle body and upper/lower range components, if they add distinct task value.

Requirements:
- Every price input uses the same declared basis or explicitly records mixed quote sides.
- Return formula, reference price, interval, arithmetic/log convention and scaling are fixed.
- Do not store many overlapping lookbacks without incremental-value evidence.
- A price distance is not called a pip/point until broker/instrument semantics define that unit.
- If source OHLC is bid-only, do not silently treat it as mid or executable price.

### 5.2 Volatility and range

Potential candidates:
- one robust range-based measure;
- one return-dispersion measure only if it captures information not already represented;
- volatility expansion/contraction or shock flags with declared windows and thresholds.

Requirements:
- Distinguish realized volatility estimates from candle range and from future volatility targets.
- Declare annualization or non-annualized units.
- Warm-up, gaps, zero-range bars and outlier behavior must be explicit.
- Avoid a large family of near-identical ATR/standard-deviation/range windows.
- Thresholds must be selected using training data or fixed ex-ante rules, never the full dataset.

### 5.3 Trend and momentum

Potential candidates:
- compact multi-horizon return/slope summaries;
- distance from a causally defined reference level;
- one trend-strength descriptor only if it adds beyond simple return/range features.

Requirements:
- Do not equate positive momentum with a guaranteed future rise.
- Avoid many moving-average periods and duplicated oscillators.
- Define whether a trend measure is continuous, categorical or event-based.
- Parameter selection and scaling are fit on training only.

### 5.4 Market structure

Potential candidates:
- confirmed swing references;
- range boundaries;
- break/failed-break events;
- structure direction and invalidation state.

Requirements:
- Confirmation time must be recorded separately from pivot/event time.
- Provisional and confirmed events must remain distinct.
- A future bar cannot retroactively make a feature available at the earlier pivot time.
- Definitions must be deterministic or carry annotation reliability/ambiguity.
- BOS/CHoCH and similar terms require explicit competing operational definitions before admission.

### 5.5 Multi-timeframe context

Potential candidates:
- a minimal higher-timeframe return/structure/volatility context;
- alignment and conflict indicators;
- freshness and completion state.

Requirements:
- Higher-timeframe values are joined by availability time, not by a naive matching candle label.
- Partial bars are explicitly marked and never silently substituted for completed bars.
- A timeframe is retained only if it adds measurable value beyond the primary timeframe and other retained context.
- Avoid a full Cartesian product of features × timeframes × horizons.

### 5.6 Session and calendar context

Potential candidates:
- session identity or overlap flag;
- elapsed time within a documented session;
- scheduled-event proximity, only where a point-in-time licensed calendar is available.

Requirements:
- Session calendar, timezone and daylight-saving database/version are explicit.
- A session label is not a causal market feature unless its calendar was knowable.
- Event proximity is not equivalent to actual news impact.
- Avoid arbitrary time buckets without evidence of stability.

### 5.7 Liquidity and SMC research candidates

Potential candidates include equal-high/low zones, liquidity sweeps, imbalance/FVG, order-block-like zones and premium/discount location.

These are **not accepted as objective facts by naming convention**. Before admission:
- define exact algorithm, parameters, price basis and confirmation time;
- define when the zone/event becomes available and when it expires;
- test sensitivity to small parameter changes and bar construction;
- compare independent annotators if subjective judgment is involved;
- test incremental value against simpler swing/range/return representations;
- avoid claims of institutional orders or hidden liquidity unless the source observes them.

Do not create one feature per popular SMC term merely to increase coverage.

### 5.8 News, macro and execution context

These are conditional modalities, not mandatory market features:
- news requires licensed point-in-time release/publication/update history;
- execution requires broker-specific quote, order, deal and specification evidence;
- simulated execution assumptions must be marked as modeled, never observed.

A feature family is excluded if its historical availability, rights or source semantics cannot be established.

## 6. Feature dependency graph and causal firewall

Represent each feature as a node in a directed acyclic dependency graph. Every edge identifies the upstream feature/source version and time window.

For feature (f) used at decision time (t_d):
- every dependency must be available by (t_d);
- the feature's own `available_at` is no earlier than the latest availability of any dependency plus any required computation/confirmation delay;
- lookback windows must end at or before the declared cutoff;
- learned preprocessing parameters must be fitted on training only;
- future labels, future-confirmed events, post-decision fills and future revisions are forbidden dependencies.

If the feature depends on a swing confirmed three bars later, it is unavailable until that confirmation time, regardless of the earlier pivot timestamp.

A derived feature must carry the dependency references needed to reconstruct the exact input window. A formula that cannot be causally reconstructed is rejected.

## 7. Normalization and representation policy

- Preserve source-faithful raw values separately from normalized model inputs.
- Use units and scale metadata; do not rely on column names to imply units.
- Fit scalers, imputers, clipping thresholds, dimensionality reduction and learned encoders on training data only.
- Store fitted transform artifacts and their training split/version references.
- Never use full-dataset means, quantiles or extrema for preprocessing.
- Do not silently replace unavailable values with zero.
- If clipping or winsorization is used, retain original values and record threshold/version.
- Missingness indicators may be useful, but test whether they encode source outages or future information.
- Avoid per-sample normalization that erases economically meaningful scale unless its purpose is demonstrated.
- Preserve source/feed identity when normalizing across brokers; normalization must not conceal material feed differences.

## 8. Redundancy analysis: more than correlation

Redundancy is assessed at several levels:

1. **Semantic duplication:** two fields assert the same fact under different names.
2. **Formula duplication:** one feature is a deterministic transform or near-copy of another.
3. **Statistical redundancy:** strong dependence under relevant periods/regimes.
4. **Conditional redundancy:** little incremental contribution after other features are present.
5. **Operational redundancy:** extra feature increases fragility/cost without changing a decision or metric.
6. **Dataset duplication:** repeated episodes or copied explanations masquerade as independent information.

Use correlation and mutual-information diagnostics as exploratory tools only. They do not prove equivalence or causal value. Compare nested feature sets and conditional ablations on chronological validation, with uncertainty intervals and regime/source breakdowns.

Highly correlated features may remain if they have distinct semantics or improve robustness. Low correlation is not a reason to retain a feature.

## 9. Incremental-value evaluation protocol

For each candidate feature or tightly related group:

1. Pre-register the task, consumer, hypothesis, metric, baseline and validation periods.
2. Freeze the feature definition and availability rule.
3. Validate source integrity, warm-up and edge cases.
4. Compare a baseline model/rule with the same system plus the candidate feature.
5. Keep target, split, cost assumptions and evaluation code identical.
6. Use chronological validation and episode-aware dependence controls.
7. Report metric delta, uncertainty/confidence interval, sample and independent episode counts.
8. Break down by time period, volatility regime, session and source/feed where feasible.
9. Test reasonable parameter/source perturbations and missingness scenarios.
10. Record decision: ACCEPT, REJECT, REVISE or INSUFFICIENT_EVIDENCE.

For probabilistic targets, inspect calibration and proper scoring rules, not only accuracy. For trading policies, include realistic costs, exposure, drawdown and abstention/coverage. A small apparent gain with a wide interval crossing zero is not evidence of useful incremental value.

No universal numerical threshold is set in Phase 0. Thresholds must be predeclared per task based on the use case and effective sample size.

## 10. Feature-set minimization and admission rules

A feature may be admitted only if all hard gates pass:
- point-in-time availability is defensible;
- formula, units, parameters and dependencies are reproducible;
- source rights and provenance are acceptable;
- missingness and invalidity are explicit;
- it is not a future target or post-decision field;
- it has a named consumer and measurable hypothesis;
- it survives redundancy and robustness review.

Among candidates that pass, prefer the smallest feature set whose validation performance and stability are statistically and operationally indistinguishable from or better than larger alternatives.

Feature selection must occur within training/validation procedures, never by repeated inspection of the final test set. The final test is used only after feature and protocol decisions are frozen.

## 11. Failure and quarantine conditions

Reject or quarantine a feature when:
- availability time is unknown or retrospectively backdated;
- a formula changes across source/timeframe without versioning;
- dependencies include future bars or target information;
- the source's price/volume semantics are unknown;
- warm-up or missingness is silently imputed;
- a value is not reproducible from its registered dependencies;
- a feature's apparent value vanishes under chronological validation;
- the feature is highly parameter-sensitive without a robust rationale;
- a data outage or broker change is encoded as market behavior;
- its use cannot be licensed or audited.

## 12. Recommended compact core for research — not yet approved

The initial candidate research set should be intentionally small:

- canonical point-in-time OHLC/quote context;
- a few non-overlapping return/displacement summaries;
- one primary range/volatility representation plus at most one distinct complement;
- a compact trend/structure description with strict confirmation times;
- only those higher-timeframe context fields that survive incremental ablation;
- data freshness, partial-bar and quality states.

Do not add a broad oscillator library, every timeframe, large SMC taxonomy, news, image embeddings or broker execution features to the first core by default. They remain conditional extensions with separate promotion gates.

This is a research starting point, not an approved feature list or claim of predictive value.

## 13. Feature ablation and interaction policy

Evaluate:
- each feature group alone against a simple baseline;
- each group added to the core;
- removal of each retained group from the full candidate set;
- selected interactions only when motivated by a task hypothesis;
- robustness under source loss, stale inputs and regime changes.

Avoid exhaustive combinatorial search. Predefine a small number of plausible interactions and correct interpretation for multiple comparisons. Do not retain a feature solely because it helps one overfit configuration.

## 14. Monitoring, drift and retirement

For every accepted feature, monitor:
- missingness/staleness and source coverage;
- distribution changes by period, source and regime;
- formula/parameter/version changes;
- sensitivity to feed/specification changes;
- downstream metric and calibration contribution.

A feature may be retired or restricted when its source becomes unreliable, its meaning changes, or incremental value disappears. Retirement creates a new registry state/version and does not erase historical lineage.

## 15. Required artifacts before feature implementation

Before computing any real feature values, the later approved design must provide:
1. source and instrument field contracts;
2. final canonical timestamp and unit representations;
3. task-specific feature registry schema;
4. frozen candidate definitions and parameter policy;
5. causal dependency and availability tests;
6. warm-up/missingness/quality behavior;
7. redundancy and incremental-value protocol;
8. chronological split and final-test protection;
9. provenance and reproducibility manifest integration;
10. Stage 5 compatibility decision and explicit user authorization.

## 16. Open decisions

- Primary decision cadence and small justified lookback/horizon set.
- Actual admitted OHLC/quote price basis and feed(s).
- Exact minimal timeframe hierarchy.
- Which return and volatility definitions best fit source semantics.
- Whether structure/SMC definitions can be made reliable and useful.
- Whether session/calendar context adds value.
- Whether cross-source normalization is justified.
- Task-specific metric thresholds and confidence interval methods.
- How feature registry versions map to Stage 5 schemas.

## 17. Gate

This document is ready for design review only. It does not approve feature formulas, select data sources, inspect uploaded archives, compute feature values, create datasets, implement a pipeline, train models or modify external projects.

Promotion to a frozen feature catalog requires source feasibility, Stage 5 compatibility, task/horizon selection, a reviewed semantic contract and explicit user approval.
