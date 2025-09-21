#!/usr/bin/env python3
"""
Enable live trading mode for approved strategies
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

def go_live():
    """Enable live trading for all approved strategies"""

    print("\n" + "=" * 60)
    print("🚀 ENABLE LIVE TRADING")
    print("=" * 60 + "\n")

    # Check for approved strategies
    if not os.path.exists('live_trading_config.json'):
        print("❌ No strategies approved for live trading")
        print("\nUse 'python approve_strategy.py <id>' to approve strategies first")
        return False

    with open('live_trading_config.json', 'r') as f:
        config = json.load(f)

    print(f"📊 Approved Strategy: {config['strategy_name']}")
    print(f"ID: {config['strategy_id'][:8]}")
    print(f"Approved: {config['approved_at']}")
    print()
    print("🛡️ Safety Limits:")
    print(f"• Max Position Size: ${config['max_position_size']}")
    print(f"• Stop Loss: {config['stop_loss']*100:.1f}%")
    print(f"• Daily Loss Limit: ${config['daily_loss_limit']}")
    print()

    # Check exchange credentials
    has_api_key = bool(os.getenv('BINANCE_API_KEY'))
    has_api_secret = bool(os.getenv('BINANCE_API_SECRET'))

    if not has_api_key or not has_api_secret:
        print("❌ Exchange API credentials not found!")
        print("\nPlease set in .env file:")
        print("  BINANCE_API_KEY=your_api_key")
        print("  BINANCE_API_SECRET=your_api_secret")
        return False

    print("✅ Exchange credentials found")
    print()

    # Final confirmation
    print("⚠️  WARNING: This will enable REAL MONEY trading!")
    print("Make sure you:")
    print("• Have tested thoroughly in dry-run mode")
    print("• Understand the risks involved")
    print("• Have sufficient balance in your account")
    print("• Are prepared to monitor the system")
    print()

    response = input("Enable LIVE TRADING? Type 'GO LIVE' to confirm: ")

    if response == "GO LIVE":
        # Enable live trading in .env
        env_file = '.env'
        set_key(env_file, 'ENABLE_LIVE_TRADING', 'true')

        # Create live trading marker
        live_marker = {
            'enabled': True,
            'enabled_at': datetime.now().isoformat(),
            'strategy_id': config['strategy_id'],
            'strategy_name': config['strategy_name'],
            'safety_limits': {
                'max_position_size': config['max_position_size'],
                'stop_loss': config['stop_loss'],
                'daily_loss_limit': config['daily_loss_limit']
            }
        }

        with open('LIVE_TRADING_ACTIVE.json', 'w') as f:
            json.dump(live_marker, f, indent=2)

        print("\n" + "=" * 60)
        print("✅ LIVE TRADING ENABLED!")
        print("=" * 60)
        print()
        print("The system will now execute REAL trades")
        print()
        print("📱 Monitor via:")
        print("• Telegram notifications")
        print("• python get_status.py")
        print("• tail -f logs/funding_exec.log")
        print()
        print("🛑 To stop live trading:")
        print("• python stop_trading.py")
        print("• Or set ENABLE_LIVE_TRADING=false in .env")
        print()

        return True
    else:
        print("\n❌ Live trading NOT enabled")
        return False


if __name__ == "__main__":
    go_live()