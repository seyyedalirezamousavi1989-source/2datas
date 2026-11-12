# AURORA QUANT dataset

## Current contents

- `seed/identity.jsonl`: assistant, creator, team, host-app and Forex-tab interaction identity examples.
- `seed/forex_knowledge.jsonl`: authored foundational Forex and market-analysis examples.
- `market_data/xauusd_source_manifest.json`: immutable fingerprint and inventory of the uploaded six-timeframe XAUUSD source archive.
- `reports/xauusd_source_quality_report.json`: read-only structural audit summary.

The raw `XAUUSD.zip` is not stored in this repository. Its SHA-256 and per-file hashes are recorded in the source manifest. The six CSVs contain 681,227 source rows across M5, M15, M30, H1, H4 and D1, from 2020-11-11 to 2026-11-10.

## Important status

The archive has been inventoried and structurally audited, but it has **not** yet been normalized or converted into market-derived SFT examples. Source timezone, bar timestamp convention, provider, and price basis remain unconfirmed. Do not guess these fields. See [the source audit](../docs/phase-0/XAUUSD_MULTI_TIMEFRAME_SOURCE_AUDIT.md).

The Forex tab in the LocalChat Agent UI is the planned future data acquisition interface. The model is trained to request data through that interface only when it is actually exposed at runtime. This dataset documentation does not implement the UI or provider connector. See [the Forex Tab access contract](../docs/phase-0/FOREX_TAB_DATA_ACCESS_CONTRACT.md).

See [the initial curated seed specification](../docs/phase-0/INITIAL_CURATED_SEED_DATASET.md) for the authored seed corpus limitations.
