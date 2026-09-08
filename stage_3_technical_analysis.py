"""Stage 3: Technical Analysis

Calculates technical indicators and generates trading signals from OHLCV data.
Includes moving averages, momentum indicators, volatility metrics, and trend analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging
from config.config import LOG_LEVEL, LOG_FILENAME

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class TechnicalAnalyzer:
    """Performs technical analysis on financial time series data."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with OHLCV dataframe.
        
        Args:
            df: DataFrame with columns: Open, High, Low, Close, Volume, Adj Close
        """
        self.df = df.copy()
        self.df.index = pd.to_datetime(self.df.index)
        logger.info(f"Initialized TechnicalAnalyzer with {len(self.df)} records")
    
    def calculate_sma(self, period: int, column: str = 'Close') -> pd.Series:
        """Calculate Simple Moving Average.
        
        Args:
            period: Number of periods for SMA
            column: Column name to calculate SMA on (default: 'Close')
            
        Returns:
            Series with SMA values
        """
        return self.df[column].rolling(window=period).mean()
    
    def calculate_ema(self, period: int, column: str = 'Close') -> pd.Series:
        """Calculate Exponential Moving Average.
        
        Args:
            period: Number of periods for EMA
            column: Column name to calculate EMA on (default: 'Close')
            
        Returns:
            Series with EMA values
        """
        return self.df[column].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, period: int = 14, column: str = 'Close') -> pd.Series:
        """Calculate Relative Strength Index (RSI).
        
        Args:
            period: Number of periods (default: 14)
            column: Column name (default: 'Close')
            
        Returns:
            Series with RSI values (0-100)
        """
        delta = self.df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9,
                       column: str = 'Close') -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
            column: Column name (default: 'Close')
            
        Returns:
            DataFrame with MACD, Signal, and Histogram columns
        """
        ema_fast = self.df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df[column].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return pd.DataFrame({
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        }, index=self.df.index)
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2,
                                   column: str = 'Close') -> pd.DataFrame:
        """Calculate Bollinger Bands.
        
        Args:
            period: Number of periods for SMA (default: 20)
            std_dev: Number of standard deviations (default: 2)
            column: Column name (default: 'Close')
            
        Returns:
            DataFrame with Upper, Middle (SMA), and Lower bands
        """
        sma = self.df[column].rolling(window=period).mean()
        std = self.df[column].rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': sma,
            'Lower': lower
        }, index=self.df.index)
    
    def calculate_atr(self, period: int = 14) -> pd.Series:
        """Calculate Average True Range (volatility indicator).
        
        Args:
            period: Number of periods (default: 14)
            
        Returns:
            Series with ATR values
        """
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_stochastic(self, period: int = 14, k: int = 3, d: int = 3) -> pd.DataFrame:
        """Calculate Stochastic Oscillator.
        
        Args:
            period: Lookback period (default: 14)
            k: K-line smoothing period (default: 3)
            d: D-line smoothing period (default: 3)
            
        Returns:
            DataFrame with %K and %D lines
        """
        low_min = self.df['Low'].rolling(window=period).min()
        high_max = self.df['High'].rolling(window=period).max()
        
        fast_k = 100 * ((self.df['Close'] - low_min) / (high_max - low_min))
        slow_k = fast_k.rolling(window=k).mean()
        slow_d = slow_k.rolling(window=d).mean()
        
        return pd.DataFrame({
            '%K': slow_k,
            '%D': slow_d
        }, index=self.df.index)
    
    def calculate_volatility(self, period: int = 20) -> pd.Series:
        """Calculate historical volatility (standard deviation of returns).
        
        Args:
            period: Number of periods (default: 20)
            
        Returns:
            Series with volatility values
        """
        returns = self.df['Close'].pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        
        return volatility
    
    def calculate_roc(self, period: int = 12) -> pd.Series:
        """Calculate Rate of Change.
        
        Args:
            period: Number of periods (default: 12)
            
        Returns:
            Series with ROC values
        """
        roc = ((self.df['Close'] - self.df['Close'].shift(period)) / 
               self.df['Close'].shift(period)) * 100
        
        return roc
    
    def find_support_resistance(self, window: int = 20) -> Tuple[float, float]:
        """Identify support and resistance levels using local min/max.
        
        Args:
            window: Window size for local extrema (default: 20)
            
        Returns:
            Tuple of (support_level, resistance_level)
        """
        # Find local minima (support)
        local_min = self.df['Low'].rolling(window=window, center=True).min()
        support = local_min[local_min == self.df['Low']].max()
        
        # Find local maxima (resistance)
        local_max = self.df['High'].rolling(window=window, center=True).max()
        resistance = local_max[local_max == self.df['High']].max()
        
        return float(support), float(resistance)
    
    def calculate_all_indicators(self, sma_periods: list = None, 
                                 ema_periods: list = None) -> pd.DataFrame:
        """Calculate all major technical indicators at once.
        
        Args:
            sma_periods: List of SMA periods (default: [20, 50, 200])
            ema_periods: List of EMA periods (default: [12, 26])
            
        Returns:
            DataFrame with all indicators
        """
        if sma_periods is None:
            sma_periods = [20, 50, 200]
        if ema_periods is None:
            ema_periods = [12, 26]
        
        result = self.df.copy()
        
        # Add SMAs
        for period in sma_periods:
            result[f'SMA_{period}'] = self.calculate_sma(period)
        
        # Add EMAs
        for period in ema_periods:
            result[f'EMA_{period}'] = self.calculate_ema(period)
        
        # Add momentum indicators
        result['RSI'] = self.calculate_rsi()
        macd_df = self.calculate_macd()
        result['MACD'] = macd_df['MACD']
        result['MACD_Signal'] = macd_df['Signal']
        result['MACD_Histogram'] = macd_df['Histogram']
        
        # Add volatility indicators
        bb_df = self.calculate_bollinger_bands()
        result['BB_Upper'] = bb_df['Upper']
        result['BB_Middle'] = bb_df['Middle']
        result['BB_Lower'] = bb_df['Lower']
        result['ATR'] = self.calculate_atr()
        result['Volatility'] = self.calculate_volatility()
        
        # Add stochastic
        stoch_df = self.calculate_stochastic()
        result['Stochastic_%K'] = stoch_df['%K']
        result['Stochastic_%D'] = stoch_df['%D']
        
        # Add ROC
        result['ROC'] = self.calculate_roc()
        
        logger.info(f"Calculated {len(result.columns)} indicators")
        
        return result
    
    def generate_signals(self, method: str = 'golden_cross') -> pd.Series:
        """Generate trading signals based on technical indicators.
        
        Args:
            method: Signal generation method ('golden_cross', 'rsi', 'macd')
            
        Returns:
            Series with signal values (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=self.df.index)
        
        if method == 'golden_cross':
            # Golden Cross: SMA50 > SMA200
            sma_50 = self.calculate_sma(50)
            sma_200 = self.calculate_sma(200)
            signals = ((sma_50 > sma_200) * 1 + (sma_50 < sma_200) * -1).fillna(0)
        
        elif method == 'rsi':
            # RSI based: RSI < 30 (buy), RSI > 70 (sell)
            rsi = self.calculate_rsi()
            signals[(rsi < 30)] = 1
            signals[(rsi > 70)] = -1
        
        elif method == 'macd':
            # MACD based: MACD > Signal (buy), MACD < Signal (sell)
            macd_df = self.calculate_macd()
            signals[(macd_df['MACD'] > macd_df['Signal'])] = 1
            signals[(macd_df['MACD'] < macd_df['Signal'])] = -1
        
        return signals


def analyze_stock(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Convenience function to analyze a stock dataframe.
    
    Args:
        df: OHLCV dataframe
        ticker: Stock ticker symbol
        
    Returns:
        DataFrame with all indicators
    """
    analyzer = TechnicalAnalyzer(df)
    result = analyzer.calculate_all_indicators()
    logger.info(f"Analysis complete for {ticker}")
    return result


if __name__ == "__main__":
    # Example usage
    print("Stage 3: Technical Analysis module loaded successfully.")
