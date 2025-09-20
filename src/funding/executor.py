import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from src.exchange.binance import BinanceClient
from src.funding.model import (
    FundingOpportunity,
    Position,
    calculate_funding_edge,
    is_profitable_opportunity,
    calculate_position_size,
    calculate_funding_payment,
    project_window_pnl
)
from src.notify.telegram import TelegramNotifier
from src.risk.guards import RiskGuard
from src.utils.logger import get_logger, setup_logger
from src.utils.time import (
    get_utc_now,
    get_next_funding_time,
    seconds_until,
    format_duration
)

logger = get_logger()


class FundingExecutor:
    def __init__(self, config: Dict[str, Any], dry_run: bool = True):
        self.config = config
        self.dry_run = dry_run
        self.running = True

        self.symbol = config.get('symbol', 'BTC/USDT')
        self.notional_usdt = config.get('notional_usdt', 100)
        self.threshold_bps = config.get('threshold_bps', 0.5)
        self.fee_bps = config.get('fee_bps', 7.0)
        self.slippage_bps = config.get('slippage_bps', 2.0)
        self.leverage = config.get('leverage', 1)
        self.maker_only = config.get('maker_only', True)

        self.exchange = BinanceClient(dry_run=dry_run)
        self.telegram = TelegramNotifier(enabled=True)  # Enable for both dry-run and live
        self.risk_guard = RiskGuard(config)

        self.position: Optional[Position] = None
        self.state_file = Path("logs/state.json")

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._check_kill_switch()
        self._load_state()

    def _signal_handler(self, signum, frame):
        logger.info("Received shutdown signal")
        self.running = False
        self._save_state()
        sys.exit(0)

    def _check_kill_switch(self) -> bool:
        if os.path.exists('.kill'):
            logger.warning("Kill switch activated (.kill file found)")
            self.running = False
            return True

        if os.getenv('KILL') == '1':
            logger.warning("Kill switch activated (KILL=1)")
            self.running = False
            return True

        return False

    def _load_state(self):
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            if state.get('position'):
                pos_data = state['position']
                self.position = Position(
                    symbol=pos_data['symbol'],
                    spot_amount=pos_data['spot_amount'],
                    futures_amount=pos_data['futures_amount'],
                    spot_entry_price=pos_data['spot_entry_price'],
                    futures_entry_price=pos_data['futures_entry_price'],
                    notional_usdt=pos_data['notional_usdt'],
                    entry_time=datetime.fromisoformat(pos_data['entry_time']),
                    funding_collected=pos_data.get('funding_collected', 0),
                    realized_pnl=pos_data.get('realized_pnl', 0)
                )

            logger.info("Loaded state from file")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")

    def _save_state(self):
        state = {
            'timestamp': get_utc_now().isoformat(),
            'position': self.position.to_dict() if self.position else None,
            'dry_run': self.dry_run
        }

        try:
            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def check_funding_opportunity(self) -> Optional[FundingOpportunity]:
        try:
            spot_ticker = self.exchange.get_ticker(self.symbol, 'spot')
            futures_ticker = self.exchange.get_ticker(self.symbol, 'futures')

            funding_rate, _ = self.exchange.get_funding_rate(self.symbol)

            edge_bps = calculate_funding_edge(
                funding_rate,
                self.fee_bps,
                self.slippage_bps
            )

            next_funding = get_next_funding_time()

            is_profitable = is_profitable_opportunity(edge_bps, self.threshold_bps)

            opportunity = FundingOpportunity(
                symbol=self.symbol,
                funding_rate_bps=funding_rate * 10000,
                spot_price=spot_ticker['bid'],
                futures_price=futures_ticker['ask'],
                notional_usdt=self.notional_usdt,
                edge_bps=edge_bps,
                fees_bps=self.fee_bps,
                slippage_bps=self.slippage_bps,
                next_funding_time=next_funding,
                is_profitable=is_profitable
            )

            return opportunity

        except Exception as e:
            logger.error(f"Failed to check funding opportunity: {e}")
            return None

    def open_position(self, opportunity: FundingOpportunity) -> bool:
        if self.position:
            logger.warning("Position already exists")
            return False

        if not self.risk_guard.can_open_position(opportunity):
            logger.warning("Risk guard prevented position opening")
            return False

        try:
            spot_amount = calculate_position_size(
                opportunity.notional_usdt,
                opportunity.spot_price,
                1.0
            )

            futures_amount = calculate_position_size(
                opportunity.notional_usdt,
                opportunity.futures_price,
                self.leverage
            )

            self.exchange.set_leverage(self.symbol, self.leverage)

            spot_order = self.exchange.place_spot_order(
                symbol=self.symbol,
                side='buy',
                amount=spot_amount,
                price=opportunity.spot_price,
                order_type='limit' if self.maker_only else 'market',
                post_only=self.maker_only
            )

            futures_order = self.exchange.place_futures_order(
                symbol=self.symbol,
                side='sell',
                amount=futures_amount,
                price=opportunity.futures_price,
                order_type='limit' if self.maker_only else 'market',
                post_only=self.maker_only
            )

            self.position = Position(
                symbol=self.symbol,
                spot_amount=spot_amount,
                futures_amount=futures_amount,
                spot_entry_price=opportunity.spot_price,
                futures_entry_price=opportunity.futures_price,
                notional_usdt=opportunity.notional_usdt,
                entry_time=get_utc_now()
            )

            mode_prefix = "[DRY-RUN] " if self.dry_run else ""
            msg = (
                f"{mode_prefix}✅ Opened position\n"
                f"Symbol: {self.symbol}\n"
                f"Notional: ${opportunity.notional_usdt:.2f}\n"
                f"Edge: {opportunity.edge_bps:.2f} bps\n"
                f"Spot: ${opportunity.spot_price:.2f}\n"
                f"Futures: ${opportunity.futures_price:.2f}"
            )

            logger.info(msg)
            self.telegram.send_message(msg)
            self._save_state()

            return True

        except Exception as e:
            logger.error(f"Failed to open position: {e}")
            self.telegram.send_message(f"❌ Failed to open position: {str(e)}")
            return False

    def close_position(self) -> bool:
        if not self.position:
            logger.warning("No position to close")
            return False

        try:
            spot_ticker = self.exchange.get_ticker(self.symbol, 'spot')
            futures_ticker = self.exchange.get_ticker(self.symbol, 'futures')

            spot_order = self.exchange.place_spot_order(
                symbol=self.symbol,
                side='sell',
                amount=self.position.spot_amount,
                price=spot_ticker['ask'],
                order_type='limit' if self.maker_only else 'market',
                post_only=self.maker_only
            )

            futures_order = self.exchange.place_futures_order(
                symbol=self.symbol,
                side='buy',
                amount=self.position.futures_amount,
                price=futures_ticker['bid'],
                order_type='limit' if self.maker_only else 'market',
                reduce_only=True,
                post_only=self.maker_only
            )

            final_pnl = self.position.calculate_pnl(
                spot_ticker['ask'],
                futures_ticker['bid'],
                0.0
            )

            msg = (
                f"📊 Closed position\n"
                f"Symbol: {self.symbol}\n"
                f"Duration: {format_duration((get_utc_now() - self.position.entry_time).total_seconds())}\n"
                f"Funding collected: ${self.position.funding_collected:.4f}\n"
                f"Total P&L: ${final_pnl:.4f}"
            )

            logger.info(msg)
            self.telegram.send_message(msg)

            self.position.realized_pnl = final_pnl
            self._save_state()
            self.position = None

            return True

        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            self.telegram.send_message(f"❌ Failed to close position: {str(e)}")
            return False

    def collect_funding(self):
        if not self.position:
            return

        try:
            funding_rate, _ = self.exchange.get_funding_rate(self.symbol)
            futures_ticker = self.exchange.get_ticker(self.symbol, 'futures')

            payment = calculate_funding_payment(
                self.position.futures_amount,
                futures_ticker['last'],
                funding_rate
            )

            self.position.funding_collected += payment

            msg = (
                f"💰 Funding collected\n"
                f"Symbol: {self.symbol}\n"
                f"Payment: ${payment:.4f}\n"
                f"Total collected: ${self.position.funding_collected:.4f}"
            )

            logger.info(msg)
            self.telegram.send_message(msg)
            self._save_state()

        except Exception as e:
            logger.error(f"Failed to collect funding: {e}")

    def run_cycle(self):
        try:
            opportunity = self.check_funding_opportunity()
            if not opportunity:
                return

            next_funding = opportunity.next_funding_time
            time_to_funding = seconds_until(next_funding)

            status = "DRY-RUN" if self.dry_run else "LIVE"
            logger.info(
                f"[{status}] Next funding in {format_duration(time_to_funding)}, "
                f"Edge: {opportunity.edge_bps:.2f} bps, "
                f"Profitable: {opportunity.is_profitable}"
            )

            if time_to_funding < 300 and self.position:
                self.collect_funding()

            if time_to_funding < 60 and self.position:
                logger.info("Closing position before funding window ends")
                self.close_position()

            elif opportunity.is_profitable and not self.position and time_to_funding > 300:
                logger.info(f"Opening position with edge of {opportunity.edge_bps:.2f} bps")
                self.open_position(opportunity)

            if self.position:
                spot_ticker = self.exchange.get_ticker(self.symbol, 'spot')
                futures_ticker = self.exchange.get_ticker(self.symbol, 'futures')
                current_pnl = self.position.calculate_pnl(
                    spot_ticker['last'],
                    futures_ticker['last'],
                    0.0
                )
                logger.debug(f"Current P&L: ${current_pnl:.4f}")

        except Exception as e:
            logger.error(f"Error in run cycle: {e}")

    def run(self, loop_seconds: int = 300):
        mode = 'DRY-RUN' if self.dry_run else 'LIVE'
        logger.info(f"Starting funding executor ({mode})")

        # Send startup notification
        startup_msg = (
            f"🚀 Bot started in {mode} mode\n"
            f"Symbol: {self.symbol}\n"
            f"Notional: ${self.notional_usdt}\n"
            f"Threshold: {self.threshold_bps} bps"
        )
        self.telegram.send_message(startup_msg)

        self.exchange.load_markets()

        cycles = 0
        while self.running and cycles < 2:
            if self._check_kill_switch():
                break

            self.run_cycle()

            if self.dry_run:
                cycles += 1

            if self.running and (not self.dry_run or cycles < 2):
                time.sleep(loop_seconds)

        if self.position:
            logger.info("Closing position before shutdown")
            self.close_position()

        self._save_state()
        logger.info("Funding executor stopped")