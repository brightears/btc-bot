import json
import logging
from datetime import datetime, timedelta, timezone

import pytest

from exchange.binance import FundingInfo, PriceSnapshot
from funding.executor import FundingExecutor


class FakeExchange:
    def __init__(self) -> None:
        self.open_calls = 0
        self.close_calls = 0
        self.last_quantity = None

    def setup_leverage(self, symbol: str) -> None:
        return None

    def get_funding_info(self, symbol: str) -> FundingInfo:
        eta = datetime.now(timezone.utc) + timedelta(hours=1)
        return FundingInfo(funding_bps=12.0, next_funding_time=eta)

    def get_prices(self, symbol: str) -> PriceSnapshot:
        return PriceSnapshot(spot_price=50000.0, perp_price=50010.0)

    def open_carry_position(self, symbol: str, notional: float):
        self.open_calls += 1
        qty = notional / 50000.0
        self.last_quantity = qty
        return {"orders": {"spot": {"amount": qty}}}

    def close_carry_position(self, symbol: str, quantity: float):
        self.close_calls += 1
        self.last_quantity = quantity
        return {"status": "closed"}


class DummyNotifier:
    def __init__(self) -> None:
        self.messages = []

    def send_message(self, text: str) -> None:
        self.messages.append(text)


@pytest.fixture
def config():
    return {
        "symbol": "BTC/USDT",
        "notional_usdt": 100,
        "threshold_bps": 0.5,
        "loop_seconds": 1,
        "maker_only": True,
        "leverage": 1,
        "fee_bps": 7,
        "slippage_bps": 2,
        "whitelist_symbols": ["BTC/USDT"],
        "log_level": "DEBUG",
    }


def test_dry_run_opens_position(tmp_path, config):
    exchange = FakeExchange()
    notifier = DummyNotifier()
    logger = logging.getLogger("test")

    state_path = tmp_path / "state.json"
    executor = FundingExecutor(
        exchange=exchange,
        notifier=notifier,
        config=config,
        logger=logger,
        dry_run=True,
        state_path=str(state_path),
    )

    summary = executor.run_once()

    assert "edge_bps" in summary
    assert executor.state["position"] is not None
    assert notifier.messages
    with open(state_path, "r", encoding="utf-8") as fh:
        persisted = json.load(fh)
    assert persisted["position"] is not None

    # Second run should close after funding eta passes
    executor.state["position"]["funding_eta"] = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    ).isoformat()
    summary = executor.run_once()
    assert executor.state["position"] is None
    assert exchange.close_calls == 1
