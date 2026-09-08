"""Data quality metrics calculation module.

Provides methods to calculate and report data quality metrics for financial datasets.
"""

import logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class DataQualityMetrics:
    """Calculates and reports data quality metrics.
    
    Generates comprehensive quality reports including:
    - Completeness (missing data percentage)
    - Accuracy (data anomalies)
    - Consistency (logical relationships)
    - Timeliness (data freshness)
    """
    
    @staticmethod
    def calculate_completeness(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate data completeness metrics.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            
        Returns:
            Dict with completeness statistics.
        """
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        complete_cells = total_cells - missing_cells
        
        return {
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'complete_cells': complete_cells,
            'completeness_ratio': complete_cells / total_cells if total_cells > 0 else 0,
            'missing_ratio': missing_cells / total_cells if total_cells > 0 else 0,
        }
    
    @staticmethod
    def calculate_numeric_range(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate min, max, mean, std for numeric columns.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            
        Returns:
            Dict with statistics for each numeric column.
        """
        numeric_df = df.select_dtypes(include=['number'])
        
        stats = {}
        for col in numeric_df.columns:
            stats[col] = {
                'min': float(numeric_df[col].min()),
                'max': float(numeric_df[col].max()),
                'mean': float(numeric_df[col].mean()),
                'median': float(numeric_df[col].median()),
                'std': float(numeric_df[col].std()),
            }
        
        return stats
    
    @staticmethod
    def identify_outliers(df: pd.DataFrame, column: str, std_threshold: float = 3.0) -> List[int]:
        """Identify outliers using standard deviation method.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            column (str): Column name to check.
            std_threshold (float): Number of standard deviations for outlier detection.
            
        Returns:
            List of indices with outliers.
        """
        if column not in df.columns:
            return []
        
        mean = df[column].mean()
        std = df[column].std()
        
        outlier_indices = df[
            (df[column] < mean - std_threshold * std) | 
            (df[column] > mean + std_threshold * std)
        ].index.tolist()
        
        return outlier_indices
    
    @staticmethod
    def generate_quality_report(df: pd.DataFrame, ticker: str) -> Dict:
        """Generate comprehensive quality report.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            ticker (str): Stock ticker symbol.
            
        Returns:
            Dict with complete quality metrics.
        """
        report = {
            'ticker': ticker,
            'rows': len(df),
            'columns': len(df.columns),
            'date_range': {
                'start': str(df.index.min()) if len(df) > 0 else None,
                'end': str(df.index.max()) if len(df) > 0 else None,
            },
            'completeness': DataQualityMetrics.calculate_completeness(df),
            'numeric_stats': DataQualityMetrics.calculate_numeric_range(df),
        }
        
        # Add outlier analysis for common columns
        for col in ['Close', 'Volume']:
            if col in df.columns:
                outliers = DataQualityMetrics.identify_outliers(df, col)
                report[f'{col}_outliers'] = len(outliers)
        
        return report
