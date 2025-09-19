# VPS Deployment Guide

## Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Clone repository
git clone <your-repo> /opt/btc-bot
cd /opt/btc-bot
```

## Systemd Service

Create `/etc/systemd/system/btc-bot.service`:
```ini
[Unit]
Description=BTC Funding Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/btc-bot
Environment="PATH=/opt/btc-bot/.venv/bin"
ExecStart=/opt/btc-bot/.venv/bin/python /opt/btc-bot/run_funding_exec.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable btc-bot
sudo systemctl start btc-bot
```

## Monitoring

```bash
# Check status
sudo systemctl status btc-bot

# View logs
sudo journalctl -u btc-bot -f
```