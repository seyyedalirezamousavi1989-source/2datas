# Trade Lifecycle, Decision Policy and Active Risk Management — Phase 0

## 1. Purpose and status

Define a complete, auditable contract for trade-decision intelligence from initial observation through final post-trade review. The goal is to teach disciplined scenario reasoning, risk-aware action selection, and ongoing management—not merely LONG/SHORT classification.

**Design only.** This document does not inspect or modify AURORA QUANT, its trading engine, broker configuration, or Stage 5 artifacts. It does not authorize data acquisition, labeling, implementation, backtesting, model training, or live/demo trading.

Any existing deterministic risk, account, broker, and execution controls remain authoritative. The dataset must not grant a model authority to bypass them.

## 2. Separate objective facts, forecasts, policy and realized outcomes

Keep four layers distinct:

1. **Market observation:** point-in-time price, quotes, spread, volatility, structure and source availability.
2. **Forecast/scenario:** conditional future possibilities with horizon, probability semantics, evidence and invalidation.
3. **Decision/policy:** action selected under a declared strategy, account constraints and risk policy.
4. **Realized execution/outcome:** actual orders, fills, costs, position changes and final P&L.

A profitable trade is not automatically a good decision; a losing trade is not automatically a bad decision. Evaluate the decision using information available at the time and evaluate realized outcomes separately.

Do not use hindsight profitability as the sole ground truth for LONG/SHORT labels. Preserve the strategy/policy version and constraints that produced each action.

## 3. Decision action space

The action vocabulary should be compact and explicit:

- LONG: a long setup satisfies the approved policy and all required gates.
- SHORT: a short setup satisfies the approved policy and all required gates.
- WATCH: a potentially relevant condition exists, but no actionable setup is confirmed.
- WAIT_FOR_CONFIRMATION: a named, observable trigger is still missing.
- NO_TRADE: no trade is justified, evidence is insufficient, or constraints prohibit entry.
- MANAGE_OPEN_POSITION: an existing position requires a management decision.
- EXIT: a defined exit condition is satisfied.

These are policy actions, not market truth labels. NO_TRADE is a valid, important outcome, not a failure class to be balanced away. Preserve reason codes such as insufficient evidence, conflicting timeframes, poor reward/risk, excessive spread, event restriction, stale data, invalid setup, risk limit, or execution unavailable.

## 4. Scenario contract

A scenario is a conditional hypothesis, not a prediction stated as certainty.

Each scenario should identify:
- scenario_id and policy/definition version;
- decision timestamp and eligible market snapshot references;
- direction or neutral outcome;
- thesis and concise supporting evidence references;
- contradictory evidence and unresolved uncertainty;
- trigger conditions and exact confirmation semantics;
- entry type and permissible entry zone/range;
- stop/invalidation logic and the evidence that invalidates the thesis;
- target logic and horizon/expiry;
- estimated costs and execution assumptions;
- risk budget and constraints;
- scenario status (candidate, active, triggered, invalidated, expired, cancelled, completed);
- time created, time activated and time invalidated/expired.

Store alternative scenarios where plausible. Do not force one direction if both bullish and bearish paths remain credible. If no scenario meets the policy, explicitly choose NO_TRADE or WATCH.

## 5. Entry and trigger discipline

Distinguish a planned entry from an executable order and an actual fill.

A setup record must define:
- market/limit/stop order intent, if relevant;
- trigger condition and whether it is based on close, wick, quote, or event;
- permissible entry range and maximum chase distance;
- confirmation timeframe and bar-completion requirement;
- spread and slippage assumptions/limits;
- order expiry and cancellation conditions;
- behavior if price gaps through the intended entry;
- behavior if trigger occurs while source data is stale or incomplete.

Never infer a fill from a candle touching a planned price. Actual fill requires broker/execution evidence. Candle-only data cannot establish the precise intrabar sequence or executable quote.

## 6. Stop loss, target and reward/risk semantics

A stop and target must be grounded in a declared setup/invalidation logic and instrument price conventions.

Record:
- planned entry reference/range;
- stop price and stop rationale;
- target price(s) and target rationale;
- stop/target distance in price units and ticks;
- gross reward/risk and cost-adjusted expected reward/risk where calculable;
- price side used for entry and exit;
- gap, spread, commission, slippage and swap assumptions;
- whether stop/target is static or rule-adjusted;
- conditions that invalidate the original calculation.

A visually attractive reward/risk ratio does not establish positive expectancy. Targets and stops must not be moved retrospectively to fit the realized path. Any adjustment is a new management event with timestamp, reason and before/after values.

## 7. Deterministic risk authority

Position sizing and account constraints must be calculated by a deterministic, tested engine using authoritative current account and broker data—not generated as free-form model text.

Inputs may include:
- equity/balance and account currency;
- risk budget and strategy/account caps;
- symbol contract size, tick size/value and profit calculation mode;
- volume minimum, maximum and step;
- entry/stop price and applicable bid/ask side;
- currency conversion rates and their timestamps;
- commission, swap, margin and leverage rules;
- open positions, pending orders and correlated exposure;
- daily loss, total drawdown, consecutive-loss and trade-count limits;
- broker stop/freeze levels and execution constraints.

The engine must validate all inputs, reject stale/missing values, calculate loss per lot under broker-specific semantics, round volume only according to broker rules, and recalculate worst-case risk after rounding. It must check margin and aggregate exposure, not only the individual trade.

The model may explain or challenge a deterministic result, identify inconsistent assumptions, or recommend a lower risk within allowed policy. It must never fabricate account data, contract specifications, conversions, margin, volume, or approval status.

## 8. Trade lifecycle as an event stream

Represent a trade as a sequence of immutable events, not one mutable row that overwrites history.

Potential lifecycle events:
1. market condition observed;
2. setup candidate created;
3. scenario accepted/rejected;
4. entry trigger confirmed;
5. risk calculation requested and validated;
6. order submitted, rejected, cancelled or expired;
7. partial/full fill received;
8. position opened/modified/reduced;
9. stop/target/BE/trailing updated;
10. partial or full exit executed;
11. broker reconciliation/correction;
12. trade closed;
13. post-trade review completed.

Each event should carry event ID, trade/scenario/order/position IDs as applicable, event type, event time, system receive time, source, state_before/state_after, payload schema version, causation/correlation IDs and idempotency key.

Support partial fills, multiple orders, multiple positions, corrections, rejected requests, reconnect/replay and broker reconciliation. Do not assume one order equals one position or that event arrival order always equals exchange/broker event order. Preserve original event and correction history.

## 9. Open-position management

Management decisions are conditional on the current position state and current available evidence.

Potential actions:
- HOLD without change;
- MOVE_STOP_TO_BREAK_EVEN;
- TRAIL_STOP;
- REDUCE_PARTIAL;
- CLOSE_POSITION;
- EXTEND_TARGET only if an approved policy permits it;
- TIME_EXIT;
- EMERGENCY_RISK_REDUCTION;
- NO_ACTION / WAIT.

For each action, require an observable trigger, policy permission, current position/order snapshot, proposed change, estimated incremental risk/cost, and explicit reason. A model suggestion is not proof that a broker modification succeeded; record requested, acknowledged, rejected and confirmed states separately.

Break-even must account for commission, spread, swap and execution costs. A stop at entry price is not necessarily net break-even.

Trailing rules must specify reference price, activation threshold, distance/step, update cadence, minimum modification interval, broker stop/freeze constraints and behavior on gaps or stale quotes.

Partial exits must record requested and actual volume, fill price, residual position, realized costs and recalculated remaining risk. Ensure volume-step/minimum constraints.

## 10. Invalidations, exits and exceptional conditions

A trade thesis can be invalidated before the stop is reached. Conversely, a price touching a planned stop does not prove an actual fill.

Explicitly model:
- structural invalidation;
- scenario expiry/time stop;
- adverse regime transition;
- volatility/spread expansion;
- scheduled-event restriction;
- stale or contradictory market data;
- broker disconnect or execution uncertainty;
- margin or account-risk breach;
- order rejection/requote/gap;
- market closure or trading halt;
- manual intervention and policy override.

Separate thesis_invalidated, exit_decision, exit_order_submitted, and position_closed. They are different events and may occur at different times.

## 11. Costs and execution realism

A simulated outcome must identify what is known and what is assumed.

Preserve bid/ask side, spread history, commissions, swap/financing, slippage, latency, order type, fill policy, partial fills, rejection/requote behavior, gaps, market hours and broker-specific restrictions where source evidence exists.

When only OHLC bars are available, label execution assumptions as approximate. If stop and target are both touched within the same bar and tick sequence is unavailable, mark outcome ambiguous or use a declared conservative rule; never choose the favorable order retrospectively.

Do not treat a theoretical entry/exit price as an actual fill. Separate market-path labels from executable trade outcomes.

## 12. NO_TRADE and abstention intelligence

Include examples where:
- no reliable setup exists;
- bullish and bearish scenarios conflict;
- expected edge is too uncertain;
- cost-adjusted reward/risk is inadequate;
- spread/volatility is abnormal;
- a high-impact event creates a policy restriction;
- account risk or margin limits prohibit entry;
- market data is stale, incomplete or contradictory;
- trigger never occurs before expiry;
- execution is unavailable or rejected.

Record the reason and evidence. Do not synthesize extra NO_TRADE examples simply to balance class counts. Evaluate whether abstention improves calibration, drawdown, net expectancy and operational safety.

## 13. Decision-time explanation

A compact explanation should answer:
- What is observed now?
- What is confirmed versus provisional?
- Which evidence supports and contradicts each scenario?
- What is the selected action and why?
- What exact condition would change the decision?
- What invalidates the scenario?
- What risk/cost constraints apply?
- What information is missing or uncertain?

Explanations must reference evidence IDs and versions. Do not reward verbosity, invented precision or unsupported confidence. Distinguish calibrated probability from subjective confidence.

## 14. Post-trade review without hindsight leakage

Post-trade review may use the full realized path, but it belongs to a separate post-outcome task and must never be fed into the original decision-time input.

Review:
- whether the original decision followed the declared policy;
- whether inputs were correct and available;
- whether the scenario and invalidation were explicit;
- execution quality versus assumptions;
- risk engine and broker reconciliation;
- realized MFE/MAE and costs;
- whether management actions followed policy;
- whether any process failure occurred.

Store outcome-based lessons separately from decision-time labels. A trade that lost under a valid process should not automatically become a negative decision example. A profitable trade caused by a rule violation should not become a positive policy example.

## 15. Evaluation

Evaluate each layer separately.

### Decision policy
- action confusion and class-wise precision/recall;
- NO_TRADE/abstention rate and quality;
- scenario trigger/expiry/invalidation accuracy;
- decision consistency under identical snapshots.

### Risk and management
- risk calculation agreement with deterministic engine;
- constraint violation rate (target zero);
- management action validity under policy;
- stop/target modification correctness;
- residual exposure and risk after partial exits.

### Execution and lifecycle
- simulated-versus-observed fill discrepancy;
- cost/slippage error;
- event ordering and reconciliation correctness;
- duplicate/missing event handling;
- unresolved execution-state rate.

### Strategy outcomes
- net expectancy in R and currency where valid;
- profit factor, drawdown, tail loss and exposure;
- turnover, trade frequency and holding time;
- sensitivity to spread, slippage, latency and gaps;
- confidence intervals and regime-specific stability.

Always compare against simple baselines and the existing deterministic policy where available. Do not infer generalization from a small number of trades. Report uncertainty and effective independent episode counts.

## 16. Leakage and integrity tests

Test:
- future outcome used to choose original action;
- later swing confirmation backdated into entry rationale;
- planned price mistaken for actual fill;
- stop/target hit order inferred from ambiguous OHLC;
- revised account/broker values substituted into an earlier decision;
- post-trade explanation leaking into decision input;
- multiple overlapping windows from one trade crossing splits;
- partial fills or corrections lost during event reconstruction;
- risk rounded volume not revalidated;
- costs omitted from break-even or expectancy;
- rejected order represented as opened position;
- stop modification request represented as confirmed broker state;
- profitable outcome relabeled as correct policy action;
- loss relabeled as bad decision without process analysis.

Any critical leakage, risk-control mismatch or event reconstruction failure blocks admission.

## 17. Promotion gate

Trade intelligence is eligible for later implementation only when:
1. policy actions and objective outcome labels are explicitly separated;
2. scenario, trigger, invalidation and expiry definitions are frozen;
3. deterministic risk and execution authorities are identified and verified;
4. lifecycle event semantics support partial fills and corrections;
5. cost and ambiguous-bar policies are explicit;
6. NO_TRADE and abstention are first-class;
7. post-trade data is isolated from decision-time inputs;
8. chronological evaluation and leakage tests are specified;
9. Stage 5 compatibility and source feasibility are reviewed;
10. the user separately approves the next phase.

## 18. Explicit non-decisions

This document does not define an actual AURORA strategy, risk percentage, leverage, stop/target formula, trailing parameters, event restriction, order type preference, broker behavior, or model action authority. It does not inspect or modify the trading application and does not authorize data processing, labeling, implementation, backtesting, or training.

Those decisions require verified system contracts, source evidence and separate approval.
