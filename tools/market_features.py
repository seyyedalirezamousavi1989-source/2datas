"""Causal market-feature extraction from ordered, completed OHLC bars."""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable
import hashlib, json

def _time(value: str, field: str) -> datetime:
    if not isinstance(value, str): raise ValueError(f"{field} must be an ISO-8601 timestamp")
    try: dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise ValueError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError(f"{field} must include an explicit timezone")
    return dt.astimezone(timezone.utc)

def _dec(value: Any, field: str) -> Decimal:
    if not isinstance(value, (str, int)) or isinstance(value, bool): raise ValueError(f"{field} must be a decimal string or integer")
    try: result = Decimal(str(value))
    except InvalidOperation as exc: raise ValueError(f"{field} must be a valid decimal") from exc
    if not result.is_finite(): raise ValueError(f"{field} must be finite")
    return result

def extract_market_features(bars: Iterable[dict[str, Any]], *, decision_timestamp: str,
                            pivot_left: int = 2, pivot_right: int = 2,
                            atr_period: int = 14) -> dict[str, Any]:
    """Extract causal swings, BOS/CHoCH, FVG, liquidity sweeps and ATR."""
    cutoff = _time(decision_timestamp, "decision_timestamp")
    for name, value in (("pivot_left", pivot_left), ("pivot_right", pivot_right), ("atr_period", atr_period)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1: raise ValueError(f"{name} must be a positive integer")
    source = list(bars); admitted = []; previous_start = None; seen = set()
    for index, row in enumerate(source):
        if not isinstance(row, dict): raise ValueError("each bar must be an object")
        required = ("record_id","instrument_id","provider","price_basis","timeframe","interval_start","interval_end","available_at","completion_status","open","high","low","close")
        if any(k not in row for k in required): raise ValueError(f"bar {index} is missing required fields")
        if not isinstance(row["record_id"], str) or not row["record_id"]: raise ValueError("record_id must be a non-empty string")
        if row["record_id"] in seen: raise ValueError("record_id values must be unique")
        seen.add(row["record_id"])
        start,end = _time(row["interval_start"],"interval_start"),_time(row["interval_end"],"interval_end")
        available = _time(row["available_at"],"available_at")
        if end <= start: raise ValueError("interval_end must be later than interval_start")
        if previous_start is not None and start <= previous_start: raise ValueError("bars must be strictly chronological with no duplicate or out-of-order starts")
        previous_start = start
        if row["completion_status"] not in {"COMPLETE","PARTIAL"}: raise ValueError("completion_status must be COMPLETE or PARTIAL")
        if row["completion_status"] == "COMPLETE" and available < end: raise ValueError("completed bar cannot be available before interval_end")
        o,h,l,c = (_dec(row[k],k) for k in ("open","high","low","close"))
        if h < max(o,c,l) or l > min(o,c,h) or h < l: raise ValueError(f"bar {index} violates OHLC invariants")
        if row["completion_status"] == "COMPLETE" and end <= cutoff and available <= cutoff:
            admitted.append({**row,"_start":start,"_end":end,"_available":available,"_o":o,"_h":h,"_l":l,"_c":c})

    events=[]; pivots=[]; n=len(admitted)
    for i in range(pivot_left,n-pivot_right):
        window=admitted[i-pivot_left:i+pivot_right+1]; candidate=admitted[i]
        highs=[x["_h"] for x in window]; lows=[x["_l"] for x in window]
        if highs.count(candidate["_h"]) == 1 and candidate["_h"] == max(highs):
            pivots.append({"kind":"SWING_HIGH","index":i,"price":candidate["_h"],"pivot_record_id":candidate["record_id"],"confirmed_record_id":admitted[i+pivot_right]["record_id"],"available_at":admitted[i+pivot_right]["_available"]})
        if lows.count(candidate["_l"]) == 1 and candidate["_l"] == min(lows):
            pivots.append({"kind":"SWING_LOW","index":i,"price":candidate["_l"],"pivot_record_id":candidate["record_id"],"confirmed_record_id":admitted[i+pivot_right]["record_id"],"available_at":admitted[i+pivot_right]["_available"]})
    pivots.sort(key=lambda p:(p["index"],p["kind"]))
    for p in pivots:
        events.append({"event_type":p["kind"],"event_record_id":p["pivot_record_id"],"confirmed_by_record_id":p["confirmed_record_id"],"event_time":admitted[p["index"]]["interval_end"].isoformat().replace("+00:00","Z"),"available_at":p["available_at"].isoformat().replace("+00:00","Z"),"price":str(p["price"]),"causal":True})

    last_high=last_low=None; trend="UNDEFINED"; broken_high=set(); broken_low=set()
    for i,bar in enumerate(admitted):
        eligible=[p for p in pivots if p["index"]+pivot_right < i]
        highs=[p for p in eligible if p["kind"]=="SWING_HIGH"]; lows=[p for p in eligible if p["kind"]=="SWING_LOW"]
        if highs: last_high=highs[-1]
        if lows: last_low=lows[-1]
        if last_high and last_high["pivot_record_id"] not in broken_high and bar["_c"] > last_high["price"]:
            kind="BOS_BULLISH" if trend in {"BULLISH","UNDEFINED"} else "CHOCH_BULLISH"
            events.append({"event_type":kind,"event_record_id":bar["record_id"],"reference_pivot_record_id":last_high["pivot_record_id"],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"price":str(bar["_c"]),"causal":True})
            trend="BULLISH"; broken_high.add(last_high["pivot_record_id"])
        if last_low and last_low["pivot_record_id"] not in broken_low and bar["_c"] < last_low["price"]:
            kind="BOS_BEARISH" if trend in {"BEARISH","UNDEFINED"} else "CHOCH_BEARISH"
            events.append({"event_type":kind,"event_record_id":bar["record_id"],"reference_pivot_record_id":last_low["pivot_record_id"],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"price":str(bar["_c"]),"causal":True})
            trend="BEARISH"; broken_low.add(last_low["pivot_record_id"])
        if last_high and bar["_h"] > last_high["price"] and bar["_c"] < last_high["price"]:
            events.append({"event_type":"BUYSIDE_LIQUIDITY_SWEEP","event_record_id":bar["record_id"],"reference_pivot_record_id":last_high["pivot_record_id"],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"swept_level":str(last_high["price"]),"causal":True})
        if last_low and bar["_l"] < last_low["price"] and bar["_c"] > last_low["price"]:
            events.append({"event_type":"SELLSIDE_LIQUIDITY_SWEEP","event_record_id":bar["record_id"],"reference_pivot_record_id":last_low["pivot_record_id"],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"swept_level":str(last_low["price"]),"causal":True})
        if i>=2:
            first=admitted[i-2]
            if bar["_l"] > first["_h"]:
                events.append({"event_type":"FVG_BULLISH","event_record_id":bar["record_id"],"reference_record_ids":[first["record_id"],admitted[i-1]["record_id"],bar["record_id"]],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"zone_low":str(first["_h"]),"zone_high":str(bar["_l"]),"causal":True})
            if bar["_h"] < first["_l"]:
                events.append({"event_type":"FVG_BEARISH","event_record_id":bar["record_id"],"reference_record_ids":[first["record_id"],admitted[i-1]["record_id"],bar["record_id"]],"event_time":bar["_end"].isoformat().replace("+00:00","Z"),"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"zone_low":str(bar["_h"]),"zone_high":str(first["_l"]),"causal":True})

    atr=[]; trs=[]
    for i,bar in enumerate(admitted):
        prev=admitted[i-1]["_c"] if i else bar["_c"]
        tr=max(bar["_h"]-bar["_l"],abs(bar["_h"]-prev),abs(bar["_l"]-prev)); trs.append(tr)
        if i+1>=atr_period:
            atr.append({"record_id":bar["record_id"],"available_at":bar["_available"].isoformat().replace("+00:00","Z"),"true_range":str(tr),"atr":str(sum(trs[i+1-atr_period:i+1])/Decimal(atr_period)),"period":atr_period,"causal":True})
    events.sort(key=lambda e:(e["available_at"],e["event_type"],e["event_record_id"]))
    output={"schema_version":"1.0.0","engine":"causal_market_features","decision_timestamp":cutoff.isoformat().replace("+00:00","Z"),
      "instrument_id":admitted[-1]["instrument_id"] if admitted else None,"provider":admitted[-1]["provider"] if admitted else None,
      "price_basis":admitted[-1]["price_basis"] if admitted else None,"timeframe":admitted[-1]["timeframe"] if admitted else None,
      "admitted_bar_count":len(admitted),"events":events,"atr":atr,
      "diagnostics":{"future_bars_used":False,"input_mutated":False,"network_access":False,"market_data_written":False,
      "order_blocks_emitted":False,"order_block_policy":"deferred: requires explicit versioned displacement and mitigation definitions",
      "note":"Research features only; not trade recommendations or calibrated probabilities."}}
    output["feature_fingerprint"]=hashlib.sha256(json.dumps(output,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return output
