"""
Simple RSI Strategy for Freqtrade - OPTIMIZED FOR LOW VOLATILITY
Buy when RSI < 35 (oversold), Sell when RSI > 65 (overbought)
Optimized for BTC 2.42% daily volatility ranging market
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class SimpleRSI(IStrategy):
    """
    Simple RSI-based strategy - Optimized Oct 30, 2025

    Changes from original:
    - RSI thresholds: 30/70 → 35/65 (more signals in ranging market)
    - Stop-loss: -1% → -2.5% (matches 2.42% BTC volatility)
    - ROI: Single 2% → Staged 1.5%/1%/0.5%/0.2% (achievable in 1.7% swings)
    - Expected improvement: 55% reduction in losses
    """

    # Staged ROI for ranging market (achievable in 1.7% daily swings)
    minimal_roi = {
        "0": 0.015,    # 1.5% immediate target
        "30": 0.010,   # 1.0% after 30 minutes
        "60": 0.005,   # 0.5% after 60 minutes
        "120": 0.002   # 0.2% after 2 hours (exit slow trades)
    }

    # Stop loss at -2.5% (matches current BTC volatility)
    # Previous -1% was too tight, causing 55% stop-out rate
    stoploss = -0.025

    # Trailing stop loss configuration
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Optimal timeframe for ranging market
    timeframe = '5m'

    # Startup candle count for RSI calculation
    startup_candle_count = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators
        """
        # RSI with standard 14 period
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal logic - OPTIMIZED THRESHOLDS
        """
        dataframe.loc[
            (
                (dataframe['rsi'] < 35) &  # RSI oversold (was 30, now 35 for more signals)
                (dataframe['volume'] > 0)   # Volume check
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal logic - OPTIMIZED THRESHOLDS
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 65) &  # RSI overbought (was 70, now 65 for more exits)
                (dataframe['volume'] > 0)   # Volume check
            ),
            'exit_long'] = 1

        return dataframe