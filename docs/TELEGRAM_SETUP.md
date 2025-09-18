# Telegram Setup

1. **Create a bot**
   - Open Telegram and talk to [@BotFather](https://t.me/BotFather).
   - `/newbot` → choose a descriptive name and username.
   - Save the HTTP API token (do **not** commit it to git).

2. **Find your chat ID**
   - Add the new bot to a private chat or group.
   - Send a `/start` message to the bot.
   - Call the following from the command line (replace `TOKEN`):
     ```bash
     curl -s https://api.telegram.org/botTOKEN/getUpdates | jq '.result[0].message.chat.id'
     ```

3. **Configure `.env`**
   ```ini
   TELEGRAM_TOKEN=123456:ABC...
   TELEGRAM_CHAT_ID=987654321
   ```

4. **Verify**
   - Run the bot in dry-run mode.
   - You should receive notifications for entries/exits and `/status` summaries.
   - If messages fail, check network firewalls and confirm the bot has access to the chat.

> The notifier never logs tokens or chat IDs, but keep `.env` strictly local.
