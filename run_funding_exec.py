#!/usr/bin/env python3
"""CLI entrypoint for the funding carry bot."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from exchange.binance import BinanceExchange
from funding.executor import FundingExecutor
from notify.telegram import TelegramNotifier
from utils.logger import configure_logging


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BTC funding carry executor")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--live", action="store_true", help="Enable live trading (requires env)")
    parser.add_argument("--notional_usdt", type=float, help="Override notional size in USDT")
    parser.add_argument("--threshold_bps", type=float, help="Override edge threshold in bps")
    parser.add_argument("--loop_seconds", type=int, help="Override polling interval seconds")
    parser.add_argument("--maker-only", dest="maker_only", action="store_true", help="Force maker-only")
    parser.add_argument("--no-maker-only", dest="maker_only", action="store_false", help="Allow taker fills")
    parser.set_defaults(maker_only=None)
    parser.add_argument("--max-loops", type=int, help="Maximum loop iterations (for testing)")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    load_dotenv(override=False)

    config_path = Path(args.config)
    config = load_config(str(config_path))

    if args.notional_usdt is not None:
        config["notional_usdt"] = args.notional_usdt
    if args.threshold_bps is not None:
        config["threshold_bps"] = args.threshold_bps
    if args.loop_seconds is not None:
        config["loop_seconds"] = args.loop_seconds
    if args.maker_only is not None:
        config["maker_only"] = args.maker_only

    logger = configure_logging(config.get("log_level", "INFO"))

    live_env = os.getenv("LIVE_TRADING", "NO").strip().upper() == "YES"
    live = bool(args.live and live_env)
    if args.live and not live_env:
        logger.warning("--live flag supplied but LIVE_TRADING env is not YES; running dry-run")

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notifier = TelegramNotifier(token=token, chat_id=chat_id, logger=logger)

    exchange = BinanceExchange(
        dry_run=not live,
        logger=logger,
        maker_only=config.get("maker_only", True),
        leverage=config.get("leverage", 1),
    )

    executor = FundingExecutor(
        exchange=exchange,
        notifier=notifier,
        config=config,
        logger=logger,
        dry_run=not live,
    )

    executor.run(max_loops=args.max_loops)


if __name__ == "__main__":
    main()
