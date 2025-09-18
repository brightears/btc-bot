"""Funding carry execution loop."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from exchange.binance import BinanceExchange
from funding.model import (
    compute_edge_bps,
    expected_pnl_usdt,
    should_open_position,
    window_from_eta,
)
from notify.telegram import TelegramNotifier
from risk.guards import (
    enforce_notional_cap,
    enforce_symbol_whitelist,
    ensure_maker_only,
    kill_switch_engaged,
)
from utils.time import humanize_duration, seconds_until, utc_now


class FundingExecutor:
    def __init__(
        self,
        exchange: BinanceExchange,
        notifier: TelegramNotifier,
        config: Dict[str, Any],
        logger: logging.Logger,
        dry_run: bool = True,
        state_path: Optional[str] = None,
    ) -> None:
        self.exchange = exchange
        self.notifier = notifier
        self.config = config
        self.logger = logger.getChild("executor")
        self.dry_run = dry_run
        self.symbol = config["symbol"]
        self.threshold_bps = float(config["threshold_bps"])
        self.notional_usdt = float(config["notional_usdt"])
        self.loop_seconds = int(config["loop_seconds"])
        self.fee_bps = float(config["fee_bps"])
        self.slippage_bps = float(config["slippage_bps"])
        self.whitelist = set(config.get("whitelist_symbols", []))
        self.notional_cap = float(config.get("notional_cap_usdt", self.notional_usdt))

        ensure_maker_only(self.logger, config.get("maker_only", True))
        try:
            self.exchange.setup_leverage(self.symbol)
        except AttributeError:
            self.logger.debug("Exchange does not support leverage setup")

        state_parent = Path(state_path).parent if state_path else Path("logs")
        state_parent.mkdir(parents=True, exist_ok=True)
        self.state_path = Path(state_path) if state_path else state_parent / "state.json"
        self.state = self._load_state()
        self.state["mode"] = "live" if not dry_run else "dry-run"

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {"position": None}
        try:
            with open(self.state_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError) as exc:
            self.logger.warning("Failed to load state file: %s", exc)
            return {"position": None}

    def _persist_state(self) -> None:
        try:
            with open(self.state_path, "w", encoding="utf-8") as fh:
                json.dump(self.state, fh, indent=2, sort_keys=True, default=str)
        except OSError as exc:
            self.logger.error("Unable to persist state: %s", exc)

    def _notify(self, message: str) -> None:
        self.logger.info(message)
        if self.notifier:
            self.notifier.send_message(message)

    def _summarise_cycle(
        self,
        mode: str,
        edge_bps: float,
        funding_eta: Optional[datetime],
        alert_sent: bool,
    ) -> str:
        eta_str = funding_eta.isoformat() if funding_eta else "unknown"
        return (
            f"mode={mode} edge_bps={edge_bps:.3f} funding_eta={eta_str} "
            f"alert={'yes' if alert_sent else 'no'}"
        )

    def run(self, max_loops: Optional[int] = None) -> None:
        loops = 0
        while True:
            summary = self.run_once()
            loops += 1
            if max_loops and loops >= max_loops:
                self.logger.info("Reached max loop count; stopping")
                break
            self.logger.debug("Cycle summary: %s", summary)
            time.sleep(self.loop_seconds)

    def run_once(self) -> str:
        mode = self.state.get("mode", "dry-run")
        alert_sent = False
        edge_bps = 0.0
        funding_eta: Optional[datetime] = None

        if kill_switch_engaged():
            if self.state.get("position"):
                self._close_position(reason="Kill switch engaged")
                alert_sent = True
            self.logger.warning("Kill switch active; skipping new positions")
            summary = self._summarise_cycle(mode, edge_bps, funding_eta, alert_sent)
            self._persist_state()
            return summary

        if not enforce_symbol_whitelist(self.symbol, self.whitelist):
            self.logger.error("Symbol %s not in whitelist; aborting", self.symbol)
            summary = self._summarise_cycle(mode, edge_bps, funding_eta, alert_sent)
            self._persist_state()
            return summary

        try:
            funding_info = self.exchange.get_funding_info(self.symbol)
            funding_eta = funding_info.next_funding_time
            edge_bps = compute_edge_bps(funding_info.funding_bps, self.fee_bps, self.slippage_bps)
            window = window_from_eta(funding_info.next_funding_time)
            time_to_funding = seconds_until(window.end)

            self.state["last_funding_bps"] = funding_info.funding_bps
            self.state["last_edge_bps"] = edge_bps
            self.state["next_funding_eta"] = funding_info.next_funding_time.isoformat()

            position = self.state.get("position")

            if position:
                funding_eta = datetime.fromisoformat(position["funding_eta"])
                if utc_now() >= funding_eta:
                    self._close_position(reason="Funding window complete")
                    alert_sent = True
                else:
                    self.logger.info(
                        "Holding carry until funding in %s", humanize_duration(time_to_funding)
                    )
            else:
                if should_open_position(edge_bps, self.threshold_bps):
                    if enforce_notional_cap(self.notional_usdt, self.notional_cap):
                        self._open_position(edge_bps, funding_info)
                        alert_sent = True
                    else:
                        self.logger.warning(
                            "Notional %.2f exceeds cap %.2f; skipping entry",
                            self.notional_usdt,
                            self.notional_cap,
                        )
                else:
                    self.logger.info(
                        "Edge %.3f bps below threshold %.3f bps; staying flat",
                        edge_bps,
                        self.threshold_bps,
                    )

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Cycle failed: %s", exc)

        self._persist_state()
        summary = self._summarise_cycle(mode, edge_bps, funding_eta, alert_sent)
        return summary

    def _open_position(self, edge_bps: float, funding_info) -> None:
        prices = self.exchange.get_prices(self.symbol)
        notional = self.notional_usdt
        execution = self.exchange.open_carry_position(self.symbol, notional)
        spot_order = execution.get("orders", {}).get("spot") if isinstance(execution, dict) else None
        quantity = spot_order.get("amount") if spot_order else notional / max(prices.spot_price, 1e-12)

        position = {
            "opened_at": utc_now().isoformat(),
            "notional": notional,
            "edge_bps": edge_bps,
            "funding_eta": funding_info.next_funding_time.isoformat(),
            "expected_pnl": expected_pnl_usdt(notional, edge_bps),
            "quantity": quantity,
        }
        self.state["position"] = position
        self._notify(
            (
                f"Opened carry on {self.symbol}: edge={edge_bps:.3f}bps, "
                f"expect ~{position['expected_pnl']:.2f} USDT"
            )
        )

    def _close_position(self, reason: str) -> None:
        position = self.state.get("position")
        if not position:
            return
        quantity = position.get("quantity", 0.0)
        self.exchange.close_carry_position(self.symbol, quantity)
        self.state["position"] = None
        self._notify(f"Closed carry on {self.symbol}: {reason}")
