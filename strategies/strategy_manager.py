"""
Strategy Manager
Manages multiple trading strategies running in parallel
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from strategies.base_strategy import BaseStrategy, Signal
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator


class StrategyManager:
    """Manages and coordinates multiple trading strategies"""

    def __init__(self, telegram_notifier=None):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.telegram = telegram_notifier
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator()

        self.manager_state_file = Path("knowledge/manager_state.json")
        self.manager_state_file.parent.mkdir(parents=True, exist_ok=True)

        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.evaluation_interval = 3600  # Evaluate every hour
        self.last_evaluation = datetime.now(timezone.utc)

        # Performance tracking
        self.performance_history = []
        self.ready_for_live = []  # Strategies ready to go live

        self.load_state()

    def load_state(self):
        """Load manager state from disk"""
        if self.manager_state_file.exists():
            with open(self.manager_state_file, 'r') as f:
                state = json.load(f)
                self.performance_history = state.get('performance_history', [])
                self.ready_for_live = state.get('ready_for_live', [])

    def save_state(self):
        """Save manager state to disk"""
        state = {
            'performance_history': self.performance_history[-1000:],  # Keep last 1000 entries
            'ready_for_live': self.ready_for_live,
            'total_strategies': len(self.strategies),
            'active_strategies': sum(1 for s in self.strategies.values() if s.is_active),
            'last_evaluation': self.last_evaluation.isoformat()
        }

        with open(self.manager_state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to the manager"""
        self.strategies[strategy.strategy_id] = strategy

        if self.telegram:
            self.telegram.send_message(
                f"🆕 New strategy added: {strategy.name}\n"
                f"ID: {strategy.strategy_id}\n"
                f"Description: {strategy.description}"
            )

        self.save_state()

    def remove_strategy(self, strategy_id: str):
        """Remove a strategy from the manager"""
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            strategy.stop()
            del self.strategies[strategy_id]

            if self.telegram:
                self.telegram.send_message(
                    f"🗑️ Strategy removed: {strategy.name}\n"
                    f"Final P&L: ${strategy.metrics.total_pnl:.2f}"
                )

            self.save_state()

    async def run_strategy(self, strategy_id: str, market_data: Dict):
        """Run a single strategy with market data"""
        if strategy_id not in self.strategies:
            return

        strategy = self.strategies[strategy_id]

        if not strategy.is_active:
            return

        try:
            # Get AI analysis
            ai_analysis = self.learning_engine.analyze_market(market_data)

            # Add AI insights to market data
            market_data['ai_analysis'] = ai_analysis

            # Generate signal
            signal = strategy.analyze(market_data)

            # Execute if confident enough
            if signal.confidence > 50:
                success = strategy.execute_signal(signal)

                # Learn from the execution
                if success:
                    self.learning_engine.learn_from_trade({
                        'strategy_id': strategy_id,
                        'profit': strategy.metrics.total_pnl,
                        'patterns': ai_analysis['patterns']
                    })

                # Save strategy state
                strategy.save_state()

        except Exception as e:
            print(f"Error running strategy {strategy_id}: {e}")

    async def run_all_strategies(self, market_data: Dict):
        """Run all active strategies in parallel"""
        tasks = []
        for strategy_id in self.strategies.keys():
            task = asyncio.create_task(self.run_strategy(strategy_id, market_data))
            tasks.append(task)

        await asyncio.gather(*tasks)

    def evaluate_strategies(self):
        """Evaluate all strategies and identify those ready for live trading"""
        evaluation_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'strategies_evaluated': len(self.strategies),
            'ready_for_live': [],
            'needs_optimization': [],
            'should_stop': []
        }

        for strategy_id, strategy in self.strategies.items():
            status = strategy.get_status()

            # Check if ready for live
            if strategy.should_go_live() and strategy_id not in self.ready_for_live:
                self.ready_for_live.append(strategy_id)
                evaluation_report['ready_for_live'].append({
                    'id': strategy_id,
                    'name': strategy.name,
                    'confidence': status['confidence_score'],
                    'win_rate': status['metrics']['win_rate'],
                    'total_pnl': status['metrics']['total_pnl']
                })

                # Send Telegram alert
                if self.telegram:
                    self.telegram.send_message(
                        f"🎯 STRATEGY READY FOR LIVE!\n\n"
                        f"Strategy: {strategy.name}\n"
                        f"ID: {strategy_id}\n"
                        f"Confidence: {status['confidence_score']:.1f}%\n"
                        f"Win Rate: {status['metrics']['win_rate']:.1f}%\n"
                        f"Total P&L: ${status['metrics']['total_pnl']:.2f}\n\n"
                        f"Use /approve {strategy_id} to go live\n"
                        f"Use /reject {strategy_id} to continue testing"
                    )

            # Check if needs optimization
            elif status['metrics']['total_trades'] > 20 and status['metrics']['win_rate'] < 45:
                evaluation_report['needs_optimization'].append(strategy_id)

                # Try to optimize parameters
                current_params = strategy.config
                optimized_params = self.learning_engine.optimize_parameters(
                    strategy_id,
                    current_params,
                    status['metrics']['total_pnl']
                )
                strategy.config = optimized_params

            # Check if should stop
            elif status['metrics']['total_trades'] > 50 and status['metrics']['total_pnl'] < -100:
                evaluation_report['should_stop'].append(strategy_id)
                strategy.stop()

        # Record evaluation
        self.performance_history.append(evaluation_report)
        self.save_state()

        return evaluation_report

    def launch_new_experiment(self):
        """Launch a new experimental strategy from hypothesis generator"""
        # Get next hypothesis to test
        hypothesis = self.hypothesis_generator.get_next_hypothesis_to_test()

        if hypothesis:
            # Create experimental strategy from hypothesis
            from strategies.experimental_strategy import ExperimentalStrategy

            exp_strategy = ExperimentalStrategy(
                hypothesis_id=hypothesis['id'],
                hypothesis=hypothesis
            )

            self.add_strategy(exp_strategy)

            if self.telegram:
                self.telegram.send_message(
                    f"🧪 New Experiment Launched!\n\n"
                    f"Name: {hypothesis['name']}\n"
                    f"Category: {hypothesis['category']}\n"
                    f"Description: {hypothesis['description']}\n"
                    f"Initial Confidence: {hypothesis.get('confidence', 50)}%"
                )

            return hypothesis

        return None

    def generate_crazy_idea(self):
        """Generate and launch a crazy trading idea"""
        crazy_idea = self.hypothesis_generator.generate_crazy_idea()

        if self.telegram:
            self.telegram.send_message(
                f"🤪 CRAZY IDEA GENERATED!\n\n"
                f"Name: {crazy_idea['name']}\n"
                f"Description: {crazy_idea['description']}\n"
                f"Source: {crazy_idea['source']}\n"
                f"Risk Limit: ${crazy_idea['risk_limit']}\n\n"
                f"Testing will begin automatically..."
            )

        # Create experimental strategy for crazy idea
        from strategies.experimental_strategy import ExperimentalStrategy

        exp_strategy = ExperimentalStrategy(
            hypothesis_id=crazy_idea['id'],
            hypothesis=crazy_idea
        )

        self.add_strategy(exp_strategy)

        return crazy_idea

    def approve_strategy_for_live(self, strategy_id: str) -> bool:
        """Approve a strategy to go live"""
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]

            if strategy.go_live():
                if self.telegram:
                    self.telegram.send_message(
                        f"✅ Strategy {strategy.name} is now LIVE!\n"
                        f"Real trading will begin on next signal."
                    )

                # Remove from ready list
                if strategy_id in self.ready_for_live:
                    self.ready_for_live.remove(strategy_id)

                self.save_state()
                return True
            else:
                if self.telegram:
                    self.telegram.send_message(
                        f"⚠️ Strategy {strategy.name} doesn't meet criteria for live trading yet."
                    )

        return False

    def reject_strategy(self, strategy_id: str):
        """Reject a strategy and continue testing"""
        if strategy_id in self.ready_for_live:
            self.ready_for_live.remove(strategy_id)

            if strategy_id in self.strategies:
                strategy = self.strategies[strategy_id]

                if self.telegram:
                    self.telegram.send_message(
                        f"👎 Strategy {strategy.name} rejected.\n"
                        f"Continuing paper trading..."
                    )

                # Reset confidence to continue learning
                strategy.confidence_score = 50
                strategy.save_state()

            self.save_state()

    def get_ai_report(self) -> Dict:
        """Generate comprehensive AI report"""
        # Get market insights
        market_insights = self.learning_engine.get_market_insights()

        # Get hypothesis statistics
        hypothesis_stats = self.hypothesis_generator.get_statistics()

        # Compile strategy performance
        strategy_performance = []
        for strategy_id, strategy in self.strategies.items():
            status = strategy.get_status()
            strategy_performance.append({
                'name': strategy.name,
                'confidence': status['confidence_score'],
                'win_rate': status['metrics']['win_rate'],
                'total_pnl': status['metrics']['total_pnl'],
                'status': 'LIVE' if strategy.is_live else 'TESTING'
            })

        # Sort by total P&L
        strategy_performance.sort(key=lambda x: x['total_pnl'], reverse=True)

        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'active_strategies': len(self.strategies),
            'live_strategies': sum(1 for s in self.strategies.values() if s.is_live),
            'ready_for_live': len(self.ready_for_live),
            'top_strategies': strategy_performance[:5],
            'market_insights': market_insights,
            'hypothesis_statistics': hypothesis_stats,
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate AI recommendations"""
        recommendations = []

        # Check if we need more experiments
        active_experiments = sum(1 for s in self.strategies.values() if 'experimental' in s.name.lower())
        if active_experiments < 3:
            recommendations.append("Launch more experimental strategies for discovery")

        # Check if we have successful strategies not yet live
        if self.ready_for_live:
            recommendations.append(f"Review {len(self.ready_for_live)} strategies ready for live trading")

        # Check learning progress
        insights = self.learning_engine.get_market_insights()
        if insights['discovered_edges'] < 10:
            recommendations.append("Need more market data to discover profitable edges")

        # Performance-based recommendations
        profitable_strategies = sum(
            1 for s in self.strategies.values()
            if s.metrics.total_pnl > 0
        )

        if profitable_strategies < len(self.strategies) * 0.3:
            recommendations.append("Consider adjusting risk parameters - too many losing strategies")

        return recommendations

    def start(self):
        """Start the strategy manager"""
        self.is_running = True

        async def run_loop():
            while self.is_running:
                try:
                    # Get market data (placeholder - integrate with exchange)
                    market_data = self._get_market_data()

                    # Run all strategies
                    await self.run_all_strategies(market_data)

                    # Periodic evaluation
                    if (datetime.now(timezone.utc) - self.last_evaluation).total_seconds() > self.evaluation_interval:
                        self.evaluate_strategies()
                        self.last_evaluation = datetime.now(timezone.utc)

                        # Maybe launch new experiment
                        if self.learning_engine.should_explore_new_strategy():
                            self.launch_new_experiment()

                    # Sleep before next iteration
                    await asyncio.sleep(60)  # Run every minute

                except Exception as e:
                    print(f"Error in strategy manager loop: {e}")
                    await asyncio.sleep(10)

        # Run async loop
        asyncio.run(run_loop())

    def stop(self):
        """Stop the strategy manager"""
        self.is_running = False

        # Stop all strategies
        for strategy in self.strategies.values():
            strategy.stop()

        self.save_state()

        if self.telegram:
            self.telegram.send_message(
                "🛑 Strategy Manager stopped.\n"
                f"Final statistics:\n"
                f"Total strategies: {len(self.strategies)}\n"
                f"Profitable: {sum(1 for s in self.strategies.values() if s.metrics.total_pnl > 0)}"
            )

    def _get_market_data(self) -> Dict:
        """Get current market data - placeholder for exchange integration"""
        # This would integrate with your exchange API
        # For now, returning dummy data
        return {
            'timestamp': datetime.now(timezone.utc),
            'price': 65000,
            'volume': 1000000,
            'funding_rate': 0.0001,
            'price_history': [],
            'volume_history': []
        }