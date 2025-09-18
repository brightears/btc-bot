# BTC Funding Carry Bot

Delta-neutral funding carry executor for Binance spot and USDⓈ-M futures using ccxt. The bot monitors upcoming funding windows, evaluates the edge after fees and slippage, and enters a maker-only long-spot/short-perp pair trade once the configured threshold is exceeded. Dry-run mode is the default; live trading requires explicit opt-in.

## Quickstart

1. Bootstrap environment:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   ```
2. Run the dry-run executor (uses `config.yaml` and `.env` if present):
   ```bash
   ./run_funding_exec.py
   ```
3. Guarded live command (requires `LIVE_TRADING=YES` plus all Binance keys):
   ```bash
   LIVE_TRADING=YES ./run_funding_exec.py --live
   ```

## Runtime Notes

- Populate `.env` (see `.env.sample`) with Binance spot/USDⓈ-M API keys and optional Telegram credentials. Secrets stay local and are ignored by git.
- If required environment variables are missing, the bot stays in dry-run mode and logs the deficiency without revealing secrets.
- Configuration defaults live in `config.yaml`; see `docs/CONFIG_REFERENCE.md` for details.
- Logs are rotated in `logs/` and the JSON state snapshot lives at `logs/state.json`.

## Next Steps

- Review runbooks in `docs/RUNBOOK_DRYRUN.md` and `docs/RUNBOOK_GO_LIVE.md`.
- Consult `docs/SECURITY_CHECKLIST.md` before enabling live trading.
- Use `pytest` to validate the cost model and executor logic.
