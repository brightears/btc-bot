# Manual VPS Deployment Instructions

## 🚀 Deploy Freqtrade to Hetzner VPS

Since SSH key access needs to be configured, follow these manual steps:

### Step 1: SSH into VPS
```bash
ssh root@5.223.55.219
# Enter your VPS password when prompted
```

### Step 2: Navigate to Project
```bash
cd /root/btc-bot
```

### Step 3: Pull Latest Code
```bash
git pull origin main
```

### Step 4: Stop Old Bot
```bash
pkill -f ai_trading_lab || true
pkill -f freqtrade || true
```

### Step 5: Setup Freqtrade
```bash
# Create virtual environment if needed
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install Freqtrade and dependencies
pip install --upgrade pip
pip install freqtrade python-dotenv

# Update config from .env
python update_config_from_env.py
```

### Step 6: Run Strategy Rotation
```bash
# This selects the best strategy based on backtests
python strategy_rotator.py
```

### Step 7: Start Freqtrade
```bash
# Option A: Run in foreground (for testing)
freqtrade trade --config config.json

# Option B: Run in background
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &

# Option C: Use screen (recommended)
screen -S freqtrade
freqtrade trade --config config.json
# Press Ctrl+A, then D to detach
# Re-attach with: screen -r freqtrade
```

### Step 8: Verify It's Running
```bash
# Check process
ps aux | grep freqtrade | grep -v grep

# Check logs
tail -f freqtrade.log

# Or if using screen:
screen -r freqtrade
```

## 📱 Verify Telegram

You should receive a startup message in Telegram:
- Bot name: freqtrade_btc
- Status: Running in dry-run mode
- Pair: BTC/USDT
- Strategy: (whichever was selected by rotation)

## 🔧 Troubleshooting

### If Freqtrade won't install:
```bash
# Install TA-Lib dependencies first
apt-get update
apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Then install Freqtrade
pip install freqtrade
```

### If config.json is missing API keys:
```bash
# Manually update config
python update_config_from_env.py

# Or verify .env file exists
cat .env | grep BINANCE_KEY
cat .env | grep TELEGRAM_TOKEN
```

### If no strategies found:
```bash
# List strategies
freqtrade list-strategies

# Download historical data
freqtrade download-data --exchange binance --pairs BTC/USDT --timeframes 5m 15m --days 30
```

## 🔄 Auto-Restart on Reboot (Optional)

Create systemd service:

```bash
# Create service file
cat > /etc/systemd/system/freqtrade.service << 'EOF'
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/btc-bot
Environment="PATH=/root/btc-bot/.venv/bin"
ExecStart=/root/btc-bot/.venv/bin/freqtrade trade --config /root/btc-bot/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable freqtrade
systemctl start freqtrade

# Check status
systemctl status freqtrade

# View logs
journalctl -u freqtrade -f
```

## 📊 Monitoring Commands

```bash
# View live logs
tail -f /root/btc-bot/freqtrade.log

# Check bot status
ps aux | grep freqtrade

# Check trades
freqtrade show-trades --config config.json

# Check performance
freqtrade profit --config config.json
```

## ✅ Deployment Checklist

- [ ] SSH into VPS (root@5.223.55.219)
- [ ] Navigate to /root/btc-bot
- [ ] Git pull latest code
- [ ] Stop old bot (pkill -f ai_trading_lab)
- [ ] Create/activate venv
- [ ] Install Freqtrade
- [ ] Update config from .env
- [ ] Run strategy rotation
- [ ] Start Freqtrade (screen or systemd)
- [ ] Verify process running
- [ ] Check Telegram for startup message
- [ ] Monitor logs for first hour
