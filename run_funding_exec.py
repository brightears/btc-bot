#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

from src.funding.executor import FundingExecutor
from src.utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()


def load_config(config_path: str = "config.yaml") -> dict:
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def main():
    parser = argparse.ArgumentParser(description='BTC Funding-Carry Bot')

    parser.add_argument(
        '--live',
        action='store_true',
        help='Enable live trading (requires LIVE_TRADING=YES env var)'
    )

    parser.add_argument(
        '--notional_usdt',
        type=float,
        help='Notional amount in USDT'
    )

    parser.add_argument(
        '--threshold_bps',
        type=float,
        help='Minimum edge threshold in basis points'
    )

    parser.add_argument(
        '--loop_seconds',
        type=int,
        default=300,
        help='Loop interval in seconds (default: 300)'
    )

    parser.add_argument(
        '--maker_only',
        action='store_true',
        default=True,
        help='Use maker-only orders'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file'
    )

    args = parser.parse_args()

    config = load_config(args.config)

    if args.notional_usdt:
        config['notional_usdt'] = args.notional_usdt

    if args.threshold_bps:
        config['threshold_bps'] = args.threshold_bps

    config['maker_only'] = args.maker_only

    live_env = os.getenv('LIVE_TRADING') == 'YES'
    dry_run = not (args.live and live_env)

    if args.live and not live_env:
        print("⚠️  Live trading requires LIVE_TRADING=YES environment variable")
        print("Running in DRY-RUN mode")

    log_level = config.get('log_level', 'INFO')
    setup_logger(level=log_level)

    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Starting BTC Funding-Carry Bot in {mode} mode")
    print(f"Symbol: {config.get('symbol', 'BTC/USDT')}")
    print(f"Notional: ${config.get('notional_usdt', 100)}")
    print(f"Threshold: {config.get('threshold_bps', 0.5)} bps")
    print(f"Loop: {args.loop_seconds}s")
    print("-" * 40)

    executor = FundingExecutor(config, dry_run=dry_run)

    try:
        executor.run(loop_seconds=args.loop_seconds)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()