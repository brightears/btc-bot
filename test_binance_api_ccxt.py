#!/usr/bin/env python3
"""
Binance API Connectivity Test for Bot Validation
Uses ccxt library to test API access and fetch BTC market data
"""

import ccxt
from datetime import datetime, timedelta
import json

def test_binance_connectivity():
    """Test Binance API connectivity for bot validation purposes"""

    print("=" * 60)
    print("BINANCE API CONNECTIVITY TEST FOR BOT VALIDATION")
    print("=" * 60)
    print()

    # Initialize Binance exchange (public API, no authentication needed for market data)
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        print("✓ Binance exchange object initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Binance exchange: {e}")
        return

    # Test 1: Fetch current BTC/USDT price
    print("\n1. CURRENT BTC/USDT PRICE")
    print("-" * 40)
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        bid = ticker['bid']
        ask = ticker['ask']
        volume_24h = ticker['baseVolume']
        change_24h = ticker['percentage']

        print(f"✓ Current Price: ${current_price:,.2f}")
        print(f"  Bid/Ask: ${bid:,.2f} / ${ask:,.2f}")
        print(f"  Spread: ${ask - bid:.2f} ({((ask - bid) / current_price * 100):.3f}%)")
        print(f"  24h Change: {change_24h:+.2f}%")
        print(f"  24h Volume: {volume_24h:,.4f} BTC")
    except Exception as e:
        print(f"✗ Failed to fetch current price: {e}")
        current_price = None

    # Test 2: Fetch historical OHLCV data
    print("\n2. HISTORICAL DATA ACCESS (30 DAYS)")
    print("-" * 40)
    try:
        # Fetch 30 days of daily candles
        since = exchange.parse8601((datetime.now() - timedelta(days=30)).isoformat())
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1d', since=since, limit=30)

        if ohlcv:
            print(f"✓ Successfully fetched {len(ohlcv)} days of historical data")

            # Calculate some basic statistics
            closes = [candle[4] for candle in ohlcv]
            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]

            avg_price = sum(closes) / len(closes)
            max_price = max(highs)
            min_price = min(lows)
            price_range = max_price - min_price
            volatility = (price_range / avg_price) * 100

            # Calculate 30-day return
            return_30d = ((closes[-1] - closes[0]) / closes[0]) * 100

            print(f"\n  30-Day Statistics:")
            print(f"  - Average Price: ${avg_price:,.2f}")
            print(f"  - Price Range: ${min_price:,.2f} - ${max_price:,.2f}")
            print(f"  - Range Width: ${price_range:,.2f} ({volatility:.2f}% of avg)")
            print(f"  - 30-Day Return: {return_30d:+.2f}%")
    except Exception as e:
        print(f"✗ Failed to fetch historical data: {e}")
        ohlcv = None

    # Test 3: Check order book depth (important for grid bots)
    print("\n3. ORDER BOOK DEPTH")
    print("-" * 40)
    try:
        order_book = exchange.fetch_order_book('BTC/USDT', limit=10)

        # Calculate cumulative depth at different levels
        bid_depth_1pct = current_price * 0.99 if current_price else 0
        ask_depth_1pct = current_price * 1.01 if current_price else 0

        bid_volume = sum([bid[1] for bid in order_book['bids']])
        ask_volume = sum([ask[1] for ask in order_book['asks']])

        print(f"✓ Order book fetched successfully")
        print(f"  Top 10 Bids Volume: {bid_volume:.4f} BTC")
        print(f"  Top 10 Asks Volume: {ask_volume:.4f} BTC")
        print(f"  Best Bid: ${order_book['bids'][0][0]:,.2f}" if order_book['bids'] else "  No bids")
        print(f"  Best Ask: ${order_book['asks'][0][0]:,.2f}" if order_book['asks'] else "  No asks")
    except Exception as e:
        print(f"✗ Failed to fetch order book: {e}")

    # Test 4: Check available timeframes (for different analysis periods)
    print("\n4. AVAILABLE TIMEFRAMES")
    print("-" * 40)
    try:
        timeframes = exchange.timeframes
        print(f"✓ Available timeframes for analysis:")
        print(f"  {', '.join(list(timeframes.keys())[:10])}")
        if len(timeframes) > 10:
            print(f"  ... and {len(timeframes) - 10} more")
    except Exception as e:
        print(f"✗ Failed to fetch timeframes: {e}")

    # Test 5: Check API rate limits
    print("\n5. API RATE LIMITS")
    print("-" * 40)
    try:
        if hasattr(exchange, 'rateLimit'):
            print(f"✓ Rate limit: {exchange.rateLimit}ms between requests")
        else:
            print("  Rate limit information not available")

        # Check if we can access exchange info
        if exchange.has['fetchStatus']:
            status = exchange.fetch_status()
            print(f"✓ Exchange status: {status.get('status', 'Unknown')}")
    except Exception as e:
        print(f"  Note: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION CAPABILITY ASSESSMENT")
    print("=" * 60)

    capabilities = {
        "current_price": current_price is not None,
        "historical_data": ohlcv is not None and len(ohlcv) > 0,
        "order_book": 'order_book' in locals(),
        "multiple_timeframes": 'timeframes' in locals() and len(timeframes) > 0
    }

    all_working = all(capabilities.values())

    if all_working:
        print("✓ ALL SYSTEMS OPERATIONAL")
        print("\nValidation Capabilities Confirmed:")
        print("✓ Real-time price monitoring for P&L tracking")
        print("✓ Historical data for backtesting validation")
        print("✓ Order book depth for grid bot feasibility")
        print("✓ Multiple timeframes for comprehensive analysis")
        print("\nData Available for Bot Validation:")
        print("- Current market conditions and volatility")
        print("- 30-day price history and trends")
        print("- Market depth and liquidity metrics")
        print("- Multiple analysis periods (1m to 1M)")
    else:
        print("⚠ PARTIAL FUNCTIONALITY")
        print("\nWorking:")
        for feature, status in capabilities.items():
            if status:
                print(f"✓ {feature.replace('_', ' ').title()}")
        print("\nNot Working:")
        for feature, status in capabilities.items():
            if not status:
                print(f"✗ {feature.replace('_', ' ').title()}")

    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Note about API credentials
    print("\n" + "=" * 60)
    print("API CREDENTIALS STATUS")
    print("=" * 60)
    print("Note: Currently using PUBLIC API endpoints")
    print("- No authentication required for market data")
    print("- Sufficient for bot performance validation")
    print("- Private API would be needed for:")
    print("  • Checking actual bot positions")
    print("  • Retrieving trade history")
    print("  • Account balance verification")

if __name__ == "__main__":
    test_binance_connectivity()