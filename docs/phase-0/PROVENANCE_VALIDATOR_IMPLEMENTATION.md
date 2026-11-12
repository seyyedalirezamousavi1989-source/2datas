# Provenance Validator — Implementation Contract

## Status and boundary

The repository now contains a metadata-only validator for the five provenance JSON contracts. This is a Phase 0 engineering aid, not authorization to ingest market data, inspect the existing archive, run MetaTrader 5, call external market-data APIs, build a dataset, train a model, or modify AURORA QUANT / Stage 5.

The validator accepts JSON manifests supplied by an operator. It does not discover files, fetch providers, calculate checksums from market payloads, or write/alter manifests.

## Components

- `schemas/provenance/*.schema.json`: Draft 2020-12 structural contracts.
- `tools/provenance_validator.py`: structural validation plus cross-document semantic checks.
- `tests/test_provenance_validator.py`: deterministic unit tests using small in-memory fixtures.
- `requirements-dev.txt`: development-only dependency declaration.

## Semantic invariants

The implementation checks:

1. Artifact IDs are unique; parent and superseded-artifact references resolve; lineage is acyclic.
2. Transformation start/finish timestamps are timezone-aware and ordered; input/output IDs are unique and immutable; a run cannot overwrite an input artifact.
3. Split boundaries are strictly chronological; group intervals are valid; duplicate clusters cannot cross train/validation/test; overlapping time intervals across different splits are rejected.
4. Every sample input's `available_at` is no later than its decision timestamp.
5. A released dataset must have passing validation, leakage, integrity and lineage gates; approved rights; resolvable component and split references; and frozen splits.

## Local use

From the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/provenance_validator.py artifact path/to/artifact-manifest.json
python tools/provenance_validator.py transformation_run path/to/transformation-run.json
python tools/provenance_validator.py dataset_build path/to/dataset-build-manifest.json
python tools/provenance_validator.py split path/to/split-manifest.json
python tools/provenance_validator.py sample path/to/sample-lineage.json
```

Exit codes: `0` valid, `1` contract/semantic issues, `2` fatal input or schema-loading error. Output is machine-readable JSON.

## Deliberate limits / follow-up

- JSON Schema format checks and local constraints do not prove that a SHA-256 matches an artifact's bytes.
- The validator cannot independently establish source licensing, provider terms, broker symbol semantics, or truthful availability timestamps.
- Cross-split interval checks are conservative; target-horizon-specific purge/embargo and episode dependency checks still require explicit policy inputs and richer lineage.
- The release gate validates declared evidence; it cannot independently certify that the evidence is genuine.
- Full repository-wide batch validation, CI integration, signed review approvals, content-store verification, and a richer dependency graph are future work.

A passing result means only that the submitted metadata satisfies the checks implemented here. It is not evidence of predictive quality, trading profitability, or training readiness.
