#!/usr/bin/env python3
"""
Bot2 & Bot4 Optimization Monitoring Script
Date: November 4, 2025
Purpose: Monitor performance of Bot2 & Bot4 after optimization deployment
"""

import subprocess
import json
from datetime import datetime, timedelta
import sys

# SSH command prefix
SSH_PREFIX = "ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219"

def run_ssh_command(command):
    """Execute command on VPS via SSH"""
    full_command = f'{SSH_PREFIX} "{command}"'
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def check_bot_status():
    """Check if bots are running"""
    print("\n" + "="*60)
    print("BOT STATUS CHECK")
    print("="*60)

    # Check Bot2
    bot2_status = run_ssh_command("ps aux | grep 'bot2_strategy004' | grep -v grep | wc -l")
    bot2_running = int(bot2_status) > 0 if bot2_status else False

    # Check Bot4
    bot4_status = run_ssh_command("ps aux | grep 'bot4_paxg_strategy004' | grep -v grep | wc -l")
    bot4_running = int(bot4_status) > 0 if bot4_status else False

    print(f"Bot2 (BTC/USDT):  {'✅ Running' if bot2_running else '❌ Stopped'}")
    print(f"Bot4 (PAXG/USDT): {'✅ Running' if bot4_running else '❌ Stopped'}")

    return bot2_running, bot4_running

def check_parameters():
    """Verify deployed parameters"""
    print("\n" + "="*60)
    print("PARAMETER VERIFICATION")
    print("="*60)

    # Check Bot2 parameters
    bot2_config = run_ssh_command("cat /root/btc-bot/bot2_strategy004/config.json")
    if bot2_config:
        config = json.loads(bot2_config)
        print("\nBot2 Parameters:")
        print(f"  ROI: {config.get('minimal_roi', 'Not found')}")
        print(f"  Stoploss: {config.get('stoploss', 'Not found')}")
        print(f"  Trailing Stop: {config.get('trailing_stop', 'Not found')}")

    # Check Bot4 parameters
    bot4_config = run_ssh_command("cat /root/btc-bot/bot4_paxg_strategy004/config.json")
    if bot4_config:
        config = json.loads(bot4_config)
        print("\nBot4 Parameters:")
        print(f"  ROI: {config.get('minimal_roi', 'Not found')}")
        print(f"  Stoploss: {config.get('stoploss', 'Not found')}")
        print(f"  Trailing Stop: {config.get('trailing_stop', 'Not found')}")

def check_performance():
    """Check trading performance metrics"""
    print("\n" + "="*60)
    print("PERFORMANCE METRICS")
    print("="*60)

    # Bot2 performance
    print("\nBot2 (Strategy004 - BTC/USDT):")
    bot2_query = """
    SELECT
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit_abs > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN close_profit_abs <= 0 THEN 1 ELSE 0 END) as losses,
        ROUND(AVG(close_profit_abs), 4) as avg_pl,
        ROUND(SUM(close_profit_abs), 2) as total_pl,
        ROUND(AVG(CASE WHEN close_profit_abs > 0 THEN close_profit_abs END), 4) as avg_win,
        ROUND(AVG(CASE WHEN close_profit_abs <= 0 THEN close_profit_abs END), 4) as avg_loss
    FROM trades
    WHERE close_date > datetime('now', '-7 days')
    """

    bot2_result = run_ssh_command(
        f"sqlite3 /root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite \"{bot2_query}\""
    )

    if bot2_result:
        metrics = bot2_result.split('|')
        if len(metrics) >= 7:
            total = int(metrics[0]) if metrics[0] else 0
            wins = int(metrics[1]) if metrics[1] else 0
            losses = int(metrics[2]) if metrics[2] else 0
            win_rate = (wins / total * 100) if total > 0 else 0

            print(f"  Total Trades (7d): {total}")
            print(f"  Win Rate: {win_rate:.1f}% ({wins}W/{losses}L)")
            print(f"  Total P&L: ${metrics[4]} USDT")
            print(f"  Avg P&L: ${metrics[3]} USDT")
            print(f"  Avg Win: ${metrics[5]} USDT")
            print(f"  Avg Loss: ${metrics[6]} USDT")

    # Bot4 performance
    print("\nBot4 (Strategy004 - PAXG/USDT):")
    bot4_result = run_ssh_command(
        f"sqlite3 /root/btc-bot/bot4_paxg_strategy004/tradesv3.dryrun.sqlite \"{bot2_query}\""
    )

    if bot4_result:
        metrics = bot4_result.split('|')
        if len(metrics) >= 7:
            total = int(metrics[0]) if metrics[0] else 0
            wins = int(metrics[1]) if metrics[1] else 0
            losses = int(metrics[2]) if metrics[2] else 0
            win_rate = (wins / total * 100) if total > 0 else 0

            print(f"  Total Trades (7d): {total}")
            print(f"  Win Rate: {win_rate:.1f}% ({wins}W/{losses}L)")
            print(f"  Total P&L: ${metrics[4]} USDT")
            print(f"  Avg P&L: ${metrics[3]} USDT")
            print(f"  Avg Win: ${metrics[5]} USDT")
            print(f"  Avg Loss: ${metrics[6]} USDT")

def check_recent_trades():
    """Show recent trades for both bots"""
    print("\n" + "="*60)
    print("RECENT TRADES (Last 24 Hours)")
    print("="*60)

    # Bot2 recent trades
    print("\nBot2 Recent Trades:")
    bot2_trades = run_ssh_command("""
        sqlite3 /root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite "
        SELECT
            strftime('%m-%d %H:%M', open_date) as opened,
            strftime('%H:%M', close_date) as closed,
            ROUND(close_profit_abs, 2) as pl,
            exit_reason
        FROM trades
        WHERE close_date > datetime('now', '-24 hours')
        ORDER BY close_date DESC
        LIMIT 5"
    """)

    if bot2_trades:
        print(bot2_trades)
    else:
        print("  No trades in last 24 hours")

    # Bot4 recent trades
    print("\nBot4 Recent Trades:")
    bot4_trades = run_ssh_command("""
        sqlite3 /root/btc-bot/bot4_paxg_strategy004/tradesv3.dryrun.sqlite "
        SELECT
            strftime('%m-%d %H:%M', open_date) as opened,
            strftime('%H:%M', close_date) as closed,
            ROUND(close_profit_abs, 2) as pl,
            exit_reason
        FROM trades
        WHERE close_date > datetime('now', '-24 hours')
        ORDER BY close_date DESC
        LIMIT 5"
    """)

    if bot4_trades:
        print(bot4_trades)
    else:
        print("  No trades in last 24 hours")

def check_rollback_triggers():
    """Check if any rollback conditions are met"""
    print("\n" + "="*60)
    print("ROLLBACK TRIGGER ANALYSIS")
    print("="*60)

    triggers = []

    # Check 24h losses
    bot2_24h_loss = run_ssh_command("""
        sqlite3 /root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite "
        SELECT ROUND(SUM(close_profit_abs), 2)
        FROM trades
        WHERE close_date > datetime('now', '-24 hours')"
    """)

    bot4_24h_loss = run_ssh_command("""
        sqlite3 /root/btc-bot/bot4_paxg_strategy004/tradesv3.dryrun.sqlite "
        SELECT ROUND(SUM(close_profit_abs), 2)
        FROM trades
        WHERE close_date > datetime('now', '-24 hours')"
    """)

    bot2_loss = float(bot2_24h_loss) if bot2_24h_loss else 0
    bot4_loss = float(bot4_24h_loss) if bot4_24h_loss else 0

    print(f"Bot2 24h P&L: ${bot2_loss:.2f}")
    print(f"Bot4 24h P&L: ${bot4_loss:.2f}")

    if bot2_loss < -100:
        triggers.append(f"❌ Bot2 daily loss exceeds $100: ${bot2_loss:.2f}")
    if bot4_loss < -100:
        triggers.append(f"❌ Bot4 daily loss exceeds $100: ${bot4_loss:.2f}")

    # Check combined 48h loss
    combined_loss = bot2_loss + bot4_loss
    if combined_loss < -50:
        triggers.append(f"⚠️ Combined loss approaching limit: ${combined_loss:.2f}")

    # Check win rates
    bot2_stats = run_ssh_command("""
        sqlite3 /root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite "
        SELECT
            COUNT(*),
            SUM(CASE WHEN close_profit_abs > 0 THEN 1 ELSE 0 END)
        FROM trades
        WHERE close_date > datetime('now', '-2 days')"
    """)

    if bot2_stats:
        parts = bot2_stats.split('|')
        if len(parts) == 2 and parts[0] and int(parts[0]) >= 5:
            total = int(parts[0])
            wins = int(parts[1]) if parts[1] else 0
            win_rate = (wins / total * 100) if total > 0 else 0
            if win_rate < 20:
                triggers.append(f"⚠️ Bot2 win rate below 20%: {win_rate:.1f}%")

    if triggers:
        print("\n⚠️ ROLLBACK TRIGGERS DETECTED:")
        for trigger in triggers:
            print(f"  {trigger}")
        print("\n  Consider executing: /root/btc-bot/rollback_bot2_bot4.sh")
    else:
        print("\n✅ No rollback triggers detected")

def generate_summary():
    """Generate monitoring summary"""
    print("\n" + "="*60)
    print("MONITORING SUMMARY")
    print("="*60)

    deployment_time = datetime(2025, 11, 4, 10, 0)  # Adjust based on actual deployment
    time_elapsed = datetime.now() - deployment_time

    print(f"\nTime Since Deployment: {time_elapsed}")
    print(f"Monitoring Period: 7 days")
    print(f"Next Checkpoint: {deployment_time + timedelta(days=1)}")

    print("\n📊 Success Criteria Progress:")
    print("Bot2: Target ≥7 trades, ≥45% win rate in 7 days")
    print("Bot4: Target ≥3 trades, ≥40% win rate in 7 days")

    print("\n📋 Monitoring Schedule:")
    if time_elapsed < timedelta(days=1):
        print("  Status: 24-HOUR CHECKPOINT")
        print("  Action: Close monitoring, check every 2 hours")
    elif time_elapsed < timedelta(days=2):
        print("  Status: 48-HOUR CHECKPOINT")
        print("  Action: Go/No-go decision point")
    elif time_elapsed < timedelta(days=7):
        print("  Status: VALIDATION PERIOD")
        print("  Action: Daily monitoring")
    else:
        print("  Status: FINAL ASSESSMENT")
        print("  Action: Success/failure determination")

def main():
    """Main monitoring function"""
    print("\n" + "="*80)
    print(" BOT2 & BOT4 OPTIMIZATION MONITORING")
    print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*80)

    # Run all checks
    bot2_running, bot4_running = check_bot_status()

    if not bot2_running or not bot4_running:
        print("\n⚠️ WARNING: One or both bots are not running!")
        print("  Please check and restart if necessary")

    check_parameters()
    check_performance()
    check_recent_trades()
    check_rollback_triggers()
    generate_summary()

    print("\n" + "="*80)
    print(" END OF MONITORING REPORT")
    print("="*80)

if __name__ == "__main__":
    main()