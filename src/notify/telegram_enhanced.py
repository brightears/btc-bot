import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
from src.utils.logger import get_logger
from src.utils.time import get_utc_now, format_duration

logger = get_logger()


class EnhancedTelegramNotifier:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.bot: Optional[Bot] = None
        self.app: Optional[Application] = None
        self.chat_id: Optional[str] = None
        self.state_file = Path("logs/state.json")
        self.metrics_file = Path("logs/metrics.json")

        if enabled:
            token = os.getenv('TELEGRAM_TOKEN')
            self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

            if token and self.chat_id:
                try:
                    self.bot = Bot(token=token)
                    self.app = Application.builder().token(token).build()
                    self._setup_handlers()
                    logger.info("Enhanced Telegram notifier initialized with commands")
                except Exception as e:
                    logger.warning(f"Failed to initialize Telegram bot: {e}")
                    self.bot = None
                    self.app = None
            else:
                logger.info("Telegram credentials not found, notifications disabled")
                self.bot = None
                self.app = None

    def _setup_handlers(self):
        """Set up command handlers"""
        if self.app:
            self.app.add_handler(CommandHandler("status", self.handle_status_command))
            self.app.add_handler(CommandHandler("metrics", self.handle_metrics_command))
            self.app.add_handler(CommandHandler("help", self.handle_help_command))
            self.app.add_handler(CommandHandler("pause", self.handle_pause_command))
            self.app.add_handler(CommandHandler("resume", self.handle_resume_command))

            # Start the bot in a background thread
            asyncio.create_task(self.app.initialize())
            asyncio.create_task(self.app.start())
            asyncio.create_task(self.app.updater.start_polling())

    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """Send a message to Telegram"""
        if not self.bot or not self.chat_id or not self.enabled:
            return False

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_async(message, parse_mode))
            loop.close()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def _send_async(self, message: str, parse_mode: str):
        """Async send message"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")

    async def handle_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Load current state
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {}

            # Check if bot is running
            mode = "DRY-RUN" if state.get('dry_run', True) else "LIVE"

            if state.get('position'):
                pos = state['position']
                entry_time = datetime.fromisoformat(pos['entry_time'])
                duration = format_duration((get_utc_now() - entry_time).total_seconds())

                status_msg = (
                    f"🤖 *Bot Status: ACTIVE*\n"
                    f"Mode: {mode}\n\n"
                    f"📊 *Current Position*\n"
                    f"Symbol: {pos.get('symbol', 'N/A')}\n"
                    f"Notional: ${pos.get('notional_usdt', 0):.2f}\n"
                    f"Entry: ${pos.get('spot_entry_price', 0):.2f} / ${pos.get('futures_entry_price', 0):.2f}\n"
                    f"Duration: {duration}\n"
                    f"Funding Collected: ${pos.get('funding_collected', 0):.4f}\n"
                    f"Current P&L: ${pos.get('realized_pnl', 0):.4f}"
                )
            else:
                status_msg = (
                    f"🤖 *Bot Status: MONITORING*\n"
                    f"Mode: {mode}\n\n"
                    f"📊 *No Active Position*\n"
                    f"Waiting for profitable opportunity..."
                )

            # Add last check time
            if 'timestamp' in state:
                last_check = datetime.fromisoformat(state['timestamp'])
                time_ago = format_duration((get_utc_now() - last_check).total_seconds())
                status_msg += f"\n\n⏰ Last Update: {time_ago} ago"

            await update.message.reply_text(status_msg, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error handling /status command: {e}")
            await update.message.reply_text("❌ Error retrieving status")

    async def handle_metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /metrics command - show performance metrics"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = self._initialize_metrics()

            metrics_msg = (
                f"📈 *Performance Metrics*\n\n"
                f"*Session Stats*\n"
                f"Total Trades: {metrics.get('total_trades', 0)}\n"
                f"Winning Trades: {metrics.get('winning_trades', 0)}\n"
                f"Total P&L: ${metrics.get('total_pnl', 0):.4f}\n"
                f"Win Rate: {metrics.get('win_rate', 0):.1f}%\n\n"
                f"*Funding Stats*\n"
                f"Total Collected: ${metrics.get('total_funding', 0):.4f}\n"
                f"Avg Funding/Trade: ${metrics.get('avg_funding', 0):.4f}\n"
                f"Best Trade: ${metrics.get('best_trade', 0):.4f}\n"
                f"Worst Trade: ${metrics.get('worst_trade', 0):.4f}"
            )

            await update.message.reply_text(metrics_msg, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error handling /metrics command: {e}")
            await update.message.reply_text("❌ Error retrieving metrics")

    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = (
            "🤖 *BTC Funding Bot Commands*\n\n"
            "/status - Current bot status and position\n"
            "/metrics - Performance metrics\n"
            "/pause - Pause bot (stop opening new positions)\n"
            "/resume - Resume bot operations\n"
            "/help - Show this help message\n\n"
            "The bot monitors BTC funding rates and opens\n"
            "delta-neutral positions when profitable.\n\n"
            "Current threshold: 0.5 bps"
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def handle_pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command - creates a pause flag"""
        try:
            pause_file = Path("logs/paused")
            pause_file.touch()
            await update.message.reply_text(
                "⏸️ Bot PAUSED\n"
                "Will not open new positions.\n"
                "Use /resume to continue.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error handling /pause command: {e}")
            await update.message.reply_text("❌ Error pausing bot")

    async def handle_resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command - removes pause flag"""
        try:
            pause_file = Path("logs/paused")
            if pause_file.exists():
                pause_file.unlink()
                await update.message.reply_text(
                    "▶️ Bot RESUMED\n"
                    "Will monitor for opportunities.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("Bot was not paused.", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error handling /resume command: {e}")
            await update.message.reply_text("❌ Error resuming bot")

    def _initialize_metrics(self) -> Dict[str, Any]:
        """Initialize empty metrics"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'total_funding': 0.0,
            'avg_funding': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'win_rate': 0.0,
            'start_time': get_utc_now().isoformat()
        }

    def update_metrics(self, trade_pnl: float, funding_collected: float):
        """Update performance metrics after a trade"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = self._initialize_metrics()

            # Update metrics
            metrics['total_trades'] += 1
            metrics['total_pnl'] += trade_pnl
            metrics['total_funding'] += funding_collected

            if trade_pnl > 0:
                metrics['winning_trades'] += 1

            if trade_pnl > metrics['best_trade']:
                metrics['best_trade'] = trade_pnl

            if trade_pnl < metrics['worst_trade']:
                metrics['worst_trade'] = trade_pnl

            # Calculate averages
            if metrics['total_trades'] > 0:
                metrics['avg_funding'] = metrics['total_funding'] / metrics['total_trades']
                metrics['win_rate'] = (metrics['winning_trades'] / metrics['total_trades']) * 100

            # Save updated metrics
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    def send_daily_summary(self):
        """Send daily performance summary"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)

                summary = (
                    "📊 *Daily Summary*\n\n"
                    f"Trades Today: {metrics.get('total_trades', 0)}\n"
                    f"Total P&L: ${metrics.get('total_pnl', 0):.4f}\n"
                    f"Win Rate: {metrics.get('win_rate', 0):.1f}%\n"
                    f"Funding Collected: ${metrics.get('total_funding', 0):.4f}\n\n"
                    "Keep monitoring! 📈"
                )

                self.send_message(summary)

        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    async def shutdown(self):
        """Shutdown the bot properly"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()