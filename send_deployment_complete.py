#!/usr/bin/env python3
"""
Send deployment completion status to Telegram
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

    msg = f"""✅ *VPS Deployment Complete!*

**Status:**
• 🚀 AI Trading Lab running on VPS (PID: 99292)
• ✅ All code pushed to GitHub
• ✅ Local instances stopped
• ✅ Monitoring script deployed
• 🔄 Auto-restart enabled

**You can now safely turn off your computer!** 💻

**The VPS will:**
• Send hourly status reports
• Send 6-hour heartbeat confirmations
• Alert when strategies need approval
• Auto-restart if the bot crashes

**Management from anywhere:**
• SSH to VPS: `ssh root@5.223.55.219`
• Check status: `python get_status.py`
• View logs: `tail -f ai_lab.log`
• Stop bot: `pkill -f ai_trading_lab`

**Next notifications:**
• Hourly report: ~11:57 UTC
• Heartbeat: ~15:57 UTC

The AI Trading Lab is now running 24/7 on your VPS! 🎉

_Time: {datetime.now().strftime('%H:%M UTC')}_"""

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode='Markdown'
        )
        print("✅ Deployment complete message sent!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_status())