# Dry-Run Runbook

1. **Prep environment**
   - `cp .env.sample .env` and populate optional Telegram fields (leave Binance keys blank for dry-run).
   - Review `config.yaml`; adjust `threshold_bps`, `notional_usdt`, or loop timings as needed.

2. **Install dependencies**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the executor**
   ```bash
   ./run_funding_exec.py --max-loops 2
   ```
   - Logs stream to stdout and `logs/funding_exec.log`.
   - `logs/state.json` tracks the simulated position state.

4. **Monitor**
   - Tail `logs/funding_exec.log` for funding edges and decision outcomes.
   - Run `scripts/health_ping.sh` to report the current mode and state snapshot.

5. **Stop**
   - Press `Ctrl+C` to interrupt the loop, or set `KILL=1` / touch `.kill` to exit gracefully on the next cycle.
