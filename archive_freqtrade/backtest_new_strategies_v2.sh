#!/bin/bash
# Backtest Script v2 for CofiBitStrategy_LowVol and Low_BB_PAXG
# Date: Nov 4, 2025
# Test Period: Oct 15 - Nov 4 (20 days)
# Success Criteria:
#   - CofiBitStrategy: >55% win rate, >50 trades
#   - Low_BB_PAXG: >60% win rate, >30 trades
#
# CRITICAL FIX: Uses dedicated backtest configs without parameter overrides

set -e  # Exit on error

BACKTEST_DIR="/root/btc-bot/backtest_results"
DATE_RANGE="20251015-20251104"
LOG_FILE="$BACKTEST_DIR/backtest_${DATE_RANGE}_v2.log"

echo "===== BACKTEST NEW STRATEGIES V2 =====" | tee -a "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "Test Period: Oct 15 - Nov 4, 2025 (20 days)" | tee -a "$LOG_FILE"
echo "Fix: Using configs without parameter overrides" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Create backtest directory
mkdir -p "$BACKTEST_DIR"
cd /root/btc-bot

# Activate virtual environment
source .venv/bin/activate

# BACKTEST 1: CofiBitStrategy_LowVol (Bot2 - BTC/USDT)
echo "========================================" | tee -a "$LOG_FILE"
echo "BACKTEST 1: CofiBitStrategy_LowVol (BTC/USDT)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Expected: ROI 1.5%, stoploss -2.5%, trailing TRUE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running backtest..." | tee -a "$LOG_FILE"
.venv/bin/freqtrade backtesting \
    --config backtest_cofibit_config.json \
    --strategy CofiBitStrategy_LowVol \
    --timerange 20251015-20251104 \
    --export trades \
    --export-filename "$BACKTEST_DIR/cofibit_backtest_v2.json" \
    2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "CofiBitStrategy backtest complete!" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# BACKTEST 2: Low_BB_PAXG (Bot4 - PAXG/USDT)
echo "========================================" | tee -a "$LOG_FILE"
echo "BACKTEST 2: Low_BB_PAXG (PAXG/USDT)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Expected: ROI 0.8%, stoploss -1.5%, trailing TRUE, timeframe 1m" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running backtest..." | tee -a "$LOG_FILE"
.venv/bin/freqtrade backtesting \
    --config backtest_lowbb_config.json \
    --strategy Low_BB_PAXG \
    --timerange 20251015-20251104 \
    --export trades \
    --export-filename "$BACKTEST_DIR/lowbb_backtest_v2.json" \
    2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Low_BB_PAXG backtest complete!" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# SUMMARY
echo "========================================" | tee -a "$LOG_FILE"
echo "BACKTEST SUMMARY" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Results saved to:" | tee -a "$LOG_FILE"
echo "  - CofiBitStrategy: $BACKTEST_DIR/cofibit_backtest_v2.json" | tee -a "$LOG_FILE"
echo "  - Low_BB_PAXG: $BACKTEST_DIR/lowbb_backtest_v2.json" | tee -a "$LOG_FILE"
echo "  - Full log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "SUCCESS CRITERIA CHECK:" | tee -a "$LOG_FILE"
echo "  CofiBitStrategy: Need >55% win rate AND >50 trades" | tee -a "$LOG_FILE"
echo "  Low_BB_PAXG: Need >60% win rate AND >30 trades" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Review the RESULT FOR STRATEGY sections above:" | tee -a "$LOG_FILE"
echo "  - Total trades" | tee -a "$LOG_FILE"
echo "  - Win rate %" | tee -a "$LOG_FILE"
echo "  - Total profit %" | tee -a "$LOG_FILE"
echo "  - Avg profit %" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "If BOTH strategies meet criteria: PASS - Deploy to Bot2 & Bot4" | tee -a "$LOG_FILE"
echo "If EITHER strategy fails: FAIL - Re-optimize or try different strategies" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Backtest complete: $(date)" | tee -a "$LOG_FILE"
