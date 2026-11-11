# Multi-Timeframe and Market-Structure Intelligence — Phase 0

## 1. Purpose and status

Define a causal, testable contract for market-structure interpretation and multi-timeframe (MTF) synthesis for XAUUSD.

This is design documentation only. It does not authorize archive inspection, market-data processing, feature computation, annotation, dataset generation, implementation, or training. Exact timeframe selection, swing parameters, event thresholds, source conventions and final schemas remain open until Stage 5 compatibility and source feasibility are separately approved.

The objective is not to teach the model to repeat technical-analysis vocabulary. It is to teach it to distinguish directly observed price facts, confirmed events under a declared rule, provisional hypotheses, conflicting interpretations, and unavailable or insufficient evidence.

## 2. Core causal rule

A structure event is usable only from the moment its confirmation evidence is available—not from the historical pivot where it visually appears to have formed.

For every structure object, preserve:
- event_start_time: earliest market time associated with the candidate event;
- event_end_time: end of the price interval involved;
- confirmed_at: first time the frozen rule has enough evidence to confirm it;
- available_at: time the system actually received the confirming evidence;
- decision_timestamp: snapshot cutoff for a downstream decision;
- definition_version: exact rule version.

A structure object may be displayed retrospectively at its pivot location for charting, but its historical decision-time availability must remain confirmed_at/available_at. Never backdate it as known at event_start_time.

## 3. Price and bar conventions

Before defining any structure event, specify source/provider and exact XAUUSD symbol mapping; bid, ask, mid, last, or provider-defined OHLC basis; timeframe and bar interval convention; bar completion and actual availability rule; timezone/session/DST behavior; tick size/precision and equality tolerance; and handling of gaps, missing bars, corrections and partial bars.

Do not combine structure labels calculated on different price bases or bar constructions without explicit source normalization and provenance.

## 4. Swing and pivot definitions

A swing high/low is a rule-defined local extremum, not an objectively unique market fact.

Candidate families include fixed left/right bar confirmation, volatility-scaled prominence, directional-change/reversal-threshold pivots, and source-defined fractal pivots.

For any selected method, freeze:
- left/right observation requirements or reversal threshold;
- tie/equal-high/equal-low behavior;
- minimum prominence/distance if used;
- earliest confirmation point;
- behavior at session gaps and incomplete history;
- whether a pivot can be superseded or revised;
- sensitivity analysis across plausible parameter changes.

Use separate statuses: candidate (potential pivot, not confirmed); confirmed (full evidence requirement satisfied); superseded (later rule-defined event changes the active structural interpretation); ambiguous (tie, gap or source limitations prevent a unique result); unavailable (insufficient history or missing source data).

A confirmed pivot is immutable as a historical observation under its original definition version. A later structural interpretation may supersede its active role, but must not rewrite what was known earlier.

## 5. Trend and range state

Trend/range classification must be operational, versioned and allowed to abstain.

A candidate state model may include uptrend, downtrend, range, transition/uncertain, and insufficient evidence.

Do not define an uptrend solely as a recent sequence of HH/HL labels unless swing confirmation and minimum significance are specified. Similarly, a range requires explicit boundary construction, tolerance, minimum duration, and invalidation/break criteria.

Store the evidence supporting the state, its start time, confirmation/availability time, confidence semantics if empirically calibrated, and expiry/invalidation conditions. Avoid emitting a forced trend label for every bar.

## 6. BOS, CHoCH and break events

BOS and CHoCH are interpretive conventions, not universal exchange events. Each retained concept requires a precise operational definition.

The definition must state:
- which confirmed swing or range boundary is being tested;
- whether a break uses wick, close, bid/ask, or another price rule;
- required distance/buffer relative to tick size, spread or volatility;
- whether a close beyond the level is required;
- whether the event is provisional on intrabar movement and confirmed only at bar close;
- treatment of gaps through a level;
- how repeated breaks and failed breaks are represented;
- how trend context is established without lookahead;
- invalidation and expiry rules.

Prefer storing the underlying break fact (level, price, time, price basis, confirmation) separately from a higher-level BOS/CHoCH interpretation. This allows alternative definitions to be compared without changing raw evidence.

Do not label a wick through a level as a confirmed close-break. Do not assume a break is meaningful merely because a chart annotation looks convincing.

## 7. Support, resistance and zones

A level or zone is a derived hypothesis with provenance, not a timeless fact.

Every zone definition must specify construction method and source pivots/events; price bounds and tolerance; creation and availability times; number and independence of contributing touches; whether touches are wick-based or close-based; freshness/decay rule; reaction/break/invalidation criteria; and overlap/merge rules for nearby zones.

Do not count repeated bars within one continuous contact as independent confirmations. Do not let a future reaction determine the zone boundaries retrospectively for a decision-time input.

## 8. Liquidity and SMC candidate concepts

SMC terminology must not be treated as verified institutional order-flow data. Unless actual order-book/flow sources support the claim, these are price-action interpretations only.

For each candidate:
- Equal highs/lows: define tolerance, eligible pivots, time separation and clustering.
- BSL/SSL pools: specify the observable price pattern used as a proxy; do not claim actual resting orders are known.
- Sweep: define the reference pool, penetration threshold, reclaim rule, confirmation time and failed-sweep handling.
- Displacement: define normalized move size, body/range characteristics, volatility baseline and confirmation.
- FVG/imbalance: define exact bar pattern, price bounds, timeframe, creation time, mitigation and invalidation.
- Order block: define the precise source candle/sequence and subsequent qualifying displacement; specify mitigation/invalidation and alternative competing definitions.
- Premium/discount: define the dealing range endpoints and when both became knowable; do not use future swing endpoints.
- Mitigation: define observable revisit/penetration criteria and whether partial fills of a zone count.

Each concept must pass annotation reliability or deterministic reproducibility tests and demonstrate incremental value beyond simpler price/structure features before promotion.

## 9. Multi-timeframe as-of synchronization

MTF synthesis is an as-of join, not a chart-layout exercise.

For each decision timestamp:
1. Select only source observations actually available by the cutoff.
2. Identify the latest eligible completed bar for each timeframe.
3. If partial-bar use is intended, represent it as a separate partial snapshot with an exact availability cutoff and never confuse it with a completed bar.
4. Preserve bar open/close, source availability, completion status and source revision.
5. Apply consistent session, DST, broker-bar and late-arrival rules.
6. Mark missing, stale or conflicting timeframe inputs explicitly.

A higher-timeframe bar whose interval overlaps the decision time is not automatically available. A bar becomes eligible only under its declared completion and availability policy.

Do not construct an H1 or H4 value using lower-timeframe bars that had not yet arrived at the decision cutoff. Corrections arriving later create a new snapshot revision; they do not alter an earlier historical information set.

## 10. Timeframe selection and role separation

M1, M5, M15, M30, H1, H4 and D1 are candidate intervals, not a mandatory full matrix.

Select the smallest useful set based on intended decision cadence and forecast horizon; verified source coverage and timestamp reliability; distinct information contribution; computational and context cost; and robustness across sessions and regimes.

Assign explicit roles only if evidence supports them, for example context timeframe, setup timeframe, and trigger/observation timeframe.

Do not assume a fixed mapping such as D1=direction, H4=trend, M15=setup, M5=entry is universally optimal. Test whether each timeframe contributes incremental information and whether it creates conflicting or redundant signals.

## 11. Conflict-aware MTF synthesis

The model must not be trained to force agreement across timeframes.

Represent each timeframe assessment separately, then synthesize aligned evidence, conflicting evidence, neutral or range-bound evidence, stale/missing evidence, provisional versus confirmed structure, the dominant context (if a defined policy supports one), and conditions that would resolve the conflict.

Examples of legitimate conflict:
- higher timeframe bullish while lower timeframe is correcting;
- higher timeframe range while lower timeframe breaks locally;
- one timeframe has a confirmed break while another has only a provisional pivot;
- a partial higher-timeframe bar disagrees with its last completed bar.

The output should explain whether the conflict supports waiting, conditional scenarios or abstention—not silently discard the inconvenient timeframe.

## 12. Evidence graph and compact representation

Avoid copying the same structure explanation into every task record.

A logical StructureAssessment should reference MarketSnapshot ID; timeframe and eligible bar references; pivot/level/event IDs and definition versions; supporting and conflicting evidence references; current state and status; confirmation/availability timestamps; and invalidation/expiry conditions.

An MTFAssessment should reference the individual timeframe assessments and identify its synthesis policy/version. Task examples should store references plus only the minimal task-specific interpretation.

## 13. Annotation and reproducibility protocol

For interpretive concepts:
1. Freeze a written operational definition and edge-case guide.
2. Create a representative pilot only after data-generation approval.
3. Use independent annotation where feasible and blind annotators to future outcomes.
4. Measure agreement, timing disagreement and class prevalence.
5. Preserve unresolved ambiguity and adjudication history.
6. Test parameter sensitivity and alternative definitions.
7. Reject concepts whose reliability or incremental value is inadequate.

For rule-derived features, require deterministic repeatability, boundary tests, and independent implementation checks where practical.

## 14. Evaluation

### Event level
- precision/recall and event prevalence;
- false break and missed break rates;
- pivot confirmation delay;
- level/zone boundary and timing disagreement;
- reliability by timeframe, session, regime and source.

### State level
- class-wise metrics and confusion;
- duration/persistence accuracy;
- transition timing tolerance;
- abstention and unresolved-case rates.

### MTF level
- incremental value over the best single-timeframe baseline;
- robustness when one timeframe is missing or delayed;
- calibration of any probabilistic output;
- stability across chronological folds and market regimes.

### Downstream level
- improvement to a separately defined forecast or setup policy;
- cost-aware outcome and risk metrics where execution assumptions are supported;
- confidence intervals and effective independent episode counts.

Do not claim that a structure label is useful merely because annotators agree. Reliability and predictive/decision value are separate gates.

## 15. Leakage and edge-case test matrix

Before accepting any definition, test:
- pivot visible retrospectively but not yet confirmed;
- equal highs/lows and tolerance boundaries;
- wick-only breach versus close beyond level;
- gap through a level;
- missing or delayed bar;
- partial higher-timeframe bar;
- late correction to a completed bar;
- session boundary and DST transition;
- overlapping zones and repeated touches;
- future endpoint used inadvertently in premium/discount;
- same episode represented by many overlapping windows;
- conflicting timeframes and stale inputs.

Any failed causality or reproducibility test blocks admission.

## 16. Promotion gate

A market-structure or MTF concept is eligible for later implementation only when its downstream purpose is named; operational definition and version are frozen; source and price basis are known; confirmation and availability times are causal; missingness and ambiguity are explicit; annotation reliability or deterministic reproducibility is adequate; it adds measurable value beyond simpler alternatives; chronological evaluation and leakage tests are specified; Stage 5 compatibility and source feasibility are reviewed; and the user explicitly approves the next phase.

## 17. Explicit non-decisions

This document does not freeze a particular swing algorithm or parameter; exact BOS/CHoCH or SMC definitions; timeframe set or role assignment; zone merge/decay rules; a dataset schema or feature list; or any data processing, labeling, training or implementation.

These require evidence and separate phase approval.
