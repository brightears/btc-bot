"""Time helpers for funding calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple


def utc_now() -> datetime:
    """Return the current UTC time with tzinfo."""
    return datetime.now(timezone.utc)


def as_utc(dt: datetime) -> datetime:
    """Convert aware/naive datetimes into a timezone-aware UTC datetime."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def seconds_until(target: datetime, reference: datetime | None = None) -> float:
    """Return the number of seconds until the target time from the reference (default now)."""
    ref = utc_now() if reference is None else as_utc(reference)
    return max((as_utc(target) - ref).total_seconds(), 0.0)


def funding_window_bounds(
    funding_eta: datetime, interval_hours: int = 8
) -> Tuple[datetime, datetime]:
    """Return the start and end timestamps for the current funding window."""
    funding_eta_utc = as_utc(funding_eta)
    start = funding_eta_utc - timedelta(hours=interval_hours)
    return start, funding_eta_utc


def humanize_duration(seconds: float) -> str:
    """Return a coarse human-readable duration string."""
    seconds = max(int(seconds), 0)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)
