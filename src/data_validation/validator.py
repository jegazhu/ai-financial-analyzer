"""Data validation module for financial data quality checks.

This module provides comprehensive validation of financial market data,
including checks for missing values, outliers, data consistency, and more.
"""

import logging
from typing import Dict, Tuple, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates financial data quality and completeness.
    
    Performs various checks on OHLCV data including:
    - Missing values detection
    - Outlier detection
    - Data type validation
    - Price logic validation (High >= Low, etc.)
    - Volume validation
    """
    
    def __init__(self, threshold_missing: float = 0.1):
        """Initialize the data validator.
        
        Args:
            threshold_missing (float): Maximum acceptable missing data ratio (0-1).
        """
        self.threshold_missing = threshold_missing
        logger.info(f"DataValidator initialized with missing threshold: {threshold_missing}")
    
    def validate_ohlcv_data(self, df: pd.DataFrame, ticker: str) -> Tuple[bool, Dict[str, any]]:
        """Validate complete OHLCV dataset.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data.
            ticker (str): Stock ticker symbol for logging.
            
        Returns:
            Tuple[bool, Dict]: (is_valid, validation_report)
        """
        report = {
            'ticker': ticker,
            'total_rows': len(df),
            'checks_passed': [],
            'checks_failed': [],
            'warnings': []
        }
        
        try:
            # Check 1: Missing values
            missing_check = self._check_missing_values(df, ticker)
            if missing_check['passed']:
                report['checks_passed'].append('missing_values')
            else:
                report['checks_failed'].append('missing_values')
                report['warnings'].append(missing_check['message'])
            
            # Check 2: Data types
            dtype_check = self._check_data_types(df, ticker)
            if dtype_check['passed']:
                report['checks_passed'].append('data_types')
            else:
                report['checks_failed'].append('data_types')
                report['warnings'].append(dtype_check['message'])
            
            # Check 3: Price logic (High >= Low, Close within range, etc.)
            price_check = self._check_price_logic(df, ticker)
            if price_check['passed']:
                report['checks_passed'].append('price_logic')
            else:
                report['checks_failed'].append('price_logic')
                report['warnings'].append(price_check['message'])
            
            # Check 4: Volume validation
            volume_check = self._check_volume(df, ticker)
            if volume_check['passed']:
                report['checks_passed'].append('volume')
            else:
                report['checks_failed'].append('volume')
                report['warnings'].append(volume_check['message'])
            
            # Check 5: Date index validation
            date_check = self._check_date_index(df, ticker)
            if date_check['passed']:
                report['checks_passed'].append('date_index')
            else:
                report['checks_failed'].append('date_index')
                report['warnings'].append(date_check['message'])
            
            is_valid = len(report['checks_failed']) == 0
            
            logger.info(f"{ticker}: Validation complete - "
                       f"Passed: {len(report['checks_passed'])}, "
                       f"Failed: {len(report['checks_failed'])}")
            
            return is_valid, report
        
        except Exception as e:
            logger.error(f"{ticker}: Validation error: {str(e)}")
            report['checks_failed'].append('validation_error')
            report['warnings'].append(str(e))
            return False, report
    
    def _check_missing_values(self, df: pd.DataFrame, ticker: str) -> Dict[str, any]:
        """Check for missing values in the dataset."""
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        
        passed = missing_ratio <= self.threshold_missing
        message = f"Missing values: {missing_ratio:.2%} (threshold: {self.threshold_missing:.2%})"
        
        if not passed:
            logger.warning(f"{ticker}: {message}")
        
        return {'passed': passed, 'message': message, 'ratio': missing_ratio}
    
    def _check_data_types(self, df: pd.DataFrame, ticker: str) -> Dict[str, any]:
        """Check that columns have appropriate data types."""
        expected_numeric = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        issues = []
        
        for col in df.columns:
            if col in expected_numeric:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"{col} is not numeric")
        
        passed = len(issues) == 0
        message = "; ".join(issues) if issues else "All columns have correct data types"
        
        if not passed:
            logger.warning(f"{ticker}: {message}")
        
        return {'passed': passed, 'message': message}
    
    def _check_price_logic(self, df: pd.DataFrame, ticker: str) -> Dict[str, any]:
        """Check logical relationships between OHLC prices."""
        issues = []
        
        # Check: High >= Low
        if (df['High'] < df['Low']).any():
            issues.append(f"Found {(df['High'] < df['Low']).sum()} rows where High < Low")
        
        # Check: High >= Open and Close
        if (df['High'] < df['Open']).any():
            issues.append(f"Found {(df['High'] < df['Open']).sum()} rows where High < Open")
        if (df['High'] < df['Close']).any():
            issues.append(f"Found {(df['High'] < df['Close']).sum()} rows where High < Close")
        
        # Check: Low <= Open and Close
        if (df['Low'] > df['Open']).any():
            issues.append(f"Found {(df['Low'] > df['Open']).sum()} rows where Low > Open")
        if (df['Low'] > df['Close']).any():
            issues.append(f"Found {(df['Low'] > df['Close']).sum()} rows where Low > Close")
        
        passed = len(issues) == 0
        message = "; ".join(issues) if issues else "Price logic is valid"
        
        if not passed:
            logger.warning(f"{ticker}: {message}")
        
        return {'passed': passed, 'message': message}
    
    def _check_volume(self, df: pd.DataFrame, ticker: str) -> Dict[str, any]:
        """Check volume data validity."""
        issues = []
        
        # Check: No negative volumes
        if (df['Volume'] < 0).any():
            issues.append(f"Found {(df['Volume'] < 0).sum()} rows with negative volume")
        
        # Check: Most volumes should be non-zero (allow up to 10% zero volume days)
        zero_volume_ratio = (df['Volume'] == 0).sum() / len(df)
        if zero_volume_ratio > 0.1:
            issues.append(f"High zero-volume days: {zero_volume_ratio:.2%}")
        
        passed = len(issues) == 0
        message = "; ".join(issues) if issues else "Volume data is valid"
        
        if not passed:
            logger.warning(f"{ticker}: {message}")
        
        return {'passed': passed, 'message': message}
    
    def _check_date_index(self, df: pd.DataFrame, ticker: str) -> Dict[str, any]:
        """Check date index validity."""
        issues = []
        
        # Check: Index is datetime or can be converted
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            issues.append("Index is not datetime type")
        
        # Check: Index is sorted
        if not df.index.is_monotonic_increasing:
            issues.append("Date index is not sorted chronologically")
        
        # Check: No duplicate dates
        if df.index.duplicated().any():
            issues.append(f"Found {df.index.duplicated().sum()} duplicate dates")
        
        passed = len(issues) == 0
        message = "; ".join(issues) if issues else "Date index is valid"
        
        if not passed:
            logger.warning(f"{ticker}: {message}")
        
        return {'passed': passed, 'message': message}
