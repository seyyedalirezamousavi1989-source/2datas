"""Tests for safe, read-only artifact integrity verification."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.artifact_integrity import verify_manifest_file
from tools.provenance_validator import load_schemas


class ArtifactIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schemas()["artifact"]

    def _manifest(self, root, relative_path, payload, declared_size=None):
        artifact = root / relative_path
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_bytes(payload)
        manifest = {
            "artifact_id": "artifact-1",
            "artifact_type": "source_artifact",
            "schema_version": "1.0.0",
            "created_at": "2026-01-01T00:00:00Z",
            "content": {"sha256": hashlib.sha256(payload).hexdigest(), "byte_size": len(payload) if declared_size is None else declared_size},
            "reproducibility_level": "R0_TRACEABLE",
            "status": "candidate",
            "metadata": {"storage_path": relative_path},
        }
        manifest_path = root.parent / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path, artifact

    def test_valid_artifact_passes_and_bytes_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / "artifacts"; root.mkdir()
            manifest, artifact = self._manifest(root, "nested/data.bin", b"sample-bytes")
            before = artifact.read_bytes()
            result = verify_manifest_file(manifest, root, self.schema)
            self.assertEqual(result["status"], "passed")
            self.assertEqual(artifact.read_bytes(), before)

    def test_modified_bytes_fail_hash_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / "artifacts"; root.mkdir()
            manifest, artifact = self._manifest(root, "data.bin", b"original")
            artifact.write_bytes(b"tampered")
            result = verify_manifest_file(manifest, root, self.schema)
            self.assertIn("SHA256_MISMATCH", {issue["code"] for issue in result["issues"]})

    def test_byte_size_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / "artifacts"; root.mkdir()
            manifest, _ = self._manifest(root, "data.bin", b"1234", declared_size=9)
            result = verify_manifest_file(manifest, root, self.schema)
            self.assertIn("BYTE_SIZE_MISMATCH", {issue["code"] for issue in result["issues"]})

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / "artifacts"; root.mkdir()
            manifest_path = base / "manifest.json"
            manifest = {"artifact_id": "artifact-1", "artifact_type": "source_artifact", "schema_version": "1.0.0",
                "created_at": "2026-01-01T00:00:00Z", "content": {"sha256": "a" * 64},
                "reproducibility_level": "R0_TRACEABLE", "status": "candidate",
                "metadata": {"storage_path": "../outside.bin"}}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = verify_manifest_file(manifest_path, root, self.schema)
            self.assertIn("UNSAFE_STORAGE_PATH", {issue["code"] for issue in result["issues"]})

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / "artifacts"; root.mkdir()
            outside = base / "outside.bin"; outside.write_bytes(b"outside")
            link = root / "linked.bin"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are unavailable in this environment.")
            manifest_path = base / "manifest.json"
            manifest = {"artifact_id": "artifact-1", "artifact_type": "source_artifact", "schema_version": "1.0.0",
                "created_at": "2026-01-01T00:00:00Z", "content": {"sha256": hashlib.sha256(b"outside").hexdigest()},
                "reproducibility_level": "R0_TRACEABLE", "status": "candidate",
                "metadata": {"storage_path": "linked.bin"}}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = verify_manifest_file(manifest_path, root, self.schema)
            self.assertIn("SYMLINK_NOT_ALLOWED", {issue["code"] for issue in result["issues"]})


if __name__ == "__main__":
    unittest.main()
