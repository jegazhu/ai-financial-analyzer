# Stage 2: Data Validation & Storage

## Overview

Stage 2 builds upon the data collection foundation from Stage 1 by adding:

1. **Data Validation Layer** - Comprehensive quality checks
2. **Multiple Storage Formats** - Excel, CSV, and Parquet support
3. **Quality Metrics** - Detailed data quality reporting
4. **Enhanced Pipeline** - Integrated validation and storage

---

## What Was Built

### 1. Data Validation Module (`src/data_validation/`)

#### A. `DataValidator` Class

**Purpose**: Performs comprehensive quality checks on financial data.

**Key Validations**:

```python
# 1. Missing Values Check
- Calculates percentage of missing data
- Compares against configurable threshold (default: 10%)
- Logs warnings for datasets exceeding threshold

# 2. Data Type Validation
- Ensures numeric columns contain numbers
- Validates column structure
- Flags type conversion issues

# 3. Price Logic Validation
- High >= Low (for each day)
- High >= Open and Close
- Low <= Open and Close
- Detects impossible price relationships

# 4. Volume Validation
- No negative volumes
- Checks for excessive zero-volume days
- Flags unusual volume patterns

# 5. Date Index Validation
- Ensures chronological ordering
- Detects duplicate dates
- Validates datetime format
```

**Usage Example**:
```python
from src.data_validation import DataValidator

validator = DataValidator(threshold_missing=0.1)
is_valid, report = validator.validate_ohlcv_data(df, 'AAPL')

if is_valid:
    print("Data passed all validation checks!")
else:
    print(f"Validation failed: {report['warnings']}")
```

**Output Report**:
```
{
    'ticker': 'AAPL',
    'total_rows': 756,
    'checks_passed': ['missing_values', 'data_types', 'price_logic', 'volume', 'date_index'],
    'checks_failed': [],
    'warnings': []
}
```

#### B. `DataQualityMetrics` Class

**Purpose**: Calculates and reports data quality metrics.

**Available Metrics**:

1. **Completeness**
   - Total cells, missing cells, complete cells
   - Completeness ratio (0-1)
   - Missing ratio (0-1)

2. **Numeric Statistics**
   - Min, Max, Mean, Median, Std Dev for each column
   - Helps understand data distribution

3. **Outlier Detection**
   - Uses standard deviation method (configurable threshold)
   - Identifies unusual price or volume movements
   - Default: 3 standard deviations

4. **Comprehensive Quality Report**
   - Combines all metrics into one report
   - Includes date range and row/column counts
   - Outlier counts for Close price and Volume

**Usage Example**:
```python
from src.data_validation import DataQualityMetrics

# Calculate completeness
completeness = DataQualityMetrics.calculate_completeness(df)
print(f"Data is {completeness['completeness_ratio']:.2%} complete")

# Find outliers
outliers = DataQualityMetrics.identify_outliers(df, 'Close', std_threshold=3.0)
print(f"Found {len(outliers)} outlier days")

# Generate full report
report = DataQualityMetrics.generate_quality_report(df, 'AAPL')
```

---

### 2. Data Storage Module (`src/data_storage/`)

#### `DataStorage` Class

**Purpose**: Unified interface for saving and loading data in multiple formats.

**Supported Formats**:

1. **Excel (.xlsx)**
   - Best for: Manual inspection, sharing with non-technical users
   - Advantages: Familiar format, built-in charts
   - Limitations: Large files can be slow

2. **CSV (.csv)**
   - Best for: Data exchange, simple text format
   - Advantages: Universal compatibility, human-readable
   - Limitations: No schema, no compression

3. **Parquet (.parquet)**
   - Best for: Big data, efficient storage and processing
   - Advantages: Highly compressed, fast querying, schema-aware
   - Limitations: Not human-readable, requires special tools

**Methods**:

```python
# Save single file
DataStorage.save_single(df, Path('output/AAPL.csv'), format='csv')

# Save multiple files
data_dict = {'AAPL': df_aapl, 'MSFT': df_msft}
DataStorage.save_multiple(
    data_dict, 
    Path('output'), 
    format='parquet',
    filename_prefix='historical_prices'
)

# Save to Excel workbook (multiple sheets)
DataStorage.save_workbook(
    {'AAPL': df_aapl, 'MSFT': df_msft},
    Path('output/all_stocks.xlsx')
)

# Load data
df = DataStorage.load(Path('output/AAPL.csv'))
```

---

### 3. Updated Configuration (`config/config.py`)

New settings for Stage 2:

```python
# Data Validation
VALIDATION_THRESHOLD_MISSING = 0.1      # 10% max missing data
GENERATE_VALIDATION_REPORTS = True      # Create quality reports

# Storage
SAVE_ALL_FORMATS = True                 # Save as Excel, CSV, and Parquet
OUTPUT_FORMAT = 'excel'                 # Primary format
```

---

## Data Pipeline Architecture (Stage 2)

```
┌─────────────────────────────────────────────────────────────┐
│                   DATA COLLECTION LAYER                     │
│           (Yahoo Finance via yfinance wrapper)              │
└─────────────────────────────────┬───────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   VALIDATION LAYER                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DataValidator:                                      │   │
│  │  • Missing Values Check                             │   │
│  │  • Data Type Validation                             │   │
│  │  • Price Logic Validation                           │   │
│  │  • Volume Validation                                │   │
│  │  • Date Index Validation                            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DataQualityMetrics:                                 │   │
│  │  • Completeness Analysis                            │   │
│  │  • Numeric Statistics                               │   │
│  │  • Outlier Detection                                │   │
│  │  • Quality Reports                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────┘
                                  ↓
              ┌───────────────────────────────────┐
              │    QUALITY CHECKS PASSED?         │
              │  ✓ Yes → Continue to Storage      │
              │  ✗ No  → Log Warnings & Store     │
              └───────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DataStorage:                                        │   │
│  │  • Excel (.xlsx) - Multiple sheets per workbook     │   │
│  │  • CSV (.csv) - Individual files                    │   │
│  │  • Parquet (.parquet) - Columnar format             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT FILES                              │
│  ├── output/historical_prices.xlsx                          │
│  ├── output/historical_prices_AAPL.csv                      │
│  ├── output/historical_prices_AAPL.parquet                  │
│  ├── output/historical_prices_MSFT.csv                      │
│  ├── output/historical_prices_MSFT.parquet                  │
│  └── ... (one set per ticker)                              │
│                                                             │
│  ├── logs/ai_financial_analyzer.log                         │
│  └── logs/validation_report_AAPL.json                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Schema

### Input Schema (From Yahoo Finance)

```
Column Name     | Data Type    | Description
────────────────|──────────────|─────────────────────────────────
Date (Index)    | datetime64   | Trading date (UTC)
Open            | float64      | Opening price (USD)
High            | float64      | Highest price during trading day
Low             | float64      | Lowest price during trading day
Close           | float64      | Closing price (USD)
Adj Close       | float64      | Adjusted close (splits & dividends)
Volume          | int64        | Number of shares traded
```

### Validation Rules

```
1. MISSING DATA
   Rule: Missing data ratio must be < 10%
   Severity: Warning (data still usable)
   Action: Log warning and proceed

2. DATA TYPES
   Rule: Numeric columns must be numeric types
   Severity: Error (data cannot be used)
   Action: Convert or reject data

3. PRICE LOGIC
   Rule: High >= Low (daily)
   Rule: High >= Open, Close
   Rule: Low <= Open, Close
   Severity: Error (indicates data corruption)
   Action: Flag rows and log details

4. VOLUME
   Rule: Volume >= 0
   Rule: Zero-volume days < 10% of total
   Severity: Warning (unusual but possible)
   Action: Flag and investigate

5. DATE INDEX
   Rule: Chronologically sorted
   Rule: No duplicate dates
   Rule: DateTime format
   Severity: Error (breaks time-series analysis)
   Action: Reject or reorder
```

---

## Validation Report Structure

Each validated dataset generates a report:

```json
{
  "ticker": "AAPL",
  "total_rows": 756,
  "checks_passed": [
    "missing_values",
    "data_types",
    "price_logic",
    "volume",
    "date_index"
  ],
  "checks_failed": [],
  "warnings": [],
  "completeness": {
    "total_cells": 4536,
    "missing_cells": 0,
    "complete_cells": 4536,
    "completeness_ratio": 1.0,
    "missing_ratio": 0.0
  },
  "numeric_stats": {
    "Open": {
      "min": 120.45,
      "max": 198.76,
      "mean": 155.23,
      "median": 152.10,
      "std": 18.92
    },
    "Close": {...},
    "Volume": {...}
  },
  "Close_outliers": 2,
  "Volume_outliers": 5
}
```

---

## Pipeline Flow

### Execution Steps

1. **Initialize**
   - Set up logging
   - Load configuration
   - Create directories

2. **Data Collection**
   - Fetch data for each ticker
   - Retry on failure (up to 3 times)
   - Rate limit between requests

3. **Validation**
   - Run all validation checks
   - Calculate quality metrics
   - Generate detailed reports
   - Log any issues

4. **Storage**
   - Save to all configured formats
   - Create workbook with multiple sheets
   - Preserve data integrity

5. **Summary**
   - Report statistics
   - List output files
   - Log execution time

### Pseudocode

```python
for ticker in TICKERS:
    # Step 1: Collect
    data = fetcher.fetch_historical_data(ticker, start_date, end_date)
    if data is None:
        log_error(f"Failed to fetch {ticker}")
        continue
    
    # Step 2: Validate
    validator = DataValidator(threshold_missing=0.1)
    is_valid, report = validator.validate_ohlcv_data(data, ticker)
    
    # Step 3: Quality metrics
    quality = DataQualityMetrics.generate_quality_report(data, ticker)
    
    # Step 4: Store
    if SAVE_ALL_FORMATS:
        DataStorage.save_single(data, f"output/{ticker}.csv", format='csv')
        DataStorage.save_single(data, f"output/{ticker}.parquet", format='parquet')
    
    log_summary(ticker, is_valid, len(data))
```

---

## How to Use Stage 2

### Basic Usage

```bash
python main.py
```

### Output Files Generated

**Excel Workbook** (all tickers in one file):
```
output/historical_prices.xlsx
├── Sheet: AAPL
├── Sheet: MSFT
├── Sheet: GOOGL
└── ...
```

**Individual CSV Files**:
```
output/historical_prices_AAPL.csv
output/historical_prices_MSFT.csv
output/historical_prices_GOOGL.csv
...
```

**Individual Parquet Files**:
```
output/historical_prices_AAPL.parquet
output/historical_prices_MSFT.parquet
output/historical_prices_GOOGL.parquet
...
```

**Validation Reports**:
```
logs/ai_financial_analyzer.log      # Main execution log
logs/validation_reports/            # Detailed validation reports (future)
```

### Customize Configuration

Edit `config/config.py`:

```python
# Change validation threshold
VALIDATION_THRESHOLD_MISSING = 0.05  # 5% max missing

# Only save primary format
SAVE_ALL_FORMATS = False
OUTPUT_FORMAT = 'parquet'  # Use Parquet for efficiency

# Generate additional validation reports
GENERATE_VALIDATION_REPORTS = True
```

---

## Format Comparison

| Aspect | Excel | CSV | Parquet |
|--------|-------|-----|----------|
| **File Size** | Medium | Large | Small (compressed) |
| **Speed** | Medium | Slow | Very Fast |
| **Human Readable** | Yes | Yes | No |
| **Schema Info** | No | No | Yes |
| **Good for** | Manual inspection | Data exchange | Big data |
| **Python Support** | openpyxl | built-in | pyarrow |

---

## Error Handling in Stage 2

### Scenarios & Responses

```python
# Scenario 1: Missing values exceed threshold
if missing_ratio > VALIDATION_THRESHOLD_MISSING:
    logger.warning(f"High missing data: {missing_ratio:.2%}")
    # Still proceed but flag in report

# Scenario 2: Price logic violated
if (df['High'] < df['Low']).any():
    logger.error("Data corruption detected: High < Low")
    # Flag problematic rows

# Scenario 3: File save fails
if not DataStorage.save_single(df, path):
    logger.error(f"Failed to save {path}")
    # Try alternative format or location

# Scenario 4: Empty data returned
if df.empty:
    logger.warning(f"No data for {ticker}")
    # Skip this ticker, continue with others
```

---

## Testing Stage 2

### Manual Validation Test

```python
from src.data_validation import DataValidator
from src.data_storage import DataStorage
import pandas as pd

# Create test data
test_df = pd.read_csv('output/historical_prices_AAPL.csv')

# Validate
validator = DataValidator()
is_valid, report = validator.validate_ohlcv_data(test_df, 'TEST')
assert is_valid, f"Validation failed: {report['warnings']}"

# Check quality
from src.data_validation import DataQualityMetrics
quality = DataQualityMetrics.generate_quality_report(test_df, 'TEST')
assert quality['completeness']['completeness_ratio'] >= 0.9

print("✓ All tests passed!")
```

---

## Learning Outcomes

Completing Stage 2 demonstrates:

✅ **Data Quality Assessment** - Comprehensive validation framework
✅ **Error Detection** - Identifies data issues automatically
✅ **Data Storage** - Multi-format export capabilities
✅ **Pipeline Integration** - Seamless data flow
✅ **Reporting** - Detailed quality metrics
✅ **Flexibility** - Configurable validation rules

---

## Next Steps (Stage 3)

Stage 3 will add **Technical Analysis**:
- Implement technical indicators (MA, RSI, Bollinger Bands, MACD)
- Calculate returns, volatility, Sharpe ratio
- Generate trading signals
- Document: Technical analysis methodology

---

## Troubleshooting

### Issue: "Parquet requires pyarrow"
**Solution**: Run `pip install pyarrow`

### Issue: "Validation failed: High < Low detected"
**Solution**: Check data quality with Yahoo Finance; may indicate stock split

### Issue: "CSV files are huge"
**Solution**: Use Parquet format instead (much smaller compressed files)

### Issue: "Multiple formats slow down execution"
**Solution**: Set `SAVE_ALL_FORMATS = False` and keep only one format

---

## Summary

**Stage 2 Complete!** 🎉

You now have:
- ✅ Robust data validation
- ✅ Multi-format storage
- ✅ Quality metrics reporting
- ✅ Production-ready pipeline

**Ready for Stage 3: Technical Analysis!**
