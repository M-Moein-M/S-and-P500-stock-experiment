## 🎯 Research Question

**"Does it matter which specific day you invest, or is consistency what truly matters in Dollar Cost Averaging?"**

This simulation tests whether timing matters in DCA strategies by comparing daily investments against weekly and monthly random timing approaches across the same investment periods.


# 🔎 Results Summary

A quick, high-visibility snapshot of strategy performance so you see outcomes first.

## 📆 4-Year Horizon (1460 days)

| Strategy | Avg Return | Best | Worst | Std Dev | Success Rate | Risk/Return |
|----------|------------|------|-------|---------|--------------|-------------|
| 🥇 Weekly Random | **+24.92%** | +30.80% | +21.68% | 1.70% | 100.0% | 14.63 |
| 🥈 Monthly Random | **+24.92%** | +31.55% | +21.29% | 1.95% | 100.0% | 12.79 |
| 🥉 Daily Investment | **+24.90%** | +30.83% | +21.62% | 1.71% | 100.0% | 14.57 |

## 📆 3-Year Horizon (1095 days)

| Strategy | Avg Return | Best | Worst | Std Dev | Success Rate | Risk/Return |
|----------|------------|------|-------|---------|--------------|-------------|
| 🥇 Weekly Random | **+13.92%** | +22.63% | +6.27% | 3.74% | 100.0% | 3.72 |
| 🥈 Daily Investment | **+13.91%** | +22.65% | +6.30% | 3.72% | 100.0% | 3.74 |
| 🥉 Monthly Random | **+13.82%** | +22.62% | +6.45% | 3.75% | 100.0% | 3.68 |

## 📆 2-Year Horizon (730 days)

| Strategy | Avg Return | Best | Worst | Std Dev | Success Rate | Risk/Return |
|----------|------------|------|-------|---------|--------------|-------------|
| 🥇 Daily Investment | **+10.18%** | +20.20% | -6.16% | 7.72% | 90.0% | 1.32 |
| 🥈 Weekly Random | **+10.14%** | +20.13% | -6.17% | 7.70% | 90.0% | 1.32 |
| 🥉 Monthly Random | **+10.06%** | +19.61% | -6.41% | 7.68% | 90.0% | 1.31 |

### 💡 Cross-Horizon Takeaways

- **Consistency Wins**: Differences across timing strategies are small within each horizon.
- **Risk Drops Over Time**: Longer horizons show markedly lower volatility (std dev).
- **Risk-Adjusted Edge**: For 3–4 years, weekly/daily offer the best risk-adjusted returns.
- **All Positive Long-Run**: 3–4 year horizons had 100% success rates in simulations.

— See full analyses: [2yrs_multi_strategy_report.md](2yrs_multi_strategy_report.md), [3yrs_multi_strategy_report.md](3yrs_multi_strategy_report.md), [4yrs_multi_strategy_report.md](4yrs_multi_strategy_report.md)

# 📈 S&P 500 Dollar Cost Averaging Strategy Comparison

A comprehensive simulation framework comparing different Dollar Cost Averaging (DCA) investment timing strategies using historical S&P 500 data. This project explores whether the specific timing of investments within a given period significantly impacts long-term returns.

## 📊 Dataset

This project uses historical S&P 500 stock data from 2013-2018, sourced from [Kaggle's S&P 500 Stock Data](https://www.kaggle.com/datasets/camnugent/sandp500). The dataset includes daily price information for all S&P 500 companies during this period.

## 🚀 Quick Start

1. **Run the multi-strategy experiment:**
   ```bash
   python main_experiment.py
   ```

2. **Review results:**
   - Generated reports: [2yrs_multi_strategy_report.md](2yrs_multi_strategy_report.md), [3yrs_multi_strategy_report.md](3yrs_multi_strategy_report.md), [4yrs_multi_strategy_report.md](4yrs_multi_strategy_report.md)
   - Console output shows real-time progress and summary statistics

## 💡 Investment Strategies

The simulation compares three distinct Dollar Cost Averaging approaches:

### 📅 Daily Strategy
- **Method**: Invests $1.00 every single trading day
- **Frequency**: ~252 investments per year
- **Approach**: Maximum consistency and market timing neutralization

### 🎲 Weekly Random Strategy  
- **Method**: Invests weekly equivalent ($5-7) on one random day each week
- **Frequency**: ~52 investments per year  
- **Approach**: Tests whether weekly timing variations affect returns

### 🗓️ Monthly Random Strategy
- **Method**: Invests monthly equivalent ($20-23) on one random day each month
- **Frequency**: ~12 investments per year
- **Approach**: Tests whether monthly timing variations affect returns

All strategies invest identical total amounts over the same time periods, ensuring fair comparison across different timing approaches.

## 📊 Experiment Design

- **Sample Size**: 20 experiments with different random start dates
- **Duration**: 3 years (1,095 days) per experiment  
- **Investment**: $1/day equivalent across all strategies
- **Price Data**: Uses closing prices for all purchases
- **Scope**: Equal investment across all available S&P 500 stocks
- **Time Period**: Historical data from 2013-2018

## 🗂️ Project Structure

```
stock-snp500-experiment/
├── main_experiment.py          # Main simulation script
├── strategy.py                 # Strategy class implementations  
├── all_stocks_5yr.csv         # S&P 500 historical data (2013-2018)
├── 3yrs_multi_strategy_report.md # Generated analysis report
└── sandpzipfolder/            # Data processing utilities
    ├── getSandP.py
    ├── merge.sh
    └── individual_stocks_5yr/  # Individual stock data files
```

## ⚙️ Configuration

Customize your experiment by editing `main_experiment.py`:

```python
# Core Parameters
DAILY_INVESTMENT = 1.0                    # Daily investment amount ($)
EXPERIMENT_DURATION_DAYS = 365*3          # Experiment length (days)
NUM_EXPERIMENTS = 20                      # Number of random start dates
RANDOM_SEED = 42                         # For reproducible results

# Optional Customizations  
PRICE_COLUMN = 'close'                   # Price type for purchases
STOCK_TICKER = None                      # Specific stock or None for all S&P 500
OUTPUT_FILE = '3yrs_multi_strategy_report.md'  # Report filename
```

## 📋 Understanding Results

The generated report provides comprehensive analysis including:

### Performance Comparison
- Average returns across all experiments
- Success rates (percentage of profitable experiments)  
- Risk metrics and volatility measures
- Risk-adjusted performance ratios

### Detailed Analysis
- Individual experiment outcomes
- Strategy-specific performance breakdowns
- Investment timing impact assessment

### Key Insights
- Whether timing variations significantly affect returns
- Risk-return tradeoffs between strategies
- Consistency and reliability measures

## 🔬 Architecture

The simulation framework uses an object-oriented design with three main strategy classes:

### Strategy Classes
- **`DailyStrategy`**: Implements daily investment logic
- **`WeeklyRandomStrategy`**: Implements weekly random timing
- **`MonthlyRandomStrategy`**: Implements monthly random timing

Each strategy inherits from `BaseStrategy` and manages its own:
- Portfolio tracking and position management
- Transaction recording and history
- Performance calculation and metrics
- Final portfolio valuation

### Extensibility
The modular design allows easy addition of new investment strategies by creating new classes that inherit from `BaseStrategy` and implement the required methods.

## 🧪 Customizing Your Analysis

### Test Specific Stocks
```python
STOCK_TICKER = 'AAPL'  # Focus on Apple
STOCK_TICKER = 'GOOGL' # Focus on Google  
STOCK_TICKER = None    # Use entire S&P 500
```

### Adjust Time Horizons
```python
EXPERIMENT_DURATION_DAYS = 365      # 1 year analysis
EXPERIMENT_DURATION_DAYS = 365*2    # 2 year analysis
EXPERIMENT_DURATION_DAYS = 365*5    # 5 year analysis
```

### Modify Investment Amounts
```python
DAILY_INVESTMENT = 5.0   # $5/day equivalent
DAILY_INVESTMENT = 10.0  # $10/day equivalent
```

## ⚠️ Important Considerations

- **Educational Purpose**: This simulation was created based on personal curiosity.
- **Historical Analysis**: Results are based on historical data and do not predict future market performance
- **Simplified Model**: Real-world investing involves transaction costs, taxes, dividends, and other factors not modeled in this simulation
- **Data Dependency**: Analysis quality depends on the accuracy and completeness of the historical dataset

## Next Step
- Consider making a website that people can build their own strategy and compete with each other. The AI would also implement the code and would fit the code into the framework.


