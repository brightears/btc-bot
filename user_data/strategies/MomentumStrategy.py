"""
Momentum Strategy with EMA Crossover
Buy when fast EMA crosses above slow EMA, sell on opposite
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class MomentumStrategy(IStrategy):
    """
    EMA Crossover Momentum Strategy
    """

    # ROI table
    minimal_roi = {
        "0": 0.025,     # 2.5% profit target
        "30": 0.015,    # 1.5% after 30 min
        "60": 0.01      # 1% after 1 hour
    }

    # Stop loss
    stoploss = -0.015

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # Timeframe
    timeframe = '15m'

    # Startup candle count
    startup_candle_count = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators
        """
        # EMA - short and long
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=26)

        # RSI for confirmation
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume SMA for volume confirmation
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal logic
        """
        dataframe.loc[
            (
                (dataframe['ema_fast'] > dataframe['ema_slow']) &  # Fast EMA above slow
                (dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1)) &  # Crossover happened
                (dataframe['rsi'] > 40) &  # Not oversold (avoid dead cat bounce)
                (dataframe['rsi'] < 70) &  # Not overbought
                (dataframe['volume'] > dataframe['volume_sma'])  # Volume above average
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal logic
        """
        dataframe.loc[
            (
                (dataframe['ema_fast'] < dataframe['ema_slow']) &  # Fast EMA below slow
                (dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1)) &  # Cross down happened
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
