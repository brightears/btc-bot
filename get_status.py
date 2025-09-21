#!/usr/bin/env python3
"""
Get current status of AI Trading Lab
"""

import json
import os
from datetime import datetime, timezone
from strategies.strategy_manager import StrategyManager
from strategies.funding_carry import FundingCarryStrategy

def get_status():
    """Display current status of all strategies and AI components"""

    print("\n" + "=" * 60)
    print("📊 AI TRADING LAB STATUS REPORT")
    print("=" * 60 + "\n")

    # Check if manager state exists
    state_file = 'knowledge/manager_state.json'
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)

        print("📈 MANAGER STATE")
        print("-" * 40)
        print(f"Total Strategies: {state.get('total_strategies', 0)}")
        print(f"Active Strategies: {state.get('active_strategies', 0)}")
        print(f"Ready for Live: {len(state.get('ready_for_live', []))}")

        last_eval = state.get('last_evaluation', 'Never')
        if last_eval != 'Never':
            last_eval_time = datetime.fromisoformat(last_eval.replace('+00:00', '+00:00'))
            age_minutes = (datetime.now(timezone.utc) - last_eval_time).total_seconds() / 60
            print(f"Last Evaluation: {int(age_minutes)} minutes ago")
        print()

    # Check hypotheses
    hyp_file = 'knowledge/hypotheses.json'
    if os.path.exists(hyp_file):
        with open(hyp_file, 'r') as f:
            hypotheses = json.load(f)

        print("🧪 HYPOTHESIS PIPELINE")
        print("-" * 40)
        print(f"Pending: {len(hypotheses.get('pending', []))}")
        print(f"Testing: {len(hypotheses.get('testing', []))}")
        print(f"Successful: {len(hypotheses.get('successful', []))}")
        print(f"Failed: {len(hypotheses.get('failed', []))}")
        print(f"Crazy Ideas: {len(hypotheses.get('crazy_ideas', []))}")
        print()

        # Show pending hypotheses
        pending = hypotheses.get('pending', [])
        if pending:
            print("📋 PENDING HYPOTHESES")
            print("-" * 40)
            for h in pending[:3]:  # Show top 3
                print(f"• {h['name']}")
                print(f"  Category: {h['category']}")
                print(f"  Confidence: {h['confidence']}%")
            print()

    # Check individual strategy files
    strategy_dir = 'knowledge/strategies'
    if os.path.exists(strategy_dir):
        import glob
        strategy_files = glob.glob(f'{strategy_dir}/*.json')

        if strategy_files:
            print("📊 INDIVIDUAL STRATEGIES")
            print("-" * 40)

            for file in strategy_files:
                with open(file, 'r') as f:
                    strategy_data = json.load(f)

                name = strategy_data.get('name', 'Unknown')
                confidence = strategy_data.get('confidence_score', 0)
                metrics = strategy_data.get('metrics', {})

                print(f"• {name}")
                print(f"  ID: {strategy_data.get('id', 'N/A')[:8]}")
                print(f"  Confidence: {confidence:.1f}%")

                if metrics:
                    print(f"  Win Rate: {metrics.get('win_rate', 0):.1f}%")
                    print(f"  Total Trades: {metrics.get('total_trades', 0)}")
                    print(f"  Total P&L: ${metrics.get('total_pnl', 0):.2f}")

                    ready = (
                        confidence >= 75 and
                        metrics.get('total_trades', 0) >= 50 and
                        metrics.get('win_rate', 0) >= 55
                    )
                    if ready:
                        print(f"  ⚡ READY FOR LIVE TRADING")
                print()

    # Check if bot is running
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'ai_trading_lab.py' in result.stdout:
            print("✅ AI Trading Lab is RUNNING")
        else:
            print("⚠️  AI Trading Lab is NOT RUNNING")
            print("   Start with: python ai_trading_lab.py")
    except:
        pass

    print("\n" + "=" * 60)
    print("Use 'python approve_strategy.py <id>' to approve a strategy")
    print("Use 'python go_live.py' to enable live trading mode")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    get_status()