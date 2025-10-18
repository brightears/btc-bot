# AI Trading Lab - Intelligent Cryptocurrency Trading System

## Overview

The AI Trading Lab is an advanced, self-learning cryptocurrency trading system that combines delta-neutral funding carry strategies with artificial intelligence to continuously discover, test, and optimize trading opportunities. Currently deployed and running 24/7 on VPS.

### Key Features

- **AI-Powered Strategy Generation**: Continuously generates and tests new trading hypotheses
- **Self-Learning System**: Learns from market patterns and improves over time
- **Persistent Memory**: Maintains learning across restarts (strategies.json, experience_replay.pkl)
- **Real Market Data**: Uses live Binance data - NO simulated/fake data
- **Paper Trading**: Realistic simulation with actual market prices and fees
- **Data Integrity Validation**: Prevents AI hallucination by validating all data
- **Enhanced AI Intelligence**: Gemini 2.5 Flash LLM, news monitoring, on-chain analysis
- **Backtesting Infrastructure**: Historical data analysis for strategy validation
- **Experience Replay Buffer**: Deep reinforcement learning with 10,000 capacity buffer
- **Market Regime Detection**: Identifies Bull/Bear/Ranging/Volatile markets
- **Sentiment Correlation**: Learns news impact on price movements
- **Parallel Strategy Testing**: Tests multiple strategies simultaneously in dry-run mode
- **Delta-Neutral Funding Carry**: Core strategy using long spot + short perpetual positions
- **24/7 VPS Operation**: Runs continuously with auto-restart monitoring
- **Telegram Integration**: Real-time updates every 2 minutes
- **48-Hour Validation**: Paper trades before recommending live trading
- **Double-Gated Safety**: Dry-run by default with manual approval for live trading

## System Status

**Current Deployment:**
- **Status**: ✅ Running Freqtrade 2025.6 on Hetzner VPS (5.223.55.219, btc-carry-sg)
- **Framework**: Freqtrade (migrated from custom bot on Oct 7, 2025)
- **Mode**: Dry-run (Paper Trading)
- **Architecture**: 6-bot parallel testing (3 BTC + 3 PAXG gold)
- **Active Strategies**:
  - **BTC Bots** (Bitcoin Trading):
    - **Bot 1**: Strategy001 (Trend following, optimized) - $3,000
    - **Bot 2**: Strategy004 (Hybrid multi-indicator, optimized) - $3,000
    - **Bot 3**: SimpleRSI (Mean reversion, original params) - $3,000
  - **PAXG Bots** (Gold Trading - NEW Oct 14):
    - **Bot 4**: Strategy004 Baseline (PAXG/USDT) - $3,000
    - **Bot 5**: Strategy004 Optimized (PAXG/USDT, gold-tuned) ⭐ - $3,000
    - **Bot 6**: Strategy001 (PAXG/USDT, comparison) - $3,000
- **Trading Pairs**: BTC/USDT (Bots 1-3), PAXG/USDT (Bots 4-6)
- **Virtual Capital**: $18,000 USDT total ($9K BTC + $9K PAXG)
- **Exchange**: Binance (via CCXT 4.5.7)
- **Notifications**: All Telegram disabled (analysis via databases)
- **Monitoring**: Zombie detection active, Telegram alerts for crashes
- **API Ports**: 8080-8085 (unique per bot, fixes applied Oct 18)
- **Memory**: 2GB swap active + optimized configs (132 MB available)
- **Last Update**: October 18, 2025, 12:00 PM UTC (Zombie crashes fixed, trade frequency improved)

**Week 1 Performance (Oct 7-13):**
- **Trades**: 15 total
- **Win Rate**: 33.33%
- **P&L**: -$12.81 (includes -$11.96 loss from Oct 10 Bitcoin crash)
- **Strategy**: SimpleRSI (single bot)
- **Analysis**: See [WEEK_1_COMMUNITY_STRATEGIES_REPORT.md](WEEK_1_COMMUNITY_STRATEGIES_REPORT.md)

**Current Trading Configuration (Per Bot):**
- **Max Open Trades**: 1 per bot (6 total system-wide)
- **Stake per Trade**: $100 USDT
- **Minimum ROI**: Varies by strategy
  - BTC bots: 1-3% (optimized for volatility)
  - PAXG Bot 4: 1-3% (baseline)
  - PAXG Bot 5: 2-7% (gold-optimized, wider targets)
  - PAXG Bot 6: 1-3% (baseline)
- **Stop-loss**:
  - BTC: -6% (Strategy001, Strategy004), -10% (SimpleRSI)
  - PAXG Bot 4/6: -6%, PAXG Bot 5: -4% (gold-tuned)
- **Trailing Stops**: Bot 5 only (gold-optimized)
- **Timeframe**: 5m (all bots)
- **Position Adjustment**: Off
- **Order Types**: Limit orders (entry/exit)
- **Balance per Bot**: $3,000 USDT (dry-run wallet)

## System Requirements

### VPS Specifications (Minimum)

**For 6-bot deployment:**
- **CPU**: 2 vCPU (shared)
- **RAM**: 2GB minimum + 2GB swap (4GB RAM recommended)
- **Disk**: 20GB SSD
- **Bandwidth**: 20TB/month
- **Cost**: €4-5/month (2GB) or €8-10/month (4GB recommended)

**Memory Breakdown:**
- Bot1-3 (BTC): ~100-150 MB each = 450 MB
- Bot4-6 (PAXG): ~280-300 MB each = 850 MB
- System + overhead: ~300 MB
- **Total**: ~1.6 GB used, 380 MB available

**Critical Setup:**
- ⚠️ **Swap space REQUIRED** if using 2GB RAM (prevents OOM kills)
- ✅ **Memory optimization** enabled in all bot configs
- ✅ **Monitoring system** tracks memory and alerts on low availability

See [MONITORING_SYSTEM.md](MONITORING_SYSTEM.md) for memory issue resolution details.

---

## Quick Start

### New VPS Deployment (Hetzner Cloud)

**Complete deployment guide**: See [DEPLOYMENT_SUCCESS_2025_10_07.md](DEPLOYMENT_SUCCESS_2025_10_07.md)

**Quick deployment:**
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/hetzner_btc_bot -C "btc-bot-vps"

# 2. Use rescue mode to add SSH key (if locked out)
# See DEPLOYMENT_SUCCESS_2025_10_07.md for rescue mode procedure

# 3. Deploy Freqtrade (once SSH works)
ssh -i ~/.ssh/hetzner_btc_bot root@YOUR_VPS_IP
cd /root && git clone https://github.com/brightears/btc-bot.git
cd btc-bot
# Follow deployment steps in DEPLOYMENT_SUCCESS_2025_10_07.md
```

### VPS Management (Freqtrade)
```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219

# Check bot status
ps aux | grep freqtrade
tail -f /root/btc-bot/freqtrade.log

# Start/Stop bot
cd /root/btc-bot
source .venv/bin/activate

# Start
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &

# Stop
pkill -f freqtrade

# Run strategy rotation
python strategy_rotator.py

# Update config from .env
python update_config_from_env.py
```

### Telegram Commands
Once the bot is running, use these commands in Telegram:
- `/status` - Current open trades
- `/profit` - Profit/loss summary
- `/balance` - Wallet balance
- `/daily` - Daily statistics
- `/help` - All available commands

## Architecture

### Core Components

1. **AI Brain** (`ai_brain/`)
   - `learning_engine.py`: Pattern recognition and market analysis
   - `hypothesis_generator.py`: Creates innovative trading strategies
   - `strategy_evaluator.py`: Evaluates strategy performance

2. **Trading Execution** (`src/`)
   - `funding/executor.py`: Executes funding carry trades
   - `exchange/binance.py`: Exchange integration via CCXT
   - `risk/guards.py`: Risk management and safety checks

3. **Management Scripts**
   - `ai_trading_lab.py`: Main AI system with notifications
   - `get_status.py`: Check current system state
   - `approve_strategy.py`: Approve strategies for live trading
   - `go_live.py`: Enable live trading mode
   - `stop_trading.py`: Emergency stop
   - `monitor_bot.sh`: VPS monitoring and auto-restart

## Trading Strategies

### Active Strategies

1. **Delta-Neutral Funding Carry**
   - Long spot BTC + Short BTC perpetual futures
   - Captures funding rate differential
   - Market-neutral position

2. **AI-Generated Strategies** (Testing)
   - Pattern-based strategies from market analysis
   - Hypothesis-driven experimental strategies
   - Creative "crazy ideas" for edge discovery

## Safety Features

### Multi-Layer Protection

1. **Dry-Run Default**: All strategies test in simulation first
2. **Manual Approval**: Strategies require explicit approval
3. **Double-Gated Live Trading**: Two confirmations needed
4. **Position Limits**: Max position size constraints
5. **Emergency Stop**: Instant shutdown capability
6. **Risk Guards**: Continuous monitoring and limits

## Monitoring

### Telegram Notifications

- **Hourly Reports**: Strategy performance and market analysis
- **6-Hour Heartbeat**: System health confirmation
- **Action Alerts**: When manual intervention needed
- **Strategy Discoveries**: New promising strategies found

### Logs and Metrics

```bash
# View main log
tail -f ai_lab.log

# Check strategy performance
cat strategies/performance_log.json

# Monitor system metrics
python get_status.py
```

## Configuration

### Environment Variables (.env)

```bash
# Exchange API
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=True

# Telegram
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Safety Gates
LIVE_TRADING_ENABLED=false
LIVE_TRADE_REQUIRE_DOUBLE_CHECK=true
MAX_POSITION_SIZE_USDT=1000
```

## Development

### Project Structure

```
btc-bot/
├── ai_brain/              # AI components
│   ├── learning_engine.py
│   ├── hypothesis_generator.py
│   └── strategy_evaluator.py
├── src/                   # Core trading logic
│   ├── exchange/         # Exchange integration
│   ├── funding/          # Funding carry execution
│   └── risk/             # Risk management
├── strategies/           # Strategy storage
├── ai_trading_lab.py     # Main AI system
├── monitor_bot.sh        # VPS monitoring
└── management_scripts/   # Control scripts
```

### Testing

```bash
# Run tests
pytest tests/ -v

# Test specific component
pytest tests/test_ai_brain.py -v

# Dry-run testing
python ai_trading_lab.py --dry-run
```

## Management Commands

### Control Scripts

- **get_status.py** - Check system status and active strategies
- **approve_strategy.py** - Approve AI-generated strategies for live testing
- **go_live.py** - Enable live trading (requires double confirmation)
- **stop_trading.py** - Emergency stop all trading
- **send_test_notification.py** - Test Telegram connectivity

### Monitoring

- **monitor_bot.sh** - Auto-restart script for VPS
- **ai_lab.log** - Main system log file
- **strategies/performance_log.json** - Strategy performance metrics

## Roadmap

### Phase 1: Foundation ✅
- Basic funding carry bot
- Telegram notifications
- Safety gates and controls

### Phase 2: AI Integration ✅
- Learning engine
- Pattern recognition
- Hypothesis generation

### Phase 3: VPS Deployment ✅
- Automated deployment
- 24/7 operation
- Remote management

### Phase 4: Advanced Learning (Current)
- Deep reinforcement learning
- Multi-market correlation
- Cross-strategy optimization

### Phase 5: Scaling (Planned)
- Multiple exchange support
- Portfolio-level optimization
- Distributed strategy testing

## VPS Deployment

### Current Infrastructure

- **Server**: Hetzner Cloud (Singapore)
- **IP**: 5.223.55.219
- **GitHub**: https://github.com/brightears/btc-bot.git

### Deployment Process

```bash
# Push updates to GitHub
git add .
git commit -m "Update AI Trading Lab"
git push origin main

# On VPS - Pull and restart
ssh root@5.223.55.219
cd /root/btc-bot
git pull
python3 -m pip install -r requirements.txt

# Restart AI Lab (auto-restart handles this)
pkill -f ai_trading_lab
# monitor_bot.sh will auto-restart
```

## Documentation

### Key Documentation Files

**Deployment & Setup:**
- [DEPLOYMENT_SUCCESS_2025_10_07.md](DEPLOYMENT_SUCCESS_2025_10_07.md) - Full deployment story and setup guide
- [MULTI_BOT_DEPLOYMENT_GUIDE.md](MULTI_BOT_DEPLOYMENT_GUIDE.md) - Step-by-step multi-bot deployment instructions

**Monitoring & Management:**
- [MONITORING_SYSTEM.md](MONITORING_SYSTEM.md) - **NEW**: Auto-restart monitoring (Oct 14, 2025)
- [WEEKLY_MONITORING_GUIDE.md](WEEKLY_MONITORING_GUIDE.md) - Daily/weekly monitoring procedures
- [WEEK_1_COMMUNITY_STRATEGIES_REPORT.md](WEEK_1_COMMUNITY_STRATEGIES_REPORT.md) - Week 1 BTC analysis
- [PAXG_DEPLOYMENT_REPORT.md](PAXG_DEPLOYMENT_REPORT.md) - Gold trading deployment (Oct 14, 2025)

**Project History:**
- [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Why we migrated to Freqtrade
- [README.md](README.md) - This file (project overview)

## Support

For issues or questions:
- Check logs: `tail -f freqtrade.log` (on VPS)
- View bot status: `ps aux | grep freqtrade`
- Telegram commands: `/status`, `/profit`, `/help`
- Emergency stop: `pkill -f freqtrade`

## License

Proprietary - All rights reserved

---

**Note**: This system is in active development. Always monitor performance and never risk more than you can afford to lose in cryptocurrency trading.