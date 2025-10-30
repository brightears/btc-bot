# 24-48 Hour Monitoring Plan - Bot3 & Bot5 Parameter Optimizations
**Creation Date**: October 30, 2025  
**Deployment Times**: Bot3 (08:27 UTC), Bot5 (09:09 UTC)  
**Monitoring Period**: Oct 30 08:27 UTC - Nov 1 09:09 UTC (48 hours)  
**Analyst**: Quantitative Trading Performance Analyst

---

## 📊 EXECUTIVE SUMMARY

Comprehensive monitoring framework for Bot3 (SimpleRSI) and Bot5 (Strategy004-opt) post-optimization. This plan defines quantitative success criteria, automated monitoring queries, intervention thresholds, and decision trees for Phase 2.3 progression.

**Critical Success Metrics:**
- Bot3: Win rate target 55% (from 40.91%), stop-loss rate ≤23% (from 55%)
- Bot5: Win rate improvement >10%, ROI exit efficiency >50%
- System-wide: Fee-to-profit ratio <15%, no degradation in other bots

---

## 🎯 SUCCESS CRITERIA

### 24-Hour Checkpoint (Oct 31, 08:27 UTC)

#### Bot3 (SimpleRSI) - MINIMUM THRESHOLDS
```
PASS Criteria:
- Win rate ≥ 48% (halfway to 55% target)
- Stop-loss rate ≤ 40% (improving from 55%)
- Minimum 3 trades closed (statistical relevance)
- Average profit per win > fees paid
- No system crashes or errors

WARNING Criteria:
- Win rate 42-47% (marginal improvement)
- Stop-loss rate 41-50% (slow improvement)
- Only 1-2 trades closed
- Fee ratio 15-25% of gross profit

FAIL Criteria:
- Win rate < 42% (no improvement)
- Stop-loss rate > 50% (deterioration)
- Zero trades or only losses
- Fee ratio > 25% of gross profit
```

#### Bot5 (Strategy004-opt) - MINIMUM THRESHOLDS
```
PASS Criteria:
- Win rate improvement ≥ 5% vs baseline
- ROI exits ≥ 40% of total exits
- Average hold time 2-8 hours (not premature)
- Profit factor > 1.2
- Sharpe ratio > 0.5

WARNING Criteria:
- Win rate improvement 0-4%
- ROI exits 20-39% of total
- Hold times < 1 hour or > 24 hours
- Profit factor 1.0-1.2

FAIL Criteria:
- Win rate deterioration
- ROI exits < 20% (ineffective)
- All exits via stop-loss
- Profit factor < 1.0
```

### 48-Hour Checkpoint (Nov 1, 09:09 UTC)

#### Bot3 - FULL VALIDATION
```
PHASE 2.3 PROGRESSION Criteria:
- Win rate ≥ 53% (≥95% of target)
- Stop-loss rate ≤ 25% (≤109% of target)
- Minimum 6 trades (statistical confidence)
- Sharpe ratio > 1.0
- Maximum drawdown < 5%
- Profit factor > 1.5
- 95% confidence interval includes target metrics

EXTEND MONITORING Criteria:
- Win rate 48-52% (promising but uncertain)
- Stop-loss rate 26-35% (good progress)
- 3-5 trades (need more data)
- Mixed signals in other metrics

ROLLBACK Criteria:
- Win rate < 48% (failed to improve)
- Stop-loss rate > 35% (insufficient improvement)
- Negative total P&L
- Sharpe ratio < 0
- System instability detected
```

#### Bot5 - FULL VALIDATION
```
PHASE 2.3 PROGRESSION Criteria:
- Win rate improvement ≥ 10%
- ROI exits ≥ 50% of total exits
- Optimal hold time 3-6 hours average
- Sortino ratio > 1.0
- Fee efficiency < 10% of gross profit
- No correlation increase with Bot4 (maintain <0.7)

EXTEND MONITORING Criteria:
- Win rate improvement 5-9%
- ROI exits 35-49%
- Metrics trending positive
- Need larger sample size

ROLLBACK Criteria:
- Win rate deterioration > 5%
- Excessive churning (>20 trades/day)
- Fee ratio > 20% of gross profit
- Correlation with Bot4 > 0.8
```

---

## 📈 METRICS TO TRACK

### Core Performance Metrics
1. **Win Rate**: `(profitable_trades / total_closed_trades) * 100`
2. **Stop-Loss Rate**: `(stoploss_exits / total_closed_trades) * 100`
3. **ROI Exit Rate**: `(roi_exits / total_closed_trades) * 100`
4. **Profit Factor**: `gross_profits / gross_losses`
5. **Sharpe Ratio**: `mean_return / std_dev_return * sqrt(365)`
6. **Sortino Ratio**: `mean_return / downside_std_dev * sqrt(365)`
7. **Maximum Drawdown**: `(peak_value - trough_value) / peak_value`

### Fee Efficiency Metrics
1. **Total Fees**: `sum(fee_open + fee_close)`
2. **Fee-to-Volume Ratio**: `total_fees / total_volume`
3. **Fee-to-Profit Ratio**: `total_fees / gross_profit`
4. **Break-Even Win Rate**: `1 / (1 + (avg_win - fees) / (avg_loss + fees))`
5. **Net Profit After Fees**: `gross_profit - total_fees`

### Risk Management Metrics
1. **Average Risk per Trade**: `avg(amount * abs(stop_loss_pct))`
2. **Risk-Reward Ratio**: `avg_win / avg_loss`
3. **Position Size Consistency**: `std_dev(stake_amount) / mean(stake_amount)`
4. **Leverage Usage**: `max(stake_amount) / min(stake_amount)`
5. **Time in Market**: `sum(trade_duration) / monitoring_period`

### System Health Metrics
1. **Trade Frequency**: `trades_per_day`
2. **Signal Generation Rate**: `entries_analyzed / candles_processed`
3. **Execution Slippage**: `(actual_price - signal_price) / signal_price`
4. **Open Position Duration**: `time_since_open`
5. **Bot Uptime**: `(runtime - downtime) / runtime`

---

## 💾 SQL QUERIES FOR MONITORING

### Connect to VPS and Access Databases
```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Navigate to bot directories
cd /root/btc-bot

# Access Bot3 database
sqlite3 bot3_*/tradesv3.dryrun.sqlite

# Access Bot5 database  
sqlite3 bot5_*/tradesv3.dryrun.sqlite
```

### Query 1: Overall Performance Summary (Run on each bot)
```sql
-- Performance metrics for last 24/48 hours
WITH time_filter AS (
    SELECT datetime('now', '-24 hours') as start_time  -- Change to -48 for 48h
),
trade_stats AS (
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as winning_trades,
        SUM(CASE WHEN close_profit <= 0 THEN 1 ELSE 0 END) as losing_trades,
        ROUND(AVG(close_profit), 4) as avg_profit_pct,
        ROUND(AVG(CASE WHEN close_profit > 0 THEN close_profit END), 4) as avg_win,
        ROUND(AVG(CASE WHEN close_profit <= 0 THEN close_profit END), 4) as avg_loss,
        ROUND(SUM(close_profit), 4) as total_profit_pct,
        ROUND(SUM(fee_open + fee_close), 4) as total_fees,
        ROUND(SUM(close_profit * stake_amount / 100), 2) as total_profit_usd
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time
    AND is_open = 0
)
SELECT 
    *,
    ROUND(CAST(winning_trades AS REAL) / total_trades * 100, 2) as win_rate,
    ROUND(avg_win / ABS(avg_loss), 2) as risk_reward_ratio,
    ROUND(total_fees / NULLIF(total_profit_usd, 0) * 100, 2) as fee_to_profit_pct
FROM trade_stats;
```

### Query 2: Exit Reason Analysis (Critical for validation)
```sql
-- Analyze exit reasons distribution
WITH time_filter AS (
    SELECT datetime('now', '-24 hours') as start_time  -- Change to -48 for 48h
)
SELECT 
    exit_reason,
    COUNT(*) as count,
    ROUND(AVG(close_profit), 4) as avg_profit,
    ROUND(SUM(close_profit), 4) as total_profit,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trades, time_filter 
                               WHERE close_date >= time_filter.start_time 
                               AND is_open = 0), 2) as percentage
FROM trades, time_filter
WHERE close_date >= time_filter.start_time
AND is_open = 0
GROUP BY exit_reason
ORDER BY count DESC;
```

### Query 3: Stop-Loss Performance (Bot3 Focus)
```sql
-- Detailed stop-loss analysis
WITH time_filter AS (
    SELECT datetime('now', '-24 hours') as start_time
)
SELECT 
    COUNT(*) as stoploss_exits,
    ROUND(AVG(close_profit), 4) as avg_stoploss_loss,
    ROUND(MIN(close_profit), 4) as worst_stoploss,
    ROUND(MAX(close_profit), 4) as best_stoploss,
    ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 AS REAL)), 2) as avg_hours_to_stop
FROM trades, time_filter
WHERE close_date >= time_filter.start_time
AND exit_reason = 'stop_loss'
AND is_open = 0;
```

### Query 4: ROI Exit Efficiency (Bot5 Focus)
```sql
-- ROI exit analysis for Bot5
WITH time_filter AS (
    SELECT datetime('now', '-24 hours') as start_time
)
SELECT 
    COUNT(*) as roi_exits,
    ROUND(AVG(close_profit), 4) as avg_roi_profit,
    ROUND(MIN(close_profit), 4) as min_roi_profit,
    ROUND(MAX(close_profit), 4) as max_roi_profit,
    ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 AS REAL)), 2) as avg_hold_hours,
    ROUND(SUM(fee_open + fee_close), 4) as total_roi_fees
FROM trades, time_filter
WHERE close_date >= time_filter.start_time
AND exit_reason = 'roi'
AND is_open = 0;
```

### Query 5: Hourly Trade Distribution
```sql
-- Trade frequency pattern analysis
WITH time_filter AS (
    SELECT datetime('now', '-48 hours') as start_time
)
SELECT 
    strftime('%Y-%m-%d %H:00', close_date) as hour,
    COUNT(*) as trades_closed,
    ROUND(AVG(close_profit), 4) as avg_profit,
    SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN close_profit <= 0 THEN 1 ELSE 0 END) as losses
FROM trades, time_filter
WHERE close_date >= time_filter.start_time
AND is_open = 0
GROUP BY hour
ORDER BY hour DESC
LIMIT 48;
```

### Query 6: Fee Impact Analysis
```sql
-- Comprehensive fee analysis
WITH time_filter AS (
    SELECT datetime('now', '-24 hours') as start_time
),
fee_stats AS (
    SELECT 
        SUM(fee_open) as total_open_fees,
        SUM(fee_close) as total_close_fees,
        SUM(fee_open + fee_close) as total_fees,
        SUM(stake_amount) as total_volume,
        COUNT(*) as trade_count,
        SUM(CASE WHEN close_profit > 0 THEN close_profit * stake_amount / 100 ELSE 0 END) as gross_profits,
        SUM(CASE WHEN close_profit <= 0 THEN ABS(close_profit * stake_amount / 100) ELSE 0 END) as gross_losses
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time
    AND is_open = 0
)
SELECT 
    ROUND(total_fees, 4) as total_fees_usd,
    ROUND(total_fees / total_volume * 100, 4) as fee_to_volume_pct,
    ROUND(total_fees / NULLIF(gross_profits, 0) * 100, 2) as fee_to_profit_pct,
    ROUND(total_fees / trade_count, 4) as avg_fee_per_trade,
    ROUND(gross_profits / NULLIF(gross_losses, 0), 2) as profit_factor,
    ROUND(gross_profits - gross_losses - total_fees, 2) as net_profit_after_fees
FROM fee_stats;
```

### Query 7: Current Open Positions
```sql
-- Monitor open positions
SELECT 
    trade_id,
    pair,
    stake_amount,
    amount,
    open_rate,
    stop_loss,
    ROUND((stop_loss - open_rate) / open_rate * 100, 2) as stop_loss_pct,
    datetime(open_date) as opened_at,
    ROUND(CAST((julianday('now') - julianday(open_date)) * 24 AS REAL), 2) as hours_open,
    fee_open
FROM trades
WHERE is_open = 1
ORDER BY open_date DESC;
```

### Query 8: Drawdown Analysis
```sql
-- Calculate running P&L and drawdown
WITH time_filter AS (
    SELECT datetime('now', '-48 hours') as start_time
),
running_pnl AS (
    SELECT 
        close_date,
        close_profit * stake_amount / 100 - (fee_open + fee_close) as net_profit,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) 
            OVER (ORDER BY close_date) as cumulative_pnl
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time
    AND is_open = 0
),
drawdown AS (
    SELECT 
        close_date,
        cumulative_pnl,
        MAX(cumulative_pnl) OVER (ORDER BY close_date ROWS UNBOUNDED PRECEDING) as running_max,
        cumulative_pnl - MAX(cumulative_pnl) OVER (ORDER BY close_date ROWS UNBOUNDED PRECEDING) as drawdown_value
    FROM running_pnl
)
SELECT 
    MIN(drawdown_value) as max_drawdown_usd,
    ROUND(MIN(drawdown_value) / NULLIF(MAX(running_max), 0) * 100, 2) as max_drawdown_pct,
    COUNT(CASE WHEN drawdown_value < 0 THEN 1 END) as periods_in_drawdown,
    ROUND(AVG(CASE WHEN drawdown_value < 0 THEN drawdown_value END), 2) as avg_drawdown
FROM drawdown;
```

---

## ⚠️ WARNING THRESHOLDS & INTERVENTION TRIGGERS

### IMMEDIATE INTERVENTION REQUIRED (Any Single Trigger)
```yaml
Critical_Alerts:
  - Max drawdown > 10% in 24 hours
  - Win rate < 30% with >5 trades
  - Fee ratio > 40% of gross profit
  - Stop-loss rate > 70% (systematic failure)
  - Bot process crash or zombie state
  - Memory usage > 90% available
  - Correlation spike > 0.9 between Bot4/Bot5
  - Position size > 2x normal stake
  - Open position > 48 hours without exit
  - Trade frequency > 50/day (churning)
```

### WARNING LEVEL (Monitor Closely)
```yaml
Warning_Alerts:
  - Drawdown 5-10% in 24 hours
  - Win rate 30-40% declining trend
  - Fee ratio 25-40% of gross profit  
  - 3+ consecutive stop-losses
  - No trades in 12 hours (if market active)
  - Memory growth > 100MB/day
  - Increasing slippage > 0.1%
  - Hold times all < 30 minutes
  - Signal generation < 1% of candles
```

### MONITORING COMMANDS
```bash
# Real-time monitoring script
cat > /tmp/monitor_bots.sh << 'SCRIPT'
#!/bin/bash
while true; do
    clear
    echo "=== BOT3 & BOT5 OPTIMIZATION MONITORING ==="
    echo "Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    
    # Check bot processes
    echo "Process Status:"
    ps aux | grep -E "bot[35]" | grep -v grep
    echo ""
    
    # Memory usage
    echo "Memory Usage:"
    free -h | grep -E "^Mem|^Swap"
    echo ""
    
    # Recent trades (last 5)
    echo "Recent Bot3 Trades:"
    sqlite3 /root/btc-bot/bot3_*/tradesv3.dryrun.sqlite \
        "SELECT datetime(close_date), exit_reason, round(close_profit,2) 
         FROM trades WHERE is_open=0 
         ORDER BY close_date DESC LIMIT 5;" 2>/dev/null
    echo ""
    
    echo "Recent Bot5 Trades:"
    sqlite3 /root/btc-bot/bot5_*/tradesv3.dryrun.sqlite \
        "SELECT datetime(close_date), exit_reason, round(close_profit,2) 
         FROM trades WHERE is_open=0 
         ORDER BY close_date DESC LIMIT 5;" 2>/dev/null
    
    sleep 300  # Update every 5 minutes
done
SCRIPT

chmod +x /tmp/monitor_bots.sh
# Run in background: nohup /tmp/monitor_bots.sh > /tmp/monitor.log 2>&1 &
```

---

## 🌲 DECISION TREE

### 24-Hour Decision Point (Oct 31, 08:27 UTC)

```
START
  │
  ├─ Both Bots Meeting PASS Criteria?
  │    │
  │    ├─ YES → Continue to 48h monitoring
  │    │         Document metrics, no changes
  │    │
  │    └─ NO → Individual Bot Analysis
  │              │
  │              ├─ Bot3 Status?
  │              │    ├─ PASS → Keep Bot3 parameters
  │              │    ├─ WARNING → Extend monitoring, prepare rollback
  │              │    └─ FAIL → Rollback Bot3 immediately
  │              │
  │              └─ Bot5 Status?
  │                   ├─ PASS → Keep Bot5 parameters
  │                   ├─ WARNING → Analyze fee impact
  │                   │            └─ Fees > 25%? → Adjust ROI targets
  │                   └─ FAIL → Rollback Bot5 immediately
  │
  └─ Any Critical Alerts?
       │
       ├─ YES → EMERGENCY ROLLBACK BOTH BOTS
       │        Investigate root cause
       │        Document failure mode
       │
       └─ NO → Continue per individual status
```

### 48-Hour Decision Point (Nov 1, 09:09 UTC)

```
START
  │
  ├─ Calculate Confidence Intervals (95% CI)
  │    │
  │    └─ Do CIs Include Target Metrics?
  │         │
  │         ├─ BOTH YES → PROCEED TO PHASE 2.3
  │         │              Deploy remaining bot optimizations
  │         │              Maintain 24h monitoring cycle
  │         │
  │         ├─ MIXED → Selective Progression
  │         │           │
  │         │           ├─ Bot3 CI includes targets?
  │         │           │    ├─ YES → Lock Bot3, continue
  │         │           │    └─ NO → Extend Bot3 monitoring 24h
  │         │           │
  │         │           └─ Bot5 CI includes targets?
  │         │                ├─ YES → Lock Bot5, continue
  │         │                └─ NO → Adjust ROI targets slightly
  │         │
  │         └─ BOTH NO → Performance Review
  │                        │
  │                        ├─ Positive trend? → EXTEND 48h
  │                        ├─ Flat? → PARAMETER TUNING
  │                        │         ├─ Bot3: RSI 35/65 → 33/67
  │                        │         └─ Bot5: ROI +0.2% all levels
  │                        └─ Negative? → FULL ROLLBACK
  │
  └─ Risk Assessment
       │
       ├─ Max Drawdown < 5%?
       ├─ Sharpe Ratio > 0.8?  
       ├─ Fee Efficiency < 15%?
       └─ All YES? → Safe to proceed
           Any NO? → Address specific issue before Phase 2.3
```

---

## 📋 ROLLBACK PROCEDURES

### Bot3 Rollback Commands
```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Stop Bot3
supervisorctl stop bot3

# Restore original config
cd /root/btc-bot/bot3_*
cp config.json.backup config.json  # Ensure backup exists

# Edit config to restore parameters
nano config.json
# Set: "stoploss": -0.01
# Set: "rsi_lower": 30, "rsi_upper": 70
# Remove staged ROI, restore original

# Restart Bot3
supervisorctl start bot3

# Verify running with old parameters
tail -n 50 bot3.log | grep -E "stoploss|RSI"
```

### Bot5 Rollback Commands
```bash
# Stop Bot5
supervisorctl stop bot5

# Restore original config  
cd /root/btc-bot/bot5_*
cp config.json.backup config.json

# Edit config to restore parameters
nano config.json
# Set: "stoploss": -0.04
# Set ROI: {"0": 0.07, "10": 0.05, "20": 0.03, "40": 0.02}

# Restart Bot5
supervisorctl start bot5

# Verify
tail -n 50 bot5.log | grep -E "stoploss|ROI"
```

---

## 📊 REPORTING TEMPLATES

### 24-Hour Report Template
```markdown
## 24-Hour Optimization Report - [DATE]

### Bot3 (SimpleRSI) Performance
- **Trades Closed**: X
- **Win Rate**: X% (Target: 55%, Previous: 40.91%)
- **Stop-Loss Rate**: X% (Target: 23%, Previous: 55%)
- **Profit Factor**: X.XX
- **Sharpe Ratio**: X.XX
- **Total P&L**: $X.XX
- **Fees Paid**: $X.XX (X% of gross)
- **Status**: [PASS/WARNING/FAIL]

### Bot5 (Strategy004-opt) Performance  
- **Trades Closed**: X
- **Win Rate**: X% (Improvement: +X%)
- **ROI Exits**: X% of total
- **Average Hold Time**: X.X hours
- **Sortino Ratio**: X.XX
- **Total P&L**: $X.XX
- **Fee Efficiency**: X%
- **Status**: [PASS/WARNING/FAIL]

### System Health
- **Uptime**: 100%
- **Memory Usage**: X.XGB/3.7GB
- **Other Bots**: [Stable/Degraded]
- **Correlation Bot4/5**: X.XX

### Decision
[Continue Monitoring / Rollback Bot3 / Rollback Bot5 / Emergency Stop]

### Next Checkpoint
[DATE TIME UTC]
```

### 48-Hour Final Report Template
```markdown
## 48-Hour Optimization Validation - [DATE]

### Statistical Validation

#### Bot3 Confidence Intervals (95%)
- Win Rate CI: [X%, Y%] (Target: 55%)
- Stop-Loss Rate CI: [X%, Y%] (Target: 23%)
- Statistical Significance: [YES/NO]

#### Bot5 Confidence Intervals (95%)
- Win Rate Improvement CI: [X%, Y%] (Target: >10%)
- ROI Exit Rate CI: [X%, Y%] (Target: >50%)
- Statistical Significance: [YES/NO]

### Risk Metrics
- Maximum Drawdown: X%
- Sharpe Ratio: X.XX
- Sortino Ratio: X.XX
- Value at Risk (95%): $X.XX
- Fee Impact: X% of gross profits

### Final Decision
[PROCEED TO PHASE 2.3 / EXTEND MONITORING / ROLLBACK]

### Phase 2.3 Deployment Plan
1. [Next bot to optimize]
2. [Timeline]
3. [Success criteria]
```

---

## 🚀 PHASE 2.3 PROGRESSION CRITERIA

If both Bot3 and Bot5 meet 48-hour success criteria:

### Next Optimization Candidates (Priority Order)
1. **Bot2 (Strategy004 BTC)**
   - Similar to Bot5, apply proven ROI adjustments
   - Risk: Higher volume, more impact if fails
   
2. **Bot4 (Strategy004 PAXG)**
   - Twin of Bot5, should mirror improvements
   - Risk: Lower, good correlation baseline

3. **Bot1 & Bot6 (Strategy001)**
   - Most complex, save for last
   - Require separate optimization study

### Deployment Schedule
```
Day 0-2: Bot3 & Bot5 (Current)
Day 2-4: Validate and lock
Day 4-6: Deploy Bot2
Day 6-8: Deploy Bot4  
Day 8-10: Full system validation
Day 10+: Consider Bot1/Bot6 or maintain
```

---

## 📞 EMERGENCY CONTACTS & ESCALATION

### Escalation Triggers
1. Total system P&L < -$50 in 24h
2. Any bot with >10 consecutive losses
3. System crash affecting >2 bots
4. Correlation >0.95 (systemic risk)
5. Unexpected behavior not in parameters

### Response Protocol
```bash
# 1. Immediate system snapshot
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219 \
  "cd /root/btc-bot && ./emergency_snapshot.sh"

# 2. Pause affected bots
supervisorctl stop bot3 bot5

# 3. Export recent trades for analysis
sqlite3 bot3_*/tradesv3.dryrun.sqlite ".dump trades" > bot3_emergency.sql
sqlite3 bot5_*/tradesv3.dryrun.sqlite ".dump trades" > bot5_emergency.sql

# 4. Rollback configurations
# [Use rollback procedures above]

# 5. Document incident
echo "Incident at $(date): [DESCRIPTION]" >> incidents.log
```

---

## ✅ CHECKLIST FOR MONITORING EXECUTION

### Every 6 Hours
- [ ] Run Query 1 (Overall Performance) for Bot3 & Bot5
- [ ] Run Query 2 (Exit Reason Analysis)  
- [ ] Check for warning thresholds
- [ ] Note any anomalies in trade patterns
- [ ] Verify bot processes still running

### At 24-Hour Checkpoint
- [ ] Run all 8 SQL queries
- [ ] Calculate confidence intervals
- [ ] Compare against success criteria
- [ ] Generate 24-hour report
- [ ] Make continue/rollback decision
- [ ] Document decision rationale

### At 48-Hour Checkpoint
- [ ] Complete statistical validation
- [ ] Calculate all risk metrics
- [ ] Review correlation matrix
- [ ] Assess fee efficiency
- [ ] Generate final report
- [ ] Execute Phase 2.3 decision
- [ ] Plan next optimization cycle

---

## 📝 APPENDIX: STATISTICAL FORMULAS

### Confidence Interval for Win Rate
```
CI = p ± z * sqrt(p(1-p)/n)
where p = observed win rate, n = number of trades, z = 1.96 for 95% CI
```

### Sharpe Ratio Calculation
```
Sharpe = (Mean_Return - Risk_Free_Rate) / StdDev_Returns * sqrt(365)
Assume Risk_Free_Rate = 0 for crypto
```

### Sortino Ratio Calculation
```
Sortino = (Mean_Return - Target_Return) / Downside_Deviation * sqrt(365)
Target_Return = 0, Downside_Deviation = StdDev of negative returns only
```

### Profit Factor
```
Profit_Factor = Sum(Winning_Trades) / |Sum(Losing_Trades)|
Target > 1.5 for robust strategy
```

---

**Document Version**: 1.0  
**Next Review**: October 31, 2025, 08:27 UTC (24-hour checkpoint)  
**Final Review**: November 1, 2025, 09:09 UTC (48-hour checkpoint)

