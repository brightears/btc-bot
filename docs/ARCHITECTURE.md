# Architecture

## High-Level Flow

1. `run_funding_exec.py` loads `config.yaml`, environment variables, and initialises logging.
2. `BinanceExchange` (ccxt) fetches market metadata, funding rates, and handles order placement.
3. `FundingExecutor` loops on a timer to evaluate the funding edge and manage positions.
4. Risk guards enforce kill switch, whitelist, notional limits, and maker-only discipline.
5. `TelegramNotifier` emits alerts and status messages when credentials are configured.
6. State snapshots and logs are persisted under `logs/` for observability and recovery.

## Modules

- `utils.logger`: Configures rotating logs for CLI and worker usage.
- `utils.time`: UTC helpers and funding window calculations.
- `utils.filters`: Applies tick/step/min-notional filters before creating orders.
- `exchange.binance`: Thin wrapper over ccxt clients for spot and USDⓈ-M futures.
- `funding.model`: Pure functions for edge math and funding window logic.
- `funding.executor`: Orchestrates pricing, risk checks, and order execution.
- `risk.guards`: Stateless guardrails for kill switch, whitelist, and notional caps.
- `notify.telegram`: Optional Telegram message delivery.

## State & Persistence

- `logs/funding_exec.log`: Rotating file handler for operational logs.
- `logs/state.json`: Durable record of the latest funding metrics and open position.
- `.kill`: Presence of this file triggers the kill switch for the next loop.

## Extensibility

- Add new exchanges by implementing the `get_funding_info`, `get_prices`, `open_carry_position`, and `close_carry_position` methods.
- Augment risk controls in `risk/guards.py` and inject them into the executor.
- Extend notifications by adding adapters under `src/notify/` and wiring them into `_notify`.
