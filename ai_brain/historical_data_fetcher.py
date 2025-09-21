"""
Historical Data Fetcher
Fetches and caches historical Bitcoin price data for backtesting
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging

class HistoricalDataFetcher:
    """Fetches and manages historical price data for backtesting"""

    def __init__(self):
        """Initialize historical data fetcher"""
        self.logger = logging.getLogger(__name__)

        # Cache directory
        self.cache_dir = Path("cache/historical")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # API endpoints (free tier)
        self.api_endpoints = {
            'coingecko': 'https://api.coingecko.com/api/v3',
            'binance': 'https://api.binance.com/api/v3',
            'coinbase': 'https://api.coinbase.com/v2'
        }

        # Cache duration
        self.cache_duration = timedelta(hours=6)

    async def fetch_historical_data(self, days: int = 30, interval: str = '1h') -> List[Dict]:
        """
        Fetch historical Bitcoin price data

        Args:
            days: Number of days of history to fetch
            interval: Time interval (1h, 4h, 1d)

        Returns:
            List of price data points
        """
        # Check cache first
        cache_file = self.cache_dir / f"btc_{days}d_{interval}.json"

        if self._is_cache_valid(cache_file):
            self.logger.info(f"Loading historical data from cache")
            with open(cache_file, 'r') as f:
                return json.load(f)

        # Fetch fresh data
        self.logger.info(f"Fetching {days} days of historical data")

        try:
            # Try Binance first (most reliable)
            data = await self._fetch_binance_data(days, interval)

            if not data:
                # Fallback to CoinGecko
                data = await self._fetch_coingecko_data(days)

            if data:
                # Cache the data
                with open(cache_file, 'w') as f:
                    json.dump(data, f)

                self.logger.info(f"Fetched {len(data)} data points")
                return data

        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")

        # Return empty list if all fails
        return []

    async def _fetch_binance_data(self, days: int, interval: str) -> List[Dict]:
        """Fetch data from Binance API"""
        try:
            # Convert interval to Binance format
            binance_intervals = {
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }

            if interval not in binance_intervals:
                interval = '1h'

            # Calculate timestamps
            end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)

            url = f"{self.api_endpoints['binance']}/klines"
            params = {
                'symbol': 'BTCUSDT',
                'interval': binance_intervals[interval],
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000  # Max limit
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        raw_data = await response.json()

                        # Convert to our format
                        data = []
                        for candle in raw_data:
                            data.append({
                                'timestamp': datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc).isoformat(),
                                'open': float(candle[1]),
                                'high': float(candle[2]),
                                'low': float(candle[3]),
                                'close': float(candle[4]),
                                'volume': float(candle[5]),
                                'price': float(candle[4])  # Use close as price
                            })

                        return data

        except Exception as e:
            self.logger.error(f"Binance API error: {e}")

        return []

    async def _fetch_coingecko_data(self, days: int) -> List[Dict]:
        """Fetch data from CoinGecko API (fallback)"""
        try:
            url = f"{self.api_endpoints['coingecko']}/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 90 else 'daily'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        raw_data = await response.json()

                        # Convert to our format
                        data = []
                        prices = raw_data.get('prices', [])
                        volumes = raw_data.get('total_volumes', [])

                        # Create volume lookup
                        volume_dict = {v[0]: v[1] for v in volumes}

                        for price_point in prices:
                            timestamp_ms = price_point[0]
                            price = price_point[1]
                            volume = volume_dict.get(timestamp_ms, 0)

                            data.append({
                                'timestamp': datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat(),
                                'price': price,
                                'volume': volume,
                                'open': price,  # CoinGecko doesn't provide OHLC
                                'high': price * 1.002,  # Estimate with small variation
                                'low': price * 0.998,
                                'close': price
                            })

                        return data

        except Exception as e:
            self.logger.error(f"CoinGecko API error: {e}")

        return []

    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid"""
        if not cache_file.exists():
            return False

        # Check age
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)

        return file_age < self.cache_duration

    async def get_backtest_data(self, strategy_type: str = 'default', days: int = 30) -> List[Dict]:
        """
        Get historical data formatted for backtesting

        Args:
            strategy_type: Type of strategy (affects data requirements)
            days: Number of days of history

        Returns:
            List of market data points for backtesting
        """
        # Fetch raw historical data
        raw_data = await self.fetch_historical_data(days=days, interval='1h')

        if not raw_data:
            self.logger.warning("No historical data available for backtesting")
            return []

        # Format for backtesting
        backtest_data = []

        for i, point in enumerate(raw_data):
            # Calculate moving averages
            if i >= 20:
                ma_20 = sum(d['price'] for d in raw_data[i-20:i]) / 20
            else:
                ma_20 = point['price']

            if i >= 50 and len(raw_data) > 50:
                ma_50 = sum(d['price'] for d in raw_data[i-50:i]) / 50
            else:
                ma_50 = point['price']

            # Calculate RSI (simplified)
            rsi = 50  # Default
            if i >= 14:
                gains = []
                losses = []
                for j in range(i-14, i):
                    change = raw_data[j]['price'] - raw_data[j-1]['price']
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))

                if gains and losses:
                    avg_gain = sum(gains) / len(gains) if gains else 0
                    avg_loss = sum(losses) / len(losses) if losses else 0

                    if avg_loss > 0:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))

            # Build market data point
            market_data = {
                'timestamp': datetime.fromisoformat(point['timestamp']),
                'price': point['price'],
                'open': point['open'],
                'high': point['high'],
                'low': point['low'],
                'close': point['close'],
                'volume': point['volume'],
                'ma_20': ma_20,
                'ma_50': ma_50,
                'rsi': rsi,
                'price_history': [d['price'] for d in raw_data[max(0, i-100):i+1]],
                'volume_history': [d['volume'] for d in raw_data[max(0, i-100):i+1]],

                # Add AI analysis placeholder (would be generated by AI in real scenario)
                'ai_analysis': {
                    'patterns': {
                        'trend': 'bullish' if point['price'] > ma_20 else 'bearish',
                        'volatility': 'high' if i > 0 and abs(point['price'] - raw_data[i-1]['price']) / raw_data[i-1]['price'] > 0.02 else 'low'
                    },
                    'confidence': 50 + (10 if point['price'] > ma_20 else -10),
                    'recommendation': 'buy' if rsi < 30 else 'sell' if rsi > 70 else 'hold'
                }
            }

            backtest_data.append(market_data)

        return backtest_data

    async def get_recent_performance(self, hours: int = 24) -> Dict:
        """
        Get recent market performance metrics

        Args:
            hours: Number of hours to analyze

        Returns:
            Performance metrics dict
        """
        # Fetch recent data
        days = max(1, hours // 24 + 1)
        data = await self.fetch_historical_data(days=days, interval='1h')

        if not data:
            return {}

        # Get data for specified hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_data = [
            d for d in data
            if datetime.fromisoformat(d['timestamp']) > cutoff_time
        ]

        if not recent_data:
            return {}

        prices = [d['price'] for d in recent_data]
        volumes = [d['volume'] for d in recent_data]

        return {
            'start_price': prices[0],
            'end_price': prices[-1],
            'high': max(prices),
            'low': min(prices),
            'price_change': prices[-1] - prices[0],
            'price_change_pct': ((prices[-1] - prices[0]) / prices[0]) * 100,
            'avg_volume': sum(volumes) / len(volumes),
            'total_volume': sum(volumes),
            'volatility': self._calculate_volatility(prices),
            'trend': 'up' if prices[-1] > prices[0] else 'down',
            'data_points': len(recent_data)
        }

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate simple volatility metric"""
        if len(prices) < 2:
            return 0.0

        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i] - prices[i-1]) / prices[i-1])

        if not returns:
            return 0.0

        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)

        return (variance ** 0.5) * 100  # Return as percentage