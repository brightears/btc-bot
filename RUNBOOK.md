# Runbook (Ops)

## Where is it running?
- Host: <VPS_IP>   • User: `bot`   • Dir: `/opt/btc-bot`

## Health checks
```bash
pgrep -af run_funding_exec.py
tail -n 100 -f /opt/btc-bot/logs/funding_exec.log
```
- Cron: `crontab -l`
- Systemd: `sudo systemctl status btc-bot --no-pager`

## Common actions
- **Restart (systemd):** `sudo systemctl restart btc-bot`
- **Rotate logs now:** `sudo logrotate -f /etc/logrotate.d/btc-bot`
- **Update code:** rsync → restart

## Triage
1) Read last 200 log lines  
2) Check API timeouts / network  
3) Verify `.env` present & readable  
4) If stuck: disable scheduler, run one-shot locally with `-vv` logging

## Telegram
- `/status` → reports mode, notional, next funding ETA, PID, uptime.
- Expect succinct alerts: window enter/exit, rebalances, errors, daily summary.
