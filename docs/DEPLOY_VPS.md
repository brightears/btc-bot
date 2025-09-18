# VPS Deployment Guide

1. **Provision host**
   - Choose a minimal Ubuntu/Debian VPS with >1 GB RAM.
   - Harden SSH: disable password login, use key-based auth, and keep packages updated.

2. **Bootstrap environment**
   ```bash
   sudo apt update && sudo apt install -y python3 python3-venv git
   git clone <your-repo> btc-bot
   cd btc-bot
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure secrets**
   - Copy `.env.sample` to `.env` and populate Binance/Telegram credentials.
   - Use tools like `ansible-vault` or the VPS secret manager to store backups securely.

4. **Service management**
   - Create a `systemd` unit to keep the bot running:
     ```ini
     [Unit]
     Description=BTC Funding Carry Bot
     After=network.target

     [Service]
     WorkingDirectory=/opt/btc-bot
     ExecStart=/opt/btc-bot/.venv/bin/python /opt/btc-bot/run_funding_exec.py
     Environment=LIVE_TRADING=YES
     Restart=on-failure

     [Install]
     WantedBy=multi-user.target
     ```
   - Remember to set `--live` in `ExecStart` only after completing security checks.

5. **Observability**
   - Ship `logs/funding_exec.log` to a log aggregator (e.g., vector, fluent-bit) without leaking secrets.
   - Use `scripts/health_ping.sh` in cron or a monitoring agent for heartbeat checks.

6. **Maintenance**
   - Run `git pull` + `pip install -r requirements.txt --upgrade` during planned maintenance windows.
   - Stop the service (`systemctl stop btc-bot`) before performing upgrades.
