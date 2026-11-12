"""Schema and cross-document validation for 2datas provenance contracts.

This module validates metadata only. It never reads market data, contacts providers,
creates dataset artifacts, or trains models.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "provenance"
SCHEMA_FILES = {
    "artifact": "artifact-manifest.schema.json",
    "transformation_run": "transformation-run.schema.json",
    "dataset_build": "dataset-build-manifest.schema.json",
    "split": "split-manifest.schema.json",
    "sample": "sample-lineage.schema.json",
}


def load_schemas(schema_dir: Path = SCHEMA_DIR) -> dict[str, dict[str, Any]]:
    schemas = {
        key: json.loads((schema_dir / filename).read_text(encoding="utf-8"))
        for key, filename in SCHEMA_FILES.items()
    }
    registry = Registry()
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(
            schema["$id"], Resource.from_contents(schema)
        )
    # Keep the registry attached for callers that need cross-schema references.
    schemas["_registry"] = registry  # type: ignore[assignment]
    return schemas


def schema_issues(
    document: dict[str, Any], schema: dict[str, Any], registry: Registry | None = None
) -> list[dict[str, str]]:
    validator = Draft202012Validator(
        schema, registry=registry or Registry(), format_checker=FormatChecker()
    )
    return [
        {
            "severity": "error",
            "code": "SCHEMA_INVALID",
            "path": "/" + "/".join(str(part) for part in error.absolute_path),
            "message": error.message,
        }
        for error in sorted(validator.iter_errors(document), key=lambda e: list(map(str, e.absolute_path)))
    ]


def _parse_time(value: Any, path: str, issues: list[dict[str, str]]) -> datetime | None:
    if not isinstance(value, str):
        issues.append(_issue("INVALID_TIMESTAMP", path, "Expected an ISO-8601 timestamp."))
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timezone is required")
        return parsed.astimezone(timezone.utc)
    except ValueError:
        issues.append(_issue("INVALID_TIMESTAMP", path, "Timestamp must be valid ISO-8601 with an explicit timezone."))
        return None


def _issue(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "message": message}


def validate_artifact_graph(artifacts: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    items = list(artifacts)
    issues: list[dict[str, str]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, artifact in enumerate(items):
        artifact_id = artifact.get("artifact_id")
        if not artifact_id:
            issues.append(_issue("MISSING_ARTIFACT_ID", f"/artifacts/{index}/artifact_id", "Artifact ID is required."))
            continue
        if artifact_id in by_id:
            issues.append(_issue("DUPLICATE_ARTIFACT_ID", f"/artifacts/{index}/artifact_id", f"Duplicate artifact ID: {artifact_id}."))
        by_id[artifact_id] = artifact

    graph: dict[str, list[str]] = {key: [] for key in by_id}
    for artifact_id, artifact in by_id.items():
        for index, parent in enumerate(artifact.get("parents", [])):
            parent_id = parent.get("artifact_id")
            if parent_id not in by_id:
                issues.append(_issue("MISSING_PARENT", f"/artifacts/{artifact_id}/parents/{index}", f"Unknown parent artifact: {parent_id}."))
            else:
                graph[artifact_id].append(parent_id)
        supersedes = artifact.get("supersedes_artifact_id")
        if supersedes and supersedes not in by_id:
            issues.append(_issue("MISSING_SUPERSEDED_ARTIFACT", f"/artifacts/{artifact_id}/supersedes_artifact_id", f"Unknown superseded artifact: {supersedes}."))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            issues.append(_issue("PROVENANCE_CYCLE", f"/artifacts/{node}/parents", "Artifact lineage must be a directed acyclic graph."))
            return
        if node in visited:
            return
        visiting.add(node)
        for parent in graph.get(node, []):
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for artifact_id in graph:
        visit(artifact_id)
    return issues


def validate_transformation_run(run: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    started = _parse_time(run.get("started_at"), "/started_at", issues)
    finished_value = run.get("finished_at")
    if finished_value is not None:
        finished = _parse_time(finished_value, "/finished_at", issues)
        if started and finished and finished < started:
            issues.append(_issue("RUN_TIME_REVERSED", "/finished_at", "Run finish time cannot precede start time."))
    if run.get("status") == "succeeded" and run.get("errors"):
        issues.append(_issue("SUCCEEDED_WITH_ERRORS", "/errors", "A succeeded run must not contain unresolved errors."))
    if run.get("status") == "failed" and run.get("outputs"):
        issues.append(_issue("FAILED_RUN_HAS_OUTPUTS", "/outputs", "Failed runs must not publish accepted outputs; use quarantined outputs or a non-success status."))
    input_ids = [item.get("artifact_id") for item in run.get("inputs", [])]
    output_ids = [item.get("artifact_id") for item in run.get("outputs", [])]
    if len(input_ids) != len(set(input_ids)):
        issues.append(_issue("DUPLICATE_RUN_INPUT", "/inputs", "Input artifact IDs must be unique within a run."))
    if len(output_ids) != len(set(output_ids)):
        issues.append(_issue("DUPLICATE_RUN_OUTPUT", "/outputs", "Output artifact IDs must be unique within a run."))
    if set(input_ids) & set(output_ids):
        issues.append(_issue("IN_PLACE_ARTIFACT_MUTATION", "/", "A transformation must create new immutable output artifact IDs; it cannot overwrite an input."))
    return issues


def validate_split_manifest(split: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    boundaries = split.get("boundaries", {})
    parsed_boundaries = {
        key: _parse_time(boundaries.get(key), f"/boundaries/{key}", issues)
        for key in ("train_end", "validation_end", "test_end")
    }
    ordered = [parsed_boundaries[k] for k in ("train_end", "validation_end", "test_end")]
    if all(ordered) and not (ordered[0] < ordered[1] < ordered[2]):
        issues.append(_issue("SPLIT_BOUNDARIES_NOT_INCREASING", "/boundaries", "Expected train_end < validation_end < test_end."))

    seen_groups: set[str] = set()
    cluster_splits: dict[str, set[str]] = {}
    intervals: list[tuple[datetime, datetime, str, str]] = []
    for index, group in enumerate(split.get("groups", [])):
        group_id, split_name = group.get("group_id"), group.get("split")
        if group_id in seen_groups:
            issues.append(_issue("DUPLICATE_GROUP_ID", f"/groups/{index}/group_id", f"Duplicate group ID: {group_id}."))
        seen_groups.add(group_id)
        start = _parse_time(group.get("start_time"), f"/groups/{index}/start_time", issues)
        end = _parse_time(group.get("end_time"), f"/groups/{index}/end_time", issues)
        if start and end:
            if end < start:
                issues.append(_issue("GROUP_INTERVAL_REVERSED", f"/groups/{index}", "Group end_time cannot precede start_time."))
            if split_name in {"train", "validation", "test"}:
                intervals.append((start, end, split_name, group_id))
        cluster = group.get("cluster_id")
        if cluster and split_name in {"train", "validation", "test"}:
            cluster_splits.setdefault(cluster, set()).add(split_name)

    for cluster, assignments in cluster_splits.items():
        if len(assignments) > 1:
            issues.append(_issue("DUPLICATE_CLUSTER_CROSSES_SPLITS", "/groups", f"Near-duplicate cluster {cluster} crosses splits: {sorted(assignments)}."))

    # Overlap is checked across different split assignments; same-split overlap is allowed.
    intervals.sort(key=lambda item: item[0])
    for index, current in enumerate(intervals):
        for other in intervals[index + 1:]:
            if other[0] >= current[1]:
                break
            if current[2] != other[2] and current[0] < other[1] and other[0] < current[1]:
                issues.append(_issue("CROSS_SPLIT_TIME_OVERLAP", "/groups", f"Groups {current[3]} and {other[3]} overlap across {current[2]} and {other[2]} splits."))
    return issues


def validate_sample_lineage(sample: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    decision = _parse_time(sample.get("decision_timestamp"), "/decision_timestamp", issues)
    for index, source in enumerate(sample.get("inputs", [])):
        available = _parse_time(source.get("available_at"), f"/inputs/{index}/available_at", issues)
        if decision and available and available > decision:
            issues.append(_issue("FUTURE_INPUT_LEAKAGE", f"/inputs/{index}/available_at", "Input was not available at the sample decision timestamp."))
    return issues


def validate_dataset_release(
    manifest: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    splits: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if manifest.get("status") == "released":
        if manifest.get("validation", {}).get("status") not in {"passed", "passed_with_warnings"}:
            issues.append(_issue("RELEASE_WITHOUT_VALIDATION", "/validation/status", "Released datasets require a passing validation status."))
        if manifest.get("rights", {}).get("review_status") != "approved":
            issues.append(_issue("RELEASE_WITHOUT_RIGHTS_APPROVAL", "/rights/review_status", "Released datasets require approved source rights."))
        if manifest.get("validation", {}).get("leakage_check") != "passed":
            issues.append(_issue("RELEASE_WITHOUT_LEAKAGE_PASS", "/validation/leakage_check", "Released datasets require an explicit passing leakage check."))
        if manifest.get("validation", {}).get("integrity_check") != "passed":
            issues.append(_issue("RELEASE_WITHOUT_INTEGRITY_PASS", "/validation/integrity_check", "Released datasets require an explicit passing integrity check."))
        if manifest.get("validation", {}).get("lineage_check") != "passed":
            issues.append(_issue("RELEASE_WITHOUT_LINEAGE_PASS", "/validation/lineage_check", "Released datasets require an explicit passing lineage check."))

    component_ids: list[str] = []
    for key in ("source_artifact_ids", "normalized_artifact_ids", "feature_artifact_ids", "label_artifact_ids"):
        component_ids.extend(manifest.get("components", {}).get(key, []))
    for artifact_id in component_ids:
        if artifact_id not in artifacts:
            issues.append(_issue("DATASET_COMPONENT_MISSING", "/components", f"Dataset references missing artifact {artifact_id}."))
    for split_id in manifest.get("split_manifest_ids", []):
        if split_id not in splits:
            issues.append(_issue("DATASET_SPLIT_MISSING", "/split_manifest_ids", f"Dataset references missing split manifest {split_id}."))
        elif manifest.get("status") == "released" and not splits[split_id].get("frozen", False):
            issues.append(_issue("RELEASE_USES_UNFROZEN_SPLIT", "/split_manifest_ids", f"Released dataset references unfrozen split {split_id}."))
    return issues


def validate_document(kind: str, document: dict[str, Any], schemas: dict[str, Any]) -> list[dict[str, str]]:
    schema = schemas[kind]
    issues = schema_issues(document, schema, schemas.get("_registry"))
    if issues:
        return issues
    if kind == "transformation_run":
        return validate_transformation_run(document)
    if kind == "split":
        return validate_split_manifest(document)
    if kind == "sample":
        return validate_sample_lineage(document)
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate 2datas provenance JSON contracts.")
    parser.add_argument("kind", choices=SCHEMA_FILES)
    parser.add_argument("document", type=Path)
    args = parser.parse_args(argv)
    try:
        schemas = load_schemas()
        document = json.loads(args.document.read_text(encoding="utf-8"))
        issues = validate_document(args.kind, document, schemas)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(json.dumps({"valid": False, "fatal_error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
