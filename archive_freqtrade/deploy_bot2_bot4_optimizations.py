#!/usr/bin/env python3
"""
Bot2 & Bot4 Parallel Optimization Deployment Script
Date: November 4, 2025
Purpose: Deploy conservative parameter optimizations for Strategy004 bots
"""

import json
import subprocess
import sys
from datetime import datetime
import time

# SSH command prefix
SSH_PREFIX = "ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219"

def run_ssh_command(command, description=""):
    """Execute command on VPS via SSH"""
    full_command = f'{SSH_PREFIX} "{command}"'
    print(f"\n{'='*60}")
    print(f"Executing: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False, result.stderr
        print(f"✅ Success: {result.stdout}")
        return True, result.stdout
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, str(e)

def backup_configs():
    """Backup current configurations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "="*80)
    print("STEP 1: BACKING UP CURRENT CONFIGURATIONS")
    print("="*80)

    # Backup Bot2
    success, output = run_ssh_command(
        f"cp /root/btc-bot/bot2_strategy004/config.json "
        f"/root/btc-bot/bot2_strategy004/config.backup.{timestamp}.json",
        "Backing up Bot2 config"
    )
    if not success:
        return False

    # Backup Bot4
    success, output = run_ssh_command(
        f"cp /root/btc-bot/bot4_paxg_strategy004/config.json "
        f"/root/btc-bot/bot4_paxg_strategy004/config.backup.{timestamp}.json",
        "Backing up Bot4 config"
    )
    if not success:
        return False

    print(f"\n✅ Backups created with timestamp: {timestamp}")
    return True

def update_bot2_parameters():
    """Update Bot2 parameters with conservative optimizations"""
    print("\n" + "="*80)
    print("STEP 2: UPDATING BOT2 PARAMETERS")
    print("="*80)

    update_script = """
import json

config_path = '/root/btc-bot/bot2_strategy004/config.json'

# Read current config
with open(config_path, 'r') as f:
    config = json.load(f)

# Update with optimized parameters for BTC/USDT
config['minimal_roi'] = {
    '0': 0.015,   # 1.5% immediate
    '20': 0.012,  # 1.2% after 20min
    '40': 0.008,  # 0.8% after 40min
    '60': 0.005   # 0.5% after 60min
}
config['stoploss'] = -0.025  # 2.5% stop-loss
config['trailing_stop'] = True
config['trailing_stop_positive'] = 0.006  # 0.6% profit trigger
config['trailing_stop_positive_offset'] = 0.010  # 1.0% offset
config['trailing_only_offset_is_reached'] = True

# Ensure exit signals are enabled
config['use_exit_signal'] = True
config['exit_profit_only'] = False

# Write updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('Bot2 parameters updated successfully!')
print(f'ROI: {config["minimal_roi"]}')
print(f'Stoploss: {config["stoploss"]}')
print(f'Trailing: {config["trailing_stop"]}')
"""

    # Write script to VPS
    success, output = run_ssh_command(
        f"cat > /tmp/update_bot2.py << 'EOF'\n{update_script}\nEOF",
        "Writing Bot2 update script"
    )
    if not success:
        return False

    # Execute script
    success, output = run_ssh_command(
        "python3 /tmp/update_bot2.py",
        "Executing Bot2 parameter update"
    )
    if not success:
        return False

    return True

def update_bot4_parameters():
    """Update Bot4 parameters with conservative optimizations"""
    print("\n" + "="*80)
    print("STEP 3: UPDATING BOT4 PARAMETERS")
    print("="*80)

    update_script = """
import json

config_path = '/root/btc-bot/bot4_paxg_strategy004/config.json'

# Read current config
with open(config_path, 'r') as f:
    config = json.load(f)

# Update with optimized parameters for PAXG/USDT
config['minimal_roi'] = {
    '0': 0.010,   # 1.0% immediate
    '30': 0.007,  # 0.7% after 30min
    '60': 0.004,  # 0.4% after 60min
    '120': 0.002  # 0.2% after 2 hours
}
config['stoploss'] = -0.015  # 1.5% stop-loss
config['trailing_stop'] = True
config['trailing_stop_positive'] = 0.004  # 0.4% profit trigger
config['trailing_stop_positive_offset'] = 0.006  # 0.6% offset
config['trailing_only_offset_is_reached'] = True

# Ensure exit signals are enabled
config['use_exit_signal'] = True
config['exit_profit_only'] = False

# Write updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('Bot4 parameters updated successfully!')
print(f'ROI: {config["minimal_roi"]}')
print(f'Stoploss: {config["stoploss"]}')
print(f'Trailing: {config["trailing_stop"]}')
"""

    # Write script to VPS
    success, output = run_ssh_command(
        f"cat > /tmp/update_bot4.py << 'EOF'\n{update_script}\nEOF",
        "Writing Bot4 update script"
    )
    if not success:
        return False

    # Execute script
    success, output = run_ssh_command(
        "python3 /tmp/update_bot4.py",
        "Executing Bot4 parameter update"
    )
    if not success:
        return False

    return True

def restart_bots():
    """Restart Bot2 and Bot4 with new parameters"""
    print("\n" + "="*80)
    print("STEP 4: RESTARTING BOTS WITH NEW PARAMETERS")
    print("="*80)

    # Kill Bot2
    success, output = run_ssh_command(
        "pkill -f 'bot2_strategy004'",
        "Stopping Bot2"
    )
    time.sleep(5)

    # Kill Bot4
    success, output = run_ssh_command(
        "pkill -f 'bot4_paxg_strategy004'",
        "Stopping Bot4"
    )
    time.sleep(5)

    # Start Bot2
    success, output = run_ssh_command(
        "cd /root/btc-bot && nohup .venv/bin/freqtrade trade "
        "--config bot2_strategy004/config.json "
        "--strategy Strategy004 "
        "> bot2_strategy004/nohup.out 2>&1 &",
        "Starting Bot2"
    )
    if not success:
        return False

    time.sleep(5)

    # Start Bot4
    success, output = run_ssh_command(
        "cd /root/btc-bot && nohup .venv/bin/freqtrade trade "
        "--config bot4_paxg_strategy004/config.json "
        "--strategy Strategy004 "
        "> bot4_paxg_strategy004/nohup.out 2>&1 &",
        "Starting Bot4"
    )
    if not success:
        return False

    print("\n✅ Bots restarted successfully")
    return True

def verify_deployment():
    """Verify bots are running with new parameters"""
    print("\n" + "="*80)
    print("STEP 5: VERIFYING DEPLOYMENT")
    print("="*80)

    time.sleep(10)  # Wait for bots to fully start

    # Check running processes
    success, output = run_ssh_command(
        "ps aux | grep -E 'bot2_strategy004|bot4_paxg_strategy004' | grep -v grep",
        "Checking running processes"
    )
    if not success or not output:
        print("❌ Warning: Bots may not be running")
        return False

    # Check Bot2 logs for parameter confirmation
    success, output = run_ssh_command(
        "tail -20 /root/btc-bot/bot2_strategy004/nohup.out | grep -E 'stoploss|minimal_roi'",
        "Checking Bot2 parameter loading"
    )

    # Check Bot4 logs for parameter confirmation
    success, output = run_ssh_command(
        "tail -20 /root/btc-bot/bot4_paxg_strategy004/nohup.out | grep -E 'stoploss|minimal_roi'",
        "Checking Bot4 parameter loading"
    )

    # Count total running bots
    success, output = run_ssh_command(
        "ps aux | grep freqtrade | grep -v grep | wc -l",
        "Counting total running bots"
    )
    if success and output:
        bot_count = int(output.strip())
        print(f"\n📊 Total bots running: {bot_count}")
        if bot_count < 6:
            print("⚠️ Warning: Expected 6 bots, found", bot_count)

    return True

def create_rollback_script():
    """Create rollback script for emergency use"""
    print("\n" + "="*80)
    print("STEP 6: CREATING ROLLBACK SCRIPT")
    print("="*80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rollback_script = f"""#!/bin/bash
# Emergency rollback script for Bot2 & Bot4
# Created: {timestamp}

echo "Starting emergency rollback..."

# Stop bots
pkill -f 'bot2_strategy004'
pkill -f 'bot4_paxg_strategy004'
sleep 5

# Restore configs
cp /root/btc-bot/bot2_strategy004/config.backup.{timestamp}.json /root/btc-bot/bot2_strategy004/config.json
cp /root/btc-bot/bot4_paxg_strategy004/config.backup.{timestamp}.json /root/btc-bot/bot4_paxg_strategy004/config.json

# Restart bots
cd /root/btc-bot
nohup .venv/bin/freqtrade trade --config bot2_strategy004/config.json --strategy Strategy004 > bot2_strategy004/nohup.out 2>&1 &
sleep 5
nohup .venv/bin/freqtrade trade --config bot4_paxg_strategy004/config.json --strategy Strategy004 > bot4_paxg_strategy004/nohup.out 2>&1 &

echo "Rollback complete!"
ps aux | grep freqtrade | grep -v grep
"""

    success, output = run_ssh_command(
        f"cat > /root/btc-bot/rollback_bot2_bot4.sh << 'EOF'\n{rollback_script}\nEOF && "
        f"chmod +x /root/btc-bot/rollback_bot2_bot4.sh",
        "Creating rollback script"
    )

    if success:
        print(f"\n✅ Rollback script created: /root/btc-bot/rollback_bot2_bot4.sh")
        print("   To rollback, run: ./rollback_bot2_bot4.sh")

    return success

def main():
    """Main deployment function"""
    print("\n" + "="*80)
    print(" BOT2 & BOT4 OPTIMIZATION DEPLOYMENT")
    print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*80)

    print("\n⚠️  WARNING: This will modify Bot2 and Bot4 parameters!")
    print("   Bot2: Strategy004 - BTC/USDT")
    print("   Bot4: Strategy004 - PAXG/USDT")

    response = input("\nProceed with deployment? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Deployment cancelled")
        return

    # Execute deployment steps
    steps = [
        ("Backing up configurations", backup_configs),
        ("Updating Bot2 parameters", update_bot2_parameters),
        ("Updating Bot4 parameters", update_bot4_parameters),
        ("Restarting bots", restart_bots),
        ("Verifying deployment", verify_deployment),
        ("Creating rollback script", create_rollback_script)
    ]

    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"\n❌ Deployment failed at: {step_name}")
            print("   Please check the errors and consider manual rollback")
            return

    print("\n" + "="*80)
    print(" DEPLOYMENT COMPLETE!")
    print("="*80)
    print("\n✅ Bot2 and Bot4 have been updated with optimized parameters")
    print("\n📊 Next Steps:")
    print("   1. Monitor closely for the next 2 hours")
    print("   2. Check first trades for proper execution")
    print("   3. Review 24-hour checkpoint tomorrow")
    print("   4. Full validation after 7 days")
    print("\n🔄 Rollback available at: /root/btc-bot/rollback_bot2_bot4.sh")
    print("\n📈 Success Criteria:")
    print("   Bot2: ≥7 trades, ≥45% win rate in 7 days")
    print("   Bot4: ≥3 trades, ≥40% win rate in 7 days")

if __name__ == "__main__":
    main()