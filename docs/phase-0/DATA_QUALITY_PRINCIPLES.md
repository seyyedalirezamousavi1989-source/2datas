# Data Quality, Signal Density, and Leakage Controls

## 1. Inclusion test: does this information earn its place?

A candidate field, feature, task, or sample is included only if it passes all applicable checks:

1. **Purpose:** a named task or evaluation question uses it.
2. **Definition:** its calculation/meaning is precise and versioned.
3. **Availability:** its value was available at the decision timestamp.
4. **Reliability:** source and calculation limitations are known.
5. **Incremental value:** it adds information beyond existing fields or a simpler representation.
6. **Non-duplication:** it is not an exact, near, or semantic duplicate without a justified reason.
7. **Evaluability:** its contribution can be tested on chronological held-out data.
8. **Cost:** its storage, complexity, and maintenance burden are justified.

If incremental value is unknown, mark the field as a research candidate—not an approved feature. Do not automatically retain every indicator or every possible timeframe.

## 2. Redundancy control

Detect and review:
- exact duplicate records and identical payloads;
- overlapping windows that create near-identical examples;
- repeated chart images or equivalent chart snapshots;
- copied narrative templates with only superficial wording changes;
- derived indicators that encode nearly the same underlying signal;
- duplicated target outcomes under different names;
- the same market event repeated across tasks without a distinct learning objective.

Use stable canonical observation IDs and content fingerprints. Similarity-based deduplication must not erase genuinely distinct market states or chronological events. Keep lineage to the canonical source record.

Do not inflate dataset size by paraphrasing the same example. One high-quality, well-evidenced example is preferable to many cosmetic variants.

## 3. Label discipline

Every label specification must state:
- target concept and operational formula;
- decision time and target horizon/event window;
- price side and price source (bid/ask/mid/last as appropriate);
- costs included or excluded;
- confirmation time;
- ambiguous-path handling;
- censoring and incomplete-data handling;
- version and reproducibility test.

For OHLC bars where both stop and target could have been touched but intrabar order is unknown, mark the outcome ambiguous or resolve it only with sufficiently granular data. Never assume the favorable sequence.

SMC/structure labels require operational definitions and inter-annotator or algorithmic reliability checks. A discretionary concept is not objective ground truth merely because it has a familiar name.

## 4. Missingness and ambiguity

Do not overload null. Define explicit states such as:
- `known`;
- `unknown`;
- `unavailable_from_source`;
- `not_applicable`;
- `not_yet_observable`;
- `ambiguous`;
- `censored`;
- `invalid`.

The schema may encode these as status enums plus optional values. Never replace missing evidence with zero, a default class, or fabricated certainty unless the domain definition explicitly requires it.

## 5. Leakage prevention

Audit for:
- future candles, partial-bar values that were not yet available, and future-confirmed swings;
- indicators computed with centered windows or future-dependent normalization;
- news data indexed by event date rather than actual publication/availability time;
- target-derived fields or post-trade metrics leaking into inputs;
- overlapping input/target windows across train/validation/test;
- duplicate or near-duplicate market intervals across splits;
- higher-timeframe values whose bars had not closed;
- preprocessing fitted using validation/test data;
- chart annotations, scaling, captions, or filenames revealing future outcomes;
- label revisions or source corrections unavailable at the historical decision time.

Split chronologically. Purge overlapping target windows and apply an embargo appropriate to each target horizon and data dependency. Freeze split boundaries before model selection; keep the final test set untouched until the protocol is fixed.

Do not adopt a fixed 60/20/20 split by habit. Choose date boundaries based on coverage, regime representation, target horizon, sample adequacy, and leakage dependencies.

## 6. Market and source integrity

Required checks, adapted to source granularity:
- timestamp monotonicity, timezone conversion, duplicates, missing intervals;
- OHLC invariants and impossible values;
- quote-side consistency, spread validity, tick ordering where available;
- volume semantics (tick volume vs traded volume);
- precision, contract/instrument specification changes;
- session and daylight-saving transitions;
- source disagreement, corrections, outliers, stale quotes;
- timeframe aggregation consistency.

Do not interpolate or synthesize market observations without explicit labeling and a justified use. Preserve raw values and record every transformation.

## 7. Statistical quality

Report distributions by time and regime, not just overall totals:
- coverage and missingness;
- target prevalence and class imbalance;
- volatility/session/regime coverage;
- time concentration and duplicate rate;
- label ambiguity/censoring rates;
- confidence intervals and effective independent sample size;
- temporal drift and source/provider shifts.

A large count of highly overlapping windows is not equivalent to a large independent sample.

## 8. Evaluation integrity

Compare against simple and relevant baselines: NO_TRADE, majority class, naive directional rules, momentum, mean reversion, trend following, deterministic setups, and existing AURORA components where access is later authorized.

Use metrics appropriate to the target:
- classification: precision/recall, F1, balanced accuracy, confusion matrix;
- probability: Brier score, log loss, reliability/calibration, confidence intervals;
- regression: MAE/RMSE and normalized errors;
- trading: net expectancy in R, drawdown, profit factor, trade frequency, exposure, turnover, cost sensitivity, and uncertainty intervals.

AUC near 0.50 is not evidence of useful discrimination. Apparent expectancy near zero or with an interval spanning zero is not evidence of an edge. Report failed and negative results.

## 9. Synthetic data

Synthetic examples may be used later for schema tests and software edge cases only. They must be explicitly marked, stored separately, and excluded from empirical claims and real-market training unless a separate, justified research protocol is approved.

## 10. Release checklist

A dataset release is blocked if any critical item is unresolved:
- provenance or licensing is unknown;
- causal availability cannot be established;
- label definitions are not reproducible;
- critical leakage or split contamination exists;
- ambiguous outcomes are silently forced into classes;
- financial/execution assumptions are unverified;
- QC failures are unexplained;
- generation cannot be reproduced;
- test data has influenced feature/label selection;
- limitations are hidden or performance is overstated.
