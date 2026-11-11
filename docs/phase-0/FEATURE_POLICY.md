# Feature Admission Policy — Phase 0

## 1. Objective

Build a small, interpretable, point-in-time feature set. Do not maximize the number of indicators. Each feature must justify its existence through reliability, causal availability, and measurable incremental value.

This document defines admission rules; it does not approve any actual market feature or compute values.

## 2. Feature registry contract

Every proposed feature must have a registry entry containing:

| Field | Meaning |
|---|---|
| feature_id | Stable unique identifier |
| name | Concise canonical name |
| definition_version | Version of formula/semantics |
| purpose | Exact task or research question served |
| input_dependencies | Source fields and upstream features |
| formula_or_rule | Complete reproducible definition |
| unit_and_scale | Units, normalization, valid range if known |
| event_time_rule | Market time represented |
| available_at_rule | Earliest time the feature can be used |
| lookback | Required history and warm-up behavior |
| timeframe | Source timeframe and bar-completion policy |
| missingness_policy | Explicit missing/unavailable behavior |
| invalidity_conditions | Conditions under which value must not be used |
| redundancy_group | Related features to compare |
| known_limitations | Sensitivity, source dependence, instability |
| validation_status | Proposed, tested, accepted, rejected, retired |
| evidence_reference | Test/report supporting admission |

No feature may be marked accepted while formula, availability, or missingness behavior is undefined.

## 3. Candidate feature families

These are research categories, not an approved shopping list.

### A. Price and return representation
Prefer a compact set of causally valid returns and normalized price/range measures over many overlapping transformations. Define price side and reference convention consistently.

### B. Volatility and range
Prefer measures with distinct horizons or clearly different semantics. Avoid retaining multiple nearly equivalent rolling range/volatility estimators without evidence of incremental value.

### C. Trend and momentum
Use a limited set of interpretable measures. Compare each candidate against simpler return/slope representations. Do not include multiple parameter variants merely to increase dimensionality.

### D. Structure
Candidate swing, break, range-boundary, and invalidation features require strict confirmation-time rules. A swing that becomes knowable only after later bars cannot be backdated as if it were known at the pivot.

### E. Multi-timeframe context
Only include higher-timeframe values available at the decision time. Record whether each bar is complete or partial and apply one consistent as-of rule.

### F. Session and event context
Session/time-of-day fields must encode timezone, session calendar, and daylight-saving rules. News/event fields require point-in-time publication and availability metadata.

### G. Liquidity/SMC candidates
Each concept requires a formal operational definition, sensitivity analysis, and labeling reliability review. Never label a feature as institutional order flow unless the source actually observes such flow.

## 4. Admission workflow

1. Propose one feature with a named consumer.
2. Specify formula, units, dependencies, lookback, and availability.
3. Test source reliability and edge cases.
4. Check exact/near duplication and correlation conditional on regime/time.
5. Compare against a simpler baseline representation.
6. Measure incremental value on chronological validation data.
7. Test stability across time, sessions, volatility regimes, and source changes.
8. Admit, revise, or reject with a recorded reason.

A high correlation alone is not an automatic deletion rule; two features can be correlated yet serve different semantics. Conversely, low correlation does not prove usefulness. Evaluate conditional incremental value and stability.

## 5. Normalization and preprocessing

- Fit scaling, imputation, feature selection, and any learned transform on training data only.
- Preserve units and raw reference values where necessary for interpretation.
- Do not normalize using future observations or full-dataset statistics.
- Define warm-up and missing-history behavior explicitly.
- Do not silently clip outliers; record thresholds and retain raw source values.
- Treat broker/source changes as possible distribution shifts.

## 6. Feature retirement

A feature should be rejected or retired if it is:
- unavailable at the intended decision time;
- non-reproducible or source-dependent without traceability;
- a duplicate with no distinct consumer;
- unstable across chronological periods;
- too sensitive to arbitrary parameters;
- not incrementally useful after controlling for simpler features;
- expensive to maintain relative to demonstrated value.

Retirement must not erase historical definitions: keep version history and identify which dataset releases used each version.
