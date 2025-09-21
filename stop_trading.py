#!/usr/bin/env python3
"""
Emergency stop for all trading activities
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

def stop_trading():
    """Stop all trading activities immediately"""

    print("\n" + "=" * 60)
    print("🛑 EMERGENCY STOP - DISABLE ALL TRADING")
    print("=" * 60 + "\n")

    # Disable live trading in .env
    env_file = '.env'
    set_key(env_file, 'ENABLE_LIVE_TRADING', 'false')
    print("✅ Disabled ENABLE_LIVE_TRADING in .env")

    # Remove live trading marker
    if os.path.exists('LIVE_TRADING_ACTIVE.json'):
        # Archive it first
        with open('LIVE_TRADING_ACTIVE.json', 'r') as f:
            live_data = json.load(f)

        archive_name = f"archived_live_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f'logs/{archive_name}', 'w') as f:
            json.dump(live_data, f, indent=2)

        os.remove('LIVE_TRADING_ACTIVE.json')
        print(f"✅ Removed live trading marker (archived to logs/{archive_name})")

    # Kill all running bots
    import subprocess
    try:
        subprocess.run(['pkill', '-f', 'python.*ai_trading_lab'], capture_output=True)
        print("✅ Stopped AI Trading Lab")
    except:
        pass

    try:
        subprocess.run(['pkill', '-f', 'python.*run_funding_exec'], capture_output=True)
        print("✅ Stopped funding executor")
    except:
        pass

    # Create stop marker
    stop_marker = {
        'stopped_at': datetime.now().isoformat(),
        'reason': 'Manual emergency stop',
        'action': 'All trading disabled'
    }

    with open('TRADING_STOPPED.json', 'w') as f:
        json.dump(stop_marker, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ ALL TRADING STOPPED")
    print("=" * 60)
    print()
    print("• Live trading disabled")
    print("• All bots stopped")
    print("• Safety marker created")
    print()
    print("To restart:")
    print("1. Remove TRADING_STOPPED.json")
    print("2. python ai_trading_lab.py")
    print("3. python go_live.py (when ready)")
    print()


if __name__ == "__main__":
    response = input("⚠️  Stop all trading? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        stop_trading()
    else:
        print("Cancelled")