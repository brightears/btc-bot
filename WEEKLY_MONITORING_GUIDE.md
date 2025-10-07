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

## 🔍 What to Look For

### ✅ Good Signs (Everything Normal)

- **Win Rate**: 40-60% (for mean reversion strategy like SimpleRSI)
- **Trade Frequency**: 5-15 trades per day
- **Average Trade Duration**: 30 minutes - 2 hours
- **Profit per Trade**: $1-5 on winners, $0.50-1 on losers
- **Max Drawdown**: Stays under 5% ($500)
- **No Error Messages**: Bot runs smoothly

### ⚠️ Warning Signs (Needs Attention)

- **Win Rate <30%** after 50+ trades → Strategy not working for current market
- **Too Many Trades** (>30/day) → Overtrading, adjust strategy
- **Too Few Trades** (0-2/day) → Market ranging, strategy can't find signals
- **All Trades Hitting Stop-Loss** → Entry logic broken
- **Trades Not Closing** (open >4 hours) → Exit logic issue
- **Balance Dropping >5%** in 3 days → Performance problem

### 🚨 Red Flags (Immediate Action)

- **Bot Stops Responding** → Check if process died
- **Error Messages in Telegram** → Share with Claude immediately
- **Balance Dropping >10%** → Stop bot, investigate
- **Same Trade Opening Repeatedly** → Logic bug, stop immediately
- **No Telegram Messages for >24 hours** → Bot or Telegram connection issue

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

**Last Updated**: October 7, 2025
**Bot Status**: Running (SimpleRSI, 5m, BTC/USDT)
**Next Rotation**: Sunday, October 13, 2025
