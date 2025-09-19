#!/bin/bash

# Health check script for monitoring bot status

LOG_FILE="logs/funding_exec.log"
STATE_FILE="logs/state.json"

# Check if process is running
if pgrep -f "run_funding_exec.py" > /dev/null; then
    echo "✅ Bot process is running"
else
    echo "❌ Bot process is NOT running"
    exit 1
fi

# Check if log file is being written
if [ -f "$LOG_FILE" ]; then
    LAST_LOG=$(stat -f %m "$LOG_FILE" 2>/dev/null || stat -c %Y "$LOG_FILE" 2>/dev/null)
    NOW=$(date +%s)
    DIFF=$((NOW - LAST_LOG))

    if [ $DIFF -gt 600 ]; then
        echo "⚠️  No log activity for $DIFF seconds"
    else
        echo "✅ Logs updated $DIFF seconds ago"
    fi
else
    echo "❌ Log file not found"
fi

# Check state file
if [ -f "$STATE_FILE" ]; then
    echo "✅ State file exists"
    POSITION=$(jq -r '.position' "$STATE_FILE" 2>/dev/null)
    if [ "$POSITION" != "null" ]; then
        echo "📊 Active position found"
    else
        echo "📊 No active position"
    fi
else
    echo "⚠️  State file not found"
fi

echo "---"
echo "Last 5 log entries:"
tail -n 5 "$LOG_FILE" 2>/dev/null || echo "Unable to read logs"