# Canonical Dataset Contract and Normalization Engine

## Status and boundary

This is a versioned serialization/normalization contract for a future pipeline. It does not authorize collection, provider connections, use of real market data, dataset release, or model training. The implementation is offline and acts only on one explicitly named input file and one explicit mapping file. Tests use synthetic fixtures.

This contract operationalizes the existing logical data model; it does not supersede the Stage 5 audit, source-admission decisions, or AURORA QUANT. Changes to field meaning require a schema-version change and a reviewed migration.

## Canonical OHLCV v1.0.0

- Identity: `instrument_id` is a stable internal instrument identity; `symbol` is the source/display symbol; `venue` and `provider` remain separate dimensions.
- Time: `event_time` is the market event/bar timestamp; `available_at` is when the value became available; `recorded_at` is when this pipeline/source record was recorded. All serialize as UTC RFC3339/ISO-8601 with a trailing `Z`; source timestamps must carry an explicit offset. No naive-time timezone is guessed.
- Granularity: timeframe is a positive integer plus unit, e.g. `1m`, `5m`, `1h`, `1d`, `1w`. Session calendars and bar-boundary conventions are source metadata and are not inferred here.
- Prices: OHLC are positive finite decimal strings. Strings are intentional: JSON binary floating-point numbers are not used as the canonical representation. OHLC invariants are checked exactly with Decimal.
- Volume: optional, finite, non-negative decimal string. If supplied, its unit must be explicit when known; no conversion between contracts, lots, base units, or quote units is guessed.
- Price basis: required enum `bid|ask|mid|last|mark|index|unknown`. Unknown is explicit, not an inferred default.
- Provenance: source artifact and record IDs are required. The original parsed source record and its SHA-256 are retained in each normalized record. This is a source-record payload preservation mechanism, not a substitute for immutable raw artifact storage and artifact-level manifests.

## Explicit mapping

The mapping JSON maps canonical target names to exact source column/key names. No fuzzy matching, aliases, case folding, default symbol, inferred price side, inferred timezone, or guessed unit conversion is performed. All required targets must be mapped. Optional `volume` and `volume_unit` can be mapped explicitly. Unknown mapping targets fail closed.

Example mapping (adapt names only after inspecting the source format):

```json
{
  "instrument_id": "instrument_id",
  "venue": "venue",
  "provider": "provider",
  "symbol": "symbol",
  "timeframe": "timeframe",
  "event_time": "event_time",
  "available_at": "available_at",
  "recorded_at": "recorded_at",
  "open": "open",
  "high": "high",
  "low": "low",
  "close": "close",
  "price_basis": "price_basis",
  "source_artifact_id": "source_artifact_id",
  "source_record_id": "source_record_id",
  "volume": "volume",
  "volume_unit": "volume_unit"
}
```

## Determinism and identity

Input row order is preserved. The engine does not sort, aggregate, deduplicate, resample, fill missing bars, interpolate, repair OHLC, remove outliers, or reconcile providers. It rejects duplicate observation identities across provider, venue, instrument, timeframe, event time, and price basis rather than silently merging feeds. Different source record IDs do not make the same observation identity distinct.

Output JSONL uses stable key ordering, compact UTF-8 JSON, one record per line, and a newline terminator. Decimal formatting is normalized without binary float conversion. The raw parsed payload is embedded and hashed. Exact reproducibility assumes the same input bytes, mapping bytes/semantics, and implementation version.

## Safety

- No network, API, broker, MT5, or provider code.
- No directory scanning; one explicit input only.
- Source file and mapping are read-only.
- Output must be a distinct path; existing outputs are never overwritten. Exclusive file creation guards against overwrite races.
- Output parent must already exist.
- No data is automatically admitted to training or a release.
- The CLI emits a deterministic summary and exits non-zero on invalid input.

## CLI

`python tools/dataset_normalizer.py --input source.csv --mapping mapping.json --output canonical.jsonl`

or use `.jsonl` / `.ndjson` input. The mapping file is required for every source.

## Known limitations / next gates

This v1 tool does not define provider-specific bar-open versus bar-close conventions, instrument contract multipliers, tick-size/precision rules, volume economics, corporate actions, futures rolls, FX sessions, DST calendars, corrections/revisions, quote/tick normalization, or multi-source reconciliation. Those require source-specific, reviewed metadata and must not be inferred. The embedded raw payload may increase output size; a production pipeline should reference immutable raw artifacts by content hash while retaining source-record lineage.

The tool does not establish licensing, source authenticity, point-in-time causal correctness, completeness, or training suitability. Quality audit and provenance validation remain separate required gates. No real market data or model training is included in this stage.
