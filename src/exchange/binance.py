"""Binance exchange integration via ccxt."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

import ccxt
from tenacity import retry, stop_after_attempt, wait_fixed

from utils.filters import SymbolFilters, apply_filters


@dataclass
class PriceSnapshot:
    spot_price: float
    perp_price: float


@dataclass
class FundingInfo:
    funding_bps: float
    next_funding_time: datetime


class BinanceExchange:
    def __init__(
        self,
        dry_run: bool,
        logger: logging.Logger,
        maker_only: bool = True,
        leverage: int = 1,
    ) -> None:
        self.dry_run = dry_run
        self.logger = logger.getChild("binance")
        self.maker_only = maker_only
        self.leverage = leverage

        spot_key = os.getenv("BINANCE_API_KEY")
        spot_secret = os.getenv("BINANCE_API_SECRET")
        perp_key = os.getenv("BINANCE_USDM_API_KEY")
        perp_secret = os.getenv("BINANCE_USDM_API_SECRET")

        spot_params: Dict[str, Any] = {
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
        perp_params: Dict[str, Any] = {
            "enableRateLimit": True,
            "options": {"defaultType": "future"},
        }

        if not dry_run:
            if not (spot_key and spot_secret and perp_key and perp_secret):
                raise RuntimeError("Live mode requires both spot and USDⓈ-M API credentials")
            spot_params.update({"apiKey": spot_key, "secret": spot_secret})
            perp_params.update({"apiKey": perp_key, "secret": perp_secret})

        self.spot = ccxt.binance(spot_params)
        self.perp = ccxt.binanceusdm(perp_params)

        self._markets_loaded = False

    def load_markets(self) -> None:
        if self._markets_loaded:
            return
        self.spot.load_markets()
        self.perp.load_markets()
        self._markets_loaded = True

    def _perp_symbol(self, symbol: str) -> str:
        self.load_markets()
        if symbol in self.perp.symbols:
            return symbol
        if "/" in symbol:
            base, quote = symbol.split("/")
            candidate = f"{base}/{quote}:{quote}"
            if candidate in self.perp.symbols:
                return candidate
        raise ccxt.BadSymbol(f"Perp symbol not found for {symbol}")

    def _filters_from_market(self, market: Dict[str, Any]) -> SymbolFilters:
        precision = market.get("precision", {})
        limits = market.get("limits", {})
        price_precision = precision.get("price")
        amount_precision = precision.get("amount")
        tick_size = 10 ** (-price_precision) if price_precision is not None else None
        step_size = 10 ** (-amount_precision) if amount_precision is not None else None
        min_notional = limits.get("cost", {}).get("min")
        return SymbolFilters(tick_size=tick_size, step_size=step_size, min_notional=min_notional)

    def _spot_filters(self, symbol: str) -> SymbolFilters:
        self.load_markets()
        return self._filters_from_market(self.spot.market(symbol))

    def _perp_filters(self, symbol: str) -> SymbolFilters:
        self.load_markets()
        perp_symbol = self._perp_symbol(symbol)
        return self._filters_from_market(self.perp.market(perp_symbol))

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def get_prices(self, symbol: str) -> PriceSnapshot:
        self.load_markets()
        spot_ticker = self.spot.fetch_ticker(symbol)
        perp_symbol = self._perp_symbol(symbol)
        perp_ticker = self.perp.fetch_ticker(perp_symbol)
        spot_price = float(spot_ticker.get("last") or spot_ticker["close"])
        perp_price = float(perp_ticker.get("last") or perp_ticker["close"])
        return PriceSnapshot(spot_price=spot_price, perp_price=perp_price)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def get_funding_info(self, symbol: str) -> FundingInfo:
        self.load_markets()
        perp_symbol = self._perp_symbol(symbol)
        data = self.perp.fetchFundingRate(perp_symbol)
        rate = float(data.get("fundingRate", 0.0))
        next_time_ms = (
            data.get("nextFundingTime")
            or data.get("nextFundingTimestamp")
            or data.get("fundingTime")
            or data.get("fundingTimestamp")
        )
        if next_time_ms is None:
            info = data.get("info", {})
            next_time_ms = info.get("nextFundingTime") or info.get("nextFundingTimestamp")
        if next_time_ms is None:
            raise RuntimeError("Missing funding time from exchange response")
        funding_time = datetime.fromtimestamp(int(next_time_ms) / 1000, tz=timezone.utc)
        return FundingInfo(funding_bps=rate * 10000, next_funding_time=funding_time)

    def setup_leverage(self, symbol: str) -> None:
        if self.dry_run:
            return
        try:
            perp_symbol = self._perp_symbol(symbol)
            self.perp.set_leverage(self.leverage, perp_symbol)
        except ccxt.BaseError as exc:
            self.logger.warning("Failed to set leverage to %s: %s", self.leverage, exc)

    def _prepare_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        market_type: str,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        if market_type == "spot":
            api_symbol = symbol
            filters = self._spot_filters(symbol)
        else:
            api_symbol = self._perp_symbol(symbol)
            filters = self._perp_filters(symbol)
        adj_price, adj_qty = apply_filters(price, quantity, filters)
        params = {"postOnly": self.maker_only}
        if reduce_only:
            params["reduceOnly"] = True
        return {
            "api_symbol": api_symbol,
            "market_type": market_type,
            "side": side,
            "amount": adj_qty,
            "price": adj_price,
            "params": params,
        }

    def open_carry_position(self, symbol: str, notional: float) -> Dict[str, Any]:
        prices = self.get_prices(symbol)
        base_qty = notional / prices.spot_price
        spot_order = self._prepare_order(
            symbol=symbol,
            side="buy",
            quantity=base_qty,
            price=prices.spot_price * (0.999 if self.maker_only else 1.0),
            market_type="spot",
        )
        perp_order = self._prepare_order(
            symbol=symbol,
            side="sell",
            quantity=spot_order["amount"],
            price=prices.perp_price * (1.001 if self.maker_only else 1.0),
            market_type="perp",
        )

        if self.dry_run:
            self.logger.info(
                "DRY-RUN open carry: buy %.6f %s spot @ %.2f, sell perp @ %.2f",
                spot_order["amount"],
                symbol,
                spot_order["price"],
                perp_order["price"],
            )
            return {"status": "dry_run", "orders": {"spot": spot_order, "perp": perp_order}}

        self.logger.info("Submitting live carry orders")
        spot_resp = self.spot.create_limit_buy_order(
            spot_order["api_symbol"],
            amount=spot_order["amount"],
            price=spot_order["price"],
            params=spot_order["params"],
        )
        perp_resp = self.perp.create_limit_sell_order(
            perp_order["api_symbol"],
            amount=perp_order["amount"],
            price=perp_order["price"],
            params=perp_order["params"],
        )
        return {"spot_order": spot_resp, "perp_order": perp_resp}

    def close_carry_position(self, symbol: str, quantity: float) -> Dict[str, Any]:
        prices = self.get_prices(symbol)
        spot_order = self._prepare_order(
            symbol=symbol,
            side="sell",
            quantity=quantity,
            price=prices.spot_price * (1.001 if self.maker_only else 1.0),
            market_type="spot",
        )
        perp_order = self._prepare_order(
            symbol=symbol,
            side="buy",
            quantity=quantity,
            price=prices.perp_price * (0.999 if self.maker_only else 1.0),
            market_type="perp",
            reduce_only=True,
        )

        if self.dry_run:
            self.logger.info(
                "DRY-RUN close carry: sell %.6f %s spot @ %.2f, buy perp @ %.2f",
                spot_order["amount"],
                symbol,
                spot_order["price"],
                perp_order["price"],
            )
            return {"status": "dry_run", "orders": {"spot": spot_order, "perp": perp_order}}

        self.logger.info("Closing live carry")
        spot_resp = self.spot.create_limit_sell_order(
            spot_order["api_symbol"],
            amount=spot_order["amount"],
            price=spot_order["price"],
            params=spot_order["params"],
        )
        perp_resp = self.perp.create_limit_buy_order(
            perp_order["api_symbol"],
            amount=perp_order["amount"],
            price=perp_order["price"],
            params=perp_order["params"],
        )
        return {"spot_order": spot_resp, "perp_order": perp_resp}
