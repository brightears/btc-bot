"""Pure funding model helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from utils.time import as_utc, funding_window_bounds

BASIS_POINT = 1 / 10000


@dataclass
class FundingWindow:
    start: datetime
    end: datetime


def compute_edge_bps(funding_bps: float, fee_bps: float, slippage_bps: float) -> float:
    """Net edge after subtracting fees and slippage."""
    return funding_bps - fee_bps - slippage_bps


def expected_pnl_usdt(notional: float, edge_bps: float) -> float:
    """Return expected profit in USDT for the window."""
    return notional * edge_bps * BASIS_POINT


def should_open_position(edge_bps: float, threshold_bps: float) -> bool:
    return edge_bps >= threshold_bps


def window_from_eta(funding_eta: datetime, interval_hours: int = 8) -> FundingWindow:
    start, end = funding_window_bounds(funding_eta, interval_hours=interval_hours)
    return FundingWindow(start=start, end=end)


def accrue_window_pnl(
    notional: float,
    realized_funding_bps: float,
    fee_bps: float,
    slippage_bps: float,
) -> float:
    """Return realized pnl for a full funding window."""
    edge = compute_edge_bps(realized_funding_bps, fee_bps, slippage_bps)
    return expected_pnl_usdt(notional, edge)


def prorate_edge(edge_bps: float, seconds_elapsed: float, window_seconds: Optional[float] = None) -> float:
    """Prorate the expected edge by elapsed seconds against the window size."""
    if window_seconds is None:
        window_seconds = 8 * 3600
    if window_seconds <= 0:
        return 0.0
    ratio = min(max(seconds_elapsed / window_seconds, 0.0), 1.0)
    return edge_bps * ratio


def next_window_eta(last_eta: datetime) -> datetime:
    """Return the next expected funding eta, assuming fixed 8h cadence."""
    return as_utc(last_eta) + timedelta(hours=8)
