from __future__ import annotations

from datetime import datetime, timedelta
from math import isfinite
from typing import Iterable

from .broker_profiles import BrokerProfile, to_utc
from .ingest import Bar
from .quality import parse_source_time, timeframe_minutes

FEATURE_VERSION = "price-action-0.2.0"


def _true_range(bar: Bar, previous_close: float | None) -> float:
    if previous_close is None:
        return bar.high - bar.low
    return max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close))


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    return ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def compute_price_action_features(
    bars: Iterable[Bar], *, pivot_left: int = 3, pivot_right: int = 3,
    atr_period: int = 14, equal_level_atr_tolerance: float = 0.10,
    fvg_min_atr: float = 0.05, ob_lookback: int = 8,
    broker_profile: BrokerProfile | None = None,
    source_sha256: str | None = None,
    include_last_bar: bool = False,
) -> list[dict]:
    """Causal, bar-close feature events. No future bar is read at an event's availability time.

    Swing pivots are emitted only after right-side confirmation bars have closed.
    FVG/OB are operational hypotheses, not claims about hidden institutional orders.
    """
    rows = list(bars)
    if rows and not include_last_bar:
        rows = rows[:-1]  # The newest exported candle may still be forming.
    if pivot_left < 1 or pivot_right < 1 or atr_period < 1 or ob_lookback < 1:
        raise ValueError("pivot_left, pivot_right and atr_period must be positive")
    if equal_level_atr_tolerance < 0 or fvg_min_atr < 0:
        raise ValueError("ATR tolerances cannot be negative")
    times = [parse_source_time(b) for b in rows]
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("Bars must be strictly time-ordered with no duplicate timestamps")
    tr = [_true_range(b, rows[i-1].close if i else None) for i, b in enumerate(rows)]
    atr: list[float | None] = []
    for i in range(len(rows)):
        window = tr[max(0, i - atr_period + 1):i + 1]
        atr.append(sum(window) / atr_period if len(window) == atr_period else None)

    events: list[dict] = []
    confirmed_highs: list[tuple[int, float]] = []
    confirmed_lows: list[tuple[int, float]] = []
    last_structure = "UNDETERMINED"
    last_broken_high_origin: int | None = None
    last_broken_low_origin: int | None = None
    previous_close = None
    prior_atr_values: list[float] = []
    active_fvgs: list[dict] = []
    active_order_blocks: list[dict] = []
    latest_equal_high_pool: dict | None = None
    latest_equal_low_pool: dict | None = None

    for i, bar in enumerate(rows):
        a = atr[i]
        available_at_utc = None
        availability_status = "UNRESOLVED_BAR_TIMESTAMP_CONVENTION"
        if broker_profile is not None:
            source_utc, source_status = to_utc(bar.source_timestamp, bar.timestamp_precision, broker_profile)
            if source_utc is None:
                availability_status = source_status
            elif broker_profile.bar_timestamp_convention == "interval_end":
                available_at_utc = source_utc
                availability_status = "RESOLVED_AT_INTERVAL_END"
            elif bar.timeframe.startswith(("M", "H")) and timeframe_minutes(bar.timeframe) is not None:
                minutes = timeframe_minutes(bar.timeframe)
                available_at_utc = (datetime.fromisoformat(source_utc) + timedelta(minutes=minutes)).isoformat()
                availability_status = "RESOLVED_AT_INTERVAL_CLOSE"
            else:
                availability_status = "SESSION_CALENDAR_REQUIRED_FOR_INTERVAL_CLOSE"
        fvg_zone_updates = []
        for zone in active_fvgs:
            if zone["status"] in {"FULLY_FILLED", "INVALIDATED"}:
                continue
            width = zone["upper"] - zone["lower"]
            if width <= 0:
                continue
            if zone["type"] == "BULLISH_FVG":
                fraction = min(1.0, max(0.0, (zone["upper"] - max(bar.low, zone["lower"])) / width)) if bar.low <= zone["upper"] else 0.0
                invalidated = bar.close < zone["lower"]
            else:
                fraction = min(1.0, max(0.0, (min(bar.high, zone["upper"]) - zone["lower"]) / width)) if bar.high >= zone["lower"] else 0.0
                invalidated = bar.close > zone["upper"]
            if fraction > zone["fill_fraction"] or invalidated:
                zone["fill_fraction"] = max(zone["fill_fraction"], fraction)
                zone["status"] = "INVALIDATED" if invalidated else "FULLY_FILLED" if zone["fill_fraction"] >= 1.0 else "PARTIALLY_FILLED"
                fvg_zone_updates.append({"zone_id": zone["zone_id"], "status": zone["status"], "fill_fraction": round(zone["fill_fraction"], 6), "invalidated": invalidated})

        order_block_updates = []
        for zone in active_order_blocks:
            if zone["status"] == "INVALIDATED":
                continue
            touched = bar.low <= zone["upper"] and bar.high >= zone["lower"]
            invalidated = bar.close < zone["lower"] if zone["direction"] == "BULLISH" else bar.close > zone["upper"]
            if invalidated and zone["status"] != "INVALIDATED":
                zone["status"] = "INVALIDATED"
                order_block_updates.append({"zone_id": zone["zone_id"], "status": zone["status"], "touched": touched, "invalidated": True})
            elif touched and zone["status"] == "ACTIVE":
                zone["status"] = "MITIGATED"
                order_block_updates.append({"zone_id": zone["zone_id"], "status": zone["status"], "touched": True, "invalidated": False})

        # Retain only zones whose lifecycle is still active; terminal updates are
        # emitted once, preventing an ever-growing historical scan on long series.
        active_fvgs[:] = [zone for zone in active_fvgs if zone["status"] not in {"FULLY_FILLED", "INVALIDATED"}]
        active_order_blocks[:] = [zone for zone in active_order_blocks if zone["status"] != "INVALIDATED"]

        event = {
            "feature_version": FEATURE_VERSION,
            "instrument": bar.instrument,
            "timeframe": bar.timeframe,
            "source_file": bar.source_file,
            "source_sha256": source_sha256,
            "source_row_number": i + 2,
            "source_timestamp": bar.source_timestamp,
            "event_index": i,
            "feature_parameters": {"pivot_left": pivot_left, "pivot_right": pivot_right, "atr_period": atr_period, "equal_level_atr_tolerance": equal_level_atr_tolerance, "fvg_min_atr": fvg_min_atr, "ob_lookback": ob_lookback, "include_last_bar": include_last_bar},
            "available_at_utc": available_at_utc,
            "availability_time_status": availability_status,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "tick_volume": bar.tick_volume,
            "spread_points": bar.spread_points,
            "atr": a,
            "true_range": tr[i],
            "body": abs(bar.close - bar.open),
            "body_to_range": abs(bar.close - bar.open) / (bar.high - bar.low) if bar.high > bar.low else 0.0,
            "displacement": None,
            "volatility_ratio": None,
            "volatility_state": "WARMUP",
            "close_location": (bar.close - bar.low) / (bar.high - bar.low) if bar.high > bar.low else 0.5,
            "return_1": (bar.close / previous_close - 1.0) if previous_close else None,
            "swing_high_confirmed": False,
            "swing_low_confirmed": False,
            "bos": None,
            "choch": None,
            "fvg": None,
            "liquidity_sweep": None,
            "equal_high_pool": None,
            "equal_low_pool": None,
            "order_block_candidate": None,
            "price_gap": None,
            "fvg_zone_updates": fvg_zone_updates,
            "order_block_updates": order_block_updates,
        }

        # Pivot at p becomes knowable only on bar i=p+pivot_right.
        p = i - pivot_right
        if p >= pivot_left:
            left = rows[p-pivot_left:p]
            right = rows[p+1:i+1]
            candidate = rows[p]
            if all(candidate.high > x.high for x in left) and all(candidate.high >= x.high for x in right):
                confirmed_highs.append((p, candidate.high))
                event["swing_high_confirmed"] = True
                event["confirmed_swing_high"] = candidate.high
                event["swing_high_origin_index"] = p
            if all(candidate.low < x.low for x in left) and all(candidate.low <= x.low for x in right):
                confirmed_lows.append((p, candidate.low))
                event["swing_low_confirmed"] = True
                event["confirmed_swing_low"] = candidate.low
                event["swing_low_origin_index"] = p

        if confirmed_highs and bar.close > confirmed_highs[-1][1] and confirmed_highs[-1][0] != last_broken_high_origin:
            direction = "BULLISH"
            event["bos"] = "BULLISH_BREAK_OF_CONFIRMED_SWING_HIGH"
            last_broken_high_origin = confirmed_highs[-1][0]
            if last_structure == "BEARISH":
                event["choch"] = "BULLISH_CHOCH"
            last_structure = direction
        elif confirmed_lows and bar.close < confirmed_lows[-1][1] and confirmed_lows[-1][0] != last_broken_low_origin:
            direction = "BEARISH"
            event["bos"] = "BEARISH_BREAK_OF_CONFIRMED_SWING_LOW"
            last_broken_low_origin = confirmed_lows[-1][0]
            if last_structure == "BULLISH":
                event["choch"] = "BEARISH_CHOCH"
            last_structure = direction

        if a and i >= 2:
            older = rows[i-2]
            min_gap = a * fvg_min_atr
            if bar.low - older.high >= min_gap and bar.low > older.high:
                event["fvg"] = {"type": "BULLISH_FVG", "lower": older.high, "upper": bar.low, "size": bar.low-older.high}
            elif older.low - bar.high >= min_gap and older.low > bar.high:
                event["fvg"] = {"type": "BEARISH_FVG", "lower": bar.high, "upper": older.low, "size": older.low-bar.high}

            tolerance = a * equal_level_atr_tolerance
            if event["swing_high_confirmed"] and len(confirmed_highs) >= 2:
                prior_highs = [v for _, v in confirmed_highs[-101:-1] if abs(v-confirmed_highs[-1][1]) <= tolerance]
                if prior_highs:
                    event["equal_high_pool"] = {"level": _median(prior_highs + [confirmed_highs[-1][1]]), "touch_count": len(prior_highs)+1}
                    latest_equal_high_pool = event["equal_high_pool"]
            if event["swing_low_confirmed"] and len(confirmed_lows) >= 2:
                prior_lows = [v for _, v in confirmed_lows[-101:-1] if abs(v-confirmed_lows[-1][1]) <= tolerance]
                if prior_lows:
                    event["equal_low_pool"] = {"level": _median(prior_lows + [confirmed_lows[-1][1]]), "touch_count": len(prior_lows)+1}
                    latest_equal_low_pool = event["equal_low_pool"]
            if confirmed_highs and bar.high > confirmed_highs[-1][1] and bar.close < confirmed_highs[-1][1]:
                event["liquidity_sweep"] = {"side": "BUY_SIDE_LIQUIDITY", "reference_level": confirmed_highs[-1][1], "reclaimed": True}
            elif confirmed_lows and bar.low < confirmed_lows[-1][1] and bar.close > confirmed_lows[-1][1]:
                event["liquidity_sweep"] = {"side": "SELL_SIDE_LIQUIDITY", "reference_level": confirmed_lows[-1][1], "reclaimed": True}

            # Transparent heuristic: last opposite candle before a confirmed close-through BOS.
            if event["bos"]:
                bullish = event["bos"].startswith("BULLISH")
                start = max(0, i - ob_lookback)
                for j in range(i-1, start-1, -1):
                    opposite = rows[j].close < rows[j].open if bullish else rows[j].close > rows[j].open
                    if opposite:
                        event["order_block_candidate"] = {
                            "type": "BULLISH_ORDER_BLOCK_CANDIDATE" if bullish else "BEARISH_ORDER_BLOCK_CANDIDATE",
                            "lower": rows[j].low, "upper": rows[j].high,
                            "origin_index": j,
                            "definition": "Last opposite-colour candle within lookback before close-through of latest confirmed swing; heuristic, not proof of institutional orders.",
                        }
                        break

        if previous_close is not None and a and abs(bar.open - previous_close) >= a * 0.10:
            event["price_gap"] = {
                "direction": "UP" if bar.open > previous_close else "DOWN",
                "size": abs(bar.open - previous_close),
                "previous_close": previous_close,
                "current_open": bar.open,
                "threshold": "0.10 * current ATR; candidate discontinuity only, session/weekend cause not inferred",
            }
        if a and isfinite(a) and a > 0:
            event["range_to_atr"] = (bar.high-bar.low)/a
            event["body_to_atr"] = abs(bar.close-bar.open)/a
            event["displacement"] = bool(event["body_to_atr"] >= 1.5 and event["body_to_range"] >= 0.65)
            baseline = _median(prior_atr_values[-100:]) if len(prior_atr_values) >= 20 else None
            if baseline and baseline > 0:
                event["volatility_ratio"] = a / baseline
                event["volatility_state"] = "EXPANSION" if a / baseline >= 1.5 else "CONTRACTION" if a / baseline <= 0.67 else "NORMAL"
            prior_atr_values.append(a)
        else:
            event["range_to_atr"] = None
            event["body_to_atr"] = None

        if event["fvg"] is not None:
            zone_id = f"fvg:{bar.instrument}:{bar.timeframe}:{i}"
            event["fvg"].update({"zone_id": zone_id, "status": "ACTIVE", "fill_fraction": 0.0})
            active_fvgs.append({
                "zone_id": zone_id, "type": event["fvg"]["type"],
                "lower": event["fvg"]["lower"], "upper": event["fvg"]["upper"],
                "status": "ACTIVE", "fill_fraction": 0.0,
            })
        if event["order_block_candidate"] is not None:
            candidate = event["order_block_candidate"]
            zone_id = f"ob:{bar.instrument}:{bar.timeframe}:{i}"
            candidate.update({"zone_id": zone_id, "status": "ACTIVE"})
            active_order_blocks.append({
                "zone_id": zone_id,
                "direction": "BULLISH" if candidate["type"].startswith("BULLISH") else "BEARISH",
                "lower": candidate["lower"], "upper": candidate["upper"], "status": "ACTIVE",
            })

        event.update({
            "structure_direction": last_structure,
            "last_confirmed_swing_high": confirmed_highs[-1][1] if confirmed_highs else None,
            "last_confirmed_swing_high_origin_index": confirmed_highs[-1][0] if confirmed_highs else None,
            "last_confirmed_swing_low": confirmed_lows[-1][1] if confirmed_lows else None,
            "last_confirmed_swing_low_origin_index": confirmed_lows[-1][0] if confirmed_lows else None,
            "latest_equal_high_pool": latest_equal_high_pool,
            "latest_equal_low_pool": latest_equal_low_pool,
            "active_fvg_zones": [
                {key: zone[key] for key in ("zone_id", "type", "lower", "upper", "status", "fill_fraction")}
                for zone in active_fvgs if zone["status"] in {"ACTIVE", "PARTIALLY_FILLED"}
            ][-20:],
            "active_order_block_zones": [
                {key: zone[key] for key in ("zone_id", "direction", "lower", "upper", "status")}
                for zone in active_order_blocks if zone["status"] in {"ACTIVE", "MITIGATED"}
            ][-20:],
        })
        events.append(event)
        previous_close = bar.close
    return events
