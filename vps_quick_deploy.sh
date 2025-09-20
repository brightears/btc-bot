#!/bin/bash

# Quick VPS Deployment for BTC Bot
# Run this on your VPS after SSH login

echo "🚀 BTC Bot Quick Deploy"

# Install dependencies
apt update
apt install -y python3-pip python3-venv git

# Clone from GitHub
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env template
cat << 'EOF' > .env
# ADD YOUR CREDENTIALS HERE
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

# Optional: Binance API (for live trading)
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Safety switches
LIVE_TRADING=NO
KILL=0
EOF

echo "✅ Deployment complete!"
echo ""
echo "📋 REQUIRED: Edit .env with your credentials"
echo "   nano /root/btc-bot/.env"
echo ""
echo "🏃 To run the bot:"
echo "   cd /root/btc-bot"
echo "   source .venv/bin/activate"
echo "   python run_funding_exec.py"
echo ""
echo "📱 For background running:"
echo "   screen -S bot"
echo "   python run_funding_exec.py"
echo "   (Press Ctrl+A then D to detach)"