# Operations Guide

Complete guide for monitoring, controlling, and maintaining the BTC Funding Bot.

## Table of Contents
- [Daily Operations](#daily-operations)
- [Monitoring Tools](#monitoring-tools)
- [Control Commands](#control-commands)
- [Troubleshooting](#troubleshooting)
- [Emergency Procedures](#emergency-procedures)
- [Maintenance Tasks](#maintenance-tasks)

## Daily Operations

### Morning Check (5 minutes)
```bash
# 1. Check bot status via Telegram
/status

# 2. Review overnight metrics
/metrics

# 3. Check VPS health (optional)
ssh root@5.223.55.219
screen -ls  # Should show btc-bot and telegram-bot
exit
```

### Throughout the Day
- Monitor Telegram for alerts
- Check `/status` if market volatility increases
- Review logs if unusual behavior noticed

### Evening Review (10 minutes)
```bash
# 1. Check performance
python monitor.py  # Run locally for dashboard

# 2. Review logs for errors
ssh root@5.223.55.219
tail -20 /root/btc-bot/logs/funding_exec.log
exit

# 3. Verify state persistence
cat logs/state.json | jq '.position'
cat logs/metrics.json | jq '.win_rate'
```

## Monitoring Tools

### 1. Real-Time Dashboard
```bash
# Terminal-based monitoring UI
python monitor.py
```
Shows:
- Current bot status
- Active positions
- Market conditions
- Performance metrics
- Recent log entries

### 2. Telegram Commands
```
/status   - Current position & bot state
/metrics  - Performance statistics
/help     - Available commands
```

### 3. Log Analysis
```bash
# Live log monitoring
tail -f logs/funding_exec.log

# Search for errors
grep ERROR logs/funding_exec.log

# View last 50 lines
tail -50 logs/funding_exec.log

# Check specific date
grep "2024-09-19" logs/funding_exec.log
```

### 4. State Files
```bash
# Current position
cat logs/state.json | jq

# Performance metrics
cat logs/metrics.json | jq

# Check if paused
ls -la logs/paused
```

## Control Commands

### Telegram Bot Control
```
/pause   - Stop opening new positions
/resume  - Resume normal operations
/stop    - Emergency shutdown
```

### Command Line Control
```bash
# Pause operations
touch logs/paused

# Resume operations
rm logs/paused

# Emergency stop
touch .kill

# Restart bot
screen -S btc-bot -X quit
screen -dmS btc-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python run_funding_exec.py'
```

### Process Management
```bash
# View running processes
screen -ls

# Attach to main bot
screen -r btc-bot

# Attach to Telegram bot
screen -r telegram-bot

# Detach from screen
Ctrl+A, then D

# Kill a screen session
screen -S btc-bot -X quit
```

## Troubleshooting

### Bot Not Responding
1. Check if process is running:
```bash
ssh root@5.223.55.219
screen -ls
ps aux | grep python
```

2. Check for kill file:
```bash
ls -la .kill
rm .kill  # If exists and you want to restart
```

3. Review recent logs:
```bash
tail -100 logs/funding_exec.log | grep ERROR
```

4. Restart if needed:
```bash
screen -S btc-bot -X quit
screen -dmS btc-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python run_funding_exec.py'
```

### Telegram Not Working
1. Test bot token:
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

2. Check credentials:
```bash
grep TELEGRAM .env
```

3. Restart Telegram bot:
```bash
screen -S telegram-bot -X quit
screen -dmS telegram-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python telegram_bot.py'
```

### Position Stuck
1. Check position details:
```bash
cat logs/state.json | jq '.position'
```

2. Check funding rate:
```bash
grep "Current funding" logs/funding_exec.log | tail -5
```

3. Force close (emergency only):
```bash
# Create kill file to trigger close
touch .kill
# Wait 30 seconds for bot to close position
# Then remove kill file
rm .kill
```

### High CPU/Memory Usage
```bash
# Check resource usage
htop

# Check bot memory
ps aux | grep python

# Restart if needed
screen -S btc-bot -X quit
# Clear logs if too large
mv logs/funding_exec.log logs/funding_exec.log.old
# Restart
screen -dmS btc-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python run_funding_exec.py'
```

## Emergency Procedures

### 1. Emergency Stop
```bash
# Via Telegram
/stop

# Or via SSH
ssh root@5.223.55.219
touch /root/btc-bot/.kill
```

### 2. Position Emergency Close
```bash
# If position needs immediate closing:
touch .kill  # Forces position close
# Wait for confirmation in logs
tail -f logs/funding_exec.log | grep "Position closed"
# Remove kill file after position closed
rm .kill
```

### 3. Complete Shutdown
```bash
ssh root@5.223.55.219
cd /root/btc-bot

# Stop all processes
screen -S btc-bot -X quit
screen -S telegram-bot -X quit

# Create kill file to prevent restart
touch .kill

# Verify stopped
ps aux | grep python
```

### 4. Data Backup
```bash
# Backup important files
cd /root/btc-bot
tar -czf backup_$(date +%Y%m%d).tar.gz logs/ .env config.yaml

# Download backup
scp root@5.223.55.219:/root/btc-bot/backup_*.tar.gz ./
```

## Maintenance Tasks

### Daily
- [ ] Check `/status` via Telegram
- [ ] Review `/metrics` for anomalies
- [ ] Verify VPS is responsive

### Weekly
- [ ] Review performance metrics
- [ ] Check log file sizes
- [ ] Update documentation if needed
- [ ] Test emergency procedures

### Monthly
- [ ] Rotate log files
- [ ] Update dependencies
- [ ] Review and optimize configuration
- [ ] Backup configuration and metrics

### Log Rotation
```bash
# Manual log rotation
cd /root/btc-bot/logs
mv funding_exec.log funding_exec.$(date +%Y%m%d).log
touch funding_exec.log

# Set up automatic rotation (optional)
cat > /etc/logrotate.d/btc-bot << EOF
/root/btc-bot/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
```

### Dependency Updates
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade ccxt

# Update all packages (careful!)
pip install --upgrade -r requirements.txt
```

### Performance Review
```python
# Analyze metrics
import json
with open('logs/metrics.json') as f:
    metrics = json.load(f)

print(f"Win Rate: {metrics['win_rate']:.1f}%")
print(f"Total P&L: ${metrics['total_pnl']:.4f}")
print(f"Avg Funding: ${metrics['avg_funding']:.4f}")
```

## Configuration Tuning

### Adjusting Parameters
```bash
# Edit configuration
nano config.yaml

# Or use command line
python run_funding_exec.py \
  --notional_usdt 1000 \      # Increase position size
  --threshold_bps 0.3 \        # Lower threshold for more trades
  --max_position_usdt 10000    # Increase max exposure
```

### Testing Changes
1. Always test in dry-run first
2. Run for at least 24 hours
3. Review metrics before applying to live

## Support Channels

### Getting Help
1. Check this documentation
2. Review logs for specific errors
3. Use Telegram `/help` command
4. Check GitHub issues

### Reporting Issues
Include:
- Bot version (git rev-parse HEAD)
- Last 100 lines of logs
- State.json contents
- Metrics.json contents
- Steps to reproduce

## Quick Reference Card

### Essential Commands
```bash
# Status check
/status                        # Telegram
cat logs/state.json | jq       # Terminal

# Control
/pause                         # Telegram pause
touch logs/paused              # Terminal pause
touch .kill                    # Emergency stop

# Monitoring
python monitor.py              # Dashboard
tail -f logs/funding_exec.log  # Live logs

# VPS Access
ssh root@5.223.55.219          # Connect
screen -r btc-bot              # View main bot
screen -r telegram-bot         # View Telegram bot
Ctrl+A, D                      # Detach from screen

# Restart
screen -S btc-bot -X quit      # Stop bot
screen -dmS btc-bot bash -c 'cd /root/btc-bot && source venv/bin/activate && python run_funding_exec.py'
```

### Key Files
- `logs/state.json` - Current position and bot state
- `logs/metrics.json` - Performance statistics
- `logs/funding_exec.log` - Detailed execution logs
- `logs/paused` - Pause flag (presence = paused)
- `.kill` - Kill switch (presence = stop)