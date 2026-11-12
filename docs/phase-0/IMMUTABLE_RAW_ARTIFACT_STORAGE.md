# Immutable Raw Artifact Storage — Synthetic Foundation

## Scope and hard boundary
This increment establishes a content-addressed storage primitive and manifest writer using only caller-supplied in-memory synthetic fixture bytes. It does not connect to acquisition adapters, read market-data files, contact brokers/providers, download data, or create a real market-data archive. No training or dataset build is invoked. Do not pass real market data to this module; real-data storage remains outside the authorized scope.

## Storage layout
Objects are stored by SHA-256 under `objects/sha256/<first-two-hex>/<full-sha256>`. Identical bytes therefore share one immutable object. Manifests are stored separately under `manifests/<artifact_id>.json` and bind artifact identity, creation time, byte size, media type, synthetic source declaration, reproducibility level, status, and relative storage path.

## Write guarantees
- Files are created exclusively; existing manifest paths are never overwritten.
- Object files are created read-only (0444 where supported) and are content-addressed.
- If an object already exists, its bytes must match the requested payload exactly.
- Artifact IDs are restricted to a conservative filename-safe character set.
- Symlink storage components and path escapes are rejected.
- The storage root must already exist; the engine does not silently create an arbitrary root.
- Verification streams bytes and recomputes SHA-256 and byte size without modifying content.

The primitive is intended for the synthetic fixture harness only. It is not yet an archival service: crash recovery, fsync of parent directories, concurrent multi-process coordination, signed manifests, object-store retention locks, and garbage collection policy remain future work.

## Example layout
```
artifact-root/
  objects/sha256/ab/ab...<64-char-sha256>
  manifests/fixture-001.json
```

## Validation
Run `python -m unittest discover -s tests -v`. Tests use synthetic bytes only and cover successful storage/verification, overwrite refusal, tamper detection, unsafe IDs, timezone requirements, and symlink rejection.

## Deferred
A later separately reviewed increment may design production-grade immutable storage and recovery. Any use with actual market data requires explicit authorization, source admission for the intended use, licensing review, and a dedicated operational security design. This commit does not authorize those actions.
