#!/usr/bin/env python3
"""
Binance API Connectivity Test for Portfolio Allocation Research
Tests API access and fetches basic BTC market data
"""

import json
import requests
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple

def fetch_current_price() -> float:
    """Fetch current BTC/USDT price from Binance"""
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": "BTCUSDT"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return None

def fetch_historical_klines(days: int = 30) -> List[Dict]:
    """Fetch historical kline data for BTC/USDT"""
    url = "https://api.binance.com/api/v3/klines"

    # Calculate time range
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

    params = {
        "symbol": "BTCUSDT",
        "interval": "1d",  # Daily candles
        "startTime": start_time,
        "endTime": end_time,
        "limit": days + 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        klines = response.json()

        # Parse kline data
        parsed_data = []
        for kline in klines:
            parsed_data.append({
                "timestamp": kline[0],
                "date": datetime.fromtimestamp(kline[0]/1000).strftime("%Y-%m-%d"),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5])
            })

        return parsed_data
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []

def calculate_metrics(historical_data: List[Dict]) -> Dict:
    """Calculate basic metrics from historical data"""
    if not historical_data:
        return {}

    # Extract closing prices
    closes = [d["close"] for d in historical_data]

    # Calculate returns
    returns = []
    for i in range(1, len(closes)):
        daily_return = (closes[i] - closes[i-1]) / closes[i-1] * 100
        returns.append(daily_return)

    # Calculate metrics
    metrics = {
        "average_price": np.mean(closes),
        "std_deviation": np.std(closes),
        "price_volatility_pct": (np.std(closes) / np.mean(closes)) * 100,
        "returns_volatility_pct": np.std(returns) if returns else 0,
        "total_return_pct": ((closes[-1] - closes[0]) / closes[0] * 100) if len(closes) > 1 else 0,
        "min_price": min(closes),
        "max_price": max(closes),
        "price_range": max(closes) - min(closes)
    }

    return metrics

def test_24h_stats() -> Dict:
    """Fetch 24-hour trading statistics"""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": "BTCUSDT"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "24h_change_pct": float(data["priceChangePercent"]),
            "24h_high": float(data["highPrice"]),
            "24h_low": float(data["lowPrice"]),
            "24h_volume_btc": float(data["volume"]),
            "24h_volume_usdt": float(data["quoteVolume"])
        }
    except Exception as e:
        print(f"Error fetching 24h stats: {e}")
        return {}

def main():
    """Main function to test API connectivity"""
    print("=" * 60)
    print("BINANCE API CONNECTIVITY TEST")
    print("Testing API access for Portfolio Allocation Research")
    print("=" * 60)
    print()

    # Test 1: Current Price
    print("1. FETCHING CURRENT BTC/USDT PRICE")
    print("-" * 40)
    current_price = fetch_current_price()
    if current_price:
        print(f"✓ Current BTC Price: ${current_price:,.2f}")
        print(f"✓ API endpoint responsive")
    else:
        print("✗ Failed to fetch current price")
    print()

    # Test 2: Historical Data
    print("2. FETCHING 30-DAY HISTORICAL DATA")
    print("-" * 40)
    historical_data = fetch_historical_klines(30)
    if historical_data:
        print(f"✓ Successfully fetched {len(historical_data)} days of data")
        print(f"✓ Date range: {historical_data[0]['date']} to {historical_data[-1]['date']}")
    else:
        print("✗ Failed to fetch historical data")
    print()

    # Test 3: Calculate Metrics
    print("3. CALCULATING MARKET METRICS")
    print("-" * 40)
    if historical_data:
        metrics = calculate_metrics(historical_data)

        print(f"30-Day Average Price:     ${metrics['average_price']:,.2f}")
        print(f"30-Day Price Volatility:  {metrics['price_volatility_pct']:.2f}%")
        print(f"30-Day Returns Volatility: {metrics['returns_volatility_pct']:.2f}% (daily)")
        print(f"30-Day Total Return:      {metrics['total_return_pct']:+.2f}%")
        print(f"30-Day Price Range:       ${metrics['min_price']:,.2f} - ${metrics['max_price']:,.2f}")
        print(f"                          (${metrics['price_range']:,.2f} range)")
    print()

    # Test 4: 24h Statistics
    print("4. FETCHING 24-HOUR STATISTICS")
    print("-" * 40)
    stats_24h = test_24h_stats()
    if stats_24h:
        print(f"24h Change:        {stats_24h['24h_change_pct']:+.2f}%")
        print(f"24h High/Low:      ${stats_24h['24h_high']:,.2f} / ${stats_24h['24h_low']:,.2f}")
        print(f"24h Volume (BTC):  {stats_24h['24h_volume_btc']:,.4f}")
        print(f"24h Volume (USDT): ${stats_24h['24h_volume_usdt']:,.2f}")
    print()

    # Summary
    print("=" * 60)
    print("API CONNECTIVITY TEST SUMMARY")
    print("=" * 60)

    api_working = all([
        current_price is not None,
        len(historical_data) > 0,
        len(stats_24h) > 0
    ])

    if api_working:
        print("✓ API ACCESS CONFIRMED: All endpoints working")
        print("✓ Current price data available")
        print("✓ Historical kline data available")
        print("✓ Market statistics available")
        print()
        print("READY FOR PORTFOLIO ALLOCATION RESEARCH:")
        print("- Can fetch real-time BTC prices")
        print("- Can access historical price data for backtesting")
        print("- Can calculate volatility and return metrics")
        print("- Can analyze market conditions and trends")
    else:
        print("✗ API ACCESS ISSUES DETECTED")
        print("Some endpoints may not be working properly")

    print()
    print("Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Return data for potential further use
    return {
        "current_price": current_price,
        "historical_data": historical_data,
        "metrics": metrics if historical_data else {},
        "stats_24h": stats_24h,
        "api_status": "WORKING" if api_working else "PARTIAL"
    }

if __name__ == "__main__":
    result = main()