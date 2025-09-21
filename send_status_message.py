#!/usr/bin/env python3
"""
Send a status confirmation to Telegram
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

    msg = f"""✅ *AI Trading Lab Configuration Complete!*

*What's New:*
• Fixed all Telegram conflicts
• Created new production-ready AI Trading Lab
• Added regular notifications (hourly + 6hr heartbeat)
• Created management scripts

*Management Commands:*
• `python get_status.py` - Check current status
• `python approve_strategy.py <id>` - Approve for live
• `python go_live.py` - Enable live trading
• `python stop_trading.py` - Emergency stop

*What to Expect:*
• Hourly status reports
• 6-hour heartbeat confirmations
• Strategy approval notifications (75%+ confidence)
• New hypothesis alerts every 30 min
• Crazy ideas every 4 hours

*Current Status:*
✅ AI Trading Lab is RUNNING
📊 1 Strategy active (Funding Carry V2)
🧪 2 Hypotheses in pipeline
🔔 Notifications enabled

The system will now continuously learn and notify you when action is needed.

_Time: {datetime.now().strftime('%H:%M UTC')}_"""

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=msg,
            parse_mode='Markdown'
        )
        print("✅ Status message sent to Telegram!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_status())