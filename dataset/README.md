# AURORA QUANT dataset

## Learning corpus

- `seed/identity.jsonl`: assistant identity, project context, and data-access behavior.
- `seed/forex_knowledge.jsonl`: foundational Forex, market structure, quantitative, risk, and analysis knowledge.
- `seed/strategy_selection.jsonl`: 20 broker- and timeframe-agnostic strategy-selection starter examples.
- `seed/advanced_market_reasoning.jsonl`: 32 detailed scenario-response examples covering regime transitions, breakouts, pullbacks, momentum, volatility, multi-timeframe conflicts, structure, indicators, macro context, risk, no-trade, forecasting, data defects, execution constraints, overfitting, calibration, and post-trade review.
- `seed/adversarial_market_reasoning.jsonl`: 46 contrastive cases designed to resist leading prompts, indicator double-counting, late entries, look-ahead leakage, selection bias, poor calibration, data conflicts, execution-policy overrides, and hindsight rewriting.
- `market_data/xauusd_source_manifest.json`: fingerprint and inventory of the supplied six-timeframe XAUUSD archive.
- `reports/xauusd_source_quality_report.json`: structural audit summary of that archive.

## Intended behavior

The model receives market data from the LocalChat agent. The model is not responsible for connecting to brokers or acquiring files. It should analyze the actual supplied series regardless of provider or timeframe labels, provided the agent supplies enough information to interpret the observations. It should identify the market regime, compare relevant strategy families, choose the best-supported approach conditionally, explain alternatives and invalidation, and explicitly return no-trade when evidence is weak.

The strategy and advanced-reasoning corpora are authored instructional SFT material, not evidence that any strategy is profitable. The advanced and adversarial examples are deliberately hypothetical teaching scenarios, not real market observations or verified trade outcomes. The adversarial set emphasizes counterexamples, uncertainty, causal availability, dataset leakage, and disciplined refusal to force a trade. It contains no real market-derived labels or trade outcomes. The uploaded XAUUSD archive has been inventoried but has not yet been converted into market-derived examples. Do not imply otherwise.

## Data policy

Do not hard-code a particular broker, symbol suffix, or timeframe. Do not silently reinterpret missing fields or timestamps. If a missing property changes the analysis materially, state the limitation. Keep source acquisition and data delivery in the host agent; keep market interpretation and strategy reasoning in AURORA QUANT.
