# Backtest Failure Report - November 4, 2025

## Executive Summary

**Status**: ❌ **BOTH STRATEGIES FAILED VALIDATION**
**Outcome**: Neither CofiBitStrategy nor Low_BB_PAXG are suitable for deployment
**Root Cause**: Strategies fundamentally incompatible with low-volatility market conditions
**Next Step**: Request new strategy recommendations from freqtrade-strategy-selector agent

---

## Background

After Bot1/Bot6 optimization rollback, attempted to replace broken Strategy004 on Bot2 (BTC) and Bot4 (PAXG) with:
- **Bot2**: CofiBitStrategy_LowVol (mean reversion/scalping hybrid)
- **Bot4**: Low_BB_PAXG (Bollinger Band mean reversion)

Both strategies recommended by freqtrade-strategy-selector agent with 72% confidence.

---

## Test Methodology

### Phase 1: Initial Backtests (INVALID)
- Ran backtests using Bot2/Bot4 existing configs
- **DISCOVERY**: Configs were overriding strategy parameters with baseline Strategy001 values
- Results showed catastrophic failure, but tests were INVALID

### Phase 2: backtest-validator Agent Analysis
- Used backtest-validator agent to diagnose root cause
- Agent identified config overrides as PRIMARY failure cause
- **PREDICTION**: Expected 50-60% win rates after removing overrides
- Created clean configs removing: minimal_roi, stoploss, trailing_stop, timeframe

### Phase 3: Clean Config Backtests (VALID)
- Uploaded clean configs to VPS
- Re-ran backtests with strategy parameters only
- **RESULT**: Strategies still failed catastrophically

---

## Test Results

### CofiBitStrategy_LowVol (Bot2 - BTC/USDT)

**Parameters Verified (CORRECT)**:
```
ROI: 1.5% max (not overridden)
Stoploss: -2.5% (not overridden)
Trailing Stop: TRUE (not overridden)
Timeframe: 5m
```

**Results**:
- **Trades**: 55 ✅ (>50 required)
- **Win Rate**: 14.5% ❌ (need >55%)
- **P&L**: -$19.25 USDT ❌ (need profit)
- **Wins/Losses**: 8 wins, 47 losses
- **Max Consecutive Losses**: 20

**Exit Breakdown**:
- Stop-loss: 2 exits (-$5.36)
- Exit signal: 53 exits (-$13.89)

**Verdict**: **FAILED ALL CRITERIA** - Strategy enters correctly but cannot exit profitably

---

### Low_BB_PAXG (Bot4 - PAXG/USDT)

**Parameters Verified (CORRECT)**:
```
ROI: 0.8% max (not overridden)
Stoploss: -1.5% (not overridden)
Trailing Stop: TRUE (not overridden)
Timeframe: 1m (not overridden!) ✅
```

**Results**:
- **Trades**: 0 ❌ (need >30)
- **Win Rate**: N/A
- **P&L**: $0.00 USDT ❌

**Verdict**: **COMPLETE FAILURE** - Entry conditions never met, no trades generated

---

## Root Cause Analysis

### Why CofiBitStrategy Failed

**Strategy Logic**: Buy on Stochastic oversold + ADX trend, sell on Stochastic overbought or price > EMA high

**Failure Mechanism**:
1. **Entry signals generated correctly** (55 trades)
2. **Exit signals fire TOO EARLY** in low-volatility environment
3. **1.5% ROI target unreachable** in 2.42% daily volatility market
4. **Price reversals** happen BEFORE ROI targets hit
5. **Result**: 85.5% of trades exit at loss

**Market Mismatch**:
- Strategy designed for 5-10% daily volatility
- Current BTC volatility: 2.42% daily
- ROI expectations exceed realistic price movement

---

### Why Low_BB_PAXG Failed

**Strategy Logic**: Buy when price crosses below 98% of lower Bollinger Band (20-period, 2 std dev)

**Failure Mechanism**:
1. **PAXG volatility: 1.19% daily** (extremely low)
2. **Lower BB rarely touched** in stable gold-backed asset
3. **Entry condition**: `close <= 0.98 * bb_lowerband`
4. **Result**: Condition NEVER met in 20-day test period

**Market Mismatch**:
- Strategy designed for volatile assets (3-5% daily moves)
- PAXG is gold-backed stablecoin (0.5-2% daily moves)
- Bollinger Band threshold too aggressive for asset characteristics

---

## backtest-validator Agent Prediction vs Reality

**Agent Predicted**:
- CofiBitStrategy: 50-60% win rate after removing overrides
- Low_BB_PAXG: 55-65% win rate, 80-120 trades

**Actual Results**:
- CofiBitStrategy: 14.5% win rate ❌
- Low_BB_PAXG: 0 trades ❌

**Analysis of Agent Error**:
1. Agent correctly identified config override issue
2. Agent INCORRECTLY assumed strategies were sound underneath
3. Agent did not account for market regime incompatibility
4. **Lesson**: Config validation ≠ strategy validation

---

## Market Conditions (Oct 15 - Nov 4, 2025)

- **BTC Volatility**: 2.42% daily (LOW)
- **PAXG Volatility**: 1.19% daily (ULTRA-LOW)
- **Market Regime**: Range-bound, low volatility
- **BTC Price Change**: -5.69% over 20 days

**Strategy Requirements**:
- CofiBitStrategy: 5-10% daily volatility (2X higher than actual)
- Low_BB_PAXG: 3-5% daily volatility (3X higher than actual)

**Conclusion**: Strategies are volatility-dependent and current market lacks sufficient movement.

---

## Lessons Learned

### What Worked
1. ✅ Scientific approach using backtest-validator agent
2. ✅ Identification and removal of config overrides
3. ✅ Parameter verification in logs
4. ✅ Comprehensive testing methodology

### What Failed
1. ❌ Strategy selection based on agent confidence without market regime analysis
2. ❌ Assumption that "community strategies" work in all conditions
3. ❌ Insufficient validation of strategy volatility requirements
4. ❌ Trust in backtest-validator predictions without empirical verification

### Process Improvements Needed
1. **Market Regime Analysis FIRST** before strategy selection
2. **Volatility matching** - ensure strategy volatility needs match current market
3. **Multi-agent validation** - don't rely on single agent prediction
4. **Smaller parameter changes** - test conservative modifications first
5. **Walk-forward validation** - test on multiple time periods

---

## Recommendations

### IMMEDIATE (Next 2 Hours)

1. **Use freqtrade-strategy-selector agent AGAIN** with new criteria:
   - **Market Regime**: Low volatility (BTC 2-3%, PAXG 1-2%)
   - **Strategy Type**: Range-bound, not trend-following
   - **Proven Backtests**: Community strategies with validated results
   - **Success Criteria**: >50% win rate in LOW volatility conditions

2. **Specify Exact Requirements**:
   - BTC strategy: Target 0.5-1.5% ROI per trade
   - PAXG strategy: Target 0.3-0.8% ROI per trade
   - Both: Proven to work in 1-3% daily volatility environments

### SHORT-TERM (Next 24-48 Hours)

3. **Test 3-5 Candidate Strategies**:
   - Download top recommendations
   - Backtest on Oct 15-Nov 4 data
   - Require >50% win rate, >20 trades minimum
   - Deploy only strategies that PASS validation

4. **Parallel: Fix Bot1**:
   - trading-strategy-debugger found Bot1 failure was config rollback, not optimization
   - Re-deploy Bot1 with corrected parameters (-2.0% stop vs -1.5%)
   - Add config rollback protection

### MEDIUM-TERM (Next Week)

5. **Implement market-regime-detector Agent**:
   - Hourly market regime analysis
   - Automatic strategy rotation based on volatility regime
   - Prevent deploying high-volatility strategies in low-volatility markets

6. **Build Strategy Validation Pipeline**:
   - Automated backtesting on deployment
   - Multi-period walk-forward analysis
   - Volatility requirement validation
   - Agent consensus (≥2 agents must approve)

---

## Success Criteria for Next Attempt

**Backtest Requirements**:
- Win Rate: >50% (lowered from >55% due to low volatility)
- Trade Count: >20 trades over 20 days (1/day minimum)
- P&L: Positive (any profit acceptable given conditions)
- Max Consecutive Losses: <10
- Drawdown: <5%

**Deployment Gate**:
- MUST pass backtest on Oct 15-Nov 4 data
- MUST be validated by ≥2 agents (strategy-selector + backtest-validator)
- MUST have volatility requirements ≤ current market conditions
- MUST have proven community adoption (≥100 GitHub stars or equivalent)

---

## Files Created

1. `bot2_clean_config.json` - Bot2 config without strategy overrides
2. `bot4_clean_config.json` - Bot4 config without strategy overrides
3. `CofiBitStrategy_LowVol.py` - Modified strategy (FAILED validation)
4. `Low_BB_PAXG.py` - Modified strategy (FAILED validation)

## Backtest Results

1. `/root/btc-bot/user_data/backtest_results/backtest-result-2025-11-04_11-53-53.meta.json` - CofiBitStrategy final test
2. `/root/btc-bot/user_data/backtest_results/backtest-result-2025-11-04_11-54-16.meta.json` - Low_BB_PAXG final test

---

## Status

**Bot2 (BTC/USDT)**: Still running broken Strategy004, awaiting replacement
**Bot4 (PAXG/USDT)**: Still running broken Strategy004, awaiting replacement

**Current System State**:
- All 6 bots running
- Bot1/Bot6 rolled back to baseline (Oct 30 optimizations reversed)
- Bot3/Bot5 running optimized strategies (successful)
- Bot2/Bot4 blocked pending new strategy identification

**Next Action**: Launch freqtrade-strategy-selector agent with revised criteria focusing on LOW VOLATILITY strategies.

---

**Report Date**: November 4, 2025, 11:55 UTC
**Test Period**: October 15 - November 4, 2025 (20 days)
**Conclusion**: Both strategies REJECTED for deployment. Require new strategy candidates.

🤖 Generated with Claude Code (https://claude.com/claude-code)
