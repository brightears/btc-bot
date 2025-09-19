from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class FundingOpportunity:
    symbol: str
    funding_rate_bps: float
    spot_price: float
    futures_price: float
    notional_usdt: float
    edge_bps: float
    fees_bps: float
    slippage_bps: float
    next_funding_time: datetime
    is_profitable: bool

    @property
    def net_edge_bps(self) -> float:
        return self.edge_bps

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'funding_rate_bps': self.funding_rate_bps,
            'spot_price': self.spot_price,
            'futures_price': self.futures_price,
            'notional_usdt': self.notional_usdt,
            'edge_bps': self.edge_bps,
            'fees_bps': self.fees_bps,
            'slippage_bps': self.slippage_bps,
            'next_funding_time': self.next_funding_time.isoformat(),
            'is_profitable': self.is_profitable
        }


@dataclass
class Position:
    symbol: str
    spot_amount: float
    futures_amount: float
    spot_entry_price: float
    futures_entry_price: float
    notional_usdt: float
    entry_time: datetime
    funding_collected: float = 0.0
    realized_pnl: float = 0.0

    def calculate_pnl(
        self,
        current_spot_price: float,
        current_futures_price: float,
        funding_payment: float = 0.0
    ) -> float:
        spot_pnl = (current_spot_price - self.spot_entry_price) * self.spot_amount
        futures_pnl = -(current_futures_price - self.futures_entry_price) * self.futures_amount
        self.funding_collected += funding_payment
        total_pnl = spot_pnl + futures_pnl + self.funding_collected
        return total_pnl

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'spot_amount': self.spot_amount,
            'futures_amount': self.futures_amount,
            'spot_entry_price': self.spot_entry_price,
            'futures_entry_price': self.futures_entry_price,
            'notional_usdt': self.notional_usdt,
            'entry_time': self.entry_time.isoformat(),
            'funding_collected': self.funding_collected,
            'realized_pnl': self.realized_pnl
        }


def calculate_funding_edge(
    funding_rate: float,
    fee_bps: float = 7.0,
    slippage_bps: float = 2.0
) -> float:
    funding_bps = funding_rate * 10000
    edge_bps = funding_bps - fee_bps - slippage_bps
    return edge_bps


def is_profitable_opportunity(
    edge_bps: float,
    threshold_bps: float
) -> bool:
    return edge_bps >= threshold_bps


def calculate_position_size(
    notional_usdt: float,
    price: float,
    leverage: float = 1.0
) -> float:
    return (notional_usdt / price) * leverage


def calculate_funding_payment(
    position_size: float,
    mark_price: float,
    funding_rate: float
) -> float:
    return position_size * mark_price * funding_rate


def estimate_total_cost(
    notional_usdt: float,
    fee_rate: float = 0.0007,
    slippage_rate: float = 0.0002
) -> float:
    fee_cost = notional_usdt * fee_rate * 2
    slippage_cost = notional_usdt * slippage_rate * 2
    return fee_cost + slippage_cost


def calculate_breakeven_funding_rate(
    fee_bps: float = 7.0,
    slippage_bps: float = 2.0
) -> float:
    total_cost_bps = fee_bps + slippage_bps
    return total_cost_bps / 10000


def project_window_pnl(
    notional_usdt: float,
    funding_rate: float,
    fee_bps: float = 7.0,
    slippage_bps: float = 2.0,
    num_periods: int = 1
) -> Dict[str, float]:
    funding_income = notional_usdt * funding_rate * num_periods
    total_fees = notional_usdt * (fee_bps / 10000) * 2
    total_slippage = notional_usdt * (slippage_bps / 10000) * 2

    net_pnl = funding_income - total_fees - total_slippage

    return {
        'funding_income': funding_income,
        'total_fees': total_fees,
        'total_slippage': total_slippage,
        'net_pnl': net_pnl,
        'net_pnl_bps': (net_pnl / notional_usdt) * 10000
    }