#!/bin/bash
# Enhanced AI Trading Lab startup script

BOT_DIR="/root/btc-bot"
LOG_FILE="$BOT_DIR/ai_lab_enhanced.log"
PID_FILE="$BOT_DIR/ai_lab.pid"

# Kill any existing instances
echo "[$(date)] Stopping any existing bot instances..."
pkill -f ai_trading_lab || true
sleep 2

# Start the enhanced version in virtual environment
cd $BOT_DIR
echo "[$(date)] Starting Enhanced AI Trading Lab..."
source .venv/bin/activate
nohup python ai_trading_lab_enhanced.py >> $LOG_FILE 2>&1 &
echo $! > $PID_FILE
echo "[$(date)] Enhanced AI Trading Lab started with PID $(cat $PID_FILE)"

# Show initial logs
sleep 5
echo "[$(date)] Initial startup logs:"
tail -20 $LOG_FILE