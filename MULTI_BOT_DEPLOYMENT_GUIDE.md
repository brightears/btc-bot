# Multi-Bot Deployment Guide - Week 2

**Purpose:** Deploy 3 Freqtrade strategies in parallel for maximum data collection
**Date:** October 13, 2025
**Target Completion:** 30-45 minutes
**Difficulty:** Intermediate

---

## Prerequisites

✅ VPS access: `ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219`
✅ Strategies selected: Strategy001, Strategy004, SimpleRSI
✅ Optimized parameters ready
✅ Week 1 bot stopped

---

## Architecture Overview

```
/root/btc-bot/
├── bot1_strategy001/          # Bot 1: Strategy001 optimized
│   ├── config.json
│   ├── tradesv3.dryrun.sqlite
│   └── freqtrade.log
├── bot2_strategy004/          # Bot 2: Strategy004 optimized
│   ├── config.json
│   ├── tradesv3.dryrun.sqlite
│   └── freqtrade.log
├── bot3_simplersi/            # Bot 3: SimpleRSI original
│   ├── config.json
│   ├── tradesv3.dryrun.sqlite
│   └── freqtrade.log
└── user_data/                 # Shared strategies folder
    └── strategies/
        ├── Strategy001.py (OPTIMIZED)
        ├── Strategy004.py (OPTIMIZED)
        └── SimpleRSI.py (ORIGINAL)
```

**Each bot:**
- Runs independently with own database
- Uses $3,000 dry-run capital ($100/trade)
- Sends Telegram notifications with bot name prefix
- Logs to separate file

---

## Step-by-Step Deployment

### PHASE 1: Pre-Deployment Checks (5 minutes)

#### Step 1.1: SSH to VPS
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
cd /root/btc-bot
```

#### Step 1.2: Stop Current Bot
```bash
# Find running Freqtrade processes
ps aux | grep freqtrade

# Kill all Freqtrade processes
pkill -9 -f freqtrade

# Verify nothing running
ps aux | grep freqtrade | grep -v grep
# Should return nothing
```

#### Step 1.3: Backup Current State
```bash
# Backup current database
cp tradesv3.dryrun.sqlite tradesv3.dryrun.sqlite.week1.backup

# Backup current config
cp config.json config.json.week1.backup

# Backup current log
cp freqtrade.log freqtrade.log.week1.backup

echo "Week 1 backup complete"
```

#### Step 1.4: Verify Strategy Files
```bash
# Check optimized strategies exist
ls -lh user_data/strategies/Strategy001.py
ls -lh user_data/strategies/Strategy004.py
ls -lh user_data/strategies/SimpleRSI.py

# Verify parameters in Strategy001
grep -A 5 "minimal_roi\|stoploss" user_data/strategies/Strategy001.py | head -10

# Expected output:
# minimal_roi = {
#     "0": 0.03,
#     "20": 0.02,
#     "40": 0.015,
#     "60": 0.01
# }
# stoploss = -0.06
```

---

### PHASE 2: Create Bot Directories (5 minutes)

#### Step 2.1: Create Directory Structure
```bash
cd /root/btc-bot

# Create bot directories
mkdir -p bot1_strategy001
mkdir -p bot2_strategy004
mkdir -p bot3_simplersi

# Verify
ls -ld bot*/
```

#### Step 2.2: Copy Base Configuration to Each Bot
```bash
# Copy config.json to each bot directory
cp config.json bot1_strategy001/
cp config.json bot2_strategy004/
cp config.json bot3_simplersi/

# Verify
ls bot*/config.json
```

---

### PHASE 3: Configure Bot 1 - Strategy001 (5 minutes)

#### Step 3.1: Edit Bot 1 Configuration
```bash
cd /root/btc-bot/bot1_strategy001

# Open config.json for editing
nano config.json
```

#### Step 3.2: Update Configuration

**Find and modify these sections:**

```json
{
  "strategy": "Strategy001",
  "dry_run": true,
  "dry_run_wallet": 3000,
  "stake_currency": "USDT",
  "stake_amount": 100,
  "max_open_trades": 1,

  "minimal_roi": {
    "0": 0.03,
    "20": 0.02,
    "40": 0.015,
    "60": 0.01
  },
  "stoploss": -0.06,

  "timeframe": "5m",

  "exchange": {
    "name": "binance",
    "key": "YOUR_BINANCE_KEY",
    "secret": "YOUR_BINANCE_SECRET",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": ["BTC/USDT"],
    "pair_blacklist": []
  },

  "telegram": {
    "enabled": true,
    "token": "YOUR_TELEGRAM_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "entry": "on",
      "exit": "on",
      "entry_fill": "on",
      "exit_fill": "on",
      "bot_name": "Bot1_Strategy001"
    }
  },

  "datadir": "/root/btc-bot/user_data/data/binance",
  "user_data_dir": "/root/btc-bot/user_data",
  "db_url": "sqlite:////root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite",
  "logfile": "/root/btc-bot/bot1_strategy001/freqtrade.log"
}
```

**Key Changes:**
- `"strategy": "Strategy001"`
- `"dry_run_wallet": 3000`
- `"minimal_roi"` and `"stoploss"` with optimized values
- `"bot_name": "Bot1_Strategy001"`
- `"db_url"` pointing to bot1 directory
- `"logfile"` pointing to bot1 directory

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

#### Step 3.3: Verify Configuration
```bash
# Check strategy name
grep '"strategy"' config.json

# Check bot name
grep '"bot_name"' config.json

# Check database path
grep '"db_url"' config.json
```

---

### PHASE 4: Configure Bot 2 - Strategy004 (5 minutes)

#### Step 4.1: Edit Bot 2 Configuration
```bash
cd /root/btc-bot/bot2_strategy004
nano config.json
```

#### Step 4.2: Make Same Changes as Bot 1

**Change these values:**
- `"strategy": "Strategy004"`
- `"bot_name": "Bot2_Strategy004"`
- `"db_url": "sqlite:////root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite"`
- `"logfile": "/root/btc-bot/bot2_strategy004/freqtrade.log"`
- Keep same `minimal_roi` and `stoploss` as Bot 1 (both strategies optimized the same)

**Save and exit**

#### Step 4.3: Verify
```bash
grep '"strategy"\|"bot_name"\|"db_url"' config.json
```

---

### PHASE 5: Configure Bot 3 - SimpleRSI (5 minutes)

#### Step 5.1: Edit Bot 3 Configuration
```bash
cd /root/btc-bot/bot3_simplersi
nano config.json
```

#### Step 5.2: Configure SimpleRSI (ORIGINAL Parameters)

**Change these values:**
- `"strategy": "SimpleRSI"`
- `"bot_name": "Bot3_SimpleRSI"`
- `"db_url": "sqlite:////root/btc-bot/bot3_simplersi/tradesv3.dryrun.sqlite"`
- `"logfile": "/root/btc-bot/bot3_simplersi/freqtrade.log"`

**IMPORTANT - Use ORIGINAL SimpleRSI parameters:**
```json
{
  "minimal_roi": {
    "0": 0.02
  },
  "stoploss": -0.01,
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.015,
  "trailing_only_offset_is_reached": true
}
```

**Save and exit**

#### Step 5.3: Verify
```bash
grep '"strategy"\|"bot_name"\|"stoploss"' config.json
```

---

### PHASE 6: Start All Bots (5 minutes)

#### Step 6.1: Activate Virtual Environment
```bash
cd /root/btc-bot
source .venv/bin/activate
```

#### Step 6.2: Start Bot 1
```bash
cd bot1_strategy001
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
echo "Bot 1 PID: $!"
```

#### Step 6.3: Start Bot 2
```bash
cd /root/btc-bot/bot2_strategy004
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
echo "Bot 2 PID: $!"
```

#### Step 6.4: Start Bot 3
```bash
cd /root/btc-bot/bot3_simplersi
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
echo "Bot 3 PID: $!"
```

#### Step 6.5: Verify All Running
```bash
ps aux | grep freqtrade | grep -v grep

# Expected output: 3 processes
# root     12345  ... freqtrade trade --config bot1_strategy001/config.json
# root     12346  ... freqtrade trade --config bot2_strategy004/config.json
# root     12347  ... freqtrade trade --config bot3_simplersi/config.json
```

---

### PHASE 7: Verification (10 minutes)

#### Step 7.1: Check Logs for Errors
```bash
cd /root/btc-bot

# Check Bot 1 startup
tail -50 bot1_strategy001/freqtrade.log

# Look for:
# - "Dry run is enabled" ✅
# - "Strategy: Strategy001" ✅
# - "Searching for USDT pairs" ✅
# - NO errors ✅

# Check Bot 2
tail -50 bot2_strategy004/freqtrade.log

# Check Bot 3
tail -50 bot3_simplersi/freqtrade.log
```

#### Step 7.2: Verify Telegram Notifications

**Open Telegram and check for 3 startup messages:**

1. **Bot1_Strategy001:**
   ```
   Dry run is enabled. All trades are simulated.

   Exchange: binance
   Stake per trade: 100 USDT
   Strategy: Strategy001
   ```

2. **Bot2_Strategy004:**
   ```
   Dry run is enabled. All trades are simulated.

   Exchange: binance
   Stake per trade: 100 USDT
   Strategy: Strategy004
   ```

3. **Bot3_SimpleRSI:**
   ```
   Dry run is enabled. All trades are simulated.

   Exchange: binance
   Stake per trade: 100 USDT
   Strategy: SimpleRSI
   ```

#### Step 7.3: Test Telegram Commands

**In Telegram, send to each bot:**
```
/status
/balance
/count
```

**Expected responses:**
- `/status` - "no active trade" (initial state)
- `/balance` - "9900.00 USDT" (3x $3000 - $100 for initial setup)
- `/count` - "current: 0, max: 1, total: 0"

#### Step 7.4: Monitor Live Logs
```bash
# Watch all 3 bots simultaneously (Ctrl+C to exit)
tail -f bot1_strategy001/freqtrade.log bot2_strategy004/freqtrade.log bot3_simplersi/freqtrade.log
```

**Look for heartbeat messages every ~60 seconds:**
```
Bot heartbeat. PID=12345, version='2025.6', state='RUNNING'
```

---

### PHASE 8: Post-Deployment Tasks (5 minutes)

#### Step 8.1: Document PIDs
```bash
# Save process IDs for reference
ps aux | grep freqtrade | grep -v grep > /root/btc-bot/running_bots.txt

cat /root/btc-bot/running_bots.txt
```

#### Step 8.2: Create Monitoring Script
```bash
cat > /root/btc-bot/check_all_bots.sh << 'EOF'
#!/bin/bash
echo "=== Bot Status Check ==="
echo ""
ps aux | grep freqtrade | grep -v grep | wc -l | xargs echo "Running bots:"
echo ""
echo "Bot 1 (Strategy001) - Last 5 log lines:"
tail -5 /root/btc-bot/bot1_strategy001/freqtrade.log
echo ""
echo "Bot 2 (Strategy004) - Last 5 log lines:"
tail -5 /root/btc-bot/bot2_strategy004/freqtrade.log
echo ""
echo "Bot 3 (SimpleRSI) - Last 5 log lines:"
tail -5 /root/btc-bot/bot3_simplersi/freqtrade.log
EOF

chmod +x /root/btc-bot/check_all_bots.sh

# Test it
./check_all_bots.sh
```

#### Step 8.3: Set Up Automatic Restart (Optional)
```bash
# Create systemd service for each bot (advanced)
# OR use screen/tmux for persistent sessions
# OR monitor manually

# Simple cron job to check every hour:
crontab -e

# Add line:
# 0 * * * * /root/btc-bot/check_all_bots.sh > /root/btc-bot/bot_status_$(date +\%Y\%m\%d_\%H).log
```

---

## Troubleshooting

### Issue: Bot Won't Start

**Error:** "Strategy not found"
```bash
# Solution: Check strategy file exists
ls user_data/strategies/Strategy001.py

# If missing, copy from backup or original repo
```

**Error:** "Database locked"
```bash
# Solution: Kill all freqtrade processes
pkill -9 -f freqtrade

# Wait 10 seconds, then restart
```

**Error:** "Invalid configuration"
```bash
# Solution: Validate JSON syntax
python3 -c "import json; json.load(open('bot1_strategy001/config.json'))"

# If error, check for:
# - Missing commas
# - Extra commas
# - Unmatched brackets
```

### Issue: No Telegram Messages

**Check Telegram configuration:**
```bash
grep '"telegram"' -A 10 bot1_strategy001/config.json

# Verify:
# - "enabled": true
# - Correct token
# - Correct chat_id
```

**Test manually:**
```bash
# Send test message using bot token
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test from VPS"
```

### Issue: Bots Trading Identically

**Check they're using different strategies:**
```bash
grep '"strategy"' bot*/config.json

# Expected output:
# bot1_strategy001/config.json:  "strategy": "Strategy001",
# bot2_strategy004/config.json:  "strategy": "Strategy004",
# bot3_simplersi/config.json:  "strategy": "SimpleRSI",
```

### Issue: Bot Crashes After Start

**Check logs for errors:**
```bash
grep -i "error\|exception\|traceback" bot1_strategy001/freqtrade.log
```

**Common causes:**
- Missing dependencies: `pip install -r requirements.txt`
- Strategy has bugs: Check strategy file syntax
- Database corruption: Delete `.sqlite` file and restart

---

## Monitoring Commands

### Quick Status Check
```bash
# Are all 3 bots running?
ps aux | grep freqtrade | grep -v grep | wc -l
# Should output: 3
```

### Check Trade Activity
```bash
# See active trades from all bots
sqlite3 bot1_strategy001/tradesv3.dryrun.sqlite "SELECT COUNT(*) FROM trades WHERE is_open=1;"
sqlite3 bot2_strategy004/tradesv3.dryrun.sqlite "SELECT COUNT(*) FROM trades WHERE is_open=1;"
sqlite3 bot3_simplersi/tradesv3.dryrun.sqlite "SELECT COUNT(*) FROM trades WHERE is_open=1;"
```

### View Recent Trades
```bash
# Last 5 trades from Bot 1
sqlite3 bot1_strategy001/tradesv3.dryrun.sqlite \
  "SELECT open_date, close_date, close_profit FROM trades ORDER BY id DESC LIMIT 5;"
```

### Stop All Bots
```bash
# Graceful shutdown
pkill -15 -f freqtrade

# Wait 10 seconds
sleep 10

# Force kill if still running
pkill -9 -f freqtrade
```

### Restart Single Bot
```bash
# Find PID of specific bot
ps aux | grep "bot1_strategy001" | grep -v grep

# Kill that specific PID
kill -9 <PID>

# Restart
cd /root/btc-bot/bot1_strategy001
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
```

---

## Week 2 Monitoring Schedule

### Daily (5-10 minutes)
- Morning: Check Telegram for all 3 bots
- Evening: Run `/profit` on all 3 bots
- Log daily P/L in tracking spreadsheet

### Wednesday (Mid-Week Review - 15 minutes)
- Review 3 days of performance
- Check if strategies behaving as expected
- Make adjustments if critical issues

### Sunday (End of Week - 30 minutes)
- Comprehensive performance analysis
- Compare all 3 strategies
- Select winner for Week 3
- Document lessons learned

---

## Success Criteria

**Deployment Successful If:**
- ✅ All 3 bots start without errors
- ✅ Each bot sends Telegram startup message
- ✅ Each bot has separate database file
- ✅ Logs show "RUNNING" state
- ✅ No crashes in first 4 hours

**Week 2 Successful If:**
- ✅ Collect 60-90 total trades across all bots
- ✅ At least 1 strategy achieves >45% win rate
- ✅ Clear performance winner identified
- ✅ No catastrophic losses (>$100 in a day)

---

## Rollback Procedure

**If deployment fails catastrophically:**

### Option A: Restore Week 1 Setup
```bash
cd /root/btc-bot

# Stop all bots
pkill -9 -f freqtrade

# Restore Week 1 config
cp config.json.week1.backup config.json

# Restore Week 1 database
cp tradesv3.dryrun.sqlite.week1.backup tradesv3.dryrun.sqlite

# Restart single bot
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
```

### Option B: Clean Start
```bash
# Remove all bot directories
rm -rf bot1_strategy001 bot2_strategy004 bot3_simplersi

# Start fresh from this guide
```

---

## Files Created by This Deployment

### Configuration Files
- `/root/btc-bot/bot1_strategy001/config.json`
- `/root/btc-bot/bot2_strategy004/config.json`
- `/root/btc-bot/bot3_simplersi/config.json`

### Database Files
- `/root/btc-bot/bot1_strategy001/tradesv3.dryrun.sqlite`
- `/root/btc-bot/bot2_strategy004/tradesv3.dryrun.sqlite`
- `/root/btc-bot/bot3_simplersi/tradesv3.dryrun.sqlite`

### Log Files
- `/root/btc-bot/bot1_strategy001/freqtrade.log`
- `/root/btc-bot/bot2_strategy004/freqtrade.log`
- `/root/btc-bot/bot3_simplersi/freqtrade.log`

### Helper Scripts
- `/root/btc-bot/check_all_bots.sh`
- `/root/btc-bot/running_bots.txt`

### Backup Files
- `/root/btc-bot/config.json.week1.backup`
- `/root/btc-bot/tradesv3.dryrun.sqlite.week1.backup`
- `/root/btc-bot/freqtrade.log.week1.backup`

---

## Next Steps After Deployment

1. **Monitor for 24 hours** - Ensure no crashes
2. **Check first trades** - Verify strategies behaving correctly
3. **Update tracking spreadsheet** - Log daily performance
4. **Review Wednesday** - Mid-week check-in
5. **Analyze Sunday** - Week 2 comprehensive review

---

## Support & References

- **Main Report:** `WEEK_1_COMMUNITY_STRATEGIES_REPORT.md`
- **Monitoring Guide:** `WEEKLY_MONITORING_GUIDE.md`
- **Original Deployment:** `DEPLOYMENT_SUCCESS_2025_10_07.md`
- **Freqtrade Docs:** https://www.freqtrade.io/en/stable/
- **Telegram Bot Commands:** Send `/help` to any bot

---

**Deployment Guide Version:** 1.0
**Last Updated:** October 13, 2025
**Author:** Claude Code with Subagent Analysis
**Status:** Ready for Execution
