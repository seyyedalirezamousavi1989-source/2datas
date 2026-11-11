# Target Portfolio and Redundancy Decision — Phase 0

## 1. Status and scope

**Provisional target-portfolio decision v0.1; no target is approved for generation.**

This document reconciles the F01–F08 candidate families in FORECAST_TARGET_ENGINEERING.md with Y01–Y06 in TARGET_AND_LABEL_INTELLIGENCE_GOVERNANCE.md and the A–M/T01–T11 task architecture.

No data, labels, samples, benchmarks or training runs were produced. Exact horizons, thresholds, price bases, source requirements and final target selection remain gated by Stage 5 acceptance, source feasibility and explicit user approval.

## 2. Governing decision

The target portfolio must not treat every mathematical view of the same future price path as an independent learning problem or independent sample.

Use four relationships:
- **Primary target:** the canonical future quantity/event that answers a distinct downstream question.
- **Derived projection:** a deterministic transformation of a primary target, such as a directional class derived from a return and neutral band.
- **Alternative parameterization:** another view of the same event/path, such as time-to-barrier derived from a first-passage event.
- **Conditional extension:** a target requiring additional source precision, policy provenance, broker history or annotation reliability.

A single decision episode may have multiple valid target views, but those views share episode identity and must not be counted as independent evidence. Each target has its own target_id/version, but lineage must expose shared underlying observations and overlapping future windows.

## 3. F01–F08 to Y01–Y06 crosswalk

| Forecast family | Governance candidate | Portfolio role | Provisional decision | Main redundancy/feasibility rule |
|---|---|---|---|---|
| F01 Fixed-horizon forward return | Y01 Fixed-horizon return distribution | Primary market-outcome target candidate | **Core candidate** | One canonical return definition per horizon/price basis; exact horizon remains open |
| F02 Directional outcome classes | Y02 Directional partition | Derived projection of F01 | **Not an independent core target** | Derive from the same return path using a frozen neutral band; promote as a separate output head only if a distinct consumer and incremental value are shown |
| F03 Barrier first-passage | Y03 First-passage barriers | Distinct path-sensitive event target | **Conditional** | Requires validated tick/quote order or honest OHLC ambiguity/censoring; not a probability of trade profit |
| F04 MFE/MAE | Y04 MFE/MAE | Path/risk sidecar target | **Conditional sidecar** | Describes excursions, not event order or decision correctness; avoid separate rows if no management/risk consumer |
| F05 Time-to-event/barrier | Usually derived from F03 | Alternative parameterization | **Do not duplicate by default** | Keep only if a censoring-aware time-to-event consumer justifies it; same event/episode lineage as F03 |
| F06 Future volatility/range | Y05 Future range/volatility | Distinct future magnitude target | **Conditional** | Must be target-only and separate from current T09 volatility-regime features; retain only with a downstream use |
| F07 Market-state transition | Y06 State transition | Future transition target | **Conditional** | Requires reliable initial/destination taxonomy; must not duplicate T01 current state or T09 volatility transition |
| F08 Net outcome of hypothetical trade | Separate policy/execution extension | Executable-policy outcome | **Excluded from initial market-forecast core** | Requires complete trade specification, broker/instrument rules, bid/ask, costs, latency/fills/gaps; simulated outcomes remain explicitly simulated |

## 4. Minimal first-portfolio recommendation

Subject to source feasibility and Stage 5 compatibility, the smallest defensible first forecast portfolio is:

1. **F01/Y01 fixed-horizon return** as the canonical continuous market-outcome target.
2. **F02/Y02 directional projection** only as a derived view of F01, not an additional independent sample family. A separate classification head is optional and must prove value.
3. **F03/Y03 barrier first-passage** only if source resolution is sufficient; otherwise defer rather than force OHLC path order.
4. Keep F04 MFE/MAE as a sidecar measurement for later management/risk research, not a default standalone training target.
5. Defer F05 time-to-event unless survival-style outputs answer a distinct downstream question.
6. Defer F06 future volatility/range and F07 state transition until T09/T01 target taxonomies and downstream consumers are stable.
7. Exclude F08 net hypothetical-trade outcome from the initial market forecast core.

This is a research ordering, not authorization to create these targets. Even F01 remains conditional on source, price-basis and horizon feasibility.

## 5. Keep non-market targets in separate namespaces

The following are not market-outcome target substitutes:

- **Policy/action labels:** actual output of a named, reconstructable policy at decision time. Entry actions and management actions use their own canonical domains. Never infer them from eventual P&L.
- **Execution labels:** broker/system facts such as submitted, acknowledged, rejected, filled, partial fill and realized costs. Require verified broker records.
- **Process-quality labels:** whether a decision followed its stated policy and constraints. Evaluate separately from outcome.
- **Structure/SMC labels:** objective event labels only after operational definitions, independent reproducibility and annotation reliability.
- **Scenario assessments:** conditional hypothesis lifecycle/assessment, not a forced market outcome class.
- **News/visual reasoning:** evidence modalities; they do not create new target families by themselves.

## 6. Target dependency and redundancy controls

Every target definition must declare:
- target_id/version and family;
- primary/derived/alternative/conditional relationship;
- underlying observation and source revision references;
- decision snapshot and future observation window;
- horizon/expiry and confirmation time;
- price basis, units and cost treatment;
- ambiguity/censoring rule;
- downstream task/consumer;
- evaluation metric and baseline;
- episode/group identity and overlap dependencies.

Rules:
1. F02 derived from F01 must share the same future-path lineage and episode grouping.
2. F05 derived from F03 must not create a second independent event count.
3. F04 MFE/MAE, F03 barrier outcomes and F01 returns may overlap in the same future path; account for this in multi-task sampling and effective sample size.
4. F06 future volatility is not a current-time feature; current T09 regime state is a separate input-time assessment.
5. F07 transition labels must specify whether the destination is a T01 price/structure state or T09 volatility state; do not merge both taxonomies.
6. F08 net trade outcome must reference a complete policy/execution specification and must not be mixed with observed market returns.
7. Overlapping target windows from one episode remain grouped before chronological splitting, purging and embargo.

## 7. Horizon and threshold policy

Do not choose horizons, neutral bands, barrier distances, lookbacks or volatility thresholds by convenience or class balancing.

For each candidate:
- name the downstream decision it supports;
- confirm the source can resolve the horizon at the required precision;
- freeze the target formula and boundary rules before final-test access;
- quantify overlap and effective independent episodes;
- compare only a small, justified set of variants under a multiple-comparison-aware protocol;
- remove variants that do not add distinct value.

Chart timeframe is not automatically forecast horizon. No exact horizon or threshold is selected by this document.

## 8. Evaluation separation

Evaluate each target family according to its own meaning:
- F01: return error/distribution quality and directional skill as a secondary view.
- F02: class-wise precision/recall and proper probability scoring if calibrated; compare with F01-derived baseline.
- F03: event scoring/calibration, ambiguity rate, timing and path-resolution coverage.
- F04: excursion error/quantile coverage and tail behavior; do not infer barrier order.
- F05: censoring-aware survival metrics only if retained.
- F06: future range/volatility error, quantile coverage and stability.
- F07: transition accuracy/timing and state-label reliability.
- F08: net expectancy, costs, drawdown, execution realism and uncertainty only under complete execution assumptions.

Always report sample count, effective independent episodes, unresolved/censored rates, chronological fold dispersion and regime/source coverage. A higher metric on a redundant projection does not prove independent information gain.

## 9. Decisions and open gates

Accepted provisionally:
- F01/Y01 is the primary market-outcome candidate.
- F02/Y02 is a derived projection, not an independent sample family by default.
- F03/Y03 is a distinct but source-conditional path target.
- F04/Y04 is a sidecar unless a specific management consumer justifies training on it.
- F05/Y05/F06/Y06/F07/F08 remain conditional or deferred as stated above.
- Policy, execution, process-quality and post-trade outcomes remain separate target namespaces.

Still open:
- exact source, price side and horizon;
- neutral-band and barrier definitions;
- whether quote/tick history resolves first passage;
- T09 future volatility target value beyond current regime features;
- state taxonomy reliability for F07;
- broker/policy/execution provenance for F08;
- sample sufficiency and split dependencies.

No target is empirically accepted by a design decision. Stage 5 acceptance, source feasibility, independent review and explicit user approval remain mandatory.

## 10. Explicit non-authorization

This document does not authorize archive inspection, data acquisition, target/label generation, sample selection, pipeline implementation, benchmark execution, model training, AURORA QUANT modification, Stage 5 modification or branch merge.
