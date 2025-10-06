# Configuration

Bot reads from `.env` and CLI flags.

## Environment variables
| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| LIVE_TRADING | no | `NO` | `YES` enables real orders (only after 48h dry-run). |
| TELEGRAM_TOKEN | yes* | — | Bot token from @BotFather (alerts). |
| TELEGRAM_CHAT_ID | yes* | — | Your chat/channel ID for alerts. |
| BINANCE_API_KEY | no (dry-run) | — | API key with minimal perms. |
| BINANCE_API_SECRET | no (dry-run) | — | API secret. |
| DEFAULT_NOTIONAL_USDT | no | `100` | Default notional for examples/tests. |
| DEFAULT_REBALANCE_WINDOW_MIN | no | `15` | Minutes before funding to rebalance. |
| DEFAULT_DELTA_THRESHOLD | no | `0.0005` | Trigger threshold (in BTC). |

> *Telegram keys only needed if you want alerts.

## CLI flags (examples)
```bash
python run_funding_exec.py --notional_usdt 100
python run_funding_exec.py --rebalance_window_min 10 --delta_threshold 0.0004
```

## .env sample
See `.env.sample`.
