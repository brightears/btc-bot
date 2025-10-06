#!/usr/bin/env python3
"""
Update Freqtrade config.json with API keys from .env file
"""
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read current config
with open('config.json', 'r') as f:
    config = json.load(f)

# Update with API keys from .env
config['exchange']['key'] = os.getenv('BINANCE_KEY', '')
config['exchange']['secret'] = os.getenv('BINANCE_SECRET', '')
config['telegram']['token'] = os.getenv('TELEGRAM_TOKEN', '')
config['telegram']['chat_id'] = os.getenv('TELEGRAM_CHAT_ID', '')

# Write updated config
with open('config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("✅ Updated config.json with API keys from .env")
print(f"   - Binance Key: {config['exchange']['key'][:10]}...")
print(f"   - Telegram Token: {config['telegram']['token'][:10]}...")
print(f"   - Telegram Chat ID: {config['telegram']['chat_id']}")
