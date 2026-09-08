#!/usr/bin/env python
"""Main entry point for AI Financial Analyzer.

This script orchestrates the complete data collection, validation, technical analysis,
fundamental analysis, and storage pipeline.

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
from src.fundamental_analysis import FinancialStatements, FinancialRatios, ValuationMetrics
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
    validator = DataValidator(threshold_missing=VALIDATION_THRESHOLD_MISSING)
    is_valid, validation_report = validator.validate_ohlcv_data(df, ticker)
    quality_report = DataQualityMetrics.generate_quality_report(df, ticker)
    
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
    logger.info(f"{ticker}: Technical indicators calculated")
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
    return report


def get_fundamental_analysis(ticker: str) -> dict:
    """Get fundamental analysis data.
    
    Args:
        ticker (str): Stock ticker symbol.
        
    Returns:
        dict: Fundamental analysis results.
    """
    logger.info(f"{ticker}: Fetching financial statements...")
    
    fundamental = {
        'financial_statements': {},
        'financial_ratios': {},
        'valuation': {},
    }
    
    try:
        # Get financial statements
        statements = FinancialStatements.get_all_statements(ticker, quarterly=False)
        
        if statements['income_statement'] is not None and statements['balance_sheet'] is not None:
            # Generate ratio report
            ratio_report = FinancialRatios.generate_ratio_report(
                ticker,
                statements['income_statement'],
                statements['balance_sheet'],
                statements['cashflow'] if statements['cashflow'] is not None else pd.DataFrame()
            )
            fundamental['financial_ratios'] = ratio_report
            logger.info(f"{ticker}: Financial ratios calculated")
        
        # Get valuation metrics
        valuation_report = ValuationMetrics.generate_valuation_report(ticker)
        fundamental['valuation'] = valuation_report
        logger.info(f"{ticker}: Valuation metrics calculated")
        
    except Exception as e:
        logger.warning(f"{ticker}: Fundamental analysis failed: {str(e)}")
    
    return fundamental


def save_data(df: pd.DataFrame, ticker: str) -> int:
    """Save data in configured formats.
    
    Args:
        df (pd.DataFrame): Historical price data with indicators.
        ticker (str): Stock ticker symbol.
        
    Returns:
        int: Number of files successfully saved.
    """
    saved_count = 0
    df_for_excel = remove_timezone(df)
    
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
        csv_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.csv"
        if DataStorage.save_single(df_for_excel, csv_path, format='csv'):
            saved_count += 1
    
    if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
        parquet_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}_{ticker}.parquet"
        if DataStorage.save_single(df, parquet_path, format='parquet'):
            saved_count += 1
    
    return saved_count, df_for_excel


def main():
    """Main execution function for the complete pipeline.
    
    This function orchestrates:
    1. Data collection
    2. Data validation
    3. Technical analysis
    4. Fundamental analysis
    5. Storage in multiple formats
    """
    logger.info("="*80)
    logger.info("AI FINANCIAL ANALYZER - Stage 4: Fundamental Analysis Pipeline")
    logger.info("="*80)
    
    try:
        # Initialize fetcher
        logger.info(f"Initializing Yahoo Finance fetcher...")
        fetcher = YahooFinanceFetcher(max_retries=3, retry_delay=5, rate_limit_delay=0.5)
        logger.info(f"Fetcher initialized successfully")
        
        # Fetch data for all tickers
        logger.info(f"Starting data collection for {len(TICKERS)} tickers")
        all_data = fetcher.fetch_multiple_tickers(TICKERS, START_DATE, END_DATE)
        
        successful_fetches = sum(1 for data in all_data.values() if data is not None)
        failed_fetches = sum(1 for data in all_data.values() if data is None)
        
        logger.info(f"Data collection complete: {successful_fetches} successful, {failed_fetches} failed")
        logger.info(f"Starting comprehensive analysis pipeline...")
        
        validation_reports = {}
        quality_reports = {}
        technical_reports = {}
        returns_reports = {}
        fundamental_reports = {}
        excel_data = {}
        
        for ticker, data in all_data.items():
            if data is None:
                logger.warning(f"{ticker}: Skipped (no data available)")
                continue
            
            logger.info(f"\n--- Processing {ticker} ---")
            
            # Stage 2: Validate
            is_valid, val_report, qual_report = validate_and_report(data, ticker)
            validation_reports[ticker] = val_report
            quality_reports[ticker] = qual_report
            
            # Stage 3: Technical Analysis
            data_with_indicators = calculate_technical_indicators(data, ticker)
            technical_reports[ticker] = data_with_indicators
            
            returns_report = calculate_returns_metrics(data['Close'], ticker)
            returns_reports[ticker] = returns_report
            
            # Stage 4: Fundamental Analysis
            fundamental_report = get_fundamental_analysis(ticker)
            fundamental_reports[ticker] = fundamental_report
            
            # Save data
            save_count, df_for_excel = save_data(data_with_indicators, ticker)
            logger.info(f"{ticker}: Saved to {save_count} format(s)")
            excel_data[ticker] = df_for_excel
        
        # Save Excel workbook
        logger.info(f"\nCreating Excel workbook with all tickers...")
        excel_path = OUTPUT_DIR / f"{OUTPUT_FILENAME}.xlsx"
        if DataStorage.save_workbook(excel_data, excel_path):
            logger.info(f"Excel workbook saved: {excel_path}")
        
        # Save comprehensive reports
        logger.info(f"Saving comprehensive analysis reports...")
        reports_dir = OUTPUT_DIR / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Save returns and fundamental reports
        for ticker in returns_reports.keys():
            # Returns report
            returns_path = reports_dir / f"{ticker}_returns_report.json"
            try:
                with open(returns_path, 'w') as f:
                    json.dump(returns_reports[ticker], f, indent=2)
            except Exception as e:
                logger.error(f"Failed to save returns report for {ticker}: {str(e)}")
            
            # Fundamental report
            fundamental_path = reports_dir / f"{ticker}_fundamental_report.json"
            try:
                with open(fundamental_path, 'w') as f:
                    json.dump(fundamental_reports[ticker], f, indent=2, default=str)
                logger.info(f"Fundamental report saved: {fundamental_path}")
            except Exception as e:
                logger.error(f"Failed to save fundamental report for {ticker}: {str(e)}")
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Tickers processed: {len(TICKERS)}")
        logger.info(f"Successful data fetches: {successful_fetches}")
        logger.info(f"Failed data fetches: {failed_fetches}")
        logger.info(f"Technical analyses performed: {len(technical_reports)}")
        logger.info(f"Fundamental analyses performed: {len(fundamental_reports)}")
        logger.info(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
        logger.info(f"\nOutput files:")
        logger.info(f"  - Excel workbook: {excel_path}")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'csv':
            logger.info(f"  - CSV files: output/{OUTPUT_FILENAME}_*.csv")
        if SAVE_ALL_FORMATS or OUTPUT_FORMAT == 'parquet':
            logger.info(f"  - Parquet files: output/{OUTPUT_FILENAME}_*.parquet")
        logger.info(f"  - Analysis reports: output/reports/*_returns_report.json")
        logger.info(f"  - Fundamental reports: output/reports/*_fundamental_report.json")
        logger.info(f"\nLogs: {LOG_DIR / 'ai_financial_analyzer.log'}")
        logger.info("="*80)
        
        return 0
    
    except Exception as e:
        logger.exception(f"Fatal error in main pipeline: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
