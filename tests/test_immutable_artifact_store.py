import json, tempfile, unittest
from pathlib import Path
from tools.immutable_artifact_store import store_synthetic_fixture, verify_stored_object

class ImmutableArtifactStoreTests(unittest.TestCase):
    def test_content_addressed_store_and_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); result=store_synthetic_fixture(root,b"SYNTHETIC-OHLCV-fixture",
                artifact_id="fixture-001",created_at="2026-01-01T00:00:00Z")
            manifest=result["manifest"]
            self.assertTrue(result["object_created"])
            self.assertTrue(verify_stored_object(root,manifest)["valid"])
            self.assertEqual(json.loads(Path(result["manifest_path"]).read_text()),manifest)
    def test_manifest_overwrite_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            store_synthetic_fixture(root,b"fixture",artifact_id="same-id",created_at="2026-01-01T00:00:00Z")
            with self.assertRaisesRegex(ValueError,"overwrite"):
                store_synthetic_fixture(root,b"different",artifact_id="same-id",created_at="2026-01-01T00:00:00Z")
    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); r=store_synthetic_fixture(root,b"immutable",artifact_id="fixture",created_at="2026-01-01T00:00:00Z")
            Path(r["object_path"]).chmod(0o644); Path(r["object_path"]).write_bytes(b"tampered")
            self.assertFalse(verify_stored_object(root,r["manifest"])["valid"])
    def test_rejects_bad_id_and_naive_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,"artifact_id"):
                store_synthetic_fixture(root,b"x",artifact_id="../escape",created_at="2026-01-01T00:00:00Z")
            with self.assertRaisesRegex(ValueError,"timezone"):
                store_synthetic_fixture(root,b"x",artifact_id="x",created_at="2026-01-01T00:00:00")
    def test_rejects_symlink_object_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); r=store_synthetic_fixture(root,b"safe",artifact_id="fixture",created_at="2026-01-01T00:00:00Z")
            obj=Path(r["object_path"]); target=root/"outside"; target.write_bytes(b"safe")
            obj.unlink(); obj.symlink_to(target)
            with self.assertRaisesRegex(ValueError,"symlink"):
                verify_stored_object(root,r["manifest"])

if __name__=="__main__": unittest.main()
