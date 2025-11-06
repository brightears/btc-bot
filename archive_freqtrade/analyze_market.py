#!/usr/bin/env python3
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

exchange = ccxt.binance()
symbol = "PAXG/USDT"
timeframe = "5m"
limit = 500

# Fetch recent data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# Calculate volatility metrics
df["price_change"] = df["close"].pct_change()
df["high_low_range"] = (df["high"] - df["low"]) / df["close"] * 100
df["candle_body"] = abs(df["close"] - df["open"]) / df["open"] * 100

print("PAXG/USDT Market Analysis (Last 41 hours, 5m candles):")
print(f"Current Price: ${df['close'].iloc[-1]:.2f}")
print(f"24h Range: ${df['low'].tail(288).min():.2f} - ${df['high'].tail(288).max():.2f}")
print(f"24h Volatility: {df['price_change'].tail(288).std() * np.sqrt(288) * 100:.2f}%")
print(f"\nVolatility Metrics:")
print(f"  5m candle avg range: {df['high_low_range'].mean():.3f}%")
print(f"  5m candle 95th percentile range: {df['high_low_range'].quantile(0.95):.3f}%")
print(f"  5m candle avg body: {df['candle_body'].mean():.3f}%")
print(f"  Hourly volatility: {df['price_change'].std() * np.sqrt(12) * 100:.3f}%")
print(f"\nAchievable ROI targets (based on 95th percentile moves):")
print(f"  Conservative (50% of range): {df['high_low_range'].quantile(0.95) * 0.5:.3f}%")
print(f"  Moderate (75% of range): {df['high_low_range'].quantile(0.95) * 0.75:.3f}%")
print(f"  Aggressive (full range): {df['high_low_range'].quantile(0.95):.3f}%")

# Show maximum observed moves
print(f"\nMaximum observed moves in dataset:")
print(f"  Max 5m range: {df['high_low_range'].max():.3f}%")
print(f"  Max 1hr move: {df['close'].rolling(12).apply(lambda x: (x.iloc[-1]/x.iloc[0] - 1)*100).max():.2f}%")
print(f"  Max 4hr move: {df['close'].rolling(48).apply(lambda x: (x.iloc[-1]/x.iloc[0] - 1)*100).max():.2f}%")