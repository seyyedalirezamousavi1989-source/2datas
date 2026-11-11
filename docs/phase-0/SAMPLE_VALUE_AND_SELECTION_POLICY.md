# Sample Value, Selection and Dataset Efficiency — Phase 0

## 1. Purpose and boundary

Define a defensible method for deciding which candidate decision-time examples deserve inclusion in a future XAUUSD dataset.

**Design only.** This specification does not inspect, select, label, process, or generate market examples. It does not authorize source acquisition or pipeline implementation.

The objective is not to maximize dataset size or produce a single opaque quality score. It is to retain examples that are valid, distinct, useful for a named task, and representative of the intended deployment domain.

## 2. Candidate record and evidence bundle

A candidate example is evaluated as a bundle containing:
- canonical decision/snapshot ID;
- instrument and provider symbol;
- decision timestamp and information cutoff;
- source record references and revision IDs;
- input window boundaries and timeframe set;
- target/label family, definition version and horizon;
- target confirmation/censoring status;
- overlap/episode cluster IDs;
- task intended to consume the example;
- quality findings and provenance;
- split eligibility and restrictions.

A candidate without enough metadata to establish its information set cannot pass admission.

## 3. Hard gates before value assessment

Apply hard validity gates first. No high information score can compensate for a critical validity failure.

Reject or quarantine candidates with:
- unknown or impermissible source rights;
- unverifiable decision-time availability;
- invalid instrument mapping or price basis;
- unresolved corruption or impossible market values;
- target definition not frozen or target not reproducible;
- future information in the input or annotation;
- split contamination that cannot be resolved;
- fabricated, silently imputed or unsupported fields;
- an unresolved critical execution/risk semantic where the task depends on it.

Use typed outcomes: ACCEPT_CANDIDATE, QUARANTINE, REJECT, NOT_APPLICABLE. Preserve reason codes and evidence; do not silently discard failures.

## 4. Multi-dimensional value profile

After hard gates, assess each candidate across separate dimensions. Do not collapse them prematurely into one weighted score.

### A. Task relevance
Does the example teach or test a named capability? Is the target distinct from other tasks? Is the capability required for intended use?

### B. Information novelty
Does it contain a new market episode, transition, structure, event, source corroboration, uncertainty pattern, or management state? Is it merely another overlapping snapshot of the same move?

### C. Evidence quality
Are inputs and targets sourced, causal, reproducible and sufficiently precise? Are material assumptions explicit?

### D. Domain coverage
Does it add coverage of a relevant period, volatility state, session, regime, event family, or execution condition that is currently underrepresented?

### E. Learning difficulty
Does it represent a meaningful boundary case, conflicting evidence, failed setup, ambiguity, or rare but operationally important condition? Difficulty alone is not value if the label is unreliable.

### F. Evaluation usefulness
Can it contribute to a valid held-out test, stress case, calibration segment, or baseline comparison without leakage?

### G. Maintenance and cost
What are the storage, annotation, compute, licensing, and future refresh costs? Does its expected contribution justify them?

Each dimension should have a documented categorical assessment and short evidence-based rationale. If numeric ratings are introduced later, their definitions and inter-reviewer reliability must be validated first.

## 5. Why a single quality score is unsafe

A weighted sum can hide fatal weaknesses: high novelty must not compensate for look-ahead leakage; rarity must not compensate for unreliable labels; visual complexity must not compensate for no incremental value.

Use a gated, multi-criteria decision:
1. validity gates;
2. task relevance;
3. distinctness/novelty;
4. evidence reliability;
5. coverage contribution;
6. cost and evaluation suitability.

Candidates that are incomparable across dimensions should remain in a review queue rather than being force-ranked. A Pareto-style comparison may help identify dominated candidates, but it must not replace expert review or task-specific evidence.

## 6. Redundancy comparison hierarchy

Compare candidates in this order:

1. Identity equality: same canonical source event/snapshot/revision.
2. Window overlap: same instrument, timeframe and substantially shared input/target intervals.
3. Target equivalence: same target event/outcome and same task definition.
4. Feature similarity: highly similar derived state after accounting for scale and regime.
5. Semantic equivalence: same reasoning target and evidence with only wording or rendering changes.

A duplicate decision must preserve why records are considered equivalent and which canonical record is retained. Similar feature vectors alone are insufficient to delete a sample: two similar states at different times may have different future outcomes and can be useful for calibration or robustness.

Cross-provider observations are not duplicates by default. Preserve their provenance and use them to assess source robustness when appropriate.

## 7. Episode-aware selection

Adjacent snapshots often describe one continuous episode. Build episode clusters using predeclared rules based on time overlap, target horizon, market-event identity and task semantics.

For each cluster, record:
- episode start/end;
- member snapshot IDs;
- common or overlapping target intervals;
- regime/event descriptors available without hindsight;
- cluster-level split assignment;
- representative examples selected and exclusion reasons.

Do not let a large episode contribute hundreds of near-identical rows while a distinct regime contributes only a few. At the same time, do not reduce every episode to one sample if different decision points teach distinct policy states (for example, before trigger, after confirmation, after invalidation).

## 8. Coverage selection without cherry-picking

Coverage dimensions should be defined before examining final test outcomes. Candidate strata include:
- chronological period;
- session and session transition;
- volatility state;
- trend/range/transition/unresolved regime;
- timeframe and MTF alignment/conflict;
- event-risk status;
- spread/liquidity state;
- scenario state (candidate, triggered, invalidated, expired);
- decision action and reason code;
- lifecycle stage and execution outcome availability.

Use natural prevalence for the main evaluation set. Any curated challenge set must be separately named, versioned and reported; it cannot substitute for natural-distribution testing.

Rare states may deserve dedicated evaluation even if they are not oversampled into training. Report both natural and curated distributions.

## 9. Sample selection by task family

The selection criteria depend on the target:

- Forecasting: valid future target window, explicit price convention, horizon and censoring; avoid repeated overlapping target windows dominating.
- Structure/SMC: clear operational criteria, confirmation time and ambiguity handling; retain disagreement cases for reliability research, not forced supervised truth.
- MTF reasoning: synchronized as-of snapshots with correct higher-timeframe completion state.
- Trade policy: decision-time evidence, policy version, deterministic constraints and explicit reason; do not use realized P&L as the action label.
- Risk: authoritative account/instrument inputs and deterministic calculation reference; no fabricated account values.
- Execution: actual broker evidence or explicitly marked simulation assumptions; no assumed fills from candle touches.
- Management: correct event order, position state, partial fills and broker acknowledgement.
- News: point-in-time publication/consensus/revision provenance.
- Visual: image/source snapshot linkage, causal rendering and demonstrated incremental value.

## 10. Human review and disagreement

Human review is reserved for candidates where it can resolve a meaningful semantic or provenance question. Reviewers should see the evidence relevant to the task and remain blinded to future outcomes when judging decision-time reasoning.

Record reviewer, rubric version, decision, reason code, confidence semantics and disagreement. A reviewer's confidence is not a calibrated probability unless validated as such.

For ambiguous or subjective candidates, preserve AMBIGUOUS or QUARANTINE; do not force inclusion to meet a target count.

## 11. Train/validation/test separation

Selection must respect the split protocol:
- define chronological boundaries before train-only sampling;
- group duplicates and overlapping episodes before splitting;
- keep every derived crop, paraphrase, augmentation and target-linked sample with its parent episode;
- apply task-specific purge/embargo;
- prohibit test-driven feature, threshold, annotation-guide or selection-rule tuning;
- allow test data only for final frozen evaluation;
- if test contamination occurs, retire and replace the test period under documented governance.

Do not curate a balanced test set from future knowledge. A separate challenge set may be designed, but it must remain distinct from the untouched chronological test.

## 12. Admission outcomes

Use explicit dispositions:
- INCLUDE: all hard gates pass and value is justified for the named task/split.
- INCLUDE_RESEARCH_ONLY: valid but exploratory; not part of core training release.
- QUARANTINE: potentially useful but a resolvable quality, label or provenance issue remains.
- EXCLUDE_REDUNDANT: adds no distinct evidence or task value relative to a retained canonical example.
- EXCLUDE_INVALID: fails a hard validity gate.
- EXCLUDE_OUT_OF_SCOPE: not relevant to approved tasks.
- HOLD_FOR_REVIEW: evidence is insufficient for a defensible decision.

Every disposition must include a reason and policy version.

## 13. Selection audit report

A future release should report:
- candidate count and disposition counts;
- exclusions by reason;
- hard-gate failure rates;
- value profile by task and dimension;
- duplicate/overlap/episode-cluster statistics;
- coverage before and after selection;
- natural versus curated distributions;
- reviewer disagreement and unresolved queue;
- train-only sampling/weighting details;
- effective independent episode count;
- split leakage audit results.

This report must show what was excluded as clearly as what was retained.

## 14. Release acceptance criteria

A selection policy is ready for implementation only when:
1. task families and target definitions are frozen;
2. hard gates and typed dispositions are operationally unambiguous;
3. duplicate and episode rules are testable;
4. coverage dimensions are predeclared;
5. test-set isolation is enforceable;
6. reviewer rubric and disagreement policy are documented;
7. selection can be reproduced from versioned inputs/configuration;
8. excluded samples and reasons remain auditable;
9. Stage 5 compatibility and source feasibility are reviewed;
10. the user explicitly approves implementation and data work.

## 15. Explicit non-decisions

This document does not set target sample counts, fixed sampling intervals, numeric quality weights, class quotas, minimum event counts, or a universal score threshold. These cannot be responsibly selected before source coverage, target horizon, task needs and effective independent sample sizes are known.

No selection or dataset generation has been performed.
