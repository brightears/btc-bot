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
- **Status**: ✅ Running Enhanced AI Lab on VPS (5.223.55.219)
- **Version**: v2.1-enhanced-ai-persistent-learning
- **Mode**: Paper Trading with Real Market Data
- **Data Source**: Binance API (Real-time)
- **AI Model**: Gemini 2.5 Flash (Company Account)
- **Learning**: Continuous with Persistent Memory
- **Features**: News Analysis, On-chain Monitoring, Hypothesis Generation
- **Monitoring**: Auto-restart enabled
- **Notifications**: Telegram active (every 2 minutes)
- **Last Update**: January 23, 2025 (API migration, learning persistence)

## Quick Start

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start AI Trading Lab
python ai_trading_lab.py
```

### VPS Management
```bash
# SSH to VPS
ssh root@5.223.55.219

# Check status
python get_status.py

# View logs
tail -f ai_lab.log

# Approve a strategy
python approve_strategy.py STRATEGY_ID

# Enable live trading (requires double confirmation)
python go_live.py

# Emergency stop
python stop_trading.py
```

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

## Support

For issues or questions:
- Check logs: `tail -f ai_lab.log`
- View status: `python get_status.py`
- Emergency stop: `python stop_trading.py`
- Telegram notifications for real-time updates

## License

Proprietary - All rights reserved

---

**Note**: This system is in active development. Always monitor performance and never risk more than you can afford to lose in cryptocurrency trading.