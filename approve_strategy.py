#!/usr/bin/env python3
"""
Approve a strategy for live trading
"""

import sys
import json
import os
from datetime import datetime, timezone


def approve_strategy(strategy_id):
    """Approve a specific strategy for live trading"""

    # Check strategy exists
    strategy_file = f'knowledge/strategies/{strategy_id}.json'

    if not os.path.exists(strategy_file):
        # Try with partial ID
        import glob
        matches = glob.glob(f'knowledge/strategies/{strategy_id}*.json')
        if matches:
            strategy_file = matches[0]
        else:
            print(f"❌ Strategy {strategy_id} not found")
            print("\nAvailable strategies:")
            for file in glob.glob('knowledge/strategies/*.json'):
                with open(file, 'r') as f:
                    data = json.load(f)
                    print(f"  • {data['id'][:8]}: {data['name']}")
            return False

    # Load strategy
    with open(strategy_file, 'r') as f:
        strategy = json.load(f)

    print(f"\n📊 Strategy: {strategy['name']}")
    print(f"ID: {strategy['id'][:8]}")
    print(f"Confidence: {strategy.get('confidence_score', 0):.1f}%")

    metrics = strategy.get('metrics', {})
    if metrics:
        print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
        print(f"Total Trades: {metrics.get('total_trades', 0)}")
        print(f"Total P&L: ${metrics.get('total_pnl', 0):.2f}")

    # Confirm approval
    response = input("\n⚠️  Approve this strategy for LIVE TRADING? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        # Mark as approved
        strategy['approved_for_live'] = True
        strategy['approval_time'] = datetime.now(timezone.utc).isoformat()
        strategy['is_live'] = True

        # Save updated strategy
        with open(strategy_file, 'w') as f:
            json.dump(strategy, f, indent=2)

        # Update manager state
        state_file = 'knowledge/manager_state.json'
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)

            ready = state.get('ready_for_live', [])
            if strategy['id'] not in ready:
                ready.append(strategy['id'])
            state['ready_for_live'] = ready

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

        print(f"\n✅ Strategy {strategy['name']} APPROVED for live trading!")
        print("\n⚠️  IMPORTANT: Live trading will begin on next cycle")
        print("Make sure to:")
        print("1. Set ENABLE_LIVE_TRADING=true in .env")
        print("2. Have sufficient balance in your exchange account")
        print("3. Monitor the first few trades closely")

        # Create live trading config
        live_config = {
            'strategy_id': strategy['id'],
            'strategy_name': strategy['name'],
            'approved_at': datetime.now(timezone.utc).isoformat(),
            'max_position_size': 1000,  # Safety limit
            'stop_loss': 0.02,  # 2% stop loss
            'daily_loss_limit': 100,  # Max $100 loss per day
            'require_confirmation': True  # Require confirmation for first trade
        }

        with open('live_trading_config.json', 'w') as f:
            json.dump(live_config, f, indent=2)

        return True
    else:
        print("❌ Approval cancelled")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python approve_strategy.py <strategy_id>")
        print("\nExample: python approve_strategy.py funding123")
        print("\nUse 'python get_status.py' to see available strategies")
        sys.exit(1)

    strategy_id = sys.argv[1]
    approve_strategy(strategy_id)