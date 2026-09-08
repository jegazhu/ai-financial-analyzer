"""Stage 4: Visualization & Reporting

Generates interactive charts, dashboards, and statistical reports from technical analysis data.
Supports multiple output formats including HTML, PNG, and PDF.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from config.config import OUTPUT_DIR, LOG_LEVEL, LOG_FILENAME

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class ChartGenerator:
    """Generates charts and visualizations from financial data."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """Initialize chart generator.
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"ChartGenerator initialized with output directory: {self.output_dir}")
    
    def _ensure_plotly(self):
        """Check if plotly is available, provide installation guidance if not."""
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            return go, px
        except ImportError:
            logger.warning("plotly not installed. Install with: pip install plotly")
            raise ImportError("Plotly required for visualization. Install with: pip install plotly")
    
    def plot_price_chart(self, df: pd.DataFrame, ticker: str,
                         title: Optional[str] = None,
                         save: bool = True) -> None:
        """Create interactive price chart with technical indicators.
        
        Args:
            df: DataFrame with OHLC and indicator data
            ticker: Stock ticker symbol
            title: Custom chart title
            save: Whether to save the chart as HTML
        """
        go, px = self._ensure_plotly()
        
        if title is None:
            title = f"{ticker} - Price Chart with Technical Indicators"
        
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
        
        # Add SMAs if available
        for col in df.columns:
            if col.startswith('SMA_'):
                period = col.split('_')[1]
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=f'SMA {period}',
                    mode='lines'
                ))
        
        # Add Bollinger Bands if available
        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                name='BB Upper',
                mode='lines',
                line=dict(dash='dash', color='rgba(255, 0, 0, 0.3)')
            ))
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                name='BB Lower',
                mode='lines',
                line=dict(dash='dash', color='rgba(255, 0, 0, 0.3)'),
                fill='tonexty',
                fillcolor='rgba(255, 0, 0, 0.1)'
            ))
        
        fig.update_layout(
            title=title,
            yaxis_title=f"{ticker} Price (USD)",
            xaxis_title="Date",
            template="plotly_dark",
            height=600,
            hovermode='x unified',
            xaxis_rangeslider_visible=False
        )
        
        if save:
            filepath = self.output_dir / f"{ticker}_price_chart.html"
            fig.write_html(str(filepath))
            logger.info(f"Price chart saved: {filepath}")
        
        return fig
    
    def plot_rsi_indicator(self, df: pd.DataFrame, ticker: str,
                          save: bool = True) -> None:
        """Create RSI (Relative Strength Index) chart.
        
        Args:
            df: DataFrame with RSI data
            ticker: Stock ticker symbol
            save: Whether to save the chart
        """
        go, px = self._ensure_plotly()
        
        if 'RSI' not in df.columns:
            logger.warning("RSI not found in dataframe")
            return
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            name='RSI',
            mode='lines',
            line=dict(color='blue')
        ))
        
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                      annotation_text="Overbought (70)")
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                      annotation_text="Oversold (30)")
        
        fig.update_layout(
            title=f"{ticker} - Relative Strength Index (RSI)",
            yaxis_title="RSI",
            xaxis_title="Date",
            template="plotly_dark",
            height=400,
            hovermode='x unified'
        )
        
        if save:
            filepath = self.output_dir / f"{ticker}_rsi.html"
            fig.write_html(str(filepath))
            logger.info(f"RSI chart saved: {filepath}")
        
        return fig
    
    def plot_macd_indicator(self, df: pd.DataFrame, ticker: str,
                           save: bool = True) -> None:
        """Create MACD (Moving Average Convergence Divergence) chart.
        
        Args:
            df: DataFrame with MACD data
            ticker: Stock ticker symbol
            save: Whether to save the chart
        """
        go, px = self._ensure_plotly()
        
        if 'MACD' not in df.columns:
            logger.warning("MACD not found in dataframe")
            return
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            name='MACD',
            mode='lines',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            name='Signal Line',
            mode='lines',
            line=dict(color='red')
        ))
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker=dict(color=['green' if x > 0 else 'red' for x in df['MACD_Histogram']])
        ))
        
        fig.update_layout(
            title=f"{ticker} - MACD",
            yaxis_title="MACD Value",
            xaxis_title="Date",
            template="plotly_dark",
            height=400,
            hovermode='x unified'
        )
        
        if save:
            filepath = self.output_dir / f"{ticker}_macd.html"
            fig.write_html(str(filepath))
            logger.info(f"MACD chart saved: {filepath}")
        
        return fig
    
    def plot_volatility_chart(self, df: pd.DataFrame, ticker: str,
                             save: bool = True) -> None:
        """Create volatility and ATR chart.
        
        Args:
            df: DataFrame with volatility/ATR data
            ticker: Stock ticker symbol
            save: Whether to save the chart
        """
        go, px = self._ensure_plotly()
        
        fig = go.Figure()
        
        if 'Volatility' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Volatility'],
                name='Historical Volatility (Annualized)',
                mode='lines',
                line=dict(color='blue')
            ))
        
        if 'ATR' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['ATR'],
                name='Average True Range (ATR)',
                mode='lines',
                line=dict(color='orange', dash='dash')
            ))
        
        fig.update_layout(
            title=f"{ticker} - Volatility Analysis",
            yaxis_title="Value",
            xaxis_title="Date",
            template="plotly_dark",
            height=400,
            hovermode='x unified'
        )
        
        if save:
            filepath = self.output_dir / f"{ticker}_volatility.html"
            fig.write_html(str(filepath))
            logger.info(f"Volatility chart saved: {filepath}")
        
        return fig
    
    def plot_comparative_returns(self, data_dict: Dict[str, pd.DataFrame],
                                 tickers: List[str],
                                 save: bool = True) -> None:
        """Create comparative returns chart for multiple stocks.
        
        Args:
            data_dict: Dictionary of {ticker: dataframe}
            tickers: List of tickers to compare
            save: Whether to save the chart
        """
        go, px = self._ensure_plotly()
        
        fig = go.Figure()
        
        for ticker in tickers:
            if ticker in data_dict:
                df = data_dict[ticker]
                returns = (df['Close'] / df['Close'].iloc[0] - 1) * 100
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=returns,
                    name=ticker,
                    mode='lines'
                ))
        
        fig.update_layout(
            title="Comparative Returns Analysis",
            yaxis_title="Return (%)",
            xaxis_title="Date",
            template="plotly_dark",
            height=600,
            hovermode='x unified'
        )
        
        if save:
            filepath = self.output_dir / "comparative_returns.html"
            fig.write_html(str(filepath))
            logger.info(f"Comparative returns chart saved: {filepath}")
        
        return fig


class ReportGenerator:
    """Generates statistical reports and summaries."""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"ReportGenerator initialized with output directory: {self.output_dir}")
    
    def generate_summary_statistics(self, df: pd.DataFrame, ticker: str) -> Dict:
        """Generate summary statistics for a stock.
        
        Args:
            df: OHLCV dataframe
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with statistical metrics
        """
        returns = df['Close'].pct_change()
        
        stats = {
            'Ticker': ticker,
            'Period Start': df.index[0],
            'Period End': df.index[-1],
            'Days': len(df),
            'Starting Price': f"${df['Close'].iloc[0]:.2f}",
            'Ending Price': f"${df['Close'].iloc[-1]:.2f}",
            'Total Return': f"{((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100:.2f}%",
            'Average Daily Return': f"{returns.mean() * 100:.4f}%",
            'Annual Return': f"{returns.mean() * 252 * 100:.2f}%",
            'Volatility (Daily)': f"{returns.std() * 100:.2f}%",
            'Volatility (Annual)': f"{returns.std() * np.sqrt(252) * 100:.2f}%",
            'Sharpe Ratio': f"{(returns.mean() / returns.std()) * np.sqrt(252):.2f}",
            'Max Drawdown': f"{self._calculate_max_drawdown(df['Close']) * 100:.2f}%",
            'Highest Price': f"${df['High'].max():.2f}",
            'Lowest Price': f"${df['Low'].min():.2f}",
        }
        
        return stats
    
    @staticmethod
    def _calculate_max_drawdown(prices: pd.Series) -> float:
        """Calculate maximum drawdown.
        
        Args:
            prices: Series of prices
            
        Returns:
            Maximum drawdown as a decimal
        """
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def generate_text_report(self, df: pd.DataFrame, ticker: str,
                            save: bool = True) -> str:
        """Generate a text-based statistical report.
        
        Args:
            df: OHLCV dataframe
            ticker: Stock ticker symbol
            save: Whether to save the report
            
        Returns:
            Report text
        """
        stats = self.generate_summary_statistics(df, ticker)
        
        report_lines = [
            f"={'='*60}",
            f"FINANCIAL ANALYSIS REPORT: {ticker}",
            f"={'='*60}",
            "",
            "SUMMARY STATISTICS",
            f"-{'-'*58}",
        ]
        
        for key, value in stats.items():
            report_lines.append(f"{key:.<40} {value:>15}")
        
        report_lines.extend([
            "",
            "="*60,
        ])
        
        report_text = "\n".join(report_lines)
        
        if save:
            filepath = self.output_dir / f"{ticker}_report.txt"
            with open(filepath, 'w') as f:
                f.write(report_text)
            logger.info(f"Text report saved: {filepath}")
        
        return report_text
    
    def generate_html_report(self, df: pd.DataFrame, ticker: str,
                            save: bool = True) -> str:
        """Generate an HTML report with statistics.
        
        Args:
            df: OHLCV dataframe with indicators
            ticker: Stock ticker symbol
            save: Whether to save the report
            
        Returns:
            HTML report string
        """
        stats = self.generate_summary_statistics(df, ticker)
        
        html_rows = "".join([
            f"<tr><td>{key}</td><td>{value}</td></tr>"
            for key, value in stats.items()
        ])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{ticker} - Financial Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .header {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; max-width: 800px; background-color: white; }}
                th {{ background-color: #0066cc; color: white; padding: 10px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1 class="header">Financial Analysis Report: {ticker}</h1>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                {html_rows}
            </table>
        </body>
        </html>
        """
        
        if save:
            filepath = self.output_dir / f"{ticker}_report.html"
            with open(filepath, 'w') as f:
                f.write(html)
            logger.info(f"HTML report saved: {filepath}")
        
        return html


def visualize_stock(df: pd.DataFrame, ticker: str) -> None:
    """Convenience function to generate all visualizations for a stock.
    
    Args:
        df: OHLCV dataframe with technical indicators
        ticker: Stock ticker symbol
    """
    chart_gen = ChartGenerator()
    report_gen = ReportGenerator()
    
    try:
        chart_gen.plot_price_chart(df, ticker)
        if 'RSI' in df.columns:
            chart_gen.plot_rsi_indicator(df, ticker)
        if 'MACD' in df.columns:
            chart_gen.plot_macd_indicator(df, ticker)
        if 'Volatility' in df.columns or 'ATR' in df.columns:
            chart_gen.plot_volatility_chart(df, ticker)
        
        report_gen.generate_text_report(df, ticker)
        report_gen.generate_html_report(df, ticker)
        
        logger.info(f"All visualizations generated for {ticker}")
    except ImportError as e:
        logger.error(f"Visualization skipped - {e}")


if __name__ == "__main__":
    print("Stage 4: Visualization & Reporting module loaded successfully.")
