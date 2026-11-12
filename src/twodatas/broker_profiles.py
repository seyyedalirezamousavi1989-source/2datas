from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class BrokerProfile:
    profile_id: str
    broker_name: str
    server_timezone: str | None
    bar_timestamp_convention: str | None  # interval_start | interval_end
    status: str  # verified | candidate_unverified | user_configured
    evidence: str


# Alpari commonly uses an EET/EEST-like server clock, but the exact server,
# historical policy and export convention must be verified before activation.
BUILTIN_PROFILES = {
    "alpari_mt5_candidate": BrokerProfile(
        profile_id="alpari_mt5_candidate",
        broker_name="Alpari",
        server_timezone="Europe/Helsinki",
        bar_timestamp_convention=None,
        status="candidate_unverified",
        evidence="Candidate only; confirm the exact Alpari MT5 server and historical DST policy from terminal/export metadata.",
    )
}


def resolve_profile(profile_id: str | None = None, *, broker_name: str | None = None,
                    server_timezone: str | None = None,
                    bar_timestamp_convention: str | None = None) -> BrokerProfile:
    if server_timezone:
        try:
            ZoneInfo(server_timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown IANA timezone: {server_timezone}") from exc
        if bar_timestamp_convention not in {"interval_start", "interval_end"}:
            raise ValueError("Explicit timezone requires bar_timestamp_convention=interval_start|interval_end")
        return BrokerProfile(
            profile_id=profile_id or "user_configured",
            broker_name=broker_name or "User-configured broker",
            server_timezone=server_timezone,
            bar_timestamp_convention=bar_timestamp_convention,
            status="user_configured",
            evidence="Explicit user-supplied source configuration; not independently broker-verified.",
        )
    if profile_id and profile_id in BUILTIN_PROFILES:
        return BUILTIN_PROFILES[profile_id]
    return BrokerProfile(
        profile_id="unknown",
        broker_name=broker_name or "Unknown",
        server_timezone=None,
        bar_timestamp_convention=None,
        status="candidate_unverified",
        evidence="No authoritative broker/server time contract supplied.",
    )


def to_utc(source_timestamp: str, precision: str, profile: BrokerProfile) -> tuple[str | None, str]:
    """Convert only when both timezone and bar convention are verified/configured."""
    if not profile.server_timezone or not profile.bar_timestamp_convention:
        return None, "UNRESOLVED_SOURCE_TIME"
    fmt = "%Y.%m.%d %H:%M:%S" if precision == "second" else "%Y.%m.%d"
    local_naive = datetime.strptime(source_timestamp, fmt)
    zone = ZoneInfo(profile.server_timezone)
    candidate = local_naive.replace(tzinfo=zone)
    # Reject nonexistent or ambiguous local wall times rather than silently selecting a fold.
    roundtrip = candidate.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
    if roundtrip != local_naive:
        return None, "NONEXISTENT_LOCAL_TIME"
    alternate = local_naive.replace(tzinfo=zone, fold=1)
    if candidate.utcoffset() != alternate.utcoffset():
        return None, "AMBIGUOUS_LOCAL_TIME"
    if profile.bar_timestamp_convention == "interval_end":
        return candidate.astimezone(timezone.utc).isoformat(), "RESOLVED_INTERVAL_END"
    return candidate.astimezone(timezone.utc).isoformat(), "RESOLVED_INTERVAL_START"
