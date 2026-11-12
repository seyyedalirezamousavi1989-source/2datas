from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ingest import read_zip
from .quality import audit_archive
from .normalize import normalize_archive
from .alignment import audit_timeframe_alignment


def main() -> None:
    parser = argparse.ArgumentParser(prog="2datas", description="Audit and normalize XAUUSD source exports")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Run non-destructive source integrity audit")
    audit.add_argument("archive", type=Path)
    audit.add_argument("--output", type=Path, default=Path("reports/source_audit.json"))
    normalize = sub.add_parser("normalize", help="Create traceable gzip CSV partitions")
    normalize.add_argument("archive", type=Path)
    normalize.add_argument("--output-dir", type=Path, default=Path("data/processed/xauusd"))
    args = parser.parse_args()

    if args.command == "audit":
        result = audit_archive(read_zip(str(args.archive)))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"status": result["overall_status"], "total_rows": result["total_rows"], "report": str(args.output)}, ensure_ascii=False))
    elif args.command == "normalize":
        result = normalize_archive(str(args.archive), str(args.output_dir))
        print(json.dumps({"status": "MATERIALIZED", "total_rows": result["total_rows"], "manifest": str(args.output_dir / "manifest.json")}, ensure_ascii=False))
    elif args.command == "alignment":
        result = audit_timeframe_alignment(list(read_zip(str(args.archive))))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"status": "COMPLETED", "comparisons": len(result["comparisons"]), "report": str(args.output)}, ensure_ascii=False))
