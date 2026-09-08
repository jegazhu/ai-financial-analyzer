#!/usr/bin/env python
"""Main entry point for AI Financial Analyzer.

This script orchestrates the complete data collection, validation, and storage pipeline.
It fetches historical price data, validates quality, and exports in multiple formats.

Usage:
    python main.py
"""

import logging
from pathlib import Path
import pandas as pd

from config.config import (
    TICKERS,
    START_DATE,
    END_DATE,
    OUTPUT_DIR,
    OUTPUT_FILENAME,
    LOG_LEVEL,
    LOG_DIR,
    VALIDATION_THRESHOLD_MISSING,
    GENERATE_VALIDATION_REPORTS,
    SAVE_ALL_FORMATS,
    OUTPUT_FORMAT,
)
from src.data_collection import YahooFinanceFetcher
from src.data_validation import DataValidator, DataQualityMetrics
from src.data_storage import DataStorage
from src.utils import setup_logger


# Set up logging
logger = setup_logger(
    __name__,
    log_level=LOG_LEVEL,
    log_file='ai_financial_analyzer.log',
    log_dir=LOG_DIR
)


def validate_and_report(df: pd.DataFrame, ticker: str) -> tuple:
    """Validate data and generate quality report.
    
    Args:
        df (pd.DataFrame): Historical price data.
        ticker (str): Stock ticker symbol.
        
    Returns:
        tuple: (is_valid, validation_report, quality_report)
    """
    # Initialize validator
    validator = DataValidator(threshold_missing=VALIDATION_THRESHOLD_MISSING)
    
    # Run validation
    is_valid, validation_report = validator.validate_ohlcv_data(df, ticker)
    
    # Generate quality metrics
    quality_report = DataQualityMetrics.generate_quality_report(df, ticker)
    
    # Log results
    if is_valid:
        logger.info(f"{ticker}: ✓ All validation checks passed")
    else:
        logger.warning(f"{ticker}: ✗ Validation checks failed")
        for warning in validation_report['warnings']:
            logger.warning(f"  → {warning}")
    
    return is_valid, validation_report, quality_report


def save_data(df: pd.DataFrame, ticker: str) -> int:
    """Save data in configured formats.
    
    Args:
        df (pd.DataFrame): Historical price data.
        ticker (str): Stock ticker symbol.
        
    Returns:
        int: Number of files successfully saved.
    """
    saved_count = 0
    
    # Save to Excel
    excel_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}.xlsx"
    if not excel_path.exists():
        # Create new workbook
        pd.DataFrame().to_excel(excel_path)
    
    # For Excel, we'll build a dictionary and save all at once later
    
    # Save to CSV if configured
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
        csv_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.csv"
        if DataStorage.save_single(df, csv_path, format='csv'):
            saved_count += 1
    
    # Save to Parquet if configured
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
        parquet_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.parquet"
        if DataStorage.save_single(df, parquet_path, format='parquet'):
            saved_count += 1
    
    return saved_count


def main():
    """Main execution function for the complete pipeline.
    
    This function:
    1. Initializes the Yahoo Finance fetcher
    2. Fetches historical data for all configured tickers
    3. Validates data quality
    4. Generates quality reports
    5. Saves data in multiple formats
    6. Provides comprehensive summary
    """
    logger.info("="*80)
    logger.info("AI FINANCIAL ANALYZER - Stage 2: Data Validation & Storage Pipeline")
    logger.info("="*80)
    
    try:
        # Initialize fetcher
        logger.info(f"Initializing Yahoo Finance fetcher...")
        fetcher = YahooFinanceFetcher(max_retries=3, retry_delay=5, rate_limit_delay=0.5)
        logger.info(f"Fetcher initialized successfully")
        
        # Fetch data for all tickers
        logger.info(f"Starting data collection for {len(TICKERS)} tickers")
        logger.info(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
        
        all_data = fetcher.fetch_multiple_tickers(TICKERS, START_DATE, END_DATE)
        
        # Count successful and failed fetches
        successful_fetches = sum(1 for data in all_data.values() if data is not None)
        failed_fetches = sum(1 for data in all_data.values() if data is None)
        
        logger.info(f"Data collection complete: {successful_fetches} successful, {failed_fetches} failed")
        
        # Process each ticker: validate, report, and save
        logger.info(f"Starting validation and storage process...")
        
        validation_reports = {}
        quality_reports = {}
        excel_data = {}  # For combining into one workbook
        
        for ticker, data in all_data.items():
            if data is None:
                logger.warning(f"{ticker}: Skipped (no data available)")
                continue
            
            logger.info(f"\n--- Processing {ticker} ---")
            
            # Validate
            is_valid, val_report, qual_report = validate_and_report(data, ticker)
            validation_reports[ticker] = val_report
            quality_reports[ticker] = qual_report
            
            # Log quality metrics
            completeness = qual_report['completeness']['completeness_ratio']
            logger.info(f"{ticker}: Data completeness: {completeness:.2%}")
            logger.info(f"{ticker}: Date range: {qual_report['date_range']['start']} to {qual_report['date_range']['end']}")
            
            # Save data
            save_count = save_data(data, ticker)
            logger.info(f"{ticker}: Saved to {save_count} format(s)")
            
            # Store for Excel workbook
            excel_data[ticker] = data
        
        # Save Excel workbook with all tickers
        logger.info(f"\nCreating Excel workbook with all tickers...")
        excel_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}.xlsx"
        if DataStorage.save_workbook(excel_data, excel_path):
            logger.info(f"Excel workbook saved: {excel_path}")
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Tickers processed: {len(TICKERS)}")
        logger.info(f"Successful data fetches: {successful_fetches}")
        logger.info(f"Failed data fetches: {failed_fetches}")
        logger.info(f"Validation checks performed: {len(validation_reports)}")
        logger.info(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
        logger.info(f"\nOutput files:")
        logger.info(f"  - Excel workbook: {excel_path}")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
            logger.info(f"  - CSV files: output/{OUTPUT_FILENAME}_*.csv")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
            logger.info(f"  - Parquet files: output/{OUTPUT_FILENAME}_*.parquet")
        logger.info(f"\nLogs: {LOG_DIR / 'ai_financial_analyzer.log'}")
        logger.info("="*80)
        
        return 0
    
    except Exception as e:
        logger.exception(f"Fatal error in main pipeline: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
