# Trading Scenario Specification — Phase 0

## 1. Purpose and boundary

Specify how a future model may describe plausible XAUUSD paths and reason about conditional actions. This is a design contract only; no market data, scenarios, labels, or training examples are being produced.

A scenario is a conditional hypothesis, not a prediction presented as certainty and not an order instruction. The model must be able to conclude that evidence is insufficient.

## 2. Preserve the original architecture

This specification extends—not replaces—the initial A–M task architecture:
- A–D supply market structure, SMC candidates, multi-timeframe context, and regime/volatility.
- E supplies separately defined probabilistic forecasts.
- F consumes evidence and forecasts to assess a conditional setup or abstain.
- G supplies deterministic risk/account/instrument constraints.
- H–J cover monitoring, execution, and chronological trade lifecycle.
- K supplies point-in-time news/fundamental context where feasible.
- L is an optional visual evidence path, synchronized to canonical market data.
- M is a concise, evidence-linked explanation layer.

The prioritized T01–T11 catalog is a compact grouping of these capabilities, not a deletion of the original A–M scope. Candidate tasks remain subject to feasibility and incremental-value tests.

## 3. Scenario object

A future scenario record should contain the following conceptual fields. Final machine schema and required/optional status remain pending source and Stage 5 compatibility review.

| Field | Contract |
|---|---|
| scenario_id | Stable identifier within one decision snapshot |
| snapshot_id | Reference to canonical point-in-time market context |
| decision_timestamp | Exact time at which the scenario set is formed |
| scenario_type | bullish, bearish, range, transition, or unresolved; exact taxonomy to be frozen |
| hypothesis | Short, falsifiable description of the possible path |
| evidence_refs | References to observed facts and validated features |
| supporting_evidence | Evidence supporting the hypothesis |
| conflicting_evidence | Evidence weakening or contradicting it |
| required_conditions | Observable conditions that must occur before activation |
| invalidation_conditions | Observable conditions that make it no longer valid |
| expected_path | Conditional sequence or zone/event description, not fabricated precision |
| horizon_or_expiry | Explicit time or event expiry |
| probability | Optional calibrated probability tied to a defined event space |
| probability_model_version | Required whenever probability is supplied |
| uncertainty | Explicit limitations, ambiguity, and data-quality constraints |
| scenario_status | DRAFT/CANDIDATE/ACTIVE/TRIGGERED/COMPLETED/INVALIDATED/EXPIRED/CANCELLED/SUPERSEDED lifecycle; see scoped enum governance |
| next_observation | What new evidence would change the assessment |

A scenario must not contain a probability unless its event is precisely defined and calibration has been evaluated. Qualitative plausibility rankings must not be disguised as numeric probabilities.

## 4. Scenario generation protocol

At a decision timestamp, the future system should:

1. Freeze an as-of snapshot; exclude unavailable or partial information unless explicitly modeled as partial.
2. Summarize market state, relevant structure, volatility, and timeframe alignment/conflict.
3. Identify a small number of materially distinct plausible paths. Do not generate several paraphrases of the same path.
4. For each path, state supporting and conflicting evidence.
5. Define activation conditions and invalidation conditions before observing the future outcome.
6. State the horizon/expiry and what observation would change the assessment.
7. Attach calibrated probabilities only if the target event and calibration protocol are approved.
8. Pass any proposed action through the separate setup and deterministic risk constraints.
9. Prefer unresolved/NO_TRADE when evidence is contradictory, stale, incomplete, or lacks a testable edge.

The number of scenarios is not fixed. The objective is coverage of materially different possibilities, not forced symmetry or a fixed bullish/bearish count.

## 5. Probability semantics

Keep these distinct:
- probability of a directional return event;
- probability of touching a specified upper/lower barrier;
- probability of a regime transition;
- probability that a fully specified trade reaches a net outcome threshold after costs;
- confidence/uncertainty in the model estimate.

These are not interchangeable. A scenario's subjective plausibility is not a calibrated probability. If scenarios are not mutually exclusive and collectively exhaustive, their probabilities must not be forced to sum to 100%.

Calibration must be assessed by horizon, event definition, and relevant regime, with sample counts and uncertainty intervals. Do not infer calibration from a high classification accuracy alone.

## 6. Scenario-to-action separation

Scenario assessment and trading policy are separate tasks.

A scenario may be plausible while no trade is justified because:
- activation conditions have not occurred;
- reward/risk after costs is inadequate;
- spread, volatility, or execution conditions are unacceptable;
- risk limits or account constraints prohibit entry;
- evidence across timeframes materially conflicts;
- the data is stale or uncertain;
- no reliable edge has been demonstrated.

A LONG/SHORT decision must reference a scenario and specify its trigger, invalidation, expiry, and constraints. NO_TRADE is a valid output, not a failure to answer.

## 7. Avoid hindsight and narrative leakage

- Freeze the scenario at decision time.
- Preserve the original scenario even if later invalidated; append later events rather than rewriting history.
- Do not train the model to describe the realized path as if it had been obvious.
- Do not use post-decision candles, MFE/MAE, final outcome, or label-confirmation data in scenario inputs.
- Store scenario revision events with timestamps and reason codes.
- Evaluate calibration and policy separately from narrative plausibility.

## 8. Evaluation questions

A scenario framework is useful only if it demonstrates:
- reproducible event definitions;
- calibrated probabilities where probabilities are claimed;
- meaningful discrimination from simple baselines;
- stable performance across chronological periods/regimes;
- useful conditional invalidation and abstention;
- incremental benefit to downstream decisions after costs and risk constraints.

Long, persuasive explanations are not evidence of predictive value.

## 9. Scenario set: coverage without forced symmetry

A decision snapshot may have zero, one, or several scenarios. The system must not invent a bullish and bearish scenario merely to appear balanced.

A scenario set should:
- cover materially distinct paths that could change the downstream decision;
- avoid paraphrases and cosmetic variants of the same path;
- retain a neutral/range or unresolved possibility when supported;
- identify omitted plausible paths when the evidence space is incomplete;
- distinguish a primary working hypothesis from alternatives without implying certainty;
- preserve scenario identity across revisions within the same decision episode.

Scenarios are not automatically mutually exclusive or exhaustive. If a probabilistic partition is required, define a separate exhaustive event space and its target contract. Do not normalize arbitrary scenario scores into probabilities.

## 10. Operational conditions and falsifiability

Every activation, invalidation, and expiry condition must be expressible as an observable predicate or an explicitly typed human-review condition.

A condition definition should specify:
- condition_id and definition_version;
- referenced source/feature/event IDs;
- comparison/operator and threshold, where applicable;
- price side and unit;
- timeframe and bar-completion rule;
- observation/availability requirement;
- persistence/debounce rule, if any;
- evaluation window and expiry;
- unknown/stale/missing-data behavior;
- whether the condition is a trigger, supporting evidence, invalidation, or safety gate.

Avoid vague conditions such as “strong momentum”, “institutional confirmation”, or “price reacts well” unless translated into a registered operational definition. If a condition cannot be evaluated from available evidence, its state is UNKNOWN—not satisfied.

Do not select thresholds after seeing the future path. Thresholds and parameters must be frozen ex ante or derived only from data available at the decision timestamp.

## 11. Scenario lifecycle and immutable revisions

Use the canonical scenario lifecycle and transition rules in SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md:

    DRAFT → CANDIDATE → ACTIVE → TRIGGERED → (COMPLETED | INVALIDATED | EXPIRED | CANCELLED)

SUPERSEDED is available only when an explicitly linked replacement revision supersedes this scenario. Not every scenario passes through every state. Terminal states cannot be silently reopened.

UNRESOLVED is an assessment state, not a lifecycle state. Where a separate point-in-time assessment is needed, use scenario_assessment = SUPPORTED | CONTRADICTED | UNRESOLVED. Each assessment revision preserves its evidence and timestamp.

Condition predicates use condition_state = NOT_EVALUATED | TRUE | FALSE | UNKNOWN | STALE | INVALID. UNKNOWN, STALE, INVALID and NOT_EVALUATED never satisfy a trigger. Each evaluation is an immutable time-stamped record; later evidence must not backdate an earlier condition result.

Rules:
- Creation records the original hypothesis and evidence snapshot.
- Activation requires the registered trigger predicate to be observed and available.
- Triggered means the scenario condition occurred; it does not mean an order was submitted or filled.
- Invalidation and expiry are distinct: invalidation is evidence against the thesis; expiry is the end of its declared validity window.
- Cancellation is an explicit policy/user action, not a market outcome.
- Completion requires a registered terminal event definition.
- Later evidence creates an append-only revision/event; it never rewrites what was known at the original decision time.
- Corrections to source data create traceable revisions and must not backdate knowledge availability.

A scenario revision should include prior_revision_id, new_revision_id, revision_time, available_at, reason_code, changed_fields, new_evidence_refs and actor/policy version. Preserve the original and all intermediate revisions.

## 12. Scenario-to-policy decision gate

The scenario layer proposes conditional hypotheses. The policy layer independently decides whether any action is justified.

A future policy evaluation should check, in order:
1. Input validity: is the snapshot complete enough, fresh, correctly synchronized and point-in-time valid?
2. Evidence sufficiency: does at least one scenario have traceable supporting evidence, with material contradictions disclosed?
3. Trigger state: is the required trigger confirmed, or is WAIT_FOR_CONFIRMATION the correct output?
4. Invalidation/expiry: is the scenario still valid and within its declared horizon?
5. Forecast semantics: are probabilities tied to the exact target, event space and horizon, with calibration evidence?
6. Trade economics: are entry type, price-side convention, costs, gap/slippage assumptions and cost-adjusted reward/risk defined?
7. Deterministic risk: has the authoritative risk engine returned a current, valid, permitted result?
8. Execution feasibility: are spread, market state, broker availability and order constraints acceptable and evidenced?
9. Action authorization: does the named policy permit the proposed action and size?

If a mandatory gate is failed or unknown, the policy must choose the appropriate non-entry/abstention outcome, request fresh evidence, or require deterministic recalculation. A plausible scenario alone never authorizes LONG or SHORT.

## 13. Action output must remain distinct from scenario description

A decision record references scenario IDs and separately identifies:
- action class: LONG, SHORT, NO_TRADE, WATCH, WAIT_FOR_CONFIRMATION, or ABSTAIN;
- action/policy definition version;
- decision timestamp and expiry;
- selected scenario and rejected/retained alternatives;
- trigger state and evidence references;
- entry intent/type and permitted range, if applicable;
- stop/invalidation and target logic;
- cost and execution assumptions;
- deterministic risk result reference and constraint status;
- reason codes and unresolved conditions.

The scenario record itself must not claim that an order was placed, accepted, filled, or that a position exists. Those facts belong to the execution/lifecycle event stream. A policy recommendation is not an instruction to bypass authorization or broker safeguards.

## 14. Contradiction and uncertainty handling

Contradictions must be represented, not hidden by a single aggregate score.

Examples include:
- higher timeframe trend conflicts with lower timeframe trigger;
- price structure conflicts with momentum/volatility evidence;
- two feeds disagree beyond a declared tolerance;
- a news interpretation conflicts with the primary source record;
- a partial bar suggests a condition that is absent on completed bars;
- scenario probability estimates disagree across models or regimes.

For each material conflict, preserve both evidence references, their availability/freshness, the conflict type and its decision relevance. Do not average incompatible sources without a registered reconciliation rule.

Uncertainty should distinguish at least missing/stale source evidence, provisional/unconfirmed structure, target/event ambiguity, model estimation uncertainty, calibration uncertainty, source disagreement, and policy/constraint uncertainty.

A model's fluent explanation or self-reported confidence is not a substitute for calibrated uncertainty.

## 15. Scenario evaluation and audit metrics

Evaluate scenario quality separately from language quality and realized trade P&L.

Candidate evaluation dimensions:
- Definition validity: proportion of conditions reproducibly evaluable from registered evidence.
- Temporal validity: trigger/invalidation/expiry availability-time correctness.
- Coverage: whether material outcome paths are represented without forced scenario inflation.
- Distinctness: duplicate/paraphrase rate among scenarios in the same set.
- Falsifiability: proportion with testable activation and invalidation predicates.
- Probability quality: proper scoring and calibration only for approved, well-defined events.
- Revision discipline: whether updates preserve prior versions and use only newly available evidence.
- Policy usefulness: incremental decision value over simple scenario-free baselines after costs and constraints.
- Abstention quality: unsafe-action avoidance and performance/coverage trade-off.
- Robustness: stability across chronological periods, regimes, sessions and source/feed changes.

Report denominators, unresolved cases, missing evidence, sample/episode counts and uncertainty intervals. Do not score a scenario highly merely because its narrative resembles the realized path after the fact.

## 16. Dataset representation and anti-duplication

The canonical snapshot, feature, forecast, risk and lifecycle records remain separately owned. A scenario dataset should reference these entities by stable IDs and versions rather than copying their full payloads into every example.

Store one scenario-set identity per decision snapshot and task definition; stable scenario identity and append-only revision history; evidence references rather than repeated prose summaries as pseudo-evidence; explicit scenario/decision policy version; independent outcome labels in the target namespace; and episode/group identity for overlapping snapshots and related scenarios.

Do not create multiple training rows from minor wording variations of the same scenario. If several scenarios share the same evidence and differ only in narrative phrasing, deduplicate or keep one canonical representation. Preserve genuinely distinct conditional paths only when their trigger, invalidation, expected path, or downstream consequence differs materially.

## 17. Minimum viable scenario capability — research priority only

The first scenario capability should be deliberately narrow:
- current snapshot and evidence references;
- only materially distinct bullish, bearish, range/neutral, or unresolved hypotheses supported by evidence;
- explicit trigger, invalidation, expiry and next-observation conditions;
- separate supporting and conflicting evidence;
- no numeric scenario probability unless the event is registered and calibrated;
- separate policy action with NO_TRADE/WAIT/ABSTAIN options;
- reference to deterministic risk feasibility for any actionable plan.

Advanced path trees, many nested sub-scenarios, free-form price projections, news narratives, image-only scenarios and model-generated trade sizing are not core requirements. Add them only if a named task needs them and incremental value is demonstrated.

## 18. Freeze and promotion gates

Before scenario definitions can be frozen:
1. Reconcile this contract with the canonical data model, field/status semantics, T04 task I/O and lifecycle policy.
2. Define exact scenario types and status domains without duplicating generic field-status enums.
3. Specify condition predicate semantics and unknown/stale handling.
4. Define scenario-set identity, revision and episode grouping.
5. Select only task-relevant decision horizons after source feasibility.
6. Freeze probability event spaces separately from scenario taxonomy.
7. Define evaluation baselines, abstention metrics and chronological split protections.
8. Confirm Stage 5 compatibility after its independent acceptance.
9. Obtain explicit user approval.

This document does not authorize data inspection, scenario generation, label creation, implementation, backtesting, model training, or changes to AURORA QUANT or Stage 5.