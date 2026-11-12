from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class InstrumentSpec:
    source_symbol: str
    canonical_instrument: str
    digits: int
    point_size: str
    tick_size: str
    contract_size: str
    price_currency: str
    profit_currency: str
    spread_unit: str
    volume_semantics: str
    effective_from: str
    effective_to: str | None
    evidence: str
    tick_value: str | None = None
    tick_value_currency: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _positive_decimal(value: Any, field: str) -> str:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive decimal")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field} must be a positive decimal") from None
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field} must be finite and greater than zero")
    return format(number.normalize(), "f")


def validate_instrument_spec(source_symbol: str, raw: dict[str, Any]) -> InstrumentSpec:
    if not isinstance(source_symbol, str) or not source_symbol.strip():
        raise ValueError("instrument_specs keys must be non-empty source symbols")
    if not isinstance(raw, dict):
        raise ValueError(f"{source_symbol}: each specification must be a JSON object")
    required = {
        "canonical_instrument", "digits", "point_size", "tick_size", "contract_size",
        "price_currency", "profit_currency", "spread_unit", "volume_semantics",
        "effective_from", "evidence",
    }
    optional = {"effective_to", "tick_value", "tick_value_currency"}
    missing, unknown = required - set(raw), set(raw) - required - optional
    if missing:
        raise ValueError(f"{source_symbol}: missing instrument spec fields: {sorted(missing)}")
    if unknown:
        raise ValueError(f"{source_symbol}: unknown instrument spec fields: {sorted(unknown)}")
    canonical, digits = raw["canonical_instrument"], raw["digits"]
    if not isinstance(canonical, str) or not canonical.strip():
        raise ValueError(f"{source_symbol}: canonical_instrument must be non-empty")
    if isinstance(digits, bool) or not isinstance(digits, int) or not 0 <= digits <= 12:
        raise ValueError(f"{source_symbol}: digits must be an integer from 0 to 12")
    for field in ("price_currency", "profit_currency", "evidence"):
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise ValueError(f"{source_symbol}: {field} must be non-empty")
    spread_unit, volume_semantics = raw["spread_unit"], raw["volume_semantics"]
    if spread_unit not in {"points", "price", "unknown"}:
        raise ValueError(f"{source_symbol}: invalid spread_unit")
    if volume_semantics not in {"tick_count", "real_volume", "unknown"}:
        raise ValueError(f"{source_symbol}: invalid volume_semantics")
    try:
        start = date.fromisoformat(raw["effective_from"])
        end = date.fromisoformat(raw["effective_to"]) if raw.get("effective_to") else None
    except (TypeError, ValueError):
        raise ValueError(f"{source_symbol}: effective dates must use YYYY-MM-DD") from None
    if end and end <= start:
        raise ValueError(f"{source_symbol}: effective_to is exclusive and must be later than effective_from")
    tick_value, tick_value_currency = raw.get("tick_value"), raw.get("tick_value_currency")
    if (tick_value is None) != (tick_value_currency is None):
        raise ValueError(f"{source_symbol}: tick_value and tick_value_currency must be supplied together")
    if tick_value is not None:
        tick_value = _positive_decimal(tick_value, "tick_value")
        if not isinstance(tick_value_currency, str) or not tick_value_currency.strip():
            raise ValueError(f"{source_symbol}: tick_value_currency must be non-empty")
    return InstrumentSpec(
        source_symbol=source_symbol.strip().upper(),
        canonical_instrument=canonical.strip().upper(),
        digits=digits,
        point_size=_positive_decimal(raw["point_size"], "point_size"),
        tick_size=_positive_decimal(raw["tick_size"], "tick_size"),
        contract_size=_positive_decimal(raw["contract_size"], "contract_size"),
        price_currency=raw["price_currency"].strip().upper(),
        profit_currency=raw["profit_currency"].strip().upper(),
        spread_unit=spread_unit,
        volume_semantics=volume_semantics,
        effective_from=start.isoformat(),
        effective_to=end.isoformat() if end else None,
        evidence=raw["evidence"].strip(),
        tick_value=tick_value,
        tick_value_currency=tick_value_currency.strip().upper() if tick_value_currency else None,
    )


def validate_instrument_specs(raw: Any) -> dict[str, list[InstrumentSpec]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("instrument_specs must map source symbols to spec objects or arrays")
    result: dict[str, list[InstrumentSpec]] = {}
    for symbol, entries in raw.items():
        entries = entries if isinstance(entries, list) else [entries]
        if not entries:
            raise ValueError(f"{symbol}: specification history cannot be empty")
        validated = sorted(
            (validate_instrument_spec(symbol, entry) for entry in entries),
            key=lambda item: item.effective_from,
        )
        for previous, current in zip(validated, validated[1:]):
            previous_end = date.fromisoformat(previous.effective_to) if previous.effective_to else None
            current_start = date.fromisoformat(current.effective_from)
            if previous_end is None or current_start < previous_end:
                raise ValueError(f"{symbol}: overlapping effective-dated instrument specifications")
        normalized_symbol = symbol.strip().upper()
        if normalized_symbol in result:
            raise ValueError(f"Duplicate instrument spec key after normalization: {normalized_symbol}")
        result[normalized_symbol] = validated
    return result



def resolve_instrument_spec(
    specs: dict[str, list[InstrumentSpec]],
    source_symbol: str,
    source_timestamp: str,
) -> tuple[InstrumentSpec | None, str, str | None]:
    """Resolve the exact source-symbol contract effective on the source-local bar date."""
    symbol = source_symbol.strip().upper()
    if not symbol:
        return None, "INVALID_SOURCE_SYMBOL", None
    try:
        observation_date = date.fromisoformat(source_timestamp.split()[0].replace(".", "-"))
    except (ValueError, IndexError):
        return None, "INVALID_SOURCE_TIMESTAMP", None
    history = specs.get(symbol)
    if not history:
        return None, "SPEC_NOT_CONFIGURED", None
    for item in history:
        start = date.fromisoformat(item.effective_from)
        end = date.fromisoformat(item.effective_to) if item.effective_to else None
        if start <= observation_date and (end is None or observation_date < end):
            payload = json.dumps(item.as_dict(), sort_keys=True, separators=(",", ":"))
            spec_id = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            return item, "SPEC_MATCHED", spec_id
    return None, "NO_EFFECTIVE_SPEC_FOR_DATE", None


def spec_values_for_bar(
    specs: dict[str, list[InstrumentSpec]],
    source_symbol: str,
    source_timestamp: str,
    spread_raw: str | float | None = None,
) -> dict[str, str]:
    """Return explicit point-in-time metadata and unit-safe spread conversions."""
    item, status, spec_id = resolve_instrument_spec(specs, source_symbol, source_timestamp)
    values = {
        "instrument_spec_status": status,
        "instrument_spec_id": spec_id or "",
        "instrument_spec_effective_from": "",
        "instrument_spec_effective_to": "",
        "instrument_digits": "",
        "point_size": "",
        "tick_size": "",
        "contract_size": "",
        "price_currency": "",
        "profit_currency": "",
        "spread_unit": "",
        "spread_raw": "" if spread_raw is None else str(spread_raw),
        "spread_points": "",
        "spread_price": "",
        "volume_semantics": "",
        "tick_value": "",
        "tick_value_currency": "",
    }
    if item is None:
        return values
    values.update({
        "instrument_spec_effective_from": item.effective_from,
        "instrument_spec_effective_to": item.effective_to or "",
        "instrument_digits": str(item.digits),
        "point_size": item.point_size,
        "tick_size": item.tick_size,
        "contract_size": item.contract_size,
        "price_currency": item.price_currency,
        "profit_currency": item.profit_currency,
        "spread_unit": item.spread_unit,
        "volume_semantics": item.volume_semantics,
        "tick_value": item.tick_value or "",
        "tick_value_currency": item.tick_value_currency or "",
    })
    if spread_raw is not None:
        raw_value = Decimal(str(spread_raw))
        if not raw_value.is_finite() or raw_value < 0:
            raise ValueError("spread_raw must be finite and non-negative")
        if item.spread_unit == "points":
            values["spread_points"] = format(raw_value, "f")
            values["spread_price"] = format(raw_value * Decimal(item.point_size), "f")
        elif item.spread_unit == "price":
            values["spread_price"] = format(raw_value, "f")
    return values


def audit_instrument_specs(
    specs: dict[str, list[InstrumentSpec]],
    *,
    source_symbols: set[str] | None = None,
    observed_periods: dict[str, tuple[str, str]] | None = None,
) -> dict[str, Any]:
    source_symbols = {item.upper() for item in (source_symbols or set())}
    missing = sorted(source_symbols - set(specs))
    uncovered = []
    for symbol, (first_text, last_text) in (observed_periods or {}).items():
        if symbol not in specs:
            continue
        first, last = date.fromisoformat(first_text), date.fromisoformat(last_text)
        intervals = specs[symbol]
        cursor = first
        for item in intervals:
            start = date.fromisoformat(item.effective_from)
            end = date.fromisoformat(item.effective_to) if item.effective_to else None
            if end is not None and end <= cursor:
                continue
            if start > cursor:
                break
            if end is None or end > last:
                cursor = last + timedelta(days=1)
                break
            cursor = end
            if cursor > last:
                break
        if cursor <= last:
            uncovered.append({"source_symbol": symbol, "observed_from": first_text, "observed_to": last_text, "uncovered_from": cursor.isoformat()})
    status = "COMPLETE_FOR_OBSERVED_PERIODS" if specs and not missing and not uncovered else (
        "NOT_CONFIGURED" if not specs else "INCOMPLETE"
    )
    return {
        "registry_version": "instrument-spec-0.2.0",
        "spec_count": sum(len(items) for items in specs.values()),
        "source_symbols": sorted(source_symbols),
        "missing_source_symbols": missing,
        "uncovered_observed_periods": uncovered,
        "specifications": {key: [item.as_dict() for item in specs[key]] for key in sorted(specs)},
        "status": status,
        "admission_status": "REFERENCE_METADATA_ONLY_NOT_TRAINING_LABELS",
        "limitations": [
            "Specifications are source/server/time-period specific and require authoritative evidence.",
            "effective_to is exclusive; histories must not overlap and must cover every observed source date.",
            "Tick value may depend on deposit currency and conversion rates; it is not inferred.",
            "No account number, account owner or Demo/Real account type is required.",
            "Missing fields are never inferred from symbol names or OHLC prices.",
        ],
    }
