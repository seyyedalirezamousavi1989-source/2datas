from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .ingest import read_zip
from .quality import audit_archive
from .normalize import normalize_archive
from .alignment import audit_timeframe_alignment
from .price_action import compute_price_action_features
from .broker_profiles import resolve_profile


def main() -> None:
    parser = argparse.ArgumentParser(prog="2datas", description="Audit and normalize XAUUSD source exports")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Run non-destructive source integrity audit")
    audit.add_argument("archive", type=Path)
    audit.add_argument("--output", type=Path, default=Path("reports/source_audit.json"))
    normalize = sub.add_parser("normalize", help="Create traceable gzip CSV partitions")
    normalize.add_argument("archive", type=Path)
    normalize.add_argument("--output-dir", type=Path, default=Path("data/processed/xauusd"))
    normalize.add_argument("--broker-profile", default=None, help="Versioned broker profile ID, e.g. alpari_mt5_candidate")
    normalize.add_argument("--broker-name", default=None)
    normalize.add_argument("--server-name", default=None)
    normalize.add_argument("--server-timezone", default=None, help="IANA timezone, e.g. Europe/Helsinki")
    normalize.add_argument("--bar-timestamp-convention", choices=["interval_start", "interval_end"], default=None)
    alignment = sub.add_parser("alignment", help="Audit cross-timeframe aggregation consistency")
    alignment.add_argument("archive", type=Path)
    alignment.add_argument("--output", type=Path, default=Path("reports/timeframe_alignment.json"))
    features = sub.add_parser("features", help="Generate causal price-action feature events")
    features.add_argument("archive", type=Path)
    features.add_argument("--output-dir", type=Path, default=Path("data/features/price_action"))
    features.add_argument("--broker-profile", default=None)
    features.add_argument("--broker-name", default=None)
    features.add_argument("--server-name", default=None)
    features.add_argument("--server-timezone", default=None)
    features.add_argument("--bar-timestamp-convention", choices=["interval_start", "interval_end"], default=None)
    features.add_argument("--include-last-bar", action="store_true", help="Include newest bar only when independently known to be complete")
    args = parser.parse_args()

    if args.command == "audit":
        result = audit_archive(read_zip(str(args.archive)))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"status": result["overall_status"], "total_rows": result["total_rows"], "report": str(args.output)}, ensure_ascii=False))
    elif args.command == "normalize":
        result = normalize_archive(str(args.archive), str(args.output_dir), broker_profile_id=args.broker_profile, broker_name=args.broker_name, server_name=args.server_name, server_timezone=args.server_timezone, bar_timestamp_convention=args.bar_timestamp_convention)
        print(json.dumps({"status": "MATERIALIZED", "total_rows": result["total_rows"], "manifest": str(args.output_dir / "manifest.json")}, ensure_ascii=False))
    elif args.command == "features":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        profile = resolve_profile(args.broker_profile, broker_name=args.broker_name, server_name=args.server_name, server_timezone=args.server_timezone, bar_timestamp_convention=args.bar_timestamp_convention)
        summaries = []
        for source in read_zip(str(args.archive)):
            rows = compute_price_action_features(source.rows, broker_profile=profile, source_sha256=source.source_sha256, include_last_bar=args.include_last_bar)
            instrument = source.rows[0].instrument if source.rows else "UNKNOWN"
            target = args.output_dir / f"{instrument}_{source.timeframe}.jsonl"
            with target.open("w", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + chr(10))
            summaries.append({"instrument": instrument, "timeframe": source.timeframe, "events": len(rows), "source_file": source.source_file, "source_sha256": source.source_sha256, "output_path": str(target), "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        manifest = {
            "feature_version": "price-action-0.1.0",
            "broker_profile": {"profile_id": profile.profile_id, "broker_name": profile.broker_name, "server_name": profile.server_name, "server_timezone": profile.server_timezone, "bar_timestamp_convention": profile.bar_timestamp_convention, "status": profile.status, "evidence": profile.evidence},
            "parameters": {"pivot_left": 3, "pivot_right": 3, "atr_period": 14, "equal_level_atr_tolerance": 0.10, "fvg_min_atr": 0.05, "ob_lookback": 8, "include_last_bar": args.include_last_bar},
            "partitions": summaries,
            "total_events": sum(item["events"] for item in summaries),
            "admission_status": "CANDIDATE_FEATURES_NOT_VALIDATED_FOR_TRAINING",
        }
        manifest_path = args.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"status": "MATERIALIZED", "total_events": manifest["total_events"], "manifest": str(manifest_path)}, ensure_ascii=False))
    elif args.command == "alignment":
        result = audit_timeframe_alignment(list(read_zip(str(args.archive))))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"status": "COMPLETED", "comparisons": len(result["comparisons"]), "report": str(args.output)}, ensure_ascii=False))
