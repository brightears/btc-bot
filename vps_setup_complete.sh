#!/bin/bash

# Complete VPS Setup Script
echo "🚀 Setting up BTC Bot on VPS..."

# Step 1: Clone and setup
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Step 2: Install Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Step 3: Create .env with your credentials
cat << 'EOF' > .env
# Runtime toggles
LIVE_TRADING=NO
KILL=0

# Binance API credentials (add these later for live trading)
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Telegram notifications (YOUR ACTUAL CREDENTIALS)
TELEGRAM_TOKEN=8476508713:AAFhMSVEQ_rgG9qTL-LpVTtFSqDA0DPbzUI
TELEGRAM_CHAT_ID=8352324945
EOF

echo "✅ Setup complete! Bot configured with your Telegram credentials."
echo ""
echo "🏃 To run the bot:"
echo "   cd /root/btc-bot"
echo "   source .venv/bin/activate"
echo "   python run_funding_exec.py"