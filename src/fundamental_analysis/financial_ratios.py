"""Financial ratios calculation module.

Provides methods to calculate financial ratios for fundamental analysis.
"""

import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FinancialRatios:
    """Calculate financial ratios for fundamental analysis.
    
    Ratios are organized into categories:
    - Profitability Ratios
    - Liquidity Ratios
    - Leverage/Solvency Ratios
    - Efficiency Ratios
    - Growth Ratios
    """
    
    # ========================================================================
    # PROFITABILITY RATIOS - How well the company makes profits
    # ========================================================================
    
    @staticmethod
    def gross_profit_margin(revenue: float, cost_of_goods_sold: float) -> Optional[float]:
        """Calculate Gross Profit Margin.
        
        Gross Profit Margin = (Revenue - COGS) / Revenue
        
        Shows what % of revenue remains after paying for goods sold.
        Higher is better (means more efficient production).
        
        Args:
            revenue (float): Total revenue.
            cost_of_goods_sold (float): COGS.
            
        Returns:
            float: Gross profit margin (0-1 scale).
        """
        if revenue == 0:
            return None
        return (revenue - cost_of_goods_sold) / revenue
    
    @staticmethod
    def operating_profit_margin(operating_income: float, revenue: float) -> Optional[float]:
        """Calculate Operating Profit Margin.
        
        Operating Profit Margin = Operating Income / Revenue
        
        Shows profitability from core business operations.
        
        Args:
            operating_income (float): Operating income (EBIT).
            revenue (float): Total revenue.
            
        Returns:
            float: Operating profit margin (0-1 scale).
        """
        if revenue == 0:
            return None
        return operating_income / revenue
    
    @staticmethod
    def net_profit_margin(net_income: float, revenue: float) -> Optional[float]:
        """Calculate Net Profit Margin.
        
        Net Profit Margin = Net Income / Revenue
        
        Shows what % of revenue becomes profit after all expenses.
        Most important profitability metric.
        
        Args:
            net_income (float): Net income (bottom line).
            revenue (float): Total revenue.
            
        Returns:
            float: Net profit margin (0-1 scale).
        """
        if revenue == 0:
            return None
        return net_income / revenue
    
    @staticmethod
    def return_on_equity(net_income: float, shareholders_equity: float) -> Optional[float]:
        """Calculate Return on Equity (ROE).
        
        ROE = Net Income / Shareholders' Equity
        
        Shows how efficiently company uses shareholder money to generate profits.
        Higher is better. Industry varies (tech ~20%, utilities ~10%).
        
        Args:
            net_income (float): Net income.
            shareholders_equity (float): Total shareholders' equity.
            
        Returns:
            float: ROE (0-1 scale, interpret as percentage).
        """
        if shareholders_equity == 0:
            return None
        return net_income / shareholders_equity
    
    @staticmethod
    def return_on_assets(net_income: float, total_assets: float) -> Optional[float]:
        """Calculate Return on Assets (ROA).
        
        ROA = Net Income / Total Assets
        
        Shows how efficiently company uses all assets to generate profits.
        Lower than ROE (doesn't account for debt).
        
        Args:
            net_income (float): Net income.
            total_assets (float): Total assets.
            
        Returns:
            float: ROA (0-1 scale).
        """
        if total_assets == 0:
            return None
        return net_income / total_assets
    
    # ========================================================================
    # LIQUIDITY RATIOS - Can company pay short-term obligations?
    # ========================================================================
    
    @staticmethod
    def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
        """Calculate Current Ratio.
        
        Current Ratio = Current Assets / Current Liabilities
        
        Shows ability to pay short-term debt with short-term assets.
        Interpretation:
        - > 2.0: Strong liquidity
        - 1.0-2.0: Healthy
        - < 1.0: Liquidity concerns
        
        Args:
            current_assets (float): Current assets (cash, receivables, inventory).
            current_liabilities (float): Current liabilities (due within 1 year).
            
        Returns:
            float: Current ratio.
        """
        if current_liabilities == 0:
            return None
        return current_assets / current_liabilities
    
    @staticmethod
    def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> Optional[float]:
        """Calculate Quick Ratio (Acid Test).
        
        Quick Ratio = (Current Assets - Inventory) / Current Liabilities
        
        More conservative than current ratio (excludes inventory).
        Shows liquid assets available to pay short-term debt.
        
        Args:
            current_assets (float): Current assets.
            inventory (float): Inventory (least liquid current asset).
            current_liabilities (float): Current liabilities.
            
        Returns:
            float: Quick ratio.
        """
        if current_liabilities == 0:
            return None
        return (current_assets - inventory) / current_liabilities
    
    @staticmethod
    def cash_ratio(cash: float, current_liabilities: float) -> Optional[float]:
        """Calculate Cash Ratio.
        
        Cash Ratio = Cash & Equivalents / Current Liabilities
        
        Most conservative liquidity measure (only counts actual cash).
        
        Args:
            cash (float): Cash and cash equivalents.
            current_liabilities (float): Current liabilities.
            
        Returns:
            float: Cash ratio.
        """
        if current_liabilities == 0:
            return None
        return cash / current_liabilities
    
    # ========================================================================
    # LEVERAGE/SOLVENCY RATIOS - How much debt does company have?
    # ========================================================================
    
    @staticmethod
    def debt_to_equity(total_debt: float, shareholders_equity: float) -> Optional[float]:
        """Calculate Debt-to-Equity Ratio.
        
        Debt-to-Equity = Total Debt / Shareholders' Equity
        
        Shows leverage and financial risk.
        Interpretation:
        - < 0.5: Conservative (low leverage)
        - 0.5-2.0: Moderate (typical)
        - > 2.0: High leverage (risky)
        
        Args:
            total_debt (float): Total debt (short + long term).
            shareholders_equity (float): Total equity.
            
        Returns:
            float: Debt-to-equity ratio.
        """
        if shareholders_equity == 0:
            return None
        return total_debt / shareholders_equity
    
    @staticmethod
    def debt_to_assets(total_debt: float, total_assets: float) -> Optional[float]:
        """Calculate Debt-to-Assets Ratio.
        
        Debt-to-Assets = Total Debt / Total Assets
        
        Shows what % of assets are financed by debt.
        Interpretation:
        - < 0.3: Low leverage
        - 0.3-0.6: Moderate leverage
        - > 0.6: High leverage
        
        Args:
            total_debt (float): Total debt.
            total_assets (float): Total assets.
            
        Returns:
            float: Debt-to-assets ratio.
        """
        if total_assets == 0:
            return None
        return total_debt / total_assets
    
    @staticmethod
    def equity_ratio(shareholders_equity: float, total_assets: float) -> Optional[float]:
        """Calculate Equity Ratio.
        
        Equity Ratio = Shareholders' Equity / Total Assets
        
        Shows what % of assets are financed by equity (inverse of debt-to-assets).
        Higher is better (less financial risk).
        
        Args:
            shareholders_equity (float): Total equity.
            total_assets (float): Total assets.
            
        Returns:
            float: Equity ratio (0-1 scale).
        """
        if total_assets == 0:
            return None
        return shareholders_equity / total_assets
    
    @staticmethod
    def interest_coverage(ebit: float, interest_expense: float) -> Optional[float]:
        """Calculate Interest Coverage Ratio.
        
        Interest Coverage = EBIT / Interest Expense
        
        Shows how many times company can cover interest payments with earnings.
        Higher is better. < 2.0 is risky.
        
        Args:
            ebit (float): Earnings before interest and taxes.
            interest_expense (float): Interest expense.
            
        Returns:
            float: Interest coverage ratio.
        """
        if interest_expense == 0:
            return None
        return ebit / interest_expense
    
    # ========================================================================
    # EFFICIENCY RATIOS - How well company uses assets?
    # ========================================================================
    
    @staticmethod
    def asset_turnover(revenue: float, average_total_assets: float) -> Optional[float]:
        """Calculate Asset Turnover Ratio.
        
        Asset Turnover = Revenue / Average Total Assets
        
        Shows how efficiently company uses assets to generate revenue.
        Higher is better (more revenue per dollar of assets).
        
        Args:
            revenue (float): Total revenue.
            average_total_assets (float): Average total assets over period.
            
        Returns:
            float: Asset turnover ratio.
        """
        if average_total_assets == 0:
            return None
        return revenue / average_total_assets
    
    @staticmethod
    def inventory_turnover(cost_of_goods_sold: float, average_inventory: float) -> Optional[float]:
        """Calculate Inventory Turnover Ratio.
        
        Inventory Turnover = COGS / Average Inventory
        
        Shows how many times inventory is sold and replaced.
        Higher is better (less capital tied up in inventory).
        
        Args:
            cost_of_goods_sold (float): COGS.
            average_inventory (float): Average inventory.
            
        Returns:
            float: Inventory turnover ratio.
        """
        if average_inventory == 0:
            return None
        return cost_of_goods_sold / average_inventory
    
    @staticmethod
    def receivables_turnover(revenue: float, average_accounts_receivable: float) -> Optional[float]:
        """Calculate Receivables Turnover Ratio.
        
        Receivables Turnover = Revenue / Average Accounts Receivable
        
        Shows how quickly company collects payments from customers.
        Higher is better.
        
        Args:
            revenue (float): Total revenue.
            average_accounts_receivable (float): Average receivables.
            
        Returns:
            float: Receivables turnover ratio.
        """
        if average_accounts_receivable == 0:
            return None
        return revenue / average_accounts_receivable
    
    # ========================================================================
    # GROWTH RATIOS - Is company growing?
    # ========================================================================
    
    @staticmethod
    def revenue_growth(current_revenue: float, previous_revenue: float) -> Optional[float]:
        """Calculate Revenue Growth Rate.
        
        Revenue Growth = (Current Revenue - Previous Revenue) / Previous Revenue
        
        Year-over-year or period-over-period growth.
        
        Args:
            current_revenue (float): Current period revenue.
            previous_revenue (float): Previous period revenue.
            
        Returns:
            float: Growth rate (0-1 scale, interpret as percentage).
        """
        if previous_revenue == 0:
            return None
        return (current_revenue - previous_revenue) / previous_revenue
    
    @staticmethod
    def earnings_growth(current_earnings: float, previous_earnings: float) -> Optional[float]:
        """Calculate Earnings Growth Rate.
        
        Earnings Growth = (Current Earnings - Previous Earnings) / Previous Earnings
        
        Shows growth in net income.
        
        Args:
            current_earnings (float): Current period earnings.
            previous_earnings (float): Previous period earnings.
            
        Returns:
            float: Growth rate (0-1 scale).
        """
        if previous_earnings == 0:
            return None
        return (current_earnings - previous_earnings) / previous_earnings
    
    @staticmethod
    def generate_ratio_report(ticker: str, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame, 
                             cashflow: pd.DataFrame) -> Dict:
        """Generate comprehensive financial ratio report.
        
        Args:
            ticker (str): Stock ticker symbol.
            income_stmt (pd.DataFrame): Income statement.
            balance_sheet (pd.DataFrame): Balance sheet.
            cashflow (pd.DataFrame): Cash flow statement.
            
        Returns:
            Dict: Comprehensive ratio report.
        """
        report = {
            'ticker': ticker,
            'profitability': {},
            'liquidity': {},
            'leverage': {},
            'efficiency': {},
            'growth': {},
        }
        
        try:
            # Get latest period data
            latest_income = income_stmt.iloc[:, 0]
            latest_balance = balance_sheet.iloc[:, 0]
            
            # Profitability Ratios
            revenue = latest_income.get('Total Revenue', 0)
            net_income = latest_income.get('Net Income', 0)
            operating_income = latest_income.get('Operating Income', 0)
            cogs = latest_income.get('Cost of Revenue', 0)
            
            report['profitability']['gross_margin'] = FinancialRatios.gross_profit_margin(revenue, cogs)
            report['profitability']['operating_margin'] = FinancialRatios.operating_profit_margin(operating_income, revenue)
            report['profitability']['net_margin'] = FinancialRatios.net_profit_margin(net_income, revenue)
            
            # Get balance sheet items
            total_assets = latest_balance.get('Total Assets', 0)
            shareholders_equity = latest_balance.get('Total Stockholder Equity', 0)
            
            report['profitability']['roa'] = FinancialRatios.return_on_assets(net_income, total_assets)
            report['profitability']['roe'] = FinancialRatios.return_on_equity(net_income, shareholders_equity)
            
            # Liquidity Ratios
            current_assets = latest_balance.get('Current Assets', 0)
            current_liabilities = latest_balance.get('Current Liabilities', 0)
            cash = latest_balance.get('Cash And Cash Equivalents', 0)
            inventory = latest_balance.get('Inventory', 0)
            
            report['liquidity']['current_ratio'] = FinancialRatios.current_ratio(current_assets, current_liabilities)
            report['liquidity']['quick_ratio'] = FinancialRatios.quick_ratio(current_assets, inventory, current_liabilities)
            report['liquidity']['cash_ratio'] = FinancialRatios.cash_ratio(cash, current_liabilities)
            
            # Leverage Ratios
            total_debt = latest_balance.get('Total Debt', 0)
            interest_expense = latest_income.get('Interest Expense', 0)
            ebit = latest_income.get('Operating Income', 0)
            
            report['leverage']['debt_to_equity'] = FinancialRatios.debt_to_equity(total_debt, shareholders_equity)
            report['leverage']['debt_to_assets'] = FinancialRatios.debt_to_assets(total_debt, total_assets)
            report['leverage']['equity_ratio'] = FinancialRatios.equity_ratio(shareholders_equity, total_assets)
            report['leverage']['interest_coverage'] = FinancialRatios.interest_coverage(ebit, interest_expense)
            
            logger.info(f"{ticker}: Generated financial ratio report")
            return report
        
        except Exception as e:
            logger.error(f"{ticker}: Failed to generate ratio report: {str(e)}")
            return report
