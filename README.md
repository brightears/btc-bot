# BTC Funding Carry Bot 🤖

Production-ready bot for executing delta-neutral funding carry strategies on Binance. Currently monitoring in dry-run mode.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/brightears/btc-bot.git
cd btc-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure (copy .env.sample and add your credentials)
cp .env.sample .env
nano .env

# Run in dry-run mode (default)
python run_funding_exec.py

# Monitor with dashboard
python monitor.py

# Run Telegram command bot
python telegram_bot.py
```

## 📊 Current Status

- **Mode**: DRY-RUN (Paper Trading)
- **Strategy**: Delta-neutral BTC funding carry
- **Exchange**: Binance USDⓈ-M Futures
- **Monitoring**: 24/7 on Hetzner VPS (Singapore)

## 🎮 Control Commands

### Telegram Bot Commands
```
/status   - Current position and bot status
/metrics  - Performance metrics
/pause    - Pause new position opening
/resume   - Resume operations
/stop     - Emergency stop (creates kill file)
/help     - Show available commands
```

### Terminal Monitoring
```bash
# Real-time dashboard
python monitor.py

# Check logs
tail -f logs/funding_exec.log

# View current state
cat logs/state.json | jq

# Check metrics
cat logs/metrics.json | jq
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Binance API (for live trading)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Telegram notifications
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Safety gate for live trading
LIVE_TRADING=NO  # Must be YES for live trading
```

### Strategy Parameters
```bash
# Run with custom settings
python run_funding_exec.py \
  --notional_usdt 500 \     # Position size in USDT
  --threshold_bps 0.5 \      # Min edge to enter (basis points)
  --max_position_usdt 5000 \ # Max total exposure
  --loop_seconds 300          # Check interval (5 minutes)
```

## 📈 How It Works

1. **Monitor Funding Rates**: Checks BTC perpetual funding every 5 minutes
2. **Calculate Edge**: `funding_rate - fees - slippage`
3. **Open Position**: When edge > 0.5 bps:
   - Long spot BTC
   - Short equal USDⓈ-M futures
4. **Collect Funding**: Every 8 hours (00:00, 08:00, 16:00 UTC)
5. **Close Position**: When edge becomes negative

### Risk Management
- **Delta-neutral**: No directional market risk
- **Position limits**: Max exposure caps
- **Double-gate safety**: Requires env var AND CLI flag for live
- **Emergency stop**: Kill file immediately closes positions
- **Dry-run default**: Always starts in simulation mode

## 🚢 VPS Deployment

### Current Setup
- **Server**: Hetzner Cloud (Singapore)
- **IP**: 5.223.55.219
- **Processes**:
  - Main bot: `screen -r btc-bot`
  - Telegram bot: `screen -r telegram-bot`

### Deploy Updates
```bash
# Push to GitHub
git add .
git commit -m "Update"
git push

# On VPS
ssh root@5.223.55.219
cd /root/btc-bot
git pull
source venv/bin/activate
pip install -r requirements.txt

# Restart services
screen -S btc-bot -X quit
screen -S telegram-bot -X quit
screen -dmS btc-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python run_funding_exec.py'
screen -dmS telegram-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python telegram_bot.py'
```

## 📊 Performance Tracking

### Metrics Collected
- Total trades executed
- Win rate percentage
- Total P&L (profit/loss)
- Total funding collected
- Average funding per trade
- Best/worst trade P&L

### State Persistence
- `logs/state.json` - Current position and bot state
- `logs/metrics.json` - Cumulative performance metrics
- `logs/funding_exec.log` - Detailed execution logs

## 🛡️ Safety Features

1. **Dry-Run Default**: Always starts in paper trading mode
2. **Double-Gate Live**: Needs `LIVE_TRADING=YES` + `--live` flag
3. **Kill Switch**: Touch `.kill` file for emergency stop
4. **Pause/Resume**: Control via Telegram commands
5. **Position Limits**: Configurable max exposure
6. **Balance Checks**: Ensures sufficient funds before trading
7. **Exchange Compliance**: Respects tick size, step size, min notional

## 📚 Documentation

- **[Strategy Guide](docs/FUNDING_CARRY.md)** - Understanding funding carry
- **[Operations Manual](docs/RUNBOOK_DRYRUN.md)** - Daily operations
- **[Going Live Checklist](docs/RUNBOOK_GO_LIVE.md)** - Production preparation
- **[Configuration Reference](docs/CONFIG_REFERENCE.md)** - All settings
- **[Security Guidelines](docs/SECURITY_CHECKLIST.md)** - Best practices
- **[Architecture](docs/ARCHITECTURE.md)** - System design

## 🎯 Next Steps

### Phase 1: Dry-Run (Current)
- [x] Deploy to VPS
- [x] Setup monitoring
- [x] Enable Telegram commands
- [ ] Run for 48-72 hours
- [ ] Collect performance metrics
- [ ] Analyze trading decisions

### Phase 2: Evaluation
- [ ] Review dry-run results
- [ ] Calculate expected returns
- [ ] Verify risk controls
- [ ] Test emergency procedures

### Phase 3: Go Live (Optional)
- [ ] Add Binance API keys
- [ ] Enable `LIVE_TRADING=YES`
- [ ] Start with small position
- [ ] Monitor closely for 24 hours
- [ ] Scale up gradually

## 🤝 Support

For issues or questions:
1. Check the [documentation](docs/)
2. Review [logs](logs/) for errors
3. Use Telegram `/help` command
4. Check bot status with `/status`

## ⚠️ Disclaimer

This bot is for educational purposes. Cryptocurrency trading carries risk. Always test thoroughly in dry-run mode before using real funds. The authors are not responsible for any financial losses.

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details