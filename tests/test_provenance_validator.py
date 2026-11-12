"""Focused tests for schema and semantic provenance validation."""
import unittest

from tools.provenance_validator import (
    load_schemas,
    schema_issues,
    validate_artifact_graph,
    validate_dataset_release,
    validate_sample_lineage,
    validate_split_manifest,
    validate_transformation_run,
)


def artifact(artifact_id, parents=None):
    return {
        "artifact_id": artifact_id,
        "artifact_type": "source_artifact",
        "schema_version": "1.0.0",
        "created_at": "2026-01-01T00:00:00Z",
        "content": {"sha256": "a" * 64},
        "parents": parents or [],
        "reproducibility_level": "R0_TRACEABLE",
        "status": "candidate",
    }


class ProvenanceValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = load_schemas()

    def test_all_schema_documents_are_valid_json_schema(self):
        self.assertEqual(set(self.schemas) - {"_registry"}, {
            "artifact", "transformation_run", "dataset_build", "split", "sample"
        })

    def test_artifact_schema_accepts_minimal_manifest(self):
        self.assertEqual(schema_issues(artifact("a1"), self.schemas["artifact"]), [])

    def test_artifact_graph_detects_missing_parent_and_cycle(self):
        docs = [
            artifact("a", [{"artifact_id": "b", "relationship": "derived_from"}]),
            artifact("b", [{"artifact_id": "a", "relationship": "derived_from"}]),
        ]
        codes = {item["code"] for item in validate_artifact_graph(docs)}
        self.assertIn("PROVENANCE_CYCLE", codes)
        self.assertNotIn("MISSING_PARENT", codes)

    def test_artifact_graph_detects_unresolved_parent(self):
        codes = {item["code"] for item in validate_artifact_graph([
            artifact("child", [{"artifact_id": "absent", "relationship": "derived_from"}])
        ])}
        self.assertIn("MISSING_PARENT", codes)

    def test_transformation_cannot_overwrite_input(self):
        run = {
            "run_id": "r1", "operation": "normalize",
            "started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:01:00Z",
            "status": "succeeded",
            "inputs": [{"artifact_id": "a", "sha256": "a" * 64}],
            "outputs": [{"artifact_id": "a", "sha256": "b" * 64}],
            "code": {"repository": "repo", "commit_sha": "abc", "working_tree": "clean"},
            "configuration": {"sha256": "c" * 64},
            "environment": {"runtime": "python"},
        }
        codes = {item["code"] for item in validate_transformation_run(run)}
        self.assertIn("IN_PLACE_ARTIFACT_MUTATION", codes)

    def test_split_detects_non_chronological_boundaries(self):
        split = {
            "boundaries": {
                "train_end": "2026-03-01T00:00:00Z",
                "validation_end": "2026-02-01T00:00:00Z",
                "test_end": "2026-04-01T00:00:00Z",
            },
            "groups": [],
        }
        codes = {item["code"] for item in validate_split_manifest(split)}
        self.assertIn("SPLIT_BOUNDARIES_NOT_INCREASING", codes)

    def test_split_detects_cluster_leakage(self):
        split = {
            "boundaries": {
                "train_end": "2026-01-31T00:00:00Z",
                "validation_end": "2026-02-28T00:00:00Z",
                "test_end": "2026-03-31T00:00:00Z",
            },
            "groups": [
                {"group_id": "g1", "split": "train", "start_time": "2026-01-01T00:00:00Z", "end_time": "2026-01-02T00:00:00Z", "cluster_id": "c1"},
                {"group_id": "g2", "split": "test", "start_time": "2026-03-01T00:00:00Z", "end_time": "2026-03-02T00:00:00Z", "cluster_id": "c1"},
            ],
        }
        codes = {item["code"] for item in validate_split_manifest(split)}
        self.assertIn("DUPLICATE_CLUSTER_CROSSES_SPLITS", codes)

    def test_sample_rejects_future_available_input(self):
        sample = {
            "decision_timestamp": "2026-01-01T10:00:00Z",
            "inputs": [{
                "artifact_id": "a", "sha256": "a" * 64,
                "available_at": "2026-01-01T10:01:00Z",
            }],
        }
        codes = {item["code"] for item in validate_sample_lineage(sample)}
        self.assertIn("FUTURE_INPUT_LEAKAGE", codes)

    def test_release_requires_rights_and_all_validation_gates(self):
        manifest = {
            "status": "released",
            "components": {
                "source_artifact_ids": ["missing"],
                "normalized_artifact_ids": [],
                "feature_artifact_ids": [],
                "label_artifact_ids": [],
            },
            "split_manifest_ids": ["split-1"],
            "validation": {"status": "not_run"},
            "rights": {"review_status": "not_reviewed"},
        }
        codes = {item["code"] for item in validate_dataset_release(manifest, {}, {"split-1": {"frozen": False}})}
        self.assertTrue({
            "RELEASE_WITHOUT_VALIDATION",
            "RELEASE_WITHOUT_RIGHTS_APPROVAL",
            "RELEASE_WITHOUT_LEAKAGE_PASS",
            "RELEASE_WITHOUT_INTEGRITY_PASS",
            "RELEASE_WITHOUT_LINEAGE_PASS",
            "DATASET_COMPONENT_MISSING",
            "RELEASE_USES_UNFROZEN_SPLIT",
        }.issubset(codes))


if __name__ == "__main__":
    unittest.main()
