# Forex Tab Market-Data Access Contract

## Purpose

AURORA QUANT is intended to obtain current or historical market data through the **Forex tab in the LocalChat Agent UI**. The Forex tab is the application's data-acquisition and delivery boundary; the language model is the analysis and reasoning component.

## Runtime status

This is a future integration contract, not a claim that the Forex tab connector is already implemented or exposed to the model. The model must only call a data capability when the application actually supplies it in the runtime. If it is absent, the model must say that retrieval is not currently available and may ask the user to provide data. It must never fabricate a live quote or pretend a broker request succeeded.

## Request contract

A data request should specify:
- instrument/symbol (for example, XAUUSD);
- provider/broker/feed identity or an explicit provider-selection policy;
- timeframe(s), each stated explicitly;
- start/end timestamps or a clearly defined latest-data request;
- required fields (OHLC, tick volume, spread, bid/ask or price basis, and any available quote metadata);
- requested freshness and whether completed or partial bars are allowed;
- source timezone and bar timestamp convention when known.

Request only the data needed for the current task. Never ask the model to handle broker passwords, API secrets, or account credentials in conversation text.

## Response contract

The Agent UI should return a structured payload with:
- request ID and retrieval status;
- instrument mapping and provider/source revision;
- timeframe and exact requested/returned range;
- timestamp timezone, bar-open/bar-close convention, interval start/end and availability time;
- price basis and OHLC units/precision;
- volume and spread semantics;
- completeness/partial-bar status, pagination and coverage metadata;
- immutable raw artifact reference and SHA-256 where applicable;
- explicit errors, stale-data warnings, and gaps.

The application—not the model—owns provider credentials, network access, retry/rate-limit behavior, and data persistence.

## Model behavior

1. Use only payloads actually returned by the Forex tab or explicitly supplied by the user.
2. Before analysis, inspect provenance, timestamps, source revision, price basis, completeness, ordering, duplicates, OHLC invariants, and field semantics.
3. Keep providers, price bases, instruments, and timeframes distinct until a documented reconciliation step authorizes comparison.
4. For multi-timeframe analysis, use only bars and derived events available at the decision cutoff. Never use an unfinished higher-timeframe candle as a completed candle.
5. If essential metadata is missing, preserve the uncertainty and request clarification; do not guess a timezone or silently convert timestamps.
6. Distinguish historical data from current/live data and report the data's as-of time.
7. Do not claim that the future integration exists until the Agent runtime actually exposes it.

## Training implication

SFT examples may teach the model this intended interaction protocol. They do not implement the UI, provider adapters, or data transport. The future LocalChat Agent integration must expose a typed tool/interface and return validated structured data.
