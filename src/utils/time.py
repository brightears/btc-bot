from datetime import datetime, timezone, timedelta
from typing import Tuple


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seconds_until(target_time: datetime) -> float:
    now = get_utc_now()
    delta = target_time - now
    return delta.total_seconds()


def get_funding_window(funding_hour: int = 8) -> Tuple[datetime, datetime]:
    now = get_utc_now()

    today_funding = now.replace(
        hour=funding_hour, minute=0, second=0, microsecond=0
    )

    if now >= today_funding:
        start = today_funding
        end = start + timedelta(hours=8)
    else:
        start = today_funding - timedelta(hours=16)
        end = today_funding

    return start, end


def get_next_funding_time(funding_hours: list = None) -> datetime:
    if funding_hours is None:
        funding_hours = [0, 8, 16]

    now = get_utc_now()
    current_hour = now.hour

    for hour in funding_hours:
        funding_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if funding_time > now:
            return funding_time

    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=funding_hours[0], minute=0, second=0, microsecond=0)


def format_duration(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"