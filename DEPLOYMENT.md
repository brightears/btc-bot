# AI Trading Lab - Deployment Documentation

## Current Production Deployment

### Server Information
- **Provider**: Hetzner Cloud
- **Location**: Singapore (FSN1-DC14)
- **IP Address**: 5.223.55.219
- **OS**: Ubuntu 22.04 LTS
- **Status**: ✅ OPERATIONAL (24/7)

### GitHub Repository
- **URL**: https://github.com/brightears/btc-bot.git
- **Branch**: main
- **Latest Tag**: v1.0-ai-lab-deployed

## Quick Deployment Commands

### Access VPS
```bash
ssh root@5.223.55.219
```

### Deploy Updates from Local
```bash
# Commit and push changes
git add .
git commit -m "Update description"
git push origin main

# On VPS - Pull and restart
ssh root@5.223.55.219
cd /root/btc-bot
git pull
python3 -m pip install -r requirements.txt
# Monitor script auto-restarts the bot
```

## Initial Setup (Already Completed)

### 1. VPS Provisioning
```bash
# Hetzner Cloud Console
- Created CX21 instance (2 vCPU, 4GB RAM, 40GB SSD)
- Selected Ubuntu 22.04
- Added SSH key
- Singapore location for low latency
```

### 2. System Configuration
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git screen

# Install Python packages globally (for system scripts)
pip3 install python-telegram-bot python-dotenv
```

### 3. Application Deployment
```bash
# Clone repository
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Install Python dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add API keys and tokens
```

### 4. Process Management
```bash
# Start monitoring script
nohup ./monitor_bot.sh > monitor.log 2>&1 &

# Monitor script automatically starts AI Trading Lab
# Checks every 5 minutes and restarts if needed
```

## Architecture Overview

### Running Processes
1. **Monitor Script** (`monitor_bot.sh`)
   - Runs continuously in background
   - Checks AI Lab process every 5 minutes
   - Auto-restarts on failure

2. **AI Trading Lab** (`ai_trading_lab.py`)
   - Main trading system
   - Generates and tests strategies
   - Sends Telegram notifications

### Directory Structure
```
/root/btc-bot/
├── ai_brain/              # AI components
│   ├── __init__.py
│   ├── learning_engine.py
│   ├── hypothesis_generator.py
│   └── strategy_evaluator.py
├── src/                   # Core trading logic
│   ├── exchange/
│   ├── funding/
│   └── risk/
├── strategies/            # Strategy storage
├── ai_trading_lab.py      # Main process
├── monitor_bot.sh         # Auto-restart script
├── get_status.py          # Status checker
├── approve_strategy.py    # Strategy approval
├── go_live.py            # Enable live trading
├── stop_trading.py       # Emergency stop
└── .env                  # Configuration (not in Git)
```

## Environment Configuration

### Required Environment Variables (.env)
```bash
# Exchange API (Binance)
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET=False  # Use mainnet

# Telegram Bot
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Safety Configuration
LIVE_TRADING_ENABLED=false  # Keep false for dry-run
LIVE_TRADE_REQUIRE_DOUBLE_CHECK=true
MAX_POSITION_SIZE_USDT=1000

# AI Configuration
AI_LEARNING_ENABLED=true
AI_HYPOTHESIS_GENERATION=true
AI_PARALLEL_TESTING=true
```

## Monitoring & Logs

### Check System Status
```bash
# SSH to VPS
ssh root@5.223.55.219

# Check if processes are running
ps aux | grep -E "ai_trading_lab|monitor_bot"

# View recent logs
tail -f /root/btc-bot/ai_lab.log

# Check system status
python get_status.py
```

### Log Files
- **Main Log**: `/root/btc-bot/ai_lab.log`
- **Monitor Log**: `/root/monitor.log`
- **Strategy Performance**: `/root/btc-bot/strategies/performance_log.json`

### Telegram Notifications
- Hourly status reports
- 6-hour heartbeat confirmations
- Strategy discovery alerts
- Action required notifications

## Maintenance Procedures

### Regular Updates
```bash
# Local development
git add .
git commit -m "Feature: description"
git push origin main

# On VPS
ssh root@5.223.55.219
cd /root/btc-bot
git pull
pip3 install -r requirements.txt
# Auto-restart handles process restart
```

### Manual Restart
```bash
# Kill existing processes
pkill -f ai_trading_lab
pkill -f monitor_bot

# Restart monitor (which starts AI Lab)
nohup ./monitor_bot.sh > monitor.log 2>&1 &
```

### Emergency Stop
```bash
# Stop all trading immediately
python stop_trading.py

# Kill all processes
pkill -f ai_trading_lab
pkill -f monitor_bot
```

## Backup & Recovery

### Create Backup
```bash
# On VPS
cd /root
tar -czf btc-bot-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  btc-bot/.env \
  btc-bot/strategies/ \
  btc-bot/ai_lab.log

# Download to local
scp root@5.223.55.219:/root/btc-bot-backup-*.tar.gz ./backups/
```

### Restore from Backup
```bash
# On VPS
cd /root
tar -xzf btc-bot-backup-TIMESTAMP.tar.gz

# Restart services
cd btc-bot
nohup ./monitor_bot.sh > monitor.log 2>&1 &
```

### Fresh Deployment
```bash
# Clone repository
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Install dependencies
pip3 install -r requirements.txt

# Restore configuration
cp /path/to/backup/.env .

# Start services
nohup ./monitor_bot.sh > monitor.log 2>&1 &
```

## Security Considerations

### API Key Security
- Trading permissions only (no withdrawal)
- Keys stored in .env (never in Git)
- File permissions: 600 (read/write owner only)

### VPS Security
- SSH key authentication only
- Firewall configured (ufw)
- Regular security updates
- No unnecessary services

### Trading Safety
- Dry-run mode by default
- Position size limits
- Double-confirmation for live trading
- Emergency stop capability

## Troubleshooting

### Bot Not Running
```bash
# Check processes
ps aux | grep ai_trading_lab

# Check monitor script
ps aux | grep monitor_bot

# View error logs
tail -100 ai_lab.log | grep ERROR

# Manual start for debugging
python3 ai_trading_lab.py
```

### Telegram Not Working
```bash
# Test notification
python send_test_notification.py

# Check credentials
grep TELEGRAM .env

# View Telegram errors
grep telegram ai_lab.log | tail -20
```

### Strategy Issues
```bash
# Check strategy generation
grep "Generated strategy" ai_lab.log | tail -10

# View strategy files
ls -la strategies/testing/

# Check AI brain
python3 -c "from ai_brain import learning_engine; print('AI Brain OK')"
```

## Performance Optimization

### Resource Usage
```bash
# Monitor resources
htop

# Check disk usage
df -h

# View memory usage
free -h

# Network statistics
netstat -tulpn
```

### Log Management
```bash
# Rotate logs manually
mv ai_lab.log ai_lab.log.$(date +%Y%m%d)
touch ai_lab.log

# Clean old strategies
find strategies/retired/ -mtime +30 -delete
```

## Going Live Checklist

### Prerequisites
- [ ] Run dry-run for minimum 48 hours
- [ ] Review strategy performance metrics
- [ ] Verify risk parameters
- [ ] Test emergency stop
- [ ] Confirm API keys have trading permission
- [ ] Backup current state

### Enable Live Trading
```bash
# Edit configuration
nano .env
# Set: LIVE_TRADING_ENABLED=true

# Run go-live script
python go_live.py
# Confirm twice when prompted

# Monitor closely
watch -n 5 python get_status.py
```

## Support Information

### Quick Commands
- **Status**: `python get_status.py`
- **Logs**: `tail -f ai_lab.log`
- **Stop**: `python stop_trading.py`
- **Restart**: `pkill -f ai_trading_lab` (auto-restarts)

### File Locations
- **Config**: `/root/btc-bot/.env`
- **Logs**: `/root/btc-bot/ai_lab.log`
- **Strategies**: `/root/btc-bot/strategies/`
- **Code**: `/root/btc-bot/`

---

**Version**: 1.0
**Last Updated**: January 2025
**Status**: ✅ Deployed and Operational