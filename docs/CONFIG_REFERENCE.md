# Configuration Reference

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| BINANCE_API_KEY | For live | - | Binance API key |
| BINANCE_API_SECRET | For live | - | Binance API secret |
| TELEGRAM_TOKEN | No | - | Telegram bot token |
| TELEGRAM_CHAT_ID | No | - | Telegram chat ID |
| LIVE_TRADING | Yes | NO | Must be YES for live |
| KILL | No | 0 | Set to 1 to stop |

## Config YAML

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| symbol | str | BTC/USDT | Trading pair |
| notional_usdt | float | 100 | Position size |
| threshold_bps | float | 0.5 | Min edge to enter |
| fee_bps | float | 7 | Trading fees (bps) |
| slippage_bps | float | 2 | Expected slippage |
| leverage | int | 1 | Futures leverage |
| maker_only | bool | true | Post-only orders |
| whitelist_symbols | list | [BTC/USDT] | Allowed symbols |
| max_notional_usdt | float | 10000 | Max position |
| min_notional_usdt | float | 10 | Min position |
| log_level | str | INFO | Logging level |