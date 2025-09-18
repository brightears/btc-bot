# Security Checklist

- [ ] Store Binance and Telegram secrets only in `.env`; confirm `.gitignore` excludes it.
- [ ] Restrict API keys to required permissions (read and trade) and IP whitelist when possible.
- [ ] Enable two-factor authentication on Binance and revoke unused keys.
- [ ] Review server firewall rules; allow only necessary outbound traffic.
- [ ] Monitor `logs/funding_exec.log` for abnormal errors before enabling live mode.
- [ ] Validate system clock sync (ntp/chrony) to avoid funding window drift.
- [ ] Rotate logs/state archives regularly and remove sensitive historical data if exported.
- [ ] Test the kill switch by setting `KILL=1` and confirming the bot exits gracefully.
