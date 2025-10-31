# Phase 2.3 Monitoring Quick Reference Guide
**Status**: Ready for immediate deployment  
**Created**: October 30, 2025, 10:28 UTC  
**Analyst**: Quantitative Trading Performance Analyst

---

## CRITICAL DATES & TIMES (UTC)

| Event | Date/Time | Action | Status |
|-------|-----------|--------|--------|
| **Bot1 Deployed** | Oct 30, 10:21:41 | Start monitoring | ✅ DONE |
| **Bot6 Deployed** | Oct 30, 10:27:19 | Start monitoring | ✅ DONE |
| **24h Checkpoint** | Oct 31, 10:30:00 | Run all queries, make decision | ✅ COMPLETE - Extended |
| **EXTENDED Checkpoint** | **Nov 4, 10:00-12:00** | **Final Phase 2 decision (4.5 days)** | ⏳ PENDING |

**NOTE**: 48h checkpoint (Nov 1) CANCELLED due to extreme market low activity. Extended to Tuesday Nov 4 to capture weekend + weekday data (4.5 days total). See 24H_CHECKPOINT_20251031.md for rationale.

---

## ONE-MINUTE CHECKPOINT SUMMARY

### 24-Hour Checkpoint Results (Oct 31, 10:30 UTC) ✅ COMPLETE
**Bot1**: 2 trades, 50% win rate, -$1.37 P&L ⚠️ INSUFFICIENT DATA
**Bot6**: 1 trade, 100% win rate, +$0.31 P&L ⚠️ INSUFFICIENT DATA
**Portfolio**: Only 7 total trades across all 6 bots (market-wide low activity)

**Decision**: ⚠️ EXTENDED TO TUESDAY NOV 4 (insufficient sample size, not bot failure)

### Tuesday 4.5-Day Checkpoint Success Criteria (Nov 4, 10:00-12:00 UTC)
**Bot1** (ADJUSTED for low market activity):
- >=8 trades (lowered from 10)
- >=55% win rate
- P&L >= $0 (positive or breakeven)

**Bot6** (ADJUSTED for low market activity):
- >=10 trades (should show frequency improvement)
- >=60% win rate
- P&L > $0 (positive)

**Portfolio**:
- All 6 bots operational
- No daily loss >3% ($540)
- Optimized bots (Bot1/3/5/6) equal/better than non-optimized (Bot2/4)

**Decision**: Both PASS → Phase 2 COMPLETE | Either FAIL → Rollback failed bot(s)

---

## IMMEDIATE ROLLBACK TRIGGERS (Emergency Stop)

- Bot1 win rate <40% after 8+ trades
- Bot6 win rate <50% after 10+ trades
- Combined P&L <-$10 (catastrophic loss)
- Fee ratio >40% of gross (self-defeating)
- Trailing stop not executing (parameter failure)
- System P&L degradation >5%
- Correlation Bot1/Bot6 >0.9 (redundancy)
- Daily loss >3% of capital (>$540)

**Action**: EXECUTE ROLLBACK IMMEDIATELY - See procedures below

---

## SQL QUERIES (5 New Queries for Bot1/Bot6)

### Query 1A: Bot1 Performance Snapshot
```bash
sqlite3 /root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite << 'SQL'
WITH trade_stats AS (
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
        ROUND(SUM(close_profit * stake_amount / 100), 2) as total_profit_usd,
        ROUND(SUM(fee_open + fee_close), 4) as total_fees_usd,
        ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 * 60 AS REAL)), 1) as avg_hold_min
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:21:41')
    AND is_open = 0
)
SELECT 
    total_trades,
    ROUND(CAST(wins AS REAL) / total_trades * 100, 1) as win_rate_pct,
    total_profit_usd,
    total_fees_usd,
    ROUND(total_fees_usd / NULLIF(total_profit_usd, 0) * 100, 1) as fee_to_profit_pct,
    avg_hold_min
FROM trade_stats;
SQL
```

### Query 1B: Bot6 Performance Snapshot
```bash
sqlite3 /root/btc-bot/bot6_paxg_strategy001/tradesv3.dryrun.sqlite << 'SQL'
WITH trade_stats AS (
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN exit_reason IN ('roi', 'exit_signal') THEN 1 ELSE 0 END) as roi_exits,
        ROUND(SUM(close_profit * stake_amount / 100), 2) as total_profit_usd,
        ROUND(SUM(fee_open + fee_close), 4) as total_fees_usd,
        ROUND(AVG(CAST((julianday(close_date) - julianday(open_date)) * 24 * 60 AS REAL)), 1) as avg_hold_min
    FROM trades
    WHERE close_date >= datetime('2025-10-30 10:27:19')
    AND is_open = 0
)
SELECT 
    total_trades,
    ROUND(CAST(wins AS REAL) / total_trades * 100, 1) as win_rate_pct,
    roi_exits,
    ROUND(CAST(roi_exits AS REAL) / total_trades * 100, 1) as roi_exit_rate_pct,
    total_profit_usd,
    total_fees_usd,
    ROUND(total_fees_usd / NULLIF(total_profit_usd, 0) * 100, 1) as fee_to_profit_pct,
    avg_hold_min
FROM trade_stats;
SQL
```

### Query 2-5: See Full Document
(See MONITORING_PLAN_PHASE_2_3_UPDATE_20251030.md for trade frequency, correlation, trailing stop, and Sharpe/Sortino queries)

---

## SYSTEM HEALTH CHECK (Every 6 Hours)

```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Check process status
echo "=== PROCESS STATUS ===" && \
ps aux | grep -E 'bot[16]_' | grep -v grep && \
echo "" && \
echo "=== MEMORY USAGE ===" && \
free -h && \
echo "" && \
echo "=== PORT STATUS ===" && \
netstat -ln | grep -E ':(8080|8085)'
```

**Success Indicators**:
- Both Bot1 and Bot6 processes running
- Memory usage <80%
- Ports 8080 and 8085 bound (listening)

---

## TUESDAY CHECKPOINT EXECUTION (Nov 4, 10:00-12:00 UTC)

### Step 1: Connect to VPS
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
cd /root/btc-bot
```

### Step 2: Run Bot1 Query (4.5-day period)
```bash
sqlite3 bot1_strategy001/tradesv3.dryrun.sqlite \
"SELECT COUNT(*) trades, ROUND(CAST(SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 1) win_rate, ROUND(SUM(close_profit * stake_amount / 100), 2) pnl_usd FROM trades WHERE close_date >= '2025-10-30 10:21:41' AND is_open = 0;"
```

### Step 3: Run Bot6 Query (4.5-day period)
```bash
sqlite3 bot6_paxg_strategy001/tradesv3.dryrun.sqlite \
"SELECT COUNT(*) trades, ROUND(CAST(SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 1) win_rate, ROUND(SUM(close_profit * stake_amount / 100), 2) pnl_usd FROM trades WHERE close_date >= '2025-10-30 10:27:19' AND is_open = 0;"
```

### Step 4: Compare All Bots (Market Activity Context)
```bash
# Check all 6 bots over same period for comparison
for bot in bot1_strategy001 bot2_strategy004 bot3_simplersi bot4_paxg_strategy004 bot5_paxg_strategy004_opt bot6_paxg_strategy001; do
  echo "=== $bot ===" && sqlite3 /root/btc-bot/$bot/tradesv3.dryrun.sqlite "SELECT COUNT(*) FROM trades WHERE close_date >= '2025-10-30 10:00:00' AND is_open = 0;"
done
```

### Step 5: Evaluate Against Adjusted Success Criteria
- Bot1: Trades >=8? Win rate >=55%? P&L >= $0?
- Bot6: Trades >=10? Win rate >=60%? P&L > $0?
- Portfolio: Bot1/6 equal/better than Bot2/4 over same period?

### Step 6: Decision
- **Both PASS** → Phase 2 COMPLETE, plan Phase 3
- **Either FAIL** → Execute rollback (see below), document root cause

---

## EMERGENCY ROLLBACK PROCEDURES

### Rollback Bot1
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Stop and restore
pkill -9 -f 'bot1_strategy001'
sleep 3
cp /root/btc-bot/bot1_strategy001/config.json.backup_20251030_102013 \
   /root/btc-bot/bot1_strategy001/config.json

# Restart
cd /root/btc-bot && nohup .venv/bin/freqtrade trade --config bot1_strategy001/config.json > bot1_strategy001/nohup.out 2>&1 &

# Verify
sleep 5 && pgrep -f 'bot1_strategy001' && echo "Bot1 ROLLED BACK"
```

### Rollback Bot6
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Stop and restore
pkill -9 -f 'bot6_paxg_strategy001'
sleep 3
cp /root/btc-bot/bot6_paxg_strategy001/config.json.backup_20251030_102013 \
   /root/btc-bot/bot6_paxg_strategy001/config.json

# Restart
cd /root/btc-bot && nohup .venv/bin/freqtrade trade --config bot6_paxg_strategy001/config.json > bot6_paxg_strategy001/freqtrade.log 2>&1 &

# Verify
sleep 5 && pgrep -f 'bot6_paxg_strategy001' && echo "Bot6 ROLLED BACK"
```

---

## CHECKPOINT REPORT TEMPLATE (Use at Both 24h & 48h)

```markdown
## [24H / 48H] PHASE 2.3 CHECKPOINT REPORT
**Date**: [YYYY-MM-DD HH:MM UTC]

### BOT1 METRICS
- Trades Closed: [X]
- Win Rate: [X%]
- P&L: $[X.XX]
- Status: [PASS / WARNING / FAIL]

### BOT6 METRICS
- Trades Closed: [X]
- Win Rate: [X%]
- P&L: $[X.XX]
- Status: [PASS / WARNING / FAIL]

### PORTFOLIO CHECK
- Bot3 P&L: $[X] (Baseline: -)
- Bot5 P&L: $[X] (Baseline: -)
- Combined Bot1+6: $[X] (Target: >-2.00)

### DECISION
[CONTINUE 48H / ROLLBACK BOT1 / ROLLBACK BOT6 / ROLLBACK BOTH]

### CONFIDENCE LEVEL
[0-50% LOW / 50-75% MEDIUM / 75-100% HIGH]
```

---

## KEY PARAMETERS DEPLOYED

### Bot1 (Strategy001-BTC)
```
stoploss: -0.015 (from -0.06)
minimal_roi: {"0": 0.012, "15": 0.008, "30": 0.005, "60": 0.003}
trailing_stop: true
trailing_stop_positive: 0.005
trailing_stop_positive_offset: 0.008
```

### Bot6 (Strategy001-PAXG)
```
stoploss: -0.01 (from -0.06)
minimal_roi: {"0": 0.008, "30": 0.006, "60": 0.004, "120": 0.002}
trailing_stop: true
trailing_stop_positive: 0.003
trailing_stop_positive_offset: 0.005
```

---

## DOCUMENT REFERENCES

**Detailed Framework**: `/Users/norbert/Documents/Coding Projects/btc-bot/MONITORING_PLAN_PHASE_2_3_UPDATE_20251030.md` (822 lines)

**Integration Summary**: `/Users/norbert/Documents/Coding Projects/btc-bot/MONITORING_INTEGRATION_SUMMARY.txt` (336 lines)

**Previous Plans**:
- MONITORING_PLAN_20251030.md (Bot3/Bot5 framework)
- PHASE_2_3_COMPLETION_20251030.md (deployment details)
- RISK_VALIDATION_SUMMARY.md (risk assessment)

---

## CONTACT & ESCALATION

**System Down / Emergency**: Immediate rollback (see procedures above)  
**Questions**: Refer to full monitoring plan (822 lines, all scenarios covered)  
**Phase 3 Planning**: If Phase 2 approved, plan Bot2 & Bot4 optimization

---

**Status**: Extended monitoring in progress
**Next Action**: Execute Tuesday checkpoint (Nov 4, 10:00-12:00 UTC)
**Last Updated**: October 31, 2025, 10:45 UTC (24h checkpoint complete, extended to Tuesday)

