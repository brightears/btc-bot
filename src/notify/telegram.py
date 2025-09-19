import os
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from src.utils.logger import get_logger

logger = get_logger()


class TelegramNotifier:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.bot: Optional[Bot] = None
        self.chat_id: Optional[str] = None

        if enabled:
            token = os.getenv('TELEGRAM_TOKEN')
            self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

            if token and self.chat_id:
                try:
                    self.bot = Bot(token=token)
                    logger.info("Telegram notifier initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Telegram bot: {e}")
                    self.bot = None
            else:
                logger.info("Telegram credentials not found, notifications disabled")
                self.bot = None

    def send_message(self, message: str) -> bool:
        if not self.bot or not self.chat_id or not self.enabled:
            return False

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_async(message))
            loop.close()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def _send_async(self, message: str):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")

    def handle_status_command(self, state: dict) -> str:
        if state.get('position'):
            pos = state['position']
            status = (
                "📊 *Current Status*\n\n"
                f"Symbol: {pos.get('symbol', 'N/A')}\n"
                f"Notional: ${pos.get('notional_usdt', 0):.2f}\n"
                f"Entry Time: {pos.get('entry_time', 'N/A')}\n"
                f"Funding Collected: ${pos.get('funding_collected', 0):.4f}\n"
                f"Realized P&L: ${pos.get('realized_pnl', 0):.4f}"
            )
        else:
            status = "📊 *Current Status*\n\nNo active position"

        return status