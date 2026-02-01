# 📈 S&P 500 Dollar Cost Averaging Strategy Comparison

A comprehensive simulation comparing different Dollar Cost Averaging (DCA) investment timing strategies using historical S&P 500 data from 2013-2018.

## 🎯 Core Question

**"Does it matter which specific day you invest, or is consistency what truly matters in Dollar Cost Averaging?"**

This project tests whether the timing of your investments within a given period (daily vs. weekly vs. monthly) significantly impacts returns, or if DCA smooths out market noise regardless of the specific day chosen.

## 🚀 Quick Start

1. **Run the experiment:**
   ```bash
   python main_experiment.py
   ```

2. **View results:**
   - Check the generated markdown report: `3yrs_multi_strategy_report.md`
   - Review console output for real-time experiment progress

## 💡 Investment Strategies Tested

### 📅 Daily Strategy
- **Method**: Invests $1.00 every single trading day
- **Frequency**: ~252 investments per year
- **Philosophy**: Maximum consistency and smoothing

### 🎲 Weekly Random Strategy  
- **Method**: Invests $5-7 (weekly equivalent) on one random day each week
- **Frequency**: ~52 investments per year  
- **Philosophy**: Tests if weekly timing matters

### 🗓️ Monthly Random Strategy
- **Method**: Invests $20-23 (monthly equivalent) on one random day each month
- **Frequency**: ~12 investments per year
- **Philosophy**: Tests if monthly timing matters

> **Key Insight**: All strategies invest the same total amount over the same time periods, ensuring fair comparison.

## 📊 Experiment Design

- **🎲 Sample Size**: 20 experiments with different random start dates
- **⏱️ Duration**: 3 years (1,095 days) per experiment  
- **💰 Investment**: $1/day equivalent across all strategies
- **📈 Price**: Uses closing prices for purchases
- **🎯 Scope**: Invests equally across all S&P 500 stocks
- **📅 Data**: Historical S&P 500 data (2013-2018)

## 🗂️ Project Structure

```
stock-snp500-experiment/
├── main_experiment.py          # Main script - runs all strategies
├── strategy.py                 # Strategy class implementations  
├── all_stocks_5yr.csv         # Historical S&P 500 data (2013-2018)
├── 3yrs_multi_strategy_report.md # Generated analysis report
├── sandpzipfolder/            # Data processing utilities
│   ├── getSandP.py
│   ├── merge.sh
│   └── individual_stocks_5yr/  # Individual stock data files
└── README.md                  # This file
```

## ⚙️ Configuration Options

Edit `main_experiment.py` to customize your experiment:

```python
# Investment Parameters
DAILY_INVESTMENT = 1.0                    # Daily investment amount ($)
EXPERIMENT_DURATION_DAYS = 365*3          # Experiment length (days)
PRICE_COLUMN = 'close'                    # Price type: 'open', 'high', 'low', 'close'

# Experiment Settings
NUM_EXPERIMENTS = 20                      # Number of random start dates to test
RANDOM_SEED = 42                         # For reproducible results (None = random)

# Stock Selection  
STOCK_TICKER = None                      # Specific stock ('AAPL') or None for all S&P 500

# Output
OUTPUT_FILE = '3yrs_multi_strategy_report.md'  # Report filename
```

## 📋 Understanding the Results

The generated report includes:

### 🏆 Strategy Performance Comparison
- Average returns across all experiments
- Success rates (% profitable experiments)  
- Risk metrics (standard deviation)
- Risk-adjusted returns (Sharpe ratio)

### 📊 Detailed Analysis
- Best and worst performance for each strategy
- Individual experiment results
- Investment timing impact analysis

### 💡 Key Metrics
- **Total Return %**: Overall profit/loss percentage
- **Annualized Return %**: Yearly equivalent return rate
- **Success Rate**: Percentage of profitable experiments
- **Risk/Return Ratio**: Return per unit of risk taken

## 🔬 Sample Results Interpretation

**Scenario A - Timing Doesn't Matter Much:**
```
Daily: +8.2% average return
Weekly Random: +8.1% average return  
Monthly Random: +8.3% average return
→ Conclusion: DCA timing impact is minimal
```

**Scenario B - Timing Matters:**
```
Daily: +8.2% average return
Weekly Random: +6.8% average return
Monthly Random: +5.1% average return  
→ Conclusion: More frequent investing may be better
```

## 🛠️ Technical Requirements

### Python Dependencies
```python
pandas>=1.3.0        # Data manipulation
numpy>=1.20.0        # Numerical computing  
datetime             # Date/time handling
random               # Random number generation
```

### Data Requirements
- `all_stocks_5yr.csv`: Historical S&P 500 stock data
- Required columns: `date`, `Name`, `open`, `high`, `low`, `close`, `volume`
- Date range: 2013-2018 (or sufficient for your experiment duration)

## 🚀 Running Your Own Experiments

### Test Different Stocks
```python
STOCK_TICKER = 'AAPL'  # Test Apple specifically
STOCK_TICKER = 'GOOGL'  # Test Google specifically  
STOCK_TICKER = None     # Test entire S&P 500
```

### Adjust Time Periods
```python
EXPERIMENT_DURATION_DAYS = 365      # 1 year experiments
EXPERIMENT_DURATION_DAYS = 365*2    # 2 year experiments
EXPERIMENT_DURATION_DAYS = 365*5    # 5 year experiments
```

### Change Investment Amounts
```python
DAILY_INVESTMENT = 5.0   # $5/day experiments
DAILY_INVESTMENT = 10.0  # $10/day experiments
```

## 📈 Strategy Classes

The `strategy.py` file contains three main classes:

- **`DailyStrategy`**: Implements daily investment logic
- **`WeeklyRandomStrategy`**: Implements weekly random timing
- **`MonthlyRandomStrategy`**: Implements monthly random timing

Each strategy inherits from `BaseStrategy` and implements:
- Portfolio tracking
- Transaction recording  
- Performance calculation
- Final valuation

## 🧪 Extending the Project

### Add New Strategies
Create a new strategy class in `strategy.py`:

```python
class YourCustomStrategy(BaseStrategy):
    @property
    def strategy_name(self) -> str:
        return "Your Strategy Name"
    
    def run_experiment(self, df, start_date, duration_days):
        # Implement your investment logic
        pass
```

### Modify Analysis
Edit the report generation in `generate_multi_strategy_report()` to add:
- New performance metrics
- Different visualizations  
- Custom insights

## ⚠️ Important Notes

- **Educational Purpose**: This is a simulation for learning about investment strategies
- **Historical Data**: Past performance does not guarantee future results
- **Simplified Model**: Real investing has fees, taxes, and other complexities not modeled
- **Data Quality**: Results depend on the accuracy of historical data used

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new strategies
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure you comply with any data licensing requirements for the S&P 500 historical data used.

---

*Happy investing and may your Dollar Cost Averaging strategy be ever in your favor! 📈*