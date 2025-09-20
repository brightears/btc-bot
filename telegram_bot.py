#!/usr/bin/env python3
"""
Standalone Telegram Bot for monitoring and controlling the funding bot
Run this alongside the main bot to enable commands
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()


class TelegramBotHandler:
    def __init__(self):
        self.state_file = Path("logs/state.json")
        self.metrics_file = Path("logs/metrics.json")
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.token:
            print("❌ No TELEGRAM_TOKEN found in .env")
            exit(1)

    def load_state(self):
        """Load bot state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def load_metrics(self):
        """Load metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return self._default_metrics()

    def _default_metrics(self):
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'total_funding': 0.0,
            'avg_funding': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'win_rate': 0.0
        }

    def format_duration(self, seconds):
        """Format duration"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        state = self.load_state()
        mode = "🔴 LIVE" if not state.get('dry_run', True) else "🟢 DRY-RUN"

        if state.get('position'):
            pos = state['position']
            msg = (
                f"🤖 *Bot Status*\n"
                f"Mode: {mode}\n\n"
                f"📊 *Active Position*\n"
                f"Symbol: {pos.get('symbol', 'N/A')}\n"
                f"Notional: ${pos.get('notional_usdt', 0):.2f}\n"
                f"Entry Spot: ${pos.get('spot_entry_price', 0):.2f}\n"
                f"Entry Futures: ${pos.get('futures_entry_price', 0):.2f}\n"
                f"Funding Collected: ${pos.get('funding_collected', 0):.4f}\n"
                f"P&L: ${pos.get('realized_pnl', 0):.4f}"
            )
        else:
            msg = (
                f"🤖 *Bot Status*\n"
                f"Mode: {mode}\n\n"
                f"📊 *No Active Position*\n"
                f"Monitoring for opportunities..."
            )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /metrics command"""
        metrics = self.load_metrics()

        msg = (
            f"📈 *Performance Metrics*\n\n"
            f"Total Trades: {metrics['total_trades']}\n"
            f"Winning Trades: {metrics['winning_trades']}\n"
            f"Win Rate: {metrics['win_rate']:.1f}%\n\n"
            f"💰 *P&L Summary*\n"
            f"Total P&L: ${metrics['total_pnl']:.4f}\n"
            f"Total Funding: ${metrics['total_funding']:.4f}\n"
            f"Avg Funding/Trade: ${metrics['avg_funding']:.4f}\n\n"
            f"📊 *Best/Worst*\n"
            f"Best Trade: ${metrics['best_trade']:.4f}\n"
            f"Worst Trade: ${metrics['worst_trade']:.4f}"
        )

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        msg = (
            "🤖 *BTC Funding Bot Commands*\n\n"
            "/status - Current position and bot status\n"
            "/metrics - Performance metrics\n"
            "/pause - Pause new position opening\n"
            "/resume - Resume operations\n"
            "/stop - Emergency stop (creates kill file)\n"
            "/help - Show this message\n\n"
            "Bot monitors BTC funding rates and\n"
            "opens delta-neutral positions when\n"
            "edge > threshold (0.5 bps)"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command"""
        pause_file = Path("logs/paused")
        pause_file.touch()
        msg = "⏸️ *Bot Paused*\nNo new positions will be opened.\nUse /resume to continue."
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        pause_file = Path("logs/paused")
        if pause_file.exists():
            pause_file.unlink()
            msg = "▶️ *Bot Resumed*\nMonitoring for opportunities..."
        else:
            msg = "Bot was not paused."
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command - emergency stop"""
        kill_file = Path(".kill")
        kill_file.touch()
        msg = (
            "🛑 *EMERGENCY STOP ACTIVATED*\n\n"
            "Bot will close any open positions and shut down.\n"
            "To restart, remove .kill file and restart bot."
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    def run(self):
        """Run the Telegram bot"""
        print("🤖 Starting Telegram Command Bot...")
        print(f"Commands: /status /metrics /pause /resume /stop /help")

        # Create application
        app = Application.builder().token(self.token).build()

        # Add command handlers
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("metrics", self.metrics_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("pause", self.pause_command))
        app.add_handler(CommandHandler("resume", self.resume_command))
        app.add_handler(CommandHandler("stop", self.stop_command))

        # Run the bot
        print("✅ Bot is running. Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TelegramBotHandler()
    bot.run()