# AI Financial Analyzer

**AI-powered financial data collection, analysis, and visualization pipeline. Automates retrieval and analysis of stock market data from Yahoo Finance.**

---

## 📋 Overview

This project provides a comprehensive framework for automated financial market data retrieval, processing, and analysis using Python. It leverages the `yfinance` library as a programmatic bridge to Yahoo Finance, enabling:

- **Historical Price Analysis**: OHLCV (Open, High, Low, Close, Volume) data retrieval
- **Fundamental Valuation**: Financial statements, balance sheets, and valuation metrics
- **Corporate Actions**: Dividend tracking, stock splits, and capital distributions
- **Derivatives & Volatility**: Option chains, strike prices, and implied volatility surfaces

---

## 🎯 Problem Statement

Manual collection of financial data is:
- **Time-consuming** and inefficient
- **Error-prone** and inconsistent
- **Hindering** timely investment analysis
- **Limiting** scalability for portfolio monitoring

This solution automates the entire data pipeline, enabling reproducible and scalable financial analysis.

---

## 🏗️ Architecture

### Stage 1: Data Retrieval (`stage_1_data_retrieval.py`)
- Fetches historical price data for multiple securities
- Retrieves fundamental company metrics
- Caches data for efficiency
- Handles API rate limits and errors gracefully

### Stage 2: Data Parsing & Cleaning (`stage_2_data_parsing.py`)
- Validates OHLCV data integrity
- Normalizes financial statements
- Handles missing values and outliers
- Converts raw data into analysis-ready formats

### Stage 3: Technical Analysis (`stage_3_technical_analysis.py`)
- Calculates moving averages (SMA, EMA)
- Computes volatility metrics (standard deviation, ATR)
- Identifies support/resistance levels
- Generates trend and momentum indicators

### Stage 4: Visualization & Reporting (`stage_4_visualization.py`)
- Creates interactive price charts with technical overlays
- Generates comparative performance dashboards
- Produces statistical summary reports
- Exports analysis results to multiple formats

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

```bash
# Clone the repository
git clone https://github.com/jegazhu/ai-financial-analyzer.git
cd ai-financial-analyzer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `yfinance` - Yahoo Finance data retrieval
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `matplotlib` - Static visualizations
- `plotly` - Interactive visualizations
- `scikit-learn` - Statistical analysis (optional)

---

## 🚀 Quick Start

### Basic Usage

```python
from stage_1_data_retrieval import fetch_stock_data
from stage_3_technical_analysis import calculate_technical_indicators
from stage_4_visualization import plot_price_chart

# Fetch data
ticker = "AAPL"
df = fetch_stock_data(ticker, start="2023-01-01", end="2024-01-01")

# Calculate indicators
df = calculate_technical_indicators(df)

# Visualize
plot_price_chart(df, ticker)
```

### Analyzing Multiple Stocks

```python
from stage_1_data_retrieval import fetch_multiple_stocks
from stage_4_visualization import plot_comparative_analysis

tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
data = fetch_multiple_stocks(tickers, start="2023-01-01")

plot_comparative_analysis(data, tickers)
```

---

## 📊 Example Outputs

### Price Charts with Technical Indicators
- Interactive candlestick charts with moving averages
- Bollinger Bands and volume analysis
- Support/resistance level identification

### Performance Dashboards
- Multi-stock comparative returns
- Risk-adjusted performance metrics
- Correlation matrices

### Statistical Reports
- Descriptive statistics (mean, std dev, skewness, kurtosis)
- Maximum drawdown and Sharpe ratio calculations
- Volatility analysis by time period

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Data retrieval settings
DEFAULT_START_DATE = "2023-01-01"
DEFAULT_END_DATE = "2024-01-01"
DATA_CACHE_DIR = "./data/cache"

# Technical analysis parameters
SMA_PERIODS = [20, 50, 200]
EMA_PERIODS = [12, 26]
BOLLINGER_BANDS_PERIOD = 20
BOLLINGER_BANDS_STD = 2

# Visualization settings
CHART_HEIGHT = 600
CHART_WIDTH = 1200
THEME = "plotly_dark"
```

---

## 📖 Detailed Documentation

### Stage 1: Data Retrieval
- Fetches real-time and historical data
- Supports multiple tickers and date ranges
- Implements caching to reduce API calls
- Error handling for invalid tickers and network issues

### Stage 2: Data Parsing
- Validates OHLCV data integrity
- Normalizes financial metrics across different sources
- Handles corporate actions (splits, dividends)
- Cleans and standardizes data formats

### Stage 3: Technical Analysis
- Moving Average convergence/divergence (MACD)
- Relative Strength Index (RSI)
- Average True Range (ATR)
- Stochastic Oscillator
- Custom technical indicators

### Stage 4: Visualization
- Interactive Plotly charts
- Static matplotlib exports
- Customizable themes and layouts
- Multi-panel dashboards

---

## 📈 Supported Analysis

| Analysis Type | Metrics | Use Case |
|---------------|---------|----------|
| **Price Action** | OHLCV, trends, support/resistance | Trend following, momentum trading |
| **Volatility** | Historical vol, ATR, Bollinger Bands | Risk management, option strategies |
| **Momentum** | RSI, MACD, Stochastic | Entry/exit signals, overbought/oversold |
| **Performance** | Returns, Sharpe ratio, max drawdown | Portfolio evaluation, risk-adjusted returns |
| **Correlation** | Cross-asset correlation | Diversification, hedging strategies |

---

## 💡 Use Cases

1. **Personal Investment Portfolio Monitoring**
   - Track multiple holdings automatically
   - Generate periodic performance reports
   - Identify rebalancing opportunities

2. **Technical Analysis & Trading Signals**
   - Automated indicator calculation
   - Chart pattern recognition
   - Trading signal generation

3. **Fundamental Analysis**
   - Extract and analyze financial statements
   - Calculate valuation multiples
   - Compare peer companies

4. **Risk Management**
   - Calculate Value-at-Risk (VaR)
   - Analyze portfolio correlation
   - Stress testing capabilities

5. **Research & Backtesting**
   - Historical data for strategy development
   - Performance attribution analysis
   - Hypothesis testing framework

---

## ⚠️ Limitations & Considerations

- **Data Source**: Limited to Yahoo Finance data availability
- **Real-time**: Historical data only (slight delay for real-time data)
- **Accuracy**: Depends on Yahoo Finance data quality
- **Rate Limiting**: Implicit rate limits on API calls
- **Corporate Actions**: May have delays in processing splits/dividends

---

## 🔄 Workflow Pipeline

```
┌─────────────────────────┐
│  Stage 1: Data Retrieval│
│  (yfinance API calls)   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Stage 2: Data Parsing  │
│  (Validation & Cleaning)│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Stage 3: Analysis      │
│  (Indicators & Metrics) │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Stage 4: Visualization │
│  (Charts & Reports)     │
└─────────────────────────┘
```

---

## 📝 Examples

### Example 1: Compare Tech Stocks
```python
import pandas as pd
from stage_1_data_retrieval import fetch_multiple_stocks
from stage_3_technical_analysis import calculate_technical_indicators

tickers = ["AAPL", "GOOGL", "MSFT"]
data = fetch_multiple_stocks(tickers, start="2023-01-01")

# Calculate returns
returns = {}
for ticker, df in data.items():
    returns[ticker] = df['Adj Close'].pct_change().mean() * 252

print("Annualized Returns:")
for ticker, ret in returns.items():
    print(f"{ticker}: {ret:.2%}")
```

### Example 2: Identify Support/Resistance
```python
from stage_3_technical_analysis import find_support_resistance

ticker = "AAPL"
df = fetch_stock_data(ticker, start="2023-01-01")

support, resistance = find_support_resistance(df)
print(f"Support Level: ${support:.2f}")
print(f"Resistance Level: ${resistance:.2f}")
```

### Example 3: Generate Trading Signals
```python
from stage_3_technical_analysis import generate_signals

df = fetch_stock_data("AAPL")
df = calculate_technical_indicators(df)

# Golden Cross signal (SMA 50 > SMA 200)
df['Signal'] = (df['SMA_50'] > df['SMA_200']).astype(int)
df['Position'] = df['Signal'].diff()

print(df[['Close', 'SMA_50', 'SMA_200', 'Position']].tail(10))
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .
flake8 .
```

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Contact & Support

- **Author**: Jega Zhu
- **Repository**: [github.com/jegazhu/ai-financial-analyzer](https://github.com/jegazhu/ai-financial-analyzer)
- **Issues**: [GitHub Issues](https://github.com/jegazhu/ai-financial-analyzer/issues)

---

## 📚 References

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Technical Analysis Libraries](https://en.wikipedia.org/wiki/Technical_analysis)
- [Plotly Documentation](https://plotly.com/python/)

---

## 🙏 Acknowledgments

- Yahoo Finance for financial data
- Open-source community for libraries and tools
- Contributors and users for feedback and improvements

---

**Last Updated**: September 2026  
**Version**: 1.0.0
