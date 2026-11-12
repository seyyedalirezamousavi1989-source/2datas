# Data Source Registry and Admission Gate

## Purpose and boundary

This stage adds a versioned registry for provider/feed metadata and an offline, deterministic gate for one explicitly named target use. It implements the source-registry layer described in the architecture and remains separate from normalization, quality auditing and cross-source reconciliation.

This does not verify providers, provide legal advice, connect to brokers/APIs, authorize collection, or authorize model training. Tests use synthetic records only. No real market data is included. Stage 5 and AURORA QUANT remain unchanged and out of scope.

## Registry contract

Each source has an immutable source_id and positive revision. Material changes to provider mapping, license, timestamp convention or feed properties require a new revision. Records include provider/feed identity, source type, modalities, asset classes, canonical instrument-to-provider symbol mappings, supported timeframes, price basis, volume meaning/unit, timezone, timestamp/bar-boundary conventions, availability claims and evidence class, separate usage permissions, lifecycle status and provenance.

Permissions are independent for research, model_training, redistribution and commercial use, each recorded as allowed, prohibited or unknown. One permission never implies another. Evidence references and their verification labels are metadata only: this tool does not fetch or authenticate them. Source-reported and independently verified claims remain distinguishable.

Never store API keys, credentials, tokens, passwords, account identifiers or unnecessary personal data in registry records, logs or commits.

## Admission decisions

Each immutable decision records source ID and revision, timestamp, target use, decision, evidence references, individual checks, rationale, reviewer, policy version and revalidation date. The CLI refuses to overwrite an existing decision output. Re-evaluation creates a new decision artifact and never mutates the registry or historical decisions.

## Gate policy

- Only approved registry records can pass lifecycle checks. Draft, under-review, rejected, suspended and retired sources are rejected.
- Explicitly prohibited use is rejected. Unknown permission yields needs_review; unknown model-training permission can never be admitted.
- Timezone, timestamp semantics and bar boundary must be explicit; canonical instrument mappings must exist.
- Unknown price basis or volume semantics require review. Volume may be not_applicable only when explicitly declared.
- Evidence references must exist as metadata; no external resource is fetched or verified.
- Expired valid_until yields needs_review.
- Reconciliation agreement and provider popularity are not trust evidence or rankings.
- Research permission does not grant training, redistribution or commercial permission.

Downstream use must require an admitted decision for the exact source revision and target use, plus all other integrity, quality, provenance, causal and split gates.

## CLI

Validate: python tools/source_registry.py validate --registry registry.json

Evaluate: python tools/source_registry.py evaluate --registry registry.json --source-id SOURCE_ID --use model_training --reviewer-id REVIEWER --decision-output decisions/decision.json

The output parent must already exist. Existing files and symlinks are never overwritten. Explicit paths only; no directory scan, network, ingestion or real data processing. Exit code 0 means evaluation completed; the decision field independently states admitted, rejected or needs_review. Exit code 2 means invalid input or I/O failure.

## Validation and limitations

Schema validation uses JSON Schema Draft 2020-12. Semantic checks enforce unique source IDs, exact source resolution and fail-closed decisions. CI uses synthetic fixtures. The implementation does not prove legal rights, authenticity, source independence, latency, historical availability, completeness, instrument specifications or causal correctness. Human evidence review remains necessary. No live data ingestion or model training is implemented.
