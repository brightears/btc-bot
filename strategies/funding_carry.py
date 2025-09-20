"""
Funding Carry Strategy
Adapted version of the original funding carry strategy using the new framework
"""

from typing import Dict, List
from datetime import datetime, timezone, timedelta

from strategies.base_strategy import BaseStrategy, Signal


class FundingCarryStrategy(BaseStrategy):
    """Delta-neutral funding carry strategy"""

    def __init__(self, config: Dict = None):
        default_config = {
            'symbol': 'BTC/USDT',
            'notional_usdt': 100,
            'threshold_bps': 0.5,
            'fee_bps': 7.0,
            'slippage_bps': 2.0,
            'max_position_usdt': 1000
        }

        if config:
            default_config.update(config)

        super().__init__(strategy_id='funding_carry_v2', config=default_config)

    @property
    def name(self) -> str:
        return "Funding Carry V2"

    @property
    def description(self) -> str:
        return "Delta-neutral strategy capturing perpetual funding rates with AI optimization"

    @property
    def min_confidence_for_live(self) -> float:
        return 65.0  # Lower threshold for known strategy

    def analyze(self, market_data: Dict) -> Signal:
        """Analyze funding rate opportunities"""
        # Get funding rate
        funding_rate = market_data.get('funding_rate', 0)
        funding_rate_bps = funding_rate * 10000  # Convert to basis points

        # Calculate edge
        fee_bps = self.config['fee_bps']
        slippage_bps = self.config['slippage_bps']
        edge_bps = funding_rate_bps - fee_bps - slippage_bps

        # Get AI analysis
        ai_analysis = market_data.get('ai_analysis', {})
        ai_confidence = ai_analysis.get('confidence', 50)
        ai_recommendation = ai_analysis.get('recommendation', 'monitor')

        # Calculate time to next funding
        next_funding = market_data.get('next_funding_time')
        if next_funding:
            time_to_funding = (next_funding - datetime.now(timezone.utc)).total_seconds()
        else:
            time_to_funding = 0

        # Decision logic
        if edge_bps > self.config['threshold_bps'] and not self.position:
            # Profitable opportunity to enter
            confidence = min(100, 50 + edge_bps * 10 + ai_confidence * 0.3)

            # Boost confidence if AI agrees
            if ai_recommendation in ['strong_entry', 'cautious_entry']:
                confidence = min(100, confidence + 10)

            # Reduce confidence if too close to funding time
            if time_to_funding < 300:  # Less than 5 minutes
                confidence *= 0.7

            signal = Signal(
                action='open_long',  # Long spot, short futures
                confidence=confidence,
                size=self.config['notional_usdt'],
                reason=f"Edge: {edge_bps:.2f} bps, AI: {ai_recommendation}",
                metadata={
                    'edge_bps': edge_bps,
                    'funding_rate_bps': funding_rate_bps,
                    'time_to_funding': time_to_funding,
                    'ai_confidence': ai_confidence
                }
            )

        elif edge_bps < 0 and self.position:
            # No longer profitable, close position
            signal = Signal(
                action='close',
                confidence=90,
                size=0,
                reason=f"Edge turned negative: {edge_bps:.2f} bps",
                metadata={'edge_bps': edge_bps}
            )

        elif self.position and time_to_funding < 60:
            # Close to funding time, collect and reassess
            signal = Signal(
                action='hold',
                confidence=80,
                size=0,
                reason="Holding for funding collection",
                metadata={'time_to_funding': time_to_funding}
            )

        else:
            # No action
            signal = Signal(
                action='hold',
                confidence=0,
                size=0,
                reason=f"Edge {edge_bps:.2f} bps below threshold {self.config['threshold_bps']} bps",
                metadata={'edge_bps': edge_bps}
            )

        return signal

    def backtest(self, historical_data: List[Dict]) -> Dict:
        """Backtest the funding carry strategy"""
        results = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0,
            'total_funding_collected': 0,
            'max_drawdown': 0,
            'signals': []
        }

        position = None
        equity_curve = [0]

        for data_point in historical_data:
            signal = self.analyze(data_point)

            if signal.action == 'open_long' and not position:
                # Open position
                position = {
                    'entry_time': data_point.get('timestamp'),
                    'entry_price': data_point.get('price', 0),
                    'size': signal.size,
                    'funding_collected': 0
                }
                results['total_trades'] += 1

            elif position:
                # Collect funding if at funding time
                if data_point.get('is_funding_time', False):
                    funding_payment = (
                        position['size'] *
                        data_point.get('funding_rate', 0)
                    )
                    position['funding_collected'] += funding_payment
                    results['total_funding_collected'] += funding_payment

                # Close position if signal says so
                if signal.action == 'close':
                    # Calculate P&L (mainly from funding)
                    pnl = position['funding_collected']

                    # Account for fees
                    fees = position['size'] * (self.config['fee_bps'] / 10000) * 2  # Entry + exit
                    pnl -= fees

                    results['total_pnl'] += pnl
                    equity_curve.append(results['total_pnl'])

                    if pnl > 0:
                        results['winning_trades'] += 1

                    # Calculate max drawdown
                    peak = max(equity_curve)
                    drawdown = peak - equity_curve[-1]
                    results['max_drawdown'] = max(results['max_drawdown'], drawdown)

                    position = None

            # Record signal
            results['signals'].append({
                'timestamp': data_point.get('timestamp'),
                'action': signal.action,
                'confidence': signal.confidence,
                'edge_bps': signal.metadata.get('edge_bps', 0)
            })

        # Calculate final metrics
        if results['total_trades'] > 0:
            results['win_rate'] = (results['winning_trades'] / results['total_trades']) * 100
            results['avg_funding_per_trade'] = results['total_funding_collected'] / results['total_trades']
        else:
            results['win_rate'] = 0
            results['avg_funding_per_trade'] = 0

        return results

    def optimize_parameters(self, performance_data: Dict):
        """Optimize strategy parameters based on performance"""
        # Adjust threshold based on win rate
        if performance_data.get('win_rate', 0) < 50:
            # Increase threshold to be more selective
            self.config['threshold_bps'] = min(2.0, self.config['threshold_bps'] + 0.1)
        elif performance_data.get('win_rate', 0) > 70:
            # Decrease threshold to capture more opportunities
            self.config['threshold_bps'] = max(0.3, self.config['threshold_bps'] - 0.1)

        # Adjust position size based on confidence
        if self.confidence_score > 80:
            self.config['notional_usdt'] = min(500, self.config['notional_usdt'] * 1.1)
        elif self.confidence_score < 40:
            self.config['notional_usdt'] = max(50, self.config['notional_usdt'] * 0.9)

        self.save_state()