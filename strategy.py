#!/usr/bin/env python3
"""
Investment Strategy Classes for S&P 500 Dollar Cost Averaging Experiments

This module contains different investment strategy implementations:
- DailyStrategy: Invests every trading day
- WeeklyRandomStrategy: Invests weekly amount on random day each week  
- MonthlyRandomStrategy: Invests monthly amount on random day each month
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseStrategy(ABC):
    """Base class for all investment strategies."""
    
    def __init__(self, daily_investment: float, price_column: str = 'close', stock_ticker: str = None):
        """
        Initialize the strategy.
        
        Args:
            daily_investment: Amount to invest per day (strategy will scale appropriately)
            price_column: Which price column to use ('open', 'high', 'low', 'close')
            stock_ticker: Specific stock to invest in (None for all S&P 500 stocks)
        """
        self.daily_investment = daily_investment
        self.price_column = price_column
        self.stock_ticker = stock_ticker
        
        # Strategy-specific data
        self.portfolio = {}  # {stock_name: {'shares': float, 'cost_basis': float, 'prices': []}}
        self.investment_records = []
        self.total_invested = 0.0
        self.final_value = 0.0
        self.total_return = 0.0
        self.return_pct = 0.0
        
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this strategy."""
        pass
        
    @property
    @abstractmethod
    def strategy_description(self) -> str:
        """Return a description of this strategy."""
        pass
    
    def reset(self):
        """Reset strategy state for a new experiment."""
        self.portfolio = {}
        self.investment_records = []
        self.total_invested = 0.0
        self.final_value = 0.0
        self.total_return = 0.0
        self.return_pct = 0.0
    
    def invest_on_day(self, day_data: pd.DataFrame, investment_amount: float, trading_date: pd.Timestamp, **kwargs):
        """
        Make an investment on a specific day.
        
        Args:
            day_data: DataFrame with stock data for that day
            investment_amount: Amount to invest that day
            trading_date: The trading date
            **kwargs: Additional strategy-specific parameters
        """
        if self.stock_ticker:
            # Invest all in one specific stock
            stocks_to_buy = day_data[day_data['Name'] == self.stock_ticker]
            if stocks_to_buy.empty:
                return  # Skip if stock not available that day
            investment_per_stock = investment_amount
        else:
            # Invest equally across all available stocks that day
            stocks_to_buy = day_data
            num_stocks = len(stocks_to_buy)
            investment_per_stock = investment_amount / num_stocks if num_stocks > 0 else 0
        
        for _, row in stocks_to_buy.iterrows():
            stock_name = row['Name']
            price = row[self.price_column]
            
            if price <= 0:
                continue
                
            shares_bought = investment_per_stock / price
            
            if stock_name not in self.portfolio:
                self.portfolio[stock_name] = {'shares': 0, 'cost_basis': 0, 'prices': []}
            
            self.portfolio[stock_name]['shares'] += shares_bought
            self.portfolio[stock_name]['cost_basis'] += investment_per_stock
            self.portfolio[stock_name]['prices'].append(price)
            
            record = {
                'date': trading_date,
                'stock': stock_name,
                'price': price,
                'shares_bought': shares_bought,
                'investment': investment_per_stock,
                'strategy': self.strategy_name
            }
            record.update(kwargs)  # Add any strategy-specific data
            self.investment_records.append(record)
    
    @abstractmethod
    def run_experiment(self, df: pd.DataFrame, start_date: pd.Timestamp, duration_days: int) -> Dict[str, Any]:
        """
        Run the investment strategy experiment.
        
        Args:
            df: Stock data DataFrame
            start_date: Start date for the experiment
            duration_days: Duration in days
            
        Returns:
            Dictionary with experiment results
        """
        pass
    
    def calculate_final_value(self, experiment_data: pd.DataFrame, trading_days: List[pd.Timestamp]) -> float:
        """Calculate the final portfolio value."""
        if not trading_days:
            return 0.0
            
        final_day = trading_days[-1]
        final_day_data = experiment_data[experiment_data['date'] == final_day]
        
        total_value = 0
        final_positions = []
        
        for stock_name, position in self.portfolio.items():
            # Get the last price for this stock
            stock_final = final_day_data[final_day_data['Name'] == stock_name]
            if not stock_final.empty:
                final_price = stock_final[self.price_column].values[0]
            else:
                # If stock not traded on final day, use the last available price
                stock_data = experiment_data[experiment_data['Name'] == stock_name]
                if not stock_data.empty:
                    final_price = stock_data[stock_data['date'] == stock_data['date'].max()][self.price_column].values[0]
                else:
                    final_price = 0
            
            position_value = position['shares'] * final_price
            total_value += position_value
            
            avg_price = position['cost_basis'] / position['shares'] if position['shares'] > 0 else 0
            
            final_positions.append({
                'stock': stock_name,
                'shares': position['shares'],
                'cost_basis': position['cost_basis'],
                'final_price': final_price,
                'final_value': position_value,
                'avg_buy_price': avg_price,
                'return_pct': ((position_value / position['cost_basis']) - 1) * 100 if position['cost_basis'] > 0 else 0,
                'min_price': min(position['prices']) if position['prices'] else 0,
                'max_price': max(position['prices']) if position['prices'] else 0
            })
        
        self.final_positions = sorted(final_positions, key=lambda x: x['return_pct'], reverse=True)
        return total_value
    
    def get_results(self) -> Dict[str, Any]:
        """Get the results of the last experiment run."""
        all_prices = [r['price'] for r in self.investment_records]
        
        return {
            'strategy_name': self.strategy_name,
            'strategy_description': self.strategy_description,
            'total_invested': self.total_invested,
            'final_value': self.final_value,
            'total_return': self.total_return,
            'return_pct': self.return_pct,
            'num_stocks': len(self.portfolio),
            'num_transactions': len(self.investment_records),
            'min_price_bought': min(all_prices) if all_prices else 0,
            'max_price_bought': max(all_prices) if all_prices else 0,
            'avg_price_bought': np.mean(all_prices) if all_prices else 0,
            'final_positions': getattr(self, 'final_positions', []),
            'investment_records': self.investment_records
        }


class DailyStrategy(BaseStrategy):
    """Strategy that invests every trading day."""
    
    @property
    def strategy_name(self) -> str:
        return "Daily"
    
    @property
    def strategy_description(self) -> str:
        return "Invests fixed amount every trading day"
    
    def run_experiment(self, df: pd.DataFrame, start_date: pd.Timestamp, duration_days: int) -> Dict[str, Any]:
        """Run daily investment strategy."""
        self.reset()
        
        end_date = start_date + timedelta(days=duration_days)
        
        # Filter data for the experiment period
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        if self.stock_ticker:
            mask &= (df['Name'] == self.stock_ticker)
        
        experiment_data = df[mask].copy()
        
        if experiment_data.empty:
            raise ValueError(f"No data found for {self.strategy_name} strategy. Stock: {self.stock_ticker}, Period: {start_date} to {end_date}")
        
        # Get unique trading days
        trading_days = sorted(experiment_data['date'].unique())
        
        # Invest daily
        for day in trading_days:
            day_data = experiment_data[experiment_data['date'] == day]
            self.invest_on_day(day_data, self.daily_investment, day)
        
        # Calculate results
        self.total_invested = sum(r['investment'] for r in self.investment_records)
        self.final_value = self.calculate_final_value(experiment_data, trading_days)
        self.total_return = self.final_value - self.total_invested
        self.return_pct = (self.total_return / self.total_invested) * 100 if self.total_invested > 0 else 0
        
        return self.get_results()


class WeeklyRandomStrategy(BaseStrategy):
    """Strategy that invests weekly amount on a random day each week."""
    
    @property
    def strategy_name(self) -> str:
        return "Weekly Random"
    
    @property
    def strategy_description(self) -> str:
        return "Invests weekly amount on one random day per week"
    
    def run_experiment(self, df: pd.DataFrame, start_date: pd.Timestamp, duration_days: int) -> Dict[str, Any]:
        """Run weekly random investment strategy."""
        self.reset()
        
        end_date = start_date + timedelta(days=duration_days)
        
        # Filter data for the experiment period
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        if self.stock_ticker:
            mask &= (df['Name'] == self.stock_ticker)
        
        experiment_data = df[mask].copy()
        
        if experiment_data.empty:
            raise ValueError(f"No data found for {self.strategy_name} strategy. Stock: {self.stock_ticker}, Period: {start_date} to {end_date}")
        
        # Get unique trading days
        trading_days = sorted(experiment_data['date'].unique())
        
        # Group trading days by week (ISO week number)
        trading_days_df = pd.DataFrame({'date': trading_days})
        trading_days_df['year_week'] = trading_days_df['date'].apply(
            lambda x: (pd.Timestamp(x).isocalendar()[0], pd.Timestamp(x).isocalendar()[1])
        )
        
        # Group days by week
        weeks = trading_days_df.groupby('year_week')['date'].apply(list).to_dict()
        
        # For each week, pick a random day to invest
        for year_week, week_days in weeks.items():
            # Calculate weekly investment amount
            num_trading_days_in_week = len(week_days)
            weekly_investment = self.daily_investment * num_trading_days_in_week
            
            # Pick a random day from this week to invest
            investment_day = random.choice(week_days)
            
            day_data = experiment_data[experiment_data['date'] == investment_day]
            self.invest_on_day(
                day_data, 
                weekly_investment, 
                investment_day,
                week=year_week,
                trading_days_in_week=num_trading_days_in_week
            )
        
        # Calculate results
        self.total_invested = sum(r['investment'] for r in self.investment_records)
        self.final_value = self.calculate_final_value(experiment_data, trading_days)
        self.total_return = self.final_value - self.total_invested
        self.return_pct = (self.total_return / self.total_invested) * 100 if self.total_invested > 0 else 0
        
        return self.get_results()


class MonthlyRandomStrategy(BaseStrategy):
    """Strategy that invests monthly amount on a random day each month."""
    
    @property
    def strategy_name(self) -> str:
        return "Monthly Random"
    
    @property
    def strategy_description(self) -> str:
        return "Invests monthly amount on one random day per month"
    
    def run_experiment(self, df: pd.DataFrame, start_date: pd.Timestamp, duration_days: int) -> Dict[str, Any]:
        """Run monthly random investment strategy."""
        self.reset()
        
        end_date = start_date + timedelta(days=duration_days)
        
        # Filter data for the experiment period
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        if self.stock_ticker:
            mask &= (df['Name'] == self.stock_ticker)
        
        experiment_data = df[mask].copy()
        
        if experiment_data.empty:
            raise ValueError(f"No data found for {self.strategy_name} strategy. Stock: {self.stock_ticker}, Period: {start_date} to {end_date}")
        
        # Get unique trading days
        trading_days = sorted(experiment_data['date'].unique())
        
        # Group trading days by month (year-month)
        trading_days_df = pd.DataFrame({'date': trading_days})
        trading_days_df['year_month'] = trading_days_df['date'].apply(
            lambda x: (pd.Timestamp(x).year, pd.Timestamp(x).month)
        )
        
        # Group days by month
        months = trading_days_df.groupby('year_month')['date'].apply(list).to_dict()
        
        # For each month, pick a random day to invest
        for year_month, month_days in months.items():
            # Calculate monthly investment amount
            num_trading_days_in_month = len(month_days)
            monthly_investment = self.daily_investment * num_trading_days_in_month
            
            # Pick a random day from this month to invest
            investment_day = random.choice(month_days)
            
            day_data = experiment_data[experiment_data['date'] == investment_day]
            self.invest_on_day(
                day_data, 
                monthly_investment, 
                investment_day,
                month=year_month,
                trading_days_in_month=num_trading_days_in_month
            )
        
        # Calculate results
        self.total_invested = sum(r['investment'] for r in self.investment_records)
        self.final_value = self.calculate_final_value(experiment_data, trading_days)
        self.total_return = self.final_value - self.total_invested
        self.return_pct = (self.total_return / self.total_invested) * 100 if self.total_invested > 0 else 0
        
        return self.get_results()