#!/usr/bin/env python3
"""
S&P 500 Dollar Cost Averaging Experiment

This script simulates a dollar-cost averaging investment strategy where we invest
a fixed amount ($1 by default) each day the market is open for a configurable duration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ============================================================================
# CONFIGURATION - Modify these values to customize the experiment
# ============================================================================

# Investment amount per day (in USD)
DAILY_INVESTMENT = 1.0

# Duration of the experiment in days (365 = 1 year)
EXPERIMENT_DURATION_DAYS = 365

# Column to use for buying shares: 'open', 'high', 'low', 'close'
PRICE_COLUMN = 'close'

# Stock ticker to invest in (use None to invest in the whole S&P 500 index equally)
# Examples: 'AAPL', 'GOOGL', 'AMZN', or None for all stocks
STOCK_TICKER = None

# Random seed for reproducibility (set to None for truly random)
RANDOM_SEED = 42

# Number of experiments to run (different random start dates)
NUM_EXPERIMENTS = 20

# Output file for the report
OUTPUT_FILE = 'experiment_report.md'

# Path to the dataset
DATASET_PATH = 'all_stocks_5yr.csv'

# ============================================================================
# EXPERIMENT CODE
# ============================================================================

def load_data(filepath: str) -> pd.DataFrame:
    """Load and preprocess the stock data."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['date', 'Name']).reset_index(drop=True)
    print(f"Loaded {len(df):,} records for {df['Name'].nunique()} stocks")
    return df


def get_valid_start_dates(df: pd.DataFrame, duration_days: int) -> list:
    """Get all valid start dates that allow for the full experiment duration."""
    all_dates = df['date'].unique()
    all_dates = sorted(all_dates)
    
    min_date = pd.Timestamp(all_dates[0])
    max_date = pd.Timestamp(all_dates[-1])
    
    # The latest valid start date is max_date - duration_days
    latest_start = max_date - timedelta(days=duration_days)
    
    valid_starts = [d for d in all_dates if pd.Timestamp(d) <= latest_start]
    return valid_starts


def pick_random_start_date(valid_dates: list, seed: int = None) -> pd.Timestamp:
    """Pick a random start date from the valid dates."""
    if seed is not None:
        random.seed(seed)
    return pd.Timestamp(random.choice(valid_dates))


def run_experiment(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    duration_days: int,
    daily_investment: float,
    price_column: str,
    stock_ticker: str = None
) -> dict:
    """
    Run the dollar-cost averaging experiment.
    
    Returns a dictionary with experiment results.
    """
    end_date = start_date + timedelta(days=duration_days)
    
    # Filter data for the experiment period
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    if stock_ticker:
        mask &= (df['Name'] == stock_ticker)
    
    experiment_data = df[mask].copy()
    
    if experiment_data.empty:
        raise ValueError(f"No data found for the specified parameters. Stock: {stock_ticker}, Period: {start_date} to {end_date}")
    
    # Get unique trading days in the experiment period
    trading_days = sorted(experiment_data['date'].unique())
    
    # Track investments
    portfolio = {}  # {stock_name: {'shares': float, 'cost_basis': float}}
    daily_records = []
    
    for day in trading_days:
        day_data = experiment_data[experiment_data['date'] == day]
        
        if stock_ticker:
            # Invest all in one stock
            stocks_to_buy = day_data
            investment_per_stock = daily_investment
        else:
            # Invest equally across all available stocks that day
            stocks_to_buy = day_data
            num_stocks = len(stocks_to_buy)
            investment_per_stock = daily_investment / num_stocks if num_stocks > 0 else 0
        
        for _, row in stocks_to_buy.iterrows():
            stock_name = row['Name']
            price = row[price_column]
            
            if price <= 0:
                continue
                
            shares_bought = investment_per_stock / price
            
            if stock_name not in portfolio:
                portfolio[stock_name] = {'shares': 0, 'cost_basis': 0, 'prices': []}
            
            portfolio[stock_name]['shares'] += shares_bought
            portfolio[stock_name]['cost_basis'] += investment_per_stock
            portfolio[stock_name]['prices'].append(price)
            
            daily_records.append({
                'date': day,
                'stock': stock_name,
                'price': price,
                'shares_bought': shares_bought,
                'investment': investment_per_stock
            })
    
    # Calculate final portfolio value using the last available price for each stock
    final_day = trading_days[-1]
    final_day_data = experiment_data[experiment_data['date'] == final_day]
    
    total_value = 0
    final_positions = []
    
    for stock_name, position in portfolio.items():
        # Get the last price for this stock
        stock_final = final_day_data[final_day_data['Name'] == stock_name]
        if not stock_final.empty:
            final_price = stock_final[price_column].values[0]
        else:
            # If stock not traded on final day, use the last available price
            stock_data = experiment_data[experiment_data['Name'] == stock_name]
            final_price = stock_data[stock_data['date'] == stock_data['date'].max()][price_column].values[0]
        
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
            'min_price': min(position['prices']),
            'max_price': max(position['prices'])
        })
    
    # Calculate summary statistics
    total_invested = sum(r['investment'] for r in daily_records)
    total_return = total_value - total_invested
    return_pct = (total_return / total_invested) * 100 if total_invested > 0 else 0
    
    all_prices = [r['price'] for r in daily_records]
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'actual_end_date': trading_days[-1],
        'duration_days': duration_days,
        'trading_days_count': len(trading_days),
        'daily_investment': daily_investment,
        'price_column': price_column,
        'stock_ticker': stock_ticker,
        'total_invested': total_invested,
        'final_value': total_value,
        'total_return': total_return,
        'return_pct': return_pct,
        'annualized_return_pct': (((total_value / total_invested) ** (365 / duration_days)) - 1) * 100 if total_invested > 0 and duration_days > 0 else 0,
        'num_stocks': len(portfolio),
        'num_transactions': len(daily_records),
        'min_price_bought': min(all_prices) if all_prices else 0,
        'max_price_bought': max(all_prices) if all_prices else 0,
        'avg_price_bought': np.mean(all_prices) if all_prices else 0,
        'final_positions': sorted(final_positions, key=lambda x: x['return_pct'], reverse=True),
        'daily_records': daily_records
    }


def generate_report(all_results: list, output_file: str):
    """Generate a markdown report of the experiment results."""
    
    report = []
    report.append("# 📈 S&P 500 Dollar Cost Averaging Experiment Report\n")
    report.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Use first result for common parameters
    first_result = all_results[0]
    num_experiments = len(all_results)
    
    # Experiment Parameters
    report.append("## 🔧 Experiment Parameters\n")
    report.append("| Parameter | Value |")
    report.append("|-----------|-------|")
    report.append(f"| Number of Experiments | {num_experiments} |")
    report.append(f"| Duration per Experiment | {first_result['duration_days']} days |")
    report.append(f"| Daily Investment | ${first_result['daily_investment']:.2f} |")
    report.append(f"| Price Column Used | {first_result['price_column']} |")
    report.append(f"| Stock(s) | {first_result['stock_ticker'] if first_result['stock_ticker'] else 'All S&P 500 stocks'} |")
    report.append("")
    
    # Aggregate Statistics
    returns = [r['return_pct'] for r in all_results]
    annualized_returns = [r['annualized_return_pct'] for r in all_results]
    total_invested_list = [r['total_invested'] for r in all_results]
    final_values = [r['final_value'] for r in all_results]
    
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    min_return = min(returns)
    max_return = max(returns)
    median_return = np.median(returns)
    
    avg_annualized = np.mean(annualized_returns)
    avg_invested = np.mean(total_invested_list)
    avg_final_value = np.mean(final_values)
    
    profitable_experiments = sum(1 for r in returns if r > 0)
    
    # Aggregate Summary
    report.append("## 📊 Aggregate Results Summary\n")
    report.append(f"*Statistics across {num_experiments} experiments with different start dates*\n")
    report.append("")
    
    overall_emoji = "🟢" if avg_return >= 0 else "🔴"
    report.append("### Return Statistics\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| {overall_emoji} **Average Return** | **{avg_return:+.2f}%** |")
    report.append(f"| Median Return | {median_return:+.2f}% |")
    report.append(f"| Standard Deviation | {std_return:.2f}% |")
    report.append(f"| Best Return | {max_return:+.2f}% |")
    report.append(f"| Worst Return | {min_return:+.2f}% |")
    report.append(f"| Average Annualized Return | {avg_annualized:+.2f}% |")
    report.append(f"| Profitable Experiments | {profitable_experiments}/{num_experiments} ({(profitable_experiments/num_experiments)*100:.1f}%) |")
    report.append("")
    
    report.append("### Investment Statistics\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Average Amount Invested | ${avg_invested:,.2f} |")
    report.append(f"| Average Final Value | ${avg_final_value:,.2f} |")
    report.append(f"| Average Profit/Loss | ${avg_final_value - avg_invested:+,.2f} |")
    report.append("")
    
    # Individual Experiment Results Table
    report.append("## 📋 Individual Experiment Results\n")
    report.append("| # | Start Date | End Date | Invested | Final Value | Return | Return % |")
    report.append("|---|------------|----------|----------|-------------|--------|----------|")
    
    # Sort by return percentage for display
    sorted_results = sorted(all_results, key=lambda x: x['return_pct'], reverse=True)
    for i, r in enumerate(sorted_results, 1):
        emoji = "🟢" if r['return_pct'] >= 0 else "🔴"
        report.append(f"| {i} | {r['start_date'].strftime('%Y-%m-%d')} | {r['actual_end_date'].strftime('%Y-%m-%d')} | ${r['total_invested']:,.2f} | ${r['final_value']:,.2f} | ${r['total_return']:+,.2f} | {emoji} {r['return_pct']:+.2f}% |")
    report.append("")
    
    # Best and Worst Experiments Detail
    best_exp = max(all_results, key=lambda x: x['return_pct'])
    worst_exp = min(all_results, key=lambda x: x['return_pct'])
    
    report.append("## 🏆 Best Performing Period\n")
    report.append(f"**Period:** {best_exp['start_date'].strftime('%Y-%m-%d')} to {best_exp['actual_end_date'].strftime('%Y-%m-%d')}\n")
    report.append(f"- Invested: ${best_exp['total_invested']:,.2f}")
    report.append(f"- Final Value: ${best_exp['final_value']:,.2f}")
    report.append(f"- Return: {best_exp['return_pct']:+.2f}% (${best_exp['total_return']:+,.2f})")
    report.append(f"- Trading Days: {best_exp['trading_days_count']}")
    report.append("")
    
    report.append("## 📉 Worst Performing Period\n")
    report.append(f"**Period:** {worst_exp['start_date'].strftime('%Y-%m-%d')} to {worst_exp['actual_end_date'].strftime('%Y-%m-%d')}\n")
    report.append(f"- Invested: ${worst_exp['total_invested']:,.2f}")
    report.append(f"- Final Value: ${worst_exp['final_value']:,.2f}")
    report.append(f"- Return: {worst_exp['return_pct']:+.2f}% (${worst_exp['total_return']:+,.2f})")
    report.append(f"- Trading Days: {worst_exp['trading_days_count']}")
    report.append("")
    
    # Key Insights
    report.append("## 💡 Key Insights\n")
    
    report.append(f"- **Experiments Run**: {num_experiments} different {first_result['duration_days']}-day investment periods were simulated")
    report.append(f"- **Success Rate**: {profitable_experiments} out of {num_experiments} experiments ({(profitable_experiments/num_experiments)*100:.1f}%) were profitable")
    report.append(f"- **Average Performance**: On average, a ${avg_invested:.2f} investment grew to ${avg_final_value:.2f} ({avg_return:+.2f}%)")
    report.append(f"- **Risk Assessment**: Returns varied from {min_return:+.2f}% to {max_return:+.2f}% with a standard deviation of {std_return:.2f}%")
    report.append(f"- **Consistency**: The median return was {median_return:+.2f}%, {'close to' if abs(median_return - avg_return) < 2 else 'different from'} the average of {avg_return:+.2f}%")
    
    # Calculate Sharpe-like ratio (simplified, assuming 0% risk-free rate)
    sharpe_like = avg_return / std_return if std_return > 0 else 0
    report.append(f"- **Risk-Adjusted Performance**: Return/Risk ratio of {sharpe_like:.2f}")
    
    report.append("")
    report.append("---")
    report.append("*This is a simulation for educational purposes only. Past performance does not guarantee future results.*")
    
    # Write to file
    report_content = "\n".join(report)
    with open(output_file, 'w') as f:
        f.write(report_content)
    
    print(f"\n✅ Report saved to: {output_file}")
    return report_content


def main():
    """Main entry point for the experiment."""
    print("=" * 60)
    print("🚀 S&P 500 Dollar Cost Averaging Experiment")
    print(f"   Running {NUM_EXPERIMENTS} experiments")
    print("=" * 60)
    
    # Get the script's directory to handle relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, DATASET_PATH)
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    
    # Load data
    df = load_data(dataset_path)
    
    # Get valid start dates
    valid_dates = get_valid_start_dates(df, EXPERIMENT_DURATION_DAYS)
    print(f"Found {len(valid_dates)} valid start dates for a {EXPERIMENT_DURATION_DAYS}-day experiment")
    
    if not valid_dates:
        print("❌ Error: No valid start dates found. Try reducing the experiment duration.")
        return
    
    # Initialize random seed if provided
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)
    
    # Select random start dates for all experiments (without replacement if possible)
    if len(valid_dates) >= NUM_EXPERIMENTS:
        selected_dates = random.sample(valid_dates, NUM_EXPERIMENTS)
    else:
        # If not enough unique dates, allow duplicates
        selected_dates = random.choices(valid_dates, k=NUM_EXPERIMENTS)
    
    selected_dates = sorted(selected_dates)  # Sort chronologically for nicer output
    
    # Run all experiments
    all_results = []
    print(f"\n🔄 Running {NUM_EXPERIMENTS} experiments...")
    
    for i, start_date in enumerate(selected_dates, 1):
        print(f"   [{i}/{NUM_EXPERIMENTS}] Starting from {pd.Timestamp(start_date).strftime('%Y-%m-%d')}...", end=" ")
        
        results = run_experiment(
            df=df,
            start_date=pd.Timestamp(start_date),
            duration_days=EXPERIMENT_DURATION_DAYS,
            daily_investment=DAILY_INVESTMENT,
            price_column=PRICE_COLUMN,
            stock_ticker=STOCK_TICKER
        )
        all_results.append(results)
        print(f"Return: {results['return_pct']:+.2f}%")
    
    # Calculate aggregate statistics
    returns = [r['return_pct'] for r in all_results]
    avg_return = np.mean(returns)
    avg_invested = np.mean([r['total_invested'] for r in all_results])
    avg_final = np.mean([r['final_value'] for r in all_results])
    
    # Print aggregate summary
    print(f"\n📊 Aggregate Summary ({NUM_EXPERIMENTS} experiments):")
    print(f"   • Average Return: {avg_return:+.2f}%")
    print(f"   • Best Return: {max(returns):+.2f}%")
    print(f"   • Worst Return: {min(returns):+.2f}%")
    print(f"   • Std Deviation: {np.std(returns):.2f}%")
    print(f"   • Average Invested: ${avg_invested:,.2f}")
    print(f"   • Average Final Value: ${avg_final:,.2f}")
    
    # Generate report
    generate_report(all_results, output_path)
    
    print("\n" + "=" * 60)
    print("✨ Experiment complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
