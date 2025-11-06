#!/bin/bash
# Deploy LLM Enhancement to VPS

echo "🚀 Deploying LLM Enhancement to VPS..."
echo "=================================="

# SSH to VPS and update
ssh root@5.223.55.219 << 'ENDSSH'
cd /root/btc-bot

# Pull latest code
echo "📦 Pulling latest code..."
git pull

# Install new dependencies
echo "📚 Installing dependencies..."
pip3 install google-generativeai feedparser aiohttp

# Create cache directory
mkdir -p cache/news

# Check if GEMINI_API_KEY is set
if grep -q "GEMINI_API_KEY" .env; then
    echo "✅ GEMINI_API_KEY found in .env"
else
    echo "⚠️  GEMINI_API_KEY not found in .env"
    echo "Please add: GEMINI_API_KEY=your_key_here"
fi

# Stop current process
echo "🛑 Stopping current process..."
pkill -f ai_trading_lab

# The monitor script will auto-restart with new code
echo "✅ Deployment complete! Monitor will auto-restart the enhanced lab."
echo ""
echo "📝 Next steps:"
echo "1. Ensure GEMINI_API_KEY is in /root/btc-bot/.env"
echo "2. Monitor will automatically start the enhanced version"
echo "3. Watch for enhanced AI insights in Telegram"
ENDSSH

echo ""
echo "✅ LLM Enhancement deployed successfully!"
echo "Check Telegram for enhanced AI insights."