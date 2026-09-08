"""Technical indicators for financial market analysis.

Provides a comprehensive set of technical indicators including:
- Moving averages (SMA, EMA)
- Momentum indicators (RSI, MACD)
- Volatility indicators (Bollinger Bands, ATR)
- Trend indicators
"""

import logging
from typing import Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for financial time series data.
    
    This class provides methods to calculate various technical indicators
    commonly used in financial analysis and trading strategies.
    """
    
    @staticmethod
    def sma(prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average (SMA).
        
        SMA is the average of prices over a specific period.
        Used to identify trends and support/resistance levels.
        
        Args:
            prices (pd.Series): Price series (typically Close prices).
            period (int): Number of periods for the moving average. Default: 20.
            
        Returns:
            pd.Series: Simple moving average values.
            
        Example:
            >>> sma_20 = TechnicalIndicators.sma(df['Close'], period=20)
            >>> sma_50 = TechnicalIndicators.sma(df['Close'], period=50)
        """
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def ema(prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average (EMA).
        
        EMA gives more weight to recent prices, making it more responsive
        to price changes than SMA. Useful for identifying momentum.
        
        Args:
            prices (pd.Series): Price series.
            period (int): Number of periods for the moving average. Default: 20.
            
        Returns:
            pd.Series: Exponential moving average values.
            
        Example:
            >>> ema_12 = TechnicalIndicators.ema(df['Close'], period=12)
            >>> ema_26 = TechnicalIndicators.ema(df['Close'], period=26)
        """
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI).
        
        RSI measures the magnitude of recent price changes to evaluate
        overbought or oversold conditions. Range: 0-100
        - RSI > 70: Overbought (potential sell signal)
        - RSI < 30: Oversold (potential buy signal)
        
        Args:
            prices (pd.Series): Price series (typically Close prices).
            period (int): Number of periods for RSI. Default: 14.
            
        Returns:
            pd.Series: RSI values (0-100).
            
        Example:
            >>> rsi = TechnicalIndicators.rsi(df['Close'], period=14)
            >>> overbought = rsi[rsi > 70]  # Potential sell signals
            >>> oversold = rsi[rsi < 30]    # Potential buy signals
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        MACD is a trend-following momentum indicator. It shows the relationship
        between two moving averages.
        
        Args:
            prices (pd.Series): Price series.
            fast (int): Fast EMA period. Default: 12.
            slow (int): Slow EMA period. Default: 26.
            signal (int): Signal line period. Default: 9.
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
            - MACD line: Difference between fast and slow EMA
            - Signal line: EMA of MACD line
            - Histogram: Difference between MACD and signal line
            
        Example:
            >>> macd, signal, histogram = TechnicalIndicators.macd(df['Close'])
            >>> buy_signals = macd[macd > signal]  # MACD crosses above signal
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands.
        
        Bollinger Bands consist of a middle band (SMA) and upper/lower bands
        (SMA +/- standard deviations). Used to identify volatility and extremes.
        
        Args:
            prices (pd.Series): Price series.
            period (int): Period for the moving average. Default: 20.
            num_std (float): Number of standard deviations. Default: 2.0.
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
            
        Example:
            >>> upper, middle, lower = TechnicalIndicators.bollinger_bands(df['Close'])
            >>> df['BB_Upper'] = upper
            >>> df['BB_Lower'] = lower
            >>> overbought = df['Close'] > upper  # Price above upper band
        """
        middle_band = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR).
        
        ATR measures market volatility by analyzing the range of price movement.
        Used for setting stop losses and position sizing.
        
        Args:
            high (pd.Series): High prices.
            low (pd.Series): Low prices.
            close (pd.Series): Close prices.
            period (int): Period for ATR. Default: 14.
            
        Returns:
            pd.Series: Average True Range values.
            
        Example:
            >>> atr = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'])
            >>> stop_loss = df['Close'] - (2 * atr)  # Set stop loss 2x ATR below price
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14, k_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator.
        
        Stochastic measures where the closing price is relative to the
        high-low range over a specific period. Range: 0-100
        
        Args:
            high (pd.Series): High prices.
            low (pd.Series): Low prices.
            close (pd.Series): Close prices.
            period (int): Lookback period. Default: 14.
            k_period (int): K smoothing period. Default: 3.
            
        Returns:
            Tuple of (k_line, d_line)
            - K line: Raw stochastic value
            - D line: Signal line (SMA of K)
            
        Example:
            >>> k, d = TechnicalIndicators.stochastic(df['High'], df['Low'], df['Close'])
            >>> oversold = k[k < 20]  # Potential buy signals
        """
        low_min = low.rolling(window=period).min()
        high_max = high.rolling(window=period).max()
        
        k_line = 100 * ((close - low_min) / (high_max - low_min))
        d_line = k_line.rolling(window=k_period).mean()
        
        return k_line, d_line
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add all common technical indicators to a DataFrame.
        
        Convenience method that adds multiple indicators at once.
        
        Args:
            df (pd.DataFrame): OHLCV DataFrame with columns: Open, High, Low, Close, Volume
            
        Returns:
            pd.DataFrame: Original DataFrame with added indicator columns.
            
        Columns added:
            - SMA_20, SMA_50, SMA_200
            - EMA_12, EMA_26
            - RSI_14
            - MACD, MACD_Signal, MACD_Histogram
            - BB_Upper, BB_Middle, BB_Lower
            - ATR_14
            - Stoch_K, Stoch_D
            
        Example:
            >>> df = TechnicalIndicators.add_all_indicators(df)
            >>> print(df.columns)  # Now includes all indicator columns
        """
        df = df.copy()
        
        # Moving Averages
        df['SMA_20'] = TechnicalIndicators.sma(df['Close'], 20)
        df['SMA_50'] = TechnicalIndicators.sma(df['Close'], 50)
        df['SMA_200'] = TechnicalIndicators.sma(df['Close'], 200)
        
        df['EMA_12'] = TechnicalIndicators.ema(df['Close'], 12)
        df['EMA_26'] = TechnicalIndicators.ema(df['Close'], 26)
        
        # Momentum
        df['RSI_14'] = TechnicalIndicators.rsi(df['Close'], 14)
        
        macd, signal, histogram = TechnicalIndicators.macd(df['Close'])
        df['MACD'] = macd
        df['MACD_Signal'] = signal
        df['MACD_Histogram'] = histogram
        
        # Volatility
        upper, middle, lower = TechnicalIndicators.bollinger_bands(df['Close'])
        df['BB_Upper'] = upper
        df['BB_Middle'] = middle
        df['BB_Lower'] = lower
        
        df['ATR_14'] = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'], 14)
        
        # Stochastic
        k, d = TechnicalIndicators.stochastic(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = k
        df['Stoch_D'] = d
        
        logger.info(f"Added {len(df.columns) - 6} technical indicators")
        
        return df
