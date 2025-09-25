#!/usr/bin/env python3
"""
Volume Calculation Test Script

This script tests the volume calculation in realtime_market_data.py
to verify that BTC volume is correctly calculated in USD (not just BTC).

Expected results:
- Volume should be in billions of USD (typically $10B-$50B daily)
- The calculation should be: BTC_volume * BTC_price = USD_volume
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_brain.realtime_market_data import RealtimeMarketData


async def test_binance_api_directly():
    """Test Binance API directly to understand the raw data"""
    print("=" * 60)
    print("TESTING BINANCE API DIRECTLY")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        try:
            # Test the same endpoint used in realtime_market_data.py
            url = "https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': 'BTCUSDT'}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Extract key values
                    last_price = float(data['lastPrice'])
                    volume_btc = float(data['volume'])
                    volume_usd_from_api = float(data.get('quoteVolume', 0))

                    # Calculate USD volume ourselves
                    calculated_volume_usd = volume_btc * last_price

                    print(f"Raw Binance Data:")
                    print(f"  Last Price: ${last_price:,.2f}")
                    print(f"  BTC Volume (24h): {volume_btc:,.2f} BTC")
                    print(f"  Quote Volume from API: ${volume_usd_from_api:,.0f}")
                    print(f"  Calculated USD Volume: ${calculated_volume_usd:,.0f}")
                    print(f"  Calculated Volume (Billions): ${calculated_volume_usd/1e9:.2f}B")

                    # Check if our calculation matches API quote volume
                    difference = abs(calculated_volume_usd - volume_usd_from_api)
                    difference_percent = (difference / volume_usd_from_api) * 100 if volume_usd_from_api > 0 else 0

                    print(f"\nVolume Calculation Verification:")
                    print(f"  Difference: ${difference:,.0f} ({difference_percent:.2f}%)")

                    if difference_percent < 1:
                        print("  ✅ Our calculation matches Binance quote volume!")
                    else:
                        print("  ❌ Significant difference - need to investigate")

                    # Volume sanity checks
                    print(f"\nVolume Sanity Checks:")
                    if calculated_volume_usd > 1e9:  # > $1B
                        print(f"  ✅ Volume ${calculated_volume_usd/1e9:.1f}B is reasonable for BTC")
                    else:
                        print(f"  ❌ Volume ${calculated_volume_usd/1e9:.1f}B seems too low for BTC")

                    if calculated_volume_usd < 100e9:  # < $100B
                        print(f"  ✅ Volume ${calculated_volume_usd/1e9:.1f}B is within expected range")
                    else:
                        print(f"  ⚠️  Volume ${calculated_volume_usd/1e9:.1f}B is unusually high")

                    return {
                        'price': last_price,
                        'volume_btc': volume_btc,
                        'volume_usd': calculated_volume_usd,
                        'api_quote_volume': volume_usd_from_api
                    }
                else:
                    print(f"❌ API Error: {response.status}")
                    return None

        except Exception as e:
            print(f"❌ Exception: {e}")
            return None


async def test_realtime_market_data():
    """Test our RealtimeMarketData class"""
    print("\n" + "=" * 60)
    print("TESTING REALTIME MARKET DATA CLASS")
    print("=" * 60)

    # Setup logging to see detailed volume calculations
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    market_data = RealtimeMarketData()

    try:
        # Get market data
        data = await market_data.get_market_data()

        print(f"Market Data Results:")
        print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"  Price: ${data.get('price', 0):,.2f}")
        print(f"  Volume (24h): ${data.get('volume', 0):,.0f}")
        print(f"  Volume (Billions): ${data.get('volume', 0)/1e9:.2f}B")
        print(f"  High 24h: ${data.get('high_24h', 0):,.2f}")
        print(f"  Low 24h: ${data.get('low_24h', 0):,.2f}")
        print(f"  Change 24h: {data.get('change_24h', 0):.2f}%")
        print(f"  Is Real Data: {data.get('is_real_data', False)}")

        # Data quality assessment
        quality = data.get('data_quality', {})
        print(f"\nData Quality:")
        print(f"  Score: {quality.get('score', 0)}/100")
        if quality.get('issues'):
            print(f"  Issues: {', '.join(quality.get('issues', []))}")

        # Volume validation
        volume = data.get('volume', 0)
        print(f"\nVolume Validation:")
        if volume >= 1e9:  # >= $1B
            print(f"  ✅ Volume ${volume/1e9:.1f}B is reasonable for BTC")
        else:
            print(f"  ❌ Volume ${volume/1e9:.1f}B seems too low for BTC")

        if volume <= 100e9:  # <= $100B
            print(f"  ✅ Volume ${volume/1e9:.1f}B is within expected range")
        else:
            print(f"  ⚠️  Volume ${volume/1e9:.1f}B is unusually high")

        return data

    except Exception as e:
        print(f"❌ Error testing RealtimeMarketData: {e}")
        return None


async def compare_volume_calculations(api_data, market_data):
    """Compare the volume calculations between direct API and our class"""
    print("\n" + "=" * 60)
    print("VOLUME CALCULATION COMPARISON")
    print("=" * 60)

    if not api_data or not market_data:
        print("❌ Cannot compare - missing data")
        return

    api_volume = api_data.get('volume_usd', 0)
    class_volume = market_data.get('volume', 0)

    print(f"Direct API Volume: ${api_volume:,.0f} (${api_volume/1e9:.2f}B)")
    print(f"Class Volume:      ${class_volume:,.0f} (${class_volume/1e9:.2f}B)")

    if api_volume > 0:
        difference = abs(api_volume - class_volume)
        difference_percent = (difference / api_volume) * 100

        print(f"Difference: ${difference:,.0f} ({difference_percent:.2f}%)")

        if difference_percent < 1:
            print("✅ Volume calculations match!")
        else:
            print("❌ Volume calculations don't match - investigation needed")
    else:
        print("❌ Cannot compare - no API volume data")


async def test_volume_edge_cases():
    """Test edge cases for volume calculation"""
    print("\n" + "=" * 60)
    print("TESTING VOLUME EDGE CASES")
    print("=" * 60)

    test_cases = [
        {"price": 50000, "volume_btc": 500000, "expected_usd": 25e9},  # $25B
        {"price": 100000, "volume_btc": 200000, "expected_usd": 20e9},  # $20B
        {"price": 30000, "volume_btc": 1000000, "expected_usd": 30e9},  # $30B
    ]

    for i, case in enumerate(test_cases, 1):
        price = case["price"]
        volume_btc = case["volume_btc"]
        expected = case["expected_usd"]

        calculated = price * volume_btc

        print(f"Test Case {i}:")
        print(f"  Price: ${price:,}")
        print(f"  BTC Volume: {volume_btc:,} BTC")
        print(f"  Calculated USD Volume: ${calculated:,.0f} (${calculated/1e9:.1f}B)")
        print(f"  Expected USD Volume: ${expected:,.0f} (${expected/1e9:.1f}B)")

        if abs(calculated - expected) < 1000:  # Within $1000
            print(f"  ✅ Calculation correct")
        else:
            print(f"  ❌ Calculation error")
        print()


async def main():
    """Main test function"""
    print("BTC Volume Calculation Test")
    print("=" * 60)
    print("This script tests that BTC volume is correctly calculated in USD")
    print("Expected: Volume should be in billions of USD ($10B-$50B typical)")
    print()

    try:
        # Test 1: Direct Binance API call
        api_data = await test_binance_api_directly()

        # Test 2: Our RealtimeMarketData class
        market_data = await test_realtime_market_data()

        # Test 3: Compare results
        await compare_volume_calculations(api_data, market_data)

        # Test 4: Edge cases
        await test_volume_edge_cases()

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        if api_data and market_data:
            api_vol = api_data.get('volume_usd', 0) / 1e9
            class_vol = market_data.get('volume', 0) / 1e9

            print(f"✅ Successfully fetched data from both sources")
            print(f"📊 API Volume: ${api_vol:.2f}B")
            print(f"📊 Class Volume: ${class_vol:.2f}B")

            if 1 <= api_vol <= 100:
                print(f"✅ Volume is in reasonable range for BTC")
            else:
                print(f"⚠️  Volume may be outside normal range")

        else:
            print("❌ Failed to fetch data from one or more sources")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())