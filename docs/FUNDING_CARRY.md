# Funding Carry Strategy

The bot captures positive funding differentials between Binance spot and USDⓈ-M perpetual futures while remaining delta-neutral.

## Trade Structure

- **Spot leg**: Long BTC/USDT on Binance spot.
- **Perp leg**: Short BTC/USDT on Binance USDⓈ-M futures with leverage fixed at 1x.
- **Objective**: Earn the net funding payments when the expected funding exceeds execution costs.

## Edge Calculation

```
net_edge_bps = funding_bps - fee_bps - slippage_bps
expected_usdt = notional_usdt * net_edge_bps / 10_000
```

- `funding_bps`: Latest funding rate from Binance, converted to basis points.
- `fee_bps`: Combined maker fees for both legs.
- `slippage_bps`: Cushion for adverse fills due to tick/step rounding.

If `net_edge_bps` meets or exceeds the configured `threshold_bps`, the executor enters the carry trade. Positions are closed just before the funding time or when the kill switch is engaged.

## Risk Considerations

1. **Execution quality**: Orders are posted as maker-only limits to avoid taker fees.
2. **Funding variance**: Actual funding can change after entry; the bot reassesses each loop.
3. **Notional caps**: Configurable guard ensures the deployed capital cannot exceed limits.
4. **Kill switch**: Setting `KILL=1` or touching the `.kill` file forces an exit and prevents new positions.
5. **Exchange filters**: Tick, step, and minimum notional constraints are applied before orders are submitted.

## Telemetry

- Rotating log file at `logs/funding_exec.log` summarises each decision.
- `logs/state.json` tracks the active position and latest funding metrics.
- Optional Telegram alerts provide human-readable incident reports and `/status` responses.
