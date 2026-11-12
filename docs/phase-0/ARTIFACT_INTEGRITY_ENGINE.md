# Artifact Integrity Engine

## Purpose and safety boundary

The Artifact Integrity Engine performs read-only verification of local artifact files against immutable artifact manifests. It checks SHA-256 and, when declared, byte size.

It is deliberately not a data-ingestion or dataset-building tool. It does not download data, contact providers, inspect broker archives, invoke MetaTrader 5, modify or delete files, generate manifests, train models, or touch AURORA QUANT / Stage 5. Operators must explicitly provide both the manifest directory and artifact root.

## Storage locator convention

For local verification, an artifact manifest may include:

~~~json
{
  "metadata": {
    "storage_path": "source/immutable-export.bin"
  }
}
~~~

The path is relative to the explicitly supplied artifact root. Absolute paths, parent-directory traversal, symlinks, paths escaping the root, missing files, and non-regular files are rejected. The storage path is metadata, not a new required field in the shared artifact schema; remote locators and other metadata remain possible.

## Local use

From the repository root:

~~~bash
python tools/artifact_integrity.py --manifests path/to/manifests --artifact-root path/to/artifacts
~~~

The command recursively reads *.json manifests under the selected manifest directory and emits a JSON report. Exit codes: 0 all manifests verified, 1 one or more manifests failed (including an empty manifest directory), 2 invalid arguments or fatal setup error.

The verifier streams files in 1 MiB chunks, so it does not need to load large artifacts into memory. It never writes into either supplied directory.

## What a pass means

A pass means the file currently found at the declared relative path has the declared SHA-256 and optional byte size. It does not establish:
- that the source or license is legitimate;
- that the file contents are semantically valid or complete;
- that the manifest itself was signed or approved;
- that the file cannot change immediately after verification (TOCTOU);
- that the artifact is suitable for training or evaluation.

For regulated or shared storage, run against a read-only snapshot and add signed manifest approvals and immutable object-store retention before relying on release decisions.

## Tests and CI

tests/test_artifact_integrity.py covers successful verification, byte tampering, byte-size mismatch, path traversal rejection, and symlink rejection. The existing provenance workflow runs the complete tests suite.
