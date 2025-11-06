#!/usr/bin/env python3
"""Market Regime Analysis Tool for BTC/USDT and ETH/USDT"""

import json
import urllib.request
import math
from datetime import datetime, timedelta
import sys

def fetch_ticker_data(symbol):
    """Fetch 24hr ticker data"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def fetch_klines(symbol, interval="1d", limit=30):
    """Fetch historical klines data"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def calculate_std_dev(values):
    """Calculate standard deviation"""
    if not values:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def calculate_mean(values):
    """Calculate mean"""
    if not values:
        return 0
    return sum(values) / len(values)

def calculate_volatility(klines):
    """Calculate daily volatility metrics"""
    closes = [float(k[4]) for k in klines]

    # Calculate daily returns
    returns = []
    for i in range(1, len(closes)):
        daily_return = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
        returns.append(daily_return)

    # Standard deviation of returns
    daily_volatility = calculate_std_dev(returns) if returns else 0

    # 7-day vs 30-day volatility
    recent_7d_vol = calculate_std_dev(returns[-7:]) if len(returns) >= 7 else daily_volatility

    # Annualized volatility (sqrt(365) * daily vol)
    annualized_vol = daily_volatility * math.sqrt(365)

    return {
        "daily_volatility": daily_volatility,
        "7d_volatility": recent_7d_vol,
        "30d_volatility": daily_volatility,
        "annualized_volatility": annualized_vol,
        "returns": returns
    }

def calculate_trend(klines):
    """Calculate trend indicators"""
    closes = [float(k[4]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    current_price = closes[-1]

    # 20-day SMA
    sma20_prices = closes[-20:] if len(closes) >= 20 else closes
    sma20 = calculate_mean(sma20_prices)

    # Price position relative to SMA
    sma_distance = ((current_price - sma20) / sma20) * 100

    # Volume analysis
    recent_7d_vol = calculate_mean(volumes[-7:]) if len(volumes) >= 7 else calculate_mean(volumes)
    older_23d_vol = calculate_mean(volumes[-30:-7]) if len(volumes) >= 30 else calculate_mean(volumes[:-7]) if len(volumes) > 7 else calculate_mean(volumes)
    volume_change = ((recent_7d_vol - older_23d_vol) / older_23d_vol) * 100 if older_23d_vol > 0 else 0

    # RSI calculation (14-period)
    rsi = calculate_rsi(closes, 14)

    # Support and resistance (recent highs/lows)
    recent_highs = highs[-10:] if len(highs) >= 10 else highs
    recent_lows = lows[-10:] if len(lows) >= 10 else lows
    recent_high = max(recent_highs) if recent_highs else 0
    recent_low = min(recent_lows) if recent_lows else 0

    # 30-day price change
    price_30d_ago = closes[0] if len(closes) > 0 else current_price
    change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100

    return {
        "current_price": current_price,
        "sma20": sma20,
        "sma_distance": sma_distance,
        "volume_change": volume_change,
        "rsi": rsi,
        "recent_high": recent_high,
        "recent_low": recent_low,
        "change_30d": change_30d
    }

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    if len(prices) < period + 1:
        return 50  # Neutral if not enough data

    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # Use recent period for calculation
    recent_gains = gains[-period:] if len(gains) >= period else gains
    recent_losses = losses[-period:] if len(losses) >= period else losses

    avg_gain = calculate_mean(recent_gains) if recent_gains else 0
    avg_loss = calculate_mean(recent_losses) if recent_losses else 0

    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def classify_regime(volatility, trend):
    """Classify market regime based on metrics"""
    daily_vol = volatility["daily_volatility"]
    sma_distance = trend["sma_distance"]
    change_30d = trend["change_30d"]
    rsi = trend["rsi"]

    regime = ""
    confidence = 0
    reasoning = []

    # Check for high uncertainty first
    if daily_vol > 5:
        regime = "HIGH_UNCERTAINTY"
        confidence = 95
        reasoning.append(f"Extreme volatility at {daily_vol:.2f}% daily")
        reasoning.append("Market too unstable for grid bots")

    # Low volatility check
    elif daily_vol < 1.5:
        regime = "LOW_VOLATILITY"
        confidence = 90
        reasoning.append(f"Low volatility at {daily_vol:.2f}% daily")
        reasoning.append("Insufficient price movement for profitable grid trading")

    # Ranging market (ideal for grids)
    elif abs(sma_distance) < 2 and abs(change_30d) < 10:
        regime = "RANGING"
        confidence = 85
        reasoning.append(f"Price oscillating near SMA20 ({sma_distance:+.1f}%)")
        reasoning.append(f"30-day movement contained ({change_30d:+.1f}%)")
        reasoning.append(f"Volatility optimal for grids ({daily_vol:.2f}% daily)")

    # Trending market
    elif abs(change_30d) > 10 or abs(sma_distance) > 5:
        if change_30d > 0:
            regime = "TRENDING_UP"
        else:
            regime = "TRENDING_DOWN"
        confidence = 80
        reasoning.append(f"Strong {change_30d:+.1f}% move over 30 days")
        reasoning.append(f"Price {sma_distance:+.1f}% from SMA20")
        reasoning.append(f"Trend may challenge grid boundaries")

    # Default to ranging with medium volatility
    else:
        regime = "RANGING"
        confidence = 75
        reasoning.append(f"Moderate volatility ({daily_vol:.2f}% daily)")
        reasoning.append(f"No strong directional bias")

    return {
        "regime": regime,
        "confidence": confidence,
        "reasoning": reasoning
    }

def generate_grid_recommendation(regime_data, volatility, trend):
    """Generate grid bot recommendations"""
    regime = regime_data["regime"]
    daily_vol = volatility["daily_volatility"]
    current_price = trend["current_price"]

    if regime == "RANGING":
        # Ideal conditions for grid bots
        grid_range = daily_vol * 3  # 3x daily volatility for range
        return {
            "recommendation": "DEPLOY",
            "grid_range_percent": grid_range,
            "lower_bound": current_price * (1 - grid_range/100),
            "upper_bound": current_price * (1 + grid_range/100),
            "grids": 75,
            "expected_apr": 20 + (daily_vol - 1.5) * 5,  # Higher vol = higher returns
            "risk_level": "MEDIUM",
            "notes": [
                f"Optimal ranging conditions with {daily_vol:.1f}% daily volatility",
                f"Deploy grid with ±{grid_range:.1f}% range from current price",
                "Monitor for regime changes daily"
            ]
        }

    elif regime in ["TRENDING_UP", "TRENDING_DOWN"]:
        # Moderate suitability
        grid_range = daily_vol * 5  # Wider range for trending
        return {
            "recommendation": "CAUTION",
            "grid_range_percent": grid_range,
            "lower_bound": current_price * (1 - grid_range/100),
            "upper_bound": current_price * (1 + grid_range/100),
            "grids": 50,
            "expected_apr": 15,
            "risk_level": "HIGH",
            "notes": [
                f"Market trending {regime.split('_')[1].lower()}, grid bots risky",
                "Consider DCA strategy instead",
                "If deploying grids, use wider range and fewer grids"
            ]
        }

    elif regime == "LOW_VOLATILITY":
        return {
            "recommendation": "AVOID",
            "grid_range_percent": 0,
            "risk_level": "LOW",
            "notes": [
                f"Volatility too low ({daily_vol:.1f}% daily) for profitable grids",
                "Grid profits would be minimal (<10% APR)",
                "Consider DCA or holding strategies instead"
            ]
        }

    else:  # HIGH_UNCERTAINTY
        return {
            "recommendation": "WAIT",
            "grid_range_percent": 0,
            "risk_level": "EXTREME",
            "notes": [
                f"Extreme volatility ({daily_vol:.1f}% daily) creates liquidation risk",
                "Market conditions too unstable for safe grid deployment",
                "Wait for volatility to decrease below 4% daily"
            ]
        }

def main():
    print("=" * 70)
    print("MARKET REGIME ANALYSIS - BINANCE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

    # Analyze BTC/USDT
    print("\nFetching BTC/USDT data...")
    btc_ticker = fetch_ticker_data("BTCUSDT")
    btc_klines = fetch_klines("BTCUSDT", "1d", 30)

    btc_volatility = calculate_volatility(btc_klines)
    btc_trend = calculate_trend(btc_klines)
    btc_regime = classify_regime(btc_volatility, btc_trend)
    btc_recommendation = generate_grid_recommendation(btc_regime, btc_volatility, btc_trend)

    # Analyze ETH/USDT
    print("Fetching ETH/USDT data...")
    eth_ticker = fetch_ticker_data("ETHUSDT")
    eth_klines = fetch_klines("ETHUSDT", "1d", 30)

    eth_volatility = calculate_volatility(eth_klines)
    eth_trend = calculate_trend(eth_klines)
    eth_regime = classify_regime(eth_volatility, eth_trend)
    eth_recommendation = generate_grid_recommendation(eth_regime, eth_volatility, eth_trend)

    # Output results
    print("\n" + "=" * 70)
    print("BTC/USDT ANALYSIS")
    print("=" * 70)
    print(f"Current Price: ${btc_trend['current_price']:,.2f}")
    print(f"24h Change: {float(btc_ticker['priceChangePercent']):+.2f}%")
    print(f"30d Change: {btc_trend['change_30d']:+.2f}%")
    print(f"\nVolatility Metrics:")
    print(f"  Daily: {btc_volatility['daily_volatility']:.2f}%")
    print(f"  7-day: {btc_volatility['7d_volatility']:.2f}%")
    print(f"  Annualized: {btc_volatility['annualized_volatility']:.1f}%")
    print(f"\nTrend Indicators:")
    print(f"  SMA20: ${btc_trend['sma20']:,.2f}")
    print(f"  Distance from SMA: {btc_trend['sma_distance']:+.2f}%")
    print(f"  RSI(14): {btc_trend['rsi']:.1f}")
    print(f"  Volume Change: {btc_trend['volume_change']:+.1f}%")
    print(f"\nRegime: {btc_regime['regime']} (Confidence: {btc_regime['confidence']}%)")
    for reason in btc_regime['reasoning']:
        print(f"  - {reason}")
    print(f"\nGrid Bot Recommendation: {btc_recommendation['recommendation']}")
    for note in btc_recommendation.get('notes', []):
        print(f"  - {note}")

    print("\n" + "=" * 70)
    print("ETH/USDT ANALYSIS")
    print("=" * 70)
    print(f"Current Price: ${eth_trend['current_price']:,.2f}")
    print(f"24h Change: {float(eth_ticker['priceChangePercent']):+.2f}%")
    print(f"30d Change: {eth_trend['change_30d']:+.2f}%")
    print(f"\nVolatility Metrics:")
    print(f"  Daily: {eth_volatility['daily_volatility']:.2f}%")
    print(f"  7-day: {eth_volatility['7d_volatility']:.2f}%")
    print(f"  Annualized: {eth_volatility['annualized_volatility']:.1f}%")
    print(f"\nTrend Indicators:")
    print(f"  SMA20: ${eth_trend['sma20']:,.2f}")
    print(f"  Distance from SMA: {eth_trend['sma_distance']:+.2f}%")
    print(f"  RSI(14): {eth_trend['rsi']:.1f}")
    print(f"  Volume Change: {eth_trend['volume_change']:+.1f}%")
    print(f"\nRegime: {eth_regime['regime']} (Confidence: {eth_regime['confidence']}%)")
    for reason in eth_regime['reasoning']:
        print(f"  - {reason}")
    print(f"\nGrid Bot Recommendation: {eth_recommendation['recommendation']}")
    for note in eth_recommendation.get('notes', []):
        print(f"  - {note}")

    # Save analysis data
    analysis_data = {
        "timestamp": datetime.now().isoformat(),
        "btc": {
            "ticker": btc_ticker,
            "volatility": {k: v for k, v in btc_volatility.items() if k != 'returns'},
            "trend": btc_trend,
            "regime": btc_regime,
            "recommendation": btc_recommendation
        },
        "eth": {
            "ticker": eth_ticker,
            "volatility": {k: v for k, v in eth_volatility.items() if k != 'returns'},
            "trend": eth_trend,
            "regime": eth_regime,
            "recommendation": eth_recommendation
        }
    }

    with open("/tmp/regime_analysis.json", "w") as f:
        json.dump(analysis_data, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print("Analysis complete. Data saved to /tmp/regime_analysis.json")

    # Get last 5 closing prices for appendix
    btc_closes = [float(k[4]) for k in btc_klines[-5:]]
    eth_closes = [float(k[4]) for k in eth_klines[-5:]]

    print("\nBTC Last 5 Daily Closes:")
    for i, price in enumerate(btc_closes):
        print(f"  Day -{5-i}: ${price:,.2f}")

    print("\nETH Last 5 Daily Closes:")
    for i, price in enumerate(eth_closes):
        print(f"  Day -{5-i}: ${price:,.2f}")

    return analysis_data

if __name__ == "__main__":
    main()