#!/usr/bin/env python3
print("""
S&P 500 Dollar Cost Averaging Experiment - Multi-Strategy Comparison

This script runs three different investment strategies simultaneously:
1. Daily: Invests every trading day
2. Weekly Random: Invests weekly amount on random day each week  
3. Monthly Random: Invests monthly amount on random day each month

All strategies use the same total investment amount and time periods for fair comparison.
""")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from strategy import DailyStrategy, WeeklyRandomStrategy, MonthlyRandomStrategy

# ============================================================================
# CONFIGURATION - Modify these values to customize the experiment
# ============================================================================

# Investment amount per day (in USD)
DAILY_INVESTMENT = 1.0

# Duration of the experiment in days (365 = 1 year)
EXPERIMENT_DURATION_DAYS = 365*1

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
OUTPUT_FILE = f'{EXPERIMENT_DURATION_DAYS//365}yrs_multi_strategy_report.md'

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


def run_multi_strategy_experiment(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    duration_days: int,
    daily_investment: float,
    price_column: str,
    stock_ticker: str = None
) -> dict:
    """
    Run all three strategies on the same time period.
    
    Returns a dictionary with results for each strategy.
    """
    end_date = start_date + timedelta(days=duration_days)
    
    # Initialize strategies
    strategies = {
        'daily': DailyStrategy(daily_investment, price_column, stock_ticker),
        'weekly_random': WeeklyRandomStrategy(daily_investment, price_column, stock_ticker),
        'monthly_random': MonthlyRandomStrategy(daily_investment, price_column, stock_ticker)
    }
    
    # Run each strategy
    results = {}
    
    for strategy_key, strategy in strategies.items():
        try:
            strategy_results = strategy.run_experiment(df, start_date, duration_days)
            
            # Add common experiment metadata
            strategy_results.update({
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': duration_days,
                'daily_investment': daily_investment,
                'price_column': price_column,
                'stock_ticker': stock_ticker,
                'annualized_return_pct': (((strategy_results['final_value'] / strategy_results['total_invested']) ** (365 / duration_days)) - 1) * 100 
                                          if strategy_results['total_invested'] > 0 and duration_days > 0 else 0
            })
            
            results[strategy_key] = strategy_results
            
        except Exception as e:
            print(f"Error running {strategy.strategy_name} strategy: {e}")
            results[strategy_key] = None
    
    return results


def generate_multi_strategy_report(all_results: list, output_file: str):
    """Generate a comprehensive markdown report comparing all strategies."""
    
    report = []
    report.append("# 📈 S&P 500 Multi-Strategy Dollar Cost Averaging Report\n")
    report.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Get experiment count and basic parameters
    num_experiments = len(all_results)
    first_result = all_results[0]
    
    # Find first valid strategy result for parameters
    sample_strategy = None
    for strategy_key in ['daily', 'weekly_random', 'monthly_random']:
        if first_result[strategy_key] is not None:
            sample_strategy = first_result[strategy_key]
            break
    
    if sample_strategy is None:
        report.append("❌ **Error**: No valid strategy results found.\n")
        return "\n".join(report)
    
    # Experiment Parameters
    report.append("## 🔧 Experiment Parameters\n")
    report.append("| Parameter | Value |")
    report.append("|-----------|-------|")
    report.append(f"| Number of Experiments | {num_experiments} |")
    report.append(f"| Duration per Experiment | {sample_strategy['duration_days']} days |")
    report.append(f"| Daily Investment | ${sample_strategy['daily_investment']:.2f} |")
    report.append(f"| Price Column Used | {sample_strategy['price_column']} |")
    report.append(f"| Stock(s) | {sample_strategy['stock_ticker'] if sample_strategy['stock_ticker'] else 'All S&P 500 stocks'} |")
    report.append("")
    
    # Strategy Comparison
    report.append("## 🥇 Strategy Performance Comparison\n")
    
    # Collect results by strategy
    strategy_stats = {}
    strategy_names = {
        'daily': 'Daily Investment',
        'weekly_random': 'Weekly Random',
        'monthly_random': 'Monthly Random'
    }
    
    for strategy_key, strategy_name in strategy_names.items():
        returns = []
        annualized_returns = []
        investments = []
        final_values = []
        
        for result in all_results:
            if result[strategy_key] is not None:
                returns.append(result[strategy_key]['return_pct'])
                annualized_returns.append(result[strategy_key]['annualized_return_pct'])
                investments.append(result[strategy_key]['total_invested'])
                final_values.append(result[strategy_key]['final_value'])
        
        if returns:  # Only calculate if we have data
            strategy_stats[strategy_key] = {
                'name': strategy_name,
                'avg_return': np.mean(returns),
                'median_return': np.median(returns),
                'std_return': np.std(returns),
                'min_return': min(returns),
                'max_return': max(returns),
                'avg_annualized': np.mean(annualized_returns),
                'avg_invested': np.mean(investments),
                'avg_final_value': np.mean(final_values),
                'profitable_count': sum(1 for r in returns if r > 0),
                'total_experiments': len(returns),
                'sharpe_ratio': np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            }
    
    # Strategy Summary Table
    report.append("### 📊 Strategy Performance Summary\n")
    report.append("| Strategy | Avg Return | Best | Worst | Std Dev | Success Rate | Risk/Return |")
    report.append("|----------|------------|------|-------|---------|--------------|-------------|")
    
    # Sort strategies by average return for ranking
    sorted_strategies = sorted(strategy_stats.items(), key=lambda x: x[1]['avg_return'], reverse=True)
    
    for i, (strategy_key, stats) in enumerate(sorted_strategies):
        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📊"
        success_rate = (stats['profitable_count'] / stats['total_experiments']) * 100
        report.append(f"| {emoji} **{stats['name']}** | **{stats['avg_return']:+.2f}%** | {stats['max_return']:+.2f}% | {stats['min_return']:+.2f}% | {stats['std_return']:.2f}% | {success_rate:.1f}% | {stats['sharpe_ratio']:.2f} |")
    
    report.append("")
    
    # Detailed Strategy Analysis
    report.append("## 📋 Detailed Strategy Analysis\n")
    
    for strategy_key, stats in sorted_strategies:
        emoji = "🟢" if stats['avg_return'] >= 0 else "🔴"
        report.append(f"### {emoji} {stats['name']}\n")
        report.append(f"**Strategy**: {strategy_stats[strategy_key]['name']}\n")
        report.append("")
        report.append("| Metric | Value |")
        report.append("|--------|-------|")
        report.append(f"| Average Return | {stats['avg_return']:+.2f}% |")
        report.append(f"| Median Return | {stats['median_return']:+.2f}% |")
        report.append(f"| Annualized Return | {stats['avg_annualized']:+.2f}% |")
        report.append(f"| Standard Deviation | {stats['std_return']:.2f}% |")
        report.append(f"| Best Performance | {stats['max_return']:+.2f}% |")
        report.append(f"| Worst Performance | {stats['min_return']:+.2f}% |")
        report.append(f"| Success Rate | {(stats['profitable_count']/stats['total_experiments'])*100:.1f}% ({stats['profitable_count']}/{stats['total_experiments']}) |")
        report.append(f"| Average Invested | ${stats['avg_invested']:,.2f} |")
        report.append(f"| Average Final Value | ${stats['avg_final_value']:,.2f} |")
        report.append(f"| Risk-Adjusted Return | {stats['sharpe_ratio']:.3f} |")
        report.append("")
    
    # Individual Experiment Results
    report.append("## 📅 Individual Experiment Results\n")
    report.append("| # | Start Date | Daily | Weekly Random | Monthly Random | Best Strategy |")
    report.append("|---|------------|-------|---------------|----------------|---------------|")
    
    for i, result in enumerate(all_results, 1):
        start_date = ""
        daily_return = "N/A"
        weekly_return = "N/A"
        monthly_return = "N/A"
        
        returns = {}
        
        if result['daily'] is not None:
            start_date = result['daily']['start_date'].strftime('%Y-%m-%d')
            daily_return = f"{result['daily']['return_pct']:+.2f}%"
            returns['Daily'] = result['daily']['return_pct']
        
        if result['weekly_random'] is not None:
            if not start_date:
                start_date = result['weekly_random']['start_date'].strftime('%Y-%m-%d')
            weekly_return = f"{result['weekly_random']['return_pct']:+.2f}%"
            returns['Weekly'] = result['weekly_random']['return_pct']
        
        if result['monthly_random'] is not None:
            if not start_date:
                start_date = result['monthly_random']['start_date'].strftime('%Y-%m-%d')
            monthly_return = f"{result['monthly_random']['return_pct']:+.2f}%"
            returns['Monthly'] = result['monthly_random']['return_pct']
        
        # Find best strategy for this experiment
        if returns:
            best_strategy = max(returns, key=returns.get)
            best_return = returns[best_strategy]
            best_display = f"🏆 {best_strategy} ({best_return:+.2f}%)"
        else:
            best_display = "N/A"
        
        report.append(f"| {i} | {start_date} | {daily_return} | {weekly_return} | {monthly_return} | {best_display} |")
    
    report.append("")
    
    # Key Insights
    report.append("## 💡 Key Insights\n")
    
    if strategy_stats:
        best_strategy = sorted_strategies[0]
        worst_strategy = sorted_strategies[-1] if len(sorted_strategies) > 1 else sorted_strategies[0]
        
        report.append(f"- **Best Strategy**: {best_strategy[1]['name']} with average return of {best_strategy[1]['avg_return']:+.2f}%")
        report.append(f"- **Most Consistent**: Strategy with lowest risk (std dev): {min(strategy_stats.values(), key=lambda x: x['std_return'])['name']}")
        report.append(f"- **Highest Success Rate**: {max(strategy_stats.values(), key=lambda x: x['profitable_count']/x['total_experiments'])['name']} with {max(s['profitable_count']/s['total_experiments'] for s in strategy_stats.values())*100:.1f}% profitable experiments")
        
        # Investment timing insight
        daily_avg = strategy_stats.get('daily', {}).get('avg_return', 0)
        weekly_avg = strategy_stats.get('weekly_random', {}).get('avg_return', 0) 
        monthly_avg = strategy_stats.get('monthly_random', {}).get('avg_return', 0)
        
        timing_diff = max(daily_avg, weekly_avg, monthly_avg) - min(daily_avg, weekly_avg, monthly_avg)
        
        if timing_diff < 1:
            report.append(f"- **Timing Impact**: Minimal difference ({timing_diff:.2f}%) between strategies suggests timing within periods has low impact")
        else:
            report.append(f"- **Timing Impact**: Notable difference ({timing_diff:.2f}%) between strategies suggests timing can matter")
        
        report.append(f"- **Risk vs Return**: Consider both return and consistency when choosing a strategy")
    
    report.append("")
    report.append("---")
    report.append("*This is a simulation for educational purposes only. Past performance does not guarantee future results.*")
    
    # Write to file
    report_content = "\n".join(report)
    with open(output_file, 'w') as f:
        f.write(report_content)
    
    print(f"\n✅ Multi-strategy report saved to: {output_file}")
    return report_content


def main():
    """Main entry point for the multi-strategy experiment."""
    print("=" * 70)
    print("🚀 S&P 500 Multi-Strategy Dollar Cost Averaging Experiment")
    print(f"   Comparing 3 strategies across {NUM_EXPERIMENTS} experiments")
    print("=" * 70)
    
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
    
    # Select random start dates for all experiments
    if len(valid_dates) >= NUM_EXPERIMENTS:
        selected_dates = random.sample(valid_dates, NUM_EXPERIMENTS)
    else:
        # If not enough unique dates, allow duplicates
        selected_dates = random.choices(valid_dates, k=NUM_EXPERIMENTS)
    
    selected_dates = sorted(selected_dates)
    
    # Run all experiments
    all_results = []
    print(f"\n🔄 Running {NUM_EXPERIMENTS} experiments with 3 strategies each...")
    
    for i, start_date in enumerate(selected_dates, 1):
        print(f"   [{i:2d}/{NUM_EXPERIMENTS}] Starting from {pd.Timestamp(start_date).strftime('%Y-%m-%d')}...")
        
        results = run_multi_strategy_experiment(
            df=df,
            start_date=pd.Timestamp(start_date),
            duration_days=EXPERIMENT_DURATION_DAYS,
            daily_investment=DAILY_INVESTMENT,
            price_column=PRICE_COLUMN,
            stock_ticker=STOCK_TICKER
        )
        all_results.append(results)
        
        # Print quick summary for this experiment
        returns_summary = []
        for strategy_key in ['daily', 'weekly_random', 'monthly_random']:
            if results[strategy_key] is not None:
                returns_summary.append(f"{strategy_key.replace('_', ' ').title()}: {results[strategy_key]['return_pct']:+.2f}%")
        print(f"       {' | '.join(returns_summary)}")
    
    # Generate aggregate summary
    print(f"\n📊 Experiment Complete!")
    print(f"   Ran {NUM_EXPERIMENTS} experiments × 3 strategies = {NUM_EXPERIMENTS * 3} total simulations")
    
    # Generate comprehensive report
    generate_multi_strategy_report(all_results, output_path)
    
    print("\n" + "=" * 70)
    print("✨ Multi-strategy analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()