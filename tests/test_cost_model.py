import pytest
from src.funding.model import (
    calculate_funding_edge,
    is_profitable_opportunity,
    calculate_position_size,
    calculate_funding_payment,
    estimate_total_cost,
    calculate_breakeven_funding_rate,
    project_window_pnl
)


class TestCostModel:
    def test_calculate_funding_edge(self):
        funding_rate = 0.001
        fee_bps = 7.0
        slippage_bps = 2.0

        edge = calculate_funding_edge(funding_rate, fee_bps, slippage_bps)

        expected_edge = (funding_rate * 10000) - fee_bps - slippage_bps
        assert edge == expected_edge
        assert edge == 1.0

    def test_is_profitable_opportunity(self):
        assert is_profitable_opportunity(5.0, 3.0) == True
        assert is_profitable_opportunity(2.0, 3.0) == False
        assert is_profitable_opportunity(3.0, 3.0) == True

    def test_calculate_position_size(self):
        notional = 1000
        price = 50000
        leverage = 1

        size = calculate_position_size(notional, price, leverage)
        assert size == 0.02

        size_2x = calculate_position_size(notional, price, 2)
        assert size_2x == 0.04

    def test_calculate_funding_payment(self):
        position_size = 0.1
        mark_price = 50000
        funding_rate = 0.001

        payment = calculate_funding_payment(position_size, mark_price, funding_rate)
        assert payment == 5.0

    def test_estimate_total_cost(self):
        notional = 10000
        fee_rate = 0.0007
        slippage_rate = 0.0002

        cost = estimate_total_cost(notional, fee_rate, slippage_rate)

        expected_fee_cost = notional * fee_rate * 2
        expected_slippage = notional * slippage_rate * 2
        expected_total = expected_fee_cost + expected_slippage

        assert cost == expected_total
        assert cost == 18.0

    def test_calculate_breakeven_funding_rate(self):
        fee_bps = 7.0
        slippage_bps = 2.0

        breakeven = calculate_breakeven_funding_rate(fee_bps, slippage_bps)
        assert breakeven == 0.0009

    def test_project_window_pnl(self):
        notional = 10000
        funding_rate = 0.001
        fee_bps = 7.0
        slippage_bps = 2.0

        result = project_window_pnl(notional, funding_rate, fee_bps, slippage_bps)

        assert result['funding_income'] == 10.0
        assert result['total_fees'] == 14.0
        assert result['total_slippage'] == 4.0
        assert result['net_pnl'] == -8.0
        assert result['net_pnl_bps'] == -8.0

    def test_project_window_pnl_multiple_periods(self):
        notional = 10000
        funding_rate = 0.001
        fee_bps = 7.0
        slippage_bps = 2.0
        periods = 3

        result = project_window_pnl(
            notional, funding_rate, fee_bps, slippage_bps, periods
        )

        assert result['funding_income'] == 30.0
        assert result['total_fees'] == 14.0
        assert result['total_slippage'] == 4.0
        assert result['net_pnl'] == 12.0
        assert abs(result['net_pnl_bps'] - 12.0) < 0.01