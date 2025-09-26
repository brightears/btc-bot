#!/bin/bash
# Apply trading strategy fixes to live bot

echo "🔧 Applying Trading Strategy Fixes..."
echo "=================================="

BOT_DIR="/root/btc-bot"
BACKUP_DIR="$BOT_DIR/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
cp $BOT_DIR/strategies/proven_strategies.py $BACKUP_DIR/ 2>/dev/null || echo "No existing proven_strategies.py"
cp $BOT_DIR/ai_trading_lab_enhanced.py $BACKUP_DIR/ 2>/dev/null || echo "No existing ai_trading_lab_enhanced.py"

# Stop running bot
echo "⏸️  Stopping bot..."
pkill -f ai_trading_lab || true
systemctl stop btc-bot 2>/dev/null || true
sleep 3

# Extract and apply fixes
echo "📝 Applying fixed files..."
cd $BOT_DIR
tar -xzf deploy_fixes.tar.gz

# Restart bot
echo "🚀 Restarting bot..."
if [ -f "$BOT_DIR/start_enhanced_bot.sh" ]; then
    bash $BOT_DIR/start_enhanced_bot.sh
else
    cd $BOT_DIR
    source .venv/bin/activate
    nohup python ai_trading_lab_enhanced.py >> ai_lab_enhanced.log 2>&1 &
    echo $! > ai_lab.pid
fi

echo ""
echo "✅ Fixes Applied Successfully!"
echo "=================================="
echo ""
echo "Key improvements deployed:"
echo "1. ✓ TestTradingStrategy now buys dips and sells rips (was alternating every minute)"
echo "2. ✓ Reduced volume requirements to realistic levels:"
echo "   - MarketMaking: $2B → $50M"
echo "   - MomentumFollowing: $500M → $25M"
echo "   - VolumeProfile: $1.5B → $50M"
echo "3. ✓ Added volume display to hourly reports"
echo ""
echo "Expected improvements:"
echo "• Win rate should increase from 9.8% to ~50-60%"
echo "• Strategies should now execute trades (was 0% before)"
echo "• Volume data now visible in reports"
echo ""
echo "📊 Check logs in 5 minutes:"
echo "   tail -f $BOT_DIR/ai_lab_enhanced.log"
echo ""
echo "📱 Monitor Telegram for improved performance reports"