# Label Specification — Phase 0

## 1. Purpose

Labels define what a training target means. A label is not a convenient class name or an opinion written after observing the outcome. Every label must be reproducible from identified evidence under a frozen rule.

No labels are being generated in this phase.

## 2. Distinct target namespaces

### 2.1 Market outcome labels

Describe what the market did after a decision timestamp, independent of what a trader should have done.

Candidate target types:
- forward return over a fixed horizon;
- first-touch event for explicitly defined upper/lower barriers;
- maximum favorable/adverse excursion over a fixed horizon;
- volatility or regime transition;
- objectively defined structure event, if its confirmation rule is reliable.

Every outcome target must state price source/side, horizon, event window, cost treatment, and censoring/ambiguity behavior.

### 2.2 Policy/action labels

Describe an action under a specified information set and policy:
- LONG;
- SHORT;
- NO_TRADE;
- WATCH;
- WAIT_FOR_CONFIRMATION.

Policy labels require a named policy version, available evidence, constraints, decision rules, and rationale provenance. They must not be inferred from future profitability alone.

NO_TRADE is a valid and important decision. Do not force a directional label when evidence is insufficient or risk constraints prohibit action.

ABSTAIN is distinct from NO_TRADE: ABSTAIN means a reliable policy decision cannot be made from current evidence/state. Existing-position management labels use the separate management_action domain. Execution facts and post-trade/process-quality labels are separate namespaces, not additional policy classes.

## 3. Required label registry fields

| Field | Meaning |
|---|---|
| label_id | Stable target identifier |
| target_family | outcome or policy |
| definition_version | Immutable definition version |
| target_event | Exact event/quantity being labeled |
| decision_timestamp | Point at which inputs are frozen |
| horizon_or_expiry | Fixed horizon or explicit event expiry |
| price_convention | Bid/ask/mid/last or other defined source |
| cost_model_version | Costs included and assumptions |
| confirmation_rule | Evidence needed to resolve target |
| label_confirmed_at | When target became knowable |
| ambiguity_rule | Intrabar/path ambiguity handling |
| censoring_rule | Treatment of incomplete horizon/data |
| label_status | PENDING, RESOLVED, AMBIGUOUS, CENSORED, UNAVAILABLE, INVALID under the canonical label-resolution domain |
| label_value | Typed label value, required only when label_status=RESOLVED |
| provenance | Source IDs and transformation/version references |

## 4. Ambiguous paths and barrier targets

If both stop and target are touched within an OHLC bar and intrabar order is unknown, do not guess which happened first. Mark the sample ambiguous or use finer-grained evidence if it is available and validated.

Specify whether barriers are evaluated against bid, ask, or another price convention. For executable trade outcomes, use side-aware prices and realistic spread/cost assumptions; mid-price-only results must not be presented as executable outcomes.

If a target horizon extends beyond available data, mark it censored/unresolved according to the target contract. Do not convert it into a negative class.

## 5. Probability target design

A probability vector must declare:
- the event space;
- horizon;
- whether classes are mutually exclusive and exhaustive;
- price and cost conventions;
- calibration/evaluation method.

Only mutually exclusive and exhaustive outcomes form a probability partition whose values must sum to one. Directional probability, barrier-touch probability, and probability of a profitable trade are different targets.

Avoid a generic `confidence` field. Use separately named calibrated probabilities and a separately defined uncertainty representation.

## 6. Label quality and reliability

Before admission:
- independently reproduce labels from the same source/version;
- test boundary conditions and timestamp edges;
- measure disagreement for human/discretionary annotations;
- review class prevalence by period and regime;
- test sensitivity to parameters and price conventions;
- document known irreducible ambiguity.

For discretionary structure/SMC concepts, agreement and stability must be demonstrated. If annotators or algorithms cannot consistently identify the event, the label is not reliable ground truth.

## 7. Label leakage firewall

Label values, confirmation timestamps, post-decision excursions, realized trade outcomes, and any field derived from the target must never enter the input feature set for that same prediction.

Dataset construction must enforce separate namespaces/storage and test this invariant automatically before any future release.

## 8. Versioning

Any change to target formula, horizon, price convention, cost model, confirmation rule, ambiguity handling, or policy definition creates a new label version. Never silently relabel an existing release.

## 9. Initial label candidates — not yet approved

1. Fixed-horizon forward return with explicit price convention.
2. Volatility-scaled upper/lower barrier event with ambiguous-path handling.
3. MFE/MAE over a fixed observation horizon.
4. Market-state/regime label only after operational definitions and reliability tests.
5. Policy decision label only when a defensible point-in-time policy provenance exists.

Candidate ranking and final selection depend on intended decision horizons, source feasibility, and the separate Stage 5 compatibility review.
