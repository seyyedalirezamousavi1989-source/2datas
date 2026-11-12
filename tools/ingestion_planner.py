"""Create a metadata-only ingestion plan; never acquire or read market data."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
PLAN_SCHEMA=ROOT/"schemas/ingestion/ingestion-plan.schema.json"
REGISTRY_SCHEMA=ROOT/"schemas/registry/data-source.schema.json"
DECISION_SCHEMA=ROOT/"schemas/registry/source-admission-decision.schema.json"

def load_json(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValueError(f"cannot read JSON metadata {path}: {exc}") from exc

def validate(value: Any, schema_path: Path) -> None:
    try:
        import jsonschema
        jsonschema.Draft202012Validator(load_json(schema_path),format_checker=jsonschema.FormatChecker()).validate(value)
    except ImportError as exc: raise ValueError("jsonschema dependency is required") from exc
    except Exception as exc:
        if exc.__class__.__module__.startswith("jsonschema"): raise ValueError(f"schema validation failed: {exc.message}") from exc
        raise

def parse_time(value: str) -> datetime:
    try: result=datetime.fromisoformat(value.replace("Z","+00:00"))
    except (TypeError,ValueError) as exc: raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if result.tzinfo is None or result.utcoffset() is None: raise ValueError("timestamps must include an explicit timezone")
    return result.astimezone(timezone.utc)

def build_plan(registry: dict[str,Any], decision: dict[str,Any], request: dict[str,Any]) -> dict[str,Any]:
    validate(decision,DECISION_SCHEMA)
    if not isinstance(registry,dict) or registry.get("schema_version")!="1.0.0" or not isinstance(registry.get("sources"),list):
        raise ValueError("registry requires schema_version 1.0.0 and a sources array")
    sources={}
    for source in registry["sources"]:
        validate(source,REGISTRY_SCHEMA)
        sid=source["source_id"]
        if sid in sources: raise ValueError(f"duplicate source_id: {sid}")
        sources[sid]=source
    required=("plan_id","created_at","source_id","source_revision","instrument_id","timeframe","start","end")
    missing=[key for key in required if key not in request]
    if missing: raise ValueError("request is missing: "+", ".join(missing))
    sid=request["source_id"]; source=sources.get(sid)
    if source is None: raise ValueError("requested source does not exist in registry")
    if source["revision"]!=request["source_revision"]: raise ValueError("requested source revision does not match registry")
    if source["status"]!="approved": raise ValueError("source lifecycle status must be approved")
    if decision["decision"]!="admitted" or decision["target_use"]!="research":
        raise ValueError("an admitted research-use decision is required")
    if decision["source_id"]!=sid or decision["source_revision"]!=source["revision"]:
        raise ValueError("admission decision does not match requested source revision")
    now=parse_time(request["created_at"])
    for expiry in (source.get("valid_until"),decision.get("revalidation_due")):
        if expiry and parse_time(expiry)<=now: raise ValueError("source approval or admission decision has expired")
    if "ohlcv" not in source["modalities"]: raise ValueError("source is not registered for OHLCV")
    instrument=request["instrument_id"]
    mappings=[x for x in source["instruments"] if x["instrument_id"]==instrument]
    if len(mappings)!=1: raise ValueError("instrument_id must resolve to exactly one provider-symbol mapping")
    timeframe=request["timeframe"]
    if timeframe not in source["supported_timeframes"]: raise ValueError("requested timeframe is not supported")
    start,end=parse_time(request["start"]),parse_time(request["end"])
    if start>=end: raise ValueError("requested range start must precede end")
    plan={"schema_version":"1.0.0","plan_id":request["plan_id"],"created_at":now.isoformat().replace("+00:00","Z"),
      "source_id":sid,"source_revision":source["revision"],"admission_decision_id":decision["decision_id"],"target_use":"research",
      "instrument_id":instrument,"provider_symbol":mappings[0]["provider_symbol"],"timeframe":timeframe,
      "range":{"start":start.isoformat().replace("+00:00","Z"),"end":end.isoformat().replace("+00:00","Z")},
      "requested_modality":"ohlcv","output_contract":{"schema_ref":"schemas/data/canonical-ohlcv-record.schema.json","format":"jsonl","preserve_raw_source":True},
      "execution":{"status":"planned_only","acquisition_authorized":False,"network_access":False,"market_data_read":False,"dataset_written":False,
        "reason":"Planning only. Explicit authorization and a separately reviewed acquisition implementation are required before real market data access."}}
    validate(plan,PLAN_SCHEMA)
    return plan

def write_new_plan(plan: dict[str,Any], output: Path) -> None:
    validate(plan,PLAN_SCHEMA); output=output.absolute()
    if output.exists() or output.is_symlink(): raise ValueError("plan output exists or is a symlink; refusing overwrite")
    if not output.parent.is_dir(): raise ValueError("plan output parent directory must already exist")
    with output.open("x",encoding="utf-8",newline="") as stream:
        json.dump(plan,stream,ensure_ascii=False,sort_keys=True,indent=2); stream.write("\n")

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="Metadata-only ingestion readiness planner")
    sub=parser.add_subparsers(dest="command",required=True); cmd=sub.add_parser("plan")
    cmd.add_argument("--registry",required=True,type=Path); cmd.add_argument("--decision",required=True,type=Path)
    cmd.add_argument("--request",required=True,type=Path); cmd.add_argument("--output",required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        result=build_plan(load_json(args.registry),load_json(args.decision),load_json(args.request))
        write_new_plan(result,args.output); print(json.dumps(result,ensure_ascii=False,sort_keys=True)); return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},ensure_ascii=False),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
