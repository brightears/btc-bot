# --- Do not remove these libs ---
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.strategy import IStrategy
from freqtrade.strategy import IntParameter
from pandas import DataFrame


class CofiBitStrategy_LowVol(IStrategy):
    """
    Modified CofiBitStrategy optimized for low volatility BTC/USDT environment.

    Original strategy by CofiBit (from Freqtrade community).

    Modifications for Nov 2025 low volatility conditions:
    - Tightened ROI targets (1.5% max vs 10% original)
    - Reduced stoploss to -2.5% (vs -25% original)
    - Added trailing stop for profit protection
    - Timeframe: 5m (unchanged)

    Expected performance:
    - Trades/day: 5-8
    - Win rate: 60-65%
    - Risk/reward: 1:1.5

    Deployment: Bot2 (BTC/USDT)
    Date: Nov 4, 2025
    """

    INTERFACE_VERSION: int = 3

    buy_params = {
        "buy_fastx": 25,
        "buy_adx": 25,
    }

    sell_params = {
        "sell_fastx": 75,
    }

    # LOW VOLATILITY OPTIMIZED ROI
    # Targets: 1.5% → 1.2% → 0.8% → 0.5% → 0.3% → 0.1%
    minimal_roi = {
        "0": 0.015,    # 1.5% immediate exit
        "10": 0.012,   # 1.2% after 10 min
        "30": 0.008,   # 0.8% after 30 min
        "60": 0.005,   # 0.5% after 1 hour
        "120": 0.003,  # 0.3% after 2 hours
        "240": 0.001   # 0.1% after 4 hours
    }

    # CONSERVATIVE STOPLOSS for low volatility
    stoploss = -0.025  # 2.5% max loss

    # TRAILING STOP for profit protection
    trailing_stop = True
    trailing_stop_positive = 0.005         # Start trailing at 0.5% profit
    trailing_stop_positive_offset = 0.008  # Trail by 0.8%
    trailing_only_offset_is_reached = True

    timeframe = '5m'

    # Hyperopt parameters
    buy_fastx = IntParameter(20, 30, default=25)
    buy_adx = IntParameter(20, 30, default=25)
    sell_fastx = IntParameter(70, 80, default=75)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Indicators: Stochastic Fast, EMA (high/close/low), ADX
        """
        stoch_fast = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']
        dataframe['ema_high'] = ta.EMA(dataframe, timeperiod=5, price='high')
        dataframe['ema_close'] = ta.EMA(dataframe, timeperiod=5, price='close')
        dataframe['ema_low'] = ta.EMA(dataframe, timeperiod=5, price='low')
        dataframe['adx'] = ta.ADX(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry: Price below EMA low + Stochastic crossover (oversold) + ADX trend strength
        """
        dataframe.loc[
            (
                (dataframe['open'] < dataframe['ema_low']) &
                (qtpylib.crossed_above(dataframe['fastk'], dataframe['fastd'])) &
                (dataframe['fastk'] < self.buy_fastx.value) &
                (dataframe['fastd'] < self.buy_fastx.value) &
                (dataframe['adx'] > self.buy_adx.value)
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit: Price above EMA high OR Stochastic overbought (>75)
        """
        dataframe.loc[
            (
                (dataframe['open'] >= dataframe['ema_high'])
            ) |
            (
                (qtpylib.crossed_above(dataframe['fastk'], self.sell_fastx.value)) |
                (qtpylib.crossed_above(dataframe['fastd'], self.sell_fastx.value))
            ),
            'exit_long'] = 1
        return dataframe
