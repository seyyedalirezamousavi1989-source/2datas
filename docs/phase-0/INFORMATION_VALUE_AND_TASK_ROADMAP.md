# Information-Value Roadmap and Task Promotion Gates — Phase 0

## 1. Purpose and status

This document defines how the project prioritizes learning capabilities and admits information into a future XAUUSD dataset. It is a design policy only. It does not authorize source inspection, data acquisition, feature computation, labeling, dataset generation, model training, or implementation.

The optimization target is **verified information value per independent decision episode**, not row count, token count, number of indicators, task count, or apparent sophistication.

A candidate is valuable only when it is:
- available at the intended decision time;
- reliably sourced or reproducibly derived;
- defined without hindsight;
- distinct from existing information;
- useful to a named downstream decision or research question;
- measurable against a credible baseline;
- worth its acquisition, storage, annotation, and maintenance cost.

## 2. Capability priority

Priorities below are a research ordering, not a promise that every task will be built. Each tier has a promotion gate.

### Tier A — Minimum viable decision intelligence

| Capability | Required contribution | Why it is foundational | Promotion gate |
|---|---|---|---|
| Market state and structure (T01, selected T07) | Compact, causal description of current price/structure state | Establishes what is observable before forecasting | Operational definitions, point-in-time confirmation, reproducibility |
| Multi-timeframe synthesis (T02) | Alignment, conflict and missing/partial context | Avoids isolated timeframe reasoning | Exact as-of synchronization and evidence that selected TFs add value |
| Outcome forecasting (T03) | Calibrated estimate for a narrowly defined event/horizon | Separates prediction from action | Target feasibility, sufficient effective samples, calibration and chronological baseline comparison |
| Conditional scenario/setup policy (T04) | Conditional paths, triggers, invalidation and NO_TRADE | Converts evidence into disciplined choices | Policy provenance, realistic costs, abstention and decision-coverage evaluation |
| Risk interpretation (T05) | Faithful interpretation of deterministic risk outputs | Connects choices to capital constraints | Verified engine contract; no model-owned authoritative calculations |
| Lifecycle reasoning (T06) | Event-based monitoring and management | Teaches decisions after entry, not just entry selection | Broker-state identifiers, event chronology and reconciliation feasibility |

Tier A is the first coherent capability set to validate. It is not a claim that all six tasks have enough data today.

### Tier B — Add only when evidence supports it

| Capability | Potential value | Main cost/risk | Promotion gate |
|---|---|---|---|
| Execution interpretation (T08) | Realistic spread, slippage, fill and rejection understanding | Broker-specific quote/fill archives and clock/ID quality | Reliable bid/ask and broker event history; measurable gain over simpler cost assumptions |
| Regime/volatility refinement (T09) | Better conditional analysis and robustness | Duplicate state labels and regime instability | Distinct target/consumer and incremental value beyond T01 |
| News context (T10) | Point-in-time macro context | Licensing, historical revisions and publication-time leakage | Licensed point-in-time archive; gain over market-only baseline |
| Visual chart reasoning (T11) | May extract visual patterns or spatial relationships | Expensive images, rendering artifacts, modality leakage | Controlled same-snapshot image-vs-structured ablation shows meaningful stable gain |

### Tier C — Research candidates, not default training scope

- SMC vocabulary and sub-concepts (liquidity sweeps, FVG, order blocks, premium/discount).
- Fine-grained candlestick/pattern taxonomies.
- Broad indicator collections.
- Long-form free-form analysis transcripts.
- Large synthetic scenario corpora.
- Every possible timeframe, horizon, session and broker combination.

Promote a candidate only after its definition is reproducible, annotators/rules are reliable, it adds information beyond simpler features, and it improves a defined downstream task. Familiarity or popularity is not evidence of value.

## 3. Dependency order

The logical dependency graph is:

1. **Canonical source observations and instrument identity** establish what was actually observed.
2. **Point-in-time snapshots and data-quality states** establish what was knowable at a decision time.
3. **Minimal validated features and market-state descriptions** summarize current evidence.
4. **Forecast targets** estimate a precisely defined future event independently of policy.
5. **Scenarios and setup decisions** consume evidence/forecasts but retain separate policy labels.
6. **Deterministic risk calculations** gate whether a plan is feasible.
7. **Broker-confirmed lifecycle/execution events** support management and execution reasoning.
8. **Evaluation and release audits** determine whether any capability earns retention.
9. Optional news and visual modalities enter only through incremental-value tests.

This is a conceptual dependency order. The Stage 5 compatibility audit may change interfaces and sequencing.

## 4. The minimum useful information contract

For each retained field, record:

- **Claim:** what does this field assert?
- **Origin:** source observation, deterministic derivation, model interpretation, policy, or future outcome?
- **Availability:** when did it become available to the system?
- **Definition:** exact calculation or annotation rule and version.
- **Units/semantics:** price basis, timezone, volume meaning, currency, timeframe, and status.
- **Quality:** missingness, freshness, uncertainty, corrections and limitations.
- **Consumer:** which task uses it and for what decision.
- **Evaluation:** how its contribution is measured.
- **Cost:** acquisition, compute, annotation, storage, license and maintenance burden.

If any required element is unknown, the field is provisional or excluded; it must not be silently filled with a guessed value.

## 5. Feature admission scorecard

Do not create a single opaque weighted score that can hide a critical defect. Apply hard gates first, then compare surviving candidates.

### Hard gates (all required)
- Point-in-time availability is provable.
- Definition and units are documented.
- Source/derivation is traceable.
- Missing/ambiguous behavior is explicit.
- No target leakage or retrospective construction.
- No duplicate representation without a separate consumer.
- Legal/license constraints are acceptable.

### Comparative evidence (rank after hard gates)
- Incremental predictive or decision value on chronological validation.
- Stability across periods, sessions, volatility states and sources.
- Robustness to reasonable cost and data-quality perturbations.
- Independent information contribution vs existing features.
- Effective sample coverage and uncertainty of the measured gain.
- Operational cost and fragility.

A feature with a hard-gate failure is rejected regardless of its apparent predictive performance.

## 6. Redundancy and compression rules

Prefer one canonical fact plus references over copied variants.

Examples:
- Keep canonical OHLC/quote observations once; derived returns/ranges reference their definition and source interval.
- Do not store the same trend state as multiple synonymous labels.
- Do not add many moving-average periods unless each has a distinct tested purpose.
- Do not duplicate T03 forecast values into T04 as observed facts; T04 references the forecast.
- Do not duplicate the same explanation in several phrasings and count it as more market evidence.
- Do not treat each adjacent minute in one continuous move as an independent episode.
- Preserve independent provider observations when they support source robustness; do not merge away provenance.

Compression must never erase provenance, timing, source disagreement, uncertainty, or exceptional events.

## 7. Dataset composition principles

A future dataset should preserve natural prevalence for evaluation and represent both ordinary and exceptional conditions.

Include, when reliable:
- routine market conditions as well as high-volatility episodes;
- trend, range, transition and uncertain states;
- valid setups, invalidated setups and no-trade decisions;
- winning and losing outcomes;
- rejected, delayed, partial and failed execution events;
- management decisions that did and did not improve the risk path;
- missing, stale and contradictory evidence cases.

Do not force equal class counts. Use train-only weighting/sampling only if justified, preserve natural-distribution validation/test sets, and report effective independent episode counts.

## 8. Data budget and stopping rule

No fixed row target is specified at this stage. The required sample size depends on target prevalence, horizon overlap, regime coverage, label reliability, and confidence intervals.

For each task, stop expanding the dataset when:
- new records mostly repeat already-covered states/episodes;
- incremental coverage or metric uncertainty no longer improves meaningfully;
- source quality or label agreement degrades;
- additional modality/feature cost exceeds demonstrated gain;
- rare classes cannot be supported with honest effective sample sizes.

If the available evidence cannot support a target, remove or narrow the target rather than fabricate examples or oversample copies and call them new evidence.

## 9. Task promotion checklist

A task moves from candidate to approved design only when:
1. named consumer and decision are explicit;
2. target semantics differ from existing tasks;
3. point-in-time input contract is testable;
4. source and label feasibility are evidenced;
5. ambiguity and abstention are represented;
6. baseline and evaluation metrics are specified;
7. incremental value can be tested;
8. operational and license cost is acceptable;
9. Stage 5 compatibility is reviewed;
10. the user approves the next phase.

## 10. Recommended first research sequence after Phase 0 gates

Subject to Stage 5 acceptance, source feasibility and explicit approval:

1. Verify source/instrument identity and timestamp semantics.
2. Establish a minimal canonical OHLC/quote snapshot with data-quality flags.
3. Validate a small set of causal market-state/structure definitions.
4. Choose one or a small number of primary decision horizons based on intended use and source coverage.
5. Define one forecast target per horizon with unambiguous outcome semantics.
6. Establish NO_TRADE, simple market rules and current approved deterministic logic as baselines.
7. Validate setup and risk interpretation separately.
8. Add lifecycle management only to the extent broker event history is trustworthy.
9. Evaluate optional news, execution detail and images as independent extensions.

This sequence is deliberately narrow. It prioritizes a reliable core before expensive breadth.

## 11. Explicit non-decisions

This document does not decide:
- exact timeframe set or decision cadence;
- numeric sample count or train/validation/test dates;
- broker/provider or licensing choice;
- feature formulas or indicator periods;
- exact model architecture, base model or fine-tuning method;
- whether SMC, news, images or all execution details will be retained;
- any final physical schema or pipeline implementation.

These require evidence from later approved phases, not assumptions in Phase 0.
