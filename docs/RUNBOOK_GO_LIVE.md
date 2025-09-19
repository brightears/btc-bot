# Go-Live Checklist

## Prerequisites

- [ ] Dry-run tested for 24+ hours
- [ ] Binance API keys with spot + futures permissions
- [ ] Small test notional (start with $100)
- [ ] Telegram bot configured (optional)

## Steps

1. **Set Environment**
   ```bash
   export LIVE_TRADING=YES
   ```

2. **Verify Config**
   - Check config.yaml parameters
   - Confirm whitelist symbols
   - Verify risk limits

3. **Start with Monitoring**
   ```bash
   python run_funding_exec.py --live --notional_usdt 100
   ```

4. **Watch Closely**
   - First funding cycle
   - Order execution
   - P&L tracking

## Emergency Stop

```bash
# Method 1: Environment variable
export KILL=1

# Method 2: File trigger
touch .kill

# Method 3: Ctrl+C
```