from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re


@dataclass(frozen=True)
class BrokerProfile:
    profile_id: str
    broker_name: str
    server_name: str | None
    server_timezone: str | None
    bar_timestamp_convention: str | None  # interval_start | interval_end
    status: str  # verified | candidate_unverified | user_configured
    evidence: str


# Built-in Alpari profile. Only exact recognized MT5 server names activate this
# documented seasonal clock; all other server identities remain quarantined.
BUILTIN_PROFILES = {
    "alpari_mt5_candidate": BrokerProfile(
        profile_id="alpari_mt5_candidate",
        broker_name="Alpari",
        server_name=None,
        server_timezone="Europe/Helsinki",
        bar_timestamp_convention="interval_start",
        status="candidate_unverified",
        evidence="Alpari documentation describes GMT+2 in winter and GMT+3 during DST (last Sunday of March/October); exact account server still must match a published MT5 server.",
    )
}


def _clock_zone(value: str):
    fixed = re.fullmatch(r"UTC([+-])(\d{2}):(\d{2})", value.upper())
    if fixed:
        hours, minutes = int(fixed.group(2)), int(fixed.group(3))
        if hours > 14 or minutes > 59 or (hours == 14 and minutes != 0):
            raise ValueError(f"Invalid fixed UTC offset: {value}")
        delta = timedelta(hours=hours, minutes=minutes)
        if fixed.group(1) == "-":
            delta = -delta
        return timezone(delta, name=value)
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown IANA timezone or fixed UTC offset: {value}") from exc


def resolve_profile(
    profile_id: str | None = None,
    *,
    broker_name: str | None = None,
    server_name: str | None = None,
    server_timezone: str | None = None,
    bar_timestamp_convention: str | None = None,
) -> BrokerProfile:
    if server_timezone:
        _clock_zone(server_timezone)
        if bar_timestamp_convention not in {"interval_start", "interval_end"}:
            raise ValueError("Explicit timezone requires bar_timestamp_convention=interval_start|interval_end")
        return BrokerProfile(
            profile_id=profile_id or "user_configured",
            broker_name=broker_name or "User-configured broker",
            server_name=server_name,
            server_timezone=server_timezone,
            bar_timestamp_convention=bar_timestamp_convention,
            status="user_configured",
            evidence="Explicit user-supplied source configuration; not independently broker-verified.",
        )
    if profile_id and profile_id in BUILTIN_PROFILES:
        candidate = BUILTIN_PROFILES[profile_id]
        # A broker label or server string is not proof of historical clock
        # semantics. Built-in profiles remain candidates until independently
        # verified against source metadata/documentation for the relevant era.
        return BrokerProfile(
            profile_id=candidate.profile_id,
            broker_name=candidate.broker_name,
            server_name=server_name,
            server_timezone=candidate.server_timezone,
            bar_timestamp_convention=candidate.bar_timestamp_convention,
            status="candidate_unverified",
            evidence=candidate.evidence + " Broker/server identity alone does not verify the historical clock contract.",
        )
    return BrokerProfile(
        profile_id=profile_id or "unknown",
        broker_name=broker_name or "Unknown",
        server_name=server_name,
        server_timezone=None,
        bar_timestamp_convention=None,
        status="candidate_unverified",
        evidence="No authoritative broker/server time contract supplied.",
    )


def to_utc(source_timestamp: str, precision: str, profile: BrokerProfile) -> tuple[str | None, str]:
    """Convert only when timezone and bar convention are explicitly configured."""
    if profile.status not in {"verified", "user_configured"}:
        return None, "BROKER_PROFILE_NOT_VERIFIED"
    if not profile.server_timezone or not profile.bar_timestamp_convention:
        return None, "UNRESOLVED_SOURCE_TIME"
    fmt = "%Y.%m.%d %H:%M:%S" if precision == "second" else "%Y.%m.%d"
    local_naive = datetime.strptime(source_timestamp, fmt)
    zone = _clock_zone(profile.server_timezone)
    candidate = local_naive.replace(tzinfo=zone)
    roundtrip = candidate.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
    if roundtrip != local_naive:
        return None, "NONEXISTENT_LOCAL_TIME"
    alternate = local_naive.replace(tzinfo=zone, fold=1)
    if candidate.utcoffset() != alternate.utcoffset():
        return None, "AMBIGUOUS_LOCAL_TIME"
    status = "RESOLVED_INTERVAL_END" if profile.bar_timestamp_convention == "interval_end" else "RESOLVED_INTERVAL_START"
    return candidate.astimezone(timezone.utc).isoformat(), status


def resolve_profile_for_archive(
    archive_path: str,
    *,
    config_path: str | None = None,
    profile_id: str | None = None,
    broker_name: str | None = None,
    server_name: str | None = None,
    server_timezone: str | None = None,
    bar_timestamp_convention: str | None = None,
) -> tuple[BrokerProfile, dict]:
    """Resolve a source-specific profile from an adjacent JSON sidecar or explicit CLI values.

    Sidecar candidates are <archive>.broker.json and <archive-stem>.broker.json.
    Ambiguous configuration is rejected; clock semantics are never inferred from OHLC.
    """
    from pathlib import Path
    import hashlib
    import json

    archive = Path(archive_path)
    candidates = [Path(str(archive) + ".broker.json"), archive.with_suffix(".broker.json")]
    if config_path:
        selected = Path(config_path)
        if not selected.is_file():
            raise FileNotFoundError(f"Broker config not found: {selected}")
    else:
        found = [path for path in candidates if path.is_file()]
        if len(found) > 1:
            raise ValueError(f"Multiple broker sidecars found; pass --broker-config explicitly: {found}")
        selected = found[0] if found else None

    explicit = any(value is not None for value in (
        profile_id, broker_name, server_name, server_timezone, bar_timestamp_convention
    ))
    if selected is not None:
        if explicit:
            raise ValueError("Do not mix a broker sidecar with explicit broker CLI fields; edit the sidecar or omit it.")
        raw = selected.read_bytes()
        config = json.loads(raw.decode("utf-8"))
        if not isinstance(config, dict):
            raise ValueError("Broker config root must be a JSON object")
        allowed = {
            "schema_version", "profile_id", "broker_name", "server_name",
            "server_timezone", "bar_timestamp_convention", "symbol_aliases",
        }
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"Unknown broker config keys: {sorted(unknown)}")
        if config.get("schema_version") != "2datas-broker-clock-1":
            raise ValueError("Broker config schema_version must be '2datas-broker-clock-1'")
        required = ("server_timezone", "bar_timestamp_convention")
        missing = [key for key in required if not isinstance(config.get(key), str) or not config[key].strip()]
        if missing:
            raise ValueError(f"Broker config missing required fields: {missing}")
        for key in ("profile_id", "broker_name", "server_name"):
            if config.get(key) is not None and not isinstance(config[key], str):
                raise ValueError(f"Broker config {key} must be a string")
        if config["bar_timestamp_convention"] not in {"interval_start", "interval_end"}:
            raise ValueError("bar_timestamp_convention must be interval_start or interval_end")
        aliases = config.get("symbol_aliases", {})
        if not isinstance(aliases, dict) or any(
            not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip()
            for key, value in aliases.items()
        ):
            raise ValueError("symbol_aliases must map non-empty source symbols to canonical symbols")
        aliases = {key.strip().upper(): value.strip().upper() for key, value in aliases.items()}
        profile = resolve_profile(
            config.get("profile_id"),
            broker_name=config.get("broker_name"),
            server_name=config.get("server_name"),
            server_timezone=config["server_timezone"],
            bar_timestamp_convention=config["bar_timestamp_convention"],
        )
        return profile, {
            "mode": "sidecar",
            "path": selected.name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "symbol_aliases": aliases,
        }

    profile = resolve_profile(
        profile_id,
        broker_name=broker_name,
        server_name=server_name,
        server_timezone=server_timezone,
        bar_timestamp_convention=bar_timestamp_convention,
    )
    return profile, {"mode": "explicit_cli" if explicit else "unresolved", "path": None, "sha256": None, "symbol_aliases": {}}
