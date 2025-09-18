# Go-Live Runbook

1. **Pre-flight checks**
   - Complete the `docs/SECURITY_CHECKLIST.md` items.
   - Confirm `.env` contains valid keys for both Binance spot and USDⓈ-M accounts.
   - Ensure `LIVE_TRADING=YES` is set either in the shell or `.env`.
   - Validate leverage and maker fees on the Binance account (should be 1x and maker rebate or lowest tier possible).

2. **Sanity tests**
   - Run `pytest` and confirm all tests pass.
   - Execute one dry-run loop to verify connectivity:
     ```bash
     ./run_funding_exec.py --max-loops 1
     ```

3. **Activate live mode**
   ```bash
   LIVE_TRADING=YES ./run_funding_exec.py --live
   ```
   - Watch the console for funding edge calculations and order submission logs.
   - Telegram (if configured) should announce entry/exit decisions.

4. **Operate**
   - Keep `scripts/health_ping.sh` running (e.g., via cron) for lightweight telemetry.
   - Monitor Binance order history to confirm fills remain maker-only and reduce-only on exits.
   - Maintain awareness of upcoming maintenance windows or funding rate spikes.

5. **Emergency procedures**
   - Set `KILL=1` or create a `.kill` file to force the executor to flatten on the next loop.
   - Revoke API keys at the exchange if compromise is suspected.
   - If orders hang or the position drifts, manually close both legs and inspect logs/state for root cause.
