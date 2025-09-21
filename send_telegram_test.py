#!/usr/bin/env python3
"""
Simple test to send a Telegram message
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def send_test():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")
        return

    bot = Bot(token=token)

    try:
        await bot.send_message(
            chat_id=chat_id,
            text="🚀 *AI Trading Lab Ready!*\n\nThe system is active and monitoring markets.\n\nYou'll receive notifications when:\n• Strategies meet approval thresholds\n• New discoveries are made\n• Action is required\n\nCurrent mode: Dry-run (Safe)",
            parse_mode='Markdown'
        )
        print("✅ Message sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(send_test())
    if success:
        print("AI Trading Lab notification sent to Telegram!")