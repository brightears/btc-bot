"""
Bollinger Bands Mean Reversion Strategy
Buy when price touches lower band, sell when price reaches upper band or middle
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class BollingerMeanReversionFixed(IStrategy):
    """
    Mean Reversion using Bollinger Bands
    """

    # ROI table
    minimal_roi = {
        "0": 0.02,      # 2% profit target
        "15": 0.015,    # 1.5% after 15 min
        "45": 0.01      # 1% after 45 min
    }

    # Stop loss
    stoploss = -0.012

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.008
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Timeframe
    timeframe = '15m'

    # Startup candle count
    startup_candle_count = 50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators
        """
        # Bollinger Bands - Fixed to use floats
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_upper'] = bollinger['upperband']

        # Calculate bandwidth (volatility measure)
        dataframe['bb_bandwidth'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']

        # RSI for confirmation
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal logic - Buy at lower band
        """
        dataframe.loc[
            (
                (dataframe['close'] <= dataframe['bb_lower']) &  # Price at or below lower band
                (dataframe['close'] > dataframe['bb_lower'] * 0.995) &  # Not too far below
                (dataframe['rsi'] < 40) &  # Oversold confirmation
                (dataframe['bb_bandwidth'] > 0.015) &  # Sufficient volatility
                (dataframe['volume'] > dataframe['volume_sma'])  # Volume confirmation
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal logic - Sell at middle or upper band
        """
        dataframe.loc[
            (
                (
                    (dataframe['close'] >= dataframe['bb_middle']) |  # Price reached middle band
                    (dataframe['close'] >= dataframe['bb_upper'])     # or upper band
                ) &
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1

        return dataframe
