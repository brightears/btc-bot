# Dry-Run Testing Guide

## Pre-flight Checks

1. Verify config.yaml exists
2. Check .env.sample (don't need real keys for dry-run)
3. Ensure logs/ directory is writable

## Running Dry-Run

```bash
# Basic dry-run
python run_funding_exec.py

# With custom parameters
python run_funding_exec.py --notional_usdt 500 --threshold_bps 1.0

# Faster loop for testing
python run_funding_exec.py --loop_seconds 60
```

## What to Expect

- "[DRY-RUN]" prefix in logs
- Simulated orders logged
- State saved to logs/state.json
- No real trades executed

## Monitoring

```bash
# Watch logs
tail -f logs/funding_exec.log

# Check state
cat logs/state.json | jq .
```