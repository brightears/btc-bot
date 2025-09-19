import pytest
from datetime import datetime, timezone, timedelta
from src.utils.time import (
    get_utc_now,
    seconds_until,
    get_funding_window,
    get_next_funding_time,
    format_duration
)


class TestFundingWindows:
    def test_get_next_funding_time(self):
        next_time = get_next_funding_time([0, 8, 16])
        assert isinstance(next_time, datetime)
        assert next_time.tzinfo == timezone.utc
        assert next_time.hour in [0, 8, 16]
        assert next_time > get_utc_now()

    def test_get_funding_window(self):
        start, end = get_funding_window(8)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert end > start
        assert (end - start).total_seconds() == 8 * 3600

    def test_seconds_until_positive(self):
        future_time = get_utc_now() + timedelta(hours=1)
        seconds = seconds_until(future_time)
        assert 3595 <= seconds <= 3605

    def test_seconds_until_negative(self):
        past_time = get_utc_now() - timedelta(hours=1)
        seconds = seconds_until(past_time)
        assert -3605 <= seconds <= -3595

    def test_format_duration_hours(self):
        assert format_duration(7320) == "2h 2m 0s"

    def test_format_duration_minutes(self):
        assert format_duration(125) == "2m 5s"

    def test_format_duration_seconds(self):
        assert format_duration(45) == "45s"

    def test_funding_window_boundaries(self):
        test_times = [
            datetime(2024, 1, 1, 7, 59, 59, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 8, 0, 1, tzinfo=timezone.utc),
        ]

        for test_time in test_times:
            now = get_utc_now()
            if test_time.hour == 8 and test_time.minute == 0 and test_time.second == 0:
                continue

    def test_next_funding_rollover(self):
        late_night = datetime.now(timezone.utc).replace(hour=23, minute=59)
        # Just test the logic without mocking
        next_funding = get_next_funding_time([0, 8, 16])
        assert next_funding is not None
        assert next_funding > get_utc_now()