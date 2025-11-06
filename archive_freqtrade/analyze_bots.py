#!/usr/bin/env python3
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Bot5 trades
conn5 = sqlite3.connect("bot5_paxg_strategy004_opt/tradesv3.dryrun.sqlite")
trades5 = pd.read_sql("SELECT * FROM trades WHERE close_date IS NOT NULL ORDER BY close_date DESC LIMIT 20", conn5)
conn5.close()

# Bot4 trades
conn4 = sqlite3.connect("bot4_paxg_strategy004/tradesv3.dryrun.sqlite")
trades4 = pd.read_sql("SELECT * FROM trades WHERE close_date IS NOT NULL ORDER BY close_date DESC LIMIT 20", conn4)
conn4.close()

print("BOT5 RECENT TRADES (Optimized):")
if not trades5.empty:
    for _, t in trades5.head(10).iterrows():
        profit_pct = (t["close_profit_abs"] / t["stake_amount"]) * 100 if t["stake_amount"] else 0
        print(f'  Profit: {t["close_profit_abs"]:.2f} USDT ({profit_pct:.2f}%), Exit: {t["exit_reason"]}')
    print(f'  Total trades: {len(trades5)}, Total P&L: {trades5["close_profit_abs"].sum():.2f} USDT')
    print(f'  Win rate: {(trades5["close_profit_abs"] > 0).mean()*100:.1f}%')
    print(f'  Avg profit per trade: {trades5["close_profit_abs"].mean():.2f} USDT')
else:
    print("  No recent trades")

print("\nBOT4 RECENT TRADES (Baseline):")
if not trades4.empty:
    for _, t in trades4.head(10).iterrows():
        profit_pct = (t["close_profit_abs"] / t["stake_amount"]) * 100 if t["stake_amount"] else 0
        print(f'  Profit: {t["close_profit_abs"]:.2f} USDT ({profit_pct:.2f}%), Exit: {t["exit_reason"]}')
    print(f'  Total trades: {len(trades4)}, Total P&L: {trades4["close_profit_abs"].sum():.2f} USDT')
    print(f'  Win rate: {(trades4["close_profit_abs"] > 0).mean()*100:.1f}%')
    print(f'  Avg profit per trade: {trades4["close_profit_abs"].mean():.2f} USDT')
else:
    print("  No recent trades")