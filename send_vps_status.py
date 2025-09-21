#!/usr/bin/env python3
"""
Send VPS deployment status to Telegram
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

load_dotenv()

async def send_status():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Missing Telegram credentials")
        return

    bot = Bot(token=token)

    msg = f"""⚠️ *VPS Deployment Update*

**Current Situation:**
• ✅ Code pushed to GitHub successfully
• ✅ VPS pulled latest code
• ⚠️ VPS missing Python dependencies (numpy, dotenv, telegram)
• 🔄 AI Trading Lab running LOCALLY on your computer

**What This Means:**
• You'll receive hourly updates from the LOCAL instance
• Your computer needs to stay on for now
• VPS is not ready yet (missing packages)

**Next Steps:**
1. I'll install all dependencies on VPS
2. Start AI Trading Lab on VPS
3. Stop local instance
4. Confirm VPS is sending notifications

**ETA:** 5-10 minutes to complete VPS setup

_The bot is working locally, so you'll still get your hourly update soon!_

_Time: {datetime.now().strftime('%H:%M UTC')}_"""

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode='Markdown'
        )
        print("✅ VPS status sent to Telegram!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_status())