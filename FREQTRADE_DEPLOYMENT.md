# Freqtrade Deployment Guide

## 📋 Quick Start

### Local Development
```bash
# Start the bot locally (dry-run mode)
./start_freqtrade.sh
```

### VPS Deployment
```bash
# Deploy to VPS
./deploy_to_vps_freqtrade.sh
```

## 🏗️ Architecture

### Components:
1. **Freqtrade Bot** - Main trading engine
2. **Strategy Rotator** - Intelligent strategy selection (runs weekly)
3. **Telegram Bot** - Notifications and monitoring
4. **Backup System** - Original bot backed up in `backup_old_bot/`

### Strategies Available:
- **NostalgiaForInfinityX5** - Community-proven momentum strategy
- **SimpleRSI** - RSI oversold/overbought strategy
- **MomentumStrategy** - EMA crossover strategy
- **BollingerMeanReversion** - Mean reversion with Bollinger Bands

## 🔧 Configuration

### Environment Variables (.env):
```bash
BINANCE_KEY=your_binance_api_key
BINANCE_SECRET=your_binance_api_secret
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### config.json:
- **dry_run**: `true` for paper trading, `false` for live
- **max_open_trades**: 3 (conservative)
- **stake_amount**: $100 per trade
- **dry_run_wallet**: $10,000 (paper trading balance)

## 📊 Strategy Rotation

The system automatically selects the best strategy based on:
- **Recent backtest performance** (last 7 days)
- **Win rate** (30% weight)
- **Profit** (40% weight)
- **Sharpe ratio** (20% weight)
- **Max drawdown** (10% penalty)

### Manual Strategy Rotation:
```bash
python strategy_rotator.py
```

### View Rotation History:
```bash
cat user_data/strategy_rotation_log.json
```

## 🤖 Telegram Commands

Once running, use these Telegram commands:
- `/start` - Start the bot
- `/stop` - Stop the bot
- `/status` - Show open trades and performance
- `/profit` - Show profit summary
- `/balance` - Show current balance
- `/daily` - Show daily profit
- `/stats` - Show statistics
- `/performance` - Show performance metrics
- `/reload_config` - Reload configuration

## 📈 Monitoring

### View Live Logs:
```bash
tail -f user_data/logs/freqtrade.log
```

### Check Bot Status:
```bash
# On VPS
ssh root@5.223.55.219
ps aux | grep freqtrade
```

## 🚀 VPS Deployment

### 1. Push to GitHub:
```bash
git add -A
git commit -m "Freqtrade migration complete"
git push origin main
```

### 2. Deploy to VPS:
```bash
ssh root@5.223.55.219
cd /root/btc-bot
git pull origin main
./deploy_vps.sh
```

### 3. Start Bot on VPS:
```bash
# Using systemd (recommended)
sudo systemctl start freqtrade
sudo systemctl enable freqtrade  # Auto-start on reboot

# Or manual start
./start_freqtrade.sh
```

## 🔄 Weekly Rotation Schedule

Strategy rotation runs automatically:
- **Sunday 00:00 UTC** - Backtest all strategies
- **Select best performer** for upcoming week
- **Update config.json** automatically
- **Restart bot** with new strategy

### Cron Job:
```bash
0 0 * * 0 cd /root/btc-bot && python strategy_rotator.py && systemctl restart freqtrade
```

## 📝 Performance Tracking

### Daily Reports (Telegram):
- Hourly updates on performance
- Trade notifications (entry/exit)
- P&L summaries
- Win rate tracking

### Weekly Analysis:
- Strategy rotation report
- Backtest comparison
- Live vs backtest divergence check

## 🛡️ Safety Features

### Circuit Breakers:
- **Max open trades**: 3
- **Max drawdown**: Stops at 20% loss
- **Stoploss**: -1% to -1.5% per trade
- **ROI targets**: 1-2.5% profit targets

### Risk Management:
- Position sizing: $100 per trade
- Total risk: $300 maximum (3 trades)
- Conservative approach during dry-run phase

## 🐛 Troubleshooting

### Bot Not Trading:
```bash
# Check if strategies are loaded
freqtrade list-strategies

# Verify config
python -c "import json; print(json.load(open('config.json'))['strategy'])"

# Test strategy manually
freqtrade backtesting --strategy NostalgiaForInfinityX5 --timeframe 5m
```

### Telegram Not Working:
```bash
# Test Telegram connection
python -c "from telegram import Bot; bot = Bot('YOUR_TOKEN'); print(bot.get_me())"
```

### API Errors:
```bash
# Verify API keys
python update_config_from_env.py
```

## 📚 Resources

- **Freqtrade Docs**: https://www.freqtrade.io/
- **Strategy Database**: https://github.com/freqtrade/freqtrade-strategies
- **Telegram Bot**: @BotFather for bot management
- **VPS Access**: `ssh root@5.223.55.219`

## 🎯 Next Steps

1. **Week 1**: Dry-run validation
   - Monitor backtest vs live divergence
   - Verify Telegram notifications
   - Check strategy rotation

2. **Week 2**: Performance analysis
   - Use performance-analyzer agent
   - Check fee efficiency
   - Validate risk management

3. **Week 3+**: Gradual live deployment
   - Start with $500 (5% of capital)
   - Scale based on performance
   - Monitor with all 8 agents
