#!/bin/bash

# Freqtrade VPS Deployment Script
# Deploys to Hetzner VPS at 5.223.55.219

set -e  # Exit on error

VPS_HOST="root@5.223.55.219"
VPS_DIR="/root/btc-bot"

echo "🚀 Deploying Freqtrade to VPS..."

# Step 1: Commit and push changes
echo "📝 Committing changes to git..."
git add -A
git commit -m "Freqtrade deployment $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"
git push origin main

# Step 2: Deploy to VPS
echo "📦 Deploying to VPS..."
ssh $VPS_HOST << 'EOF'
    cd /root/btc-bot

    # Pull latest code
    echo "⬇️  Pulling latest code..."
    git pull origin main

    # Stop existing bot
    echo "🛑 Stopping existing bot..."
    pkill -f freqtrade || true
    sleep 2

    # Create virtual environment if not exists
    if [ ! -d ".venv" ]; then
        echo "🐍 Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Activate venv and install/update Freqtrade
    source .venv/bin/activate

    echo "📥 Installing/updating Freqtrade..."
    pip install --upgrade pip
    pip install freqtrade python-dotenv

    # Update config from .env
    echo "⚙️  Updating configuration..."
    python update_config_from_env.py

    # Run strategy rotation
    echo "🔄 Running strategy rotation..."
    python strategy_rotator.py || echo "Strategy rotation failed, using default"

    # Start Freqtrade in background
    echo "🚀 Starting Freqtrade..."
    nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &

    echo "✅ Deployment complete!"
    echo "📊 Bot is running in dry-run mode"

    # Show status
    sleep 2
    ps aux | grep freqtrade | grep -v grep
EOF

echo ""
echo "✨ Deployment successful!"
echo ""
echo "📱 Next steps:"
echo "   1. Check Telegram for startup message"
echo "   2. Monitor: ssh $VPS_HOST 'tail -f /root/btc-bot/freqtrade.log'"
echo "   3. Check status: ssh $VPS_HOST 'ps aux | grep freqtrade'"
echo ""
echo "🔗 VPS: ssh $VPS_HOST"
