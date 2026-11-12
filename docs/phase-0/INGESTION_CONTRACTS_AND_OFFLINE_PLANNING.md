# Ingestion Contracts and Offline Planning

## Purpose

This stage bridges the source registry/admission gate and a future controlled acquisition implementation. It validates a requested OHLCV collection specification against an approved source revision and an admitted research-use decision, then emits a declarative readiness plan.

## Strict authorization boundary

This implementation is planning-only. It does not connect to a broker, exchange, vendor, API, website or terminal. It does not inspect source data files, download or parse market records, generate candles, normalize observations, write datasets, or train models. Execution flags for acquisition authorization, network access, market-data reading and dataset writing are hard-coded to false. There is no CLI switch to enable them.

No real market data is read or processed. Tests use synthetic metadata fixtures only. Existing archive files, Stage 5 and AURORA QUANT are untouched. A future acquisition stage requires explicit authorization and a separately reviewed implementation.

## Admission and planning checks

A plan requires a schema-valid registry record with approved lifecycle status; exact source ID and revision agreement across request, registry and admission decision; an admitted decision specifically for research use; unexpired source approval and decision revalidation date; OHLCV modality; exactly one canonical instrument mapping; a supported timeframe; and timezone-aware start/end timestamps with start before end.

The planner does not create training examples or assert training eligibility. Training permission remains a separate gate.

## Output contract

The plan schema records source revision, admission decision, instrument/provider mapping, timeframe, requested range and canonical output contract. It specifies JSONL records conforming to the canonical OHLCV schema and requires raw-source lineage preservation.

The output is metadata only. It is written to a new path using exclusive-create semantics; existing files and symlinks are rejected. The output parent directory must already exist.

## CLI

python tools/ingestion_planner.py plan --registry registry.json --decision admitted-research-decision.json --request request.json --output plans/plan.json

The request JSON contains plan_id, created_at, source_id, source_revision, instrument_id, timeframe, start and end. All timestamps must include an explicit timezone.

Exit code 0 means a metadata plan was validated and written. It does not mean data was acquired or a dataset was built. Exit code 2 indicates invalid metadata, policy mismatch or I/O failure.

## Limitations and next gate

This stage does not validate actual provider coverage, historical availability, bar completeness, rate limits, pagination, correction semantics, or market-data quality. Evidence references remain metadata and are not fetched or authenticated. Before real acquisition, the project needs explicit user authorization, source-specific technical/legal review, a read-only acquisition adapter, raw immutable artifact handling, rate-limit/retry policy, and a synthetic end-to-end integration test. Only then can a separately authorized real-data run be considered.
