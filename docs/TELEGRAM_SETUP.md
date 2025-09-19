# Telegram Bot Setup

## Creating a Bot

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose name and username
4. Save the token

## Getting Chat ID

1. Message your bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find your chat ID in the response

## Configuration

Add to `.env`:
```
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Alert Types

- Position opened/closed
- Funding collected
- Errors and warnings
- `/status` command support