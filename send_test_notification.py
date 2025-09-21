#!/usr/bin/env python3
"""
Send test notification to confirm Telegram is working
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

load_dotenv()

async def send_test():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Missing Telegram credentials")
        return

    bot = Bot(token=token)

    msg = f"""✅ *AI Trading Lab Fixed!*

The 'currentmarketstate' error has been resolved.

*What was fixed:*
• Added price_history to market data
• Added volume_history to market data
• Learning engine now has proper data

*Status:*
• VPS updated with fix
• Auto-restart will apply changes
• Should receive hourly reports normally

_Time: {datetime.now().strftime('%H:%M UTC')}_"""

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode='Markdown'
        )
        print("✅ Test notification sent!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_test())