"""Offline-only acquisition simulation. No network or real market-data access."""
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import hashlib, json

def utc_timestamp(value, source_timezone=None):
    try:
        dt=datetime.fromisoformat(value.replace("Z","+00:00"))
        if dt.tzinfo is None:
            if not source_timezone: raise ValueError("naive timestamp requires an explicit source timezone")
            dt=dt.replace(tzinfo=ZoneInfo(source_timezone))
    except (ValueError,ZoneInfoNotFoundError) as exc:
        raise ValueError(f"invalid timestamp or timezone: {exc}") from exc
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z")

def request_fingerprint(request):
    raw=json.dumps(request,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def classify_error(code):
    return {"timeout":"transient","connection_reset":"transient","rate_limit":"rate_limited",
      "auth_required":"auth_required","unsupported":"unsupported","invalid_request":"permanent"}.get(code,"permanent")

class SyntheticAdapter:
    adapter_id="synthetic.fixture.v1"
    network_enabled=False
    _rows=(
      {"timestamp":"2025-01-01T00:00:00Z","open":"1.1000","high":"1.1010","low":"1.0990","close":"1.1005","volume":"10","bar_state":"closed","completeness":"complete"},
      {"timestamp":"2025-01-01T00:01:00Z","open":"1.1005","high":"1.1020","low":"1.1000","close":"1.1015","volume":"12","bar_state":"closed","completeness":"complete"},
      {"timestamp":"2025-01-01T00:02:00Z","open":"1.1015","high":"1.1030","low":"1.1010","close":"1.1020","volume":"9","bar_state":"open","completeness":"incomplete"},
      {"timestamp":"2025-01-01T00:03:00Z","open":"1.1020","high":"1.1040","low":"1.1015","close":"1.1030","volume":"8","bar_state":"closed","completeness":"incomplete"})
    def fetch_page(self,cursor=None,page_size=2):
        if page_size<1: raise ValueError("page_size must be positive")
        offset=int(cursor or "0")
        if offset<0 or offset>len(self._rows): raise ValueError("invalid cursor")
        rows=self._rows[offset:offset+page_size]
        return rows,(str(offset+len(rows)) if offset+len(rows)<len(self._rows) else None)

def collect_fixture_pages(adapter,page_size=2,max_pages=10):
    if getattr(adapter,"network_enabled",True) is not False: raise ValueError("network-capable adapter forbidden")
    cursor=None; seen=set(); rows=[]; pages=0
    while True:
        if pages>=max_pages: raise ValueError("pagination page limit exceeded")
        batch,nxt=adapter.fetch_page(cursor,page_size); pages+=1; rows.extend(batch)
        if nxt is None: break
        if nxt==cursor or nxt in seen: raise ValueError("pagination cursor loop detected")
        seen.add(nxt); cursor=nxt
    return rows,pages

def inspect_bar(row):
    warnings=[]
    if row.get("bar_state")!="closed": warnings.append("bar_not_closed")
    if row.get("completeness")!="complete": warnings.append("bar_incomplete")
    try:
        o,h,l,c=(Decimal(row[k]) for k in ("open","high","low","close"))
        if not all(x.is_finite() for x in (o,h,l,c)) or h<max(o,c) or l>min(o,c) or h<l: warnings.append("ohlc_invalid")
    except Exception: warnings.append("ohlc_unparseable")
    return warnings

def simulate(plan,adapter,run_id,started_at,page_size=2,max_pages=10):
    execution=plan.get("execution",{})
    if execution.get("status")!="planned_only" or execution.get("acquisition_authorized") is not False:
        raise ValueError("metadata-only non-authorized plan required")
    rows,pages=collect_fixture_pages(adapter,page_size,max_pages)
    fp=request_fingerprint({"plan":plan,"adapter_id":adapter.adapter_id,"page_size":page_size})
    return {"schema_version":"1.0.0","run_id":run_id,"request_fingerprint":fp,
      "idempotency_key":hashlib.sha256((run_id+fp).encode()).hexdigest(),"plan_id":plan["plan_id"],
      "adapter_id":adapter.adapter_id,"mode":"offline_fixture_only","started_at":utc_timestamp(started_at),
      "status":"simulated","pages_seen":pages,"records_seen":len(rows),
      "warnings":sorted({w for r in rows for w in inspect_bar(r)}),
      "execution":{"network_access":False,"real_market_data_read":False,"raw_artifact_written":False,"dataset_written":False}}
