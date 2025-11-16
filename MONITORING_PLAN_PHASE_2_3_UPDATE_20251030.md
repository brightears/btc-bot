# Phase 2.3 Monitoring Update - Bot1 & Bot6 Integration
**Creation Date**: October 30, 2025, 10:28 UTC  
**Update Scope**: Extends MONITORING_PLAN_20251030.md (Bot3/Bot5) to include Bot1 & Bot6  
**Monitoring Period**: Oct 30, 10:21 UTC - Nov 1, 10:27 UTC (48 hours)  
**Analyst**: Quantitative Trading Performance Analyst

---

## EXECUTIVE SUMMARY

Phase 2.3 optimization of Bot1 (Strategy001-BTC) and Bot6 (Strategy001-PAXG) represents the final stage of Phase 2 deployment (4 of 6 bots optimized). This update extends the existing monitoring framework to track Bot1/Bot6 metrics alongside Bot3/Bot5, with consolidated checkpoint criteria and portfolio-level risk assessment.

**Deployment Status:**
- Bot1: 10:21:41 UTC (PID 544720) - stoploss -1.5%, staged ROI, trailing stop enabled
- Bot6: 10:27:19 UTC (PID 545736) - stoploss -1.0%, staged ROI, trailing stop enabled
- Expected combined improvement: +23.04 USDT over 7 days (38 total trades)

---

## CHECKPOINT CRITERIA CONSOLIDATED

### 24-Hour Checkpoint (Oct 31, 10:21 UTC)

**Bot1 (Strategy001-BTC) Minimum Thresholds:**
```
PASS Criteria:
- Win rate ≥55% (target 65% by 48h)
- Minimum 5 trades closed (validates trade frequency increase)
- Average profit per winning trade > 0.3%
- Trailing stop activation ≥2 trades (mechanism working)
- No stoploss cascades (max 2 consecutive)
- Fee ratio ≤20% of gross profit

WARNING Criteria:
- Win rate 45-54% (below target but improving)
- 2-4 trades closed (low sample, insufficient data)
- Stop-loss rate >50% (trailing stop may not be optimal)
- Fee ratio 20-30% of gross profit

FAIL Criteria:
- Win rate <45% (deterioration from baseline)
- Zero trades or 1 trade (no activity)
- P&L worse than baseline (-5.24 USDT)
- Trailing stop not activating (parameter load failure)
```

**Bot6 (Strategy001-PAXG) Minimum Thresholds:**
```
PASS Criteria:
- Win rate ≥60% (target 68% by 48h)
- Minimum 6 trades closed (validates 3-4x frequency improvement)
- Average hold time 3-20 minutes (not too quick, not locked up)
- ROI exits ≥50% of total exits
- Fee ratio ≤15% of gross profit (PAXG efficiency better)

WARNING Criteria:
- Win rate 50-59% (below target)
- 3-5 trades closed (need more data for PAXG)
- Hold times <2 min or >30 min (suboptimal entry/exit)
- ROI exits 30-49% (partial ROI mechanism working)

FAIL Criteria:
- Win rate <50% (no improvement)
- 0-2 trades (frequency improvement not visible)
- P&L worse than baseline (-3.20 USDT)
- Fee ratio >30% of gross profit (eroding alpha)
```

**Portfolio-Level Criteria (24h):**
```
PASS Criteria:
- Combined P&L Bot1+Bot6 > -2.00 USDT (positive trend)
- Total system P&L not degraded vs Oct 30 baseline
- Bot3 & Bot5 maintained (no regression)
- No correlation spike between Bot1/Bot6 (r < 0.8)

WARNING Criteria:
- Combined P&L -2.00 to -5.00 USDT (marginal improvement)
- Slight degradation in other bots (<1% impact)
- Correlation Bot1/Bot6 0.7-0.8 (elevated)

FAIL Criteria:
- Combined P&L worse than baseline
- Any other bot experiencing degradation >5%
- Total system downtime >5 minutes
- Correlation >0.9 (systemic risk)
```

### 48-Hour Checkpoint (Nov 1, 10:27 UTC) - GO/NO-GO Decision

**Bot1 Full Validation:**
```
PHASE 2 COMPLETION Criteria:
- Win rate ≥60% (≥92% of 65% target, achievable by 48h)
- P&L cumulative ≥ +5.00 USDT (approaching +7.88 target)
- Minimum 10 trades (statistical significance n=10)
- Trailing stop contributing to 20%+ of exits
- Fee efficiency ≤15% of gross profit
- Sharpe ratio >0.5 (risk-adjusted positive)
- 95% CI for win rate includes 55-70% range

EXTEND MONITORING Criteria:
- Win rate 50-59% (promising, need more data)
- P&L +2 to +5 USDT (positive trend)
- 5-9 trades (need 48h additional monitoring)
- Mixed signals in fee efficiency

ROLLBACK Criteria:
- Win rate <50% (failed to meet minimum)
- P&L negative or worse than baseline
- Stop-loss rate >70% (trailing stop malfunction)
- Sharpe ratio <-0.5 (risk-adjusted negative)
- Correlation with Bot3 >0.85 (systemic risk)
```

**Bot6 Full Validation:**
```
PHASE 2 COMPLETION Criteria:
- Win rate ≥65% (target achieved, 95%+ of 68% target)
- Trade frequency 3-4x baseline (16+ trades in 48h vs baseline 0.57/day = 3 expected)
- P&L cumulative ≥ +4.00 USDT (approaching +6.72 target)
- ROI exits ≥55% of total (primary exit mechanism working)
- Fee efficiency ≤12% of gross profit (ultra-efficient PAXG)
- Sortino ratio >0.8 (downside risk controlled)
- 95% CI for trade frequency includes 3-5x improvement

EXTEND MONITORING Criteria:
- Win rate 55-64% (good but short of target)
- Trade frequency 2-3x baseline (improving but could be better)
- 10-15 trades (adequate sample)
- P&L +2 to +4 USDT (positive trajectory)

ROLLBACK Criteria:
- Win rate <55% (below minimum acceptable)
- Trade frequency <2x baseline at 48h (mechanism failure)
- P&L negative
- Fee efficiency >25% of gross profit (self-defeating)
- Correlation with Bot5 >0.87 (PAXG strategy redundancy)
```

**Portfolio-Level Validation (48h):**
```
PHASE 2 COMPLETE (All 6 Bots Optimized):
- BOTH Bot1 and Bot6 pass criteria above
- Combined Bot1+Bot6 P&L ≥ +8.00 USDT (vs -8.44 baseline = +16.44 improvement)
- Portfolio P&L improvement ≥3% vs Oct 30 baseline
- No degradation in Bot2/Bot3/Bot4/Bot5 (each ≥baseline)
- System uptime 100%, all ports bound
- Correlation matrix: No pair >0.88 (managed risk)

CONDITIONAL PROGRESSION (With Extensions):
- One bot meets criteria, one extended
- Portfolio P&L flat or slightly positive
- No critical issues, but data insufficient
- Action: Extend monitoring 24-48 hours, reassess

ROLLBACK REQUIRED:
- Either bot fails criteria
- Portfolio P&L worse than baseline
- Systemic correlation issues (>2 bots >0.85)
- Risk guardian thresholds breached
```

---

## METRICS TO TRACK (Consolidated Framework)

### Bot1 & Bot6 Specific Metrics

**Trade-Level Metrics:**
1. **Trade Count**: `COUNT(close_date >= deployment_time AND is_open = 0)`
2. **Win Rate**: `(COUNT(close_profit > 0) / COUNT(*)) * 100`
3. **Trailing Stop Utilization**: `COUNT(exit_reason = 'trailing_stop_loss') / COUNT(*) * 100`
4. **ROI Exit Rate**: `COUNT(exit_reason LIKE '%roi%') / COUNT(*) * 100`
5. **Stop-Loss Rate**: `COUNT(exit_reason = 'stop_loss') / COUNT(*) * 100`
6. **Average Hold Time**: `AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 * 60 AS REAL))` (minutes)

**Profit Metrics:**
1. **Total Profit %**: `SUM(close_profit)`
2. **Total Profit USD**: `SUM(close_profit * stake_amount / 100)`
3. **Average Profit %**: `AVG(close_profit)`
4. **Profit Factor**: `SUM(close_profit > 0) / ABS(SUM(close_profit < 0))`
5. **Average Win Size**: `AVG(close_profit WHEN close_profit > 0)`
6. **Average Loss Size**: `AVG(close_profit WHEN close_profit < 0)`

**Risk Metrics:**
1. **Maximum Drawdown**: `MIN(cumulative_pnl - MAX(cumulative_pnl))`
2. **Sharpe Ratio**: `(MEAN(daily_returns) / STDEV(daily_returns)) * SQRT(365)`
3. **Sortino Ratio**: `(MEAN(daily_returns) / STDEV(negative_returns)) * SQRT(365)`
4. **Risk-Reward Ratio**: `AVG(winning_profit) / ABS(AVG(losing_loss))`

**Fee Metrics:**
1. **Total Fees USD**: `SUM(fee_open + fee_close)`
2. **Fee per Trade**: `SUM(fee_open + fee_close) / COUNT(*)`
3. **Fee-to-Gross Profit %**: `SUM(fee_open + fee_close) / SUM(ABS(close_profit * stake_amount / 100)) * 100`
4. **Break-Even Win Rate**: `1 / (1 + (AVG_WIN - fees) / (ABS(AVG_LOSS) + fees))`

### Portfolio-Level Metrics (Bot3, Bot5, Bot1, Bot6)

**Correlation Matrix**: Calculate Pearson correlation between daily P&L of each bot pair
- Target: All pairs <0.7, no pair >0.85
- Watch: Bot1↔Bot6 (same strategy), Bot5↔Bot6 (PAXG), Bot3↔Bot1 (BTC focus)

**Portfolio P&L**: `SUM(all_bots_daily_profit)`
**Portfolio Volatility**: `STDEV(portfolio_daily_returns)`
**Portfolio Sharpe Ratio**: `MEAN(portfolio_returns) / STDEV(portfolio_returns) * SQRT(365)`
**Diversification Benefit**: `Portfolio_Sharpe / AVG(Individual_Sharpes)` (target >1.2)

---

## SQL QUERIES - BOT1 & BOT6 SPECIFIC

### Query 1A: Bot1 Performance (24/48h snapshot)
```sql
WITH time_filter AS (
    SELECT datetime('2025-10-30 10:21:41') as start_time,
           datetime('now') as end_time
),
trade_stats AS (
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN exit_reason = 'stop_loss' THEN 1 ELSE 0 END) as stoploss_count,
        SUM(CASE WHEN exit_reason IN ('roi', 'exit_signal') THEN 1 ELSE 0 END) as roi_exits,
        SUM(CASE WHEN exit_reason = 'trailing_stop_loss' THEN 1 ELSE 0 END) as trailing_exits,
        ROUND(AVG(close_profit), 4) as avg_profit_pct,
        ROUND(AVG(CASE WHEN close_profit > 0 THEN close_profit END), 4) as avg_win,
        ROUND(AVG(CASE WHEN close_profit <= 0 THEN close_profit END), 4) as avg_loss,
        ROUND(SUM(close_profit * stake_amount / 100), 2) as total_profit_usd,
        ROUND(SUM(fee_open + fee_close), 4) as total_fees_usd,
        ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 * 60 AS REAL)), 1) as avg_hold_min
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time 
    AND close_date <= time_filter.end_time
    AND is_open = 0
)
SELECT 
    total_trades,
    wins,
    ROUND(CAST(wins AS REAL) / total_trades * 100, 1) as win_rate_pct,
    stoploss_count,
    ROUND(CAST(stoploss_count AS REAL) / total_trades * 100, 1) as stoploss_rate_pct,
    roi_exits,
    trailing_exits,
    ROUND(avg_win / ABS(avg_loss), 2) as risk_reward_ratio,
    avg_profit_pct,
    total_profit_usd,
    total_fees_usd,
    ROUND(total_fees_usd / NULLIF(total_profit_usd, 0) * 100, 1) as fee_to_profit_pct,
    avg_hold_min
FROM trade_stats;
```

### Query 1B: Bot6 Performance (24/48h snapshot)
```sql
WITH time_filter AS (
    SELECT datetime('2025-10-30 10:27:19') as start_time,
           datetime('now') as end_time
),
trade_stats AS (
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN exit_reason = 'stop_loss' THEN 1 ELSE 0 END) as stoploss_count,
        SUM(CASE WHEN exit_reason IN ('roi', 'exit_signal') THEN 1 ELSE 0 END) as roi_exits,
        ROUND(AVG(close_profit), 4) as avg_profit_pct,
        ROUND(AVG(CASE WHEN close_profit > 0 THEN close_profit END), 4) as avg_win,
        ROUND(AVG(CASE WHEN close_profit <= 0 THEN close_profit END), 4) as avg_loss,
        ROUND(SUM(close_profit * stake_amount / 100), 2) as total_profit_usd,
        ROUND(SUM(fee_open + fee_close), 4) as total_fees_usd,
        ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 * 60 AS REAL)), 1) as avg_hold_min
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time 
    AND close_date <= time_filter.end_time
    AND is_open = 0
)
SELECT 
    total_trades,
    wins,
    ROUND(CAST(wins AS REAL) / total_trades * 100, 1) as win_rate_pct,
    stoploss_count,
    roi_exits,
    ROUND(CAST(roi_exits AS REAL) / total_trades * 100, 1) as roi_exit_rate_pct,
    ROUND(avg_win / ABS(avg_loss), 2) as risk_reward_ratio,
    total_profit_usd,
    total_fees_usd,
    ROUND(total_fees_usd / NULLIF(total_profit_usd, 0) * 100, 1) as fee_to_profit_pct,
    avg_hold_min
FROM trade_stats;
```

### Query 2: Trade Frequency Validation (for Bot6 especially)
```sql
WITH time_filter AS (
    SELECT datetime('2025-10-30 10:27:19') as start_time,
           datetime('now') as end_time
),
hourly_trades AS (
    SELECT 
        strftime('%Y-%m-%d %H:00', close_date) as hour,
        COUNT(*) as trades_closed,
        ROUND(AVG(close_profit), 4) as avg_profit,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins
    FROM trades, time_filter
    WHERE close_date >= time_filter.start_time 
    AND close_date <= time_filter.end_time
    AND is_open = 0
    GROUP BY hour
)
SELECT 
    hour,
    trades_closed,
    avg_profit,
    wins,
    ROUND(CAST(trades_closed AS REAL) / 1 * 24, 1) as trades_per_day_projection
FROM hourly_trades
ORDER BY hour DESC;
```

### Query 3: Correlation Impact (Bot1 vs Bot3, Bot6 vs Bot5)
```sql
-- For Bot1 vs Bot3 (both BTC-focused)
WITH bot1_daily AS (
    SELECT 
        DATE(close_date) as trade_date,
        SUM(close_profit * stake_amount / 100) as bot1_daily_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
    GROUP BY DATE(close_date)
),
bot3_daily AS (
    SELECT 
        DATE(close_date) as trade_date,
        SUM(close_profit * stake_amount / 100) as bot3_daily_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
    GROUP BY DATE(close_date)
)
SELECT 
    COUNT(*) as days,
    ROUND(AVG(bot1_daily_pnl), 2) as bot1_avg_daily,
    ROUND(AVG(bot3_daily_pnl), 2) as bot3_avg_daily,
    ROUND((SUM((bot1_daily_pnl - (SELECT AVG(bot1_daily_pnl) FROM bot1_daily)) * 
              (bot3_daily_pnl - (SELECT AVG(bot3_daily_pnl) FROM bot3_daily))) /
             SQRT(SUM(POWER(bot1_daily_pnl - (SELECT AVG(bot1_daily_pnl) FROM bot1_daily), 2)) *
                  SUM(POWER(bot3_daily_pnl - (SELECT AVG(bot3_daily_pnl) FROM bot3_daily), 2)))), 2) as correlation
FROM bot1_daily
JOIN bot3_daily ON bot1_daily.trade_date = bot3_daily.trade_date;
```

### Query 4: Trailing Stop Effectiveness (Bot1 & Bot6)
```sql
WITH trailing_analysis AS (
    SELECT 
        exit_reason,
        COUNT(*) as count,
        ROUND(AVG(close_profit), 4) as avg_profit,
        SUM(close_profit) as total_profit,
        ROUND(MIN(close_profit), 4) as worst,
        ROUND(MAX(close_profit), 4) as best
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
    AND exit_reason IN ('trailing_stop_loss', 'stop_loss', 'roi', 'exit_signal')
    GROUP BY exit_reason
)
SELECT 
    exit_reason,
    count,
    ROUND(count * 100.0 / (SELECT COUNT(*) FROM trades 
        WHERE close_date >= datetime('2025-10-30 10:21:41') 
        AND is_open = 0), 1) as pct_of_total,
    avg_profit,
    total_profit,
    worst,
    best
FROM trailing_analysis
ORDER BY count DESC;
```

### Query 5: Risk-Adjusted Performance (Sharpe/Sortino)
```sql
WITH daily_returns AS (
    SELECT 
        DATE(close_date) as trade_date,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) as daily_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
    GROUP BY DATE(close_date)
),
return_stats AS (
    SELECT 
        COUNT(*) as days,
        ROUND(AVG(daily_pnl), 2) as mean_daily_return,
        ROUND(SQRT(SUM(POWER(daily_pnl - (SELECT AVG(daily_pnl) FROM daily_returns), 2)) / 
                   COUNT(*)), 2) as std_dev_return,
        ROUND(SQRT(SUM(POWER(
            CASE WHEN daily_pnl < 0 THEN daily_pnl ELSE 0 END - 0, 2)) / 
            COUNT(*)), 2) as downside_std_dev
    FROM daily_returns
)
SELECT 
    days,
    mean_daily_return,
    std_dev_return,
    downside_std_dev,
    ROUND(mean_daily_return / NULLIF(std_dev_return, 0) * SQRT(365), 2) as sharpe_ratio,
    ROUND(mean_daily_return / NULLIF(downside_std_dev, 0) * SQRT(365), 2) as sortino_ratio
FROM return_stats;
```

---

## MONITORING SCHEDULE & CHECKPOINTS

### Every 6 Hours (Automated Monitoring)
1. **Process Health**: `ps aux | grep -E 'bot1_strategy001|bot6_paxg_strategy001' | grep -v grep`
2. **Memory Check**: `free -h` (ensure <80% used)
3. **Port Status**: `netstat -ln | grep -E ':808[0-5]'` (all 6 ports bound)
4. **Recent Trades**: Run Query 1A and 1B for 6-hour snapshot
5. **Alert Check**: Any win rate <30%, P&L <-20% hourly, fees >50%

### 24-Hour Checkpoint (Oct 31, 10:21 UTC)
1. Run all 5 Bot1/Bot6 specific queries
2. Run existing Bot3/Bot5 queries from MONITORING_PLAN_20251030.md (Queries 1-8)
3. Calculate 95% confidence intervals for all metrics
4. Compare against 24-hour success criteria above
5. Generate checkpoint report
6. Make CONTINUE/ROLLBACK decision for individual bots

### 48-Hour Checkpoint (Nov 1, 10:27 UTC)
1. Complete all queries with full 48-hour dataset
2. Calculate final statistics and confidence intervals
3. Run correlation analysis (Query 3)
4. Validate trailing stop effectiveness (Query 4)
5. Calculate risk-adjusted metrics (Query 5)
6. Generate final Phase 2 completion report
7. Execute Phase 2 completion or Phase 2 extension decision

---

## INTEGRATION WITH EXISTING BOTS (Bot3 & Bot5)

### No Changes Required to Bot3/Bot5 Monitoring
- Continue existing monitoring protocol from MONITORING_PLAN_20251030.md
- Bot3: Maintain RSI-focused metrics
- Bot5: Maintain ROI exit efficiency tracking

### Portfolio-Level Metrics (All 4 Optimized Bots)

**Combined P&L Tracking:**
```sql
WITH all_optimized AS (
    SELECT 
        'Bot1' as bot,
        datetime('2025-10-30 10:21:41') as start_time,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) as cumulative_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
    
    UNION ALL
    
    SELECT 
        'Bot3' as bot,
        datetime('2025-10-30 08:27:00') as start_time,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) as cumulative_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 08:27:00')
    AND is_open = 0
    
    UNION ALL
    
    SELECT 
        'Bot5' as bot,
        datetime('2025-10-30 09:09:00') as start_time,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) as cumulative_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 09:09:00')
    AND is_open = 0
    
    UNION ALL
    
    SELECT 
        'Bot6' as bot,
        datetime('2025-10-30 10:27:19') as start_time,
        SUM(close_profit * stake_amount / 100 - (fee_open + fee_close)) as cumulative_pnl
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:27:19')
    AND is_open = 0
)
SELECT 
    bot,
    cumulative_pnl,
    ROUND(cumulative_pnl / 50, 1) as estimated_roi_pct  -- assuming ~$50 per bot
FROM all_optimized
ORDER BY cumulative_pnl DESC;
```

### Correlation Matrix Construction
Run correlation calculations for all bot pairs:
- Bot1 ↔ Bot3 (both BTC, Strategy001 vs SimpleRSI)
- Bot1 ↔ Bot6 (same Strategy001, different pairs)
- Bot3 ↔ Bot5 (SimpleRSI vs Strategy004-opt)
- Bot5 ↔ Bot6 (both PAXG, Strategy004 vs Strategy001)

**Success Criterion**: No pair >0.85 correlation (acceptable systemic risk)

---

## CRITICAL ALERTS & INTERVENTION TRIGGERS

### Immediate Rollback (Any Single Trigger)
- Bot1 win rate <40% after 8+ trades
- Bot6 win rate <50% after 10+ trades
- Combined Bot1+Bot6 P&L <-$10 USD (catastrophic loss)
- Fee ratio >40% of gross profit (self-defeating)
- Trailing stop not executing (parameter load failure)
- Portfolio P&L degradation >5% vs Oct 30 baseline
- Correlation Bot1↔Bot6 >0.9 (signal competition)
- Daily loss >3% of capital ($540)

### Warning Level (Monitor Closely)
- Win rate 40-50% for either bot (underperforming)
- Fee ratio 25-40% of gross profit (eroding alpha)
- Hold times <30 seconds or >1 hour (mechanism issues)
- No ROI exits visible in Bot6 (target ROI mechanism broken)
- Correlation 0.75-0.85 (elevated but manageable)
- Drawdown >5% in 24h (volatility spike)
- Process memory >600MB for either bot (memory leak)

---

## DECISION TREES

### 24-Hour Decision (Oct 31, 10:21 UTC)

```
START ASSESSMENT
  │
  ├─ BOTH Bot1 AND Bot6 Pass Criteria?
  │    ├─ YES → Continue to 48h checkpoint
  │    │         Lock parameters, document metrics
  │    │
  │    └─ NO → Individual Analysis
  │         │
  │         ├─ Bot1 Status?
  │         │    ├─ PASS → Keep Bot1, continue monitoring
  │         │    ├─ WARNING → Prepare rollback, extend monitoring
  │         │    └─ FAIL → ROLLBACK Bot1 immediately
  │         │
  │         └─ Bot6 Status?
  │              ├─ PASS → Keep Bot6, continue monitoring
  │              ├─ WARNING → Check fee impact, consider minor adjustment
  │              └─ FAIL → ROLLBACK Bot6 immediately
  │
  ├─ Critical Alerts Triggered?
  │    ├─ YES → EMERGENCY ROLLBACK (see triggers above)
  │    │         Capture system state, document failure
  │    │
  │    └─ NO → Continue per individual bot status
  │
  └─ Portfolio Health Check
       ├─ System P&L degraded >5%? → PAUSE and investigate
       ├─ Other bots degraded >2%? → Isolated issue, continue
       └─ No degradation? → Safe to proceed
```

### 48-Hour Decision (Nov 1, 10:27 UTC) - Phase 2 Completion

```
START FINAL ASSESSMENT
  │
  ├─ Calculate 95% Confidence Intervals for All Metrics
  │    │
  │    ├─ BOTH Bot1 AND Bot6 CIs Include Target Metrics?
  │    │    │
  │    │    ├─ YES → PROCEED TO PHASE 2 COMPLETION
  │    │    │         - All 4 optimized bots (Bot1/3/5/6) locked
  │    │    │         - Deploy Bot2 & Bot4 in Phase 3
  │    │    │         - Portfolio expected +20 USDT/week
  │    │    │
  │    │    └─ NO → Evaluate Individual Performance
  │    │         │
  │    │         ├─ Bot1 CI Includes Targets?
  │    │         │    ├─ YES → Lock Bot1
  │    │         │    └─ NO → EXTEND 24-48h monitoring
  │    │         │
  │    │         └─ Bot6 CI Includes Targets?
  │    │              ├─ YES → Lock Bot6
  │    │              └─ NO → EXTEND 24-48h monitoring
  │    │
  │    └─ Risk Metrics Validation
  │         ├─ Max Drawdown <3%? ✓
  │         ├─ Correlation All Pairs <0.85? ✓
  │         ├─ Fee Efficiency <15%? ✓
  │         └─ All YES? → Proceed to completion
  │             Any NO? → Address before completion
```

---

## ROLLBACK PROCEDURES (Consolidated)

### Bot1 Emergency Rollback
```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Stop Bot1
pkill -9 -f 'bot1_strategy001'
sleep 3

# Restore backup
cp /root/btc-bot/bot1_strategy001/config.json.backup_20251030_102013 \
   /root/btc-bot/bot1_strategy001/config.json

# Verify old parameters
grep -A 5 '"stoploss"' /root/btc-bot/bot1_strategy001/config.json

# Restart
cd /root/btc-bot && nohup .venv/bin/freqtrade trade --config bot1_strategy001/config.json > bot1_strategy001/nohup.out 2>&1 &

# Verify running
sleep 5 && pgrep -f 'bot1_strategy001' && echo "Bot1 rolled back successfully"
```

### Bot6 Emergency Rollback
```bash
# Stop Bot6
pkill -9 -f 'bot6_paxg_strategy001'
sleep 3

# Restore backup
cp /root/btc-bot/bot6_paxg_strategy001/config.json.backup_20251030_102013 \
   /root/btc-bot/bot6_paxg_strategy001/config.json

# Verify old parameters
grep -A 5 '"stoploss"' /root/btc-bot/bot6_paxg_strategy001/config.json

# Restart
cd /root/btc-bot && nohup .venv/bin/freqtrade trade --config bot6_paxg_strategy001/config.json > bot6_paxg_strategy001/freqtrade.log 2>&1 &

# Verify
sleep 5 && pgrep -f 'bot6_paxg_strategy001' && echo "Bot6 rolled back successfully"
```

---

## REPORTING TEMPLATES

### 24-Hour Checkpoint Report Template

```markdown
## 24-Hour Phase 2.3 Checkpoint - Oct 31, 10:21 UTC

### Bot1 (Strategy001-BTC) Results
- **Trades Closed**: X (Target: ≥5)
- **Win Rate**: X% (Target: ≥55%)
- **Trailing Stop Activations**: X (Target: ≥2)
- **P&L**: +/- $X.XX USD (Baseline: -5.24)
- **Fee Ratio**: X% of gross profit (Target: ≤20%)
- **Average Hold Time**: X min (Target: 5-30 min)
- **Status**: PASS / WARNING / FAIL

### Bot6 (Strategy001-PAXG) Results
- **Trades Closed**: X (Target: ≥6)
- **Win Rate**: X% (Target: ≥60%)
- **ROI Exits**: X% (Target: ≥50%)
- **P&L**: +/- $X.XX USD (Baseline: -3.20)
- **Fee Ratio**: X% of gross profit (Target: ≤15%)
- **Average Hold Time**: X min (Target: 3-20 min)
- **Trade Frequency**: X/day (Target: 3-4/day improvement)
- **Status**: PASS / WARNING / FAIL

### Portfolio Integration
- **Bot3 P&L**: +/- $X (Monitoring: No degradation)
- **Bot5 P&L**: +/- $X (Monitoring: No degradation)
- **Combined Bot1+Bot6**: +/- $X (Target: ≥-2.00)
- **System Uptime**: X% (Target: 100%)
- **Correlation Status**: All pairs <0.80 (Critical threshold: <0.90)

### Decision
[CONTINUE TO 48H / ROLLBACK BOT1 / ROLLBACK BOT6 / EMERGENCY ROLLBACK]

### Next Checkpoint
Nov 1, 2025, 10:27 UTC (48-hour go/no-go decision)
```

### 48-Hour Final Report Template

```markdown
## 48-Hour Phase 2.3 Completion Validation - Nov 1, 10:27 UTC

### Statistical Confidence Intervals (95%)

#### Bot1 (Strategy001-BTC)
- **Win Rate**: X% [CI: X%-Y%] (Target: ≥60%)
- **P&L**: +$X.XX [CI: $X-$Y] (Target: ≥+5.00)
- **Trade Count**: X (Target: ≥10)
- **CI Includes Target?**: YES / NO

#### Bot6 (Strategy001-PAXG)
- **Win Rate**: X% [CI: X%-Y%] (Target: ≥65%)
- **Trade Frequency**: X/day [CI: X-Y/day] (Target: 3-4x baseline)
- **P&L**: +$X.XX [CI: $X-$Y] (Target: ≥+4.00)
- **CI Includes Target?**: YES / NO

### Risk-Adjusted Performance
- **Portfolio Sharpe Ratio**: X.XX (Baseline: -0.20)
- **Max Drawdown (All 4 Bots)**: X% (Target: <3%)
- **Fee Efficiency**: X% of gross (Target: <15%)
- **Correlation Matrix**:
  - Bot1 ↔ Bot3: X.XX
  - Bot1 ↔ Bot6: X.XX
  - Bot5 ↔ Bot6: X.XX
  - Status: All <0.85? YES / NO

### Phase 2 Completion Decision

**PROCEED TO COMPLETION**: 
- Both bots pass 95% CI targets
- Risk metrics within limits
- Portfolio health verified
- 4 of 6 bots optimized (Phase 2 complete)
- Next: Plan Phase 3 (Bot2 & Bot4 optimization)

**EXTEND MONITORING**:
- One or both bots below target but positive trend
- Data insufficient (n<10 trades)
- Continue 24-48 more hours before decision

**ROLLBACK**:
- Either bot fails criteria
- P&L worse than baseline
- Risk thresholds breached
- Document failure mode for learning

### Phase 2 Completion Metrics (If Approved)
- **4 Bots Optimized**: Bot1, Bot3, Bot5, Bot6
- **Portfolio Improvement**: +23.04 USDT (7-day expected)
- **Trade Frequency**: +2.9x (Phase 2 optimizations)
- **Risk Score**: 6/10 (Managed, monitored)
- **Confidence**: 80%+
```

---

## MONITORING EXECUTION CHECKLIST

### Every 6 Hours
- [ ] Run Query 1A and 1B (Bot performance snapshot)
- [ ] Verify process health (ps aux)
- [ ] Check memory usage (<80%)
- [ ] Verify port bindings (all 6 bound)
- [ ] Review alert threshold status
- [ ] Note any anomalies in trade patterns

### At 24-Hour Checkpoint (Oct 31, 10:21 UTC)
- [ ] Run all Bot1/Bot6 specific queries (1A-5)
- [ ] Run Bot3/Bot5 queries from original plan (1-8)
- [ ] Calculate 95% confidence intervals
- [ ] Compare against 24-hour success criteria
- [ ] Verify correlation status
- [ ] Generate 24-hour report
- [ ] Execute continue/rollback decision
- [ ] Document decision rationale

### At 48-Hour Checkpoint (Nov 1, 10:27 UTC)
- [ ] Complete statistical validation with full dataset
- [ ] Calculate final risk-adjusted metrics
- [ ] Run correlation matrix analysis
- [ ] Validate trailing stop effectiveness
- [ ] Compare portfolio-level metrics
- [ ] Generate final Phase 2 report
- [ ] Execute Phase 2 completion or extension decision
- [ ] Plan Phase 3 deployment (if approved)

---

## TECHNICAL REFERENCE

### Database Locations
```bash
# Bot1 trades database
/root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite

# Bot6 trades database  
/root/btc-bot/bot6_paxg_strategy001/tradesv3.dryrun.sqlite

# Connect via SSH
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
sqlite3 /root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite
```

### Key Parameters Deployed
```
Bot1:
- stoploss: -0.015 (was -0.06)
- minimal_roi: {"0": 0.012, "15": 0.008, "30": 0.005, "60": 0.003}
- trailing_stop: true (new)
- trailing_stop_positive: 0.005
- trailing_stop_positive_offset: 0.008

Bot6:
- stoploss: -0.01 (was -0.06)
- minimal_roi: {"0": 0.008, "30": 0.006, "60": 0.004, "120": 0.002}
- trailing_stop: true (new)
- trailing_stop_positive: 0.003
- trailing_stop_positive_offset: 0.005
```

---

**Document Version**: 1.0 (Phase 2.3 Update)  
**Base Document**: MONITORING_PLAN_20251030.md (Bot3/Bot5)  
**Next Checkpoint**: October 31, 2025, 10:21 UTC (24-hour)  
**Final Checkpoint**: November 1, 2025, 10:27 UTC (48-hour completion decision)  
**Analyst**: Quantitative Trading Performance Analyst
