"""
Strategy Manager
Manages multiple trading strategies running in parallel
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from strategies.base_strategy import BaseStrategy, Signal
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator
from ai_brain.historical_data_fetcher import HistoricalDataFetcher


class StrategyManager:
    """Manages and coordinates multiple trading strategies"""

    def __init__(self, telegram_notifier=None):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.telegram = telegram_notifier
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator()
        self.historical_fetcher = HistoricalDataFetcher()
        self.logger = logging.getLogger(__name__)

        self.manager_state_file = Path("knowledge/manager_state.json")
        self.strategies_file = Path("knowledge/strategies.json")
        self.manager_state_file.parent.mkdir(parents=True, exist_ok=True)

        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.evaluation_interval = 3600  # Evaluate every hour
        self.last_evaluation = datetime.now(timezone.utc)

        # Performance tracking
        self.performance_history = []
        self.ready_for_live = []  # Strategies ready to go live
        self.backtest_results = {}  # Store backtest results by strategy ID

        self.load_state()
        self.load_strategies()

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

        # Also save strategies
        self.save_strategies()

    def save_strategies(self):
        """Save all strategies to JSON file"""
        strategies_data = {}
        for strategy_id, strategy in self.strategies.items():
            strategies_data[strategy_id] = {
                'id': strategy.strategy_id,
                'name': strategy.name,
                'type': strategy.__class__.__name__,
                'parameters': getattr(strategy, 'parameters', {}),
                'confidence_score': strategy.confidence_score,
                'is_active': strategy.is_active,
                'is_live': strategy.is_live,
                'metrics': strategy.get_status()['metrics'],
                'created_at': getattr(strategy, 'created_at', datetime.now(timezone.utc)).isoformat()
            }

        with open(self.strategies_file, 'w') as f:
            json.dump(strategies_data, f, indent=2, default=str)
        self.logger.info(f"Saved {len(strategies_data)} strategies to {self.strategies_file}")

    def load_strategies(self):
        """Load strategies from JSON file"""
        if not self.strategies_file.exists():
            self.logger.info("No strategies file found, starting fresh")
            return

        try:
            with open(self.strategies_file, 'r') as f:
                strategies_data = json.load(f)

            for strategy_id, data in strategies_data.items():
                # For now, just log that we would load this strategy
                # In a full implementation, we'd recreate the strategy objects
                self.logger.info(f"Found saved strategy: {data['name']} (ID: {strategy_id})")

            self.logger.info(f"Found {len(strategies_data)} saved strategies")
        except Exception as e:
            self.logger.error(f"Error loading strategies: {e}")

    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to the manager"""
        self.strategies[strategy.strategy_id] = strategy
        self.save_strategies()  # Persist immediately

        if self.telegram:
            import asyncio
            message = (
                f"🆕 New strategy added: {strategy.name}\n"
                f"ID: {strategy.strategy_id}\n"
                f"Description: {strategy.description}"
            )
            # Handle both sync and async telegram notifiers
            if asyncio.iscoroutinefunction(self.telegram.send_message):
                asyncio.create_task(self.telegram.send_message(message))
            else:
                self.telegram.send_message(message)

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
            'should_stop': [],
            'backtest_vs_live': []
        }

        for strategy_id, strategy in self.strategies.items():
            status = strategy.get_status()

            # Compare with backtest if available
            if strategy_id in self.backtest_results:
                backtest = self.backtest_results[strategy_id]
                live_metrics = status['metrics']

                comparison = {
                    'strategy_id': strategy_id,
                    'name': strategy.name,
                    'backtest_win_rate': backtest.get('win_rate', 0),
                    'live_win_rate': live_metrics['win_rate'],
                    'backtest_pnl': backtest.get('total_pnl', 0),
                    'live_pnl': live_metrics['total_pnl'],
                    'performance_delta': live_metrics['win_rate'] - backtest.get('win_rate', 0)
                }
                evaluation_report['backtest_vs_live'].append(comparison)

            # Check if ready for live
            if strategy.should_go_live() and strategy_id not in self.ready_for_live:
                self.ready_for_live.append(strategy_id)

                # Include backtest comparison in ready notification
                backtest_info = ""
                if strategy_id in self.backtest_results:
                    bt = self.backtest_results[strategy_id]
                    backtest_info = f"Backtest: {bt.get('win_rate', 0):.1f}% win rate, "

                evaluation_report['ready_for_live'].append({
                    'id': strategy_id,
                    'name': strategy.name,
                    'confidence': status['confidence_score'],
                    'win_rate': status['metrics']['win_rate'],
                    'total_pnl': status['metrics']['total_pnl'],
                    'backtest_comparison': backtest_info
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

    async def backtest_strategy(self, strategy: BaseStrategy) -> Dict:
        """Run backtest on a strategy before live testing"""
        self.logger.info(f"Starting backtest for strategy: {strategy.name}")
        try:
            # Fetch historical data
            self.logger.info("Fetching 30 days of historical data for backtesting...")
            backtest_data = await self.historical_fetcher.get_backtest_data(days=30)

            if not backtest_data:
                return {
                    'success': False,
                    'error': 'No historical data available'
                }

            # Run backtest
            self.logger.info(f"Running backtest with {len(backtest_data)} data points...")
            results = strategy.backtest(backtest_data)

            # Store results
            self.backtest_results[strategy.strategy_id] = results
            self.logger.info(f"Backtest complete - Win rate: {results.get('win_rate', 0):.1f}%, Total P&L: ${results.get('total_pnl', 0):.2f}")

            return {
                'success': True,
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Backtest error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def launch_new_experiment(self):
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

            # Run backtest first
            backtest_result = await self.backtest_strategy(exp_strategy)

            if backtest_result['success']:
                backtest_metrics = backtest_result['results']

                # Only add strategy if backtest shows promise
                if backtest_metrics.get('win_rate', 0) >= 40 or backtest_metrics.get('total_pnl', 0) > 0:
                    self.add_strategy(exp_strategy)

                    # Send detailed notification with backtest results
                    if self.telegram:
                        await self.telegram.send_message(
                            f"🧪 *New Experiment Launched!*\n\n"
                            f"*Name:* {hypothesis['name']}\n"
                            f"*Category:* {hypothesis['category']}\n"
                            f"*Description:* {hypothesis['description']}\n"
                            f"*Initial Confidence:* {hypothesis.get('confidence', 50)}%\n\n"
                            f"*📊 Backtest Results (30 days):*\n"
                            f"• Total Trades: {backtest_metrics.get('total_trades', 0)}\n"
                            f"• Win Rate: {backtest_metrics.get('win_rate', 0):.1f}%\n"
                            f"• Total P&L: ${backtest_metrics.get('total_pnl', 0):.2f}\n"
                            f"• Max Drawdown: ${backtest_metrics.get('max_drawdown', 0):.2f}\n\n"
                            f"_Strategy passed backtest and is now live testing_"
                        )
                else:
                    # Strategy failed backtest
                    if self.telegram:
                        await self.telegram.send_message(
                            f"❌ *Experiment Failed Backtest*\n\n"
                            f"*Name:* {hypothesis['name']}\n"
                            f"*Win Rate:* {backtest_metrics.get('win_rate', 0):.1f}%\n"
                            f"*P&L:* ${backtest_metrics.get('total_pnl', 0):.2f}\n\n"
                            f"_Strategy discarded, generating new hypothesis..._"
                        )

                    # Mark hypothesis as failed
                    self.hypothesis_generator.evaluate_hypothesis(
                        hypothesis['id'],
                        backtest_metrics
                    )

                    # Try another hypothesis
                    return await self.launch_new_experiment()
            else:
                # Backtest failed to run
                # Add strategy anyway but note the issue
                self.add_strategy(exp_strategy)

                if self.telegram:
                    await self.telegram.send_message(
                        f"🧪 *New Experiment (No Backtest)*\n\n"
                        f"*Name:* {hypothesis['name']}\n"
                        f"*Category:* {hypothesis['category']}\n"
                        f"_Backtest unavailable, proceeding with live testing_"
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

            perf_data = {
                'name': strategy.name,
                'confidence': status['confidence_score'],
                'win_rate': status['metrics']['win_rate'],
                'total_pnl': status['metrics']['total_pnl'],
                'status': 'LIVE' if strategy.is_live else 'TESTING'
            }

            # Add backtest comparison if available
            if strategy_id in self.backtest_results:
                bt = self.backtest_results[strategy_id]
                perf_data['backtest_win_rate'] = bt.get('win_rate', 0)
                perf_data['backtest_pnl'] = bt.get('total_pnl', 0)
                perf_data['performance_vs_backtest'] = (
                    'outperforming' if status['metrics']['win_rate'] > bt.get('win_rate', 0)
                    else 'underperforming'
                )

            strategy_performance.append(perf_data)

        # Sort by total P&L
        strategy_performance.sort(key=lambda x: x['total_pnl'], reverse=True)

        # Calculate backtest statistics
        backtest_stats = {
            'total_backtested': len(self.backtest_results),
            'avg_backtest_win_rate': sum(bt.get('win_rate', 0) for bt in self.backtest_results.values()) / max(len(self.backtest_results), 1),
            'strategies_beating_backtest': sum(
                1 for sid, strategy in self.strategies.items()
                if sid in self.backtest_results and
                strategy.get_status()['metrics']['win_rate'] > self.backtest_results[sid].get('win_rate', 0)
            )
        }

        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'active_strategies': len(self.strategies),
            'live_strategies': sum(1 for s in self.strategies.values() if s.is_live),
            'ready_for_live': len(self.ready_for_live),
            'top_strategies': strategy_performance[:5],
            'backtest_statistics': backtest_stats,
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