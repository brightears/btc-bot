# BTC Funding-Carry Bot

A delta-neutral funding carry strategy bot for BTC on Binance (spot + USDⓈ-M perpetual futures).

## ⚡ Quick Start

```bash
# 1. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run in dry-run mode (default, safe)
python run_funding_exec.py

# 3. Run live (requires both env var AND flag)
# First: export LIVE_TRADING=YES
# Then: python run_funding_exec.py --live
```

## 📊 Strategy Overview

The bot executes a delta-neutral funding carry strategy:
- **Long spot BTC** + **Short perpetual futures BTC**
- Captures funding rate payments (every 8 hours on Binance)
- Enters when: `edge_bps = funding_bps - fees_bps - slippage_bps > threshold`
- Exits at funding window end or kill switch activation

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Copy .env.sample to .env
cp .env.sample .env

# Required for live trading:
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Optional Telegram alerts:
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Safety switches:
LIVE_TRADING=NO  # Must be YES for live
KILL=0           # Set to 1 to stop bot
```

### Config File (config.yaml)
- `symbol`: Trading pair (default: BTC/USDT)
- `notional_usdt`: Position size in USDT (default: 100)
- `threshold_bps`: Minimum edge to enter (default: 0.5)
- `fee_bps`: Trading fees in bps (default: 7)
- `slippage_bps`: Expected slippage (default: 2)

## 🛡️ Safety Features

1. **Dual-gate live trading**: Requires BOTH `LIVE_TRADING=YES` env var AND `--live` flag
2. **Kill switch**: Set `KILL=1` env var or create `.kill` file to stop immediately
3. **Post-only orders**: Uses maker orders to avoid taker fees
4. **Reduce-only on close**: Ensures no accidental position increase
5. **Symbol whitelist**: Only trades approved symbols
6. **Notional caps**: Min/max position size limits
7. **Exchange filters**: Respects tick size, step size, min notional

## 📁 Project Structure

```
btc-bot/
├── src/
│   ├── exchange/      # Binance integration (ccxt)
│   ├── funding/       # Core strategy logic
│   ├── notify/        # Telegram notifications
│   ├── risk/          # Risk management
│   └── utils/         # Logging, time, filters
├── tests/             # Unit tests
├── docs/              # Documentation
├── scripts/           # Monitoring tools
├── config.yaml        # Configuration
├── requirements.txt   # Dependencies
└── run_funding_exec.py # Main entry point
```

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design
- [Funding Carry Strategy](docs/FUNDING_CARRY.md) - Strategy details
- [Dry-Run Guide](docs/RUNBOOK_DRYRUN.md) - Testing guide
- [Go-Live Guide](docs/RUNBOOK_GO_LIVE.md) - Production checklist
- [Security Checklist](docs/SECURITY_CHECKLIST.md) - Security best practices
- [Telegram Setup](docs/TELEGRAM_SETUP.md) - Alert configuration
- [VPS Deployment](docs/DEPLOY_VPS.md) - Server deployment

## 📜 License

Private - Not for distribution
