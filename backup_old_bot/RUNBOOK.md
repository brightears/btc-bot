# AI Trading Lab - Operational Runbook

## Quick Reference

**VPS Access**: `ssh root@5.223.55.219`
**GitHub**: https://github.com/brightears/btc-bot.git
**Status Check**: `python get_status.py`
**Emergency Stop**: `python stop_trading.py`

## System Overview

The AI Trading Lab runs 24/7 on a Hetzner VPS, continuously generating and testing trading strategies while sending hourly reports via Telegram.

## Daily Operations

### Morning Check (5 minutes)
1. Review Telegram notifications from last 24 hours
2. Check for any error alerts
3. Verify heartbeat messages received
4. Review any pending strategy approvals

### Strategy Review (10 minutes)
```bash
# SSH to VPS
ssh root@5.223.55.219

# Check system status
cd /root/btc-bot
python get_status.py

# Review recent logs
tail -n 100 ai_lab.log | grep -E "ERROR|WARNING"

# Check strategy performance
cat strategies/performance_log.json | jq
```

### Approve Promising Strategies
```bash
# View pending strategies
python get_status.py --pending

# Approve a specific strategy
python approve_strategy.py STRATEGY_ID

# Confirm approval
python get_status.py --approved
```

## Common Tasks

### Deploy Code Updates

#### From Local Machine:
```bash
# Commit and push changes
git add .
git commit -m "Update description"
git push origin main
```

#### On VPS:
```bash
ssh root@5.223.55.219
cd /root/btc-bot
git pull
python3 -m pip install -r requirements.txt

# The monitor script will auto-restart the bot
# Or manually restart:
pkill -f ai_trading_lab
# monitor_bot.sh will restart it within 5 minutes
```

### Check System Health

```bash
# Process status
ps aux | grep ai_trading_lab

# Monitor script status
ps aux | grep monitor_bot

# Resource usage
htop

# Disk space
df -h

# Network connectivity
ping -c 3 api.binance.com
```

### Review Logs

```bash
# Live log monitoring
tail -f ai_lab.log

# Search for errors
grep ERROR ai_lab.log | tail -20

# Check specific time period
grep "2024-01-20" ai_lab.log | grep "strategy"

# Performance metrics
grep "Performance" ai_lab.log | tail -10
```

## Telegram Notifications

### Expected Messages

#### Hourly Report (Every Hour)
```
📊 Hourly Report - 14:00 UTC
• Active Strategies: 5
• Best Performance: +2.3%
• System Status: Healthy
• Next Action: None required
```

#### Heartbeat (Every 6 Hours)
```
💚 AI Trading Lab Heartbeat
System running normally
Uptime: 72 hours
Strategies tested: 234
```

#### Action Required
```
🎯 Strategy Approval Needed!
Strategy: Momentum Alpha
Backtest: +15.2%
Dry-run: +3.1%
Run: python approve_strategy.py momentum_alpha
```

### Missing Notifications

If notifications stop:
1. Check VPS connection: `ssh root@5.223.55.219`
2. Check process: `ps aux | grep ai_trading_lab`
3. Check logs: `tail -50 ai_lab.log`
4. Restart if needed: `pkill -f ai_trading_lab`

## Going Live (Production Trading)

### Pre-Live Checklist
- [ ] Run in dry-run for minimum 48 hours
- [ ] Review all strategy performance metrics
- [ ] Verify risk management parameters
- [ ] Test emergency stop procedure
- [ ] Confirm API keys have trading permissions
- [ ] Set appropriate position limits

### Enable Live Trading
```bash
# First confirmation
python go_live.py

# When prompted, type: CONFIRM

# Second confirmation
# When prompted again, type: I UNDERSTAND THE RISKS

# Verify live mode
python get_status.py
# Should show: Mode: LIVE TRADING
```

### Monitor Live Trading
```bash
# Watch positions in real-time
watch -n 10 python get_status.py

# Monitor logs closely
tail -f ai_lab.log | grep -E "TRADE|POSITION|ERROR"

# Check Telegram frequently for alerts
```

## Emergency Procedures

### Immediate Stop
```bash
# Emergency stop - closes all positions
python stop_trading.py

# Verify stopped
ps aux | grep ai_trading_lab
# Should show no processes

# Check positions closed
python get_status.py
# Should show: No open positions
```

### Network Issues
```bash
# Test connectivity
ping api.binance.com
curl -I https://api.binance.com

# Restart network if needed
systemctl restart networking

# Check DNS
nslookup api.binance.com
```

### High CPU/Memory Usage
```bash
# Check resource usage
htop

# Find heavy processes
ps aux | sort -nrk 3,3 | head -10

# Restart AI Lab
pkill -f ai_trading_lab
# Will auto-restart via monitor
```

### Telegram Not Working
```bash
# Test Telegram
python send_test_notification.py

# Check credentials
cat .env | grep TELEGRAM

# View Telegram errors
grep "telegram" ai_lab.log | tail -20
```

## Troubleshooting

### Bot Not Starting
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check dependencies
pip3 list | grep -E "ccxt|telegram|numpy"

# Try manual start
python3 ai_trading_lab.py
# Watch for error messages
```

### Strategies Not Generating
```bash
# Check AI brain components
python3 -c "from ai_brain import learning_engine; print('OK')"

# Review strategy generation logs
grep "hypothesis" ai_lab.log | tail -20

# Check market data feed
python3 -c "import ccxt; exchange = ccxt.binance(); print(exchange.fetch_ticker('BTC/USDT'))"
```

### Performance Issues
```bash
# Check strategy count
ls strategies/testing/ | wc -l
# If > 100, consider cleanup

# Archive old strategies
mkdir -p strategies/archive/$(date +%Y%m%d)
mv strategies/retired/* strategies/archive/$(date +%Y%m%d)/

# Clear old logs
tail -n 10000 ai_lab.log > ai_lab.log.tmp
mv ai_lab.log.tmp ai_lab.log
```

## Maintenance Windows

### Weekly Maintenance (Sundays 00:00 UTC)
1. Review week's performance metrics
2. Archive old strategies
3. Rotate logs
4. Update dependencies if needed
5. Review and adjust risk parameters

### Monthly Maintenance
1. Full system backup
2. Review architecture for improvements
3. Update documentation
4. Performance optimization review
5. Security audit

## Backup and Recovery

### Backup Current State
```bash
# On VPS
cd /root
tar -czf btc-bot-backup-$(date +%Y%m%d).tar.gz btc-bot/

# Download to local
scp root@5.223.55.219:/root/btc-bot-backup-*.tar.gz ./backups/
```

### Restore from Backup
```bash
# On VPS
cd /root
tar -xzf btc-bot-backup-YYYYMMDD.tar.gz

# Restart services
cd btc-bot
./monitor_bot.sh &
```

### Restore from Git
```bash
# Clone fresh copy
cd /root
mv btc-bot btc-bot.old
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Copy environment file
cp ../btc-bot.old/.env .

# Install dependencies
python3 -m pip install -r requirements.txt

# Start services
nohup ./monitor_bot.sh &
```

## Contact Information

### System Issues
- Primary: Check Telegram for bot notifications
- Logs: `/root/btc-bot/ai_lab.log`
- GitHub Issues: https://github.com/brightears/btc-bot/issues

### Critical Failures
1. Execute emergency stop
2. Document error in logs
3. Create GitHub issue if code-related
4. Restore from backup if necessary

---

**Version**: 1.0
**Last Updated**: v1.0-ai-lab-deployed
**Next Review**: End of current month