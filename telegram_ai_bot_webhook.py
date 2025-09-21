#!/usr/bin/env python3
"""
AI Trading Lab - Telegram Bot with Webhook Mode
Uses webhook instead of polling to avoid conflicts
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request
import threading

# Import AI components
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator
from strategies.strategy_manager import StrategyManager
from strategies.funding_carry import FundingCarryStrategy

load_dotenv()

# Flask app for webhook
app = Flask(__name__)
bot_instance = None
application = None

class AITelegramBot:
    """Enhanced Telegram bot with AI capabilities"""

    def __init__(self):
        """Initialize bot with AI components"""
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found in environment")

        # Initialize AI components
        print("🧠 Initializing AI components...")
        self.strategy_manager = StrategyManager(telegram_notifier=self)
        self.learning_engine = LearningEngine()
        self.hypothesis_generator = HypothesisGenerator()

        # Load initial strategies
        self._load_initial_strategies()

        # Track user preferences
        self.user_preferences = {
            'notification_level': 'important',  # important, all, minimal
            'auto_approve_threshold': 85,
            'max_risk_per_strategy': 1000
        }

        # Simple bot for sending messages
        self.bot = Bot(token=self.token)

    def _load_initial_strategies(self):
        """Load initial strategies including funding carry"""
        # Add funding carry as base strategy
        funding_strategy = FundingCarryStrategy()
        self.strategy_manager.add_strategy(funding_strategy)
        print(f"✅ Loaded {funding_strategy.name}")

        # Load pending hypotheses
        hypotheses = self.hypothesis_generator.get_pending_hypotheses()
        for hypothesis in hypotheses[:3]:  # Start with top 3
            strategy = self.strategy_manager.create_experimental_strategy(hypothesis)
            if strategy:
                print(f"✅ Loaded experimental: {strategy.name}")

    async def send_message(self, text: str, important: bool = False):
        """Send message to Telegram"""
        try:
            if self.chat_id:
                # Filter based on importance
                if self.user_preferences['notification_level'] == 'minimal' and not important:
                    return

                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 *AI Trading Lab - Active!*

I'm your autonomous trading AI, continuously learning and evolving strategies.

*Current Capabilities:*
• 🧠 Learning from market patterns
• 🔬 Testing multiple strategies in parallel
• 🎯 Auto-discovery of profitable edges
• 🚀 Launching experimental strategies
• 📊 Real-time performance tracking

*Commands:*
/strategies - View all active strategies
/ai_report - Get comprehensive AI analysis
/launch - Start new strategy experiment
/crazy_idea - Generate wild strategy idea
/settings - Adjust preferences
/help - Show all commands

*Current Mode:* Dry Run (Safe)
*Learning Engine:* Online
*Pattern Recognition:* Active
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all active strategies with performance"""
        strategies = self.strategy_manager.get_all_strategies()

        if not strategies:
            await update.message.reply_text("No active strategies")
            return

        msg = "📊 *Active Strategies:*\n\n"

        for strategy in strategies:
            status = strategy.get_status()
            emoji = "🟢" if status['is_active'] else "🔴"
            ready_emoji = "✅" if status['ready_for_live'] else "🧪"

            msg += f"{emoji} *{status['name']}*\n"
            msg += f"  {ready_emoji} Confidence: {status['confidence_score']:.1f}%\n"

            if status['metrics']['total_trades'] > 0:
                msg += f"  📈 Win Rate: {status['metrics']['win_rate']:.1f}%\n"
                msg += f"  💰 Total P&L: ${status['metrics']['total_pnl']:.2f}\n"
                msg += f"  📊 Trades: {status['metrics']['total_trades']}\n"
            else:
                msg += f"  ⏳ Gathering data...\n"

            msg += f"  🎯 Patterns: {', '.join(status['patterns_learned'][:3]) if status['patterns_learned'] else 'Learning...'}\n\n"

        # Add summary
        total_pnl = sum(s.metrics.total_pnl for s in strategies)
        ready_count = sum(1 for s in strategies if s.should_go_live())

        msg += f"\n*Summary:*\n"
        msg += f"Total Strategies: {len(strategies)}\n"
        msg += f"Ready for Live: {ready_count}\n"
        msg += f"Combined P&L: ${total_pnl:.2f}"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def ai_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate comprehensive AI analysis report"""
        msg = "🧠 *AI Trading Lab Report*\n\n"

        # Learning insights
        insights = self.learning_engine.get_market_insights()
        msg += "*Machine Learning Insights:*\n"
        msg += f"• Patterns Identified: {insights['patterns_learned']}\n"
        msg += f"• Market Edges Found: {insights['discovered_edges']}\n"
        msg += f"• Current Market State: {insights['current_market_state']}\n\n"

        # Hypothesis statistics
        stats = self.hypothesis_generator.get_statistics()
        msg += "*Hypothesis Pipeline:*\n"
        msg += f"• Total Generated: {stats['total_generated']}\n"
        msg += f"• Currently Testing: {stats['currently_testing']}\n"
        msg += f"• Success Rate: {stats['success_rate']:.1f}%\n\n"

        # Top performing patterns
        msg += "*Top Performing Patterns:*\n"
        for pattern in insights['top_patterns'][:5]:
            msg += f"• {pattern['name']}: {pattern['win_rate']:.1f}% WR\n"

        # Optimization suggestions
        if insights['optimization_suggestions']:
            msg += "\n*AI Recommendations:*\n"
            for suggestion in insights['optimization_suggestions'][:3]:
                msg += f"• {suggestion}\n"

        # Next actions
        msg += "\n*Next AI Actions:*\n"
        msg += "• Continuing pattern analysis\n"
        msg += "• Testing 2 new hypotheses\n"
        msg += "• Optimizing existing strategies\n"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def launch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Launch a new experimental strategy"""
        # Generate and launch new hypothesis
        market_data = self._get_current_market_data()
        hypothesis = self.hypothesis_generator.generate_hypothesis(market_data)

        # Create strategy from hypothesis
        strategy = self.strategy_manager.create_experimental_strategy(hypothesis)

        if strategy:
            msg = f"🚀 *Launching New Experiment!*\n\n"
            msg += f"*Strategy:* {hypothesis['name']}\n"
            msg += f"*Category:* {hypothesis['category']}\n"
            msg += f"*Description:* {hypothesis['description']}\n"
            msg += f"*Initial Confidence:* {hypothesis['confidence']}%\n"
            msg += f"*Risk Limit:* ${hypothesis['risk_parameters']['max_position_size']:.2f}\n\n"
            msg += "The AI will now test this strategy and learn from its performance.\n"
            msg += "You'll be notified if it meets criteria for live trading."

            await update.message.reply_text(msg, parse_mode='Markdown')

            # Start testing
            self.strategy_manager.start_strategy(strategy.id)
        else:
            await update.message.reply_text("Failed to create strategy. Try again.")

    async def crazy_idea_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a crazy trading idea"""
        idea = self.hypothesis_generator.generate_crazy_idea()

        msg = f"🤪 *Crazy Strategy Idea!*\n\n"
        msg += f"*Name:* {idea['name']}\n"
        msg += f"*Description:* {idea['description']}\n"
        msg += f"*Source:* {idea['source']}\n"
        msg += f"*Risk Limit:* ${idea['risk_limit']}\n\n"
        msg += f"*AI Reasoning:* {idea['explanation']}\n\n"
        msg += "Reply /test_crazy to actually test this idea (at your own risk! 😅)"

        # Store for potential testing
        context.user_data['last_crazy_idea'] = idea

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def test_crazy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test the last crazy idea"""
        idea = context.user_data.get('last_crazy_idea')
        if not idea:
            await update.message.reply_text("No crazy idea to test. Use /crazy_idea first!")
            return

        # Convert crazy idea to testable hypothesis
        hypothesis = {
            'id': idea['id'],
            'name': idea['name'],
            'category': 'experimental_crazy',
            'pattern': 'ai_generated_wild',
            'description': idea['description'],
            'entry_conditions': [],
            'exit_conditions': [],
            'risk_parameters': {
                'max_position_size': idea['risk_limit'],
                'max_daily_trades': 3,
                'max_correlation': 0.9,
                'required_edge_bps': 50,
                'min_liquidity': 100000
            },
            'confidence': idea['confidence'],
            'created_at': idea['created_at'],
            'status': 'testing',
            'backtest_required': False  # YOLO mode
        }

        strategy = self.strategy_manager.create_experimental_strategy(hypothesis)
        if strategy:
            await update.message.reply_text(
                f"😈 *YOLO Mode Activated!*\n\n"
                f"Testing: {idea['name']}\n"
                f"May the odds be ever in your favor! 🎰",
                parse_mode='Markdown'
            )
            self.strategy_manager.start_strategy(strategy.id)
        else:
            await update.message.reply_text("Even the AI thinks this is too crazy! 😅")

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Approve a strategy for live trading"""
        if not context.args:
            await update.message.reply_text("Usage: /approve <strategy_id>")
            return

        strategy_id = context.args[0]
        success = self.strategy_manager.approve_strategy_for_live(strategy_id)

        if success:
            await update.message.reply_text(
                f"✅ Strategy approved for LIVE trading!\n"
                f"The AI will now execute real trades with this strategy.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Strategy not found or not ready for live trading.")

    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reject and stop a strategy"""
        if not context.args:
            await update.message.reply_text("Usage: /reject <strategy_id>")
            return

        strategy_id = context.args[0]
        self.strategy_manager.stop_strategy(strategy_id)

        # AI learns from rejection
        self.learning_engine.record_user_feedback(strategy_id, 'rejected')

        await update.message.reply_text(
            f"❌ Strategy rejected and stopped.\n"
            f"The AI will learn from this feedback.",
            parse_mode='Markdown'
        )

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Adjust user preferences"""
        msg = "⚙️ *Settings*\n\n"
        msg += f"*Notification Level:* {self.user_preferences['notification_level']}\n"
        msg += f"*Auto-Approve Threshold:* {self.user_preferences['auto_approve_threshold']}%\n"
        msg += f"*Max Risk Per Strategy:* ${self.user_preferences['max_risk_per_strategy']}\n\n"
        msg += "*Commands:*\n"
        msg += "/set_notifications <minimal|important|all>\n"
        msg += "/set_auto_approve <threshold>\n"
        msg += "/set_max_risk <amount>"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
🤖 *AI Trading Lab Commands*

*Strategy Management:*
/strategies - View all active strategies
/launch - Start new experiment
/approve <id> - Approve for live trading
/reject <id> - Stop and reject strategy

*AI Features:*
/ai_report - Comprehensive AI analysis
/crazy_idea - Generate wild strategy
/test_crazy - Test the crazy idea

*Settings:*
/settings - View current settings
/set_notifications - Adjust alerts
/help - This message

*How it Works:*
1. AI continuously analyzes markets
2. Generates and tests hypotheses
3. Learns from successes/failures
4. Notifies when strategies are ready
5. You approve for live trading

The AI is always learning and improving! 🧠
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    def _get_current_market_data(self):
        """Get current market data for analysis"""
        # This would connect to exchange in production
        return {
            'timestamp': datetime.now(timezone.utc),
            'price': 65000,
            'volume': 1000000,
            'funding_rate': 0.0001,
            'sentiment': 'neutral'
        }

    async def run_webhook(self):
        """Run bot with webhook instead of polling"""
        print("🤖 AI Trading Lab starting in webhook mode...")

        # Send startup message
        await self.send_message(
            "🤖 AI Trading Lab is now active in webhook mode!\n\n"
            "Use /help to see available commands.",
            important=True
        )

        # Start background tasks
        asyncio.create_task(self._run_ai_loop())

        print("✅ AI Trading Lab running in webhook mode!")

    async def _run_ai_loop(self):
        """Main AI loop for continuous learning and trading"""
        while True:
            try:
                # Get market data
                market_data = self._get_current_market_data()

                # AI analysis
                analysis = self.learning_engine.analyze_market(market_data)

                # Update all strategies
                await self.strategy_manager.update_all(market_data, analysis)

                # Check for strategies ready for live
                for strategy in self.strategy_manager.get_all_strategies():
                    if strategy.should_go_live() and not strategy.is_live:
                        confidence = strategy.confidence_score

                        if confidence >= self.user_preferences['auto_approve_threshold']:
                            # Auto-approve high confidence strategies
                            self.strategy_manager.approve_strategy_for_live(strategy.id)
                            await self.send_message(
                                f"🚀 *Auto-Approved for LIVE!*\n\n"
                                f"Strategy: {strategy.name}\n"
                                f"Confidence: {confidence:.1f}%\n"
                                f"The AI has started live trading!",
                                important=True
                            )
                        else:
                            # Request user approval
                            await self.send_message(
                                f"✅ *Strategy Ready for Live!*\n\n"
                                f"Strategy: {strategy.name}\n"
                                f"Confidence: {confidence:.1f}%\n"
                                f"Win Rate: {strategy.metrics.win_rate:.1f}%\n"
                                f"Total P&L: ${strategy.metrics.total_pnl:.2f}\n\n"
                                f"Use /approve {strategy.id[:8]} to go live",
                                important=True
                            )

                # Generate new hypotheses periodically
                if datetime.now().minute % 30 == 0:  # Every 30 minutes
                    hypothesis = self.hypothesis_generator.generate_hypothesis(market_data)
                    if hypothesis['confidence'] > 60:
                        strategy = self.strategy_manager.create_experimental_strategy(hypothesis)
                        if strategy:
                            await self.send_message(
                                f"🔬 New experiment started: {hypothesis['name']}"
                            )

                # Sleep for a minute
                await asyncio.sleep(60)

            except Exception as e:
                print(f"Error in AI loop: {e}")
                await asyncio.sleep(60)


# Global bot instance
global_bot = None

@app.route(f'/{os.getenv("TELEGRAM_TOKEN")}', methods=['POST'])
def webhook():
    """Handle incoming webhook updates"""
    global global_bot
    if global_bot:
        update = Update.de_json(request.get_json(), global_bot.bot)
        asyncio.run(application.process_update(update))
    return 'OK'


async def setup_webhook():
    """Setup webhook for Telegram"""
    global global_bot, application

    # Initialize bot
    global_bot = AITelegramBot()

    # Create application
    application = Application.builder().token(global_bot.token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", global_bot.start_command))
    application.add_handler(CommandHandler("strategies", global_bot.strategies_command))
    application.add_handler(CommandHandler("ai_report", global_bot.ai_report_command))
    application.add_handler(CommandHandler("launch", global_bot.launch_command))
    application.add_handler(CommandHandler("crazy_idea", global_bot.crazy_idea_command))
    application.add_handler(CommandHandler("test_crazy", global_bot.test_crazy_command))
    application.add_handler(CommandHandler("approve", global_bot.approve_command))
    application.add_handler(CommandHandler("reject", global_bot.reject_command))
    application.add_handler(CommandHandler("settings", global_bot.settings_command))
    application.add_handler(CommandHandler("help", global_bot.help_command))

    # Initialize application
    await application.initialize()

    # Start webhook mode
    await global_bot.run_webhook()

    return global_bot, application


def run_flask():
    """Run Flask server for webhook"""
    app.run(host='127.0.0.1', port=8080, debug=False)


if __name__ == "__main__":
    print("🚀 Starting AI Trading Lab with Webhook...")
    print("This avoids polling conflicts with other bot instances")

    # Start Flask in a thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Setup and run bot
    asyncio.run(setup_webhook())