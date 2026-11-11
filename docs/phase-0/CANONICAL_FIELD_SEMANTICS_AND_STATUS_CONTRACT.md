# Canonical Field Semantics and Scoped Status Contract — Phase 0

## 1. Status and boundary

This document reconciles shared field meanings across the logical data model, task I/O, features, forecasts, labels, deterministic risk and trade lifecycle specifications.

It is a **semantic contract proposal**, not a frozen JSON Schema, database schema, implementation, migration or data-generation authorization. Exact serialization types, precision, requiredness by task and Stage 5 compatibility remain open. This contract must be reviewed and approved before schema freeze.

The governing rule: a field name has one meaning throughout the project. If two concepts differ, they must have different names or explicitly scoped types.

## 2. Universal field ownership

| Concept | Canonical meaning | Semantic owner |
|---|---|---|
| `record_id` | Stable identity of this logical record, immutable after publication | Data model |
| `record_type` | Discriminator for the entity contract | Data model |
| `schema_version` | Structural contract version for this record type | Schema registry |
| `created_at` | UTC instant this system created the record | Provenance |
| `event_time` | When the represented event occurred in the source/world | Source/event contract |
| `source_timestamp` | Original provider timestamp as supplied, including original timezone/precision semantics | Source adapter |
| `available_at` | Earliest defensible time the information was available to the decision system | Causal-time contract |
| `received_at` | Time the receiving system actually received the record | Ingestion contract |
| `ingested_at` | Time the record was durably recorded in this project | Provenance |
| `decision_timestamp` | Cutoff instant at which a particular decision's eligible inputs are frozen | Snapshot/task contract |
| `valid_from` / `valid_to` | Effective-time interval during which a specification or mapping applies | Effective-dated reference |
| `confirmed_at` | Time a condition/target became confirmable under its declared rule | Event/label definition |
| `expires_at` | End of validity of a forecast, scenario, decision or request | Entity-specific contract |
| `status` | Lifecycle/validity state from the status domain assigned to that entity | Entity-specific contract |
| `quality_flags` | Non-exclusive diagnostic flags; do not replace the primary status | Quality contract |
| `provenance_refs` | Stable references to upstream evidence, definitions and transformation runs | Provenance |
| `definition_id` / `definition_version` | Identity/version of the feature, target, policy, taxonomy or metric being applied | Relevant registry |
| `source_id` / `feed_id` | Provider/source identity and distinct feed/server identity | Source registry |
| `instrument_id` | Canonical instrument identity, distinct from a provider's symbol string | Instrument registry |
| `source_symbol` | Exact symbol string used by the provider/broker | Source adapter |
| `specification_id` / `specification_version` | Effective-dated instrument/account specification used for a calculation | Specification registry |
| `snapshot_id` | Immutable identity of a point-in-time input context | Snapshot contract |
| `target_id` / `target_version` | Exact future event/outcome definition | Target registry |
| `policy_id` / `policy_version` | Exact decision/management policy semantics | Policy registry |
| `run_id` | One execution of a transformation, evaluation or training process | Provenance |
| `artifact_id` | Immutable stored artifact identity | Artifact registry |

Do not overload `timestamp`, `time`, `date`, `price`, `value`, `confidence`, `source`, or `metadata` when the underlying semantics differ. Use explicit qualified names.

## 3. Three clocks and one decision cutoff

The project must keep three different notions of time separate:

1. **Event/valid time:** when a market event, release, broker action or specification was true/effective.
2. **Knowledge/availability time:** when the information could actually have been known to the decision system.
3. **System/processing time:** when the project received, stored or processed it.

The decision cutoff is a task-specific instant against which knowledge availability is tested; it is not a fourth source clock.

For any input record used at decision time (t_d):
- it must satisfy `available_at <= decision_timestamp`;
- if availability is unknown, it cannot silently be treated as available at event time;
- if the source was delayed, the later availability time governs;
- if a record is revised, each revision has its own availability time;
- if a historical archive cannot establish point-in-time availability, mark the limitation and restrict tasks that require it.

A candle's close time, a news event's scheduled time, and an order's request time do not automatically equal their availability/confirmation times.

## 4. Timestamp representation rules

The eventual serialization must preserve:
- normalized UTC instant;
- original source timestamp and timezone/offset where provided;
- precision/resolution of the source clock;
- clock/source identity and known synchronization uncertainty;
- event-time vs receive-time vs ingestion-time semantics.

Never strip timezone information before normalization. Never infer missing timezone from the machine's current locale. Daylight-saving/session interpretation must use the source's documented calendar and a versioned timezone database where relevant.

If source precision is only one second, do not fabricate millisecond precision. If two events share a timestamp and no sequence/order key exists, preserve ordering ambiguity.

## 5. Price, quantity, rate and currency semantics

A numerical value is incomplete without a declared unit and basis.

### 5.1 Price

Every price must identify:
- instrument and source/feed;
- quote side/basis: BID, ASK, MID, LAST, BAR_BID, BAR_ASK, BAR_MID, PROVIDER_DEFINED or another explicitly registered basis;
- currency/quote convention where applicable;
- precision/tick-size context and effective instrument specification;
- event/availability timestamp;
- observed, derived, estimated or simulated origin.

Do not store a generic `price` if the field may represent bid in one row and midpoint in another. Prefer `bid_price`, `ask_price`, `mid_price`, `entry_price`, `exit_price` with a required basis reference.

### 5.2 Price distance and return

- Price distance: state whether absolute price units, points, ticks, percentage or volatility-normalized units.
- Return: state arithmetic vs log return, reference prices, interval/horizon, quote side and scaling.
- Pip/point terminology must not be assumed universal for XAUUSD; use the actual instrument specification and explicit unit conversion.

### 5.3 Volume and quantity

Every volume must declare unit and semantics: lots, contracts, base units, quote units, traded volume, tick count, requested order volume, filled volume or residual position volume. These are not interchangeable.

### 5.4 Currency and monetary values

Every monetary value must include currency code and whether it is account, quote, profit, margin or reporting currency. Currency conversion must reference the rate source, side/method and timestamp. Never infer currency from a symbol name alone.

### 5.5 Rates, ratios and probabilities

- Rates declare denominator and period (for example, per-bar, annualized or per-trade).
- Ratios declare numerator/denominator and zero-denominator behavior.
- Probabilities declare target/event ID, target version, horizon and event-space semantics.
- A probability partition must be mutually exclusive and exhaustive; only then is a sum-to-one check appropriate.
- Independent/overlapping event probabilities must not be forced to sum to one.

## 6. Universal status is not one universal enum

A single status list cannot correctly describe market observation validity, field absence, label resolution, order state and release approval. Use **scoped status domains**.

### 6.1 Field availability status

Used when a field/value may or may not be known/applicable:
- `KNOWN`: value is established under the field's evidence contract.
- `UNKNOWN`: evidence is insufficient to establish a value.
- `UNAVAILABLE`: required source/value was not supplied or cannot be accessed.
- `NOT_APPLICABLE`: field does not apply to this entity/task.
- `NOT_YET_OBSERVABLE`: value can only become knowable after the relevant cutoff.
- `STALE`: value exists but exceeds its declared freshness limit.
- `AMBIGUOUS`: multiple materially different interpretations remain possible.
- `INVALID`: supplied value violates its contract or failed validation.

### 6.2 Label resolution status

Used only for target/label outcomes:
- `PENDING`: target window has not yet completed or confirmation condition has not occurred.
- `RESOLVED`: target is determined under the target definition.
- `AMBIGUOUS`: evidence cannot distinguish possible outcomes under the declared resolution rule.
- `CENSORED`: observation ended before the target could be resolved, under the declared censoring rule.
- `UNAVAILABLE`: required future/source evidence is absent.
- `INVALID`: label construction failed validation.

Do not map PENDING to NOT_YET_OBSERVABLE automatically; the former is target lifecycle, the latter is field availability.

### 6.3 Observation/record validation status

Used for source/derived records:
- `VALID`
- `VALID_WITH_WARNINGS`
- `QUARANTINED`
- `REJECTED`
- `SUPERSEDED`

Quality flags remain non-exclusive diagnostics such as `GAP`, `DUPLICATE_CANDIDATE`, `CLOCK_UNCERTAIN`, `PARTIAL_BAR`, `LATE_ARRIVAL`, `SOURCE_REVISION`, `CROSSED_QUOTE`, `STALE_QUOTE`, and `OUTLIER_REVIEW_REQUIRED`. The flag registry must define each flag and its trigger.

### 6.4 Scenario and decision status

Scenario lifecycle, scenario assessment, condition evaluation and entry-policy action are separate domains. Their canonical values and transitions are owned by SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md and detailed by SCENARIO_SPECIFICATION.md.

- Scenario lifecycle uses DRAFT, CANDIDATE, ACTIVE, TRIGGERED, COMPLETED, INVALIDATED, EXPIRED, CANCELLED and SUPERSEDED.
- Scenario assessment, when required, uses SUPPORTED, CONTRADICTED or UNRESOLVED; this is not a lifecycle state.
- Condition evaluation uses NOT_EVALUATED, TRUE, FALSE, UNKNOWN, STALE or INVALID.
- Entry decision class uses LONG, SHORT, WATCH, WAIT_FOR_CONFIRMATION, NO_TRADE or ABSTAIN.
- WAIT is deprecated as a standalone entry action. NO_TRADE is a policy conclusion; ABSTAIN means a reliable decision cannot be made.
- Existing-position management actions use a separate management_action domain.
- Decision review status, if needed, is separate and must not alter the original decision.

### 6.5 Order, deal and position status

Do not collapse broker order status, deal/fill events, position state and reconciliation state. Their canonical normalized values and transitions are defined in SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md.

- Order lifecycle uses its own order_status domain; preserve exact broker-native values and mapping version.
- Deal/fill is an immutable event stream (confirmed, corrected, busted or reversed), not a mutable order/position status.
- Position status is OPEN, CLOSE_PENDING or CLOSED under the account's netting/hedging model.
- Reconciliation uses a separate reconciliation_status domain; uncertainty must not be inserted into order_status or position_status.

A missing acknowledgement is not proof of rejection or non-execution. A fill does not by itself prove that the local position projection has been reconciled.

### 6.6 Artifact/release status

Artifact lifecycle and dataset release approval are distinct:
- Artifact: `DRAFT`, `CANDIDATE`, `ACCEPTED`, `QUARANTINED`, `REJECTED`, `SUPERSEDED`.
- Dataset release: `PROPOSED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `WITHDRAWN`.
- Approval must reference reviewer, scope, evidence and timestamp.

## 7. Value/null/status consistency

A null is a serialization fact, not a semantic explanation. Each field definition must declare:
- whether null is allowed;
- which scoped statuses permit null;
- whether a typed value must be present;
- whether a value can be present with a warning;
- whether zero is a valid measured value or a sentinel (sentinels are discouraged).

Rules:
1. If status is KNOWN, the typed value must be present and validated.
2. If status is UNKNOWN, UNAVAILABLE, NOT_APPLICABLE or NOT_YET_OBSERVABLE, a value must not be fabricated; a null may be permitted with the status.
3. If status is AMBIGUOUS, preserve candidate interpretations/evidence where practical; do not force one scalar.
4. If status is STALE, a prior value may be retained only with its original timestamp and freshness metadata; consumers must not treat it as current.
5. If status is INVALID, preserve the raw invalid value in the quarantined evidence layer when lawful, but do not expose it as a valid feature.
6. A zero, empty string, false and null are distinct values and must never be interchanged as missing-value sentinels.

Applicability is separate from availability: a field can be applicable but unavailable, or not applicable regardless of source coverage.

## 8. Confidence, probability and uncertainty

Do not use a generic `confidence` field across records.

Use explicit names and definitions, for example:
- `event_probability`: probability of one named event under a target definition;
- `class_probabilities`: probabilities over a named mutually exclusive/exhaustive class partition;
- `calibration_version`: calibration procedure/version;
- `prediction_interval` or `quantile_forecast`: a declared distributional uncertainty object;
- `annotation_agreement`: a defined inter-annotator statistic;
- `data_quality_status`: quality of inputs, not model uncertainty;
- `model_uncertainty`: only if a validated method actually estimates it.

A model's self-reported confidence is not a calibrated probability. Evidence strength, data quality, epistemic uncertainty, aleatoric uncertainty and annotator disagreement must not be collapsed into one score.

## 9. Identity and reference semantics

- IDs are opaque stable identifiers; do not encode mutable labels, row numbers or current file paths as identity.
- Every reference must identify entity type and version where the referenced object is versioned.
- A provider-native ID is retained separately from the project's canonical ID.
- Corrections create new immutable revisions linked by explicit supersession/correction relationships.
- A hash proves byte identity only; it does not prove correctness or semantic equivalence.
- Duplicate detection must include source, time, price basis, revision and feed semantics; equal numeric values alone do not prove duplication.

## 10. Requiredness and applicability matrix

Final requiredness is task-specific. The schema design must use these rules:

| Field family | Required when | Not required when |
|---|---|---|
| source/feed identity | Any source-derived observation or claim | Purely synthetic software fixture, which must be marked synthetic |
| instrument/specification | Price, contract, risk or execution semantics depend on it | A non-instrument annotation unrelated to those semantics |
| event/availability timestamps | Any time-dependent evidence | Only if a record is explicitly timeless and its contract justifies that exception |
| decision timestamp | Any prediction, scenario, policy or decision-time task example | Raw source observation with no decision context |
| snapshot reference | Any task consuming a frozen market context | Source record or independent broker event |
| feature definition/version | Any derived feature value | Raw observation |
| target definition/version | Any outcome label or forecast target | Input-only context record |
| policy version | Any policy/action target or decision | Market-outcome target |
| currency/unit | Any monetary, price-distance, volume or rate field | Non-numeric descriptive field |
| provenance | Every derived, labeled, annotated, assembled or evaluated artifact | Never optional for released artifacts |

Task-specific contracts may add required fields but may not weaken these universal conditions without an explicit exception and rationale.

## 11. Cross-document reconciliation decisions

1. The earlier broad status vocabulary is now split into scoped domains; do not reuse one enum for labels, observations, decisions, orders and releases.
2. The logical data model's `status` field is polymorphic only by record type; each record type must point to exactly one declared status domain.
3. Feature availability uses field availability status; feature admission lifecycle (proposed/tested/accepted/rejected/retired) is a separate `validation_status`.
4. Label `status` uses the label-resolution domain; it is not the same as record validation status.
5. A forecast's probability semantics are determined by target definition and event-space; no generic probability/confidence field is accepted.
6. `created_at`, `event_time`, `available_at`, `received_at`, `ingested_at`, `decision_timestamp`, and `confirmed_at` are never interchangeable.
7. `price`, `volume`, `distance`, `return`, `rate`, and monetary amounts require explicit basis/unit metadata.
8. A decision class is not a scenario status, broker order status, or outcome label.

## 12. Unresolved items requiring later evidence

- Exact timestamp precision and serialization representation for each admitted source.
- Canonical instrument and currency code standards after Stage 5/source review.
- Exact numeric precision/rounding and decimal representation for prices, lots, account money and derived features.
- Broker-specific order-state mapping and netting/hedging representation.
- Per-task required/optional field matrix after final task/horizon selection.
- Whether source availability can be reconstructed historically for each provider.
- Which quality flags are essential rather than decorative.
- Exact enum wire values and schema compatibility strategy.

## 13. Gate

This semantic contract may be promoted to frozen schemas only after the Stage 5 deliverables have been independently accepted and audited, source feasibility and licensing are known, unresolved units/timestamps are evidence-backed, and the user explicitly approves schema freeze.

No implementation, archive inspection, data acquisition, labeling, training or external project modification is authorized by this document.
