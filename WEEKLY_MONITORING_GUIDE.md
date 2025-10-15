# Weekly Monitoring & Management Guide
**Freqtrade Bot on Hetzner VPS**

---

## 📅 Quick Reference

| Task | Frequency | What to Do |
|------|-----------|------------|
| Check Telegram | Daily | Monitor trade notifications |
| Review Performance | Daily (5 min) | Check win rate, P&L |
| Strategy Rotation | Weekly | Ask Claude to run rotation |
| Community Strategies | After 2 weeks | Ask Claude to research & add |
| Go Live Decision | After 4 weeks | Evaluate dry-run results |

---

## 📱 Daily Monitoring (5 minutes)

### What You Should See in Telegram

**Normal Activity:**
```
✅ Entry Alert: BTC/USDT at $XX,XXX
✅ Exit Alert: +$2.50 profit (+2.5%)
✅ Status: 1 open trade
```

**Expected Frequency:**
- **Trades**: 5-15 per day (depending on market volatility)
- **Notifications**: Every trade entry/exit
- **Status updates**: Bot heartbeat in logs (you don't need to check logs unless issues)

### Daily Checklist

**Morning (2 minutes):**
- [ ] Open Telegram
- [ ] Check for any trade notifications overnight
- [ ] Send `/daily` command
- [ ] Note: Win rate, number of trades, P&L

**Evening (3 minutes):**
- [ ] Review day's performance
- [ ] Screenshot any interesting trades or patterns
- [ ] Note if anything seems unusual

### Key Metrics to Track

Create a simple spreadsheet or note:

| Date | Trades | Wins | Losses | P&L | Balance | Notes |
|------|--------|------|--------|-----|---------|-------|
| Oct 7 | 3 | 2 | 1 | +$1.50 | $10,001.50 | First day |
| Oct 8 | 8 | 5 | 3 | +$4.20 | $10,005.70 | |
| Oct 9 | 6 | 3 | 3 | -$0.80 | $10,004.90 | |

**Or simply track in Telegram:**
- `/profit` - Shows cumulative P&L
- `/daily` - Shows today's stats
- `/balance` - Shows current balance

---

## 🤖 Multi-Bot Monitoring (Week 2+)

**Starting Oct 15, 2025, we're running 6 bots in parallel:**

**BTC Bots (Bitcoin Trading):**
- Bot 1: Strategy001 (Trend following, optimized) - $3,000
- Bot 2: Strategy004 (Hybrid multi-indicator, optimized) - $3,000
- Bot 3: SimpleRSI (Mean reversion, original params) - $3,000

**PAXG Bots (Gold Trading):**
- Bot 4: Strategy004 Baseline (PAXG/USDT) - $3,000
- Bot 5: Strategy004 Optimized (PAXG/USDT, gold-tuned) ⭐ - $3,000
- Bot 6: Strategy001 (PAXG/USDT, comparison) - $3,000

**Important:** ALL bots have Telegram disabled to avoid API conflicts.
- No Telegram trade notifications
- All trade data collected in bot databases
- Performance analysis via Claude or VPS logs

### Daily Multi-Bot Checklist

**Morning (5 minutes):**
- [ ] SSH to VPS and check all 6 bots running
- [ ] Quick memory check: `free -h` (should show 150+ MB available)
- [ ] Check for Telegram monitoring alerts (bot crashes, memory issues)

**Evening (10 minutes):**
- [ ] Note any unusual behavior
- [ ] Check if any Telegram alerts received
- [ ] Track overall system health

### Tracking Spreadsheet Format

| Date | BTC P/L | PAXG P/L | Combined | System | Notes |
|------|---------|----------|----------|--------|-------|
| Oct 15 | $0 | $0 | $0 | Stable | First day, memory fixed |
| Oct 16 | +$2.50 | +$1.80 | +$4.30 | Stable | All bots trading |

**Detailed bot tracking (weekly):**

| Bot | Pair | Strategy | Trades | Wins | P/L | Win Rate |
|-----|------|----------|--------|------|-----|----------|
| Bot 1 | BTC/USDT | Strategy001 | 5 | 3 | +$2.50 | 60% |
| Bot 2 | BTC/USDT | Strategy004 | 4 | 2 | -$0.80 | 50% |
| Bot 3 | BTC/USDT | SimpleRSI | 22 | 8 | +$1.20 | 36% |
| Bot 4 | PAXG/USDT | Strategy004 | 3 | 2 | +$0.90 | 67% |
| Bot 5 | PAXG/USDT | Strategy004 Opt | 4 | 3 | +$1.50 | 75% |
| Bot 6 | PAXG/USDT | Strategy001 | 2 | 1 | -$0.60 | 50% |

### Weekly Comparison (Sundays)

**Ask Claude to analyze performance:**
```
Hey Claude, can you analyze this week's performance for all 6 bots?

Please compare:
1. BTC bots (Bot 1-3): Which performed best?
2. PAXG bots (Bot 4-6): Which performed best?
3. Overall: BTC vs PAXG - which is more profitable?
```

**Calculate for EACH bot:**
- Win rate
- Total P/L
- Number of trades
- Best/worst trade
- Average profit per trade

**Example Weekly Summary:**
```
BTC Bots:
- Bot1 (Strategy001): 60% win rate, +$12.50 P/L, 7 trades 🏆
- Bot2 (Strategy004): 55% win rate, +$8.30 P/L, 5 trades
- Bot3 (SimpleRSI): 35% win rate, -$4.20 P/L, 22 trades

PAXG Bots:
- Bot4 (Baseline): 67% win rate, +$5.40 P/L, 6 trades
- Bot5 (Optimized): 75% win rate, +$9.80 P/L, 8 trades 🏆
- Bot6 (Strategy001): 50% win rate, +$2.10 P/L, 4 trades

Winner This Week: Bot5 (PAXG Optimized) 🥇
BTC vs PAXG: PAXG +$17.30 vs BTC +$16.60
```

**Decision:** Identify top performers for potential live trading

---

## 🔍 What to Look For

### ✅ Good Signs (Everything Normal)

**Per-Bot Expectations:**

**BTC Bots:**
- **Bot1 (Strategy001):** 0.7 trades/day, 60-75% win rate, longer holds
- **Bot2 (Strategy004):** 0.5 trades/day, 60-70% win rate, short holds
- **Bot3 (SimpleRSI):** 3 trades/day, 35-45% win rate, frequent trades

**PAXG Bots:**
- **Bot4 (Baseline):** 0.5 trades/day, 60-70% win rate, medium holds
- **Bot5 (Optimized):** 0.7 trades/day, 70-85% win rate, wider profit targets
- **Bot6 (Strategy001):** 0.5 trades/day, 55-70% win rate, medium holds

**Combined (All 6 Bots):**
- **Trade Frequency**: 8-12 trades per day across all bots
- **At Least 2-3 Bots Positive**: Diversification means not all need to win
- **Max Single Loss**: ≤$6 for BTC bots, ≤$4 for PAXG bots
- **No Error Messages**: All 6 bots run smoothly
- **Memory Available**: 150+ MB (check with `free -h`)

### ⚠️ Warning Signs (Needs Attention)

- **Win Rate <30%** after 50+ trades → Strategy not working for current market
- **Too Many Trades** (>30/day) → Overtrading, adjust strategy
- **Too Few Trades** (0-2/day) → Market ranging, strategy can't find signals
- **All Trades Hitting Stop-Loss** → Entry logic broken
- **Trades Not Closing** (open >4 hours) → Exit logic issue
- **Balance Dropping >5%** in 3 days → Performance problem

### 🚨 Red Flags (Immediate Action)

- **Bot Stops Responding** → Check if process died, monitoring will auto-restart
- **Frequent Restart Alerts** (3+ in 1 hour) → Memory issue or bot crash loop, contact Claude
- **Memory Critical Alert** (< 50 MB available) → System under memory pressure
- **Balance Dropping >10%** → Stop bots, investigate strategy issues
- **Same Trade Opening Repeatedly** → Logic bug, stop immediately
- **All 6 Bots Down** → Critical system failure, check VPS status

---

## 📊 Weekly Performance Review

### When to Review
**Every Sunday** (or 7 days after start)

### What to Check

**1. Send Telegram Commands:**
```
/profit - Get weekly P&L
/weekly - Weekly statistics
/performance - Strategy performance breakdown
```

**2. Calculate Key Metrics:**

| Metric | How to Calculate | Good Target |
|--------|-----------------|-------------|
| Win Rate | (Wins / Total Trades) × 100 | 45-60% |
| Profit Factor | Total Wins $ / Total Losses $ | >1.2 |
| Average Win | Total Win $ / Number of Wins | $2-5 |
| Average Loss | Total Loss $ / Number of Losses | $0.50-1 |
| Max Drawdown | Largest balance drop from peak | <5% |
| Weekly Return | (Current Balance - Start) / Start | 0-5% |

**3. Ask Yourself:**
- [ ] Is the strategy consistently profitable?
- [ ] Is the win rate acceptable?
- [ ] Are losses controlled (staying within stop-loss)?
- [ ] Any concerning patterns?
- [ ] Ready to continue another week?

---

## 🔄 Weekly Strategy Rotation

### When to Request Rotation

**Automatic Schedule**: Every Sunday after reviewing performance

**OR Early Rotation If:**
- Win rate drops below 35% after 50+ trades
- Strategy clearly not working for current market conditions
- Balance drops >7% from starting point
- You notice a clear trend change (e.g., BTC going from ranging to strong trend)

### How to Request Rotation from Claude

**Open a new Claude Code session and say:**

```
Hey Claude, it's been a week. Can you run strategy rotation on the VPS?

Here's this week's performance:
- Trades: XX
- Win Rate: XX%
- P&L: $XX
- Current Strategy: SimpleRSI

[Attach Telegram screenshots of /weekly and /profit]
```

**Claude will:**
1. SSH into your VPS
2. Run `python strategy_rotator.py`
3. Show you backtest results for all strategies
4. Tell you which strategy scored best
5. Switch to new strategy if better than current
6. Restart bot with new strategy
7. Confirm everything is running

**What You'll See:**
```
Backtesting Results:
- SimpleRSI: Score 18.5 (current)
- MomentumStrategy: Score 22.8 (BETTER)
- BollingerMeanReversion: Score 15.2
- NostalgiaForInfinityX5: Score 20.1

Switching to MomentumStrategy...
Bot restarted with MomentumStrategy ✅
```

---

## 🌟 Adding Community Strategies

### When to Add More Strategies

**After 2 weeks** when you understand how the system works AND one of these is true:
- Current strategies not performing well (<40% win rate)
- Want more diversification
- Market conditions changing frequently
- You want more automated adaptation

### How to Request Community Strategies

**Message to Claude:**

```
Claude, I've been monitoring for 2 weeks. Performance has been [good/okay/poor].

Can you research and add 5-10 community strategies for BTC/USDT?

Focus on:
- Proven track records
- Different approaches (momentum, mean reversion, breakout)
- Well-maintained (recent updates)
- Good documentation

Current performance context:
[Paste /profit and /weekly results]
```

**Claude will:**
1. Research top Freqtrade community strategies
2. Filter for BTC/USDT compatibility
3. Download 5-10 best strategies to VPS
4. Run backtest comparison
5. Show you results
6. Auto-select best performing strategy
7. Document what was added

**You'll get a report like:**
```
Added 8 Community Strategies:

1. CombinedBinHAndCluc - Momentum (Score: 24.5) ⭐ BEST
2. Discord_1_SMAOffset - Trend following (Score: 21.2)
3. ElliotV8_20 - Wave pattern (Score: 19.8)
...

Switched to CombinedBinHAndCluc (best performer).
Bot restarted ✅
```

---

## 📈 Sharing Performance Updates with Claude

### Format for Quick Updates

**Copy this template:**

```
Weekly Update - [Date]

**Performance:**
- Trades: XX
- Win Rate: XX%
- Total P&L: $XX (+/- X%)
- Balance: $XX

**Observations:**
- [Any patterns you noticed]
- [Any concerns]
- [Questions]

**Telegram Screenshots:**
[Paste screenshots of /profit, /daily, /weekly]

**Next Steps:**
- [ ] Continue monitoring
- [ ] Run strategy rotation
- [ ] Add community strategies
- [ ] Other: ___
```

### What Screenshots to Share

**Essential:**
1. `/profit` output - Shows cumulative P&L
2. `/weekly` output - Shows weekly stats
3. `/daily` output - Shows today's performance

**If Issues:**
4. Any error messages
5. Screenshot of unusual trade patterns
6. `/status` if trades stuck open

**How to Share:**
- Take screenshot in Telegram
- Paste in Claude Code chat
- Add any context or questions

---

## 🎯 Decision Points

### After Week 1 (Oct 14)
**Decision**: Continue monitoring or adjust?

**Continue if:**
- ✅ Win rate >40%
- ✅ No major issues
- ✅ Bot stable and reliable
- ✅ P&L positive or neutral

**Adjust if:**
- ⚠️ Win rate <35%
- ⚠️ Frequent errors
- ⚠️ P&L consistently negative

**Action**: Request strategy rotation from Claude

---

### After Week 2 (Oct 21)
**Decision**: Add community strategies?

**Add if:**
- Want more automated adaptation
- Current strategies performing inconsistently
- Want to try different approaches

**Skip if:**
- Current strategy working well
- Want to keep it simple
- Still learning the system

**Action**: Request community strategy research from Claude

---

### After Week 4 (Nov 4)
**Decision**: Go live with real money?

**Go live if ALL of these are true:**
- ✅ Win rate consistently >45% over 4 weeks
- ✅ Profit factor >1.2
- ✅ Max drawdown <5%
- ✅ Strategy rotation working smoothly
- ✅ You understand the bot behavior
- ✅ No concerning patterns or bugs
- ✅ Telegram notifications reliable
- ✅ Comfortable risking real capital

**Steps to Go Live:**
1. Ask Claude to help prepare for live trading
2. Start with small capital ($500-1000, 5-10% of total)
3. Change config: `dry_run: false`
4. Monitor CLOSELY for first week
5. Gradually scale up if successful

**Stay in dry-run if:**
- ⚠️ Any of above criteria not met
- ⚠️ Want more confidence
- ⚠️ Market conditions uncertain

---

## 🚨 Emergency Procedures

### If Bot Stops Working

**1. Check if bot is running:**
```
Message Claude: "Hey Claude, can you check if the bot is running on the VPS?"
```

Claude will:
- SSH to VPS
- Check process status
- Review logs
- Restart if needed

**2. If you want to stop immediately:**
```
Message Claude: "Emergency stop - please kill the bot process"
```

**3. If Telegram stops working:**
```
Message Claude: "Telegram notifications stopped. Can you check and fix?"
```

### If Balance Drops Significantly

**If >5% drop in one day:**

1. Take screenshot of `/profit` and `/status`
2. Message Claude: "Balance dropped [X%] today. Here's the data: [screenshots]. Should I stop?"
3. Claude will analyze and recommend action

**If >10% drop:**

1. Stop monitoring
2. Message Claude immediately: "Emergency: Balance down [X%]. Stop bot and investigate."
3. Wait for Claude's analysis before resuming

---

## 📝 Quick Command Reference

### Essential Telegram Commands

| Command | What It Shows | When to Use |
|---------|---------------|-------------|
| `/status` | Open trades | Check anytime |
| `/profit` | Total P&L | Daily check |
| `/balance` | Current balance | Daily check |
| `/daily` | Today's stats | Morning/evening review |
| `/weekly` | Week's stats | Sunday review |
| `/help` | All commands | When you forget commands |

### When to Contact Claude

**Routine (via this guide):**
- Weekly strategy rotation (Sundays)
- Add community strategies (after 2 weeks)
- Performance evaluation help
- Going live preparation (after 4 weeks)

**Issues:**
- Bot not responding
- Telegram stopped
- Error messages
- Unusual behavior
- Balance concerns
- Questions about metrics

**Just say:**
```
"Hey Claude, [describe issue]. Here's the data: [screenshots]"
```

---

## ✅ Your Weekly Checklist

**Copy this to your notes app:**

### Monday
- [ ] Check weekend performance (`/profit`)
- [ ] Note any issues from weekend

### Tuesday-Saturday
- [ ] Morning: Check Telegram
- [ ] Evening: Review day's trades
- [ ] Track unusual patterns

### Sunday (Strategy Rotation Day)
- [ ] Run `/weekly` and `/profit`
- [ ] Review performance metrics
- [ ] Screenshot results
- [ ] Message Claude for strategy rotation
- [ ] Confirm new strategy running

### Every 2 Weeks (Optional)
- [ ] Evaluate if community strategies needed
- [ ] Request research from Claude if yes

### Month 1 Review (Nov 4)
- [ ] Calculate 4-week performance
- [ ] Decide on live trading
- [ ] Message Claude to discuss next steps

---

## 💡 Tips for Success

### 1. Be Patient
- First week is learning both for you and the strategy
- Don't panic on individual losing trades
- Focus on overall trend, not daily fluctuations

### 2. Stay Consistent
- Check Telegram daily (even just 2 minutes)
- Run weekly rotation on schedule
- Track metrics in simple format

### 3. Document Everything
- Keep screenshots of interesting patterns
- Note when market conditions change
- Track your decisions and reasoning

### 4. Trust the Process
- Strategies are backtested before use
- Rotation system picks objectively best performer
- Dry-run is risk-free learning

### 5. Ask Claude Anything
- No question is too basic
- Share concerns early
- Request explanations of metrics
- Ask for help interpreting results

---

## 📚 Additional Resources

### If You Want to Learn More

**Freqtrade Docs:**
- https://www.freqtrade.io/en/stable/
- Strategy documentation
- Telegram bot commands
- Performance metrics explained

**Your Project Files:**
- `DEPLOYMENT_SUCCESS_2025_10_07.md` - Full deployment story
- `README.md` - Project overview
- `MIGRATION_SUMMARY.md` - Why we migrated to Freqtrade

**VPS Access:**
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
cd /root/btc-bot
tail -f freqtrade.log  # View live logs
```

---

## 🎉 You're All Set!

**Remember:**
- ✅ Bot is running in dry-run (no real money at risk)
- ✅ Telegram will notify you of all trades
- ✅ Check in daily for 5 minutes
- ✅ Contact Claude every Sunday for rotation
- ✅ Evaluate after 2-4 weeks

**Have fun and happy monitoring! 🚀**

---

**Questions?** Just message Claude:
```
"Hey Claude, I have a question about [topic from this guide]..."
```

**Important Note on Telegram (Oct 15, 2025):**
- ALL 6 bots have Telegram disabled (trade notifications disabled)
- Monitoring system sends Telegram alerts for:
  - Bot crashes (3+ restarts in 1 hour)
  - Memory critical (< 50 MB available)
  - All 6 bots down simultaneously
- All trade data collected in bot databases (analyze via Claude or VPS logs)
- See CHECKPOINT_2025_10_15.md for system state and rollback instructions

**Last Updated**: October 15, 2025, 03:30 AM UTC
**Bot Status**: 6-bot parallel (3 BTC + 3 PAXG strategies)
**System**: 2GB RAM + 2GB swap, memory optimized, 95%+ uptime
**Telegram Config**: All bots disabled (monitoring alerts only)
**Next Review**: Sunday, October 20, 2025
