# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


# --------------------------------


class ADXMomentum_Bot1(IStrategy):
    """
    ADXMomentum strategy adapted for Bot1 (BTC/USDT)

    Original author: Gert Wohlgemuth
    Converted from: https://github.com/sthewissen/Mynt/blob/master/src/Mynt.Core/Strategies/AdxMomentum.cs

    Strategy: Multi-indicator trend-following
    - ADX (14): Trend strength (>25 = strong trend)
    - PLUS_DI/MINUS_DI (25): Directional indicators
    - SAR: Parabolic stop and reverse
    - MOM (14): Momentum oscillator

    Deployment: Bot1 (BTC/USDT)
    Date: Nov 5, 2025

    Note: Original has known issue - indicator logic may be "backwards"
    Will validate during backtesting phase.
    """

    INTERFACE_VERSION: int = 3

    # Minimal ROI designed for the strategy
    # Will be optimized during backtesting to match BTC volatility (2.42%)
    minimal_roi = {
        "0": 0.01
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.25

    # Optimal timeframe for the strategy
    timeframe = '1h'

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 20

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe, timeperiod=25)
        dataframe['minus_di'] = ta.MINUS_DI(dataframe, timeperiod=25)
        dataframe['sar'] = ta.SAR(dataframe)
        dataframe['mom'] = ta.MOM(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry: Strong uptrend detected
        - ADX > 25 (strong trend)
        - MOM > 0 (positive momentum)
        - PLUS_DI > 25 (strong buying pressure)
        - PLUS_DI > MINUS_DI (buyers dominate)
        """
        dataframe.loc[
            (
                    (dataframe['adx'] > 25) &
                    (dataframe['mom'] > 0) &
                    (dataframe['plus_di'] > 25) &
                    (dataframe['plus_di'] > dataframe['minus_di'])

            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit: Trend reversal detected
        - ADX > 25 (still strong trend but reversing)
        - MOM < 0 (negative momentum)
        - MINUS_DI > 25 (strong selling pressure)
        - MINUS_DI > PLUS_DI (sellers dominate)
        """
        dataframe.loc[
            (
                    (dataframe['adx'] > 25) &
                    (dataframe['mom'] < 0) &
                    (dataframe['minus_di'] > 25) &
                    (dataframe['plus_di'] < dataframe['minus_di'])

            ),
            'exit_long'] = 1
        return dataframe
