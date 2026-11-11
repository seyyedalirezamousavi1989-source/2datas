# Annotation and Label Reliability Protocol — Phase 0

## 1. Purpose and status

Define how future human- or rule-assigned labels must be created, reviewed and versioned. No annotation work is authorized or performed by this document.

A label is not ground truth merely because an annotator or indicator produced it. Every label needs a defined claim, evidence, time semantics and reliability assessment.

## 2. Label family separation

Maintain separate namespaces for:

1. **Observable event labels** — objectively testable events under a frozen operational definition.
2. **Market outcome labels** — future returns, barrier events, MFE/MAE, regime transitions or other defined outcomes.
3. **Interpretive labels** — market structure/SMC or visual assessments that may contain legitimate ambiguity.
4. **Policy labels** — actions prescribed by a specific versioned policy using decision-time evidence.
5. **Process-quality labels** — whether a decision followed its stated policy and constraints, independent of eventual P&L.

Never merge these into one generic correct/incorrect trade target.

## 3. Annotation unit and point-in-time boundary

Every annotation must reference:
- immutable snapshot/decision ID;
- exact task and label definition version;
- evidence references available at the relevant time;
- annotation timestamp and annotator/tool identity;
- status and ambiguity reason;
- review/adjudication state;
- provenance and any superseded annotation.

For decision-time interpretation, annotators must not see future candles, realized outcomes, post-decision news revisions or later management events. For outcome labeling, future data may be used only in the isolated target-generation process and must never be exposed as decision-time evidence.

Where blinding cannot be enforced, record the limitation and do not claim unbiased annotation.

## 4. Operational definitions before annotation

Before annotating a concept, freeze:
- exact positive and negative criteria;
- event start/end and confirmation time;
- timeframe and price basis;
- treatment of partial bars, gaps, equal highs/lows, spread and intrabar ambiguity;
- tolerance bands and invalidation rules;
- unknown/ambiguous/not-applicable cases;
- borderline examples;
- definition version and change rationale.

BOS, CHoCH, liquidity sweep, order block, FVG, mitigation, support/resistance and strong trend are not self-defining. Each requires an operational definition and reliability pilot before large-scale use.

## 5. Independent annotation and adjudication

For subjective or interpretive labels:
1. Prepare a written guide and edge-case examples.
2. Have at least two annotators label a representative pilot independently where feasible.
3. Keep annotators blind to each other's labels and future outcomes.
4. Measure agreement using a metric appropriate to label type and prevalence; report raw agreement and class prevalence too.
5. Review disagreement categories and identify unclear definitions.
6. Adjudicate only under a documented rule; preserve original annotations and adjudication history.
7. Revise the definition and repeat the pilot if reliability is inadequate.

A single adjudicated label must not erase genuine ambiguity. Some examples should remain unresolved.

For objective rule-derived labels, test independent reimplementation or deterministic reproducibility instead of treating multiple annotators as proof of correctness.

## 6. Reliability metrics and limitations

Choose metrics appropriate to nominal, ordinal, event-time or continuous labels. Depending on task, report raw agreement; Cohen's kappa or suitable multi-rater statistic; class-wise disagreement; event timing difference/tolerance; intraclass correlation or absolute error for continuous annotations; prevalence and confidence intervals.

Kappa-like metrics can be distorted by prevalence imbalance. Never report one coefficient without disagreement profile and sample context.

## 7. Ambiguity and abstention policy

Allowed statuses include resolved_positive, resolved_negative, ambiguous, unknown, not_applicable, insufficient_evidence, censored and invalidated_by_source_correction.

Do not force ambiguous cases into positive/negative merely to simplify training. Report ambiguity rate by task, period, regime, source and annotator.

If a label definition repeatedly produces disagreement, simplify or remove the target rather than increasing annotation volume.

## 8. Policy-label provenance

A policy label must identify:
- policy version and effective interval;
- decision-time input snapshot;
- constraints and deterministic risk result;
- allowed action set;
- policy reason code;
- whether action was proposed, approved, rejected or executed.

Do not infer the correct policy action from whether a trade later won or lost. Outcome and policy labels remain separate.

## 9. Label revision and versioning

If source corrections, definition changes or adjudication alter a label:
- create a new label revision;
- preserve the prior record;
- identify superseded version and reason;
- rebuild affected manifests only under a separately approved release process;
- rerun split/leakage and evaluation checks.

Never silently rewrite a historical label while retaining the same version identifier.

## 10. Label release gate

A label family is not ready for production generation until the target has an operational definition; decision and confirmation timestamps are valid; ambiguity/censoring are represented; pilot reliability is acceptable; source coverage is adequate; generation rules are reproducible; no future-derived field leaks into inputs; downstream evaluation/baselines are defined; and the user approves the next phase.
