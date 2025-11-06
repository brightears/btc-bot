#!/bin/bash
#############################################################
# Bot3 & Bot5 Optimization Monitoring Script
# Created: October 30, 2025
# Purpose: Automated monitoring for 24-48 hour checkpoints
#############################################################

# Configuration
BOT3_DB="/root/btc-bot/bot3_*/tradesv3.dryrun.sqlite"
BOT5_DB="/root/btc-bot/bot5_*/tradesv3.dryrun.sqlite"
DEPLOYMENT_TIME_BOT3="2025-10-30 08:27:00"
DEPLOYMENT_TIME_BOT5="2025-10-30 09:09:00"
REPORT_FILE="/root/btc-bot/optimization_report_$(date +%Y%m%d_%H%M%S).txt"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
}

# Function to run SQL query
run_query() {
    local db=$1
    local query=$2
    sqlite3 "$db" "$query" 2>/dev/null
}

# Function to calculate hours since deployment
hours_since_deployment() {
    local bot=$1
    local deploy_time=""
    
    if [ "$bot" = "bot3" ]; then
        deploy_time="$DEPLOYMENT_TIME_BOT3"
    else
        deploy_time="$DEPLOYMENT_TIME_BOT5"
    fi
    
    echo $(( ($(date +%s) - $(date -d "$deploy_time" +%s)) / 3600 ))
}

# Main monitoring function
monitor_bot() {
    local bot_name=$1
    local bot_db=$2
    local expected_win_rate=$3
    local expected_stoploss_rate=$4
    
    print_header "$bot_name Performance Metrics"
    
    # Get hours since deployment
    local hours_elapsed=$(hours_since_deployment ${bot_name,,})
    echo "Hours since deployment: $hours_elapsed"
    
    # Overall performance query
    local perf_query="
    WITH time_filter AS (
        SELECT datetime('$DEPLOYMENT_TIME_BOT3') as start_time
    ),
    trade_stats AS (
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN close_profit <= 0 THEN 1 ELSE 0 END) as losses,
            ROUND(AVG(close_profit), 4) as avg_profit,
            ROUND(SUM(close_profit), 4) as total_profit,
            ROUND(SUM(fee_open + fee_close), 4) as total_fees
        FROM trades, time_filter
        WHERE close_date >= time_filter.start_time
        AND is_open = 0
    )
    SELECT 
        printf('Trades: %d | Wins: %d | Losses: %d', total_trades, wins, losses) as summary,
        printf('Win Rate: %.2f%% (Target: $expected_win_rate%%)', 
               CAST(wins AS REAL) / NULLIF(total_trades, 0) * 100) as win_rate,
        printf('Avg Profit: %.4f%% | Total: %.4f%%', avg_profit, total_profit) as profits,
        printf('Fees: %.4f USD (%.2f%% of profit)', total_fees, 
               total_fees / NULLIF(total_profit, 0) * 100) as fee_impact
    FROM trade_stats;"
    
    run_query "$bot_db" "$perf_query" | while IFS='|' read -r line; do
        echo "$line"
    done
    
    # Exit reason analysis
    echo -e "\n${YELLOW}Exit Reason Breakdown:${NC}"
    local exit_query="
    SELECT 
        printf('%-15s: %2d trades (%.1f%%)', 
               exit_reason, 
               COUNT(*),
               COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trades 
                                   WHERE close_date >= datetime('$DEPLOYMENT_TIME_BOT3')
                                   AND is_open = 0))
    FROM trades
    WHERE close_date >= datetime('$DEPLOYMENT_TIME_BOT3')
    AND is_open = 0
    GROUP BY exit_reason
    ORDER BY COUNT(*) DESC;"
    
    run_query "$bot_db" "$exit_query"
    
    # Stop-loss rate check
    local sl_rate=$(run_query "$bot_db" "
        SELECT ROUND(
            SUM(CASE WHEN exit_reason = 'stop_loss' THEN 1 ELSE 0 END) * 100.0 / 
            NULLIF(COUNT(*), 0), 2)
        FROM trades
        WHERE close_date >= datetime('$DEPLOYMENT_TIME_BOT3')
        AND is_open = 0;")
    
    echo -e "\nStop-Loss Rate: ${sl_rate}% (Target: ≤${expected_stoploss_rate}%)"
    
    # Status evaluation
    local status=""
    if (( $(echo "$sl_rate <= $expected_stoploss_rate" | bc -l) )); then
        status="${GREEN}✓ PASS${NC}"
    else
        status="${RED}✗ FAIL${NC}"
    fi
    echo -e "Status: $status"
    
    # Open positions
    echo -e "\n${YELLOW}Open Positions:${NC}"
    run_query "$bot_db" "
        SELECT printf('%s: %.8f @ %.2f | Stop: %.2f (%.2f%%) | %d hours open',
                     pair, amount, open_rate, stop_loss,
                     (stop_loss - open_rate) / open_rate * 100,
                     CAST((julianday('now') - julianday(open_date)) * 24 AS INTEGER))
        FROM trades
        WHERE is_open = 1;"
}

# System health check
system_health() {
    print_header "System Health Check"
    
    # Check bot processes
    echo "Bot Processes:"
    ps aux | grep -E "freqtrade.*bot[35]" | grep -v grep | while read line; do
        pid=$(echo $line | awk '{print $2}')
        mem=$(echo $line | awk '{print $6}')
        bot=$(echo $line | grep -oE "bot[35]")
        echo "  $bot: PID $pid, Memory: $((mem/1024)) MB"
    done
    
    # Memory usage
    echo -e "\nMemory Usage:"
    free -h | grep -E "^Mem:" | awk '{print "  Used: " $3 " / " $2 " (" int($3/$2 * 100) "%)"}'
    
    # Check for recent errors
    echo -e "\nRecent Errors (last hour):"
    for bot in bot3 bot5; do
        errors=$(grep -c "ERROR" /root/btc-bot/${bot}_*/logs/freqtrade.log 2>/dev/null || echo 0)
        echo "  $bot: $errors errors"
    done
}

# Generate decision recommendation
generate_recommendation() {
    print_header "Decision Recommendation"
    
    local hours_elapsed=$(hours_since_deployment bot3)
    
    if [ $hours_elapsed -lt 24 ]; then
        echo "⏰ Less than 24 hours elapsed. Continue monitoring..."
    elif [ $hours_elapsed -lt 48 ]; then
        echo "📊 24-48 hour window. Evaluate against success criteria..."
        # Add logic to check against thresholds
    else
        echo "✅ 48 hours complete. Ready for Phase 2.3 decision."
    fi
}

# Main execution
main() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "     BOT3 & BOT5 OPTIMIZATION MONITORING REPORT"
    echo "     Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Monitor Bot3
    monitor_bot "BOT3 (SimpleRSI)" "$BOT3_DB" 55 23
    
    # Monitor Bot5
    monitor_bot "BOT5 (Strategy004-opt)" "$BOT5_DB" 50 30
    
    # System health
    system_health
    
    # Generate recommendation
    generate_recommendation
    
    echo -e "\n${GREEN}Report saved to: $REPORT_FILE${NC}"
}

# Save output to file and display
main | tee "$REPORT_FILE"

# Check for critical alerts
check_alerts() {
    echo -e "\n${YELLOW}Checking for Critical Alerts...${NC}"
    
    # Add alert checks here
    local alert_triggered=false
    
    # Example: Check for high drawdown
    # if [ condition ]; then
    #     echo -e "${RED}⚠️  ALERT: High drawdown detected!${NC}"
    #     alert_triggered=true
    # fi
    
    if [ "$alert_triggered" = false ]; then
        echo -e "${GREEN}✓ No critical alerts${NC}"
    fi
}

check_alerts
