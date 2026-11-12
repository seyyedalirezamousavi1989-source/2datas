"""Exclusive, content-addressed storage foundation; synthetic fixtures only.

This module is deliberately not wired to acquisition, broker, filesystem-import,
or dataset pipelines. It accepts in-memory synthetic fixture bytes only.
"""
from __future__ import annotations
import hashlib, json, os, re
from datetime import datetime
from pathlib import Path
from typing import Any

_ARTIFACT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

def _utc(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("created_at must be ISO-8601 with timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("created_at must include a timezone")
    return parsed.isoformat().replace("+00:00", "Z")

def _ensure_safe_dir(root: Path, relative: str) -> Path:
    current = root
    for part in relative.split("/"):
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError("symlink storage directories are forbidden")
        current.mkdir(exist_ok=True)
        if not current.is_dir():
            raise ValueError("storage path component is not a directory")
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root.resolve(strict=True)):
        raise ValueError("storage path escapes root")
    return resolved

def _exclusive_write(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o444)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try: path.unlink()
        except OSError: pass
        raise

def store_synthetic_fixture(root: Path, payload: bytes, *, artifact_id: str,
                            created_at: str, media_type: str = "application/octet-stream") -> dict[str, Any]:
    """Store explicitly synthetic in-memory bytes; never reads external source files."""
    if not isinstance(payload, bytes) or not payload:
        raise ValueError("payload must be non-empty bytes")
    if not isinstance(artifact_id, str) or not _ARTIFACT_ID.fullmatch(artifact_id):
        raise ValueError("unsafe artifact_id")
    if not isinstance(media_type, str) or not media_type.strip():
        raise ValueError("media_type must be non-empty")
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("storage root must be an existing directory")
    digest = hashlib.sha256(payload).hexdigest()
    object_dir = _ensure_safe_dir(root, f"objects/sha256/{digest[:2]}")
    object_rel = f"objects/sha256/{digest[:2]}/{digest}"
    object_path = object_dir / digest
    created_object = False
    try:
        _exclusive_write(object_path, payload)
        created_object = True
    except FileExistsError:
        # Existing content-addressed object is accepted only after byte-for-byte verification.
        if object_path.is_symlink() or not object_path.is_file() or object_path.read_bytes() != payload:
            raise ValueError("existing content-addressed object failed integrity check")

    manifest_dir = _ensure_safe_dir(root, "manifests")
    manifest_rel = f"manifests/{artifact_id}.json"
    manifest_path = manifest_dir / f"{artifact_id}.json"
    manifest = {
        "artifact_id": artifact_id,
        "artifact_type": "source_artifact",
        "schema_version": "1.0.0",
        "created_at": _utc(created_at),
        "content": {"sha256": digest, "byte_size": len(payload), "media_type": media_type,
                    "serialization_format": "opaque_bytes"},
        "source": {"provider_id": "synthetic-fixture", "license_id": "synthetic-only",
                   "permitted_use": "testing", "source_locator": "in-memory://synthetic-fixture"},
        "reproducibility_level": "R2_BITWISE",
        "status": "candidate",
        "metadata": {"storage_path": object_rel, "storage_mode": "content_addressed_exclusive",
                     "fixture_only": True, "manifest_path": manifest_rel}
    }
    encoded = (json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        _exclusive_write(manifest_path, encoded)
    except FileExistsError as exc:
        if created_object:
            # The object is immutable and content-addressed; retain it rather than risk deletion
            # because another manifest may already reference the same digest.
            pass
        raise ValueError("manifest already exists; refusing overwrite") from exc
    return {"manifest": manifest, "object_created": created_object,
            "object_path": str(object_path), "manifest_path": str(manifest_path)}

def verify_stored_object(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Verify an in-root stored object without modifying it."""
    relative = manifest.get("metadata", {}).get("storage_path")
    if not isinstance(relative, str) or relative.startswith("/") or ".." in Path(relative).parts:
        raise ValueError("unsafe storage_path")
    root = Path(root).resolve(strict=True)
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink object paths are forbidden")
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("object path escapes storage root")
    if not resolved.is_file():
        raise ValueError("stored object is not a regular file")
    digest = hashlib.sha256()
    size = 0
    with resolved.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk); size += len(chunk)
    expected = manifest["content"]
    return {"valid": digest.hexdigest() == expected["sha256"] and size == expected["byte_size"],
            "sha256": digest.hexdigest(), "byte_size": size}
