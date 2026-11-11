# Target Dependency, Episode Grouping and Temporal Split Contract — Phase 0

## 1. Status

**Provisional split-dependency contract v0.1; exact horizons and durations remain unfrozen.**

This document defines how related samples/targets are grouped and how chronological splits avoid target leakage. It does not select dates, horizons, embargo lengths, source latency, or generate split manifests.

Authorities:
- Target definitions and horizon semantics: FORECAST_TARGET_ENGINEERING.md and TARGET_AND_LABEL_INTELLIGENCE_GOVERNANCE.md.
- Target priority/redundancy: TARGET_PORTFOLIO_AND_REDUNDANCY_DECISION.md.
- Point-in-time availability and snapshot revisions: POINT_IN_TIME_INTERVAL_AND_SNAPSHOT_REVISION_CONTRACT.md.
- Sample selection and redundancy: SAMPLE_VALUE_AND_SELECTION_POLICY.md and DATASET_COMPOSITION_AND_REDUNDANCY.md.
- Evaluation split policy: EVALUATION_PROTOCOL.md.
- Provenance and manifests: DATASET_PROVENANCE_VERSIONING_REPRODUCIBILITY.md.

## 2. Why row-level splitting is invalid

A row is not necessarily an independent observation. Multiple records may share:
- the same decision snapshot;
- overlapping input windows;
- the same future price path;
- a derived target and its primary target;
- the same scenario/position/order episode;
- duplicate or near-duplicate evidence;
- a late source revision or label-confirmation dependency.

If related rows are assigned to different splits, validation/test information can leak into training even when decision timestamps differ. Split the dependency group, not merely the row.

## 3. Canonical identities and grouping hierarchy

Use separate identities for distinct purposes:

- **snapshot_id:** immutable point-in-time input context.
- **decision_id:** one policy/forecast decision at one cutoff.
- **target_id/version:** exact target definition.
- **target_instance_id:** one target outcome attempt for one decision/snapshot.
- **episode_id:** stable market/decision episode that links related decisions and outcomes.
- **dependency_group_id:** grouping key for records that must not cross split boundaries due to overlapping target/input dependencies or shared future path.
- **lifecycle_episode_id:** one position/order/deal lineage where broker lifecycle applies.
- **duplicate_cluster_id:** exact/near-duplicate group discovered by a versioned deduplication rule.

Do not use row number, file order or ingestion batch as identity. One episode may contain multiple decision snapshots; one dependency group may combine overlapping episodes when their future target windows intersect.

## 4. Target dependency map

| Target family | Input cutoff | Future dependency window | Grouping rule |
|---|---|---|---|
| F01/Y01 fixed-horizon return | decision_timestamp | From first eligible post-cutoff observation through target endpoint | Group windows that overlap in underlying observations; retain horizon/version in target identity |
| F02/Y02 directional projection | Same as its F01 parent | Same future return window as parent | Inherit parent's dependency_group_id; never split independently from F01 |
| F03/Y03 barrier first-passage | decision_timestamp | Until first resolved barrier event or declared expiry | Group all records sharing/overlapping the same barrier path and episode |
| F04/Y04 MFE/MAE | decision_timestamp | Full declared excursion window | Group with any F01/F03/F05 targets using the same future path/window |
| F05 time-to-event | decision_timestamp | Until event or censoring/expiry | If parameterizing the same F03 barrier, inherit its dependency group; do not count as independent episode |
| F06/Y05 future volatility/range | decision_timestamp | Full future measurement window | Group overlapping future windows and any target derived from the same future returns |
| F07/Y06 state transition | decision_timestamp | Until transition confirmation or expiry | Group by initial state episode and overlapping transition window; preserve confirmation delay |
| F08 net hypothetical-trade outcome | decision_timestamp/order-intent cutoff | Full trade simulation/actual lifecycle through close/expiry | Group by trade policy instance and all linked order/deal/position events |
| Policy/action label | decision_timestamp | No future outcome dependency for the action itself; process/outcome review may be later | Keep policy decision with its snapshot; any later review is a separate target and shares episode lineage |
| Execution/lifecycle target | request/event cutoff | Broker event/position lifecycle through reconciliation/close | Group all linked order/deal/position events and corrections |
| Structure event target | event definition's observation start | Until actual confirmation/invalidation under its rule | Group pivot/lookback and confirmation window; no future-confirmed event may be backdated |

The exact intervals and grouping granularity are target-specific. This table does not choose horizons.

## 5. Derived targets and shared future paths

1. A derived projection inherits the parent target's dependency group. F02 cannot be placed in a different split from the F01 return from which it was derived.
2. Alternative parameterizations of one event (for example F03 and F05 for the same barrier) share dependency lineage.
3. MFE/MAE, barrier outcomes and fixed-horizon returns may use the same future path. Preserve that relationship and do not treat their records as independent observations.
4. A future volatility/range target and a current volatility-regime feature are different time roles. The future target must not leak into the current feature.
5. If multiple target horizons overlap, the dependency group must cover the union of their future windows.
6. If a source correction changes an input or target, preserve revision lineage and ensure all related versions remain in the same split group or are excluded under the release policy.

## 6. Input-window and duplicate grouping

Target-window overlap is not the only dependency.

Before split assignment:
- cluster exact duplicate snapshots/records;
- identify near duplicates using versioned semantic keys and documented similarity thresholds;
- group repeated examples generated from the same decision snapshot and task definition;
- group overlapping target windows and shared future paths;
- group all derived projections with their primary target;
- group lifecycle sequences by position/order lineage;
- preserve independent source observations as distinct evidence unless the source/record semantics prove duplication.

Do not merge independent broker feeds solely because numerical prices match. Conversely, do not count multiple paraphrases or repeated serialization of the same snapshot as independent samples.

If grouping transitive overlaps causes large clusters, report the cluster size and effective independent episode count rather than breaking a true dependency to increase row count.

## 7. Chronological split assignment

Split assignment must be chronological by decision_timestamp and frozen before final evaluation.

A defensible sequence:
1. Freeze target definitions, horizons, source availability/revision rules and duplicate rules.
2. Build target/input dependency intervals for each candidate example.
3. Construct episode/dependency/duplicate groups.
4. Assign groups to chronological train, validation and final-test periods without splitting a group.
5. Purge training examples whose target/dependency interval intersects a validation/test protected interval.
6. Apply an embargo after split boundaries to cover residual dependence, delayed target confirmation and source-revision uncertainty.
7. Verify no duplicate, derived target or shared future path crosses splits.
8. Freeze split manifest and checksums before model/feature selection is finalized.
9. Keep final test untouched until the protocol and candidate choices are frozen.

Do not use random row-level splitting for these market time series.

## 8. Purge and embargo derivation

Purge/embargo must be derived from the maximum relevant dependency, not an arbitrary number of bars.

For each target/task, identify:
- maximum future observation horizon;
- event-confirmation delay;
- source publication/availability latency;
- late-arriving revision/correction window;
- any lifecycle reconciliation/post-event dependency;
- input-window overlap relevant to duplicate or near-duplicate examples.

The protected interval must cover the union of the applicable dependencies. Where source latency/revision bounds are unknown, the split cannot claim full point-in-time isolation for affected targets; narrow or defer those targets rather than inventing a safe duration.

No universal 60/20/20 ratio, fixed bar-count embargo or fixed calendar gap is approved. Exact date boundaries depend on verified source coverage, target horizons, effective episode counts and regime coverage.

## 9. Policy, execution and lifecycle grouping

- Policy decisions are grouped with their exact snapshot, policy version and risk/constraint references.
- A later policy/process review must not be placed in an earlier decision-time input.
- Order requests, acknowledgements, deals, partial fills, corrections, position changes and reconciliation events remain in one lifecycle lineage.
- Multiple orders or deals may belong to one position/episode; do not assume one order equals one trade.
- Simulated execution is a distinct lineage from observed broker execution.
- A corrected broker event appends to the original lifecycle episode; it does not create an independent training sample.

## 10. Effective sample size and reporting

Every split/release report should include:
- raw row count;
- unique snapshot count;
- unique decision count;
- unique episode and dependency_group counts;
- target-specific resolved/ambiguous/censored/unavailable counts;
- number and size distribution of overlap/duplicate clusters;
- source and revision coverage;
- class/target distribution by chronological period and relevant regime;
- purged sample count and reason;
- embargo interval and derivation;
- effective independent episode count and uncertainty method.

Do not use raw row count as evidence of sample adequacy. Multiple labels from one future path do not create independent market episodes.

## 11. Leakage acceptance tests

Block release if any of the following occurs:
- F02 split differs from its F01 parent;
- F03/F05 same-event parameterizations cross splits;
- overlapping target windows cross protected split boundaries;
- exact/near duplicates cross splits without an approved independent-source rationale;
- source revisions available after decision time enter the earlier snapshot;
- lifecycle events from one position/order lineage are split across training and evaluation in a way that leaks outcomes;
- post-trade review or realized outcome appears in decision-time inputs;
- final test is used for target/threshold selection or calibration;
- purge/embargo uses a fixed arbitrary duration unsupported by target/source dependencies.

## 12. Remaining decisions and non-authorization

Still open:
- exact horizons, observation starts and endpoints;
- source-specific latency/revision bounds;
- episode clustering thresholds and transitive grouping behavior;
- date boundaries and walk-forward folds;
- purge/embargo durations;
- target-specific effective sample sufficiency and confidence intervals.

These cannot be frozen before Stage 5 acceptance, source feasibility and explicit user approval. This document does not authorize archive inspection, data acquisition, label/sample/dataset generation, split-manifest creation, implementation, benchmarks, model training, AURORA QUANT changes or Stage 5 changes.
