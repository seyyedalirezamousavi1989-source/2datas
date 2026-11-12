# Broker and time normalization contract

## Non-negotiable principle

A broker label is not a timezone. A server timezone is not a bar timestamp convention. A valid multi-broker pipeline must preserve the raw timestamp and only produce canonical UTC timestamps when both the server clock and bar convention are supported by evidence.

## Resolution order

1. Explicit export metadata with provider documentation/version.
2. A versioned broker/server profile verified for the exact account server and historical period.
3. Explicit user-supplied IANA timezone plus interval-start/interval-end convention.
4. Otherwise retain source-local naive time and mark UTC unresolved. Do not infer by guessing.

A broker may operate multiple MT5 servers with different clocks or change DST policy. The source contract therefore records broker + exact server + profile version; the long-term registry must support effective date ranges. The current first implementation accepts one explicit profile per normalization run. DST ambiguous/nonexistent local times are quarantined. Historical timezone rules must be applied per date.

## Alpari

The supplied archive is identified by the user as Alpari, but the CSV files contain no exact MT5 server identity. Alpari help material describes GMT+2 in winter and GMT+3 during DST, with transitions on the last Sundays of March and October. The published MT5 server list includes `Alpari-MT5` and `Alpari-MT5-Demo`. The profile recognizes those exact server names; other server names remain unverified. `Europe/Helsinki` models the documented EET/EEST seasonal clock.

MT5 timeseries documentation defines bar time as the bar opening/period-start time, so the profile uses `interval_start`. This does not remove the need to confirm the exact server shown in the user terminal.

## Other brokers and timeframes

- Infer timeframe from explicit MT5 filename tokens where possible; otherwise require an explicit override or inspect verified export metadata.
- Accept any recognized MT5 timeframe, not only the six initial exports.
- Never assume all brokers use the same symbol name, point size, digits, contract size, sessions, spread units or real-volume semantics.
- Normalize timestamps to UTC only after resolving server timezone/fixed offset and bar start/end convention.
- Normalize bar intervals to half-open [start_utc, end_utc), keeping source timestamp and source convention alongside canonical fields.
- Store broker, exact server, symbol alias, profile ID, timezone, timestamp resolution status and evidence reference in the manifest and normalized rows.
- The current implementation does not yet support multiple historical profile epochs within one archive; add that before claiming automatic adaptation to a broker that changed server-clock policy.

## Alpari/MT5 evidence references

- [Alpari: trading server timezone](https://www.alparitrade.net/en/help/trading-platform/features-and-settings/What-time-zone-is-your-server-set-to/)
- [Alpari FAQ: MT5 server names and EET session clock](https://alpariworld.com/en/faq/)
- [MQL5: iTime returns the bar opening time](https://www.mql5.com/en/docs/series/itime)

## Profile admission evidence

A profile becomes verified only after:
- exact server identity is recorded;
- broker documentation or terminal metadata supports the timezone and DST policy;
- timestamp convention is checked against known market/session boundaries and adjacent timeframes;
- historical transitions are checked across winter/summer periods;
- no unexplained one-hour discontinuity remains;
- the profile is reviewed and versioned.

OHLC aggregation agreement is a useful consistency check, not proof of timezone or timestamp convention.


## Automatic source-specific configuration

A broker name is not sufficient to infer the server clock. For repeatable multi-broker ingestion, place a JSON sidecar next to each source archive:

- `archive.zip.broker.json`
- or `archive.broker.json`

The schema is `2datas-broker-clock-1`; it requires the exact server name, IANA timezone (preferred where DST applies) or a documented fixed UTC offset, and `interval_start` or `interval_end`. Optional fields are `broker_name` and `profile_id`. The normalizer and feature command discover the sidecar automatically and record its SHA-256. Use `--broker-config path/to/file.json` when the sidecar is stored elsewhere.

Do not mix a discovered/explicit sidecar with broker clock CLI overrides. If two sidecar candidates exist, configuration is rejected until the user selects one. If no valid source-specific configuration exists, UTC stays unresolved. This is deliberate: broker/server/timezone inference from OHLC values alone is not reliable.

The current sidecar contract applies one clock profile to one archive. If a single archive spans a broker server-clock policy change, split it at the verified effective date or extend the profile registry with dated epochs before normalization. Do not apply today's DST rule blindly to older exports.
