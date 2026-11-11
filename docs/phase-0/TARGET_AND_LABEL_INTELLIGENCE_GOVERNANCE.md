# Target and Label Intelligence Governance — Phase 0

## 1. Purpose and status

This document consolidates the target-design rules into one governance contract. Its purpose is to ensure the model learns well-defined, decision-relevant market outcomes and policy behavior rather than hindsight narratives, profitable-trade shortcuts, or duplicated labels.

**Status: design only.** No source data has been inspected for label construction, no target values have been generated, and no labeling, training, or benchmark has been performed. Candidate targets in this document are not approved for implementation. Stage 5 compatibility, source feasibility, exact task/horizon selection and explicit user authorization remain mandatory.

The primary optimization is **reliable information per independent market episode**, not maximum label count.

## 2. The central separation: five different things

Every record must distinguish:

1. **Observed market state:** what was available at decision time.
2. **Market outcome:** what subsequently happened, defined without reference to whether a trade should have been taken.
3. **Forecast:** a probability/distribution estimate about one registered market outcome.
4. **Policy decision:** what a named decision policy recommended given the information and constraints at that time.
5. **Execution and realized result:** what a broker actually accepted/filled and what the resulting position/account outcome was.

These are not interchangeable labels. A profitable outcome does not prove that the original decision was sound; a losing outcome does not prove that the decision was unsound. A correct market forecast does not guarantee a feasible or profitable trade.

## 3. Label ontology and task boundaries

### 3.1 Market outcome targets

Objective future quantities/events, independent of trading policy:
- fixed-horizon return;
- directional movement under a predeclared neutral band;
- first passage to one of a defined set of barriers;
- MFE/MAE over a fixed future window;
- time-to-event with censoring;
- realized future volatility/range;
- objectively defined market-state transition;
- objectively confirmed structural event, only if its event/confirmation semantics are reproducible.

### 3.2 Policy/action targets

Decision outputs generated under a named, frozen policy:
- LONG, SHORT, WATCH, WAIT_FOR_CONFIRMATION, NO_TRADE, ABSTAIN for entry policy; existing-position management uses the separate management_action domain;
- scenario acceptance/rejection;
- hold/reduce/modify/trail/partial exit/close/abstain, where the state and authority are defined.

Policy labels must preserve the actual information set, policy version, constraints, and evidence. They must not be backfilled from the future P&L.

### 3.3 Execution targets

Broker/system facts:
- request submitted;
- accepted/rejected/cancelled/expired;
- partial/full fill;
- fill price/quantity;
- commission/swap and other realized costs;
- modification/cancellation acknowledgement;
- reconciliation outcome.

Only verified broker/system records can establish observed execution. Simulated fills must be labeled as simulations and never mixed with actual execution.

### 3.4 Post-trade outcome targets

Realized trade/account outcomes are downstream evaluation targets:
- net P&L and R;
- realized costs;
- maximum adverse/favorable path;
- drawdown contribution;
- exposure and holding time;
- policy compliance and execution quality.

These targets must not be used as substitutes for market outcome, forecast correctness, or decision quality.

## 4. Target registry: mandatory semantic contract

Every target must have:
- stable `target_id` and immutable `target_version`;
- `target_family` and exact event/quantity;
- target formula or event predicate;
- instrument/feed and price-side convention;
- decision cutoff and eligible observation start;
- horizon/expiry and endpoint selection;
- units, scaling and rounding;
- event space and partition semantics;
- confirmation and availability rules;
- ambiguity, censoring and missing-source rules;
- cost/execution assumptions, if relevant;
- provenance and source revisions;
- intended task/consumer and evaluation protocol;
- known limitations and unsupported interpretations.

Any change to formula, price side, horizon, threshold, cost model, event-space, confirmation, ambiguity or censoring behavior creates a new version. Existing releases are never silently relabeled.

## 5. Recommended compact target portfolio — candidates only

The detailed F01–F08 to Y01–Y06 crosswalk and provisional redundancy decisions are owned by TARGET_PORTFOLIO_AND_REDUNDANCY_DECISION.md. This section summarizes the current design boundary; it does not approve target generation.

| Candidate | Portfolio role | Provisional disposition |
|---|---|---|
| Y01 Fixed-horizon return distribution | Primary market-outcome target candidate | Core candidate; exact horizon/source remain open |
| Y02 Directional partition | Derived projection of Y01 using a frozen neutral band | Not an independent sample family by default |
| Y03 First-passage barriers | Path-sensitive market-outcome target | Conditional on reliable intrabar order or honest ambiguity handling |
| Y04 MFE/MAE | Path/risk sidecar | Conditional; not a default standalone target |
| Y05 Future range/volatility | Future magnitude target | Conditional; separate from current T09 regime state |
| Y06 State transition | Future state-transition target | Deferred until T01/T09 taxonomies and reliability are stable |

Policy, execution, lifecycle, process-quality and net-trade outcome targets are separate namespaces. They are not part of the initial market-forecast core unless their own source/policy provenance and downstream consumer are proven.

Do not instantiate every target family, horizon, timeframe and barrier multiplier. Remove redundant projections and targets without a distinct consumer or reliable resolution rule.

## 6. Probability semantics and mathematical consistency

### 6.1 Mutually exclusive class partition

A vector such as UP / DOWN / NEUTRAL is a valid categorical distribution only when:
- classes are mutually exclusive;
- classes are exhaustive for all resolved outcomes;
- threshold boundaries are explicitly assigned;
- ambiguous/censored/unavailable cases are not forced into a class.

Only then must class probabilities be non-negative and sum to one within a declared numerical tolerance.

### 6.2 Independent event probabilities

Events such as “upper barrier touched”, “volatility exceeded threshold” and “news event occurred” can overlap. Their probabilities are independent event estimates and must not be forced to sum to one.

### 6.3 Different probabilities are different targets

Do not conflate:
- probability price rises over horizon;
- probability upper barrier is reached first;
- probability a fully specified hypothetical trade is net profitable;
- probability a setup meets a named policy;
- probability an order fills under a specified execution model.

Each requires its own target ID/version, horizon, event space and evidence.

### 6.4 Calibration

A probability is not a model's self-reported confidence. Evaluation must include proper scoring rules (Brier/log loss where appropriate), reliability diagrams, calibration uncertainty and temporal/regime breakdowns. Calibration maps must not be fitted on the final test set.

## 7. Thresholds, barriers and horizon selection

Every threshold must be:
- fixed ex ante or calculated only from information available at decision time;
- expressed in explicit price/return/volatility units;
- versioned with exact formula and parameters;
- selected without inspecting final-test outcomes;
- tested for reasonable sensitivity and prevalence stability.

Avoid arbitrary thresholds selected to create balanced classes. Preserve natural class prevalence and use training/evaluation methods appropriate for imbalance.

Horizon is a target property, not automatically equal to chart timeframe. Select a small number of horizons that correspond to actual downstream decisions and source resolution. Record overlapping windows and effective independent episode counts.

## 8. Ambiguity, censoring and resolution rules

Keep the canonical label_status domain distinct:
- PENDING: target window/confirmation is not complete.
- RESOLVED: target outcome is determined under its registered rule.
- AMBIGUOUS: multiple outcomes remain possible under available evidence.
- CENSORED: observation definitively ends before target resolution under the censoring rule.
- UNAVAILABLE: required source evidence is absent.
- INVALID: target construction fails validation.

NOT_APPLICABLE belongs to field/entity applicability, not label resolution. A target that does not apply should be omitted or represented through a separately defined applicability field; do not add NOT_APPLICABLE to label_status.

Specific rules:
- If both barriers are touched within an OHLC bar and no valid intrabar sequence exists, label AMBIGUOUS.
- If the target horizon extends beyond available data, label CENSORED/PENDING according to whether observation is still ongoing or definitively ended.
- A missing endpoint is not a zero return or neutral class.
- A gap across a barrier requires a declared gap/first-observable-price rule; do not assume a fill at the barrier.
- Late corrections and revised source data must be versioned and their availability times preserved.
- Ambiguity is informative metadata; do not discard it merely to simplify classification.

## 9. Policy labels: prevent hindsight imitation

A policy/action label is admissible only if the policy is reconstructable at decision time:
- policy ID/version and exact rule set;
- eligible inputs and their availability cutoffs;
- account/instrument constraints used;
- deterministic risk result references;
- evidence supporting and contradicting the action;
- allowed action set and abstention conditions;
- policy output timestamp and expiry.

If no defensible historical policy existed, do not fabricate a “correct action” label from subsequent price movement. A separately named counterfactual policy simulation may be studied only with a fully specified policy and explicit simulation provenance.

A policy label must not be named “profitable trade” or “best action” unless its definition truly evaluates that exact concept under complete costs, constraints and execution assumptions.

## 10. NO_TRADE and abstention are first-class outcomes

NO_TRADE is not a negative class or failed prediction. It may be correct because:
- evidence is insufficient or contradictory;
- inputs are stale or unavailable;
- setup conditions are incomplete;
- reward/risk is inadequate under the named policy;
- deterministic risk constraints prohibit entry;
- execution conditions are unsafe or unknown.

WATCH and WAIT_FOR_CONFIRMATION are also distinct: WATCH means monitor a candidate; WAIT_FOR_CONFIRMATION means a specific missing condition prevents a decision. ABSTAIN means the system cannot safely or validly produce the requested output.

Evaluate coverage and abstention quality alongside conditional performance. Never optimize apparent accuracy by silently excluding difficult cases.

## 11. Trade-management labels: sequence, not hindsight snapshots

For management tasks, preserve each decision point as a chronological prefix:
- verified position/order state;
- information available by the decision cutoff;
- original thesis and invalidation;
- new evidence and changed conditions;
- deterministic risk calculation reference;
- policy action proposed;
- authorization state;
- actual subsequent broker event, stored only as later outcome.

Do not create labels such as “move stop to breakeven at +1R” as universal truths. Each management action belongs to a named policy and must be evaluated across regimes, cost conditions, tail risk and execution constraints.

A request to close is not a closed position. A stop modification proposal is not a confirmed broker modification. Unknown broker state must lead to reconciliation/abstention, not fabricated state.

## 12. Label leakage firewall

For a decision timestamp (t_d), model inputs may contain only records whose defensible `available_at <= t_d`.

The following are target-only for that same example:
- future prices/bars/quotes;
- future excursions and barrier outcomes;
- target confirmation time;
- future state/structure confirmation;
- post-decision news/revisions;
- fills, realized costs and position changes occurring later;
- final trade P&L and post-trade commentary;
- labels or explanations derived from any of the above.

Separate input and target namespaces/storage. Enforce automated dependency checks before any future release. A timestamp field alone does not prove absence of leakage; trace the actual dependency graph.

## 13. Sampling, overlapping labels and effective sample size

A million rows generated from adjacent overlapping windows may represent far fewer independent market episodes.

Define:
- episode boundaries and event identity;
- target-window overlap rules;
- sampling cadence per task;
- duplicate/near-duplicate policy;
- minimum separation or clustering rule;
- purge/embargo behavior across chronological splits.

Group related decision points and overlapping sequences by episode before assigning splits. Report raw row count and effective independent episode count separately. Do not use random row splitting for temporal market data.

## 14. Label reliability and independent reproduction

Before a target is admitted:
1. Independently implement/reproduce its rule from the same versioned evidence.
2. Test boundary values, gaps, session transitions and timestamp edges.
3. Compare independent labelers/algorithms for subjective targets.
4. Quantify disagreement and unresolved/ambiguous prevalence.
5. Test parameter and price-side sensitivity.
6. Audit prevalence over time, regime, session and source.
7. Confirm every resolved label has complete provenance.
8. Freeze the target definition before final-test evaluation.

For discretionary SMC/structure labels, do not call annotations ground truth unless operational consistency and independent agreement justify it.

## 15. Evaluation must match the target

| Target family | Appropriate evaluation |
|---|---|
| Return/distribution | MAE/RMSE or robust loss, quantile loss, distribution calibration |
| Directional partition | Per-class precision/recall, balanced accuracy, confusion matrix, Brier/log loss |
| First-passage | Event/multiclass scoring, calibration, ambiguity and censoring rates |
| MFE/MAE | Error/quantile loss and tail/interval coverage |
| Time-to-event | Censoring-aware survival metrics |
| Volatility/range | Error/quantile loss, interval coverage, temporal stability |
| State transition | Transition precision/recall, timing tolerance, label reliability |
| Policy actions | Policy compliance, unsafe-action rate, abstention/coverage, constraints |
| Execution | Fill/rejection/latency/cost accuracy against verified broker records |
| Net trade outcome | Net expectancy, drawdown, tail loss, cost sensitivity and confidence intervals |
| Lifecycle sequence | State reconstruction, event ordering, reconciliation and action safety |

Always compare against meaningful simple baselines, including NO_TRADE where applicable. Report confidence intervals, period/regime/source breakdowns, sample counts and effective episode counts. A favorable metric without realistic costs or independent temporal evidence is not proof of trading edge.

## 16. Dataset construction rules

- Inputs and future targets must be physically/logically separated in the data contract.
- Target values may be joined only in a controlled labeling/evaluation stage.
- Every label stores target definition/version, source revisions, computation run and confirmation time.
- Preserve unresolved records with typed status where useful; do not coerce them to resolved labels.
- Synthetic labels are allowed only for software/schema edge-case fixtures, marked synthetic and isolated from empirical data.
- Human rationales must cite evidence and identify observation vs interpretation.
- Never copy a narrative explanation into multiple samples and count it as independent information.
- Corrections produce new immutable dataset versions and impact reports.

## 17. Promotion gates

A target can move from PROPOSED to SPECIFIED only when its event, units, timing and edge cases are unambiguous.

It can move to IMPLEMENTATION-READY only after:
- source coverage, point-in-time availability and rights are established;
- target can be independently reproduced;
- ambiguity/censoring and overlap rules are tested on representative evidence;
- task consumer and horizon are justified;
- metrics/baselines and temporal split protocol are frozen;
- leakage firewall is testable;
- Stage 5 compatibility is reviewed;
- user explicitly authorizes the next phase.

No target is empirically ACCEPTED based on a design document alone.

## 18. Open decisions

- Which small subset of Y01–Y06 has distinct value for the first model objective.
- Decision cadence and horizons justified by actual source granularity.
- Price side/feed and gap/endpoint conventions.
- Neutral-band and barrier definitions, if selected.
- Effective episode and overlap policy.
- Whether reliable policy labels and historical deterministic risk snapshots exist.
- Whether execution evidence is sufficient for any net-trade targets.
- Exact per-target sample sufficiency and confidence interval approach.

## 19. Gate and exclusions

This is a Phase 0 target governance design. It does not authorize:
- inspection or processing of the uploaded XAUUSD archive;
- acquisition of market/news/broker data;
- target or label generation;
- changes to Stage 5 or AURORA QUANT;
- pipeline implementation;
- model training or benchmarking;
- merging this branch into `main`.

All such work requires the relevant prior gate and explicit user approval.
