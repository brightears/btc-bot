# 🧠 PROJECT MEMORY - BTC Trading Bot
*Last Updated: October 2, 2025, 09:00 UTC*

## 🚨 CRITICAL: WHERE THE BOT LIVES
- **PRODUCTION SERVER**: Hetzner VPS at `5.223.55.219` (Singapore, hostname: btc-carry-sg)
- **NOT on DigitalOcean!** (Common confusion - we tried accessing 64.23.206.191 which doesn't exist)
- **Access**: `ssh root@5.223.55.219`
- **Bot Location**: `/root/btc-bot/`
- **Process**: Running as `python3 ai_trading_lab_enhanced.py`

## 📊 CURRENT BOT STATUS (as of Oct 2, 2025)
- **Status**: ✅ RUNNING - All critical bugs FIXED
- **Latest Commit**: 321be75 (equity reporting enhancement)
- **Balance**: $9,999.35 (down $0.65 from $10k initial)
- **Performance**: 0W/6L (building data, confidence fix working)
- **Open Positions**: 0
- **Critical**: Confidence parameter bug fixed, equity reporting working

## ⚙️ CURRENT CONFIGURATION
```python
# Optimized Settings (Oct 1-2, 2025)
confidence_threshold = 72%   # OPTIMAL: Reduced from 85% (was causing 0 trades)
dynamic_adjustment = -3% to +5%  # Based on win rate performance
max_open_positions = 3       # Tight control to prevent overexposure
max_position_size = $100     # Base size with confidence scaling (50-100%)
stop_loss = 1%              # Auto-set 1% below entry on ALL positions
take_profit = 2%            # Auto-set 2% above entry on ALL positions

# Circuit Breaker Active
max_daily_trades = 20       # Hard limit
max_daily_loss = $200       # Trading halts if exceeded
min_trade_interval = 1800   # 30 minutes between trades per strategy (reduced from 60min)
consecutive_loss_halt = 5   # Auto-halt after 5 consecutive losses

# Position Sizing (Confidence-Based)
72-85% confidence → $50 (50% of base)
85-90% confidence → $75 (75% of base)
90%+ confidence → $100 (100% of base)
```

### Why These Settings:
- **72% threshold**: OPTIMAL balance - allows 8-15 trades/day vs 0 at 85%
- **Dynamic adjustments**: Tightens to 77% if win rate <30%, loosens to 69% if >60%
- **3 positions max**: Tight control prevents catastrophic overexposure
- **$50-100 size**: Confidence-scaled to match conviction level
- **Auto stop-losses**: Every position protected with 1% stop-loss
- **Circuit breaker**: Enhanced with consecutive loss protection

## 📈 PERFORMANCE HISTORY

### Phase 1: Initial Disaster (Sep 26-28)
- **Win Rate**: 0.1% (1W/857L)
- **Problem**: Signal constructor parameter order bug + 40% threshold overtrading
- **Losses**: -$794.65 (-7.9%) in 48 hours
- **Root Cause**: Swapped confidence/size parameters, 862 trades in 48h

### Phase 2: Emergency Fixes (Sep 30)
- **Fix Applied**: Correct Signal() parameter order, 85% threshold
- **Result**: Overtrading stopped BUT 0 trades in 10+ hours
- **Issue**: 85% threshold too restrictive, no strategy could reach it
- **Status**: Bot effectively disabled

### Phase 3: Confidence Optimization (Oct 1)
- **Changes**: 72% threshold with dynamic adjustments (-3% to +5%)
- **Result**: Still 0 trades - missing confidence parameter bug discovered
- **Issue**: strategy_manager NOT passing confidence to paper_trader
- **Impact**: Paper trader defaulted to 50%, size_multiplier became 0.0

### Phase 4: Ghost Trades Fixed (Oct 2)
- **Fix Applied**: Pass confidence parameter in execute_trade()
- **Result**: Real trades executing! 3 positions @ $50-75 each
- **Performance**: 0W/6L (early stage, strategies learning)
- **Balance**: $9,999.35 (minimal loss, circuit breaker working)

### Phase 5: Equity Reporting (Oct 2)
- **Enhancement**: Show both cash balance and total equity
- **Fix**: Implement get_current_equity() with unrealized P&L
- **Benefit**: Users see total account value, not just cash
- **Status**: Deployed and monitoring

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

## 🐛 CRITICAL BUGS FIXED

### Bug 1: Signal Constructor Parameter Swap ✅ FIXED (Sep 30)
- **Problem**: All strategies calling Signal(action, size, confidence, reason)
- **Correct Order**: Signal(action, confidence, size, reason)
- **Impact**: 862 trades in 48h, 0.1% win rate
- **Fix**: strategies/proven_strategies.py lines 81, 192, 292, 423, 600, 751, 906

### Bug 2: Missing Confidence Parameter ✅ FIXED (Oct 2)
- **Problem**: strategy_manager NOT passing confidence to paper_trader
- **Impact**: $0 ghost trades, balance frozen
- **Fix**: Added 'confidence': signal.confidence at line 459
- **Commit**: 2ae3944

### Bug 3: Division by Zero Errors ✅ FIXED (Oct 2)
- **Problem**: Win rate, P&L calculations dividing by zero
- **Impact**: Hundreds of errors, bot crashes
- **Fix**: Added safe division with zero checks
- **Commit**: a951dac

### Bug 4: Stale Balance Reporting ✅ FIXED (Oct 2)
- **Problem**: Telegram showing cash only, not total account value
- **Impact**: Looked like money lost when just invested
- **Fix**: Implemented get_current_equity() with unrealized P&L
- **Commit**: 321be75

## 🐛 KNOWN LIMITATIONS

### Limitation 1: Early Stage Performance
- **Current**: 0W/6L (strategies still learning)
- **Expected**: 45-55% win rate after 50+ trades
- **Action**: Continue monitoring, no changes needed yet

### Limitation 2: Weekend vs Weekday Volume
- **Weekend**: $0.6B-1.5B volume (lower signal quality)
- **Weekday**: $2B-3B volume (better opportunities)
- **Impact**: Fewer trades on weekends (expected)

## 📱 TELEGRAM MONITORING
- **Bot**: @btc_carry_alerts_bot
- **Reports**: Every hour
- **Key Metrics**: Win rate, P&L, Open positions

## 🎯 NEXT STEPS

### Immediate (Next 24 Hours)
1. **Monitor First 10 Trades**
   - Verify confidence >72% on all executions
   - Confirm position sizes are $50-100 (not $0)
   - Check stop-losses set automatically
   - Watch for circuit breaker triggers

2. **Telegram Monitoring**
   - Hourly reports should show Cash Balance + Total Equity
   - Expected: 8-15 trades per day
   - Watch for 45-55% win rate emerging

### This Week
1. **Performance Validation**
   - Track win rate trend (target: 40-50% after 50 trades)
   - Monitor fee efficiency (<20% of gross P&L)
   - Verify circuit breaker prevents overtrading
   - Ensure all positions have stop-losses

2. **Possible Optimizations**
   - If win rate >60%: Lower threshold to 69% (dynamic adjustment)
   - If win rate <30%: Raise threshold to 77% (dynamic adjustment)
   - Consider per-strategy thresholds if some underperform

### Quick Status Check
```bash
# Is bot running?
ssh root@5.223.55.219 "ps aux | grep ai_trading_lab_enhanced | grep -v grep"

# Check current balance and performance
ssh root@5.223.55.219 "cat /root/btc-bot/knowledge/paper_trading_state.json | python3 -m json.tool | head -30"

# Verify latest commit
ssh root@5.223.55.219 "cd /root/btc-bot && git log --oneline -5"

# Check recent trades
ssh root@5.223.55.219 "tail -200 /root/btc-bot/ai_lab_enhanced.log | grep -E '(Trade executed|EXECUTING|Balance)'"
```

## 📝 IMPORTANT REMINDERS

1. **ALWAYS sync all three locations** (Local, GitHub, VPS)
2. **ALWAYS restart bot after changes** on VPS (pkill -f ai_trading_lab_enhanced)
3. **Current threshold is 72%** with dynamic adjustments (-3% to +5%)
4. **The bot is on HETZNER** (5.223.55.219) not DigitalOcean
5. **Use python3** not python (python doesn't exist on VPS)
6. **All critical bugs are FIXED** - confidence parameter, division by zero, equity reporting
7. **Expected trade frequency**: 8-15 trades per day (not 862 like before!)

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

1. **Parameter order matters** - Signal(action, confidence, size, reason) NOT (action, size, confidence, reason)
2. **Always pass parameters explicitly** - Don't rely on defaults (confidence parameter bug)
3. **Threshold is critical** - 40% = overtrading, 85% = no trades, 72% = optimal
4. **Show total value** - Users need to see equity (cash + positions), not just cash
5. **Circuit breakers are essential** - Prevent catastrophic overtrading
6. **Division by zero everywhere** - Always check denominators before dividing
7. **Test changes thoroughly** - Bot needs restart, verify on VPS, check logs
8. **Document everything** - Critical for debugging and knowledge continuity
9. **Use subagents** - trading-strategy-debugger caught issues humans missed

## 📚 KEY FILES TO READ

1. **EMERGENCY_FIX_REPORT.md** - Sep 30 catastrophe and fixes
2. **CONFIDENCE_OPTIMIZATION_REPORT.md** - Oct 1 threshold analysis
3. **checkpoint_2025_10_02.md** - Today's work and bug fixes
4. **deployment_instructions.md** - How to deploy to VPS
5. **.claude/agents/** - Subagent definitions for debugging

---
*Use this file to quickly get back up to speed when returning to the project.*