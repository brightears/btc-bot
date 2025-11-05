"""
Bollinger Band Breakout + Volume Strategy for Bot2
Breakout strategy for BTC trending markets

PHASE 3 STRATEGY (Nov 5, 2025):
- Asset-Strategy Alignment: Breakout for trending BTC (not mean-reversion)
- Entry: BB upper breakout + volume surge + RSI momentum
- Exit: Opposite BB or ROI target
- Volatility-Matched: 2.5% ROI for 2.42% BTC daily volatility

Bot5 Principles Applied:
1. Volatility-matched ROI: 2.42% × 1.03 = 2.5% (achievable)
2. Asset-strategy alignment: Breakout for trending market ✅
3. Exit-profit-only: False (allow early exits)
4. Optimization culture: Parameters tuned for BTC volatility

Expected Performance:
- Win Rate: 55-60% (higher than mean-reversion on trending asset)
- Trades/Day: 2-3
- Avg Win: 1.5-2.5%
- Avg Loss: 2-3%
- Risk/Reward: 1:1.2

Deployment: Bot2 (BTC/USDT)
Date: Nov 5, 2025
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class BBBreakout_Bot2(IStrategy):
    """
    Bollinger Band Breakout strategy for trending BTC markets

    Logic: Buy breakouts with volume confirmation, sell on reversal
    """

    INTERFACE_VERSION: int = 3

    # ROI targets - matched to BTC volatility (2.42% daily)
    minimal_roi = {
        "0": 0.025,    # 2.5% immediate (2.42% × 1.03)
        "30": 0.020,   # 2.0% after 30 min
        "60": 0.015,   # 1.5% after 1 hour
        "120": 0.010   # 1.0% after 2 hours
    }

    # Stop loss - 3% (wider than PAXG due to BTC volatility)
    stoploss = -0.03

    # Trailing stop - lock profits on breakout moves
    trailing_stop = True
    trailing_stop_positive = 0.015          # Start trailing at 1.5% profit
    trailing_stop_positive_offset = 0.020   # Trail by 2.0%
    trailing_only_offset_is_reached = True

    # 15min timeframe - balance between noise and opportunity
    timeframe = '15m'

    # Startup candle count
    startup_candle_count = 50

    # Process only new candles
    process_only_new_candles = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators: Bollinger Bands, RSI, Volume
        """
        # Bollinger Bands (20 period, 2 std)
        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_width'] = (dataframe['bb_upperband'] - dataframe['bb_lowerband']) / dataframe['bb_middleband']

        # RSI (14 period) - for momentum confirmation
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume mean for filter
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry: Breakout above upper BB with volume surge and momentum

        Conditions (ALL must be true):
        1. Close > BB upper band (breakout)
        2. Volume > 2× 20-period mean (significant interest)
        3. RSI > 50 (momentum confirming uptrend)
        4. BB width > 0.02 (volatility present for breakout)

        This captures strong trending moves with confirmation.
        """
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['bb_upperband']) &           # Breakout
                (dataframe['volume'] > dataframe['volume_mean'] * 2.0) &     # Volume surge
                (dataframe['rsi'] > 50) &                                     # Momentum
                (dataframe['bb_width'] > 0.02) &                              # Volatility present
                (dataframe['volume'] > 0)                                     # Basic check
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit: Reversal detected or momentum fading

        Conditions (ANY can trigger):
        1. Close < BB lower band (full reversal)
        2. RSI < 40 (momentum lost)

        This allows exits on trend reversal while letting profits run.
        """
        dataframe.loc[
            (
                (
                    (dataframe['close'] < dataframe['bb_lowerband']) |  # Reversal to lower BB
                    (dataframe['rsi'] < 40)                              # Momentum fading
                ) &
                (dataframe['volume'] > 0)                                # Basic check
            ),
            'exit_long'] = 1

        return dataframe
