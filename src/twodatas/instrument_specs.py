from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
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
        raise ValueError(f"{source_symbol}: instrument spec must be a JSON object")
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
        raise ValueError(f"{source_symbol}: canonical_instrument must be a non-empty string")
    if isinstance(digits, bool) or not isinstance(digits, int) or not 0 <= digits <= 12:
        raise ValueError(f"{source_symbol}: digits must be an integer from 0 to 12")
    for field in ("price_currency", "profit_currency", "evidence"):
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise ValueError(f"{source_symbol}: {field} must be a non-empty string")
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
        raise ValueError(f"{source_symbol}: effective_to must be later than effective_from")

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


def validate_instrument_specs(raw: Any) -> dict[str, InstrumentSpec]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("instrument_specs must be an object keyed by source symbol")
    result = {}
    for symbol, spec in raw.items():
        item = validate_instrument_spec(symbol, spec)
        if item.source_symbol in result:
            raise ValueError(f"Duplicate instrument spec for {item.source_symbol}")
        result[item.source_symbol] = item
    return result


def audit_instrument_specs(
    specs: dict[str, InstrumentSpec], *, source_symbols: set[str] | None = None
) -> dict[str, Any]:
    source_symbols = {item.upper() for item in (source_symbols or set())}
    missing = sorted(source_symbols - set(specs))
    return {
        "registry_version": "instrument-spec-0.1.0",
        "spec_count": len(specs),
        "source_symbols": sorted(source_symbols),
        "missing_source_symbols": missing,
        "specifications": [specs[key].as_dict() for key in sorted(specs)],
        "status": "COMPLETE_FOR_SOURCE_SYMBOLS" if not missing else ("NOT_CONFIGURED" if not specs else "INCOMPLETE"),
        "admission_status": "REFERENCE_METADATA_ONLY_NOT_TRAINING_LABELS",
        "limitations": [
            "Specifications are source/server/time-period specific and require authoritative evidence.",
            "Tick value may depend on deposit currency and conversion rates; it is not inferred.",
            "No account number, account owner or Demo/Real account type is required.",
            "Missing fields are never inferred from symbol names or OHLC prices.",
        ],
    }
