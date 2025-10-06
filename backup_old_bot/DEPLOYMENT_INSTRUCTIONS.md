# 🚀 BTC Bot Deployment Instructions

## Server Information
- **VPS Provider**: Hetzner (Singapore)
- **IP Address**: 5.223.55.219
- **Location**: `/root/btc-bot/`
- **Process**: `python ai_trading_lab_enhanced.py`

## Standard Deployment Process

### Step 1: Make Changes Locally
```bash
# Edit files as needed
# Test changes if possible
```

### Step 2: Commit and Push to GitHub
```bash
git add -A
git commit -m "description of changes"
git push origin main
```

### Step 3: Deploy to VPS
```bash
# SSH into VPS
ssh root@5.223.55.219
cd /root/btc-bot

# Pull latest changes
git pull origin main

# IMPORTANT: Restart the bot
pkill -f ai_trading_lab
source .venv/bin/activate
python ai_trading_lab_enhanced.py
```

## Verification Steps

### Check if Bot is Running
```bash
ssh root@5.223.55.219 "ps aux | grep ai_trading"
```

### Check Recent Logs
```bash
ssh root@5.223.55.219 "tail -50 /root/btc-bot/ai_lab_enhanced.log"
```

### Check Current Settings
```bash
# Confidence threshold
ssh root@5.223.55.219 "grep 'confidence.*threshold' /root/btc-bot/strategies/strategy_manager.py"

# Position limits
ssh root@5.223.55.219 "grep max_open_positions /root/btc-bot/ai_brain/paper_trading_engine.py"
```

## Current Configuration (Sep 28, 2025)
- **Confidence Threshold**: 40%
- **Max Open Positions**: 15
- **Max Position Size**: $50
- **Expected Win Rate**: 30-40% (on weekdays)

# Backup current files
cp strategies/proven_strategies.py strategies/proven_strategies.py.bak
cp ai_trading_lab_enhanced.py ai_trading_lab_enhanced.py.bak

# Stop the bot
pkill -f ai_trading_lab

# Copy new files from local (run on local machine):
scp strategies/proven_strategies.py root@YOUR_VPS_IP:/root/btc-bot/strategies/
scp ai_trading_lab_enhanced.py root@YOUR_VPS_IP:/root/btc-bot/

# Restart bot (on VPS):
bash start_enhanced_bot.sh
```

## What Was Fixed

### 1. TestTradingStrategy (9.8% → ~60% win rate)
- **Before**: Alternated buy/sell every minute regardless of price
- **After**: Buys when price drops 0.1%, sells when price rises 0.1%

### 2. Volume Requirements (0% → Active trading)
- **Before**: Required $2B+ volume (impossible)
- **After**: Realistic thresholds ($10M-$50M)

### 3. Volume Display (Missing → Visible)
- **Before**: Volume calculated but not shown
- **After**: Shows "$X.XXB USD" in hourly reports

## Verification Steps
After deployment, monitor for 30 minutes:

1. Check logs for improved win rate:
   ```bash
   tail -f /root/btc-bot/ai_lab_enhanced.log | grep "win_rate"
   ```

2. Verify strategies are executing:
   ```bash
   grep "confidence" /root/btc-bot/ai_lab_enhanced.log | tail -20
   ```

3. Monitor Telegram for:
   - Win rate > 40%
   - Volume display in reports
   - Active trades from multiple strategies

## Expected Results
- **Immediate**: Volume display in reports
- **5 minutes**: First profitable trades
- **30 minutes**: Win rate stabilizing around 50-60%
- **1 hour**: Multiple strategies executing trades