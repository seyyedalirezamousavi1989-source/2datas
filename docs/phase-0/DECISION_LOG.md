# Decision Log

This log records decisions, not assumptions. New decisions must include rationale, evidence, impact, and date. Superseded decisions remain visible.

## D-001 — Design-only authorization

- Status: Accepted
- Date: 2026-11-12
- Decision: Current work is limited to technical design and documentation.
- Consequence: No archive inspection, data download/processing, dataset generation, pipeline implementation, model training, or expensive benchmarks.
- Revisit condition: Separate explicit user approval.

## D-002 — Independent repository

- Status: Accepted
- Date: 2026-11-12
- Decision: This project is maintained in `seyyedalirezamousavi1989-source/2datas` and remains separate from AURORA QUANT implementation and the other Stage 5 dataset project.
- Consequence: No changes to those external projects under this authorization.

## D-003 — Preserve uploaded archive

- Status: Accepted
- Date: 2026-11-12
- Decision: Existing `XAUUSD.zip` is an uninspected source artifact and must remain unchanged.
- Consequence: No claims are made about its contents, source, completeness, quality, or suitability.

## D-004 — Optimize information value, not dataset size

- Status: Accepted
- Date: 2026-11-12
- Decision: Include only fields and examples with explicit purpose, point-in-time validity, reliable definitions, non-duplicative information, and testable value.
- Consequence: No paraphrase-based sample inflation or indiscriminate indicator collection.

## D-005 — Separate outcomes from decisions

- Status: Accepted
- Date: 2026-11-12
- Decision: Objective future market outcomes and policy/action labels are separate target families.
- Consequence: A profitable hindsight trade is not automatically a correct decision label.

## D-006 — Deterministic risk/execution authority

- Status: Accepted
- Date: 2026-11-12
- Decision: Financial calculations and execution safeguards remain deterministic and authoritative; the model interprets verified outputs.
- Consequence: No model-generated replacement for broker/account facts or authoritative risk calculations.

## D-007 — Compact task catalog and feature admission

- Status: Accepted as a design rule; empirical admission remains pending
- Date: 2026-11-12
- Decision: Learning objectives are prioritized and merged when they do not have distinct targets/evaluation. Features require defined purpose, causal availability, reliability, and evidence of incremental value.
- Consequence: Task families and candidate feature categories are not blanket approval to generate labels or calculate every candidate.

## D-008 — Outcome and policy labels remain disjoint

- Status: Accepted
- Date: 2026-11-12
- Decision: Market outcome labels and policy/action labels have separate semantics and provenance.
- Consequence: Future profitability cannot be used as a shortcut to infer the correctness of a historical decision.


## D-009 — Canonical shared data model

- Status: Accepted as a logical design contract; physical schemas remain pending
- Date: 2026-11-12
- Decision: Use canonical source observations and point-in-time snapshots referenced by task-specific Forecast, Scenario, TradeDecision, RiskCalculation, and LifecycleEvent records.
- Consequence: Do not duplicate the same market context across task datasets. Final JSON Schema, physical layout, and Stage 5 compatibility mapping remain deferred.

## D-010 — Typed status semantics

- Status: Accepted
- Date: 2026-11-12
- Decision: Distinguish observed, derived, estimated, unknown, unavailable, not_applicable, not_yet_observable, stale, ambiguous, invalid, and censored states.
- Consequence: Do not overload null or force unresolved evidence into a confident class.

## D-011 — Information-density composition policy

- Status: Accepted as a design rule; empirical sampling remains pending
- Date: 2026-11-12
- Decision: Select by distinct information contribution, preserve independent source corroboration, and account for overlapping windows/episodes.
- Consequence: Do not count paraphrases, adjacent highly overlapping windows, or oversampled copies as independent market evidence. Keep natural-distribution evaluation data.


## D-012 — Preserve A–M through canonical task mapping

- Status: Accepted as a logical mapping; individual task schemas remain provisional
- Date: 2026-11-12
- Decision: Preserve the initial A–M capability architecture and map it to canonical shared entities. T01–T11 are prioritization/grouping, not a replacement architecture.
- Consequence: Do not drop a capability merely because the compact task catalog groups it with another. Split or merge only when target semantics, inputs, consumers, and evaluation justify it.

## Open questions — do not silently resolve

1. **Stage 5 compatibility:** What exact deliverables and schemas will exist after independent acceptance? Audit only after user confirms that milestone.
2. **Source feasibility:** Which providers offer licensed, point-in-time XAUUSD quotes/ticks/bars, broker specification history, and execution records with adequate coverage?
3. **Instrument identity:** Which broker/server symbol definitions and contract-specification changes are relevant to the intended deployment?
4. **Primary decision horizons:** Which trading horizons and decision cadence are genuinely required? Avoid supporting every timeframe merely for completeness.
5. **Target priority:** Which outcome targets demonstrate value for the intended decisions, and which can be removed?
6. **News archive:** Is reliable historical publication-time data available under an acceptable license?
7. **Visual modality:** Do synchronized charts add measurable value over structured data after controlled comparison?
8. **Annotation reliability:** Which discretionary concepts can be defined consistently enough to label?
9. **Evaluation protocol:** What date ranges, regimes, purging/embargo rules, and minimum effective sample sizes are justified by source coverage and target horizons?
10. **Model selection:** Which locally available model and training method fit the final task mix, after representative low-cost feasibility tests?

## Next authorized work

Continue Phase 0 design review only. Resolve definitions and dependencies, remove unnecessary overlap, and prepare a concise specification for user approval. Do not advance to source inspection or implementation automatically.
