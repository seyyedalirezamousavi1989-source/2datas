# Scoped Enum and State Transition Governance — Phase 0

## 1. Status and authority

Status: **provisional governance contract v0.1; not frozen**.

This is a design contract, not an operational schema, state-machine implementation, broker adapter, dataset, label set or authorization to inspect/process data.

This document owns cross-entity enum and transition governance. Domain documents remain authoritative for detailed meaning:
- CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md: shared field meaning and scoped status separation.
- DATA_MODEL_AND_SCHEMA_CONTRACTS.md: entities and relationships.
- SCENARIO_SPECIFICATION.md: scenario and condition semantics.
- TRADE_LIFECYCLE_AND_MANAGEMENT_POLICY.md and TRADE_LIFECYCLE_AND_RISK_INTELLIGENCE.md: broker events and management.
- TASK_IO_CONTRACTS.md: task output boundaries.
- DECISION_LOG.md: cross-document decisions.

A domain may be reused only when its semantics are identical. Similar wording is not enough. Preserve broker-native values alongside normalized mappings.

## 2. Core principles

1. No universal status enum. Every status field declares exactly one domain and version.
2. Action is not status. Policy action, scenario lifecycle, order lifecycle, data quality and review state are distinct.
3. State is not evidence. Every transition requires an evidence/event reference and effective timestamp.
4. Unknown is not false. Missing, stale, ambiguous, not-yet-observable and invalid evidence cannot satisfy a trigger.
5. Historical decisions and states are immutable; corrections append revisions/events.
6. A request is not acknowledgement; acknowledgement is not fill; fill is not position reconciliation.
7. Terminal states are not silently reopened. A correction creates a linked revision/event.
8. Invalid transitions fail closed; preserve the attempted transition and rejection reason.
9. Preserve event/effective time, availability time and ingestion order separately.
10. Add enum values only for distinct operational meaning.

## 3. Field availability domain

Field: availability_status

Values: KNOWN, UNKNOWN, UNAVAILABLE, NOT_APPLICABLE, NOT_YET_OBSERVABLE, STALE, AMBIGUOUS, INVALID.

- KNOWN requires a present, typed, validated value.
- UNKNOWN means evidence is insufficient.
- UNAVAILABLE means a required source/value was not supplied or cannot be accessed.
- NOT_APPLICABLE means the field does not apply to this entity/task.
- NOT_YET_OBSERVABLE means the value can only become knowable after the relevant cutoff.
- STALE means a prior value exists but exceeds its freshness limit.
- AMBIGUOUS means materially different interpretations remain possible.
- INVALID means the supplied value violates its contract.

A stale value may be retained only with its original timestamp/freshness metadata; it is not current evidence. Ambiguity must not be collapsed to a scalar without an approved resolution rule. Availability does not transition merely because time passes: a new observation/evaluation creates a new record or revision.

## 4. Record/observation validation domain

Field: validation_status (or record_status where the entity contract explicitly names it).

Values: VALID, VALID_WITH_WARNINGS, QUARANTINED, REJECTED, SUPERSEDED.

Allowed transitions:
- VALID → SUPERSEDED only when a new immutable revision explicitly supersedes it.
- VALID_WITH_WARNINGS → VALID only after documented revalidation; otherwise publish a new validation record.
- VALID_WITH_WARNINGS → QUARANTINED or REJECTED when a defect is found.
- QUARANTINED → VALID or VALID_WITH_WARNINGS only after explicit revalidation.
- QUARANTINED → REJECTED after failed remediation or irreparable defect.
- REJECTED and SUPERSEDED are terminal for that record revision.

A source correction is a new revision, not an in-place status flip. Quality flags are diagnostics and do not replace validation status.

## 5. Label resolution domain

Field: label_status.

Values: PENDING, RESOLVED, AMBIGUOUS, CENSORED, UNAVAILABLE, INVALID.

Allowed transitions:
- PENDING → RESOLVED, AMBIGUOUS, CENSORED, UNAVAILABLE or INVALID.
- RESOLVED is terminal for that label revision. A correction creates a new linked label revision.
- AMBIGUOUS, CENSORED, UNAVAILABLE and INVALID are terminal for that attempt; later evidence may create a new revision only under a documented late-data/relabel policy.

PENDING is target lifecycle, not field availability NOT_YET_OBSERVABLE. Never force ambiguous cases into a majority class without an approved target-specific adjudication rule.

## 6. Feature admission domain

Field: feature_validation_status.

Values: PROPOSED, UNDER_REVIEW, ACCEPTED, REJECTED, RETIRED.

Allowed transitions:
- PROPOSED → UNDER_REVIEW or REJECTED.
- UNDER_REVIEW → ACCEPTED or REJECTED.
- ACCEPTED → RETIRED when superseded, unstable, redundant, invalid or no longer useful.
- REJECTED is terminal for that definition version; a materially changed formula requires a new version.
- RETIRED is terminal for new admission; historical uses remain traceable.

Feature admission does not imply an individual feature value is available or valid. FeatureValue separately carries availability and record validation.

## 7. Scenario lifecycle and condition evaluation

### 7.1 Scenario lifecycle

Field: scenario_status.

Values: DRAFT, CANDIDATE, ACTIVE, TRIGGERED, COMPLETED, INVALIDATED, EXPIRED, CANCELLED, SUPERSEDED.

Allowed transitions:
- DRAFT → CANDIDATE or CANCELLED.
- CANDIDATE → ACTIVE, INVALIDATED, EXPIRED, CANCELLED or SUPERSEDED.
- ACTIVE → TRIGGERED, INVALIDATED, EXPIRED, CANCELLED or SUPERSEDED.
- TRIGGERED → COMPLETED, INVALIDATED, EXPIRED, CANCELLED or SUPERSEDED.
- COMPLETED, INVALIDATED, EXPIRED, CANCELLED and SUPERSEDED are terminal for that scenario revision.

TRIGGERED means the registered trigger occurred; it does not mean an order was submitted or filled. INVALIDATED means evidence met the invalidation rule. EXPIRED means the validity window ended. CANCELLED is an explicit authorized withdrawal, not a market outcome. Corrections create linked revisions and never rewrite history.

### 7.2 Scenario assessment

If needed, use a separate scenario_assessment field: SUPPORTED, CONTRADICTED, UNRESOLVED. It is a point-in-time assessment, not lifecycle. Changes require a new assessment record/revision with timestamp and evidence. Do not add UNRESOLVED to scenario_status.

### 7.3 Condition evaluation

Field: condition_state.

Values: NOT_EVALUATED, TRUE, FALSE, UNKNOWN, STALE, INVALID.

- UNKNOWN, STALE, INVALID and NOT_EVALUATED never satisfy a trigger.
- NOT_EVALUATED changes only after the condition evaluation runs.
- TRUE and FALSE may alternate across successive evaluation records as new evidence arrives; never overwrite prior evaluations.
- INVALID requires correction/revision of the condition definition or evidence.
- NOT_APPLICABLE is not a condition result; optional conditions should be omitted or explicitly marked outside the evaluated condition set.

## 8. Entry decision action domain

Field: decision_class for entry policy only.

Values:
- LONG: entry policy passes all required gates for a long action.
- SHORT: entry policy passes all required gates for a short action.
- WATCH: monitor a relevant condition; no specific trigger is pending/actionable.
- WAIT_FOR_CONFIRMATION: a named, observable trigger is pending; setup is not yet actionable.
- NO_TRADE: policy evaluated the evidence and concluded no entry is justified, or a known constraint prohibits entry.
- ABSTAIN: policy cannot safely decide because critical inputs/state are unknown, invalid, stale, unavailable or irreconcilably contradictory.

WAIT is deprecated as a standalone entry action. Use WAIT_FOR_CONFIRMATION only when a specific trigger is named; otherwise use WATCH or NO_TRADE according to their definitions. NO_TRADE is a policy conclusion; ABSTAIN is inability to reach a reliable conclusion. LONG/SHORT require a referenced eligible scenario, current valid risk result and all policy gates.

Entry decision_class excludes MANAGE_OPEN_POSITION and EXIT; those belong to management actions. Each decision is an immutable as-of record. No universal transition graph is imposed on decision classes.

## 9. Management action domain

Field: management_action for an existing position only.

Values: HOLD, MOVE_STOP_TO_BREAK_EVEN, TRAIL_STOP, REDUCE_PARTIAL, CLOSE_POSITION, EXTEND_TARGET, TIME_EXIT, EMERGENCY_RISK_REDUCTION, NO_ACTION, ABSTAIN.

- HOLD affirmatively recommends maintaining the verified current position under policy.
- NO_ACTION means no management change is justified at this evaluation; it does not mean evidence is missing.
- ABSTAIN means current position/order/broker state or required evidence cannot be trusted.
- WAIT is not a management action; use NO_ACTION or ABSTAIN with reason and next-observation condition.
- Proposed stop/target/volume changes require a fresh deterministic risk calculation where applicable.
- Recommendation, request, broker acknowledgement and confirmed state are separate events.

## 10. Order lifecycle domain

Field: order_status is a normalized mapping. Always retain exact broker-native status and mapping version.

Values: DRAFT, SUBMITTED, ACKNOWLEDGED, WORKING, PARTIALLY_FILLED, CANCEL_REQUESTED, FILLED, CANCELLED, REJECTED, EXPIRED, REPLACED.

Rules:
- SUBMITTED means sent by client; ACKNOWLEDGED means broker receipt/acceptance according to mapped evidence; WORKING means confirmed working.
- PARTIALLY_FILLED means nonzero executed quantity with residual quantity remaining.
- CANCELLED may follow partial fills; cumulative filled quantity and deal records remain preserved.
- FILLED means the full order quantity was executed under broker evidence; it does not prove position reconciliation.
- REPLACED links to a replacement order; prior fills remain attached to the original.
- Missing acknowledgement is not REJECTED.
- Reconciliation uncertainty is a separate reconciliation_status.

Allowed transitions:
- DRAFT → SUBMITTED or CANCELLED.
- SUBMITTED → ACKNOWLEDGED, WORKING, PARTIALLY_FILLED, FILLED, REJECTED, CANCEL_REQUESTED or EXPIRED, only with supporting broker evidence.
- ACKNOWLEDGED → WORKING, PARTIALLY_FILLED, FILLED, REJECTED, CANCEL_REQUESTED or EXPIRED.
- WORKING → PARTIALLY_FILLED, FILLED, CANCEL_REQUESTED, EXPIRED or REPLACED.
- PARTIALLY_FILLED → PARTIALLY_FILLED (new fill event), FILLED, CANCEL_REQUESTED, EXPIRED or REPLACED.
- CANCEL_REQUESTED → CANCELLED, PARTIALLY_FILLED or FILLED, depending on broker race/fill evidence.
- CANCELLED, REJECTED, EXPIRED, FILLED and REPLACED are terminal for that order identity. Corrections append events; they do not silently reverse state.

## 11. Deal/fill and position domains

Deal/fill records are immutable execution events. Use event types FILL_CONFIRMED, FILL_CORRECTED, FILL_BUSTED and FILL_REVERSED. Corrections reference the original, preserve original and corrected values, and carry their own event/availability times.

Field: position_status. Values: OPEN, CLOSE_PENDING, CLOSED.

Partial reduction appends a position event and updates verified remaining quantity; it is not a terminal state. Additions/reductions respect broker netting/hedging semantics. CLOSED requires broker-confirmed zero remaining quantity or an authoritative close event. Unknown/divergent state belongs in reconciliation_status.

## 12. Reconciliation status domain

Field: reconciliation_status. Values: NOT_REQUIRED, PENDING, MATCHED, DIVERGENT, UNRESOLVED.

Allowed transitions:
- NOT_REQUIRED → PENDING when reconciliation becomes necessary.
- PENDING → MATCHED, DIVERGENT or UNRESOLVED.
- DIVERGENT/UNRESOLVED → PENDING after new broker/local evidence.
- MATCHED → PENDING when a later event invalidates prior reconciliation; preserve prior reconciliation record.
- No management action requiring verified state may proceed while DIVERGENT or UNRESOLVED.

## 13. Risk calculation and policy constraint domains

Calculation status and permission are separate.

Field: risk_calculation_status. Values: REQUESTED, VALIDATING, CALCULATED, REJECTED_INPUT, STALE_INPUT, FAILED, EXPIRED, SUPERSEDED.

Field: constraint_outcome. Values: PERMITTED, PROHIBITED, RECALCULATION_REQUIRED, PENDING_AUTHORIZATION.

A CALCULATED result may still prohibit the proposed trade. Constraint outcome references policy version, risk result, account/instrument state and reason codes. Model text cannot override it.

## 14. Artifact and dataset release domains

artifact_status: DRAFT, CANDIDATE, ACCEPTED, QUARANTINED, REJECTED, SUPERSEDED.

release_status: PROPOSED, UNDER_REVIEW, APPROVED, REJECTED, WITHDRAWN.

Release approval requires reviewer, scope, evidence, timestamp and immutable manifest reference. Artifact acceptance does not approve a dataset release.

## 15. Annotation/adjudication domain

annotation_status: UNREVIEWED, INDEPENDENTLY_ANNOTATED, DISAGREEMENT, ADJUDICATED, UNRESOLVED, REJECTED.

Preserve independent annotations. Adjudication is an additional record with method, reviewer, rationale and evidence; never overwrite disagreement.

## 16. Null and value consistency

For every field, the schema registry declares nullability, typed value requirements and allowed status/value pairs.

- KNOWN requires a valid typed value.
- UNKNOWN, UNAVAILABLE, NOT_APPLICABLE and NOT_YET_OBSERVABLE must not carry fabricated values.
- STALE may retain an old value only with original timestamp/freshness metadata.
- AMBIGUOUS preserves alternatives or an explicit ambiguity representation.
- INVALID values are quarantined, not exposed as accepted features.
- Zero, false, empty string and null are distinct.
- Status domains cannot be mixed in one field.

## 17. Freeze gates

This proposal is not frozen until every entity declares its status/action domain, every transition has evidence/time rules, broker-native mappings are source-verified, scenario/condition/management domains are reconciled with owner docs, nullability is defined field-by-field, Stage 5 is independently accepted and audited, source feasibility/licensing are evidenced, and the user explicitly approves schema freeze.

No archive inspection, data processing, sample/label generation, implementation, benchmark, training, AURORA QUANT modification or Stage 5 modification is authorized.
