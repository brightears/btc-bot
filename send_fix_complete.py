#!/usr/bin/env python3
"""
Send notification about complete fix
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

load_dotenv()

async def send_notification():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Missing Telegram credentials")
        return

    bot = Bot(token=token)

    msg = f"""🎉 *All Errors Fixed!*

The AI Trading Lab is now running smoothly on VPS.

*Fixed Issues:*
✅ Added price/volume history to market data
✅ Fixed current market state KeyError
✅ Fixed record trade AttributeError

*Current Status:*
• VPS updated with all fixes
• Process restarted automatically
• Monitor script active (auto-restart)
• No more error messages expected

*What to Expect:*
• Clean hourly reports (top of each hour)
• 6-hour heartbeats
• Strategy notifications when ready
• No error messages

The AI Trading Lab is learning and testing strategies 24/7! 🚀

Time: {datetime.now().strftime('%H:%M UTC')}"""

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode='Markdown'
        )
        print("✅ Fix complete notification sent!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_notification())