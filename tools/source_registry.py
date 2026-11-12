"""Offline source registry validation and fail-closed admission decisions."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USES=("research","model_training","redistribution","commercial")
ROOT=Path(__file__).resolve().parents[1]
REGISTRY_SCHEMA=ROOT/"schemas/registry/data-source.schema.json"
DECISION_SCHEMA=ROOT/"schemas/registry/source-admission-decision.schema.json"

def load_json(path):
    try:
        with Path(path).open(encoding="utf-8") as f: return json.load(f)
    except (OSError,json.JSONDecodeError) as exc: raise ValueError(f"cannot read JSON: {exc}") from exc

def validate_schema(value,path):
    try:
        import jsonschema
        jsonschema.Draft202012Validator(load_json(path),format_checker=jsonschema.FormatChecker()).validate(value)
    except ImportError as exc: raise ValueError("jsonschema dependency is required") from exc
    except Exception as exc:
        if exc.__class__.__module__.startswith("jsonschema"): raise ValueError(f"schema validation failed: {exc.message}") from exc
        raise

def validate_registry(registry):
    if not isinstance(registry,dict) or registry.get("schema_version")!="1.0.0" or not isinstance(registry.get("sources"),list):
        raise ValueError("registry requires schema_version 1.0.0 and a sources array")
    seen=set()
    for item in registry["sources"]:
        validate_schema(item,REGISTRY_SCHEMA)
        sid=item["source_id"]
        if sid in seen: raise ValueError(f"duplicate source_id: {sid}")
        seen.add(sid)
    return sorted(seen)

def parse_time(value):
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError("timezone-aware timestamp required")
    return dt.astimezone(timezone.utc)

def evaluate_source(registry,source_id,target_use,now=None,reviewer_id="unassigned",policy_version="1.0.0"):
    if target_use not in USES: raise ValueError(f"unsupported target use: {target_use}")
    validate_registry(registry)
    matches=[s for s in registry["sources"] if s["source_id"]==source_id]
    if len(matches)!=1: raise ValueError("source_id must resolve to exactly one registry record")
    s=matches[0]; now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    checks=[]; reasons=[]
    def add(key,status,detail):
        checks.append({"check_id":key,"status":status,"detail":detail})
        if status!="pass": reasons.append(detail)
    add("registry_status","pass" if s["status"]=="approved" else "fail",
        "source is approved" if s["status"]=="approved" else f"source status {s['status']} is not approved")
    perm=s["license"]["permissions"][target_use]
    add("usage_permission",{"allowed":"pass","prohibited":"fail","unknown":"review"}[perm],
        f"{target_use} permission is {perm}")
    add("license_reference","pass" if s["license"]["reference"] else "review","license/terms reference must be recorded")
    t=s["timestamp_convention"]
    tz=t["timezone"].upper() in ("UTC","ETC/UTC","Z") or "/" in t["timezone"]
    timing=tz and t["timestamp_field_semantics"]!="unknown" and t["bar_boundary"]!="unknown"
    add("timestamp_convention","pass" if timing else "review","timestamp timezone, semantics and bar boundary must be explicit")
    mapping=bool(s["instruments"]) and all(x.get("instrument_id") and x.get("provider_symbol") for x in s["instruments"])
    add("instrument_mapping","pass" if mapping else "review","canonical instrument mappings must be present")
    add("price_basis","pass" if s["price_basis"] not in ("unknown",) else "review","price basis must be explicit")
    v=s["volume_semantics"]; vok=v["meaning"]!="unknown" and (v["meaning"]=="not_applicable" or bool(v.get("unit")))
    add("volume_semantics","pass" if vok else "review","volume meaning and unit must be explicit or not applicable")
    refs=s["provenance"]["evidence_refs"]; evidence=sorted({x["artifact_id"] for x in refs})
    add("evidence_references","pass" if evidence else "review","evidence references are metadata only; no external fetch or verification is performed")
    if s.get("valid_until"):
        expired=parse_time(s["valid_until"])<=now
        add("approval_expiry","review" if expired else "pass","approval expired; revalidation required" if expired else "approval is within declared validity")
    else: add("approval_expiry","pass","no expiry declared; periodic review remains required")
    states={x["status"] for x in checks}
    decision="rejected" if "fail" in states else ("needs_review" if "review" in states else "admitted")
    record={"schema_version":"1.0.0","decision_id":f"decision:{source_id}:r{s['revision']}:{target_use}:{now.strftime('%Y%m%dT%H%M%SZ')}",
      "source_id":source_id,"source_revision":s["revision"],"decision_timestamp":now.isoformat().replace("+00:00","Z"),
      "target_use":target_use,"decision":decision,"evidence_refs":evidence,"checks":checks,
      "rationale":reasons or ["All required admission checks passed."],"reviewer_id":reviewer_id,
      "policy_version":policy_version,"revalidation_due":s.get("valid_until")}
    validate_schema(record,DECISION_SCHEMA)
    return record

def write_new_decision(record,output):
    validate_schema(record,DECISION_SCHEMA); output=Path(output).absolute()
    if output.exists() or output.is_symlink(): raise ValueError("decision output exists or is a symlink; refusing overwrite")
    if not output.parent.is_dir(): raise ValueError("decision output parent directory must exist")
    with output.open("x",encoding="utf-8",newline="") as f: json.dump(record,f,ensure_ascii=False,sort_keys=True,indent=2); f.write("\n")

def main(argv=None):
    p=argparse.ArgumentParser(description="Offline source registry and admission gate")
    sub=p.add_subparsers(dest="command",required=True)
    v=sub.add_parser("validate"); v.add_argument("--registry",required=True,type=Path)
    e=sub.add_parser("evaluate"); e.add_argument("--registry",required=True,type=Path); e.add_argument("--source-id",required=True)
    e.add_argument("--use",required=True,choices=USES); e.add_argument("--decision-output",required=True,type=Path)
    e.add_argument("--reviewer-id",required=True); e.add_argument("--policy-version",default="1.0.0")
    a=p.parse_args(argv)
    try:
        registry=load_json(a.registry)
        if a.command=="validate":
            ids=validate_registry(registry); print(json.dumps({"status":"valid","source_count":len(ids),"source_ids":ids},sort_keys=True))
        else:
            result=evaluate_source(registry,a.source_id,a.use,reviewer_id=a.reviewer_id,policy_version=a.policy_version)
            write_new_decision(result,a.decision_output); print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},ensure_ascii=False),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
