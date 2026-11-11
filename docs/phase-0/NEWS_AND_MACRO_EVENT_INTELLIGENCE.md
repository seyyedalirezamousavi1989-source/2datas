# Point-in-Time Macro News and Event Intelligence — Phase 0

## 1. Purpose and status

Define a rigorous contract for optional macroeconomic/news context in an XAUUSD research dataset.

**Design only:** no news archive, economic calendar, market series, or source file has been inspected or acquired. No event labels, impact labels, features, or datasets have been generated. This document does not authorize collection, processing, licensing, implementation, or model training.

The goal is to teach the model what information was actually public at a decision time, what changed relative to expectations, how market prices subsequently behaved, and what remains uncertain. It must not teach hindsight narratives as if they were known before the event.

## 2. Core separation: fact, expectation, interpretation, reaction

Keep four information layers separate:
1. **Published fact:** the value/text released by an identifiable publisher, with publication time and revision history.
2. **Pre-release expectation:** the consensus, survey, market-implied expectation, or forecast snapshot available before publication, with its own timestamp and methodology.
3. **Model interpretation:** a derived description such as positive/negative/mixed surprise or potential relevance to gold. It is not a source fact.
4. **Observed market reaction:** subsequent USD, rates, gold, volatility, spread, and liquidity behavior measured from market data after the information became available.

Never collapse these layers into a single field such as news_impact=bullish_gold. The actual reaction may contradict a simple macro narrative.

## 3. Point-in-time publication contract

Every news or economic event record must preserve, where applicable:
- stable event_id and source-specific event identifier;
- publisher/provider and original source reference;
- event title/name and country/currency/topic taxonomy;
- scheduled release time as last known before release;
- actual publication timestamp;
- timestamp precision, timezone and source clock semantics;
- ingestion/availability timestamp as observed by the system;
- original published value/text;
- unit, scale, seasonal adjustment and period represented;
- previous value as known before release;
- consensus/forecast value and the timestamp/provider that supplied it;
- revised previous values and the times those revisions became public;
- correction, cancellation, delay or embargo status;
- source revision/version and immutable raw provenance.

For a decision at time t, a field is eligible only if its actual public availability and system availability are no later than the decision cutoff, according to the declared policy. A later correction must create a new version; it must not rewrite the earlier information set.

Scheduled time is not publication time. A calendar schedule can change, and a release may be delayed. Do not make an event available to the model merely because its expected schedule has passed.

## 4. Event taxonomy

Use a compact hierarchy with stable IDs rather than an uncontrolled collection of synonymous tags.

### Monetary policy
- central-bank policy rate decisions;
- policy statements and meeting minutes;
- press conferences and speeches;
- forward guidance and policy projections;
- balance-sheet / liquidity announcements.

### Inflation
- CPI and core CPI;
- PCE and core PCE;
- producer prices and inflation expectations, where source quality supports them.

### Labor and activity
- payrolls, unemployment, participation and wages;
- jobless claims;
- GDP, retail sales, industrial production and surveys.

### Rates, currency and sovereign risk
- Treasury yields and curve changes;
- real yields and breakeven inflation, if reliably sourced;
- USD index or explicitly defined currency basket;
- sovereign/credit/geopolitical risk events where a licensed, timestamped source exists.

### Gold-specific context
- central-bank gold demand and official holdings;
- ETF flows and holdings;
- mine supply, recycling and demand statistics;
- exchange inventory and futures positioning, subject to reporting delay and publication semantics.

Taxonomy inclusion does not imply a feature is approved. Each family must pass source, point-in-time and incremental-value gates.

## 5. Release values and surprise semantics

For numerical releases, preserve raw published values and units. A derived surprise may be computed only when the pre-release expectation is genuinely point-in-time and comparable.

A basic numeric surprise is actual minus expectation. But this raw difference is not universally comparable. The registry must define sign convention and whether higher is economically positive/negative/ambiguous; units and scale; seasonal adjustment and period alignment; expectation source and snapshot cutoff; standardization method, if any, fitted without test leakage; missing-consensus behavior; and revisions and whether surprise is recomputed for a later information snapshot.

Do not infer consensus from post-release commentary. Do not use revised historical values as if they were the original release. Do not assume that a higher CPI or NFP value has a fixed directional effect on gold; the market response depends on expectations, policy regime, positioning, yields, USD, and other simultaneous information.

For text releases (statements, minutes, speeches), preserve original text and publication metadata where licensing permits. Any summaries, extracted stance, topic, or hawkish/dovish interpretation must be separately versioned, attributed to its method/model, and treated as an interpretation—not a fact.

## 6. Market reaction is a separate event study

A market reaction record references the public event and the independently sourced market observations used to measure reaction.

Potential response variables include XAUUSD returns and ranges at declared horizons; USD basket/index movement; nominal and real yield changes where available; volatility and spread changes; and liquidity or volume proxies only with clear source semantics.

For each response window define baseline cutoff and eligible pre-event observations; start/end offsets from actual publication time; price/quote basis and market session; overlapping news/events and confounder policy; missing/stale market data treatment; source and calculation versions.

Do not label an observed move as caused by one release merely because it occurred after the release. Use wording such as post_event_observed_response unless a defensible identification design supports causal attribution. Simultaneous releases, leaks, speeches, geopolitical events and market positioning can confound simple event studies.

## 7. Event risk and trading policy

A calendar event's risk category is not a forecast of price direction.

Potential policy context includes time until a scheduled high-impact event; event status (scheduled, delayed, released, cancelled, unknown); uncertainty around release time; observed spread/volatility expansion; and whether a setup is prohibited, reduced, delayed or merely flagged by a separately approved policy.

Keep policy decisions separate from source facts and forecasts. If AURORA QUANT has deterministic event-risk restrictions, the dataset may teach interpretation of their outputs but must not invent or override them. The exact policy must be verified against the approved system; no such rules are assumed here.

## 8. News and market data alignment

Use UTC internally while preserving original timezone and timestamp semantics. Handle daylight-saving changes, publication-time precision, late arrivals, vendor ingestion delay, corrections and market closures.

A decision snapshot should distinguish event scheduled but not released; release time reached but publication not verified; release published but not yet ingested; release available to the system; and post-release correction/revision available later.

If exact publication time cannot be established, mark the event timing uncertain and exclude it from narrow event windows or point-in-time model inputs as required by the task.

## 9. Source quality, provenance and licensing

Before any provider is selected, assess official publisher vs secondary aggregator; original publication timestamp and revision history; historical archive completeness and point-in-time snapshots; consensus methodology and contributor coverage; timestamp precision, timezone and correction policy; API/export reliability, missingness and outage history; redistribution, storage, derived-data and model-training rights; attribution requirements, retention limits and cost; and coverage over the intended historical period.

Official sources are preferred for release facts where practical, but official publication does not automatically provide historical point-in-time consensus or redistribution/training rights. A free calendar feed is not automatically a complete, licensed training archive.

No provider or license is approved by this document.

## 10. News feature admission and redundancy

Do not create dozens of overlapping event flags or narrative summaries.

A candidate feature must state its exact claim and consumer task; original source and availability time; whether it is raw fact, expectation, derived surprise, text interpretation, or market reaction; definition and version; missingness and uncertainty behavior; incremental value over market-only and simpler event-time baselines; and cost, license and maintenance burden.

Prefer a canonical event object referenced by tasks over copied news text in every training example. Preserve the original source and its versions separately from compact task-specific interpretation.

## 11. Evaluation protocol

Evaluate the news modality with controlled chronological comparisons:
1. market-only baseline;
2. event-time/calendar-only baseline;
3. numerical release facts and point-in-time surprise;
4. text-derived interpretation, if licensed and reliable;
5. combined news + market context.

Use identical decision timestamps, splits, target definitions and model capacity where practical. Report incremental performance and uncertainty, not only standalone correlations.

Stratify carefully by event family, policy regime, session, volatility, source coverage and overlapping-event status. Avoid claiming broad value from a small number of exceptional releases.

For event studies, report the distribution and confidence intervals of post-event responses; distinguish descriptive association from causal effect. For forecast tasks, use the target-appropriate calibration and loss metrics from the forecast specification.

## 12. Leakage and failure cases

Explicitly test using a revised previous value before its revision timestamp; using a consensus snapshot updated after release; scheduled time substituted for actual publication time; delayed or cancelled release treated as published; news headline ingested after decision cutoff; article updated after original publication; text summary generated using later market reaction; future market prices included in a news-impact label; overlapping releases attributed to one event; timezone/DST offset errors; publication time rounded too coarsely; leaked embargoed information; and source licensing or retention restrictions ignored.

Any point-in-time failure blocks use of the affected record/field for that decision snapshot.

## 13. Promotion gate

News intelligence is eligible for later inclusion only when the downstream task and expected benefit are explicit; source archives and point-in-time versions are available; publication and ingestion times are reliable; historical expectations are demonstrably pre-release; corrections and revisions are preserved; licensing permits the intended storage and model use; market reaction is not mislabeled as causal impact; incremental value over market-only baselines is testable; sample size and event coverage support honest uncertainty; Stage 5 compatibility and source feasibility are reviewed; and the user separately approves source inspection/acquisition and the next phase.

## 14. Explicit non-decisions

This document does not choose a news/calendar vendor, approve a license, define a final event taxonomy, select a surprise normalization, specify event windows, approve text embeddings/sentiment models, or authorize any collection, processing, labeling, implementation or training.

Those decisions require source feasibility evidence and separate approval.