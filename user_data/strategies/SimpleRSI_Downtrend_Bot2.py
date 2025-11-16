# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimpleRSI_Downtrend_Bot2(IStrategy):
    """
    SimpleRSI adapted for BTC downtrend conditions
    
    Strategy: Mean reversion on RSI oversold bounces
    Market: BTC/USDT DOWNTREND with medium volatility (2.83% daily)
    
    Key Modifications from Bot3 SimpleRSI:
    - Tighter entry (RSI < 30 vs 35) - wait for deeper oversold in downtrend
    - Faster exits (RSI > 60 vs 65) - exit earlier before trend resumes
    - Wider stop-loss (3% vs 2%) - account for 2.83% daily volatility
    - Lower ROI targets (1.2% max vs 1.5%) - realistic for downtrend bounces
    - 15m timeframe vs 5m - reduces noise in volatile downtrend
    
    Expected Performance:
    - Win Rate: 50-55% (realistic in downtrend)
    - Trades/Day: 4-6
    - Avg Win: 0.8-1.2%
    - Avg Loss: 2-3%
    - Risk/Reward: 1:2.5
    
    Deployment: Bot2 (BTC/USDT)
    Date: Nov 4, 2025
    """
    
    INTERFACE_VERSION: int = 3
    
    # ROI targets - conservative for downtrend
    minimal_roi = {
        "0": 0.012,    # 1.2% immediate (achievable in bounces)
        "30": 0.008,   # 0.8% after 30 min
        "60": 0.005,   # 0.5% after 1 hour
        "120": 0.002   # 0.2% after 2 hours
    }
    
    # Wider stoploss to handle 2.83% daily volatility
    stoploss = -0.03  # 3% max loss
    
    # Trailing stop - adjusted for lower ROI targets
    trailing_stop = True
    trailing_stop_positive = 0.008          # Start trailing at 0.8% profit
    trailing_stop_positive_offset = 0.012   # Trail by 1.2%
    trailing_only_offset_is_reached = True
    
    # 15m timeframe - reduces noise vs 5m
    timeframe = '15m'
    
    # Startup candle count
    startup_candle_count = 50
    
    # Process only new candles
    process_only_new_candles = True
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate RSI indicator
        """
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry: Wait for deeper oversold (RSI < 30) in downtrend
        """
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &  # Deeper oversold threshold
                (dataframe['volume'] > 0)   # Volume check
            ),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit: Earlier exit (RSI > 60) before downtrend resumes
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 60) &  # Earlier exit threshold
                (dataframe['volume'] > 0)   # Volume check
            ),
            'exit_long'] = 1
        return dataframe
