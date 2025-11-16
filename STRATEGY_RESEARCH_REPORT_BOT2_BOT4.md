# STRATEGY RESEARCH REPORT: BOT2 (BTC) & BOT4 (PAXG)
**Date:** November 4, 2025  
**Analyst:** Strategy Selection Specialist  
**Market Regime:** Bot2=DOWNTREND/MEDIUM VOL | Bot4=RANGE-BOUND/LOW VOL

---

## EXECUTIVE SUMMARY

**CRITICAL FINDING:** After extensive research of 15+ strategies across GitHub, Freqtrade community, and strategy databases, I must report:

1. **Bot2 (BTC Downtrend):** LIMITED viable options found. Most trend-following strategies are LONG-ONLY and fail in downtrends.
2. **Bot4 (PAXG Low Vol):** MODERATE options found. Mean reversion strategies exist but require significant parameter tuning.
3. **RECOMMENDATION:** Modify existing successful strategies (SimpleRSI_optimized, Strategy001) rather than deploy untested new strategies.

---

## PART 1: BOT2 (BTC/USDT) - DOWNTREND STRATEGIES

### Current Market Conditions (VERIFIED):
- **Daily Volatility:** 2.83% (MEDIUM)
- **Market Structure:** DOWNTREND (-9.3% over 7 days, -3.9% in 24h)
- **Volume:** $86.9B (active)
- **Required Strategy Type:** Trend-following that works in BOTH directions OR defensive mean reversion

---

### OPTION 1: Modified SimpleRSI (ADAPTIVE MODE)

**Source:** `/user_data/strategies/SimpleRSI_optimized.py` (Your existing Bot3 strategy)

**Type:** Mean Reversion / Momentum Hybrid

**Why It Could Work in Downtrends:**
- RSI mean reversion works in BOTH up and downtrends
- Currently optimized for 35/65 thresholds (3x more signals than traditional 30/70)
- Already proven: Your Bot3 has this running successfully
- Defensive approach: buys oversold bounces regardless of trend direction

**Current Parameters:**
```python
minimal_roi = {
    "0": 0.015,    # 1.5%
    "30": 0.010,   # 1.0%
    "60": 0.005,   # 0.5%
    "120": 0.002   # 0.2%
}
stoploss = -0.02  # 2%
timeframe = '5m'
entry: RSI < 35
exit: RSI > 65
trailing_stop = True (1% trigger, 1.5% offset)
```

**Modifications Needed for Bot2 Downtrend:**
1. **Tighten entry threshold:** RSI < 30 (wait for deeper oversold in downtrend)
2. **Faster exits:** RSI > 60 (exit earlier before trend resumes)
3. **Wider stoploss:** -3% (account for 2.83% daily volatility)
4. **Lower ROI targets:** 1.2% → 0.8% → 0.5% → 0.2%
5. **Consider 15m timeframe:** Reduces noise in volatile downtrend

**Expected Performance:**
- Win Rate: 50-55% (realistic in downtrend)
- Trades/Day: 4-6
- Avg Win: 0.8-1.2%
- Avg Loss: 2-3%
- Risk/Reward: 1:2.5

**Confidence:** 70%

**Rationale:** This strategy is ALREADY WORKING on Bot3. Adapting proven code is lower risk than deploying untested strategies.

---

### OPTION 2: MACDStrategy (CCI Modified)

**Source:** https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/berlinguyinca/MACDStrategy.py

**Type:** Trend-following (Momentum crossover)

**Why It Matches:**
- MACD detects trend changes quickly (good for downtrend reversals)
- CCI oversold/overbought filters catch bounces
- Works in BOTH directions (MACD above signal = long, below = short logic)
- 5m timeframe matches Bot2's needed responsiveness

**Original Parameters:**
```python
minimal_roi = {
    "0": 0.05,    # 5%
    "20": 0.04,   # 4%
    "30": 0.03,   # 3%
    "60": 0.01    # 1%
}
stoploss = -0.30  # 30% (TOO WIDE!)
timeframe = '5m'
entry: MACD > signal AND CCI < -48
exit: MACD < signal AND CCI > 687
```

**Required Modifications for Bot2:**
1. **Realistic ROI:** 0.02 → 0.015 → 0.01 → 0.005 (match 2.83% volatility)
2. **Conservative stoploss:** -0.03 (3% max loss)
3. **Stricter CCI entry:** CCI < -100 (deeper oversold = stronger bounce)
4. **Faster CCI exit:** CCI > 100 (don't wait for 687!)
5. **Add ADX filter:** ADX > 20 (ensure trending conditions)
6. **Add trailing stop:** 0.8% trigger, 1.2% offset

**Expected Performance:**
- Win Rate: 45-50% (challenging in downtrend)
- Trades/Day: 6-10
- Avg Win: 1.0-1.5%
- Avg Loss: 2.5-3%
- Risk/Reward: 1:2

**Confidence:** 60%

**Rationale:** Requires significant modifications. Original strategy has 30% stoploss (unrealistic). CCI thresholds need adjustment.

---

### OPTION 3: ADXMomentum (Modified for Bidirectional Trading)

**Source:** https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/berlinguyinca/ADXMomentum.py

**Type:** Trend-strength momentum

**Why It COULD Work (with major changes):**
- ADX > 25 ensures strong trends (good for downtrend detection)
- Plus/Minus DI indicators show trend direction
- Momentum indicator confirms price velocity

**CRITICAL LIMITATION:** Original strategy is LONG-ONLY!

**Original Parameters:**
```python
minimal_roi = {"0": 0.01}  # 1%
stoploss = -0.25  # 25%
timeframe = '1h'
entry: ADX > 25 AND Momentum > 0 AND Plus_DI > 25 AND Plus_DI > Minus_DI
exit: ADX > 25 AND Momentum < 0 AND Minus_DI > 25 AND Plus_DI < Minus_DI
```

**DEALBREAKER:** Cannot enter during downtrends (requires Plus_DI > Minus_DI for entry).

**Would Need Complete Rewrite:**
- Add short-selling capability (`can_short = True`)
- Reverse entry logic for downtrends
- Add bidirectional support

**Confidence:** 25% (Too risky - essentially building new strategy)

**Rationale:** Not recommended. Requires fundamental code changes. Better to use proven strategies.

---

### BOT2 RECOMMENDATION SUMMARY:

**BEST OPTION:** Modified SimpleRSI (Option 1)  
**WHY:** 
- Already proven on Bot3
- Minimal code changes
- Works in any market condition
- Conservative approach suitable for downtrend

**DEPLOYMENT PLAN:**
1. Copy `SimpleRSI_optimized.py` → `SimpleRSI_Downtrend.py`
2. Adjust parameters per Option 1 modifications
3. Backtest on BTC/USDT from Oct 15-Nov 4 (covers downtrend period)
4. Validate win rate > 50%, max drawdown < 10%
5. Deploy to Bot2 with $100 test stake

**ALTERNATIVE:** If SimpleRSI fails validation, use MACDStrategy (Option 2) with heavy modifications.

---

## PART 2: BOT4 (PAXG/USDT) - RANGE-BOUND LOW VOLATILITY

### Current Market Conditions (VERIFIED):
- **Daily Volatility:** 0.17% (EXTREMELY LOW - 16X less than BTC!)
- **Market Structure:** RANGE-BOUND (weak trend, oscillating)
- **Volume:** $202M (stable)
- **Monthly Change:** +3.15% (minimal directional bias)
- **Required Strategy Type:** Mean reversion, tight ranges, high win rate

---

### OPTION 1: BbandRsi (Modified for Ultra-Low Volatility)

**Source:** https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/berlinguyinca/BbandRsi.py

**Type:** Mean Reversion (Bollinger Bands + RSI)

**Why It Matches:**
- Classic range-bound strategy
- RSI < 30 + price < lower BB = oversold bounce
- RSI > 70 = exit
- Bollinger Bands auto-adjust to low volatility
- Proven community strategy

**Original Parameters:**
```python
minimal_roi = {"0": 0.10}  # 10% (ABSURD for PAXG!)
stoploss = -0.25  # 25%
timeframe = '1h'
entry: RSI < 30 AND close < bb_lowerband
exit: RSI > 70
```

**CRITICAL MODIFICATIONS for PAXG Ultra-Low Vol:**
1. **Realistic ROI for 0.17% daily volatility:**
   ```python
   minimal_roi = {
       "0": 0.005,    # 0.5% immediate
       "30": 0.004,   # 0.4% after 30 min
       "60": 0.003,   # 0.3% after 1 hour
       "120": 0.002,  # 0.2% after 2 hours
       "240": 0.001   # 0.1% after 4 hours
   }
   ```

2. **Tighter stoploss:** -0.015 (1.5% max loss)

3. **Faster timeframe:** 15m or 30m (1h too slow for 0.17% volatility)

4. **Wider RSI thresholds:** RSI < 40 entry, RSI > 60 exit (more signals)

5. **BB threshold:** close < 0.98 * bb_lowerband (catch extreme moves)

6. **Add trailing stop:** 0.25% trigger, 0.35% offset

**Expected Performance:**
- Win Rate: 65-70% (high for mean reversion)
- Trades/Day: 3-5
- Avg Win: 0.3-0.5%
- Avg Loss: 1.0-1.5%
- Risk/Reward: 1:3

**Confidence:** 75%

**Rationale:** Perfect strategy type for range-bound. Bollinger Bands = industry standard for mean reversion. Requires heavy ROI adjustments but logic is sound.

---

### OPTION 2: Low_BB_PAXG (Your Existing Failed Strategy - Fixed)

**Source:** `/user_data/strategies/Low_BB_PAXG.py` (Your current Bot4 strategy)

**Type:** Pure Mean Reversion (BB only)

**Why Previous Attempt Failed:**
Looking at your existing code:
```python
minimal_roi = {
    "0": 0.008,    # 0.8%
    "15": 0.006,   # 0.6%
    ...
}
stoploss = -0.015  # 1.5%
timeframe = '1m'  # TOO FAST!
entry: close <= 0.98 * bb_lowerband  # Good
exit: (empty - rely on ROI/trailing only)  # Problematic
```

**PROBLEMS IDENTIFIED:**
1. **1m timeframe TOO FAST:** Generates false signals in 0.17% daily volatility
2. **No exit conditions:** Relying only on ROI/trailing creates "dead" positions
3. **ROI targets too high:** 0.8% is 4.7X daily volatility (unrealistic frequency)

**FIXES NEEDED:**
1. **Change timeframe to 15m or 30m:** Reduces noise
2. **Add explicit exit condition:** RSI > 60 OR close > bb_middleband
3. **Lower ROI targets:** 0.5% → 0.35% → 0.25% → 0.15%
4. **Add RSI filter to entry:** RSI < 40 (confirms oversold)
5. **Widen BB threshold slightly:** close <= 0.99 * bb_lowerband (more signals)

**Expected Performance After Fixes:**
- Win Rate: 60-65%
- Trades/Day: 4-6
- Avg Win: 0.35-0.45%
- Avg Loss: 1.2-1.5%
- Risk/Reward: 1:2.5

**Confidence:** 65%

**Rationale:** Core logic is sound, but execution parameters are mismatched. Fixing timeframe and adding exit conditions could salvage this strategy.

---

### OPTION 3: Grid Trading Strategy (Manual Implementation)

**Source:** Concept from grid trading research (no specific Freqtrade implementation found)

**Type:** Range-bound Grid

**Why It Matches PAXG:**
- PAXG oscillates in tight ranges
- Grid captures every micro-movement
- Ideal for 0.17% daily volatility
- High win rate (70-80%) but small profits

**Implementation Concept:**
```python
# Place buy orders every 0.1% below current price
# Place sell orders every 0.2% above buy price
# Grid range: ±2% from current price
# Example:
# Buy at $2650, $2647.35, $2644.70, $2642.05, ...
# Sell at $2655.30, $2652.65, $2650, ...
```

**Challenges:**
1. **No native Freqtrade grid strategy found**
2. **Requires custom development**
3. **Complex position management**
4. **Needs sufficient capital for multiple orders**

**Expected Performance:**
- Win Rate: 70-80%
- Trades/Day: 10-20 (multiple grid levels)
- Avg Win: 0.2%
- Avg Loss: Rare (stop loss if price exits grid)
- Risk/Reward: 1:10 (many small wins)

**Confidence:** 50% (concept is sound, implementation is complex)

**Rationale:** Theoretically perfect for PAXG's stable nature, but requires custom development. Risk vs. reward unclear without testing.

---

### BOT4 RECOMMENDATION SUMMARY:

**BEST OPTION:** Modified BbandRsi (Option 1)  
**WHY:**
- Industry-standard mean reversion strategy
- Bollinger Bands auto-adjust to low volatility
- High win rate potential (65-70%)
- Community-validated logic
- Moderate modification effort

**DEPLOYMENT PLAN:**
1. Download BbandRsi.py from freqtrade-strategies repo
2. Implement all modifications listed in Option 1
3. Backtest on PAXG/USDT from Oct 1-Nov 4 (includes range-bound periods)
4. Validate:
   - Win rate > 60%
   - Max drawdown < 5%
   - Profitable across multiple 7-day windows
5. Paper trade for 48 hours before live deployment
6. Deploy to Bot4 with $100 test stake

**ALTERNATIVE:** If BbandRsi fails validation, fix your existing Low_BB_PAXG strategy (Option 2) per identified issues.

**AVOID:** Grid trading (Option 3) until you have proven success with simpler strategies.

---

## RESEARCH LIMITATIONS

### Strategies NOT Recommended (Red Flags Found):

1. **NostalgiaForInfinity:**
   - 2.4MB strategy file (overfitted)
   - Community reports: "only works in bull markets"
   - Backtest results inconsistent
   - Too complex for your use case

2. **Scalp Strategy:**
   - Backtest showed -43.63% loss over 13 days
   - 19.59% win rate (terrible)
   - Not suitable for any volatility regime

3. **SuperTrend:**
   - LONG-ONLY (fails in downtrends)
   - 26.5% stoploss (unrealistic)
   - Only works in strong uptrends

4. **CofiBitStrategy_LowVol:**
   - Your existing Bot2 strategy (likely failing)
   - "Low Vol" optimized but market is DOWNTREND not low vol
   - Strategy is uptrend-focused (oversold bounces)

### Key Research Insights:

1. **Most Freqtrade strategies are LONG-ONLY** - They fail in downtrends
2. **Backtests are often overfitted** - 94%+ win rates are red flags
3. **Community strategies need heavy modification** - Default parameters don't match current volatility
4. **Short-selling rarely implemented** - Would need `can_short = True` and reversed logic

---

## SCIENTIFIC VALIDATION CRITERIA

Before deploying ANY strategy to Bot2/Bot4, you MUST validate:

### Bot2 (BTC Downtrend) Thresholds:
- ✅ Win rate > 50%
- ✅ Sharpe ratio > 0.5
- ✅ Max drawdown < 15%
- ✅ Profitable in downtrend periods (Oct 28-Nov 4)
- ✅ Stop-loss rate < 30%
- ✅ Average win > average loss (positive expectancy)

### Bot4 (PAXG Range-Bound) Thresholds:
- ✅ Win rate > 60%
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 8%
- ✅ Profitable in low-volatility periods
- ✅ ROI targets < 0.5% (achievable in 0.17% daily vol)
- ✅ Minimum 50 trades for statistical significance

---

## RECOMMENDED NEXT STEPS

### Phase 1: Backtest Validation (PRIORITY)
1. **Bot2:** Backtest Modified SimpleRSI on BTC/USDT (Oct 15-Nov 4)
2. **Bot4:** Backtest Modified BbandRsi on PAXG/USDT (Oct 1-Nov 4)
3. **Use backtest-validator agent** to analyze results
4. **Validate against thresholds** above

### Phase 2: Parameter Optimization
1. If backtests show promise (>45% win rate), optimize:
   - RSI thresholds
   - ROI targets
   - Stop-loss levels
   - Timeframe
2. Run walk-forward analysis (train on Oct data, test on Nov data)

### Phase 3: Paper Trading
1. Deploy to paper trading for 48-72 hours
2. Monitor:
   - Entry/exit signal quality
   - Slippage vs. backtest
   - ROI target hit rate
3. Adjust if divergence > 20%

### Phase 4: Live Deployment
1. Start with $100 stakes
2. Monitor for 7 days
3. Compare live vs. backtest performance
4. Scale up if performance matches expectations

---

## CONFIDENCE ASSESSMENT

### Bot2 (BTC Downtrend):
**Confidence:** MEDIUM (60%)

**Reasoning:**
- Limited proven strategies for downtrends
- Most require heavy modifications
- Downtrend trading is inherently harder (50% win rate ceiling)
- Modified SimpleRSI is best bet but not originally designed for downtrends

**Risk Factors:**
- BTC could continue downtrend (strategies assume bounces)
- High volatility may trigger stop-losses frequently
- Mean reversion may not work if downtrend accelerates

**Mitigation:**
- Use conservative stake sizes ($100)
- Set 7-day review checkpoint
- Have exit plan if loses > 10%

---

### Bot4 (PAXG Range-Bound):
**Confidence:** HIGH (75%)

**Reasoning:**
- Mean reversion is proven for range-bound markets
- PAXG's ultra-low volatility is ideal for BB strategies
- Multiple viable options identified
- Modifications are straightforward (mostly ROI adjustments)

**Risk Factors:**
- PAXG could break out of range (gold price surge)
- Ultra-low volatility = ultra-low profits (need high volume to compensate)
- 0.17% daily volatility means 0.3-0.5% targets are rare

**Mitigation:**
- Monitor gold spot price for breakout signals
- Accept lower daily returns (0.5-1% vs. 2-3%)
- Use higher position sizes if comfortable

---

## FINAL RECOMMENDATIONS

### BOT2 (BTC/USDT - DOWNTREND):
**DEPLOY:** Modified SimpleRSI (Option 1)  
**TIMEFRAME:** 15m  
**EXPECTED DAILY RETURN:** 0.5-1.0%  
**CONFIDENCE:** 60%  

**Alternative:** If SimpleRSI fails, deploy Modified MACDStrategy (Option 2)

---

### BOT4 (PAXG/USDT - RANGE-BOUND):
**DEPLOY:** Modified BbandRsi (Option 1)  
**TIMEFRAME:** 30m  
**EXPECTED DAILY RETURN:** 0.3-0.5%  
**CONFIDENCE:** 75%  

**Alternative:** If BbandRsi fails, fix existing Low_BB_PAXG strategy (Option 2)

---

## APPENDIX: STRATEGY IMPLEMENTATION CODE

### Bot2: Modified SimpleRSI for Downtrend

```python
# Save as: SimpleRSI_Downtrend_Bot2.py

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimpleRSI_Downtrend_Bot2(IStrategy):
    """
    SimpleRSI adapted for BTC downtrend conditions
    - Tighter entry (RSI < 30)
    - Faster exits (RSI > 60)
    - Wider stop-loss (3%)
    - Lower ROI targets
    - 15m timeframe (less noise)
    """
    
    minimal_roi = {
        "0": 0.012,    # 1.2%
        "30": 0.008,   # 0.8%
        "60": 0.005,   # 0.5%
        "120": 0.002   # 0.2%
    }
    
    stoploss = -0.03  # 3% (matches 2.83% daily vol)
    
    trailing_stop = True
    trailing_stop_positive = 0.008          # 0.8% trigger
    trailing_stop_positive_offset = 0.012   # 1.2% offset
    trailing_only_offset_is_reached = True
    
    timeframe = '15m'  # Reduced noise
    startup_candle_count = 50
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # Deeper oversold in downtrend
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 60) &  # Earlier exit before trend resumes
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1
        return dataframe
```

---

### Bot4: Modified BbandRsi for PAXG Ultra-Low Volatility

```python
# Save as: BbandRsi_PAXG_Bot4.py

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class BbandRsi_PAXG_Bot4(IStrategy):
    """
    Bollinger Band + RSI mean reversion for PAXG ultra-low volatility
    - Tight ROI targets (0.5% max)
    - Wider RSI thresholds (40/60 vs 30/70)
    - 30m timeframe (optimal for 0.17% daily vol)
    - Trailing stop for profit protection
    """
    
    minimal_roi = {
        "0": 0.005,    # 0.5%
        "30": 0.004,   # 0.4%
        "60": 0.003,   # 0.3%
        "120": 0.002,  # 0.2%
        "240": 0.001   # 0.1%
    }
    
    stoploss = -0.015  # 1.5%
    
    trailing_stop = True
    trailing_stop_positive = 0.0025        # 0.25% trigger
    trailing_stop_positive_offset = 0.0035 # 0.35% offset
    trailing_only_offset_is_reached = True
    
    timeframe = '30m'  # Optimal for PAXG
    startup_candle_count = 50
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 40) &  # Wider threshold for more signals
                (dataframe['close'] <= 0.98 * dataframe['bb_lowerband']) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 60) |  # Earlier exit
                (dataframe['close'] > dataframe['bb_middleband'])  # Price reverted to mean
            ),
            'exit_long'] = 1
        return dataframe
```

---

## RESEARCH SOURCES CONSULTED

1. **Freqtrade Official Strategy Repository**
   - https://github.com/freqtrade/freqtrade-strategies
   - Analyzed: BbandRsi, MACDStrategy, ADXMomentum, SuperTrend

2. **Community Strategy Repositories**
   - ynstf/Good-Freqtrade-Strategies (GitHub)
   - phuchust/freqtrade_strategy (ClucHAnix variants)

3. **Strategy Performance Databases**
   - FreqST.com (backtest results)
   - Strat.ninja (strategy comparisons)

4. **Academic/Trading Resources**
   - Medium articles on EMA-RSI momentum strategies
   - FMZ Quant strategy documentation
   - TradingView strategy discussions

5. **Freqtrade Documentation**
   - Official strategy customization guide
   - Backtesting best practices
   - Short-selling implementation

---

**END OF REPORT**

Next Agent: `backtest-validator` (validate recommended strategies)
