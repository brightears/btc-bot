#!/bin/bash

# Bot1 & Bot6 Performance Monitor
# Purpose: Track optimization impact in real-time

echo "================================================"
echo "Bot1 & Bot6 Performance Monitor"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================"
echo ""

# Function to query bot performance
check_bot_performance() {
    local bot_name=$1
    local db_path=$2
    local bot_label=$3

    echo "### $bot_label Performance ###"

    if [ ! -f "$db_path" ]; then
        echo "⚠ Database not found: $db_path"
        echo ""
        return
    fi

    # Get trade statistics for last 24 hours
    sqlite3 "$db_path" << 'SQL' 2>/dev/null || echo "No trades yet"
.headers on
.mode column
SELECT
    COUNT(*) as total_trades,
    COUNT(CASE WHEN close_date >= datetime('now', '-24 hours') THEN 1 END) as trades_24h,
    ROUND(AVG(CASE WHEN close_profit_abs > 0 THEN 1.0 ELSE 0.0 END) * 100, 1) as win_rate_pct,
    ROUND(SUM(close_profit_abs), 2) as total_pnl,
    ROUND(SUM(CASE WHEN close_date >= datetime('now', '-24 hours') THEN close_profit_abs ELSE 0 END), 2) as pnl_24h,
    ROUND(AVG(close_profit_abs), 3) as avg_profit,
    COUNT(CASE WHEN exit_reason = 'stop_loss' THEN 1 END) as stop_losses,
    COUNT(CASE WHEN exit_reason LIKE '%roi%' THEN 1 END) as roi_exits,
    COUNT(CASE WHEN exit_reason LIKE '%trailing%' THEN 1 END) as trailing_exits
FROM trades
WHERE is_open = 0
AND close_date IS NOT NULL;
SQL

    # Show recent trades
    echo ""
    echo "Last 3 trades:"
    sqlite3 "$db_path" << 'SQL' 2>/dev/null || echo "No recent trades"
.headers on
.mode column
SELECT
    strftime('%m-%d %H:%M', close_date) as closed,
    ROUND((julianday(close_date) - julianday(open_date)) * 24 * 60, 0) as duration_min,
    ROUND(close_profit_abs, 3) as profit,
    ROUND(close_profit * 100, 2) as profit_pct,
    exit_reason
FROM trades
WHERE is_open = 0
AND close_date IS NOT NULL
ORDER BY close_date DESC
LIMIT 3;
SQL

    # Check for open trades
    echo ""
    local open_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM trades WHERE is_open = 1;" 2>/dev/null || echo "0")
    if [ "$open_count" -gt 0 ]; then
        echo "Open positions: $open_count"
        sqlite3 "$db_path" << 'SQL' 2>/dev/null
.headers on
.mode column
SELECT
    strftime('%m-%d %H:%M', open_date) as opened,
    ROUND((julianday('now') - julianday(open_date)) * 24 * 60, 0) as duration_min,
    ROUND(profit_ratio * 100, 2) as current_profit_pct,
    stop_loss_ratio * 100 as stop_pct
FROM trades
WHERE is_open = 1;
SQL
    else
        echo "No open positions"
    fi

    echo ""
    echo "----------------------------------------"
    echo ""
}

# Check Bot1
check_bot_performance "bot1_strategy001" "/root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite" "Bot1 (BTC/USDT)"

# Check Bot6
check_bot_performance "bot6_paxg_strategy001" "/root/btc-bot/bot6_paxg_strategy001/tradesv3.dryrun.sqlite" "Bot6 (PAXG/USDT)"

# Check if bots are running
echo "### System Status ###"
echo ""

echo "Running processes:"
ps aux | grep -E "bot1_strategy001|bot6_paxg_strategy001" | grep -v grep | awk '{print $11" - PID:"$2" Memory:"$6"KB"}' || echo "No bots running!"

echo ""
echo "API endpoints:"
for port in 8080 8085; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port"; then
        echo "✓ Port $port is listening"
    else
        echo "✗ Port $port is NOT listening"
    fi
done

echo ""
echo "Recent log entries (errors/warnings):"
echo ""

echo "Bot1 logs:"
tail -50 /root/btc-bot/bot1_strategy001/freqtrade.log 2>/dev/null | grep -E "ERROR|WARNING|stoploss|roi" | tail -3 || echo "No recent issues"

echo ""
echo "Bot6 logs:"
tail -50 /root/btc-bot/bot6_paxg_strategy001/freqtrade.log 2>/dev/null | grep -E "ERROR|WARNING|stoploss|roi" | tail -3 || echo "No recent issues"

echo ""
echo "### Parameter Verification ###"
echo ""

# Check Bot1 current parameters
echo "Bot1 loaded parameters:"
grep -A 5 "Strategy using" /root/btc-bot/bot1_strategy001/freqtrade.log 2>/dev/null | tail -6 || echo "Parameters not found in log"

echo ""
echo "Bot6 loaded parameters:"
grep -A 5 "Strategy using" /root/btc-bot/bot6_paxg_strategy001/freqtrade.log 2>/dev/null | tail -6 || echo "Parameters not found in log"

echo ""
echo "================================================"
echo "Expected Targets (24h):"
echo "  Bot1: Win rate >60%, >2 trades/day, avg profit >0"
echo "  Bot6: Win rate >60%, >2 trades/day, ROI exits >50%"
echo ""
echo "Critical Thresholds:"
echo "  Stop-loss rate >40% = WARNING"
echo "  Win rate <30% = CRITICAL"
echo "  No trades in 24h = CHECK CONFIGURATION"
echo "================================================"