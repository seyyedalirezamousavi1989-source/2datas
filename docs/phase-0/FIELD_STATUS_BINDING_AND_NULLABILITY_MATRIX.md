# Field Status Binding and Nullability Matrix — Phase 0

## 1. Status

**Provisional design matrix v0.1; not frozen.** This is a human-readable binding aid for the logical model. It is not JSON Schema, a physical schema, a migration, an implementation or permission to inspect/process data.

Authorities:
- Canonical entity/relationship owner: DATA_MODEL_AND_SCHEMA_CONTRACTS.md.
- Field semantics and general null/value rules: CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md.
- Enum values/transitions: SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md.
- Field ownership/task projection: CANONICAL_FIELD_REGISTRY_AND_SEMANTIC_RECONCILIATION.md.
- Task input/output boundaries: TASK_IO_CONTRACTS.md.

This matrix binds existing concepts; it does not authorize adding fields simply because a status is available.

## 2. Global binding rules

1. Record-level validation status and field-level availability status are separate. A record can be valid while an optional field is unavailable.
2. Do not attach an availability enum to every field by default. Use it where the value can legitimately be known, unknown, stale, unavailable, not applicable, not yet observable, ambiguous or invalid.
3. If a required field is absent, the record cannot be admitted as a complete record of that type. Quarantine/reject it or represent a distinct incomplete record type only if that type has a named consumer.
4. If an optional field is absent, record the correct scoped availability status when that absence matters to downstream behavior. Otherwise omit the field; do not add decorative nulls.
5. A null never explains itself. It is allowed only where the field contract maps it to a specific status.
6. KNOWN requires a typed value. UNKNOWN/UNAVAILABLE/NOT_APPLICABLE/NOT_YET_OBSERVABLE do not permit fabricated values. STALE may retain a historical value only with its original timestamp and freshness. AMBIGUOUS must preserve alternatives or an explicit ambiguity object. INVALID values are quarantined.
7. A status must not be copied into the value itself or confused with record validation, lifecycle or policy action.
8. observed/derived/estimated/simulated are value-origin descriptors, not statuses.
9. Post-decision targets, realized outcomes and future confirmation fields never enter decision-time inputs.
10. Exact serialization types, precision and per-task requiredness remain pending source feasibility and Stage 5 compatibility.

## 3. Core entity matrix

### 3.1 SourceDefinition and InstrumentSpecification

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| source_id, feed_id | Required for source-derived evidence | No field-level availability status; absence invalidates source lineage |
| source_symbol | Required for symbol-specific source records | Preserve exact provider string; never infer from canonical instrument_id |
| license_id, rights_scope | Required before release/training use | If rights cannot be established, source admission is blocked; do not treat null as permission |
| instrument_id | Required for instrument-specific records | Missing mapping is unresolved source identity; do not guess |
| specification_id/version | Required when price, contract, risk or execution semantics depend on it | No valid authoritative calculation if specification is missing, stale or not effective at event time |
| valid_from/valid_to | Required for effective-dated mappings/specifications | Must obey the interval contract; source-dependent interval conventions remain open |

Admission state of a source or specification must be defined by its governance owner; do not reuse order, label or field-availability status.

### 3.2 MarketObservation

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| observation_id, observation_type | Required | Missing means invalid record identity/type |
| source_id, feed_id, instrument_id, source_symbol | Required for source-derived observations | Missing lineage blocks admission |
| event_time | Required for time-dependent observation | If source event time cannot be established, preserve source timestamp/limitation and do not admit to time-sensitive decision input |
| source_timestamp | Required when provider supplies it | If absent at source, omit; do not fabricate |
| received_at, ingested_at | Required when actual telemetry exists | Do not backfill as if observed historically |
| available_at | Mandatory for any decision-time input | If unknown, the observation is not causally admissible to a decision snapshot |
| price_basis | Required for every price-bearing observation | Missing basis invalidates price interpretation |
| bid_price/ask_price | Required only for a two-sided quote record | If feed supplies only one side, mark the other side UNAVAILABLE; do not synthesize it |
| open/high/low/close_price | Required for a complete OHLC bar | Partial bar must be explicitly typed as partial; missing OHLC in a purported complete bar invalidates/quarantines it |
| volume_value/unit/semantics | Optional unless a task requires it and source supports it | Use UNAVAILABLE if expected but not supplied; NOT_APPLICABLE only when not meaningful for this observation type |
| bar_completion_status | Required for bar/timeframe use | Completed/partial/unavailable follows the bar contract; partial values cannot masquerade as completed bars |
| validation_status | Record-level | VALID/VALID_WITH_WARNINGS/QUARANTINED/REJECTED/SUPERSEDED; independent of field availability |

### 3.3 FeatureDefinition and FeatureValue

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| feature_id/version | Required for every defined feature | Missing definition identity invalidates the derived value |
| formula/dependencies/units | Required in feature definition | Incomplete definition cannot be ACCEPTED |
| feature_value_id | Required for each emitted value | Missing identity invalidates the record |
| feature_value | Required when availability_status=KNOWN | Typed value must match the feature definition |
| feature_unit | Required for numeric features | Missing unit blocks use in cross-source or risk calculations |
| dependency_refs | Required for derived values | Missing dependency lineage invalidates causal verification |
| feature_available_at | Required for decision-time use | Cannot precede availability of required inputs plus actual processing availability |
| availability_status | Required when a feature value is absent, stale, ambiguous or not yet usable | Uses field availability domain only |
| feature_validation_status | Definition-level, not FeatureValue-level | PROPOSED/UNDER_REVIEW/ACCEPTED/REJECTED/RETIRED; never substitutes for availability |
| validation_status | Record-level | Validates the emitted FeatureValue record, not the feature's scientific admission |

If required dependencies are missing, do not emit a fabricated numeric feature. Either omit the value with a typed availability status in an explicitly supported incomplete record or do not emit the FeatureValue record.

### 3.4 MarketSnapshot

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| snapshot_id, decision_timestamp, snapshot_spec_version | Required | Missing identity/cutoff/spec invalidates the snapshot |
| instrument_id and applicable specification ref | Required where instrument context is material | No inferred contract specification |
| observation_refs, feature_refs | Required for included inputs | Every ref resolves to an immutable record/version |
| timeframe_state_refs | Required only for timeframes consumed by the task | Each timeframe separately declares completed/partial/missing and available_at |
| snapshot_hash | Required for released reproducible snapshot after canonical serialization is frozen | Until then, provisional; never claim a hash proves semantic correctness |
| validation_status | Record-level | A snapshot with causal violations or unresolved mandatory dependencies is QUARANTINED/REJECTED, not marked KNOWN |

Do not create a second universal snapshot status. Use validation_status plus registered quality flags and per-input availability.

### 3.5 Forecast

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| forecast_id, snapshot_id, target_id/version, horizon_id | Required | Missing target/horizon identity invalidates the forecast |
| event_space_id/version | Required for class probability vectors | Must define mutually exclusive/exhaustive outcomes if probabilities sum to one |
| event_probability or class_probabilities | Conditional | Include only when the event/partition and target are exact; do not use null as a substitute for an uncalibrated score |
| calibration_version | Required when probabilities are represented as calibrated | If no valid calibration evidence exists, do not claim calibrated probability |
| prediction_interval/quantiles | Conditional | Require explicit coverage/quantile semantics and evaluation |
| model/version and created_at | Required for model-produced forecasts | Provenance is mandatory |

Forecast quality is not a field-availability status. A forecast revision is a new immutable record.

### 3.6 Scenario and ConditionEvaluation

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| scenario_id, snapshot_id, decision_timestamp, definition version | Required | Missing identity/cutoff invalidates the scenario |
| scenario_type, hypothesis | Required for a candidate scenario | Taxonomy must be versioned; do not force a scenario where evidence supports none |
| supporting/conflicting evidence refs | Required for auditable scenario | Empty list is allowed only when explicitly justified; no fabricated evidence |
| trigger/invalidation condition refs | Required for actionable/falsifiable scenarios | Each condition must have a registered definition |
| scenario_status | Required | Uses scenario lifecycle domain only |
| scenario_assessment | Conditional | SUPPORTED/CONTRADICTED/UNRESOLVED; assessment, not lifecycle |
| condition_state | Required per evaluated condition | NOT_EVALUATED/TRUE/FALSE/UNKNOWN/STALE/INVALID; unknown/stale/invalid never satisfy trigger |
| probability | Optional | Omit unless a registered event and calibrated estimate exist; scenario plausibility is not probability |
| scenario_expires_at | Required for time-bounded scenario | Expiry is distinct from invalidation |

### 3.7 TradeDecision

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| decision_id, snapshot_id, decision_timestamp, policy_id/version | Required | Missing identity/policy/cutoff invalidates decision |
| decision_class | Required for a completed policy decision | LONG/SHORT/WATCH/WAIT_FOR_CONFIRMATION/NO_TRADE/ABSTAIN; WAIT is deprecated |
| selected_scenario_refs | Conditional | May be empty for NO_TRADE or ABSTAIN; never invent a scenario to fill it |
| reason_code_refs | Required for NO_TRADE and ABSTAIN; required for other actions where policy specifies | Typed, registered reason codes |
| risk_result_ref | Required for LONG/SHORT where risk is applicable | Must reference a current deterministic result and constraint outcome |
| decision_expires_at | Required when decision is time-bounded | Expiry does not rewrite the original decision |

A completed decision has a known decision_class, even when that class is ABSTAIN. Do not use field availability UNKNOWN as a substitute for ABSTAIN.

### 3.8 RiskCalculation and ConstraintEvaluation

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| risk_request_id, engine_version, input refs | Required | Missing engine/input provenance invalidates authoritative result |
| risk_calculation_status | Required | REQUESTED/VALIDATING/CALCULATED/REJECTED_INPUT/STALE_INPUT/FAILED/EXPIRED/SUPERSEDED |
| calculated risk/volume/margin outputs | Required only when CALCULATED and applicable | Otherwise omit; never fabricate zero/default values |
| constraint_outcome | Required after policy evaluation | PERMITTED/PROHIBITED/RECALCULATION_REQUIRED/PENDING_AUTHORIZATION; separate from calculation status |
| reason_code_refs | Required when calculation/constraint fails or requires action | Must identify missing/stale/invalid inputs or violated rule |
| result_expiry | Required for time-sensitive result | Expired result cannot authorize a new decision |

A CALCULATED result is not permission to trade. A permitted result is not broker execution.

### 3.9 LifecycleEvent, Order, Deal and Position

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| event_id, event_type, event schema version | Required | Missing identity/type invalidates event |
| event_time | Required when event semantics have an effective time | If unavailable, preserve uncertainty; do not substitute received_at |
| received_at | Required when receiving telemetry exists | Actual system time only |
| order_id/deal_id/position_id | Conditional on event type | Missing only when genuinely not applicable or unavailable under a typed rule |
| broker-native status and mapping version | Required when broker provides a status | Preserve raw value; unmapped raw status does not become a guessed normalized status |
| order_status | Required when an order state is evidenced and mapped | Uses order lifecycle domain; no UNKNOWN enum—use reconciliation_status for uncertainty |
| position_status | Required when position state is broker-confirmed | OPEN/CLOSE_PENDING/CLOSED; no fabricated state for unresolved broker state |
| reconciliation_status | Required when local/broker state comparison is required | NOT_REQUIRED/PENDING/MATCHED/DIVERGENT/UNRESOLVED |
| fill_price/volume/cost fields | Required for the corresponding confirmed deal when supplied | Observed values only; modeled assumptions live in separate fields |
| idempotency/correlation/causation refs | Required where supported/needed to reconstruct event stream | Missing support is documented as a source limitation |

### 3.10 OutcomeLabel and PolicyLabel

| Field | Requiredness | Status binding / null rule |
|---|---|---|
| label_id/version, decision/snapshot ref, target_id/version | Required | Missing target lineage invalidates label |
| label_status | Required | PENDING/RESOLVED/AMBIGUOUS/CENSORED/UNAVAILABLE/INVALID |
| label_value | Required only when RESOLVED | For other statuses, do not force a class; ambiguity/censoring reason must be traceable |
| label_confirmed_at | Required when final resolution status is established | Must not enter original decision-time input |
| policy_id/version | Required for policy/action label | Profit/loss cannot infer policy correctness |
| outcome vs policy namespace | Required separation | Never merge realized market outcome, policy action, process quality and P&L into one label |

## 4. Exclusion and omission rules

- Do not store null fields that have no consumer or do not affect interpretation, validation, provenance or evaluation.
- Do not duplicate the same status at field, record and task levels unless each layer has a distinct purpose.
- Do not add both a boolean and a status for the same fact (for example, is_stale plus availability_status=STALE) without a proven consumer need.
- Do not copy broker order state into position state or vice versa.
- Do not copy scenario lifecycle into decision_class.
- Do not repeat source/feature payloads in task records when stable canonical references suffice.
- Do not emit generic confidence, generic value, generic timestamp or generic metadata fields.

## 5. Remaining work

This matrix is not complete for conditional news, visual, annotation, evaluation, dataset-release and training-run entities. Those fields must be added only when their source and consumer requirements are sufficiently defined.

Before schema freeze:
1. Complete remaining entity/field inventory.
2. Verify all task projections and status domains.
3. Define exact field types, precision, nullability and serialization after source feasibility.
4. Audit Stage 5 actual deliverables after independent acceptance.
5. Obtain explicit user approval.

No archive inspection, data acquisition, sample/label generation, pipeline implementation, benchmark, training, AURORA QUANT modification or Stage 5 modification is authorized.
