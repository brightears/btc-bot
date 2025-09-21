"""
Market Sentiment Analyzer
Combines multiple sentiment sources for comprehensive market mood assessment
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import logging

class MarketSentimentAnalyzer:
    """Analyzes market sentiment from multiple data sources"""

    def __init__(self, llm_analyzer=None):
        """Initialize sentiment analyzer"""
        self.logger = logging.getLogger(__name__)
        self.llm_analyzer = llm_analyzer

        # Sentiment history for trend analysis
        self.sentiment_history = []
        self.max_history = 100

        # Thresholds for sentiment classification
        self.thresholds = {
            'extreme_fear': -0.8,
            'fear': -0.4,
            'neutral': 0.4,
            'greed': 0.8,
            'extreme_greed': 1.0
        }

    async def analyze_comprehensive_sentiment(self, market_data: Dict, news_items: List[Dict] = None) -> Dict:
        """Comprehensive sentiment analysis from all sources"""
        sentiment_scores = {}

        # 1. Technical sentiment from market data
        technical_sentiment = self._analyze_technical_sentiment(market_data)
        sentiment_scores['technical'] = technical_sentiment

        # 2. News sentiment (if LLM is available)
        if news_items and self.llm_analyzer:
            news_sentiment = await self._analyze_news_sentiment(news_items)
            sentiment_scores['news'] = news_sentiment

        # 3. Funding rate sentiment
        funding_sentiment = self._analyze_funding_sentiment(market_data.get('funding_rate', 0))
        sentiment_scores['funding'] = funding_sentiment

        # 4. Volume sentiment
        volume_sentiment = self._analyze_volume_sentiment(market_data)
        sentiment_scores['volume'] = volume_sentiment

        # 5. Price momentum sentiment
        momentum_sentiment = self._analyze_momentum_sentiment(market_data)
        sentiment_scores['momentum'] = momentum_sentiment

        # Calculate weighted composite sentiment
        composite_sentiment = self._calculate_composite_sentiment(sentiment_scores)

        # Determine market regime
        regime = self._determine_market_regime(composite_sentiment, sentiment_scores)

        # Check for sentiment divergences (contrarian signals)
        divergences = self._detect_sentiment_divergences(sentiment_scores)

        # Store in history
        self._update_sentiment_history(composite_sentiment)

        # Calculate sentiment trend
        sentiment_trend = self._calculate_sentiment_trend()

        result = {
            'timestamp': datetime.now(timezone.utc),
            'composite_score': composite_sentiment,
            'sentiment_label': self._get_sentiment_label(composite_sentiment),
            'market_regime': regime,
            'components': sentiment_scores,
            'divergences': divergences,
            'trend': sentiment_trend,
            'confidence': self._calculate_confidence(sentiment_scores),
            'trading_bias': self._get_trading_bias(composite_sentiment, regime, divergences)
        }

        return result

    def _analyze_technical_sentiment(self, market_data: Dict) -> float:
        """Analyze sentiment from technical indicators"""
        sentiment = 0.0
        weights = 0

        # Price position relative to recent range
        if 'price_history' in market_data and len(market_data['price_history']) > 20:
            prices = market_data['price_history']
            current_price = market_data['price']

            # Calculate percentile position
            min_price = min(prices[-20:])
            max_price = max(prices[-20:])
            if max_price > min_price:
                position = (current_price - min_price) / (max_price - min_price)
                sentiment += (position - 0.5) * 2  # Convert to -1 to 1
                weights += 1

            # RSI-like calculation
            gains = []
            losses = []
            for i in range(1, len(prices[-14:])):
                change = prices[-14:][i] - prices[-14:][i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

            if gains and losses:
                avg_gain = statistics.mean(gains) if gains else 0
                avg_loss = statistics.mean(losses) if losses else 0

                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    # Convert RSI to sentiment (-1 to 1)
                    rsi_sentiment = (rsi - 50) / 50
                    sentiment += rsi_sentiment
                    weights += 1

        return sentiment / weights if weights > 0 else 0.0

    async def _analyze_news_sentiment(self, news_items: List[Dict]) -> float:
        """Analyze sentiment from news using LLM"""
        if not news_items or not self.llm_analyzer:
            return 0.0

        try:
            # Use LLM to analyze news sentiment
            analysis = await self.llm_analyzer.analyze_news(news_items)

            # Convert sentiment label to score
            sentiment_map = {
                'bullish': 0.6,
                'very bullish': 0.9,
                'neutral': 0.0,
                'bearish': -0.6,
                'very bearish': -0.9
            }

            sentiment_label = analysis.get('sentiment', 'neutral').lower()
            return sentiment_map.get(sentiment_label, 0.0)

        except Exception as e:
            self.logger.error(f"News sentiment analysis error: {e}")
            return 0.0

    def _analyze_funding_sentiment(self, funding_rate: float) -> float:
        """Analyze sentiment from funding rate"""
        if funding_rate == 0:
            return 0.0

        # Funding rate indicates market positioning
        # Positive = longs pay shorts (bullish positioning)
        # Negative = shorts pay longs (bearish positioning)

        # Normalize funding rate to sentiment score
        # Typical funding rates are -0.01% to 0.01% per 8 hours
        max_funding = 0.001  # 0.1%

        if abs(funding_rate) > max_funding:
            # Extreme funding = contrarian signal
            return -1.0 if funding_rate > 0 else 1.0
        else:
            # Normal funding = trend following
            return funding_rate / max_funding

    def _analyze_volume_sentiment(self, market_data: Dict) -> float:
        """Analyze sentiment from volume patterns"""
        if 'volume_history' not in market_data or len(market_data['volume_history']) < 10:
            return 0.0

        volumes = market_data['volume_history']
        current_volume = market_data.get('volume', volumes[-1])

        # Calculate volume relative to average
        avg_volume = statistics.mean(volumes[-20:]) if len(volumes) >= 20 else statistics.mean(volumes)

        if avg_volume == 0:
            return 0.0

        volume_ratio = current_volume / avg_volume

        # High volume can indicate:
        # - Breakout (if with price movement)
        # - Distribution/Accumulation (if price stable)

        if 'price_history' in market_data and len(market_data['price_history']) > 2:
            price_change = (market_data['price'] - market_data['price_history'][-2]) / market_data['price_history'][-2]

            if volume_ratio > 1.5:  # High volume
                if abs(price_change) > 0.01:  # With price movement
                    return 0.5 if price_change > 0 else -0.5
                else:  # Without price movement (potential reversal)
                    return -0.3
            elif volume_ratio < 0.7:  # Low volume
                return -0.2  # Lack of interest
            else:
                return 0.0
        else:
            return 0.0

    def _analyze_momentum_sentiment(self, market_data: Dict) -> float:
        """Analyze sentiment from price momentum"""
        if 'price_history' not in market_data or len(market_data['price_history']) < 10:
            return 0.0

        prices = market_data['price_history']

        # Short-term momentum (5 periods)
        if len(prices) >= 5:
            short_momentum = (prices[-1] - prices[-5]) / prices[-5]
        else:
            short_momentum = 0

        # Medium-term momentum (20 periods)
        if len(prices) >= 20:
            medium_momentum = (prices[-1] - prices[-20]) / prices[-20]
        else:
            medium_momentum = short_momentum

        # Weight short-term more heavily
        momentum = (short_momentum * 0.7 + medium_momentum * 0.3)

        # Convert to sentiment score (-1 to 1)
        # Cap at reasonable levels (±5% momentum = ±1 sentiment)
        return max(-1, min(1, momentum * 20))

    def _calculate_composite_sentiment(self, sentiment_scores: Dict[str, float]) -> float:
        """Calculate weighted composite sentiment score"""
        # Define weights for each component
        weights = {
            'technical': 0.25,
            'news': 0.20,
            'funding': 0.20,
            'volume': 0.15,
            'momentum': 0.20
        }

        total_score = 0
        total_weight = 0

        for component, score in sentiment_scores.items():
            if component in weights:
                total_score += score * weights[component]
                total_weight += weights[component]

        return total_score / total_weight if total_weight > 0 else 0.0

    def _determine_market_regime(self, composite_sentiment: float, components: Dict) -> str:
        """Determine current market regime"""
        # Check for specific patterns
        if composite_sentiment > 0.6:
            if components.get('momentum', 0) > 0.7:
                return 'Strong Uptrend'
            else:
                return 'Bullish'
        elif composite_sentiment < -0.6:
            if components.get('momentum', 0) < -0.7:
                return 'Strong Downtrend'
            else:
                return 'Bearish'
        elif abs(composite_sentiment) < 0.2:
            if components.get('volume', 0) < -0.3:
                return 'Consolidation'
            else:
                return 'Ranging'
        else:
            if composite_sentiment > 0:
                return 'Weak Bullish'
            else:
                return 'Weak Bearish'

    def _detect_sentiment_divergences(self, sentiment_scores: Dict) -> List[str]:
        """Detect divergences between sentiment components"""
        divergences = []

        # Check for major divergences
        components = list(sentiment_scores.values())
        if not components:
            return divergences

        # Price vs Funding divergence
        if 'momentum' in sentiment_scores and 'funding' in sentiment_scores:
            if sentiment_scores['momentum'] > 0.5 and sentiment_scores['funding'] < -0.5:
                divergences.append('Bullish price with bearish funding (potential long squeeze)')
            elif sentiment_scores['momentum'] < -0.5 and sentiment_scores['funding'] > 0.5:
                divergences.append('Bearish price with bullish funding (potential short squeeze)')

        # Technical vs News divergence
        if 'technical' in sentiment_scores and 'news' in sentiment_scores:
            if abs(sentiment_scores['technical'] - sentiment_scores['news']) > 1.0:
                if sentiment_scores['technical'] > sentiment_scores['news']:
                    divergences.append('Technical bullish but news bearish (fade the news)')
                else:
                    divergences.append('News bullish but technical bearish (fade the hype)')

        # Volume divergence
        if 'volume' in sentiment_scores and 'momentum' in sentiment_scores:
            if sentiment_scores['momentum'] > 0.5 and sentiment_scores['volume'] < -0.3:
                divergences.append('Price rising on low volume (weak rally)')
            elif sentiment_scores['momentum'] < -0.5 and sentiment_scores['volume'] > 0.3:
                divergences.append('Price falling on high volume (capitulation)')

        return divergences

    def _update_sentiment_history(self, sentiment: float):
        """Update sentiment history for trend analysis"""
        self.sentiment_history.append({
            'timestamp': datetime.now(timezone.utc),
            'sentiment': sentiment
        })

        # Keep only recent history
        if len(self.sentiment_history) > self.max_history:
            self.sentiment_history = self.sentiment_history[-self.max_history:]

    def _calculate_sentiment_trend(self) -> str:
        """Calculate sentiment trend direction"""
        if len(self.sentiment_history) < 5:
            return 'Insufficient data'

        recent = [h['sentiment'] for h in self.sentiment_history[-5:]]
        older = [h['sentiment'] for h in self.sentiment_history[-10:-5]] if len(self.sentiment_history) >= 10 else recent

        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)

        if recent_avg > older_avg + 0.1:
            return 'Improving'
        elif recent_avg < older_avg - 0.1:
            return 'Deteriorating'
        else:
            return 'Stable'

    def _calculate_confidence(self, sentiment_scores: Dict) -> float:
        """Calculate confidence in sentiment reading"""
        if not sentiment_scores:
            return 0.0

        # Higher confidence when components agree
        values = list(sentiment_scores.values())
        if len(values) < 2:
            return 0.5

        # Calculate standard deviation
        std_dev = statistics.stdev(values)

        # Lower std dev = higher agreement = higher confidence
        # Max confidence when std_dev < 0.2, min when std_dev > 0.8
        confidence = max(0, min(100, (1 - std_dev / 0.8) * 100))

        return confidence

    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score <= self.thresholds['extreme_fear']:
            return 'Extreme Fear'
        elif score <= self.thresholds['fear']:
            return 'Fear'
        elif score <= self.thresholds['neutral']:
            return 'Neutral'
        elif score <= self.thresholds['greed']:
            return 'Greed'
        else:
            return 'Extreme Greed'

    def _get_trading_bias(self, sentiment: float, regime: str, divergences: List[str]) -> str:
        """Determine trading bias based on sentiment analysis"""
        # Contrarian approach at extremes
        if sentiment > 0.8:
            return 'Look for shorts (extreme greed)'
        elif sentiment < -0.8:
            return 'Look for longs (extreme fear)'

        # Trend following in strong regimes
        elif 'Strong' in regime:
            if 'Uptrend' in regime:
                return 'Long bias (strong trend)'
            else:
                return 'Short bias (strong trend)'

        # Caution on divergences
        elif divergences:
            return 'Cautious (divergences detected)'

        # Neutral in ranging markets
        elif regime in ['Ranging', 'Consolidation']:
            return 'Range trading (buy support, sell resistance)'

        # Default to trend following
        elif sentiment > 0.2:
            return 'Mild long bias'
        elif sentiment < -0.2:
            return 'Mild short bias'
        else:
            return 'Neutral (wait for clear signal)'