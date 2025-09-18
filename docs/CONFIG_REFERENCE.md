# Config Reference

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `symbol` | string | `"BTC/USDT"` | Trading pair for both spot and perp legs (must exist on Binance spot/USDⓈ-M). |
| `notional_usdt` | float | `100` | USDT value of the carry trade; also used as the default notional cap. |
| `threshold_bps` | float | `0.5` | Minimum net edge (in basis points) required to open a position. |
| `loop_seconds` | int | `300` | Sleep interval between funding checks. |
| `maker_only` | bool | `true` | If true, submits post-only orders to avoid taker fees. |
| `leverage` | int | `1` | Leverage applied to the USDⓈ-M leg; executor enforces 1x. |
| `fee_bps` | float | `7` | Combined maker fee assumption applied in edge calculations. |
| `slippage_bps` | float | `2` | Cushion for orderbook slippage and rounding. |
| `whitelist_symbols` | list[str] | `["BTC/USDT"]` | Symbols allowed to trade; acts as an additional guard. |
| `log_level` | string | `"INFO"` | Logging level for console and file handlers. |
| `notional_cap_usdt` | float | `notional_usdt` | Optional cap for maximum notional; absence defaults to `notional_usdt`. |

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `LIVE_TRADING` | Must be set to `YES` **and** `--live` flag must be passed to enable live trading. |
| `BINANCE_API_KEY` / `BINANCE_API_SECRET` | Credentials for Binance spot account. |
| `BINANCE_USDM_API_KEY` / `BINANCE_USDM_API_SECRET` | Credentials for Binance USDⓈ-M futures account. |
| `TELEGRAM_TOKEN` / `TELEGRAM_CHAT_ID` | Optional notifier credentials; absence disables alerts. |
| `KILL` | Set to `1`, `true`, or `yes` to trigger the kill switch regardless of `.kill` file state. |

Missing credentials simply keep the bot in dry-run mode.
