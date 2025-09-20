"""
Experimental Strategy
A flexible strategy that can be configured from hypotheses
"""

from typing import Dict, List
import random
from datetime import datetime, timezone

from strategies.base_strategy import BaseStrategy, Signal


class ExperimentalStrategy(BaseStrategy):
    """Experimental strategy based on generated hypothesis"""

    def __init__(self, hypothesis_id: str, hypothesis: Dict):
        self.hypothesis = hypothesis
        self.hypothesis_id = hypothesis_id

        config = {
            'hypothesis_id': hypothesis_id,
            'risk_limit': hypothesis.get('risk_limit', 100),
            'entry_conditions': hypothesis.get('entry_conditions', []),
            'exit_conditions': hypothesis.get('exit_conditions', [])
        }

        super().__init__(strategy_id=f"exp_{hypothesis_id}", config=config)

    @property
    def name(self) -> str:
        return self.hypothesis.get('name', f'Experimental {self.hypothesis_id}')

    @property
    def description(self) -> str:
        return self.hypothesis.get('description', 'Experimental strategy from AI hypothesis')

    @property
    def min_confidence_for_live(self) -> float:
        # Higher threshold for experimental strategies
        return 70.0

    def analyze(self, market_data: Dict) -> Signal:
        """Analyze market data based on hypothesis conditions"""
        # Check entry conditions
        conditions_met = self._check_conditions(
            market_data,
            self.hypothesis.get('entry_conditions', [])
        )

        # Use AI analysis to boost confidence
        ai_analysis = market_data.get('ai_analysis', {})
        ai_confidence = ai_analysis.get('confidence', 50)

        # Calculate signal confidence
        base_confidence = self.hypothesis.get('confidence', 50)

        if conditions_met:
            # Entry signal
            confidence = min(100, base_confidence + ai_confidence * 0.3)

            # Determine action based on hypothesis type
            action = self._determine_action(market_data)

            signal = Signal(
                action=action,
                confidence=confidence,
                size=min(self.config['risk_limit'], 100),  # Conservative size for experiments
                reason=f"Experimental: {self.hypothesis.get('pattern', 'unknown')}",
                metadata={
                    'hypothesis_id': self.hypothesis_id,
                    'ai_recommendation': ai_analysis.get('recommendation', 'none'),
                    'pattern': self.hypothesis.get('pattern', 'unknown')
                }
            )

        elif self.position:
            # Check exit conditions
            should_exit = self._check_exit_conditions(market_data)

            if should_exit:
                signal = Signal(
                    action='close',
                    confidence=90,
                    size=0,
                    reason='Exit conditions met',
                    metadata={'hypothesis_id': self.hypothesis_id}
                )
            else:
                signal = Signal(
                    action='hold',
                    confidence=50,
                    size=0,
                    reason='Holding position',
                    metadata={'hypothesis_id': self.hypothesis_id}
                )
        else:
            # No action
            signal = Signal(
                action='hold',
                confidence=0,
                size=0,
                reason='Conditions not met',
                metadata={'hypothesis_id': self.hypothesis_id}
            )

        return signal

    def _check_conditions(self, market_data: Dict, conditions: List[Dict]) -> bool:
        """Check if entry conditions are met"""
        if not conditions:
            return False

        met_count = 0
        total_conditions = len(conditions)

        for condition in conditions:
            condition_type = condition.get('type')
            condition_value = condition.get('condition')

            # Simplified condition checking - in reality, would be more sophisticated
            if condition_type == 'time_based':
                if self._check_time_condition(market_data, condition_value):
                    met_count += 1

            elif condition_type == 'volatility':
                if self._check_volatility_condition(market_data, condition_value):
                    met_count += 1

            elif condition_type == 'sentiment':
                if self._check_sentiment_condition(market_data, condition_value):
                    met_count += 1

            elif condition_type == 'pattern':
                if self._check_pattern_condition(market_data, condition_value):
                    met_count += 1

            elif condition_type == 'experimental':
                # For experimental conditions, use randomness with bias
                if random.random() < 0.3:  # 30% chance for experimental
                    met_count += 1

        # Require majority of conditions to be met
        return met_count >= (total_conditions * 0.6)

    def _check_time_condition(self, market_data: Dict, condition: str) -> bool:
        """Check time-based conditions"""
        timestamp = market_data.get('timestamp', datetime.now(timezone.utc))

        if 'weekend' in condition:
            return timestamp.weekday() >= 5

        elif 'prime_time' in condition:
            return 14 <= timestamp.hour <= 18

        elif 'asian' in condition:
            return 0 <= timestamp.hour <= 8

        return False

    def _check_volatility_condition(self, market_data: Dict, condition: str) -> bool:
        """Check volatility conditions"""
        ai_analysis = market_data.get('ai_analysis', {})
        patterns = ai_analysis.get('patterns', {})
        volatility = patterns.get('volatility', 'medium')

        if 'below_average' in condition:
            return volatility in ['low', 'medium']
        elif 'above_average' in condition:
            return volatility in ['high']

        return False

    def _check_sentiment_condition(self, market_data: Dict, condition: str) -> bool:
        """Check sentiment conditions"""
        # Simplified - would integrate with real sentiment data
        if 'fear' in condition:
            # Check if market is in fear
            return market_data.get('price', 0) < market_data.get('ma_20', 100000)

        elif 'greed' in condition:
            # Check if market is in greed
            return market_data.get('price', 0) > market_data.get('ma_20', 0)

        return random.random() < 0.3  # Fallback

    def _check_pattern_condition(self, market_data: Dict, condition: str) -> bool:
        """Check pattern conditions"""
        ai_analysis = market_data.get('ai_analysis', {})
        patterns = ai_analysis.get('patterns', {})

        # Check if any detected pattern matches the condition
        for pattern_key, pattern_value in patterns.items():
            if condition.lower() in str(pattern_value).lower():
                return True

        return False

    def _determine_action(self, market_data: Dict) -> str:
        """Determine trading action based on hypothesis"""
        category = self.hypothesis.get('category', '')

        if category in ['sentiment_indicators', 'market_anomalies']:
            # Counter-trend strategies
            ai_analysis = market_data.get('ai_analysis', {})
            trend = ai_analysis.get('patterns', {}).get('trend', 'neutral')

            if trend == 'bullish':
                return 'open_short'
            elif trend == 'bearish':
                return 'open_long'
            else:
                return 'open_long'  # Default to long

        else:
            # Trend-following strategies
            return 'open_long'

    def _check_exit_conditions(self, market_data: Dict) -> bool:
        """Check if exit conditions are met"""
        exit_conditions = self.hypothesis.get('exit_conditions', [])

        for condition in exit_conditions:
            condition_type = condition.get('type')
            value = condition.get('value', 0)

            if condition_type == 'take_profit':
                # Check if profit target reached
                if self.position and self.position.get('unrealized_pnl', 0) > value:
                    return True

            elif condition_type == 'stop_loss':
                # Check if stop loss hit
                if self.position and self.position.get('unrealized_pnl', 0) < -value:
                    return True

            elif condition_type == 'time_based':
                # Check if time limit reached
                if self.position:
                    entry_time = self.position.get('entry_time')
                    if entry_time:
                        hours_held = (datetime.now(timezone.utc) - entry_time).total_seconds() / 3600
                        if hours_held > value:
                            return True

        return False

    def backtest(self, historical_data: List[Dict]) -> Dict:
        """Backtest the experimental strategy"""
        results = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0,
            'max_drawdown': 0,
            'signals_generated': []
        }

        position = None
        equity_curve = [0]

        for data_point in historical_data:
            signal = self.analyze(data_point)

            if signal.action in ['open_long', 'open_short'] and not position:
                # Open position
                position = {
                    'type': signal.action,
                    'entry_price': data_point.get('price', 0),
                    'size': signal.size
                }
                results['total_trades'] += 1

            elif signal.action == 'close' and position:
                # Close position
                exit_price = data_point.get('price', 0)

                if position['type'] == 'open_long':
                    pnl = (exit_price - position['entry_price']) * position['size'] / position['entry_price']
                else:  # short
                    pnl = (position['entry_price'] - exit_price) * position['size'] / position['entry_price']

                results['total_pnl'] += pnl
                equity_curve.append(results['total_pnl'])

                if pnl > 0:
                    results['winning_trades'] += 1

                # Calculate max drawdown
                peak = max(equity_curve)
                drawdown = peak - equity_curve[-1]
                results['max_drawdown'] = max(results['max_drawdown'], drawdown)

                position = None

            results['signals_generated'].append({
                'timestamp': data_point.get('timestamp'),
                'action': signal.action,
                'confidence': signal.confidence
            })

        # Calculate final metrics
        if results['total_trades'] > 0:
            results['win_rate'] = (results['winning_trades'] / results['total_trades']) * 100
        else:
            results['win_rate'] = 0

        return results