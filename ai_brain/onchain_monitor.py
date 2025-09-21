"""
On-chain Data Monitor
Tracks blockchain metrics for trading insights
"""

import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
import json
from pathlib import Path

class OnChainMonitor:
    """Monitors on-chain Bitcoin metrics for trading signals"""

    def __init__(self):
        """Initialize on-chain monitor"""
        self.logger = logging.getLogger(__name__)

        # Free API endpoints for on-chain data
        self.api_endpoints = {
            'blockchain_info': 'https://api.blockchain.info',
            'mempool_space': 'https://mempool.space/api',
            'blockchair': 'https://api.blockchair.com/bitcoin'
        }

        # Cache for API responses
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

        # Historical data storage
        self.metrics_history = []
        self.max_history = 1000

    async def get_onchain_metrics(self) -> Dict:
        """Fetch comprehensive on-chain metrics"""
        metrics = {}

        # Get multiple metrics in parallel
        tasks = [
            self._get_network_stats(),
            self._get_mempool_stats(),
            self._get_exchange_flows(),
            self._get_whale_activity()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        for result in results:
            if isinstance(result, dict):
                metrics.update(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Error fetching metrics: {result}")

        # Add timestamp
        metrics['timestamp'] = datetime.now(timezone.utc)

        # Store in history
        self._update_history(metrics)

        # Calculate derived metrics
        metrics['signals'] = self._calculate_signals(metrics)

        return metrics

    async def _get_network_stats(self) -> Dict:
        """Get Bitcoin network statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get basic network stats
                url = f"{self.api_endpoints['blockchain_info']}/stats"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'hash_rate': data.get('hash_rate', 0),
                            'difficulty': data.get('difficulty', 0),
                            'n_tx': data.get('n_tx', 0),  # Number of transactions
                            'total_btc_sent': data.get('total_btc_sent', 0) / 100000000,  # Convert to BTC
                            'market_price_usd': data.get('market_price_usd', 0),
                            'total_fees_btc': data.get('total_fees_btc', 0) / 100000000
                        }
        except Exception as e:
            self.logger.error(f"Error fetching network stats: {e}")

        return {}

    async def _get_mempool_stats(self) -> Dict:
        """Get mempool statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get mempool stats from mempool.space
                url = f"{self.api_endpoints['mempool_space']}/mempool"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Calculate fee pressure
                        fee_levels = data.get('fee_histogram', [])
                        if fee_levels:
                            avg_fee = sum(f[0] * f[1] for f in fee_levels) / sum(f[1] for f in fee_levels)
                        else:
                            avg_fee = 0

                        return {
                            'mempool_size': data.get('vsize', 0),
                            'mempool_tx_count': data.get('count', 0),
                            'mempool_fees': avg_fee,
                            'fee_pressure': 'high' if avg_fee > 50 else 'medium' if avg_fee > 20 else 'low'
                        }
        except Exception as e:
            self.logger.error(f"Error fetching mempool stats: {e}")

        return {}

    async def _get_exchange_flows(self) -> Dict:
        """Estimate exchange flows from public data"""
        try:
            # This would normally use specialized APIs
            # For now, we'll use proxy metrics

            # High fees often correlate with exchange activity
            mempool_stats = await self._get_mempool_stats()
            fee_pressure = mempool_stats.get('fee_pressure', 'medium')

            # Estimate based on network activity
            if fee_pressure == 'high':
                flow_estimate = 'outflow'  # High fees = people moving coins
            elif fee_pressure == 'low':
                flow_estimate = 'accumulation'
            else:
                flow_estimate = 'neutral'

            return {
                'exchange_flow_estimate': flow_estimate,
                'exchange_flow_confidence': 'low'  # Since we're estimating
            }
        except Exception as e:
            self.logger.error(f"Error estimating exchange flows: {e}")

        return {'exchange_flow_estimate': 'unknown'}

    async def _get_whale_activity(self) -> Dict:
        """Monitor large transactions (whale activity)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get recent large transactions
                url = f"{self.api_endpoints['blockchain_info']}/unconfirmed-transactions?format=json"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        txs = data.get('txs', [])[:100]  # Analyze last 100 transactions

                        # Count large transactions (>10 BTC)
                        large_txs = []
                        for tx in txs:
                            # Calculate total output
                            total_out = sum(out.get('value', 0) for out in tx.get('out', [])) / 100000000
                            if total_out > 10:  # More than 10 BTC
                                large_txs.append(total_out)

                        whale_activity = 'high' if len(large_txs) > 10 else 'medium' if len(large_txs) > 5 else 'low'

                        return {
                            'whale_transactions': len(large_txs),
                            'whale_volume_btc': sum(large_txs),
                            'whale_activity': whale_activity,
                            'largest_tx_btc': max(large_txs) if large_txs else 0
                        }
        except Exception as e:
            self.logger.error(f"Error fetching whale activity: {e}")

        return {'whale_activity': 'unknown'}

    async def get_fear_greed_index(self) -> Dict:
        """Get simplified fear & greed metrics"""
        try:
            metrics = await self.get_onchain_metrics()

            # Calculate fear/greed based on on-chain metrics
            score = 50  # Start neutral

            # Hash rate trend (increasing = greed)
            if 'hash_rate' in metrics:
                if len(self.metrics_history) > 10:
                    recent_hash = metrics['hash_rate']
                    avg_hash = sum(m.get('hash_rate', recent_hash) for m in self.metrics_history[-10:]) / 10
                    if recent_hash > avg_hash * 1.05:
                        score += 10
                    elif recent_hash < avg_hash * 0.95:
                        score -= 10

            # Fee pressure (high fees = greed/FOMO)
            fee_pressure = metrics.get('fee_pressure', 'medium')
            if fee_pressure == 'high':
                score += 15
            elif fee_pressure == 'low':
                score -= 15

            # Whale activity
            whale_activity = metrics.get('whale_activity', 'medium')
            if whale_activity == 'high':
                score += 10  # Whales active = something happening
            elif whale_activity == 'low':
                score -= 5  # Quiet market

            # Exchange flows
            flow = metrics.get('exchange_flow_estimate', 'neutral')
            if flow == 'outflow':
                score += 10  # Coins leaving exchanges = bullish
            elif flow == 'accumulation':
                score -= 10  # Coins entering exchanges = bearish

            # Cap between 0-100
            score = max(0, min(100, score))

            # Determine sentiment label
            if score < 20:
                label = 'Extreme Fear'
            elif score < 40:
                label = 'Fear'
            elif score < 60:
                label = 'Neutral'
            elif score < 80:
                label = 'Greed'
            else:
                label = 'Extreme Greed'

            return {
                'fear_greed_index': score,
                'sentiment': label,
                'components': {
                    'hash_rate_trend': 'increasing' if score > 50 else 'decreasing',
                    'fee_pressure': fee_pressure,
                    'whale_activity': whale_activity,
                    'exchange_flows': flow
                }
            }
        except Exception as e:
            self.logger.error(f"Error calculating fear/greed index: {e}")
            return {'fear_greed_index': 50, 'sentiment': 'Neutral'}

    def _calculate_signals(self, metrics: Dict) -> List[Dict]:
        """Calculate trading signals from on-chain metrics"""
        signals = []

        # Signal 1: High network activity
        if metrics.get('n_tx', 0) > 400000:  # High transaction count
            signals.append({
                'type': 'network_activity',
                'signal': 'bullish',
                'reason': 'High network usage indicates strong adoption',
                'strength': 'medium'
            })

        # Signal 2: Whale accumulation
        if metrics.get('whale_activity') == 'high' and metrics.get('exchange_flow_estimate') == 'outflow':
            signals.append({
                'type': 'whale_accumulation',
                'signal': 'bullish',
                'reason': 'Whales moving coins off exchanges (accumulation)',
                'strength': 'high'
            })

        # Signal 3: Fee spike (FOMO or panic)
        if metrics.get('fee_pressure') == 'high':
            # High fees could mean FOMO (bullish) or panic selling (bearish)
            # Need more context to determine
            signals.append({
                'type': 'fee_spike',
                'signal': 'volatile',
                'reason': 'High fees indicate urgent transactions',
                'strength': 'medium'
            })

        # Signal 4: Miner capitulation check
        if 'hash_rate' in metrics and len(self.metrics_history) > 30:
            recent_hash = metrics['hash_rate']
            avg_hash = sum(m.get('hash_rate', recent_hash) for m in self.metrics_history[-30:]) / 30
            if recent_hash < avg_hash * 0.9:  # 10% drop in hash rate
                signals.append({
                    'type': 'miner_capitulation',
                    'signal': 'bearish',
                    'reason': 'Hash rate dropping, miners may be selling',
                    'strength': 'high'
                })

        # Signal 5: Exchange flow reversal
        if len(self.metrics_history) > 5:
            recent_flows = [m.get('exchange_flow_estimate', 'neutral') for m in self.metrics_history[-5:]]
            if recent_flows.count('outflow') > 3:
                signals.append({
                    'type': 'sustained_outflow',
                    'signal': 'bullish',
                    'reason': 'Sustained exchange outflows (accumulation phase)',
                    'strength': 'medium'
                })

        return signals

    def _update_history(self, metrics: Dict):
        """Update metrics history"""
        self.metrics_history.append(metrics)

        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]

    async def get_market_intelligence(self) -> Dict:
        """Get comprehensive market intelligence from on-chain data"""
        metrics = await self.get_onchain_metrics()
        fear_greed = await self.get_fear_greed_index()

        # Combine all intelligence
        intelligence = {
            'timestamp': datetime.now(timezone.utc),
            'metrics': metrics,
            'fear_greed': fear_greed,
            'signals': metrics.get('signals', []),
            'recommendation': self._generate_recommendation(metrics, fear_greed)
        }

        return intelligence

    def _generate_recommendation(self, metrics: Dict, fear_greed: Dict) -> str:
        """Generate trading recommendation based on on-chain data"""
        signals = metrics.get('signals', [])
        fg_score = fear_greed.get('fear_greed_index', 50)

        bullish_signals = sum(1 for s in signals if s['signal'] == 'bullish')
        bearish_signals = sum(1 for s in signals if s['signal'] == 'bearish')

        # Contrarian at extremes
        if fg_score < 20:
            return "Extreme fear detected - consider contrarian long positions"
        elif fg_score > 80:
            return "Extreme greed detected - consider taking profits or hedging"

        # Follow the signals
        elif bullish_signals > bearish_signals + 1:
            return "On-chain metrics bullish - look for long opportunities"
        elif bearish_signals > bullish_signals + 1:
            return "On-chain metrics bearish - be cautious or consider shorts"
        else:
            return "Mixed signals - wait for clearer on-chain trends"