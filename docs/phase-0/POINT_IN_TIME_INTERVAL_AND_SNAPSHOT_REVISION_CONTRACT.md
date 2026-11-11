# Point-in-Time, Interval and Snapshot Revision Contract — Phase 0

## 1. Status and authority

**Provisional temporal contract v0.1; not frozen or source-validated.**

This document defines internal temporal semantics for causal market observations, bars, derived features, snapshots and revisions. It does not inspect any archive, choose a broker/provider, infer historical latency, implement snapshot materialization or authorize data generation.

Authorities:
- Shared field meanings: CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md.
- Entity relationships: DATA_MODEL_AND_SCHEMA_CONTRACTS.md.
- Scoped status values: SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md.
- Field/null bindings: FIELD_STATUS_BINDING_AND_NULLABILITY_MATRIX.md.
- Source-specific evidence and licensing: DATA_SOURCE_FEASIBILITY_FRAMEWORK.md.
- Snapshot/feature ownership: ARCHITECTURE.md and feature registry documents.

Internal conventions below do not override provider/broker evidence. Where a source's timestamp, bar construction or availability cannot be verified, the affected record is not eligible for point-in-time decision inputs.

## 2. Three time axes and one decision cutoff

Every time-dependent record must distinguish:

1. **Event/valid time:** when the represented market event occurred or a fact was effective.
2. **Knowledge/availability time:** when the information could actually have been known by the target decision system.
3. **Processing/system time:** when the project received, stored, transformed or materialized it.
4. **Decision cutoff:** the as-of instant at which one decision's eligible information set is frozen.

The decision cutoff is a query boundary, not a substitute for any of the three time axes.

Canonical fields:
- event_time: event occurrence/effective time;
- available_at: earliest defensible time the target system could use the information;
- received_at: actual receiver timestamp, when telemetry exists;
- ingested_at/created_at: project persistence/creation time;
- decision_timestamp: exact cutoff for one task decision;
- revision_available_at: when a correction/revision became knowable;
- interval_start/interval_end: normalized bar/aggregate interval.

Never substitute event_time, bar close, scheduled release time or ingestion time for available_at without evidence.

## 3. Causal eligibility rule

For every model input selected for decision time t_d:

- available_at must be known and satisfy available_at <= t_d.
- All dependencies of a derived feature must themselves be eligible at t_d.
- feature_available_at cannot precede the latest required dependency availability plus actual processing completion.
- A value whose availability cannot be established is excluded from the decision snapshot or represented as unavailable context that cannot influence a claimed point-in-time conclusion.
- Late-arriving evidence is not retroactively inserted into the original snapshot.
- Future-derived target values and label confirmation timestamps remain outside model inputs.

A historical archive that contains event timestamps but no reliable publication/receipt/availability history does not prove that its values were known at those event times. Mark the limitation and restrict the affected task; do not assume zero latency.

## 4. Internal interval convention and raw source timestamps

### 4.1 Normalized intervals

Internally represent time bars/aggregates with half-open intervals:

    [interval_start, interval_end)

The start is included; the end is excluded. Adjacent intervals therefore do not overlap at a shared boundary. All normalized interval endpoints are UTC instants.

This is an internal indexing convention only. It does not assert that a provider's aggregation, session calendar, quote selection or bar timestamp convention matches this model.

### 4.2 Preserve provider convention

Preserve the raw source timestamp and a source-specific bar timestamp convention:
- OPEN_STAMPED
- CLOSE_STAMPED
- PROVIDER_DEFINED
- UNKNOWN

A verified source adapter maps the provider's raw timestamp to normalized interval_start/interval_end using a documented timeframe/session rule. If convention or mapping is UNKNOWN, do not silently infer the interval or use the bar for causal training.

Keep:
- raw timestamp string/value;
- original timezone/offset and precision;
- provider/feed and adapter version;
- normalized interval boundaries;
- timeframe and aggregation/session definition version.

Do not fabricate millisecond precision from a second-resolution source. Equal timestamps without a reliable sequence key remain unordered/ambiguous.

## 5. Completed and partial bars

A bar's nominal interval_end is not proof that its completed values were available at that instant.

- COMPLETE: the source/adapter confirms the interval is closed under its documented bar-construction rule and its availability is known.
- PARTIAL: the interval is still forming at the snapshot cutoff; its values are a point-in-time partial observation.
- UNAVAILABLE: no usable bar value exists for the requested interval/timeframe.

A partial bar must carry the exact decision cutoff/as-of time and must never be substituted for a completed bar. When a completed bar arrives later, it is a distinct observation/revision with its own available_at.

For each timeframe in a snapshot:
- identify the exact bar/partial-bar reference;
- record interval_start/interval_end;
- record completion status and available_at;
- record source revision and timeframe/calendar definition;
- state whether it was eligible at decision_timestamp.

Do not assume that all timeframes close simultaneously or that an H1/H4/D1 bar is available exactly at its nominal boundary.

## 6. Multi-timeframe as-of selection

For each requested timeframe, select only the latest source-valid bar revision whose:
- normalized interval is known;
- completion/partial status is explicit;
- available_at <= decision_timestamp;
- revision_available_at <= decision_timestamp, if revised;
- source/instrument/timeframe mapping is valid for the interval.

If the most recent completed bar is not yet available at t_d, use the latest earlier eligible completed bar and disclose its age; do not use the later bar. A partial bar may be included only as a separate, explicitly partial input if the task contract permits it.

A timeframe hierarchy does not override availability. Higher-timeframe context may be stale or absent while lower-timeframe data is current; preserve that condition rather than forcing alignment.

## 7. Late arrivals and source corrections

A correction can have:
- an effective/event interval in the past;
- a later revision_available_at when the correction became knowable;
- a later received_at/ingested_at when the project obtained it.

Preserve the original observation and append the corrected revision with explicit supersession/correction references. Never overwrite the prior value or backdate the correction's knowledge time.

As-of selection at t_d uses only the latest revision that was available by t_d. A correction arriving after t_d must not alter the original decision input, target rationale or historical snapshot.

If a source archive exposes only the latest corrected history and not earlier revisions, document that point-in-time limitation. Do not claim a faithful historical replay for tasks where revisions could materially affect the decision.

## 8. Clock source, precision and uncertainty

Where available, retain:
- source clock identity;
- receiver clock identity;
- timestamp precision/resolution;
- synchronization method and known offset;
- uncertainty/tolerance bound;
- timezone/offset and versioned timezone database;
- session/calendar definition and version.

If clock uncertainty overlaps the decision cutoff or prevents ordering of material events, use a conservative exclusion or an explicit ambiguous state. Do not create artificial ordering from ingestion order alone.

For daylight-saving transitions, preserve UTC instants and the source timezone/session calendar used to interpret local market sessions. Never infer timezone from the machine locale.

## 9. News and scheduled events

Keep separate:
- scheduled_for: announced future event time;
- published_at: when the source released the information;
- available_at: when the decision system could access it;
- revised_at/revision_available_at: when a later correction became known;
- actual_event_time: when the underlying event occurred, if distinct.

A future scheduled event can be known before it occurs only if its schedule was published and available by t_d. The eventual release value, surprise, outcome or later revision cannot appear in the earlier snapshot.

## 10. Broker and lifecycle events

For broker events, preserve:
- broker-native event/order/deal/position IDs;
- broker event time and source sequence, if supplied;
- client request time;
- broker acknowledgement time;
- fill/deal time;
- receiver time;
- reconciliation time.

Arrival order is not necessarily broker event order. Use broker sequence/causation references where reliable; otherwise preserve uncertainty. Duplicate/replayed events must be idempotently recognized without deleting the original evidence. Corrections and reversals append events.

## 11. Immutable MarketSnapshot contract

A MarketSnapshot is a frozen point-in-time selection, not a mutable view over the latest corrected database.

It must identify:
- snapshot_id and snapshot_spec_version;
- instrument_id and effective instrument specification reference;
- decision_timestamp/as-of cutoff;
- exact source/feed and observation revision references;
- exact FeatureValue IDs and feature definition versions;
- per-timeframe bar references, interval and completion/availability state;
- source coverage, stale/missing/ambiguous conditions;
- materialization/created_at time, distinct from decision_timestamp;
- canonical ordered reference set and content hash when serialization is frozen.

Snapshot identity must be stable for the same canonical specification and exact input revision set. A hash proves content identity, not correctness or point-in-time validity.

A snapshot materialized later for research may still represent an earlier decision time only if every included record's availability/revision history proves eligibility at that cutoff. Its materialization time must remain visible; do not claim the snapshot existed live at decision time.

## 12. Snapshot revisions and supersession

Once referenced by a decision, a snapshot is immutable.

If a source correction, feature correction, adapter fix or specification change affects its contents:
1. retain the original snapshot and all original references;
2. create a new snapshot identity/revision;
3. link it to the prior snapshot with supersedes/supersession reason;
4. record the new revision's creation and availability times;
5. identify affected downstream forecasts, scenarios, decisions, labels and evaluations;
6. do not rewrite the original decision's input context.

A corrected snapshot is not automatically eligible to replace the original in training. The release/target policy must explicitly decide whether the original as-known input, corrected retrospective truth, or both are retained—and in separate roles.

## 13. Temporal leakage checks

Every future materialization must test:
- available_at <= decision_timestamp for every input and dependency;
- revision_available_at <= decision_timestamp for selected revisions;
- no future completed bar or future partial-bar state;
- no higher-timeframe bar selected before actual availability;
- no future swing/structure confirmation backdated to pivot time;
- no late news revision or post-event value used as earlier-known fact;
- no broker fill/acknowledgement ordered by ingestion time when source event order differs;
- no correction overwriting historical snapshot content;
- no label value/confirmation timestamp in model inputs;
- no overlapping target episode or post-decision event crossing a split without purge/embargo protection.

A single critical causal violation blocks the affected record or release.

## 14. Source-dependent questions still open

The following cannot be frozen without source evidence:
- provider/broker bar timestamp convention and aggregation boundary;
- session calendars, weekend/holiday handling and DST behavior;
- historical publication/availability/latency metadata;
- source clock precision and synchronization uncertainty;
- historical correction/revision availability;
- broker event sequencing and identifier reliability;
- whether historical replay can reproduce the information actually available at the time.

No provider is assumed to satisfy these requirements merely because it offers historical OHLC.

## 15. Freeze gates and non-authorization

Before this contract is frozen:
1. independently accept and audit the separate Stage 5 deliverables;
2. receive separate user authorization for source feasibility review;
3. verify source-specific bar, clock, availability and revision semantics;
4. verify instrument/session/timezone mapping;
5. test snapshot reconstruction and as-of selection on approved evidence;
6. define target-dependent episode/purge/embargo rules;
7. obtain explicit user approval.

This document does not authorize opening XAUUSD.zip, downloading or processing market data, generating samples/labels/datasets, implementing adapters or snapshot pipelines, running benchmarks, training models, modifying AURORA QUANT or changing the separate Stage 5 project.
