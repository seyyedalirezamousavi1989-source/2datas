# Broker-Neutral Market Data Ingestion Standard

## Objective

AURORA QUANT must be able to reason over market data from different brokers, liquidity providers, terminals, vendors, and export formats without learning a separate candle format for each source. The canonical dataset is provider-neutral; source identity and source-specific meaning remain attached to every observation.

This is the next implementation gate after the XAUUSD archive audit. It establishes a **source-profile + adapter + canonical-record** architecture. It is not a claim that every broker is already connected, nor does one generic adapter magically support every broker API.

## Core architecture

`Forex Tab request -> provider adapter -> immutable raw response/artifact -> source-profile validation -> canonical normalization -> quality/provenance checks -> point-in-time alignment -> analysis payload for AURORA QUANT`

The UI/runtime owns credentials, connections, provider-specific pagination, retries, rate limits, caching, and persistence. AURORA QUANT requests typed data and analyzes validated results; it must not receive secrets.

### 1. Provider adapter

Each provider/feed has a small adapter implementing the same application interface. An adapter translates provider-specific requests and responses; it does not redefine canonical market semantics.

Initial adapter families:
- MT5 terminal/export (including broker-specific symbol suffixes and contract specifications);
- broker REST/WebSocket APIs;
- vendor market-data APIs;
- CSV/TSV/JSON exports;
- custom adapters for sources with non-standard sessions or fields.

A provider is supported only after its adapter passes the shared contract tests. Unsupported providers must fail explicitly rather than return plausible but semantically wrong data.

### 2. Versioned provider profile

Every feed must have a versioned profile conforming to `schemas/ingestion/provider-profile.schema.json`. Profiles explicitly declare:
- provider, feed/server identity, adapter kind, and exact provider-symbol to canonical-instrument mappings;
- supported timeframes, including seconds/minutes/hours/days/weeks/months where the provider supports them;
- source timezone (IANA zone, fixed offset, UTC, or unknown), timestamp precision, and whether timestamps denote bar-open or bar-close;
- DST ambiguity policy, bar boundaries, trading-session calendar, partial-bar policy, and correction/revision behavior;
- price basis, quote currency, volume meaning/unit, spread meaning/unit;
- exact source field names and evidence/limitations.

No fuzzy symbol matching, silent aliases, guessed timezone, guessed price basis, or guessed unit conversion is permitted. Unknown is a valid recorded state but blocks operations that require the missing meaning.

### 3. Canonical record and source lineage

All supported sources project into the canonical OHLCV record while retaining:
- provider/feed, venue, canonical instrument and exact source symbol;
- timeframe and source revision;
- original source timestamp, timezone, timestamp convention, and normalized UTC interval;
- event/availability/receive/ingestion times as separate clocks;
- OHLC decimal values, price basis, volume/spread semantics, and completion state;
- raw artifact reference/hash and source-record identity.

Do not collapse broker feeds just because they share a display symbol. XAUUSD from two brokers may differ in symbol mapping, contract specification, session boundaries, spread, price basis, and candle construction.

### 4. Timeframe universality

The interface accepts a list of requested timeframes rather than a hard-coded list. It must distinguish:
- **native timeframe:** returned directly by the provider;
- **derived timeframe:** built from lower-timeframe data only when the aggregation rule, session calendar, price basis, and completeness are valid;
- **unsupported timeframe:** rejected with the provider's supported list.

Never synthesize a missing timeframe silently. Aggregation must preserve OHLC rules, source lineage, session boundaries, and incomplete-bar state. Monthly bars are calendar/session intervals, not a fixed number of seconds. Daily/weekly/monthly bars must use the provider's verified trading calendar and timezone; fixed UTC durations are not a substitute.

### 5. Timezone and DST safety

Preserve the exact source timestamp and timezone metadata. Convert to UTC only after the profile establishes an unambiguous timezone interpretation. For local wall-clock timestamps that fall into a repeated DST hour, require provider sequence/fold evidence or reject the affected records. Reject nonexistent local times. Never infer a historical timezone from the computer's current timezone or from the broker's current server setting.

A provider profile may be marked unknown during discovery, but data requiring UTC alignment, cross-timeframe joins, or causal availability must remain blocked until resolved.

### 6. Data quality and missingness

Validate, without silently repairing:
- schema and field mapping;
- monotonicity, duplicate identities, gaps, OHLC invariants, decimal precision;
- completed vs partial candles and late/corrected bars;
- quote side/price basis, volume units, spread units;
- requested vs returned range, pagination completeness, freshness and staleness;
- instrument specification and trading-session calendar.

A gap is not automatically a missing candle: weekends, holidays, session breaks, halts, and provider outages must be distinguished using the source calendar and retrieval evidence. Preserve raw values and report diagnostics; repairs/resampling require separate versioned transformations.

### 7. Forex Tab request/response

A request should include:
- canonical instrument plus optional exact provider symbol;
- provider/feed selection (or an explicit policy allowing multiple feeds);
- one or more timeframes;
- historical range or latest/current request;
- fields and quote basis;
- completed-only vs partial-bar permission;
- freshness requirement and page/record limits.

The response must return one independently identifiable dataset partition per provider/feed, instrument, timeframe, and price basis, plus request ID, source-profile version, as-of time, returned coverage, raw artifact references, hashes, quality report, and explicit unsupported/error states.

The model may compare feeds only through a named reconciliation procedure. It must not average or merge broker candles by default.

## XAUUSD archive disposition

The uploaded six-timeframe archive remains a source-discovery fixture, not a canonical dataset. It has no embedded verified provider identity, source timezone, bar-open/bar-close declaration, or price-basis declaration. The user's recollection that it may be an Alpari MT5 export is useful investigative evidence but is not yet authoritative provenance. The profile for this archive must remain provisional until the exact MT5 server timezone at export time, timestamp convention, and price basis are confirmed.

Do not assume the current Alpari server timezone was constant throughout the six-year history. If the broker changed its server offset or DST policy, a single fixed offset is not enough; use historical provider documentation or terminal evidence.

## Implementation sequence

1. Freeze this provider-neutral profile schema and common adapter interface.
2. Implement profile-driven CSV/TSV/JSONL ingestion with explicit mappings and timezone/DST handling.
3. Add MT5-specific export adapter and tests for broker symbol suffixes, volume/spread semantics, and bar-open/bar-close behavior.
4. Add provider adapters incrementally; each adapter must pass the same conformance suite.
5. Add calendar-aware native/derived timeframe handling and point-in-time alignment.
6. Only after source profile verification, reprocess the Alpari-like XAUUSD archive and generate market-derived learning examples under a separately approved dataset-build gate.

## Non-goals and safety boundaries

This contract does not connect to a broker, request credentials, place orders, alter account state, or authorize live trading. It does not claim that every provider has an available API or redistribution rights. It does not create labels, signals, strategy performance claims, or model training data. Broker support is adapter-by-adapter and subject to API availability, source terms, and quality evidence.
