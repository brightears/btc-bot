# Funding Carry Strategy

## Overview

The funding carry strategy captures the funding rate differential between spot and perpetual futures markets.

## How It Works

1. **Entry Signal**
   - Monitor funding rates every loop cycle
   - Calculate edge: `funding_bps - fees_bps - slippage_bps`
   - Enter when edge > threshold_bps

2. **Position Structure**
   - Long spot BTC (buy physical)
   - Short futures BTC (sell perpetual)
   - Equal notional values = delta neutral

3. **Profit Mechanism**
   - Collect funding payments (3x daily)
   - Shorts pay longs when funding > 0
   - Position is market-neutral

4. **Exit Conditions**
   - Funding window ends (<60s remaining)
   - Kill switch activated
   - Risk limits breached

## Risk Management

- Post-only orders (maker fees)
- Reduce-only on exit
- Position size limits
- Symbol whitelist
- Exchange filter compliance