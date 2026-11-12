"""Read-only verification of local files against immutable artifact manifests.

The verifier only reads explicitly supplied manifest and artifact directories. It
never downloads, modifies, deletes, moves, or creates artifact files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from tools.provenance_validator import load_schemas, schema_issues

CHUNK_SIZE = 1024 * 1024


def _safe_artifact_path(root: Path, relative: Any) -> tuple[Path | None, str | None]:
    if not isinstance(relative, str) or not relative.strip():
        return None, "STORAGE_PATH_MISSING"
    candidate = Path(relative)
    if candidate.is_absolute() or candidate.drive or ".." in candidate.parts:
        return None, "UNSAFE_STORAGE_PATH"
    root_resolved = root.resolve(strict=True)
    current = root_resolved
    for part in candidate.parts:
        if part in ("", "."):
            continue
        current = current / part
        if current.is_symlink():
            return None, "SYMLINK_NOT_ALLOWED"
    try:
        resolved = current.resolve(strict=True)
    except FileNotFoundError:
        return None, "ARTIFACT_FILE_MISSING"
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        return None, "PATH_ESCAPES_ARTIFACT_ROOT"
    if not resolved.is_file():
        return None, "ARTIFACT_NOT_REGULAR_FILE"
    return resolved, None


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def verify_manifest_file(manifest_path: Path, artifact_root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"manifest": str(manifest_path), "artifact_id": None, "status": "failed", "issues": []}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        result["issues"].append({"code": "MANIFEST_READ_ERROR", "message": str(exc)})
        return result

    result["artifact_id"] = manifest.get("artifact_id") if isinstance(manifest, dict) else None
    structural = schema_issues(manifest, schema)
    if structural:
        result["issues"].extend(
            {"code": item["code"], "path": item["path"], "message": item["message"]}
            for item in structural
        )
        return result

    metadata = manifest.get("metadata") or {}
    storage_path = metadata.get("storage_path") if isinstance(metadata, dict) else None
    path, error = _safe_artifact_path(artifact_root, storage_path)
    if error:
        result["issues"].append({
            "code": error,
            "path": "/metadata/storage_path",
            "message": f"Cannot safely resolve artifact storage path: {storage_path!r}.",
        })
        return result

    expected_hash = manifest["content"]["sha256"].lower()
    expected_size = manifest["content"].get("byte_size")
    try:
        actual_hash, actual_size = _hash_file(path)
    except OSError as exc:
        result["issues"].append({"code": "ARTIFACT_READ_ERROR", "message": str(exc)})
        return result

    result["storage_path"] = str(storage_path)
    result["actual"] = {"sha256": actual_hash, "byte_size": actual_size}
    result["expected"] = {"sha256": expected_hash, "byte_size": expected_size}
    if actual_hash != expected_hash:
        result["issues"].append({"code": "SHA256_MISMATCH", "path": "/content/sha256", "message": "Artifact bytes do not match the manifest SHA-256."})
    if expected_size is not None and actual_size != expected_size:
        result["issues"].append({"code": "BYTE_SIZE_MISMATCH", "path": "/content/byte_size", "message": f"Expected {expected_size} bytes; found {actual_size}."})
    result["status"] = "passed" if not result["issues"] else "failed"
    return result


def verify_directory(manifest_dir: Path, artifact_root: Path) -> dict[str, Any]:
    schemas = load_schemas()
    if not manifest_dir.is_dir():
        raise ValueError(f"Manifest directory does not exist: {manifest_dir}")
    if not artifact_root.is_dir():
        raise ValueError(f"Artifact root does not exist: {artifact_root}")
    manifest_files = sorted(path for path in manifest_dir.rglob("*.json") if path.is_file())
    results = [verify_manifest_file(path, artifact_root, schemas["artifact"]) for path in manifest_files]
    return {
        "valid": bool(results) and all(item["status"] == "passed" for item in results),
        "manifest_count": len(results),
        "passed": sum(item["status"] == "passed" for item in results),
        "failed": sum(item["status"] != "passed" for item in results),
        "results": results,
        "limitations": [
            "This verifies byte identity and declared byte size only.",
            "It does not prove source licensing, semantic correctness, or that a manifest is truthful.",
            "No files are created, changed, deleted, downloaded, or moved.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only SHA-256 and byte-size verification for local artifact manifests.")
    parser.add_argument("--manifests", required=True, type=Path, help="Directory containing artifact manifest JSON files.")
    parser.add_argument("--artifact-root", required=True, type=Path, help="Root directory against which metadata.storage_path is resolved.")
    args = parser.parse_args(argv)
    try:
        report = verify_directory(args.manifests, args.artifact_root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "fatal_error": str(exc)}, indent=2))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
