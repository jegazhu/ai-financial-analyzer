"""Configuration settings for AI Financial Analyzer.

This module centralizes all configuration parameters for the financial data pipeline.
Modify these settings to customize the behavior of the application.
"""

import datetime
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA COLLECTION SETTINGS
# ============================================================================

# List of stock tickers to analyze
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'TSM', 'TCEHY', 'ASML', 'ORCL']

# Date range for historical data
# Convert Unix timestamps to datetime objects
START_DATE = datetime.datetime.fromtimestamp(1672617540)  # 2023-01-02
END_DATE = datetime.datetime.fromtimestamp(1788998340)    # 2026-09-09

# Interval for data download
INTERVAL = '1d'  # Daily data

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# Output file format
OUTPUT_FORMAT = 'excel'  # Options: 'excel', 'csv', 'parquet'

# Output filename
OUTPUT_FILENAME = 'historical_prices'

# Whether to save in multiple formats
SAVE_ALL_FORMATS = True  # Save as Excel, CSV, and Parquet

# ============================================================================
# DATA VALIDATION SETTINGS
# ============================================================================

# Maximum acceptable missing data ratio (0-1)
VALIDATION_THRESHOLD_MISSING = 0.1

# Generate validation reports
GENERATE_VALIDATION_REPORTS = True

# ============================================================================
# RETRY SETTINGS
# ============================================================================

# Number of retry attempts for failed API calls
MAX_RETRIES = 3

# Delay between retries (in seconds)
RETRY_DELAY = 5

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# Log filename
LOG_FILENAME = 'ai_financial_analyzer.log'

# Whether to include timestamps in console output
LOG_INCLUDE_TIMESTAMP = True

# ============================================================================
# API SETTINGS
# ============================================================================

# Rate limiting delay between API calls (in seconds)
RATE_LIMIT_DELAY = 0.5
