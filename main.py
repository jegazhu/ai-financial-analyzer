#!/usr/bin/env python
"""Main entry point for AI Financial Analyzer.

This script orchestrates the complete data collection, validation, technical analysis, and storage pipeline.
It fetches historical price data, validates quality, calculates technical indicators, and exports results.

Usage:
    python main.py
"""

import logging
from pathlib import Path
import pandas as pd
import json

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
from src.technical_analysis import TechnicalIndicators, ReturnsMetrics
from src.utils import setup_logger


# Set up logging
logger = setup_logger(
    __name__,
    log_level=LOG_LEVEL,
    log_file='ai_financial_analyzer.log',
    log_dir=LOG_DIR
)


def remove_timezone(df: pd.DataFrame) -> pd.DataFrame:
    """Remove timezone information from datetime index for Excel compatibility.
    
    Args:
        df (pd.DataFrame): DataFrame with timezone-aware datetime index.
        
    Returns:
        pd.DataFrame: DataFrame with timezone-naive datetime index.
    """
    if hasattr(df.index, 'tz') and df.index.tz is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    return df


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


def calculate_technical_indicators(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Calculate all technical indicators for the dataset.
    
    Args:
        df (pd.DataFrame): OHLCV data.
        ticker (str): Stock ticker symbol.
        
    Returns:
        pd.DataFrame: DataFrame with added indicator columns.
    """
    logger.info(f"{ticker}: Calculating technical indicators...")
    
    df = TechnicalIndicators.add_all_indicators(df)
    
    logger.info(f"{ticker}: Added moving averages, momentum, volatility, and stochastic indicators")
    
    return df


def calculate_returns_metrics(prices: pd.Series, ticker: str) -> dict:
    """Calculate returns and risk metrics.
    
    Args:
        prices (pd.Series): Close prices.
        ticker (str): Stock ticker symbol.
        
    Returns:
        dict: Returns and risk metrics report.
    """
    logger.info(f"{ticker}: Calculating returns and risk metrics...")
    
    report = ReturnsMetrics.generate_returns_report(prices, ticker)
    
    logger.info(f"{ticker}: Total Return: {report['total_return_pct']:.2f}%")
    logger.info(f"{ticker}: Volatility: {report['volatility_pct']:.2f}%")
    logger.info(f"{ticker}: Sharpe Ratio: {report['sharpe_ratio']:.2f}")
    logger.info(f"{ticker}: Max Drawdown: {report['maximum_drawdown_pct']:.2f}%")
    
    return report


def save_data(df: pd.DataFrame, ticker: str) -> int:
    """Save data in configured formats.
    
    Args:
        df (pd.DataFrame): Historical price data with indicators.
        ticker (str): Stock ticker symbol.
        
    Returns:
        int: Number of files successfully saved.
    """
    saved_count = 0
    
    # Remove timezone for Excel compatibility
    df_for_excel = remove_timezone(df)
    
    # Save to CSV if configured
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
        csv_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.csv"
        if DataStorage.save_single(df_for_excel, csv_path, format='csv'):
            saved_count += 1
    
    # Save to Parquet if configured
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
        parquet_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.parquet"
        if DataStorage.save_single(df, parquet_path, format='parquet'):
            saved_count += 1
    
    return saved_count, df_for_excel


def main():
    """Main execution function for the complete pipeline.
    
    This function:
    1. Initializes the Yahoo Finance fetcher
    2. Fetches historical data for all configured tickers
    3. Validates data quality
    4. Calculates technical indicators
    5. Calculates returns and risk metrics
    6. Saves data in multiple formats
    7. Provides comprehensive summary
    """
    logger.info("="*80)
    logger.info("AI FINANCIAL ANALYZER - Stage 3: Technical Analysis Pipeline")
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
        
        # Process each ticker: validate, analyze, and save
        logger.info(f"Starting validation, technical analysis, and storage process...")
        
        validation_reports = {}
        quality_reports = {}
        technical_reports = {}
        returns_reports = {}
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
            
            # Calculate technical indicators
            data_with_indicators = calculate_technical_indicators(data, ticker)
            technical_reports[ticker] = data_with_indicators
            
            # Calculate returns metrics
            returns_report = calculate_returns_metrics(data['Close'], ticker)
            returns_reports[ticker] = returns_report
            
            # Save data
            save_count, df_for_excel = save_data(data_with_indicators, ticker)
            logger.info(f"{ticker}: Saved to {save_count} format(s)")
            
            # Store for Excel workbook (using timezone-naive version)
            excel_data[ticker] = df_for_excel
        
        # Save Excel workbook with all tickers
        logger.info(f"\nCreating Excel workbook with all tickers...")
        excel_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}.xlsx"
        if DataStorage.save_workbook(excel_data, excel_path):
            logger.info(f"Excel workbook saved: {excel_path}")
        
        # Save returns reports as JSON
        logger.info(f"Saving returns and risk metrics reports...")
        reports_dir = OUTPUT_DIR / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        for ticker, report in returns_reports.items():
            report_path = reports_dir / f"{ticker}_returns_report.json"
            try:
                with open(report_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Returns report saved: {report_path}")
            except Exception as e:
                logger.error(f"Failed to save returns report for {ticker}: {str(e)}")
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Tickers processed: {len(TICKERS)}")
        logger.info(f"Successful data fetches: {successful_fetches}")
        logger.info(f"Failed data fetches: {failed_fetches}")
        logger.info(f"Validation checks performed: {len(validation_reports)}")
        logger.info(f"Technical indicators calculated: {len(technical_reports)}")
        logger.info(f"Returns reports generated: {len(returns_reports)}")
        logger.info(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
        logger.info(f"\nOutput files:")
        logger.info(f"  - Excel workbook: {excel_path}")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
            logger.info(f"  - CSV files: output/{OUTPUT_FILENAME}_*.csv")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
            logger.info(f"  - Parquet files: output/{OUTPUT_FILENAME}_*.parquet")
        logger.info(f"  - Returns reports: output/reports/*_returns_report.json")
        logger.info(f"\nLogs: {LOG_DIR / 'ai_financial_analyzer.log'}")
        logger.info("="*80)
        
        return 0
    
    except Exception as e:
        logger.exception(f"Fatal error in main pipeline: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
