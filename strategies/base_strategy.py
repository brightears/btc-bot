"""
Base Strategy Abstract Class
Defines the interface for all trading strategies
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid


@dataclass
class StrategyMetrics:
    """Performance metrics for a strategy"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    total_fees: float = 0.0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_win_rate(self):
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100

    def to_dict(self) -> Dict:
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
            'avg_profit': self.avg_profit,
            'avg_loss': self.avg_loss,
            'best_trade': self.best_trade,
            'worst_trade': self.worst_trade,
            'total_fees': self.total_fees,
            'runtime_hours': (datetime.now(timezone.utc) - self.start_time).total_seconds() / 3600
        }


@dataclass
class Signal:
    """Trading signal from a strategy"""
    action: str  # 'open_long', 'open_short', 'close', 'hold'
    confidence: float  # 0-100
    size: float  # Position size in USDT
    reason: str  # Explanation for the signal
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""

    def __init__(self, strategy_id: str = None, config: Dict = None):
        self.strategy_id = strategy_id or str(uuid.uuid4())[:8]
        self.config = config or {}
        self.metrics = StrategyMetrics()
        self.is_live = False
        self.is_active = True
        self.position = None
        self.state_file = Path(f"knowledge/strategies/{self.strategy_id}_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Learning-related attributes
        self.patterns_learned = []
        self.confidence_score = 50.0  # Start at neutral confidence
        self.adaptation_rate = 0.1  # How quickly strategy adapts

        self.load_state()

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Strategy description"""
        pass

    @property
    @abstractmethod
    def min_confidence_for_live(self) -> float:
        """Minimum confidence score needed to go live"""
        pass

    @abstractmethod
    def analyze(self, market_data: Dict) -> Signal:
        """
        Analyze market data and generate trading signal

        Args:
            market_data: Current market data including price, volume, indicators

        Returns:
            Signal object with trading decision
        """
        pass

    @abstractmethod
    def backtest(self, historical_data: List[Dict]) -> Dict:
        """
        Run backtest on historical data

        Args:
            historical_data: List of historical market data points

        Returns:
            Backtest results including metrics
        """
        pass

    def execute_signal(self, signal: Signal) -> bool:
        """Execute a trading signal"""
        if signal.action == 'hold':
            return True

        # Record the trade attempt
        self.metrics.total_trades += 1

        # In dry-run mode, simulate execution
        if not self.is_live:
            self.simulate_execution(signal)
            return True

        # In live mode, actual execution would happen here
        # This would integrate with exchange APIs
        return self.execute_live_trade(signal)

    def simulate_execution(self, signal: Signal):
        """Simulate trade execution for dry-run mode"""
        # Simplified simulation - you'd add more realistic simulation here
        simulated_pnl = (signal.confidence - 50) * 0.01 * signal.size  # Simple confidence-based P&L

        self.update_metrics(simulated_pnl)
        self.learn_from_trade(signal, simulated_pnl)

    def execute_live_trade(self, signal: Signal) -> bool:
        """Execute live trade - to be implemented with exchange integration"""
        # This would connect to actual exchange APIs
        raise NotImplementedError("Live trading not yet implemented")

    def update_metrics(self, pnl: float):
        """Update strategy metrics after a trade"""
        self.metrics.total_pnl += pnl

        if pnl > 0:
            self.metrics.winning_trades += 1
            self.metrics.avg_profit = (
                (self.metrics.avg_profit * (self.metrics.winning_trades - 1) + pnl)
                / self.metrics.winning_trades
            )
            if pnl > self.metrics.best_trade:
                self.metrics.best_trade = pnl
        else:
            self.metrics.losing_trades += 1
            self.metrics.avg_loss = (
                (self.metrics.avg_loss * (self.metrics.losing_trades - 1) + abs(pnl))
                / self.metrics.losing_trades
            )
            if pnl < self.metrics.worst_trade:
                self.metrics.worst_trade = pnl

        self.metrics.update_win_rate()
        self.update_confidence()

    def learn_from_trade(self, signal: Signal, pnl: float):
        """Learn from trade outcome to improve future decisions"""
        # Adjust confidence based on outcome
        if pnl > 0:
            self.confidence_score = min(100, self.confidence_score + self.adaptation_rate * 10)
        else:
            self.confidence_score = max(0, self.confidence_score - self.adaptation_rate * 5)

        # Store pattern for future reference
        pattern = {
            'timestamp': signal.timestamp.isoformat(),
            'signal': signal.action,
            'confidence': signal.confidence,
            'pnl': pnl,
            'market_conditions': signal.metadata.get('market_conditions', {})
        }
        self.patterns_learned.append(pattern)

        # Keep only recent patterns (last 100)
        self.patterns_learned = self.patterns_learned[-100:]

    def update_confidence(self):
        """Update overall strategy confidence based on recent performance"""
        if self.metrics.total_trades > 10:  # Need minimum trades for confidence
            # Weighted confidence based on win rate and profit factor
            profit_factor = abs(self.metrics.avg_profit / self.metrics.avg_loss) if self.metrics.avg_loss > 0 else 1

            confidence_from_winrate = self.metrics.win_rate
            confidence_from_profit = min(100, profit_factor * 30)

            # Weighted average
            self.confidence_score = (confidence_from_winrate * 0.6 + confidence_from_profit * 0.4)

    def should_go_live(self) -> bool:
        """Check if strategy meets criteria for live trading"""
        return (
            self.confidence_score >= self.min_confidence_for_live and
            self.metrics.total_trades >= 50 and  # Minimum sample size
            self.metrics.win_rate >= 55 and  # Minimum win rate
            self.metrics.total_pnl > 0  # Profitable overall
        )

    def get_status(self) -> Dict:
        """Get current strategy status"""
        return {
            'strategy_id': self.strategy_id,
            'name': self.name,
            'description': self.description,
            'is_live': self.is_live,
            'is_active': self.is_active,
            'confidence_score': round(self.confidence_score, 2),
            'ready_for_live': self.should_go_live(),
            'metrics': self.metrics.to_dict(),
            'position': self.position,
            'patterns_learned': len(self.patterns_learned)
        }

    def save_state(self):
        """Save strategy state to disk"""
        state = {
            'strategy_id': self.strategy_id,
            'config': self.config,
            'metrics': self.metrics.to_dict(),
            'is_live': self.is_live,
            'is_active': self.is_active,
            'confidence_score': self.confidence_score,
            'patterns_learned': self.patterns_learned[-50:],  # Save last 50 patterns
            'position': self.position
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self):
        """Load strategy state from disk"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.confidence_score = state.get('confidence_score', 50.0)
            self.patterns_learned = state.get('patterns_learned', [])
            self.is_live = state.get('is_live', False)
            self.is_active = state.get('is_active', True)
            self.position = state.get('position')

            # Restore metrics
            metrics_dict = state.get('metrics', {})
            for key, value in metrics_dict.items():
                if hasattr(self.metrics, key) and key != 'start_time':
                    setattr(self.metrics, key, value)

    def reset(self):
        """Reset strategy to initial state"""
        self.metrics = StrategyMetrics()
        self.confidence_score = 50.0
        self.patterns_learned = []
        self.position = None
        self.save_state()

    def stop(self):
        """Stop the strategy"""
        self.is_active = False
        if self.position:
            # Close any open positions
            self.execute_signal(Signal(
                action='close',
                confidence=100,
                size=0,
                reason='Strategy stopped'
            ))
        self.save_state()

    def go_live(self):
        """Switch strategy to live trading"""
        if self.should_go_live():
            self.is_live = True
            self.save_state()
            return True
        return False

    def go_paper(self):
        """Switch strategy back to paper trading"""
        self.is_live = False
        self.save_state()