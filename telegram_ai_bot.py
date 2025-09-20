#!/usr/bin/env python3
"""
AI-Enhanced Telegram Bot for Trading Lab
Provides control and monitoring of AI trading strategies
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from strategies.strategy_manager import StrategyManager
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator

load_dotenv()


class AITelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.token:
            print("❌ No TELEGRAM_TOKEN found in .env")
            exit(1)

        # Initialize AI components
        self.strategy_manager = StrategyManager(telegram_notifier=self)
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator()

    def send_message(self, message: str, parse_mode: str = 'Markdown'):
        """Send a message to Telegram (called by strategy manager)"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_async(message, parse_mode))
            loop.close()
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    async def _send_async(self, message: str, parse_mode: str):
        """Async send message"""
        from telegram import Bot
        bot = Bot(token=self.token)
        await bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )

    async def strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategies command - list all running strategies"""
        strategies = self.strategy_manager.strategies

        if not strategies:
            msg = "📊 *No Active Strategies*\n\nUse /launch to start a new experiment!"
        else:
            msg = "📊 *Active Strategies*\n\n"

            for strategy_id, strategy in strategies.items():
                status = strategy.get_status()
                emoji = "🟢" if strategy.is_live else "🔵"
                trend = "📈" if status['metrics']['total_pnl'] > 0 else "📉"

                msg += (
                    f"{emoji} *{strategy.name}*\n"
                    f"ID: `{strategy_id}`\n"
                    f"Status: {'LIVE' if strategy.is_live else 'TESTING'}\n"
                    f"Confidence: {status['confidence_score']:.1f}%\n"
                    f"Win Rate: {status['metrics']['win_rate']:.1f}%\n"
                    f"P&L: ${status['metrics']['total_pnl']:.2f} {trend}\n\n"
                )

            # Add summary
            total_pnl = sum(s.metrics.total_pnl for s in strategies.values())
            live_count = sum(1 for s in strategies.values() if s.is_live)

            msg += (
                f"*Summary*\n"
                f"Total Strategies: {len(strategies)}\n"
                f"Live Strategies: {live_count}\n"
                f"Total P&L: ${total_pnl:.2f}"
            )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def ai_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ai_report command - comprehensive AI analysis"""
        report = self.strategy_manager.get_ai_report()

        msg = "🤖 *AI Trading Lab Report*\n\n"

        # Active strategies summary
        msg += f"*Active Experiments*: {report['active_strategies']}\n"
        msg += f"*Live Strategies*: {report['live_strategies']}\n"
        msg += f"*Ready for Live*: {report['ready_for_live']}\n\n"

        # Top strategies
        if report['top_strategies']:
            msg += "*Top Performers*\n"
            for i, strategy in enumerate(report['top_strategies'][:3], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                msg += (
                    f"{emoji} {strategy['name']}\n"
                    f"   Win: {strategy['win_rate']:.1f}% | P&L: ${strategy['total_pnl']:.2f}\n"
                )
            msg += "\n"

        # Market insights
        insights = report['market_insights']
        msg += "*Market Insights*\n"
        msg += f"Edges Discovered: {insights['discovered_edges']}\n"
        msg += f"Patterns Learned: {insights['patterns_learned']}\n"

        if insights['recent_discoveries']:
            msg += "\n*Recent Discoveries*\n"
            for discovery in insights['recent_discoveries'][-2:]:
                msg += f"• {discovery.get('description', 'Unknown')}\n"

        # Hypothesis stats
        hyp_stats = report['hypothesis_statistics']
        msg += f"\n*Hypothesis Testing*\n"
        msg += f"Total Generated: {hyp_stats['total_generated']}\n"
        msg += f"Currently Testing: {hyp_stats['currently_testing']}\n"
        msg += f"Success Rate: {hyp_stats['success_rate']:.1f}%\n"

        # AI recommendations
        if report['recommendations']:
            msg += "\n*AI Recommendations*\n"
            for rec in report['recommendations']:
                msg += f"• {rec}\n"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def experiments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /experiments command - list experimental strategies"""
        experiments = [
            (sid, s) for sid, s in self.strategy_manager.strategies.items()
            if 'exp_' in sid or 'experimental' in s.name.lower()
        ]

        if not experiments:
            msg = "🧪 *No Active Experiments*\n\nUse /launch to start a new experiment!"
        else:
            msg = "🧪 *Active Experiments*\n\n"

            for strategy_id, strategy in experiments:
                status = strategy.get_status()

                msg += (
                    f"*{strategy.name}*\n"
                    f"ID: `{strategy_id}`\n"
                    f"Confidence: {status['confidence_score']:.1f}%\n"
                    f"Trades: {status['metrics']['total_trades']}\n"
                    f"Win Rate: {status['metrics']['win_rate']:.1f}%\n"
                    f"P&L: ${status['metrics']['total_pnl']:.2f}\n\n"
                )

        # Add hypothesis statistics
        hyp_stats = self.hypothesis_generator.get_statistics()
        msg += (
            f"\n*Hypothesis Pipeline*\n"
            f"Pending Tests: {hyp_stats['pending']}\n"
            f"Currently Testing: {hyp_stats['currently_testing']}\n"
            f"Successful: {hyp_stats['successful']}\n"
            f"Failed: {hyp_stats['failed']}"
        )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def crazy_idea_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /crazy_idea command - generate wild strategy"""
        crazy_idea = self.strategy_manager.generate_crazy_idea()

        # Message is sent automatically by strategy_manager
        await update.message.reply_text(
            "🎲 Generating crazy idea... Check the message above!",
            parse_mode='Markdown'
        )

    async def launch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /launch command - start new experiment"""
        hypothesis = self.strategy_manager.launch_new_experiment()

        if hypothesis:
            msg = (
                "🚀 *New Experiment Launched!*\n\n"
                f"Testing will begin immediately.\n"
                f"Use /experiments to monitor progress."
            )
        else:
            msg = "⚠️ No new hypotheses available. Generating new ideas..."
            # Generate a new hypothesis
            self.hypothesis_generator.generate_hypothesis()
            hypothesis = self.strategy_manager.launch_new_experiment()
            if hypothesis:
                msg = "✅ Generated and launched new hypothesis!"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve <strategy_id> command"""
        if not context.args:
            await update.message.reply_text(
                "Usage: /approve <strategy_id>\nExample: /approve exp_abc123",
                parse_mode='Markdown'
            )
            return

        strategy_id = context.args[0]

        if self.strategy_manager.approve_strategy_for_live(strategy_id):
            msg = f"✅ Strategy {strategy_id} approved for LIVE trading!"
        else:
            msg = f"❌ Could not approve {strategy_id}. Check if it meets criteria."

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject <strategy_id> command"""
        if not context.args:
            await update.message.reply_text(
                "Usage: /reject <strategy_id>\nExample: /reject exp_abc123",
                parse_mode='Markdown'
            )
            return

        strategy_id = context.args[0]
        self.strategy_manager.reject_strategy(strategy_id)

        msg = f"👎 Strategy {strategy_id} rejected. Will continue paper trading."
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def confidence_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /confidence command - show AI confidence in strategies"""
        strategies = self.strategy_manager.strategies

        if not strategies:
            msg = "No strategies to evaluate."
        else:
            msg = "🎯 *AI Confidence Levels*\n\n"

            # Sort by confidence
            sorted_strategies = sorted(
                strategies.items(),
                key=lambda x: x[1].confidence_score,
                reverse=True
            )

            for strategy_id, strategy in sorted_strategies:
                status = strategy.get_status()
                bar_length = int(status['confidence_score'] / 10)
                bar = '█' * bar_length + '░' * (10 - bar_length)

                msg += (
                    f"*{strategy.name}*\n"
                    f"{bar} {status['confidence_score']:.1f}%\n"
                )

                if status['ready_for_live']:
                    msg += "✅ Ready for live!\n"
                else:
                    reasons = []
                    if status['confidence_score'] < strategy.min_confidence_for_live:
                        reasons.append(f"Need {strategy.min_confidence_for_live:.0f}% confidence")
                    if status['metrics']['total_trades'] < 50:
                        reasons.append(f"Need {50 - status['metrics']['total_trades']} more trades")
                    if status['metrics']['win_rate'] < 55:
                        reasons.append(f"Need {55 - status['metrics']['win_rate']:.1f}% higher win rate")

                    if reasons:
                        msg += f"📋 Requirements: {', '.join(reasons)}\n"

                msg += "\n"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /learn <insight> command - teach AI a pattern"""
        if not context.args:
            await update.message.reply_text(
                "Usage: /learn <insight>\nExample: /learn Funding spikes on Fridays before expiry",
                parse_mode='Markdown'
            )
            return

        insight = ' '.join(context.args)

        # Add to discovered edges
        self.learning_engine.insights['discovered_edges'].append({
            'description': insight,
            'discovered_at': datetime.now(timezone.utc).isoformat(),
            'source': 'human_input'
        })
        self.learning_engine.save_insights()

        msg = (
            f"🧠 *Learned New Pattern*\n\n"
            f"Pattern: {insight}\n\n"
            f"I'll incorporate this into future strategy generation and testing."
        )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def research_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /research <topic> command"""
        if not context.args:
            topics = [
                "volatility patterns", "funding anomalies", "whale behavior",
                "sentiment extremes", "correlation breaks", "liquidity cycles"
            ]
            msg = (
                f"*Research Topics*\n\n"
                f"Usage: /research <topic>\n\n"
                f"Suggested topics:\n" +
                '\n'.join(f"• {t}" for t in topics)
            )
        else:
            topic = ' '.join(context.args)
            msg = (
                f"🔬 *Researching: {topic}*\n\n"
                f"Generating hypotheses based on {topic}...\n"
            )

            # Generate hypothesis based on topic
            hypothesis = self.hypothesis_generator.generate_hypothesis({'research_topic': topic})

            msg += (
                f"\n*Generated Hypothesis*\n"
                f"Name: {hypothesis['name']}\n"
                f"Description: {hypothesis['description']}\n\n"
                f"Use /launch to test this hypothesis."
            )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        msg = (
            "🤖 *AI Trading Lab Commands*\n\n"
            "*Monitoring*\n"
            "/strategies - List all active strategies\n"
            "/ai_report - Comprehensive AI analysis\n"
            "/experiments - Show running experiments\n"
            "/confidence - AI confidence levels\n\n"
            "*Control*\n"
            "/approve <id> - Approve strategy for live\n"
            "/reject <id> - Reject and continue testing\n"
            "/launch - Start new experiment\n"
            "/crazy_idea - Generate wild strategy\n\n"
            "*Learning*\n"
            "/learn <insight> - Teach AI a pattern\n"
            "/research <topic> - Research new strategies\n\n"
            "*Original Commands*\n"
            "/status - Current bot status\n"
            "/metrics - Performance metrics\n"
            "/pause - Pause operations\n"
            "/resume - Resume operations\n"
            "/help - Show this message"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - overall system status"""
        strategies_count = len(self.strategy_manager.strategies)
        live_count = sum(1 for s in self.strategy_manager.strategies.values() if s.is_live)
        total_pnl = sum(s.metrics.total_pnl for s in self.strategy_manager.strategies.values())

        insights = self.learning_engine.get_market_insights()

        msg = (
            f"🤖 *AI Trading Lab Status*\n\n"
            f"*System Overview*\n"
            f"Active Strategies: {strategies_count}\n"
            f"Live Trading: {live_count}\n"
            f"Total P&L: ${total_pnl:.2f}\n\n"
            f"*Learning Progress*\n"
            f"Patterns Learned: {insights['patterns_learned']}\n"
            f"Edges Discovered: {insights['discovered_edges']}\n"
            f"Success Rate: {self.hypothesis_generator.get_statistics()['success_rate']:.1f}%\n\n"
            f"*Current Mode*: {'LIVE' if live_count > 0 else 'PAPER TRADING'}\n"
        )

        await update.message.reply_text(msg, parse_mode='Markdown')

    def run(self):
        """Run the Telegram bot"""
        print("🤖 Starting AI Trading Lab Telegram Bot...")
        print("Commands available: /strategies /ai_report /experiments /crazy_idea /launch /approve /reject /confidence /learn /research")

        # Create application
        app = Application.builder().token(self.token).build()

        # Add command handlers
        app.add_handler(CommandHandler("strategies", self.strategies_command))
        app.add_handler(CommandHandler("ai_report", self.ai_report_command))
        app.add_handler(CommandHandler("experiments", self.experiments_command))
        app.add_handler(CommandHandler("crazy_idea", self.crazy_idea_command))
        app.add_handler(CommandHandler("launch", self.launch_command))
        app.add_handler(CommandHandler("approve", self.approve_command))
        app.add_handler(CommandHandler("reject", self.reject_command))
        app.add_handler(CommandHandler("confidence", self.confidence_command))
        app.add_handler(CommandHandler("learn", self.learn_command))
        app.add_handler(CommandHandler("research", self.research_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("help", self.help_command))

        # Start strategy manager in background
        import threading
        manager_thread = threading.Thread(target=self.strategy_manager.start, daemon=True)
        manager_thread.start()

        # Run the bot
        print("✅ AI Trading Lab is running. Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = AITelegramBot()
    bot.run()