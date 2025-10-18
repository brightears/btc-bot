# How to Start Conversations When Returning

This guide provides conversation templates to help Claude quickly understand your context when you return to analyze trading performance or troubleshoot issues.

---

## 🎯 Quick Reference

| Scenario | When to Use | Template Link |
|----------|-------------|---------------|
| **Performance Analysis** | After 2-3 days of trading | [Jump to template](#performance-analysis-after-2-3-days) |
| **Troubleshooting Alerts** | Received Telegram alerts | [Jump to template](#troubleshooting-telegram-alerts) |
| **Bots Stopped Trading** | No trades for hours/days | [Jump to template](#bots-not-trading) |
| **Going Live Preparation** | After 4+ weeks success | [Jump to template](#going-live-after-4-weeks) |
| **Quick Status Check** | Just checking in | [Jump to template](#quick-status-check) |
| **After Long Absence** | Been away 1+ weeks | [Jump to template](#after-long-absence-1-weeks) |

---

## Performance Analysis (After 2-3 Days)

**When to use:** You've waited 2-3 days since Oct 15 for stable trading data accumulation.

**Template:**
```
Hey Claude, I'm back after [X] days. Can you analyze the performance of our 6 trading bots?

Starting point:
- Checkpoint: CHECKPOINT_2025_10_15.md
- Git commit: 4840ec9
- Bots running since: Oct 15, 2025, 03:00 AM UTC

Please analyze:
1. **BTC bots** (Bot 1-3): Which strategy performed best?
2. **PAXG bots** (Bot 4-6): Which strategy performed best?
3. **BTC vs PAXG**: Which asset is more profitable overall?
4. **Trade statistics**: Win rates, P&L, trade frequency for each bot
5. **Concerns**: Any worrying patterns, bugs, or issues?
6. **Recommendation**: Continue testing, adjust strategies, or prepare for live trading?

[Optional: Attach any Telegram screenshots if you received alerts]
```

**What Claude will do:**
1. SSH to VPS and query all 6 bot databases
2. Extract trade history, wins/losses, P&L for each bot
3. Calculate win rates, profit factors, and other metrics
4. Compare strategies and asset classes
5. Provide detailed performance report
6. Recommend next steps

---

## Troubleshooting Telegram Alerts

**When to use:** You received Telegram alerts about bot crashes or memory issues.

**Template:**
```
Claude, I received Telegram alerts. Can you investigate?

Alert details:
- Type: [Bot restart alert / Memory critical / All bots down]
- Time: [When you saw the alert]
- Frequency: [How many times / ongoing]
- Screenshot: [Paste Telegram screenshot if available]

System checkpoint: CHECKPOINT_2025_10_15.md
Git commit: 4840ec9

Please check:
1. Are all 6 bots currently running?
2. What's the memory status? (free -h)
3. Any errors in bot logs?
4. What caused the crashes?
5. Is this a one-time issue or recurring problem?
6. Do I need to take action, or is auto-restart handling it?
```

**Example alert scenarios:**

**Scenario 1: Frequent restart alerts**
```
Alert received:
🚨 BOT ALERT: bot3_simplersi restarted 6 times in last hour!
Monitor immediately: ssh root@5.223.55.219

My message to Claude:
"Claude, I got 6 restart alerts for bot3. Is this the memory issue again?
Checkpoint: CHECKPOINT_2025_10_15.md"
```

**Scenario 2: Memory critical**
```
Alert received:
⚠️ Memory critical! Only 45MB available. Swap: 1.9GB used.

My message to Claude:
"Claude, memory critical alert. Should I upgrade to 4GB RAM now?
Checkpoint: CHECKPOINT_2025_10_15.md"
```

**Scenario 3: All bots down**
```
Alert received:
🚨 CRITICAL: All 6 bots are DOWN! Manual intervention required.

My message to Claude:
"Claude, all 6 bots crashed. Please investigate and restart.
Checkpoint: CHECKPOINT_2025_10_15.md"
```

---

## Bots Not Trading

**When to use:** Bots haven't made any trades for an unusually long time.

**Template:**
```
Claude, the bots haven't traded in [X hours/days]. Can you check if they're working?

Observation:
- Last trade I saw: [Date/time or "I don't remember seeing any trades"]
- Expected: Should see 8-12 trades/day across all 6 bots
- Duration: It's been [X hours/days] with no activity

System checkpoint: CHECKPOINT_2025_10_15.md
Git commit: 4840ec9

Please investigate:
1. Are all 6 bots running and healthy?
2. Are they analyzing market data properly?
3. Any errors preventing trade execution?
4. Is this normal for current market conditions (ranging/low volatility)?
5. Should I be concerned or is this expected behavior?
```

**Possible causes Claude will check:**
- Bots crashed (monitoring should have restarted them)
- Market is ranging (no clear signals)
- Strategy conditions not met
- Exchange connectivity issues
- Configuration errors

---

## Going Live (After 4+ Weeks)

**When to use:** You've tested for 4+ weeks, results look good, ready to trade with real money.

**Template:**
```
Claude, it's been [X] weeks since we started. Dry-run results look [excellent/good/promising].

Performance summary (my observations):
- Overall P&L: [Estimate if you tracked it]
- Best performing bot: [If you noticed one doing well]
- System stability: [Any issues or smooth sailing?]

System checkpoint: CHECKPOINT_2025_10_15.md
Git commit: 4840ec9

I'm thinking about going live with real money. Please help prepare:

1. **Review 4-week performance**: Is it good enough to go live?
   - What are the actual win rates for each bot?
   - Which bot(s) should I deploy live?
   - Any red flags that say "don't do it yet"?

2. **Recommend VPS upgrade**: Should I upgrade to 4GB RAM before going live?
   - Current: 2GB + 2GB swap
   - Cost: ~€5-10/month more
   - Benefits and necessity?

3. **Create go-live checklist**: What do I need to do?
   - Start with how much capital? ($500? $1000?)
   - Deploy all 6 bots or just best performer?
   - What settings to change (dry_run: false, etc.)?
   - Safety measures to have in place?

4. **Risk management**: How to minimize risk?
   - Position sizing
   - Stop-loss verification
   - Monitoring frequency during first week
```

**What Claude will do:**
1. Analyze full 4-week performance history
2. Calculate comprehensive statistics
3. Identify best performing strategies
4. Recommend VPS upgrade (strongly advised before live trading)
5. Create detailed go-live checklist
6. Set up enhanced monitoring for live trading
7. Help with initial configuration changes

---

## Quick Status Check

**When to use:** Just want to confirm everything is running smoothly.

**Template:**
```
Hey Claude, quick status check on our 6-bot system.

Checkpoint: CHECKPOINT_2025_10_15.md
Git commit: 4840ec9

Please verify:
1. All 6 bots running? (ps count)
2. Memory healthy? (free -h)
3. Any recent alerts or issues?
4. System uptime since last restart?

Just a quick health check - no deep analysis needed.
```

**Expected response time:** 1-2 minutes for quick verification.

---

## After Long Absence (1+ Weeks)

**When to use:** You've been away for a week or more and need a comprehensive catch-up.

**Template:**
```
Claude, I'm back after [X weeks]. I need a comprehensive update.

Last known state:
- Checkpoint: CHECKPOINT_2025_10_15.md
- Git commit: 4840ec9
- System start: Oct 15, 2025, 03:00 AM UTC
- Last checked: [Date you last looked]

Please give me a full status report:

1. **System Health**:
   - Are all 6 bots still running?
   - Any crashes, restarts, or issues?
   - Memory status and stability?
   - VPS health (disk space, CPU, etc.)?

2. **Performance Summary** (since Oct 15):
   - Total trades executed
   - Overall P&L (all 6 bots combined)
   - Best performing bot
   - Worst performing bot
   - BTC vs PAXG comparison

3. **Issues & Incidents**:
   - Any Telegram alerts sent?
   - Any downtime or system failures?
   - Problems that occurred and how they were resolved?

4. **Current State**:
   - Are we still at git commit 4840ec9?
   - Any configuration changes needed?
   - System still stable with 2GB + swap?

5. **Recommended Next Steps**:
   - Continue monitoring?
   - Adjust strategies?
   - Ready to go live?
   - VPS upgrade needed?

Take your time with this analysis - I've been away a while and need the full picture.
```

**What Claude will do:**
1. Comprehensive system health check
2. Deep analysis of all trading activity
3. Review of all monitoring logs
4. Detailed incident report (if any)
5. Current state verification
6. Personalized recommendations based on performance

---

## Special Scenarios

### Scenario: Want to Add More Bots

**Template:**
```
Claude, our current 6 bots are performing [well/okay]. I want to add more bots.

Current state:
- Checkpoint: CHECKPOINT_2025_10_15.md
- 6 bots running on 2GB + 2GB swap

Question: Can I add more bots with current resources?

Please analyze:
1. Current memory usage and headroom
2. Maximum number of bots possible with 2GB + swap
3. Should I upgrade to 4GB RAM first?
4. Which additional strategies to test?
```

---

### Scenario: Want to Stop a Specific Bot

**Template:**
```
Claude, I want to stop [Bot X] because [reason].

Current state:
- Checkpoint: CHECKPOINT_2025_10_15.md
- All 6 bots running

Please help:
1. How to safely stop just [Bot X]?
2. Will monitoring try to restart it?
3. Should I remove it from configs or just stop the process?
4. Can the other 5 bots continue running?
```

---

### Scenario: Market Crash or Major Event

**Template:**
```
Claude, [describe major event - e.g., "Bitcoin crashed 20% today" or "Major Fed announcement"].

Current state:
- Checkpoint: CHECKPOINT_2025_10_15.md
- Bots running in dry-run mode

Question: Should I stop the bots or let them continue?

Please analyze:
1. How are our bots handling this volatility?
2. Any unusual losses or wins?
3. Recommendation: Stop, continue, or adjust?
4. Is this a good learning opportunity for the strategies?
```

---

## Key Information to Always Include

**Minimum context for Claude:**
- ✅ **Checkpoint**: CHECKPOINT_2025_10_15.md
- ✅ **Git commit**: 4840ec9 (if you know it hasn't changed)
- ✅ **What you want to know**: Specific question or analysis needed

**Optional but helpful:**
- 📅 **Time reference**: "Been running since Oct 15" or "Last checked 3 days ago"
- 📸 **Screenshots**: Any Telegram alerts, unusual trade patterns, or error messages
- 📊 **Observations**: Anything you noticed (e.g., "Bot 3 seems to trade more frequently")

---

## What Claude Will Access

**When you start a conversation, Claude can:**
1. ✅ SSH to VPS and check system status
2. ✅ Read all bot databases for trade history
3. ✅ Analyze monitoring logs for incidents
4. ✅ Check git commit and file states
5. ✅ Review bot configurations
6. ✅ Execute diagnostic commands

**What Claude CANNOT see unless you provide:**
- ❌ Your Telegram messages (you need to screenshot and share)
- ❌ What you've been thinking/observing
- ❌ Changes you made manually on VPS without committing

---

## Tips for Best Results

**Be specific:**
✅ "Bot 3 hasn't traded in 2 days"
❌ "Something seems wrong"

**Include timeframes:**
✅ "Since yesterday at 3 PM"
❌ "A while ago"

**Share observations:**
✅ "I noticed Bot 5 (PAXG) seems to be winning more often"
❌ Just asking "how are the bots doing?"

**Attach evidence:**
✅ Telegram screenshot of alert
❌ "I got some alert about restarts"

**State your goal:**
✅ "I want to know if we're ready to go live"
❌ "What's the performance?"

---

## Emergency Contacts

**If you can't reach Claude or need immediate help:**

1. **Stop all bots:**
   ```bash
   ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219 "pkill -f freqtrade"
   ```

2. **Check system status:**
   ```bash
   ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219 "free -h && ps aux | grep freqtrade | grep -v grep | wc -l"
   ```

3. **Rollback to checkpoint:**
   ```bash
   ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
   cd /root/btc-bot
   git reset --hard 4840ec9
   python3 start_6_bots.py
   ```

4. **Review documentation:**
   - [CHECKPOINT_2025_10_15.md](CHECKPOINT_2025_10_15.md) - Full system state
   - [MONITORING_SYSTEM.md](MONITORING_SYSTEM.md) - Troubleshooting guides
   - [WEEKLY_MONITORING_GUIDE.md](WEEKLY_MONITORING_GUIDE.md) - Monitoring procedures

---

## Example: Perfect Return Message

**Template for returning after Oct 18 fixes (Use Oct 28, 2025):**

```
Hey Claude, it's been 10 days since you fixed the zombie crashes and low trade frequency.

Context:
- Checkpoint: CHECKPOINT_2025_10_18.md
- Fixes applied: Oct 18, 2025
  1. Bot 2/3 port conflicts resolved (8081, 8082)
  2. exit_profit_only bug fixed in all strategies
  3. Zombie detection added to monitoring

What I observed:
- Telegram alerts received: [describe any alerts or say "none"]
- Expected improvement: +300% trade frequency

Please analyze:
1. Total trades accumulated (expected 80-120 vs previous 9)
2. Trade frequency per bot (should be 8-10/day total now)
3. Which bots are winning? (BTC vs PAXG comparison)
4. Win rates and P/L for each bot
5. Any zombie crashes detected and auto-fixed?
6. Recommendation: Continue testing or ready for go-live?

Read CHECKPOINT_2025_10_18.md first to understand what was fixed.
```

**Why this template is perfect:**
- ✅ References correct checkpoint (Oct 18)
- ✅ Mentions specific fixes applied
- ✅ Sets expectations (trade frequency improvement)
- ✅ Asks for zombie detection verification
- ✅ Focuses on 10-day performance window

---

**Last Updated**: October 18, 2025, 12:00 PM UTC
**For System**: 6-bot parallel trading (CHECKPOINT_2025_10_18.md)
**Fixes Applied**: Port conflicts + exit_profit_only + zombie detection
**Next Expected Use**: October 28, 2025 (10 days after fixes)

**Remember**: Always reference CHECKPOINT_2025_10_18.md so Claude knows the latest system state! 🎯
