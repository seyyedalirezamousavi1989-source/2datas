# AURORA QUANT dataset

## Learning corpus

- `seed/identity.jsonl`: assistant identity, project context, and data-access behavior.
- `seed/forex_knowledge.jsonl`: foundational Forex, market structure, quantitative, risk, and analysis knowledge.
- `seed/strategy_selection.jsonl`: 20 broker- and timeframe-agnostic examples teaching adaptive regime classification, strategy comparison, multi-timeframe reasoning, no-trade decisions, uncertainty, and post-trade review.
- `market_data/xauusd_source_manifest.json`: fingerprint and inventory of the supplied six-timeframe XAUUSD archive.
- `reports/xauusd_source_quality_report.json`: structural audit summary of that archive.

## Intended behavior

The model receives market data from the LocalChat agent. The model is not responsible for connecting to brokers or acquiring files. It should analyze the actual supplied series regardless of provider or timeframe labels, provided the agent supplies enough information to interpret the observations. It should identify the market regime, compare relevant strategy families, choose the best-supported approach conditionally, explain alternatives and invalidation, and explicitly return no-trade when evidence is weak.

The strategy corpus is authored instructional SFT material, not evidence that any strategy is profitable. It contains no real market-derived labels or trade outcomes. The uploaded XAUUSD archive has been inventoried but has not yet been converted into market-derived examples. Do not imply otherwise.

## Data policy

Do not hard-code a particular broker, symbol suffix, or timeframe. Do not silently reinterpret missing fields or timestamps. If a missing property changes the analysis materially, state the limitation. Keep source acquisition and data delivery in the host agent; keep market interpretation and strategy reasoning in AURORA QUANT.
