# Stage 4: Visualization & Reporting

## Overview

Stage 4 transforms technical analysis data into interactive visualizations and statistical reports. It provides two main components:

- **ChartGenerator**: Creates interactive Plotly charts and dashboards
- **ReportGenerator**: Generates statistical summaries in text and HTML formats

---

## ChartGenerator

### Purpose
Generates publication-ready visualizations for financial data and technical indicators.

### Key Methods

#### `plot_price_chart(df, ticker, title=None, save=True)`
Creates an interactive candlestick chart with technical overlays (SMA, EMA, Bollinger Bands).

**Example:**
```python
from stage_4_visualization import ChartGenerator

gen = ChartGenerator()
gen.plot_price_chart(df, "AAPL")
# Output: output/AAPL_price_chart.html
```

#### `plot_rsi_indicator(df, ticker, save=True)`
Plots RSI with overbought (70) and oversold (30) reference lines.

#### `plot_macd_indicator(df, ticker, save=True)`
Displays MACD, Signal line, and Histogram bars.

#### `plot_volatility_chart(df, ticker, save=True)`
Shows historical volatility and ATR (Average True Range).

#### `plot_comparative_returns(data_dict, tickers, save=True)`
Compares normalized returns across multiple stocks.

**Example:**
```python
data = {
    "AAPL": df_aapl,
    "MSFT": df_msft,
    "GOOGL": df_googl
}
gen.plot_comparative_returns(data, ["AAPL", "MSFT", "GOOGL"])
# Output: output/comparative_returns.html
```

### Output Format
- **Type**: Interactive HTML (Plotly)
- **Location**: `output/` directory
- **Files**: `{TICKER}_price_chart.html`, `{TICKER}_rsi.html`, etc.

---

## ReportGenerator

### Purpose
Generates statistical summaries and performance metrics.

### Key Methods

#### `generate_summary_statistics(df, ticker)`
Returns a dictionary of key metrics:

```python
{
    'Ticker': 'AAPL',
    'Period Start': Timestamp(...),
    'Period End': Timestamp(...),
    'Days': 252,
    'Starting Price': '$150.00',
    'Ending Price': '$175.50',
    'Total Return': '17.00%',
    'Average Daily Return': '0.0567%',
    'Annual Return': '14.50%',
    'Volatility (Annual)': '22.45%',
    'Sharpe Ratio': '0.65',
    'Max Drawdown': '-18.32%',
    'Highest Price': '$185.00',
    'Lowest Price': '$145.00'
}
```

#### `generate_text_report(df, ticker, save=True)`
Creates a formatted text report (.txt).

**Example:**
```python
from stage_4_visualization import ReportGenerator

gen = ReportGenerator()
report_text = gen.generate_text_report(df, "AAPL")
# Output: output/AAPL_report.txt
# Also prints formatted table
```

#### `generate_html_report(df, ticker, save=True)`
Creates a styled HTML report (.html) with statistics table.

**Example:**
```python
html = gen.generate_html_report(df, "AAPL")
# Output: output/AAPL_report.html
```

---

## Quick Start

### Single Stock Analysis
```python
from stage_1_data_retrieval import fetch_stock_data
from stage_3_technical_analysis import analyze_stock
from stage_4_visualization import visualize_stock

# Fetch and analyze
df = fetch_stock_data("AAPL", start="2023-01-01", end="2024-01-01")
df = analyze_stock(df, "AAPL")

# Generate all visualizations and reports
visualize_stock(df, "AAPL")
```

### Multiple Stocks Comparison
```python
from stage_4_visualization import ChartGenerator, ReportGenerator

tickers = ["AAPL", "MSFT", "GOOGL"]
data = {ticker: analyze_stock(fetch_stock_data(ticker), ticker) 
        for ticker in tickers}

# Create comparative chart
chart_gen = ChartGenerator()
chart_gen.plot_comparative_returns(data, tickers)

# Generate individual reports
report_gen = ReportGenerator()
for ticker in tickers:
    report_gen.generate_html_report(data[ticker], ticker)
```

---

## Key Features

### Interactive Charts
- **Zoom & Pan**: Explore data at any time scale
- **Hover Details**: See exact values on mouseover
- **Legend Toggle**: Click to show/hide indicators
- **Dark Theme**: Professional plotly_dark template

### Technical Overlays
- Moving Averages (SMA 20/50/200)
- Bollinger Bands with fill areas
- Volume analysis ready for extension
- Multiple indicator support

### Statistical Metrics
- **Return Calculations**: Total, daily, annualized
- **Risk Metrics**: Volatility, Sharpe Ratio, Max Drawdown
- **Price Levels**: High/Low, support/resistance
- **Performance Period**: Configurable date ranges

---

## Dependencies

**Required** (already in requirements.txt):
- `pandas` - Data manipulation
- `numpy` - Numerical computation

**Optional** (for visualization):
- `plotly >= 5.14.0` - Interactive charts
  - Install: `pip install plotly`

**Charts work without plotly** - gracefully degrades with warning message.

---

## Output Directory Structure

```
output/
├── AAPL_price_chart.html          # Interactive candlestick chart
├── AAPL_rsi.html                  # RSI indicator chart
├── AAPL_macd.html                 # MACD indicator chart
├── AAPL_volatility.html           # Volatility/ATR chart
├── AAPL_report.txt                # Text statistical report
├── AAPL_report.html               # HTML statistical report
├── MSFT_price_chart.html
├── ...
└── comparative_returns.html       # Multi-stock comparison chart
```

---

## Configuration

Visualization settings can be customized in `config/config.py`:

```python
# Chart dimensions (when implemented)
CHART_HEIGHT = 600
CHART_WIDTH = 1200

# Theme
THEME = "plotly_dark"  # or "plotly" for light theme

# Output location
OUTPUT_DIR = PROJECT_ROOT / "output"
```

---

## Limitations & Next Steps

### Current Limitations
- Plotly required for interactive charts
- No matplotlib export (yet)
- No PDF generation (requires additional library)
- Limited to 2D charts

### Future Enhancements
- PDF export functionality
- 3D volatility surface plots
- Real-time dashboard updates
- Custom color schemes
- Technical pattern recognition overlays
- Portfolio-level analytics

---

## Error Handling

All methods include try-except blocks with logging. Missing dependencies gracefully degrade:

```python
try:
    chart_gen.plot_price_chart(df, "AAPL")
except ImportError:
    print("Install plotly: pip install plotly")
    logger.error("Visualization skipped - plotly not installed")
```

---

## See Also

- **Stage 1**: `stage_1_data_retrieval.py` - Data fetching
- **Stage 2**: `stage_2_data_parsing.py` - Data cleaning  
- **Stage 3**: `stage_3_technical_analysis.py` - Indicator calculation
- **Config**: `config/config.py` - Central settings

---

**Last Updated**: September 2026  
**Version**: 1.0.0
