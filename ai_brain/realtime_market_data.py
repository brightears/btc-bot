"""
Real-time Market Data Fetcher
Gets ACTUAL market data from exchanges instead of simulated data
Prevents AI hallucination by grounding in reality
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import deque
import statistics


class RealtimeMarketData:
    """Fetches and manages real-time market data from exchanges"""

    def __init__(self):
        """Initialize real-time market data fetcher"""
        self.logger = logging.getLogger(__name__)

        # Binance API endpoints
        self.api_base = "https://api.binance.com/api/v3"
        self.futures_base = "https://fapi.binance.com/fapi/v1"

        # Data storage
        self.price_history = deque(maxlen=100)
        self.volume_history = deque(maxlen=100)
        self.funding_history = deque(maxlen=24)  # 24 hours of funding

        # Cache for latest data
        self.latest_data = {}
        self.last_update = None
        self.update_interval = 60  # Update every minute

        # Validation thresholds
        self.max_price_change = 0.1  # Max 10% price change in 1 minute
        self.min_price = 10000  # BTC shouldn't be below $10k
        self.max_price = 200000  # BTC shouldn't be above $200k

    async def get_market_data(self) -> Dict:
        """
        Get real market data from Binance

        Returns:
            Dict with actual market data, not simulated
        """
        try:
            # Check if we need to update
            if self._should_update():
                await self._fetch_all_data()

            # Return cached data if fetch fails
            if not self.latest_data:
                self.logger.warning("No market data available, using fallback")
                return self._get_fallback_data()

            # Add historical data for indicators
            self.latest_data['price_history'] = list(self.price_history)
            self.latest_data['volume_history'] = list(self.volume_history)

            # Calculate technical indicators from REAL data
            if len(self.price_history) >= 20:
                self.latest_data['ma_20'] = statistics.mean(list(self.price_history)[-20:])

            if len(self.price_history) >= 50:
                self.latest_data['ma_50'] = statistics.mean(list(self.price_history)[-50:])

            # Calculate RSI from real price movements
            self.latest_data['rsi'] = self._calculate_real_rsi()

            # Add data quality indicators
            self.latest_data['data_quality'] = self._assess_data_quality()
            self.latest_data['is_real_data'] = True

            return self.latest_data

        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
            return self._get_fallback_data()

    async def _fetch_all_data(self):
        """Fetch all market data from exchanges"""
        async with aiohttp.ClientSession() as session:
            # Fetch spot price and volume
            spot_data = await self._fetch_spot_data(session)

            # Fetch futures data (funding rate)
            futures_data = await self._fetch_futures_data(session)

            # Fetch order book depth
            depth_data = await self._fetch_orderbook_data(session)

            # Validate and combine data
            if self._validate_data(spot_data, futures_data):
                self.latest_data = {
                    'timestamp': datetime.now(timezone.utc),
                    'price': spot_data['price'],
                    'volume': spot_data['volume_24h'],
                    'bid': depth_data['bid'],
                    'ask': depth_data['ask'],
                    'spread': depth_data['spread'],
                    'funding_rate': futures_data['funding_rate'],
                    'next_funding': futures_data['next_funding'],
                    'open_interest': futures_data.get('open_interest', 0),
                    'high_24h': spot_data['high_24h'],
                    'low_24h': spot_data['low_24h'],
                    'change_24h': spot_data['price_change_percent']
                }

                # Update history
                self.price_history.append(spot_data['price'])
                self.volume_history.append(spot_data['volume_24h'])
                self.funding_history.append(futures_data['funding_rate'])

                self.last_update = datetime.now(timezone.utc)
                self.logger.info(f"Updated market data: BTC ${spot_data['price']:.2f}")

    async def _fetch_spot_data(self, session) -> Dict:
        """Fetch spot market data from Binance"""
        try:
            url = f"{self.api_base}/ticker/24hr"
            params = {'symbol': 'BTCUSDT'}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'price': float(data['lastPrice']),
                        'volume_24h': float(data['volume']),
                        'high_24h': float(data['highPrice']),
                        'low_24h': float(data['lowPrice']),
                        'price_change_percent': float(data['priceChangePercent'])
                    }
        except Exception as e:
            self.logger.error(f"Error fetching spot data: {e}")

        return {}

    async def _fetch_futures_data(self, session) -> Dict:
        """Fetch futures data including funding rate"""
        try:
            # Get funding rate
            url = f"{self.futures_base}/fundingRate"
            params = {'symbol': 'BTCUSDT', 'limit': 1}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        funding_data = data[0]
                        return {
                            'funding_rate': float(funding_data['fundingRate']),
                            'next_funding': datetime.fromtimestamp(
                                funding_data['fundingTime'] / 1000,
                                tz=timezone.utc
                            )
                        }
        except Exception as e:
            self.logger.error(f"Error fetching futures data: {e}")

        return {'funding_rate': 0.0001, 'next_funding': datetime.now(timezone.utc)}

    async def _fetch_orderbook_data(self, session) -> Dict:
        """Fetch order book data for spread analysis"""
        try:
            url = f"{self.api_base}/depth"
            params = {'symbol': 'BTCUSDT', 'limit': 5}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    best_bid = float(data['bids'][0][0]) if data['bids'] else 0
                    best_ask = float(data['asks'][0][0]) if data['asks'] else 0

                    return {
                        'bid': best_bid,
                        'ask': best_ask,
                        'spread': best_ask - best_bid if best_bid and best_ask else 0
                    }
        except Exception as e:
            self.logger.error(f"Error fetching orderbook: {e}")

        return {'bid': 0, 'ask': 0, 'spread': 0}

    def _validate_data(self, spot_data: Dict, futures_data: Dict) -> bool:
        """
        Validate market data to prevent hallucination

        Returns:
            True if data is valid and reasonable
        """
        if not spot_data or 'price' not in spot_data:
            self.logger.warning("Missing spot data")
            return False

        price = spot_data['price']

        # Check price bounds
        if price < self.min_price or price > self.max_price:
            self.logger.error(f"Price ${price} outside reasonable bounds")
            return False

        # Check for sudden price spikes (potential bad data)
        if self.price_history:
            last_price = self.price_history[-1]
            change = abs(price - last_price) / last_price

            if change > self.max_price_change:
                self.logger.warning(f"Price change {change:.2%} exceeds threshold")
                return False

        # Check volume is reasonable
        volume = spot_data.get('volume_24h', 0)
        if volume <= 0:
            self.logger.warning("Invalid volume data")
            return False

        # Check funding rate is reasonable (usually between -0.1% and 0.1%)
        funding = futures_data.get('funding_rate', 0)
        if abs(funding) > 0.001:  # 0.1%
            self.logger.warning(f"Unusual funding rate: {funding}")

        return True

    def _calculate_real_rsi(self, period: int = 14) -> float:
        """Calculate RSI from real price data"""
        if len(self.price_history) < period + 1:
            return 50.0  # Neutral

        prices = list(self.price_history)
        gains = []
        losses = []

        for i in range(1, period + 1):
            if i < len(prices):
                change = prices[-i] - prices[-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

        if not gains and not losses:
            return 50.0

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _assess_data_quality(self) -> Dict:
        """Assess the quality and reliability of current data"""
        quality = {
            'score': 100,
            'issues': []
        }

        # Check data freshness
        if self.last_update:
            age = (datetime.now(timezone.utc) - self.last_update).seconds
            if age > 300:  # Data older than 5 minutes
                quality['score'] -= 20
                quality['issues'].append('Stale data')

        # Check data completeness
        if len(self.price_history) < 20:
            quality['score'] -= 10
            quality['issues'].append('Insufficient history')

        # Check for data anomalies
        if self.price_history and len(self.price_history) > 10:
            recent_prices = list(self.price_history)[-10:]
            std_dev = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0

            # High volatility warning
            if std_dev > statistics.mean(recent_prices) * 0.02:
                quality['score'] -= 5
                quality['issues'].append('High volatility')

        return quality

    def _should_update(self) -> bool:
        """Check if data should be updated"""
        if not self.last_update:
            return True

        elapsed = (datetime.now(timezone.utc) - self.last_update).seconds
        return elapsed >= self.update_interval

    def _get_fallback_data(self) -> Dict:
        """
        Get fallback data when real data unavailable
        This should trigger alerts, not be used for trading
        """
        self.logger.warning("Using fallback data - DO NOT TRADE")

        # Return last known good data or safe defaults
        if self.latest_data:
            fallback = self.latest_data.copy()
            fallback['is_real_data'] = False
            fallback['data_quality'] = {'score': 0, 'issues': ['Using fallback data']}
            return fallback

        # Absolute fallback with clear indicators it's not real
        return {
            'timestamp': datetime.now(timezone.utc),
            'price': 50000,  # Safe middle value
            'volume': 0,
            'funding_rate': 0,
            'is_real_data': False,
            'data_quality': {'score': 0, 'issues': ['No real data available']},
            'warning': 'DO NOT TRADE - No real market data available'
        }

    def get_data_status(self) -> Dict:
        """Get status of data feed"""
        return {
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'price_history_count': len(self.price_history),
            'latest_price': self.price_history[-1] if self.price_history else None,
            'data_quality': self._assess_data_quality(),
            'is_connected': self.last_update and (datetime.now(timezone.utc) - self.last_update).seconds < 300
        }