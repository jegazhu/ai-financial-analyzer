"""Data storage module with support for multiple formats.

Provides unified interface for storing data in Excel, CSV, and Parquet formats.
"""

import logging
from typing import Optional
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles data storage in multiple formats.
    
    Supports:
    - Excel (.xlsx)
    - CSV (.csv)
    - Parquet (.parquet)
    """
    
    SUPPORTED_FORMATS = ['excel', 'csv', 'parquet']
    
    @staticmethod
    def save_single(df: pd.DataFrame, path: Path, format: str = 'excel') -> bool:
        """Save a single DataFrame to file.
        
        Args:
            df (pd.DataFrame): DataFrame to save.
            path (Path): File path to save to.
            format (str): Output format ('excel', 'csv', 'parquet').
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if format not in DataStorage.SUPPORTED_FORMATS:
            logger.error(f"Unsupported format: {format}. Supported: {DataStorage.SUPPORTED_FORMATS}")
            return False
        
        try:
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            if format == 'excel':
                df.to_excel(path)
                logger.info(f"Saved to Excel: {path}")
            elif format == 'csv':
                df.to_csv(path)
                logger.info(f"Saved to CSV: {path}")
            elif format == 'parquet':
                df.to_parquet(path)
                logger.info(f"Saved to Parquet: {path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save {path}: {str(e)}")
            return False
    
    @staticmethod
    def save_multiple(data_dict: dict, output_dir: Path, format: str = 'excel', filename_prefix: str = '') -> int:
        """Save multiple DataFrames to separate files.
        
        Args:
            data_dict (dict): Dictionary mapping names to DataFrames.
            output_dir (Path): Output directory.
            format (str): Output format.
            filename_prefix (str): Prefix for all filenames.
            
        Returns:
            int: Number of files successfully saved.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        success_count = 0
        
        for name, df in data_dict.items():
            if df is None:
                logger.warning(f"Skipping {name}: DataFrame is None")
                continue
            
            # Construct filename
            if filename_prefix:
                filename = f"{filename_prefix}_{name}.{format}"
            else:
                filename = f"{name}.{format}"
            
            filepath = output_dir / filename
            
            if DataStorage.save_single(df, filepath, format):
                success_count += 1
        
        logger.info(f"Successfully saved {success_count}/{len(data_dict)} files")
        return success_count
    
    @staticmethod
    def save_workbook(data_dict: dict, path: Path) -> bool:
        """Save multiple DataFrames to single Excel workbook (different sheets).
        
        Args:
            data_dict (dict): Dictionary mapping sheet names to DataFrames.
            path (Path): Path to Excel file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    if df is None:
                        logger.warning(f"Skipping sheet {sheet_name}: DataFrame is None")
                        continue
                    
                    # Flatten MultiIndex columns if present
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.droplevel(0)
                    
                    # Excel sheet names have a 31-character limit
                    safe_sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=safe_sheet_name)
                    logger.info(f"Saved sheet: {safe_sheet_name}")
            
            logger.info(f"Saved workbook to: {path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save workbook {path}: {str(e)}")
            return False
    
    @staticmethod
    def load(path: Path, format: str = None) -> Optional[pd.DataFrame]:
        """Load data from file.
        
        Args:
            path (Path): File path.
            format (str): Format ('excel', 'csv', 'parquet'). Auto-detect if None.
            
        Returns:
            pd.DataFrame: Loaded data, or None if failed.
        """
        try:
            if format is None:
                # Auto-detect from extension
                format = path.suffix.lower().lstrip('.')
                if format == 'xlsx':
                    format = 'excel'
            
            if format == 'excel':
                df = pd.read_excel(path)
                logger.info(f"Loaded from Excel: {path}")
            elif format == 'csv':
                df = pd.read_csv(path)
                logger.info(f"Loaded from CSV: {path}")
            elif format == 'parquet':
                df = pd.read_parquet(path)
                logger.info(f"Loaded from Parquet: {path}")
            else:
                logger.error(f"Unsupported format: {format}")
                return None
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to load {path}: {str(e)}")
            return None
