#!/usr/bin/env python3
"""
Start AI Trading Lab with direct messaging (no polling)
Avoids Telegram conflicts by only sending messages
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Bot

# Import AI components
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator
from strategies.strategy_manager import StrategyManager
from strategies.funding_carry import FundingCarryStrategy

load_dotenv()


class AITradingLab:
    """AI Trading Lab - Direct messaging mode"""

    def __init__(self):
        """Initialize AI Trading Lab"""
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found")

        # Simple bot for sending messages only
        self.bot = Bot(token=self.token)

        # Initialize AI components
        print("🧠 Initializing AI components...")
        self.strategy_manager = StrategyManager(telegram_notifier=self)
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator()

        # User preferences
        self.auto_approve_threshold = 85
        self.max_risk_per_strategy = 1000

    async def send_message(self, text: str, important: bool = False):
        """Send message to Telegram"""
        try:
            if self.chat_id:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode='Markdown'
                )
                print(f"📱 Sent: {text[:50]}...")
        except Exception as e:
            print(f"Error sending message: {e}")

    async def initialize_strategies(self):
        """Initialize and load strategies"""
        # Add funding carry as base strategy
        funding_strategy = FundingCarryStrategy()
        self.strategy_manager.add_strategy(funding_strategy)
        print(f"✅ Loaded {funding_strategy.name}")

        # We'll start with just the funding carry strategy
        # Experimental strategies will be added via the AI loop
        print("📊 Starting with Funding Carry strategy")

    def _get_market_data(self):
        """Get simulated market data"""
        return {
            'timestamp': datetime.now(timezone.utc),
            'price': 65000 + (datetime.now().second * 10),  # Slight variation
            'volume': 1000000,
            'funding_rate': 0.0001,
            'sentiment': 'neutral'
        }

    async def send_startup_report(self):
        """Send initial status report"""
        # Get strategies from the internal dict
        strategies = list(self.strategy_manager.strategies.values())
        stats = self.hypothesis_generator.get_statistics()

        msg = "🚀 *AI Trading Lab Started!*\n\n"
        msg += "*System Status:*\n"
        msg += "• 🧠 Learning Engine: Online\n"
        msg += "• 🔬 Pattern Recognition: Active\n"
        msg += "• 📊 Strategy Testing: Running\n\n"

        msg += f"*Active Strategies:* {len(strategies)}\n"
        msg += f"*Hypotheses in Pipeline:* {stats['total_generated']}\n"
        msg += f"*Success Rate:* {stats['success_rate']:.1f}%\n\n"

        msg += "*Currently Testing:*\n"
        for strategy in strategies[:3]:
            status = strategy.get_status()
            msg += f"• {status['name']}\n"

        msg += "\n_I'll notify you when strategies are ready for live trading._"

        await self.send_message(msg, important=True)

    async def run_ai_loop(self):
        """Main AI loop"""
        print("🤖 Starting AI Trading Lab main loop...")

        # Send startup message
        await self.send_startup_report()

        # Track last report times
        last_hourly_report = datetime.now()
        last_hypothesis = datetime.now()
        last_crazy_idea = datetime.now()

        iteration = 0
        while True:
            try:
                iteration += 1
                now = datetime.now()

                # Get market data
                market_data = self._get_market_data()

                # AI analysis
                analysis = self.learning_engine.analyze_market(market_data)

                # Update all strategies
                await self.strategy_manager.run_all_strategies(market_data)

                # Check for strategies ready for live
                for strategy in self.strategy_manager.strategies.values():
                    if strategy.should_go_live() and not strategy.is_live:
                        confidence = strategy.confidence_score

                        if confidence >= self.auto_approve_threshold:
                            # Auto-approve high confidence
                            self.strategy_manager.approve_strategy_for_live(strategy.id)
                            await self.send_message(
                                f"🚀 *AUTO-APPROVED FOR LIVE!*\n\n"
                                f"Strategy: {strategy.name}\n"
                                f"Confidence: {confidence:.1f}%\n"
                                f"Win Rate: {strategy.metrics.win_rate:.1f}%\n\n"
                                f"Live trading has begun! 💰",
                                important=True
                            )
                        else:
                            # Notify for manual approval
                            await self.send_message(
                                f"✅ *Strategy Ready for Live!*\n\n"
                                f"Strategy: {strategy.name}\n"
                                f"Confidence: {confidence:.1f}%\n"
                                f"Win Rate: {strategy.metrics.win_rate:.1f}%\n"
                                f"P&L: ${strategy.metrics.total_pnl:.2f}\n\n"
                                f"_Ready for your approval_",
                                important=True
                            )

                # Generate new hypothesis every 30 minutes
                if (now - last_hypothesis).seconds > 1800:
                    hypothesis = self.hypothesis_generator.generate_hypothesis(market_data)
                    if hypothesis['confidence'] > 60:
                        # Just notify about the hypothesis for now
                        await self.send_message(
                            f"🔬 *New Hypothesis Generated*\n"
                            f"Name: {hypothesis['name']}\n"
                            f"Category: {hypothesis['category']}\n"
                            f"Confidence: {hypothesis['confidence']}%"
                        )
                    last_hypothesis = now

                # Generate crazy idea every 2 hours
                if (now - last_crazy_idea).seconds > 7200:
                    idea = self.hypothesis_generator.generate_crazy_idea()
                    await self.send_message(
                        f"🤪 *Crazy Idea Generated!*\n\n"
                        f"_{idea['name']}_\n"
                        f"{idea['description']}\n\n"
                        f"Confidence: {idea['confidence']}%"
                    )
                    last_crazy_idea = now

                # Send hourly status update
                if (now - last_hourly_report).seconds > 3600:
                    strategies = list(self.strategy_manager.strategies.values())
                    total_pnl = sum(s.metrics.total_pnl for s in strategies)
                    ready = sum(1 for s in strategies if s.should_go_live())

                    insights = self.learning_engine.get_market_insights()

                    await self.send_message(
                        f"📊 *Hourly AI Report*\n\n"
                        f"Strategies Active: {len(strategies)}\n"
                        f"Ready for Live: {ready}\n"
                        f"Combined P&L: ${total_pnl:.2f}\n"
                        f"Patterns Found: {insights['patterns_learned']}\n"
                        f"Market State: {insights['current_market_state']}"
                    )
                    last_hourly_report = now

                # Quick status every 10 iterations (10 minutes)
                if iteration % 10 == 0:
                    print(f"🔄 Iteration {iteration}: {len(self.strategy_manager.strategies)} strategies active")

                # Sleep for a minute
                await asyncio.sleep(60)

            except Exception as e:
                print(f"Error in AI loop: {e}")
                await self.send_message(f"⚠️ AI loop error: {str(e)[:100]}")
                await asyncio.sleep(60)


async def main():
    """Main entry point"""
    print("=" * 50)
    print("🚀 STARTING AI TRADING LAB")
    print("=" * 50)
    print()
    print("This bot will:")
    print("• Continuously analyze markets")
    print("• Test multiple strategies in parallel")
    print("• Learn from successes and failures")
    print("• Notify you via Telegram when action is needed")
    print()
    print("Mode: Message-only (no command polling)")
    print("This avoids conflicts with other bot instances")
    print()
    print("-" * 50)

    try:
        # Create and initialize lab
        lab = AITradingLab()

        # Load initial strategies
        await lab.initialize_strategies()

        # Run main loop
        await lab.run_ai_loop()

    except KeyboardInterrupt:
        print("\n\n🛑 AI Trading Lab stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())