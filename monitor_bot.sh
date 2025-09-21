#!/bin/bash
# Bot monitoring and auto-restart script
# Run this on VPS to ensure bot stays alive

BOT_NAME="ai_trading_lab.py"
BOT_DIR="/root/btc-bot"
LOG_FILE="$BOT_DIR/ai_lab.log"

# Function to check if bot is running
is_running() {
    pgrep -f "python3.*$BOT_NAME" > /dev/null
    return $?
}

# Function to start the bot
start_bot() {
    cd $BOT_DIR
    nohup python3 $BOT_NAME > $LOG_FILE 2>&1 &
    echo "[$(date)] Bot started with PID $!"
}

# Main monitoring loop
while true; do
    if ! is_running; then
        echo "[$(date)] Bot not running! Starting..."
        start_bot

        # Send notification (optional)
        # You can add a curl command here to send a webhook notification
    fi

    # Check every 5 minutes
    sleep 300
done