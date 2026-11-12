"""Offline multi-source canonical OHLCV comparison; never selects or merges feeds."""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

IDENTITY=("instrument_id","timeframe","event_time","price_basis")
PRICES=("open","high","low","close")
SOURCE=("provider","venue","source_artifact_id","source_record_id")

def dec(value: Any, label: str) -> Decimal:
    if not isinstance(value,str): raise ValueError(f"{label} must be a decimal string")
    try: number=Decimal(value)
    except InvalidOperation as exc: raise ValueError(f"{label} is invalid") from exc
    if not number.is_finite(): raise ValueError(f"{label} must be finite")
    return number

def timestamp_seconds(value: str) -> Decimal:
    try: parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc: raise ValueError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None: raise ValueError("timestamp timezone is required")
    delta=parsed.astimezone(timezone.utc)-datetime(1970,1,1,tzinfo=timezone.utc)
    return Decimal(delta.days*86400+delta.seconds)+Decimal(delta.microseconds)/Decimal(1000000)

def read_records(path: Path) -> list[dict[str,Any]]:
    result=[]
    with path.open(encoding="utf-8") as stream:
        for n,line in enumerate(stream,1):
            if not line.strip(): continue
            try: row=json.loads(line)
            except json.JSONDecodeError as exc: raise ValueError(f"{path}:{n}: invalid JSON") from exc
            if not isinstance(row,dict): raise ValueError(f"{path}:{n}: expected object")
            for field in IDENTITY+SOURCE+PRICES+("available_at","recorded_at"):
                if not isinstance(row.get(field),str) or not row[field]: raise ValueError(f"{path}:{n}: missing {field}")
            for field in PRICES:
                if dec(row[field],field)<=0: raise ValueError(f"{path}:{n}: {field} must be positive")
            timestamp_seconds(row["available_at"]); timestamp_seconds(row["recorded_at"])
            result.append(row)
    return result

def source_ref(row):
    return {key:row[key] for key in SOURCE}

def reconcile_records(inputs: list[tuple[str,list[dict[str,Any]]]], tolerance: Decimal) -> dict[str,Any]:
    if not tolerance.is_finite() or tolerance<0: raise ValueError("tolerance must be finite and non-negative")
    groups=defaultdict(list)
    for name,records in inputs:
        for n,row in enumerate(records,1):
            item=dict(row); item["_input"]=name; item["_row"]=n
            groups[tuple(item[k] for k in IDENTITY)].append(item)
    observations=[]; stats=defaultdict(lambda:{"observations":0,"compared_pairs":0,"within_tolerance_pairs":0,"divergent_pairs":0})
    for identity in sorted(groups):
        rows=sorted(groups[identity],key=lambda r:tuple(r[k] for k in SOURCE)+(r["_input"],r["_row"]))
        for r in rows: stats[r["provider"]]["observations"]+=1
        dup=sorted({p for p in (r["provider"] for r in rows) if sum(x["provider"]==p for x in rows)>1})
        entry={"identity":dict(zip(IDENTITY,identity)),"sources":[source_ref(r) for r in rows],"comparisons":[]}
        if dup:
            entry.update(status="ambiguous_duplicate_source",duplicate_providers=dup)
        elif len(rows)<2:
            entry["status"]="insufficient_sources"
        else:
            for i,left in enumerate(rows):
                for right in rows[i+1:]:
                    deltas={f:abs(dec(left[f],f)-dec(right[f],f)) for f in PRICES}
                    maximum=max(deltas.values()); passed=maximum<=tolerance
                    volume="not_comparable"
                    if left.get("volume") not in (None,"") and right.get("volume") not in (None,""):
                        if left.get("volume_unit") and left.get("volume_unit")==right.get("volume_unit"):
                            volume="equal" if dec(left["volume"],"volume")==dec(right["volume"],"volume") else "different"
                        else: volume="unit_mismatch_or_missing"
                    available_delta=abs(timestamp_seconds(left["available_at"])-timestamp_seconds(right["available_at"]))
                    entry["comparisons"].append({
                        "source_a":source_ref(left),"source_b":source_ref(right),
                        "absolute_price_deltas":{k:format_decimal(v) for k,v in deltas.items()},
                        "max_absolute_price_delta":format_decimal(maximum),
                        "price_status":"within_tolerance" if passed else "divergent",
                        "volume_status":volume,
                        "available_at_delta_seconds":format_decimal(available_delta)})
                    for provider in (left["provider"],right["provider"]):
                        stats[provider]["compared_pairs"]+=1
                        stats[provider]["within_tolerance_pairs" if passed else "divergent_pairs"]+=1
            statuses={x["price_status"] for x in entry["comparisons"]}
            entry["status"]="divergent" if "divergent" in statuses else "all_within_tolerance"
        observations.append(entry)
    counts=defaultdict(int)
    for item in observations: counts[item["status"]]+=1
    return {"report_schema_version":"1.0.0","engine_version":"1.0.0",
      "comparison_policy":{"identity_fields":list(IDENTITY),"price_fields":list(PRICES),
       "absolute_price_tolerance":format_decimal(tolerance),
       "price_rule":"maximum absolute OHLC difference <= declared tolerance",
       "volume_rule":"compare only identical explicit units; no conversion","source_selection":"none"},
      "summary":{"observation_groups":len(observations),
       "all_within_tolerance":counts["all_within_tolerance"],"divergent":counts["divergent"],
       "insufficient_sources":counts["insufficient_sources"],
       "ambiguous_duplicate_source":counts["ambiguous_duplicate_source"]},
      "provider_statistics":{k:stats[k] for k in sorted(stats)},"observations":observations}

def format_decimal(value: Decimal) -> str:
    text=format(value,"f")
    return text.rstrip("0").rstrip(".") if "." in text else text

def reconcile_files(paths: list[Path], output: Path, tolerance: Decimal) -> dict[str,Any]:
    if len({p.resolve(strict=True) for p in paths})!=len(paths): raise ValueError("duplicate input path")
    resolved=[p.resolve(strict=True) for p in paths]
    if any(not p.is_file() for p in resolved): raise ValueError("inputs must be regular files")
    dest=output.absolute()
    if dest.exists() or dest.is_symlink(): raise ValueError("report exists or is a symlink; refusing overwrite")
    if not dest.parent.is_dir(): raise ValueError("report parent directory must exist")
    report=reconcile_records([(str(p),read_records(p)) for p in resolved],tolerance)
    with dest.open("x",encoding="utf-8",newline="") as f: json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2); f.write("\n")
    return {"status":"completed","report":str(dest),**report["summary"]}

def main(argv=None):
    parser=argparse.ArgumentParser(description="Compare explicit canonical OHLCV feeds without selecting or merging")
    parser.add_argument("--input",action="append",required=True,type=Path)
    parser.add_argument("--absolute-price-tolerance",required=True)
    parser.add_argument("--report",required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        result=reconcile_files(args.input,args.report,dec(args.absolute_price_tolerance,"tolerance"))
        print(json.dumps(result,indent=2,sort_keys=True)); return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({"status":"error","error":str(exc)}),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
