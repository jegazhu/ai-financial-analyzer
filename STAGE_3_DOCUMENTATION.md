# Stage 3: Technical Analysis

## Overview

Stage 3 adds comprehensive technical analysis capabilities to the financial analyzer. This stage builds upon the data collection and validation from Stages 1-2 by adding:

1. **Technical Indicators** - 9+ indicators for market analysis
2. **Returns & Risk Metrics** - Performance measurement and risk assessment
3. **Enhanced Reporting** - Detailed analysis reports in JSON format
4. **Indicator Integration** - Seamless calculation and storage

---

## What Was Built

### 1. Technical Indicators Module (`src/technical_analysis/indicators.py`)

#### Overview

Provides 9 major technical indicators used by traders and analysts:

#### A. Moving Averages

**Simple Moving Average (SMA)**
```python
sma_20 = TechnicalIndicators.sma(df['Close'], period=20)
sma_50 = TechnicalIndicators.sma(df['Close'], period=50)
sma_200 = TechnicalIndicators.sma(df['Close'], period=200)
```

**Purpose**: Identifies trends and support/resistance levels
- Longer periods (50, 200) show major trends
- Shorter periods (20, 50) show short-term momentum
- Golden Cross: SMA_50 crosses above SMA_200 (bullish signal)
- Death Cross: SMA_50 crosses below SMA_200 (bearish signal)

**Exponential Moving Average (EMA)**
```python
ema_12 = TechnicalIndicators.ema(df['Close'], period=12)
ema_26 = TechnicalIndicators.ema(df['Close'], period=26)
```

**Purpose**: More responsive to recent price changes than SMA
- Gives more weight to recent prices
- Better for identifying momentum
- Used as basis for MACD indicator

#### B. Momentum Indicators

**Relative Strength Index (RSI)**
```python
rsi = TechnicalIndicators.rsi(df['Close'], period=14)

# Interpretation:
# RSI > 70: Overbought (potential sell signal)
# RSI < 30: Oversold (potential buy signal)
# 30-70: Neutral zone
```

**Formula**:
```
RS = Average Gain / Average Loss
RSI = 100 - (100 / (1 + RS))
```

**Use Cases**:
- Identify overbought/oversold conditions
- Confirm trend reversals
- Divergence analysis (price makes new high but RSI doesn't)

**MACD (Moving Average Convergence Divergence)**
```python
macd_line, signal_line, histogram = TechnicalIndicators.macd(df['Close'])

# Signals:
# MACD > Signal: Bullish
# MACD < Signal: Bearish
# Histogram shows the difference (momentum)
```

**Components**:
- **MACD Line**: 12-EMA minus 26-EMA
- **Signal Line**: 9-EMA of MACD
- **Histogram**: MACD minus Signal (visual momentum)

**Trading Signals**:
- MACD crosses above signal line: Buy signal
- MACD crosses below signal line: Sell signal
- Divergence: Price and MACD move in opposite directions

#### C. Volatility Indicators

**Bollinger Bands**
```python
upper_band, middle_band, lower_band = TechnicalIndicators.bollinger_bands(df['Close'])

# Middle band = 20-SMA
# Upper/Lower = SMA ± (2 × Standard Deviation)
```

**Interpretation**:
- Price touches upper band: Potential resistance/overbought
- Price touches lower band: Potential support/oversold
- Bands widen: Increasing volatility
- Bands narrow: Decreasing volatility (potential breakout coming)

**Average True Range (ATR)**
```python
atr = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'], period=14)

# Use for position sizing:
stop_loss = df['Close'] - (2 * atr)  # 2x ATR below entry
take_profit = df['Close'] + (2 * atr)  # 2x ATR above entry
```

**Measures**: Market volatility (range of price movement)
- High ATR: High volatility, wider stop losses needed
- Low ATR: Low volatility, tighter stops can be used

**Stochastic Oscillator**
```python
k_line, d_line = TechnicalIndicators.stochastic(df['High'], df['Low'], df['Close'])

# Similar to RSI but uses High-Low range
# K > 80: Overbought
# K < 20: Oversold
```

**Purpose**: Shows position of close relative to high-low range
- More responsive than RSI
- Good for identifying extremes in range-bound markets

#### D. All-in-One Indicator Calculation

```python
# Add all indicators at once
df = TechnicalIndicators.add_all_indicators(df)

# Resulting columns:
df.columns
# ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
#  'SMA_20', 'SMA_50', 'SMA_200',
#  'EMA_12', 'EMA_26',
#  'RSI_14',
#  'MACD', 'MACD_Signal', 'MACD_Histogram',
#  'BB_Upper', 'BB_Middle', 'BB_Lower',
#  'ATR_14',
#  'Stoch_K', 'Stoch_D']
```

---

### 2. Returns & Risk Metrics Module (`src/technical_analysis/returns_metrics.py`)

#### A. Return Calculations

**Simple Returns**
```python
returns = ReturnsMetrics.simple_returns(df['Close'])
# Formula: (Price_t - Price_t-1) / Price_t-1
# Shows percentage gain/loss each day
```

**Log Returns**
```python
log_returns = ReturnsMetrics.log_returns(df['Close'])
# Formula: ln(Price_t / Price_t-1)
# Mathematically convenient for analysis
```

**Cumulative Returns**
```python
cum_returns = ReturnsMetrics.cumulative_returns(df['Close'])
# Shows total return from start to each date
# If cum_return = 0.25, means 25% total gain
```

#### B. Volatility & Risk Metrics

**Volatility (Annualized)**
```python
vol = ReturnsMetrics.volatility(df['Close'])
# Measured as annualized standard deviation of returns
# vol = 0.25 means 25% annualized volatility
# Higher volatility = riskier investment
```

**Rolling Volatility**
```python
rolling_vol = ReturnsMetrics.rolling_volatility(df['Close'], window=30)
# Shows how volatility changes over time
# Useful for detecting market stress periods
```

**Sharpe Ratio**
```python
sharpe = ReturnsMetrics.sharpe_ratio(df['Close'])
# Sharpe = (Return - Risk-Free Rate) / Volatility
# Higher = better risk-adjusted returns
# Interpretation:
#   > 1.0: Good
#   > 2.0: Very Good
#   > 3.0: Excellent
```

**Maximum Drawdown**
```python
max_dd = ReturnsMetrics.maximum_drawdown(df['Close'])
# Largest peak-to-trough decline
# -0.30 means 30% worst-case loss from peak
```

**Drawdown Series**
```python
dd_series = ReturnsMetrics.drawdown_series(df['Close'])
# Current loss from previous peak at each point
# Useful for understanding underwater periods
```

**Calmar Ratio**
```python
calmar = ReturnsMetrics.calmar_ratio(df['Close'])
# Calmar = Annual Return / Absolute Max Drawdown
# Higher = better risk-adjusted return
```

#### C. Comprehensive Report

```python
report = ReturnsMetrics.generate_returns_report(df['Close'], 'AAPL')

# Returns dictionary with:
report = {
    'ticker': 'AAPL',
    'period_days': 756,
    'start_price': 150.42,
    'end_price': 228.65,
    'total_return': 0.5203,  # 52.03%
    'total_return_pct': 52.03,
    'daily_returns': {
        'mean': 0.0008,
        'std': 0.0185,
        'min': -0.0847,
        'max': 0.0924,
    },
    'volatility': 0.2945,  # 29.45% annualized
    'volatility_pct': 29.45,
    'sharpe_ratio': 1.75,
    'maximum_drawdown': -0.3234,  # -32.34%
    'maximum_drawdown_pct': -32.34,
    'calmar_ratio': 1.61,
}
```

---

## Technical Analysis Architecture

```
┌──────────────────────────────────────────────────────────┐
│              DATA COLLECTION & VALIDATION                │
│         (From Stages 1 & 2: OHLCV Data)                  │
└─────────────────────────────┬──────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────┐
│           TECHNICAL ANALYSIS LAYER (STAGE 3)            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Moving Averages:                                   │  │
│  │  • SMA_20, SMA_50, SMA_200                         │  │
│  │  • EMA_12, EMA_26                                 │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Momentum Indicators:                               │  │
│  │  • RSI_14 (Overbought/Oversold)                    │  │
│  │  • MACD, MACD_Signal, MACD_Histogram              │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Volatility Indicators:                             │  │
│  │  • Bollinger Bands (Upper, Middle, Lower)         │  │
│  │  • ATR_14 (Average True Range)                     │  │
│  │  • Stoch_K, Stoch_D (Stochastic)                  │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Returns & Risk Metrics:                            │  │
│  │  • Total Return, Daily Returns                     │  │
│  │  • Volatility (Annualized)                         │  │
│  │  • Sharpe Ratio, Calmar Ratio                      │  │
│  │  • Maximum Drawdown, Drawdown Series               │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────┬──────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────┐
│                    STORAGE & REPORTING                    │
│  • Excel with all indicators and prices                   │
│  • CSV files with full analysis                           │
│  • JSON reports with risk metrics                         │
│  • Detailed logs of all calculations                      │
└──────────────────────────────────────────────────────────┘
```

---

## Indicator Formulas

### Moving Averages

**SMA (Simple Moving Average)**
```
SMA = (P1 + P2 + ... + Pn) / n
```

**EMA (Exponential Moving Average)**
```
Multiplier = 2 / (n + 1)
EMA = (Close - Previous_EMA) × Multiplier + Previous_EMA
```

### Momentum

**RSI (Relative Strength Index)**
```
Average Gain = Sum of gains over period / period
Average Loss = Sum of losses over period / period
RS = Average Gain / Average Loss
RSI = 100 - (100 / (1 + RS))
```

**MACD**
```
MACD_Line = EMA_12 - EMA_26
Signal_Line = EMA_9(MACD_Line)
Histogram = MACD_Line - Signal_Line
```

### Volatility

**Bollinger Bands**
```
Middle_Band = SMA_20(Close)
Std_Dev = Standard_Deviation(Close, 20)
Upper_Band = Middle_Band + (2 × Std_Dev)
Lower_Band = Middle_Band - (2 × Std_Dev)
```

**ATR (Average True Range)**
```
True_Range = max(High - Low, |High - Previous_Close|, |Low - Previous_Close|)
ATR = Simple_Moving_Average(True_Range, 14)
```

### Risk Metrics

**Sharpe Ratio**
```
Sharpe = (Annual_Return - Risk_Free_Rate) / Annual_Volatility
```

**Calmar Ratio**
```
Calmar = Annual_Return / Absolute_Maximum_Drawdown
```

**Maximum Drawdown**
```
DD = (Trough_Value - Peak_Value) / Peak_Value
Max_DD = Minimum(DD) over entire period
```

---

## How to Use Stage 3

### Basic Usage

```bash
python main.py
```

### What Gets Calculated

For each stock ticker:

1. **Technical Indicators** (20 columns added)
   - Moving averages (5)
   - Momentum indicators (4)
   - Volatility indicators (6)
   - Returns metrics (calculated internally)

2. **Returns Reports** (JSON files)
   - Total return percentage
   - Daily return statistics
   - Annualized volatility
   - Risk-adjusted returns (Sharpe, Calmar)
   - Maximum drawdown

### Output Files

**Excel File** (with indicators):
```
output/historical_prices.xlsx
├── AAPL (756 rows × 26 columns)
│   └── Open, High, Low, Close, Volume, Adj Close,
│       SMA_20, SMA_50, SMA_200, EMA_12, EMA_26,
│       RSI_14, MACD, MACD_Signal, MACD_Histogram,
│       BB_Upper, BB_Middle, BB_Lower, ATR_14,
│       Stoch_K, Stoch_D
├── MSFT
├── GOOGL
└── ... (other tickers)
```

**CSV Files** (with indicators):
```
output/historical_prices_AAPL.csv
output/historical_prices_MSFT.csv
...
```

**Returns Reports** (JSON):
```
output/reports/AAPL_returns_report.json
output/reports/MSFT_returns_report.json
...
```

### Example Returns Report

```json
{
  "ticker": "AAPL",
  "period_days": 756,
  "start_price": 150.42,
  "end_price": 228.65,
  "total_return": 0.5203,
  "total_return_pct": 52.03,
  "daily_returns": {
    "mean": 0.0008,
    "std": 0.0185,
    "min": -0.0847,
    "max": 0.0924
  },
  "volatility": 0.2945,
  "volatility_pct": 29.45,
  "sharpe_ratio": 1.75,
  "maximum_drawdown": -0.3234,
  "maximum_drawdown_pct": -32.34,
  "calmar_ratio": 1.61
}
```

---

## Trading Signal Examples

### Golden Cross Strategy
```python
df['Golden_Cross'] = (
    (df['SMA_50'] > df['SMA_200']) & 
    (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1))
)
# Buy signal when 50-SMA crosses above 200-SMA
```

### RSI Overbought/Oversold
```python
df['RSI_Buy'] = df['RSI_14'] < 30
df['RSI_Sell'] = df['RSI_14'] > 70
```

### MACD Crossover
```python
df['MACD_Buy'] = (
    (df['MACD'] > df['MACD_Signal']) & 
    (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
)
df['MACD_Sell'] = (
    (df['MACD'] < df['MACD_Signal']) & 
    (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
)
```

### Bollinger Bands Breakout
```python
df['BB_Breakout_Up'] = df['Close'] > df['BB_Upper']
df['BB_Breakout_Down'] = df['Close'] < df['BB_Lower']
```

---

## Performance Interpretation

### Return Levels
- **> 50%**: Excellent
- **20-50%**: Very Good
- **10-20%**: Good
- **5-10%**: Acceptable
- **< 5%**: Underperforming

### Volatility Levels
- **< 15%**: Low (stable stocks, bonds)
- **15-25%**: Medium (typical stocks)
- **25-40%**: High (growth stocks, crypto-adjacent)
- **> 40%**: Very High (speculative, risky)

### Sharpe Ratio Interpretation
- **< 0**: Losing money risk-adjusted
- **0-1**: Poor risk-adjusted returns
- **1-2**: Good risk-adjusted returns
- **2-3**: Very good risk-adjusted returns
- **> 3**: Exceptional risk-adjusted returns

### Maximum Drawdown
- **< -10%**: Minimal drawdown (stable)
- **-10% to -20%**: Moderate drawdown
- **-20% to -40%**: Significant drawdown
- **> -40%**: Severe drawdown (high risk)

---

## Technical Analysis Strategies

### Trend Following
```python
# Use moving average crossovers
trend_up = df['EMA_12'] > df['EMA_26']
trend_down = df['EMA_12'] < df['EMA_26']
```

### Mean Reversion
```python
# Use Bollinger Bands and RSI
oversold = (df['RSI_14'] < 30) & (df['Close'] < df['BB_Lower'])
overbought = (df['RSI_14'] > 70) & (df['Close'] > df['BB_Upper'])
```

### Momentum
```python
# Use MACD and Stochastic
momentum_up = (df['MACD'] > df['MACD_Signal']) & (df['Stoch_K'] > 50)
momentum_down = (df['MACD'] < df['MACD_Signal']) & (df['Stoch_K'] < 50)
```

### Volatility Trading
```python
# Use ATR and Bollinger Bands width
volatility_expanding = df['BB_Upper'] - df['BB_Lower'] > df['ATR_14']
```

---

## Testing Stage 3

### Verify Indicators Are Calculated

```python
import pandas as pd
from src.data_storage import DataStorage

# Load the Excel file with indicators
df = pd.read_excel('output/historical_prices.xlsx', sheet_name='AAPL')

# Check indicator columns exist
print("Indicator columns:")
for col in df.columns:
    if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
        print(f"  ✓ {col}")

# Check for NaN values (should be minimal)
print(f"\nMissing values in indicators:")
for col in df.columns:
    nan_count = df[col].isna().sum()
    if nan_count > 0:
        print(f"  {col}: {nan_count} NaN values")
```

### Verify Returns Report

```python
import json

# Load returns report
with open('output/reports/AAPL_returns_report.json') as f:
    report = json.load(f)

print(f"Ticker: {report['ticker']}")
print(f"Total Return: {report['total_return_pct']:.2f}%")
print(f"Volatility: {report['volatility_pct']:.2f}%")
print(f"Sharpe Ratio: {report['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {report['maximum_drawdown_pct']:.2f}%")
print(f"Calmar Ratio: {report['calmar_ratio']:.2f}")
```

---

## Learning Outcomes

Completing Stage 3 demonstrates:

✅ **Technical Analysis Knowledge** - Understanding of 9+ indicators
✅ **Time Series Analysis** - Working with financial time series data
✅ **Quantitative Finance** - Risk metrics and return calculations
✅ **Data Enhancement** - Adding derived features to raw data
✅ **Performance Reporting** - Comprehensive financial reporting
✅ **Financial Python** - Implementing financial formulas in code
✅ **Data Visualization Preparation** - Data ready for charting (next stage)

---

## Next Steps (Stage 4)

Stage 4: **Fundamental Analysis**
- Extract and analyze financial statements
- Calculate financial ratios (P/E, debt-to-equity, ROE, etc.)
- Compare companies by metrics
- Create valuation models
- Document: Financial metrics and valuation methodology

---

## Common Issues & Solutions

### Issue: NaN values in indicators
**Cause**: Initial periods need data to calculate (e.g., SMA_20 needs 20 days)
**Solution**: Drop first N rows or use `skipna=True`
```python
df = df.iloc[200:]  # Skip first 200 rows with NaN
```

### Issue: Sharpe ratio is negative
**Cause**: Stock lost money over the period
**Solution**: Check if investment was profitable overall
```python
if report['total_return'] < 0:
    print("Investment lost money - negative Sharpe is expected")
```

### Issue: Max drawdown seems too small
**Cause**: Stock may have had strong trend (few drawdowns)
**Solution**: Check cumulative return to confirm
```python
if report['total_return'] > 0:
    print("Strong uptrend - low drawdown is expected")
```

---

## Summary

**Stage 3 Complete!** 🎉

You now have:
- ✅ Professional technical indicators
- ✅ Comprehensive risk metrics
- ✅ Detailed financial reports
- ✅ Foundation for trading strategies
- ✅ Production-ready analysis pipeline

**Ready for Stage 4: Fundamental Analysis!**
