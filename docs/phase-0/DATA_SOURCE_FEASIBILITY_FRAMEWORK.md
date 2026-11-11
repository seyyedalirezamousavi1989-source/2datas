# XAUUSD Data Source Feasibility and Admission Framework — Phase 0

## 1. Purpose and authorization boundary

Define what evidence a future source-feasibility review must collect before any provider or archive is accepted.

**Design only.** No provider has been contacted or approved; no website, API, archive or uploaded file has been inspected; no market data has been downloaded or processed. The existing XAUUSD.zip remains an uninspected, unchanged artifact. This document does not authorize Stage 5 inspection, source acquisition, extraction, labeling, pipeline implementation or training.

The objective is to acquire the smallest set of licensed, trustworthy source records that can support the approved tasks. More data sources are not inherently better.

## 2. Source roles and evidence tiers

Classify sources by the claims they can legitimately support.

### Tier A — Primary market observations
Broker/server-specific ticks, bid/ask quotes and bars. These support point-in-time price and execution research tied to a particular feed. They are not a universal consolidated XAUUSD market tape.

### Tier B — Independent market corroboration
A second broker or provider can quantify feed-specific differences, gaps and robustness. Do not merge feeds into a fictitious single price series. Preserve provider identity, timestamp semantics and symbol definition.

### Tier C — Instrument and execution specifications
Contract size, tick size/value, digits, volume constraints, calculation mode, trading sessions, margin rules, swap, commissions, stop/freeze levels and historical changes. These must match the broker/server/account context for broker-specific risk or execution claims.

### Tier D — Macro and event information
Official releases and point-in-time calendar/consensus archives. Actual release, expected value, prior value, revisions and ingestion/availability times must be distinct. A current calendar page is not a historical point-in-time archive.

### Tier E — Execution and account evidence
Order requests, acknowledgements, rejections, fills, partial fills, modifications, cancellations, positions, costs and account snapshots. These are required for claims about realized execution and lifecycle behavior. Simulated fills must be labeled as simulated.

### Tier F — Derived or contextual material
News articles, research notes, chart images, third-party indicators and derived features. These are optional and must prove provenance, rights, causal availability and incremental value over simpler primary data.

## 3. Task-to-source dependency

Do not acquire every source class for every task.

| Capability | Minimum evidence | Important limitation |
|---|---|---|
| OHLC market state | Identified provider bars with construction/timezone rules | Cannot recover exact intrabar path |
| Spread-aware analysis | Timestamped bid/ask or trustworthy spread series | OHLC mid/close alone is insufficient |
| Tick/first-passage targets | Ordered tick/quote data with sequence semantics | Bar approximations must be explicitly marked |
| Multi-timeframe analysis | One consistent source plus exact bar boundaries | Cross-provider bars may not align |
| Broker-specific risk | Historical contract/account currency specifications | Generic symbol metadata is insufficient |
| Realized execution | Broker event/fill history and reconciliation | Planned price is not a fill |
| News reaction | Point-in-time release and expectation snapshots plus market data | Later revisions create hindsight leakage |
| Visual analysis | Reproducible causal chart rendering linked to source snapshot | Images add cost and may duplicate numeric input |
| Post-trade review | Full event chronology and realized costs | Must remain isolated from decision-time input |

A task with unmet source dependencies must be deferred, simplified or explicitly restricted. Do not substitute a weaker source while retaining a stronger claim.

## 4. Required source dossier

Every candidate provider/archive must have a versioned dossier with:

### Identity and access
- Provider/legal entity and product name.
- Exact API, archive, terminal or export route.
- Account/subscription tier and access conditions.
- Stable instrument/symbol identifiers.
- Retrieval date and source documentation revision.
- Contact/ownership and support path where relevant.

### Coverage and granularity
- First/last available timestamp.
- Timezone and daylight-saving behavior.
- Supported timeframes and bar construction.
- Tick/quote granularity and sequence guarantees.
- Bid, ask, last, midpoint and volume fields.
- Session breaks, holidays and maintenance gaps.
- Historical symbol/specification changes.

### Temporal semantics
- Event timestamp, provider timestamp and local receive/ingestion timestamp.
- Precision, clock source and known drift.
- Ordering guarantees for equal timestamps.
- Late, corrected or revised record behavior.
- Whether historical data represents what was available in real time.
- Whether bars are final, revised or reconstructed.

### Quality and limitations
- Missingness and gap reporting.
- Duplicate behavior and correction policy.
- Outlier/zero/negative quote conventions.
- Price precision and rounding.
- Volume meaning (tick count, traded volume, broker volume, unknown).
- Known outages, feed changes and backfill behavior.
- Cross-provider differences and non-comparability.

### Rights and governance
- License owner and governing terms.
- Permitted storage, transformation, derived labels and model training.
- Redistribution and publication restrictions.
- Retention/deletion requirements.
- Commercial use and deployment restrictions.
- Attribution requirements.
- Legal review status.

A source without adequate rights evidence is not admitted, regardless of technical quality.

## 5. Minimum canonical raw market record

The final physical schema remains pending, but a source adapter must preserve, where supplied:
- provider_id, feed_id and account/server context if relevant;
- source_symbol and canonical instrument mapping version;
- event_timestamp and timestamp precision;
- receive/ingestion timestamp when available;
- sequence number or provider ordering token when available;
- bid and ask as separate fields;
- last/trade price only with explicit semantics;
- volume with its exact meaning and unit;
- source revision/correction identifier;
- raw record reference and integrity checksum.

Do not fabricate unavailable fields. Do not silently convert bid/ask into a single price. Derived midpoint or bars must be separate versioned records with formula and lineage.

## 6. Bar construction and timeframe rules

A provider's M1 bar is not automatically equivalent to another provider's M1 bar.

For every bar series, document:
- interval convention (for example, left-closed/right-open);
- timestamp denotes bar open or close;
- timezone and session calendar;
- price side or aggregation basis;
- OHLC construction from bid, ask, last or midpoint;
- volume aggregation meaning;
- treatment of missing intervals and no-tick bars;
- late tick and bar revision policy;
- whether incomplete/current bars are exposed.

Higher-timeframe bars should be derived from a canonical lower-level source only when the aggregation rule is known and validated. Otherwise retain provider-native bars as a distinct series. Never combine partial bars with completed bars without explicit state.

## 7. Tick and quote feasibility

Tick data is valuable for spread, order-trigger and intrabar ordering questions only if its semantics are reliable.

Verify:
- whether records are quote updates, trades, or both;
- whether bid and ask are simultaneous snapshots or independently updated fields;
- whether unchanged-side quotes are repeated or omitted;
- sequence ordering and equal-timestamp behavior;
- timestamp precision and clock synchronization;
- dropped packet/gap indicators;
- market closure and stale-quote conventions;
- whether historical ticks are raw, filtered, compressed or reconstructed.

A dataset labeled tick without these details must not be assumed to support execution-grade simulation.

## 8. Broker specification and account context

A symbol named XAUUSD can differ across brokers and account types.

For each relevant effective period, seek:
- contract size and calculation mode;
- digits, point, tick size and tick value;
- profit currency and account-currency conversion behavior;
- volume minimum/maximum/step;
- margin calculation and leverage tier;
- stop level and freeze level;
- execution mode and filling policy;
- trading sessions, holidays and rollover;
- commission schedule and swap/financing rules;
- specification effective-from/effective-to timestamps.

Distinguish static published specifications from actual account/server-specific behavior. If historical specifications cannot be recovered, restrict claims to the period and assumptions that can be verified.

## 9. News and macro archive requirements

For each event/release preserve, when available:
- unique event ID and source;
- scheduled time and actual publication time;
- original timezone and normalized UTC time;
- initial released value;
- consensus snapshot captured before release;
- prior value as known before release;
- subsequent revisions as separate versioned events;
- source publication and system ingestion times;
- currency/asset relevance classification and its version;
- license and permitted model-training use.

Do not infer a historical consensus from a current page. Do not use revised macro values as if they were known at initial publication. News text and interpretations require their own source lineage and availability timestamps.

## 10. Execution and account-history requirements

For actual execution claims, a source should preserve:
- request ID and order ID;
- request time and broker acknowledgement time;
- requested side, type, price, volume and constraints;
- accepted/rejected/cancelled/expired status and reason;
- deal/fill IDs, time, price and volume;
- partial fills and residual quantity;
- commissions, swap, fees and realized P&L;
- position IDs and linkage across netting/hedging semantics;
- modifications and broker acknowledgements;
- account equity/balance/margin snapshots with currency and timestamps;
- corrections, reconnect gaps and reconciliation evidence.

Protect personal/account identifiers. Only retain fields necessary for approved research, and never place credentials, tokens or secrets in the repository or dataset.

## 11. Source comparison and admission rubric

Evaluate each source independently against these gates:
1. Rights: permitted use for intended transformation, model training and retention.
2. Identity: unambiguous provider, symbol and feed identity.
3. Temporal integrity: timestamp meaning, ordering and availability are understood.
4. Coverage: period and granularity match the task.
5. Semantic integrity: bid/ask, volume, bars and specs have documented meanings.
6. Quality: gaps, duplicates, corrections and anomalies are measurable.
7. Reproducibility: retrieval/version/checksum can be recorded.
8. Incremental value: source adds a distinct capability or useful independent corroboration.
9. Cost: licensing, storage, compute and maintenance are proportionate.
10. Governance: privacy, security and retention controls are acceptable.

Disposition:
- APPROVED_FOR_SPECIFIC_TASKS
- APPROVED_WITH_LIMITATIONS
- RESEARCH_ONLY
- QUARANTINED_PENDING_EVIDENCE
- REJECTED

Approval is task-specific, not blanket approval for all uses. Keep evidence and rationale for every decision. No numeric weighted score can override a failed rights or temporal-integrity gate.

## 12. Minimal-source strategy

Prefer the smallest defensible source set:
- one primary feed for internally consistent market-state and forecast tasks;
- a second independent feed only where corroboration or robustness adds measurable value;
- tick/quote history only for tasks that need intrabar/spread/execution semantics;
- broker specifications only for the broker/account domain being modeled;
- macro/news archive only if point-in-time coverage and rights pass;
- actual execution history only for lifecycle/execution claims;
- chart images only after a controlled structured-versus-visual comparison justifies them.

Avoid collecting multiple overlapping providers merely to increase row count. Do not merge incompatible feeds or present one broker's history as universal gold-market truth.

## 13. Source limitations must travel with every derived record

Each derived record should retain references to:
- provider/feed and source record IDs;
- symbol mapping and specification version;
- timestamp semantics and availability;
- source quality flags;
- transformations and software/configuration version;
- assumptions and limitations;
- license/usage classification;
- missingness or imputation status.

A downstream model or evaluator must distinguish observed fact, derived value, estimate, simulation assumption and unknown state.

## 14. Source feasibility review deliverable

When separately authorized and when project gates permit, the source-feasibility phase should produce:
1. Candidate source inventory and source dossiers.
2. Rights/license decision for each intended use.
3. Coverage and granularity matrix.
4. Timestamp and bar-semantics comparison.
5. Quality/gap/correction assessment.
6. Broker-specification coverage.
7. News and execution evidence availability.
8. Source-to-task dependency matrix.
9. Estimated licensing/storage/compute costs.
10. Explicit accepted, restricted, deferred and rejected sources.
11. Unresolved risks and evidence gaps.
12. Reproducible retrieval/provenance plan.

Do not declare a source feasible based only on marketing descriptions or a small attractive sample.

## 15. Promotion gate

A source may be admitted to a later pipeline only when:
- rights are documented for the exact intended use;
- identity and temporal semantics are understood;
- task-specific coverage is sufficient;
- critical data quality issues are measurable and controlled;
- transformations preserve provenance;
- independent-source differences are not hidden;
- limitations are represented in schemas;
- source-to-task value is justified;
- Stage 5 compatibility has been reviewed at the authorized milestone;
- the user separately approves source inspection/acquisition and the next phase.

## 16. Explicit non-decisions

This document does not select a vendor, approve the uploaded archive, set a historical date range, define a required tick count, establish a broker of record, approve a license, or authorize downloads. Those choices require a separate evidence-based feasibility review and explicit approval.
