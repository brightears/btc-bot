# 🧠 PROJECT MEMORY - BTC Trading Bot
*Last Updated: September 28, 2025, 02:50 UTC*

## 🚨 CRITICAL: WHERE THE BOT LIVES
- **PRODUCTION SERVER**: Hetzner VPS at `5.223.55.219` (Singapore)
- **NOT on DigitalOcean!** (Common confusion - we tried accessing 64.23.206.191 which doesn't exist)
- **Access**: `ssh root@5.223.55.219`
- **Bot Location**: `/root/btc-bot/`
- **Process**: Running as `python ai_trading_lab_enhanced.py`

## 📊 CURRENT BOT STATUS (as of Sep 30, 2025)
- **Status**: ✅ RUNNING on VPS with EMERGENCY FIXES APPLIED
- **Uptime**: Restarted at 15:16 UTC (Sep 30)
- **Performance**: Emergency fixes deployed - monitoring initial trades
- **Critical**: All major bugs fixed, expecting 45-55% win rate

## ⚙️ CURRENT CONFIGURATION
```python
# Emergency Fix Settings (Sep 30)
confidence_threshold = 85%   # CRITICAL: Raised from 40% to prevent overtrading
max_open_positions = 3       # Reduced from 15 to control exposure
max_position_size = $100     # Base size with confidence scaling (50-100%)
stop_loss = 1%              # Auto-set 1% below entry on ALL positions
take_profit = 2%            # Auto-set 2% above entry on ALL positions

# Circuit Breaker Active
max_daily_trades = 20       # Hard limit (was 862 trades in 48h!)
max_daily_loss = $200       # Trading halts if exceeded
min_trade_interval = 3600   # 1 hour between trades per strategy
```

### Why These Settings:
- **85% threshold**: CRITICAL - Only highest conviction trades to prevent overtrading
- **3 positions max**: Tight control prevents catastrophic overexposure
- **$50-100 size**: Confidence-scaled to match conviction level
- **Auto stop-losses**: Every position protected with 1% stop-loss
- **Circuit breaker**: Hard limits prevent runaway trading disasters

## 📈 PERFORMANCE HISTORY

### Phase 1: Initial Disaster (Sep 26)
- **Win Rate**: 7-9%
- **Problem**: TestTradingStrategy alternating buy/sell every minute
- **Losses**: -$65+ in paper trading

### Phase 2: First Fix (Sep 26-27)
- **Fix Applied**: TestTradingStrategy now buys dips/sells rips
- **Win Rate**: Improved to 28-44%
- **Issue**: Too many positions (90+), high fees ($100+)

### Phase 3: Over-Optimization (Sep 27)
- **Changes**: 50% threshold, 15 position limit
- **Result**: 0% win rate - threshold too high for weekend
- **Problem**: Bot wasn't properly restarted with new code

### Phase 4: Current State (Sep 28)
- **Settings**: 40% threshold, 15 positions, $50 max
- **Status**: Bot properly restarted with optimizations
- **Expected**: Recovery in progress, better on Monday

## 🔄 DEPLOYMENT PROCESS (IMPORTANT!)

### The Three-Location Sync:
1. **Local** → Make changes
2. **GitHub** → Push changes
3. **VPS** → Pull & restart bot

### Commands for Deployment:
```bash
# Local
git add -A
git commit -m "your message"
git push origin main

# On VPS
ssh root@5.223.55.219
cd /root/btc-bot
git pull origin main
pkill -f ai_trading_lab
source .venv/bin/activate
python ai_trading_lab_enhanced.py
```

## 🐛 KNOWN ISSUES & SOLUTIONS

### Issue 1: Weekend Low Volume
- **Problem**: Volume drops to $0.6B on weekends (vs $2B+ weekdays)
- **Solution**: Lower confidence threshold to 40% for weekends

### Issue 2: All Strategies Show 0% Win Rate
- **Cause**: Bot running old code (not restarted after deployment)
- **Solution**: Always restart bot after pulling changes!

### Issue 3: Can't SSH to VPS
- **Wrong IP**: 64.23.206.191 (doesn't exist)
- **Correct IP**: 5.223.55.219 (Hetzner Singapore)

## 📱 TELEGRAM MONITORING
- **Bot**: @btc_carry_alerts_bot
- **Reports**: Every hour
- **Key Metrics**: Win rate, P&L, Open positions

## 🎯 NEXT STEPS (Monday, Sep 29)

1. **Monitor Monday Performance**
   - Volume should increase to $2B+
   - Win rate should improve to 30-40%+
   - Watch for profitability

2. **Possible Adjustments**
   - If volume is high, could increase threshold to 45%
   - If still not profitable, reduce position size to $30
   - Consider enabling only best-performing strategies

3. **Check These First**:
   ```bash
   # Is bot running?
   ssh root@5.223.55.219 "ps aux | grep ai_trading"

   # Check recent performance
   ssh root@5.223.55.219 "tail -100 /root/btc-bot/ai_lab_enhanced.log | grep win_rate"

   # Verify settings
   ssh root@5.223.55.219 "grep threshold /root/btc-bot/strategies/strategy_manager.py"
   ```

## 📝 IMPORTANT REMINDERS

1. **ALWAYS sync all three locations** (Local, GitHub, VPS)
2. **ALWAYS restart bot after changes** on VPS
3. **Weekend volume is LOW** - don't panic about poor weekend performance
4. **The bot is on HETZNER** not DigitalOcean
5. **Current threshold is 40%** not 35% or 50%

## 🔧 QUICK TROUBLESHOOTING

### Bot Not Trading?
1. Check if running: `ps aux | grep ai_trading`
2. Check confidence threshold in logs
3. Check market volume (might be too low)
4. Verify bot has latest code (git pull)

### Poor Performance?
1. Check win rate trend (improving or declining?)
2. Check position count (should be ≤15)
3. Check fees (should be <$0.50 per trade)
4. Wait for Monday volume

### Can't Connect?
- Use: `ssh root@5.223.55.219`
- NOT: `ssh root@64.23.206.191`

## 💡 LESSONS LEARNED

1. **Test changes properly** - Bot needs restart to load new code
2. **Consider market conditions** - Weekend vs weekday volume matters
3. **Balance is key** - Too strict = no trades, too loose = bad trades
4. **Monitor continuously** - Use Telegram alerts to catch issues early
5. **Document everything** - This file exists because we kept forgetting details!

---
*Use this file to quickly get back up to speed when returning to the project.*