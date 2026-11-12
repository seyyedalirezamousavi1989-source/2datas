# Integrated Architecture, Dependency Map and Consistency Audit — Phase 0

## 1. Status and authority

This document consolidates the current Phase 0 design into one navigable architecture and records cross-document overlap, unresolved semantics and phase dependencies.

**Mixed status: design audit plus first implementation/source audit.** The user-provided XAUUSD.zip has been inspected, structurally audited and normalized into six local timeframe partitions (681,227 rows total). The repository now contains the ingestion/normalization code, tests, initial source audit and normalized manifest. No market features, outcome labels, benchmark or model has yet been produced. The separate `datas` repository and AURORA QUANT remain untouched; 2datas is self-contained and has no cross-repository dependency.

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
| Layered architecture | ARCHITECTURE | DATA_MODEL, SOURCE_FEASIBILITY, PROVENANCE | Aligned at conceptual level | Map physical boundaries after this project's own source-feasibility review |
| A–M vs T01–T11 | TASK_TO_SCHEMA_MAPPING | TASK_CATALOG, TASK_IO_CONTRACTS | Compatible, intentional grouping | Preserve A–M traceability in any future task removal |
| Canonical entities | DATA_MODEL_AND_SCHEMA_CONTRACTS | TASK_TO_SCHEMA_MAPPING, ARCHITECTURE | Compatible logical model | Resolve exact field types/requiredness after source feasibility |
| Forecast vs policy | FORECAST_TARGET_ENGINEERING | LABEL_SPECIFICATION, TASK_IO_CONTRACTS, SCENARIO_SPECIFICATION | Aligned | Keep event spaces and policy labels separately versioned |
| Price/structure state vs volatility regime | TASK_CATALOG | TASK_TO_SCHEMA_MAPPING, TASK_IO_CONTRACTS, FEATURE_POLICY | Provisional semantic boundary defined; T09 remains conditional | Require source coverage and incremental-value evidence before T09 admission |
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
17. Which independently licensed source feeds and broker-specific records are admissible under 2datas contracts.

## 9. Recommended minimum core vs conditional extensions

### Minimum core candidate

Subject to this project's source feasibility review:
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
- This project is self-contained and has no cross-repository Stage 5 compatibility gate.
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

### 12.2 Resolved provisionally: scoped action and lifecycle domains

- SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md now defines separate domains for entry decision, scenario lifecycle/assessment, condition evaluation, management action, order lifecycle, deal/fill events, position state, reconciliation, risk calculation, policy constraint, artifact/release, annotation, field availability, record validation and label resolution.
- WAIT is deprecated as a standalone entry action and management action. WAIT_FOR_CONFIRMATION is reserved for a named pending entry trigger; management uses NO_ACTION or ABSTAIN as defined.
- Scenario UNRESOLVED is an assessment value, not a lifecycle state.
- T04 and T06 task I/O and scenario/lifecycle owner documents have been aligned to the scoped vocabularies.

**Remaining gate:** broker-native state mapping and every entity's field-level status binding require source evidence and final schema review. This is a provisional design resolution, not a frozen wire contract.

### 12.3 Partially resolved: field-scoped epistemic and quality statuses

The canonical semantic contract and scoped enum governance now separate field availability, label resolution, record validation, feature admission, scenario lifecycle/assessment, condition evaluation, order/position/reconciliation, risk calculation/permission, annotation and release states. Null/value consistency principles are defined centrally.

**Remaining gate:** bind every field in every canonical entity to exactly one status domain, finish field-by-field nullability/value rules, and verify all owner/task documents reference rather than duplicate these definitions. This requires the complete field inventory and final schema review.

### 12.4 Resolved provisionally: internal temporal and interval semantics

- POINT_IN_TIME_INTERVAL_AND_SNAPSHOT_REVISION_CONTRACT.md defines event/valid, knowledge/availability and processing time separately, with decision_timestamp as the as-of cutoff.
- Internal normalized intervals are UTC half-open [start,end); raw provider timestamp convention is retained separately.
- Completed/partial bars, MTF as-of selection, late arrivals, correction availability, clock uncertainty, news publication and broker event timing have explicit conceptual rules.

**Remaining gate:** provider/broker bar construction, source latency, historical availability, clock precision, session/DST calendars and correction archives require source evidence. No source-specific convention is assumed or frozen.

### 12.5 Resolved provisionally: immutable snapshot and revision semantics

The temporal contract defines a MarketSnapshot as an immutable point-in-time selection with exact source/feature revisions, as-of cutoff, materialization time, canonical reference set and content hash after serialization is frozen. Corrections create linked snapshot revisions; they do not rewrite the original decision context.

**Remaining gate:** actual snapshot identity/hash construction and historical replay must be tested against approved source revision/availability evidence before any implementation or release.

### 12.6 Resolved provisionally: deterministic risk and policy handoff

- DETERMINISTIC_RISK_AND_POLICY_HANDOFF_CONTRACT.md now defines the sequence from proposal to immutable request, deterministic calculation, policy constraint evaluation, entry decision, separately authorized order submission, broker evidence and reconciliation.
- It separates risk_calculation_status from constraint_outcome and defines freshness, expiry, mandatory recalculation and fail-closed behavior.
- T04/T05/T06 consumption boundaries are specified.

**Remaining gate:** verify the actual deterministic engine interface, formulas, broker-specific instrument specifications, conversion/cost sources and authorization controls after source feasibility and the relevant 2datas review gate. No implementation is authorized by this design contract.

### 12.7 Resolved provisionally: T01/T09 semantic boundary

- T01 now owns price/structure state: trend, range, structural transition and indeterminate assessment. Volatility features may be contextual inputs but are not T01 volatility-regime targets.
- T09 now owns volatility-regime characterization: volatility state, expansion/contraction, clustering and volatility transitions.
- A–M mapping now assigns A to T01 and D to T09; T02 may consume T09 context where useful.
- Shared causal features are allowed, but duplicate labels/task rows are not.

**Remaining gate:** T09 remains a conditional extension. Retain it in a release only if source coverage, effective sample size, target reliability and incremental downstream value beyond T01/simple volatility baselines are demonstrated. Otherwise defer/merge without losing D traceability.

### 12.8 Medium: T07/SMC and T11/visual remain gated extensions

SMC/structure interpretation and chart-image reasoning have clear candidate boundaries, but their admission depends on reproducibility, source alignment, reviewer agreement and incremental value.

**Required resolution:** do not promote either into the minimum core by default. For T07, freeze event confirmation and independent reproducibility. For T11, require image-renderer lineage, exact snapshot linkage, and structured-only versus structured-plus-image ablation. No image-only future information or hidden-order claims.

### 12.9 Medium: news, execution and account history are conditional on provenance

T08/T10 and account/risk tasks require evidence that cannot be inferred from ordinary OHLC. Provider marketing claims or a small sample do not establish historical availability or rights.

**Required resolution:** maintain task-specific source dossiers. If point-in-time news, historical instrument specifications, bid/ask/tick, or broker-confirmed order/deal history cannot be proven, remove or narrow the dependent target rather than substituting generic assumptions.

### 12.10 Medium: split and episode policy must be derived from target dependencies

The current documents correctly reject random splitting and fixed universal sampling intervals, but the exact episode clustering, purge and embargo algorithms remain open.

**Required resolution:** once target horizons, late-arrival windows and event confirmation rules are frozen, define a split dependency graph. Group duplicates and overlapping target episodes before assigning splits. Purge/embargo must cover the maximum relevant target/event dependency and source-latency uncertainty, not an arbitrary fixed number of bars.

### 12.11 Partially resolved: task-level field ownership and nullability

- CANONICAL_FIELD_REGISTRY_AND_SEMANTIC_RECONCILIATION.md provides the provisional shared field inventory and task projection matrix.
- SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md owns scoped enum values and transition rules.
- FIELD_STATUS_BINDING_AND_NULLABILITY_MATRIX.md binds core canonical entities to requiredness, scoped status and value/null rules.
- DATA_MODEL_AND_SCHEMA_CONTRACTS.md references the scoped status authority and separates value origin (observed/derived/estimated) from status.

**Remaining gate:** complete conditional news, visual, annotation, evaluation, dataset-release and training-run fields; validate every core field binding against the final task projections and source evidence. Exact types, precision and wire-level nullability remain unfrozen. No operational schema should be generated until this is reviewed.

### 12.12 Resolved provisionally: target portfolio and redundancy boundary

- TARGET_PORTFOLIO_AND_REDUNDANCY_DECISION.md reconciles F01–F08 with Y01–Y06.
- F01/Y01 fixed-horizon return is the primary market-outcome candidate; F02/Y02 is a derived directional projection, not an independent sample family by default.
- F03/Y03 is conditional on intrabar resolution; F04/Y04 is a sidecar unless a distinct management consumer exists; F05 is not duplicated by default; F06/F07 remain conditional; F08 is excluded from the initial market-forecast core.
- Policy, execution, process-quality and post-trade outcomes remain separate namespaces.

**Remaining gate:** exact horizons, thresholds, source/price conventions, sample sufficiency and target-specific split dependencies remain open. This is a provisional portfolio decision, not empirical target acceptance.

### 12.13 Resolved provisionally: target dependencies and split grouping

- TARGET_DEPENDENCY_EPISODE_AND_SPLIT_CONTRACT.md defines snapshot/decision/target/episode/dependency/duplicate/lifecycle identities and target-specific future dependency windows.
- Derived projections inherit parent dependency groups; overlapping future paths are grouped before chronological split assignment.
- Purge/embargo is derived from actual target horizons, confirmation delays and source revision/availability bounds; no arbitrary fixed bar count is approved.

**Remaining gate:** exact horizons, source-latency/revision bounds, grouping thresholds, chronological dates, purge/embargo durations and effective independent sample counts remain unfrozen until source feasibility and target-specific review.

## 13. Consolidated freeze blockers

Phase 0 cannot be declared design-frozen until the following are resolved and reviewed:
1. Field-by-field status-domain binding and null/value rules across every canonical entity.
2. Canonical timestamp, interval, correction, clock uncertainty and as-of rules, supported by actual source evidence.
3. Snapshot identity, immutable revision and supersession contract at field-level.
4. Risk request/result and policy handoff, including authoritative engine/interface verification.
5. T01/T09 merge decision based on distinct target and downstream consumer.
6. Complete task-to-field registry and task projection consistency.
7. Target-dependent episode clustering, purge and embargo rules after horizons are selected.
8. Source provenance, rights, timezone and broker/bar semantics for the supplied XAUUSD archive.
9. Source feasibility, point-in-time availability and rights after explicit authorization.
10. User review and explicit design-freeze approval.

Scoped enum/action governance and the T06/T08 boundary are now documented provisionally; this does not freeze wire values, broker mappings or field-level bindings.

## 14. Active implementation roadmap

The next work is implementation-led, not another documentation-only freeze loop.

1. **Source semantics dossier:** resolve broker/provider identity, server timezone/DST, MT5 bar timestamp convention, symbol digits/point size, session calendar and source-use rights.
2. **Coverage and gap classification:** distinguish normal market closures/holidays from genuine missing intervals; explain partial child groups at timeframe boundaries.
3. **Canonical storage hardening:** validate deterministic partition rebuilds, source row lineage, schema compatibility and checksums; retain raw archive outside Git.
4. **Feature validity and broker time:** validate Alpari server clock, DST and bar convention; verify feature availability timestamps; add source-aware MTF synchronization.
5. **Feature research:** evaluate candidate structure, FVG, liquidity, OB, displacement and volatility features for stability, redundancy and incremental value.
6. **Targets and splits:** define compact market-outcome targets, ambiguity/censoring and episode-aware chronological splits.
7. **Independent QC and acceptance:** publish limitations and reject targets/features that do not add measurable value.
5. **Target implementation:** start with fixed-horizon market outcomes, then barrier/MFE-MAE only where source resolution supports them; preserve ambiguity and censoring.
6. **Episode-aware splits and baselines:** construct chronological folds after target horizons and source-latency dependencies are frozen.
7. **Independent QC and acceptance:** publish limitations and reject targets that do not add measurable value.

The initial MTF aggregation result is encouraging: every complete child group matched native parent OHLC and tick volume across M5→M15→M30→H1→H4→D1. This is internal consistency evidence only; it does not resolve source timezone, broker identity or timestamp semantics.

## 15. Audit conclusion

The conceptual architecture and initial executable data foundation are in place. Broker-independent symbol/timeframe ingestion, a conservative broker clock resolver and an initial causal price-action feature engine have been implemented. Source semantics, Alpari server verification, cross-broker validation, feature validity, target validation, rights and full dataset acceptance remain open. The presence of extensive documentation is not evidence of source feasibility, label reliability, empirical usefulness, or implementation correctness.

The supplied archive has been inspected and a normalized base-bar dataset has been generated locally. Feature-generation code and candidate definitions exist, but the updated feature engine has not yet been run across the full archive or independently validated. No outcome labels, benchmark or model has been produced. The separate `datas` repository and AURORA QUANT remain untouched. Dataset admission remains pending source semantics and rights review.
