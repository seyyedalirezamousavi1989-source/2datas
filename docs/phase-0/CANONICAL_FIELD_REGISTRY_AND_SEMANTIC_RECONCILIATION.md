# Canonical Field Registry and Semantic Reconciliation — Phase 0

## 1. Status and authority

Status: **provisional registry v0.1; not frozen**.

This document inventories the shared fields needed by the logical entities and prioritized tasks. It is a semantic ownership and dependency registry, not a physical database design, JSON Schema, migration, implementation, or authorization to inspect or generate data.

Semantic owners:
- DATA_MODEL_AND_SCHEMA_CONTRACTS.md: canonical entities, relationships and record envelope.
- CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md: field meanings, timestamps, units, price basis, scoped status domains and null/value rules.
- TASK_IO_CONTRACTS.md: task behavior and input/output boundaries.
- TASK_TO_SCHEMA_MAPPING.md: A–M to T01–T11 mapping.
- Domain specifications: source, feature, target, scenario, risk, lifecycle, evaluation and visual semantics.

This registry does not override an owner document. Conflicts must be resolved in the decision log and all affected owner documents updated together.

## 2. Registry rules

1. Every field has exactly one semantic owner.
2. Other entities/tasks reference the canonical field or define a clearly scoped projection; they do not redefine its meaning.
3. Requiredness is conditional on entity/task applicability. This registry does not imply every field appears in every record.
4. A value's availability time is when it became defensibly knowable, not when a file was later created.
5. Future-derived targets and post-decision events never enter decision-time model inputs.
6. Units, price basis, currency and instrument specification are explicit wherever relevant.
7. Unknown, unavailable, not applicable, not yet observable, stale, ambiguous, invalid and censored remain distinct.
8. A field must serve a named task, integrity rule, provenance requirement or evaluation purpose. Ease of collection is not sufficient reason to include it.

## 3. Shared record envelope

| Field | Semantic owner | Meaning | Applicability |
|---|---|---|---|
| record_type | Data model | Canonical entity discriminator | Every typed record |
| record_id | Data model | Stable opaque record identity | Every record; immutable after publication |
| schema_version | Schema registry | Structural contract version | Every released serialized record |
| created_at | Provenance | Time this system created the record | System-created records; UTC |
| provenance_refs | Provenance | References to source, definition, transformation, policy or upstream records | Mandatory for derived, labeled, annotated, assembled and evaluated artifacts |
| status | Entity-specific status owner | Lifecycle/validity state in exactly one scoped domain | Where entity contract defines a status |
| quality_flags | Quality registry | Non-exclusive diagnostic flags | Optional; every flag must be defined |
| supersedes_record_id | Revision contract | Prior record explicitly superseded by this revision | Corrections/revisions only |
| content_hash | Artifact registry | Integrity hash of canonical serialized content | Optional until canonical serialization is frozen |

## 4. Source, instrument and time fields

| Field | Semantic owner | Meaning | Applicability |
|---|---|---|---|
| source_id | Source registry | Provider/origin identity | Source-derived evidence |
| feed_id | Source registry | Distinct feed/server/venue identity | When feed differences matter |
| source_record_id | Source adapter | Provider-native record identity | If supplied by provider |
| source_symbol | Source adapter | Exact provider/broker symbol string | Symbol-specific records |
| instrument_id | Instrument registry | Canonical instrument identity | Instrument-related evidence |
| specification_id/version | Instrument specification registry | Effective-dated contract/specification | Price-unit, contract, risk and execution calculations |
| valid_from/valid_to | Effective-dated reference contract | Interval during which mapping/specification applies | Time-varying mappings/specifications |
| license_id/rights_scope | Source governance registry | License and permitted use/training/redistribution | Before source admission to a release |
| source_timestamp | Source adapter | Original provider timestamp, timezone and precision semantics | When supplied; preserve original representation |
| event_time | Source/event contract | When represented event occurred | Time-dependent observations/events |
| interval_start/interval_end | Bar/interval contract | Start and end of represented interval | Bars and interval aggregates |
| received_at | Ingestion contract | When receiving system actually received record | When receipt telemetry exists |
| available_at | Causal-time contract | Earliest defensible time information was available to decision system | Mandatory for decision-time inputs |
| ingested_at | Provenance | When durably recorded in this project | Ingested records |
| decision_timestamp | Snapshot/task contract | Frozen cutoff for eligible inputs | Forecast, scenario, policy and decision examples |
| confirmed_at | Event/label definition | When condition/target became confirmable | Conditional; never substitute event time by assumption |
| expires_at | Entity-specific validity contract | End of forecast/scenario/decision/request validity | Time-bounded entities |
| revision_available_at | Revision/causal-time contract | When correction/revision became knowable | Revised evidence |

Unresolved time decisions: interval inclusivity, provider bar timestamp convention, clock synchronization tolerance, source latency reconstruction, DST/session calendar, late-arrival selection and correction semantics. These require source evidence; no default assumptions are approved.

## 5. Market observations, features and snapshots

| Field | Semantic owner | Meaning | Applicability |
|---|---|---|---|
| observation_id/type | Market observation contract | Stable identity and scoped type: quote, tick, bar or registered event | Every market observation |
| bid_price/ask_price | Quote contract | Observed bid and ask | Only when supplied by source |
| mid_price | Quote derivation contract | Derived midpoint under registered formula | Only with valid bid and ask |
| open/high/low/close_price | Bar contract | OHLC under declared price basis | Valid bar |
| price_basis | Price semantics registry | BID/ASK/MID/LAST/provider-defined or other registered basis | Every price-bearing observation, feature and target |
| tick_size/digits/point_value | Instrument specification | Effective precision and unit conversion facts | Where relevant and sourced |
| volume_value/unit/semantics | Observation contract | Quantity/count and exact meaning | When supplied; tick count, traded volume and lots are distinct |
| bar_completion_status | Bar/timeframe contract | Completed, partial or unavailable | Timeframe snapshot references |
| source_quality_status | Observation validation contract | Source record validity | Source observations |
| feature_id/version | Feature registry | Identity/version of derived feature definition | Every FeatureValue |
| feature_value_id | Feature value entity | Identity of one derived value in context | Every FeatureValue |
| feature_value | Feature definition | Typed output defined by the feature | Derived feature only; final schemas should avoid untyped generic values |
| feature_unit | Feature definition | Unit, scale and normalization | Numeric features |
| dependency_refs | Feature registry/provenance | Exact source/feature dependencies | Derived values |
| feature_available_at | Feature availability contract | Earliest time computed feature was available | Causal feature use |
| validation_status | Feature admission registry | Proposed/tested/accepted/rejected/retired admission state | Feature definition; separate from field availability |
| snapshot_id/version | Snapshot contract | Immutable point-in-time context identity and assembly version | Task decision examples |
| snapshot_hash | Snapshot provenance | Hash of canonical ordered references/content | Optional until canonical serialization frozen |
| timeframe | Timeframe registry | Exact duration/calendar semantics | Timeframe-scoped evidence |
| timeframe_state_refs | Snapshot contract | References to bars/features and completion/availability state | Only timeframes consumed by task |
| snapshot_quality_status | Snapshot validation contract | Whether snapshot is usable under declared criteria | Snapshot |

A snapshot is immutable. A late correction or recalculation creates a new snapshot/revision linked to the prior one; it cannot rewrite the information set of a historical decision.

If a bar touches both target and stop barriers and no finer evidence resolves order, the outcome remains ambiguous/censored under the target definition. Never infer intrabar sequence.

## 6. Forecast, target, label, scenario and decision fields

| Field | Semantic owner | Meaning | Applicability |
|---|---|---|---|
| target_id/version | Target registry | Exact future event/outcome definition | Forecasts and outcome labels |
| event_space_id/version | Probability registry | Defined event partition for a probability vector | Class probabilities |
| horizon_id/definition | Target registry | Exact future horizon and cutoff semantics | Horizon-dependent target |
| forecast_id | Forecast entity | Stable forecast identity | Forecast records |
| event_probability | Forecast contract | Probability of one named event | Requires target, event, horizon and calibration context |
| class_probabilities | Forecast contract | Probabilities over mutually exclusive/exhaustive event partition | Only for a declared partition |
| prediction_interval/quantile_forecast | Forecast contract | Distributional interval/quantile estimate | When defined and evaluated |
| calibration_version | Calibration registry | Version of calibration method/data | Before calling probability calibrated |
| label_id/version | Label registry | Exact outcome/policy/process label definition | Released labels |
| label_status | Label resolution contract | Pending/resolved/ambiguous/censored/unavailable/invalid | Labels only |
| label_confirmed_at | Label definition | When future-derived label became determinable | Future-derived labels; never model input |
| label_value | Label definition | Typed target value | Only when status/definition permits |
| policy_id/version | Policy registry | Exact policy semantics | Policy/action labels and decisions |
| scenario_set_id | Scenario contract | Scenario set for one snapshot/task definition | When scenarios exist |
| scenario_id/revision_id | Scenario contract | Stable scenario and immutable revision identity | Each scenario revision |
| scenario_type | Scenario taxonomy | Registered conditional path type | Scenario |
| trigger_condition_refs/invalidation_condition_refs | Scenario condition registry | Observable activation/invalidation predicates | Falsifiable scenarios |
| scenario_expires_at | Scenario validity contract | Declared scenario expiry | Time-bounded scenarios |
| scenario_status | Scenario lifecycle contract | Scenario-specific lifecycle state | Scenario only |
| decision_id | Trade decision entity | Stable policy decision identity | Decision records |
| decision_class | Entry policy registry | LONG/SHORT/NO_TRADE/WATCH/WAIT_FOR_CONFIRMATION/ABSTAIN | Entry policy decisions only |
| selected_scenario_refs | Decision contract | Scenarios selected/considered by policy | When applicable; may be empty on abstention |
| reason_code_refs | Policy/reason registry | Typed action/abstention reasons | Auditable policy decisions |
| decision_expires_at | Decision policy | End of action validity | Time-bounded decisions |

Forecast probabilities, market outcome labels, policy labels and realized P&L are distinct. Profit is not a proxy label for decision correctness. Do not normalize scenario scores into probabilities.

## 7. Account, risk, execution and lifecycle fields

| Field | Semantic owner | Meaning | Applicability |
|---|---|---|---|
| account_id | Account reference registry | Pseudonymous account identity | Account-specific risk; never credentials |
| account_currency | Account reference registry | Currency of account figures | Monetary risk calculations |
| equity/balance/free_margin/used_margin | Verified broker/account state | Broker-reported account values at a timestamp | Only if calculation uses them; source/time/currency required |
| risk_fraction/risk_amount | Risk policy/calculation | Requested risk fraction and derived monetary risk | Risk requests/results; distinguish input from output |
| entry_reference_price/stop_reference_price | Risk request | Intended prices with explicit side/basis | Request assumptions, not confirmed fills |
| volume_requested/volume_permitted | Risk engine | Requested versus rounded/allowed size | Risk calculation; unit/step/spec required |
| margin_estimate/loss_estimate | Risk engine | Deterministic result under named assumptions | Not guaranteed realized loss under gaps/slippage |
| risk_request_id/risk_result_id | Risk engine contract | Immutable request/result identities | Risk calculations |
| risk_engine_version | Risk engine registry | Calculator version | Authoritative risk result |
| constraint_status | Risk policy | Permitted/rejected/recalculation-required | Policy constraint domain |
| order_id/deal_id/position_id | Broker lifecycle identity mapping | Broker-native/canonical identities | Preserve broker and mapping identity |
| order_request_time/broker_ack_time/fill_time | Execution event contract | Distinct request, acknowledgement and fill times | Relevant broker events |
| fill_price/fill_volume/commission/swap/slippage/spread | Execution evidence contract | Observed execution and cost facts | Only with evidence; distinguish modeled assumptions |
| event_id/event_sequence/event_type | Lifecycle event contract | Immutable event identity, order and type | Lifecycle events |
| state_before/state_after | Lifecycle transition contract | Verified state transition | Reconstructible transitions |
| reconciliation_status | Broker reconciliation contract | Agreement/uncertainty between local and broker state | Management/execution requiring verified state |

Risk and broker lifecycle specifications remain authoritative for formulas, state transitions and broker-specific mappings. The model cannot author authoritative sizing or infer fills.

## 8. Task projection matrix

Tasks consume references to canonical fields; they do not own duplicate meanings.

| Task | Minimum projection | Output/target owner | Exclusions |
|---|---|---|---|
| T01 Market state | Snapshot/timeframe refs, approved features, quality | Market-state task | Future outcomes, trade action |
| T02 MTF synthesis | Snapshot, timeframe, interval/completion/availability refs | MTF task | Future HTF bars, forced consensus |
| T03 Forecast | Snapshot/features, target/event-space/horizon refs | Forecast + outcome target | Future labels in input; generic confidence |
| T04 Scenario/policy | Snapshot/evidence, scenario refs, optional forecast/risk refs | Scenario + trade decision + policy label | Scenario as execution fact |
| T05 Risk interpretation | Immutable risk request/result and engine/spec/account/quote refs | Risk explanation | Model-authored sizing |
| T06 Management/lifecycle | Snapshot, verified position/order state, lifecycle event refs, fresh risk result | Management recommendation/process target | Execution-quality targets owned by T08 |
| T07 Structure event | Bars/quotes, feature and event-definition/confirmation refs | Structure event target | Hindsight confirmation, unverified SMC |
| T08 Execution quality | Quote/order/deal/fill events, spec and cost refs | Execution assessment target | Management action labels owned by T06 |
| T09 Regime/volatility | Snapshot and non-redundant feature refs | Regime target only if distinct from T01 | Duplicate state labels |
| T10 News context | Licensed point-in-time news/event refs and snapshot | Context assessment | Future/revised news as known |
| T11 Visual reasoning | Exact snapshot, chart artifact, renderer/annotation refs and structured context | Visual assessment | Unsynchronized/future-revealing chart |

T06 may consume verified I/execution events as context to reconstruct current state, but does not own execution-quality targets. T08 owns execution-quality/cost assessment and may reference order context without owning management recommendations. Each canonical LifecycleEvent is stored once.

## 9. Reconciliation findings

| ID | Finding | Proposed resolution | Status |
|---|---|---|---|
| R-01 | T06/T08 previously overlapped on I | T06 owns H+J management/lifecycle; I events are context. T08 owns I execution-quality/cost targets | Proposed coordinated update |
| R-02 | Malformed token SUPERSEDED) in canonical status contract | Correct spelling to SUPERSEDED and validate scoped tokens | Typographical fix |
| R-03 | Scenario documents define richer lifecycle than abbreviated status table | Scenario owner publishes complete lifecycle and transitions; shared status contract references it | Open |
| R-04 | Scenario condition uses UNKNOWN without a dedicated condition state domain | Define TRUE/FALSE/UNKNOWN/STALE/INVALID condition-evaluation domain under scenario owner | Open |
| R-05 | Risk result status may be confused with policy permission | Risk engine owns calculation status; policy owns permit/reject/recalculate decision | Open |
| R-06 | Interval/bar timestamp semantics lack source-backed final convention | Defer until source feasibility; no default assumption | Open |
| R-07 | Generic envelope status may hide entity-specific domains | Every entity declares exactly one scoped status domain | Proposed |
| R-08 | Feature availability may be confused with admission | Keep field availability separate from feature validation_status | Accepted by semantic owner |
| R-09 | Probability vectors may mix events | Bind vector to one event space and target version | Accepted by semantic owner |
| R-10 | Null may be misread as missing semantics | Define nullability and status mapping per field | Proposed |

## 10. Freeze blockers and non-authorization

Before this registry is frozen:
1. Inventory every field in all canonical entities, including news, visual, annotation, evaluation and release records.
2. Assign one semantic owner and a task consumer or governance purpose to every field.
3. Reconcile every entity's scoped status domain and transitions.
4. Reconcile all task projections against this registry.
5. Source-back time, units, price basis, currency and nullability rules.
6. Update T06/T08 and T01/T09 decisions in all owner documents.
7. Independently audit Stage 5 deliverables after their acceptance.
8. Establish source feasibility/licensing after explicit authorization.
9. Obtain explicit user approval for design freeze.

Exact serialization types, precision, physical storage, final timeframe/horizon, source-specific latency and numeric thresholds remain deferred.

This document does not authorize opening XAUUSD.zip, inspecting/downloading market data, creating samples, operational JSON Schemas, labels, datasets, pipelines, benchmarks, training, changes to AURORA QUANT, or changes to the separate Stage 5 project.

The optimization target remains **minimum sufficient fields and examples with maximum verified information value**, not maximum schema size or row count.
