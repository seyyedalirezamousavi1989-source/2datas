# Integrated Architecture, Dependency Map and Consistency Audit — Phase 0

## 1. Status and authority

This document consolidates the current Phase 0 design into one navigable architecture and records cross-document overlap, unresolved semantics and phase dependencies.

**Design/documentation only.** This is a desk review of the specifications in this repository, not a data audit or implementation audit. No source archive (including XAUUSD.zip) has been opened or validated. No market data, labels, samples, pipeline, benchmark or model has been produced. The separate Stage 5 project and AURORA QUANT remain untouched.

This document is a coordination layer; it does not silently override detailed contracts. If two specifications disagree, the conflict must be resolved in the decision log and the affected document versions updated before schema freeze.

## 2. Executive architecture

The project should be understood as five connected planes:

1. **Evidence plane** — source identity, licensing, raw observations, broker specifications, news and execution records.
2. **Causal intelligence plane** — immutable point-in-time snapshots, validated features, market-state interpretation, forecasts and conditional scenarios.
3. **Decision and lifecycle plane** — policy decisions, deterministic risk results, broker-confirmed lifecycle events and post-trade review.
4. **Research plane** — target/label generation, sample admission, episode grouping, chronological splits, baselines and evaluation.
5. **Governance plane** — provenance, versioning, reproducibility, quality controls, approvals and release decisions.

The core information path is:

`Admitted Sources → Immutable Observations → Integrity/Normalization → As-of Snapshot → Validated Features → Task-Specific Inference`

Future outcomes branch away from the decision-time input path:

`Snapshot + Target Definition + Future Observations → Isolated Outcome Labels`

Policy labels and broker outcomes are also separate branches. Only an approved release may join task inputs and target references for training/evaluation materialization, with immutable split and provenance manifests.

## 3. Canonical layer ownership

| Layer | Owns | Must not own |
|---|---|---|
| Source registry | Provider/feed identity, symbol mapping, rights, coverage, semantics | Derived features or model conclusions |
| Raw evidence | Source-faithful immutable observations/events | Silent corrections or inferred fills |
| Integrity/normalization | Timestamp normalization, validation, deduplication, quality flags | Hindsight repair or invented missing values |
| Instrument/account context | Effective-dated broker specs and verified account facts | Generic assumptions presented as account truth |
| Snapshot/context | Exact decision-time observations and timeframe states | Future targets or post-decision events |
| Feature registry/value | Versioned formulas, dependencies, availability and derived values | Unregistered duplicate indicators |
| Interpretation/tasks | State, MTF synthesis, structure, news/visual assessments | Authoritative risk calculations |
| Forecast | Named future event/horizon and calibrated estimate | Trade policy or fill certainty |
| Scenario | Conditional path, evidence, trigger, invalidation and expiry | A forecast probability relabeled as trade success |
| Policy decision | Action/abstention under a named policy and constraints | Broker execution status |
| Risk engine | Deterministic sizing, margin, limits and feasibility | Model-generated authoritative values |
| Lifecycle/execution | Broker requests, acknowledgements, deals, fills, position state and reconciliation | Inferred fills from chart candles |
| Target/label | Future outcome, interpretive annotation, policy or process label with provenance | Decision-time model input |
| Dataset assembly | Task references, episode groups, admission disposition and split assignment | Untracked duplication or test-driven curation |
| Evaluation | Frozen baselines, metrics, uncertainty and safety results | Tuning against final test |
| Release/governance | Immutable manifests, approvals, limitations and supersession | Automatic phase advancement |

## 4. Canonical task architecture and overlap resolution

The original A–M capability scope remains the full coverage map. T01–T11 are the current compact task groupings for prioritization. They are not eleven mandatory standalone datasets and do not require eleven separate physical tables.

| Canonical task | Capability coverage | Primary output | Distinct boundary |
|---|---|---|---|
| T01 Market-state assessment | A + only non-duplicative parts of D | Current observable state | No forecast or action |
| T02 MTF synthesis | C | Alignment/conflict and timeframe freshness | As-of synchronization |
| T03 Outcome forecast | E | Probabilities/distribution for one target/horizon | No trade recommendation |
| T04 Scenario and setup policy | F + selected B evidence | Conditional scenarios and LONG/SHORT/NO_TRADE/WATCH/WAIT | Policy decision, not objective outcome |
| T05 Risk interpretation | G | Explanation of deterministic risk result | Calculator remains authoritative |
| T06 Lifecycle management | H + J; uses I events as evidence | Per-decision management recommendation | Sequence/policy reasoning, not execution-cost classification |
| T07 Structure-event interpretation | A + selected B | Versioned structure/liquidity event assessment | Operational definitions and reliability |
| T08 Execution-cost interpretation | I | Fill/cost/rejection assessment | Actual vs simulated evidence |
| T09 Regime/volatility | D | Distinct regime/volatility target | Merge with T01 if no distinct consumer |
| T10 News context | K | Point-in-time facts/expectations/interpretation | Licensed, timestamped archive |
| T11 Visual reasoning | L | Visual assessment tied to snapshot | Must add value over identical structured inputs |
| M Explanation layer | Cross-cutting | Evidence-linked explanation | Not an independent task by default |

### Required clarification for T06 and T08

T06 may consume broker execution events to reconstruct position state and decide what management response is justified. T08 evaluates the execution process itself: spread, slippage, fill quality, rejects, partial fills and costs. The same LifecycleEvent can be referenced by both tasks, but the target and evaluation unit differ. Do not duplicate the event or create two paraphrased copies of the same target.

### Required clarification for T01 and T09

T01 describes the current market state for downstream context. T09 is retained only if a separately defined regime/volatility taxonomy, transition target or downstream consumer adds measurable value. If it is only a renamed trend/range field, merge it into T01.

### Required clarification for A/B and T07

SMC terminology is not ground truth. T07 is a research candidate until operational definitions, confirmation/availability rules, inter-annotator or deterministic reproducibility, and incremental value are demonstrated. Do not make every named SMC concept a separate task.

## 5. Dependency graph

The dependency order is logical, not a permission to begin implementation.

`D0 Scope/semantics`
→ `D1 Source identity, rights and feasibility`
→ `D2 Canonical records and timestamp contract`
→ `D3 Integrity and immutable snapshots`
→ `D4 Feature registry and causal derivations`
→ `D5 Outcome/annotation/policy target definitions`
→ `D6 Task input/output contracts`
→ `D7 Sample admission, deduplication and episode grouping`
→ `D8 Chronological split, purge and embargo`
→ `D9 Baselines and evaluation protocol`
→ `D10 Provenance manifests and release audit`
→ `D11 Training-readiness review`

Important cross-dependencies:
- Source licensing and temporal semantics constrain every downstream layer.
- Instrument specifications are prerequisites for broker-specific risk and executable-trade targets.
- Tick/quote ordering is a prerequisite for exact first-passage and some execution claims.
- Broker events and stable IDs are prerequisites for actual lifecycle/execution claims.
- Point-in-time macro archives are prerequisites for historical news-reaction tasks.
- Image generation/renderer lineage and identical numeric snapshots are prerequisites for visual ablation.
- Label reliability and target confirmation semantics are prerequisites for sample admission.
- Split policy must account for longest overlapping target/event dependency, not just input timestamps.
- Training method selection is downstream of task value and baseline evidence, not an early architecture assumption.

## 6. Cross-document consistency audit

The following is the current desk-review result. “Aligned” means the documents express compatible principles; it does not mean the specification is frozen or empirically validated.

| Topic | Primary authority | Related documents | Current finding | Required action before freeze |
|---|---|---|---|---|
| Scope and phase gates | PROJECT_CHARTER | README, DECISION_LOG | Aligned | Keep approval gates explicit |
| Layered architecture | ARCHITECTURE | DATA_MODEL, SOURCE_FEASIBILITY, PROVENANCE | Aligned at conceptual level | Map physical boundaries only after Stage 5/source review |
| A–M vs T01–T11 | TASK_TO_SCHEMA_MAPPING | TASK_CATALOG, TASK_IO_CONTRACTS | Compatible, intentional grouping | Preserve A–M traceability in any future task removal |
| Canonical entities | DATA_MODEL_AND_SCHEMA_CONTRACTS | TASK_TO_SCHEMA_MAPPING, ARCHITECTURE | Compatible logical model | Resolve exact field types/requiredness after source feasibility |
| Forecast vs policy | FORECAST_TARGET_ENGINEERING | LABEL_SPECIFICATION, TASK_IO_CONTRACTS, SCENARIO_SPECIFICATION | Aligned | Keep event spaces and policy labels separately versioned |
| Current state vs regime | TASK_CATALOG | TASK_TO_SCHEMA_MAPPING, FEATURE_POLICY | Potential semantic overlap | Decide T01/T09 merge based on distinct definitions and consumer |
| Lifecycle vs execution | TRADE_LIFECYCLE_AND_MANAGEMENT_POLICY | TRADE_LIFECYCLE_AND_RISK_INTELLIGENCE, TASK_IO_CONTRACTS | Compatible but task boundary can be confused | Apply T06/T08 split described in this document |
| Risk authority | RISK_AND_TRADE_MANAGEMENT_SPECIFICATION | DATA_MODEL, TASK_IO_CONTRACTS, lifecycle docs | Aligned | One canonical risk result contract; avoid duplicated competing calculations |
| Labels and annotation | LABEL_SPECIFICATION | ANNOTATION_AND_LABEL_RELIABILITY, FORECAST_TARGET_ENGINEERING | Aligned conceptually | One registry authority; annotation guide is method, not another label schema |
| Sample admission | SAMPLE_VALUE_AND_SELECTION_POLICY | DATASET_COMPOSITION_AND_REDUNDANCY, DATA_QUALITY_PRINCIPLES | Compatible; complementary levels | Selection policy owns dispositions; composition owns dataset-level reporting |
| Evaluation | EVALUATION_PROTOCOL | FORECAST_TARGET_ENGINEERING, TASK_IO_CONTRACTS, sample policy | Aligned | One frozen master protocol plus task-specific metric profiles |
| Source rights and semantics | DATA_SOURCE_FEASIBILITY_FRAMEWORK | PROJECT_CHARTER, DATA_MODEL | Aligned | No source approval before evidence and explicit user approval |
| Provenance/versioning | DATASET_PROVENANCE_VERSIONING_REPRODUCIBILITY | DATA_MODEL, source/feature/label docs | Aligned | Manifest schemas and storage backend remain undecided |
| News and macro | NEWS_AND_MACRO_EVENT_INTELLIGENCE | source framework, task IO, forecast targets | Aligned | Point-in-time archive/license feasibility remains open |
| Visual modality | CHART_AND_VISUAL_INTELLIGENCE | task IO, sample selection, evaluation | Aligned | Optional modality; no core admission without ablation evidence |
| Training strategy | MODEL_LEARNING_AND_TRAINING_STRATEGY | charter, evaluation | Aligned | No model/method selection before evidence and readiness gate |

## 7. Duplication control: single source of semantic truth

The following ownership rules prevent parallel definitions from drifting:

- **Project scope, prohibitions and gate authority:** PROJECT_CHARTER.
- **Layer boundaries and causal time rules:** ARCHITECTURE.
- **Task inventory and priority:** TASK_CATALOG.
- **A–M traceability and canonical task mapping:** TASK_TO_SCHEMA_MAPPING.
- **Logical entity definitions:** DATA_MODEL_AND_SCHEMA_CONTRACTS.
- **Behavioral task inputs/outputs:** TASK_IO_CONTRACTS.
- **Feature admission and formula governance:** FEATURE_POLICY.
- **Outcome target semantics:** FORECAST_TARGET_ENGINEERING plus LABEL_SPECIFICATION; the former owns future market target mathematics, the latter owns common label lifecycle/status and leakage rules.
- **Human/interpretive annotation method:** ANNOTATION_AND_LABEL_RELIABILITY.
- **Scenario activation/invalidation semantics:** SCENARIO_SPECIFICATION.
- **Risk authority and calculation constraints:** RISK_AND_TRADE_MANAGEMENT_SPECIFICATION.
- **Lifecycle state/event/management semantics:** TRADE_LIFECYCLE_AND_MANAGEMENT_POLICY; broader task linkage is mapped in TRADE_LIFECYCLE_AND_RISK_INTELLIGENCE.
- **Candidate-level admission dispositions:** SAMPLE_VALUE_AND_SELECTION_POLICY.
- **Dataset-level composition and redundancy reports:** DATASET_COMPOSITION_AND_REDUNDANCY.
- **Quality checks and failure classes:** DATA_QUALITY_PRINCIPLES.
- **Master evaluation design:** EVALUATION_PROTOCOL; task documents add metric details without changing split governance.
- **Source dossier and admission:** DATA_SOURCE_FEASIBILITY_FRAMEWORK.
- **Immutable lineage and release manifests:** DATASET_PROVENANCE_VERSIONING_REPRODUCIBILITY.
- **Learning method selection:** MODEL_LEARNING_AND_TRAINING_STRATEGY.
- **Cross-document decisions:** DECISION_LOG.

A related document may reference an owned contract and add task-specific detail, but must not redefine its meaning independently.

## 8. Open semantic decisions — no silent defaults

These items remain intentionally unresolved:

1. Primary decision cadence and actual deployment horizon(s).
2. Minimum useful timeframe set; do not assume M1 through D1 are all needed.
3. Whether T01/T09 are distinct after precise taxonomy and consumer definitions.
4. Which structure/SMC concepts are reliable enough for supervised labels.
5. Exact forecast target families and a small justified horizon set.
6. Price-side conventions for each target and task.
7. Broker/server/account domain for risk and execution-specific tasks.
8. Whether adequate tick/quote history exists for first-passage and execution claims.
9. Whether historical broker specifications can be recovered across the target period.
10. Whether news consensus archives include genuine point-in-time snapshots and training rights.
11. Whether actual broker order/deal/position history is available and legally usable.
12. Whether chart images add incremental value over structured context.
13. Final missing/unknown/unavailable/not-applicable/ambiguous/censored enum semantics and field-level applicability.
14. Episode clustering and purge/embargo rules based on actual target horizons and source latency.
15. Effective sample adequacy and confidence interval methods for each task.
16. Storage technology, physical formats, retention and access controls.
17. Which Stage 5 schemas and outputs must be reused, adapted or excluded after its independent acceptance.

## 9. Recommended minimum core vs conditional extensions

### Minimum core candidate

Subject to source feasibility and Stage 5 compatibility:
- consistent source-identified OHLC observations;
- exact UTC/event/availability semantics;
- canonical decision-time snapshots;
- compact, non-redundant market-state and MTF context;
- a small number of explicit market-outcome targets;
- distinct policy/abstention examples only where point-in-time policy provenance exists;
- deterministic risk-result references where reliable instrument/account context exists;
- strict episode grouping, chronological splits and evaluation;
- complete provenance and quality manifests.

### Conditional extensions

Add only when source evidence and incremental-value tests justify them:
- tick-level first-passage targets;
- broker-specific execution and lifecycle learning;
- historical contract/specification time series;
- point-in-time news/consensus;
- subjective SMC taxonomy;
- chart-image reasoning;
- synthetic edge-case fixtures (software tests only, never evidence of market frequency or performance).

This ordering prioritizes robust foundational capability without making advanced modalities a prerequisite for a useful first dataset.

## 10. Phase 0 completion criteria

Phase 0 should not be declared complete merely because documents exist. Before requesting a design freeze, verify:

- Every task has one distinct consumer and target/evaluation purpose.
- Every logical entity has one semantic owner.
- All task inputs obey the same event/availability/decision-time contract.
- Outcome, policy, process-quality and realized execution labels are separate.
- Every risk/execution claim names its authoritative evidence source.
- Source-dependent capabilities are explicitly conditional.
- Duplicate, overlap and episode semantics are compatible across sampling and splitting.
- Target horizons, purge and embargo can be expressed without contradictory rules.
- Provenance/versioning covers all transformations and evaluations.
- All unresolved decisions are listed with owner and decision gate.
- The Stage 5 compatibility gate remains pending until independent completion and acceptance.
- The user reviews and explicitly approves the frozen design before any next phase.

## 11. Next design work

After this consolidation, the most valuable remaining Phase 0 task is a **field-level semantic reconciliation** of the canonical entities and universal statuses. That work should identify one authoritative definition for every shared field, enumerate required/optional/applicable-by-task fields, and build a machine-readable schema plan without yet creating operational JSON Schemas or code.

Only after that should a concise design-freeze package be prepared for user review. Source inspection, archive inspection, data acquisition, implementation and training remain separate authorization gates.


## 12. Follow-up desk audit — concrete cross-document blockers

This section records issues found by comparing the current task catalog, task I/O contracts, task/schema mapping, dataset composition, selection policy, target governance, scenario contract and reasoning contract. These are specification findings only; no data or code was inspected.

### 12.1 Resolved: T06/T08 ownership boundary

- Decision D-033 resolves the former mismatch.
- `TASK_IO_CONTRACTS.md` and `TASK_TO_SCHEMA_MAPPING.md` now define T06 as H + J management/lifecycle reasoning; verified I execution events may be consumed as context to reconstruct state.
- T08 owns I execution-quality and cost assessment targets.
- The canonical LifecycleEvent is stored once. T06 does not label slippage/fill quality; T08 does not label management actions.

**Status:** Coordinated task-map and I/O updates are committed. Remaining broker-event semantics and source feasibility remain separate open gates.

### 12.2 High: task action vocabularies need one canonical registry

Across task and scenario documents, action vocabularies vary between WAIT, WAIT_FOR_CONFIRMATION, ABSTAIN, NO_TRADE, WATCH, and management-specific actions. These are not interchangeable.

**Required resolution:** define separate, scoped enums for:
- entry-policy decision;
- scenario lifecycle;
- scenario condition state;
- management recommendation;
- broker order lifecycle;
- field/record/target quality status.

Do not create one universal status enum. Specify allowed transitions and invalid combinations. Decide whether WAIT is deprecated in favor of WAIT_FOR_CONFIRMATION or has a distinct documented meaning. This audit does not silently rename existing fields.

### 12.3 High: epistemic and quality statuses must be field-scoped

The canonical status contract must be the sole authority for distinctions such as UNKNOWN, UNAVAILABLE, NOT_APPLICABLE, PENDING, STALE, AMBIGUOUS, CENSORED, INVALID and PROVISIONAL. Some are epistemic values, some describe data quality, and some describe lifecycle/target resolution; a single undifferentiated enum would be semantically unsafe.

**Required resolution:** define status domains by entity/field, permitted transitions, whether a status may coexist with a value, and which status is required when a value is null. Explicitly separate “not yet observable” from “source unavailable” and “not applicable.” Every task contract should reference these domains, not restate or invent alternatives.

### 12.4 High: canonical timestamp and interval semantics need a single field-level contract

The architecture uses event_time, available_at, recorded_at and decision_timestamp. Time-series and event documents also need interval open/close, source timezone, bar completion, correction/revision, and decision-cutoff semantics.

**Required resolution:** specify inclusive/exclusive interval boundaries; bar timestamp convention (open- or close-stamped); UTC normalization and original timezone retention; DST/session handling; event time vs publication/receipt/availability; correction effective time vs correction availability; clock source/precision; and as-of selection for late-arriving revisions. A nominal candle close must not imply the candle was available at that instant.

### 12.5 High: decision snapshot identity and version immutability need precise rules

The architecture depends on a frozen MarketSnapshot, while source corrections and derived feature versions may arrive later.

**Required resolution:** define stable snapshot identity, content hash, source revision set, feature registry versions, as-of cutoff, snapshot creation/recording time, and supersession relationship. A later correction must create a new snapshot revision; it must not mutate the historical information set used by an earlier decision.

### 12.6 High: risk authority and policy handoff require a strict contract

The architecture correctly reserves authoritative sizing and constraints for deterministic services. Task contracts must consistently distinguish a model's interpretation/request from a calculator's result and from broker acknowledgement.

**Required resolution:** define request/result IDs, calculator and instrument-spec versions, account-currency conversion references, quote timestamp/side, cost assumptions, volume-step rounding, post-rounding recalculation, stale-result behavior, and fail-closed status. A proposed risk change requires a new calculation; model prose cannot override a rejected result.

### 12.7 Medium: T01/T09 remain a deliberate conditional merge

The task catalog and audit agree that T09 is retained only if its taxonomy, target or consumer is distinct from T01. It must not be counted as an independent task merely because volatility fields are present.

**Required resolution:** compare the exact T01 and T09 output/target definitions and downstream consumers. If no independent value is defensible, merge T09 into T01 and preserve A–M traceability. This is not yet an empirical decision.

### 12.8 Medium: T07/SMC and T11/visual remain gated extensions

SMC/structure interpretation and chart-image reasoning have clear candidate boundaries, but their admission depends on reproducibility, source alignment, reviewer agreement and incremental value.

**Required resolution:** do not promote either into the minimum core by default. For T07, freeze event confirmation and independent reproducibility. For T11, require image-renderer lineage, exact snapshot linkage, and structured-only versus structured-plus-image ablation. No image-only future information or hidden-order claims.

### 12.9 Medium: news, execution and account history are conditional on provenance

T08/T10 and account/risk tasks require evidence that cannot be inferred from ordinary OHLC. Provider marketing claims or a small sample do not establish historical availability or rights.

**Required resolution:** maintain task-specific source dossiers. If point-in-time news, historical instrument specifications, bid/ask/tick, or broker-confirmed order/deal history cannot be proven, remove or narrow the dependent target rather than substituting generic assumptions.

### 12.10 Medium: split and episode policy must be derived from target dependencies

The current documents correctly reject random splitting and fixed universal sampling intervals, but the exact episode clustering, purge and embargo algorithms remain open.

**Required resolution:** once target horizons, late-arrival windows and event confirmation rules are frozen, define a split dependency graph. Group duplicates and overlapping target episodes before assigning splits. Purge/embargo must cover the maximum relevant target/event dependency and source-latency uncertainty, not an arbitrary fixed number of bars.

### 12.11 Medium: task-level schema ownership is not yet machine-checkable

The documents describe canonical entity ownership and task-specific references, but a field-level inventory is still required before JSON Schema or Parquet contracts are frozen.

**Required resolution:** create one field registry with entity, field path, semantic owner, type/unit, requiredness, applicability, value/status relationship, timestamp role, source/derivation, version and consuming tasks. Then generate/review task projections from that registry; do not hand-maintain competing field definitions.

## 13. Consolidated freeze blockers

Phase 0 cannot be declared design-frozen until the following are resolved and reviewed:
1. Remaining scoped enum/status transition rules (T06/T08 ownership is resolved by D-033).
2. Scoped action/status enums and transition rules.
3. Field-level null/missing/unknown/applicability semantics.
4. Canonical timestamp, interval, correction and as-of rules.
5. Snapshot identity, immutability and supersession.
6. Risk request/result and policy handoff contract.
7. T01/T09 merge decision.
8. Task-to-field registry and task projection consistency.
9. Target-dependent episode, purge and embargo rules.
10. Stage 5 compatibility after independent acceptance.
11. Source feasibility and rights after explicit authorization.
12. User review and explicit design-freeze approval.

## 14. Recommended next work item

The next highest-value design task is a **Canonical Field Registry and Semantic Reconciliation**. It should inventory existing fields from the logical data model and task contracts, map each to one semantic owner, identify collisions and unresolved requiredness/status rules, and propose a minimal task projection.

Do not generate operational JSON Schemas, data tables, sample records, labels or code as part of that reconciliation. A human-readable field registry and conflict report are sufficient for Phase 0.

## 15. Audit conclusion

The conceptual architecture is coherent and consistently prioritizes causal evidence, target separation, deterministic risk authority, provenance and information efficiency. However, the documents are not yet ready to be frozen: the blockers in Section 13 must be reconciled first. The presence of extensive documentation is not evidence of source feasibility, label reliability, empirical usefulness, or implementation correctness.

No source archive has been inspected; no market data, sample, label, benchmark, pipeline or model has been produced. The separate Stage 5 project and AURORA QUANT remain untouched. This audit does not authorize progression to another phase.
