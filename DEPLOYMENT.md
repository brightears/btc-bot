# Deployment (Ubuntu 24.04 LTS)

> Summary: create a non-root user, harden SSH/ufw, install Python, set up venv,
> run via cron **or** systemd, and rotate logs.

## 0) Prereqs
- Fresh VPS; SSH key auth enabled; your local machine has rsync/scp.

## 1) Create user & basics (as root)
```bash
adduser --disabled-password --gecos "" bot
usermod -aG sudo bot
install -d -m 700 -o bot -g bot /home/bot/.ssh
# add your public key to /home/bot/.ssh/authorized_keys
apt update && apt -y upgrade
apt -y install python3-venv python3-pip git ufw logrotate
```

## 2) Firewall (ufw)
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw --force enable
```

## 3) App directory
```bash
mkdir -p /opt/btc-bot && chown -R bot:bot /opt/btc-bot
```

## 4) Ship code (from your laptop)
```bash
rsync -avz --exclude .venv --exclude .git --exclude __pycache__/   ./btc-bot/ bot@<VPS_IP>:/opt/btc-bot/
```

## 5) Install (as bot on VPS)
```bash
ssh bot@<VPS_IP>
cd /opt/btc-bot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env   # fill secrets; keep LIVE_TRADING=NO for dry-run
```

## 6) Scheduling – choose ONE

### Option A — **cron + flock** (simple, single-instance)
```bash
crontab -l | sed '/btc-bot/d' | crontab -
( crontab -l; echo '*/5 * * * * /usr/bin/flock -n /tmp/btc-bot.lock -c "cd /opt/btc-bot && . .venv/bin/activate && python run_funding_exec.py >> logs/funding_exec.log 2>&1"'
  ; echo '@reboot /usr/bin/flock -n /tmp/btc-bot.lock -c "cd /opt/btc-bot && . .venv/bin/activate && python run_funding_exec.py >> logs/funding_exec.log 2>&1"'
) | crontab -
```

### Option B — **systemd** (richer supervision)
Create `/etc/systemd/system/btc-bot.service`:
```ini
[Unit]
Description=BTC Funding Carry (dry-run)
After=network.target

[Service]
User=bot
WorkingDirectory=/opt/btc-bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/btc-bot/.venv/bin/python run_funding_exec.py
Restart=always
RestartSec=10
# Hardening bits (sample):
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now btc-bot
sudo systemctl status btc-bot --no-pager
```

## 7) Log rotation
`/etc/logrotate.d/btc-bot`:
```conf
/opt/btc-bot/logs/*.log {
  daily
  rotate 14
  compress
  missingok
  notifempty
  copytruncate
  create 640 bot bot
}
```
Test:
```bash
sudo logrotate -d /etc/logrotate.d/btc-bot
```

## 8) Updating
```bash
rsync -avz --delete ./btc-bot/ bot@<VPS_IP>:/opt/btc-bot/
# systemd: sudo systemctl restart btc-bot
```
