# Read-Only Market Data Acquisition Engine — Offline Foundation

## Safety boundary
This increment adds provider-neutral adapter metadata and an offline simulation harness only. It does not implement a live broker/provider client. No sockets, HTTP clients, credentials, terminal integrations, market-data file readers, raw artifact writers, dataset writers, or training hooks are present. The deterministic synthetic adapter operates only on in-memory fixtures.

The mode is hard-limited to `offline_fixture_only`. The existing planner still emits `planned_only`; authorization, network access, market-data reads and dataset writes remain false. This is not authorization for a future live run.

## Contracts and orchestration
The adapter descriptor schema records provider identity, OHLCV capability, timezone and bar timestamp semantics, bar boundary, open/incomplete-bar handling, pagination limits/cursor-loop policy and declarative retry configuration. Network capability is constrained to false.

The simulation provides canonical-JSON SHA-256 request fingerprints, run-scoped idempotency keys, bounded pagination, repeated-cursor rejection, UTC conversion (naive timestamps require an explicit IANA timezone), and error classes for transient, rate-limited, authentication-required, unsupported and permanent failures. Retry settings are descriptive only; no retry/network operation occurs.

Open and incomplete synthetic bars are retained and flagged. OHLC checks are observational; records are never repaired or discarded. No source ranking or winner selection is performed.

## Run manifest
The manifest schema records plan and adapter identity, fingerprint, pagination/record counts, warnings, and hard-false execution flags. It describes a simulation, not provider access or a dataset artifact.

## Validation
Run `python -m unittest discover -s tests -v`. Tests use synthetic fixtures only and cover determinism, timezone conversion, cursor-loop prevention, page bounds, error classification, incomplete-bar preservation and disabled execution.

## Deferred before any live acquisition
A separate reviewed and explicitly authorized increment must address provider licensing/terms, secret-manager integration (never credentials in registry/config), real timeout/retry/backoff and rate-limit headers, pagination resume semantics, daylight-saving ambiguity, closed-bar confirmation, corrections/revisions, immutable raw artifact storage, checksums and a kill switch. None is enabled here.
