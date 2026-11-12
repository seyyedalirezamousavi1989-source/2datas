# AURORA XAUUSD Dataset

A research-first project to build a compact, high-information, reproducible dataset for Forex domain learning and XAUUSD market understanding.

**Current status: initial authored seed corpus plus six-timeframe XAUUSD source inventory and read-only quality audit.** Market data has been inspected structurally, but not normalized, labeled, or converted into market-derived training samples. No model has been trained.

## Non-negotiable objective

Maximize verified information value per example—not row count, feature count, or document length. Every retained field and sample must support a defined analytical, forecasting, risk, execution, or evaluation purpose. Redundant, unverifiable, hindsight-contaminated, and decorative information is excluded.

## Scope and authority

- Instrument focus for future market-data work: XAUUSD; foundational knowledge covers Forex more broadly.
- Intended capability: Forex literacy, causal multi-timeframe market interpretation, technical/fundamental/quantitative analysis, strategy research, calibrated forecasting, scenario construction, risk-aware reasoning, and disciplined abstention.
- Identity target: AURORA QUANT, intended for the LocalChat application, based on Qwen3.5:4B for specialization.
- Creator: Alireza Mousavi (سید علیرضا موسوی); team identity: AURORA AI Research Group.
- Deterministic financial calculations and execution safeguards remain authoritative outside the learned model.
- This repository is independent of AURORA QUANT implementation and the separate Stage 5 dataset project.
- The uploaded XAUUSD.zip has been inspected read-only for file inventory and structural quality. Its raw archive remains outside Git; no normalization, feature generation, labeling, or training has occurred. Canonical processing is blocked pending source timezone and bar timestamp semantics.

## Initial seed corpus

- `dataset/seed/identity.jsonl`
- `dataset/seed/forex_knowledge.jsonl`
- `schemas/training/sft-record.schema.json`
- `tests/test_seed_dataset.py`
- [Initial curated seed dataset specification](docs/phase-0/INITIAL_CURATED_SEED_DATASET.md)
- [Limited authorization record](docs/phase-0/USER_AUTHORIZATION_2026-11-13.md)

These authored examples are a starter corpus, not a complete or production-approved training dataset. The six-timeframe market source inventory is recorded separately; no market-derived SFT samples or trade outcomes have been generated yet.

- [Broker-neutral ingestion standard](docs/phase-0/BROKER_NEUTRAL_MARKET_DATA_INGESTION.md) — common provider profile, adapter interface, arbitrary supported timeframes, timezone/DST policy, and source-quality gates.

## Uploaded XAUUSD source archive

- [Six-timeframe source manifest](dataset/market_data/xauusd_source_manifest.json) — file hashes, row counts, date ranges and unresolved source semantics.
- [Read-only quality report](dataset/reports/xauusd_source_quality_report.json) — 681,227 rows across M5, M15, M30, H1, H4 and D1.
- [Source audit](docs/phase-0/XAUUSD_MULTI_TIMEFRAME_SOURCE_AUDIT.md) — findings and normalization blockers.
- [Forex Tab data-access contract](docs/phase-0/FOREX_TAB_DATA_ACCESS_CONTRACT.md) — teaches the model to request data through the future LocalChat Agent Forex tab, without pretending the integration is already live.

## Phase 0 documents

- [Project charter](docs/phase-0/PROJECT_CHARTER.md) — goals, exclusions, acceptance gates.
- [Architecture](docs/phase-0/ARCHITECTURE.md) — data layers, task boundaries, causal contract.
- [Task catalog](docs/phase-0/TASK_CATALOG.md) — prioritized, non-overlapping learning objectives.
- [Feature admission policy](docs/phase-0/FEATURE_POLICY.md) — feature registry, incremental value, redundancy control.
- [Feature intelligence and information-value system](docs/phase-0/FEATURE_INTELLIGENCE_AND_INFORMATION_VALUE_SYSTEM.md) — candidate families, causal dependencies, normalization, redundancy, ablation and feature promotion gates.
- [Label specification](docs/phase-0/LABEL_SPECIFICATION.md) — outcome vs policy labels, ambiguity, leakage firewall.
- [Target and label intelligence governance](docs/phase-0/TARGET_AND_LABEL_INTELLIGENCE_GOVERNANCE.md) — target ontology, compact target portfolio, probability semantics, policy-label safeguards, censoring and leakage gates.
- [Forecast target engineering](docs/phase-0/FORECAST_TARGET_ENGINEERING.md) — precise future-event targets, horizons, price conventions, probability semantics and censoring.
- [Target portfolio and redundancy decision](docs/phase-0/TARGET_PORTFOLIO_AND_REDUNDANCY_DECISION.md) — F01–F08/Y01–Y06 crosswalk, primary targets, derived projections and conditional extensions.
- [Target dependency, episode and split contract](docs/phase-0/TARGET_DEPENDENCY_EPISODE_AND_SPLIT_CONTRACT.md) — shared future-path grouping, duplicate clusters, purge/embargo derivation and chronological split safeguards.
- [Multi-timeframe and market structure](docs/phase-0/MULTI_TIMEFRAME_AND_MARKET_STRUCTURE.md) — causal swing confirmation, BOS/CHoCH, SMC definitions, as-of synchronization and conflict-aware MTF reasoning.
- [Market reasoning and evidence synthesis](docs/phase-0/MARKET_REASONING_AND_EVIDENCE_SYNTHESIS.md) — cross-task evidence graph, causal reasoning sequence, conflict taxonomy, calibrated forecast discipline and safe abstention.
- [News and macro event intelligence](docs/phase-0/NEWS_AND_MACRO_EVENT_INTELLIGENCE.md) — point-in-time releases, consensus snapshots, revisions, market reactions, event risk and licensing gates.
- [Chart and visual intelligence](docs/phase-0/CHART_AND_VISUAL_INTELLIGENCE.md) — causal chart snapshots, image/data consistency, visual leakage controls, annotation lineage and modality ablation.
- [Trade lifecycle and risk intelligence](docs/phase-0/TRADE_LIFECYCLE_AND_RISK_INTELLIGENCE.md) — policy actions, conditional scenarios, deterministic risk authority, event-sourced trade management, execution and post-trade review.
- [Scenario specification](docs/phase-0/SCENARIO_SPECIFICATION.md) — conditional market paths, evidence, activation, invalidation, calibrated probabilities.
- [Risk and trade management](docs/phase-0/RISK_AND_TRADE_MANAGEMENT_SPECIFICATION.md) — deterministic risk boundary and event-based lifecycle.
- [Evaluation protocol](docs/phase-0/EVALUATION_PROTOCOL.md) — chronological testing, baselines, uncertainty, cost-aware policy evaluation.
- [Canonical data model and schema contracts](docs/phase-0/DATA_MODEL_AND_SCHEMA_CONTRACTS.md) — shared entities, record boundaries, identity, timestamps and typed statuses.
- [Canonical field semantics and status contract](docs/phase-0/CANONICAL_FIELD_SEMANTICS_AND_STATUS_CONTRACT.md) — shared timestamp, units, identity, availability and scoped lifecycle/status meanings.
- [Canonical field registry and semantic reconciliation](docs/phase-0/CANONICAL_FIELD_REGISTRY_AND_SEMANTIC_RECONCILIATION.md) — field ownership, task projections, value/status boundaries and cross-document conflict register.
- [Scoped enum and state transition governance](docs/phase-0/SCOPED_ENUM_AND_STATE_TRANSITION_GOVERNANCE.md) — distinct status/action domains, legal transitions, terminal-state rules and evidence requirements.
- [Field status binding and nullability matrix](docs/phase-0/FIELD_STATUS_BINDING_AND_NULLABILITY_MATRIX.md) — provisional field-by-field value/status/null rules for core canonical entities.
- [Deterministic risk and policy handoff contract](docs/phase-0/DETERMINISTIC_RISK_AND_POLICY_HANDOFF_CONTRACT.md) — immutable risk requests/results, policy permission boundary, freshness, recalculation and fail-closed rules.
- [Point-in-time, interval and snapshot revision contract](docs/phase-0/POINT_IN_TIME_INTERVAL_AND_SNAPSHOT_REVISION_CONTRACT.md) — causal availability, half-open intervals, partial bars, late revisions, immutable snapshots and temporal leakage controls.
- [A–M task-to-schema mapping](docs/phase-0/TASK_TO_SCHEMA_MAPPING.md) — maps the original architecture to canonical inputs, outputs and task boundaries.
- [Task I/O contracts](docs/phase-0/TASK_IO_CONTRACTS.md) — behavioral input/output, abstention and evaluation contracts for T01–T11.
- [Annotation and label reliability](docs/phase-0/ANNOTATION_AND_LABEL_RELIABILITY.md) — operational definitions, independent review, ambiguity and label provenance.
- [Trade lifecycle and management policy](docs/phase-0/TRADE_LIFECYCLE_AND_MANAGEMENT_POLICY.md) — chronological position states, management decisions, broker reconciliation and sequence evaluation.
- [Information-value roadmap](docs/phase-0/INFORMATION_VALUE_AND_TASK_ROADMAP.md) — capability priorities, feature admission, redundancy rules and task promotion gates.
- [Dataset composition and redundancy](docs/phase-0/DATASET_COMPOSITION_AND_REDUNDANCY.md) — information density, overlap control, event coverage and split-safe sampling.
- [Sample value and selection policy](docs/phase-0/SAMPLE_VALUE_AND_SELECTION_POLICY.md) — hard validity gates, multi-dimensional information value, episode-aware selection and auditable inclusion/exclusion.
- [Model learning and training strategy](docs/phase-0/MODEL_LEARNING_AND_TRAINING_STRATEGY.md) — learned-vs-deterministic boundaries, evidence-led method selection, staged curriculum, multi-task controls and release gates.
- [Data source feasibility framework](docs/phase-0/DATA_SOURCE_FEASIBILITY_FRAMEWORK.md) — source evidence tiers, task dependencies, temporal/rights requirements and task-specific admission gates.
- [Dataset provenance, versioning and reproducibility](docs/phase-0/DATASET_PROVENANCE_VERSIONING_REPRODUCIBILITY.md) — immutable lineage, run manifests, semantic versioning, split traceability, change impact and release audit.
- [Integrated architecture and consistency audit](docs/phase-0/INTEGRATED_ARCHITECTURE_AND_CONSISTENCY_AUDIT.md) — canonical layer ownership, A–M/T01–T11 reconciliation, task boundaries, dependencies and unresolved design decisions.
- [Data quality principles](docs/phase-0/DATA_QUALITY_PRINCIPLES.md) — inclusion, deduplication, leakage, validation.
- [Provenance validator implementation](docs/phase-0/PROVENANCE_VALIDATOR_IMPLEMENTATION.md) — executable schema and semantic checks, local test instructions, and validation limits.
- [Artifact integrity engine](docs/phase-0/ARTIFACT_INTEGRITY_ENGINE.md) — read-only SHA-256 and byte-size verification for explicitly selected local artifacts.
- [Decision log](docs/phase-0/DECISION_LOG.md) — recorded decisions and unresolved questions.

## Provenance schema contracts

JSON Schema Draft 2020-12 contracts for immutable artifacts, transformation runs, dataset builds, chronological splits and sample lineage are maintained in [schemas/provenance](schemas/provenance/README.md). These schemas formalize the Phase 0 provenance policy. The metadata-only validator and its unit tests are documented in [Provenance Validator Implementation](docs/phase-0/PROVENANCE_VALIDATOR_IMPLEMENTATION.md); neither constitutes a data-generation pipeline or a market-data validation result.

## Quality rule

A sample is retained only when its source, point-in-time availability, target definition, and intended use are explicit; its information is not an accidental duplicate; and its limitations can be represented honestly. If evidence is ambiguous, preserve the ambiguity or exclude the sample—never manufacture certainty.

## Project gates

0. Design and specification.
1. Stage 5 compatibility audit, only after that project is independently completed and accepted.
2. Source feasibility review.
3. Freeze schemas, features, labels, and validation protocol.
4. Design pipeline.
5. Controlled generation, only after approval.
6. Integrity audit.
7. Baseline evaluation.
8. Independent acceptance.
9. Training readiness.
10. Training, only after approval.
11. Model evaluation.

Passing a gate does not authorize the next phase automatically.
