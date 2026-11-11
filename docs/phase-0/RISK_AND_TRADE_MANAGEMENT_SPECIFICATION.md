# Risk and Trade Management Specification — Phase 0

## 1. Purpose and safety boundary

Specify the information a future model may interpret across sizing, entry, protection, monitoring, and exit. This document does not implement calculations or authorize trading.

**Authority rule:** account, instrument, sizing, margin, exposure, execution, and hard risk limits are calculated and enforced by deterministic, tested components. The model may explain, critique, compare scenarios, request recalculation, or recommend less risk/NO_TRADE. It must never invent or override authoritative values.

## 2. End-to-end lifecycle

The conceptual lifecycle is event-based:

1. **Pre-trade context** — timestamped account snapshot, instrument specification, market snapshot, spread/cost context, existing exposure, policy constraints.
2. **Setup assessment** — conditional scenario, activation trigger, invalidation, expiry, and evidence.
3. **Risk feasibility** — deterministic calculator output and hard-constraint result.
4. **Order intent** — proposed side/type/volume/price constraints with idempotent intent identifier.
5. **Broker response** — accepted/rejected/partial/filled/cancelled/requoted, with broker identifiers and timestamps.
6. **Position monitoring** — current verified position, quotes, costs, risk, and market evidence.
7. **Management event** — hold, reduce, protect, move stop, partial close, full close, or no action.
8. **Reconciliation** — compare internal state with broker-confirmed orders/deals/positions; resolve discrepancies.
9. **Post-trade review** — realized costs/outcome and process-quality assessment, kept out of pre-decision inputs.

A position lifecycle must be represented by ordered events, not one final summary row that hides intermediate decisions.

## 3. Deterministic risk input contract

A risk calculation request may require:
- account ID/reference and account currency;
- balance, equity, free margin, margin level and timestamp;
- instrument symbol and broker/server identity;
- contract size, tick size, tick value, calculation mode, volume minimum/maximum/step;
- leverage, margin rules, stop-out rules and trading restrictions;
- side, order type, entry assumptions, stop level and relevant quote side;
- currency conversion rates and their timestamps where required;
- commission, spread, slippage assumptions, swap/financing and other applicable costs;
- current positions, pending orders, correlated exposure policy and daily loss state;
- requested risk budget and policy limits.

All inputs must carry source, timestamp, validity, and status. If a required fact is missing or stale, calculation should fail closed or return an explicitly constrained/unknown result—not silently substitute a generic value.

## 4. Calculation and validation requirements

The deterministic engine must document and test:
- stop distance in the instrument's actual price/point/tick convention;
- side-aware loss calculation at stop, including applicable costs;
- account-currency conversion;
- contract and tick-value semantics, including broker-specific calculation modes;
- volume-step rounding and min/max constraints;
- post-rounding risk recomputation;
- margin and free-margin feasibility;
- aggregate exposure across open positions and pending orders;
- daily loss, drawdown, consecutive-loss and trade-count constraints where configured;
- gap/slippage stress assumptions and stop execution limitations.

A naive formula based only on stop distance and a generic pip value is insufficient for all XAUUSD brokers/accounts. Never hardcode universal gold contract specifications.

## 5. Risk output contract

A deterministic risk response should expose:
- calculation ID and engine/version;
- input snapshot references and timestamps;
- requested risk budget and applicable hard limits;
- estimated loss at stop and cost assumptions;
- permitted volume before and after broker-step rounding;
- recomputed risk after rounding;
- margin estimate and feasibility status;
- exposure and daily-limit status;
- warnings, missing inputs, and rejection reason codes;
- expiry/valid-until timestamp.

The model may summarize this output, identify inconsistencies, and recommend a lower-risk alternative. It cannot edit the calculator result or treat an estimate as a guaranteed loss cap under gaps/slippage.

## 6. Trade-management action taxonomy

Candidate action vocabulary:
- HOLD / NO_ACTION;
- REDUCE_POSITION;
- MOVE_STOP_TO_DEFINED_LEVEL;
- MOVE_STOP_TO_BREAK_EVEN;
- TRAIL_STOP;
- PARTIAL_TAKE_PROFIT;
- CLOSE_POSITION;
- REQUEST_RECALCULATION;
- ABSTAIN / ESCALATE.

Every proposed action must include:
- current verified position/event reference;
- evidence available at action time;
- reason and expected benefit;
- risk impact before/after, calculated by deterministic engine;
- preconditions and broker constraints;
- invalidation/expiry;
- whether human approval is required.

The action must be conditional on the current broker-confirmed state. A stale position snapshot must not trigger an action.

## 7. Break-even and trailing-stop semantics

Do not define break-even as simply setting stop equal to entry. A true net break-even level may depend on spread, commission, swap, fees, conversion, and execution side. The deterministic engine must calculate the applicable level and disclose assumptions.

Trailing stop rules require an explicit method, activation condition, update cadence, minimum distance, broker stop/freeze levels, and anti-churn policy. Do not create training labels from arbitrary stop movements without a reproducible policy.

## 8. Event integrity and broker reconciliation

The event model must support:
- globally unique event IDs and idempotency keys;
- stable order, deal, and position identifiers;
- event and receive timestamps with clock-source metadata;
- partial fills and multiple deals per order;
- cancel/replace/requote/rejection events;
- corrections and out-of-order delivery;
- broker reconciliation and discrepancy states;
- immutable event history with explicit correction events.

Never assume an order request equals a fill or that an internal position state equals broker reality.

## 9. Execution realism

Evaluation must model or explicitly limit:
- bid/ask side and spread variation;
- commission and swap/financing;
- slippage and latency;
- gaps and stop execution behavior;
- order type, filling mode, rejection, requote, partial fill;
- broker stop/freeze distance and session restrictions.

Candle-only data cannot reliably resolve intrabar event order or actual fills. Where tick/quote/fill data is unavailable, state the limitation and avoid claims of execution realism.

## 10. Risk-management learning targets

Separate:
1. **Constraint interpretation:** explain a deterministic result and why a trade is blocked/allowed.
2. **Management policy:** propose conditional actions from a defined policy and evidence.
3. **Realized outcome:** record what actually happened, including costs and execution.
4. **Process quality:** assess whether the decision followed the information and constraints available at that time.

Do not use a profitable outcome as the sole label for a good management decision. Preserve losing trades with sound process and winning trades with poor process.

## 11. Fail-closed conditions

The model should abstain or request verification when:
- account or instrument data is missing/stale;
- broker position/order state is uncertain;
- risk calculation fails or inputs conflict;
- spread/slippage/volatility exceeds approved limits;
- hard limits are reached;
- scenario trigger or invalidation is unclear;
- execution feasibility cannot be established.

No model output may bypass a deterministic hard safety gate.
