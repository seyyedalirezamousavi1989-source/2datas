# A–M Task-to-Schema Mapping — Phase 0

## 1. Purpose

Connect the original A–M capability architecture to the canonical entities defined in `DATA_MODEL_AND_SCHEMA_CONTRACTS.md`. This prevents task-specific schemas from becoming disconnected copies of the same market context.

The A–M scope is preserved. The T01–T11 priority catalog groups capabilities for efficient planning; it does not remove A–M capabilities. Mapping and priority remain provisional until Stage 5 compatibility and source feasibility are reviewed.

## 2. Shared input contract

All tasks consume a reference to a frozen `MarketSnapshot` and its provenance. A task may reference only the observations/features it actually needs.

Common constraints:
- Inputs are selected as-of `decision_timestamp`.
- Each value resolves to a source/feature version and availability time.
- Partial, stale, missing, or conflicting timeframe context is explicit.
- No task input contains its own future target, target confirmation time, realized trade outcome, or retrospective explanation.
- Repeated context is referenced, not copied.

## 3. A–M mapping

| Family | Canonical input references | Primary output entity | Target/evaluation focus | Retention rule |
|---|---|---|---|---|
| A. Market structure | MarketSnapshot, bars, approved structure FeatureValues | StructureAssessment (logical task output) | Reproducible swing/trend/range/break/failure events | Confirmed vs provisional and confirmation time must be explicit |
| B. Liquidity / SMC | MarketSnapshot, bars, validated structure/liquidity FeatureValues | StructureAssessment or Scenario evidence | Operational event detection and reliability | No hidden institutional-flow claims; each concept requires precise definition |
| C. Multi-timeframe | MarketSnapshot timeframe references and availability/completion states | MTFAssessment (logical task output) | Alignment/conflict correctness and as-of integrity | Include only timeframes with distinct decision value |
| D. Regime / volatility | MarketSnapshot and non-redundant volatility/return FeatureValues | RegimeAssessment (logical task output) | State/transition reliability and stability | Merge with A when target semantics do not differ |
| E. Forecasting | MarketSnapshot plus approved causal feature references | Forecast | Event-specific discrimination and calibration | Every forecast names target, event space, horizon and probability semantics |
| F. Setup decision | MarketSnapshot, Forecast references, Scenario references, RiskCalculation result | TradeDecision | Policy compliance, abstention quality, net results after costs | Separate from market outcome labels and order execution |
| G. Risk | Verified account/instrument/quote/exposure references and deterministic engine | RiskCalculation | Exact calculation reproducibility and constraint compliance | Model interprets; deterministic service calculates and enforces |
| H. Active management | Broker-confirmed LifecycleEvent history, current verified position, MarketSnapshot, RiskCalculation | Management recommendation (TradeDecision subtype or versioned policy output) | Event-level action quality and risk-path compliance | No stale position state; action references exact event/snapshot |
| I. Execution | Order/deal/quote LifecycleEvents, instrument specification, cost context | ExecutionAssessment (logical task output) | Fill/cost/rejection/slippage realism | An order request is not a fill; candle-only limits are explicit |
| J. Trade lifecycle | Ordered LifecycleEvents, linked Scenario/TradeDecision/RiskCalculation | LifecycleAssessment (logical task output) | Chronology, reconciliation, policy and process quality | Preserve partial fills, corrections, rejects and exceptional paths |
| K. News / fundamentals | Point-in-time news/event SourceDefinition and timestamped source observations | ContextAssessment (logical task output) | Availability-time correctness, fact/expectation separation | No inclusion without licensed and reliable historical timestamps |
| L. Visual chart intelligence | Chart artifact reference tied to exact MarketSnapshot and rendering spec | VisualAssessment (logical task output) | Incremental value vs same structured inputs | Optional; chart must not reveal future candles or inconsistent data |
| M. Analytical explanation | References to snapshot, features, forecasts, scenarios, decision and risk outputs | Explanation artifact linked to source records | Evidence traceability, contradiction and uncertainty handling | Keep concise; do not create duplicate narrative targets |

The names in the “logical task output” column are conceptual boundaries, not commitments to create standalone storage tables. Related outputs may share one versioned task envelope when semantics and evaluation remain distinct and unambiguous.

## 4. Mapping to prioritized T01–T11

| Priority task | A–M coverage | Canonical entities |
|---|---|---|
| T01 Market-state assessment | A + D | MarketSnapshot, FeatureValue, logical MarketStateAssessment |
| T02 Multi-timeframe synthesis | C + relevant A/D context | MarketSnapshot, logical MTFAssessment |
| T03 Probabilistic outcome forecast | E | Forecast, OutcomeLabel |
| T04 Conditional setup decision | F + scenario evidence from A–E | Scenario, TradeDecision, PolicyLabel |
| T05 Risk-plan interpretation | G | RiskCalculation |
| T06 Trade lifecycle reasoning | H + I + J | LifecycleEvent, RiskCalculation, logical ManagementAssessment |
| T07 Structure-event interpretation | A + selected B concepts | FeatureValue, logical StructureAssessment, OutcomeLabel if objectively defined |
| T08 Execution-cost interpretation | I | LifecycleEvent, InstrumentSpecification, logical ExecutionAssessment |
| T09 Regime/volatility characterization | D | FeatureValue, logical RegimeAssessment |
| T10 News-context interpretation | K | SourceDefinition, timestamped observation, logical ContextAssessment |
| T11 Visual chart reasoning | L | MarketSnapshot, chart artifact reference, logical VisualAssessment |

M is a cross-cutting explanation layer, not an additional duplicated task for every row. It should be attached only where explanation adds a separately testable capability.

## 5. Output layering

Each task output must separate:
1. **Evidence references** — what source records/features were used.
2. **Observed facts** — values directly present in the source.
3. **Derived measurements** — outputs from versioned deterministic transformations.
4. **Interpretation** — the task's assessment.
5. **Forecast** — future event estimate, if applicable.
6. **Policy/action** — recommendation, if applicable.
7. **Uncertainty/status** — missing, stale, ambiguous, unresolved or calibrated uncertainty.
8. **Next condition** — what event/observation would update or invalidate the output.

Not every task needs all eight sections. Omit inapplicable fields rather than emitting empty filler.

## 6. Cross-task dependency rules

- A–D can supply evidence to E and F, but must not import future target values.
- E produces forecasts; F may consume them as versioned estimates but cannot relabel them as observed facts.
- F produces a policy decision; G independently calculates risk feasibility.
- A plausible scenario cannot bypass G hard constraints.
- H recommendations require current broker-confirmed position/order state and fresh market context.
- I and J preserve actual execution events; they do not infer fills from model recommendations.
- K and L are optional evidence sources and must pass point-in-time and incremental-value tests.
- M explains referenced outputs; it cannot invent unsupported evidence or overwrite upstream records.

## 7. Preventing duplicate training targets

Before creating separate task datasets, ask:
- Is the target mathematically or semantically distinct?
- Does it require a different input contract?
- Does it have an independent evaluation metric?
- Is there a downstream consumer?
- Does it add information beyond an existing task?

If not, merge it into the existing task or represent it as a field/reference. In particular:
- Do not create separate copies of trend and regime labels unless definitions differ meaningfully.
- Do not treat SMC terms as additional labels until operational reliability is established.
- Do not duplicate the same forecast as a scenario probability and a trade-decision confidence.
- Do not make M narrative paraphrases into independent examples.
- Do not turn realized trade results into policy labels.

## 8. Open decisions

1. Which decision cadence and forecast horizons will be primary?
2. Which minimum timeframe set supports those horizons?
3. Which A/B structure events have reliable, reproducible definitions?
4. Which D regime targets are distinct enough to retain separately from A?
5. Which F policy labels can be sourced from a defensible point-in-time policy rather than hindsight?
6. Which H/I/J event data can actually be obtained with trustworthy broker identifiers and timestamps?
7. Whether K and L pass source feasibility and incremental-value tests.

These questions must be resolved before final machine schemas are frozen.
