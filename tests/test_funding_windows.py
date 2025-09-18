from datetime import datetime, timezone

from funding.model import next_window_eta, window_from_eta


def test_window_from_eta():
    eta = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
    window = window_from_eta(eta)
    assert window.end == eta
    assert window.start == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_next_window_eta():
    eta = datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
    new_eta = next_window_eta(eta)
    assert new_eta == datetime(2024, 1, 1, 16, 0, tzinfo=timezone.utc)
