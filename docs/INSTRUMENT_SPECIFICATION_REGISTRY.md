# Instrument specification registry

## Purpose

The registry records how each broker/server's source symbol is defined over time. It is reference metadata for interpreting prices, spread and later deterministic calculations. It is not a training label and does not make an unverified source eligible for training.

## Source-specific and effective-dated

Add an optional `instrument_specs` object to the broker sidecar. Keys are exact source symbols from the export (for example `GOLD`, `XAUUSD`, or a broker suffix). Each value is either one specification object or a list of historical specifications.

Each record requires:

- `canonical_instrument`: the canonical dataset identity, explicitly mapped.
- `digits`, `point_size`, `tick_size`, `contract_size`.
- `price_currency` and `profit_currency`.
- `spread_unit`: `points`, `price`, or `unknown`.
- `volume_semantics`: `tick_count`, `real_volume`, or `unknown`.
- `effective_from`: inclusive ISO date.
- `effective_to`: exclusive ISO date; omit only when the record remains valid through the latest known date.
- `evidence`: exact document/source and revision, not a guess.

Optional `tick_value` must be accompanied by `tick_value_currency`. Tick value is not a universal instrument constant: it can depend on account deposit currency, broker calculation mode, conversion rates and contract details. The registry therefore does not require or infer it. A static tick value must never be used for account risk calculations without validating its calculation context.

## Point-in-time application to normalized bars

During normalization, each bar is matched using its exact source symbol and the calendar date written in the broker's source timestamp. Effective dates are interpreted as broker-server-local calendar dates; they are not converted to UTC before contract lookup. This prevents a UTC date boundary from accidentally selecting the wrong contract revision. Each normalized row receives `instrument_spec_status`, a deterministic `instrument_spec_id`, the effective-date bounds and the matched contract attributes. Missing or out-of-range metadata remains blank with an explicit status; it is never forward-filled or guessed.

The raw export spread is retained as `spread_raw`. `spread_points` is populated only when the matching specification declares `spread_unit=points`; `spread_price` is calculated as raw spread × point size. When the unit is `price`, `spread_price` is the raw value and `spread_points` remains blank. When the unit is `unknown` or no specification matches, both derived fields remain blank. This avoids silently treating a broker's raw spread as points.

`tick_value` is retained as source reference metadata only. It is not sufficient for position sizing or account-risk calculations unless its currency, account conversion context, calculation mode and validity are independently established.

## Historical validity rules

- Histories for the same source symbol must not overlap.
- The spec audit compares the observed date range of the archive with the effective-dated records and reports uncovered dates.
- `effective_to` is exclusive, avoiding ambiguity at changeover boundaries.
- If the provider changed digits, point size, tick size, contract size, profit currency, or volume/spread semantics, create a new effective-dated record.
- Never copy Alpari values to another broker, even when both call the instrument XAUUSD.
- Missing specifications remain missing; symbol names and OHLC values are not evidence of contract metadata.

## Audit

Run:

```bash
2datas spec-audit path/to/export.zip --output reports/instrument_spec_audit.json
```

The normalizer also embeds the same coverage audit in `manifest.json`. Normalized bar schema `market-bars-0.4.0` carries the point-in-time specification match and unit-safe spread fields. A complete registry means the observed source symbols and dates are covered by supplied records; it does not independently certify that the cited broker documents are authentic or that the export license permits research use.

## Explicitly excluded

No account number, account owner, login, password, or Demo/Real account type is collected. Such identity is irrelevant to the source instrument's market-data specification.
