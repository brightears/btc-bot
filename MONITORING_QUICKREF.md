# 🚀 QUICK REFERENCE - Bot3 & Bot5 Optimization Monitoring

**Deployment Times:** Bot3 @ 08:27 UTC | Bot5 @ 09:09 UTC (Oct 30, 2025)

## 🔍 ESSENTIAL COMMANDS

### Connect to VPS
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
```

### Quick Performance Check (Run on VPS)
```bash
# Bot3 - Last 24h performance
sqlite3 /root/btc-bot/bot3_*/tradesv3.dryrun.sqlite "
SELECT 'Bot3 24h:',
  COUNT(*) as trades,
  ROUND(SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as win_rate,
  ROUND(SUM(CASE WHEN exit_reason = 'stop_loss' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as sl_rate
FROM trades 
WHERE close_date >= datetime('now', '-24 hours') AND is_open = 0;"

# Bot5 - Last 24h performance  
sqlite3 /root/btc-bot/bot5_*/tradesv3.dryrun.sqlite "
SELECT 'Bot5 24h:',
  COUNT(*) as trades,
  ROUND(SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as win_rate,
  ROUND(SUM(CASE WHEN exit_reason = 'roi' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as roi_rate  
FROM trades
WHERE close_date >= datetime('now', '-24 hours') AND is_open = 0;"
```

### Check Stop-Loss Performance (Critical for Bot3)
```bash
sqlite3 /root/btc-bot/bot3_*/tradesv3.dryrun.sqlite "
SELECT exit_reason, COUNT(*) as count, ROUND(AVG(close_profit), 2) as avg_profit
FROM trades
WHERE close_date >= '2025-10-30 08:27:00' AND is_open = 0
GROUP BY exit_reason;"
```

### Monitor Open Positions
```bash
# Both bots open positions
for bot in bot3 bot5; do
  echo "=== $bot open positions ===" 
  sqlite3 /root/btc-bot/${bot}_*/tradesv3.dryrun.sqlite "
    SELECT pair, ROUND((julianday('now') - julianday(open_date)) * 24, 1) as hours_open,
           ROUND((stop_loss - open_rate) / open_rate * 100, 2) as sl_pct
    FROM trades WHERE is_open = 1;"
done
```

### System Health Quick Check
```bash
# Process status
supervisorctl status bot3 bot5

# Memory check
free -h | grep Mem

# Recent errors
grep -c ERROR /root/btc-bot/bot{3,5}_*/logs/freqtrade.log
```

## 📊 SUCCESS CRITERIA SUMMARY

### 24-Hour (Oct 31, 08:27 UTC)
| Bot | Win Rate | Stop-Loss Rate | Min Trades | Decision |
|-----|----------|----------------|------------|----------|
| Bot3 | ≥48% | ≤40% | 3+ | Continue or Rollback |
| Bot5 | +5% improvement | - | 3+ | Continue or Rollback |

### 48-Hour (Nov 1, 09:09 UTC)  
| Bot | Win Rate | Stop-Loss Rate | Min Trades | Decision |
|-----|----------|----------------|------------|----------|
| Bot3 | ≥53% | ≤25% | 6+ | Phase 2.3 or Rollback |
| Bot5 | +10% improvement | ROI exits ≥50% | 6+ | Phase 2.3 or Rollback |

## 🚨 EMERGENCY ROLLBACK

### Bot3 Rollback (if needed)
```bash
supervisorctl stop bot3
cd /root/btc-bot/bot3_*
# Edit config.json: stoploss: -0.01, RSI: 30/70, remove staged ROI
nano config.json
supervisorctl start bot3
```

### Bot5 Rollback (if needed)
```bash
supervisorctl stop bot5
cd /root/btc-bot/bot5_*
# Edit config.json: stoploss: -0.04, ROI: 7%/5%/3%/2%
nano config.json
supervisorctl start bot5
```

## ⏰ CHECKPOINT SCHEDULE

- **6-Hour Checks**: Run quick performance check above
- **24-Hour (Oct 31, 08:27 UTC)**: Full analysis, continue/rollback decision
- **48-Hour (Nov 1, 09:09 UTC)**: Final validation, Phase 2.3 decision

## 📈 KEY METRICS TO TRACK

1. **Win Rate Trend**: Must show improvement toward targets
2. **Stop-Loss Frequency**: Bot3 must show reduction from 55%
3. **Fee Impact**: Should stay <15% of gross profit
4. **Trade Frequency**: Minimum 3-6 trades per bot per 48h
5. **ROI Efficiency**: Bot5 should exit via ROI >50% of time

## 🔴 CRITICAL ALERTS - IMMEDIATE ACTION

- Drawdown >10% in 24h → ROLLBACK
- Win rate <30% with >5 trades → ROLLBACK  
- Stop-loss rate >70% (Bot3) → ROLLBACK
- Fee ratio >40% of profit → INVESTIGATE
- Bot crash/zombie → RESTART & INVESTIGATE

## 📝 REPORTING TEMPLATE

```markdown
## [24h/48h] Checkpoint - [DATE TIME]

**Bot3 Performance:**
- Trades: X | Win Rate: X% (Target: 55%)
- Stop-Loss Rate: X% (Target: 23%)
- Status: [PASS/WARNING/FAIL]

**Bot5 Performance:**
- Trades: X | Win Rate Change: +X%
- ROI Exits: X% | Fee Impact: X%
- Status: [PASS/WARNING/FAIL]

**Decision:** [Continue/Rollback/Phase 2.3]
**Next Check:** [DATE TIME]
```

---
*Save this for quick reference during monitoring period*
