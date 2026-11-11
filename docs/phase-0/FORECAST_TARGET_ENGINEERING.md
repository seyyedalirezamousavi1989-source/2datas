# Forecast Target Engineering — Phase 0

## 1. Purpose and status

This document defines candidate future-market targets for XAUUSD forecasting. It specifies what a forecast means, how it is observed, and how ambiguity is handled.

**Design only:** no market data has been inspected or processed, no target values or labels have been generated, and no training or benchmark has been run. Exact horizons, thresholds, source feeds, price conventions, and final schemas remain deferred until source feasibility and the Stage 5 compatibility gate are complete.

The governing rule is to forecast a precisely defined market event—not an ambiguous phrase such as "price will go up" or "trade has a high chance of success."

## 2. Forecasting boundary

A forecast is a statement about a future market outcome conditional on a frozen information set at decision time. It is not:
- a trade recommendation;
- a guarantee or certainty;
- an authoritative execution or fill estimate;
- a probability of profit unless the target explicitly models a complete executable trade and its costs;
- a replacement for deterministic account, instrument, sizing, margin, or risk calculations.

Keep four outputs distinct:
1. **Market-state description:** what is observable now.
2. **Outcome forecast:** what defined future market event may occur.
3. **Scenario:** a conditional path with activation and invalidation conditions.
4. **Policy decision:** whether a trade is justified under a named policy and deterministic constraints.

## 3. Universal target definition

Every target must be registered with the following semantics before any examples are generated:

| Attribute | Required meaning |
|---|---|
| target_id / version | Stable identity and immutable definition version |
| target_family | Return, barrier, excursion, event-time, volatility, state-transition, or net-trade outcome |
| instrument_identity | Exact source/broker symbol mapping and contract context where relevant |
| decision_timestamp | Time at which model inputs are frozen |
| observation_start | First eligible future observation after the decision cutoff |
| observation_end / horizon | Fixed endpoint or explicit event expiry |
| source_and_price_basis | Feed, bid/ask/mid/other, and bar/tick convention |
| target_formula | Versioned mathematical or event rule |
| event_space | Exact outcomes and whether mutually exclusive/exhaustive |
| cost_treatment | None, modeled, or realized; specify components |
| confirmation_rule | When the outcome becomes knowable |
| ambiguity_rule | Intrabar ordering, gaps, missing data and competing events |
| censoring_rule | Incomplete horizon or unavailable future observations |
| units | Return fraction, basis points, USD/oz, points, seconds, volatility units, or R |
| provenance | Source revisions and transformation version |

The target registry must be separate from model input fields. A target's confirmation time, realized future path, or final outcome must never enter its own decision-time input.

## 4. Candidate target families

### F01 — Fixed-horizon forward return

**Question:** What was the price return over a defined future horizon?

For a declared price series P and horizon h:

- Simple return: R(t,h) = P(t+h) / P(t) - 1
- Log return: r(t,h) = ln(P(t+h) / P(t))

The registry must specify whether P is bid, ask, mid, or another source-defined price; how the first eligible post-decision observation is selected; and whether the endpoint is an exact timestamp or next available observation.

**Use:** directional distribution, return magnitude, and baseline forecasting.

**Limitations:** a mid-price return is not an executable trade result. Fixed-horizon returns do not encode path risk or whether a threshold was touched earlier.

### F02 — Directional outcome classes

A categorical target may classify the F01 return as positive, negative, or neutral only after a neutral band is defined.

The neutral band must be specified in advance, potentially as a fixed threshold or a volatility-scaled threshold based only on information available at decision time. The threshold, volatility estimator, lookback, warm-up, and version must be frozen.

Boundary equality, rounding, missing endpoints, and tiny price changes must have explicit rules. Do not select a neutral threshold by maximizing final-test performance.

**Probability semantics:** up/down/neutral may form a probability partition only if every possible resolved outcome belongs to exactly one class. Censored or ambiguous records are not silently assigned to neutral.

### F03 — Barrier first-passage outcomes

**Question:** Which predeclared barrier, if any, was reached first within horizon h?

Define upper and lower barriers from a reference price and a declared distance rule. Distance may be absolute, percentage-based, or scaled by a volatility estimate available at decision time. The formula and all parameters are versioned.

Candidate outcomes:
- upper barrier first;
- lower barrier first;
- neither barrier reached by expiry;
- ambiguous path;
- censored/unresolved.

If both barriers are touched within one OHLC bar and intrabar sequence is unavailable, the result is ambiguous—not whichever outcome is more convenient. Finer-grained tick/quote evidence may resolve the order only if its coverage and timestamp integrity are validated.

A barrier probability is not a probability of a profitable trade. Barriers must declare price side and cost assumptions.

### F04 — Maximum favorable/adverse excursion (MFE/MAE)

**Question:** How far did price move favorably or adversely relative to a declared reference during a future window?

Define direction convention, reference price, future observation window, price side, and units. Preserve both absolute price distance and normalized forms only when their meaning is explicit.

For a long-oriented reference, illustrative raw excursion definitions are:
- MFE = maximum eligible future high minus reference entry price.
- MAE = reference entry price minus minimum eligible future low.

Short-oriented definitions reverse the favorable/adverse direction. These formulas are descriptive market-path measures; executable trade excursions require side-aware bid/ask and realistic fill assumptions.

OHLC extrema reveal excursion magnitude but not the path/order of extrema. Do not infer stop/target sequencing from MFE and MAE alone.

### F05 — Time-to-event / time-to-barrier

**Question:** How long until a specified event occurs, if it occurs within the observation window?

Specify event definition, clock basis, eligible observation start, event timestamp resolution, expiry, and censoring. A sample with no event by expiry is right-censored, not necessarily a permanent negative.

Evaluate survival/time-to-event predictions with methods appropriate to censoring; do not convert censored cases into ordinary classification negatives.

### F06 — Future volatility and range

**Question:** What realized volatility or price range occurred over a defined future window?

Specify estimator, sampling frequency, price basis, annualization (if any), units, missing-bar treatment, and window boundaries. Distinguish:
- realized return volatility;
- high-low range;
- absolute movement;
- volatility-regime transition.

A future volatility label is a target only. It must never be used as a current-time feature for the same decision.

### F07 — Market-state transition

**Question:** Did the market transition from a defined current state to another state within a future window?

Both the initial and destination state taxonomies must be operationally defined and versioned. Specify transition onset vs confirmation time, minimum persistence, reversals, multiple transitions, and unresolved cases.

A state transition target is distinct from current-state classification. If state labels are unreliable, the transition target is not admissible.

### F08 — Net outcome of a fully specified hypothetical trade

**Question:** What would the net outcome have been for a precisely specified executable trade policy under stated assumptions?

This target is admissible only when the trade specification is complete: direction, entry trigger/fill rule, order type, quantity convention, stop/target/expiry, broker instrument specification, bid/ask, spread, commission, swap, slippage, latency, partial fills, gaps, and rejection behavior as supported by evidence.

Separate:
- observed historical broker execution;
- simulated execution under a versioned model;
- simplified candle-based proxy.

Never label a simulated fill as an actual fill. If execution data is insufficient, narrow the claim to a market-path target rather than fabricate net P&L.

## 5. Price and execution conventions

Gold price feeds and broker symbols may differ in quote precision, contract size, tick size, trading hours, and historical specification. Do not assume universal XAUUSD contract semantics.

For every target, state:
- exact symbol/feed mapping and any symbol changes;
- bid, ask, mid, last, or bar-derived price;
- timestamp and bar interval convention;
- timezone and daylight-saving handling;
- spread/commission/swap treatment;
- currency conversion and contract specification when translating price movement into account P&L;
- whether price is observed, reconstructed, or simulated.

Market-price targets and executable-trade targets must not be mixed in one unlabeled field.

## 6. Horizon selection without target proliferation

Do not create a large Cartesian product of every timeframe, threshold, barrier multiplier, and horizon.

Choose a small number of horizons from the intended downstream decisions and verified source coverage. For each candidate horizon:
1. state which decision it supports;
2. establish that future observations are available at the required resolution;
3. quantify overlapping target windows and effective independent episodes;
4. define a primary target before exploring variants;
5. compare variants only under a documented multiple-comparison protocol;
6. remove horizons that do not add distinct value.

Forecast horizon is independent of chart timeframe. A model may use several timeframes to predict one explicitly defined future horizon.

## 7. Probability outputs and distribution forecasts

Each probability output must identify one target_id/version and horizon. If outcomes form a mutually exclusive and exhaustive partition, probabilities must be non-negative and sum to one within a declared numerical tolerance.

If outcomes overlap (for example, upper barrier touched and a volatility threshold exceeded), they are separate event probabilities and are not required to sum to one.

Potential forecast forms:
- categorical probabilities for a valid partition;
- event probability for one precisely defined event;
- conditional quantiles of future return/range;
- a predictive distribution with documented support and calibration method;
- time-to-event/survival distribution when censoring is present.

Do not emit an unqualified generic confidence score. Distinguish aleatoric uncertainty, model uncertainty where measurable, and data-quality limitations; do not claim a decomposition unless it is actually estimated.

## 8. Cost-aware targets and price-side consistency

A directional market forecast can be useful even when costs are not included, but its meaning must remain explicit.

For net-trade targets, entry and exit prices must reflect the correct side of the quote and the trade direction. Include commissions, swaps, currency conversion and realistic slippage only when evidence or a documented simulation model supports them.

Do not subtract a generic fixed spread from all historical observations if spread varies materially by time, session, volatility, or broker. If costs are modeled, retain both the observed market path and the cost-model version.

## 9. Ambiguity, missing data and censoring

Represent separately:
- resolved outcome;
- ambiguous intrabar path;
- no event by expiry;
- right-censored due to end of available data;
- missing or invalid source interval;
- stale/incomplete quote;
- source correction;
- not applicable.

Do not silently forward-fill future prices, interpolate across market closures, infer tick order from OHLC, or turn missing endpoints into zero returns.

A target may be unusable for one target family but still valid for another. Preserve target-specific status rather than discarding or coercing the entire market snapshot.

## 10. Leakage and split controls specific to forecasts

- Input cutoff is the actual availability time, not merely the candle timestamp.
- Future target windows must be excluded from all input materializations.
- Purge examples whose target windows overlap across train/validation/test boundaries.
- Apply embargo where delayed confirmation, serial dependence, or event duration can bridge splits.
- Group highly overlapping examples by episode before assigning splits.
- Fit thresholds, scalers, volatility normalizers, and calibration maps on training/validation only as appropriate.
- Freeze target definitions before opening the final test.
- If multiple target/horizon variants are explored, record all trials to expose selection bias.

## 11. Forecast evaluation by target family

| Target | Core evaluation |
|---|---|
| Fixed-horizon return | MAE/RMSE or robust alternatives; directional skill as a secondary metric; calibration of predictive distributions |
| Directional classes | Per-class precision/recall, balanced accuracy, confusion matrix; Brier/log loss for probabilities |
| Barrier first-passage | Multiclass/event Brier or log loss, calibration, event precision/recall, ambiguity rate |
| MFE/MAE | MAE/RMSE/quantile loss; calibration and tail coverage for distributions |
| Time-to-event | Censoring-aware survival metrics, calibration and discrimination |
| Future volatility/range | MAE/RMSE/quantile loss; interval coverage and stability |
| State transition | Transition precision/recall, timing tolerance, calibration and state-label reliability |
| Net trade outcome | Net expectancy and distribution, drawdown/tail risk, cost sensitivity, execution realism and confidence intervals |

Always report sample count, effective independent episodes, confidence intervals, chronological fold dispersion, and performance by relevant regimes/sessions/sources. Compare against persistence, unconditional prevalence/distribution, simple momentum/mean-reversion and other appropriate baselines.

## 12. Target admission and retirement gate

Admit a target only if:
1. it answers a named downstream question;
2. the source can resolve it at the required temporal/price precision;
3. formula, units, horizon and price convention are unambiguous;
4. ambiguous/censored cases are handled honestly;
5. target generation is reproducible;
6. leakage and split rules are testable;
7. metric and baseline are specified;
8. it is not a redundant re-expression without a distinct consumer;
9. its expected value justifies data and maintenance cost;
10. the user approves the next phase.

Retire or narrow a target if it is unreliable, redundant, too sparse, highly sensitive to arbitrary thresholds, impossible to evaluate robustly, or not useful to a downstream decision.

## 13. Explicit non-decisions

This document does not select:
- exact forecast horizons or timeframe set;
- barrier distances or neutral bands;
- price feed/provider or broker;
- a universal volatility estimator;
- target prevalence or sample count;
- a model architecture or training method;
- any dataset-generation or evaluation run.

These decisions require Stage 5 compatibility, source feasibility, and separate user authorization.
