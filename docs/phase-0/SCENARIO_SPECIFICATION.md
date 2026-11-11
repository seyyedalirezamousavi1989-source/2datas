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
| status | candidate, active, invalidated, expired, or unresolved |
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
