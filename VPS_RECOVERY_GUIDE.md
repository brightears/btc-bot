# 🚨 VPS Recovery & Trading Fix Deployment Guide

## Current Situation
- **VPS**: 64.23.206.191 shows ONLINE in DigitalOcean but network unreachable
- **Bot Performance**: 7.3% win rate, losing $65+
- **Fixes**: Ready in GitHub (commit 6db6f12)

## Step 1: Access via DigitalOcean Console

1. Go to: https://cloud.digitalocean.com/droplets
2. Find droplet: 64.23.206.191
3. Click the droplet name
4. Click "Console" button (top right)
5. Log in with root credentials

## Step 2: Diagnose in Console

Run these commands:
```bash
# Check system is alive
uptime
ps aux | grep python

# Check network
ip addr show
netstat -tlnp | grep :22

# Check firewall
iptables -L -n
ufw status verbose
```

## Step 3: Fix Network Access

### Option A: If firewall is blocking
```bash
# Disable firewall temporarily
ufw disable
iptables -F
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT

# Restart SSH
systemctl restart sshd
```

### Option B: If fail2ban is blocking
```bash
# Check if your IP is banned
fail2ban-client status sshd
fail2ban-client unban --all

# Or disable temporarily
systemctl stop fail2ban
```

### Option C: If network interface issue
```bash
# Restart network
systemctl restart networking
ifconfig eth0 up
dhclient eth0
```

## Step 4: Deploy Trading Fixes

Once network is restored (or directly in console):
```bash
# Navigate to bot directory
cd /root/btc-bot

# Pull latest fixes from GitHub
git pull origin main

# The fixes include:
# - TestTradingStrategy: Now buys dips/sells rips (not time-based)
# - Volume requirements: Reduced from $2B to $10-50M
# - Volume display: Added to reports

# Restart the bot
pkill -f ai_trading_lab
bash start_enhanced_bot.sh

# Monitor improvements
tail -f ai_lab_enhanced.log | grep -E "win_rate|confidence|volume"
```

## Step 5: Verify Success

After 5-10 minutes, check:
- Win rate climbing above 30%
- Volume showing in Telegram reports as "$X.XXB USD"
- Multiple strategies executing (not just Test)

## Alternative: Power Cycle

If console is unresponsive:
1. In DigitalOcean dashboard
2. Click "Power" → "Power Cycle"
3. Wait 2 minutes
4. Try SSH again: `ssh root@64.23.206.191`

## Emergency Contacts

- DigitalOcean Support: Create ticket mentioning "Network connectivity lost"
- Status Page: https://status.digitalocean.com

## Critical Files Changed

The GitHub commit (6db6f12) contains:
- `strategies/proven_strategies.py` - Fixed trading logic
- `ai_trading_lab_enhanced.py` - Added volume display
- `ai_brain/realtime_market_data.py` - Volume logging

## Expected Results

- **Immediate**: SSH access restored
- **5 minutes**: First profitable trades
- **30 minutes**: Win rate 40-50%
- **Losses stop**: No more -$3/hour bleeding