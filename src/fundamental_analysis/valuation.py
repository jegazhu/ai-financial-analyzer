"""Valuation metrics calculation module.

Provides valuation metrics for fundamental analysis.
"""

import logging
from typing import Optional, Dict
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class ValuationMetrics:
    """Calculate valuation metrics.
    
    Metrics used to determine if stock is cheap, fair, or expensive.
    """
    
    @staticmethod
    def get_market_data(ticker: str) -> Dict:
        """Get current market data for valuation calculations.
        
        Args:
            ticker (str): Stock ticker symbol.
            
        Returns:
            Dict with market data (market cap, shares, price, etc.)
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            return {
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'trailing_pe': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'price_to_book': info.get('priceToBook', None),
                'price_to_sales': info.get('priceToSalesTrailing12Months', None),
                'dividend_yield': info.get('dividendYield', 0),
                'earnings_per_share': info.get('trailingEps', 0),
                'book_value_per_share': info.get('bookValue', 0),
            }
        
        except Exception as e:
            logger.error(f"{ticker}: Failed to get market data: {str(e)}")
            return {}
    
    @staticmethod
    def price_to_earnings(current_price: float, earnings_per_share: float) -> Optional[float]:
        """Calculate Price-to-Earnings Ratio (P/E).
        
        P/E = Stock Price / Earnings Per Share
        
        Shows how much investors are willing to pay for each dollar of earnings.
        Lower P/E can indicate undervaluation (or slower growth).
        Higher P/E can indicate growth expectations (or overvaluation).
        
        Interpretation:
        - < 10: Very cheap (possible value stock)
        - 10-15: Undervalued
        - 15-25: Fair value
        - > 25: Potentially expensive
        
        Args:
            current_price (float): Current stock price.
            earnings_per_share (float): Trailing twelve months EPS.
            
        Returns:
            float: P/E ratio.
        """
        if earnings_per_share == 0:
            return None
        return current_price / earnings_per_share
    
    @staticmethod
    def price_to_book(current_price: float, book_value_per_share: float) -> Optional[float]:
        """Calculate Price-to-Book Ratio (P/B).
        
        P/B = Stock Price / Book Value Per Share
        
        Shows how much investors pay for each dollar of assets.
        Lower is generally better.
        
        Interpretation:
        - < 1.0: Trading below book value (potential value)
        - 1.0-3.0: Fair range
        - > 3.0: Premium valuation
        
        Args:
            current_price (float): Current stock price.
            book_value_per_share (float): Book value per share.
            
        Returns:
            float: P/B ratio.
        """
        if book_value_per_share == 0:
            return None
        return current_price / book_value_per_share
    
    @staticmethod
    def price_to_sales(market_cap: float, total_revenue: float) -> Optional[float]:
        """Calculate Price-to-Sales Ratio (P/S).
        
        P/S = Market Cap / Total Revenue
        
        Hard to manipulate (based on revenue, not earnings).
        Lower is better.
        
        Interpretation:
        - < 1.0: Very cheap
        - 1.0-2.0: Undervalued
        - 2.0-5.0: Fair to expensive
        - > 5.0: Very expensive
        
        Args:
            market_cap (float): Total market capitalization.
            total_revenue (float): Annual revenue.
            
        Returns:
            float: P/S ratio.
        """
        if total_revenue == 0:
            return None
        return market_cap / total_revenue
    
    @staticmethod
    def peg_ratio(price_to_earnings: float, earnings_growth_rate: float) -> Optional[float]:
        """Calculate PEG Ratio (Price/Earnings to Growth).
        
        PEG = P/E Ratio / Earnings Growth Rate
        
        Adjusts P/E for growth expectations.
        PEG < 1.0 suggests stock is undervalued relative to growth.
        PEG > 1.0 suggests stock is overvalued relative to growth.
        
        Args:
            price_to_earnings (float): P/E ratio.
            earnings_growth_rate (float): Annual earnings growth rate (0-1 scale).
            
        Returns:
            float: PEG ratio.
        """
        if earnings_growth_rate <= 0:
            return None
        return price_to_earnings / (earnings_growth_rate * 100)
    
    @staticmethod
    def enterprise_value_to_ebitda(market_cap: float, total_debt: float, cash: float, 
                                   ebitda: float) -> Optional[float]:
        """Calculate EV/EBITDA Ratio.
        
        EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA
        
        Compares enterprise value to operating earnings.
        Good for comparing companies with different capital structures.
        Lower is better.
        
        Interpretation:
        - < 8: Undervalued
        - 8-12: Fair value
        - > 12: Overvalued
        
        Args:
            market_cap (float): Market capitalization.
            total_debt (float): Total debt.
            cash (float): Cash and equivalents.
            ebitda (float): Earnings before interest, taxes, depreciation, amortization.
            
        Returns:
            float: EV/EBITDA ratio.
        """
        if ebitda == 0:
            return None
        
        enterprise_value = market_cap + total_debt - cash
        return enterprise_value / ebitda
    
    @staticmethod
    def dividend_yield(annual_dividend: float, current_price: float) -> Optional[float]:
        """Calculate Dividend Yield.
        
        Dividend Yield = Annual Dividend / Stock Price
        
        Shows income generated by dividends relative to investment.
        
        Interpretation:
        - 0-2%: Low (typical for growth stocks)
        - 2-4%: Moderate (attractive)
        - 4-6%: High (income stocks)
        - > 6%: Very high (possible yield trap)
        
        Args:
            annual_dividend (float): Annual dividend per share.
            current_price (float): Current stock price.
            
        Returns:
            float: Dividend yield (0-1 scale).
        """
        if current_price == 0:
            return None
        return annual_dividend / current_price
    
    @staticmethod
    def generate_valuation_report(ticker: str, current_price: float = None, 
                                 earnings_per_share: float = None, 
                                 book_value_per_share: float = None,
                                 market_cap: float = None,
                                 total_revenue: float = None) -> Dict:
        """Generate comprehensive valuation report.
        
        Args:
            ticker (str): Stock ticker symbol.
            current_price (float): Current stock price. If None, fetches from API.
            earnings_per_share (float): EPS.
            book_value_per_share (float): Book value per share.
            market_cap (float): Market capitalization.
            total_revenue (float): Annual revenue.
            
        Returns:
            Dict: Valuation metrics report.
        """
        # Get market data if not provided
        market_data = ValuationMetrics.get_market_data(ticker)
        
        current_price = current_price or market_data.get('current_price', 0)
        earnings_per_share = earnings_per_share or market_data.get('earnings_per_share', 0)
        book_value_per_share = book_value_per_share or market_data.get('book_value_per_share', 0)
        market_cap = market_cap or market_data.get('market_cap', 0)
        
        report = {
            'ticker': ticker,
            'current_price': current_price,
            'market_cap': market_cap,
            'earnings_per_share': earnings_per_share,
            'book_value_per_share': book_value_per_share,
            'valuation_multiples': {
                'price_to_earnings': ValuationMetrics.price_to_earnings(current_price, earnings_per_share),
                'price_to_book': ValuationMetrics.price_to_book(current_price, book_value_per_share),
                'price_to_sales': ValuationMetrics.price_to_sales(market_cap, total_revenue) if total_revenue else None,
                'dividend_yield': market_data.get('dividend_yield', 0),
            },
            'multiples_from_api': {
                'trailing_pe': market_data.get('trailing_pe'),
                'forward_pe': market_data.get('forward_pe'),
                'peg_ratio': market_data.get('peg_ratio'),
                'price_to_book': market_data.get('price_to_book'),
                'price_to_sales': market_data.get('price_to_sales'),
            }
        }
        
        logger.info(f"{ticker}: Generated valuation report")
        return report
