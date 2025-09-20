#!/bin/bash

# VPS Deployment Script for BTC Funding-Carry Bot
# Run this on your VPS after SSH login

set -e  # Exit on error

echo "🚀 Starting BTC Bot VPS Deployment..."

# Step 1: Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Step 2: Install Python and dependencies
echo "🐍 Installing Python and required packages..."
apt install -y python3-pip python3-venv git screen

# Step 3: Clone repository
echo "📂 Cloning repository..."
cd /root
if [ -d "btc-bot" ]; then
    echo "Repository already exists, pulling latest..."
    cd btc-bot
    git pull
else
    git clone https://github.com/yourusername/btc-bot.git
    cd btc-bot
fi

# Step 4: Set up Python environment
echo "🔧 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Create .env file
echo "📝 Creating .env file..."
cat << 'EOF' > .env
# Binance API Credentials
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Telegram Bot Configuration
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

# Live Trading Safety
LIVE_TRADING=NO

# Kill Switch
KILL=0
EOF

echo "⚠️  IMPORTANT: Edit .env file with your credentials!"
echo "Run: nano /root/btc-bot/.env"

# Step 6: Create systemd service
echo "⚙️ Creating systemd service..."
cat << 'EOF' > /etc/systemd/system/btc-bot.service
[Unit]
Description=BTC Funding-Carry Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/btc-bot
Environment="PATH=/root/btc-bot/.venv/bin"
ExecStart=/root/btc-bot/.venv/bin/python /root/btc-bot/run_funding_exec.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Enable service
echo "🔄 Enabling systemd service..."
systemctl daemon-reload
systemctl enable btc-bot

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file: nano /root/btc-bot/.env"
echo "2. Add your TELEGRAM_TOKEN and TELEGRAM_CHAT_ID"
echo "3. Add Binance API keys (for live trading)"
echo "4. Start the bot: systemctl start btc-bot"
echo "5. Check status: systemctl status btc-bot"
echo "6. View logs: journalctl -u btc-bot -f"
echo ""
echo "🛡️ The bot will run in DRY-RUN mode by default for safety."