#!/usr/bin/env python3
"""
Grid Trading Suitability Analysis for BTC/USDT and ETH/USDT
Analyzes recent market conditions to determine optimal grid bot parameters
"""

import urllib.request
import json
from datetime import datetime, timedelta
import statistics

# Binance API endpoint
base_url = 'https://api.binance.com/api/v3/klines'

def fetch_klines(symbol, interval='1h', days=7):
    """Fetch historical kline data from Binance"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

    url = f'{base_url}?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000'

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    # Extract OHLC data
    prices = []
    for candle in data:
        prices.append({
            'time': datetime.fromtimestamp(candle[0]/1000),
            'open': float(candle[1]),
            'high': float(candle[2]),
            'low': float(candle[3]),
            'close': float(candle[4]),
            'volume': float(candle[5])
        })

    return prices

def calculate_atr(data, period=14):
    """Calculate Average True Range"""
    if len(data) < period + 1:
        period = len(data) - 1

    true_ranges = []
    for i in range(1, len(data)):
        high_low = data[i]['high'] - data[i]['low']
        high_close = abs(data[i]['high'] - data[i-1]['close'])
        low_close = abs(data[i]['low'] - data[i-1]['close'])
        true_ranges.append(max(high_low, high_close, low_close))

    # Simple moving average of true ranges
    if len(true_ranges) >= period:
        atr = sum(true_ranges[-period:]) / period
    else:
        atr = sum(true_ranges) / len(true_ranges) if true_ranges else 0

    return atr

def analyze_trend(closes, window=20):
    """Simple trend analysis using moving average"""
    if len(closes) < window:
        window = len(closes)

    ma = sum(closes[-window:]) / window
    current_price = closes[-1]

    # Calculate price position relative to MA
    position = (current_price - ma) / ma * 100

    # Calculate directional movement
    recent_changes = [closes[i] - closes[i-1] for i in range(max(1, len(closes)-window), len(closes))]
    up_moves = sum(1 for c in recent_changes if c > 0)
    down_moves = sum(1 for c in recent_changes if c < 0)

    # Calculate linear regression slope (simple)
    if len(closes) >= 5:
        recent = closes[-min(24, len(closes)):]  # Last 24 hours
        x = list(range(len(recent)))
        x_mean = sum(x) / len(x)
        y_mean = sum(recent) / len(recent)

        numerator = sum((x[i] - x_mean) * (recent[i] - y_mean) for i in range(len(recent)))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(len(recent)))

        if denominator != 0:
            slope = numerator / denominator
            slope_pct = (slope / y_mean) * 100  # Slope as percentage of mean price
        else:
            slope_pct = 0
    else:
        slope_pct = 0

    return {
        'ma': ma,
        'position_vs_ma': position,
        'up_ratio': up_moves / len(recent_changes) if recent_changes else 0.5,
        'trend_slope': slope_pct
    }

def check_ranging_market(data, closes):
    """Determine if market is ranging or trending"""
    # Calculate various metrics
    high_7d = max(p['high'] for p in data)
    low_7d = min(p['low'] for p in data)
    range_pct = (high_7d - low_7d) / low_7d * 100

    # Check how many times price crossed the midpoint
    midpoint = (high_7d + low_7d) / 2
    crosses = 0
    for i in range(1, len(closes)):
        if (closes[i-1] < midpoint and closes[i] > midpoint) or \
           (closes[i-1] > midpoint and closes[i] < midpoint):
            crosses += 1

    # Calculate standard deviation of returns
    returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 for i in range(1, len(closes))]
    if returns:
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        mean_return = statistics.mean(returns)
    else:
        volatility = 0
        mean_return = 0

    # Ranging market criteria
    is_ranging = (
        range_pct < 15 and  # Price range less than 15%
        crosses >= 3 and  # At least 3 midpoint crosses
        abs(mean_return) < 0.5 and  # Mean hourly return close to 0
        volatility < 2.0  # Reasonable volatility
    )

    return {
        'is_ranging': is_ranging,
        'range_pct': range_pct,
        'midpoint_crosses': crosses,
        'volatility': volatility,
        'mean_return': mean_return
    }

def calculate_grid_parameters(current_price, atr, range_pct, volatility):
    """Calculate optimal grid parameters based on market conditions"""
    # Determine optimal grid count based on volatility
    if volatility < 0.5:
        grid_count = 80  # Low volatility = more grids
    elif volatility < 1.0:
        grid_count = 60  # Medium volatility
    else:
        grid_count = 40  # High volatility = fewer grids

    # Determine price range based on ATR and historical range
    # Use 1.5x ATR as base, adjusted for market conditions
    atr_range = (atr / current_price) * 100
    optimal_range = min(atr_range * 2, range_pct * 0.8)  # Conservative: 80% of historical range

    upper_price = current_price * (1 + optimal_range / 200)
    lower_price = current_price * (1 - optimal_range / 200)

    # Calculate profit per grid
    grid_gap_pct = (optimal_range * 2) / grid_count
    # Account for fees (0.075% with BNB discount)
    profit_per_grid = grid_gap_pct - (0.075 * 2)  # Buy and sell fees

    return {
        'grid_count': grid_count,
        'upper_price': upper_price,
        'lower_price': lower_price,
        'range_pct': optimal_range * 2,
        'profit_per_grid_pct': profit_per_grid,
        'grid_gap_pct': grid_gap_pct
    }

def main():
    print("=" * 60)
    print("GRID TRADING SUITABILITY ANALYSIS")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Fetch data for both pairs
    print("\nFetching market data...")
    btc_data = fetch_klines('BTCUSDT', '1h', 7)
    eth_data = fetch_klines('ETHUSDT', '1h', 7)
    print(f"Retrieved {len(btc_data)} BTC candles and {len(eth_data)} ETH candles")

    # Analyze BTC
    print("\n" + "=" * 60)
    print("BTC/USDT ANALYSIS")
    print("=" * 60)

    btc_closes = [p['close'] for p in btc_data]
    btc_atr = calculate_atr(btc_data)
    btc_trend = analyze_trend(btc_closes)
    btc_ranging = check_ranging_market(btc_data, btc_closes)

    print(f"\nCurrent Price: ${btc_closes[-1]:,.2f}")
    print(f"7-Day High: ${max(p['high'] for p in btc_data):,.2f}")
    print(f"7-Day Low: ${min(p['low'] for p in btc_data):,.2f}")
    print(f"7-Day Range: {btc_ranging['range_pct']:.2f}%")
    print(f"ATR (14): ${btc_atr:,.2f} ({(btc_atr / btc_closes[-1] * 100):.2f}% of price)")
    print(f"20-period MA: ${btc_trend['ma']:,.2f}")
    print(f"Price vs MA: {btc_trend['position_vs_ma']:+.2f}%")
    print(f"Trend Slope: {btc_trend['trend_slope']:+.3f}% per hour")
    print(f"Hourly Volatility: {btc_ranging['volatility']:.3f}%")
    print(f"Midpoint Crosses: {btc_ranging['midpoint_crosses']}")

    print(f"\n### Market Regime: {'RANGING' if btc_ranging['is_ranging'] else 'TRENDING'}")

    if btc_ranging['is_ranging']:
        btc_params = calculate_grid_parameters(
            btc_closes[-1],
            btc_atr,
            btc_ranging['range_pct'],
            btc_ranging['volatility']
        )
        print("\n### RECOMMENDED GRID PARAMETERS:")
        print(f"Grid Count: {btc_params['grid_count']}")
        print(f"Upper Price: ${btc_params['upper_price']:,.2f}")
        print(f"Lower Price: ${btc_params['lower_price']:,.2f}")
        print(f"Price Range: ±{btc_params['range_pct']/2:.2f}%")
        print(f"Grid Gap: {btc_params['grid_gap_pct']:.3f}%")
        print(f"Expected Profit per Grid: {btc_params['profit_per_grid_pct']:.3f}%")
        print(f"Recommended Allocation: $5,000-$10,000")
    else:
        print("\n### NOT SUITABLE FOR GRID TRADING")
        if abs(btc_trend['trend_slope']) > 0.1:
            print(f"Reason: Strong {'uptrend' if btc_trend['trend_slope'] > 0 else 'downtrend'} detected")
        if btc_ranging['range_pct'] > 15:
            print(f"Reason: Excessive volatility (range: {btc_ranging['range_pct']:.1f}%)")
        if btc_ranging['midpoint_crosses'] < 3:
            print(f"Reason: Insufficient price oscillation (only {btc_ranging['midpoint_crosses']} crosses)")

    # Analyze ETH
    print("\n" + "=" * 60)
    print("ETH/USDT ANALYSIS")
    print("=" * 60)

    eth_closes = [p['close'] for p in eth_data]
    eth_atr = calculate_atr(eth_data)
    eth_trend = analyze_trend(eth_closes)
    eth_ranging = check_ranging_market(eth_data, eth_closes)

    print(f"\nCurrent Price: ${eth_closes[-1]:,.2f}")
    print(f"7-Day High: ${max(p['high'] for p in eth_data):,.2f}")
    print(f"7-Day Low: ${min(p['low'] for p in eth_data):,.2f}")
    print(f"7-Day Range: {eth_ranging['range_pct']:.2f}%")
    print(f"ATR (14): ${eth_atr:,.2f} ({(eth_atr / eth_closes[-1] * 100):.2f}% of price)")
    print(f"20-period MA: ${eth_trend['ma']:,.2f}")
    print(f"Price vs MA: {eth_trend['position_vs_ma']:+.2f}%")
    print(f"Trend Slope: {eth_trend['trend_slope']:+.3f}% per hour")
    print(f"Hourly Volatility: {eth_ranging['volatility']:.3f}%")
    print(f"Midpoint Crosses: {eth_ranging['midpoint_crosses']}")

    print(f"\n### Market Regime: {'RANGING' if eth_ranging['is_ranging'] else 'TRENDING'}")

    if eth_ranging['is_ranging']:
        eth_params = calculate_grid_parameters(
            eth_closes[-1],
            eth_atr,
            eth_ranging['range_pct'],
            eth_ranging['volatility']
        )
        print("\n### RECOMMENDED GRID PARAMETERS:")
        print(f"Grid Count: {eth_params['grid_count']}")
        print(f"Upper Price: ${eth_params['upper_price']:,.2f}")
        print(f"Lower Price: ${eth_params['lower_price']:,.2f}")
        print(f"Price Range: ±{eth_params['range_pct']/2:.2f}%")
        print(f"Grid Gap: {eth_params['grid_gap_pct']:.3f}%")
        print(f"Expected Profit per Grid: {eth_params['profit_per_grid_pct']:.3f}%")
        print(f"Recommended Allocation: $3,000-$5,000")
    else:
        print("\n### NOT SUITABLE FOR GRID TRADING")
        if abs(eth_trend['trend_slope']) > 0.1:
            print(f"Reason: Strong {'uptrend' if eth_trend['trend_slope'] > 0 else 'downtrend'} detected")
        if eth_ranging['range_pct'] > 15:
            print(f"Reason: Excessive volatility (range: {eth_ranging['range_pct']:.1f}%)")
        if eth_ranging['midpoint_crosses'] < 3:
            print(f"Reason: Insufficient price oscillation (only {eth_ranging['midpoint_crosses']} crosses)")

    # Overall recommendations
    print("\n" + "=" * 60)
    print("OVERALL RECOMMENDATIONS")
    print("=" * 60)

    suitable_count = sum([btc_ranging['is_ranging'], eth_ranging['is_ranging']])

    if suitable_count == 2:
        print("\n✓ Both pairs are suitable for grid trading")
        print("✓ Market conditions favor range-bound strategies")
        print("✓ Deploy with recommended parameters above")
        print("\nRisk Management:")
        print("- Monitor daily for trend breakouts")
        print("- Set stop-loss at -5% from grid boundaries")
        print("- Rebalance if price exits grid range")
    elif suitable_count == 1:
        suitable_pair = "BTC/USDT" if btc_ranging['is_ranging'] else "ETH/USDT"
        print(f"\n⚠ Only {suitable_pair} is suitable for grid trading")
        print("⚠ Consider deploying only on the suitable pair")
        print("⚠ Wait for better conditions on the other pair")
    else:
        print("\n✗ Neither pair is suitable for grid trading currently")
        print("✗ Market is trending, not ranging")
        print("\nConditions needed for grid trading:")
        print("- Price range < 15% over 7 days")
        print("- Multiple oscillations around midpoint")
        print("- Low directional bias (trend slope < 0.1% per hour)")
        print("- Moderate volatility (0.3% - 2% hourly moves)")
        print("\nAlternative strategies to consider:")
        print("- DCA (Dollar Cost Averaging) for trending markets")
        print("- Momentum trading for strong trends")
        print("- Wait for consolidation phase")

if __name__ == "__main__":
    main()