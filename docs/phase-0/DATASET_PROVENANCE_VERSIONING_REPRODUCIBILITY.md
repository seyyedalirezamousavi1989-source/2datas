# Dataset Provenance, Versioning and Reproducibility Contract — Phase 0

## 1. Purpose and authorization boundary

Define how every future dataset artifact, record, transformation, label, split and evaluation result will be traceable and reproducible.

**Design only.** This specification does not inspect the uploaded archive, acquire data, create manifests from real data, implement a pipeline, generate datasets, run experiments or train models. It does not modify AURORA QUANT or the separate Stage 5 project. Implementation requires a later explicit approval after all project gates.

The governing rule is simple: a result is not research-grade if its origin, transformations, assumptions, versions and evaluation lineage cannot be reconstructed.

## 2. Provenance graph, not just a metadata column

Represent lineage as a directed acyclic graph of immutable artifacts and transformations.

Core node types:
- `SourceArtifact`: provider export, broker record batch, official release archive, or other admitted source object.
- `SourceRecord`: stable reference to a raw observation or event within a source artifact.
- `NormalizationRun`: parsing, timestamp normalization, symbol mapping and canonicalization.
- `DerivedArtifact`: bars, features, snapshots, chart renderings or other derived data.
- `LabelArtifact`: outcome, event, regime or policy annotations with target-definition version.
- `DatasetBuild`: a declared collection of records for a defined purpose.
- `SplitManifest`: immutable assignment of groups/episodes to train, validation, test or research-only sets.
- `EvaluationRun`: baseline/model evaluation tied to exact dataset, split, code and configuration.
- `ReviewDecision`: human approval, quarantine, rejection or promotion with evidence and reviewer identity.

Edges describe explicit relationships such as `derived_from`, `normalized_by`, `labeled_by`, `included_in`, `assigned_to_split`, `evaluated_on`, and `reviewed_by`.

A filename, row position or timestamp alone is not a stable identity. Use stable IDs and content hashes. Never overwrite an artifact that is referenced by a downstream result.

## 3. Identity and immutable artifact rules

Each artifact must have:
- globally unique stable artifact ID;
- artifact type and schema version;
- creation time and producing process/run ID;
- content checksum and checksum algorithm;
- byte size and record count where applicable;
- media/serialization format and compression details;
- parent artifact IDs and transformation IDs;
- source/license classification;
- status (draft, candidate, accepted, quarantined, rejected, superseded);
- storage locator that does not expose credentials or private account identifiers.

Content hashes establish byte identity, not semantic correctness. Two differently serialized artifacts may be semantically equivalent, while identical bytes may still contain invalid data. Preserve both checksum and validation results.

Never silently replace source data or accepted artifacts. Corrections create a new version linked to the superseded artifact, with reason and impact assessment.

## 4. Source record lineage

For each raw record or a safely addressable record group, preserve:
- source artifact ID and provider/feed identity;
- source-native record key or stable offset/range;
- original symbol and canonical mapping version;
- event timestamp, timestamp precision and timezone semantics;
- receive/ingestion timestamp where available;
- sequence/order token where available;
- original raw values or a durable immutable reference;
- correction/revision indicator;
- source quality flags;
- source license and permitted-use classification.

Do not use a derived row number as a substitute for source identity. If a provider offers no stable record key, define a deterministic composite identity and document collision risk.

For privacy and security, credentials, API tokens, account login details and unnecessary personal identifiers must never be stored in manifests, logs or repository commits.

## 5. Transformation run contract

Every normalization, feature, labeling, rendering, sampling or export run must record:
- run ID and operation type;
- input artifact IDs and checksums;
- output artifact IDs and checksums;
- code repository, commit SHA and clean/dirty working-tree status;
- dependency lockfile or environment image digest;
- configuration file and its checksum;
- schema, mapping, feature and label registry versions;
- execution start/end timestamps and clock basis;
- runtime/tool version and relevant hardware when it can affect results;
- random seed and determinism settings where applicable;
- warnings, errors, rejected-record counts and reason counts;
- operator/approval reference and authorized scope.

A run must fail closed if required inputs, versions, checksums or configuration are missing. Do not silently substitute a newer dependency, source file or configuration.

## 6. Determinism and reproducibility levels

Not every external process is perfectly deterministic. Declare the reproducibility level for each artifact:

- **R0 — Traceable:** inputs, source, versions and configuration are known, but exact recreation is not guaranteed.
- **R1 — Repeatable:** same controlled environment and inputs are expected to reproduce the same output.
- **R2 — Bitwise reproducible:** repeated execution produces identical output bytes/checksum.
- **R3 — Statistically reproducible:** nondeterministic training/inference produces results within a predeclared statistical tolerance under repeated seeds/runs.

State which level is required and why. Do not call a process reproducible merely because its script is saved.

For numerical pipelines, define floating-point precision, rounding, timezone database, locale, sorting, parallelism and serialization behavior. For model training, record seeds, framework/CUDA/driver versions, kernels, hardware, data-loader ordering and nondeterminism limitations.

## 7. Dataset build manifest

Every dataset build must have a top-level manifest with:
- dataset ID, semantic version and human-readable purpose;
- instrument/feed scope and supported task IDs;
- creation timestamp and status;
- included source, normalized, feature and label artifact IDs;
- schema/feature/label registry versions;
- sampling and exclusion policy versions;
- episode grouping and overlap-control policy;
- train/validation/test split manifest IDs;
- source rights and usage constraints;
- record counts by task, period, source, status and split;
- known limitations and unresolved issues;
- checksums for all component manifests and outputs;
- parent dataset/build ID if this is a derived revision.

The manifest must distinguish raw observations, derived features, future labels, human annotations, synthetic development examples and simulated execution outcomes. They must not become indistinguishable after export.

## 8. Versioning policy

Use semantic versioning for dataset releases, with clear interpretation:
- **MAJOR:** incompatible schema/target semantics, material source identity changes, changed time/price conventions, or changed meaning of existing fields.
- **MINOR:** backward-compatible additions of task coverage, optional fields or new independently versioned labels/features that do not alter existing semantics.
- **PATCH:** corrections that do not change the declared schema or target meaning, such as metadata fixes or corrected manifest documentation.

A patch must not conceal a changed label definition or changed historical values. If a correction changes record membership, target values, split assignments or evaluation results, document the affected artifacts and downstream invalidation; a minor or major increment may be required depending on compatibility.

Version separately:
- dataset release;
- canonical schema;
- source/symbol mapping;
- feature definitions;
- label/target definitions;
- annotation guidelines;
- split protocol and manifest;
- pipeline code/configuration;
- evaluation protocol and baseline implementation.

Do not use one dataset version number to hide changes in every component.

## 9. Change-impact and invalidation rules

When any upstream artifact changes, compute the downstream dependency closure.

Examples:
- Source correction → re-normalize affected records, rebuild dependent features/labels, reassess split membership and evaluations.
- Symbol mapping/specification change → invalidate broker-dependent calculations and execution labels for affected effective periods.
- Feature formula change → create a new feature version; rebuild only dependent datasets and rerun affected evaluations.
- Label definition change → new label version and new target artifacts; old and new targets must not be silently mixed.
- Split rule change → new split manifest; prior results remain attached to the old split and cannot be represented as results on the new one.
- Evaluation metric/code change → new evaluation run; preserve old report and explain non-comparability.

Never update a manifest in place if doing so would make a previously reported result point to different underlying data. Publish a new manifest and mark prior releases superseded where appropriate.

## 10. Split lineage and leakage-resistant identity

Split assignment must be traceable to stable episode/group identities and a frozen split protocol.

The manifest should record:
- group/episode ID and source/time range;
- assigned split and assignment rationale;
- grouping algorithm/version;
- chronological boundary and timezone;
- target horizon and label-confirmation constraints;
- purge/embargo intervals and rationale;
- overlap/near-duplicate cluster IDs;
- exceptions and review decisions.

All derivatives of the same underlying episode—including chart crops, paraphrases, alternate feature views, annotations and synthetic transformations—must remain grouped for split purposes unless a documented leakage analysis justifies otherwise.

Validation and test manifests are frozen before model selection/training. Any change creates a new split version and invalidates direct comparison with prior results unless explicitly reconciled. The final test set must remain access-controlled and unused for iterative tuning.

## 11. Label and annotation provenance

Each label must reference:
- target/label definition ID and version;
- decision timestamp and target observation window;
- label confirmation/availability timestamp where applicable;
- source records and derived inputs used;
- algorithm or annotation guideline version;
- annotator/reviewer IDs using pseudonymous identifiers;
- adjudication record and disagreement state;
- confidence/uncertainty or ambiguity status;
- censoring, missingness and exclusion reasons;
- outcome versus policy-label family.

For automated labels, record exact code/configuration and dependency versions. For human labels, preserve independent initial judgments and adjudication; do not overwrite disagreement with only the final answer. Never infer policy correctness from realized profit alone.

## 12. Evaluation and model lineage

Every evaluation report must point to immutable:
- dataset release and component manifest;
- exact split manifest;
- task/schema/label versions;
- baseline/model artifact and revision;
- inference/training configuration;
- evaluation code commit and environment;
- metric definitions, confidence interval method and random seeds;
- per-task, per-period, per-regime and per-source results;
- exclusions, failures, missing outputs and safety violations.

Reports must state whether a metric is comparable to prior results. If data, split, task semantics, cost assumptions or metric code changed, explain the comparison limits.

A model checkpoint must reference the exact training dataset manifest and split, not a mutable directory path or a human-readable dataset name alone.

## 13. Repository and storage separation

Recommended separation:
- Git: specifications, schemas, registries, code, small manifests, review decisions and documentation.
- Controlled data storage: licensed raw data and large derived datasets, access-controlled and checksummed.
- Artifact store: immutable run outputs, model checkpoints and evaluation reports.
- Secrets manager: credentials only; never Git or dataset manifests.

Do not commit large proprietary market datasets or restricted broker records to a public repository. Repository visibility and data licensing must be checked before any upload. A Git commit is not a substitute for a governed data archive.

## 14. Audit and release checklist

Before accepting a dataset release, verify:
1. All referenced artifact IDs resolve.
2. Every checksum matches the stored bytes.
3. Parent-child lineage is complete and acyclic.
4. Source rights cover the exact retained and intended uses.
5. Schema/feature/label versions are pinned.
6. All transformations have run manifests and configurations.
7. Missingness, corrections and exclusions are accounted for.
8. Episode grouping and split assignments are reproducible.
9. No derivative crosses split boundaries unexpectedly.
10. Evaluation reports point to the exact immutable inputs.
11. Superseded artifacts and invalidated reports are identified.
12. No secrets or unnecessary personal/account identifiers are present.
13. Known limitations and non-reproducible steps are disclosed.
14. Independent review and release approval are recorded.

A failed checksum, unresolved parent, missing license, unknown transformation or unexplained split inconsistency blocks release.

## 15. Minimum manifest object families

The later implementation should define schema contracts for at least:
- artifact manifest;
- source dossier and source-record reference;
- transformation/run manifest;
- dataset build manifest;
- split manifest;
- feature and label registry snapshots;
- annotation/adjudication record;
- evaluation run/report manifest;
- review/approval record;
- change-impact and supersession record.

This is a logical inventory only; exact JSON Schema, Parquet metadata and storage formats remain to be designed after source and Stage 5 compatibility review.

## 16. Promotion gate

This contract is ready for implementation planning only after:
- source and licensing constraints are known;
- canonical schemas and task contracts are accepted;
- Stage 5 compatibility is independently reviewed at the approved milestone;
- storage/security requirements are defined;
- split and evaluation protocols are frozen;
- reproducibility requirements are chosen per transformation;
- the user separately authorizes implementation.

## 17. Explicit non-decisions

This document does not select a storage vendor, database, object store, serialization format, hash algorithm, CI service, model registry, or cloud provider. It does not authorize implementation, data migration, archive inspection or upload. These decisions depend on source volume, licensing, security, local hardware, and operational constraints.
