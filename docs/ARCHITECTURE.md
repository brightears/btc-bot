# Architecture

## Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Executor  │────▶│   Exchange   │────▶│   Binance   │
│  (main loop)│     │   (ccxt)     │     │  Spot/Fut   │
└─────────────┘     └──────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Risk Guards │────▶│   Notifier   │────▶│  Telegram   │
│  (checks)   │     │   (alerts)   │     │    Bot      │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Data Flow

1. **Market Data**: Binance → CCXT → Executor
2. **Decisions**: Executor → Risk Guards → Orders
3. **Notifications**: Events → Telegram
4. **State**: Memory → JSON file

## Key Modules

- `exchange/binance.py`: API integration
- `funding/executor.py`: Main strategy loop
- `funding/model.py`: Math and data models
- `risk/guards.py`: Safety checks
- `notify/telegram.py`: Alerts
- `utils/`: Time, logging, filters