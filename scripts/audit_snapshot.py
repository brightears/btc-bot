#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime


def audit_state():
    state_file = Path("logs/state.json")

    if not state_file.exists():
        print("No state file found")
        return

    with open(state_file, 'r') as f:
        state = json.load(f)

    print("=" * 50)
    print("STATE AUDIT SNAPSHOT")
    print("=" * 50)
    print(f"Timestamp: {state.get('timestamp', 'N/A')}")
    print(f"Mode: {'DRY-RUN' if state.get('dry_run') else 'LIVE'}")

    if state.get('position'):
        pos = state['position']
        print("\n📊 Active Position:")
        print(f"  Symbol: {pos.get('symbol')}")
        print(f"  Notional: ${pos.get('notional_usdt', 0):.2f}")
        print(f"  Entry Time: {pos.get('entry_time')}")
        print(f"  Spot Entry: ${pos.get('spot_entry_price', 0):.2f}")
        print(f"  Futures Entry: ${pos.get('futures_entry_price', 0):.2f}")
        print(f"  Funding Collected: ${pos.get('funding_collected', 0):.4f}")
        print(f"  Realized P&L: ${pos.get('realized_pnl', 0):.4f}")
    else:
        print("\n📊 No active position")

    log_file = Path("logs/funding_exec.log")
    if log_file.exists():
        print("\n📝 Recent Activity:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                if "Opening position" in line or "Closing position" in line or "Edge:" in line:
                    print(f"  {line.strip()}")

    print("=" * 50)


if __name__ == "__main__":
    audit_state()