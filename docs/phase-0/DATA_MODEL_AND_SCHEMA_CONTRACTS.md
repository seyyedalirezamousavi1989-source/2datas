# Canonical Data Model and Schema Contracts — Phase 0

## 1. Purpose and status

Define the shared logical data model that connects the original A–M architecture, the prioritized task catalog, scenario reasoning, deterministic risk outputs, and evaluation.

This is a **logical contract**, not a frozen JSON Schema, database migration, pipeline implementation, or permission to create data. Final field types, requiredness, serialization, and compatibility mapping remain subject to the Stage 5 audit and explicit approval.

The governing optimization is information density: store each fact once, reference it from tasks, and keep targets and post-decision outcomes isolated.

## 2. Design rules

1. **Canonical once, task references many:** market observations and validated feature values have canonical identities. Task examples reference them rather than copying large candle histories and repeated prose.
2. **Immutable provenance:** source corrections and revised transformations create new versions/revisions; never silently overwrite evidence used by an earlier dataset release.
3. **As-of correctness:** every task input resolves to a snapshot whose values were available at its decision timestamp.
4. **Separate truth types:** raw observation, derived feature, interpretation, forecast, policy decision, deterministic calculation, broker event, and future label are different record types.
5. **Small task payloads:** task records contain only the minimum context required for their target, plus references to canonical context.
6. **Typed absence:** missing, unknown, unavailable, not applicable, not yet observable, ambiguous, invalid, and censored are not interchangeable.
7. **No implicit authority:** a model-generated value cannot impersonate a broker fact or deterministic calculation.
8. **Version everything that changes meaning:** schema, source mapping, feature, label, policy, cost model, and evaluation protocol versions are explicit.

## 3. Canonical entities and relationships

| Entity | Purpose | Key relationships |
|---|---|---|
| SourceDefinition | Provider, feed, instrument mapping, license and source limitations | Referenced by every raw observation |
| InstrumentSpecification | Broker/server-specific symbol and contract rules with validity interval | Referenced by quotes, bars, risk calculations and execution |
| MarketObservation | Immutable source-faithful quote, tick, bar, or event | Feeds snapshots and derived features |
| FeatureDefinition | Versioned formula, dependencies and availability rule | Defines FeatureValue |
| FeatureValue | Derived value for an entity/time/as-of context | Referenced by snapshots and tasks |
| MarketSnapshot | Frozen point-in-time context at a decision timestamp | References observations, feature values and timeframe states |
| Forecast | A versioned estimate for an explicitly defined future event | References one snapshot and a target definition |
| Scenario | Conditional hypothesis with evidence, trigger, invalidation and expiry | References snapshot and optionally forecasts |
| TradeDecision | Policy output such as LONG/SHORT/NO_TRADE/WATCH/WAIT | References scenario(s), snapshot and risk result |
| RiskCalculation | Deterministic calculation request/result with engine version | References account, instrument, quote, order assumptions and constraints |
| LifecycleEvent | Immutable order/deal/position/management/reconciliation event | Links to stable order, deal and position identities |
| OutcomeLabel | Future-derived market outcome, isolated from input records | References decision/snapshot and label definition |
| PolicyLabel | Policy action with policy provenance, not inferred from profit | References decision-time evidence and policy version |
| EvaluationRun | Reproducible evaluation protocol and outputs | References dataset, split, model/baseline and metric versions |

Do not create separate canonical copies of the same candle set for forecasting, scenarios, and trade decisions. Those records should reference one snapshot.

## 4. Common record envelope

Every serialized logical record should carry a common envelope, adjusted only where a source record has a documented reason to differ:

| Field | Contract |
|---|---|
| record_type | Stable discriminator, e.g. market_snapshot, forecast, scenario, trade_decision |
| record_id | Stable unique identity within the project namespace |
| schema_version | Version of this record's structural contract |
| created_at | UTC time the record was created by this system |
| provenance_refs | References to source, transformation, policy, or upstream records |
| status | Typed lifecycle/validity status appropriate to record_type |
| supersedes_record_id | Optional explicit link to a corrected/superseding record; original remains immutable |

Do not add generic fields such as `confidence`, `value`, or `metadata` when they hide different semantics. Prefer typed, named fields in each entity.

## 5. Market observation contract

### 5.1 Source and instrument identity

A market observation must identify:
- source/provider and feed/server;
- canonical instrument ID plus original provider symbol;
- broker/server-specific instrument specification version where applicable;
- observation kind (tick, bid/ask quote, trade, OHLC bar, session/event);
- source-native identifier or deterministic source key;
- source timestamp and its original timezone/offset representation;
- normalized event timestamp in UTC;
- actual availability/receipt timestamp where known;
- ingestion/recorded timestamp;
- revision/correction sequence where the source supports it.

Never assume every provider's XAUUSD symbol has the same contract, session, price precision, or bar construction.

### 5.2 Bar contract

An OHLC bar must specify:
- timeframe and aggregation definition;
- bar open and close timestamps, with a declared interval convention;
- open/high/low/close price basis (bid, ask, mid, last, or provider-defined);
- volume field meaning (tick volume, trade volume, or unknown);
- completion status and availability time;
- source revision/correction state;
- quality flags for gaps, malformed values, or incomplete history.

A bar's nominal close time does not prove the completed bar was available at that instant. The as-of contract uses actual availability when known.

## 6. MarketSnapshot contract

A MarketSnapshot is the canonical decision-time join point. It must be immutable once used by a task.

Conceptual fields:
- snapshot_id;
- decision_timestamp;
- snapshot_spec_version;
- instrument_id and applicable instrument-specification reference;
- source coverage/status;
- references to the exact market observations included;
- references to accepted feature values included;
- timeframe states, each identifying timeframe, bar reference, completion/partial status, event time and available_at;
- explicit missing/stale/conflict flags;
- snapshot content/provenance hash.

Do not embed an entire duplicate OHLC history in each task record. If a model requires a bounded context window, define a deterministic snapshot-to-window materialization rule and store the window's exact observation references and version.

A snapshot is not valid if any included input was unavailable after the decision timestamp, unless that input is explicitly modeled as a later-arriving event in a different task.

## 7. Forecast contract

A Forecast references exactly one input snapshot and one target definition/version. It must distinguish:
- event/target definition and event-space version;
- horizon/expiry;
- probability semantics (directional, barrier, regime transition, or net trade outcome);
- probabilities with named outcomes, if calibrated and supported;
- model/version and calibration version;
- uncertainty representation and known limitations;
- creation timestamp and decision timestamp.

Do not mix probability types in one vector. A forecast is an estimate, not an observed fact and not a trading instruction. Forecast revisions are new records linked to the prior forecast.

## 8. Scenario and TradeDecision contracts

A Scenario references:
- snapshot_id;
- hypothesis and scenario taxonomy version;
- evidence references with evidence roles (supporting/conflicting);
- activation conditions;
- invalidation conditions;
- horizon/expiry;
- optional forecast references;
- status and revision history.

A TradeDecision references:
- snapshot_id;
- scenario references;
- policy version;
- decision class (LONG, SHORT, NO_TRADE, WATCH, WAIT_FOR_CONFIRMATION);
- trigger/preconditions and invalidation/expiry;
- deterministic risk calculation reference, if applicable;
- evidence, conflicts, uncertainty, and abstention/rejection reason codes.

A scenario is not itself a trade decision. A trade decision is not itself an order. An order request is not a broker fill.

## 9. RiskCalculation and LifecycleEvent contracts

RiskCalculation must preserve request and result provenance, including:
- deterministic engine/version;
- account and instrument specification references;
- quote/price-side and timestamp references;
- entry/stop/target assumptions;
- costs and currency conversion references;
- limits and existing exposure snapshot;
- requested and permitted risk/volume;
- volume rounding and post-rounding recalculation;
- margin/feasibility result;
- warnings and fail-closed reason codes;
- validity/expiry.

LifecycleEvent must be append-only and include:
- event_id and idempotency key where applicable;
- event type and event schema version;
- event_time and received_at, with clock/source metadata;
- order_id, deal_id, position_id and broker identifiers where applicable;
- prior event/state reference where known;
- event payload and source/provenance;
- correction/reconciliation relationship if applicable.

Represent partial fills, rejects, requotes, cancel/replace, corrections and out-of-order delivery explicitly. Never infer a fill from an order request.

## 10. Labels and leakage boundary

Keep outcome labels and policy labels in a separate logical namespace and preferably separate physical storage from model input features.

Each label must reference:
- decision/snapshot ID;
- label definition/version;
- target event and horizon;
- confirmation time;
- price/cost convention;
- ambiguity/censoring status;
- provenance and source references.

Post-decision data—including realized price path, MFE/MAE, final trade outcome, label value, label confirmation timestamp, and retrospective explanation—must never be serialized into the corresponding input payload.

The join between inputs and targets is permitted only in controlled training/evaluation materialization, after split/purge rules are applied and leakage checks pass.

## 11. Status and missing-value vocabulary

Use explicit status codes rather than overloading null:

| Status | Meaning |
|---|---|
| observed | Directly present in source and valid under source contract |
| derived | Computed by a versioned deterministic transformation |
| estimated | Inferred/estimated, with method and uncertainty |
| unknown | Value cannot be established from available evidence |
| unavailable | Required source/value was not provided or cannot be accessed |
| not_applicable | Field does not apply to this entity/task |
| not_yet_observable | Value becomes knowable only after the current decision time |
| stale | Value exists but exceeds its declared freshness limit |
| ambiguous | Evidence supports multiple unresolved interpretations |
| invalid | Value fails validation or violates its contract |
| censored | Target outcome cannot be resolved within available observation window |

A status/value pair must obey a validation rule: e.g. a resolved label requires a typed value; an ambiguous or censored label must not carry a fabricated class. Avoid storing both a meaningful status and a contradictory non-null value.

## 12. Identity, deduplication and correction

Use stable identities derived from the semantic key, not row position or ingestion order.

Candidate identity keys:
- Source observation: source + feed + instrument mapping + observation kind + source-native key (or documented deterministic key) + revision.
- Bar: source + instrument mapping + timeframe + interval open/close + price basis + revision.
- Feature value: feature definition/version + source entity/snapshot + calculation context.
- Snapshot: instrument + decision timestamp + snapshot specification + exact source/feature revision set.
- Task example: task definition/version + snapshot ID + target/label definition/version + policy version where relevant.

Content hashes may verify exact payload identity but must not replace semantic identity. Two records with equal numerical values are not necessarily duplicates if their source, availability, price basis, or revision differs.

Deduplication must not erase genuine independent source observations. Preserve source lineage and use explicit canonicalization/reconciliation rules.

## 13. Serialization and storage boundaries

Provisional format guidance:
- Parquet: large time-series observations, feature values, and analytical tables.
- JSONL: compact task-specific instruction/target records after contracts are frozen.
- Manifest files: source/license registry, schema/feature/label/policy versions, split membership, checksums, and build configuration.
- Append-only event storage: order/deal/position lifecycle events.

Do not choose a database or file layout solely for convenience before source volume, update pattern, and Stage 5 compatibility are understood.

## 14. Required schema tests before any future release

- Every reference resolves to the correct entity and version.
- No input observation/feature has available_at after decision_timestamp.
- Timeframe bar completion/partial status matches the as-of policy.
- No label/target/post-decision field appears in model inputs.
- Every probability names its event and horizon and obeys partition rules if claimed.
- Every risk result identifies deterministic engine and input versions.
- Every order/fill/position event preserves broker identity and chronology.
- Status/value combinations are valid.
- IDs are stable and duplicate rules are deterministic.
- A full record can be traced to original source and transformation versions.
- Rebuilding a released schema/materialization produces identical semantic records and manifests.

## 15. Decisions intentionally deferred

Do not freeze the final JSON Schema or physical schema until:
1. the separate Stage 5 project is complete and independently accepted;
2. its actual artifacts and interfaces are audited for compatibility;
3. data-source feasibility and licensing are understood;
4. primary decision horizons and minimum timeframe set are selected;
5. the user separately approves the next phase.

The current document defines the intended logical relationships and safety invariants only.
