"""Financial statements extraction and processing.

Provides methods to extract and analyze financial statements from yahoo finance.
"""

import logging
from typing import Optional, Dict
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class FinancialStatements:
    """Extract and process financial statements.
    
    Retrieves:
    - Income Statement (P&L)
    - Balance Sheet
    - Cash Flow Statement
    """
    
    @staticmethod
    def get_income_statement(ticker: str, quarterly: bool = False) -> Optional[pd.DataFrame]:
        """Get income statement (Profit & Loss).
        
        Income statement shows:
        - Revenue (total sales)
        - Operating expenses
        - Operating income
        - Net income (bottom line)
        
        Args:
            ticker (str): Stock ticker symbol.
            quarterly (bool): If True, returns quarterly data. Default: False (annual).
            
        Returns:
            pd.DataFrame: Income statement data or None if fetch failed.
            
        Example:
            >>> income_stmt = FinancialStatements.get_income_statement('AAPL')
            >>> revenue = income_stmt.loc['Total Revenue']
            >>> net_income = income_stmt.loc['Net Income']
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            stmt = ticker_obj.quarterly_income_stmt if quarterly else ticker_obj.income_stmt
            
            if stmt is None or stmt.empty:
                logger.warning(f"{ticker}: No income statement data available")
                return None
            
            logger.info(f"{ticker}: Retrieved income statement ({len(stmt.columns)} periods)")
            return stmt
        
        except Exception as e:
            logger.error(f"{ticker}: Failed to get income statement: {str(e)}")
            return None
    
    @staticmethod
    def get_balance_sheet(ticker: str, quarterly: bool = False) -> Optional[pd.DataFrame]:
        """Get balance sheet.
        
        Balance sheet shows:
        - Assets (what company owns)
        - Liabilities (what company owes)
        - Equity (shareholder ownership)
        
        Args:
            ticker (str): Stock ticker symbol.
            quarterly (bool): If True, returns quarterly data. Default: False (annual).
            
        Returns:
            pd.DataFrame: Balance sheet data or None if fetch failed.
            
        Example:
            >>> balance_sheet = FinancialStatements.get_balance_sheet('AAPL')
            >>> total_assets = balance_sheet.loc['Total Assets']
            >>> total_liabilities = balance_sheet.loc['Total Liabilities']
            >>> shareholders_equity = balance_sheet.loc['Total Stockholder Equity']
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            stmt = ticker_obj.quarterly_balance_sheet if quarterly else ticker_obj.balance_sheet
            
            if stmt is None or stmt.empty:
                logger.warning(f"{ticker}: No balance sheet data available")
                return None
            
            logger.info(f"{ticker}: Retrieved balance sheet ({len(stmt.columns)} periods)")
            return stmt
        
        except Exception as e:
            logger.error(f"{ticker}: Failed to get balance sheet: {str(e)}")
            return None
    
    @staticmethod
    def get_cashflow_statement(ticker: str, quarterly: bool = False) -> Optional[pd.DataFrame]:
        """Get cash flow statement.
        
        Cash flow statement shows:
        - Operating cash flow (cash from business operations)
        - Investing cash flow (investments, acquisitions)
        - Financing cash flow (debt, equity)
        
        Args:
            ticker (str): Stock ticker symbol.
            quarterly (bool): If True, returns quarterly data. Default: False (annual).
            
        Returns:
            pd.DataFrame: Cash flow statement data or None if fetch failed.
            
        Example:
            >>> cashflow = FinancialStatements.get_cashflow_statement('AAPL')
            >>> operating_cf = cashflow.loc['Operating Cash Flow']
            >>> free_cash_flow = cashflow.loc['Free Cash Flow']
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            stmt = ticker_obj.quarterly_cashflow if quarterly else ticker_obj.cashflow
            
            if stmt is None or stmt.empty:
                logger.warning(f"{ticker}: No cash flow data available")
                return None
            
            logger.info(f"{ticker}: Retrieved cash flow statement ({len(stmt.columns)} periods)")
            return stmt
        
        except Exception as e:
            logger.error(f"{ticker}: Failed to get cash flow statement: {str(e)}")
            return None
    
    @staticmethod
    def get_all_statements(ticker: str, quarterly: bool = False) -> Dict[str, Optional[pd.DataFrame]]:
        """Get all financial statements at once.
        
        Args:
            ticker (str): Stock ticker symbol.
            quarterly (bool): If True, returns quarterly data. Default: False (annual).
            
        Returns:
            Dict with keys: 'income_statement', 'balance_sheet', 'cashflow'
            
        Example:
            >>> statements = FinancialStatements.get_all_statements('AAPL')
            >>> income = statements['income_statement']
            >>> balance = statements['balance_sheet']
            >>> cashflow = statements['cashflow']
        """
        logger.info(f"{ticker}: Fetching all financial statements...")
        
        return {
            'income_statement': FinancialStatements.get_income_statement(ticker, quarterly),
            'balance_sheet': FinancialStatements.get_balance_sheet(ticker, quarterly),
            'cashflow': FinancialStatements.get_cashflow_statement(ticker, quarterly),
        }
