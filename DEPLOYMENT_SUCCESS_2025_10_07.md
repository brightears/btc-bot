# Successful Hetzner VPS Deployment - October 7, 2025

## 🎉 Mission Accomplished

After a 2-hour battle with SSH authentication, Freqtrade is now successfully deployed and running on Hetzner Cloud VPS with full Telegram integration.

---

## The Problem: SSH Authentication Hell

### What Went Wrong
When attempting to deploy Freqtrade to Hetzner Cloud VPS (5.223.55.219), we encountered a frustrating catch-22:

1. **Ubuntu 22.04 Security Defaults**: Password authentication disabled by default in `/etc/ssh/sshd_config`
2. **Rebuild Doesn't Inject SSH Keys**: When you rebuild a server via Hetzner console or API, SSH keys are NOT automatically injected (only during initial server creation)
3. **Web Console Limitations**: Hetzner's VNC web console has no copy/paste, uses QWERTY layout, making it impractical for running complex commands
4. **DNS Resolution Issues**: Even after gaining access, DNS was misconfigured preventing package downloads

### Failed Attempts
We tried multiple approaches that didn't work:
- ❌ Enabling password auth via web console (too error-prone)
- ❌ Adding SSH keys via Hetzner Cloud API (not injected to existing server)
- ❌ Password reset via API (password auth still disabled)
- ❌ Multiple server rebuilds (keys never injected)

---

## The Solution: Hetzner Rescue Mode + Filesystem Mount

### What Finally Worked

**The Breakthrough**: Use Hetzner's rescue mode to mount the server's filesystem and directly modify it.

### Step-by-Step Procedure

#### 1. Enable Rescue Mode via API
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_HETZNER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  https://api.hetzner.cloud/v1/servers/SERVER_ID/actions/enable_rescue
```

Response includes rescue mode root password (save it!):
```json
{
  "root_password": "PPkqdvgrqRKu",
  "action": { "id": 584699674198748, ... }
}
```

#### 2. Reboot Into Rescue Mode
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_HETZNER_API_TOKEN" \
  -d '{}' \
  https://api.hetzner.cloud/v1/servers/SERVER_ID/actions/reboot
```

Wait 60 seconds for reboot to complete.

#### 3. Connect to Rescue Mode and Mount Filesystem
```bash
# Connect with rescue password
sshpass -p "PPkqdvgrqRKu" ssh root@5.223.55.219

# Mount the actual server's filesystem
mount /dev/sda1 /mnt

# Add your SSH public key
mkdir -p /mnt/root/.ssh
echo "ssh-ed25519 YOUR_PUBLIC_KEY_HERE" >> /mnt/root/.ssh/authorized_keys
chmod 700 /mnt/root/.ssh
chmod 600 /mnt/root/.ssh/authorized_keys
```

#### 4. Disable Rescue and Reboot Normally
```bash
# Disable rescue mode
curl -X POST \
  -H "Authorization: Bearer YOUR_HETZNER_API_TOKEN" \
  https://api.hetzner.cloud/v1/servers/SERVER_ID/actions/disable_rescue

# Reboot into normal mode
curl -X POST \
  -H "Authorization: Bearer YOUR_HETZNER_API_TOKEN" \
  -d '{}' \
  https://api.hetzner.cloud/v1/servers/SERVER_ID/actions/reboot
```

#### 5. Connect with SSH Key
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
```

**Success!** SSH key authentication now works.

---

## Complete Deployment Procedure

### Prerequisites
- Hetzner Cloud account
- API token (Security → API Tokens)
- Server ID (from server details)

### 1. Generate SSH Key (One Time)
```bash
ssh-keygen -t ed25519 -f ~/.ssh/hetzner_btc_bot -C "btc-bot-vps"
```

### 2. Add SSH Key via Rescue Mode
Follow the rescue mode procedure above to inject your SSH key.

### 3. Deploy Freqtrade
Once SSH access is established, run the automated deployment:

```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219 << 'ENDSSH'
set -ex

# Fix DNS first
cat > /etc/systemd/resolved.conf << 'EOF'
[Resolve]
DNS=8.8.8.8 8.8.4.4
FallbackDNS=1.1.1.1 1.0.0.1
DNSStubListener=yes
EOF
systemctl restart systemd-resolved
sleep 5

# Update system
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y git python3 python3-pip python3-venv build-essential wget curl htop screen

# Install TA-Lib (required for strategies)
cd /tmp
wget --timeout=120 http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
ldconfig

# Clone repository
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

# Setup Python environment
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install freqtrade python-dotenv ccxt pyyaml tenacity

# Create .env file
cat > .env << 'ENVEOF'
LIVE_TRADING=NO
KILL=0
BINANCE_KEY=YOUR_BINANCE_KEY
BINANCE_SECRET=YOUR_BINANCE_SECRET
TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
GEMINI_API_KEY=YOUR_GEMINI_KEY
ENVEOF

echo "Deployment complete!"
ENDSSH
```

### 4. Configure and Start Bot
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
cd /root/btc-bot
source .venv/bin/activate

# Update config from .env
python update_config_from_env.py

# Run strategy rotation
python strategy_rotator.py

# Start Freqtrade
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &

# Verify it's running
ps aux | grep freqtrade
tail -f freqtrade.log
```

---

## Current Bot Status (as of Oct 7, 2025 12:11 PM)

### ✅ Successfully Deployed
- **Server**: 5.223.55.219 (Hetzner Singapore)
- **OS**: Ubuntu 22.04.5 LTS
- **Freqtrade**: Version 2025.6
- **Python**: 3.10.12
- **CCXT**: 4.5.7
- **TA-Lib**: 0.4.0 (compiled from source)

### ✅ Bot Configuration
- **Mode**: Dry-run (paper trading)
- **Exchange**: Binance
- **Trading Pair**: BTC/USDT
- **Strategy**: SimpleRSI
- **Timeframe**: 5m
- **Stake per Trade**: $100 USDT
- **Max Open Trades**: 3
- **Virtual Capital**: $10,000 USDT
- **Minimum ROI**: 2%
- **Trailing Stoploss**: -1%

### ✅ Telegram Integration
- **Status**: Active and sending notifications
- **Bot**: @your_freqtrade_bot
- **Chat ID**: 8352324945

**Confirmed Working Messages:**
1. "Dry run is enabled. All trades are simulated."
2. Exchange configuration (Binance, $100 stake, SimpleRSI)
3. "Searching for USDT pairs to buy and sell..."
4. Status updates every 60 seconds

### ✅ Available Telegram Commands
- `/status` - Current open trades
- `/profit` - Profit/loss summary
- `/balance` - Wallet balance
- `/daily` - Daily statistics
- `/weekly` - Weekly statistics
- `/monthly` - Monthly statistics
- `/forceexit` - Force close a trade
- `/performance` - Strategy performance
- `/help` - All available commands

---

## Key Learnings

### What We Discovered

1. **Hetzner SSH Keys Only Work on Server Creation**
   - SSH keys added to Hetzner project are only injected during initial server creation
   - Rebuilding a server does NOT re-inject SSH keys
   - This is by design for security reasons

2. **Rescue Mode is the Universal Key**
   - Hetzner rescue mode boots a minimal Linux from network
   - Allows mounting and modifying the actual server filesystem
   - Perfect for recovering from SSH lockouts or corrupted configs

3. **DNS Must Be Fixed First**
   - Ubuntu 22.04 uses systemd-resolved
   - Default config often fails on cloud VPS
   - Must configure explicit DNS servers (8.8.8.8, 1.1.1.1)

4. **TA-Lib Requires Compilation**
   - No pre-built package for Ubuntu
   - Must compile from source (takes ~5 minutes)
   - Requires build-essential, wget, curl

5. **Freqtrade Telegram Setup is Automatic**
   - Once config.json has telegram token/chat_id
   - Bot automatically connects on startup
   - No additional configuration needed

### Best Practices Going Forward

1. **Always Keep SSH Key Backup**
   - Store private key securely (not in Git!)
   - Keep public key in Hetzner project for future servers

2. **Use Rescue Mode for SSH Recovery**
   - Don't waste time trying to enable password auth
   - Go straight to rescue mode → mount → fix → reboot

3. **Automate Deployment**
   - Use `cloud-init.yaml` for future server setups
   - Keep deployment scripts in version control
   - Document every step

4. **Test Telegram Immediately**
   - Don't wait to verify Telegram notifications
   - Check logs for "Enabling rpc.telegram"
   - Confirm startup messages are received

---

## Files Created

### Local Files
- `cloud-init.yaml` - Automated server setup configuration
- `deploy_to_hetzner_cloudinit.sh` - Deployment automation script
- `~/.ssh/hetzner_btc_bot` - SSH private key (NEVER commit!)
- `~/.ssh/hetzner_btc_bot.pub` - SSH public key

### VPS Files
- `/root/btc-bot/` - Complete bot repository
- `/root/btc-bot/.venv/` - Python virtual environment
- `/root/btc-bot/.env` - Environment variables with credentials
- `/root/btc-bot/config.json` - Freqtrade configuration
- `/root/btc-bot/freqtrade.log` - Bot logs
- `/root/setup.log` - Deployment completion log

---

## Troubleshooting

### If SSH Fails Again

1. **Check SSH key is in authorized_keys:**
```bash
# Via rescue mode:
mount /dev/sda1 /mnt
cat /mnt/root/.ssh/authorized_keys
```

2. **Reset via rescue mode:**
```bash
# Follow rescue mode procedure above
# Re-add SSH key to /mnt/root/.ssh/authorized_keys
```

3. **Last resort - password auth:**
```bash
# In rescue mode:
mount /dev/sda1 /mnt
echo "PasswordAuthentication yes" > /mnt/etc/ssh/sshd_config.d/99-enable-password.conf
# Reboot and use password
```

### If Bot Stops Running

1. **Check if process is alive:**
```bash
ssh -i ~/.ssh/hetzner_btc_bot root@5.223.55.219
ps aux | grep freqtrade
```

2. **Check logs:**
```bash
tail -f /root/btc-bot/freqtrade.log
```

3. **Restart bot:**
```bash
cd /root/btc-bot
source .venv/bin/activate
pkill -f freqtrade
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
```

### If Telegram Stops Working

1. **Verify bot token/chat_id in .env:**
```bash
cat /root/btc-bot/.env | grep TELEGRAM
```

2. **Update config:**
```bash
cd /root/btc-bot
source .venv/bin/activate
python update_config_from_env.py
```

3. **Restart bot:**
```bash
pkill -f freqtrade
nohup freqtrade trade --config config.json > freqtrade.log 2>&1 &
```

---

## Timeline of Events

- **3:55 AM UTC** - Started deployment attempt
- **3:56 AM - 5:00 AM** - Battled SSH authentication (multiple failed attempts)
- **5:00 AM** - Breakthrough: Discovered rescue mode solution
- **5:01 AM** - Successfully mounted filesystem and added SSH key
- **5:02 AM** - Rebooted, SSH key auth working
- **5:03 AM** - Started automated deployment
- **5:05 AM** - TA-Lib compilation complete, Freqtrade installed
- **5:06 AM** - .env created, config updated
- **5:11 AM** - Bot started successfully
- **5:11 AM** - Telegram notifications confirmed working
- **5:12 AM** - Bot heartbeat confirmed, fully operational

**Total deployment time**: ~17 minutes (after solving SSH auth)
**Total troubleshooting time**: ~2 hours (SSH authentication battle)

---

## Conclusion

What started as a simple deployment turned into a masterclass in:
- Hetzner Cloud API usage
- Linux rescue mode techniques
- SSH key management
- Freqtrade configuration
- Telegram bot integration

The key takeaway: **When locked out of SSH, use rescue mode to mount the filesystem directly.** This technique works for any Hetzner Cloud server and avoids hours of troubleshooting.

The bot is now running, Telegram is working, and we have full documentation for future deployments. 🎉

---

**Generated**: October 7, 2025
**Bot Status**: Running (PID 33878)
**Next Strategy Rotation**: Automatic (weekly)
**Monitoring**: Telegram notifications enabled
