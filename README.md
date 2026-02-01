# 📈 S&P 500 Dollar Cost Averaging Strategy Comparison

A comprehensive simulation framework comparing different Dollar Cost Averaging (DCA) investment timing strategies using historical S&P 500 data. This project explores whether the specific timing of investments within a given period significantly impacts long-term returns.

## 🎯 Research Question

**"Does it matter which specific day you invest, or is consistency what truly matters in Dollar Cost Averaging?"**

This simulation tests whether timing matters in DCA strategies by comparing daily investments against weekly and monthly random timing approaches across the same investment periods.

## 📊 Dataset

This project uses historical S&P 500 stock data from 2013-2018, sourced from [Kaggle's S&P 500 Stock Data](https://www.kaggle.com/datasets/camnugent/sandp500). The dataset includes daily price information for all S&P 500 companies during this period.

## 🚀 Quick Start

1. **Run the multi-strategy experiment:**
   ```bash
   python main_experiment.py
   ```

2. **Review results:**
   - Generated report: `3yrs_multi_strategy_report.md`
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
