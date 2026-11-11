# Temporal Trade Lifecycle and Management Policy — Phase 0

## 1. Purpose and status

Define the temporal reasoning contract for trade lifecycle and position management tasks. This is a research/design specification only. It does not authorize trading, order placement, dataset generation, or implementation.

The core learning objective is to teach the model to reassess a position as new evidence arrives, while preserving the original decision, respecting deterministic risk controls, and avoiding hindsight bias.

## 2. Three independent timelines

Every lifecycle example must keep three timelines distinct:

1. **Market timeline:** event time of quotes, bars, news and market observations.
2. **Knowledge timeline:** when each observation actually became available to the system.
3. **Trading-system timeline:** decision, request, acknowledgement, fill, modification, cancellation and reconciliation times.

Never assume these clocks are identical. Preserve source clock, timezone, offset, receipt time and clock-quality metadata where available.

## 3. Lifecycle state model

A proposed position lifecycle may include:

- FLAT — no open position is verified.
- SETUP_WATCH — a possible setup is being monitored; no order exists.
- ENTRY_ELIGIBLE — activation conditions appear satisfied, but risk/approval checks remain.
- ORDER_PENDING — an order request was sent; execution is not yet confirmed.
- PARTIALLY_FILLED — some quantity is broker-confirmed filled.
- OPEN — a broker-confirmed position exists.
- REDUCING — a close/reduction request is pending or partially filled.
- EXIT_PENDING — full exit request is pending; position may still exist.
- CLOSED — broker-confirmed residual position is zero and reconciliation is complete.
- REJECTED / CANCELLED / EXPIRED — order/setup terminal status with reason.
- UNKNOWN / RECONCILIATION_REQUIRED — evidence is conflicting, incomplete or stale.

These states must not be collapsed into a single “trade active” boolean. A transition requires an evidenced event and validation rule. Some broker workflows require additional intermediate states.

## 4. State transition evidence

Examples of valid evidence:
- SETUP_WATCH → ENTRY_ELIGIBLE: trigger condition is satisfied using available market evidence.
- ENTRY_ELIGIBLE → ORDER_PENDING: authorized order request event exists.
- ORDER_PENDING → PARTIALLY_FILLED / OPEN: broker execution/deal event confirms quantity.
- OPEN → REDUCING / EXIT_PENDING: authorized close/modify request is recorded.
- REDUCING → OPEN / CLOSED: subsequent broker fills and reconciled residual quantity determine state.
- Any state → RECONCILIATION_REQUIRED: broker events conflict, sequence gaps exist, or state freshness fails.

A model's text output is never sufficient evidence of a state transition.

## 5. Management decision cycle

At each approved observation point, a management task should follow this sequence:

1. **Reconcile:** identify current broker-confirmed order/deal/position state and unresolved events.
2. **Freshness check:** verify quote, snapshot, instrument specification and risk inputs are current enough for this decision.
3. **Reconstruct:** summarize original thesis, entry assumptions, invalidation, expiry and approved constraints without rewriting history.
4. **Observe change:** identify new market facts and distinguish them from derived features and interpretations.
5. **Reassess scenarios:** determine whether the original scenario remains valid, is weakened, invalidated, or replaced.
6. **Evaluate risk:** request/consume a fresh deterministic calculation for proposed changes; never estimate authoritative volume or loss.
7. **Select action:** choose one canonical management_action (HOLD, MOVE_STOP_TO_BREAK_EVEN, TRAIL_STOP, REDUCE_PARTIAL, CLOSE_POSITION, EXTEND_TARGET, TIME_EXIT, EMERGENCY_RISK_REDUCTION, NO_ACTION or ABSTAIN) under the task policy.
8. **State preconditions:** specify the evidence and authorization required before any external action.
9. **Record:** append the recommendation and references; never mutate the prior decision.
10. **Verify:** if an action is separately authorized and executed, rely on broker events and reconciliation—not the request—to establish its result.

## 6. Management action contract

Each proposed action must carry:
- action and policy version;
- position/order identity references;
- decision snapshot and event-history cutoff;
- reason and evidence references;
- preconditions;
- expected state transition;
- invalidation and expiry;
- risk recalculation reference if required;
- approval/authorization requirement;
- abstention reason if not safe to recommend.

Action semantics (canonical values are governed by SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md):
- HOLD: affirmative recommendation to maintain the verified current position under current policy.
- MOVE_STOP_TO_BREAK_EVEN: proposed stop change; account for spread, commission, swap, conversion and broker constraints. It is not automatically net break-even.
- TRAIL_STOP: versioned rule with activation, reference side, step/update conditions, minimum distance and stop-side validation.
- REDUCE_PARTIAL: request a smaller exposure; residual size is unknown until broker confirmation.
- CLOSE_POSITION: request full exit; the position remains open/pending until fills and reconciliation confirm closure.
- EXTEND_TARGET: permitted only by an approved policy and fresh evidence/risk review.
- TIME_EXIT: exit due to a registered time/horizon rule.
- EMERGENCY_RISK_REDUCTION: reduce risk under an explicitly defined emergency policy.
- NO_ACTION: no management change is justified at this evaluation; it does not imply missing evidence.
- ABSTAIN: state/data/risk uncertainty makes a safe recommendation impossible.
- Recalculation is a required control step/reference, not a management action class.
- WAIT is not a management action; use NO_ACTION or ABSTAIN with a reason and next-observation condition.

## 7. Stop-loss and take-profit semantics

Do not teach a universal rule that every trade must move to breakeven at a fixed R multiple or trail at a fixed distance.

For each management policy, explicitly define:
- initial stop basis and invalidation logic;
- whether stop is structural, volatility-based, fixed, or policy-defined;
- activation condition for breakeven or trailing;
- treatment of spread, commission, swap and conversion;
- broker minimum stop distance, freeze level, tick size and volume constraints;
- gap/slippage risk and the fact that stop price is not guaranteed fill price;
- partial-close rounding and remaining exposure;
- whether the action is a proposal, approved request, or confirmed broker modification.

Evaluate policies across multiple regimes and cost assumptions. A policy that raises win rate may still reduce expectancy or increase tail risk.

## 8. Partial fills, reversals and exceptional events

Represent partial fills as separate deal events. Maintain requested quantity, filled quantity, remaining quantity and broker-reported residual position separately.

Handle:
- rejection and rejection reason;
- requote and changed quote;
- timeout with unknown execution status;
- duplicate/replayed event (idempotency);
- out-of-order event delivery;
- partial fill followed by cancel;
- cancel/replace race;
- broker-side stop-out or forced liquidation;
- manual user intervention;
- connection loss and later reconciliation;
- corporate/broker symbol or specification changes where relevant.

Never infer “not executed” from a missing acknowledgement. Unknown execution status requires reconciliation.

## 9. Hindsight-safe management targets

Keep separate:
- what action was proposed at time t;
- what policy permitted at time t;
- what user/system authorized;
- what broker actually executed;
- what market did afterward;
- what realized costs and outcome resulted.

Do not use eventual profit as the sole label for a correct management action. Assess process compliance, information available at the time, risk path, execution quality and eventual outcome as separate dimensions.

For sequence learning, each step's input is a prefix of events available by that step. Future events and final outcome are target-only data.

## 10. Sequence construction and sampling

A lifecycle sequence is a set of ordered decision points linked to one position/order lineage, not a set of paraphrased chat messages.

Each step should reference:
- stable episode, order, deal and position IDs;
- prior event/decision references;
- current snapshot and knowledge cutoff;
- current state and reconciliation status;
- proposed action and its target/policy definition;
- subsequent event/outcome only in isolated target storage.

Do not create one training example per tick. Use a declared decision cadence or event-triggered sampling rule. Retain meaningful state changes, invalidations, exceptional execution events and representative no-action intervals. Cluster overlapping sequences by episode before splitting.

## 11. Sequence evaluation

Evaluate both per-step and whole-episode behavior:
- state reconstruction accuracy;
- event ordering and reconciliation;
- action/policy compliance;
- unsafe action and hard-constraint violation rate;
- abstention when state is unknown/stale;
- stop/position management behavior under realistic costs;
- net expectancy, drawdown and tail loss as downstream outcomes;
- robustness by regime, session, spread and broker;
- sensitivity to missing, delayed and out-of-order events.

Compare with no-management/hold baselines, simple predeclared management rules, deterministic policy baselines, and existing AURORA components where independently verified.

Do not report episode P&L without process and risk metrics.

## 12. Freeze criteria

This contract is not ready for implementation until:
- broker event availability and identifier quality are verified;
- state transitions are mapped to actual broker semantics;
- risk/stop/volume constraints are specified per instrument and broker;
- policy action taxonomy is frozen;
- sequence boundaries and sampling cadence are justified;
- point-in-time replay and reconciliation tests are defined;
- baselines and metrics are frozen;
- Stage 5 compatibility is audited;
- the user explicitly approves implementation.
