#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Update config with latest API keys
python update_config_from_env.py

# Run strategy rotation to select best strategy
echo "🔄 Running strategy rotation..."
python strategy_rotator.py

# Start Freqtrade in dry-run mode
echo "🚀 Starting Freqtrade..."
freqtrade trade --config config.json --strategy NostalgiaForInfinityX5
