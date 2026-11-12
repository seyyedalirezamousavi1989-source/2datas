"""Read-only OHLC quality audit for one explicitly supplied CSV/JSONL file."""
import argparse,csv,json,math,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

def _time(v):
    if not isinstance(v,str): return None
    try: d=datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError: return None
    return d.astimezone(timezone.utc) if d.tzinfo and d.utcoffset() is not None else None

def _read(p):
    if p.suffix.lower()==".csv":
        with p.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
    if p.suffix.lower() in (".jsonl",".ndjson"):
        out=[]
        with p.open(encoding="utf-8") as f:
            for n,line in enumerate(f,1):
                if line.strip():
                    x=json.loads(line)
                    if not isinstance(x,dict): raise ValueError(f"Line {n} is not an object")
                    out.append(x)
        return out
    raise ValueError("Expected CSV, JSONL, or NDJSON")

def audit_records(records,timestamp_field="event_time",key_fields=("instrument_id","timeframe","event_time"),expected_interval_seconds=None,volume_field="volume"):
    rows=list(records); issues=[]; seen={}; prev={}; gaps=[]; times=[]; counts=Counter()
    def issue(sev,code,row,msg): issues.append({"severity":sev,"code":code,"row":row,"message":msg})
    for n,r in enumerate(rows,1):
        fields=(timestamp_field,"open","high","low","close")
        missing=[k for k in fields if not isinstance(r,dict) or r.get(k) in (None,"")]
        if missing: issue("error","REQUIRED_FIELD_MISSING",n,"Missing: "+", ".join(missing)); counts["structural"]+=1; continue
        ts=_time(r[timestamp_field])
        if ts is None: issue("error","TIMESTAMP_INVALID_OR_NAIVE",n,"Timestamp needs explicit timezone."); counts["timestamp"]+=1; continue
        times.append(ts); vals={}
        for k in ("open","high","low","close"):
            try:
                vals[k]=float(r[k])
                if not math.isfinite(vals[k]): raise ValueError
            except (ValueError,TypeError,OverflowError): issue("error","OHLC_NON_FINITE_OR_NON_NUMERIC",n,f"{k} must be finite."); counts["ohlc"]+=1
        if len(vals)==4:
            o,h,l,c=(vals[k] for k in ("open","high","low","close")); bad=[]
            if h<max(o,c): bad.append("high < max(open, close)")
            if l>min(o,c): bad.append("low > min(open, close)")
            if h<l: bad.append("high < low")
            if bad: issue("error","OHLC_INVARIANT_VIOLATION",n,"; ".join(bad)); counts["ohlc"]+=1
        if volume_field and r.get(volume_field) not in (None,""):
            try:
                v=float(r[volume_field])
                if not math.isfinite(v) or v<0: raise ValueError
            except (ValueError,TypeError,OverflowError): issue("error","VOLUME_INVALID",n,"Volume must be finite and non-negative."); counts["volume"]+=1
        key=tuple(r.get(k) for k in key_fields)
        if key_fields and any(x in (None,"") for x in key): issue("warning","DUPLICATE_KEY_INCOMPLETE",n,"Duplicate key incomplete.")
        elif key_fields and key in seen: issue("error","DUPLICATE_CANONICAL_KEY",n,f"Duplicates row {seen[key]}."); counts["duplicates"]+=1
        elif key_fields: seen[key]=n
        stream=(r.get("instrument_id"),r.get("timeframe")); old=prev.get(stream)
        if old:
            oldts,oldrow=old
            if ts<=oldts: issue("error","TIMESTAMP_DUPLICATE" if ts==oldts else "TIMESTAMP_NOT_INCREASING",n,f"Timestamp must increase; previous row {oldrow}."); counts["ordering"]+=1
            elif expected_interval_seconds is not None and (ts-oldts).total_seconds()>expected_interval_seconds:
                delta=(ts-oldts).total_seconds(); gaps.append({"stream":list(stream),"after_row":oldrow,"before_row":n,"observed_seconds":delta})
                issue("warning","SCHEDULED_INTERVAL_GAP",n,f"Observed {delta:g}s; expected {expected_interval_seconds}s; no calendar applied.")
        if old is None or ts>old[0]: prev[stream]=(ts,n)
    errors=sum(x["severity"]=="error" for x in issues); warns=sum(x["severity"]=="warning" for x in issues); ordered=sorted(times)
    return {"report_version":"1.0.0","status":"failed" if errors else ("passed_with_warnings" if warns else "passed"),"read_only":True,
      "summary":{"records_seen":len(rows),"valid_timestamps":len(times),"streams_seen":len(prev),"duplicate_records":counts["duplicates"],"ohlc_errors":counts["ohlc"],"volume_errors":counts["volume"],"ordering_errors":counts["ordering"],"scheduled_gaps":len(gaps),"coverage":{"start_utc":ordered[0].isoformat().replace("+00:00","Z") if ordered else None,"end_utc":ordered[-1].isoformat().replace("+00:00","Z") if ordered else None}},
      "scheduled_gaps":gaps,"issues":issues,"limitations":["No trading/session/holiday/DST calendar is inferred.","Gaps are checked only with explicit expected cadence.","Duplicate identity depends on configured key fields.","This audit does not infer split leakage or episode membership.","Inputs are never sorted, repaired, interpolated, deleted, or rewritten."]}

def main(argv=None):
    p=argparse.ArgumentParser(description="Read-only OHLC dataset quality audit")
    p.add_argument("--input",required=True,type=Path); p.add_argument("--timestamp-field",default="event_time"); p.add_argument("--key-fields",default="instrument_id,timeframe,event_time"); p.add_argument("--expected-interval-seconds",type=int); p.add_argument("--volume-field",default="volume"); p.add_argument("--report",type=Path); a=p.parse_args(argv)
    try:
        if not a.input.is_file(): raise ValueError("Input file does not exist")
        if a.expected_interval_seconds is not None and a.expected_interval_seconds<=0: raise ValueError("Expected interval must be positive")
        result=audit_records(_read(a.input),a.timestamp_field,tuple(x.strip() for x in a.key_fields.split(",") if x.strip()),a.expected_interval_seconds,a.volume_field or None)
        rendered=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\\n"
        if a.report:
            if not a.report.parent.is_dir(): raise ValueError("Report parent directory must exist")
            a.report.write_text(rendered,encoding="utf-8")
        print(rendered,end=""); return 1 if result["status"]=="failed" else 0
    except (OSError,ValueError,json.JSONDecodeError,csv.Error) as e:
        print(json.dumps({"status":"error","fatal_error":str(e)},indent=2)); return 2
if __name__=="__main__": sys.exit(main())
