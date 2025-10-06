"""
Simple RSI Strategy for Freqtrade
Buy when RSI < 30 (oversold), Sell when RSI > 70 (overbought)
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class SimpleRSI(IStrategy):
    """
    Simple RSI-based strategy
    """

    # Minimal ROI designed for 2% profit target
    minimal_roi = {
        "0": 0.02
    }

    # Stop loss at -1%
    stoploss = -0.01

    # Trailing stop loss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Optimal timeframe
    timeframe = '5m'

    # Startup candle count
    startup_candle_count = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal logic
        """
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # RSI oversold
                (dataframe['volume'] > 0)   # Volume check
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal logic
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) &  # RSI overbought
                (dataframe['volume'] > 0)   # Volume check
            ),
            'exit_long'] = 1

        return dataframe
