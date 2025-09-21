#!/usr/bin/env python3
"""
Simple test to check Telegram connection
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def test_connection():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token:
        print("❌ No TELEGRAM_TOKEN found")
        return

    print(f"Testing with token: {token[:10]}...")

    try:
        bot = Bot(token=token)

        # Test getting bot info
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username}")

        # Try to send a message
        if chat_id:
            await bot.send_message(
                chat_id=chat_id,
                text="🤖 AI Trading Lab ready!\n\nUse /help to see available commands."
            )
            print(f"✅ Message sent to chat {chat_id}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n✅ Telegram connection working! The bot can connect.")
        print("The issue is likely that another bot instance is polling for updates.")
        print("\nTo fix:")
        print("1. Wait a few more minutes for the old connection to timeout")
        print("2. Or use a webhook instead of polling")
    else:
        print("\n❌ Could not connect to Telegram")