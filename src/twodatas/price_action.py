from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from math import isfinite
from typing import Iterable

from .ingest import Bar
from .quality import parse_source_time

FEATURE_VERSION = "price-action-0.1.0"


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
) -> list[dict]:
    """Causal, bar-close feature events. No future bar is read at an event's availability time.

    Swing pivots are emitted only after right-side confirmation bars have closed.
    FVG/OB are operational hypotheses, not claims about hidden institutional orders.
    """
    rows = list(bars)
    if pivot_left < 1 or pivot_right < 1 or atr_period < 1:
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

    for i, bar in enumerate(rows):
        a = atr[i]
        event = {
            "feature_version": FEATURE_VERSION,
            "instrument": bar.instrument,
            "timeframe": bar.timeframe,
            "source_file": bar.source_file,
            "source_timestamp": bar.source_timestamp,
            "event_index": i,
            "available_at_source_timestamp": bar.source_timestamp,
            "atr": a,
            "true_range": tr[i],
            "body": abs(bar.close - bar.open),
            "body_to_range": abs(bar.close - bar.open) / (bar.high - bar.low) if bar.high > bar.low else 0.0,
            "displacement": None,
            "volatility_ratio": None,
            "volatility_state": "WARMUP",
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
            older, middle = rows[i-2], rows[i-1]
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
            if event["swing_low_confirmed"] and len(confirmed_lows) >= 2:
                prior_lows = [v for _, v in confirmed_lows[-101:-1] if abs(v-confirmed_lows[-1][1]) <= tolerance]
                if prior_lows:
                    event["equal_low_pool"] = {"level": _median(prior_lows + [confirmed_lows[-1][1]]), "touch_count": len(prior_lows)+1}
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

        events.append(event)
        previous_close = bar.close
    return events
