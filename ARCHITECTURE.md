# Architecture

## High-level
- **Scheduler**: cron or systemd timer launches the executor every 5 min.
- **Executor** (`run_funding_exec.py`): single-shot workflow:
  1) Read config → 2) Fetch funding/market data → 3) Compute position deltas →
  4) Risk checks → 5) Place orders (dry-run by default) → 6) Emit logs/alerts.
- **Connectors**: thin wrappers around the exchange SDK / REST endpoints.
- **Alerts**: Telegram bot for status, errors, and summaries.
- **Logs**: structured logs → rotated daily via logrotate.

## Data flow
Funding API → signal calc → position sizing → (dry-run) order preview → logs + Telegram.

## Key decisions to capture as ADRs
- Which exchange SDK + endpoints for funding rates
- Cron vs systemd timers for scheduling
- Spot-only vs hedge pair, and risk caps
- Exact alert schema & message catalog
