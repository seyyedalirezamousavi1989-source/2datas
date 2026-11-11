# Deterministic Risk Calculation and Policy-Constraint Handoff — Phase 0

## 1. Status and authority

**Provisional logical contract v0.1; not frozen or implemented.**

This document defines the handoff among model proposals, deterministic risk calculation, policy constraints and broker execution. It does not implement formulas, select risk percentages, assume a broker, define XAUUSD contract specifications, inspect AURORA QUANT, or authorize data processing/trading.

Semantic ownership:
- RISK_AND_TRADE_MANAGEMENT_SPECIFICATION.md owns risk input/calculation principles and deterministic authority.
- SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md owns risk_calculation_status and constraint_outcome domains.
- DATA_MODEL_AND_SCHEMA_CONTRACTS.md owns RiskCalculation entity relationships.
- CANONICAL_FIELD_REGISTRY_AND_SEMANTIC_RECONCILIATION.md owns shared field semantics.
- FIELD_STATUS_BINDING_AND_NULLABILITY_MATRIX.md owns provisional value/status/null bindings.
- TASK_IO_CONTRACTS.md owns T04/T05/T06 consumption boundaries.

This contract clarifies interfaces; it does not duplicate the calculator's mathematical implementation.

## 2. Non-negotiable authority chain

The system must preserve this distinct sequence:

1. **Proposal:** user/model/policy proposes a trade intent and assumptions.
2. **Risk request:** a typed immutable request captures all inputs and exact versions.
3. **Deterministic calculation:** the approved calculator validates inputs and computes risk/volume/margin/exposure outputs.
4. **Policy constraint evaluation:** policy evaluates the calculation result against current hard limits and returns a separate permission outcome.
5. **Decision:** entry policy may select LONG/SHORT only if the required current result is valid and permitted.
6. **Order intent/submission:** an independently authorized order request is created.
7. **Broker evidence:** acknowledgement, rejection, fill, partial fill and position events are recorded.
8. **Reconciliation:** local and broker state are compared; only verified state can support subsequent management.

No stage implies the next stage occurred. In particular:
- A model proposal is not a risk calculation.
- A calculated result is not permission to trade.
- PERMITTED is not authorization to place an order.
- An order request is not broker acknowledgement.
- Acknowledgement is not fill.
- A fill is not proof that local position state is reconciled.

## 3. Immutable request contract

Each request has a unique risk_request_id and immutable request version. It must reference, not silently copy or infer, the relevant source entities.

### 3.1 Required identity and policy context

- request_id and request_version;
- request_created_at and decision_timestamp;
- requester/producer identity and role (user, policy engine or model proposal);
- instrument_id and effective specification_id/version;
- account reference and account currency;
- strategy/risk policy ID and version;
- entry side, order intent/type and intended execution conditions;
- expiry/valid-until rule.

Credentials, secrets and account login material are never dataset fields.

### 3.2 Account and portfolio inputs

Where required by the selected risk calculation:
- timestamped balance, equity, free/used margin and margin level;
- account currency and conversion references;
- open positions, pending orders and relevant aggregate/correlated exposure;
- daily loss, drawdown, consecutive-loss, trade-count and other configured limits;
- account mode and broker netting/hedging semantics.

Every account value must identify source, event/availability time, currency and freshness. A stale or unreconciled account snapshot cannot be treated as current.

### 3.3 Instrument and market inputs

Where relevant:
- exact broker/server symbol and instrument specification version;
- contract size, tick size/value, digits, profit calculation mode and volume min/max/step;
- applicable margin, stop/freeze and trading-session restrictions;
- quote/market snapshot reference and timestamp;
- explicit price side/basis for entry, stop, target and exit assumptions;
- currency conversion source, side/method and timestamp;
- spread, commission, swap/financing and slippage assumptions, with observed-versus-modeled origin.

No generic XAUUSD contract/tick value or universal pip convention is permitted. The effective broker specification is authoritative.

### 3.4 Proposal inputs vs authoritative facts

Keep the following separate:
- proposed entry/stop/target assumptions;
- observed quote and account facts;
- broker specification facts;
- modeled cost/stress assumptions;
- hard policy limits.

The model may propose a lower risk budget or alternate stop/entry assumptions. It may not edit broker/account facts or present a proposed value as authoritative.

## 4. Deterministic calculation contract

The risk engine must be a separately versioned, deterministic, tested component. For the same immutable request, specification, engine version and reference data, it must reproduce the same semantic result.

The engine contract must cover, as applicable:
- side-aware stop-loss exposure under the actual instrument calculation mode;
- conversion into account currency using timestamped conversion references;
- commission, spread, swap and declared execution-cost assumptions;
- requested risk amount/fraction and policy caps;
- preliminary volume and broker-step rounding;
- minimum/maximum volume constraints;
- mandatory post-rounding recalculation of risk and loss;
- margin/free-margin feasibility;
- current and pending-order aggregate exposure;
- daily loss, drawdown and other configured account-level constraints;
- gaps/slippage/stress assumptions and limitations.

A generic stop-distance × generic pip-value formula is not an acceptable universal implementation. The actual mathematical formulas, precision and broker-specific calculations remain owned by the verified deterministic engine and instrument specification.

## 5. Calculation result contract

Each result has a unique risk_result_id, references exactly one request/version, and records:
- risk_request_id/version;
- calculator name, engine_version and calculation timestamp;
- exact account, instrument specification, quote, conversion, cost, exposure and policy references used;
- risk_calculation_status;
- requested risk budget and limits;
- preliminary and permitted volume, including rounding/step information;
- post-rounding estimated loss/risk;
- margin and aggregate exposure result;
- warnings, missing/stale/invalid inputs and typed reason codes;
- valid_until/expiry and the rule used to determine freshness.

A calculated result must distinguish observed values from modeled assumptions. A stop-loss estimate is not a guaranteed maximum loss under gaps, slippage, spread expansion or execution failure.

### 5.1 Status and result invariants

- CALCULATED requires all mandatory inputs to pass validation and all applicable calculations to complete.
- REJECTED_INPUT means one or more mandatory inputs violate the request contract.
- STALE_INPUT means a mandatory input is outside its freshness rule.
- FAILED means the calculation could not complete reliably.
- EXPIRED means the result is no longer valid for a new decision.
- SUPERSEDED means a newer immutable result replaces it for subsequent decisions.

A failed/stale/rejected request must not expose fabricated numeric outputs. Preserve partial diagnostic outputs only if explicitly typed as non-authoritative and unusable for permission.

## 6. Separate policy-constraint evaluation

The deterministic calculation and policy permission are separate objects.

A ConstraintEvaluation references:
- constraint_evaluation_id/version;
- risk_result_id;
- account/portfolio snapshot and decision timestamp;
- policy_id/version;
- all relevant hard-limit and exposure references;
- constraint_outcome;
- typed reason codes and evaluated_at;
- validity/expiry.

Allowed outcomes:
- PERMITTED: all applicable constraints pass for this exact request/result and context.
- PROHIBITED: one or more known hard constraints fail.
- RECALCULATION_REQUIRED: relevant inputs changed, became stale or the proposal changed.
- PENDING_AUTHORIZATION: calculation/constraints pass but an independent authorization step remains.

A PERMITTED result is scoped to its exact request, account/instrument state, policy version and validity window. It is not a standing permission for a different entry, changed stop, changed volume or later account state.

## 7. Mandatory recalculation triggers

A new immutable request and result are required when any material assumption changes, including:
- entry, stop, target, side or order type;
- requested risk amount/fraction or policy version;
- account balance/equity/free margin or account mode;
- instrument specification, contract/tick/volume rules;
- quote side, price, conversion rate or freshness;
- spread, commission, swap, slippage or stress assumptions;
- open positions, pending orders or aggregate exposure;
- daily loss/drawdown or any configured hard limit;
- partial fill, position reduction, stop modification or broker correction.

Never patch a prior result in place. Link new request/result to the superseded request/result and record the reason.

## 8. Model and task handoff

### T04 — Scenario and entry decision

- May reference the current risk result and constraint evaluation.
- LONG/SHORT is eligible only when the applicable result is current, CALCULATED and constraint_outcome=PERMITTED, and all other policy gates pass.
- If outcome is PROHIBITED, policy must not choose LONG/SHORT under that request.
- If outcome is RECALCULATION_REQUIRED or PENDING_AUTHORIZATION, the model must not describe the trade as executable.
- NO_TRADE and ABSTAIN remain valid outcomes for different reasons.

### T05 — Risk-plan interpretation

- Explains the exact deterministic output by reference.
- May identify contradictions or missing assumptions and request a new calculation.
- Must not calculate or alter authoritative volume, tick value, margin, currency conversion or permission.
- Must disclose modeled assumptions and limitations.

### T06 — Existing-position management

- Consumes the latest reconciled broker position/order state and a fresh risk result when an action changes exposure or protection.
- Any proposed reduction, stop/target change or exit-related adjustment that affects risk must trigger the required deterministic recalculation.
- No action may rely on stale/unresolved position state or a superseded/expired result.

## 9. Fail-closed conditions

Do not produce an actionable risk result or permit entry when:
- account or instrument identity/specification is missing, invalid or stale;
- required price basis/quote side is unknown;
- currency conversion or cost assumptions required by the calculation are unavailable;
- account/portfolio state is unreconciled;
- volume rounding cannot satisfy broker constraints;
- post-rounding risk is not recalculated;
- margin or aggregate exposure cannot be evaluated;
- hard limits are breached;
- result expiry has passed;
- request and result versions do not match.

The correct response is a typed rejection, stale/recalculation outcome, prohibition or abstention—not a guessed number.

## 10. Evaluation and audit requirements

Before any future implementation/release, test:
- deterministic reproducibility for identical versioned inputs;
- independent reference calculations and broker/platform agreement;
- exact request/result/policy lineage;
- stale-input rejection and expiry behavior;
- currency conversion and quote-side correctness;
- volume-step/min/max handling and post-rounding recalculation;
- margin and aggregate exposure constraints;
- partial-fill and position-change recalculation;
- no model-authored authoritative numeric values;
- no transition from proposal to order without separate authorization;
- no order/fill/position facts inferred from model text.

Track numeric error against an independently verified engine, constraint violation rate (critical target zero), stale-result misuse, invalid handoff rate, and full audit traceability. Do not claim correctness until actual engine and broker semantics are independently verified.

## 11. Explicit non-decisions and gates

This contract does not choose a risk percentage, leverage, strategy, stop/target formula, broker, contract size, margin formula, stress multiplier, or authorization policy. It does not assume AURORA QUANT currently implements these interfaces.

Before freezing:
1. Independently accept and audit the separate Stage 5 deliverables.
2. Verify the actual AURORA/deterministic engine interface only after separate authorization.
3. Establish source feasibility and broker/instrument specification provenance.
4. Freeze exact request/result field types, precision, freshness and conversion semantics.
5. Obtain explicit user approval.

No market data/archive inspection, risk calculation implementation, dataset/label generation, backtesting, benchmark execution, model training, AURORA QUANT modification or Stage 5 modification is authorized.
