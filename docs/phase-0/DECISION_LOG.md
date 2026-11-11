# Decision Log

This log records decisions, not assumptions. New decisions must include rationale, evidence, impact, and date. Superseded decisions remain visible.

## D-001 — Design-only authorization

- Status: Accepted
- Date: 2026-11-12
- Decision: Current work is limited to technical design and documentation.
- Consequence: No archive inspection, data download/processing, dataset generation, pipeline implementation, model training, or expensive benchmarks.
- Revisit condition: Separate explicit user approval.

## D-002 — Independent repository

- Status: Accepted
- Date: 2026-11-12
- Decision: This project is maintained in `seyyedalirezamousavi1989-source/2datas` and remains separate from AURORA QUANT implementation and the other Stage 5 dataset project.
- Consequence: No changes to those external projects under this authorization.

## D-003 — Preserve uploaded archive

- Status: Accepted
- Date: 2026-11-12
- Decision: Existing `XAUUSD.zip` is an uninspected source artifact and must remain unchanged.
- Consequence: No claims are made about its contents, source, completeness, quality, or suitability.

## D-004 — Optimize information value, not dataset size

- Status: Accepted
- Date: 2026-11-12
- Decision: Include only fields and examples with explicit purpose, point-in-time validity, reliable definitions, non-duplicative information, and testable value.
- Consequence: No paraphrase-based sample inflation or indiscriminate indicator collection.

## D-005 — Separate outcomes from decisions

- Status: Accepted
- Date: 2026-11-12
- Decision: Objective future market outcomes and policy/action labels are separate target families.
- Consequence: A profitable hindsight trade is not automatically a correct decision label.

## D-006 — Deterministic risk/execution authority

- Status: Accepted
- Date: 2026-11-12
- Decision: Financial calculations and execution safeguards remain deterministic and authoritative; the model interprets verified outputs.
- Consequence: No model-generated replacement for broker/account facts or authoritative risk calculations.

## D-007 — Compact task catalog and feature admission

- Status: Accepted as a design rule; empirical admission remains pending
- Date: 2026-11-12
- Decision: Learning objectives are prioritized and merged when they do not have distinct targets/evaluation. Features require defined purpose, causal availability, reliability, and evidence of incremental value.
- Consequence: Task families and candidate feature categories are not blanket approval to generate labels or calculate every candidate.

## D-008 — Outcome and policy labels remain disjoint

- Status: Accepted
- Date: 2026-11-12
- Decision: Market outcome labels and policy/action labels have separate semantics and provenance.
- Consequence: Future profitability cannot be used as a shortcut to infer the correctness of a historical decision.


## D-009 — Canonical shared data model

- Status: Accepted as a logical design contract; physical schemas remain pending
- Date: 2026-11-12
- Decision: Use canonical source observations and point-in-time snapshots referenced by task-specific Forecast, Scenario, TradeDecision, RiskCalculation, and LifecycleEvent records.
- Consequence: Do not duplicate the same market context across task datasets. Final JSON Schema, physical layout, and Stage 5 compatibility mapping remain deferred.

## D-010 — Typed status semantics

- Status: Accepted
- Date: 2026-11-12
- Decision: Distinguish observed, derived, estimated, unknown, unavailable, not_applicable, not_yet_observable, stale, ambiguous, invalid, and censored states.
- Consequence: Do not overload null or force unresolved evidence into a confident class.

## D-011 — Information-density composition policy

- Status: Accepted as a design rule; empirical sampling remains pending
- Date: 2026-11-12
- Decision: Select by distinct information contribution, preserve independent source corroboration, and account for overlapping windows/episodes.
- Consequence: Do not count paraphrases, adjacent highly overlapping windows, or oversampled copies as independent market evidence. Keep natural-distribution evaluation data.


## D-012 — Preserve A–M through canonical task mapping

- Status: Accepted as a logical mapping; individual task schemas remain provisional
- Date: 2026-11-12
- Decision: Preserve the initial A–M capability architecture and map it to canonical shared entities. T01–T11 are prioritization/grouping, not a replacement architecture.
- Consequence: Do not drop a capability merely because the compact task catalog groups it with another. Split or merge only when target semantics, inputs, consumers, and evaluation justify it.


## D-013 — Task-level behavioral contracts

- Status: Accepted as provisional design contracts
- Date: 2026-11-12
- Decision: Define input, output, abstention, prohibition and evaluation semantics for each prioritized T01–T11 task while preserving A–M scope.
- Consequence: No task may be implemented merely from a broad capability name; its point-in-time inputs, target, downstream consumer and evaluation must be explicit.

## D-014 — Annotation reliability before scale

- Status: Accepted as a release requirement
- Date: 2026-11-12
- Decision: Interpretive labels require operational definitions, reliability pilots, disagreement reporting and preservation of ambiguity. Policy labels remain distinct from market outcomes.
- Consequence: Do not scale subjective labeling or force ambiguous cases into binary classes.


## D-015 — Temporal trade lifecycle as sequence learning

- Status: Accepted as a provisional behavioral contract
- Date: 2026-11-12
- Decision: Treat management as a chronological sequence of point-in-time decisions linked to broker-confirmed lifecycle events, rather than isolated text examples.
- Consequence: Market event time, knowledge/availability time, and trading-system event time remain distinct. An order request never proves a fill; stale or unreconciled state requires abstention/reconciliation.


## D-016 — Optimize verified information value, not volume

- Status: Accepted as a prioritization policy; empirical task promotion remains pending
- Date: 2026-11-12
- Decision: Prioritize a compact core of causal market state, multi-timeframe synthesis, explicit forecasts, conditional decisions, deterministic risk interpretation, and event-based lifecycle reasoning. Optional execution, regime refinement, news, and visual tasks require independent feasibility and incremental-value evidence.
- Consequence: No fixed row target, blanket indicator library, automatic SMC inclusion, or expensive modality is approved. Hard provenance, causality, definition, and licensing gates cannot be traded off against predictive scores.


## D-017 — Forecast targets must be event-defined and semantically separate

- Status: Accepted as a provisional target-engineering contract; target selection remains pending
- Date: 2026-11-12
- Decision: Distinguish fixed-horizon returns, directional classes, barrier first-passage, MFE/MAE, time-to-event, future volatility/range, state transitions, and fully specified net-trade outcomes. Each target must declare horizon, price basis, availability, ambiguity, censoring, costs and evaluation.
- Consequence: Directional probabilities, barrier probabilities and probability of net trade profit are not interchangeable. OHLC cannot resolve unknown intrabar ordering. No exact horizon, barrier, or target set is frozen by this decision.


## D-018 — Market structure and MTF must be causal and conflict-aware

- Status: Accepted as a provisional behavioral contract; feature admission remains pending
- Date: 2026-11-12
- Decision: Structure events become usable only at their actual confirmation and availability times. MTF synthesis uses as-of snapshots and preserves partial, stale, missing and conflicting timeframe evidence. BOS/CHoCH/SMC concepts require operational definitions rather than assumed universal meanings.
- Consequence: No pivot backdating, future swing endpoints, forced timeframe consensus, or claims of hidden institutional order flow. Exact algorithms and timeframe selection remain open.

## D-019 — Macro facts, expectations, interpretations and reactions remain separate

- Status: Accepted as a provisional point-in-time contract; source feasibility and modality admission remain pending
- Date: 2026-11-12
- Decision: News/event intelligence must preserve actual publication and ingestion times, pre-release expectation snapshots, original values and later revisions as distinct records. Derived surprise, text interpretation and observed market reaction are separate semantic layers.
- Consequence: No hindsight narrative, revised value, scheduled-but-unreleased event, or post-event price movement may be presented as information known at the earlier decision time. News inclusion requires licensing and incremental-value evidence.

## D-020 — Visual inputs must prove incremental value over structured market data

- Status: Accepted as a provisional admission policy; image modality remains unapproved
- Date: 2026-11-12
- Decision: Every chart image must be a reproducible, point-in-time rendering linked to an immutable source snapshot and renderer manifest. Visual inputs must be compared against structured-only baselines on identical chronological samples.
- Consequence: No future candles, hindsight annotations, target-revealing metadata, or cross-split image variants. Images are excluded from the core dataset unless they demonstrate reliable incremental value and pass licensing, provenance and resource gates.

## D-021 — Trade policy, realized outcome and deterministic risk authority are separate

- Status: Accepted as a provisional behavioral contract; implementation remains unapproved
- Date: 2026-11-12
- Decision: Distinguish point-in-time market observations, conditional scenarios, policy actions, and realized execution/outcomes. Trade lifecycle is represented as immutable events including partial fills, corrections and broker reconciliation. Position sizing and account/broker constraints remain deterministic and authoritative.
- Consequence: Profitability alone is not a decision-quality label; losses are not automatically bad decisions. NO_TRADE and abstention are first-class. Planned prices are not fills, management requests are not confirmed broker state, and post-trade information must not leak into decision-time inputs.

## D-022 — Sample admission is gated and multi-dimensional, not a single score

- Status: Accepted as a provisional selection policy; implementation remains unapproved
- Date: 2026-11-12
- Decision: Apply hard validity gates before assessing task relevance, novelty, evidence quality, coverage, evaluation usefulness and cost. Preserve typed inclusion, quarantine and exclusion dispositions with reasons. Cluster overlapping episodes and keep natural-distribution evaluation separate from curated challenge sets.
- Consequence: No weighted score can compensate for leakage, invalid provenance or unreliable labels. Do not impose fixed sample counts, class quotas or sampling intervals before source feasibility and effective sample size are known.

## D-023 — Training method must follow a measured capability gap

- Status: Accepted as a provisional learning framework; no training method or model selected
- Date: 2026-11-12
- Decision: Keep deterministic financial/execution authorities outside the learned model. Evaluate prompt/tool/schema improvements first, then consider SFT/PEFT and only evidence-justified advanced methods. Separate task semantics and post-trade review from decision-time inputs.
- Consequence: No default DPO/RL, synthetic preference inflation, fixed hyperparameters, model-size choice or training authorization. Each learning stage requires chronological held-out evaluation, safety checks and explicit approval.

## D-024 — Source admission is task-specific and rights-first

- Status: Accepted as a provisional feasibility framework; no source approved
- Date: 2026-11-12
- Decision: Evaluate sources by rights, identity, temporal semantics, task-specific coverage, quality, reproducibility, incremental value, cost and governance. Prefer the smallest defensible source set and preserve provider/feed identity rather than merging incompatible prices.
- Consequence: No vendor, archive, uploaded ZIP, date range or license is approved. Tick, news, broker specification and execution history are required only for tasks that depend on their semantics. Source inspection/acquisition remains separately gated.

## D-025 — Dataset lineage and releases must be immutable and reconstructable

- Status: Accepted as a provisional governance contract; implementation remains unapproved
- Date: 2026-11-12
- Decision: Represent source, transformation, feature, label, dataset, split, evaluation and review artifacts in a versioned provenance graph. Pin checksums, code/configuration/environment, schema and policy versions. Preserve superseded artifacts and invalidate downstream results when upstream semantics or content changes.
- Consequence: No mutable paths as sole lineage, no in-place replacement of accepted artifacts, no untraceable model checkpoints, and no proprietary data in Git without rights/security review. Storage technology and physical manifest schemas remain undecided.

## D-026 — One integrated architecture map and semantic owner per shared contract

- Status: Accepted as a Phase 0 coordination rule; design remains provisional
- Date: 2026-11-12
- Decision: Maintain one canonical semantic owner for each shared contract and use the integrated architecture audit to reconcile A–M capabilities with T01–T11 tasks. T06 lifecycle management may consume execution events, while T08 owns execution-quality targets; T01 current-state assessment and T09 regime characterization remain distinct only if definitions and consumers justify it.
- Consequence: Related documents may add task-specific detail but must not independently redefine shared semantics. The audit is a desk review of design documents only, not evidence of source/data validity or implementation correctness. No next phase is authorized.

## D-027 — Shared fields require one semantic definition and scoped status domains

- Status: Accepted as a provisional semantic contract; schema freeze remains pending
- Date: 2026-11-12
- Decision: Standardize event, availability, receive, ingestion, decision, confirmation and creation timestamps as distinct concepts. Require explicit price/volume/currency/rate units. Split the overloaded status vocabulary into field-availability, label-resolution, record-validation, scenario/decision, order/deal/position and artifact/release domains.
- Consequence: Null is not a missing-value explanation; each field must define nullability and allowed status/value combinations. Generic confidence/value/price/volume fields are not accepted where they hide distinct meanings. Exact wire types, precision, task requiredness and broker mappings remain evidence-dependent. No implementation or schema freeze is authorized.

## D-028 — Feature admission is evidence-led and minimizes redundant information

- Status: Accepted as a provisional feature-governance rule; no feature approved
- Date: 2026-11-12
- Decision: Treat raw observations, canonical representations, derived features, interpretations, forecasts, policy outputs and future outcomes as separate information classes. Require each feature to have a versioned definition, causal availability, explicit units/dependencies, a named task consumer, redundancy review and chronological incremental-value evidence.
- Consequence: No indicator collection or feature family is admitted by popularity or count. Prefer the smallest robust feature set. Preprocessing is fit on training only; final test is protected from feature selection. Candidate feature families in the new document are hypotheses only. No feature computation or implementation is authorized.

## D-029 — Market outcomes, forecasts, policy decisions, execution and realized results are separate target families

- Status: Accepted as a provisional target-governance rule; target catalog remains unfrozen
- Date: 2026-11-12
- Decision: Define distinct ontologies for market outcome, forecast, policy/action, broker execution and post-trade outcome. Preserve NO_TRADE/abstention as first-class policy outcomes. Require exact event-space semantics, price basis, horizon, confirmation, ambiguity/censoring, overlap and provenance for each target.
- Consequence: Profitability cannot be used as a proxy for decision correctness; a forecast probability cannot be relabeled as trade success probability; simulated fills cannot be presented as observed broker fills. Only a compact subset of target candidates should be promoted after source feasibility and Stage 5 review. No label generation or implementation is authorized.

## D-030 — Scenarios are falsifiable conditional hypotheses, separate from policy and execution

- Status: Accepted as a provisional scenario-governance rule; scenario schema remains unfrozen
- Date: 2026-11-12
- Decision: Require materially distinct scenario paths with observable activation, invalidation and expiry conditions; preserve immutable revisions and explicit evidence conflicts; keep scenario probability semantics separate from forecast targets and action policy.
- Consequence: No forced bullish/bearish symmetry, arbitrary probability normalization, vague untestable triggers, hindsight rewriting, or treating a triggered scenario as an order/fill. Any actionable policy must pass current data, economics, deterministic risk, execution and authorization gates. No scenario generation or implementation is authorized.

## D-031 — Market reasoning must be evidence-linked, causal and conflict-preserving

- Status: Accepted as a provisional cross-task reasoning contract; implementation and empirical validation remain pending
- Date: 2026-11-12
- Decision: Keep observation, measurement, interpretation, forecast and policy/action as distinct epistemic layers. Reason from an immutable decision-time snapshot and canonical evidence references. Preserve timeframe/source/price-basis conflicts, typed uncertainty and abstention; do not force consensus or invent probabilities.
- Consequence: This document coordinates existing semantic owners and does not redefine feature, structure, target, scenario, schema or policy contracts. Retain only non-duplicative reasoning examples with traceable evidence and named task value. No data inspection, annotation, generation, implementation or training is authorized.

## D-032 — Phase 0 requires field-level semantic reconciliation before design freeze

- Status: Accepted; freeze blockers remain open
- Date: 2026-11-12
- Decision: Keep the existing conceptual architecture, but do not declare it frozen until T06/T08 ownership, scoped enums, field-level null/status semantics, canonical time/interval/revision rules, snapshot immutability, risk handoff, T01/T09 disposition, task-to-field registry, and target-dependent split rules are reconciled.
- Consequence: The integrated audit is the coordination record. Canonical semantic owners remain authoritative; related documents must be updated together when a conflict is resolved. No operational schemas, data inspection, generation, implementation, training, or Stage 5 changes are authorized.

## D-033 — Canonical field ownership and T06/T08 boundary

- Status: Accepted as provisional semantic governance; field registry remains unfrozen
- Date: 2026-11-12
- Decision: Maintain one semantic owner per shared field and reference canonical values from task projections. T06 owns trade management/lifecycle reasoning (H + J) and may consume verified execution events (I) as context; T08 owns execution-quality and cost targets (I). Correct the malformed SUPERSEDED status token. Preserve scoped status domains and defer source-dependent timestamp/interval and physical-schema decisions.
- Consequence: Updated TASK_IO_CONTRACTS.md and TASK_TO_SCHEMA_MAPPING.md together; added the canonical field registry and indexed it in README. No data inspection, sample generation, operational schemas, implementation, training, Stage 5 changes or external-project changes are authorized.

## D-034 — Scoped enum and state transition governance

- Status: Accepted as provisional semantic governance; exact wire values and broker mappings remain unfrozen
- Date: 2026-11-12
- Decision: Use separate domains for field availability, record validation, label resolution, feature admission, scenario lifecycle and assessment, condition evaluation, entry decision actions, management actions, order lifecycle, deal/fill events, position state, reconciliation, risk calculation, policy constraint, annotation, artifact and dataset release. WAIT is deprecated as a standalone entry/management action; WAIT_FOR_CONFIRMATION is reserved for a named pending entry trigger, while management uses NO_ACTION or ABSTAIN.
- Consequence: Added SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md and aligned scenario, canonical status, task I/O, management policy, field registry, README and integrated audit documents. No archive/data inspection, data generation, implementation, training, Stage 5 changes or external project changes are authorized.

## Open questions — do not silently resolve

1. **Stage 5 compatibility:** What exact deliverables and schemas will exist after independent acceptance? Audit only after user confirms that milestone.
2. **Source feasibility:** Which providers offer licensed, point-in-time XAUUSD quotes/ticks/bars, broker specification history, and execution records with adequate coverage?
3. **Instrument identity:** Which broker/server symbol definitions and contract-specification changes are relevant to the intended deployment?
4. **Primary decision horizons:** Which trading horizons and decision cadence are genuinely required? Avoid supporting every timeframe merely for completeness.
5. **Target priority:** Which outcome targets demonstrate value for the intended decisions, and which can be removed?
6. **News archive:** Is reliable historical publication-time data available under an acceptable license?
7. **Visual modality:** Do synchronized charts add measurable value over structured data after controlled comparison?
8. **Annotation reliability:** Which discretionary concepts can be defined consistently enough to label?
9. **Evaluation protocol:** What date ranges, regimes, purging/embargo rules, and minimum effective sample sizes are justified by source coverage and target horizons?
10. **Model selection:** Which locally available model and training method fit the final task mix, after representative low-cost feasibility tests?

## Next authorized work

Continue Phase 0 design review only. Resolve definitions and dependencies, remove unnecessary overlap, and prepare a concise specification for user approval. Do not advance to source inspection or implementation automatically.
