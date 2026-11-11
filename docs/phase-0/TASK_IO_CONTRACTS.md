# Task Input/Output Contracts — Phase 0

## 1. Status and design intent

This document defines the intended behavioral contract for each prioritized learning task. It is implementation-neutral: field types, serialization, exact enums, prompt templates, and final JSON Schemas remain provisional until the Stage 5 compatibility audit and source-feasibility gate.

The original A–M capability architecture remains authoritative for scope. T01–T11 are task groupings for planning and evaluation, not a replacement taxonomy.

## 2. Universal task envelope

Every future task example must resolve to:
- task_id and task_definition_version;
- snapshot_id and decision_timestamp;
- required input references and their versions;
- explicit input availability and quality status;
- target definition/version, stored outside the model-input payload;
- provenance and split membership in the release manifest;
- optional policy/model/annotation version where relevant.

The materialized model input contains only information available at decision time. The target is stored separately and joined only in controlled training/evaluation materialization.

## 3. T01 — Market-state assessment (A + selected D)

**Question:** What is the current observable market state, without claiming what happens next?

**Inputs:** Canonical MarketSnapshot; completed and partial timeframe states with availability timestamps; approved structure, return, volatility and trend features; data-quality and freshness flags.

**Output:** Current state under a versioned taxonomy; structural observations with evidence references; trend/range/transition/uncertain assessment where defined; confirmed vs provisional events; conflicting evidence; validity/expiry or next observation condition.

**Prohibitions:** No future outcomes; no treating unconfirmed swings/breaks as confirmed; no confusing description with forecast or trade advice.

**Evaluation:** Per-class metrics, event timing tolerance, annotator agreement where applicable, and stability by period/regime.

## 4. T02 — Multi-timeframe synthesis (C)

**Question:** How do available timeframes agree or conflict at this exact decision time?

**Inputs:** Snapshot references to chosen timeframe bars/features; completion/partial status and available_at; declared timeframe hierarchy.

**Output:** Per-timeframe summary; alignment/conflict; context vs trigger roles if specified; missing/partial/stale disclosure; observation that could change assessment.

**Prohibitions:** No higher-timeframe candle before availability; no partial candle treated as completed; no forced agreement.

**Evaluation:** As-of correctness, partial-bar handling, rule consistency, and value vs single-timeframe baselines.

## 5. T03 — Probabilistic outcome forecast (E)

**Question:** What is the probability of a precisely defined future event over a fixed horizon?

**Inputs:** Point-in-time snapshot and approved features; one target definition/version and horizon; cost/price convention for cost-aware targets.

**Output:** Target/event ID and horizon; probabilities for named outcomes only when valid; explicit probability type (directional return, barrier touch, regime transition, or net trade outcome); uncertainty; model/calibration version.

**Prohibitions:** No mixing probability types in one vector; no presenting confidence as calibrated probability without evidence; no future path or target confirmation in inputs.

**Evaluation:** Brier score, log loss, reliability/calibration, discrimination, sample counts and chronological stability per target/horizon.

## 6. T04 — Conditional scenario and setup decision (B + F)

**Question:** Given current evidence, what conditional paths are plausible and is an action justified now?

**Inputs:** Snapshot; relevant T01/T02 outputs; optional T03 forecast references; current cost/execution context; deterministic risk feasibility result for actionable plans.

**Output:** Small set of materially distinct scenarios or unresolved state; supporting/conflicting evidence; activation, invalidation and expiry; decision class LONG/SHORT/NO_TRADE/WATCH/WAIT_FOR_CONFIRMATION; trigger and risk references for actionable decisions; abstention/rejection reasons.

**Prohibitions:** No forced trade; no confusing scenario probability with probability of profit; no executable order or bypass of risk gates; no labeling a decision correct solely from eventual P&L.

**Evaluation:** Policy compliance, abstention quality, coverage, net outcomes after realistic costs, and comparison with NO_TRADE and deterministic baselines.

## 7. T05 — Risk-plan interpretation (G)

**Question:** What does the authoritative risk engine permit, and why?

**Inputs:** Immutable RiskCalculation request/result; account, instrument, quote, costs, exposure and constraint references; engine/version.

**Output:** Faithful explanation of permitted/rejected status; explanation of risk, volume, margin and constraint values by reference; missing/stale warnings and fail-closed reasons; request for recalculation if proposing lower risk.

**Prohibitions:** No guessing volume, tick value, margin, balance or contract size as authoritative; no overriding hard limits; no describing stop-loss estimate as guaranteed maximum loss under gaps/slippage.

**Evaluation:** Exact agreement with engine outputs, zero critical fabricated values, explanation accuracy, safe abstention.

## 8. T06 — Trade lifecycle and management reasoning (H + J; consumes verified I events as context)

**Question:** Given verified broker state and chronological events, what management action, if any, is justified now?

**Inputs:** Ordered broker-confirmed LifecycleEvents; current verified position/order state and reconciliation status; fresh snapshot; latest deterministic risk result and hard constraints.

**Output:** Current lifecycle state and evidence references; action such as HOLD, REDUCE_POSITION, MOVE_STOP, TRAIL_STOP, PARTIAL_TAKE_PROFIT, CLOSE_POSITION, REQUEST_RECALCULATION or ABSTAIN; preconditions, rationale, expiry/invalidation; required recalculation/approval boundary; state uncertainty.

**Prohibitions:** No inferring fills from requests; no stale/unreconciled state; no rewriting past decisions after outcome; no arbitrary stop movement presented as universally optimal.

**Evaluation:** Event chronology, broker-state consistency, policy compliance, risk path, action timing, cost-aware results; process quality separate from P&L.

## 9. T07 — Structure-event interpretation (A + selected B)

**Question:** Did a precisely defined structure/liquidity event occur, and when did it become knowable?

**Inputs:** Canonical bars/quotes; exact event-definition version; relevant feature values; confirmation/availability rules.

**Output:** Event type and operational definition; interval and confirmation/availability time; confirmed/provisional/ambiguous/invalid status; evidence and correction history.

**Prohibitions:** No claims of hidden institutional order access; no backdating swing confirmation using future bars; no treating subjective SMC vocabulary as ground truth without reliability evidence.

**Evaluation:** Reproducibility, event precision/recall, timing tolerance, annotation agreement and incremental downstream value.

## 10. T08 — Execution-cost interpretation (I)

**Question:** What execution conditions and costs are evidenced, and what remains unknown?

**Inputs:** Bid/ask/quote and broker events; instrument specification; order type, fill policy and cost records; timestamp/latency metadata.

**Output:** Observed spread, slippage, commission, swap and fill status where available; rejection/requote/partial-fill explanation; coverage and uncertainty; observed costs separated from modeled assumptions.

**Prohibitions:** No inferring actual fills from OHLC alone; no generic broker assumptions substituted for missing historical specs; no simulated fill represented as actual execution.

**Evaluation:** Cost estimation error, fill-state classification, exception handling and sensitivity to incomplete data.

## 11. T09 — Regime and volatility characterization (D)

**Question:** Which versioned market regime/volatility state is supported by currently available data?

**Inputs:** Snapshot; approved non-redundant return/volatility features; frozen taxonomy and transition rules.

**Output:** Current regime and volatility state; evidence and transition status; uncertainty/confirmation delay; current state distinguished from future transition forecast.

**Prohibitions:** No duplicate T01 labels without distinct definition/consumer; no future-window volatility; no forced confident class.

**Evaluation:** Temporal stability, transition timing, calibration where probabilistic, and incremental value beyond T01.

## 12. T10 — News and fundamental context (K)

**Question:** What relevant information was publicly available by decision time, and what is fact vs expectation vs interpretation?

**Inputs:** Licensed source records with publication/update/availability times; event metadata and source reliability; market snapshot.

**Output:** Source and timestamps; fact, scheduled event, consensus/expectation and interpretation separated; relevance stated as hypothesis; conflicting reports/revisions/unknowns disclosed.

**Prohibitions:** No revised data presented as initially known; no invented headlines/outcomes; no unsupported attribution of price moves to news.

**Evaluation:** Point-in-time correctness, traceability, fact/interpretation separation and incremental value vs market-only baseline.

## 13. T11 — Visual chart reasoning (L)

**Question:** Does the image add useful visual information beyond synchronized structured context?

**Inputs:** Chart artifact tied to exact snapshot and renderer version; symbol, timeframe, price basis, visible interval and annotation registry; matching structured input.

**Output:** Visual observations with time/region references where feasible; evidence vs interpretation; unreadable/ambiguous disclosure; conflict report against canonical data.

**Prohibitions:** No candles beyond snapshot cutoff; no future-revealing viewport/annotation; pixels are not authoritative for exact prices.

**Evaluation:** Structured-only vs structured-plus-image ablation, visual event accuracy, rendering robustness and leakage audit.

## 14. Cross-cutting explanation layer (M)

M is not a duplicate target for every task. Attach explanation only where it adds measurable value.

Explanations should cite exact evidence references; separate observation, derivation, interpretation, forecast and policy; state conflicts, uncertainty, missing data and expiry; explain abstention; avoid repeating the full input or inventing detail.

Evaluate factual traceability and contradiction handling. Fluency and length alone are not quality metrics.

## 15. Output validation and abstention

Every task contract must define allowed outputs, required evidence references, target/horizon semantics, missing-value handling, expiry/freshness, abstention conditions, hard safety invariants, objective metrics and baselines.

Invalid, unsupported, stale or contradictory inputs must lead to typed unresolved/abstain outcomes where appropriate, not forced confidence.

## 16. Freeze criteria

A task is not ready for implementation until its downstream consumer, input cutoff, distinct operational target, source/annotation feasibility, leakage and ambiguity rules, metrics/baselines, overlap review and Stage 5 compatibility are documented—and the user approves the next phase.
