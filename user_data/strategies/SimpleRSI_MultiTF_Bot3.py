"""
Simple RSI Strategy with Multi-Timeframe Filter - Bot3 Enhancement
Buy when 5min RSI < 30 AND 15min RSI < 35 (double confirmation)
Sell when RSI > 65 (overbought)

PHASE 3 ENHANCEMENTS (Nov 5, 2025):
- Multi-timeframe: Add 15min RSI confirmation to 5min signals
- Tighter entry: RSI < 30 (from 35) - wait for deeper oversold
- Volume filter: > 1.5× rolling mean - quality over quantity
- Goal: Reduce overtrading 5.5 → 2 trades/day, win rate 50% → 55-60%

Expected Improvements:
- Frequency: 18 trades/6 days → 8-10 trades/6 days (50% reduction)
- Win rate: 50% → 55-60% (better entry quality)
- P&L: -$9.06 → +$2.50/week (eliminate fee drag)
- Fee impact: $6.60 → $2.80 (43% → 20% of P&L)
"""

from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame
import talib.abstract as ta


class SimpleRSI_MultiTF_Bot3(IStrategy):
    """
    Simple RSI-based strategy with multi-timeframe confirmation
    Reduces overtrading while maintaining edge
    """

    # Staged ROI - keep existing (working well)
    minimal_roi = {
        "0": 0.015,    # 1.5% immediate
        "30": 0.010,   # 1.0% after 30 min
        "60": 0.005,   # 0.5% after 60 min
        "120": 0.002   # 0.2% after 2 hours
    }

    # Stop loss at -2% (keep existing)
    stoploss = -0.02

    # Trailing stop loss (keep existing - works well)
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Primary timeframe
    timeframe = '5m'

    # Informative timeframes for multi-timeframe analysis
    informative_pairs = []

    # Startup candle count
    startup_candle_count = 50

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations
        """
        # Add 15min timeframe for confirmation
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, '15m') for pair in pairs]
        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate indicators for 5min timeframe
        """
        # 5min RSI (primary signal)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Volume moving average for filter
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        # Get 15min RSI for confirmation
        if self.dp:
            informative = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='15m')
            informative['rsi_15m'] = ta.RSI(informative, timeperiod=14)

            # Merge 15min data into 5min dataframe
            dataframe = merge_informative_pair(dataframe, informative, self.timeframe, '15m', ffill=True)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal logic - MULTI-TIMEFRAME with VOLUME filter

        Conditions (ALL must be true):
        1. 5min RSI < 30 (deeper oversold than before)
        2. 15min RSI < 35 (confirming oversold on higher timeframe)
        3. Volume > 1.5× 20-period mean (quality signal)

        This reduces false signals and overtrading significantly.
        """
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &                    # 5min oversold (tighter)
                (dataframe['rsi_15m'] < 35) &                # 15min confirmation
                (dataframe['volume'] > dataframe['volume_mean'] * 1.5) &  # Volume filter
                (dataframe['volume'] > 0)                     # Basic check
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal logic - UNCHANGED from original

        Exit when RSI overbought (keep existing logic)
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 65) &  # RSI overbought
                (dataframe['volume'] > 0)   # Volume check
            ),
            'exit_long'] = 1

        return dataframe
