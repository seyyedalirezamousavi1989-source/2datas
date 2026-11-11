# Market Reasoning and Evidence Synthesis — Phase 0

## 1. Purpose and boundary

This document defines how the model should reason across existing market observations, features, structure assessments, timeframe states, forecasts and scenarios without duplicating their definitions.

It is a **cross-task reasoning contract**, not a new indicator catalogue, structure taxonomy, target specification, or implementation plan. Semantic ownership remains with:
- `CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md` for shared fields, timestamps, units and statuses;
- `DATA_MODEL_AND_SCHEMA_CONTRACTS.md` for entity identity and references;
- `FEATURE_INTELLIGENCE_AND_INFORMATION_VALUE_SYSTEM.md` for feature definitions and admission;
- `MULTI_TIMEFRAME_AND_MARKET_STRUCTURE.md` for structure events and as-of MTF synchronization;
- `SCENARIO_SPECIFICATION.md` for conditional paths and scenario lifecycle;
- `TARGET_AND_LABEL_INTELLIGENCE_GOVERNANCE.md` and `FORECAST_TARGET_ENGINEERING.md` for future outcomes and forecast targets;
- `TASK_IO_CONTRACTS.md` for task-specific input/output boundaries;
- `CHART_AND_VISUAL_INTELLIGENCE.md` for image snapshots and visual evidence.

**Design only.** No data has been inspected, calculated, annotated, generated, or trained. No task, feature, taxonomy, model, or implementation is approved by this document. Stage 5 compatibility, source feasibility and explicit approval remain separate gates.

## 2. The reasoning objective

The model should produce a traceable assessment of what is known, what is inferred, what remains uncertain, and what evidence would change the assessment.

It must not optimize for:
- confident-sounding technical-analysis language;
- maximum number of indicators, patterns or scenarios;
- forced agreement among timeframes;
- hindsight explanations that fit the realized chart;
- a trade recommendation in every snapshot;
- a single opaque score that hides contradictory evidence.

The unit of reasoning is a **decision-time evidence snapshot**, not a free-form chart narrative.

## 3. Five epistemic layers

Keep the following layers explicit in every reasoning path:

1. **Observation:** source-backed market facts available by the decision cutoff.
2. **Measurement:** reproducible derived quantities with registered formulas and units.
3. **Interpretation:** rule- or annotation-defined assessment such as structure, regime or liquidity proxy.
4. **Forecast:** estimate of a separately registered future event/target and horizon.
5. **Policy/action:** decision under a named policy and deterministic constraints.

An observation is not an interpretation; an interpretation is not a forecast; a forecast is not a trade decision; a proposed action is not an execution event.

Narrative text may explain these layers but must not merge them or upgrade an uncertain interpretation into an observed fact.

## 4. Evidence graph, not prose duplication

Each material reasoning claim should reference one or more stable evidence IDs and versions. Evidence references should identify:
- source/record or canonical entity;
- definition/version for derived or interpreted evidence;
- event time and actual availability time;
- timeframe and price basis where applicable;
- quality/freshness/ambiguity status;
- role in the argument: SUPPORTS, CONTRADICTS, CONTEXT, or LIMITS.

A claim with no traceable evidence must be marked unsupported or omitted. Repeatedly copying the same evidence description into multiple task examples does not create independent evidence or extra training value.

The reasoning record should store concise claim/evidence references. Full source payloads remain in their canonical owner.

## 5. Causal reasoning sequence

For a decision timestamp (t_d), the reasoning process is conceptually ordered:

1. Validate snapshot identity, source coverage, clock semantics and freshness.
2. Exclude any input whose defensible `available_at` is later than (t_d).
3. Separate completed bars from partial observations and identify eligible timeframe states.
4. Establish direct observations and derived measurements before interpreting them.
5. Assess market state and structure using only registered definitions.
6. Identify material agreement, conflict, missingness and uncertainty across timeframes.
7. Consider only forecasts tied to explicit target definitions and horizons.
8. Construct materially distinct conditional scenarios only where evidence supports them.
9. Hand off to the separate policy gate; do not infer risk permission or execution.
10. Record what new observation, event or condition would change the assessment.

This sequence is a reasoning dependency order, not an authorization to build a runtime pipeline.

## 6. Market-state reasoning without forced labels

A state assessment may return:
- directional/trending state under a registered taxonomy;
- range/balance under a registered taxonomy;
- transition or mixed state;
- insufficient evidence;
- stale, conflicting or unavailable inputs.

The taxonomy and transition rules belong to the relevant task/definition registry. This document does not define new numeric thresholds.

Do not force every observation into bullish, bearish or sideways. Distinguish:
- current observed state;
- provisional hypothesis;
- confirmed state under a named rule;
- forecast of a future transition.

A market can have a higher-timeframe directional context and a lower-timeframe counter-move simultaneously. These are not logically inconsistent if their timeframe and scope are preserved.

## 7. Evidence hierarchy and source conflict

Do not apply a universal simplistic ranking such as “higher timeframe always wins” or “ticks always override everything.” Authority depends on the claim being made and source fitness.

For each conflict:
- retain both source/evidence references;
- compare instrument/feed identity, price basis, event and availability times;
- assess freshness, completeness, precision and known source limitations;
- identify whether the disagreement is expected (different timeframe/quote side) or material;
- apply a reconciliation rule only if that rule is registered for the relevant claim;
- otherwise preserve CONFLICT/UNKNOWN and abstain from unsupported resolution.

A broker quote can be authoritative for that broker's executable quote, but not automatically for a different provider's historical OHLC. A completed H4 bar and a partial M5 bar describe different intervals and must not be treated as competing measurements of the same thing.

## 8. Reasoning about structure and SMC concepts

Use the operational definitions and causal confirmation rules in the market-structure specification. Do not create alternate definitions inside free-form reasoning prompts.

For every structure claim, distinguish:
- directly observed level/price movement;
- candidate or confirmed pivot/event;
- higher-level interpretation such as BOS/CHoCH;
- proxy interpretation such as liquidity pool/sweep;
- confirmation and actual availability time.

Do not claim knowledge of hidden institutional orders from OHLC patterns. SMC labels are hypotheses/proxies unless independent source evidence supports a stronger claim.

Where two reasonable definitions disagree, retain definition IDs and compare them as separate interpretations; do not silently blend them.

## 9. Multi-timeframe synthesis

Each timeframe assessment remains independently inspectable. The synthesis should summarize:
- aligned evidence;
- conflicting evidence;
- neutral/range context;
- provisional versus confirmed events;
- stale, missing or partial inputs;
- the specific condition that could resolve a conflict.

Do not collapse all timeframe states into a majority vote. Do not assign a universal priority to H4, H1, M15 or M5. A dominant context may be named only under an explicit task/policy rule, with the underlying disagreement still visible.

The latest completed bar and any partial bar must be separately represented. A partial-bar signal cannot be described as a completed-bar confirmation.

## 10. Hypothesis quality and falsifiability

A useful interpretation states:
- the claim being made;
- evidence that supports it;
- evidence that contradicts it;
- assumptions and definition versions;
- current status and expiry;
- an observable condition that would strengthen, weaken or invalidate it;
- what is unknown and why.

Avoid non-falsifiable claims such as “smart money is accumulating” unless translated into a registered observable proxy and explicitly described as a proxy.

Do not retrofit the trigger or invalidation after the future path is known. A later update creates a new revision with its own availability time; the original decision-time assessment remains immutable.

## 11. Forecast reasoning and probability discipline

A forecast must reference one target definition/version, event space, horizon, price basis and snapshot. It should distinguish point estimate, distribution/interval and calibrated event probability.

Rules:
- no numeric probability without a well-defined event and an appropriate calibration/evaluation record;
- do not normalize scenario scores into probabilities;
- do not mix directional probability with barrier-first or net-profit probability;
- preserve uncertainty and unresolved target outcomes;
- distinguish model-estimation uncertainty from source ambiguity and calibration uncertainty;
- no future target evidence in the input explanation.

If probabilities are unavailable or not calibrated, use qualitative conditional language and clearly state that it is not a measured probability.

## 12. Reasoning output contract

A compact analytical response should be structured around these semantic sections, with fields bound to canonical contracts rather than independently redefined:

1. **Snapshot:** decision timestamp, source coverage, timeframe availability and quality.
2. **Observed facts:** only directly evidenced facts.
3. **Measurements:** relevant registered features with units/versions.
4. **Current interpretation:** state/structure and its definition/status.
5. **MTF synthesis:** aligned, conflicting, missing and partial evidence.
6. **Forecast references:** target/horizon and calibrated probabilities only where valid.
7. **Conditional scenarios:** distinct paths with triggers, invalidation and expiry.
8. **Uncertainty and limitations:** typed reasons, not one generic confidence value.
9. **Next information:** the specific observation/event that would change the assessment.
10. **Policy handoff:** no action recommendation unless the separate policy contract and risk gates are satisfied.

The output should be concise relative to evidence volume. Do not repeat all candles, indicators or source descriptions when stable references suffice.

## 13. Contradiction taxonomy

At minimum, distinguish:
- SOURCE_CONFLICT: feeds/providers disagree;
- PRICE_BASIS_CONFLICT: bid/ask/mid/last conventions differ;
- TIMEFRAME_SCOPE_DIFFERENCE: intervals describe different market scales;
- CONFIRMATION_CONFLICT: provisional and confirmed evidence are mixed;
- TEMPORAL_CONFLICT: late-arriving/corrected evidence differs from earlier known state;
- FEATURE_INTERPRETATION_CONFLICT: derived measures support different readings;
- MODEL_DISAGREEMENT: separate forecasts disagree;
- POLICY_CONSTRAINT_CONFLICT: a plausible setup conflicts with risk/execution constraints.

These are diagnostic categories, not new universal status values. Use the canonical scoped status domains for field, record, label, scenario and lifecycle states.

## 14. Abstention and safe failure

The reasoning layer must be able to return insufficient evidence without inventing a directional conclusion.

Abstention is appropriate when:
- critical source data is missing, stale or invalid;
- point-in-time availability cannot be established;
- conflicting feeds cannot be reconciled;
- structure confirmation is not yet available;
- the requested target/event is undefined;
- forecast probabilities lack valid semantics or calibration;
- scenario conditions cannot be evaluated;
- deterministic risk/execution inputs are missing for an actionable plan.

Use the most specific reason code available. Do not hide data-quality failure behind low confidence or use a fluent explanation to conceal missing evidence.

## 15. Evaluation of reasoning quality

Evaluate reasoning dimensions separately; do not reduce them to a single subjective “analysis quality” score.

Candidate metrics:
- **Evidence traceability:** claims with valid evidence references / claims made.
- **Causal validity:** input references satisfying availability cutoff and dependency audit.
- **Fact/interpretation separation:** unsupported interpretations incorrectly presented as facts.
- **Conflict preservation:** material conflicts retained rather than silently discarded.
- **Falsifiability:** hypotheses with testable conditions and valid expiry.
- **Calibration:** only for registered probabilistic targets, using proper scoring and reliability analysis.
- **Abstention quality:** unsafe unsupported conclusions avoided, with coverage reported.
- **Conciseness/information density:** redundant claims and repeated evidence references per decision.
- **Temporal robustness:** stability across chronological periods, sessions, regimes and source feeds.
- **Downstream incremental value:** improvement to a separately defined task/policy over a simpler baseline, including costs where execution evidence permits.

Human review rubrics must have operational criteria and independent review. Fluent prose or agreement with hindsight is not a ground-truth metric.

## 16. Dataset efficiency and deduplication

Prefer one canonical snapshot and reusable evidence graph to repeated full-context examples.

A new reasoning example should be retained only if it adds at least one of:
- a materially different market state or transition;
- a new evidence conflict or source-quality condition;
- a distinct causal structure/MTF configuration;
- a meaningful uncertainty/abstention case;
- a different target/horizon required by a named task;
- a genuinely distinct conditional scenario or decision consequence.

Do not multiply examples by paraphrasing the same reasoning. Group overlapping snapshots by market episode before splitting. Preserve natural prevalence in evaluation and keep curated edge-case sets separate.

## 17. Promotion gates

Before this reasoning contract is frozen:
1. Cross-check every field and status reference against canonical semantic ownership.
2. Cross-check T01/T03/T04/T05/T07/T09 and scenario contracts for task boundaries.
3. Ensure no duplicate definitions of swings, structure, feature formulas, target labels or policy actions.
4. Confirm evidence references can be resolved from the logical data model.
5. Define an auditable human/rule review rubric without treating hindsight as truth.
6. Establish causal, contradiction, missingness and abstention test cases after the relevant phase is approved.
7. Confirm Stage 5 compatibility only after its independent acceptance.
8. Obtain explicit user approval before any source inspection, implementation, annotation or data generation.

## 18. Explicit non-decisions

This document does not:
- select a model architecture or training method;
- approve a fixed feature set, indicator library, timeframe hierarchy or SMC taxonomy;
- define numeric market thresholds, forecast probabilities or trading rules;
- authorize image use, news acquisition, source inspection or archive extraction;
- authorize dataset generation, labeling, backtesting, model training or implementation;
- modify AURORA QUANT or the separate Stage 5 project.

The governing objective remains the smallest reliable, causal, non-redundant evidence set that demonstrably improves a named task.
