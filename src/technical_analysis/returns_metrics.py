"""Returns and risk metrics calculation module.

Calculates returns, volatility, and risk-adjusted performance metrics.
"""

import logging
from typing import Dict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ReturnsMetrics:
    """Calculate returns and risk metrics for financial time series.
    
    Provides methods to calculate:
    - Simple and log returns
    - Volatility
    - Sharpe ratio
    - Cumulative returns
    - Drawdowns
    """
    
    @staticmethod
    def simple_returns(prices: pd.Series) -> pd.Series:
        """Calculate simple (percentage) returns.
        
        Simple return = (Price_t - Price_t-1) / Price_t-1
        
        Args:
            prices (pd.Series): Price series.
            
        Returns:
            pd.Series: Simple returns.
            
        Example:
            >>> returns = ReturnsMetrics.simple_returns(df['Close'])
            >>> daily_return_pct = returns.iloc[-1] * 100  # Latest day's return
        """
        return prices.pct_change()
    
    @staticmethod
    def log_returns(prices: pd.Series) -> pd.Series:
        """Calculate logarithmic returns.
        
        Log return = ln(Price_t / Price_t-1)
        More mathematically convenient for certain analyses.
        
        Args:
            prices (pd.Series): Price series.
            
        Returns:
            pd.Series: Log returns.
            
        Example:
            >>> log_ret = ReturnsMetrics.log_returns(df['Close'])
        """
        return np.log(prices / prices.shift(1))
    
    @staticmethod
    def cumulative_returns(prices: pd.Series) -> pd.Series:
        """Calculate cumulative returns from start date.
        
        Shows total return if you bought at the first price.
        
        Args:
            prices (pd.Series): Price series.
            
        Returns:
            pd.Series: Cumulative returns (0-1 scale).
            
        Example:
            >>> cum_ret = ReturnsMetrics.cumulative_returns(df['Close'])
            >>> total_return = cum_ret.iloc[-1]  # Total return over period
            >>> return_pct = total_return * 100
        """
        return (prices / prices.iloc[0]) - 1
    
    @staticmethod
    def volatility(prices: pd.Series, period: int = 252) -> float:
        """Calculate annualized volatility (standard deviation).
        
        Args:
            prices (pd.Series): Price series.
            period (int): Trading periods per year. Default: 252 (daily).
            
        Returns:
            float: Annualized volatility (0-1 scale).
            
        Example:
            >>> vol = ReturnsMetrics.volatility(df['Close'])
            >>> vol_pct = vol * 100  # Convert to percentage
        """
        returns = ReturnsMetrics.simple_returns(prices)
        return returns.std() * np.sqrt(period)
    
    @staticmethod
    def rolling_volatility(prices: pd.Series, window: int = 30, period: int = 252) -> pd.Series:
        """Calculate rolling annualized volatility.
        
        Shows how volatility changes over time.
        
        Args:
            prices (pd.Series): Price series.
            window (int): Rolling window in days. Default: 30.
            period (int): Trading periods per year. Default: 252.
            
        Returns:
            pd.Series: Rolling volatility values.
            
        Example:
            >>> rolling_vol = ReturnsMetrics.rolling_volatility(df['Close'], window=30)
            >>> recent_vol = rolling_vol.iloc[-1]  # Latest 30-day volatility
        """
        returns = ReturnsMetrics.simple_returns(prices)
        return returns.rolling(window=window).std() * np.sqrt(period)
    
    @staticmethod
    def sharpe_ratio(prices: pd.Series, risk_free_rate: float = 0.02, period: int = 252) -> float:
        """Calculate Sharpe Ratio (return per unit of risk).
        
        Sharpe Ratio = (Return - Risk Free Rate) / Volatility
        Higher is better. Interpretation:
        - > 1: Good
        - > 2: Very Good
        - > 3: Excellent
        
        Args:
            prices (pd.Series): Price series.
            risk_free_rate (float): Annual risk-free rate. Default: 0.02 (2%).
            period (int): Trading periods per year. Default: 252.
            
        Returns:
            float: Sharpe ratio.
            
        Example:
            >>> sharpe = ReturnsMetrics.sharpe_ratio(df['Close'])
            >>> if sharpe > 1:
            ...     print("Good risk-adjusted returns")
        """
        returns = ReturnsMetrics.simple_returns(prices)
        excess_return = returns.mean() * period - risk_free_rate
        volatility = returns.std() * np.sqrt(period)
        
        if volatility == 0:
            return 0
        
        sharpe = excess_return / volatility
        return sharpe
    
    @staticmethod
    def maximum_drawdown(prices: pd.Series) -> float:
        """Calculate Maximum Drawdown (largest peak-to-trough decline).
        
        Measures the worst-case loss from a peak to trough.
        Range: 0 to -1 (or 0% to -100%)
        
        Args:
            prices (pd.Series): Price series.
            
        Returns:
            float: Maximum drawdown (negative value).
            
        Example:
            >>> max_dd = ReturnsMetrics.maximum_drawdown(df['Close'])
            >>> max_dd_pct = max_dd * 100  # Convert to percentage
            >>> print(f"Worst loss: {max_dd_pct:.2f}%")
        """
        running_max = prices.expanding().max()
        drawdown = (prices - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def drawdown_series(prices: pd.Series) -> pd.Series:
        """Calculate drawdown at each point in time.
        
        Shows the current loss from the previous peak at each date.
        
        Args:
            prices (pd.Series): Price series.
            
        Returns:
            pd.Series: Drawdown values at each date.
            
        Example:
            >>> dd = ReturnsMetrics.drawdown_series(df['Close'])
            >>> in_drawdown = dd[dd < 0]  # Filter to days in drawdown
        """
        running_max = prices.expanding().max()
        return (prices - running_max) / running_max
    
    @staticmethod
    def calmar_ratio(prices: pd.Series, period: int = 252) -> float:
        """Calculate Calmar Ratio (return divided by max drawdown).
        
        Calmar Ratio = Annual Return / Absolute Maximum Drawdown
        Higher is better. Measures return relative to risk.
        
        Args:
            prices (pd.Series): Price series.
            period (int): Trading periods per year. Default: 252.
            
        Returns:
            float: Calmar ratio.
            
        Example:
            >>> calmar = ReturnsMetrics.calmar_ratio(df['Close'])
        """
        cum_ret = ReturnsMetrics.cumulative_returns(prices).iloc[-1]
        annual_return = (1 + cum_ret) ** (period / len(prices)) - 1
        
        max_dd = abs(ReturnsMetrics.maximum_drawdown(prices))
        
        if max_dd == 0:
            return 0
        
        return annual_return / max_dd
    
    @staticmethod
    def generate_returns_report(prices: pd.Series, ticker: str) -> Dict:
        """Generate comprehensive returns and risk report.
        
        Args:
            prices (pd.Series): Price series (Close prices).
            ticker (str): Stock ticker symbol.
            
        Returns:
            Dict: Comprehensive metrics report.
            
        Example:
            >>> report = ReturnsMetrics.generate_returns_report(df['Close'], 'AAPL')
            >>> print(f"Sharpe Ratio: {report['sharpe_ratio']:.2f}")
        """
        simple_ret = ReturnsMetrics.simple_returns(prices)
        
        report = {
            'ticker': ticker,
            'period_days': len(prices),
            'start_price': float(prices.iloc[0]),
            'end_price': float(prices.iloc[-1]),
            'total_return': float(ReturnsMetrics.cumulative_returns(prices).iloc[-1]),
            'total_return_pct': float(ReturnsMetrics.cumulative_returns(prices).iloc[-1] * 100),
            'daily_returns': {
                'mean': float(simple_ret.mean()),
                'std': float(simple_ret.std()),
                'min': float(simple_ret.min()),
                'max': float(simple_ret.max()),
            },
            'volatility': float(ReturnsMetrics.volatility(prices)),
            'volatility_pct': float(ReturnsMetrics.volatility(prices) * 100),
            'sharpe_ratio': float(ReturnsMetrics.sharpe_ratio(prices)),
            'maximum_drawdown': float(ReturnsMetrics.maximum_drawdown(prices)),
            'maximum_drawdown_pct': float(ReturnsMetrics.maximum_drawdown(prices) * 100),
            'calmar_ratio': float(ReturnsMetrics.calmar_ratio(prices)),
        }
        
        return report
