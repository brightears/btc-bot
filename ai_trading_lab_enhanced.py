#!/usr/bin/env python3
"""
AI Trading Lab - Enhanced with LLM Intelligence
Real-time market analysis with Gemini 2.5 Flash integration
"""

import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from telegram import Bot
import random
import logging

# Import AI components
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator
from ai_brain.llm_analyzer import GeminiAnalyzer
from ai_brain.news_fetcher import CryptoNewsFetcher
from ai_brain.sentiment_analyzer import MarketSentimentAnalyzer
from ai_brain.onchain_monitor import OnChainMonitor
from strategies.strategy_manager import StrategyManager
from strategies.funding_carry import FundingCarryStrategy

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class EnhancedAITradingLab:
    """AI Trading Lab with LLM-powered intelligence"""

    def __init__(self):
        """Initialize Enhanced AI Trading Lab"""
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found")

        # Simple bot for sending messages only
        self.bot = Bot(token=self.token)
        self.logger = logging.getLogger(__name__)

        # Initialize LLM components
        print("🤖 Initializing LLM Intelligence...")
        self.llm_analyzer = GeminiAnalyzer()
        self.news_fetcher = CryptoNewsFetcher()
        self.sentiment_analyzer = MarketSentimentAnalyzer(llm_analyzer=self.llm_analyzer)
        self.onchain_monitor = OnChainMonitor()

        # Initialize enhanced AI components
        print("🧠 Initializing Enhanced AI components...")
        self.strategy_manager = StrategyManager(telegram_notifier=self)
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator(llm_analyzer=self.llm_analyzer)

        # User preferences
        self.auto_approve_threshold = 85
        self.max_risk_per_strategy = 1000

        # Tracking for notifications
        self.last_heartbeat = datetime.now(timezone.utc)
        self.last_hourly_report = datetime.now(timezone.utc)
        self.last_hypothesis = datetime.now(timezone.utc)
        self.last_news_check = datetime.now(timezone.utc)
        self.last_onchain_check = datetime.now(timezone.utc)
        self.startup_time = datetime.now(timezone.utc)
        self.notifications_sent = 0

        # Cache for analysis
        self.latest_sentiment = None
        self.latest_news = []
        self.latest_onchain = None

        # Initialize REAL market data fetcher
        try:
            from ai_brain.realtime_market_data import RealtimeMarketData
            self.market_data_fetcher = RealtimeMarketData()
            self.use_real_data = True
            print("✅ Using REAL market data from Binance")
        except ImportError:
            self.market_data_fetcher = None
            self.use_real_data = False
            print("⚠️ Real market data unavailable, using simulated")

        # Initialize REAL paper trading engine
        try:
            from ai_brain.paper_trading_engine import PaperTradingEngine
            self.paper_trader = PaperTradingEngine(initial_balance=10000)
            print("✅ Paper trading with REAL price movements")
        except ImportError:
            self.paper_trader = None
            print("⚠️ Paper trading engine not available")

        # Initialize data integrity validator
        try:
            from ai_brain.data_integrity_validator import DataIntegrityValidator
            self.data_validator = DataIntegrityValidator()
            print("✅ Data integrity validation enabled")
        except ImportError:
            self.data_validator = None
            print("⚠️ Data validator not available")

    async def send_message(self, text: str, important: bool = False):
        """Send message to Telegram"""
        try:
            if self.chat_id:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode='Markdown'
                )
                self.notifications_sent += 1
                print(f"📱 [{datetime.now().strftime('%H:%M')}] Sent notification #{self.notifications_sent}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def initialize_strategies(self):
        """Initialize and load strategies"""
        # Add funding carry as base strategy
        funding_strategy = FundingCarryStrategy()
        self.strategy_manager.add_strategy(funding_strategy)
        print(f"✅ Loaded {funding_strategy.name}")

        # Try to load pending hypotheses
        try:
            with open('knowledge/hypotheses.json', 'r') as f:
                data = json.load(f)
                hypotheses = data.get('pending', [])
                print(f"📚 Found {len(hypotheses)} pending hypotheses")
        except:
            print("📊 Starting with Funding Carry strategy only")

    def _get_market_data(self):
        """Get REAL market data from exchanges (synchronous wrapper)"""
        # Try to use real market data if available
        if self.use_real_data and self.market_data_fetcher:
            # Run async function in sync context
            try:
                import asyncio
                try:
                    # Try to use existing event loop if available
                    loop = asyncio.get_running_loop()
                    # We're in an async context already, can't use run_until_complete
                    # Use cached data if available
                    if hasattr(self, '_last_real_data') and self._last_real_data:
                        # Use cached data if it's recent (within 30 seconds)
                        if 'timestamp' in self._last_real_data:
                            age = (datetime.now(timezone.utc) - self._last_real_data['timestamp']).total_seconds()
                            if age < 30:
                                return self._last_real_data
                    # Return placeholder, will fetch async in background
                    asyncio.create_task(self._fetch_and_cache_market_data())
                    return self._last_real_data if hasattr(self, '_last_real_data') else self._get_simulated_market_data()
                except RuntimeError:
                    # No event loop running, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    real_data = loop.run_until_complete(self.market_data_fetcher.get_market_data())
                    loop.close()

                # Add sentiment from our analyzer
                real_data['sentiment'] = self.latest_sentiment.get('sentiment_label', 'neutral') if self.latest_sentiment else 'neutral'

                # Calculate volatility from real data
                if real_data.get('price_history') and len(real_data['price_history']) > 10:
                    prices = real_data['price_history'][-10:]
                    avg = sum(prices) / len(prices)
                    variance = sum((p - avg) ** 2 for p in prices) / len(prices)
                    volatility_pct = (variance ** 0.5) / avg
                    real_data['volatility'] = 'high' if volatility_pct > 0.02 else 'low' if volatility_pct < 0.01 else 'medium'
                else:
                    real_data['volatility'] = 'medium'

                # Cache for next call
                self._last_real_data = real_data
                return real_data

            except Exception as e:
                self.logger.error(f"Error getting real market data: {e}")

        # Fallback to simulated data (should rarely happen)
        return self._get_simulated_market_data()

    async def _get_market_data_async(self):
        """Get REAL market data from exchanges (async version)"""
        # Try to use real market data if available
        if self.use_real_data and self.market_data_fetcher:
            try:
                real_data = await self.market_data_fetcher.get_market_data()

                # Add sentiment from our analyzer
                real_data['sentiment'] = self.latest_sentiment.get('sentiment_label', 'neutral') if self.latest_sentiment else 'neutral'

                # Calculate volatility from real data
                if real_data.get('price_history') and len(real_data['price_history']) > 10:
                    prices = real_data['price_history'][-10:]
                    avg = sum(prices) / len(prices)
                    variance = sum((p - avg) ** 2 for p in prices) / len(prices)
                    volatility_pct = (variance ** 0.5) / avg
                    real_data['volatility'] = 'high' if volatility_pct > 0.02 else 'low' if volatility_pct < 0.01 else 'medium'
                else:
                    real_data['volatility'] = 'medium'

                # Cache for next call
                self._last_real_data = real_data
                return real_data

            except Exception as e:
                self.logger.error(f"Error getting real market data: {e}")

        # Fallback to simulated data
        return self._get_simulated_market_data()

    def _get_simulated_market_data(self):
        """EMERGENCY ONLY - Returns safe fallback that prevents trading"""
        self.logger.critical("NO REAL DATA AVAILABLE - TRADING DISABLED!")

        # Return minimal safe data that will prevent any trading
        return {
            'timestamp': datetime.now(timezone.utc),
            'price': 0,  # Invalid price to prevent trading
            'volume': 0,
            'funding_rate': 0,
            'sentiment': 'unknown',
            'price_history': [],
            'volume_history': [],
            'volatility': 'unknown',
            'is_real_data': False,
            'data_quality': {
                'score': 0,
                'issues': ['CRITICAL: No real market data available', 'Trading DISABLED for safety']
            },
            'error': 'NO_REAL_DATA',
            'trading_allowed': False
        }

    async def fetch_real_time_intelligence(self):
        """Fetch real-time market intelligence from all sources"""
        now = datetime.now(timezone.utc)

        # Fetch news every 15 minutes
        if (now - self.last_news_check).total_seconds() > 900:
            try:
                self.latest_news = await self.news_fetcher.fetch_all_news(max_age_hours=6)
                self.last_news_check = now
                print(f"📰 Fetched {len(self.latest_news)} news items")
            except Exception as e:
                self.logger.error(f"News fetch error: {e}")

        # Check on-chain data every 30 minutes
        if (now - self.last_onchain_check).total_seconds() > 1800:
            try:
                self.latest_onchain = await self.onchain_monitor.get_market_intelligence()
                self.last_onchain_check = now
                print(f"⛓️ Updated on-chain metrics")
            except Exception as e:
                self.logger.error(f"On-chain fetch error: {e}")

    async def send_startup_report(self):
        """Send enhanced startup report"""
        strategies = list(self.strategy_manager.strategies.values()) if hasattr(self.strategy_manager, 'strategies') else []

        msg = "🚀 *Enhanced AI Trading Lab Started!*\n\n"
        msg += "*System Status:*\n"
        msg += "• 🧠 Learning Engine: Online\n"
        msg += "• 🤖 Gemini 2.5 Flash: Connected\n"
        msg += "• 📰 News Monitor: Active\n"
        msg += "• ⛓️ On-chain Analysis: Running\n"
        msg += "• 📊 Sentiment Analysis: Enabled\n"
        msg += "• 🔬 Pattern Recognition: Active\n\n"

        msg += f"*Active Strategies:* {len(strategies)}\n"

        msg += "\n*New AI Features:*\n"
        msg += "• Real-time news sentiment analysis\n"
        msg += "• On-chain data monitoring\n"
        msg += "• LLM-powered hypothesis generation\n"
        msg += "• Google Search grounding for market intel\n"
        msg += "• Multi-source sentiment aggregation\n\n"

        msg += "_Testing strategies with enhanced AI intelligence. I'll notify you when they're ready for live trading._"

        await self.send_message(msg, important=True)

    async def send_ai_insights(self):
        """Send AI-generated market insights"""
        try:
            market_data = await self._get_market_data_async()

            # Get comprehensive sentiment
            sentiment = await self.sentiment_analyzer.analyze_comprehensive_sentiment(
                market_data,
                self.latest_news
            )

            # Get LLM market analysis
            llm_analysis = await self.llm_analyzer.analyze_market_conditions(market_data)

            # Search for real-time market intel
            search_query = "Bitcoin price prediction next 24 hours latest news"
            market_intel = await self.llm_analyzer.search_market_intel(search_query)

            msg = "🤖 *AI Market Intelligence*\n\n"

            msg += f"*Sentiment Analysis:*\n"
            msg += f"• Overall: {sentiment['sentiment_label']} ({sentiment['composite_score']:.2f})\n"
            msg += f"• Market Regime: {sentiment['market_regime']}\n"
            msg += f"• Trading Bias: {sentiment['trading_bias']}\n"
            msg += f"• Confidence: {sentiment['confidence']:.1f}%\n"

            if sentiment.get('divergences'):
                msg += f"\n*⚠️ Divergences Detected:*\n"
                for div in sentiment['divergences'][:2]:
                    msg += f"• {div}\n"

            msg += f"\n*LLM Market View:*\n"
            msg += f"• State: {llm_analysis.get('market_state', 'Unknown')}\n"
            msg += f"• Stance: {llm_analysis.get('trading_stance', 'Neutral')}\n"

            if llm_analysis.get('key_risks'):
                msg += f"• Key Risk: {llm_analysis['key_risks'][0] if llm_analysis['key_risks'] else 'None identified'}\n"

            if self.latest_onchain:
                fear_greed = self.latest_onchain.get('fear_greed', {})
                msg += f"\n*On-Chain Metrics:*\n"
                msg += f"• Fear/Greed: {fear_greed.get('fear_greed_index', 50)} ({fear_greed.get('sentiment', 'Neutral')})\n"

                signals = self.latest_onchain.get('signals', [])
                if signals:
                    strong_signals = [s for s in signals if s.get('strength') == 'high']
                    if strong_signals:
                        msg += f"• Signal: {strong_signals[0]['reason']}\n"

            msg += f"\n_AI analyzed {len(self.latest_news)} news sources and on-chain data_"

            await self.send_message(msg)

        except Exception as e:
            self.logger.error(f"Error sending AI insights: {e}")

    async def generate_ai_hypothesis(self, market_data: Dict):
        """Generate AI-powered trading hypothesis"""
        try:
            # Prepare enriched market context
            market_context = {
                'sentiment': self.latest_sentiment['sentiment_label'] if self.latest_sentiment else 'neutral',
                'volatility': market_data.get('volatility', 'medium'),
                'patterns': [],
                'news_factors': [n['title'] for n in self.latest_news[:3]] if self.latest_news else []
            }

            # Generate hypothesis with LLM
            hypothesis = self.hypothesis_generator.generate_hypothesis(market_context)

            # Send notification if confidence is high
            if hypothesis.get('confidence', 0) > 60:
                msg = f"🔬 *AI-Generated Hypothesis*\n\n"
                msg += f"*Name:* {hypothesis['name']}\n"
                msg += f"*Category:* {hypothesis['category']}\n"
                msg += f"*Confidence:* {hypothesis['confidence']}%\n"

                if hypothesis.get('llm_generated'):
                    msg += f"\n*AI Reasoning:*\n_{hypothesis.get('description', 'No description')}_\n"

                msg += f"\n_Added to testing pipeline with LLM monitoring_"

                await self.send_message(msg)

            return hypothesis

        except Exception as e:
            self.logger.error(f"Error generating AI hypothesis: {e}")
            return None

    async def run_enhanced_ai_loop(self):
        """Main AI loop with LLM intelligence"""
        print("🤖 Starting Enhanced AI Trading Lab main loop...")

        # Send startup message
        await self.send_startup_report()

        iteration = 0
        while True:
            try:
                iteration += 1
                now = datetime.now(timezone.utc)

                # Fetch real-time intelligence
                await self.fetch_real_time_intelligence()

                # Get market data
                market_data = await self._get_market_data_async()

                # Update sentiment
                self.latest_sentiment = await self.sentiment_analyzer.analyze_comprehensive_sentiment(
                    market_data,
                    self.latest_news
                )

                # AI analysis
                analysis = self.learning_engine.analyze_market(market_data)

                # Update all strategies
                if hasattr(self.strategy_manager, 'strategies'):
                    for strategy_id, strategy in self.strategy_manager.strategies.items():
                        # Use REAL paper trading instead of random simulation
                        if self.paper_trader and hasattr(strategy, 'analyze'):
                            # CRITICAL: Validate data integrity before ANY trading
                            if self.data_validator:
                                data_valid, data_issues = self.data_validator.validate_market_data(market_data)
                                if not data_valid:
                                    self.logger.error(f"Data validation failed: {data_issues}")
                                    # Skip this iteration - DO NOT TRADE ON BAD DATA
                                    continue

                            # Get real trading signal from strategy
                            signal = strategy.analyze(market_data)

                            if signal and signal.action != 'hold':
                                # Validate signal before execution
                                if self.data_validator:
                                    signal_valid, signal_issues = self.data_validator.validate_trading_signal(
                                        {'action': signal.action, 'size': signal.size},
                                        market_data
                                    )
                                    if not signal_valid:
                                        self.logger.warning(f"Signal validation failed: {signal_issues}")
                                        continue

                                # Execute with REAL paper trading engine
                                trade_result = self.paper_trader.execute_trade(
                                    {
                                        'action': signal.action,
                                        'size': signal.size,
                                        'stop_loss': getattr(signal, 'stop_loss', None),
                                        'take_profit': getattr(signal, 'take_profit', None),
                                        'strategy_id': strategy.id
                                    },
                                    market_data
                                )

                                # Update strategy metrics with REAL results
                                if trade_result.get('success') and trade_result.get('pnl_usdt') is not None:
                                    real_pnl = trade_result['pnl_usdt']
                                    if hasattr(strategy.metrics, 'record_trade'):
                                        strategy.metrics.record_trade(real_pnl)

                                    # Adjust confidence based on REAL performance
                                    if real_pnl > 0:
                                        strategy.confidence_score = min(100, strategy.confidence_score + 0.5)
                                    else:
                                        strategy.confidence_score = max(0, strategy.confidence_score - 0.3)

                        # Check stop losses and take profits with REAL prices
                        if self.paper_trader:
                            triggered_orders = self.paper_trader.check_stop_loss_take_profit(market_data)
                            for order in triggered_orders:
                                if order['result'].get('pnl_usdt'):
                                    self.logger.info(f"Order triggered: {order['type']} - P&L: ${order['result']['pnl_usdt']:.2f}")

                # Send AI insights every 2 hours
                if iteration % 120 == 0:
                    await self.send_ai_insights()

                # Strategy evaluation (every hour)
                if iteration % 60 == 0:
                    print("🔬 Running strategy evaluation...")
                    if hasattr(self.strategy_manager, 'evaluate_strategies'):
                        evaluation_report = self.strategy_manager.evaluate_strategies()
                        if evaluation_report:
                            # Send evaluation report
                            msg = "📊 *Strategy Evaluation Report*\n\n"
                            for sid, eval_data in evaluation_report.items():
                                msg += f"*{eval_data.get('name', sid)}:*\n"
                                msg += f"• Live Win Rate: {eval_data.get('live_win_rate', 0):.1f}%\n"
                                msg += f"• Backtest Win Rate: {eval_data.get('backtest_win_rate', 0):.1f}%\n"
                                msg += f"• Status: {'✅ Beating backtest' if eval_data.get('beating_backtest') else '⚠️ Underperforming'}\n\n"
                            await self.send_message(msg[:4000])  # Truncate if too long

                # Launch new experiments (every 2 hours)
                if iteration % 120 == 0:
                    print("🧪 Launching new experiment...")
                    if hasattr(self.strategy_manager, 'launch_new_experiment'):
                        try:
                            await self.strategy_manager.launch_new_experiment()
                            await self.send_message("🚀 *New Strategy Experiment Launched!*\nBacktesting in progress...")
                        except Exception as e:
                            print(f"Error launching experiment: {e}")

                # Generate AI hypothesis every hour
                if (now - self.last_hypothesis).total_seconds() > 3600:
                    await self.generate_ai_hypothesis(market_data)
                    self.last_hypothesis = now

                # Send heartbeat every 6 hours
                if (now - self.last_heartbeat).total_seconds() > 21600:
                    await self.send_enhanced_heartbeat()
                    self.last_heartbeat = now

                # Send hourly status update
                if (now - self.last_hourly_report).total_seconds() > 3600:
                    await self.send_enhanced_hourly_report()
                    self.last_hourly_report = now

                # Quick console status every 5 minutes
                if iteration % 5 == 0:
                    strategies_count = len(self.strategy_manager.strategies) if hasattr(self.strategy_manager, 'strategies') else 0
                    sentiment_label = self.latest_sentiment['sentiment_label'] if self.latest_sentiment else 'Unknown'
                    print(f"🔄 [{datetime.now().strftime('%H:%M')}] Iteration {iteration}: {strategies_count} strategies | Sentiment: {sentiment_label}")

                # Sleep for a minute
                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"Error in enhanced AI loop: {e}")
                await self.send_message(f"⚠️ AI loop error: {str(e)[:100]}\n_Auto-recovering..._")
                await asyncio.sleep(60)

    async def send_enhanced_heartbeat(self):
        """Send enhanced heartbeat with AI status"""
        uptime = datetime.now(timezone.utc) - self.startup_time
        hours = int(uptime.total_seconds() / 3600)

        strategies = list(self.strategy_manager.strategies.values()) if hasattr(self.strategy_manager, 'strategies') else []

        msg = "💓 *Enhanced AI Lab Heartbeat*\n\n"
        msg += f"✅ System running smoothly\n"
        msg += f"⏱ Uptime: {hours} hours\n"
        msg += f"📊 Active strategies: {len(strategies)}\n"
        msg += f"📨 Notifications sent: {self.notifications_sent}\n"
        msg += f"🤖 LLM API calls today: ~{self.notifications_sent * 2}\n"
        msg += f"📰 News articles analyzed: {len(self.latest_news)}\n"

        # Add AI status
        if self.latest_sentiment:
            msg += f"\n*AI Status:*\n"
            msg += f"• Market Sentiment: {self.latest_sentiment['sentiment_label']}\n"
            msg += f"• Trading Bias: {self.latest_sentiment['trading_bias']}\n"

        await self.send_message(msg)

    async def send_enhanced_hourly_report(self):
        """Send enhanced hourly report with AI insights"""
        now = datetime.now(timezone.utc)
        strategies = list(self.strategy_manager.strategies.values()) if hasattr(self.strategy_manager, 'strategies') else []

        # Get current market data to check quality
        market_data = await self._get_market_data_async()

        if strategies:
            total_pnl = sum(s.metrics.total_pnl for s in strategies if hasattr(s, 'metrics'))
            avg_confidence = sum(s.confidence_score for s in strategies if hasattr(s, 'confidence_score')) / max(len(strategies), 1)
            ready = sum(1 for s in strategies if hasattr(s, 'should_go_live') and s.should_go_live())
        else:
            total_pnl = 0
            avg_confidence = 0
            ready = 0

        insights = self.learning_engine.get_market_insights()

        msg = f"📊 *Enhanced Hourly Report - {now.strftime('%H:%M UTC')}*\n\n"

        # Add data source indicator
        if market_data.get('is_real_data', True):
            data_quality = market_data.get('data_quality', {})
            quality_score = data_quality.get('score', 100)
            quality_emoji = "🟢" if quality_score >= 80 else "🟡" if quality_score >= 50 else "🔴"
            msg += f"*Data Source:* {quality_emoji} Real Market Data (Quality: {quality_score}%)\n"
            msg += f"*BTC Price:* ${market_data.get('price', 0):,.2f}\n\n"
        else:
            msg += f"*Data Source:* ⚠️ SIMULATED DATA - DO NOT TRADE\n\n"

        msg += f"*Performance:*\n"
        msg += f"• Strategies: {len(strategies)}\n"
        msg += f"• Ready for Live: {ready}\n"
        msg += f"• Avg Confidence: {avg_confidence:.1f}%\n"

        # Add REAL paper trading performance
        if self.paper_trader:
            metrics = self.paper_trader.get_performance_metrics()
            msg += f"\n*Paper Trading (REAL):*\n"
            msg += f"• Balance: ${metrics['current_balance']:.2f}\n"
            msg += f"• P&L: ${metrics['total_pnl']:+.2f} ({metrics['roi']:+.1f}%)\n"
            msg += f"• Win Rate: {metrics['win_rate']:.1f}%\n"
            msg += f"• Trades: {metrics['winning_trades']}W/{metrics['losing_trades']}L\n"
            msg += f"• Fees Paid: ${metrics['total_fees_paid']:.2f}\n"
            if metrics['open_positions'] > 0:
                msg += f"• Open Positions: {metrics['open_positions']}\n"
        else:
            msg += f"• Combined P&L: ${total_pnl:.2f}\n"

        msg += "\n"

        # Add backtest statistics if available
        if hasattr(self.strategy_manager, 'backtest_results') and self.strategy_manager.backtest_results:
            bt_stats = self.strategy_manager.backtest_results
            avg_bt_win = sum(bt.get('win_rate', 0) for bt in bt_stats.values()) / max(len(bt_stats), 1)
            msg += f"*Backtest vs Live:*\n"
            msg += f"• Strategies Backtested: {len(bt_stats)}\n"
            msg += f"• Avg Backtest Win Rate: {avg_bt_win:.1f}%\n"

            # Count how many are beating their backtest
            beating = 0
            for sid, strategy in self.strategy_manager.strategies.items():
                if sid in bt_stats and hasattr(strategy, 'metrics'):
                    if strategy.metrics.win_rate > bt_stats[sid].get('win_rate', 0):
                        beating += 1

            if len(bt_stats) > 0:
                msg += f"• Beating Backtest: {beating}/{len(bt_stats)}\n\n"

        msg += f"*AI Learning:*\n"
        msg += f"• Patterns Found: {insights['patterns_learned']}\n"
        msg += f"• Market State: {insights.get('current_market_state', 'analyzing')}\n"

        # Add quick AI summary
        if self.latest_sentiment:
            msg += f"\n*AI Summary:*\n"
            msg += f"• Sentiment: {self.latest_sentiment['sentiment_label']}\n"
            msg += f"• News Impact: {'High' if len(self.latest_news) > 10 else 'Normal'}\n"

        msg += f"\n_Enhanced with Gemini 2.5 Flash + Backtesting ✨_"

        await self.send_message(msg)


async def main():
    """Main entry point for enhanced AI Trading Lab"""
    print("=" * 50)
    print("🚀 ENHANCED AI TRADING LAB")
    print("   Powered by Gemini 2.5 Flash")
    print("=" * 50)
    print()
    print("Features:")
    print("• Real-time news sentiment analysis")
    print("• On-chain data monitoring")
    print("• LLM-powered hypothesis generation")
    print("• Google Search market intelligence")
    print("• Multi-source sentiment aggregation")
    print("• Continuous market analysis")
    print("• Automated strategy discovery")
    print()
    print("-" * 50)

    try:
        # Create and initialize enhanced lab
        lab = EnhancedAITradingLab()

        # Load initial strategies
        await lab.initialize_strategies()

        # Run enhanced main loop
        await lab.run_enhanced_ai_loop()

    except KeyboardInterrupt:
        print("\n\n🛑 Enhanced AI Trading Lab stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())